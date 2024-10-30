from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic.edit import FormView
from django.contrib import messages  
from django.db.models import Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.core.cache import cache
import time
from .forms import  EditProductForm, OrderDetailForm, BarcodeForm, ItemForm, AddProductForm
from .models import Item, Product, Category, Order, OrderDetail, Customer, RecentlyPurchasedProduct 

# Home view
def home(request):
    return render(request, 'home.html')

# View to handle the creation of orders
class CreateOrderView(View):
    template_name = 'order_form.html'

    def get_order(self, request):
        order_id = request.session.get('order_id')
        if order_id:
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                order = self._create_new_order(request)
        else:
            order = self._create_new_order(request)
        return order

    def _create_new_order(self, request):
        # Get the next available order_id
        last_order = Order.objects.order_by('-order_id').first()
        next_order_id = 1 if not last_order else last_order.order_id + 1

        # Create a new order with the next available order_id
        order = Order.objects.create(order_id=next_order_id, total_price=Decimal('0.00'))

        # Store the new order_id in the session
        request.session['order_id'] = order.order_id

        return order

    def get(self, request, *args, **kwargs):
        order = self.get_order(request)
        form = BarcodeForm()
        order_details = order.details.all()
        total_price_before_tax = sum(detail.price for detail in order_details)
        total_price_after_tax = total_price_before_tax * Decimal('1.13')

        return render(request, self.template_name, {
            'order': order,
            'form': form,
            'order_details': order_details,
            'total_price_before_tax': total_price_before_tax,
            'total_price_after_tax': total_price_after_tax,
        })

    def post(self, request, *args, **kwargs):
        order = self.get_order(request)
        form = BarcodeForm(request.POST)

        # Check for add-to-cart by product_name and product_price (clicked item)
        product_name = request.POST.get('product_name')
        product_price = request.POST.get('product_price')

        # If product_name and product_price are provided, add the item directly
        if product_name and product_price:
            try:
                price = Decimal(product_price)
                quantity = 1  # Default quantity for click-to-add items
                order_detail, created = OrderDetail.objects.get_or_create(
                    order=order,
                    product=None,
                    defaults={'product_name': product_name, 'quantity': quantity, 'price': price}
                )
                if not created:
                    order_detail.quantity += 1
                    order_detail.price += price
                    order_detail.save()

                # Update the order's total price
                order.total_price += price
                order.save()

                messages.success(request, f"{product_name} added to the order.")
                return redirect('create_order')

            except Decimal.InvalidOperation:
                messages.error(request, "Invalid price format.")
                return redirect('create_order')

        # Barcode form submission handling
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            quantity = form.cleaned_data.get('quantity', 1)

            try:
                product = Product.objects.get(barcode=barcode)
            except Product.DoesNotExist:
                messages.error(request, f"No product found with barcode '{barcode}'.")
                return redirect('create_order')

            if product.quantity_in_stock < quantity:
                messages.error(request, f"Not enough stock for {product.name}.")
                return redirect('create_order')

            price = product.price * quantity

            order_detail, created = OrderDetail.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': quantity, 'price': price}
            )
            if not created:
                order_detail.quantity += quantity
                order_detail.price += price
                order_detail.save()

            order.total_price += price
            order.save()

            product.quantity_in_stock -= quantity
            product.save()

            messages.success(request, f"{quantity} unit(s) of {product.name} added to the order.")
            return redirect('create_order')

        # On form error, re-render with current order details
        order_details = order.details.all()
        total_price_before_tax = sum(detail.price for detail in order_details)
        total_price_after_tax = total_price_before_tax * Decimal('1.13')

        return render(request, self.template_name, {
            'order': order,
            'form': form,
            'order_details': order_details,
            'total_price_before_tax': total_price_before_tax,
            'total_price_after_tax': total_price_after_tax,
        })


class SubmitOrderView(View):
    def post(self, request, *args, **kwargs):
        if 'order_id' in request.session:
            order = get_object_or_404(Order, order_id=request.session['order_id'])

            # Loop through each OrderDetail and update RecentlyPurchasedProduct
            for detail in order.details.all():
                recently_purchased, created = RecentlyPurchasedProduct.objects.get_or_create(
                    product=detail.product
                )
                if not created:
                    recently_purchased.quantity += detail.quantity  # Increment quantity if product already exists
                else:
                    recently_purchased.quantity = detail.quantity  # Set quantity if newly created
                recently_purchased.save()

            # Mark the order as submitted and save
            order.submitted = True
            order.save()
            # Clear the session to start a new order
            del request.session['order_id']

            return redirect('order_success')  # Redirect to a success page
        return redirect('create_order')


def delete_order_item(request, item_id):
    # Fetch the order detail object by its id (od_id)
    order_detail = get_object_or_404(OrderDetail, od_id=item_id)
    order = order_detail.order  # Get the associated order
    product = order_detail.product  # Get the associated product

    # Decrease the quantity in the order by 1
    if order_detail.quantity > 1:
        order_detail.quantity -= 1
        order_detail.price -= product.price  # Adjust the price accordingly
        order_detail.save()

        # Increase the product's stock by 1
        product.quantity_in_stock += 1
        product.save()

        # Update the order's total price
        order.total_price -= product.price
        order.save()

        # Optionally, add a message to confirm the update
        messages.success(request, f"1 unit of {product.name} removed from the order.")
    else:
        # If quantity is 1, delete the order detail
        product.quantity_in_stock += order_detail.quantity  # Return all stock
        product.save()
        order.total_price -= order_detail.price  # Adjust the order's total price
        order.save()
        order_detail.delete()

        # Optionally, add a message to confirm deletion
        messages.success(request, f"{product.name} removed from the order.")

    # Redirect back to the CreateOrderView
    return redirect('create_order')


# View for order success page
class OrderSuccessView(View):
    template_name = 'order_success.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

# Checkin product to inventory
class CheckinProductView(View):
    template_name = 'checkin.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        barcode = request.POST.get('barcode')
        if barcode:
            try:
                product = Product.objects.get(barcode=barcode)
                product.quantity_in_stock += 1
                product.save()
                messages.success(request, f"1 unit of {product.name} added to stock.")
            except Product.DoesNotExist:
                messages.error(request, "Product does not exist. Please add the product first.")
                return redirect('new_product')
        else:
            messages.error(request, "No barcode provided.")
        
        return redirect('checkin')

# Display all orders
class OrderView(View):
    template_name = 'order_view.html'

    def get(self, request):
        orders = Order.objects.all()
        return render(request, self.template_name, {'orders': orders})

# Add a new product
class AddProductView(View):
    template_name = 'new_product.html'

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})

    def post(self, request):
        form = AddProductForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Product added successfully.")
                return redirect('checkin')
            except IntegrityError:
                messages.error(request, "A product with this barcode or item number already exists.")
        else:
            messages.error(request, "Failed to add product.")
        
        # Re-render the form with categories if validation fails
        return render(request, self.template_name, {
            'categories': Category.objects.all(),
            'form': form
        })

# Display inventory
class InventoryView(View):
    template_name = 'inventory_display.html'

    def get(self, request):
        categories = Category.objects.all()
        selected_category_id = request.GET.get('category_id')
        barcode_query = request.GET.get('barcode_query')
        name_query = request.GET.get('name_query')

        products = Product.objects.all().order_by('name')
        if selected_category_id:
            products = products.filter(category_id=selected_category_id)
        if barcode_query:
            products = products.filter(barcode__icontains=barcode_query)
        if name_query:
            products = products.filter(name__icontains=name_query)

        paginator = Paginator(products, 80)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, self.template_name, {
            'page_obj': page_obj,
            'categories': categories,
            'selected_category_id': selected_category_id,
            'barcode_query': barcode_query,
            'name_query': name_query,
        })

# Edit an existing product
class EditProductView(View):
    template_name = 'edit_product.html'

    def get(self, request, product_id):
        product = get_object_or_404(Product, product_id=product_id)
        form = EditProductForm(instance=product)
        return render(request, self.template_name, {
            'form': form,
            'product': product,
            'categories': Category.objects.all(),
        })

    def post(self, request, product_id):
        product = get_object_or_404(Product, product_id=product_id)
        form = EditProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully.")
            return redirect('inventory_display')
        return render(request, self.template_name, {
            'form': form,
            'product': product,
            'categories': Category.objects.all(),
        })
        
# View for displaying low-stock items
class LowStockView(View):
    template_name = 'low_stock.html'
    threshold = 3

    def get(self, request):
        barcode_query = request.GET.get('barcode_query')
        selected_category_id = request.GET.get('category_id')

        low_stock_products = Product.objects.filter(quantity_in_stock__lt=self.threshold)
        recently_purchased = RecentlyPurchasedProduct.objects.all().order_by('-order_date')
        categories = Category.objects.all()

        if barcode_query:
            low_stock_products = low_stock_products.filter(barcode__icontains=barcode_query)
        if selected_category_id:
            low_stock_products = low_stock_products.filter(category_id=selected_category_id)

        paginator_low_stock = Paginator(low_stock_products, 80)
        page_number_low_stock = request.GET.get('page')
        page_obj_low_stock = paginator_low_stock.get_page(page_number_low_stock)

        paginator_recent = Paginator(recently_purchased, 80)
        page_number_recent = request.GET.get('page_recent')
        page_obj_recent = paginator_recent.get_page(page_number_recent)

        return render(request, self.template_name, {
            'page_obj_low_stock': page_obj_low_stock,
            'page_obj_recent': page_obj_recent,
            'categories': categories,
            'selected_category_id': selected_category_id,
            'barcode_query': barcode_query,
            'threshold': self.threshold,
        })

# Delete an item
def delete_item(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product.delete()
    messages.success(request, f"Product '{product.name}' has been deleted.")
    return redirect('inventory_display')

# Delete a recently purchased product
class DeleteRecentlyPurchasedProductView(View):
    def post(self, request, product_id):
        recently_purchased = get_object_or_404(RecentlyPurchasedProduct, product_id=product_id)
        recently_purchased.delete()
        messages.success(request, f"{recently_purchased.product.name} has been deleted from the recently purchased list.")
        return redirect('low_stock')

# Delete all orders
class DeleteAllOrdersView(View):
    def post(self, request, *args, **kwargs):
        Order.objects.all().delete()
        request.session['next_order_id'] = 1
        messages.success(request, "All orders have been deleted successfully.")
        return redirect('order_view')

# Item list view
class ItemListView(View):
    template_name = 'item_list.html'
    form_class = ItemForm

    def get(self, request):
        form = self.form_class()
        items = Item.objects.all()
        return render(request, self.template_name, {'form': form, 'items': items})

    def post(self, request):
        if 'delete' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(Item, id=item_id)
            item.delete()
            messages.success(request, f"Item '{item.name}' has been deleted.")
            return redirect('item_list')
        elif 'update_checked' in request.POST:
            item_id = request.POST.get('item_id')
            is_checked = request.POST.get('is_checked') == 'on'
            item = get_object_or_404(Item, id=item_id)
            item.is_checked = is_checked
            item.save()
            return redirect('item_list')
        else:
            form = self.form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect('item_list')

        items = Item.objects.all()
        return render(request, self.template_name, {'form': form, 'items': items})

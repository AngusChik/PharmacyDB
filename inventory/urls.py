from django.contrib import admin
from django.urls import path
from app.views import InventoryView, EditProductView, AddProductView, CheckinProductView, LowStockView, CreateOrderView, OrderView,SubmitOrderView, delete_item, delete_order_item, ItemListView, DeleteRecentlyPurchasedProductView, DeleteAllOrdersView
from app import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('order/', CreateOrderView.as_view(), name='create_order'),
    path('order/submit/', SubmitOrderView.as_view(), name='submit_order'),
    path('checkin/', CheckinProductView.as_view(), name='checkin'),  # Updated to use the class-based view
    path('inventory/', InventoryView.as_view(), name='inventory_display'),
    path('low-stock/', LowStockView.as_view(), name='low_stock'),  # Low stock class-based view
    path('low-stock/delete/<int:id>/', DeleteRecentlyPurchasedProductView.as_view(), name='delete_recently_purchased_product'),
    path('orders/', OrderView.as_view(), name='order_view'),  # List all orders
    path('product/edit/<int:product_id>/', EditProductView.as_view(), name='edit_product'),
    path('new-product/', AddProductView.as_view(), name='new_product'),  # Updated to use the class-based view
    path('order/delete-item/<int:item_id>/', delete_order_item, name='delete_order_item'),
    path('product/delete/<int:product_id>/', delete_item, name='delete_item'),
    path('delete-orders/', DeleteAllOrdersView.as_view(), name='delete_all_orders'),
    path('item_list/', ItemListView.as_view(), name='item_list'),
]




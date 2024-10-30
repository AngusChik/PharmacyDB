# Generated by Django 4.2.16 on 2024-10-26 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0029_remove_orderdetail_taxable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetail',
            name='product_name',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='product_price',
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='custom_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='custom_product_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='custom_taxable',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.product'),
        ),
    ]

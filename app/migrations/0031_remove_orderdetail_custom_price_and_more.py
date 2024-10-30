# Generated by Django 4.2.16 on 2024-10-26 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_remove_orderdetail_product_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetail',
            name='custom_price',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='custom_product_name',
        ),
        migrations.RemoveField(
            model_name='orderdetail',
            name='custom_taxable',
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.product'),
        ),
    ]

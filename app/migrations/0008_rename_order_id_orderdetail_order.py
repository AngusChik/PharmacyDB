# Generated by Django 4.2.15 on 2024-08-22 19:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_orderdetail_order_id_alter_orderdetail_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderdetail',
            old_name='order_id',
            new_name='order',
        ),
    ]
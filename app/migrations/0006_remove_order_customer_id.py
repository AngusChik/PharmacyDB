# Generated by Django 4.2.15 on 2024-08-22 19:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_order_total_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='customer_id',
        ),
    ]
# Generated by Django 4.2.16 on 2024-10-29 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_rename_total_price_orderdetail_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='item',
            name='name',
        ),
        migrations.AddField(
            model_name='item',
            name='first_name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='item_name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='item_number',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='last_name',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='phone_number',
            field=models.CharField(default=1, max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='side',
            field=models.CharField(choices=[('left', 'Left'), ('right', 'Right'), ('na', 'N/A')], default=1, max_length=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='size',
            field=models.CharField(choices=[('xxsmall', 'XX-Small'), ('xsmall', 'X-Small'), ('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('xlarge', 'X-Large'), ('xxlarge', 'XX-Large')], default=1, max_length=10),
            preserve_default=False,
        ),
    ]

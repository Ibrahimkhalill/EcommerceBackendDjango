# Generated by Django 4.2.8 on 2024-05-22 09:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0032_rename_brand_product_brandname'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='brandName',
        ),
    ]

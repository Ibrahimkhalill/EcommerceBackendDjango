# Generated by Django 4.2.8 on 2024-05-22 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0031_brand_material_alter_product_brand'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='brand',
            new_name='brandName',
        ),
    ]
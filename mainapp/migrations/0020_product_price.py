# Generated by Django 4.2.8 on 2024-05-05 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0019_rename_product_productimage_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]

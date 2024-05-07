# Generated by Django 4.2.8 on 2024-05-04 09:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_remove_productimage_product_size_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productimage',
            name='product_size',
        ),
        migrations.AddField(
            model_name='productsize',
            name='product_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sizes', to='mainapp.productimage'),
        ),
    ]

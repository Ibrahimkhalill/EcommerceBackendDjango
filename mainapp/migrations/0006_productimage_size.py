# Generated by Django 4.2.8 on 2024-02-04 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_products_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='size',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]

# Generated by Django 4.2.8 on 2024-02-04 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_products_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='color',
            field=models.CharField(max_length=200, null=True),
        ),
    ]

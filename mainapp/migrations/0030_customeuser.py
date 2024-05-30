# Generated by Django 4.2.8 on 2024-05-19 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0029_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomeUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone_number', models.CharField(blank=True, max_length=11, null=True)),
            ],
        ),
    ]
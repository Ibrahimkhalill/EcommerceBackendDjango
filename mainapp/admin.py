from django import forms
from django.contrib import admin

# Register your models here.
from .models import Videos,Question





admin.site.register(Question)
admin.site.register(Videos)


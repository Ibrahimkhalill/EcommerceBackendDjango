from django import forms
from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Category)
admin.site.register(SubCategory)
# admin.site.register(ProductSubCategory)
admin.site.register(DisplayMarketing)
# admin.site.register(Products)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAdress)
admin.site.register(FeedBackUser)
admin.site.register(IssueUserEcommerce)
admin.site.register(Size)
admin.site.register(Color)
admin.site.register(Variant)
admin.site.register(WatchListProduct)
admin.site.register(QuestionAnswer)
admin.site.register(DeliveryFee)
admin.site.register(Status)
admin.site.register(OTP)
admin.site.register(CustomeUser)
admin.site.register(Brand)
admin.site.register(ProductImage)
admin.site.register(Material)
admin.site.register(Stock)

from django.forms import inlineformset_factory

# class ProductImageInline(admin.TabularInline):
#     model = ProductImage
#     extra = 1  # Number of extra forms to display
    

class ProductSizeInline(admin.TabularInline):
    model = Size
    extra = 1  # Number of extra forms to display
   
class ProductVariantInline(admin.TabularInline):
    model = Variant
    extra = 1  # Number of extra forms to display
   

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariantInline]

admin.site.register(Product, ProductAdmin)
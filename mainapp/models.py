from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.html import format_html
from django.db import transaction
from django.utils import timezone
from pytz import timezone as tz

from cloudinary.models import CloudinaryField
# Create your models here


class OTP(models.Model):
    email = models.EmailField(null=True, blank=True)
    otp = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)  # Track attempts

    def __str__(self):
        return f'OTP for {self.email}: {self.otp}'
	
    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Delete existing OTPs for the same email
            OTP.objects.filter(email=self.email).delete()
            super().save(*args, **kwargs)

class CustomeUser(models.Model):
	username = models.CharField(max_length=100, blank=True, null=True)
	email = models.EmailField(null=True, blank=True)
	phone_number = models.CharField(max_length=11, null=True, blank=True)
	def __str__(self):
		return self.username

class Category(models.Model):
	category_name = models.TextField(null=True, blank=True)
	icons =  CloudinaryField('icons',null=True,blank=True)

	def __str__(self):
		return self.category_name
class SubCategory(models.Model):
	category =   models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True,related_name='subcategories')
	subcategory_name = models.TextField(null=True, blank=True)
	image = CloudinaryField('subcategory',null=True,blank=True)

	def	 __str__(self):
		return self.subcategory_name

class Brand(models.Model):
	name = models.CharField(max_length=200, blank=True, null=True)

	def __str__(self):
		return self.name


class Material(models.Model):
	name = models.CharField(max_length=200, blank=True, null=True)

	def __str__(self):
		return self.name


class Product(models.Model):
    Product_SubCategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank =True,related_name='productsubcategories')
    name = models.TextField(null=True, blank=False)
    brand = models.ForeignKey(Brand,on_delete=models.SET_NULL, blank=True, null=True)
    material = models.ForeignKey(Material,on_delete=models.SET_NULL, blank=True, null=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    details = RichTextField(blank=True)
    discount = models.IntegerField(blank=True,null=True)
    cover_image = CloudinaryField('product_images', null=True, blank=True)
    price = models.IntegerField(blank=True,null=True)
	
    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    def __str__(self):
        return self.name
	
class ProductImage(models.Model):
    image = CloudinaryField('product_images', null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, blank=True, null=True)
    
    
    def __str__(self):
        return f"{self.color}"
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
	
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        if self.product and self.product.name:  # Check if self.product is not None and self.product.name exists
            return str(self.product.name)
        else:
            return "None"
        
class Stock(models.Model):
    variation = models.OneToOneField(Variant, related_name='stock', on_delete=models.CASCADE)
    initial_quantity = models.IntegerField(default=0)  # Total stock initially added
    sold_quantity = models.IntegerField(default=0)  # Number of items sold
    quantity = models.IntegerField(default=0)  # Current available stock
    
    def __str__(self):
          return str(self.variation.product.name)
		

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date_orderd = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        # If any order item requires shipping, return True
        orderitems = self.orderitem_set.all()
        return any(i.variant.product.digital == False for i in orderitems)

    @property
    def get_cart_total(self):
        # Calculate total amount for the order
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_order_item(self):
        # Return all order items
        return self.orderitem_set.all()

    @property
    def get_cart_items(self):
        # Return total quantity of items in the cart
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


class OrderItem(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        # Calculate total for a specific order item (quantity * price)
        if self.variant:
            return self.variant.price * self.quantity
        return 0  # Return 0 if no variant is associated

    def save(self, *args, **kwargs):
        if not self.date_added:
            dhaka_timezone = tz('Asia/Dhaka')
            self.date_added = timezone.now().astimezone(dhaka_timezone)
        super().save(*args, **kwargs)

class Status(models.Model):
	status_name = models.CharField(max_length=500,blank=True,null=True)

	def __str__(self):
		return self.status_name

class DeliveryFee(models.Model):
	address = models.CharField(max_length=500,blank=True,null=True)
	fee = models.CharField(max_length=500,blank=True,null=True)
	duration = models.CharField(max_length=500,blank=True,null=True)

	def __str__(self):
		return f"{self.address} - {self.fee}"

class ShippingAdress(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)  # Cascade to delete related Order when ShippingAddress is deleted
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=200, null=True)
    address = models.CharField(max_length=200, null=True)
    phone_number = models.CharField(max_length=11)
    date_added = models.DateTimeField(auto_now_add=True)
    delivery_fee = models.ForeignKey(DeliveryFee, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.address

    def save(self, *args, **kwargs):
        # Assign Dhaka timezone if date_added is not set
        if not self.date_added:
            dhaka_timezone = tz('Asia/Dhaka')
            self.date_added = timezone.now().astimezone(dhaka_timezone)
        super().save(*args, **kwargs)
      
class DisplayMarketing(models.Model):
	image=CloudinaryField('display',null=True,blank=True)

	
	
class FeedBackUser(models.Model):
	feddback=models.TextField(blank=True)

class IssueUserEcommerce(models.Model):
	issue_name=models.CharField(max_length = 200, blank=True)
	issue_details = models.TextField(blank=True)

	def __str__(self):
		return self.issue_name
	

class WatchListProduct(models.Model):
	user = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
	variant = models.ForeignKey(Variant,on_delete=models.CASCADE,blank=True,null=True)

	def __str__(self):
		return self.variant.product.name
	
class QuestionAnswer(models.Model):
	user = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
	product = models.ForeignKey(Product,on_delete=models.CASCADE,blank=True,null=True)
	question = models.TextField(blank=True,null=True)
	answer  = models.TextField(blank=True,null=True)
	createAt = models.DateTimeField(blank=True,null=True)

	def __str__(self):
		return f"{self.question} - {self.product.name}"

	


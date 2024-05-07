from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.utils.html import format_html

# Create your models here

class Category(models.Model):
	category_name = models.TextField(null=True, blank=True)
	icons =  models.ImageField(upload_to='icons',null=True,blank=True)

	def __str__(self):
		return self.category_name
class SubCategory(models.Model):
	category =   models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True,related_name='subcategories')
	subcategory_name = models.TextField(null=True, blank=True)
	image = models.ImageField(upload_to='subcategory',null=True,blank=True)

	def	 __str__(self):
		return self.subcategory_name


class Product(models.Model):
    Product_SubCategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank =True,related_name='productsubcategories')
    name = models.TextField(null=True, blank=False)
    brand = models.CharField(max_length=200, blank=True, null=True)
    material = models.CharField(max_length=200, blank=True, null=True)
    digital = models.BooleanField(default=False, null=True, blank=False)
    details = RichTextField(blank=True)
    discount = models.IntegerField(blank=True,null=True)
    cover_image = models.ImageField(upload_to='product_images/', null=True, blank=True)
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
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self):
        return f"{self.color.name} - {self.product.name}"
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
	
class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    image = models.ForeignKey(ProductImage, on_delete=models.SET_NULL, blank=True, null=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    price = models.IntegerField(blank=True, null=True)
    
    def __str__(self):
        return format_html(
            f"<img src='{self.image.imageURL}' width='100' height='100'> "
            f"{self.product}  - {self.size} - Quantity: {self.quantity} - Price: {self.price}"
        )
    


class Order(models.Model):
	user=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
	date_orderd=models.DateTimeField(auto_now_add=True)
	complete=models.BooleanField(default=False,null=True,blank=False)
	transaction_id=models.CharField(max_length=200,null=True)

	def __str__(self):
		return str(self.id)
		

	@property
	def shipping(self):
		shipping=False
		orderitems=self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital==False:
				shipping=True
		return shipping
	

	@property
	def get_cart_total(self):
		orderitems=self.orderitem_set.all()
		total=sum([item.get_total for item in orderitems])
		return total
	@property
	def get_cart_items(self):
		orderitems=self.orderitem_set.all()
		total=sum([item.quantity for item in orderitems])
		return total

class OrderItem(models.Model):
	variant=models.ForeignKey(Variant,on_delete=models.SET_NULL,blank=True,null=True)
	order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
	quantity=models.IntegerField(default=0,null=True,blank=True)
	date_added=models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total=self.variant.price * self.quantity
		return total
	

class ShippingAdress(models.Model):
	customer=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
	order=models.ForeignKey(Order,on_delete=models.SET_NULL,blank=True,null=True)
	name=models.CharField(max_length=200,null=True)
	address=models.CharField(max_length=200,null=True)
	division=models.CharField(max_length=200,null=True)
	district = models.CharField(max_length=50, null=True)
	upazila = models.CharField(max_length=50, null=True)
	phone_number=models.CharField(max_length=11)
	date_added=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address

class DisplayMarketing(models.Model):
	image=models.ImageField(upload_to='image',null=True,blank=True)

	def __str__(self):
		return self.image.name
	
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
		return f"{self.question} - {self.user.username}"

	


from rest_framework import serializers

from .models import *

class CategoryNameSerializer(serializers.ModelSerializer):
   
  
    class Meta:
        model = Category
        fields = ["id", "category_name"]

class SubCategorySerializer(serializers.ModelSerializer):
    category = CategoryNameSerializer()
    class Meta:
        model = SubCategory
        fields = ["id", "category", "subcategory_name","image"]
        
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
  
    class Meta:
        model = Category
        fields = ["id", "category_name", "subcategories","icons"]

class  ColorSeriaLizer(serializers.ModelSerializer):
    
    class Meta:
        model = Color
        fields = ["id","name"]
class  SizeSeriaLizer(serializers.ModelSerializer):
    
    class Meta:
        model = Color
        fields = ["id","name"]
class ProductImageSerializer(serializers.ModelSerializer):
    color = ColorSeriaLizer()
    class Meta:
        model = ProductImage
       
        fields = ["id","image","color"]
class BrandSerializer(serializers.ModelSerializer):
        class Meta:
            model = Brand
           
            fields = ["id","name"]

class MaterialSerializer(serializers.ModelSerializer):
        class Meta:
            model = Material
           
            fields = ["id","name"]
class ProductSerializer(serializers.ModelSerializer):
    Product_SubCategory = SubCategorySerializer()
    brand = BrandSerializer()
    material = MaterialSerializer()
    class Meta:
        model = Product
        fields = ['id', 'Product_SubCategory','name','brand', 'material', 'price','discount','digital','details','cover_image']   


class VariantSerializer(serializers.ModelSerializer):
    image = ProductImageSerializer()
    product = ProductSerializer()
    size = SizeSeriaLizer()
    class Meta:
        model = Variant
        fields = ["id","product","image","size","quantity","price"] 


class StockSerializer(serializers.ModelSerializer):
    variation = VariantSerializer()

    class Meta:
        model = Stock
        fields = ['id','variation','initial_quantity', 'sold_quantity', 'quantity']


class OrderItemSerializer(serializers.ModelSerializer):
    variant = VariantSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'order', 'quantity', 'date_added', 'get_total']
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'date_orderd','complete','transaction_id','get_cart_total','get_cart_items']

    get_cart_total = serializers.ReadOnlyField()
    get_cart_items = serializers.ReadOnlyField()

class DisplayMarketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = DisplayMarketing
        fields =["id","image"]


class WatchListProductSeriaLizer(serializers.ModelSerializer):
    variant = VariantSerializer()
    
    class Meta:
        model = WatchListProduct
        fields = ["id","user","variant"]
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username","email"]

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomeUser
        fields = ["id", "username","email","phone_number"]

class QuestionAnswerSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Corrected field name to 'user'
    product = ProductSerializer()
    
    class Meta:
        model = QuestionAnswer
        fields = ["id", "user","product", "question", "answer", "createAt"]
class DeliveryFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryFee
        fields = ["id", "address","fee","duration"]
class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["id", "status_name"]
class ShippingAddressSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    order = OrderSerializer()
    order_items = serializers.SerializerMethodField()
    delivery_fee = DeliveryFeeSerializer()
    status = StatusSerializer()

    class Meta:
        model = ShippingAdress
        fields = ["id", "customer", "order", "status", "name", "address", "phone_number", "delivery_fee","order_items","date_added"]

    def get_order_items(self, obj):
        order_items = OrderItem.objects.filter(order=obj.order)
        serializer = OrderItemSerializer(order_items, many=True)
        return serializer.data

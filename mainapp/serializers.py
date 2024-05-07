from rest_framework import serializers

from .models import *



class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ["id", "subcategory_name","image"]
        
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
        # fields = ["id","product", "color","image"]
        fields = ["id","image","color"]



class ProductSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Product
        fields = ['id', 'Product_SubCategory','name','brand', 'material', 'price', 'digital','details','cover_image']   


class VariantSerializer(serializers.ModelSerializer):
    image = ProductImageSerializer()
    product = ProductSerializer()
    size = SizeSeriaLizer()
    class Meta:
        model = Variant
        fields = ["id","product","image","size","quantity","price"] 

class OrderItemSerializer(serializers.ModelSerializer):
    variant = VariantSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'order', 'quantity', 'date_added', 'get_total']
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'date_orderd','get_cart_total','get_cart_items']

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
        fields = ["id", "username"]

class QuestionAnswerSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Corrected field name to 'user'
    
    class Meta:
        model = QuestionAnswer
        fields = ["id", "user","product", "question", "answer", "createAt"]
        
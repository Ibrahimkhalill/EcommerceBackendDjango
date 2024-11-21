from django.shortcuts import render
import pprint
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from mainapp.models import Product, Order, OrderItem
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import IntegrityError
from mainapp.serializers import *
from mainapp.models import ShippingAdress
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from random import shuffle
User=get_user_model()
from django.core.mail import send_mail
# from .OtpGenarator import generate_otp
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
# Create your views here.
import logging

logger = logging.getLogger(__name__)


from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

@api_view(['POST'])
def save_product(request):
    data = request.data
    files = request.FILES  # Get files from the request
    image_file = files.get('image_0')
    discount = data.get('discount')
    
    try:
        # Retrieve form data
        material_id = data.get('material')
        brand_id = data.get('brand')
        subcategory = SubCategory.objects.get(pk=data.get('subcategory'))
       

        # Create product instance
        product = Product(
            Product_SubCategory=subcategory,
            name=data.get('product_name'),
            details=data.get('description'),
            cover_image=image_file
        )
        product.save()

        if  discount or discount != "":
                product.discount = discount
                product.save()

        if brand_id:
            try:
                brand = Brand.objects.get(pk=brand_id)
                product.brand = brand
                product.save()
            except Brand.DoesNotExist:
                # Handle case where the brand does not exist, if needed
                pass

        if material_id:
            try:
                material = Material.objects.get(pk=material_id)
                product.material = material
                product.save()
            except Material.DoesNotExist:
                # Handle case where the material does not exist, if needed
                pass


        # Process variations
        variations = data.get('variations')
        if variations:
            variations = json.loads(variations)  # Parse the JSON variations data
            
            for index, item in enumerate(variations):
                color = Color.objects.get(name=item.get('color'))

                # Retrieve the image file from request.FILES
                image_file_key = f'image_{index}'
                image_file = files.get(image_file_key)
                
                if image_file:
                    # Save the product image
                    product_image = ProductImage(image=image_file, color=color)
                    product_image.save()

                    print("product_image",product_image)

                    # Process sizes for this variation
                    for size_item in item.get('size'):
                        size = Size.objects.get(name=size_item.get('size'))
                        quantity = size_item.get('quantity')
                        variation_price = size_item.get('price')

                        # Save the variant data
                        variant = Variant(
                            product=product,
                            image=product_image,
                            size=size,
                            quantity=quantity
                            
                        )
                        
                        if variation_price:
                            variant.price = variation_price
                       
                        variant.save()

                        # Save the stock for each variant
                        stock = Stock(
                            variation=variant,
                            initial_quantity=quantity,  # Set initial stock
                            sold_quantity=0,            # Initially no items sold
                            quantity=quantity           # Available stock initially matches initial quantity
                        )
                        stock.save()

        return Response({"status": "Product and stock saved successfully"})

    except Exception as e:
        print(f"Error occurred: {e}")
        return Response({"error": str(e)}, status=400)



@api_view(['PUT'])
def update_product(request, id):
    data = request.data
    files = request.FILES  # Get files from the request
    image_file = files.get('image_0')
    discount = data.get('discount')
    print("discount", discount)
    
    try:
        product = get_object_or_404(Product, pk=id)
        
        # Retrieve form data
        material_id = data.get('material')
        brand_id = data.get('brand')
        subcategory = SubCategory.objects.get(pk=data.get('subcategory'))

        print("subcategory", subcategory)

        # Update product fields
        product.Product_SubCategory = subcategory  # Remove trailing comma
        product.name = data.get('product_name')
        product.details = data.get('description')

        product.save()
        if  discount or discount != "":
                product.discount = discount
                product.save()
        # Set brand if provided
        if brand_id:
            try:
                brand = Brand.objects.get(pk=brand_id)
                product.brand = brand
                product.save()
            except Brand.DoesNotExist:
                pass  # Handle non-existent brand if needed

        # Set material if provided
        if material_id:
            try:
                material = Material.objects.get(pk=material_id)
                product.material = material
                product.save()
            except Material.DoesNotExist:
                pass  # Handle non-existent material if needed

        # Process variations
        variations = data.get('variations')
        if variations:
            variations = json.loads(variations)  # Parse JSON variations data
            
            for index, item in enumerate(variations):
                color = Color.objects.get(name=item.get('color'))
                image_file_key = f'image_{index}'
                image_file = files.get(image_file_key)

                # Check if image file is provided and save product image if so
                if image_file:
                    product_image = ProductImage(image=image_file, color=color)
                    product_image.save()
                    print("product_image", product_image)

                    # Process sizes for this variation
                    for size_item in item.get('size'):
                        size = Size.objects.get(name=size_item.get('size'))
                        quantity = size_item.get('quantity')
                        variation_price = size_item.get('price')
                        print("item",item)

                        # Get or create variant
                        variant, created = Variant.objects.get_or_create(
                            id= size_item.id
                        )
                        variant.image = product_image
                        variant.quantity = quantity
                        variant.price = variation_price 
                        variant.save()

                        # Update stock
                        stock, created = Stock.objects.get_or_create(variation=variant)
                        stock.initial_quantity = quantity
                        stock.quantity = quantity - stock.sold_quantity if stock.sold_quantity > 0 else quantity
                        stock.save()
                else:
                    # Process sizes without images
                    for size_item in item.get('size'):
                        size = Size.objects.get(name=size_item.get('size'))
                        quantity = size_item.get('quantity')
                        variation_price = size_item.get('price')
                        print("item",item)

                        # Get or create variant without image
                        variant, created = Variant.objects.get_or_create(
                            id= size_item.get("id")
                        )
                        variant.quantity = quantity
                        variant.price = variation_price 
                        variant.save()

                        # Update stock
                        stock, created = Stock.objects.get_or_create(variation=variant)
                        stock.initial_quantity = quantity
                        stock.quantity = quantity - stock.sold_quantity if stock.sold_quantity > 0 else quantity
                        stock.save()

        return Response({"status": "Product and stock saved successfully"})

    except Exception as e:
        print(f"Error occurred: {e}")
        return Response({"error": str(e)}, status=400)


@api_view(['DELETE'])
def delete_product(request, id):
    try:
        instance = Product.objects.get(pk=id)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_Stock(request, id):
    try:
        instance = Stock.objects.get(pk=id)
    except Stock.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    instance.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['DELETE'])
def delete_variation(request, id):
    try:
        instance = Variant.objects.get(pk=id)
        check_image_id = Variant.objects.filter(image =instance.image).count()
        stock = Stock.objects.get(variation = instance)
        print(check_image_id)
        if check_image_id > 1:
              stock.delete()
              instance.delete()
              return Response({'message': 'Subcategory and associated image deleted successfully'}, status=status.HTTP_200_OK)

        else:
            image_url = str(instance.image.image)
            public_id = image_url.split('/')[-1].split('.')[0]  # Adjust this if your public_id has a specific format
            # Delete from Cloudinary
            cloudinary_response = cloudinary.uploader.destroy(public_id)
            if cloudinary_response.get("result") == "ok":
                # Delete the record from your database
                stock.delete()
                instance.delete()
                return Response({'message': 'Subcategory and associated image deleted successfully'}, status=status.HTTP_200_OK)
    except Variant.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def delete_order(request, id):
    try:
        # Get the ShippingAddress instance by the provided id
        shipping_address = ShippingAdress.objects.get(pk=id)
        
        # Get the associated Order if exists
        order = shipping_address.order
       
        # Delete the ShippingAddress instance
        shipping_address.delete()

        # If the order exists, delete the associated Order
        

        return Response(status=status.HTTP_200_OK)
    except ShippingAdress.DoesNotExist:
        return Response({'detail': 'ShippingAddress not found'}, status=status.HTTP_404_NOT_FOUND)





@api_view(["GET"])
def get_order_details(request):
        if request.method == 'GET':
            questionAnswer = ShippingAdress.objects.all()
            question = ShippingAddressSerializer(questionAnswer, many=True)
            return Response(question.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})

@api_view(["GET"])
def get_stock(request):
        stock = Stock.objects.all()
        stock_serializer = StockSerializer(stock, many=True)
        return Response(stock_serializer.data, status=status.HTTP_200_OK)
    
@api_view(["GET"])
def get_product_all(request):
        products = Product.objects.all()
        varinat = Variant.objects.all()
        
        # Convert products to a list and shuffle it
       
        product_serializer = ProductSerializer(products, many=True)
        variant_serilizer = VariantSerializer(varinat, many=True)
        response_data = {
            'products': product_serializer.data,
            "variant": variant_serilizer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_product_by_id(request,id):
        products = get_object_or_404(Product, pk=id)
        variant = Variant.objects.filter(product= products)
        product_serializer = ProductSerializer(products)
        variant_serilizer = VariantSerializer(variant, many=True)
        response_data = {
            'product': product_serializer.data,
            "variant": variant_serilizer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_all(request):
        brnad = Brand.objects.all()
        category = Category.objects.all()
        material = Material.objects.all()
        # Convert products to a list and shuffle it
       
        brand_serializer = BrandSerializer(brnad, many=True)
        category_serilizer = CategorySerializer(category, many=True)
        material_serilizer = MaterialSerializer(material, many=True)
        response_data = {
            'brand': brand_serializer.data,
            "category": category_serilizer.data,
            "material": material_serilizer.data

        }

        return Response(response_data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_status(request):
        if request.method == 'GET':
            data = Status.objects.all()
            status_serializer = StatusSerializer(data, many=True)
            return Response(status_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})
@api_view(["GET"])
def get_category(request):
        if request.method == 'GET':
            data = Category.objects.all()
            category_serializer = CategorySerializer(data, many=True)
            return Response(category_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})

@csrf_exempt
@api_view(['POST'])
def saveCategory(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            category_name = data.get('category_name')  
            
            if category_name:
                category = Category(category_name=category_name)
                category.save()
                return JsonResponse({'message': 'Category saved successfully'}, status=201)
            else:
                return JsonResponse({'message': 'Invalid data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Error saving category', 'error': str(e)}, status=400)
        
@csrf_exempt
@api_view(['PUT'])
def update_category(request):
    try:
        data = json.loads(request.body)  
        category_name = data.get('category_name')  
        id = data.get('id')  
        
        if category_name:
            category = Category.objects.get(pk=id)
            category.category_name = category_name
            category.save()
            return JsonResponse({'message': 'Category Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Update category', 'error': str(e)}, status=400)
    

@api_view(['DELETE'])
def delete_category(request, id):
    try:
        instance = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_200_OK)

@api_view(["GET"])
def get_subCategory(request):
        if request.method == 'GET':
            data = SubCategory.objects.all()
            category_serializer = SubCategorySerializer(data, many=True)
            return Response(category_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})

@csrf_exempt
@api_view(['POST'])
def saveSubCategory(request):
    if request.method == 'POST':
        try:
        
            category_name = request.data.get('category_name')
            subcategory_name = request.data.get('subcategory_name')
            image = request.FILES.get('image')
            if not all([category_name, subcategory_name, image]):
                return JsonResponse({'message': 'Missing required fields'}, status=400)
            try:
                category = Category.objects.get(category_name=category_name)
            except Category.DoesNotExist:
                return JsonResponse({'message': 'Category does not exist'}, status=404)
            subcategory = SubCategory(
                category=category,
                subcategory_name=subcategory_name,
                image=image
            )
            subcategory.save()

            return JsonResponse({'message': 'SubCategory saved successfully'}, status=201)
        except Exception as e:
            return JsonResponse({'message': 'Error saving SubCategory', 'error': str(e)}, status=400)


@csrf_exempt
@api_view(['PUT'])
def update_subcategory(request):
    try:
       
        category_name = request.data.get('category_name')  
        subcategory_name = request.data.get('subcategory_name')
        image = request.data.get("image")  
        id = request.data.get('id') 
       

        category = Category.objects.get(category_name=category_name)
        print(category)
        if category:
            subcategory = SubCategory.objects.get(pk=id)
            subcategory.category = category
            subcategory.subcategory_name = subcategory_name
            subcategory.image = image
            subcategory.save()
            return JsonResponse({'message': 'Sub Category Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Sub Update category', 'error': str(e)}, status=400)
    
@api_view(['DELETE'])
def delete_subcategory(request, id):
    try:
        instance = SubCategory.objects.get(pk=id)
        image_url = str(instance.image)
        public_id = image_url.split('/')[-1].split('.')[0]  # Adjust this if your public_id has a specific format

        # Delete from Cloudinary
        cloudinary_response = cloudinary.uploader.destroy(public_id)

        if cloudinary_response.get("result") == "ok":
            # Delete the record from your database
            instance.delete()
            return Response({'message': 'Subcategory and associated image deleted successfully'}, status=status.HTTP_200_OK)
    except SubCategory.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

   
   



@api_view(["GET"])
def get_brand(request):
        if request.method == 'GET':
            data = Brand.objects.all()
            brand_serializer = BrandSerializer(data, many=True)
            return Response(brand_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})



@csrf_exempt
@api_view(['POST'])
def saveBrand(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            name = data.get('brand_name')  
            
            if name:
                brand = Brand(name=name)
                brand.save()
                return JsonResponse({'message': 'Brand saved successfully'}, status=201)
            else:
                return JsonResponse({'message': 'Invalid data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Error saving brand', 'error': str(e)}, status=400)

@csrf_exempt
@api_view(['PUT'])
def update_brand(request):
    try:
        data = json.loads(request.body)  
        name = data.get('brand_name')  
        id = data.get('id')  
        
        if id:
            brand = Brand.objects.get(pk=id)
            brand.name = name
            brand.save()
            return JsonResponse({'message': 'Brand Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Update Brand', 'error': str(e)}, status=400)

@api_view(['DELETE'])
def delete_brand(request, id):
    try:
        instance = Brand.objects.get(pk=id)
    except Brand.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_200_OK)


# material
@api_view(["GET"])
def get_material(request):
        if request.method == 'GET':
            data = Material.objects.all()
            material_serializer = MaterialSerializer(data, many=True)
            return Response(material_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})



@csrf_exempt
@api_view(['POST'])
def saveMaterial(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            name = data.get('material_name')  
            
            if name:
                brand = Material(name=name)
                brand.save()
                return JsonResponse({'message': 'Material saved successfully'}, status=201)
            else:
                return JsonResponse({'message': 'Invalid data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Error saving Material', 'error': str(e)}, status=400)

@csrf_exempt
@api_view(['PUT'])
def update_material(request):
    try:
        data = json.loads(request.body)  
        name = data.get('material_name')  
        id = data.get('id')  
        
        if id:
            brand = Material.objects.get(pk=id)
            brand.name = name
            brand.save()
            return JsonResponse({'message': 'Material Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Update Material', 'error': str(e)}, status=400)


@api_view(['DELETE'])
def delete_material(request, id):
    try:
        instance = Material.objects.get(pk=id)
    except Material.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_200_OK)



#color
@api_view(["GET"])
def get_color(request):
        if request.method == 'GET':
            data = Color.objects.all()
            color_serializer = ColorSeriaLizer(data, many=True)
            return Response(color_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})


@csrf_exempt
@api_view(['POST'])
def saveColor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            name = data.get('color_name')  
            
            if name:
                brand = Color(name=name)
                brand.save()
                return JsonResponse({'message': 'Color saved successfully'}, status=201)
            else:
                return JsonResponse({'message': 'Invalid data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Error saving Color', 'error': str(e)}, status=400)




@csrf_exempt
@api_view(['PUT'])
def update_color(request):
    try:
        data = json.loads(request.body)  
        name = data.get('color_name')  
        id = data.get('id')  
        
        if id:
            brand = Color.objects.get(pk=id)
            brand.name = name
            brand.save()
            return JsonResponse({'message': 'Color Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Update Color', 'error': str(e)}, status=400)


@api_view(['DELETE'])
def delete_color(request, id):
    try:
        instance = Color.objects.get(pk=id)
    except Color.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_200_OK)


#size
@api_view(["GET"])
def get_size(request):
        if request.method == 'GET':
            data = Size.objects.all()
            size_serializer = SizeSeriaLizer(data, many=True)
            return Response(size_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})


@csrf_exempt
@api_view(['POST'])
def saveSize(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  
            name = data.get('size_name')  
            
            if name:
                brand = Size(name=name)
                brand.save()
                return JsonResponse({'message': 'Size saved successfully'}, status=201)
            else:
                return JsonResponse({'message': 'Invalid data'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': 'Error saving Size', 'error': str(e)}, status=400)




@csrf_exempt
@api_view(['PUT'])
def update_Size(request):
    try:
        data = json.loads(request.body)  
        name = data.get('size_name')  
        id = data.get('id')  
        
        if id:
            brand = Size.objects.get(pk=id)
            brand.name = name
            brand.save()
            return JsonResponse({'message': 'Size Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Update Size', 'error': str(e)}, status=400)


@api_view(['DELETE'])
def delete_size(request, id):
    try:
        instance = Size.objects.get(pk=id)
    except Size.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_200_OK)



#question & answer 
@api_view(["GET"])
def get_question_answer(request):
        if request.method == 'GET':
            data = QuestionAnswer.objects.all()
            questionAnswer_serializer = QuestionAnswerSerializer(data, many=True)
            return Response(questionAnswer_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})



@csrf_exempt
@api_view(['PUT'])
def update_question_answer(request):
    try:
        data = json.loads(request.body)  
        answer = data.get('answer')  
        id = data.get('id')  
        
        if id:
            q_answer = QuestionAnswer.objects.get(pk=id)
            q_answer.answer = answer
            q_answer.save()
            return JsonResponse({'message': 'Answer Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Update Answer', 'error': str(e)}, status=400)


@api_view(['DELETE'])
def delete_question_answer(request, id):
    try:
        instance = QuestionAnswer.objects.get(pk=id)
    except QuestionAnswer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_200_OK)




@api_view(["PUT"])
def status_change(request):
    if request.method == 'PUT':
        status_name = request.data.get("status_id")
        id = request.data.get("id")
        try:
            status_id = Status.objects.get(pk=status_name)
            shipping = ShippingAdress.objects.get(pk=id)
            shipping.status = status_id
            shipping.save()
            shipping_serilzer = ShippingAddressSerializer(shipping)
    
            return Response(shipping_serilzer.data, status=status.HTTP_200_OK)
        except Status.DoesNotExist:
            return Response({"error": "Status not found"}, status=status.HTTP_404_NOT_FOUND)
        except ShippingAdress.DoesNotExist:
            return Response({"error": "Shipping address not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def search_transaction(request):
    if request.method == 'POST':
        transaction_id = request.data.get("transaction_id", None)
        
        if not transaction_id:
            return Response({"error": "transaction_id is required"}, status=status.HTTP_400_BAD_REQUEST)
       
        try:
            # Fetch the order by transaction_id
            order = Order.objects.get(transaction_id=transaction_id)

            # Fetch the shipping address related to the order
            shipping_address = ShippingAdress.objects.filter(order=order)

            if not shipping_address.exists():
                return Response({"error": "Shipping address not found"}, status=status.HTTP_404_NOT_FOUND)

            # Serialize the shipping address data
            shipping_serializer = ShippingAddressSerializer(shipping_address, many=True)
            return Response(shipping_serializer.data, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
from django.db.models import Sum
from datetime import date




def sales_summary(request):
    total = Stock.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    today = date.today()

    # Today's orders
    today_orders = ShippingAdress.objects.filter(date_added__date=today).count()

    # Today's sales (total amount of completed orders today)
    today_sales = sum(
        order.get_cart_total for order in Order.objects.filter(date_orderd__date=today, complete=True)
    )

    # Total sales (total amount of all completed orders)
    total_sales = sum(
        order.get_cart_total for order in Order.objects.filter(complete=True)
    )

    # Construct the response
    response_data = {
        "today_orders": today_orders,
         "today_sales": f"{today_sales:,.1f}",  # Formats as "1,000.00" or "1,00,000.00"
        "total_sales": f"{total_sales:,.1f}",  # Formats as "1,000.00" or "1,00,000.00
        "available_product": total
    }

    return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)


# display slider 

@api_view(["GET"])
def get_display_slider(request):
        if request.method == 'GET':
            data = DisplayMarketing.objects.all()
            display_serializer = DisplayMarketingSerializer(data, many=True)
            return Response(display_serializer.data, status=status.HTTP_200_OK)
        return Response({'message', "Method Not Allow"})


from PIL import Image

@api_view(['POST'])
def saveDisplaySlider(request):
    try:
        image = request.FILES.get('image')
        if not image:
            return Response({'message': 'No image provided'}, status=400)
        
        # Validate image format
        try:
            img = Image.open(image)
            img.verify()
        except Exception:
            return Response({'message': 'Invalid image format'}, status=400)

        display = DisplayMarketing(image=image)
        display.save()

        return Response({'message': 'Display Slider saved successfully'}, status=201)
    except Exception as e:
        logger.error("Error saving Display Slider: %s", str(e))
        return Response({'message': 'Error saving Display Slider', 'error': str(e)}, status=400)

@csrf_exempt
@api_view(['PUT'])
def update_material(request):
    try:
        data = json.loads(request.body)  
        name = data.get('material_name')  
        id = data.get('id')  
        
        if id:
            brand = Material.objects.get(pk=id)
            brand.name = name
            brand.save()
            return JsonResponse({'message': 'Material Update successfully'}, status=201)
        else:
            return JsonResponse({'message': 'Invalid data'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'message': 'Error Update Material', 'error': str(e)}, status=400)

import cloudinary.uploader

@api_view(['DELETE'])
def deleteDisplaySlider(request, id):
    try:
        # Fetch the display record from your database
        display = DisplayMarketing.objects.get(pk=id)
        
        # Extract Cloudinary public_id from the image URL
        # Assuming the image URL is stored in the database
        if not display.image:
            return Response({'message': 'No image associated with this record'}, status=400)

        # Extract public_id from Cloudinary URL
        image_url = str(display.image)
        public_id = image_url.split('/')[-1].split('.')[0]  # Adjust this if your public_id has a specific format

        # Delete from Cloudinary
        cloudinary_response = cloudinary.uploader.destroy(public_id)

        if cloudinary_response.get("result") == "ok":
            # Delete the record from your database
            display.delete()
            return Response({'message': 'Display Slider and associated image deleted successfully'}, status=200)
        else:
            return Response({'message': 'Failed to delete image from Cloudinary'}, status=400)

    except DisplayMarketing.DoesNotExist:
        return Response({'message': 'Record not found'}, status=404)
    except Exception as e:
        logger.error("Error deleting Display Slider: %s", str(e))
        return Response({'message': 'Error deleting Display Slider', 'error': str(e)}, status=400)
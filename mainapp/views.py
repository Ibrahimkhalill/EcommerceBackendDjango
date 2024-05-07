import datetime
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.http import JsonResponse
import json
from .models import Product, Order, OrderItem
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
from .serializers import *
from .models import ShippingAdress
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from random import shuffle
User=get_user_model()


@api_view(['POST'])
def signup_view(request):
    if request.method == 'POST':
        # Use request.data to parse JSON data
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            # Use create_user to create a new user with hashed password
            user = User.objects.create_user(username=username, email=email, password=password)

            # Check if user creation was successful
            if user:
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User registration failed'}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({'message': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        



@api_view(['POST'])
def google_signup(request):
    if request.method == 'POST':
        username = request.data.get('username')
        email = request.data.get('email')
        
        try:
        
            user = User.objects.create_user(username=username, email=email)

            if user:
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User registration failed'}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError:
            return Response({'message': 'Username or email already exists'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            print(user)
            django_login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            print()
            return JsonResponse({'token': token.key, 'username': username}, status=201)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def goole_login_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        print(username)
        
        users = User.objects.filter(username=username)
        
        if users.exists():  # Check if there are any users in the queryset
            user = users.first()  # Get the first user from the queryset
            django_login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key, 'username': username})
        else:
            return Response({'message': 'Invalid credentials'}, status=401)

@csrf_exempt
@api_view(['POST'])
def logout_view(request):
    # Perform logout operation
    logout(request)
    
    return JsonResponse({'message': 'Logout successful'})
@api_view(['GET'])
def get_products(request):
    if request.method == 'GET':
        products = Product.objects.all()
        varinat = Variant.objects.all()
        
        # Convert products to a list and shuffle it
        shuffled_products = list(products)
        shuffle(shuffled_products)

        product_serializer = ProductSerializer(shuffled_products, many=True)
        variant_serilizer = VariantSerializer(varinat, many=True)

        response_data = {
            'products': product_serializer.data,
            "variant": variant_serilizer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def get_product_subcategory(request):
#     if request.method == 'GET':
#         products = ProductSubCategory.objects.all()
        
#         # Convert products to a list and shuffle it
       
#         product_serializer = ProductSubCategorySerializer(products, many=True)

#         response_data = {
#             'products': product_serializer.data,
#         }

#         return Response(response_data, status=status.HTTP_200_OK)
@api_view(['GET'])
def get_product_image(request):
    if request.method == 'GET':
        products = ProductImage.objects.all()
        
        # Convert products to a list and shuffle it
       
        product_serializer = ProductImageSerializer(products, many=True)

        response_data = {
            'ProductImages': product_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
from random import shuffle, sample

@api_view(['GET'])
def get_subcategory(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        subcategories = SubCategory.objects.all()

        # Shuffle the subcategories
        # shuffled_subcategories = list(subcategories)
        # shuffle(shuffled_subcategories)

        # # Get a random subset of 22 subcategories
        # selected_subcategories = sample(shuffled_subcategories, k=22)

        # Serialize the selected subcategories
        subcategory_serializer = SubCategorySerializer(subcategories, many=True)
        category_serializer = CategorySerializer(categories, many=True)

        response_data = {
            'categories': category_serializer.data,
            'subcategory': subcategory_serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
@api_view(['GET'])
def get_displaymarketing(request):
    if request.method == 'GET':
        categories = DisplayMarketing.objects.all()
        category_serializer = DisplayMarketingSerializer(categories, many=True)

        response_data = {
            'display': category_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])  
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])     
def cart(request):
    try:
        data = request.user
        user = User.objects.get(username=data)
        if user is not None:
            order, created = Order.objects.get_or_create(user=user, complete=False)
            items = order.orderitem_set.all()
            
            item_serializer = OrderItemSerializer(items, many=True)
            serialized_items = item_serializer.data
            
            order_serializer = OrderSerializer(order)
            serialized_order = order_serializer.data
            response_data = {            
                'items': serialized_items,
                'carttotal': serialized_order['get_cart_total'],
                'cartItems': serialized_order['get_cart_items'],
            }
            return Response(response_data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'message': 'User not available'}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
@api_view(['POST'])  
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])   
def update_item(request):
    
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("data",data)
            variantId = data['variantId']
            action = data['action']
            count = data['count']
            print(action)
            user = request.user
               
            product = Variant.objects.get(id=variantId)
            
            order, created = Order.objects.get_or_create(user=user,complete=False)

            orderItem, created = OrderItem.objects.get_or_create(order=order, variant=product)

            if action == 'add':
                orderItem.quantity = (orderItem.quantity + count)
                print("add",orderItem.quantity)
            elif action == 'remove':
                orderItem.quantity = (orderItem.quantity - count)

            orderItem.save()

            if orderItem.quantity <= 0:
                orderItem.delete()
            order_serializer = OrderSerializer(order)
            serialized_order = order_serializer.data
            response_data = {            
                
                'cartItems': serialized_order['get_cart_items'],
            }
            return JsonResponse(response_data,status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return JsonResponse('Product does not exist', status=400, safe=False)
        except json.JSONDecodeError:
           
            return JsonResponse('Invalid JSON data', status=400, safe=False)
        
from django.http import Http404
@api_view(['GET'])
def get_product_id(request, id):
    if request.method == 'GET':
        product = get_object_or_404(Product, id=id)
    
        variant =  Variant.objects.filter(product=product)
        
        product_serializer = ProductSerializer(product)
        print(product_serializer)
        variant_serilizer = VariantSerializer(variant, many=True)
        
        # Assuming you want to filter order items by each variant
        order_items = []
        for var in variant:
            items = OrderItem.objects.filter(variant=var)
            print(items)
            if items.exists():
                order_items.append(items.first())  # Get the first item if it exists
            else:
                order_items.append(None)  # Append None if no item exists for the variant

        product_data = product_serializer.data
        response_data = {
            'order_items': [OrderItemSerializer(item).data if item else None for item in order_items],
            'product': product_data,
            'variants': variant_serilizer.data
    }

        return Response(response_data, status=status.HTTP_200_OK)
        
            # Handle the case where the user doesn't exist
       

@csrf_exempt
@api_view(['POST'])  
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])   
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = request.body.decode('utf-8')
    data_dict = json.loads(data)
    
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(user=customer, complete=False)

        total = float(data_dict['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAdress.objects.create(
                customer=customer,
                order=order,
                name=data_dict['name'],
                address=data_dict['address'],
                division=data_dict['division'],
                district=data_dict['district'],
                upazila =data_dict['upazila'],
                phone_number=data_dict['number'],
            )
            return Response("Order is Sucessfully placed")
        
    else:
        print('User is not logged in.')

    return JsonResponse('Payment submitted..', safe=False)
@api_view(['POST'])
def itemSearch(request):
    try:
        if request.method == 'POST':
            query = json.loads(request.body.decode('utf-8'))
            results = Product.objects.filter(Q(name__icontains=query))
            serialized_data = ProductSerializer(results, many=True).data
            if len(serialized_data) == 0:
                context = {
                    "results": 0
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                context = {
                    'results': serialized_data
                }
                return Response(context, status=status.HTTP_200_OK)
    except Exception:
      
        return Response({"message": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def get_subcategory_product(request):
    try:
        subcategory_id = json.loads(request.body.decode('utf-8'))
       
        try: 
            productsub = SubCategory.objects.filter(pk=subcategory_id)
          
            results = Product.objects.filter(Product_SubCategory__in=productsub)
        
            serialized_data = ProductSerializer(results, many=True).data
      
            context = {"results": serialized_data}
            return Response(context, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
           
            return Response({"message": "Subcategory not found"}, status=status.HTTP_404_NOT_FOUND)

    except json.JSONDecodeError:
       
        return Response({"message": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        
        print(f"An error occurred: {e}")
        return Response({"message": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def save_feedback(request):
    try:
        if request.method =="POST":
            data = json.loads(request.body.decode('utf-8'))
            feedback = data['feedback']
            
            result = FeedBackUser(feddback=feedback)
            result.save()

            return Response("We have received & saved your report. Thank you for your feedback!",status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"An error occurred: {str(e)}"})

@api_view(['POST'])
def save_issue(request):
    try:
        if request.method =="POST":
            data = json.loads(request.body.decode('utf-8'))
            issue_name = data['issue_name']
            issue_details = data['issue_details']
            print(issue_details)
            result = IssueUserEcommerce(issue_name=issue_name,issue_details=issue_details)
            result.save()

            return Response("We have received & saved your report. Thank you for your feedback!",status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": f"An error occurred: {str(e)}"})
    
from rest_framework import generics

# @api_view(['GET', 'POST'])
# def product_list_create_view(request):
#     if request.method == 'GET':
#         products = Products.objects.all()
#         serializer = ProductSerializer(products, many=True)
#         return Response(serializer.data)

#     elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_order_item(request, id):
    try:
        instance = OrderItem.objects.get(pk=id)
    except OrderItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@csrf_exempt
@api_view(['POST'])  
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def SaveWatchlistProduct(request):
    try:
        if request.method == "POST":
            
            data = request.user
            user = User.objects.get(username=data)
            data = json.loads(request.body.decode('utf-8'))
            variant = Variant.objects.get(pk=data['variantId'])
            try:
                wishlist_item = WatchListProduct.objects.get(user=user, variant=variant)
                wishlist_item.delete()
                return Response("Product removed from your wishlist", status=status.HTTP_200_OK)
            except WatchListProduct.DoesNotExist:
                wishlist_item = WatchListProduct(user=user, variant=variant)
                wishlist_item.save()
                return Response("Product added to your wishlist", status=status.HTTP_201_CREATED)

        return Response(status= status.HTTP_405_METHOD_NOT_ALLOWED)
            
            
    except Variant.DoesNotExist:
        return Response("Variant does not exist", status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("An error occurred:", str(e))  # Debugging
        return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def getWishlistProduct(request):
    if request.method == 'GET':
        wishlist = WatchListProduct.objects.all()
        wishlistSerializer = WatchListProductSeriaLizer(wishlist, many=True)
        return Response(wishlistSerializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def getQuestionAnswer(request):
    if request.method == 'GET':
        questionAnswer = QuestionAnswer.objects.all()
        question = QuestionAnswerSerializer(questionAnswer, many=True)
        return Response(question.data, status=status.HTTP_200_OK)



@csrf_exempt
@api_view(['POST'])  
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def SaveQuestionAnswer(request):
    try:
        if request.method == "POST":
            
            data = request.user
            user = User.objects.get(username=data)
            data = json.loads(request.body.decode('utf-8'))
            question = data['question']
            date = data['localDateTime']
            productId = data['productId']
            product = Product.objects.get(pk = productId)
            wishlist_item = QuestionAnswer(user=user, product=product, question=question,createAt = date)
            wishlist_item.save()
            return Response(status=status.HTTP_200_OK)

        return Response(status= status.HTTP_405_METHOD_NOT_ALLOWED)
            
    except Exception as e:
        print("An error occurred:", str(e))  # Debugging
        return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
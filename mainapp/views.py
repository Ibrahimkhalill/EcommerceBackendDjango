import datetime
from django.shortcuts import get_object_or_404, render
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
from django.core.mail import send_mail
from .OtpGenarator import generate_otp
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

def index(request):
    otp = generate_otp()
    return render(request,"ForgetPasswordEmail.html",{'otp':otp})

@api_view(["POST"])
def send_otp(request):
    if request.method == 'POST':
        email = request.data.get('email')

        try:
            # Generate OTP
            otp = generate_otp()
            # Save OTP to database
            OTP.objects.create(email=email, otp=otp)
            
            # Render the HTML template
            html_content = render_to_string('otp_email_template.html', {'otp': otp, 'email':email})
            
            
            # Send email
            msg = EmailMultiAlternatives(
                subject='Your OTP Code',
                body='This is an OTP email.',
                from_email='hijabpoint374@gmail.com',  # Sender's email address
                to=[email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)  
            
            return JsonResponse({'message': 'OTP sent to your email.'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'message': 'Invalid method.'})

@api_view(["POST"])
def Password_reset_send_otp(request):
    if request.method == 'POST':
        email = request.data.get('email')
        try:

            existing_user = CustomeUser.objects.get(email=email)
            if existing_user:
                    # Generate OTP
                otp = generate_otp()
                # Save OTP to database
                OTP.objects.create(email=email, otp=otp)
                
                # Render the HTML template
                html_content = render_to_string('ForgetPasswordEmail.html', {'otp': otp, 'email':email})
            
                # Send email
                msg = EmailMultiAlternatives(
                    subject='Your OTP Code',
                    body='This is an OTP email.',
                    from_email='hijabpoint374@gmail.com',  # Sender's email address
                    to=[email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send(fail_silently=False)  
                
                return JsonResponse({'message': 'OTP sent to your email.'}, status = status.HTTP_200_OK)
                
           
        except :
                    
            return Response({'message': 'The account you provided does not exist. Please try again with another account.'}, status=status.HTTP_400_BAD_REQUEST)

      
    return JsonResponse({'message': 'Invalid method.'})

@api_view(["POST"])
def verify_otp(request):
    if request.method == 'POST':
        otp = request.data.get('otp')
        print(otp)
        try:
                otp_record = OTP.objects.get(otp=otp)
                otp_record.attempts += 1  # Increment attempt count
                otp_record.save()  # Save the updated attempt count
                if (timezone.now() - otp_record.created_at).seconds > 120:
                   
                    otp_record.delete()  # Expired OTP remove korte hobe
                    return Response({'message': ' Otp Expired'})
                else:
                   
                    otp_record.delete()  # Verified OTP remove korte hobe
                    return Response('success', status=status.HTTP_200_OK)
        except OTP.DoesNotExist:
                return Response({'message': 'Invalid Otp'}, status=status.HTTP_400_BAD_REQUEST)
           
   
    return Response("Method is not allowed")

@api_view(['POST'])
def signup_view(request):
    if request.method == 'POST':
        # Use request.data to parse JSON data
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        phone_number = request.data.get('phone_number')

        # Check if a user with the given email already exists
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            # If a user with the email exists, return an error response
            return Response({'message': 'User with this email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Use create_user to create a new user with hashed password
            user = User.objects.create_user(username=username, email=email, password=password)
            customeruser = CustomeUser(username=username, email=email, phone_number = phone_number)
            customeruser.save()
            # Check if user creation was successful
            if user:
                return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'User registration failed'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': 'User registration failed', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        



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
        email = request.data.get('username')
        password = request.data.get('password')
        try:
            user = CustomeUser.objects.get(email =email)
            print(user.username)
            # Authenticate user using email and password
            user_auth = authenticate(request, username=user.username, password=password)
       
            if user_auth is not None:
                print(user_auth)
                django_login(request, user_auth)
                token, created = Token.objects.get_or_create(user=user_auth)
                print()
                return JsonResponse({'token': token.key, 'username': user.username}, status=201)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except User.DoesNotExist:
            # User with the provided email does not exist
            return JsonResponse({'error': 'User does not exist'}, status=404)   
        
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

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def changepassword(request):
    if request.method == "POST":
        user_id =  request.user
        
        old_password = request.data.get('oldpassword')
        new_password = request.data.get('newpassword')
        
        try:
            user = User.objects.get(username=user_id)
            
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Previous password does not match"}, status=status.HTTP_400_BAD_REQUEST)
        
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return Response({'message': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def reset_password(request):
    if request.method == "POST":

        email =  request.data.get('email')
        new_password = request.data.get('newpassword')
        
        try:
            userdata = CustomeUser.objects.get(email=email)
            user = User.objects.get(username=userdata.username)
            
            if user:
                user.set_password(new_password)
                user.save()
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
           
        
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    else:
        return Response({'message': 'Method Not Allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
def get_brand(request):
    if request.method == 'GET':
        brand = Brand.objects.all()
        brand_serializer = BrandSerializer(brand, many=True)
        subcategories = SubCategory.objects.all()
        subcategory_serializer = SubCategorySerializer(subcategories, many=True)

        response_data = {
            'brand': brand_serializer.data,
             'subcategory': subcategory_serializer.data
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
            

            user = CustomeUser.objects.get(username = data)
            userserializer = CustomUserSerializer(user)
            item_serializer = OrderItemSerializer(items, many=True)
            serialized_items = item_serializer.data
            delivery = DeliveryFee.objects.all()
            deliverySeriazlizer = DeliveryFeeSerializer(delivery, many=True)
            order_serializer = OrderSerializer(order)
            order_status  = Status.objects.all()
            statusSerializer = StatusSerializer(order_status,many=True)
            serialized_order = order_serializer.data
           
            response_data = {            
                'items': serialized_items,
                'carttotal': serialized_order['get_cart_total'],
                'cartItems': serialized_order['get_cart_items'],
                "delivery": deliverySeriazlizer.data,
                "status": statusSerializer.data,
                "user":userserializer.data,
                
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
        user = CustomeUser.objects.get(username = customer)
        order, created = Order.objects.get_or_create(user=customer, complete=False)
        
        total = data_dict['total']
        print(total)
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()
        status_id = Status.objects.get(status_name = data_dict['status'])   
        delivery = DeliveryFee.objects.get(pk = data_dict['delivery_id'])   

        if order.shipping == True:
            ShippingAdress.objects.create(
                customer=customer,
                order=order,
                status = status_id,
                name=data_dict['name'],
                address=data_dict['address'],
                division=data_dict['division'],
                district=data_dict['district'],
                upazila =data_dict['upazila'],
                phone_number=data_dict['number'],
                delivery_fee = delivery
            )

            order_details = OrderItem.objects.filter(order = order)
            shiiping = ShippingAdress.objects.get(order=order)
            
           
            context ={
                "order_details":order_details,
                "ShippingAdress": shiiping,
                "total": total,
                
            }
            html_content = render_to_string('OrderConfirmAtion.html',context)
            
                # Send email
            msg = EmailMultiAlternatives(
                subject='Your order has been placed!',
                body='This is an OTP email.',
                from_email='hijabpoint374@gmail.com',  # Sender's email address
                to=[user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)  
            return Response("Order is Sucessfully placed and Customer center contact you!")
        
    else:
        print('User is not logged in.')

    return JsonResponse('Payment submitted..', safe=False)
@api_view(['POST'])
def itemSearch(request):
    try:
        if request.method == 'POST':
            query = json.loads(request.body.decode('utf-8'))
            results = Product.objects.filter(
    Q(name__icontains=query) | Q(brand__name__icontains=query) | Q(Product_SubCategory__subcategory_name__icontains=query)
)
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
        username = request.user
        user = User.objects.get(username =username)
        wishlist = WatchListProduct.objects.filter(user=user)
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
    

@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getShhipingAddress(request):
    if request.method == 'GET':
        username = request.user
        user = User.objects.get(username =username)
        questionAnswer = ShippingAdress.objects.filter(customer=user)
        question = ShippingAddressSerializer(questionAnswer, many=True)
        return Response(question.data, status=status.HTTP_200_OK)




@api_view(['GET'])  
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def getUserDeatils(request):
    if request.method == 'GET':
        username = request.user
        userAll = User.objects.get(username =username)
        user = UserSerializer(userAll)
        return Response(user.data, status=status.HTTP_200_OK)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
@api_view(['DELETE'])
def delete_wishlist_product(request, id):
    try:
        instance = WatchListProduct.objects.get(pk=id)
    except WatchListProduct.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    instance.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

def OrderConfirm(request):
    order = Order.objects.get(pk=4)
    
    order_details = OrderItem.objects.filter(order = 4)
    shiiping = ShippingAdress.objects.get(order= 4)
   
            
    context ={
            "order_details": order_details,
            "ShippingAdress": shiiping,
           

            
        }
    return render(request, "orderConfirmAtion.html",context)
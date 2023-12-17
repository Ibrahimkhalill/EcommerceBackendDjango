from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view,parser_classes
from .models import Videos,Question
from .serializers import VideosSerializer,QuestionSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db import IntegrityError


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
@authentication_classes([TokenAuthentication])
def login_view(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            django_login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key, 'username': username})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

@api_view(['POST'])
def logout_view(request):
    # Perform logout operation
    logout(request)
    
    return JsonResponse({'message': 'Logout successful'})


@api_view(['GET'])
def get_videos(request):
    if request.method == 'GET':
        bank_accounts = Videos.objects.all()
        serializer = VideosSerializer(bank_accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_question_with_options(request, youtube_id):
    questions = Question.objects.filter(youtubeID__youtubeID=youtube_id)

    if not questions.exists():
        return Response({"error": "Question not found"}, status=404)

    # You might want to iterate over each question and serialize them individually
    serialized_questions = [QuestionSerializer(question).data for question in questions]

    return Response(serialized_questions)

@api_view(['GET', 'POST'])
def get_answer(request, youtube_id):
    print(youtube_id)
    
    # if request.method == 'GET':
    #     # Use youtubeID directly in the filter
    #     try:
    #         video_instance = Videos.objects.get(youtubeID=youtube_id)
           
            
    #         if not answers.exists():
    #             return Response({"error": "answers not found"}, status=404)

    #         # Serialize each answer individually
    #         serialized_answers = [AnswerSerializer(answer).data for answer in answers]

    #         return Response(serialized_answers)
    #     except Videos.DoesNotExist:
    #         return Response({"error": "video not found"}, status=404)
    
    # Handle POST request logic if needed
    return Response({"message": "This endpoint supports GET requests."}, status=400)





# views.py
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from .models import Videos
from .serializers import VideosSerializer

@api_view(['POST'])
@parser_classes([JSONParser])
def upload_json(request):
    data = request.data

    if isinstance(data, list):
        try:
            for video_data in data:
                serializer = VideosSerializer(data=video_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Videos added successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    elif isinstance(data, dict) and 'videos' in data:
        videos_data = data['videos']

        try:
            for video_id, video_data in videos_data.items():
                serializer = VideosSerializer(data=video_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Video added successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response({'error': 'Invalid data format'}, status=status.HTTP_400_BAD_REQUEST)

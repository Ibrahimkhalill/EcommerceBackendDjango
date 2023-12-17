from django.urls import path
from .views import get_videos,upload_json,get_question_with_options,get_answer,signup_view,login_view,logout_view

urlpatterns = [
    # ... other URL patterns
    path('api/signup/', signup_view, name='signup'),
    path('api/login/',login_view,name='login'),
     path('api/logout/',logout_view,name='login'),
    path('api/get-videos/', get_videos, name='get_videos'),
    path('api/upload-json/', upload_json, name='upload_json'),
    path('api/get-question/<str:youtube_id>/', get_question_with_options, name='get_question'),
    path('api/get-answer/<str:youtube_id>',get_answer,name='get_answer')
    

]
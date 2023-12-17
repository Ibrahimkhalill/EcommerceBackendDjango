from rest_framework import serializers
from .models import Videos, Question

# class OptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Option
#         fields = ['text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    # options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id','youtubeID', 'title', 'option1','option2','option3','option4','answer']

class VideosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Videos
        fields = ['noq', 'title', 'youtubeID']

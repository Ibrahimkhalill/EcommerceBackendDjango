from django.db import models


# Create your models here.



class Videos(models.Model):
    noq = models.CharField(max_length=10)
    title = models.TextField(blank=True, null=True)
    youtubeID = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.youtubeID
    
class Question(models.Model):
    youtubeID = models.ForeignKey(Videos, on_delete=models.CASCADE, blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    option1 = models.TextField(blank=True, null=True)
    option2 = models.TextField(blank=True, null=True)
    option3 = models.TextField(blank=True, null=True)
    option4 = models.TextField(blank=True, null=True)
    answer =  models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
    

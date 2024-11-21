from celery import shared_task
from .models import OTP
from django.utils import timezone
from datetime import timedelta

@shared_task
def delete_expired_otps():
    expired_otps = OTP.objects.filter(created_at__lt=timezone.now() - timedelta(minutes=2))
    expired_otps.delete()
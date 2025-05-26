from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from users.managers import UserManager
from users.base.models import TimeStampedModel
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser, TimeStampedModel):
    """
    Custom user model that extends the default Django user model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique= True)
    username= models.CharField(max_length=150, unique=True)    
    password= models.CharField()    

    objects= UserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        db_table= 'users'
    

class PasswordResetOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

class SensorData(models.Model):
    device_id = models.CharField(max_length=50)
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SensorData(device_id={self.device_id}, temperature={self.temperature}, humidity={self.humidity})"



class UserTempdata(TimeStampedModel):
    """
    Temporary data model for storing user information before final registration.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    username= models.CharField(max_length=150, unique=True)    
    password= models.CharField()
    otp= models.CharField(max_length=6)
    is_verified= models.BooleanField(default= False)
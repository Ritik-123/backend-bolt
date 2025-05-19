from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from users.managers import UserManager
from users.base.models import TimeStampedModel

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
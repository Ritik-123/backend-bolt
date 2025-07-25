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
    password= models.CharField(max_length=128)    
    phone_no= models.IntegerField(null= True, blank=True)
    address= models.CharField(max_length=500, null=True, blank=True)

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


class Category(TimeStampedModel):
    """
    Model to store product categories.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'category'
        

class Product(TimeStampedModel):
    """
    Model to store product information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique= True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'product'
    
class OrderStatus(models.TextChoices):
    PENDING = 'pending'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'

class Order(TimeStampedModel):
    """
    Model to store order information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='products_ordered')
    total_price= models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"
    
    class Meta:
        db_table = 'order'
        

class Cart(TimeStampedModel):
    """
    Model to store user's cart information.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ManyToManyField(Product, related_name='products_in_cart')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock= models.PositiveIntegerField()

    def __str__(self):
        return f"Cart {self.id} for {self.user.email}"
    
    class Meta:
        db_table = 'cart'

class SensorData(models.Model):
    device_id = models.CharField(max_length=50)
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SensorData(device_id={self.device_id}, temperature={self.temperature}, humidity={self.humidity})"
    
    class Meta:
        db_table = 'sensor_data'
        

# class Role(models.Model):
#     """
#     Table stores all the role information.
#     """
#     id= models.AutoField(primary_key= True)
#     rid= models.UUIDField(default= uuid.uuid4, editable= False, unique= True)
#     name= models.CharField(max_length= 100, unique= True, blank= True, null= True)
#     is_staff= models.BooleanField(default= False)
#     description= models.CharField(max_length= 255, null = True, blank= True)
#     level= models.IntegerField(null= True, blank= True)
#     reports_to= models.ForeignKey('self', on_delete= models.CASCADE, related_name="role_reports_to", to_field= 'rid', blank= True, null= True)
#     created_by= models.ForeignKey('self', on_delete= models.CASCADE, related_name="role_created_by", to_field= 'rid', blank= True, null= True)
#     created_on= models.DateTimeField(auto_now_add= True, editable= False, null= True, blank= True)
#     updated_on= models.DateTimeField(auto_now= True, null= True, blank= True)

#     objects= RoleManager()
    
#     class Meta:
#         db_table= 'fuzzer_role'

#     def __str__(self):
#         return self.name

# class Permission(models.Model):
#     """
#     Table stores all the Permission static data.
#     """
#     id= models.AutoField(primary_key= True)
#     permid= models.UUIDField(default= uuid.uuid4, editable= False, unique= True)
#     name= models.CharField(max_length= 100, blank= True, null= True)
#     codename= models.CharField(max_length= 200, blank= True, null= True)

#     objects= PermissionsManager()

#     class Meta:
#         db_table= 'fuzzer_permission'

#     def __str__(self):
#         return self.codename

# class RolePermission(models.Model):
#     """
#     Table stores : Permissions assign to Role.
#     """
#     id= models.AutoField(primary_key= True)
#     rpid= models.UUIDField(default= uuid.uuid4, editable= False, unique= True)
#     permid= models.ForeignKey(Permission, to_field= 'permid', on_delete= models.CASCADE, blank= True, null= True)
#     rid= models.ForeignKey(Role, to_field= 'rid', on_delete= models.CASCADE, null= True, blank= True)

#     objects= RolePermissionsManager()

#     class Meta:
#         db_table= 'fuzzer_role_permission'

#     def __str__(self):
#         return self.id



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
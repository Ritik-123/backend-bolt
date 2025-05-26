from rest_framework import serializers
from users.models import User, SensorData
from users.validators.validators import *




class UserSerializer(serializers.ModelSerializer):
    """
    **Serializer used to serialize user data.**
    """
    email= serializers.EmailField(required= True, validators= [EmailValidators()])
    username= serializers.CharField(required= True, min_length= 4, max_length= 50, validators= [NameValidator()])
    password= serializers.CharField(write_only= True, required= True, min_length= 4, max_length= 50, validators= [PasswordValidator()])

    class Meta:
        model= User
        fields= ['id','email', 'username', 'password']

    
    def create(self, validated_data):
        """
        **Create user.**
        """
        user= User.objects.create_user(**validated_data)
        return user
    
    def update(self, instance, validated_data):
        """
        **Update user.**
        """
        instance.username= validated_data.get('username', instance.username)
        instance.password= validated_data.get('password', instance.password)
        instance.save()
        return instance    
    

class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model= User
        fields= ['id', 'username', 'email', 'is_active']


# Serializer used in kafka consumer

class SensorDataSerializer(serializers.ModelSerializer):
    """
    **Used to serialize the sensor data.**
    """
    class Meta:
        model = SensorData
        fields = '__all__'
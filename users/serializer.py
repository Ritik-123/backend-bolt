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


class VerifyOTPSerializer(serializers.ModelSerializer):
    """
    **Serializer used to verify OTP.**
    """
    email = serializers.EmailField(required=True, validators=[userExistEmail], 
                                   error_messages={
                                        'required': 'Email is required',
                                        'invalid': 'Invalid email format'
                                    })
    otp = serializers.CharField(required=True, min_length=6, max_length=6,
                                error_messages={
                                    'required': 'OTP is required',
                                    'min_length': 'OTP must be exactly 6 characters long',
                                    'max_length': 'OTP must be exactly 6 characters long'
                                })

    class Meta:
        model= PasswordResetOTP
        fields = ['email', 'otp']

    def validate(self, data):
        record = PasswordResetOTP.objects.filter(email= data.get('email')).first()
        if not record:
            raise NotFound("OTP is not register for this email, please register first")

        if record.otp != data.get('otp'):
            raise serializers.ValidationError("Invalid OTP")

        if record.is_expired():
            record.delete()
            raise serializers.ValidationError("OTP has expired")
        
        return data
        
    def update(self, instance):
        """
        **Update the OTP record to mark it as verified.**
        """
        instance.is_verified = True
        instance.save()
        return instance
    


    

# Serializer used in kafka consumer

class SensorDataSerializer(serializers.ModelSerializer):
    """
    **Used to serialize the sensor data.**
    """
    class Meta:
        model = SensorData
        fields = '__all__'
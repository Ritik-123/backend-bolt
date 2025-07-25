from rest_framework import serializers
from users.models import *
from users.validators.validators import *
from django.db import transaction



class UserSerializer(serializers.ModelSerializer):
    """
    **Serializer used to serialize user data.**
    """
    email= serializers.EmailField(required= True, validators= [EmailValidators()])
    username= serializers.CharField(required= True, validators= [NameValidator()])
    password= serializers.CharField(write_only= True, required= True, validators= [PasswordValidator()])

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
    


class CategorySerializer(serializers.ModelSerializer):
    """
    **Serializer used to serialize category data.**
    """
    name = serializers.CharField(required=True, max_length=255, validators=[CategoryValidator()])
    description = serializers.CharField(required=False, allow_blank=True, max_length=500)

    class Meta:
        model= Category
        fields= '__all__'

    def validate_product(self, name):
        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError("Category with this name already exists")

    def create(self, validated_data):
        """
        **Create a new category.**
        """
        validated_data['name']= validated_data.get('name').lower()
        if 'description' in validated_data:
            validated_data['description'] = validated_data.get('description').lower()
        return Category.objects.create(**validated_data)
            
class CategoryUpdateSerializer(serializers.ModelSerializer):
    """
    **Serializer used to update category data.**
    """
    name = serializers.CharField(required= True, validators=[CategoryValidator()])
    description = serializers.CharField(allow_blank=True, max_length=500)

    class Meta:
        model= Category
        fields= ['name', 'description']

    def validate_product(self, name):
        if Category.objects.filter(name=name).exists():
            raise serializers.ValidationError("Category with this name already exists")

    def update(self, instance, validated_data):
        """
        **Update an existing category.**
        """
        if validated_data.get('name'):
            instance.name = validated_data.get('name').lower()
        if validated_data.get('description'):
            instance.description = validated_data.get('description').lower() 
        instance.save()
        return instance

class ProductSerializer(serializers.ModelSerializer):
    
    """
    **Serializer used to serialize product data.**
    """
    name = serializers.CharField(required=True, max_length=255, validators=[ProductValidator()])
    description = serializers.CharField(required=True, max_length=500)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    stock = serializers.IntegerField(required=True, min_value=0)
     
    class Meta:
        model= Product
        fields= '__all__'

    def create(self, validated_data):
        """
        **Create a new product.**
        """
        if 'name' in validated_data:
            validated_data['name'] = validated_data.get('name').lower()
        if 'description' in validated_data:
            validated_data['description'] = validated_data.get('description').lower()
        return Product.objects.create(**validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    **Serializer used to update product data.**
    """
    name = serializers.CharField(max_length=255, validators=[ProductValidator()])
    description = serializers.CharField(max_length=500)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    stock = serializers.IntegerField(min_value=0)

    class Meta:
        model= Product
        fields= ['name', 'description', 'price', 'stock']

    def update(self, instance, validated_data):
        """
        **Update an existing product.**
        """
        if validated_data.get('name'):
            instance.name = validated_data.get('name').lower()
        if validated_data.get('description'):
            instance.description = validated_data.get('description').lower()
        if validated_data.get('price'): 
            instance.price = validated_data.get('price')
        if validated_data.get('stock'):
            instance.stock = validated_data('stock')
        instance.save()
        return instance



class OrderSerializer(serializers.ModelSerializer):
    """
    **Serializer used to serialize order data.**
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    products = serializers.PrimaryKeyRelatedField( many=True, queryset=Product.objects.all())

    class Meta:
        model = Order
        fields = ['id', 'user', 'products', 'status']

    def validate(self, data):
        """
        **Validate the order data.**
        """
        products= data.get('products')
        if 'products' not in data or not data.get('products'):
            raise serializers.ValidationError("At least one product must be selected")
        for product in products:
            if product.stock <= 0:
                raise serializers.ValidationError(f"Product {product.name} is out of stock.")
        return data

    def create(self, validated_data):
        """
        **Create a new order.**
        """
        if 'products' in validated_data:
            products= validated_data.pop('products')
        validated_data['user']= self.context['request'].user
        validated_data['status']= str(OrderStatus.PENDING)
        validated_data['total_price'] = sum(product.price for product in products)
        
        with transaction.atomic():    
            order= Order.objects.create(**validated_data)
            for product in products:
                product.stock -= 1
                product.save()
            order.products.set(products)
            return order
        raise serializers.ValidationError("Failed to create order, please try again later")

class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    **Serializer used to update order data.**
    """
    status = serializers.ChoiceField(choices=OrderStatus.choices, required=True)

    class Meta:
        model = Order
        fields = ['status']

    def update(self, instance, validated_data):
        """
        **Update an existing order.**
        """
        instance.status = validated_data['status']
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    """
    **Serializer used to serialize cart data.**
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())

    class Meta:
        model = Cart
        fields = ['id', 'user', 'products', 'stock', 'total_price']

    def validate(self, data):
        """
        **Validate the cart data.**
        """
        products = data.get('products')
        if 'products' not in data or not data.get('products'):
            raise serializers.ValidationError("At least one product must be selected")
        for product in products:
            if product.stock <= 0:
                raise serializers.ValidationError(f"Product {product.name} is out of stock.")
        return data
    
    def create(self, validated_data):
        """
        **Create a new cart.**
        """
        if 'products' in validated_data:
            products = validated_data.pop('products')
        validated_data['user'] = self.context['request'].user
        validated_data['total_price'] = sum(product.price for product in products)
        
        with transaction.atomic():
            cart = Cart.objects.create(**validated_data)
            cart.product.set(products)
            return cart
        raise serializers.ValidationError("Failed to create cart, please try again later")
    
# class CartUpdateSerializer(serializers.ModelSerializer):
#     """
#     **Serializer used to update cart data.**
#     """
#     products = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
#     stock = serializers.IntegerField(min_value=0)

#     class Meta:
#         model = Cart
#         fields = ['products', 'stock']

#     def update(self, instance, validated_data):
#         """
#         **Update an existing cart.**
#         """
#         if 'products' in validated_data:
#             products = validated_data.pop('products')
#             instance.product.set(products)
#         if 'stock' in validated_data:
#             instance.stock = validated_data['stock']
#         instance.save()
#         return instance

    

    


# Serializer used in kafka consumer

class SensorDataSerializer(serializers.ModelSerializer):
    """
    **Used to serialize the sensor data.**
    """
    class Meta:
        model = SensorData
        fields = '__all__'
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from users.serializer import *
from services.responseservice import SuccessResponse, FailureResponse
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from users.validators.validators import *
from rest_framework.exceptions import PermissionDenied
from users.permission import CheckUserPermission
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from users.utils import generate_otp, send_otp_email
from users.models import *
from django.utils import timezone
from datetime import timedelta
import logging
from users.tasks import order_status_email
from users.pagination import PaginatedAPIView



logger= logging.getLogger('server')
logger.propagate = False


class CreateUserView(APIView):
    """
    **API used to create user.**\n
    It is only for admin user.
    """
    permission_classes = [IsAdminUser]

    @extend_schema(
        responses={201: UserSerializer}
    )
    def post(self, request):
        """
        **API used to create user.**
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception= True):
            serializer.save()
            return SuccessResponse(status_code=201, data=serializer.data)()
        logger.info(f"User creation failed: {serializer.errors}")
        raise serializers.ValidationError('User creation failed')
    

class UserView(APIView):
    """
    **API used to perform crud operations of user.**
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """
        **API used to return the data of given user.**\n
        Input:
            . User id (uid) in Path variable.
        """
        UidValidator()(id)
        CheckUserPermission()(request.user, id)
        serializer = UserSerializer(request.user)
        return SuccessResponse(status_code=200, data=serializer.data)()

    
        
    def put(self, request, id):
        """
        **It is used to update user**.\n
        Fields to be updated:
            username, password
        """
        UidValidator()(id)
        CheckUserPermission()(request.user, id)
        serializer= UserSerializer(data= request.data, partial= True, context= {'request': request})
        if serializer.is_valid(raise_exception= True):
            serializer.update()
            return SuccessResponse(status_code= 200, data= serializer.data)()
        logger.info(f"User updation failed: {serializer.errors}")
        raise serializers.ValidationError('User updation failed')
    
    def delete(self, request, id):
        """
        **It is used to delete a user.**\n
        Input:
            . User id (uid) in Path variable.
        Delete the user on the basis of uid.
        """
        UidValidator()(id)
        CheckUserPermission()(request.user, id)
        User.objects.filter(id= id).delete()
        return SuccessResponse(status_code= 200, data= {'message': 'User delete successfully'})()

class UserListView(APIView):

    """
    **It is used to return all the users data.**\n
    It is only for admin user.
    """
    permission_classes= [IsAdminUser]

    def get(self, request):
        instances= User.objects.all()
        serializer= UserListSerializer(instances, many= True)
        return SuccessResponse(data= serializer.data, status_code= 200)()
    

class ForgotPasswordView(APIView):
    """
    **API is used to set password if user forgot it's old password.**\n
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email")
        requiredEmail(email)
        userExistEmail(email)
        CheckUserPermission()(request.user, User.objects.get(email=email).id)
        ChkExistingOTP.existingOTP(email)
        otp= generate_otp()
        PasswordResetOTP.objects.create(email=email, otp=otp)
        username= User.objects.get(email=email).username
        if send_otp_email(username, email, otp):
            return SuccessResponse(data={"message": "OTP sent to your email"}, status_code=200)()
        raise serializers.ValidationError("Failed to send OTP")
    
class VerifyOTPView(APIView):

    """
    **API is used to verify the OTP.**\n
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):

        serializer= VerifyOTPSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email= serializer.data.get('email')
            user= User.objects.filter(email=email).first()
            CheckUserPermission()(request.user, user.id)
            # Update the OTP record to mark it as verified
            instance= PasswordResetOTP.objects.filter(email=email).first()
            serializer.update(instance)
        else:
            logger.info(f"OTP verification failed: {serializer.errors}")
            raise serializers.ValidationError('OTP verification failed')
        return SuccessResponse(data={"message": "OTP verified"}, status_code=200)()
        

class ResetPasswordView(APIView):

    """
    **API is used to reset password.**\n
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")
        if not email or not new_password:
            raise serializers.ValidationError("Email and new password both are required")
        userExistEmail(email)
        CheckUserPermission()(request.user, User.objects.get(email=email).id)
        OTPValidator()(email)
        PasswordValidator()(new_password)
        user= User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        # delete OTP records
        PasswordResetOTP.objects.filter(email=email).delete()
        return SuccessResponse(data={"message": "Password reset successful"}, status_code=200)()


# class CategoryView(APIView):
class CategoryView(PaginatedAPIView):
    
    """
    **It is used to create Category.**
    """
    permission_classes= [IsAuthenticated]

    def get(self, request):
        """
        **API used to return all categories.**
        """
        categories = Category.objects.all()
        paginatior, page= self.paginate_queryset(categories, request)
        serializer = CategorySerializer(page, many=True)
        return self.paginated_response(paginatior, serializer.data)
        # serializer = CategorySerializer(categories, many=True)
        # return SuccessResponse(data=serializer.data, status_code=200)()

    def post(self, request):
        """
        **API used to create category.**\n
        Input:
            . name: Name of the category.
            . description: Description of the category.
        """
        if request.user.is_staff == False:
            raise PermissionDenied()
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return SuccessResponse(status_code=201, data=serializer.data)()
        logger.info(f"Category creation failed: {serializer.errors}")
        raise serializers.ValidationError('Category creation failed')

class CategoryUpdateDeleteView(APIView):
    
    """
    **API used to update and delete category.**\n
    """
    permission_classes= [IsAuthenticated]

    def get(self, request, id):
        """
        **API used to return the category data.**\n
        Input:
            . Category id (id) in Path variable.
        """
        category = Category.objects.filter(id=id).first()
        if not category:
            raise NotFound(f"Category not found with id: {id}")
        serializer = CategorySerializer(category)
        return SuccessResponse(status_code=200, data=serializer.data)()

    def put(self, request, id):
        """
        **API used to update the category.**\n
        Input:
            . Category id (id) in Path variable.
            . name: Name of the category.
            . description: Description of the category.
        """
        category = Category.objects.filter(id=id).first()
        if not category:
            raise NotFound(f"Category not found with id: {id}")
        serializer = CategoryUpdateSerializer(category, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.update(category, serializer.validated_data)
            return SuccessResponse(status_code=200, data=serializer.data)()
        logger.info(f"Category update failed: {serializer.errors}")
        raise serializers.ValidationError('Category update failed')
    
    def delete(self, request, id):
        """
        **API used to delete the category.**\n
        Input:
            . Category id (id) in Path variable.
        """
        category = Category.objects.filter(id=id).first()
        if not category:
            raise NotFound(f"Category not found with id: {id}")
        category.delete()
        return SuccessResponse(status_code=200, data={'message': 'Category deleted successfully'})()


class ProductView(PaginatedAPIView):

    """
    **API used to create product.**\n
    """

    permission_classes= [IsAuthenticated]

    def get(self, request):
        """
        **API used to return all products.**
        """
        products = Product.objects.all()
        paginator, page= self.paginate_queryset(products, request)
        serializer= ProductSerializer(page, many= True)
        return self.paginated_response(paginator, serializer.data)
        # serializer = ProductSerializer(products, many=True)
        # return SuccessResponse(data=serializer.data, status_code=200)()
    
    def post(self, request):
        """
        **API used to create product.**\n
        Input:
            . name: Name of the product.
            . description: Description of the product.
            . price: Price of the product.
            . stock: Stock of the product.
            . category: Category id of the product.
        """
        if request.user.is_staff == False:
            raise PermissionDenied()
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return SuccessResponse(status_code=201, data=serializer.data)()
        logger.info(f"Product creation failed: {serializer.errors}")
        raise serializers.ValidationError('Product creation failed')
    

class ProductUpdateDeleteView(APIView):

    """
    It is used to get, update and delete product.
    """
    permission_classes= [IsAuthenticated]

    def get(self, request, id):
        """
        **API used to return the product data.**\n
        Input:
            . Product id (id) in Path variable.
        """
        product = Product.objects.filter(id=id).first()
        if not product:
            raise NotFound(f"Product not found with id: {id}")
        serializer = ProductSerializer(product)
        return SuccessResponse(status_code=200, data=serializer.data)()

    def put(self, request, id):
        """
        **API used to update the product.**\n
        Input:
            . Product id (id) in Path variable.
            . name: Name of the product.
            . description: Description of the product.
            . price: Price of the product.
            . stock: Stock of the product.
            . category: Category id of the product.
        """
        product = Product.objects.filter(id=id).first()
        if not product:
            raise NotFound(f"Product not found with id: {id}")
        serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.update(product, serializer.validated_data)
            return SuccessResponse(status_code=200, data=serializer.data)()
        logger.info(f"Product update failed: {serializer.errors}")
        raise serializers.ValidationError('Product update failed')
    
    def delete(self, request, id):
        """
        **API used to delete the product.**\n
        Input:
            . Product id (id) in Path variable.
        """
        product = Product.objects.filter(id=id).first()
        if not product:
            raise NotFound(f"Product not found with id: {id}")
        product.delete()
        return SuccessResponse(status_code=200, data={'message': 'Product deleted successfully'})()
    


class OrderView(PaginatedAPIView):

    """
    It is used to create order.
    """

    permission_classes= [IsAuthenticated]

    def get(self, request):
        """
        **API used to return all orders.**
        """
        if request.user.is_staff == True:
           orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        paginattor, page= self.paginate_queryset(orders, request)
        serializer= OrderSerializer(page, many=True)
        return self.paginated_response(paginattor, serializer.data)
        # serializer = OrderSerializer(orders, many=True)
        # return SuccessResponse(data=serializer.data, status_code=200)()
    
    def post(self, request):
        """
        **API used to create order.**\n
        Input:
            . user: User id of the order.
            . products: List of product ids in the order.
            . total_price: Total price of the order.
            . status: Status of the order.
        """
        serializer = OrderSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            # Trigger the signal to send order status update email
            order_status_email.delay(
                id=serializer.data.get('id'),
                username=request.user.username,
                order_status=serializer.data.get('status'),
                email=request.user.email
            )
            return SuccessResponse(status_code=201, data=serializer.data)()
        logger.info(f"Order creation failed: {serializer.errors}")
        raise serializers.ValidationError('Order creation failed')
    

class OrderUpdateDeleteView(APIView):

    """
    It used to get, update and delete order.
    """

    permission_classes= [IsAuthenticated]

    def get(self, request, id):
        """
        **API used to return the order data.**\n
        Input:
            . Order id (id) in Path variable.
        """
        if request.user.is_staff == True:    
            order = Order.objects.filter(id=id).first()
        else:
            order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            raise NotFound(f"Order not found with id: {id}")
        serializer = OrderUpdateSerializer(order)
        return SuccessResponse(status_code=200, data=serializer.data)()

    def put(self, request, id):
        """
        **API used to update the order.**\n
        Input:
            . Order id (id) in Path variable.
            . status: Status of the order.
        """
        if request.user.is_staff == False:
            raise PermissionDenied()
        order = Order.objects.filter(id=id).first()
        if not order:
            raise NotFound(f"Order not found with id: {id}")
        serializer = OrderUpdateSerializer(order, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            previous_status= order.status
            serializer.update(order, serializer.validated_data)
            if serializer.data.get('status') != previous_status:
            # Trigger the celery task to send order status update email
                order_status_email.delay(
                    id=order.id,
                    username=order.user.username,
                    order_status=serializer.data['status'],
                    email=order.user.email
            )
            return SuccessResponse(status_code=200, data=serializer.data)()
        logger.info(f"Order update failed: {serializer.errors}")
        raise serializers.ValidationError('Order update failed')
    
    def delete(self, request, id):
        """
        **API used to delete the order.**\n
        Input:
            . Order id (id) in Path variable.
        """
        if request.user.is_staff == True:
            order = Order.objects.filter(id=id).first()
        else:
            order = Order.objects.filter(id=id, user=request.user).first()
        if not order:
            raise NotFound(f"Order not found with id: {id}")
        order.delete()
        return SuccessResponse(status_code=200, data={'message': 'Order deleted successfully'})()
    

class CartView(PaginatedAPIView):
    """
    **API used to create cart.**\n
    It is only for authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        **API used to return all carts of the user.**
        """
        if request.user.is_staff == True:
           orders = Cart.objects.all()
        else:
            orders = Cart.objects.filter(user=request.user)
        paginattor, page= self.paginate_queryset(orders, request)
        serializer= CartSerializer(page, many=True)
        return self.paginated_response(paginattor, serializer.data)
        
    def post(self, request):
        """
        **API used to create cart.**\n
        Input:
            . user: User id of the cart.
            . products: List of product ids in the cart.
            . total_price: Total price of the cart.
            . stock: Stock of the product.
        """
        serializer = CartSerializer(data=request.data, context={'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return SuccessResponse(status_code=201, data=serializer.data)()
        logger.info(f"Cart creation failed: {serializer.errors}")
        raise serializers.ValidationError('Cart creation failed')
    

class CartUpdateDeleteView(APIView):

    """
    It is used to get, update and delete cart.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """
        **API used to return the cart data.**\n
        Input:
            . Cart id (id) in Path variable.
        """
        if request.user.is_staff == True:    
            cart = Cart.objects.filter(id=id).first()
        else:
            cart = Cart.objects.filter(id=id, user=request.user).first()
        if not cart:
            raise NotFound(f"Cart not found with id: {id}")
        serializer = CartSerializer(cart)
        return SuccessResponse(status_code=200, data=serializer.data)()
    
    # def put(self, request, id):
    #     """
    #     **API used to update the cart.**\n
    #     Input:
    #         . Cart id (id) in Path variable.
    #         . products: List of product ids in the cart.
    #         . total_price: Total price of the cart.
    #         . stock: Stock of the product.
    #     """
    #     if request.user.is_staff == True:
    #         cart = Cart.objects.filter(id=id).first()
    #     else:
    #         cart = Cart.objects.filter(id=id, user=request.user).first()
    #     if not cart:
    #         raise NotFound(f"Cart not found with id: {id}")
    #     serializer = CartSerializer(cart, data=request.data, partial=True)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.update(cart, serializer.validated_data)
    #         return SuccessResponse(status_code=200, data=serializer.data)()
    #     logger.info(f"Cart update failed: {serializer.errors}")
    #     raise serializers.ValidationError('Cart update failed')
    
    def delete(self, request, id):
        """
        **API used to delete the cart.**\n
        Input:
            . Cart id (id) in Path variable.
        """
        if request.user.is_staff == True:
            cart = Cart.objects.filter(id=id).first()
        else:
            cart = Cart.objects.filter(id=id, user=request.user).first()
        if not cart:
            raise NotFound(f"Cart not found with id: {id}")
        cart.delete()
        return SuccessResponse(status_code=200, data={'message': 'Cart deleted successfully'})()


class OrderFromCartView(APIView):
    """
    **API used to create order from cart.**\n
    It is only for authenticated user.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        **API used to create order from cart.**\n
        Input:
            . cart_id: Cart id of the cart.
        """
        cart_id = request.data.get('cart_id')
        if not cart_id:
            raise serializers.ValidationError("Cart id is required")
        cart = Cart.objects.filter(id=cart_id, user=request.user).first()
        if not cart:
            raise NotFound(f"Cart not found with id: {cart_id}")
        
        serializer = OrderSerializer(data={
            'user': request.user.id,
            'products': list(cart.products.values_list('id', flat=True)),
            'total_price': cart.total_price,
            'status': OrderStatus.PENDING
        }, context={'request': request})
        
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            # Remove this object from the cart
            cart.delete()
            # Trigger the celery task to send order status update email
            order_status_email.delay(
                id=serializer.data.get('id'),
                username=request.user.username,
                order_status=serializer.data.get('status'),
                email=request.user.email
            )
            return SuccessResponse(status_code=201, data=serializer.data)()
        
        logger.info(f"Order creation from cart failed: {serializer.errors}")
        raise serializers.ValidationError('Order creation from cart failed')




# API used in kafka consumer to get the sensor data
class SensorDataView(APIView):
    
    """
    **API used to get the sensor data.**\n
    """
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        data = SensorData.objects.all().order_by('-timestamp')[:100]
        serializer = SensorDataSerializer(data, many=True)
        return SuccessResponse(data=serializer.data, status_code=200)()




# class SMTPCreateUpdateView(APIView):
#     """
#     APIView for adding SMTP details
#     Parameters
#     ---------
#         **Argument need to be passed.
#         "in":requestBody
#         "name": host
#         "type": integer
#         "required": true
#         "name": port
#         "type": integer
#         "required": true
#         "name": tls
#         "type": bool
#         "required": true
#         "name": username
#         "type": str
#         "required": true
#         "name": password
#         "type": str
#         "required": true
#         "name": from_email
#         "type": str
#         "required": true
#         "name": test_email
#         "type": str
#         "required": true
#     Returns
#     --------
#         dict
#         Success:

#         Failed:
#         status_code : 400 BAD REQUEST
#         {"error":"error occured"}
#     """

#     permission_classes = [IsAdminUser]
#     serializer_class = CreateSMTPSerializer

#     @extend_schema(
#             responses= {201:dict}
#     )

#     def post(self, request):

#         data = request.data
    
#         service = AdminDetailService()
#         service.validate_for_create()

#         smtp_details = service.get_admin_details()  # passing admin obj for update

#         smtp_service = SMTPService(smtp_details, data)
#         result = smtp_service.configure_smtp()

#         return SuccessResponse(data=result, status_code=status.HTTP_201_CREATED)()

#     @extend_schema(
#             responses= {200:dict}
#     )
#     def put(self, request):
#         """ """
#         data = request.data
#         required_fields = ["host", "port", "tls", "username", "password"]
#         missing_fields = [field for field in required_fields if field not in data]
#         if missing_fields:
#             raise serializers.ValidationError(f"Missing required fields {', '.join(missing_fields)}")

#         empty_fields = [field for field in required_fields if not data.get(field)]
#         if empty_fields:
#             raise serializers.ValidationError(f"Fields cannot be null or empty {', '.join(empty_fields)}")
     
#         service = AdminDetailService()
#         service.check_smtp_status()

#         smtp_details = service.get_admin_details()  # passing admin obj for update

#         smtp_service = SMTPService(smtp_details, data)
#         result = smtp_service.configure_smtp()

#         return Response({"message": "SMTP updated successfully"})

#     @extend_schema(
#             responses= {200:dict}
#     )
#     def get(self, request):
#         """
#         Retrieve and return SMTP configuration details.
#         """

#         admin_service = AdminDetailService()
#         admin_details = admin_service.get_admin_details()

#         serializer = GetSMTPSerializer(admin_details)
#         data = serializer.data
#         return Response(data, status=status.HTTP_200_OK)
    
#     @extend_schema(
#             responses= {200:dict}
#     )
#     def patch(self, request):

#         data = request.data
    
#         service = AdminDetailService()
#         service.validate_for_create()

#         smtp_details = service.get_admin_details()  # passing admin obj for update

#         smtp_service = SMTPService(smtp_details, data)
#         result = smtp_service.configure_smtp()

#         return SuccessResponse(data=result, status_code=status.HTTP_201_CREATED)()
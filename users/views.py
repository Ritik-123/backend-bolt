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
from users.models import User, PasswordResetOTP
from django.utils import timezone
from datetime import timedelta
import logging



logger= logging.getLogger('server')
logger.propagate = False

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

    def post(self, request):
        email = request.data.get("email")
        if not email:
            raise serializers.ValidationError("Email is required")
        ForgotPasswordEmailValidator()(email)
        
        # existing_otp = PasswordResetOTP.objects.filter(email=email).order_by("-created_at").first()
        existing_otp = PasswordResetOTP.objects.filter(email=email).first()

        if existing_otp:
            expiry_time = existing_otp.created_at + timedelta(minutes=10)
            if timezone.now() < expiry_time:
                raise serializers.ValidationError("OTP already sent, please check your email")
            else:
                existing_otp.delete()

        otp = generate_otp()
        PasswordResetOTP.objects.create(email=email, otp=otp)
        username= User.objects.get(email=email).username
        if send_otp_email(username, email, otp):
            return SuccessResponse(data={"message": "OTP sent to your email"}, status_code=200)()
        return FailureResponse(message="Failed to send OTP", status_code=400)()


class VerifyOTPView(APIView):

    """
    **API is used to verify the OTP.**\n
    """
    permission_classes = [IsAuthenticated]
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            raise serializers.ValidationError("Email and OTP both are required")
        
        ForgotPasswordEmailValidator()(email)

        # record = PasswordResetOTP.objects.filter(email=email, otp=otp).latest("created_at")        
        record = PasswordResetOTP.objects.filter(email=email, otp=otp).first()
        if not record:
            raise NotFound("OTP is not register for this email, please register first")

        if record.is_expired():
            record.delete()
            raise serializers.ValidationError("OTP has expired")

        record.is_verified = True
        record.save()
        return SuccessResponse(data={"message": "OTP verified"}, status_code=200)()
        

class ResetPasswordView(APIView):

    """
    **API is used to reset password.**\n
    """

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        if not email or not new_password:
            raise serializers.ValidationError("Email and new password both are required")

        ForgotPasswordEmailValidator()(email)
        PasswordValidator()(new_password)
        # Check if OTP was verified
        record = PasswordResetOTP.objects.filter(email=email, is_verified=True).latest("created_at")
        if not record:
            raise serializers.ValidationError("OTP not verified or expired")
        
        user= User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

        # Optional: delete OTP records
        PasswordResetOTP.objects.filter(email=email).delete()
        return SuccessResponse(data={"message": "Password reset successful"}, status_code=200)()


# API used in kafka consumer to get the sensor data
class SensorDataView(APIView):
    
    """
    **API used to get the sensor data.**\n
    """
    
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
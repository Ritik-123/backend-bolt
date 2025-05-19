from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from users.serializer import *
from services.responseservice import SuccessResponse, FailureResponse
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from users.validators.validators import *
from rest_framework.exceptions import PermissionDenied
from users.permission import CheckUserPermission



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
        return FailureResponse(status_code=400, message=serializer.errors)()
        
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
        return FailureResponse(status_code= 400, message= serializer.errors)()
    
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
    

class ForgotPassword(APIView):
    """
    **API is used to set password if user forgot it's old password.**\n

    """
    pass
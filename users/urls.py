from django.urls import path
from users.views import *


urlpatterns= [
    # url used to get, update and delete a user on the basis of user id.
    path('user/<uuid:id>', UserView.as_view(http_method_names= ['get', 'put', 'delete']), name= 'user-get-update-delete'),
    
    # url is used to create a user.
    path('create-user', UserView.as_view(http_method_names= ['post']), name= 'create-user'),
    
    # url is used to return all the users data.
    path('users', UserListView.as_view(http_method_names= ['get']), name= 'users-list'),

    # Forgot Password url:
    path('forgot-password', ForgotPasswordView.as_view(http_method_names= ['post']), name= 'forgot-password'),

    # Verify OTP url:
    path('verify-otp', VerifyOTPView.as_view(http_method_names= ['post']), name= 'verify-otp'),
    
    # Reset Password url:
    path('reset-password', ResetPasswordView.as_view(http_method_names= ['post']), name= 'reset-password'),

    # API for saving new smtp details----------------
    # path("smtp",views.SMTPCreateUpdateView.as_view()),
    # path('smtp/toggle', views.SMTPToggle.as_view()),

]
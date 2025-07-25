from django.urls import path
from users.views import *


urlpatterns= [
    # url used to get, update and delete a user on the basis of user id.
    path('user/<uuid:id>', 
         UserView.as_view(http_method_names= ['get', 'put', 'delete']), 
         name= 'user-get-update-delete'
         ),
    
    # url is used to create a user.
    path('create-user', 
         CreateUserView.as_view(http_method_names= ['post']), 
         name= 'create-user'),
    
    # url is used to return all the users data.
    path('users', 
         UserListView.as_view(http_method_names= ['get']), 
         name= 'users-list'),

    # Forgot Password url:
    path('forgot-password', 
         ForgotPasswordView.as_view(http_method_names= ['post']), 
         name= 'forgot-password'),

    # Verify OTP url:
    path('verify-otp', 
         VerifyOTPView.as_view(http_method_names= ['post']), 
         name= 'verify-otp'),
    
    # Reset Password url:
    path('reset-password', 
         ResetPasswordView.as_view(http_method_names= ['post']), 
         name= 'reset-password'),

     # API for creating a new category and get a list of all categories
     path('category', 
         CategoryView.as_view(http_method_names= ['get', 'post']), 
          name= 'category-create'),

     # API for getting, updating and deleting a category by id
     path('category/<uuid:id>', 
          CategoryUpdateDeleteView.as_view(http_method_names= ['get', 'put', 'delete']),
          name= 'category-get-update-delete'),
     
     # Url used to get all products and create a new product
     path('product', ProductView.as_view(http_method_names=['get', 'post']), name='product-create'),

     # Url used to get, update and delete a product by id
     path('product/<uuid:id>', ProductUpdateDeleteView.as_view(http_method_names=['get', 'put', 'delete']), name='product-get-update-delete'),

     # Url used to get all orders and create a new order
     path('order', OrderView.as_view(http_method_names=['get', 'post']), name='order-create'),

     # Url used to get, update and delete an order by id
     path('order/<uuid:id>', OrderUpdateDeleteView.as_view(http_method_names=['get', 'put', 'delete']), name='order-get-update-delete'),
  
     # Url used to get get and create a cart
     path('cart', CartView.as_view(http_method_names=['get', 'post']), name='cart-create'),

     # Url used to get and delete a cart by id
     path('cart/<uuid:id>', CartUpdateDeleteView.as_view(http_method_names=['get', 'delete']), name='cart-get-delete'),
  
    # API for saving new smtp details----------------
    # path("smtp",views.SMTPCreateUpdateView.as_view()),
    # path('smtp/toggle', views.SMTPToggle.as_view()),

]
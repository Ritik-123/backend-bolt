from django.urls import path
from users.views import *


urlpatterns= [
    # url used to get, update and delete a user on the basis of user id.
    path('user/<uuid:id>', UserView.as_view(http_method_names= ['get', 'put', 'delete']), name= 'user-get-update-delete'),
    # url is used to create a user.
    path('create-user', UserView.as_view(http_method_names= ['post']), name= 'create-user'),
    # url is used to return all the users data.
    path('users', UserListView.as_view(http_method_names= ['get']), name= 'users-list')

]
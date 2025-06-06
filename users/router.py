from django.urls import path, re_path
from . import consumers

websocket_urlpatterns=[
    # re_path(r"ws/chat/(?P<roomName>\w+)/$", consumers.ChatConsumer.as_asgi()),
    
    #---usign json websocket consumer-----
    path('ws/jwsc', consumers.MyJsonWebsocketConsumer.as_asgi()),

    # -----using websocket consumer-------
    path('ws/wsc', consumers.MyWebsocketConsumer.as_asgi()),

    #--------------------
    
    path('ws/sc', consumers.MySyncConsumer.as_asgi()),
    path("ws/ac", consumers.MyAsyncConsumer.as_asgi()),
    
    # path('ws/sc/<str:groupName>', consumers.MySyncConsumer.as_asgi()),
    # path("ws/ac/<str:groupName>", consumers.MyAsyncConsumer.as_asgi()),
    # re_path(r"ws/sc/$", consumers.MySyncConsumer.as_asgi()),
    # re_path(r'ws/ac/$', consumers.MyAsyncConsumer.as_asgi())
]

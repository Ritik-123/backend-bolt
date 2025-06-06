from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from time import sleep
import asyncio
from channels.db import database_sync_to_async
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, JsonWebsocketConsumer, AsyncJsonWebsocketConsumer


#------using json websocket consumer---------

class MyJsonWebsocketConsumer(JsonWebsocketConsumer):

    def connect(self):
        print('WebSocket Connected...')
        self.accept()

    def receive_json(self, content, **kwargs):
        print(f"Message from client {content}")

    def disconnect(self, code):
        print(f'Wenbsocket disconnected... {code}')
        

# ------using Websocket Consumer-----------

class MyWebsocketConsumer(WebsocketConsumer):

    # def connect(self):
    #     self.accept()

    def connect(self):
        self.accept()
        print('WebSocket Connected...')
        

    def receive(self, text_data=None, bytes_data=None):
        print(f"Message from client {text_data}")
        self.send(text_data= f"Hello {self.scope['user']}")

    def disconnect(self, code):
        print(f'Wenbsocket disconnected... {code}')



#-------using Sync and Async Consumer---------------

# class MySyncConsumer(SyncConsumer):

#     def websocket_connect(self, event):
#         """
#         This handler is called when client initially opens a connection and 
#         is about to finish the websocket handshake.
#         """
#         print('Websocket connected...', event)
#         print(f"channel layer... {self.channel_layer}")
#         print(f"channel name... {self.channel_name}")
#         self.groupName= self.scope['url_route']['kwargs']['groupName']
#         async_to_sync(self.channel_layer.group_add)(
#             self.groupName, # group name 
#             self.channel_name
#             )
#         self.send({
#             'type': 'websocket.accept'
#         })

#     def websocket_receive(self, event):
#         """
#         This handler is called when data received from client.
#         """
#         print('Message Received...', event)
#         print(f"Message from client : {event['text']}")
#         async_to_sync(self.channel_layer.group_send)(
#             self.groupName,
#             {
#                 'type': 'chat.message',
#                 'message': event['text']
#             }
#         )
        
#     def chat_message(self, event):
#         print(f"Event.... {event}")
#         print(f"Type of Evnet data : {type(event['message'])}")
#         self.send({
#             'type': 'websocket.send',
#             'text': event['message']
#         })
        
#     def websocket_disconnect(self, event):
#         """
#         This handler is called when either connection to the client is lost,
#         either from the client closing the connection,
#         the server closing the connection, or loss of the websocket.
#         """
#         print('Websocket disconnected...', event)
#         print(f"channel layer... {self.channel_layer}")
#         print(f"channel name... {self.channel_name}")
#         async_to_sync(self.channel_layer.group_discard)(
#             self.groupName,
#             self.channel_name
#         )
#         raise StopConsumer()
    

# class MyAsyncConsumer(AsyncConsumer):

#     async def websocket_connect(self, event):
#         """
#         This handler is called when client initially opens a connection and 
#         is about to finish the websocket handshake.
#         """
#         print('Websocket connected...', event)
#         print(f"channel layer... {self.channel_layer}")
#         print(f"channel name... {self.channel_name}")
#         self.groupName= self.scope['url_route']['kwargs']['groupName']
#         print(f"\nScope is---------: {self.scope}\n ---- \n {self.scope['url_route']} \n {self.scope['url_route']['kwargs']}\n")
#         await self.channel_layer.group_add(
#             self.groupName, # group name 
#             self.channel_name
#             )
#         await self.send({
#             'type': 'websocket.accept'
#         })

#     async def websocket_receive(self, event):
#         """
#         This handler is called when data received from client.
#         """
#         print('Message Received...', event)
#         print(f"Message from client : {event['text']}")
        
#         # if self.scope['user'].is_authenticated:
            

#         # data= json.loads(event['text'])
#         # print(f"\n after converting what data is : {data}, \n type of data is : {type(data)}\n")
#         # group= await database_sync_to_async(Group.objects.get)(name= self.groupName)
#         # # chat= Chat.objects.create(group= group, content= data['msg'])
#         # chat= Chat(content= data['msg'], group= self.groupName)
#         # await database_sync_to_async(chat.save)()

#         await self.channel_layer.group_send(
#             self.groupName,
#             {
#                 'type': 'chat.message',
#                 'message': event['text']
#             }
#         )
#         # else:
#         #     await self.send({
#         #         'type': 'websocket.send',
#         #         'text': json.dumps({'msg':'Login Required'})
#         #     })
        
#     async def chat_message(self, event):
#         print(f"Event.... {event}")
#         print(f"Type of Evnet data : {type(event['message'])}")
#         await self.send({
#             'type': 'websocket.send',
#             'text': event['message']
#         })

#     async def websocket_disconnect(self, event):
#         """
#         This handler is called when either connection to the client is lost,
#         either from the client closing the connection,
#         the server closing the connection, or loss of the websocket.
#         """
#         print('Websocket disconnected...', event)
#         print(f"channel layer... {self.channel_layer}")
#         print(f"channel name... {self.channel_name}")
#         await self.channel_layer.group_discard(
#             self.groupName,
#             self.channel_name
#         )
#         raise StopConsumer()



#-----------------------------------

class MySyncConsumer(SyncConsumer):

    def websocket_connect(self, event):
        """
        This handler is called when client initially opens a connection and 
        is about to finish the websocket handshake.
        """
        print('Websocket connected...', event)
        print(f"scope ---------- {self.scope}")
        self.send({
            'type': 'websocket.accept'
        })

    def websocket_receive(self, event):
        """
        This handler is called when data received from client.
        """
        print('Message Received...', event)
        print(f"Message from client : {event['text']}")
        for i in range(50):
            self.send({
                'type': 'websocket.send',
                'text': str(i)                
            })
            sleep(1)

    def websocket_disconnect(self, event):
        """
        This handler is called when either connection to the client is lost,
        either from the client closing the connection,
        the server closing the connection, or loss of the websocket. 
        """
        print('Websocket disconnected...', event)
        raise StopConsumer()


class MyAsyncConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        """
        This handler is called when client initially opens a connection and 
        is about to finish the websocket handshake.
        """
        print('Websocket connected...', event)
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        """
        This handler is called when data received from client.
        """
        print('Message Received...', event)
        print(f"Message from client : {event['text']}")
        for i in range(50):
            await self.send({
                'type': 'websocket.send',
                'text': str(i)                
            })
            await asyncio.sleep(1)

    async def websocket_disconnect(self, event):
        """
        This handler is called when either connection to the client is lost,
        either from the client closing the connection,
        the server closing the connection, or loss of the websocket. 
        """
        print('Websocket disconnected...', event)
        raise StopConsumer()







# class ChatConsumer(WebsocketConsumer):

#     def connect(self):
#         self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
#         self.room_group_name = f"chat_{self.room_name}"

#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )

#         self.accept()

#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )

#     # Receive message from WebSocket
#     def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]

#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name, {"type": "chat.message", "message": message}
#         )

#     # Receive message from room group
#     def chat_message(self, event):
#         message = event["message"]

#         # Send message to WebSocket
#         self.send(text_data=json.dumps({"message": message}))
















# from kafka import KafkaConsumer
# import json, logging, os
# from users.models import SensorData
# from django.db import transaction

# logger= logging.getLogger('server')
# logger.propagate = False

# consumer = KafkaConsumer(
#     'iot_bulk_data',
#     bootstrap_servers= os.getenv('BOOTSTRAP_SERVERS'), #'localhost:9092',
#     value_deserializer=lambda m: json.loads(m.decode('utf-8')),
#     auto_offset_reset='earliest',
#     enable_auto_commit=True,
#     group_id='sensor-group'
# )

# def consume_and_store():
#     for message in consumer:
#         data = message.value
#         logger.info(f"Received: {data}")
#         # Store in DB
#         with transaction.atomic():
#             SensorData.objects.create(
#                 device_id=data["device_id"],
#                 temperature=data["temperature"],
#                 humidity=data["humidity"],
#                 timestamp=data["timestamp"]
#             )

# if __name__ == "__main__":
#     consume_and_store()


# # batch = []
# # BATCH_SIZE = 1000

# # for message in consumer:
# #     data = message.value
# #     batch.append(SensorData(
# #         device_id=data["device_id"],
# #         temperature=data["temperature"],
# #         humidity=data["humidity"],
# #         timestamp=data["timestamp"]
# #     ))
# #     if len(batch) >= BATCH_SIZE:
# #         with transaction.atomic():
# #             SensorData.objects.bulk_create(batch)
# #         batch.clear()
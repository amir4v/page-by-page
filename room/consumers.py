# chat/consumers.py
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from app.models import PDF, Page
import os

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


def is_owner(request, pk):
    if str(request.user) == 'AnonymousUser':
        owner = False
    else:
        owner = request.user.pdf_set.filter(pk=pk).exists()
    return owner


from asgiref.sync import sync_to_async

async def get_path(self, text_data_json, pk, page_number):
    pk = int(text_data_json["pk"])
    page_number = int(text_data_json["page_number"]) + 1
    message = '/media/' + PDF.objects.get(pk=pk).page_set.filter(page_number=page_number)[0].path
    return message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        
        pk = int(text_data_json["pk"])
        page_number = int(text_data_json["page_number"])
        
        
        pdf = PDF.objects.get(pk=pk)
        pdf.current_page = page_number
        pdf.save()
        message = '/media/' + pdf.page_set.filter(page_number=page_number)[0].path
        # message = await sync_to_async(get_path(self, text_data_json, pk, page_number)
        # await get_path(self, text_data_json, pk, page_number)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))

import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import IntegrityError
from asgiref.sync import sync_to_async

from . import models


class ChatRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        try:
            d = models.ChatName(chat_name=self.room_name)
            await sync_to_async(d.save, thread_sensitive=True)()
        except IntegrityError:
            pass

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        await self._push_messages(await self._get_old_messages())

    async def _get_old_messages(self):
        _chat_id = await sync_to_async(models.ChatName.objects.get, thread_sensitive=True)(chat_name=self.room_name)
        old_messages = await sync_to_async(models.Messages.objects.filter, thread_sensitive=True)(
            chat_id_id=_chat_id.id)
        old_messages = await sync_to_async(list)(old_messages)
        return old_messages

    async def _push_messages(self, old_messages):
        for message in old_messages:
            await self.send(text_data=json.dumps({
                'message': message.message,
                'username': message.sender,
            }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chatroom_message',
                'message': message,
                'username': username,
            }
        )

        '''добавление сообщения в бд'''
        _id = await sync_to_async(models.ChatName.objects.get)(chat_name=self.room_name)
        d = models.Messages(
            chat_id_id=_id.id,
            message=message,
            sender=username,
        )
        await sync_to_async(d.save, thread_sensitive=True)()
        # self._db.store_message(message, username, self.room_name)

    async def chatroom_message(self, event):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

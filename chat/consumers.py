import json
from channels.generic.websocket import AsyncWebsocketConsumer

from . import database


class ChatRoomConsumer(AsyncWebsocketConsumer):
    def __init__(self):
        super().__init__()

        self._db = database.PostgresDB()

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        self._db.create_chat_id(self.room_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        old_messages = self._db.get_chat_history(self.room_name)
        for message in old_messages:
            await self.send(text_data=json.dumps({
                'message': message.message_value,
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

    async def chatroom_message(self, event, send_db=True):
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
        }))

        if send_db:
            self._db.store_message(message, username, self.room_name)

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class Round1Consumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f"kyt_{self.session_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        # ✅ グループへ中継
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast_message",  # ← これに対応させる
                "data": data
            }
        )

    # ✅ これを追加（これが無かった）
    async def broadcast_message(self, event):
        await self.send(text_data=json.dumps(event["data"]))

    

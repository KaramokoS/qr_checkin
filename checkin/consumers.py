import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f"session_{self.session_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Receive message from group
    async def attendee_checked_in(self, event):
        # kept for compatibility (we may also implement other types)
        await self.send(text_data=json.dumps(event))

    # standardized event types:
    async def attendee_checked_in_event(self, event):
        await self.send(text_data=json.dumps(event))

    # handlers used in views group_send: we used type "attendee.checked_in"
    async def attendee_checked_in(self, event):
        # event contains attendee data
        await self.send(text_data=json.dumps({
            'type': 'attendee_checked_in',
            'data': event
        }))

    async def session_closed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'session_closed',
            'data': event
        }))

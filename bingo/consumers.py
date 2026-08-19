import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

# በሜሞሪ ውስጥ የRoom ሁኔታዎችን መያዣ
ROOMS = {}

class BingoRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        # 1. ተጫዋቹ Login ካላደረገ Connection ውድቅ ይደረጋል
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'bingo_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Room ከሌለ አዲስ መፍጠር
        if self.room_name not in ROOMS:
            ROOMS[self.room_name] = {
                'status': 'WAITING',
                'timer': 45,
                'players': {},  # {username: cartela_id}
                'timer_task': None
            }

        # የነበረውን ስቴት ለአዲሱ ተጫዋች መላክ
        await self.send(text_data=json.dumps({
            'type': 'room_state',
            'status': ROOMS[self.room_name]['status'],
            'timer': ROOMS[self.room_name]['timer'],
                'players': ROOMS[self.room_name]['players']
        }))

        # ቆጠራው ካልጀመረ መጀመር
        if ROOMS[self.room_name]['status'] == 'WAITING' and ROOMS[self.room_name]['timer_task'] is None:
            ROOMS[self.room_name]['timer_task'] = asyncio.create_task(self.start_room_timer())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'select_cartela':
            # 45 ሰከንዱ ካላለቀና ክፍሉ በ WAITING ላይ ከሆነ ብቻ
            if ROOMS[self.room_name]['status'] == 'WAITING':
                try:
                    cartela_id = int(data.get('cartela_id')) # int መሆኑን ማረጋገጥ
                except (ValueError, TypeError):
                    return

                username = self.user.username

                # ካርቴላው በሌላ ሰው አለመያዙን ማረጋገጥ
                if cartela_id not in ROOMS[self.room_name]['players'].values():
                    # ተጫዋቹ ቀደም ብሎ የያዘው ካርቴላ ካለ ማፅዳት
                    ROOMS[self.room_name]['players'][username] = cartela_id

                    # ለሁሉም ተጫዋቾች ማሳወቅ
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'cartela_update',
                            'cartela_id': cartela_id,
                            'player_name': username
                        }
                    )

    async def start_room_timer(self):
        """የ45 ሰከንድ ቆጠራ"""
        while ROOMS[self.room_name]['timer'] > 0:
            await asyncio.sleep(1)
            ROOMS[self.room_name]['timer'] -= 1

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'timer_tick',
                    'time_left': ROOMS[self.room_name]['timer']
                }
            )

        # 45 ሰከንዱ ሲያልቅ ጨዋታውን ማስመር
        ROOMS[self.room_name]['status'] = 'PLAYING'
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'game_start'}
        )

    # Broadcast Event Handlers
    async def timer_tick(self, event):
        await self.send(text_data=json.dumps({'type': 'timer', 'time_left': event['time_left']}))

    async def cartela_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'cartela_selected',
            'cartela_id': event['cartela_id'],
            'player_name': event['player_name']
        }))

    async def game_start(self, event):
        await self.send(text_data=json.dumps({'type': 'game_started'}))
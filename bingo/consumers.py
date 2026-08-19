import json
import asyncio
import random
from channels.generic.websocket import AsyncWebsocketConsumer

ROOMS = {}

class BingoRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            self.username = f"Guest_{random.randint(100, 999)}"
        else:
            self.username = self.user.username

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'bingo_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.room_name not in ROOMS:
            ROOMS[self.room_name] = {
                'status': 'WAITING',
                'timer': 45,
                'players': {},
                'timer_task': None,
                'drawn_numbers': [],  # የወጡ ቁጥሮች መያዣ
                'available_numbers': list(range(1, 76))  # 1-75 ቁጥሮች
            }

        await self.send(text_data=json.dumps({
            'type': 'room_state',
            'status': ROOMS[self.room_name]['status'],
            'timer': ROOMS[self.room_name]['timer'],
            'players': ROOMS[self.room_name]['players'],
            'drawn_numbers': ROOMS[self.room_name]['drawn_numbers']
        }))

        if ROOMS[self.room_name]['status'] == 'WAITING' and ROOMS[self.room_name]['timer_task'] is None:
            ROOMS[self.room_name]['timer_task'] = asyncio.create_task(self.start_room_timer())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'select_cartela':
            if ROOMS[self.room_name]['status'] == 'WAITING':
                try:
                    cartela_id = int(data.get('cartela_id'))
                except (ValueError, TypeError):
                    return

                username = self.username

                if cartela_id not in ROOMS[self.room_name]['players'].values():
                    ROOMS[self.room_name]['players'][username] = cartela_id

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

        # 45 ሰከንዱ ሲያልቅ ጨዋታውን ማስመር እና ቁጥር ማውጣት መጀመር
        ROOMS[self.room_name]['status'] = 'PLAYING'
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'game_start'}
        )
        
        # ቁጥሮችን በየ 3 ሰከንዱ በራሱ ማውጣት ይጀምራል
        asyncio.create_task(self.start_drawing_numbers())

    async def start_drawing_numbers(self):
        """በየ 3 ሰከንዱ ቁጥር የሚያወጣ Loop"""
        numbers = ROOMS[self.room_name]['available_numbers']
        random.shuffle(numbers)

        for num in numbers:
            if ROOMS[self.room_name]['status'] != 'PLAYING':
                break
                
            await asyncio.sleep(3)  # በየ 3 ሰከንዱ
            ROOMS[self.room_name]['drawn_numbers'].append(num)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'number_drawn',
                    'number': num,
                    'all_drawn': ROOMS[self.room_name]['drawn_numbers']
                }
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

    async def number_drawn(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_number',
            'number': event['number'],
            'all_drawn': event['all_drawn']
        }))
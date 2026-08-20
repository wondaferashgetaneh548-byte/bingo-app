import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

ROOMS = {}

def generate_cartela_matrix():
    ranges = {
        'B': range(1, 16),
        'I': range(16, 31),
        'N': range(31, 46),
        'G': range(46, 61),
        'O': range(61, 76)
    }
    columns = {}
    for letter, r in ranges.items():
        columns[letter] = random.sample(r, 5)
    
    matrix = []
    for i in range(5):
        row = [
            columns['B'][i],
            columns['I'][i],
            columns['N'][i] if i != 2 else 'FREE',
            columns['G'][i],
            columns['O'][i]
        ]
        matrix.append(row)
    return matrix

class BingoRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        url_kwargs = self.scope.get('url_route', {}).get('kwargs', {})
        self.room_name = url_kwargs.get('room_name', 'default_room')
        self.room_group_name = f'bingo_{self.room_name}'
        
        self.user = self.scope.get('user')
        if self.user and self.user.is_authenticated:
            self.username = self.user.username
        else:
            self.username = f"Guest_{random.randint(1000, 9999)}"

        try:
            self.stake = int(str(self.room_name).replace('room_', ''))
        except ValueError:
            self.stake = 10

        if self.room_name not in ROOMS:
            ROOMS[self.room_name] = {
                'status': 'WAITING',
                'players': {},
                'drawn_numbers': [],
                'task': None,
                'draw_task': None
            }

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        total_pot = len(ROOMS[self.room_name]['players']) * self.stake
        commission = total_pot * 0.30
        winner_pot = total_pot - commission

        players_summary = {p: info['cartela_id'] for p, info in ROOMS[self.room_name]['players'].items()}

        await self.send(text_data=json.dumps({
            'type': 'room_state',
            'status': ROOMS[self.room_name]['status'],
            'total_pot': total_pot,
            'winner_pot': winner_pot,
            'commission': commission,
            'players': players_summary,
            'drawn_numbers': ROOMS[self.room_name]['drawn_numbers']
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'select_cartela' and ROOMS[self.room_name]['status'] == 'WAITING':
            cartela_id = int(data.get('cartela_id'))
            taken_ids = [p['cartela_id'] for p in ROOMS[self.room_name]['players'].values()]

            if cartela_id not in taken_ids:
                matrix = generate_cartela_matrix()
                ROOMS[self.room_name]['players'][self.username] = {
                    'cartela_id': cartela_id,
                    'matrix': matrix
                }

                total_pot = len(ROOMS[self.room_name]['players']) * self.stake
                commission = total_pot * 0.30
                winner_pot = total_pot - commission

                await self.send(text_data=json.dumps({
                    'type': 'my_cartela_data',
                    'cartela_id': cartela_id,
                    'matrix': matrix
                }))

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'cartela_update',
                        'cartela_id': cartela_id,
                        'player_name': self.username,
                        'total_pot': total_pot,
                        'winner_pot': winner_pot,
                        'commission': commission
                    }
                )

                if len(ROOMS[self.room_name]['players']) >= 2 and ROOMS[self.room_name]['task'] is None:
                    ROOMS[self.room_name]['task'] = asyncio.create_task(self.start_countdown())

    async def start_countdown(self):
        for i in range(10, -1, -1):
            if self.room_name not in ROOMS:
                return
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'timer_update', 'seconds': i}
            )
            await asyncio.sleep(1)

        if self.room_name in ROOMS:
            ROOMS[self.room_name]['status'] = 'PLAYING'
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'game_started'}
            )
            # ቆጠራው ሲያልቅ ቁጥሮችን በራስ-ሰር ማውጣት ይጀምራል
            if ROOMS[self.room_name]['draw_task'] is None:
                ROOMS[self.room_name]['draw_task'] = asyncio.create_task(self.auto_draw_numbers())

    async def auto_draw_numbers(self):
        all_numbers = list(range(1, 76))
        random.shuffle(all_numbers)

        for number in all_numbers:
            if self.room_name not in ROOMS or ROOMS[self.room_name]['status'] != 'PLAYING':
                break
            
            ROOMS[self.room_name]['drawn_numbers'].append(number)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'number_drawn',
                    'number': number,
                    'all_drawn': ROOMS[self.room_name]['drawn_numbers']
                }
            )
            await asyncio.sleep(3)  # በየ 3 ሰከንዱ አዲስ ቁጥር ይወጣል

    # Event Handlers
    async def cartela_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'cartela_selected',
            'cartela_id': event['cartela_id'],
            'player_name': event['player_name'],
            'total_pot': event['total_pot'],
            'winner_pot': event['winner_pot'],
            'commission': event['commission']
        }))

    async def timer_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'timer_update',
            'seconds': event['seconds']
        }))

    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started'
        }))

    async def number_drawn(self, event):
        await self.send(text_data=json.dumps({
            'type': 'number_drawn',
            'number': event['number'],
            'drawn_numbers': event['all_drawn']
        }))
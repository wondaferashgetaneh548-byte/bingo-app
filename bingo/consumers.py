import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

# በሜሞሪ ውስጥ የክፍሎችን ሁኔታ መያዣ dictionary
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

class BingoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'bingo_{self.room_name}'
        self.user = self.scope['user']
        self.username = self.user.username if self.user.is_authenticated else "Guest"

        try:
            self.stake = int(self.room_name.replace('room_', ''))
        except ValueError:
            self.stake = 10

        if self.room_name not in ROOMS:
            ROOMS[self.room_name] = {
                'status': 'WAITING',
                'players': {}, # username: {'cartela_id': id, 'matrix': matrix}
                'drawn_numbers': [],
                'task': None
            }

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # ያለውን የክፍል ሁኔታ ለገባው ተጫዋች መላክ
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
            'players': players_summary
        }))

        # አዲስ ሰው ከገባ እና ቀድሞ የመረጠው ካርቴላ ካለ ማሳየት
        if self.username in ROOMS[self.room_name]['players']:
            my_info = ROOMS[self.room_name]['players'][self.username]
            await self.send(text_data=json.dumps({
                'type': 'my_cartela_data',
                'cartela_id': my_info['cartela_id'],
                'matrix': my_info['matrix']
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

                # ለተጫዋቹ የራሱን ካርቴላ መላክ
                await self.send(text_data=json.dumps({
                    'type': 'my_cartela_data',
                    'cartela_id': cartela_id,
                    'matrix': matrix
                }))

                # ለክፍሉ አዲስ የተያዘውን ካርቴላና የብር መጠኑን ማሳወቅ
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

                # ቢያንስ 2 ተጫዋች ካለና ጨዋታው ካልተጀመረ Timer ማስጀመር
                if len(ROOMS[self.room_name]['players']) >= 2 and ROOMS[self.room_name]['task'] is None:
                    ROOMS[self.room_name]['task'] = asyncio.create_task(self.start_countdown())

    async def start_countdown(self):
        for i in range(10, -1, -1):
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'timer_update', 'seconds': i}
            )
            await asyncio.sleep(1)

        ROOMS[self.room_name]['status'] = 'PLAYING'
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'game_started'}
        )
        await self.draw_numbers()

    async def draw_numbers(self):
        all_numbers = list(range(1, 76))
        random.shuffle(all_numbers)

        for num in all_numbers:
            if ROOMS[self.room_name]['status'] != 'PLAYING':
                break
            ROOMS[self.room_name]['drawn_numbers'].append(num)
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'number_drawn', 'number': num}
            )
            await asyncio.sleep(3)

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
            'number': event['number']
        }))
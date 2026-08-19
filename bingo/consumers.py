import json
import asyncio
import random
from channels.generic.websocket import AsyncWebsocketConsumer

ROOMS = {}

def generate_cartela_matrix():
    b = random.sample(range(1, 16), 5)
    i = random.sample(range(16, 31), 5)
    n = random.sample(range(31, 46), 4)
    g = random.sample(range(46, 61), 5)
    o = random.sample(range(61, 76), 5)

    matrix = []
    for r in range(5):
        row = [
            b[r],
            i[r],
            "FREE" if r == 2 else n[r if r < 2 else r - 1],
            g[r],
            o[r]
        ]
        matrix.append(row)
    return matrix

def check_bingo_win(matrix, drawn_numbers):
    """ማንኛውም 1 መስመር (አግድም፣ ቁመት፣ ዲያጎናል) መሞላቱን ያረጋግጣል"""
    drawn_set = set(drawn_numbers)
    drawn_set.add("FREE") # FREE ሁልጊዜ እንደወጣ ይቆጠራል

    # 1. አግድም መስመሮችን መፈተሽ (Rows)
    for row in matrix:
        if all(cell in drawn_set for cell in row):
            return True

    # 2. የቁመት መስመሮችን መፈተሽ (Columns)
    for col in range(5):
        if all(matrix[row][col] in drawn_set for row in range(5)):
            return True

    # 3. ዲያጎናል 1 (\)
    if all(matrix[i][i] in drawn_set for i in range(5)):
        return True

    # 4. ዲያጎናል 2 (/)
    if all(matrix[i][4 - i] in drawn_set for i in range(5)):
        return True

    return False

class BingoRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.username = self.user.username if self.user.is_authenticated else f"Guest_{random.randint(100, 999)}"
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'bingo_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.room_name not in ROOMS:
            self.reset_room_state()

        players_data = {p_name: p_info['cartela_id'] for p_name, p_info in ROOMS[self.room_name]['players'].items()}

        await self.send(text_data=json.dumps({
            'type': 'room_state',
            'status': ROOMS[self.room_name]['status'],
            'timer': ROOMS[self.room_name]['timer'],
            'players': players_data,
            'drawn_numbers': ROOMS[self.room_name]['drawn_numbers']
        }))

        if ROOMS[self.room_name]['status'] == 'WAITING' and ROOMS[self.room_name]['timer_task'] is None:
            ROOMS[self.room_name]['timer_task'] = asyncio.create_task(self.start_room_timer())

    def reset_room_state(self):
        ROOMS[self.room_name] = {
            'status': 'WAITING',
            'timer': 45,
            'players': {},
            'timer_task': None,
            'drawn_numbers': [],
            'available_numbers': list(range(1, 76))
        }

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'select_cartela' and ROOMS[self.room_name]['status'] == 'WAITING':
            try:
                cartela_id = int(data.get('cartela_id'))
            except (ValueError, TypeError):
                return

            username = self.username
            taken_ids = [p['cartela_id'] for p in ROOMS[self.room_name]['players'].values()]

            if cartela_id not in taken_ids:
                matrix = generate_cartela_matrix()
                ROOMS[self.room_name]['players'][username] = {
                    'cartela_id': cartela_id,
                    'matrix': matrix
                }

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
                        'player_name': username
                    }
                )

    async def start_room_timer(self):
        while ROOMS[self.room_name]['timer'] > 0:
            await asyncio.sleep(1)
            ROOMS[self.room_name]['timer'] -= 1

            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'timer_tick', 'time_left': ROOMS[self.room_name]['timer']}
            )

        ROOMS[self.room_name]['status'] = 'PLAYING'
        await self.channel_layer.group_send(self.room_group_name, {'type': 'game_start'})
        asyncio.create_task(self.start_drawing_numbers())

    async def start_drawing_numbers(self):
        numbers = ROOMS[self.room_name]['available_numbers']
        random.shuffle(numbers)

        for num in numbers:
            if ROOMS[self.room_name]['status'] != 'PLAYING':
                break
                
            await asyncio.sleep(3)
            ROOMS[self.room_name]['drawn_numbers'].append(num)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'number_drawn',
                    'number': num,
                    'all_drawn': ROOMS[self.room_name]['drawn_numbers']
                }
            )

            # አሸናፊ ማረጋገጥ
            winner_found = False
            for player_name, player_info in ROOMS[self.room_name]['players'].items():
                if check_bingo_win(player_info['matrix'], ROOMS[self.room_name]['drawn_numbers']):
                    ROOMS[self.room_name]['status'] = 'FINISHED'
                    winner_found = True
                    
                    # ለአሸናፊው ማሳወቅ
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'bingo_winner',
                            'winner_name': player_name,
                            'cartela_id': player_info['cartela_id']
                        }
                    )
                    break

            if winner_found:
                # ከ 6 ሰከንድ በኋላ ክፍሉን ለቀጣዩ ጨዋታ ማዘጋጀት
                await asyncio.sleep(6)
                self.reset_room_state()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {'type': 'reset_game'}
                )
                ROOMS[self.room_name]['timer_task'] = asyncio.create_task(self.start_room_timer())
                break

    # Broadcast Handlers
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

    async def bingo_winner(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner_name': event['winner_name'],
            'cartela_id': event['cartela_id']
        }))

    async def reset_game(self, event):
        await self.send(text_data=json.dumps({'type': 'restart_selection'}))
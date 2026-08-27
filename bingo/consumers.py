import json
import random
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

ROOMS = {}

def generate_cartela_matrix(cartela_id):
    # ለእያንዳንዱ ካርቴላ ቁጥር ቋሚ ቁጥሮች በየ B-I-N-G-O አምዱ እንዲወጡ ማድረግ
    rng = random.Random(int(cartela_id) * 997)
    ranges = {
        'B': range(1, 16),
        'I': range(16, 31),
        'N': range(31, 46),
        'G': range(46, 61),
        'O': range(61, 76)
    }
    
    # N አምድ 4 ቁጥሮች ይወስዳል (መሃሉ FREE ስለሚሆን)
    n_numbers = rng.sample(ranges['N'], 4)
    
    columns = {
        'B': rng.sample(ranges['B'], 5),
        'I': rng.sample(ranges['I'], 5),
        'N': [n_numbers[0], n_numbers[1], 'FREE', n_numbers[2], n_numbers[3]],
        'G': rng.sample(ranges['G'], 5),
        'O': rng.sample(ranges['O'], 5)
    }
    
    matrix = []
    for i in range(5):
        row = [
            columns['B'][i],
            columns['I'][i],
            columns['N'][i],
            columns['G'][i],
            columns['O'][i]
        ]
        matrix.append(row)
    return matrix


def check_bingo_win(matrix, drawn_numbers):
    # 1 መስመር (አግድም፣ ቀጥታ ወይም ዲያጎናል) መዘጋቱን ማረጋገጫ
    drawn_set = set(drawn_numbers)
    drawn_set.add('FREE')
    drawn_set.add('F')

    # Rows (አግድም) ማረጋገጥ
    for row in matrix:
        if all(cell in drawn_set for cell in row):
            return True

    # Columns (ቀጥታ) ማረጋገጥ
    for col_idx in range(5):
        if all(matrix[row_idx][col_idx] in drawn_set for row_idx in range(5)):
            return True

    # Diagonals (ዲያጎናል) ማረጋገጥ
    if all(matrix[i][i] in drawn_set for i in range(5)):
        return True
    if all(matrix[i][4 - i] in drawn_set for i in range(5)):
        return True

    return False


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

        # 1. ተጫዋች ካርቴላ ሲመርጥ
        if action == 'select_cartela' and ROOMS[self.room_name]['status'] == 'WAITING':
            cartela_id = int(data.get('cartela_id'))
            taken_ids = [p['cartela_id'] for p in ROOMS[self.room_name]['players'].values()]

            if cartela_id not in taken_ids:
                matrix = generate_cartela_matrix(cartela_id)
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

                # የመጀመሪያው ተጫዋች ሲገባ የ 45 ሰከንድ ቆጠራ ይጀምራል
                if ROOMS[self.room_name]['task'] is None:
                    ROOMS[self.room_name]['task'] = asyncio.create_task(self.start_countdown())

        # 2. ተጫዋች BINGO ሲል
        elif action == 'claim_bingo' and ROOMS[self.room_name]['status'] == 'PLAYING':
            player_info = ROOMS[self.room_name]['players'].get(self.username)
            if player_info:
                is_win = check_bingo_win(player_info['matrix'], ROOMS[self.room_name]['drawn_numbers'])
                if is_win:
                    ROOMS[self.room_name]['status'] = 'FINISHED'
                    
                    # አውቶማቲክ ቁጥር መሳብ እንዲቆም ማድረግ
                    if ROOMS[self.room_name]['draw_task']:
                        ROOMS[self.room_name]['draw_task'].cancel()

                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_over',
                            'winner': self.username,
                            'cartela_id': player_info['cartela_id']
                        }
                    )
                    
                    # ከ 5 ሰከንድ በኋላ ክፍሉን ለአዲስ ጨዋታ ማጽዳት
                    await asyncio.sleep(5)
                    await self.reset_room_async()

    # የ 45 ሰከንድ ቆጠራ ማስሄጃ
    async def start_countdown(self):
        try:
            for i in range(45, -1, -1):
                if self.room_name not in ROOMS or ROOMS[self.room_name]['status'] != 'WAITING':
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
                if ROOMS[self.room_name]['draw_task'] is None:
                    ROOMS[self.room_name]['draw_task'] = asyncio.create_task(self.auto_draw_numbers())
        except asyncio.CancelledError:
            pass

    # ቁጥሮች በየ 3 ሰከንዱ በራስ-ሰር እንዲወጡ ማድረግ
    async def auto_draw_numbers(self):
        try:
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
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass

    # ክፍሉን ለአዲስ ጨዋታ ማስተካከል እና ለተጫዋቾች ማሳወቅ
    async def reset_room_async(self):
        if self.room_name in ROOMS:
            if ROOMS[self.room_name]['task']:
                ROOMS[self.room_name]['task'].cancel()
            if ROOMS[self.room_name]['draw_task']:
                ROOMS[self.room_name]['draw_task'].cancel()

            ROOMS[self.room_name] = {
                'status': 'WAITING',
                'players': {},
                'drawn_numbers': [],
                'task': None,
                'draw_task': None
            }

            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'room_reset'}
            )

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
        await self.send(text_data=json.dumps({'type': 'game_started'}))

    async def number_drawn(self, event):
        await self.send(text_data=json.dumps({
            'type': 'number_drawn',
            'number': event['number'],
            'drawn_numbers': event['all_drawn']
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner'],
            'cartela_id': event['cartela_id']
        }))

    async def room_reset(self, event):
        await self.send(text_data=json.dumps({
            'type': 'room_reset'
        }))
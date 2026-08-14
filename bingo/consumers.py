import json
import asyncio
import random
from channels.generic.websocket import AsyncWebsocketConsumer

class BingoConsumer(AsyncWebsocketConsumer):
    # በክፍል (Room) ደረጃ የወጡ ቁጥሮችን እና የጨዋታ ሁኔታን መያዣ
    rooms = {}

    async def connect(self):
        # KeyError እንዳይፈጠር get() በመጠቀም default room 'default' ይሰጠዋል
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'default')
        self.room_group_name = f'bingo_{self.room_name}'

        if self.room_name not in BingoConsumer.rooms:
            BingoConsumer.rooms[self.room_name] = {
                'drawn_numbers': [],
                'is_running': False,
                'task': None
            }

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
        action = data.get('action')

        room = BingoConsumer.rooms[self.room_name]

        # ⚡ 1. Frontend ከሚልካቸው ሁለቱም የስም አይነቶች ጋር እንዲስማማ የተደረገ ('start_drawing_numbers' OR 'start_game')
        if action in ['start_drawing_numbers', 'start_game']:
            if not room['is_running']:
                room['is_running'] = True
                room['drawn_numbers'] = []
                # በየ 3 ሰከንዱ ቁጥር የሚያወጣ Loop ማስነሳት
                room['task'] = asyncio.create_task(self.auto_draw_numbers())

        # 2. ተጫዋች ቢንጎ (Bingo) ሲል
        elif action == 'claim_bingo':
            player_card = data.get('card') # የተጫዋቹ 25 ቁጥሮች
            winner_name = data.get('winner_name', 'አንድ ተጫዋች')
            winning_card_no = data.get('winning_card_no', 1)
            prize_pool = data.get('prize_pool', 0)
            winner_id = data.get('winner_id', '')

            # ካርድ ከተላከ ማረጋገጥ፣ ካልተላከ ደግሞ በቀጥታ ማሸነፉን ማወጅ
            is_valid = True
            if player_card:
                is_valid = self.check_bingo_win(player_card, room['drawn_numbers'])

            if is_valid:
                room['is_running'] = False
                if room['task']:
                    room['task'].cancel()

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'bingo_message',
                        'action': 'game_over',
                        'winner_id': winner_id,
                        'winner_name': winner_name,
                        'winning_card_no': winning_card_no,
                        'prize_pool': prize_pool,
                        'message': f'🎉 ቢንጎ! {winner_name} አሸንፈዋል!'
                    }
                )

    async def auto_draw_numbers(self):
        room = BingoConsumer.rooms[self.room_name]
        available_numbers = list(range(1, 76))
        random.shuffle(available_numbers)
        
        while room['is_running'] and available_numbers:
            await asyncio.sleep(3) # በየ 3 ሰከንዱ ይወጣል
            
            if not room['is_running']:
                break

            num = available_numbers.pop(0)
            room['drawn_numbers'].append(num)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'bingo_message',
                    'action': 'new_number',
                    'number': num
                }
            )

    async def bingo_message(self, event):
        # ለ Frontend መረጃውን መላክ
        await self.send(text_data=json.dumps(event))

    def check_bingo_win(self, card, drawn_numbers):
        if not card or len(card) < 25:
            return False

        drawn_set = set(drawn_numbers)
        
        # 5x5 Matrix መፍጠር
        matrix = []
        for i in range(5):
            matrix.append(card[i*5 : (i+1)*5])

        # 横 (Row) ማረጋገጥ
        for row in matrix:
            if all(num in ["FREE", "ነፃ", "F"] or int(num) in drawn_set for num in row):
                return True

        # 縦 (Column) ማረጋገጥ
        for col in range(5):
            if all(matrix[row][col] in ["FREE", "ነፃ", "F"] or int(matrix[row][col]) in drawn_set for row in range(5)):
                return True

        # Diagonal ማረጋገጥ
        if all(matrix[i][i] in ["FREE", "ነፃ", "F"] or int(matrix[i][i]) in drawn_set for i in range(5)):
            return True
            
        if all(matrix[i][4-i] in ["FREE", "ነፃ", "F"] or int(matrix[i][4-i]) in drawn_set for i in range(5)):
            return True

        return False
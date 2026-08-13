import json
import asyncio
import random
from channels.generic.websocket import AsyncWebsocketConsumer

class BingoConsumer(AsyncWebsocketConsumer):
    # በክፍል (Room) ደረጃ የወጡ ቁጥሮችን እና የጨዋታ ሁኔታን መያዣ
    rooms = {}

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'bingo_{self.room_name}'

        if self.room_name not in self.rooms:
            self.rooms[self.room_name] = {
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

        # 1. ጨዋታ ሲጀመር (Start Game)
        if action == 'start_game':
            room = self.rooms[self.room_name]
            if not room['is_running']:
                room['is_running'] = True
                room['drawn_numbers'] = []
                # በየ 3 ሰከንዱ ቁጥር የሚያወጣ Loop ማስነሳት
                room['task'] = asyncio.create_task(self.auto_draw_numbers())

        # 2. ተጫዋች ቢንጎ (Bingo) ሲል
        elif action == 'claim_bingo':
            player_card = data.get('card') # የተጫዋቹ 25 ቁጥሮች
            if self.check_bingo_win(player_card, self.rooms[self.room_name]['drawn_numbers']):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'bingo_message',
                        'action': 'game_over',
                        'winner': self.channel_name,
                        'message': '🎉 ቢንጎ! አሸንፈዋል!'
                    }
                )
                self.rooms[self.room_name]['is_running'] = False
                if self.rooms[self.room_name]['task']:
                    self.rooms[self.room_name]['task'].cancel()

    async def auto_draw_numbers(self):
        room = self.rooms[self.room_name]
        available_numbers = list(range(1, 76))
        
        while room['is_running'] and available_numbers:
            await asyncio.sleep(3) # በየ 3 ሰከንዱ ይወጣል
            num = random.choice(available_numbers)
            available_numbers.remove(num)
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
        await self.send(text_data=json.dumps(event))

    def check_bingo_win(self, card, drawn_numbers):
        # 5x5 Grid Check (መስመር፣ አምድ ወይም ዲያጎናል ሙሉ መሆን አለበት)
        # FREE (መካከለኛው) ሁልጊዜ እንደወጣ ይቆጠራል
        drawn_set = set(drawn_numbers)
        
        # 5x5 Matrix መፍጠር
        matrix = []
        for i in range(5):
            matrix.append(card[i*5 : (i+1)*5])

        # 横 (Row) ማረጋገጥ
        for row in matrix:
            if all(num == "FREE" or num in drawn_set for num in row):
                return True

        # 縦 (Column) ማረጋገጥ
        for col in range(5):
            if all(matrix[row][col] == "FREE" or matrix[row][col] in drawn_set for row in range(5)):
                return True

        return False
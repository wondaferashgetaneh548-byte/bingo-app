import json
import asyncio
import random
from channels.generic.websocket import AsyncWebsocketConsumer

class BingoConsumer(AsyncWebsocketConsumer):
    room_group_name = 'bingo_room'
    is_timer_running = False
    is_game_active = False
    countdown_seconds = 45
    taken_cards = {}  # {'card_no': 'username'}

    async def connect(self):
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # አዲስ ተጫዋች ሲገባ የተያዙ ካርቴላዎችን መረጃ ይላክለታል
        await self.send(text_data=json.dumps({
            'action': 'room_state',
            'taken_cards': BingoConsumer.taken_cards
        }))

        # የመጀመሪያው ተጫዋች ሲገባ የ 45 ሰከንድ ቆጠራው ይጀምራል
        if not BingoConsumer.is_timer_running and not BingoConsumer.is_game_active:
            BingoConsumer.is_timer_running = True
            asyncio.create_task(self.start_room_timer())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        # 1. ተጫዋች ካርቴላ ሲመርጥ
        if action == 'select_card':
            card_no = str(data.get('card_no'))
            username = data.get('username')

            BingoConsumer.taken_cards[card_no] = username
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'card_selected_broadcast',
                    'card_no': card_no,
                    'username': username
                }
            )

        # 2. ተጫዋች ቢንጎ ሲል
        elif action == 'claim_bingo':
            BingoConsumer.is_game_active = False
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_over_broadcast',
                    'winner_id': data.get('winner_id'),
                    'winner_name': data.get('winner_name'),
                    'winning_card_no': data.get('winning_card_no'),
                    'prize_pool': data.get('prize_pool')
                }
            )

    async def start_room_timer(self):
        current = self.countdown_seconds
        while current >= 0:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'timer_update',
                    'time_left': current
                }
            )
            await asyncio.sleep(1)
            current -= 1

        # 45 ሰከንዱ ሲያልቅ ጨዋታው ይጀምራል
        BingoConsumer.is_timer_running = False
        BingoConsumer.is_game_active = True
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'start_game_all'}
        )

        # ጨዋታው ሲጀምር ቁጥሮችን መጥራት ይጀምራል
        asyncio.create_task(self.call_bingo_numbers())

    async def call_bingo_numbers(self):
        numbers = list(range(1, 76))
        random.shuffle(numbers)

        for num in numbers:
            if not BingoConsumer.is_game_active:
                break

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'broadcast_number',
                    'number': num
                }
            )
            await asyncio.sleep(3)

    async def timer_update(self, event):
        await self.send(text_data=json.dumps({
            'action': 'timer_tick',
            'time_left': event['time_left']
        }))

    async def start_game_all(self, event):
        await self.send(text_data=json.dumps({
            'action': 'game_started'
        }))

    async def card_selected_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'action': 'card_selected_broadcast',
            'card_no': event['card_no'],
            'username': event['username']
        }))

    async def broadcast_number(self, event):
        await self.send(text_data=json.dumps({
            'number': event['number']
        }))

    async def game_over_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'action': 'game_over',
            'winner_id': event['winner_id'],
            'winner_name': event['winner_name'],
            'winning_card_no': event['winning_card_no'],
            'prize_pool': event['prize_pool']
        }))
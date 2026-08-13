const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
    cors: { origin: "*" }
});

const players = {};
let calledNumbers = [];
let gameInterval = null;
let isGameRunning = false;

// Socket.io Multiplayer Logic
io.on('connection', (socket) => {
    console.log(`ተጫዋች ተገናኝቷል: ${socket.id}`);

    // ተጫዋች ሲመዘገብ
    socket.on('register_player', (userData) => {
        players[socket.id] = {
            id: userData.userId,
            name: userData.firstName || 'ተጫዋች',
            balance: 500,
            socketId: socket.id
        };
        // የነበሩትን ተጫዋቾች ብዛት ለሁሉም ማሳወቅ
        io.emit('update_player_count', Object.keys(players).length);
    });

    // አድሚን ወይም የመጀመሪያው ተጫዋች ጨዋታ ሲያስጀምር
    socket.on('start_game', () => {
        if (isGameRunning) return;
        
        isGameRunning = true;
        calledNumbers = [];
        io.emit('game_started');

        gameInterval = setInterval(() => {
            if (calledNumbers.length >= 75) {
                clearInterval(gameInterval);
                isGameRunning = false;
                return;
            }

            let num;
            do {
                num = Math.floor(Math.random() * 75) + 1;
            } while (calledNumbers.includes(num));

            calledNumbers.push(num);
            
            // የተጠራውን ቁጥር ለሁሉም ተጫዋቾች በአንድ ጊዜ መላክ
            io.emit('number_called', { number: num, history: calledNumbers });

        }, 3500); // በየ 3.5 ሰከንዱ ቁጥር ይጠራል
    });

    // ተጫዋች ሲወጣ
    socket.on('disconnect', () => {
        delete players[socket.id];
        io.emit('update_player_count', Object.keys(players).length);
        console.log(`ተጫዋች ወጥቷል: ${socket.id}`);
    });
});

const PORT = 5000;
server.listen(PORT, () => console.log(`Multiplayer Bingo Server running on port ${PORT}`));
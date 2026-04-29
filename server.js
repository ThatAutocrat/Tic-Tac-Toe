const express = require('express');
const { WebSocketServer } = require('ws');
const http = require('http');
const path = require('path');
const crypto = require('crypto');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });

app.use(express.static(path.join(__dirname, 'public')));

const rooms = new Map();

function makeRoomId() {
  return crypto.randomBytes(3).toString('hex').toUpperCase();
}

function checkWin(board) {
  const lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]];
  for (const [a,b,c] of lines) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) return board[a];
  }
  return null;
}

function send(ws, data) {
  if (ws.readyState === 1) ws.send(JSON.stringify(data));
}

wss.on('connection', (ws) => {
  ws.roomId = null;
  ws.role = null;

  ws.on('message', (raw) => {
    let msg;
    try { msg = JSON.parse(raw); } catch { return; }

    if (msg.type === 'create') {
      const roomId = makeRoomId();
      rooms.set(roomId, {
        players: [ws],
        board: Array(9).fill(null),
        turn: 'X',
        scores: { X: 0, O: 0, D: 0 }
      });
      ws.roomId = roomId;
      ws.role = 'X';
      send(ws, { type: 'created', roomId, role: 'X' });
    }

    else if (msg.type === 'join') {
      const room = rooms.get(msg.roomId);
      if (!room) return send(ws, { type: 'error', msg: 'Room not found' });
      if (room.players.length >= 2) return send(ws, { type: 'error', msg: 'Room is full' });
      room.players.push(ws);
      ws.roomId = msg.roomId;
      ws.role = 'O';
      send(ws, { type: 'joined', roomId: msg.roomId, role: 'O', board: room.board, turn: room.turn, scores: room.scores });
      send(room.players[0], { type: 'opponent_joined', board: room.board, turn: room.turn, scores: room.scores });
    }

    else if (msg.type === 'move') {
      const room = rooms.get(ws.roomId);
      if (!room) return;
      if (room.turn !== ws.role) return;
      if (room.board[msg.index] !== null) return;

      room.board[msg.index] = ws.role;
      const winner = checkWin(room.board);
      const draw = !winner && room.board.every(Boolean);

      if (winner) room.scores[winner]++;
      if (draw) room.scores.D++;

      const state = { type: 'update', board: room.board, turn: room.turn, winner, draw, scores: room.scores };

      if (!winner && !draw) room.turn = room.turn === 'X' ? 'O' : 'X';
      state.turn = room.turn;

      room.players.forEach(p => send(p, state));
    }

    else if (msg.type === 'reset') {
      const room = rooms.get(ws.roomId);
      if (!room) return;
      room.board = Array(9).fill(null);
      room.turn = 'X';
      room.players.forEach(p => send(p, { type: 'reset', board: room.board, turn: room.turn, scores: room.scores }));
    }
  });

  ws.on('close', () => {
    const room = rooms.get(ws.roomId);
    if (!room) return;
    room.players = room.players.filter(p => p !== ws);
    if (room.players.length === 0) {
      rooms.delete(ws.roomId);
    } else {
      send(room.players[0], { type: 'opponent_left' });
    }
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));

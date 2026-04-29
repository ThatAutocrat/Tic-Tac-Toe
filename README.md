# ✕ ○ TicTacToe

Real-time multiplayer Tic Tac Toe built on Node.js + WebSockets with a single-binary static frontend.

---

## Stack
- **Runtime** — Node.js
- **Transport** — `ws` (WebSocket)
- **Server** — Express (static file serving)
- **Frontend** — Vanilla JS, no framework, no bundler

## Modes
| Mode | Transport |
|------|-----------|
| vs AI | Local state (minimax-lite) |
| Local PvP | Local state |
| Online PvP | WebSocket rooms |

## Deploy
```bash
npm install && npm start
```
Reads `process.env.PORT` — drop it anywhere (Railway, Render, Fly).

## Repo Structure

├── server.js        # WS server + room logic
├── package.json
└── public/
└── index.html   # Entire frontend, self-contained

---

> No build step. No framework. No nonsense.

# ✕ ○ TicTacToe

Real-time multiplayer Tic Tac Toe built on Node.js + WebSockets with a single-binary static frontend.

Can play mutiplayer, AI, or the same device.
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


---

> No build step. No framework. No nonsense.

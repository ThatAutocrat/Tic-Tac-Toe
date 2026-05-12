# ✕ ○ TicTacToe

Real-time multiplayer Tic Tac Toe built on Node.js + WebSockets with a single-binary static frontend.

<img width="507" height="796" alt="image" src="https://github.com/user-attachments/assets/0a6d3db4-8ca1-4c1d-84b6-9bd01989b706" />


### Can play mutiplayer, AI, or the same device.
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

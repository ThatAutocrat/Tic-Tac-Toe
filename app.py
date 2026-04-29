import os
from flask import Flask, jsonify, request, render_template_string
from tictactoe import checkWin

app = Flask(__name__)

# ---------------------------------------------------------------------------
# In-memory game state (single shared game; fine for a demo / Railway deploy)
# ---------------------------------------------------------------------------
def _fresh_state():
    return {
        "xState": [0] * 9,
        "zState": [0] * 9,
        "turn": 1,        # 1 = X's turn, 0 = O's turn
        "winner": None,   # "X", "O", or "Draw"
        "over": False,
    }

game = _fresh_state()

# ---------------------------------------------------------------------------
# HTML template – a self-contained single-page UI
# ---------------------------------------------------------------------------
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Tic-Tac-Toe</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #1a1a2e;
      color: #eee;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      gap: 24px;
    }
    h1 { font-size: 2.4rem; letter-spacing: 2px; color: #e94560; }
    #status {
      font-size: 1.2rem;
      min-height: 1.6rem;
      color: #a8dadc;
      font-weight: 600;
    }
    #board {
      display: grid;
      grid-template-columns: repeat(3, 110px);
      grid-template-rows: repeat(3, 110px);
      gap: 8px;
    }
    .cell {
      background: #16213e;
      border: 2px solid #0f3460;
      border-radius: 12px;
      font-size: 2.8rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s, transform 0.1s;
      user-select: none;
    }
    .cell:hover:not(.taken) { background: #0f3460; transform: scale(1.05); }
    .cell.taken { cursor: default; }
    .cell.x { color: #e94560; }
    .cell.o { color: #a8dadc; }
    button#restart {
      padding: 10px 32px;
      font-size: 1rem;
      border: none;
      border-radius: 8px;
      background: #e94560;
      color: #fff;
      cursor: pointer;
      font-weight: 600;
      letter-spacing: 1px;
      transition: background 0.15s;
    }
    button#restart:hover { background: #c73652; }
    #api-hint {
      font-size: 0.78rem;
      color: #555;
      margin-top: 8px;
    }
  </style>
</head>
<body>
  <h1>Tic-Tac-Toe</h1>
  <div id="status">Loading…</div>
  <div id="board"></div>
  <button id="restart" onclick="newGame()">New Game</button>
  <p id="api-hint">REST API: GET /state &nbsp;|&nbsp; POST /move {"position": 0-8} &nbsp;|&nbsp; POST /new-game</p>

  <script>
    const SYMBOLS = ['0','1','2','3','4','5','6','7','8'];

    async function fetchState() {
      const res = await fetch('/state');
      return res.json();
    }

    async function render() {
      const state = await fetchState();
      const board  = document.getElementById('board');
      const status = document.getElementById('status');

      board.innerHTML = '';
      for (let i = 0; i < 9; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        if (state.xState[i]) {
          cell.textContent = 'X';
          cell.classList.add('taken', 'x');
        } else if (state.zState[i]) {
          cell.textContent = 'O';
          cell.classList.add('taken', 'o');
        } else {
          cell.textContent = i;
          if (!state.over) {
            cell.onclick = () => makeMove(i);
          } else {
            cell.classList.add('taken');
          }
        }
        board.appendChild(cell);
      }

      if (state.over) {
        if (state.winner === 'Draw') {
          status.textContent = "It's a draw!";
        } else {
          status.textContent = `${state.winner} wins! 🎉`;
        }
      } else {
        status.textContent = `${state.turn === 1 ? 'X' : 'O'}'s turn`;
      }
    }

    async function makeMove(position) {
      await fetch('/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ position }),
      });
      render();
    }

    async function newGame() {
      await fetch('/new-game', { method: 'POST' });
      render();
    }

    render();
  </script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/state")
def state():
    """Return the current game state as JSON."""
    return jsonify(game)


@app.route("/new-game", methods=["POST"])
def new_game():
    """Reset the board and start a fresh game."""
    global game
    game = _fresh_state()
    return jsonify({"message": "New game started", "state": game})


@app.route("/move", methods=["POST"])
def move():
    """
    Make a move.

    Request body (JSON): { "position": <int 0-8> }

    Returns the updated game state or an error message.
    """
    if game["over"]:
        return jsonify({"error": "Game is already over. Start a new game."}), 400

    data = request.get_json(silent=True) or {}
    position = data.get("position")

    if position is None or not isinstance(position, int) or not (0 <= position <= 8):
        return jsonify({"error": "Invalid position. Must be an integer between 0 and 8."}), 400

    if game["xState"][position] or game["zState"][position]:
        return jsonify({"error": "Cell already taken. Choose another position."}), 400

    # Apply the move
    if game["turn"] == 1:
        game["xState"][position] = 1
    else:
        game["zState"][position] = 1

    # Check for a winner using the original logic
    result = checkWin(game["xState"], game["zState"])
    if result == 1:
        game["winner"] = "X"
        game["over"] = True
    elif result == 0:
        game["winner"] = "O"
        game["over"] = True
    elif all(game["xState"][i] or game["zState"][i] for i in range(9)):
        # All cells filled with no winner → draw
        game["winner"] = "Draw"
        game["over"] = True
    else:
        game["turn"] = 1 - game["turn"]

    return jsonify(game)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

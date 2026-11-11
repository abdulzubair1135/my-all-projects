from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import random
from typing import List, Dict, Optional
from pydantic import BaseModel

app = FastAPI(title="Tic-Tac-Toe Game", description="A modern, sleek Tic-Tac-Toe game with AI opponent")

# Game state
game_state = {
    "board": [""] * 9,
    "current_player": "X",  # X always goes first
    "winner": None,
    "game_over": False,
    "scores": {"X": 0, "O": 0, "draw": 0}
}

def check_winner(board: List[str]) -> Optional[str]:
    """Check if there's a winner on the board"""
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    
    for pattern in win_patterns:
        if board[pattern[0]] and board[pattern[0]] == board[pattern[1]] == board[pattern[2]]:
            return board[pattern[0]]
    return None

def is_board_full(board: List[str]) -> bool:
    """Check if the board is full"""
    return all(cell != "" for cell in board)

def get_available_moves(board: List[str]) -> List[int]:
    """Get all available moves on the board"""
    return [i for i, cell in enumerate(board) if cell == ""]

def minimax(board: List[str], depth: int, is_maximizing: bool, alpha: float = -float("inf"), beta: float = float("inf")) -> int:
    """
    Minimax algorithm with alpha-beta pruning for AI decision making
    AI is 'O' (maximizing player), Human is 'X' (minimizing player)
    """
    winner = check_winner(board)
    
    # Base cases
    if winner == "O":
        return 10 - depth  # AI wins
    elif winner == "X":
        return depth - 10  # Human wins
    elif is_board_full(board):
        return 0  # Draw
    
    if is_maximizing:
        # AI's turn (O)
        best_score = -float("inf")
        for move in get_available_moves(board):
            board[move] = "O"
            score = minimax(board, depth + 1, False, alpha, beta)
            board[move] = ""
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Alpha-beta pruning
        return best_score
    else:
        # Human's turn (X)
        best_score = float("inf")
        for move in get_available_moves(board):
            board[move] = "X"
            score = minimax(board, depth + 1, True, alpha, beta)
            board[move] = ""
            best_score = min(score, best_score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # Alpha-beta pruning
        return best_score

def ai_move(board: List[str]) -> int:
    """
    Make AI move using minimax algorithm with alpha-beta pruning
    Returns the best move index
    """
    available_moves = get_available_moves(board)
    
    if not available_moves:
        return -1
    
    # If only one move left, take it
    if len(available_moves) == 1:
        return available_moves[0]
    
    # Check if AI can win immediately
    for move in available_moves:
        board[move] = "O"
        if check_winner(board) == "O":
            board[move] = ""
            return move
        board[move] = ""
    
    # Check if human can win next turn and block
    for move in available_moves:
        board[move] = "X"
        if check_winner(board) == "X":
            board[move] = ""
            return move
        board[move] = ""
    
    # Use minimax to find optimal move
    best_score = -float("inf")
    best_move = available_moves[0]
    
    for move in available_moves:
        board[move] = "O"
        score = minimax(board, 0, False)  # AI is maximizing, so next is human's turn (False)
        board[move] = ""
        
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

def reset_game():
    """Reset the game state"""
    game_state["board"] = [""] * 9
    game_state["current_player"] = "X"
    game_state["winner"] = None
    game_state["game_over"] = False

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main game interface"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tic-Tac-Toe</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
            
            * {
                font-family: 'Inter', sans-serif;
            }
            
            .cell {
                width: 100px;
                height: 100px;
                font-size: 3rem;
                font-weight: 700;
                transition: all 0.2s ease;
                cursor: pointer;
                border: 2px solid #e5e7eb;
                display: flex;
                align-items: center;
                justify-content: center;
                background: white;
                border-radius: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                user-select: none;
            }
            
            .cell:hover:not(.disabled) {
                transform: scale(1.02);
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                border-color: #6366f1;
            }
            
            .cell.disabled {
                cursor: not-allowed;
                opacity: 0.7;
            }
            
            .cell.x {
                color: #6366f1;
            }
            
            .cell.o {
                color: #ec4899;
            }
            
            .cell.winning {
                background: #f0fdf4;
                border-color: #22c55e;
                animation: pulse 0.5s ease-in-out 3;
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
            }
            
            .score-card {
                background: white;
                padding: 1rem 1.5rem;
                border-radius: 12px;
                border: 1px solid #e5e7eb;
                text-align: center;
                min-width: 80px;
                transition: all 0.3s ease;
            }
            
            .score-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            }
            
            .board-container {
                background: #f8fafc;
                padding: 2rem;
                border-radius: 20px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            }
            
            .status-badge {
                display: inline-block;
                padding: 0.5rem 1.5rem;
                border-radius: 9999px;
                font-weight: 600;
                font-size: 0.875rem;
            }
            
            button {
                transition: all 0.2s ease;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }
            
            button:active {
                transform: translateY(0px);
            }
            
            .glow-effect {
                animation: glow 2s ease-in-out infinite;
            }
            
            @keyframes glow {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
            
            .thinking-dots::after {
                content: '...';
                animation: dots 1.5s steps(3, end) infinite;
            }
            
            @keyframes dots {
                0% { content: ''; }
                33% { content: '.'; }
                66% { content: '..'; }
                100% { content: '...'; }
            }
            
            @media (max-width: 640px) {
                .cell {
                    width: 80px;
                    height: 80px;
                    font-size: 2.5rem;
                }
                .board-container {
                    padding: 1rem;
                }
                .score-card {
                    min-width: 60px;
                    padding: 0.75rem 1rem;
                }
            }
        </style>
    </head>
    <body class="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 flex items-center justify-center p-4">
        <div id="app" class="w-full max-w-2xl">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-4xl font-bold text-indigo-600 mb-2">Tic-Tac-Toe</h1>
                <p class="text-gray-600">You are <span class="font-bold text-indigo-600">X</span> • AI is <span class="font-bold text-pink-500">O</span></p>
            </div>
            
            <!-- Game Board -->
            <div class="board-container mx-auto max-w-md">
                <div id="status" class="text-center mb-6">
                    <span id="statusText" class="status-badge bg-white text-gray-700 border border-gray-200">
                        Your turn
                    </span>
                </div>
                
                <div class="grid grid-cols-3 gap-3 mb-6">
                    <div class="cell" data-index="0" onclick="makeMove(0)"></div>
                    <div class="cell" data-index="1" onclick="makeMove(1)"></div>
                    <div class="cell" data-index="2" onclick="makeMove(2)"></div>
                    <div class="cell" data-index="3" onclick="makeMove(3)"></div>
                    <div class="cell" data-index="4" onclick="makeMove(4)"></div>
                    <div class="cell" data-index="5" onclick="makeMove(5)"></div>
                    <div class="cell" data-index="6" onclick="makeMove(6)"></div>
                    <div class="cell" data-index="7" onclick="makeMove(7)"></div>
                    <div class="cell" data-index="8" onclick="makeMove(8)"></div>
                </div>
                
                <div class="flex justify-center gap-4 flex-wrap">
                    <button onclick="resetGame()" class="px-6 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 shadow-md">
                        New Game
                    </button>
                    <button onclick="resetScores()" class="px-6 py-2 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 shadow-md">
                        Reset Scores
                    </button>
                </div>
            </div>
            
            <!-- Score Board -->
            <div class="mt-8 flex justify-center gap-6 flex-wrap">
                <div class="score-card">
                    <div class="text-sm text-gray-500 font-medium">Player</div>
                    <div class="text-2xl font-bold text-indigo-600" id="scoreX">0</div>
                </div>
                <div class="score-card">
                    <div class="text-sm text-gray-500 font-medium">Draws</div>
                    <div class="text-2xl font-bold text-gray-600" id="scoreDraw">0</div>
                </div>
                <div class="score-card">
                    <div class="text-sm text-gray-500 font-medium">AI</div>
                    <div class="text-2xl font-bold text-pink-500" id="scoreO">0</div>
                </div>
            </div>
        </div>

        <script>
            let currentBoard = Array(9).fill("");
            let currentPlayer = "X";
            let gameOver = false;
            let isProcessing = false;
            
            const statusText = document.getElementById("statusText");
            const cells = document.querySelectorAll(".cell");
            
            async function updateGameState() {
                try {
                    const response = await fetch("/api/game/state");
                    const data = await response.json();
                    
                    currentBoard = data.board;
                    currentPlayer = data.current_player;
                    gameOver = data.game_over;
                    
                    // Update board
                    cells.forEach((cell, index) => {
                        const value = data.board[index];
                        cell.textContent = value;
                        cell.className = "cell";
                        if (value) {
                            cell.classList.add(value.toLowerCase());
                        }
                        if (gameOver || value || isProcessing || currentPlayer === "O") {
                            cell.classList.add("disabled");
                        }
                    });
                    
                    // Update status
                    if (data.winner) {
                        if (data.winner === "X") {
                            statusText.textContent = "🎉 You win!";
                            statusText.className = "status-badge bg-green-100 text-green-700 border border-green-300";
                            highlightWinningCells();
                        } else if (data.winner === "O") {
                            statusText.textContent = "🤖 AI wins!";
                            statusText.className = "status-badge bg-red-100 text-red-700 border border-red-300";
                            highlightWinningCells();
                        } else if (data.winner === "draw") {
                            statusText.textContent = "🤝 It's a draw!";
                            statusText.className = "status-badge bg-yellow-100 text-yellow-700 border border-yellow-300";
                        }
                    } else if (data.game_over) {
                        statusText.textContent = "Game over";
                        statusText.className = "status-badge bg-gray-100 text-gray-700 border border-gray-300";
                    } else if (data.current_player === "X") {
                        statusText.textContent = "Your turn";
                        statusText.className = "status-badge bg-white text-gray-700 border border-gray-200";
                    } else {
                        statusText.textContent = "AI thinking";
                        statusText.className = "status-badge bg-pink-50 text-pink-700 border border-pink-200 glow-effect thinking-dots";
                    }
                    
                    // Update scores
                    document.getElementById("scoreX").textContent = data.scores.X || 0;
                    document.getElementById("scoreO").textContent = data.scores.O || 0;
                    document.getElementById("scoreDraw").textContent = data.scores.draw || 0;
                    
                } catch (error) {
                    console.error("Error updating game state:", error);
                }
            }
            
            async function highlightWinningCells() {
                try {
                    const response = await fetch("/api/game/winning-cells");
                    const indices = await response.json();
                    indices.forEach(index => {
                        if (index >= 0 && index < cells.length) {
                            cells[index].classList.add("winning");
                        }
                    });
                } catch (error) {
                    console.error("Error highlighting winning cells:", error);
                }
            }
            
            async function makeMove(index) {
                if (gameOver || currentBoard[index] || currentPlayer !== "X" || isProcessing) {
                    return;
                }
                
                isProcessing = true;
                statusText.textContent = "Processing...";
                statusText.className = "status-badge bg-blue-100 text-blue-700 border border-blue-300";
                
                try {
                    const response = await fetch("/api/game/move", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({ position: index })
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || "Failed to make move");
                    }
                    
                    await updateGameState();
                    
                    // If game is not over and it's AI's turn, make AI move
                    if (!gameOver && currentPlayer === "O") {
                        setTimeout(async () => {
                            await makeAIMove();
                        }, 300); // Small delay for better UX
                    }
                } catch (error) {
                    console.error("Error making move:", error);
                    statusText.textContent = "Error! Try again";
                    statusText.className = "status-badge bg-red-100 text-red-700 border border-red-300";
                } finally {
                    isProcessing = false;
                }
            }
            
            async function makeAIMove() {
                if (gameOver || currentPlayer !== "O" || isProcessing) {
                    return;
                }
                
                isProcessing = true;
                statusText.textContent = "AI thinking";
                statusText.className = "status-badge bg-pink-50 text-pink-700 border border-pink-200 glow-effect thinking-dots";
                
                try {
                    const response = await fetch("/api/game/ai-move", {
                        method: "POST"
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || "Failed to make AI move");
                    }
                    
                    await updateGameState();
                } catch (error) {
                    console.error("Error making AI move:", error);
                    statusText.textContent = "AI error! Try again";
                    statusText.className = "status-badge bg-red-100 text-red-700 border border-red-300";
                } finally {
                    isProcessing = false;
                }
            }
            
            async function resetGame() {
                if (isProcessing) return;
                
                try {
                    await fetch("/api/game/reset", {
                        method: "POST"
                    });
                    await updateGameState();
                } catch (error) {
                    console.error("Error resetting game:", error);
                }
            }
            
            async function resetScores() {
                if (isProcessing) return;
                
                try {
                    await fetch("/api/game/reset-scores", {
                        method: "POST"
                    });
                    await updateGameState();
                } catch (error) {
                    console.error("Error resetting scores:", error);
                }
            }
            
            // Initialize game
            updateGameState();
            
            // Keyboard support
            document.addEventListener("keydown", (e) => {
                if (e.key === "r" || e.key === "R") {
                    resetGame();
                }
                if (e.key >= "1" && e.key <= "9") {
                    const index = parseInt(e.key) - 1;
                    makeMove(index);
                }
            });
        </script>
    </body>
    </html>
    """)

@app.get("/api/game/state")
async def get_game_state():
    """Get current game state"""
    return {
        "board": game_state["board"],
        "current_player": game_state["current_player"],
        "winner": game_state["winner"],
        "game_over": game_state["game_over"],
        "scores": game_state["scores"]
    }

@app.get("/api/game/winning-cells")
async def get_winning_cells():
    """Get the indices of winning cells"""
    board = game_state["board"]
    win_patterns = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    
    for pattern in win_patterns:
        if board[pattern[0]] and board[pattern[0]] == board[pattern[1]] == board[pattern[2]]:
            return pattern
    return []

@app.post("/api/game/move")
async def make_move(data: dict):
    """Make a move on the board"""
    if game_state["game_over"]:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    if game_state["current_player"] != "X":
        raise HTTPException(status_code=400, detail="It's not your turn")
    
    position = data.get("position")
    if position is None or not isinstance(position, int) or position < 0 or position > 8:
        raise HTTPException(status_code=400, detail="Invalid position")
    
    if game_state["board"][position] != "":
        raise HTTPException(status_code=400, detail="Position already taken")
    
    # Make the move
    game_state["board"][position] = "X"
    
    # Check for winner or draw
    winner = check_winner(game_state["board"])
    if winner:
        game_state["winner"] = winner
        game_state["game_over"] = True
        game_state["scores"][winner] += 1
    elif is_board_full(game_state["board"]):
        game_state["winner"] = "draw"
        game_state["game_over"] = True
        game_state["scores"]["draw"] += 1
    else:
        game_state["current_player"] = "O"
    
    return {"success": True}

@app.post("/api/game/ai-move")
async def make_ai_move():
    """Make AI move using minimax algorithm"""
    if game_state["game_over"]:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    if game_state["current_player"] != "O":
        raise HTTPException(status_code=400, detail="It's not AI's turn")
    
    # Get AI move
    move = ai_move(game_state["board"])
    if move == -1:
        raise HTTPException(status_code=400, detail="No available moves")
    
    # Make the move
    game_state["board"][move] = "O"
    
    # Check for winner or draw
    winner = check_winner(game_state["board"])
    if winner:
        game_state["winner"] = winner
        game_state["game_over"] = True
        game_state["scores"][winner] += 1
    elif is_board_full(game_state["board"]):
        game_state["winner"] = "draw"
        game_state["game_over"] = True
        game_state["scores"]["draw"] += 1
    else:
        game_state["current_player"] = "X"
    
    return {"success": True, "move": move}

@app.post("/api/game/reset")
async def reset_game_route():
    """Reset the game"""
    reset_game()
    return {"success": True}

@app.post("/api/game/reset-scores")
async def reset_scores():
    """Reset all scores"""
    game_state["scores"] = {"X": 0, "O": 0, "draw": 0}
    reset_game()
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
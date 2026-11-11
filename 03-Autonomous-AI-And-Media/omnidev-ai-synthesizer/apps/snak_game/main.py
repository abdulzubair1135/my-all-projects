from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import random
import json
from typing import List, Dict, Optional
from pydantic import BaseModel
import os

app = FastAPI(title="Snake Game")

# Game state management
class GameState:
    def __init__(self):
        self.grid_size = 20
        self.reset()
    
    def reset(self):
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self.generate_food()
        self.score = 0
        self.game_over = False
        self.won = False
        self.speed = 150  # ms per move
    
    def generate_food(self):
        while True:
            food = (random.randint(0, self.grid_size - 1), 
                   random.randint(0, self.grid_size - 1))
            if food not in self.snake:
                return food
    
    def move(self):
        if self.game_over or self.won:
            return
        
        self.direction = self.next_direction
        head = self.snake[0]
        new_head = (head[0] + self.direction[0], 
                   head[1] + self.direction[1])
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= self.grid_size or
            new_head[1] < 0 or new_head[1] >= self.grid_size):
            self.game_over = True
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return
        
        self.snake.insert(0, new_head)
        
        # Check food
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            # Check win condition
            if len(self.snake) == self.grid_size * self.grid_size:
                self.won = True
        else:
            self.snake.pop()
    
    def get_state(self):
        return {
            "snake": self.snake,
            "food": self.food,
            "score": self.score,
            "game_over": self.game_over,
            "won": self.won,
            "grid_size": self.grid_size,
            "speed": self.speed
        }

game_state = GameState()

# API endpoints
@app.get("/", response_class=HTMLResponse)
async def get_game():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if not os.path.exists(html_path):
        html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/state")
async def get_state():
    return game_state.get_state()

@app.post("/api/move")
async def move_snake():
    game_state.move()
    return game_state.get_state()

@app.post("/api/reset")
async def reset_game():
    game_state.reset()
    return game_state.get_state()

@app.post("/api/direction/{direction}")
async def change_direction(direction: str):
    direction_map = {
        "up": (0, -1),
        "down": (0, 1),
        "left": (-1, 0),
        "right": (1, 0)
    }
    
    if direction not in direction_map:
        raise HTTPException(status_code=400, detail="Invalid direction")
    
    new_dir = direction_map[direction]
    # Prevent reversing
    if (new_dir[0] != -game_state.direction[0] or 
        new_dir[1] != -game_state.direction[1]):
        game_state.next_direction = new_dir
    
    return {"status": "ok"}

# Serve the HTML directly in the response if file doesn't exist
@app.get("/", response_class=HTMLResponse)
async def get_game_embedded():
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Snake Game</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 20px rgba(251, 191, 36, 0.3); }
            50% { box-shadow: 0 0 40px rgba(251, 191, 36, 0.6); }
        }
        .game-over-overlay {
            animation: glow 1.5s ease-in-out infinite;
        }
        .food-pulse {
            animation: pulse 0.8s ease-in-out infinite;
        }
        .snake-cell {
            transition: all 0.1s ease;
        }
        #gameCanvas {
            background: #1a1a2e;
            border-radius: 1rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
        }
        .score-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
    </style>
</head>
<body class="bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 min-h-screen flex items-center justify-center p-4">
    <div class="max-w-4xl w-full">
        <div class="text-center mb-8">
            <h1 class="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-red-500 to-pink-500 animate-pulse">
                🐍 Snake Game
            </h1>
            <p class="text-gray-300 mt-2 text-lg">Use arrow keys or buttons to control</p>
        </div>
        
        <div class="flex flex-col items-center">
            <div class="relative">
                <canvas id="gameCanvas" width="600" height="600" class="w-full max-w-[600px] aspect-square"></canvas>
                
                <!-- Game Over Overlay -->
                <div id="gameOverlay" class="absolute inset-0 flex items-center justify-center bg-black/70 rounded-2xl hidden game-over-overlay">
                    <div class="text-center space-y-4">
                        <h2 id="overlayTitle" class="text-5xl font-bold text-white mb-2"></h2>
                        <p id="overlayScore" class="text-2xl text-gray-300"></p>
                        <button onclick="resetGame()" class="px-8 py-3 bg-gradient-to-r from-yellow-400 to-red-500 text-white font-bold rounded-full hover:scale-105 transition-transform shadow-xl">
                            Play Again
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Score and Controls -->
            <div class="mt-6 w-full max-w-[600px]">
                <div class="flex justify-between items-center mb-4">
                    <div class="score-badge px-6 py-2 rounded-full shadow-lg">
                        <span class="text-white font-bold text-xl">🍎 Score: <span id="scoreDisplay">0</span></span>
                    </div>
                    <button onclick="resetGame()" class="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors">
                        🔄 Reset
                    </button>
                </div>
                
                <!-- Mobile Controls -->
                <div class="grid grid-cols-3 gap-2 max-w-[300px] mx-auto mt-4">
                    <div></div>
                    <button onclick="changeDirection('up')" class="bg-gray-700 hover:bg-gray-600 text-white text-2xl p-3 rounded-lg transition-colors shadow-lg">
                        ▲
                    </button>
                    <div></div>
                    <button onclick="changeDirection('left')" class="bg-gray-700 hover:bg-gray-600 text-white text-2xl p-3 rounded-lg transition-colors shadow-lg">
                        ◀
                    </button>
                    <button onclick="changeDirection('down')" class="bg-gray-700 hover:bg-gray-600 text-white text-2xl p-3 rounded-lg transition-colors shadow-lg">
                        ▼
                    </button>
                    <button onclick="changeDirection('right')" class="bg-gray-700 hover:bg-gray-600 text-white text-2xl p-3 rounded-lg transition-colors shadow-lg">
                        ▶
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisplay = document.getElementById('scoreDisplay');
        const overlay = document.getElementById('gameOverlay');
        const overlayTitle = document.getElementById('overlayTitle');
        const overlayScore = document.getElementById('overlayScore');
        
        let gameState = null;
        let gameLoop = null;
        let moveInterval = null;
        
        // Fetch game state
        async function fetchState() {
            try {
                const response = await fetch('/api/state');
                gameState = await response.json();
                renderGame();
                updateScore();
                checkGameOver();
                return gameState;
            } catch (error) {
                console.error('Error fetching state:', error);
            }
        }
        
        // Render game on canvas
        function renderGame() {
            if (!gameState) return;
            
            const { snake, food, grid_size } = gameState;
            const cellSize = canvas.width / grid_size;
            
            // Clear canvas
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
            ctx.lineWidth = 0.5;
            for (let i = 0; i <= grid_size; i++) {
                ctx.beginPath();
                ctx.moveTo(i * cellSize, 0);
                ctx.lineTo(i * cellSize, canvas.height);
                ctx.stroke();
                ctx.beginPath();
                ctx.moveTo(0, i * cellSize);
                ctx.lineTo(canvas.width, i * cellSize);
                ctx.stroke();
            }
            
            // Draw food
            const [fx, fy] = food;
            const gradient = ctx.createRadialGradient(
                fx * cellSize + cellSize/2, fy * cellSize + cellSize/2, 2,
                fx * cellSize + cellSize/2, fy * cellSize + cellSize/2, cellSize/2
            );
            gradient.addColorStop(0, '#ff6b6b');
            gradient.addColorStop(1, '#ee5a24');
            ctx.fillStyle = gradient;
            ctx.shadowColor = '#ff6b6b';
            ctx.shadowBlur = 15;
            ctx.beginPath();
            ctx.arc(fx * cellSize + cellSize/2, fy * cellSize + cellSize/2, cellSize/2 - 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
            
            // Draw snake
            snake.forEach(([x, y], index) => {
                const isHead = index === 0;
                const cellX = x * cellSize;
                const cellY = y * cellSize;
                const padding = isHead ? 1 : 2;
                const radius = 4;
                
                // Gradient for snake body
                const gradient = ctx.createLinearGradient(cellX, cellY, cellX + cellSize, cellY + cellSize);
                if (isHead) {
                    gradient.addColorStop(0, '#00d2ff');
                    gradient.addColorStop(1, '#3a7bd5');
                } else {
                    const intensity = 0.3 + (index / snake.length) * 0.5;
                    gradient.addColorStop(0, `rgba(0, 210, 255, ${intensity})`);
                    gradient.addColorStop(1, `rgba(58, 123, 213, ${intensity})`);
                }
                
                ctx.fillStyle = gradient;
                ctx.shadowColor = isHead ? '#00d2ff' : 'transparent';
                ctx.shadowBlur = isHead ? 20 : 0;
                
                // Rounded rectangle
                const x1 = cellX + padding;
                const y1 = cellY + padding;
                const w = cellSize - padding * 2;
                const h = cellSize - padding * 2;
                
                ctx.beginPath();
                ctx.moveTo(x1 + radius, y1);
                ctx.lineTo(x1 + w - radius, y1);
                ctx.quadraticCurveTo(x1 + w, y1, x1 + w, y1 + radius);
                ctx.lineTo(x1 + w, y1 + h - radius);
                ctx.quadraticCurveTo(x1 + w, y1 + h, x1 + w - radius, y1 + h);
                ctx.lineTo(x1 + radius, y1 + h);
                ctx.quadraticCurveTo(x1, y1 + h, x1, y1 + h - radius);
                ctx.lineTo(x1, y1 + radius);
                ctx.quadraticCurveTo(x1, y1, x1 + radius, y1);
                ctx.closePath();
                ctx.fill();
                ctx.shadowBlur = 0;
                
                // Eyes on head
                if (isHead) {
                    ctx.fillStyle = 'white';
                    ctx.shadowBlur = 0;
                    const eyeSize = 4;
                    const eyeOffset = 6;
                    let ex1, ey1, ex2, ey2;
                    
                    // Direction-based eyes
                    const dir = gameState.direction || [1, 0];
                    if (dir[0] === 1) { // Right
                        ex1 = cellX + cellSize - 10; ey1 = cellY + 8;
                        ex2 = cellX + cellSize - 10; ey2 = cellY + cellSize - 8;
                    } else if (dir[0] === -1) { // Left
                        ex1 = cellX + 10; ey1 = cellY + 8;
                        ex2 = cellX + 10; ey2 = cellY + cellSize - 8;
                    } else if (dir[1] === -1) { // Up
                        ex1 = cellX + 8; ey1 = cellY + 10;
                        ex2 = cellX + cellSize - 8; ey2 = cellY + 10;
                    } else { // Down
                        ex1 = cellX + 8; ey1 = cellY + cellSize - 10;
                        ex2 = cellX + cellSize - 8; ey2 = cellY + cellSize - 10;
                    }
                    
                    ctx.beginPath();
                    ctx.arc(ex1, ey1, eyeSize, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.arc(ex2, ey2, eyeSize, 0, Math.PI * 2);
                    ctx.fill();
                    
                    ctx.fillStyle = '#1a1a2e';
                    ctx.beginPath();
                    ctx.arc(ex1 + dir[0] * 2, ey1 + dir[1] * 2, 2, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.arc(ex2 + dir[0] * 2, ey2 + dir[1] * 2, 2, 0, Math.PI * 2);
                    ctx.fill();
                }
            });
        }
        
        function updateScore() {
            if (gameState) {
                scoreDisplay.textContent = gameState.score;
            }
        }
        
        function checkGameOver() {
            if (!gameState) return;
            
            if (gameState.game_over || gameState.won) {
                overlay.classList.remove('hidden');
                if (gameState.won) {
                    overlayTitle.textContent = '🎉 You Won!';
                    overlayTitle.className = 'text-5xl font-bold text-yellow-400 mb-2';
                } else {
                    overlayTitle.textContent = '💀 Game Over';
                    overlayTitle.className = 'text-5xl font-bold text-red-500 mb-2';
                }
                overlayScore.textContent = `Final Score: ${gameState.score}`;
                clearInterval(moveInterval);
                moveInterval = null;
            } else {
                overlay.classList.add('hidden');
            }
        }
        
        async function moveSnake() {
            if (gameState && !gameState.game_over && !gameState.won) {
                try {
                    const response = await fetch('/api/move', { method: 'POST' });
                    gameState = await response.json();
                    renderGame();
                    updateScore();
                    checkGameOver();
                } catch (error) {
                    console.error('Error moving snake:', error);
                }
            }
        }
        
        async function changeDirection(direction) {
            try {
                await fetch(`/api/direction/${direction}`, { method: 'POST' });
            } catch (error) {
                console.error('Error changing direction:', error);
            }
        }
        
        async function resetGame() {
            clearInterval(moveInterval);
            try {
                const response = await fetch('/api/reset', { method: 'POST' });
                gameState = await response.json();
                renderGame();
                updateScore();
                overlay.classList.add('hidden');
                startGameLoop();
            } catch (error) {
                console.error('Error resetting game:', error);
            }
        }
        
        function startGameLoop() {
            if (moveInterval) {
                clearInterval(moveInterval);
            }
            moveInterval = setInterval(moveSnake, 150);
        }
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            const keyMap = {
                'ArrowUp': 'up',
                'ArrowDown': 'down',
                'ArrowLeft': 'left',
                'ArrowRight': 'right'
            };
            if (keyMap[e.key]) {
                e.preventDefault();
                changeDirection(keyMap[e.key]);
            }
        });
        
        // Initialize game
        async function init() {
            await fetchState();
            startGameLoop();
        }
        
        init();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
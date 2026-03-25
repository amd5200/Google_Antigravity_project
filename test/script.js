const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreElement = document.getElementById('score');
const highScoreElement = document.getElementById('high-score');
const overlay = document.getElementById('game-overlay');
const overlayText = document.getElementById('overlay-text');
const startBtn = document.getElementById('start-btn');
const difficultySelect = document.getElementById('difficulty');
const audioEnableCheckbox = document.getElementById('audio-enable');


// --- 🎵 Web Audio API Setup for 8-bit Sounds ---
const AudioContext = window.AudioContext || window.webkitAudioContext;
let audioCtx;

function initAudio() {
    if (!audioCtx) {
        audioCtx = new AudioContext();
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
}

function playTone(freq, type, duration, vol=0.1) {
    if(!audioEnableCheckbox.checked || !audioCtx) return;
    
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    
    osc.type = type;
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
    
    // Quick attack and smooth release to prevent clicking
    gain.gain.setValueAtTime(vol, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
    
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    
    osc.start();
    osc.stop(audioCtx.currentTime + duration);
}

// BGM sequences
const bgmNotes = [
    130.81, 155.56, 196.00, 155.56, 130.81, 155.56, 196.00, 233.08
];
let bgmIndex = 0;
let bgmInterval;

function startBGM() {
    initAudio();
    if(bgmInterval) clearInterval(bgmInterval);
    bgmIndex = 0;
    
    bgmInterval = setInterval(() => {
        if (isPlaying && audioEnableCheckbox.checked && audioCtx) {
            playTone(bgmNotes[bgmIndex], 'square', 0.15, 0.05);
            bgmIndex = (bgmIndex + 1) % bgmNotes.length;
        }
    }, 200); // tempo
}

function stopBGM() {
    if(bgmInterval) clearInterval(bgmInterval);
}

// SFX Functions
function playEatSound() {
    initAudio();
    playTone(880, 'square', 0.1, 0.1); 
    setTimeout(() => playTone(1108.73, 'square', 0.15, 0.1), 50); 
}

function playGameOverSound() {
    initAudio();
    stopBGM();
    playTone(300, 'sawtooth', 0.2, 0.15);
    setTimeout(() => playTone(250, 'sawtooth', 0.2, 0.15), 200);
    setTimeout(() => playTone(200, 'sawtooth', 0.2, 0.15), 400);
    setTimeout(() => playTone(150, 'sawtooth', 0.4, 0.15), 600);
}


// --- 🐍 Game Logic ---
const gridSize = 20;
const tileCount = canvas.width / gridSize;

let snake = [];
let food = {};
let dx = 0;
let dy = 0;
let score = 0;
let highScore = localStorage.getItem('snakeHighScore') || 0;
let gameLoopInterval;
let gameSpeed = 150; 
let baseSpeed = 150; 
let isPlaying = false;
let isGameOver = false;

highScoreElement.textContent = highScore;

function initGame() {
    const startX = Math.floor(tileCount / 2);
    const startY = Math.floor(tileCount / 2);
    snake = [
        { x: startX, y: startY },
        { x: startX, y: startY + 1 },
        { x: startX, y: startY + 2 }
    ];
    
    dx = 0;
    dy = -1; 
    
    score = 0;
    
    baseSpeed = parseInt(difficultySelect.value);
    gameSpeed = baseSpeed;
    
    scoreElement.textContent = score;
    isGameOver = false;
    spawnFood();
}

function spawnFood() {
    food = {
        x: Math.floor(Math.random() * tileCount),
        y: Math.floor(Math.random() * tileCount)
    };
    
    for (let part of snake) {
        if (part.x === food.x && part.y === food.y) {
            spawnFood();
            break;
        }
    }
}

function startGame() {
    initAudio(); 
    initGame();
    overlay.classList.add('hidden');
    isPlaying = true;
    
    startBGM(); 
    
    if (gameLoopInterval) clearInterval(gameLoopInterval);
    gameLoopInterval = setInterval(gameLoop, gameSpeed);
}

function gameOver() {
    isPlaying = false;
    isGameOver = true;
    clearInterval(gameLoopInterval);
    playGameOverSound();
    
    if (score > highScore) {
        highScore = score;
        localStorage.setItem('snakeHighScore', highScore);
        highScoreElement.textContent = highScore;
    }
    
    overlayText.innerHTML = `GAME OVER<br><br><span style="font-size: 1rem; color: #94a3b8">最終分數: ${score}</span>`;
    startBtn.textContent = '重試';
    overlay.classList.remove('hidden');
}

function clearCanvas() {
    ctx.fillStyle = '#020617';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.strokeStyle = '#0f172a';
    ctx.lineWidth = 1;
    for (let i = 0; i < tileCount; i++) {
        ctx.beginPath();
        ctx.moveTo(i * gridSize, 0);
        ctx.lineTo(i * gridSize, canvas.height);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(0, i * gridSize);
        ctx.lineTo(canvas.width, i * gridSize);
        ctx.stroke();
    }
}

function drawSnake() {
    snake.forEach((part, index) => {
        if (index === 0) {
            ctx.fillStyle = '#059669'; 
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#059669';
        } else {
            ctx.fillStyle = '#34d399'; 
            ctx.shadowBlur = 0;
        }
        
        const gap = 2;
        ctx.beginPath();
        ctx.roundRect(
            part.x * gridSize + gap, 
            part.y * gridSize + gap, 
            gridSize - gap * 2, 
            gridSize - gap * 2,
            index === 0 ? 4 : 2 
        );
        ctx.fill();
    });
    ctx.shadowBlur = 0; 
}

function drawFood() {
    ctx.fillStyle = '#ef4444';
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#ef4444';
    
    const centerX = food.x * gridSize + gridSize / 2;
    const centerY = food.y * gridSize + gridSize / 2;
    const radius = (gridSize / 2) - 3;
    
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
    ctx.fill();
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.shadowBlur = 0;
    ctx.beginPath();
    ctx.arc(centerX - radius/3, centerY - radius/3, radius/3, 0, 2 * Math.PI);
    ctx.fill();
}

let lastFrameDx = 0;
let lastFrameDy = 0;

function moveSnake() {
    if (dx === 0 && dy === 0) return;
    
    lastFrameDx = dx;
    lastFrameDy = dy;
    
    const head = { x: snake[0].x + dx, y: snake[0].y + dy };
    
    if (head.x < 0 || head.x >= tileCount || head.y < 0 || head.y >= tileCount) {
        gameOver();
        return;
    }
    
    for (let i = 0; i < snake.length; i++) {
        if (head.x === snake[i].x && head.y === snake[i].y) {
            gameOver();
            return;
        }
    }
    
    snake.unshift(head);
    
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreElement.textContent = score;
        playEatSound(); 
        
        const speedCap = baseSpeed * 0.4; 
        if (gameSpeed > speedCap) {
            gameSpeed -= Math.floor(baseSpeed * 0.05); 
            clearInterval(gameLoopInterval);
            gameLoopInterval = setInterval(gameLoop, gameSpeed);
        }
        
        spawnFood();
    } else {
        snake.pop(); 
    }
}

function gameLoop() {
    if (!isPlaying) return;
    moveSnake();
    if (!isGameOver) {
        clearCanvas();
        drawFood();
        drawSnake();
    }
}

// Direction Handler Logic
function handleDirection(direction) {
    if (isGameOver) {
        startGame();
        return;
    }
    
    if (!isPlaying && !isGameOver) {
        if (overlay.classList.contains('hidden') === false) return;
    }
    
    const goingUp = lastFrameDy === -1;
    const goingDown = lastFrameDy === 1;
    const goingRight = lastFrameDx === 1;
    const goingLeft = lastFrameDx === -1;

    switch (direction) {
        case 'up':
            if (!goingDown) { dx = 0; dy = -1; }
            break;
        case 'down':
            if (!goingUp) { dx = 0; dy = 1; }
            break;
        case 'left':
            if (!goingRight) { dx = -1; dy = 0; }
            break;
        case 'right':
            if (!goingLeft) { dx = 1; dy = 0; }
            break;
    }
}

// Mouse / Keyboard Event Listeners
document.addEventListener('keydown', (e) => {
    if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Space"].includes(e.code)) {
        e.preventDefault();
    }
    
    if (e.code === 'Space') {
        if (!isPlaying || isGameOver) {
            startGame();
            return;
        }
    }

    if (e.code === 'ArrowUp' || e.code === 'KeyW') handleDirection('up');
    else if (e.code === 'ArrowDown' || e.code === 'KeyS') handleDirection('down');
    else if (e.code === 'ArrowLeft' || e.code === 'KeyA') handleDirection('left');
    else if (e.code === 'ArrowRight' || e.code === 'KeyD') handleDirection('right');
});

startBtn.addEventListener('click', startGame);

// UI Button Virtual DPAD Setup
['up', 'down', 'left', 'right'].forEach(dir => {
    const btn = document.getElementById(`btn-${dir}`);
    
    const handlePress = (e) => {
        e.preventDefault();
        btn.classList.add('active-touch');
        handleDirection(dir);
    };
    
    const handleRelease = (e) => {
        e.preventDefault();
        btn.classList.remove('active-touch');
    };
    
    btn.addEventListener('mousedown', handlePress);
    btn.addEventListener('mouseup', handleRelease);
    btn.addEventListener('mouseleave', handleRelease);
    
    btn.addEventListener('touchstart', handlePress, {passive: false});
    btn.addEventListener('touchend', handleRelease, {passive: false});
    btn.addEventListener('touchcancel', handleRelease, {passive: false});
});

// Draw initial state
initGame();
clearCanvas();
drawSnake();

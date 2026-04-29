# Tic Tac Toe

A browser-based Tic Tac Toe game with score tracking and local storage persistence.

## Features

- **Two-player gameplay** - Players take turns as X and O
- **Win detection** - Automatically detects winning combinations with visual highlighting
- **Score tracking** - Tracks wins for both players and draws
- **Persistent scores** - Scores are saved to localStorage and persist across sessions
- **Responsive design** - Works on desktop and mobile devices
- **Visual feedback** - Hover effects, winning cell animations, and player-specific colors

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge)

### Running the Game

1. Clone or download this repository
2. Open `index.html` in your web browser
3. Start playing!

No build process or dependencies required.

## How to Play

1. Player X always goes first
2. Click an empty cell to place your mark
3. First player to get 3 in a row (horizontally, vertically, or diagonally) wins
4. If all cells are filled with no winner, the game is a draw
5. Click "New Game" to start a fresh round (scores are preserved)

## Project Structure

```
├── index.html    # Game layout and structure
├── style.css     # Styling and animations
├── script.js     # Game logic and state management
└── README.md     # This file
```

## Technical Details

### Game State (`script.js`)

| Variable | Type | Description |
|----------|------|-------------|
| `board` | Array | 9-element array representing cell values |
| `currentPlayer` | String | Current player ('X' or 'O') |
| `gameActive` | Boolean | Whether the game is in progress |
| `scores` | Object | Win/draw counts for scoreboard |

### Key Functions

| Function | Description |
|----------|-------------|
| `init()` | Sets up event listeners and loads saved scores |
| `handleCellClick()` | Processes player moves |
| `checkResult()` | Evaluates win/draw conditions |
| `updateScore()` | Increments and saves scores |
| `resetGame()` | Clears board for new round |

### Winning Combinations

The game checks 8 possible winning lines:
- 3 horizontal rows
- 3 vertical columns
- 2 diagonals

### Storage

Scores persist via `localStorage` under the key `ticTacToeScores`.

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

## License

This project is open source and available for personal and educational use.

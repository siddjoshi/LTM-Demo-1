(function () {
    'use strict';

    const WINNING_LINES = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
        [0, 4, 8], [2, 4, 6]             // diagonals
    ];

    const board = Array(9).fill('');
    let currentPlayer = 'X';
    let gameOver = false;
    const scores = { X: 0, O: 0, draw: 0 };

    const cells = document.querySelectorAll('.cell');
    const statusEl = document.getElementById('status');
    const resetBtn = document.getElementById('reset');
    const resetAllBtn = document.getElementById('reset-all');
    const scoreEls = {
        X: document.getElementById('score-x'),
        O: document.getElementById('score-o'),
        draw: document.getElementById('score-draw')
    };

    function getWinningLine(boardState) {
        for (const line of WINNING_LINES) {
            const [a, b, c] = line;
            if (boardState[a] && boardState[a] === boardState[b] && boardState[a] === boardState[c]) {
                return line;
            }
        }
        return null;
    }

    function isDraw(boardState) {
        return boardState.every(cell => cell !== '') && !getWinningLine(boardState);
    }

    function updateStatus(text) {
        statusEl.textContent = text;
    }

    function updateScores() {
        scoreEls.X.textContent = scores.X;
        scoreEls.O.textContent = scores.O;
        scoreEls.draw.textContent = scores.draw;
    }

    function handleCellClick(event) {
        const cell = event.currentTarget;
        const index = Number(cell.dataset.index);

        if (gameOver || board[index] !== '') {
            return;
        }

        board[index] = currentPlayer;
        cell.textContent = currentPlayer;
        cell.classList.add(currentPlayer.toLowerCase());
        cell.disabled = true;

        const winningLine = getWinningLine(board);
        if (winningLine) {
            gameOver = true;
            scores[currentPlayer] += 1;
            updateScores();
            winningLine.forEach(i => cells[i].classList.add('win'));
            cells.forEach(c => { c.disabled = true; });
            updateStatus(`Player ${currentPlayer} wins! 🎉`);
            return;
        }

        if (isDraw(board)) {
            gameOver = true;
            scores.draw += 1;
            updateScores();
            updateStatus("It's a draw!");
            return;
        }

        currentPlayer = currentPlayer === 'X' ? 'O' : 'X';
        updateStatus(`Player ${currentPlayer}'s turn`);
    }

    function resetBoard() {
        for (let i = 0; i < board.length; i++) {
            board[i] = '';
        }
        gameOver = false;
        currentPlayer = 'X';
        cells.forEach(cell => {
            cell.textContent = '';
            cell.disabled = false;
            cell.classList.remove('x', 'o', 'win');
        });
        updateStatus("Player X's turn");
    }

    function resetAll() {
        scores.X = 0;
        scores.O = 0;
        scores.draw = 0;
        updateScores();
        resetBoard();
    }

    cells.forEach(cell => cell.addEventListener('click', handleCellClick));
    resetBtn.addEventListener('click', resetBoard);
    resetAllBtn.addEventListener('click', resetAll);
})();

document.addEventListener('DOMContentLoaded', function () {
    const board = document.getElementById('chessboard');
    const pieces = {
        bR: 'pieces/bR.png', bN: 'pieces/bN.png', bB: 'pieces/bB.png', bQ: 'pieces/bQ.png',
        bK: 'pieces/bK.png', bP: 'pieces/bP.png', wR: 'pieces/wR.png', wN: 'pieces/wN.png',
        wB: 'pieces/wB.png', wQ: 'pieces/wQ.png', wK: 'pieces/wK.png', wP: 'pieces/wP.png'
    };

    const initialSetup = [
        'wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR',
        'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP',
        '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '',
        'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP',
        'bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'
    ];

    function createBoard() {
        board.innerHTML = '';
        for (let i = 0; i < 64; i++) {
            const cell = document.createElement('div');
            const piece = initialSetup[i];
            const row = Math.floor(i / 8);
            const col = i % 8;

            // Apply alternating colors
            if ((row + col) % 2 === 0) {
                cell.classList.add('light-square');
            } else {
                cell.classList.add('dark-square');
            }

            if (piece) {
                const img = document.createElement('img');
                img.src = pieces[piece];
                img.className = 'piece';
                img.draggable = true;
                img.dataset.position = i;
                img.addEventListener('dragstart', dragStart);
                cell.appendChild(img);
            }
            cell.addEventListener('dragover', dragOver);
            cell.addEventListener('drop', drop);
            board.appendChild(cell);
        }
    }

    let draggedPiece = null;

    function dragStart(e) {
        draggedPiece = e.target;
        e.dataTransfer.setData('text/plain', draggedPiece.dataset.position);
    }

    function dragOver(e) {
        e.preventDefault();
    }

    function drop(e) {
        e.preventDefault();
        const targetCell = e.target;

        if (targetCell.tagName === 'DIV' && !targetCell.querySelector('.piece')) {
            targetCell.appendChild(draggedPiece);
        } else if (targetCell.tagName === 'IMG') {
            targetCell.parentElement.appendChild(draggedPiece);
        }
        draggedPiece = null;
    }

    createBoard();
});

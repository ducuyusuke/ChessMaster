import streamlit as st
import streamlit.components.v1 as components  # Add this line
import chess
import torch
import random
import base64
from chess_engine import ChessMovePredictionModel

# Function to convert board to tensor
def board_to_tensor(board):
    tensor = torch.zeros((12, 8, 8))
    piece_map = board.piece_map()

    piece_to_index = {
        chess.PAWN: 0,
        chess.KNIGHT: 1,
        chess.BISHOP: 2,
        chess.ROOK: 3,
        chess.QUEEN: 4,
        chess.KING: 5
    }

    for square, piece in piece_map.items():
        row, col = divmod(square, 8)
        piece_idx = piece_to_index[piece.piece_type]
        if piece.color == chess.WHITE:
            tensor[piece_idx, row, col] = 1
        else:
            tensor[piece_idx + 6, row, col] = 1

    return tensor.unsqueeze(0)

# Load the model
model = ChessMovePredictionModel()
model.load_state_dict(torch.load('chess_model.pth'))
model.eval()

# Function to load and encode image for embedding in HTML
def load_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

# Define the paths to your images
pieces = {
    'bR': load_image('pieces/bR.png'),
    'bN': load_image('pieces/bN.png'),
    'bB': load_image('pieces/bB.png'),
    'bQ': load_image('pieces/bQ.png'),
    'bK': load_image('pieces/bK.png'),
    'bP': load_image('pieces/bP.png'),
    'wR': load_image('pieces/wR.png'),
    'wN': load_image('pieces/wN.png'),
    'wB': load_image('pieces/wB.png'),
    'wQ': load_image('pieces/wQ.png'),
    'wK': load_image('pieces/wK.png'),
    'wP': load_image('pieces/wP.png')
}

# Define the HTML and CSS for the custom chessboard
html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chessboard</title>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden; /* Prevent scrollbars on body */
            font-family: sans-serif;
            background-color: #f0f0f0; /* Background color to match Streamlit's default */
        }}
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .chessboard-wrapper {{
            display: flex;
            flex-direction: column;
            align-items: center;
            background-color: black;
            padding: 5px; /* Adjust padding for smaller board */
            border-radius: 10px; /* Optional: Add rounded corners */
            overflow: hidden; /* Prevent scrollbars on wrapper */
        }}
        .column-labels {{
            display: flex;
            justify-content: center;
            margin-bottom: -1px; /* To overlap with the chessboard */
            background-color: black; /* Ensure background matches chessboard */
        }}
        .column-labels .label {{
            width: 45px; /* 75% of original width */
            height: 45px; /* 75% of original height */
            text-align: center;
            font-size: 12px; /* Smaller font size */
            font-weight: bold;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: black; /* Ensure background matches chessboard */
        }}
        .row-labels {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            margin-right: -1px; /* To overlap with the chessboard */
            background-color: black; /* Ensure background matches chessboard */
        }}
        .row-labels .label {{
            height: 45px; /* 75% of original height */
            width: 22px; /* 75% of original width */
            text-align: center;
            font-size: 12px; /* Smaller font size */
            font-weight: bold;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: black; /* Ensure background matches chessboard */
        }}
        .chessboard-container {{
            display: flex;
            align-items: center;
        }}
        .chessboard {{
            display: grid;
            grid-template-columns: repeat(8, 45px); /* 75% of original size */
            grid-template-rows: repeat(8, 45px); /* 75% of original size */
            border: 2px solid #333;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
            background-color: black; /* Ensure background matches chessboard */
        }}
        .chessboard div {{
            width: 45px; /* 75% of original size */
            height: 45px; /* 75% of original size */
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        .light-square {{
            background-color: #f0d9b5;
        }}
        .dark-square {{
            background-color: #b58863;
        }}
        .piece {{
            width: 35px; /* 70% of original size */
            height: 35px; /* 70% of original size */
            background-size: cover;
            cursor: grab;
        }}
        .piece:active {{
            cursor: grabbing;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="chessboard-wrapper">
            <!-- Top Column Labels -->
            <div class="column-labels">
                <div class="label"></div> <!-- Top-left corner -->
                <div class="label">a</div>
                <div class="label">b</div>
                <div class="label">c</div>
                <div class="label">d</div>
                <div class="label">e</div>
                <div class="label">f</div>
                <div class="label">g</div>
                <div class="label">h</div>
                <div class="label"></div> <!-- Top-right corner -->
            </div>

            <div class="chessboard-container">
                <!-- Left Row Labels -->
                <div class="row-labels">
                    <div class="label">8</div>
                    <div class="label">7</div>
                    <div class="label">6</div>
                    <div class="label">5</div>
                    <div class="label">4</div>
                    <div class="label">3</div>
                    <div class="label">2</div>
                    <div class="label">1</div>
                </div>

                <!-- Chessboard -->
                <div id="chessboard" class="chessboard"></div>

                <!-- Right Row Labels -->
                <div class="row-labels">
                    <div class="label">8</div>
                    <div class="label">7</div>
                    <div class="label">6</div>
                    <div class="label">5</div>
                    <div class="label">4</div>
                    <div class="label">3</div>
                    <div class="label">2</div>
                    <div class="label">1</div>
                </div>
            </div>

            <!-- Bottom Column Labels -->
            <div class="column-labels">
                <div class="label"></div> <!-- Bottom-left corner -->
                <div class="label">a</div>
                <div class="label">b</div>
                <div class="label">c</div>
                <div class="label">d</div>
                <div class="label">e</div>
                <div class="label">f</div>
                <div class="label">g</div>
                <div class="label">h</div>
                <div class="label"></div> <!-- Bottom-right corner -->
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function () {{
            const board = document.getElementById('chessboard');
            const pieces = {{
                bR: '{pieces['bR']}', 
                bN: '{pieces['bN']}',
                bB: '{pieces['bB']}',
                bQ: '{pieces['bQ']}',
                bK: '{pieces['bK']}',
                bP: '{pieces['bP']}',
                wR: '{pieces['wR']}',
                wN: '{pieces['wN']}',
                wB: '{pieces['wB']}',
                wQ: '{pieces['wQ']}',
                wK: '{pieces['wK']}',
                wP: '{pieces['wP']}'
            }};

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

            let draggedPiece = null;

            function createBoard() {{
                board.innerHTML = '';
                for (let i = 0; i < 64; i++) {{
                    const cell = document.createElement('div');
                    const piece = initialSetup[i];
                    const row = Math.floor(i / 8);
                    const col = i % 8;

                    if ((row + col) % 2 === 0) {{
                        cell.classList.add('light-square');
                    }} else {{
                        cell.classList.add('dark-square');
                    }}

                    if (piece) {{
                        const img = document.createElement('img');
                        img.src = pieces[piece];
                        img.className = 'piece';
                        img.draggable = true;
                        img.dataset.position = i;
                        img.addEventListener('dragstart', dragStart);
                        cell.appendChild(img);
                    }}
                    cell.addEventListener('dragover', dragOver);
                    cell.addEventListener('drop', drop);
                    board.appendChild(cell);
                }}
            }}

            function dragStart(e) {{
                draggedPiece = e.target;
                e.dataTransfer.setData('text/plain', draggedPiece.dataset.position);
            }}

            function dragOver(e) {{
                e.preventDefault();
            }}

            function drop(e) {{
                e.preventDefault();
                const targetCell = e.target;

                if (targetCell.tagName === 'DIV' && !targetCell.firstChild) {{
                    targetCell.appendChild(draggedPiece);
                    draggedPiece.dataset.position = Array.from(board.children).indexOf(targetCell);
                }}
            }}

            createBoard();
        }});
    </script>
</body>
</html>
"""

# Streamlit app layout
st.title("Chess Bot")
st.write("Jogue contra o bot de xadrez!")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

def bot_move():
    board_tensor = board_to_tensor(st.session_state.board)
    with torch.no_grad():
        output = model(board_tensor)
        best_move = None
        best_move_idx = torch.argmax(output).item()
        from_square = best_move_idx // 64
        to_square = best_move_idx % 64
        predicted_move = chess.Move(from_square, to_square)

        if predicted_move in st.session_state.board.legal_moves:
            best_move = predicted_move
        else:
            best_move = random.choice(list(st.session_state.board.legal_moves))

        st.session_state.board.push(best_move)

# Layout: Chess board on the left, controls on the right
col1, col2 = st.columns([3, 2])

# Left column: Custom HTML chessboard
with col1:
    components.html(html_code, height=450, scrolling=False)

    # Game History section
    st.header("Game History")
    moves = st.session_state.board.move_stack
    move_history = ""
    for i, move in enumerate(moves):
        move_history += f"{i+1}. {move.uci()}\n"
    st.text_area("Moves", move_history, height=100)

# User input and bot move logic
if st.session_state.board.turn == chess.WHITE:
    user_move = st.text_input("Enter your move (e.g., e2e4):")
    if st.button("Submit Move"):
        try:
            move = chess.Move.from_uci(user_move)
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move)
                st.experimental_rerun()
        except:
            st.write("Invalid move. Use the correct notation (e.g., e2e4).")
else:
    st.write("Bot's turn...")
    bot_move()
    st.experimental_rerun()

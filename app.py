import streamlit as st
import chess
import chess.svg
import torch
from chess_engine import ChessMovePredictionModel
import random
import os
import base64
from MiniMax import Minimax


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


mnmx = Minimax(4)

# Streamlit app layout
st.title("Chess Bot")
st.write("Jogue contra o chess master!")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "end_message" not in st.session_state:
    st.session_state.end_message = ""


def bot_move():
    if st.session_state.board.is_checkmate():
        st.session_state.end_message = "Xeque mate! O jogo acabou."
        st.session_state.game_over = True
        return
    elif st.session_state.board.is_stalemate():
        st.session_state.end_message = "Empate! O jogo acabou."
        st.session_state.game_over = True
        return

    with torch.no_grad():      
        best_move = mnmx.get_best_move(depth=4, board=st.session_state.board, time_limit=7)
        if best_move not in st.session_state.board.legal_moves:
            best_move = random.choice(list(st.session_state.board.legal_moves))
        
        st.session_state.board.push(best_move)

def load_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

# Layout: Chess board on the left, controls on the right
col1, col2 = st.columns([3, 2])

# Left column: Chess board
with col1:
    board_svg = chess.svg.board(board=st.session_state.board)
    st.markdown(f'<div>{board_svg}</div>', unsafe_allow_html=True)

# Right column: Controls
with col2:
    st.markdown('<div class="suggested-moves-title">Suggested Moves</div>', unsafe_allow_html=True)
    st.markdown('<div class="suggested-moves-container">', unsafe_allow_html=True)

    card_col1, card_col2, card_col3, card_col4 = st.columns(4)

    # Card 1
    with card_col1:
        st.markdown(f'''
            <div class="suggested-move-card">
                <div class="top-line" style="background-color: green;"></div>
                <img src="{load_image(os.path.join("images", "Group 6.png"))}" alt="Piece">
                <h4>Bg4</h4>
                <hr>
                <p>92%</p>
                <div class="score-label">Score</div>
            </div>
        ''', unsafe_allow_html=True)

    # Card 2
    with card_col2:
        st.markdown(f'''
            <div class="suggested-move-card">
                <div class="top-line" style="background-color: green;"></div>
                <img src="{load_image(os.path.join("images", "Group 7.png"))}" alt="Piece">
                <h4>Bg4</h4>
                <hr>
                <p>92%</p>
                <div class="score-label">Score</div>
            </div>
        ''', unsafe_allow_html=True)

    # Card 3
    with card_col3:
        st.markdown(f'''
            <div class="suggested-move-card">
                <div class="top-line" style="background-color: green;"></div>
                <img src="{load_image(os.path.join("images", "Group 8.png"))}" alt="Piece">
                <h4>Bg4</h4>
                <hr>
                <p>92%</p>
                <div class="score-label">Score</div>
            </div>
        ''', unsafe_allow_html=True)

    # Card 4
    with card_col4:
        st.markdown(f'''
            <div class="suggested-move-card">
                <div class="top-line" style="background-color: green;"></div>
                <img src="{load_image(os.path.join("images", "Group 9.png"))}" alt="Piece">
                <h4>Bg4</h4>
                <hr>
                <p>92%</p>
                <div class="score-label">Score</div>
            </div>
        ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.header("Game History")
    moves = st.session_state.board.move_stack
    move_history = ""
    for i, move in enumerate(moves):
        move_history += f"{i+1}. {move.uci()}\n"
    st.text_area("Moves", move_history, height=100)
    
if not st.session_state.game_over:
    if st.session_state.board.turn == chess.WHITE:
        user_move = st.text_input("Digite seu movimento (ex: e2e4):")
        if st.button("Enviar Movimento"):
            move = None
            try:
                move = chess.Move.from_uci(user_move)
                if move in st.session_state.board.legal_moves:
                    st.session_state.board.push(move)
                    st.experimental_rerun()
                else:
                    st.write("Movimento inválido. Use a notação correta (ex: e2e4).")

            except Exception as e:
                st.write(f"Erro ao processar o movimento: {str(e)}")
    else:
        st.write("Turno do bot...")
        bot_move()
        st.experimental_rerun()
    

else:
    st.write(st.session_state.end_message)

if st.button("Reiniciar Jogo"):
    st.session_state.board.reset()
    st.session_state.game_over = False
    st.session_state.end_message = ""
    st.experimental_rerun()



#PARTE FRONTEND

st.markdown(
    """
    <style>
    .suggested-moves-title {
        margin-bottom: 5px;
        font-size: 24px;
        font-weight: bold;
        margin-top: -10px;
    }
    .suggested-moves-container {
        display: flex;
        justify-content: space-between;
    }
    .suggested-move-card {
        background-color: #333333;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        text-align: center;
        width: 100%;
        max-width: 150px;
        position: relative;
    }
    .suggested-move-card .top-line {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
    }
    .suggested-move-card img {
        width: 60px;
        height: 60px; /* Fixed height for the images */
        object-fit: contain;
        margin-bottom: 5px;
    }
    .suggested-move-card h4 {
        margin: 0;
        color: #ffffff;
        font-size: 16px;
        padding: 0;
    }
    .suggested-move-card hr {
        margin: 0;
        border: none;
        border-top: 1px solid #555555;
    }
    .suggested-move-card p {
        margin: 0;
        color: green;
        font-size: 14px;
    }
    .suggested-move-card .score-label {
        margin-top: 0.5px;
        font-size: 12px;
        color: #cccccc;
    }
    </style>
    """,
    unsafe_allow_html=True
)
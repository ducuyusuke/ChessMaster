import streamlit as st
import chess
import chess.svg
import torch
from chess_engine import ChessMovePredictionModel
import random
import os
import base64
import chess.engine
from evaluation_helpers import format_evaluation, interpret_evaluation, evaluate_move, suggest_best_moves_for_white
from gemini import coach_answer

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

# Streamlit app layout
st.title("Chess Bot")
st.write("Jogue contra o chess master!")

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "end_message" not in st.session_state:
    st.session_state.end_message = ""
if "evaluation_message" not in st.session_state:
    st.session_state.evaluation_message = ""

def bot_move():
    if st.session_state.board.is_checkmate():
        st.session_state.end_message = "Xeque mate! O jogo acabou."
        st.session_state.game_over = True
        return
    elif st.session_state.board.is_stalemate():
        st.session_state.end_message = "Empate! O jogo acabou."
        st.session_state.game_over = True
        return

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

def load_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

# Layout: Chess board on the left, controls on the right
col1, col2 = st.columns([3, 1])  # Mantém a proporção para o tabuleiro e a coluna direita

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

# Left column: Chess board
with col1:
    board_svg = chess.svg.board(board=st.session_state.board)
    st.markdown(f'<div>{board_svg}</div>', unsafe_allow_html=True)

# Right column: Suggested moves and Game History
with col2:
    st.markdown('<div class="suggested-moves-title">Sugestões de Movimentos</div>', unsafe_allow_html=True)
    best_moves = suggest_best_moves_for_white(st.session_state.board, num_moves=2)

    col_moves1, col_moves2 = st.columns(2)  # Ajusta as sugestões de movimentos para ficarem lado a lado

    if len(best_moves) > 0:
        with col_moves1:
            st.markdown(f'''
                <div class="suggested-move-card">
                    <h4>{best_moves[0][0].uci()}</h4>
                    <p>Score: {best_moves[0][1]:.2f}</p>
                </div>
            ''', unsafe_allow_html=True)

    if len(best_moves) > 1:
        with col_moves2:
            st.markdown(f'''
                <div class="suggested-move-card">
                    <h4>{best_moves[1][0].uci()}</h4>
                    <p>Score: {best_moves[1][1]:.2f}</p>
                </div>
            ''', unsafe_allow_html=True)

    # Game History section logo abaixo
    st.markdown("---")  # Linha separadora
    st.header("Game History")
    moves = st.session_state.board.move_stack
    move_history = ""
    for i, move in enumerate(moves):
        move_history += f"{i+1}. {move.uci()}\n"
    st.text_area("Moves", move_history, height=100, key="unique_game_history")

    st.write(st.session_state.evaluation_message)

if not st.session_state.game_over:
    if st.session_state.board.turn == chess.WHITE:

        fen = st.session_state.board.fen()
        print(fen)

        user_move = st.text_input("Digite seu movimento (ex: e2e4):")
        if st.button("Enviar Movimento"):
            move = None
            try:
                move = chess.Move.from_uci(user_move)
                print(move)
                if move in st.session_state.board.legal_moves:
                    coach_answer(fen, move)
                    st.session_state.board.push(move)

                    raw_evaluation = evaluate_move(st.session_state.board)
                    formatted_evaluation = format_evaluation(raw_evaluation)
                    interpreted_evaluation = interpret_evaluation(raw_evaluation)
                    st.session_state.evaluation_message = (
                        f"Avaliação do último movimento do humano: {interpreted_evaluation} ({formatted_evaluation})"
                    )

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

# CSS Customization for the layout
st.markdown(
    """
    <style>
    .suggested-moves-title {
        font-size: 20px;
        font-weight: bold;
    }
    .suggested-move-card {
        background-color: #333;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: white;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

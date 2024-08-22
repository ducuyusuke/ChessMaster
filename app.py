import streamlit as st
import chess
import chess.svg
import chess.pgn
from io import StringIO
import torch
from chess_engine import ChessMovePredictionModel
import random
import streamlit as st
import streamlit.components.v1 as components
import os

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


model = ChessMovePredictionModel()
model.load_state_dict(torch.load('chess_model.pth'))
model.eval()


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


board_svg = chess.svg.board(board=st.session_state.board)
st.markdown(f'<div>{board_svg}</div>', unsafe_allow_html=True)


if st.session_state.board.turn == chess.WHITE:

    user_move = st.text_input("Digite seu movimento (ex: e2e4):")

    if st.button("Enviar Movimento"):
        try:
            move = chess.Move.from_uci(user_move)
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move)
                st.experimental_rerun()
        except:
            st.write("Movimento inválido. Use a notação correta (ex: e2e4).")

else:

    st.write("Turno do bot...")
    bot_move()
    st.experimental_rerun()


if st.button("Reiniciar Jogo"):
    st.session_state.board.reset()
    st.experimental_rerun()

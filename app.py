import streamlit as st
import chess
import chess.svg
import torch
from chess_engine import ChessMovePredictionModel
import random
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
if 'show_suggested' not in st.session_state:
    st.session_state.show_suggested = False    
if 'show_coach' not in st.session_state:
    st.session_state.show_coach = False    
def toggle_suggested():
    st.session_state.show_suggested = not st.session_state.show_suggested

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

# Left column: Chess board and user input
with col1:
    board_svg = chess.svg.board(board=st.session_state.board)
    st.markdown(f'<div>{board_svg}</div>', unsafe_allow_html=True)

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

def toggle_coach():
    st.session_state.show_coach = not st.session_state.show_coach
# Right column: Suggested moves and Game History
with col2:
    # Game History section logo abaixo
    moves = st.session_state.board.move_stack
    move_history = ""
    evaluation = ""
    button_label = "Show Coach Analysis" if not st.session_state.show_coach else "Hide Coach Analysis"
    if st.button(button_label, on_click=toggle_coach, key="coach"):
        pass
    for i, move in enumerate(moves):
            move_history += f"{i+1}. {move.uci()} - " 
    if st.session_state.show_coach:
        st.write("This is an AI analysis of the last move")     
        for i, move in enumerate(moves):
            if i % 2 == 0:     
                evaluation = coach_answer(move_history)
    else:
        st.write(" ")
        
            

    move_history = move_history.rstrip(" - ")





    st.markdown(f'''
        <div class="move-analysis-card">
            <div class="top-line" style="background-color: blue;"></div>
            <div class="piece-icon">&#9817;</div>
            <p>{evaluation}</p>
        </div>
    ''', unsafe_allow_html=True)

    # Suggested Moves section with two cards side by side
    button_label = "Show Suggested Moves" if not st.session_state.show_suggested else "Hide Suggested Moves"
    if st.button(button_label, on_click=toggle_suggested, key="suggested"):
        pass
    if st.session_state.show_suggested:
        st.write("These are some AI based suggested moves")
        st.markdown('<div class="suggested-moves-title">Suggested Moves</div>', unsafe_allow_html=True)
        st.markdown('<div class="suggested-moves-container">', unsafe_allow_html=True)
        best_moves = suggest_best_moves_for_white(st.session_state.board, num_moves=2)

        col_moves1, col_moves2 = st.columns(2)  # Ajusta as sugestões de movimentos para ficarem lado a lado

        if len(best_moves) > 0:
            with col_moves1:
                st.markdown(f'''
                    <div class="suggested-move-card">
                        <h4>{best_moves[0][0].uci()}</h4>
                        <p>Lead: {best_moves[0][1]:.2f}</p>
                    </div>
                ''', unsafe_allow_html=True)

        if len(best_moves) > 1:
            with col_moves2:
                st.markdown(f'''
                    <div class="suggested-move-card">
                        <h4>{best_moves[1][0].uci()}</h4>
                        <p>Lead: {best_moves[1][1]:.2f}</p>
                    </div>
                ''', unsafe_allow_html=True)
    else:
        st.write(" ")

    st.header("Game History")
    st.text_area("", move_history, height=50)




# CSS Customization for the layout
st.markdown(
    """
    <style>
    .suggested-moves-title {
        font-size: 20px;
        font-weight: bold;
        margin-top: 10px;
    }
    .suggested-moves-container {
        display: flex;
        justify-content: space-between;
    }
    .suggested-move-card {
        background-color: #333;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: white;
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

    .move-analysis-card {
        background-color: #222222;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        text-align: center;
        position: relative;
    }

    .move-analysis-card .top-line {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
    }

    .move-analysis-card .piece-icon {
        font-size: 48px;
        color: white;
        margin-top: 10px;
    }

    .move-analysis-card p {
        color: white;
        font-size: 14px;
        margin: 0;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

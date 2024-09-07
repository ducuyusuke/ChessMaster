import chess
import streamlit as st



def format_evaluation(value):
    if value > 0:
        return f"Vantagem das Brancas: ♔ +{value:.2f}"
    elif value < 0:
        return f"Vantagem das Pretas: ♚ {value:.2f}"
    else:
        return "Posição equilibrada: ="

def interpret_evaluation(score):
    if score is None:
        return "Avaliação não disponível"

    if hasattr(score, 'mate') and score.mate() is not None:
        if score.mate() > 0:
            return "Vitória iminente das Brancas"
        else:
            return "Vitória iminente das Pretas"
    elif hasattr(score, 'relative') and score.relative.score() is not None:
        evaluation = score.relative.score() / 100.0
        if evaluation > 1.0:
            return "Grande vantagem das Brancas"
        elif evaluation > 0:
            return "Vantagem das Brancas"
        elif evaluation == 0:
            return "Posição equilibrada"
        elif evaluation > -1.0:
            return "Vantagem das Pretas"
        else:
            return "Grande vantagem das Pretas"
    else:
        return "Avaliação não disponível"



def evaluate_move(board):
    with chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish") as engine:
        info = engine.analyse(board, chess.engine.Limit(time=0.1))
        score = info.get('score')


        if score is None or not hasattr(score, 'relative'):
            return None

        relative_score = score.relative.score() / 100.0 if score.relative.score() is not None else None
        if relative_score is None:
            return 0.0

        return relative_score



#stockfish sugere jogadas
def suggest_best_moves_for_white(board, num_moves=2):
    with chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish") as engine:
        info = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=num_moves)
        suggestions = []
        moves_played = [move.uci() for move in board.move_stack]

        for item in info:
            if 'pv' in item and 'score' in item:
                move = item['pv'][0]
                score = item['score'].relative.score() if item['score'].relative.score() is not None else 0.0
                if move.uci() not in moves_played:
                    suggestions.append((move, score / 100.0))  # Divide o score apenas se ele não for None
            else:
                st.write("Movimento sugerido não disponível nesta análise.")

    return suggestions

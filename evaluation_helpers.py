import chess


def format_evaluation(value):
    if value > 0:
        return f"Vantagem das Brancas: ♔ +{value:.2f}"
    elif value < 0:
        return f"Vantagem das Pretas: ♚ {value:.2f}"
    else:
        return "Posição equilibrada: ="

def interpret_evaluation(value):
    if value > 1:
        return "Vantagem clara das Brancas"
    elif 0.5 < value <= 1:
        return "Pequena vantagem das Brancas"
    elif -0.5 <= value <= 0.5:
        return "Posição equilibrada"
    elif -1 <= value < -0.5:
        return "Pequena vantagem das Pretas"
    else:
        return "Vantagem clara das Pretas"
def evaluate_move(board):
    with chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish") as engine:
        info = engine.analyse(board, chess.engine.Limit(time=0.1))
        score = info["score"].relative.score()
        if score is None:
            return 0
        return score / 100.0

import chess
import streamlit as st
import time

board = chess.Board()

class Minimax:
    def __init__(self, depth, alpha_beta=True):
        self.depth = depth
        self.alpha_beta = alpha_beta
        self.alpha = -float('inf')
        self.beta = float('inf')

    # def minimax(self, board, depth, is_maximizing):
    #     if depth == 0 or board.outcome():
    #         return self.evaluate_board(board)

    #     if is_maximizing == True:
    #         best_score = -float('inf')
    #         for move in board.legal_moves:
    #             board.push(move)
    #             score = self.minimax(board, depth - 1, False)
    #             board.pop()
    #             best_score = max(best_score, score)
    #             if self.alpha_beta:
    #                 self.alpha = max(self.alpha, best_score)
    #                 if self.beta <= self.alpha:
    #                     break
    #         return best_score
    #     else:
    #         best_score = float('inf')
    #         for move in board.legal_moves:
    #             board.push(move)
    #             score = self.minimax(board, depth - 1, True)
    #             board.pop()
    #             best_score = min(best_score, score)
    #             if self.alpha_beta:
    #                 self.beta = min(self.beta, best_score)
    #                 if self.beta <= self.alpha:
    #                     break
    #         return best_score
    
    def minimax(self, board, depth, is_maximizing, alpha, beta):
        if depth == 0 or board.is_checkmate() or board.is_stalemate():
            return self.evaluate_board(board)
        if is_maximizing:
            best_score = -float('inf')
            for move in board.legal_moves:
                board_copy = board.copy()
                board_copy.push(move)
                score = self.minimax(board_copy, depth - 1, False, alpha, beta)
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score
        else:
            best_score = float('inf')
            for move in board.legal_moves:
                board_copy = board.copy()
                board_copy.push(move)
                score = self.minimax(board_copy, depth - 1, True, alpha, beta)
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_score

    def evaluate_board(self, board):
        score = 0
        king_safety = 0
        king_square = board.king(board.turn)
        king = board.piece_at(king_square)
        for piece in board.piece_map().values():
            if piece.color == chess.BLACK:
                score += self.get_piece_value(piece.piece_type)
            elif piece.color == chess.WHITE:
                score -= self.get_piece_value(piece.piece_type)
            if piece.color != board.turn:
                if piece.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP]:
                    king_safety -= 0.1 * self.get_attack_value(piece, king, board)
            # Mobility term
            mobility = len(list(board.legal_moves))
            score += 0.01 * mobility
        score += king_safety
        return score

    def get_piece_value(self, piece_type):
        piece_values = {
            chess.KING: 100,
            chess.QUEEN: 9,
            chess.ROOK: 5,
            chess.BISHOP: 3,
            chess.KNIGHT: 3,
            chess.PAWN: 1
        }
        return piece_values[piece_type]
    
    def get_attack_value(self, piece, king, board):
        value = 0
        if piece.piece_type == chess.QUEEN:
            value += 1
        elif piece.piece_type == chess.ROOK:
            value += 0.5
        elif piece.piece_type == chess.BISHOP:
            value += 0.3
        if piece.color == king.color:
            value = -value
        return value
    
    def get_best_move(self, depth, board, time_limit=10):
        self.alpha = -float('inf')  # Reset alpha value
        self.beta = float('inf')  # Reset beta value
        start_time = time.time()
        best_move = None
        best_eval = -float('inf')
        for move in board.legal_moves:
            board_copy = board.copy()  # Create a copy of the current board
            board_copy.push(move)
            eval = self.minimax(board_copy, depth - 1, True, self.alpha, self.beta)
            if eval > best_eval:
                best_eval = eval
                best_move = move
            if time.time() - start_time > time_limit: 
                break
        return best_move
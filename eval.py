from piece import piece_val
from board import Board
from position_table import pawn_table, bishop_table, king_table, knight_table, rook_table, queen_table, queen_table

def score(board): # score the board on number of pieces
    score = 0
    for row in board.board:
        for piece in row:
            if piece:
                # Add or subtract the value of the piece based on its color
                piece_value = piece_val[piece.piece_type.lower()]
                if piece.color == 'w':
                    score += piece_value
                elif piece.color == 'b':
                    score -= piece_value

    return score

def eval(board):
    s = 0
    s += score(board.board)
    return s

if __name__ == "__main__":
    board = Board(
        # fen="8/p2K1p2/3bB3/1P6/p1R1p2p/rP6/2P1p2P/3k4" # r1 (-6.5)
        # fen='7K/1n6/2k3P1/8/4Pp2/4Bp2/1P3P2/8' # r2 (#13w)
        # fen='8/p4p2/3KP1b1/7k/6p1/8/4Q1P1/7q' # r3 (0.0)
    )
    print("FEN:", board.fen, board.current_turn)
    print("Evaluation score:", eval(board))   
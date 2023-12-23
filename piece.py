import numpy as np
import pygame
import os

fen_to_piece = {
    'r': 'br',
    'n': 'bn',
    'b': 'bb',
    'q': 'bq',
    'k': 'bk',
    'p': 'bp',
    'R': 'wr',
    'N': 'wn',
    'B': 'wb',
    'Q': 'wq',
    'K': 'wk',
    'P': 'wp'
}

piece_val = { # takes in lower(piece) as input
    'r':5,
    'p':1,
    'b':3,
    'n':3,
    'q':9,
    'k':1e7,
}

class Piece:
    def __init__(self, piece_char, square_size):
        self.piece_char = piece_char
        self.color = 'w' if piece_char.isupper() else 'b'
        self.piece_type = piece_char.lower()
        self.image = self.load_image(square_size)
        self.value = self.set_value()

    def load_image(self, square_size):
        file_name = fen_to_piece[self.piece_char] + '.png'
        image_path = os.path.join('pieces', file_name)
        return pygame.transform.scale(pygame.image.load(image_path), (square_size, square_size))

    def set_value(self):
        return piece_val[self.piece_type]

    def is_legal_move(self, start_pos, end_pos, board):
        # This method should be overridden in subclasses
        raise NotImplementedError

class Pawn(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        direction = -1 if self.color == 'w' else 1
        start_col, start_row = start_pos
        end_col, end_row = end_pos
        piece_at_end = board[end_row][end_col]

        # Check for a standard one-step forward move
        if start_col == end_col and end_row == start_row + direction:
            return not piece_at_end

        # Check for the initial two-step forward move
        if start_col == end_col and start_row in (1, 6) and end_row == start_row + 2 * direction:
            # Ensure path is clear for two-step move
            path_clear = not board[start_row + direction][start_col] and not piece_at_end
            return path_clear

        # Check for a diagonal capture
        if end_row == start_row + direction and abs(end_col - start_col) == 1:
            return piece_at_end is not None and piece_at_end.color != self.color

        # If none of the above conditions are met, it's not a legal move
        return False

class Rook(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        # Simplified rook logic (not checking for obstructions)
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        return start_row == end_row or start_col == end_col

class Knight(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

class Bishop(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        # Simplified bishop logic (not checking for obstructions)
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        return abs(start_row - end_row) == abs(start_col - end_col)

class Queen(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        # Combines rook and bishop movement
        return Rook.is_legal_move(self, start_pos, end_pos, board) or Bishop.is_legal_move(self, start_pos, end_pos, board)

class King(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        # Simplified king logic (not including castling)
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        return row_diff <= 1 and col_diff <= 1


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

        # En passant (optional, can be implemented as an additional feature)
        # ...

        # If none of the above conditions are met, it's not a legal move
        return False


class Rook(Piece):
    def __init__(self, piece_char, square_size):
        super().__init__(piece_char, square_size)
        self.moved = False
        
    def is_legal_move(self, start_pos, end_pos, board):

        start_col, start_row = start_pos
        end_col, end_row = end_pos

        # Rook moves either vertically or horizontally
        if start_row != end_row and start_col != end_col:
            return False  # Not a straight line

        # Check if any pieces are in the way
        if start_row == end_row:  # Horizontal move
            col_range = range(min(start_col, end_col) + 1, max(start_col, end_col))
            for col in col_range:
                if board[start_row][col] is not None:
                    return False
        else:  # Vertical move
            row_range = range(min(start_row, end_row) + 1, max(start_row, end_row))
            for row in row_range:
                if board[row][start_col] is not None:
                    return False

        # If destination square is occupied, it must be an opponent's piece
        destination_piece = board[end_row][end_col]
        if destination_piece is not None and destination_piece.color == self.color:
            return False

        return True


class Knight(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        start_col, start_row = start_pos
        end_col, end_row = end_pos

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Knight moves in an L-shape: 2 squares in one direction and 1 square in the other
        if not ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)):
            return False  # Not a valid knight move

        # If destination square is occupied, it must not be a friendly piece
        destination_piece = board[end_row][end_col]
        if destination_piece is not None and destination_piece.color == self.color:
            return False

        return True

class Bishop(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        start_col, start_row = start_pos
        end_col, end_row = end_pos

        # Bishop moves diagonally
        if abs(start_row - end_row) != abs(start_col - end_col):
            return False  # Not a diagonal move

        # Check if any pieces are in the way
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        for step in range(1, abs(end_row - start_row)):
            row = start_row + step * row_step
            col = start_col + step * col_step
            if board[row][col] is not None:
                return False

        # If destination square is occupied, it must be an opponent's piece
        destination_piece = board[end_row][end_col]
        if destination_piece is not None and destination_piece.color == self.color:
            return False

        return True
    
class Queen(Piece):
    def is_legal_move(self, start_pos, end_pos, board):
        # Combines rook and bishop movement
        return Rook.is_legal_move(self, start_pos, end_pos, board) or Bishop.is_legal_move(self, start_pos, end_pos, board)

class King(Piece):
    def __init__(self, piece_char, square_size):
        super().__init__(piece_char, square_size)
        self.moved = False

    def is_legal_move(self, start_pos, end_pos, board):
        start_col, start_row = start_pos
        end_col, end_row = end_pos

        row_diff = abs(start_row - end_row)
        col_diff = abs(start_col - end_col)

        # Standard king move
        if row_diff <= 1 and col_diff <= 1:
            destination_piece = board[end_row][end_col]
            if destination_piece is None or destination_piece.color != self.color:
                return True

        # Castling move
        if not self.moved and row_diff == 0 and col_diff == 2:
            direction = 1 if end_col > start_col else -1  # 1 for kingside, -1 for queenside
            rook_col = 7 if direction == 1 else 0  # Rook's starting column for castling
            rook = board[start_row][rook_col]
            
            # Check if the rook is eligible for castling
            if isinstance(rook, Rook) and not rook.moved:
                # Check the squares between the king and the rook
                if direction == 1:  # Kingside castling
                    intermediate_squares = [5, 6]  # Squares the king will pass through
                else:  # Queenside castling
                    intermediate_squares = [1, 2, 3]  # Squares the king will pass through, including the destination square of the rook
                    
                # Check if the squares are empty and not under attack
                for col in intermediate_squares:
                    if board[start_row][col] is not None or self.is_square_under_attack((start_row, col), board):
                        return False
                    
                # Additional check for queenside castling, the square next to the rook must also be empty, though king does not pass through it
                if direction == -1 and board[start_row][1] is not None:
                    return False

                return True


    def is_square_under_attack(self, position, board):
        # Check if the position is under attack
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.color != self.color and piece.is_legal_move((col, row), position, board):
                    return True
        return False

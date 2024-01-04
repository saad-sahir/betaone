import numpy as np
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
    def __init__(self, piece_char):
        self.piece_char = piece_char
        self.color = 'w' if piece_char.isupper() else 'b'
        self.piece_type = piece_char.lower()
        self.value = self.set_value()

    def set_value(self):
        return piece_val[self.piece_type]

    def is_legal_move(self, start_pos, end_pos, board, last_move):
        # This method should be overridden in subclasses
        raise NotImplementedError
    
    def __repr__(self):
        return self.piece_char

class Pawn(Piece):
    def is_legal_move(self, start_pos, end_pos, board, last_move):
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
        
        # En passant logic
        if last_move and last_move['piece'].piece_type.lower() == 'p':
            # Check if the pawn is in the correct rank
            if (self.color == 'w' and start_row == 3) or (self.color == 'b' and start_row == 4):
                # Check if it's a diagonal move to an empty square
                if abs(end_col - start_col) == 1 and end_row == start_row + direction and not piece_at_end:
                    # Check if the last move was a two-square move
                    _, last_start_row = last_move['start_pos']
                    last_end_col, last_end_row = last_move['end_pos']
                    if abs(last_start_row - last_end_row) == 2 and last_end_col == end_col:
                        return True


        # If none of the above conditions are met, it's not a legal move
        return False


class Rook(Piece):
    def __init__(self, piece_char):
        super().__init__(piece_char)
        self.moved = False
        
    def is_legal_move(self, start_pos, end_pos, board, last_move):

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
    def is_legal_move(self, start_pos, end_pos, board, last_move):
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
    def is_legal_move(self, start_pos, end_pos, board, last_move):
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
    def is_legal_move(self, start_pos, end_pos, board, last_move):
        # Combines rook and bishop movement
        return Rook.is_legal_move(self, start_pos, end_pos, board, last_move) or Bishop.is_legal_move(self, start_pos, end_pos, board, last_move)

class King(Piece):
    def __init__(self, piece_char):
        super().__init__(piece_char)
        self.moved = False

    def is_legal_move(self, start_pos, end_pos, board, last_move):
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
            if self.is_in_check(board, last_move):
                return False  # Cannot castle while in check

            direction = 1 if end_col > start_col else -1
            rook_col = 7 if direction == 1 else 0
            rook = board[start_row][rook_col]

            # Check if the rook is eligible for castling
            if isinstance(rook, Rook) and not rook.moved:
                intermediate_squares = [start_col + i * direction for i in range(1, abs(end_col - start_col))]
                for col in intermediate_squares:
                    if self.is_square_under_attack((start_row, col), board, last_move):
                        return False

                return True

        return False

    def is_in_check(self, board, last_move):
        # Check if the king is in check
        king_position = None
        for y in range(8):
            for x in range(8):
                if isinstance(board[y][x], King) and board[y][x].color == self.color:
                    king_position = (x, y)
                    break
            if king_position:
                break

        return self.is_square_under_attack(king_position, board, last_move)


    def is_square_under_attack(self, position, board, last_move):
        # Check if the position is under attack
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece and piece.color != self.color and piece.is_legal_move((col, row), position, board, last_move):
                    return True
        return False

import pygame
import os
from piece import Pawn, Rook, King, Knight, Queen, Bishop

class Board:

    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", turn="w", print=False):
        self._print = print
        self.current_turn = turn # 'w' for white, 'b' for black
        self.fen = fen
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 grid for chess pieces
        self.set_positions_from_FEN(fen)
        self.selected_piece = None 
        self.last_move = None

    ## Helper Functions

    def set_positions_from_FEN(self, fen):
        # Initialize board with Piece instances based on FEN string
        piece_classes = {'p': Pawn, 'r': Rook, 'n': Knight, 'b': Bishop, 'q': Queen, 'k': King}
        fen_rows = fen.split(' ')[0].split('/')
        for row_index, fen_row in enumerate(fen_rows):
            col_index = 0
            for char in fen_row:
                if char.isdigit():
                    col_index += int(char)
                else:
                    piece_type = char.lower()
                    self.board[row_index][col_index] = piece_classes[piece_type](char)
                    col_index += 1

    def _toFEN(self):
        piece_to_fen = {
            'br': 'r', 'bn': 'n', 'bb': 'b', 'bq': 'q', 'bk': 'k', 'bp': 'p',
            'wr': 'R', 'wn': 'N', 'wb': 'B', 'wq': 'Q', 'wk': 'K', 'wp': 'P'
        }

        fen_rows = []
        for row in range(8):
            empty_squares = 0
            fen_row = ''
            for col in range(8):
                piece = self.board[row][col]
                if piece is None:
                    empty_squares += 1
                else:
                    if empty_squares > 0:
                        fen_row += str(empty_squares)
                        empty_squares = 0
                    # Construct the key for the piece_to_fen dictionary
                    piece_key = piece.color + piece.piece_type
                    fen_character = piece_to_fen[piece_key]
                    fen_row += fen_character.upper() if piece.color == 'w' else fen_character.lower()
            if empty_squares > 0:
                fen_row += str(empty_squares)
            fen_rows.append(fen_row)

        # The FEN string should start with the rank 8 and end with rank 1 (board[0][0] is the a1 square)
        fen = '/'.join(fen_rows[::-1])
        return(fen)
    
    def is_in_check(self, king_color):
        # Find the king's position
        king_position = None
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color == king_color and piece.piece_type == 'k':
                    king_position = (x, y)
                    break
            if king_position:
                break

        # Check if any opponent's piece can attack the king
        opponent_color = 'b' if king_color == 'w' else 'w'
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color == opponent_color:
                    if piece.is_legal_move((x, y), king_position, self.board, self.last_move):
                        return True
        return False
    
    def is_checkmate(self, king_color):
        if not self.is_in_check(king_color):
            return False
        # Check if any move can remove the check
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece and piece.color == king_color:
                    for row in range(8):
                        for col in range(8):
                            if piece.is_legal_move((x, y), (col, row), self.board):
                                self.board[y][x] = None
                                temp_piece = self.board[row][col]
                                self.board[row][col] = piece
                                if not self.is_in_check(king_color):
                                    # Undo move
                                    self.board[row][col] = temp_piece
                                    self.board[y][x] = piece
                                    return False
                                # Undo move
                                self.board[row][col] = temp_piece
                                self.board[y][x] = piece
        return True
    
    def is_pawn_promotion(self, piece, new_position):
        if isinstance(piece, Pawn) and (new_position[1] == 0 or new_position[1] == 7):
            return True
        return False

    def is_square_under_attack(self, position, color):
        opponent_color = 'w' if color == 'b' else 'b'
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == opponent_color:
                    if piece.is_legal_move((col, row), position, self.board):
                        return True
        return False
    
    def update_last_move(self, piece, start_pos, end_pos):
        self.last_move = {'piece': piece, 'start_pos': start_pos, 'end_pos': end_pos}

    ## Legal moves

    def _legal_moves(self, piece, position):
        legal_moves = []
        is_king = piece.piece_type == 'k'

        for row in range(8):
            for col in range(8):
                if piece.is_legal_move(position, (col, row), self.board, self.last_move):
                    # Temporarily make the move
                    original_piece = self.board[row][col]
                    self.board[row][col] = piece
                    self.board[position[1]][position[0]] = None

                    # If the piece is a king, check for direct checks
                    if is_king:
                        in_check = any(
                            opp_piece.is_legal_move((opp_x, opp_y), (col, row), self.board)
                            for opp_y in range(8)
                            for opp_x in range(8)
                            if (opp_piece := self.board[opp_y][opp_x]) 
                            and opp_piece.color != piece.color
                        )
                    else:
                        in_check = self.is_in_check(piece.color)

                    # En passant logic for Pawns
                    if not in_check and isinstance(piece, Pawn) and self.last_move:
                        last_piece = self.last_move['piece']
                        last_start_pos = self.last_move['start_pos']
                        last_end_pos = self.last_move['end_pos']
                        if last_piece.piece_type.lower() == 'p' and abs(last_start_pos[1] - last_end_pos[1]) == 2:
                            if (piece.color == 'w' and position[1] == 3) or (piece.color == 'b' and position[1] == 4):
                                # Check if the last move ended beside the current pawn
                                if abs(position[0] - last_end_pos[0]) == 1 and last_end_pos[1] == position[1]:
                                    en_passant_capture_pos = (last_end_pos[0], position[1] + (1 if piece.color == 'b' else -1))
                                    legal_moves.append(en_passant_capture_pos)

                    # Additional Castling Logic for King
                    if is_king and not piece.moved and not self.is_in_check(piece.color):
                        # Check both sides for castling
                        for direction in [1, -1]:
                            rook_col = 7 if direction == 1 else 0
                            rook = self.board[position[1]][rook_col]
                            if isinstance(rook, Rook) and not rook.moved:
                                path_clear = all(self.board[position[1]][position[0] + i * direction] is None 
                                                for i in range(1, abs(rook_col - position[0])))
                                if path_clear:
                                    # Check if the king passes through an attacked square
                                    squares_to_check = [(position[0] + i * direction, position[1]) for i in range(1, 3)]
                                    if all(not self.is_square_under_attack(square, piece.color) for square in squares_to_check):
                                        castling_move = (position[0] + 2 * direction, position[1])
                                        legal_moves.append(castling_move)

                    # Pawn promotion logic
                    if isinstance(piece, Pawn) and (row == 0 or row == 7):
                        in_check = self.is_in_check(piece.color)

                    # If not in check, add to legal moves
                    if not in_check:
                        legal_moves.append((col, row))

                    # Undo the move
                    self.board[position[1]][position[0]] = piece
                    self.board[row][col] = original_piece

        return legal_moves
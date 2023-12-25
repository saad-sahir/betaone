import pygame
import os
from piece import Pawn, Rook, King, Knight, Queen, Bishop
from eval import getFEN

class Board:

    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR", turn="w", print=False):
        pygame.init()
        self._print = print
        self.window_size = 600
        self.square_size = self.window_size // 8
        self.black = (128, 70, 0)
        self.white = (255, 211, 157)
        self.highlight_color = (255, 141, 0)
        self.window = pygame.display.set_mode((self.window_size, self.window_size))
        self.current_turn = turn # 'w' for white, 'b' for black
        self.fen = fen
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 grid for chess pieces
        self.set_positions_from_FEN(fen)
        self.selected_piece = None
        self.running = True


    ## Helper Functions

    def pixel_to_board(self, x, y):
        return x // self.square_size, y // self.square_size
    
    def draw_board(self):
        legal_moves = []
        if self.selected_piece:
            legal_moves = self._legal_moves(self.selected_piece, self.selected_piece_position)
            # Highlight the current square of the selected piece
            legal_moves.append(self.selected_piece_position)

        for row in range(8):
            for col in range(8):
                color = self.white if (row + col) % 2 == 0 else self.black
                if (col, row) in legal_moves:
                    color = self.highlight_color
                pygame.draw.rect(self.window, color, (col * self.square_size, row * self.square_size, self.square_size, self.square_size))

    def draw_pieces(self):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    self.window.blit(piece.image, (col * self.square_size, row * self.square_size))

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
                    color = 'w' if char.isupper() else 'b'
                    piece_type = char.lower()
                    self.board[row_index][col_index] = piece_classes[piece_type](char, self.square_size)
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
                    if piece.is_legal_move((x, y), king_position, self.board):
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


    
    ## Legal moves

    def _legal_moves(self, piece, position):
        legal_moves = []
        is_king = piece.piece_type == 'k'

        for row in range(8):
            for col in range(8):
                if piece.is_legal_move(position, (col, row), self.board):
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

                    # Additional Castling Logic for King
                    if is_king and not piece.moved and not self.is_in_check(piece.color):
                        # Check both sides for castling
                        for direction in [1, -1]:
                            rook_col = 7 if direction == 1 else 0
                            rook = self.board[position[1]][rook_col]
                            if isinstance(rook, Rook) and not rook.moved:
                                # Check if path is clear
                                path_clear = all(self.board[position[1]][position[0] + i * direction] is None 
                                                for i in range(1, abs(rook_col - position[0])))
                                if path_clear:
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
    


    ## Game loop

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
                    self.fen = self._toFEN()
                    # print(self.fen)
                    getFEN(self.fen, _print=self._print)
            
            if self.is_checkmate(self.current_turn):
                self.running = False

            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()
            pygame.time.Clock().tick(60)
        pygame.quit()

        

    ## Mouse Click Handler

    def handle_mouse_click(self, pos):
        x, y = self.pixel_to_board(*pos)
        clicked_square = self.board[y][x]

        if self.selected_piece:
            new_position = (x, y)
            current_position = self.selected_piece_position

            if new_position != current_position and new_position in self._legal_moves(self.selected_piece, current_position):
                # Perform the move for non-promotion cases
                self.board[current_position[1]][current_position[0]] = None

                # Pawn promotion to queen
                if self.is_pawn_promotion(self.selected_piece, new_position):
                    promotion_piece = Queen('Q' if self.selected_piece.color == 'w' else 'q', self.square_size)
                    promotion_piece.color = self.selected_piece.color
                    self.board[y][x] = promotion_piece
                else:
                    self.board[y][x] = self.selected_piece
                
                    # Castling move for king
                    if isinstance(self.selected_piece, King) and abs(current_position[0] - new_position[0]) == 2:
                        direction = 1 if new_position[0] > current_position[0] else -1
                        rook_col = 7 if direction == 1 else 0
                        rook_new_col = 3 if direction == -1 else 5
                        # Move rook for castling
                        self.board[y][rook_new_col] = self.board[y][rook_col]
                        self.board[y][rook_col] = None
                        self.board[y][rook_new_col].moved = True

                # Update turn
                self.fen = self._toFEN()
                self.current_turn = 'b' if self.current_turn == 'w' else 'w'
                self.selected_piece.moved = True

            # Deselect the piece
            self.selected_piece = None

        elif clicked_square and clicked_square.color == self.current_turn:
            self.selected_piece = clicked_square
            self.selected_piece_position = (x, y)

if __name__ == "__main__":
    board = Board(
        # fen="r2k2nr/p2p1p1p/n2BN3/1pbNP2P/6P1/3P4/P1P1K3/q7", # random
        fen = "4r1r1/p1p2p1p/2k2p2/2p5/4PP2/P1N3P1/2P4P/2KRR3", # random2
        # fen='r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R', # test castling
        # fen='k7/7P/8/8/8/8/7p/K7', # test promotion
        # turn='b',
        # print=True
    )
    board.run()
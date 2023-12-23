import pygame
import os
from piece import Pawn, Rook, King, Knight, Queen, Bishop

class Board:
    def __init__(self, fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"):
        pygame.init()
        self.window_size = 600
        self.square_size = self.window_size // 8
        self.black = (128, 70, 0)
        self.white = (255, 211, 157)
        self.highlight_color = (255, 141, 0)
        self.window = pygame.display.set_mode((self.window_size, self.window_size))
        self.pieces_images = self.load_all_piece_images()
        self.fen = fen
        self.board = [[None for _ in range(8)] for _ in range(8)]  # 8x8 grid for chess pieces
        self.set_positions_from_FEN(fen)
        self.selected_piece = None
        self.running = True

    def load_piece_image(self, file_name):
        image = pygame.image.load(os.path.join('pieces', file_name))
        return pygame.transform.scale(image, (self.square_size, self.square_size))

    def load_all_piece_images(self):
        pieces_images = {}
        # Load pawns, rooks, knights, and bishops
        for piece in ['p', 'r', 'n', 'b']:
            for color in ['w', 'b']:
                for i in range(1, 9):
                    file_name = f'{color}{piece}.png'
                    piece_key = f'{color}{piece}{i}'
                    pieces_images[piece_key] = self.load_piece_image(file_name)

        # Load kings and queens
        for piece in ['k', 'q']:
            for color in ['w', 'b']:
                file_name = f'{color}{piece}.png'
                piece_key = f'{color}{piece}'
                pieces_images[piece_key] = self.load_piece_image(file_name)

        return pieces_images

    def pixel_to_board(self, x, y):
        return x // self.square_size, y // self.square_size

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)

            self.draw_board()
            self.draw_pieces()
            pygame.display.flip()
            pygame.time.Clock().tick(60)
        pygame.quit()

    def handle_mouse_click(self, pos):
        x, y = self.pixel_to_board(*pos)
        clicked_square = self.board[y][x]

        if self.selected_piece:
            new_position = (x, y)
            current_position = self.selected_piece_position

            # Check if the new position is different from the current position
            if new_position != current_position:
                if self.selected_piece.is_legal_move(current_position, new_position, self.board):
                    # Move the piece
                    self.board[y][x] = self.selected_piece
                    self.board[current_position[1]][current_position[0]] = None

            # Deselect the piece after the move or if clicked on the same square
            self.selected_piece = None

        elif clicked_square:
            self.selected_piece = clicked_square
            self.selected_piece_position = (x, y)


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

    def _printFEN(self):
        # Mapping from piece codes to FEN characters
        piece_to_fen = {
            'br': 'r', 'bn': 'n', 'bb': 'b', 'bq': 'q', 'bk': 'k', 'bp': 'p',
            'wr': 'R', 'wn': 'N', 'wb': 'B', 'wq': 'Q', 'wk': 'K', 'wp': 'P'
        }

        fen_rows = []
        for row in range(8):
            empty_squares = 0
            fen_row = ''
            for col in range(8):
                piece_found = False
                for piece, position in self.initial_positions.items():
                    if position == (col, row):  # Invert row to start from bottom
                        if empty_squares > 0:
                            fen_row += str(empty_squares)
                            empty_squares = 0
                        piece_code = piece if piece in ['bq', 'bk', 'wq', 'wk'] else piece[:-1]
                        fen_row += piece_to_fen[piece_code]
                        piece_found = True
                        break
                if not piece_found:
                    empty_squares += 1
            if empty_squares > 0:
                fen_row += str(empty_squares)
            fen_rows.append(fen_row)

        fen = '/'.join(fen_rows)
        print(fen)

    def _legal_moves(self, piece, position):
        legal_moves = []
        for row in range(8):
            for col in range(8):
                if piece.is_legal_move(position, (col, row), self.board):
                    legal_moves.append((col, row))
        return legal_moves
    
if __name__ == "__main__":
    board = Board(
        # fen="r2k2nr/p2p1p1p/n2BN3/1pbNP2P/6P1/3P4/P1P1K3/q7"
    )
    board.run()
    board._printFEN()
# run.py
import pygame
from board import Board
from piece import Pawn, Rook, King, Knight, Queen, Bishop
import os

fen_to_piece = {
        'r': 'br', 'n': 'bn', 'b': 'bb', 'q': 'bq', 'k': 'bk', 'p': 'bp',
        'R': 'wr', 'N': 'wn', 'B': 'wb', 'Q': 'wq', 'K': 'wk', 'P': 'wp'
    }

def load_images(square_size):
    images = {}
    for name in ['br', 'bn', 'bb', 'bq', 'bk', 'bp', 'wr', 'wn', 'wb', 'wq', 'wk', 'wp']:
        image = pygame.image.load(os.path.join('pieces', name + '.png'))
        images[name] = pygame.transform.scale(image, (square_size, square_size))
    return images

def draw_pieces(window, board, images, square_size):
    for y in range(8):
        for x in range(8):
            piece = board.board[y][x]
            if piece:
                image_name = fen_to_piece[piece.piece_char]
                window.blit(images[image_name], (x * square_size, y * square_size))

def run_game(board):
    pygame.init()
    window_size = 600
    square_size = window_size // 8
    black = (128, 70, 0)
    white = (255, 211, 157)
    highlight_color = (255, 141, 0)
    window = pygame.display.set_mode((window_size, window_size))
    running = True
    piece_images = load_images(square_size)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(event.pos, board, window, square_size)

        if board.is_checkmate(board.current_turn):
            running = False

        draw_board(board, window, square_size, white, black, highlight_color, piece_images)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()

def draw_board(board, window, square_size, white, black, highlight_color, piece_images):
    legal_moves = []
    if board.selected_piece:
        legal_moves = board._legal_moves(board.selected_piece, board.selected_piece_position)
        legal_moves.append(board.selected_piece_position)

    for row in range(8):
        for col in range(8):
            color = white if (row + col) % 2 == 0 else black
            if (col, row) in legal_moves:
                color = highlight_color
            pygame.draw.rect(window, color, (col * square_size, row * square_size, square_size, square_size))
            piece = board.board[row][col]
            if piece:
                piece_image = piece_images[fen_to_piece[piece.piece_char]]
                window.blit(piece_image, (col * square_size, row * square_size))

def handle_mouse_click(pos, board, _, square_size):
    x, y = pixel_to_board(pos, square_size)
    clicked_square = board.board[y][x]

    if board.selected_piece:
        new_position = (x, y)
        current_position = board.selected_piece_position

        if new_position != current_position and new_position in board._legal_moves(board.selected_piece, current_position):
            # Perform the move for non-promotion cases
            board.board[current_position[1]][current_position[0]] = None

            # Pawn promotion to queen
            if board.is_pawn_promotion(board.selected_piece, new_position):
                promotion_piece = Queen('Q' if board.selected_piece.color == 'w' else 'q', square_size)
                promotion_piece.color = board.selected_piece.color
                board.board[y][x] = promotion_piece
            else:
                board.board[y][x] = board.selected_piece
            
                # Castling move for king
                if isinstance(board.selected_piece, King) and abs(current_position[0] - new_position[0]) == 2:
                    direction = 1 if new_position[0] > current_position[0] else -1
                    rook_col = 7 if direction == 1 else 0
                    rook_new_col = 3 if direction == -1 else 5
                    # Move rook for castling
                    board.board[y][rook_new_col] = board.board[y][rook_col]
                    board.board[y][rook_col] = None
                    board.board[y][rook_new_col].moved = True

            # Update turn
            board.fen = board._toFEN()
            board.current_turn = 'b' if board.current_turn == 'w' else 'w'
            board.selected_piece.moved = True

        # Deselect the piece
        board.selected_piece = None

    elif clicked_square and clicked_square.color == board.current_turn:
        board.selected_piece = clicked_square
        board.selected_piece_position = (x, y)

def pixel_to_board(pos, square_size):
    x, y = pos
    return x // square_size, y // square_size

if __name__ == "__main__":
    board = Board()
    run_game(board)
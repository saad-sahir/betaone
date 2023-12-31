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
        legal_moves = board.legal_moves(board.selected_piece, board.selected_piece_position)
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

        if new_position != current_position and new_position in board.legal_moves(board.selected_piece, current_position):
            # Perform the move for non-promotion cases
            moving_piece = board.selected_piece
            board.board[current_position[1]][current_position[0]] = None

            # En passant capture logic
            if isinstance(moving_piece, Pawn):
                if abs(current_position[1] - new_position[1]) == 1 and current_position[0] != new_position[0] and not clicked_square:
                    capture_row = current_position[1]
                    board.board[capture_row][new_position[0]] = None  # Remove the captured pawn

            # Place the moving piece in the new position
            board.board[y][x] = moving_piece

            # Pawn promotion to queen
            if board.is_pawn_promotion(moving_piece, new_position):
                promotion_piece = Queen('Q' if moving_piece.color == 'w' else 'q')
                promotion_piece.color = moving_piece.color
                board.board[y][x] = promotion_piece
            else:
                board.board[y][x] = moving_piece
            
            # Castling move for king
            if isinstance(moving_piece, King) and abs(current_position[0] - new_position[0]) == 2:
                direction = 1 if new_position[0] > current_position[0] else -1
                rook_col = 7 if direction == 1 else 0
                rook_new_col = 3 if direction == -1 else 5
                # Move rook for castling
                board.board[y][rook_new_col] = board.board[y][rook_col]
                board.board[y][rook_col] = None
                board.board[y][rook_new_col].moved = True

            # Update last move
            board.update_last_move(moving_piece, current_position, new_position)

            # Update turn
            board.fen = board._toFEN()
            board.current_turn = 'b' if board.current_turn == 'w' else 'w'
            board.selected_piece.moved = True

            # Debug
            print(board.last_move)
            print(board.fen)

        # Deselect the piece
        board.selected_piece = None

    elif clicked_square and clicked_square.color == board.current_turn:
        board.selected_piece = clicked_square
        board.selected_piece_position = (x, y)


def pixel_to_board(pos, square_size):
    x, y = pos
    return x // square_size, y // square_size

if __name__ == "__main__":
    board = Board(
        fen="r2k2nr/p2p1p1p/n2BN3/1pbNP2P/6P1/3P4/P1P1K3/q7", # random
        # fen = "4r1r1/p1p2p1p/2k2p2/2p5/4PP2/P1N3P1/2P4P/2KRR3", # random2
        # fen='r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R', # test castling
        # fen='k7/7P/8/8/8/8/7p/K7', # test promotion
        # fen="8/p2K1p2/3bB3/1P6/p1R1p2p/rP6/2P1p2P/3k4" # r1 (-6.5)
        # fen='7K/1n6/2k3P1/8/4Pp2/4Bp2/1P3P2/8' # r2 (#13w)
        # fen='8/p4p2/3KP1b1/7k/6p1/8/4Q1P1/7q' # r3 (0.0)
        turn='b',
    )
    run_game(board)
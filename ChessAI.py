import pygame
import chess
import os


class ChessAI:
    def __init__(self) -> None:
        pygame.init()
        self.__size = 400
        self.__squares = {}
        self.__pieces = {}
        self.__board = chess.Board()
        self.__square_size = self.__size // 8
        self.__screen = pygame.display.set_mode((self.__size, self.__size))

        self.__init_squares()
        self.__init_pieces()

        self.__running = True
        self.__selected_square = None

    @staticmethod
    def __invert_position(position: str) -> str:
        return chess.square_name(chess.square_mirror(chess.parse_square(position)))

    def __square_to_pixel(self, square: int, error: int = 2) -> (int, int):
        col = square // 8
        row = square % 8
        return row * self.__square_size + error, col * self.__square_size + error

    def __init_squares(self) -> None:
        for i in range(64):
            square_name = chess.SQUARE_NAMES[i]
            x, y = chess.square_file(i), chess.square_rank(i)
            rect = pygame.Rect(x * self.__square_size, y * self.__square_size, self.__square_size, self.__square_size)
            self.__squares[square_name] = rect

    def __init_pieces(self) -> None:
        self.__pieces = {
            'P': pygame.image.load(os.path.join('pieces_png', 'white_P.png')),
            'p': pygame.image.load(os.path.join('pieces_png', 'black_p.png')),
            'R': pygame.image.load(os.path.join('pieces_png', 'white_R.png')),
            'r': pygame.image.load(os.path.join('pieces_png', 'black_r.png')),
            'B': pygame.image.load(os.path.join('pieces_png', 'white_B.png')),
            'b': pygame.image.load(os.path.join('pieces_png', 'black_b.png')),
            'K': pygame.image.load(os.path.join('pieces_png', 'white_K.png')),
            'k': pygame.image.load(os.path.join('pieces_png', 'black_k.png')),
            'Q': pygame.image.load(os.path.join('pieces_png', 'white_Q.png')),
            'q': pygame.image.load(os.path.join('pieces_png', 'black_q.png')),
            'N': pygame.image.load(os.path.join('pieces_png', 'white_N.png')),
            'n': pygame.image.load(os.path.join('pieces_png', 'black_n.png'))
        }

    def __draw_chessboard(self):
        for i in range(8):
            for j in range(8):
                rect = (i * self.__square_size, j * self.__square_size, self.__square_size, self.__square_size)
                color = (200, 150, 100) if not (i + j) % 2 == 0 else (255, 255, 255)
                pygame.draw.rect(self.__screen, color, rect)

    def __draw_pieces(self):
        for square in chess.SQUARES:
            piece = self.__board.piece_at(chess.square_mirror(square))
            if piece:
                x, y = self.__square_to_pixel(square)
                self.__screen.blit(self.__pieces[piece.symbol()], (x, y))

    def __update(self):
        self.__screen.fill((255, 255, 255))
        self.__draw_chessboard()
        self.__draw_pieces()
        pygame.display.flip()

    def __create_popup(self):

        # Create the popup surface
        popup_size = (self.__size / 1.5, self.__size / 1.5)
        popup = pygame.Surface(popup_size)
        popup_rect = popup.get_rect(center=(self.__size / 2, self.__size / 2))

        # Draw the background and border of the popup
        pygame.draw.rect(popup, (255, 255, 255), (0, 0, popup_size[0], popup_size[1]))
        pygame.draw.rect(popup, (0, 0, 0), (0, 0, popup_size[0], popup_size[1]), 2)

        # Create the buttons for the popup
        font = pygame.font.Font(None, 30)
        button_texts = ["Donna", "Torre", "Alfiere", "Cavallo"]
        pieces = ['q', 'r', 'b', 'n']
        buttons = []
        for i, text in enumerate(button_texts):
            button = pygame.Surface((130, 30))
            pygame.draw.rect(button, (0, 0, 0), (0, 0, 130, 30))
            button_text = font.render(text, True, (255, 255, 255))
            button.blit(button_text, (30, 6))
            buttons.append(button)

        # Position the buttons on the popup
        button_rects = []
        for i, button in enumerate(buttons):
            button_rect = button.get_rect(center=(popup_size[0] / 2, 60 + i * 50))
            popup.blit(button, button_rect)
            button_rects.append(button_rect)

        # Wait for the user to make a selection
        self.__screen.blit(popup, popup_rect)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if the user clicked on one of the buttons
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_pos = (mouse_pos[0] - 67, mouse_pos[1] - 67)
                    for i, button_rect in enumerate(button_rects):
                        if button_rect.collidepoint(mouse_pos):
                            return pieces[i]


    def __select_or_move(self, square):
        piece = self.__board.piece_at(chess.parse_square(square))
        promotion = ''
        if piece and (not self.__selected_square or (self.__selected_square and piece.color == self.__board.piece_at(chess.parse_square(self.__selected_square)).color)):
            self.__update()

            self.__selected_square = square
            legal_moves = list(self.__board.legal_moves)
            legal_moves = [move for move in legal_moves if move.from_square == chess.parse_square(square)]

            destination_squares = []

            for move in legal_moves:
                destination_square = self.__square_to_pixel(move.to_square)
                destination_squares.append(destination_square)

            for i, (x, y) in enumerate(destination_squares):
                destination_squares[i] = (x + 25, y + 25)

            for (x, y) in destination_squares:
                pygame.draw.circle(self.__screen, (255, 0, 0), (x-2, self.__size - y + 3), 20, 3)

            pygame.display.update()

        elif self.__selected_square:
            if (self.__board.piece_at(chess.parse_square(self.__selected_square)).symbol() == 'P' or self.__board.piece_at(chess.parse_square(self.__selected_square)).symbol() == 'p') and ('1' in square or '8' in square):
                promotion = self.__create_popup()

            mv = chess.Move.from_uci(self.__selected_square + square + promotion)

            if mv in self.__board.legal_moves:
                self.__board.push(mv)

            '''
            if self.__board.is_check():
                king_square = chess.square(self.__board.king(self.__board.turn))
                print(king_square)
            '''


            self.__selected_square = None
            self.__update()

    def run(self):
        self.__update()

        while self.__running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for square in self.__squares:
                        # piece = board.piece_at(chess.square_mirror(chess.parse_square(square)))
                        if self.__squares[square].collidepoint(event.pos):
                            self.__select_or_move(self.__invert_position(square))
                            break

if __name__ == '__main__':
    ca = ChessAI()
    ca.run()

import pygame
import chess
import chess.engine
import os


class ChessAI:
    def __init__(self) -> None:
        pygame.init()
        self.__size = 400
        self.__squares = {}
        self.__pieces = {}
        self.__board = chess.Board()
        print(dir(self.__board))
        print(self.__board._board_state())
        print(self.__board.status())
        self.__square_size = self.__size // 8
        self.__screen = pygame.display.set_mode((self.__size, self.__size))

        self.__init_squares()
        self.__init_pieces()

        self.__running = True
        self.__selected_square = None

        self.__engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")

        self.__speed = 0.0001
        self.__depth = 1

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

    def __highlight_selected(self):
        coords = self.__square_to_pixel(chess.parse_square(self.__selected_square))
        highlight_surface = pygame.Surface((self.__square_size, self.__square_size), pygame.SRCALPHA)
        highlight_surface.fill((250, 237, 39))
        highlight_surface.set_alpha(80)
        self.__screen.blit(highlight_surface, (coords[0] - 2, self.__size - coords[1] - 48))

    def __highlight_check(self):
        king_square = self.__square_to_pixel(chess.square_mirror(self.__board.king(self.__board.turn)))
        check_surface = pygame.Surface((self.__square_size, self.__square_size), pygame.SRCALPHA)
        check_surface.fill((255, 0, 0))
        check_surface.set_alpha(80)
        self.__screen.blit(check_surface, (king_square[0] - 2, king_square[1] - 2))

    def __ai_turn(self):
        value, mov_ai = self.__minimax(self.__board, self.__depth, float('-inf'), float('inf'), False)
        print('Fatto')
        self.__board.push(mov_ai)
        self.__update()

        if self.__board.is_check():
            self.__highlight_check()
            pygame.display.update()

    def __select_or_move(self, square):
        piece = self.__board.piece_at(chess.parse_square(square))
        promotion = ''
        if piece and piece.color:
            self.__update()

            if self.__board.is_check():
                self.__highlight_check()

            self.__selected_square = square
            legal_moves = list(self.__board.legal_moves)
            legal_moves = [move for move in legal_moves if move.from_square == chess.parse_square(square)]

            destination_squares = []

            self.__highlight_selected()

            for move in legal_moves:
                is_capturable = False
                tmp_moves = list(self.__board.legal_moves)
                lgl_moves = str(self.__board.legal_moves)
                lgl_moves = lgl_moves.split('(')[1]
                lgl_moves = lgl_moves.split(')')[0]
                lgl_moves = lgl_moves.split(',')
                c = 0

                for mov in tmp_moves:
                    if move == mov:
                        break
                    c += 1

                if 'x' in lgl_moves[c]:
                    is_capturable = True

                destination_square = self.__square_to_pixel(move.to_square)
                destination_squares.append([destination_square, is_capturable])

            for i, ((x, y), z) in enumerate(destination_squares):
                destination_squares[i][0] = (x + 25, y + 25)

            for ((x, y), z) in destination_squares:
                lgl_moves_surface = pygame.Surface((self.__square_size, self.__square_size), pygame.SRCALPHA)
                lgl_moves_surface.set_alpha(100)
                if z:
                    pygame.draw.circle(lgl_moves_surface, (128, 128, 128), (25, 25), 25, 3)
                    self.__screen.blit(lgl_moves_surface, (x - 27, self.__size - y - 23))
                else:
                    pygame.draw.circle(lgl_moves_surface, (128, 128, 128), (25, 25), 8)
                    self.__screen.blit(lgl_moves_surface, (x - 27, self.__size - y - 23))

            pygame.display.update()
        elif self.__selected_square:
            if (self.__board.piece_at(
                    chess.parse_square(self.__selected_square)).symbol() == 'P' or self.__board.piece_at(
                    chess.parse_square(self.__selected_square)).symbol() == 'p') and ('1' in square or '8' in square):
                promotion = self.__create_popup()

            mv = chess.Move.from_uci(self.__selected_square + square + promotion)

            done_move = False

            if mv in self.__board.legal_moves:
                self.__board.push(mv)
                done_move = True

            self.__selected_square = None
            self.__update()

            if self.__board.is_check():
                self.__highlight_check()
                pygame.display.update()

            if done_move:

                self.__ai_turn()



    '''
    def __select_or_move(self, square):
        piece = self.__board.piece_at(chess.parse_square(square))
        promotion = ''
        if piece and (not self.__selected_square or (self.__selected_square and piece.color == self.__board.piece_at(chess.parse_square(self.__selected_square)).color)):

            self.__update()

            if self.__board.is_check():
                self.__highlight_check()

            self.__selected_square = square
            legal_moves = list(self.__board.legal_moves)
            legal_moves = [move for move in legal_moves if move.from_square == chess.parse_square(square)]

            destination_squares = []

            self.__highlight_selected()

            for move in legal_moves:
                is_capturable = False
                tmp_moves = list(self.__board.legal_moves)
                lgl_moves = str(self.__board.legal_moves)
                lgl_moves = lgl_moves.split('(')[1]
                lgl_moves = lgl_moves.split(')')[0]
                lgl_moves = lgl_moves.split(',')
                c = 0

                for mov in tmp_moves:
                    if move == mov:
                        break
                    c += 1

                if 'x' in lgl_moves[c]:
                    is_capturable = True

                destination_square = self.__square_to_pixel(move.to_square)
                destination_squares.append([destination_square, is_capturable])

            for i, ((x, y), z) in enumerate(destination_squares):
                destination_squares[i][0] = (x + 25, y + 25)

            for ((x, y), z) in destination_squares:
                lgl_moves_surface = pygame.Surface((self.__square_size, self.__square_size), pygame.SRCALPHA)
                lgl_moves_surface.set_alpha(100)
                if z:
                    pygame.draw.circle(lgl_moves_surface, (128, 128, 128), (25, 25), 25, 3)
                    self.__screen.blit(lgl_moves_surface, (x - 27, self.__size - y - 23))
                else:
                    pygame.draw.circle(lgl_moves_surface, (128, 128, 128), (25, 25), 8)
                    self.__screen.blit(lgl_moves_surface, (x - 27, self.__size - y - 23))

            pygame.display.update()

        elif self.__selected_square:
            if (self.__board.piece_at(chess.parse_square(self.__selected_square)).symbol() == 'P' or self.__board.piece_at(chess.parse_square(self.__selected_square)).symbol() == 'p') and ('1' in square or '8' in square):
                promotion = self.__create_popup()

            mv = chess.Move.from_uci(self.__selected_square + square + promotion)

            if mv in self.__board.legal_moves:
                self.__board.push(mv)

            self.__selected_square = None
            self.__update()

            if self.__board.is_check():
                self.__highlight_check()
                pygame.display.update()
    '''

    def __minimax(self, board, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or board.is_game_over():
            info = self.__engine.analyse(self.__board, chess.engine.Limit(depth=10))
            score = info["score"].relative.score()
            if not score:
                return -float('inf'), None
            return score, None

        bestMove = None
        if maximizingPlayer:
            bestValue = float('-inf')
            for move in board.legal_moves:
                board.push(move)
                value, _ = self.__minimax(board, depth - 1, alpha, beta, False)
                board.pop()

                if value > bestValue:
                    bestValue = value
                    bestMove = move

                alpha = max(alpha, bestValue)
                if beta <= alpha:
                    break
            return bestValue, bestMove
        else:
            bestValue = float('inf')
            for move in board.legal_moves:
                board.push(move)
                value, _ = self.__minimax(board, depth - 1, alpha, beta, True)
                board.pop()

                if value < bestValue:
                    bestValue = value
                    bestMove = move

                beta = min(beta, bestValue)
                if beta <= alpha:
                    break
            return bestValue, bestMove

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

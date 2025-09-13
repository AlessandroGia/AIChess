import pygame
import chess
import chess.engine
import os
import time


class ChessAI:
    def __init__(self) -> None:
        pygame.init()
        self.__size = 600
        self.__error_coords = 5
        self.__squares = {}
        self.__pieces = {}
        self.__board = chess.Board()
        self.__square_size = self.__size // 8
        self.__screen = pygame.display.set_mode((self.__size, self.__size))

        self.__init_squares()
        self.__init_pieces()

        self.__running = True
        self.__selected_square = None

        self.__engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")

        self.__speed = 0.1
        self.__depth = 3

        self.__pieces_values = {
            'p': 1,
            'P': -1,
            'n': 3,
            'N': -3,
            'b': 3,
            'B': -3,
            'r': 5,
            'R': -5,
            'q': 9,
            'Q': -9,
            'k': 999,
            'K': -999
        }

    @staticmethod
    def __invert_position(position: str) -> str:
        return chess.square_name(chess.square_mirror(chess.parse_square(position)))

    def __square_to_pixel(self, square: int) -> (int, int):
        col = square // 8
        row = square % 8
        return row * self.__square_size + self.__error_coords, col * self.__square_size + self.__error_coords

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
        popup_size = (self.__size / 3.5, self.__size / 2.5)
        popup = pygame.Surface(popup_size)
        popup_rect = popup.get_rect(center=(self.__size / 2, self.__size / 2))

        # Draw the background and border of the popup
        pygame.draw.rect(popup, (255, 255, 255), (0, 0, popup_size[0], popup_size[1]))
        pygame.draw.rect(popup, (0, 0, 0), (0, 0, popup_size[0], popup_size[1]), 2)

        # Create the buttons for the popup
        font = pygame.font.Font(None, 30)
        button_texts = ["DONNA", "TORRE", "ALFIERE", "CAVALLO"]
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
            button_rect = button.get_rect(center=(popup_size[0] / 2, 60 + i * 42))
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
                    mouse_pos = (mouse_pos[0] - ((self.__size / 2) - ((self.__size / 3.5) / 2)), mouse_pos[1] - ((self.__size /2) - ((self.__size / 2.5) / 2)))
                    for i, button_rect in enumerate(button_rects):
                        if button_rect.collidepoint(mouse_pos):
                            return pieces[i]

    def __highlight_selected(self):
        coords = self.__square_to_pixel(chess.parse_square(self.__selected_square))
        highlight_surface = pygame.Surface((self.__square_size, self.__square_size), pygame.SRCALPHA)
        highlight_surface.fill((250, 237, 39))
        highlight_surface.set_alpha(80)
        self.__screen.blit(highlight_surface, (coords[0] - self.__error_coords, self.__size - coords[1] + self.__error_coords - self.__square_size))

    def __highlight_check(self):
        king_square = self.__square_to_pixel(chess.square_mirror(self.__board.king(self.__board.turn)))
        check_surface = pygame.Surface((self.__square_size, self.__square_size), pygame.SRCALPHA)
        check_surface.fill((255, 0, 0))
        check_surface.set_alpha(80)
        self.__screen.blit(check_surface, (king_square[0] - self.__error_coords, king_square[1] - self.__error_coords))

    def __ai_turn(self):
        value, mov_ai = self.__minimax(self.__board, self.__depth, -float('inf'), float('inf'), True)
        self.__board.push(mov_ai)
        #result = self.__engine.play(self.__board, chess.engine.Limit(depth=5))
        #self.__board.push(result.move)
        self.__update()

        if self.__board.is_check():
            print("scacco")
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
                    pygame.draw.circle(lgl_moves_surface, (128, 128, 128), (self.__square_size/2 + 1, self.__square_size/2 - 1), self.__square_size / 2.2, 5)
                    self.__screen.blit(lgl_moves_surface, ((x + self.__error_coords - self.__square_size / 2) + 3, self.__size - y - self.__error_coords - self.__square_size / 2))
                else:
                    pygame.draw.circle(lgl_moves_surface, (128, 128, 128), (self.__square_size/2 , self.__square_size/2), self.__square_size / 5)
                    self.__screen.blit(lgl_moves_surface, ((x + self.__error_coords - self.__square_size / 2) + 3, self.__size - y - self.__error_coords - self.__square_size / 2))

            pygame.display.update()
        elif self.__selected_square:

            sq = self.__selected_square[0]
            s = square[0]

            diff = abs(ord(sq) - ord(s))

            if (
                    self.__board.piece_at(chess.parse_square(self.__selected_square)).symbol() == 'P' and
                    '8' in square and '7' in self.__selected_square and self.__board.turn and
                    (diff == 0 and not self.__board.piece_at(chess.parse_square(square)) or
                     (diff == 1 and self.__board.piece_at(chess.parse_square(square)))
                    )
            ):
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

            if self.__board.is_checkmate() or self.__board.is_stalemate() or self.__board.is_repetition():
                time.sleep(2)
                self.__popup_game_over()

            if done_move:
                self.__ai_turn()

            if self.__board.is_checkmate() or self.__board.is_stalemate() or self.__board.is_repetition():
                time.sleep(2)
                self.__popup_game_over()

    def __popup_game_over(self):
        popup_size = (self.__size /1.8, self.__size / 3)
        popup = pygame.Surface(popup_size)
        popup_rect = popup.get_rect(center=(self.__size / 2, self.__size / 2))

        # Draw the background and border of the popup
        pygame.draw.rect(popup, (255, 255, 255), (0, 0, popup_size[0], popup_size[1]))
        pygame.draw.rect(popup, (0, 0, 0), (0, 0, popup_size[0], popup_size[1]), 2)

        ##

        result = self.__board.result()

        font = pygame.font.Font(None, 50)

        lbl = pygame.Surface((popup_size[0] / 1.2, popup_size[1] / 2))
        pygame.draw.rect(lbl, (255, 255, 255), (0, 0, popup_size[0], popup_size[1]))
        lbl_text = font.render("GAME OVER!", True, (0, 0, 0))
        if result == '*':
            result = '1/2-1/2'
        lbl_text_2 = font.render(result, True, (0, 0, 0))
        lbl.blit(lbl_text, (30, 6))
        lbl.blit(lbl_text_2, (popup_size[0] / 2 - 50, 55))

        lbl_rect = lbl.get_rect(center=(popup_size[0] / 2 - 2, 100))
        popup.blit(lbl, lbl_rect)

        self.__screen.blit(popup, popup_rect)
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__running = False
                    break

    def __minimax(self, board, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or board.is_game_over():

            info = self.__engine.analyse(self.__board, chess.engine.Limit(depth=0))
            score = info["score"].black()

            if not score.score():
                if score.mate() == 31:
                    return 8899, None
                elif score.mate() == 30:
                    return 8999, None
                elif score.mate() == 29:
                    return 9199, None
                elif score.mate() == 28:
                    return 9299, None
                elif score.mate() == 27:
                    return 9399, None
                elif score.mate() == 26:
                    return 9499, None
                elif score.mate() == 25:
                    return 9599, None
                elif score.mate() == 24:
                    return 9699, None
                elif score.mate() == 23:
                    return 9799, None
                elif score.mate() == 22:
                    return 9899, None
                elif score.mate() == 21:
                    return 9999, None
                elif score.mate() == 20:
                    return 10999, None
                elif score.mate() == 19:
                    return 11999, None
                elif score.mate() == 18:
                    return 12999, None
                elif score.mate() == 17:
                    return 13999, None
                elif score.mate() == 16:
                    return 14999, None
                elif score.mate() == 15:
                    return 15999, None
                elif score.mate() == 14:
                    return 16999, None
                elif score.mate() == 13:
                    return 17999, None
                elif score.mate() == 12:
                    return 18999, None
                elif score.mate() == 11:
                    return 19999, None
                elif score.mate() == 10:
                    return 20999, None
                elif score.mate() == 9:
                    return 21999, None
                elif score.mate() == 8:
                    return 22999, None
                elif score.mate() == 7:
                    return 23999, None
                elif score.mate() == 6:
                    return 24999, None
                elif score.mate() == 5:
                    return 25999, None
                elif score.mate() == 4:
                    return 26999, None
                elif score.mate() == 3:
                    return 27999, None
                elif score.mate() == 2:
                    return 28999, None
                elif score.mate() == 1:
                    return 29999, None
                elif score.mate() == 0:
                    return 31999, None
                else:
                    return -9999, None
        # score = self.__evaluate()
            return score.score(), None

        bestMove = None
        if maximizingPlayer:
            bestValue = -float('inf')
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

import chess.svg
import os
pieces = ['p', 'P', 'r', 'R', 'n', 'N', 'k', 'K', 'q', 'Q', 'b', 'B']
dir = 'pieces_svg'

if not os.path.exists(dir):
    os.mkdir(dir)

for piece in pieces:
    pie = chess.svg.piece(chess.Piece.from_symbol(piece))
    color = 'black'
    if piece.isupper():
        color = 'white'
    with open(os.path.join(dir, f'{color}_{piece}.svg'), 'w') as f:
        f.write(pie)


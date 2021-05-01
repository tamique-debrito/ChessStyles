import os
from chess import pgn
from CONSTANTS import GAME_DATA_PATH

def print_board_seq_from_pgn(path):
    with open(path, encoding='utf-8') as f:
        game = pgn.read_game(f)

    board = game.board()

    for m in game.mainline_moves():
        board.push(m)
        print(board)
        print('-'*15)

if __name__ == "__main__":
    dirs = os.scandir(GAME_DATA_PATH)
    pgn_path = next(dirs).path

    print_board_seq_from_pgn(pgn_path)
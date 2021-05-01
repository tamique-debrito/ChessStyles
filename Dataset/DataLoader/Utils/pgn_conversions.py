import os
from chess import pgn
from Dataset.DownloadAndSaveData.Utils.parse_userinfo_from_pgn import extract_username
from Dataset.DataLoader.Utils.board_string_to_tensor import board_string_to_tensor

from CONSTANTS import GAME_DATA_PATH


def pgn_to_board_string_list(pgn_path, trim_equal=True):
    # Loads pgn file and converts to board string split by whether it is players move or not
    username = extract_username(pgn_path)

    with open(pgn_path, 'r', encoding='utf-8') as f:
        game = pgn.read_game(f)

    board = game.board()
    before_move = []
    after_move = []

    user_turn = game.headers["White"].lower() == username
    first_turn = True

    # print(f'User has first turn: {user_turn}')

    for m in game.mainline_moves():
        board_str = str(board)
        if user_turn:
            before_move.append(board_str)
        elif not first_turn:
            after_move.append(board_str)

        user_turn = not user_turn


        board.push(m)
        first_turn = False

    if trim_equal:
        before_move = before_move[:len(after_move)]

    return before_move, after_move


def board_string_list_to_tensor_list(board_string_list, multi_channel=True):
    # converts a list of board strings to a list of corresponding tensors
    return [board_string_to_tensor(board_string, multi_channel=multi_channel)
            for board_string in board_string_list]


def pgn_to_tensor_list(pgn_path, multi_channel=True, trim_equal=True):
    before_moves, after_moves = pgn_to_board_string_list(pgn_path, trim_equal=trim_equal)
    before_moves_tensor = board_string_list_to_tensor_list(before_moves, multi_channel)
    after_moves_tensor = board_string_list_to_tensor_list(after_moves, multi_channel)
    return before_moves_tensor, after_moves_tensor


def test_pgn_to_board_string_lists():
    dirs = os.scandir(GAME_DATA_PATH)
    pgn_path = next(dirs).path
    before_move, after_move = pgn_to_board_string_list(pgn_path)
    with open(pgn_path, 'r', encoding='utf-8') as f:
        ref_game = f.read()
    print(pgn_path)
    print(ref_game[:150])
    for s in before_move[:3]:
        print(s)
        print('-' * 15)
    for s in after_move[:3]:
        print(s)
        print('-' * 15)


if __name__ == "__main__":
    test_pgn_to_board_string_lists()

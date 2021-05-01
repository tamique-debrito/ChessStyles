import os
from Dataset.DownloadAndSaveData.Utils.parse_userinfo_from_pgn import extract_username


# parse a directory containing a list of pgn files with names in format <username>_##
# and converts them to a dictionary <username> => paths containing <username>

def parse_data_directory(path):
    users_to_pgn_paths = {}
    dirs = os.scandir(path)
    for d in dirs:
        p = d.path
        username = extract_username(p)
        if username not in users_to_pgn_paths:
            users_to_pgn_paths[username] = []
        users_to_pgn_paths[username].append(p)

    return users_to_pgn_paths


def test_parse():
    test_path = 'C:\\Users\\tamiq\\PycharmProjects\\ChessStyles\\test_game_data'
    print(parse_data_directory(test_path))


if __name__ == "__main__":
    test_parse()

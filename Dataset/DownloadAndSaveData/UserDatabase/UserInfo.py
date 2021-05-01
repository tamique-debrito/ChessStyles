import os
from Dataset.DownloadAndSaveData.Utils.parse_userinfo_from_pgn import parse_userinfo_from_pgn

class UserInfo:
    def __init__(self, username, base_dir, filename_list):
        self.username = username

        game_infos = {}

        for i, filename in enumerate(filename_list):
            print(f'\rParsing user infos from PGN files {i+1}/{len(filename_list)}, filename: {filename}', end='')
            _, elo, link = parse_userinfo_from_pgn(os.path.join(base_dir, filename))
            game_infos[filename] = {'link': link, 'elo': elo}
        print("\rDone parsing user infos from PGN files")

        self.game_infos = game_infos

    def num_games(self):
        return len(self.game_infos)

    def average_elo(self):
        return sum(map(lambda x: x['elo'], list(self.game_infos.values()))) / self.num_games()


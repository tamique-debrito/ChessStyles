"""
Downloads and saves the given number of pgn_path files for a given username. Returns a list of filenames
If user does not have enough games to do this returns None without saving any files
"""

from Dataset.DownloadAndSaveData.Utils.split_text_to_files import save_text_list, split_keep_prefix
from Dataset.DownloadAndSaveData.UserDatabase.UserInfo import UserInfo

from CONSTANTS import GAME_DATA_PATH

from time import sleep

GAME_START_MARKER_STRING = '[Event'
MIN_NUM_MOVES = 10
TIMEOUT = 1.0

import requests

from datetime import datetime as dt

def has_min_moves(pgn_data_string):
    return (str(MIN_NUM_MOVES) + '... ') in pgn_data_string


def fill_user(username, game_quota, max_months_to_search=6, return_num_discarded=False):
    """

    :param username: name of user
    :param game_quota: number of games to fill
    :param max_months_to_search: maximum number of months to search backwards from current date
    :return: A UserInfo object or a tuple (UserInfo object, num_games_discarded)
    """
    current_date = dt.now()
    current_year = current_date.year
    current_month = current_date.month
    num_months_searched = 0
    num_games_found = 0
    num_games_discarded = 0

    pgn_text_strings = []

    while num_months_searched < max_months_to_search and num_games_found < game_quota:
        url = f'https://api.chess.com/pub/player/{username}/games/{current_year}/{current_month}/pgn_path'

        try:
            res = requests.get(url, timeout=TIMEOUT)
            res.raise_for_status()
        except:
            print(f"error dowloading pgn_path from url={url}")
            if return_num_discarded:
                return None, num_games_discarded
            else:
                return None
        unfiltered_pgn_data_strings = split_keep_prefix(res.text, GAME_START_MARKER_STRING, clear_empty=True)
        new_pgn_data_strings = [data_string for data_string in unfiltered_pgn_data_strings
                                if has_min_moves(data_string)]
        num_games_discarded += len(unfiltered_pgn_data_strings) - len(new_pgn_data_strings)

        num_games_found += len(new_pgn_data_strings)

        pgn_text_strings.extend(new_pgn_data_strings)

        current_month -= 1
        if current_month == 0:
            current_month = 12
            current_year -= 1
        num_months_searched += 1

    if num_games_found < game_quota:
        print(f'User {username} did not have enough games to fill quota '
              f'(got {num_games_found} out of {game_quota} searching back {max_months_to_search} months)')
        if return_num_discarded:
            return None, num_games_discarded
        else:
            return None

    else:
        saved_filenames = save_text_list(pgn_text_strings, username + '_', GAME_DATA_PATH, limit=game_quota)
        if return_num_discarded:
            return UserInfo(username, GAME_DATA_PATH, saved_filenames), num_games_discarded
        else:
            return UserInfo(username, GAME_DATA_PATH, saved_filenames)

def fill_users_from_histogram(histogram, games_per_player, start_at):
    users = {}
    username_list = histogram.get_username_list()[start_at:]
    failed_fills = []
    for i, username in enumerate(username_list):
        print(f'Attempting to fill user {i+1}/{len(username_list)}:')
        user_info, num_discarded = fill_user(username, games_per_player, return_num_discarded=True)
        if user_info is None:
            failed_fills.append(username)
            print(f"Failed to fill user. Num discarded games={num_discarded}")
        else:
            users[username] = user_info
            print(f"Successfully filled user. Num discarded games={num_discarded}")
    print('Iterated through all users')
    return users, failed_fills

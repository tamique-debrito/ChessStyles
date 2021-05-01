import os
import pickle
from .ELOHistogram import ELOHistogram

from Dataset.DownloadAndSaveData.Utils.find_users import find_users
from Dataset.DownloadAndSaveData.Utils.fill_histogram import fill_histogram
from Dataset.DownloadAndSaveData.Utils.fill_user import fill_users_from_histogram
from Dataset.DownloadAndSaveData.Utils.fill_users_and_histogram_combined import fill_histogram_and_users_combined

from CONSTANTS import USER_DATA_PATH

NUM_ELO_BINS = 5

MIN_ELO = 1000
MAX_ELO = 2000

NUM_PLAYERS = 25
GAMES_PER_PLAYER = 40

TOTAL_NUM_GAMES = NUM_PLAYERS * GAMES_PER_PLAYER

class UserDatabase:
    def __init__(self):
        self.users = {}
        self.already_filled = None
        self.load()

    def fill_database_stage_1(self):
        print("Running stage 1")
        candidate_users = find_users(d=3, breadth_limit=15, request_spacing=10)
        with open(os.path.join(USER_DATA_PATH, 'stage_1_candidate_users'), 'wb') as stage_1:
            pickle.dump(candidate_users, stage_1, pickle.HIGHEST_PROTOCOL)
        print("Stage 1 complete")

    def fill_database_stage_2(self):
        print("Running stage 2")
        with open(os.path.join(USER_DATA_PATH, 'stage_1_candidate_users'), 'rb') as stage_1:
            candidate_users = pickle.load(stage_1)

        histogram = ELOHistogram(NUM_PLAYERS, MIN_ELO, MAX_ELO, NUM_ELO_BINS)
        success = fill_histogram(histogram, candidate_users)

        if success:
            with open(os.path.join(USER_DATA_PATH, 'stage_2_filled_histogram'), 'wb') as stage_2:
                pickle.dump(histogram, stage_2, pickle.HIGHEST_PROTOCOL)
            print("Stage 2 complete")
        else:
            print("Stage 2 failed")

    def fill_database_stage_3(self, start_at=0):
        print("Running stage 3")
        with open(os.path.join(USER_DATA_PATH, 'stage_2_filled_histogram'), 'rb') as stage_2:
            histogram = pickle.load(stage_2)

        users, failed_fills = fill_users_from_histogram(histogram, GAMES_PER_PLAYER, start_at)
        if len(failed_fills) > 0:
            print("Stage 3 failed\n"
                  f"\t failed to fill the following users: {str(failed_fills)}")
        else:
            with open(os.path.join(USER_DATA_PATH, 'stage_3_filled_users'), 'wb') as stage_3:
                pickle.dump(users, stage_3, pickle.HIGHEST_PROTOCOL)
            print("Stage 3 complete")

        self.users = users

    def fill_database_stage_2_3_combined(self):
        print("Running combined stage 2 and stage 3")
        with open(os.path.join(USER_DATA_PATH, 'stage_1_candidate_users'), 'rb') as stage_1:
            candidate_users = pickle.load(stage_1)

        histogram = ELOHistogram(NUM_PLAYERS, MIN_ELO, MAX_ELO, NUM_ELO_BINS)
        users, failed_fills = fill_histogram_and_users_combined(histogram, candidate_users, GAMES_PER_PLAYER)
        if len(users) < NUM_PLAYERS:
            print("Combined stage 2 and stage 3 failed, not enough users filled")
        else:
            with open(os.path.join(USER_DATA_PATH, 'stage_3_filled_users'), 'wb') as stage_3:
                pickle.dump(users, stage_3, pickle.HIGHEST_PROTOCOL)
            print("Combined stage 2 and stage 3 complete")

    def fill_database_complete(self, combined=True):
        if combined:
            self.fill_database_stage_1()
            self.fill_database_stage_2_3_combined()
        else:
            self.fill_database_stage_1()
            self.fill_database_stage_2()
            self.fill_database_stage_3()

    def get_num_games(self, username):
        return self.users[username].num_games()

    def get_average_elo(self, username):
        return self.users[username].average_elo()

    def get_all_average_elos(self):
        return [user.average_elo() for user in self.users.values()]

    def load(self):
        load_path = os.path.join(USER_DATA_PATH, 'stage_3_filled_users')
        if os.path.exists(load_path):
            self.already_filled = True
            with open(load_path, 'rb') as users:
                self.users = pickle.load(users)
        else:
            self.already_filled = False

if __name__ == "__main__":
    db = UserDatabase()
    db.fill_database_stage_2_3_combined()
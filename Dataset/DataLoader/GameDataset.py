from torch.utils.data import Dataset as Ds
import random
from Dataset.DataLoader.Utils.pgn_conversions import pgn_to_board_string_list, board_string_list_to_tensor_list, \
    pgn_to_tensor_list, board_string_to_tensor
from Dataset.DataLoader.Utils.parse_data_directory import parse_data_directory
from Dataset.DataLoader.Utils.get_map_string_to_id_map import get_map_string_to_id

from CONSTANTS import GAME_DATA_PATH, TEST_GAME_DATA_PATH


class GameDataset(Ds):
    def __init__(self, multi_channel=True, return_next=False, return_contrastive=False,
                 board_strings_in_memory=True, tensors_in_memory=False,
                 base_path=GAME_DATA_PATH):

        if not board_strings_in_memory:
            raise Warning("Board strings must be loaded in memory in order to use GameDataset as a regular PyTorch Dataset")
        self.user_to_pgn_paths = parse_data_directory(base_path)
        self.flattened_pgn_paths = [(username, path)
                                    for username in self.user_to_pgn_paths
                                    for path in self.user_to_pgn_paths[username]]
        self.usernames = list(self.user_to_pgn_paths.keys())
        self.games = [d[1] for d in self.flattened_pgn_paths]
        self.username_to_id = get_map_string_to_id(self.usernames, id_string=base_path)
        self.game_to_id = get_map_string_to_id(self.games, id_string=base_path)

        self.multi_channel = multi_channel
        self.return_next = return_next
        self.return_contrastive = return_contrastive

        self.board_strings = None
        self.flattened_board_strings = None
        self.board_strings_in_memory = False
        self.tensors = None
        self.flattened_tensors = None
        self.tensors_in_memory = False
        if board_strings_in_memory:
            self.load_board_strings()

        if tensors_in_memory:
            self.load_tensors()

        self.len = self.calc_len()

    def __len__(self):
        if self.len is None:
            raise Exception("Tried to get length when self.len is None. "
                            "This is certainly due to not loading at least one of board strings or tensors into memory")
        return self.len

    def __getitem__(self, idx):
        result = {}
        data = self.get_single(idx)
        result['before'] = data[0]
        result['user_id'] = self.username_to_id[data[4]]
        result['game_id'] = self.game_to_id[data[3]]
        if self.return_next:
            result['after'] = data[1]
        if self.return_contrastive:
            idx_cont = random.randrange(self.len)
            data_cont = self.get_single(idx_cont)
            result['before_cont'] = data_cont[0]
            if self.return_next:
                result['after_cont'] = data_cont[1]

        return result


    def get_single(self, idx):
        if self.tensors_in_memory:
            data = self.flattened_tensors[idx]
            return data
        elif self.board_strings_in_memory:
            data = self.flattened_board_strings[idx]
            before_move, after_move = data[0], data[1]
            before_move = board_string_to_tensor(before_move, self.multi_channel)
            after_move = board_string_to_tensor(after_move, self.multi_channel)
            return (before_move, after_move, *data[2:])
        else:
            raise Exception("Tried to get item when neither board strings nor tensors are in memory")


    def calc_len(self):
        if not self.board_strings_in_memory:
            return None
        else:
            n = 0
            for username in self.board_strings:
                paths = self.board_strings[username]
                for path in paths:
                    before_move = paths[path]['before_move']
                    n += len(before_move)
            return n

    def load_board_strings(self):
        def load_function(username, path):
            return pgn_to_board_string_list(path, trim_equal=True)
        user_to_board_strings = self.load_board_data(load_function)

        self.board_strings = user_to_board_strings
        self.flattened_board_strings = self.flatten_board_data(user_to_board_strings)

        self.board_strings_in_memory = True

    def load_tensors(self):
        if self.board_strings_in_memory:
            def load_function(username, path):
                game_data = self.board_strings[username][path]
                before_board_strings = game_data['before_move']
                after_board_strings = game_data['after_move']
                before_tensors = board_string_list_to_tensor_list(before_board_strings,
                                                                  multi_channel=self.multi_channel)
                after_tensors = board_string_list_to_tensor_list(after_board_strings,
                                                                 multi_channel=self.multi_channel)
                return before_tensors, after_tensors
        else:
            def load_function(username, path):
                return pgn_to_tensor_list(path, multi_channel=self.multi_channel, trim_equal=True)

        users_to_tensors = self.load_board_data(load_function)
        self.tensors = users_to_tensors
        self.flattened_tensors = self.flatten_board_data(users_to_tensors)

        self.tensors_in_memory = True

    def load_board_data(self, load_function):
        # given load_function, a function that maps (username, game_path) to a tuple (before_moves_data, after_moves_data)
        # applies the load function to all usernames and paths stored in self to form a dictionary in form
        #   dictionary: username => (dictionary: game_path => {before_move: before_moves_data, after_move: after_moves_data})
        data = {}
        for username in self.user_to_pgn_paths:
            data[username] = {}
            pgn_paths = self.user_to_pgn_paths[username]
            for path in pgn_paths:
                before_move, after_move = load_function(username, path)
                data[username][path] = {'before_move': before_move, 'after_move': after_move}
        return data

    @staticmethod
    def flatten_board_data(data):
        # a flattening function that applies to both board string and tensor data
        # data: a dictionary: username => (dictionary: game_path => {before_move: list_of_board_states, after_move: list_of_board_states})
        #       where list_of_board_states is a list of board states, with a board state
        #       representing the state of the board at a particular move.
        #       The 'before_move'/'after_move' keys refer to whether the list of board states
        #       contains lists that are immediately before or immediately after the given player's move
        #       (where the given player is specified by 'username')
        # returns: a flattened list (before_data, after_data, move_idx, path, username)
        return [(before, after, move_idx, path, username)
                for username in data
                for path in data[username]
                for move_idx, (before, after)
                in enumerate(zip(data[username][path]['before_move'],
                                 data[username][path]['after_move']))]



############################# TESTING:

def test_loads_correctness():
    d1 = GameDataset(base_path=TEST_GAME_DATA_PATH, board_strings_in_memory=False, tensors_in_memory=False, multi_channel=False)
    d2 = GameDataset(base_path=TEST_GAME_DATA_PATH, board_strings_in_memory=True, tensors_in_memory=False, multi_channel=False)
    d3 = GameDataset(base_path=TEST_GAME_DATA_PATH, board_strings_in_memory=False, tensors_in_memory=True, multi_channel=False)
    d4 = GameDataset(base_path=TEST_GAME_DATA_PATH, board_strings_in_memory=True, tensors_in_memory=True, multi_channel=False)

    print("Should put debugging breakpoint here and manually inspect data structures")

    return None

def time_op(op):
    import time
    t0 = time.time()
    op()
    t1 = time.time()
    return f'{(t1 - t0):.0f} s'

def test_loads_memory():
    def op1():
        d1 = GameDataset(base_path=GAME_DATA_PATH, board_strings_in_memory=True, tensors_in_memory=False, multi_channel=False)
        del d1
    t = time_op(op1)
    print(f"Passed board strings (channel not applicable) ({t})")

    def op2a():
        d2a = GameDataset(base_path=GAME_DATA_PATH, board_strings_in_memory=True, tensors_in_memory=True, multi_channel=False)
        del d2a
    t = time_op(op2a)
    print(f"Passed tensors single-channel ({t})")

    def op2b():
        d2b = GameDataset(base_path=GAME_DATA_PATH, board_strings_in_memory=True, tensors_in_memory=True, multi_channel=True)
        del d2b
    t = time_op(op2b)
    print(f"Passed tensors multi-channel ({t})")

    return None


def test_getitem():
    d1 = GameDataset(base_path=TEST_GAME_DATA_PATH, board_strings_in_memory=True, tensors_in_memory=False, multi_channel=True)
    print(f"Should put debug breakpoint here and manually inspect data")
    del d1

    d2 = GameDataset(base_path=TEST_GAME_DATA_PATH, board_strings_in_memory=True, tensors_in_memory=True, multi_channel=True)
    print(f"Should put debug breakpoint here and manually inspect data")
    del d2

    return None

if __name__ == "__main__":
    # test_loads_correctness()

    test_getitem()
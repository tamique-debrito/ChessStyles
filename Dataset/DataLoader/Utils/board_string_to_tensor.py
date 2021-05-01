import torch

PIECE_LIST = ['k', 'q', 'p', 'b', 'n', 'r', 'K', 'Q', 'P', 'B', 'N', 'R']
PIECE_TO_NUM = {p: i for i, p in enumerate(PIECE_LIST)}
PIECE_TO_NUM['.'] = None

def board_string_to_tensor(board_string, multi_channel=True):
    if multi_channel:
        return board_string_to_tensor_multi_channel(board_string)
    else:
        return board_string_to_tensor_single_channel(board_string)

def board_string_to_tensor_single_channel(board_string):
    board = board_string.split('\n')
    tensor = torch.zeros(1, 8, 8)
    for i in range(8):
        for j in range(8):
            p = board[i][2*j]
            p = PIECE_TO_NUM[p]
            if p is not None:
                tensor[0][i][j] = p + 1
    return tensor

def board_string_to_tensor_multi_channel(board_string):
    board = board_string.split('\n')
    tensor = torch.zeros(12, 8, 8)
    for i in range(8):
        for j in range(8):
            p = board[i][2*j]
            c = PIECE_TO_NUM[p]
            if c is not None:
                tensor[c][i][j] = 1
    return tensor


############### TESTING:
import random
import time

def time_single_config(board_string, multi_channel, n):
    t0 = time.time()
    for _ in range(n):
        board_string_to_tensor(board_string, multi_channel)

    t1 = time.time()

    return f'{1000 * (t1 - t0):.0f} ms'

def creation_time_test(nums=(100, 1000, 10000)):
    board_empty = random_board_string(0)
    board_sparse = random_board_string(5)
    board_medium = random_board_string(16)
    board_full = random_board_string(32)
    for n in nums:
        print(f'Timing {n} iterations:\n'
              f'\tSingle-channel:\n'
              f'\t\tEmpty board: {time_single_config(board_empty, False, n)}\n'
              f'\t\tSparse board: {time_single_config(board_sparse, False, n)}\n'
              f'\t\tMedium-fill board: {time_single_config(board_medium, False, n)}\n'
              f'\t\tFull board: {time_single_config(board_full, False, n)}\n'
              f'\tMulti-channel:\n'
              f'\t\tEmpty board: {time_single_config(board_empty, True, n)}\n'
              f'\t\tSparse board: {time_single_config(board_sparse, True, n)}\n'
              f'\t\tMedium-fill board: {time_single_config(board_medium, True, n)}\n'
              f'\t\tFull board: {time_single_config(board_full, True, n)}\n')



def make_empty_board_char_list():
    l = ['' for _ in range(8 * 8 * 2)]
    for i in range(8):
        for j in range(8):
            l[2*j + 16 * i] = '.'
            l[2*j + 16 * i + 1] = ' '
        l[15 + i * 16] = '\n'

    return l

def test_empty_board():
    l = make_empty_board_char_list()
    s = ''.join(l)
    print(s)

def random_board_string(n=1):
    l = make_empty_board_char_list()
    add_random_piece_to_board_list(l, n)
    s = ''.join(l)
    return s

def add_random_piece_to_board_list(l, n=1):
    for _ in range(n):
        p = random.choice(PIECE_LIST)
        i = random.randrange(8)
        j = random.randrange(8)
        ind = 16 * i + 2 * j
        l[ind] = p

def get_random_one_piece_board_string(p):
    l = make_empty_board_char_list()
    i = random.randrange(8)
    j = random.randrange(8)
    ind = 16 * i + 2 * j
    l[ind] = p
    s = ''.join(l)
    return s, i, j

def test_single_piece_single_channel(p):
    s, i_p, j_p = get_random_one_piece_board_string(p)
    v_p = PIECE_TO_NUM[p] + 1
    tensor_single_channel = board_string_to_tensor(s, multi_channel=False)
    nonzero = torch.nonzero(tensor_single_channel).tolist()[0]

    return nonzero == [0, i_p, j_p] and tensor_single_channel[0][i_p][j_p] == v_p


def test_single_piece_multi_channel(p):
    c_p = PIECE_TO_NUM[p]
    s, i_p, j_p = get_random_one_piece_board_string(p)
    tensor_multi_channel = board_string_to_tensor(s, multi_channel=True)
    nonzero = torch.nonzero(tensor_multi_channel).tolist()[0]
    return nonzero == [c_p, i_p, j_p]

def test_all():
    single_channel_results = [test_single_piece_single_channel(p) for p in PIECE_LIST]
    if all(single_channel_results):
        print("Single-channel passed")
    else:
        print("Single-channel failed")

    multi_channel_results = [test_single_piece_multi_channel(p) for p in PIECE_LIST]
    if all(multi_channel_results):
        print("Multi-channel passed")
    else:
        print("Multi-channel failed")

if __name__ == "__main__":
    test_all()
    creation_time_test()
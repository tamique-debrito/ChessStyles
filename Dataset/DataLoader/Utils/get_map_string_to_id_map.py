# Generates a mapping from a list of strings to ids
# Should specify an additional string that describes the source of the string list
#       (for example, if the string list is a list of filenames, the additional string should probably be the directory name)
# Checks if a mapping has already been saved for given directory and string list combination
#

import os, pickle
from CONSTANTS import USER_DATA_PATH

def make_map_string_to_id(string_list):
    map_to_id = {}
    for i, s in enumerate(string_list):
        map_to_id[s] = i

    return map_to_id

def get_map_string_to_id(string_list, id_string='', save_dir=USER_DATA_PATH):
    content_hash = hash((tuple(sorted(string_list)), id_string))
    filename = 'id_map_' + str(content_hash)
    save_path = os.path.join(save_dir, filename)
    if os.path.exists(save_path):
        with open(save_path, 'rb') as f:
            map_to_id = pickle.load(f)
    else:
        map_to_id = make_map_string_to_id(string_list)
        with open(save_path, 'wb') as f:
            pickle.dump(map_to_id, f, pickle.HIGHEST_PROTOCOL)
    return map_to_id
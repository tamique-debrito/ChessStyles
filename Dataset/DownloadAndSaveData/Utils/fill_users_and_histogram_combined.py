from Dataset.DownloadAndSaveData.Utils.fill_user import fill_user

def fill_histogram_and_users_combined(histogram, candidate_users, games_per_player):
    users_parsed = 0
    users_filled = 0
    failed_fills = []
    users = {}
    for i, candidate in enumerate(candidate_users):
        print(f'\rAttempting to parse and fill candidate {i + 1}/{len(candidate_users)}', end='')
        if histogram.can_add(candidate):
            users_parsed += 1
            username = candidate['username']
            user_info, num_discarded = fill_user(username, games_per_player, return_num_discarded=True)
            if user_info is not None:
                users[username] = user_info
                users_filled += 1
                histogram.add(candidate)
                print(f"Successfully filled user. Num discarded games={num_discarded}")
            else:
                failed_fills.append(username)
                print(f"Failed to fill user. Num discarded games={num_discarded}")
        if users_filled == histogram.num_players:
            break
    print(f'\rDone iterating over candidates.\n'
          f'\tParsed {users_parsed} candidates\n'
          f'\tTried to fill {users_filled + len(failed_fills)} candidates\n'
          f'\tSuccessfully filled {users_filled}; failed to fill {len(failed_fills)}\n'
          f'\tFailed fills: {failed_fills}')

    if not histogram.histogram_full():
        print("Filling failed")
        if histogram.num_players != users_filled:
            print("Histogram was not fillable from candidates")
        else:
            print('Histogram in inconsistent state')
        return None
    else:
        print("Combined filling successful")
        return users, failed_fills
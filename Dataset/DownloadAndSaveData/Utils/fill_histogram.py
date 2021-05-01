def fill_histogram(histogram, candidate_users):
    players_added = 0
    for i, candidate in enumerate(candidate_users):
        print(f'\rParsing candidate {i+1}/{len(candidate_users)}', end='')
        if histogram.try_add(candidate):
            players_added += 1
        if players_added == histogram.num_players:
            break
    print(f'\rParsed {len(candidate_users)} candidates')

    if not histogram.histogram_full():
        if histogram.num_players != players_added:
            print("Histogram was not fillable from candidates")
        else:
            print('Histogram in inconsistent state')
        return False
    else:
        print("Histogram successfully filled")
        return True

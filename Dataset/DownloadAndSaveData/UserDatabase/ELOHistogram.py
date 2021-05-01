class ELOHistogram:
    def __init__(self, num_players, min_elo, max_elo, num_elo_bins):
        self.num_players = num_players
        self.min_elo = min_elo
        self.max_elo = max_elo
        self.num_elo_bins = num_elo_bins
        self.bin_counts = [0 for _ in range(num_elo_bins)]
        self.added_users = [[] for _ in range(num_elo_bins)]
        self.bin_target_counts = self.make_target_counts(num_players, num_elo_bins)
        self.bin_cutoffs = self.get_bin_cutoffs(min_elo, max_elo, num_elo_bins)

    def get_username_list(self):
        return [user['username'] for user_bin in self.added_users for user in user_bin]

    def add(self, info_dict):
        success = self.try_add(info_dict)
        assert success, "Tried to add user info that cannot be added!"
        return info_dict


    def try_add(self, info_dict):
        # info_dict is a dictionary with keys 'elo' and 'username'
        if self.can_add(info_dict):
            elo = info_dict['elo']
            bin_idx = self.get_bin_index(elo)
            self.added_users[bin_idx].append(info_dict)
            self.bin_counts[bin_idx] += 1
            return True
        else:
            return False

    def can_add(self, info_dict):
        elo = info_dict['elo']
        bin_idx = self.get_bin_index(elo)
        return bin_idx is not None and not self.bin_full(bin_idx)

    def histogram_full(self):
        return all([self.bin_full(i) for i in range(self.num_elo_bins)])

    def bin_full(self, bin_index):
        return self.bin_counts[bin_index] == self.bin_target_counts[bin_index]

    def in_bin(self, elo, bin_index):
        return self.bin_cutoffs[bin_index] <= elo < self.bin_cutoffs[bin_index + 1]

    def get_bin_index(self, elo):
        for i in range(self.num_elo_bins):
            if self.in_bin(elo, i):
                return i
        return None

    @staticmethod
    def make_target_counts(num_players, num_elo_bins):
        quotient = num_players // num_elo_bins
        remainder = num_players % num_elo_bins
        target_counts = [quotient for _ in range(num_elo_bins)]
        for i in range(remainder):
            target_counts[i] += 1

        return target_counts

    @staticmethod
    def get_bin_cutoffs(min_elo, max_elo, num_elo_bins):
        delta = (max_elo - min_elo) / num_elo_bins
        cutoffs = [min_elo + i * delta for i in range(num_elo_bins + 1)]
        return cutoffs
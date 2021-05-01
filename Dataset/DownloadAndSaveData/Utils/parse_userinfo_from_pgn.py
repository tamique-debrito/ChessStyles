from chess import pgn
import regex
import ntpath

def extract_username(pgn_path):
    return regex.match('(.*)_\d+', ntpath.basename(pgn_path)).group(1)

def parse_userinfo_from_pgn(pgn_path):
    with open(pgn_path, 'r', encoding='utf-8') as f:
        header = pgn.read_headers(f)
    username = extract_username(pgn_path)
    elo = header['WhiteElo'] if header['White'] == username else header['BlackElo']
    link = header['Link']

    return username, elo, link


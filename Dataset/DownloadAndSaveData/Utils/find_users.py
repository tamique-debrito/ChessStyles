# Scrapes a list of users and their ELOs on the chess.com website

import requests
import regex
import json
from time import sleep
import random

BASE_URL = 'http://chess.com/forum'

def extract_username_from_url(url):
    ref_string = 'chess.com/member/'
    i = url.find(ref_string)
    username = url[i + len(ref_string):]
    return username

REQUEST_SPACING = 10


def spaced_request_get(url):
    global REQUEST_SPACING
    sleep(REQUEST_SPACING / 1000)
    res = requests.get(url)
    return res


def get_user_info_from_url(url):
    # returns a dictionary {name: username, elo: elo} with data filled from given url
    username = extract_username_from_url(url)
    req = f'https://api.chess.com/pub/player/{username}/stats'
    res = spaced_request_get(req)
    stats = json.loads(res.text)
    elos = []
    for key in ['chess_rapid', 'chess_blitz', 'chess_daily']:
        if key in stats:
            elos.append(stats[key]['last']['rating'])
    if len(elos) > 0:
        elo = int(sum(elos) / len(elos))
        return {'username': username, 'elo': elo}
    else:
        return None

def is_user_url(url):
    return 'chess.com/member/' in url

def get_links_from_html(html):
    return regex.findall('href="([^"]*chess\.com[^"]*)"', html)

def get_links_from_url(url):
    res = spaced_request_get(url)
    try:
        res.raise_for_status()
        return get_links_from_html(res.text)
    except:
        return None

def filter_and_split_new_links(links):
    links = [link for link in links if 'chess.com' in link]
    new_user_urls = [link for link in links if is_user_url(link)]
    new_links = [link for link in links if not is_user_url(link)]
    return new_user_urls, new_links

def get_user_urls(d, breadth_limit):
    # uses breadth-first search starting from base URL to get a list of usernames
    # returns the scraped list of links to user profiles
    level_counts = [0 for _ in range(d)]
    processed_links = set()
    total_links_processed = 0
    total_urls_requested = 0
    total_seen_before_links = 0
    total_errors = 0
    urls_to_search = [BASE_URL]
    user_urls = []
    for i in range(d + 1):
        next_level = []
        for j, url in enumerate(urls_to_search):
            print(f'\rScanning at depth: {i}, processing link {j + 1}/{len(urls_to_search)}', end='')
            if url not in processed_links:
                new_links = get_links_from_url(url)
                if new_links is not None:
                    total_urls_requested += 1
                    total_links_processed += len(new_links)

                    new_user_urls, new_links = filter_and_split_new_links(new_links)

                    user_urls.extend(new_user_urls)
                    next_level.extend(new_links)
                else:
                    total_errors += 1
            else:
               total_seen_before_links += 1
        print(f'\rFinished scan at depth: {i}, processed {len(urls_to_search)} links, '
              f'got {len(next_level)} links (keeping {"all" if breadth_limit is None else breadth_limit})')
        processed_links.union(urls_to_search)
        if breadth_limit is not None:
            urls_to_search = random.sample(next_level, breadth_limit)
        else:
            urls_to_search = next_level

    user_urls_set = set(user_urls)

    num_duplicate_user_urls = len(user_urls) - len(user_urls_set)

    user_urls = list(user_urls_set)

    print(f'Completed scrape of user urls. Results:\n'
          f'\ttotal links processed     : {total_links_processed}\n'
          f'\ttotal urls requested      : {total_urls_requested}\n'
          f'\ttotal user urls retrieved : {len(user_urls)}\n'
          f'\ttotal request errors      : {total_errors}\n'
          f'\ttotal seen-before links   : {total_seen_before_links}\n'
          f'\tduplicate users scanned   : {num_duplicate_user_urls}')

    return user_urls

def find_users(d=3, breadth_limit=None, request_spacing=10, return_failed_links=False):
    # returns a list of dictionaries of {name: username, elo: elo}
    # request spacing is waiting time between requests in milliseconds
    #   (so as to not make too many requests in short time period)

    global REQUEST_SPACING
    REQUEST_SPACING = request_spacing

    user_urls = get_user_urls(d, breadth_limit)

    user_infos = []
    for i, url in enumerate(user_urls):
        print(f'\rRetrieving user info {i}/{len(user_urls)}, link: {url}', end='')
        user_infos.append(get_user_info_from_url(url))
    non_null_user_infos = [info for info in user_infos if info is not None]
    num_successes = len(non_null_user_infos)
    num_failures = len(user_infos) - num_successes
    print(f'\rCompleted scrape of user info. Results:\n'
          f'\ttotal user urls processed   : {len(user_urls)}\n'
          f'\ttotal successful retrievals : {num_successes}\n'
          f'\ttotal failed retrievals     : {num_failures}')

    if return_failed_links:
        failed_links = [link for link, info in zip(user_urls, user_infos) if info is None]
        return non_null_user_infos, failed_links
    else:
        return non_null_user_infos


def test_extract_username_from_url():
    urls = ['https://www.chess.com/member/thinablepear', 'chess.com/member/chris_e_s3']
    expected_usernames = ['thinablepear', 'chris_e_s3']
    for url, expected_name in zip(urls, expected_usernames):
        extracted_name = extract_username_from_url(url)
        assert extracted_name == expected_name,\
            f'extract_username_from_url failed, got {extracted_name}, expected {expected_name}'
    print('extract_username_from_url passed')

def test_get_user_info_from_url():
    tolerance = 0.2

    def check_correct(retrieved, expected):
        return retrieved['username'] == expected['username'] \
               and abs(retrieved['elo'] - expected['elo']) < tolerance * expected['elo']

    expected_infos = [{'username': 'thinablepear', 'elo': 975}, {'username': 'medveddevelopments', 'elo': 767}]
    urls = ['https://www.chess.com/member/thinablepear', 'https://www.chess.com/member/medveddevelopments']
    retrieved_infos = [get_user_info_from_url(url) for url in urls]

    n_correct = 0
    n_null = 0

    for retrieved, expected in zip(retrieved_infos, expected_infos):
        if retrieved is not None:
            if check_correct(retrieved, expected):
                n_correct += 1
        else:
            n_null += 1

    assert n_correct == len(urls), \
        f'get_user_info_from_url failed {n_correct}/{len(urls)} returned correct info {n_null}/{len(urls)} returned null'

    print('get_user_info_from_url passed')


def test_find_users():
    user_infos, failed_links = find_users(1, breadth_limit=50, return_failed_links=True)
    def fmt(info):
        return "\t\t" + str(info) + "\n"
    print(f'Testing find_users:\n'
          f'\tFirst 10 users found:\n'
          f'{"".join([fmt(info) for info in user_infos[:10]])}'
          f'\tFirst 10 failed links:\n'
          f'{"".join([fmt(link) for link in failed_links[:10]])}')

if __name__ == "__main__":
    test_extract_username_from_url()
    test_get_user_info_from_url()
    test_find_users()
import requests
from src.ingestion.config import RIOT_API_KEY
import time
from collections import deque

HEADERS = {"X-Riot-Token": RIOT_API_KEY}

def get_puuid(game_name: str, tag_line: str, region: str = "europe") -> str:
    throttle()
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["puuid"]

def get_match_ids(puuid: str, region: str = "europe", count: int = 5) -> list[str]:
    throttle()
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    resp = requests.get(url, headers=HEADERS, params={"count": count})
    resp.raise_for_status()
    return resp.json()

def get_match(match_id: str, region: str = "europe") -> dict:
    throttle()
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_match_timeline(match_id: str, region: str = "europe") -> dict:
    throttle()
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

# 100 requests per 2 minutes (120 seconds) is the binding limit
REQUEST_TIMES = deque()
MAX_REQUESTS = 100
WINDOW_SECONDS = 120

def throttle():
    now = time.time()
    while REQUEST_TIMES and now - REQUEST_TIMES[0] > WINDOW_SECONDS:
        REQUEST_TIMES.popleft()

    if len(REQUEST_TIMES) >= MAX_REQUESTS:
        sleep_time = WINDOW_SECONDS - (now - REQUEST_TIMES[0])
        print(f"Rate limit approaching, sleeping {sleep_time:.1f}s")
        time.sleep(sleep_time)

    REQUEST_TIMES.append(time.time())
import requests
from src.ingestion.config import RIOT_API_KEY

HEADERS = {"X-Riot-Token": RIOT_API_KEY}

def get_puuid(game_name: str, tag_line: str, region: str = "europe") -> str:
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["puuid"]

def get_match_ids(puuid: str, region: str = "europe", count: int = 5) -> list[str]:
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    resp = requests.get(url, headers=HEADERS, params={"count": count})
    resp.raise_for_status()
    return resp.json()

def get_match(match_id: str, region: str = "europe") -> dict:
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def get_match_timeline(match_id: str, region: str = "europe") -> dict:
    url = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()
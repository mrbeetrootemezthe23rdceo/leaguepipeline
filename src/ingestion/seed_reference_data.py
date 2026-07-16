import requests
from src.ingestion.db import get_connection

def get_latest_version():
    versions = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()
    return versions[0]

def fetch_champions(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    data = requests.get(url).json()
    # returns list of (champion_id: int, name: str)
    return [(int(info["key"]), info["name"]) for info in data["data"].values()]

def fetch_items(version):
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/item.json"
    data = requests.get(url).json()
    # returns list of (item_id: int, name: str)
    return [(int(item_id), info["name"]) for item_id, info in data["data"].items()]

def seed_champions(conn, champions):
    cur = conn.cursor()
    for champion_id, name in champions:
        cur.execute(
            """
            INSERT INTO champions (champion_id, name)
            VALUES (%s, %s)
            ON CONFLICT (champion_id) DO UPDATE SET name = EXCLUDED.name
            """,
            (champion_id, name)
        )
    conn.commit()
    cur.close()

def seed_items(conn, items):
    cur = conn.cursor()
    for item_id, name in items:
        cur.execute(
            """
            INSERT INTO items (item_id, name)
            VALUES (%s, %s)
            ON CONFLICT (item_id) DO UPDATE SET name = EXCLUDED.name
            """,
            (item_id, name)
        )
    conn.commit()
    cur.close()

if __name__ == "__main__":
    version = get_latest_version()
    print("Using Data Dragon version:", version)

    champions = fetch_champions(version)
    items = fetch_items(version)
    print(f"Fetched {len(champions)} champions, {len(items)} items")

    conn = get_connection()
    seed_champions(conn, champions)
    seed_items(conn, items)
    conn.close()

    print("Done seeding champions and items")
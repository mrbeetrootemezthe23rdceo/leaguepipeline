from src.ingestion.riot_client import get_match, get_match_timeline, get_puuid, get_match_ids
from collections import deque
from src.ingestion.transform import (
    extract_match_row,
    extract_participant_rows,
    build_participant_id_map,
    extract_frame_rows,
    extract_event_rows,
)
from src.ingestion.db import (
    get_connection,
    insert_match,
    insert_participants,
    insert_frames,
    insert_events,
)

def match_already_ingested(conn, match_id: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM matches WHERE match_id = %s", (match_id,))
    exists = cur.fetchone() is not None
    cur.close()
    return exists

def ingest_match(conn, match_id: str, region: str = "europe"):
    if match_already_ingested(conn, match_id):
        print(f"Skipping {match_id} — already ingested")
        return None

    print(f"Ingesting {match_id}...")
    match = get_match(match_id, region=region)
    timeline = get_match_timeline(match_id, region=region)

    match_row = extract_match_row(match_id, match)
    insert_match(conn, match_row)

    participant_rows = extract_participant_rows(match_id, match)
    insert_participants(conn, participant_rows)

    id_map = build_participant_id_map(match)
    frame_rows = extract_frame_rows(match_id, timeline, id_map)
    insert_frames(conn, frame_rows)

    event_rows = extract_event_rows(match_id, timeline, id_map)
    insert_events(conn, event_rows)

    print(f"Done: {match_id} — {len(participant_rows)} participants, {len(frame_rows)} frames, {len(event_rows)} events")
    return match

def ingest_matches(match_ids: list[str], region: str = "europe"):
    conn = get_connection()
    for match_id in match_ids:
        ingest_match(conn, match_id, region=region)
    conn.close()



def crawl(seed_puuids: list[str], region: str = "europe", max_matches: int = 500, matches_per_player: int = 20):
    conn = get_connection()

    seen_puuids = set(seed_puuids)
    queue = deque(seed_puuids)
    total_matches_ingested = 0

    while queue and total_matches_ingested < max_matches:
        current_puuid = queue.popleft()
        print(f"\n--- Processing player {current_puuid[:8]}... ({len(queue)} left in queue, {total_matches_ingested} matches so far) ---")

        try:
            match_ids = get_match_ids(current_puuid, region=region, count=matches_per_player)
        except Exception as e:
            print(f"Failed to get match IDs for {current_puuid[:8]}: {e}")
            continue

        for match_id in match_ids:
            if total_matches_ingested >= max_matches:
                break

            if match_already_ingested(conn, match_id):
                continue

            try:
                match_json = ingest_match(conn, match_id, region=region)
                total_matches_ingested += 1
            except Exception as e:
                print(f"Failed to ingest {match_id}: {e}")
                continue

            new_puuids = [p["puuid"] for p in match_json["info"]["participants"]]
            for puuid in new_puuids:
                if puuid not in seen_puuids:
                    seen_puuids.add(puuid)
                    queue.append(puuid)

                    

    conn.close()
    print(f"\nCrawl finished. Total matches ingested: {total_matches_ingested}, unique players discovered: {len(seen_puuids)}")

if __name__ == "__main__":
    my_puuid = get_puuid("brandtop", "1234", region="europe")
    crawl(seed_puuids=[my_puuid], max_matches=50, matches_per_player=100)
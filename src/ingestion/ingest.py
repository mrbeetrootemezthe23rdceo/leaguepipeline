from src.ingestion.riot_client import get_match, get_match_timeline
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
        return

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

def ingest_matches(match_ids: list[str], region: str = "europe"):
    conn = get_connection()
    for match_id in match_ids:
        ingest_match(conn, match_id, region=region)
    conn.close()

if __name__ == "__main__":
    from src.ingestion.riot_client import get_puuid, get_match_ids

    puuid = get_puuid("brandtop", "1234", region="europe")
    match_ids = get_match_ids(puuid, region="europe", count=10)

    ingest_matches(match_ids)
import psycopg2
from src.ingestion.config import DATABASE_URL

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def insert_match(conn, match_row: tuple):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO matches (match_id, patch, queue_id, game_duration, game_creation_ts, region)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (match_id) DO NOTHING
        """,
        match_row
    )
    conn.commit()
    cur.close()

def insert_participants(conn, participant_rows: list[tuple]):
    cur = conn.cursor()
    for row in participant_rows:
        cur.execute(
            """
            INSERT INTO participants
                (match_id, puuid, champion_id, team_id, role, win, kills, deaths, assists, gold_earned, items, cs)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (match_id, puuid) DO NOTHING
            """,
            row
        )
    conn.commit()
    cur.close()

def insert_frames(conn, frame_rows: list[tuple]):
    cur = conn.cursor()
    for row in frame_rows:
        cur.execute(
            """
            INSERT INTO timeline_frames (match_id, puuid, minute, gold, xp, cs, position_x, position_y)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (match_id, puuid, minute) DO NOTHING
            """,
            row
        )
    conn.commit()
    cur.close()

def insert_events(conn, event_rows: list[tuple]):
    cur = conn.cursor()
    for row in event_rows:
        cur.execute(
            """
            INSERT INTO timeline_events (match_id, timestamp, event_type, actor_puuid, victim_puuid, details)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            row
        )
    conn.commit()
    cur.close()
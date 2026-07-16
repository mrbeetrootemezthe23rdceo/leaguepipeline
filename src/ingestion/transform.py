from datetime import datetime, timezone
import json

def extract_match_row(match_id: str, match_json: dict) -> tuple:
    info = match_json["info"]

    # gameVersion looks like "14.14.567890" — we only want "14.14"
    version_parts = info["gameVersion"].split(".")
    patch = f"{version_parts[0]}.{version_parts[1]}"

    game_creation_ts = datetime.fromtimestamp(
        info["gameCreation"] / 1000, tz=timezone.utc
    )

    return (
        match_id,
        patch,
        info["queueId"],
        info["gameDuration"],
        game_creation_ts,
        info["platformId"],
    )

def extract_participant_rows(match_id: str, match_json: dict) -> list[tuple]:
    participants = match_json["info"]["participants"]
    rows = []

    for p in participants:
        items = [p[f"item{i}"] for i in range(7)]
        cs = p["totalMinionsKilled"] + p["neutralMinionsKilled"]

        row = (
            match_id,
            p["puuid"],
            p["championId"],
            p["teamId"],
            p["teamPosition"],   # -> role
            p["win"],
            p["kills"],
            p["deaths"],
            p["assists"],
            p["goldEarned"],
            items,
            cs,
        )
        rows.append(row)

    return rows

def build_participant_id_map(match_json: dict) -> dict[int, str]:
    participants = match_json["info"]["participants"]
    return {p["participantId"]: p["puuid"] for p in participants}

def extract_frame_rows(match_id: str, timeline_json: dict, id_to_puuid: dict) -> list[tuple]:
    frames = timeline_json["info"]["frames"]
    rows = []

    for minute_index, frame in enumerate(frames):
        for participant_id_str, pframe in frame["participantFrames"].items():
            participant_id = int(participant_id_str)
            puuid = id_to_puuid[participant_id]

            position = pframe.get("position")
            pos_x = position["x"] if position else None
            pos_y = position["y"] if position else None

            row = (
                match_id,
                puuid,
                minute_index,
                pframe["totalGold"],
                pframe["xp"],
                pframe["minionsKilled"] + pframe["jungleMinionsKilled"],  # cs
                pos_x,
                pos_y,
            )
            rows.append(row)

    return rows

def extract_event_rows(match_id: str, timeline_json: dict, id_to_puuid: dict) -> list[tuple]:
    frames = timeline_json["info"]["frames"]
    rows = []

    for frame in frames:
        for event in frame["events"]:
            actor_id = event.get("killerId") or event.get("creatorId") or event.get("participantId")
            victim_id = event.get("victimId")

            actor_puuid = id_to_puuid.get(actor_id) if actor_id else None
            victim_puuid = id_to_puuid.get(victim_id) if victim_id else None

            row = (
                match_id,
                event["timestamp"],
                event["type"],
                actor_puuid,
                victim_puuid,
                json.dumps(event),
            )
            rows.append(row)

    return rows
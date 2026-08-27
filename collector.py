#!/usr/bin/env python3
"""
Football Match Data Collector
Collects match data from football-data.org API
and generates clean matches.json
"""

import requests
import json
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any


# =========================================================
# CONFIGURATION
# =========================================================

API_BASE = "https://api.football-data.org/v4"
OUTPUT_FILE = "matches.json"

LEAGUE_IDS = {
    "PL": 39,
    "PD": 140,
    "SA": 135,
    "BL1": 25,
    "FL1": 61,
}


# =========================================================
# API KEY
# =========================================================

def get_api_key():

    key = os.getenv("FOOTBALL_DATA_API_KEY")

    if key:
        return key.strip()

    print("⚠️ No API key found!")
    print(
        "Get your API key at:"
        " https://www.football-data.org/client/register"
    )

    key = input("Enter your API key: ").strip()

    return key


# =========================================================
# DATETIME HELPERS
# =========================================================

def parse_datetime(value):

    if not value:
        return None

    try:
        # Example:
        # 2026-08-27T18:00:00Z
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except Exception:
        return None


def now_utc():

    return datetime.now(timezone.utc)


# =========================================================
# DETERMINE STATUS
# =========================================================

def determine_status(match):

    api_status = str(
        match.get("status") or ""
    ).upper().strip()

    utc_date = parse_datetime(
        match.get("utcDate")
    )

    now = now_utc()

    # -----------------------------------------------------
    # Explicit live statuses
    # -----------------------------------------------------

    live_statuses = {
        "IN_PLAY",
        "PAUSED",
        "LIVE",
        "SUSPENDED",
        "HALFTIME",
        "EXTRA_TIME",
        "PENALTY_SHOOTOUT",
    }

    if api_status in live_statuses:
        return "LIVE"

    # -----------------------------------------------------
    # Explicit finished statuses
    # -----------------------------------------------------

    finished_statuses = {
        "FINISHED",
        "AWARDED",
        "POSTPONED_FINISHED",
    }

    if api_status in finished_statuses:
        return "FINISHED"

    # -----------------------------------------------------
    # Cancelled / postponed
    # -----------------------------------------------------

    if api_status in {
        "CANCELLED",
        "POSTPONED",
        "SUSPENDED",
    }:

        # Suspended may actually still be live.
        if api_status == "SUSPENDED":
            return "LIVE"

        return "FINISHED"

    # -----------------------------------------------------
    # TIMED / SCHEDULED
    # -----------------------------------------------------

    if utc_date:

        # Match time already passed.
        #
        # We do NOT classify it as upcoming.
        if utc_date <= now:

            return "FINISHED"

        return "UPCOMING"

    # -----------------------------------------------------
    # Fallback
    # -----------------------------------------------------

    if api_status in {
        "SCHEDULED",
        "TIMED"
    }:
        return "UPCOMING"

    return "UPCOMING"


# =========================================================
# FETCH MATCHES
# =========================================================

def fetch_matches(api_key: str) -> List[Dict[str, Any]]:

    headers = {
        "X-Auth-Token": api_key
    }

    all_matches = []

    now = datetime.now()

    from_date = (
        now - timedelta(days=30)
    ).strftime("%Y-%m-%d")

    to_date = (
        now + timedelta(days=7)
    ).strftime("%Y-%m-%d")

    for league_code, league_id in LEAGUE_IDS.items():

        try:

            url = (
                f"{API_BASE}/competitions/"
                f"{league_id}/matches"
            )

            params = {
                "status":
                    "FINISHED,SCHEDULED,LIVE,"
                    "IN_PLAY,PAUSED",
                "dateFrom": from_date,
                "dateTo": to_date
            }

            print(
                f"📥 Fetching {league_code}...",
                end=" ",
                flush=True
            )

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=20
            )

            if response.status_code == 200:

                data = response.json()

                league_matches = data.get(
                    "matches",
                    []
                )

                print(
                    f"✅ {len(league_matches)} matches"
                )

                all_matches.extend(
                    league_matches
                )

            else:

                print(
                    f"❌ Error {response.status_code}"
                )

                try:
                    print(response.text[:300])
                except Exception:
                    pass

        except Exception as e:

            print(
                f"❌ {e}"
            )

    return all_matches


# =========================================================
# NORMALIZE MATCH
# =========================================================

def normalize_match(
    match: Dict[str, Any]
) -> Dict[str, Any]:

    home_team = match.get(
        "homeTeam",
        {}
    ) or {}

    away_team = match.get(
        "awayTeam",
        {}
    ) or {}

    competition = match.get(
        "competition",
        {}
    ) or {}

    score = match.get(
        "score",
        {}
    ) or {}

    full_time = score.get(
        "fullTime",
        {}
    ) or {}

    home_score = full_time.get(
        "home"
    )

    away_score = full_time.get(
        "away"
    )

    calculated_status = determine_status(
        match
    )

    return {

        # -------------------------------------------------
        # BASIC
        # -------------------------------------------------

        "id": match.get("id"),

        "event_date":
            match.get("utcDate"),

        "status":
            calculated_status,

        "api_status":
            match.get("status"),

        "current_minute":
            match.get("minute"),

        # -------------------------------------------------
        # LEAGUE
        # -------------------------------------------------

        "league_id":
            competition.get("id"),

        "league_name":
            competition.get("name"),

        "league_code":
            competition.get("code"),

        # -------------------------------------------------
        # HOME
        # -------------------------------------------------

        "home_team_id":
            home_team.get("id"),

        "home_team":
            home_team.get("name"),

        "home_team_name":
            home_team.get("name"),

        "home_score":
            home_score,

        # -------------------------------------------------
        # AWAY
        # -------------------------------------------------

        "away_team_id":
            away_team.get("id"),

        "away_team":
            away_team.get("name"),

        "away_team_name":
            away_team.get("name"),

        "away_score":
            away_score,

        # -------------------------------------------------
        # FINAL SCORE
        # -------------------------------------------------

        "final_score": (
            f"{home_score} - {away_score}"
            if (
                home_score is not None
                and
                away_score is not None
            )
            else None
        ),
    }


# =========================================================
# REMOVE DUPLICATES
# =========================================================

def remove_duplicates(
    matches: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    unique = {}

    for match in matches:

        match_id = match.get("id")

        if match_id is None:
            continue

        unique[match_id] = match

    return list(unique.values())


# =========================================================
# SORT MATCHES
# =========================================================

def sort_matches(
    matches: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    def sort_key(match):

        date = parse_datetime(
            match.get("event_date")
        )

        if date is None:
            return datetime.max.replace(
                tzinfo=timezone.utc
            )

        return date

    return sorted(
        matches,
        key=sort_key
    )


# =========================================================
# SAVE JSON
# =========================================================

def save_matches(
    matches: List[Dict[str, Any]]
):

    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                matches,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(
            f"\n✅ Saved "
            f"{len(matches)} matches "
            f"to {OUTPUT_FILE}"
        )

    except Exception as e:

        print(
            f"❌ Failed to save: {e}"
        )


# =========================================================
# PRINT STATISTICS
# =========================================================

def print_stats(
    matches: List[Dict[str, Any]]
):

    live = [
        m for m in matches
        if m["status"] == "LIVE"
    ]

    upcoming = [
        m for m in matches
        if m["status"] == "UPCOMING"
    ]

    finished = [
        m for m in matches
        if m["status"] == "FINISHED"
    ]

    print("\n📊 Stats:")
    print(
        f"   Total: {len(matches)}"
    )

    print(
        f"   🔴 Live: {len(live)}"
    )

    print(
        f"   🕐 Upcoming: {len(upcoming)}"
    )

    print(
        f"   ✓ Finished: {len(finished)}"
    )


# =========================================================
# DEBUG STATUS
# =========================================================

def print_status_preview(
    matches: List[Dict[str, Any]]
):

    print("\n🔎 Status preview:")

    for match in matches[:15]:

        print(
            f"  {match.get('home_team')} "
            f"vs "
            f"{match.get('away_team')} "
            f"→ "
            f"{match.get('status')} "
            f"("
            f"{match.get('api_status')}"
            f")"
        )


# =========================================================
# MAIN
# =========================================================

def main():

    print(
        "⚽ Football Match Collector"
    )

    print(
        "=" * 45
    )

    api_key = get_api_key()

    if not api_key:

        print(
            "❌ No API key provided"
        )

        return

    # -----------------------------------------------------
    # FETCH
    # -----------------------------------------------------

    raw_matches = fetch_matches(
        api_key
    )

    if not raw_matches:

        print(
            "❌ No matches found"
        )

        return

    # -----------------------------------------------------
    # NORMALIZE
    # -----------------------------------------------------

    normalized = [
        normalize_match(match)
        for match in raw_matches
    ]

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    normalized = remove_duplicates(
        normalized
    )

    # -----------------------------------------------------
    # SORT
    # -----------------------------------------------------

    normalized = sort_matches(
        normalized
    )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    save_matches(
        normalized
    )

    # -----------------------------------------------------
    # STATS
    # -----------------------------------------------------

    print_stats(
        normalized
    )

    # -----------------------------------------------------
    # DEBUG
    # -----------------------------------------------------

    print_status_preview(
        normalized
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()

import json
import os
import requests
from datetime import datetime, timedelta, timezone

API_BASE = "https://sports.bzzoiro.com/api/v2"
EVENTS_URL = f"{API_BASE}/events/"
API_KEY = os.environ["BSD_API_KEY"]

HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "User-Agent": "FootballMatchCenter/1.0"
}

today = datetime.now(timezone.utc).date()

date_from = today.isoformat()
date_to = (today + timedelta(days=7)).isoformat()

print("======================================")
print(" FOOTBALL MATCH CENTER COLLECTOR")
print("======================================")

print("From:", date_from)
print("To:", date_to)


# =========================================================
# GET ALL MATCHES
# =========================================================

matches = []

offset = 0
limit = 200

while True:

    params = {
        "date_from": date_from,
        "date_to": date_to,
        "limit": limit,
        "offset": offset
    }

    print()
    print("Downloading matches...")
    print("Offset:", offset)

    response = requests.get(
        EVENTS_URL,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    print("HTTP:", response.status_code)

    response.raise_for_status()

    data = response.json()

    results = data.get("results", [])

    print(
        "Received:",
        len(results)
    )

    matches.extend(results)

    if not data.get("next") or not results:
        break

    offset += limit


print()
print("TOTAL MATCHES:", len(matches))


# =========================================================
# SAVE MATCHES
# =========================================================

matches_output = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": "BSD Football API",
    "date_from": date_from,
    "date_to": date_to,
    "matches": matches
}

with open(
    "matches.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        matches_output,
        f,
        ensure_ascii=False,
        indent=2
    )


print("matches.json updated successfully.")


# =========================================================
# COLLECT UNIQUE TEAM IDS
# =========================================================

team_ids = set()

for match in matches:

    if match.get("home_team_id") is not None:
        team_ids.add(
            match["home_team_id"]
        )

    if match.get("away_team_id") is not None:
        team_ids.add(
            match["away_team_id"]
        )


print()
print("UNIQUE TEAMS:", len(team_ids))


# =========================================================
# COLLECT UNIQUE LEAGUE IDS
# =========================================================

league_ids = set()

for match in matches:

    if match.get("league_id") is not None:
        league_ids.add(
            match["league_id"]
        )


print(
    "UNIQUE LEAGUES:",
    len(league_ids)
)


# =========================================================
# TRY TEAM ENDPOINTS
# =========================================================

team_endpoints = [
    f"{API_BASE}/teams/",
    f"{API_BASE}/team/",
    f"{API_BASE}/participants/"
]

teams_data = {}

for url in team_endpoints:

    print()
    print("Testing TEAM endpoint:")
    print(url)

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print(
            "HTTP:",
            response.status_code
        )

        if response.status_code != 200:
            continue

        data = response.json()

        teams_data = data

        print(
            "TEAM endpoint works!"
        )

        break

    except Exception as error:

        print(
            "TEAM endpoint error:",
            error
        )


# =========================================================
# SAVE TEAM DATA IF FOUND
# =========================================================

if teams_data:

    with open(
        "teams.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            teams_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        "teams.json created successfully."
    )

else:

    print(
        "No public TEAM endpoint found."
    )


# =========================================================
# TRY LEAGUE ENDPOINTS
# =========================================================

league_endpoints = [
    f"{API_BASE}/leagues/",
    f"{API_BASE}/league/",
    f"{API_BASE}/competitions/"
]

leagues_data = {}

for url in league_endpoints:

    print()
    print("Testing LEAGUE endpoint:")
    print(url)

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        print(
            "HTTP:",
            response.status_code
        )

        if response.status_code != 200:
            continue

        data = response.json()

        leagues_data = data

        print(
            "LEAGUE endpoint works!"
        )

        break

    except Exception as error:

        print(
            "LEAGUE endpoint error:",
            error
        )


# =========================================================
# SAVE LEAGUE DATA IF FOUND
# =========================================================

if leagues_data:

    with open(
        "leagues.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            leagues_data,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        "leagues.json created successfully."
    )

else:

    print(
        "No public LEAGUE endpoint found."
    )


# =========================================================
# CREATE SIMPLE TEAM LIST
# =========================================================

simple_teams = {}

for match in matches:

    home_id = match.get(
        "home_team_id"
    )

    away_id = match.get(
        "away_team_id"
    )

    home_name = match.get(
        "home_team"
    )

    away_name = match.get(
        "away_team"
    )

    if home_id is not None:

        simple_teams[str(home_id)] = {
            "id": home_id,
            "name": home_name
        }

    if away_id is not None:

        simple_teams[str(away_id)] = {
            "id": away_id,
            "name": away_name
        }


with open(
    "team_list.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        simple_teams,
        f,
        ensure_ascii=False,
        indent=2
    )


print()
print(
    "team_list.json created:",
    len(simple_teams),
    "teams"
)


# =========================================================
# CREATE SIMPLE LEAGUE LIST
# =========================================================

simple_leagues = {}

for match in matches:

    league_id = match.get(
        "league_id"
    )

    if league_id is None:
        continue

    simple_leagues[str(league_id)] = {
        "id": league_id
    }


with open(
    "league_list.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        simple_leagues,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
    "league_list.json created:",
    len(simple_leagues),
    "leagues"
)


print()
print("======================================")
print(" COLLECTION FINISHED")
print("======================================")

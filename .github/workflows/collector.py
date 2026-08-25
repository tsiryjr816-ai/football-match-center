import json
import os
import requests
from datetime import datetime, timedelta, timezone

API_URL = "https://sports.bzzoiro.com/api/v2/events/"
API_KEY = os.environ["BSD_API_KEY"]

HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "User-Agent": "FootballMatchCenter/1.0"
}

today = datetime.now(timezone.utc).date()
date_from = today.isoformat()
date_to = (today + timedelta(days=7)).isoformat()

print("======================================")
print("FOOTBALL MATCH CENTER")
print("======================================")
print("From:", date_from)
print("To:", date_to)

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

    response = requests.get(
        API_URL,
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
        len(results),
        "| offset:",
        offset
    )

    matches.extend(results)

    if not data.get("next") or not results:
        break

    offset += limit

print("TOTAL MATCHES:", len(matches))


# matches.json
with open("matches.json", "w", encoding="utf-8") as f:
    json.dump(
        {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "source": "BSD Football API",
            "date_from": date_from,
            "date_to": date_to,
            "matches": matches
        },
        f,
        ensure_ascii=False,
        indent=2
    )

print("matches.json OK")


# TEAM IDs + names
teams = {}

for match in matches:

    home_id = match.get("home_team_id")
    away_id = match.get("away_team_id")

    home_name = match.get("home_team")
    away_name = match.get("away_team")

    if home_id is not None:
        teams[str(home_id)] = {
            "id": home_id,
            "name": home_name
        }

    if away_id is not None:
        teams[str(away_id)] = {
            "id": away_id,
            "name": away_name
        }


with open("team_list.json", "w", encoding="utf-8") as f:
    json.dump(
        teams,
        f,
        ensure_ascii=False,
        indent=2
    )

print("team_list.json OK:", len(teams))


# LEAGUE IDs
leagues = {}

for match in matches:

    league_id = match.get("league_id")

    if league_id is not None:
        leagues[str(league_id)] = {
            "id": league_id
        }


with open("league_list.json", "w", encoding="utf-8") as f:
    json.dump(
        leagues,
        f,
        ensure_ascii=False,
        indent=2
    )

print("league_list.json OK:", len(leagues))


# Get teams endpoint
teams_api = {}

try:

    url = "https://sports.bzzoiro.com/api/v2/teams/"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    print("TEAMS API:", response.status_code)

    if response.status_code == 200:
        teams_api = response.json()

except Exception as e:

    print("Teams API error:", e)


with open("teams.json", "w", encoding="utf-8") as f:
    json.dump(
        teams_api,
        f,
        ensure_ascii=False,
        indent=2
    )

print("teams.json OK")


# Get leagues endpoint
leagues_api = {}

try:

    url = "https://sports.bzzoiro.com/api/v2/leagues/"

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    print("LEAGUES API:", response.status_code)

    if response.status_code == 200:
        leagues_api = response.json()

except Exception as e:

    print("Leagues API error:", e)


with open("leagues.json", "w", encoding="utf-8") as f:
    json.dump(
        leagues_api,
        f,
        ensure_ascii=False,
        indent=2
    )

print("leagues.json OK")

print("======================================")
print("COLLECTION FINISHED")
print("======================================")

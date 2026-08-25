import json
import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "https://sports.bzzoiro.com/api/v2/events/"
TEAMS_URL = "https://sports.bzzoiro.com/api/v2/teams/"
LEAGUES_URL = "https://sports.bzzoiro.com/api/v2/leagues/"

API_KEY = os.environ["BSD_API_KEY"]

HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "User-Agent": "FootballMatchCenter/2.0"
}

WIKI_API = "https://en.wikipedia.org/w/api.php"


# ============================================================
# DATE RANGE
# ============================================================

today = datetime.now(timezone.utc).date()

date_from = today.isoformat()
date_to = (today + timedelta(days=7)).isoformat()


print("======================================")
print("FOOTBALL MATCH CENTER")
print("======================================")
print("From:", date_from)
print("To:", date_to)


# ============================================================
# DOWNLOAD MATCHES
# ============================================================

matches = []

offset = 0
limit = 200

while True:

    print()
    print("Downloading matches...")
    print("Offset:", offset)

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


print()
print("TOTAL MATCHES:", len(matches))


# ============================================================
# SAVE matches.json
# ============================================================

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

print("matches.json OK")


# ============================================================
# BUILD TEAM LIST FROM MATCHES
# ============================================================

teams = {}

for match in matches:

    home_id = match.get("home_team_id")
    away_id = match.get("away_team_id")

    home_name = match.get("home_team")
    away_name = match.get("away_team")

    if home_id is not None:

        teams[str(home_id)] = {
            "id": home_id,
            "name": home_name or "Unknown Team"
        }

    if away_id is not None:

        teams[str(away_id)] = {
            "id": away_id,
            "name": away_name or "Unknown Team"
        }


with open(
    "team_list.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        teams,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
    "team_list.json OK:",
    len(teams)
)


# ============================================================
# BUILD LEAGUE LIST
# ============================================================

leagues = {}

for match in matches:

    league_id = match.get("league_id")

    if league_id is not None:

        leagues[str(league_id)] = {
            "id": league_id,
            "name": match.get(
                "league_name",
                ""
            )
        }


with open(
    "league_list.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        leagues,
        f,
        ensure_ascii=False,
        indent=2
    )


print(
    "league_list.json OK:",
    len(leagues)
)


# ============================================================
# GET TEAMS API
# ============================================================

teams_api = {}

try:

    response = requests.get(
        TEAMS_URL,
        headers=HEADERS,
        timeout=30
    )

    print(
        "TEAMS API:",
        response.status_code
    )

    if response.status_code == 200:

        teams_api = response.json()

except Exception as e:

    print(
        "Teams API error:",
        e
    )


with open(
    "teams.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        teams_api,
        f,
        ensure_ascii=False,
        indent=2
    )


print("teams.json OK")


# ============================================================
# GET LEAGUES API
# ============================================================

leagues_api = {}

try:

    response = requests.get(
        LEAGUES_URL,
        headers=HEADERS,
        timeout=30
    )

    print(
        "LEAGUES API:",
        response.status_code
    )

    if response.status_code == 200:

        leagues_api = response.json()

except Exception as e:

    print(
        "Leagues API error:",
        e
    )


with open(
    "leagues.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        leagues_api,
        f,
        ensure_ascii=False,
        indent=2
    )


print("leagues.json OK")


# ============================================================
# TEAM LOGOS
# ============================================================

print()
print("======================================")
print("TEAM LOGO COLLECTION")
print("======================================")


def clean_team_name(name):

    if not name:
        return ""

    name = str(name).strip()

    # Remove common youth/reserve suffixes
    replacements = [
        " Women",
        " W",
        " U23",
        " U21",
        " U20",
        " U19",
        " U18",
        " U17",
        " II",
        " B"
    ]

    cleaned = name

    for item in replacements:

        if cleaned.endswith(item):

            cleaned = cleaned[:-len(item)]

    return cleaned.strip()


def get_wikipedia_logo(team_id, team_name):

    if not team_name:
        return {
            "id": team_id,
            "name": team_name,
            "logo": None,
            "source": None
        }


    # Try original name first
    names_to_try = [
        team_name,
        clean_team_name(team_name)
    ]

    # Remove duplicates
    names_to_try = list(
        dict.fromkeys(
            n for n in names_to_try
            if n
        )
    )


    for search_name in names_to_try:

        try:

            params = {
                "action": "query",
                "generator": "search",
                "gsrsearch": search_name,
                "gsrnamespace": "0",
                "gsrlimit": "5",
                "prop": "pageimages",
                "piprop": "thumbnail",
                "pithumbsize": "150",
                "format": "json"
            }

            response = requests.get(
                WIKI_API,
                params=params,
                timeout=10
            )


            if response.status_code != 200:
                continue


            data = response.json()

            pages = (
                data
                .get("query", {})
                .get("pages", {})
            )


            if not pages:
                continue


            # Find best matching result
            best_page = None

            for page in pages.values():

                title = page.get(
                    "title",
                    ""
                ).lower()

                target = search_name.lower()

                if (
                    title == target
                    or target in title
                    or title in target
                ):

                    best_page = page
                    break


            if best_page is None:

                best_page = next(
                    iter(pages.values())
                )


            thumbnail = (
                best_page
                .get("thumbnail", {})
                .get("source")
            )


            if thumbnail:

                return {
                    "id": team_id,
                    "name": team_name,
                    "logo": thumbnail,
                    "source": "Wikipedia"
                }


        except Exception:

            continue


    return {
        "id": team_id,
        "name": team_name,
        "logo": None,
        "source": None
    }


# ============================================================
# COLLECT LOGOS
# ============================================================

team_logos = {}

team_items = list(
    teams.items()
)


print(
    "Teams requiring logos:",
    len(team_items)
)


def process_team(item):

    team_id, team = item

    return get_wikipedia_logo(
        team_id,
        team.get("name", "")
    )


# Use several workers to avoid taking too long
with ThreadPoolExecutor(
    max_workers=8
) as executor:

    futures = [
        executor.submit(
            process_team,
            item
        )
        for item in team_items
    ]

    completed = 0

    for future in as_completed(futures):

        try:

            result = future.result()

            team_logos[
                str(result["id"])
            ] = result

        except Exception as e:

            print(
                "Logo error:",
                e
            )

        completed += 1

        if (
            completed % 50 == 0
            or completed == len(team_items)
        ):

            print(
                "Logo progress:",
                completed,
                "/",
                len(team_items)
            )


# ============================================================
# SAVE TEAM LOGOS
# ============================================================

with open(
    "team_logos.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        {
            "updated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "source":
                "Wikipedia",

            "teams":
                team_logos
        },
        f,
        ensure_ascii=False,
        indent=2
    )


logo_count = sum(
    1
    for team in team_logos.values()
    if team.get("logo")
)


print()
print(
    "team_logos.json OK"
)

print(
    "Teams:",
    len(team_logos)
)

print(
    "Logos found:",
    logo_count
)

print(
    "Logos missing:",
    len(team_logos) - logo_count
)


# ============================================================
# FINISHED
# ============================================================

print()
print("======================================")
print("COLLECTION FINISHED")
print("======================================")

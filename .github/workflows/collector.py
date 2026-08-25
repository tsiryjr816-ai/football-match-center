import requests
import re

URL = "https://www.eurosport.fr/football/score-center.shtml"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0 Mobile Safari/537.36"
    )
}

print("Downloading Eurosport...")

response = requests.get(
    URL,
    headers=HEADERS,
    timeout=30
)

print("HTTP status:", response.status_code)
print("Page size:", len(response.text))

html = response.text

# Search for common football-team / match indicators
patterns = [
    r'"homeTeam"',
    r'"awayTeam"',
    r'"home_team"',
    r'"away_team"',
    r'"home"',
    r'"away"',
    r'"startDate"',
    r'"startTime"',
    r'"match"',
    r'"fixture"',
    r'"event"',
    r'"competition"',
]

print("\n--- DATA INDICATORS ---")

for pattern in patterns:

    found = len(
        re.findall(
            pattern,
            html,
            flags=re.IGNORECASE
        )
    )

    print(pattern, "=>", found)

# Search for JSON-like structures containing team names
print("\n--- POSSIBLE TEAM DATA ---")

keywords = [
    "Arsenal",
    "Chelsea",
    "Liverpool",
    "Manchester",
    "Real Madrid",
    "Barcelona",
    "Bayern",
    "Juventus"
]

for keyword in keywords:

    positions = [
        m.start()
        for m in re.finditer(
            re.escape(keyword),
            html,
            flags=re.IGNORECASE
        )
    ]

    print(
        keyword,
        "=>",
        len(positions),
        "occurrences"
    )

    # Print one small context around the first occurrence
    if positions:

        pos = positions[0]

        start = max(0, pos - 300)
        end = min(len(html), pos + 500)

        print(
            html[start:end]
            .replace("\n", " ")[:800]
        )

        print("\n---")

print("\nTEST FINISHED")

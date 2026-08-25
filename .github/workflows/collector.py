import json
import os
import requests
from datetime import datetime, timedelta, timezone

API_URL = "https://sports.bzzoiro.com/api/v2/events/"
API_KEY = os.environ["BSD_API_KEY"]

headers = {
    "Authorization": f"Token {API_KEY}",
    "User-Agent": "FootballMatchCenter/1.0"
}

today = datetime.now(timezone.utc).date()

# Androany hatramin'ny +7 andro
date_from = today.isoformat()
date_to = (today + timedelta(days=7)).isoformat()

print("Downloading football matches...")
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
        headers=headers,
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
        "matches | offset:",
        offset
    )

    matches.extend(results)

    if not data.get("next") or not results:
        break

    offset += limit

print("TOTAL MATCHES:", len(matches))

output = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": "BSD Football API",
    "date_from": date_from,
    "date_to": date_to,
    "matches": matches
}

with open("matches.json", "w", encoding="utf-8") as f:
    json.dump(
        output,
        f,
        ensure_ascii=False,
        indent=2
    )

print("matches.json updated successfully.")

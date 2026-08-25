import json
import requests
from datetime import datetime, timezone

URL = "https://sporting-events.org/data/football/"

print("Downloading Sporting Events...")

response = requests.get(
    URL,
    timeout=30,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

print("HTTP status:", response.status_code)
print("Page size:", len(response.text))

if response.status_code != 200:
    raise Exception("Sporting Events download failed")

print("Source downloaded successfully.")

print("Now checking available football data...")

# Temporary test
data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "source": "Sporting Events",
    "matches": []
}

with open("matches.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("matches.json updated.")

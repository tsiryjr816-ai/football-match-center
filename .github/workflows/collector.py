import json
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

URL = "https://www.eurosport.fr/football/score-center.shtml"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Linux; Android 10) "
        "AppleWebKit/537.36 Chrome/151.0 Mobile Safari/537.36"
    )
}

def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def get_page():
    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def extract_matches(html):

    soup = BeautifulSoup(html, "html.parser")

    matches = []

    # Look through links representing football match pages.
    for link in soup.find_all("a", href=True):

        href = link.get("href", "")

        # Eurosport match links normally contain live-matches or match data.
        if "live-matches" not in href:
            continue

        text = clean(link.get_text(" ", strip=True))

        if not text:
            continue

        # Remove obvious non-match links.
        if len(text) < 5:
            continue

        # Try to identify the two teams and kickoff time.
        time_match = re.search(
            r"\b([01]?\d|2[0-3]):[0-5]\d\b",
            text
        )

        if not time_match:
            continue

        time_value = time_match.group(0)

        before = clean(text[:time_match.start()])
        after = clean(text[time_match.end():])

        # The visible match pages commonly contain:
        # Home Team + time + Away Team
        if not before or not after:
            continue

        # Remove score/live-minute information if present.
        after = re.sub(
            r"\b\d+\s*-\s*\d+\b.*$",
            "",
            after
        ).strip()

        if not after:
            continue

        match = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": time_value,
            "home_team": before,
            "away_team": after
        }

        matches.append(match)

    # Remove duplicates
    unique = {}

    for match in matches:

        key = (
            match["date"],
            match["time"],
            match["home_team"].lower(),
            match["away_team"].lower()
        )

        unique[key] = match

    return list(unique.values())


def save(matches):

    data = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "matches": matches
    }

    with open(
        "matches.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():

    print("Downloading Eurosport Score Center...")

    html = get_page()

    print("Page downloaded.")

    matches = extract_matches(html)

    print("Matches detected:", len(matches))

    for match in matches:
        print(
            match["date"],
            match["time"],
            match["home_team"],
            "vs",
            match["away_team"]
        )

    save(matches)

    print("matches.json updated successfully.")


if __name__ == "__main__":
    main()

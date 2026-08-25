import os
import requests

API_KEY = os.environ["BSD_API_KEY"]

headers = {
    "Authorization": f"Token {API_KEY}",
    "User-Agent": "FootballMatchCenter/1.0"
}

urls = [
    "https://sports.bzzoiro.com/api/v2/teams/",
    "https://sports.bzzoiro.com/api/v2/leagues/",
    "https://sports.bzzoiro.com/api/v2/competitions/"
]

for url in urls:

    print("\nTEST:", url)

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=20
        )

        print("HTTP:", response.status_code)

        print(
            response.text[:1000]
        )

    except Exception as e:

        print(
            "ERROR:",
            e
        )

import requests
from bs4 import BeautifulSoup

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

soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a", href=True)

print("Total links:", len(links))

print("\n--- FOOTBALL RELATED LINKS ---")

count = 0

keywords = [
    "football",
    "premier",
    "liga",
    "league",
    "champions",
    "match",
    "score",
    "arsenal",
    "chelsea",
    "liverpool"
]

for link in links:

    text = " ".join(link.stripped_strings)
    href = link.get("href", "")

    combined = (text + " " + href).lower()

    if any(word in combined for word in keywords):

        print("TEXT:", text[:200])
        print("URL :", href[:300])
        print("---")

        count += 1

        if count >= 50:
            break

print("\nRelated links displayed:", count)
print("TEST FINISHED")

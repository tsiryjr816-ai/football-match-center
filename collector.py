#!/usr/bin/env python3
"""
Football Match Data Collector
Collects match data from football-data.org API
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Configuration
API_BASE = "https://api.football-data.org/v4"
OUTPUT_FILE = "matches.json"

# Popular league IDs from football-data.org
LEAGUE_IDS = {
    "PL": 39,      # Premier League
    "PD": 140,     # La Liga
    "SA": 135,     # Serie A
    "BL1": 25,     # Bundesliga
    "FL1": 61,     # Ligue 1
}

def get_api_key():
    """Get API key from environment or prompt user"""
    key = os.getenv("FOOTBALL_DATA_API_KEY")
    if not key:
        print("⚠️  No API key found!")
        print("Get free key at: https://www.football-data.org/client/register")
        key = input("Enter your API key: ").strip()
    return key

def fetch_matches(api_key: str) -> List[Dict[str, Any]]:
    """Fetch matches from multiple leagues"""
    headers = {"X-Auth-Token": api_key}
    all_matches = []
    
    # Fetch last 30 days of matches
    from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    for league_code, league_id in LEAGUE_IDS.items():
        try:
            url = f"{API_BASE}/competitions/{league_id}/matches"
            params = {
                "status": "FINISHED,SCHEDULED,LIVE,IN_PLAY",
                "dateFrom": from_date,
                "dateTo": to_date
            }
            
            print(f"📥 Fetching {league_code}...", end=" ", flush=True)
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                matches = data.get("matches", [])
                print(f"✅ {len(matches)} matches")
                all_matches.extend(matches)
            else:
                print(f"❌ Error {resp.status_code}")
                
        except Exception as e:
            print(f"❌ {e}")
    
    return all_matches

def normalize_match(match: Dict[str, Any]) -> Dict[str, Any]:
    """Convert API response to our format"""
    return {
        "id": match.get("id"),
        "event_date": match.get("utcDate"),
        "status": match.get("status"),
        "current_minute": match.get("minute"),
        
        "league_id": match.get("competition", {}).get("id"),
        "league_name": match.get("competition", {}).get("name"),
        
        "home_team_id": match.get("homeTeam", {}).get("id"),
        "home_team_name": match.get("homeTeam", {}).get("name"),
        "home_score": match.get("score", {}).get("fullTime", {}).get("home"),
        
        "away_team_id": match.get("awayTeam", {}).get("id"),
        "away_team_name": match.get("awayTeam", {}).get("name"),
        "away_score": match.get("score", {}).get("fullTime", {}).get("away"),
    }

def save_matches(matches: List[Dict[str, Any]]):
    """Save matches to JSON file"""
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(matches, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(matches)} matches to {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Failed to save: {e}")

def main():
    print("⚽ Football Match Collector")
    print("=" * 40)
    
    api_key = get_api_key()
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Fetch matches
    matches = fetch_matches(api_key)
    
    if not matches:
        print("❌ No matches found")
        return
    
    # Normalize
    normalized = [normalize_match(m) for m in matches]
    
    # Save
    save_matches(normalized)
    
    # Stats
    finished = [m for m in normalized if m["home_score"] is not None]
    print(f"\n📊 Stats:")
    print(f"   Total matches: {len(normalized)}")
    print(f"   Finished: {len(finished)}")
    print(f"   Upcoming: {len(normalized) - len(finished)}")

if __name__ == "__main__":
    main()

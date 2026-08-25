import json
from datetime import datetime, timezone

# Temporary collector structure.
# The real public-source parser will be added next.

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "matches": []
}

with open("matches.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Collector executed successfully.")
print("Matches:", len(data["matches"]))

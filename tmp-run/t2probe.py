import sys, urllib.parse
sys.path.insert(0,'.')
from scripts.fotmob import _get_json
CAND=[70,71,72,123,124,125,126,127,206,207,208,299,300,301,302,303,304]
for lid in CAND:
    try:
        d=_get_json(f"https://www.fotmob.com/api/data/leagues?id={lid}&season={urllib.parse.quote('2025/2026',safe='')}")
        det=d.get("details") or {}
        print(lid, "|", det.get("country"), "|", det.get("name"), "|", det.get("selectedSeason"))
    except Exception as e:
        print(lid, "ERR", type(e).__name__, str(e)[:60])

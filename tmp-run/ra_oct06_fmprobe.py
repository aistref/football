"""Zoek de vijf FA Cup-duels in de Fotmob-daglijsten van 6 en 7 okt, op teamnaam."""
import json, re
from datetime import date
from scripts import fotmob

NAMES = ["Atherton", "Trafford", "Halesowen", "Stafford", "Scarborough",
         "Macclesfield", "Spalding", "Bury Town", "Wingate", "Bedford"]

hits = []
for d in (date(2026, 10, 6), date(2026, 10, 7)):
    fx = fotmob.fetch_fixtures(d)
    for lg in fx.get("leagues", []) or []:
        for m in lg.get("matches", []) or []:
            h = (m.get("home") or {}).get("name", "")
            a = (m.get("away") or {}).get("name", "")
            for n in NAMES:
                if n.lower() in h.lower() or n.lower() in a.lower():
                    hits.append({"day": d.isoformat(), "league": lg.get("name"),
                                 "league_id": lg.get("primaryId") or lg.get("id"),
                                 "ccode": lg.get("ccode"),
                                 "home": h, "away": a, "id": m.get("id"),
                                 "time": (m.get("status") or {}).get("utcTime")})
                    break
    print(d, "competities:", len(fx.get("leagues", []) or []))

print("\ntreffers:", len(hits))
for x in hits:
    print(" ", json.dumps(x, ensure_ascii=False))
json.dump(hits, open("tmp-run/ra_oct06_fmprobe.json", "w"), ensure_ascii=False, indent=1)

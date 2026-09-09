"""Run B, 9 sep 2026 — Stage 1: de hele Fotmob-daglijst, om te zien wie er speelt."""
import json, sys
from datetime import date
sys.path.insert(0, ".")
from scripts import fotmob

DAY = date(2026, 9, 9)
fx = fotmob.fetch_fixtures(DAY)
rows = []
for lg in fx.get("leagues", []):
    rows.append((lg.get("ccode"), lg.get("name"), lg.get("primaryId") or lg.get("id"),
                 len(lg.get("matches", []))))
print("competities in de daglijst:", len(rows))
for r in sorted(rows):
    print(r)
json.dump(rows, open("tmp-run/rb9_fx.json", "w"), ensure_ascii=False, indent=1)

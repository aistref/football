import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob

day = date(2026,9,3)
fx = fotmob.fetch_fixtures(day)
leagues = fx.get("leagues", [])
print("total leagues today:", len(leagues))
out=[]
for lg in leagues:
    out.append((lg.get("ccode"), lg.get("name"), lg.get("primaryId") or lg.get("id"), len(lg.get("matches",[]))))
for o in sorted(out): print(o)

import sys
from datetime import date, timedelta
sys.path.insert(0,'.')
from scripts import fotmob
seen={}
d0=date(2026,9,2)
for k in range(-6, 6):
    d=d0+timedelta(days=k)
    try:
        fx=fotmob.fetch_fixtures(d)
    except Exception as e:
        continue
    for lg in fx.get("leagues",[]):
        if lg.get("ccode") in ("SUI","CZE"):
            seen[(lg.get("ccode"), lg.get("primaryId") or lg.get("id"), lg.get("name"))]=seen.get((lg.get("ccode"), lg.get("primaryId") or lg.get("id"), lg.get("name")),0)+len(lg.get("matches",[]))
for k,v in sorted(seen.items()): print(k,v)

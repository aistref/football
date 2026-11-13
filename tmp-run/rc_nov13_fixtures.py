import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed
DAY=date(2026,11,13)
out={}
for d in days_needed(DAY):
    fx=fotmob.fetch_fixtures(d)
    out[str(d)]=fx
    for lg in fx.get("leagues",[]):
        if lg.get("ccode") in ("INT",) or "Nations" in lg.get("name","") or lg.get("primaryId") in (114,10608,9876,329,13287):
            print(d, lg.get("primaryId"), lg.get("id"), lg.get("ccode"), lg.get("name"), len(lg.get("matches",[])))
json.dump(out,open("tmp-run/rc_nov13_fixtures.json","w"))

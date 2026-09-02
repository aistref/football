import sys, json
sys.path.insert(0,'.')
from scripts import squad
import json as J
M=J.load(open("tmp-run/matches.json"))
ids={}
for comp,blk in M.items():
    for m in blk["matches"]:
        if m["away"] in ("FC Vaduz","MK Dons"): ids[m["away"]]=m["away_id"]
        if m["home"]=="FC Zbrojovka Brno": ids[m["home"]]=m["home_id"]
print(ids)
for name,tid in ids.items():
    d=squad.fetch_team(tid)
    hist=d.get("history") or {}
    print("==",name,tid,"keys:",list(d.keys())[:12])
    tbl = (d.get("table") or [])
    for t in tbl[:3]:
        dd=t.get("data",{})
        print("   table:", dd.get("leagueId"), dd.get("leagueName") or dd.get("name"), dd.get("ccode"))
    if hist: print("   history keys:", list(hist.keys())[:8])
    ov=d.get("overview") or {}
    print("   overview keys:", list(ov.keys())[:12])

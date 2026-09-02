import json, sys
sys.path.insert(0,'.')
from scripts.oddsapi import CreditGuard, fetch_event_markets, best_by_line
API=json.load(open("tmp-run/odds_api.json")); M=json.load(open("tmp-run/matches.json"))
KEYS={"English League One (ENG)":"soccer_england_league1","Austrian Bundesliga (AUT)":"soccer_austria_bundesliga",
      "Swiss Super League (SUI)":"soccer_switzerland_superleague"}
guard=CreditGuard(cap=337)
out={}
for comp,blk in M.items():
    if comp not in KEYS: continue
    for m in blk["matches"]:
        k=m["utc"].replace(".000Z","Z")
        ev=next((e for e in API["spreads"][comp] if e.get("commence_time")==k and
                 (e["home_team"].split()[0].lower() in m["home"].lower() or m["home"].split()[0].lower() in e["home_team"].lower())), None)
        if not ev:
            print("geen event:", comp, m["home"], m["away"]); continue
        if not guard.can_afford(1): print("budget op"); break
        try:
            r=fetch_event_markets(KEYS[comp], ev["id"], ["btts"]); guard.record(r, f"btts {m['home']}")
            out[f"{m['home']} – {m['away']}"]=r.data
            bl=best_by_line(r.data,"btts")
            print(f"{m['home']} – {m['away']}: {dict((str(a),b) for a,b in bl.items())}")
        except Exception as e:
            out[f"{m['home']} – {m['away']}"]={"error":f"{type(e).__name__}: {e}"}
            print(f"{m['home']} – {m['away']}: FOUT {e}")
print("\n"+guard.report())
json.dump(out, open("tmp-run/btts.json","w"), ensure_ascii=False)

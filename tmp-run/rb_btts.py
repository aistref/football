import json, sys
sys.path.insert(0,'tmp-run')
from scripts.oddsapi import CreditGuard, fetch_event_markets
from rb_names import best_pair
od=json.load(open('tmp-run/rb_odds.json'))
cands=json.load(open('tmp-run/rb_cands.json'))
KEY={"Greek Super League (GRE)":"soccer_greece_super_league",
     "Segunda Division (ESP)":"soccer_spain_segunda_division",
     "Allsvenskan (SWE)":"soccer_sweden_allsvenskan"}
guard=CreditGuard(cap=200)
btts={}
for c in cands:
    if c['tier']=="NONE" or c['competition'] not in KEY: continue
    evs=od['spreads'].get(c['competition']) or []
    ev=best_pair(c['home'],c['away'],evs,lambda e:e['home_team'],lambda e:e['away_team'])
    if ev is None:
        print("geen event:",c['home'],c['away']); continue
    if not guard.can_afford(2): break
    r=fetch_event_markets(KEY[c['competition']], ev['id'], ["btts"])
    guard.record(r, c['competition'])
    p = r.payload if hasattr(r,'payload') else r.data
    btts[str(c['match_id'])]=p
    nb=len(p.get('bookmakers',[])) if isinstance(p,dict) else 0
    print(f"btts {c['home']} - {c['away']}: {nb} boeken")
json.dump(btts, open('tmp-run/rb_btts.json','w'), ensure_ascii=False)
print(guard.report())

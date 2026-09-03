import json, sys
sys.path.insert(0,'.')
from scripts.oddsapi import fetch_event_markets, CreditGuard
EV={"Mjällby – Djurgården":("soccer_sweden_allsvenskan","2d16ee5cd907cbe1b2eab60ba0e0ba6d"),
    "Basel – Sion":("soccer_switzerland_superleague","d8411659b081b0c0e51e0b41c1f5a6e0"),
    "Lugano – Servette":("soccer_switzerland_superleague","6ebd4679b6f7d09a1e1c60f9c4d0b0a0")}
d=json.load(open("tmp-run/b_oddsapi.json"))
full={}
for comp,evs in d["spreads"].items():
    for e in evs: full[e["id"][:12]]=(comp,e["id"])
MAP={"Mjällby – Djurgården":"2d16ee5cd907","Basel – Sion":"d8411659b081","Lugano – Servette":"6ebd4679b6f7"}
KEY={"Allsvenskan (SWE)":"soccer_sweden_allsvenskan","Swiss Super League (SUI)":"soccer_switzerland_superleague"}
guard=CreditGuard(cap=350)
out={}
for name,short in MAP.items():
    comp, eid = full[short]
    r=fetch_event_markets(KEY[comp], eid, ["btts"]); guard.record(r, name)
    out[name]=r.data
    best={}
    for b in (r.data or {}).get("bookmakers",[]):
        for m in b.get("markets",[]):
            if m.get("key")!="btts": continue
            for o in m.get("outcomes",[]):
                n=o["name"].lower()
                if n not in best or o["price"]>best[n][0]: best[n]=(o["price"],b["title"])
    print(name, best)
print(guard.report())
json.dump(out, open("tmp-run/b_btts.json","w"), ensure_ascii=False)

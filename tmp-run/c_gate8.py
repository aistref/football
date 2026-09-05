import json, sys
sys.path.insert(0,'.')
from scripts import sides
data = json.load(open("tmp-run/c_analysis.json"))
blocked=[]
for name, m in data.items():
    cands = m.get("candidates") or []
    o1x2 = m.get("odds_1x2")
    qualified=[]
    for c in cands:
        g=c.get("gates") or {}
        if not all(g.get(k, True) for k in ("edge","odds","tier","tweede_methode","robuustheid","context")):
            continue
        chk = sides.check(c.get("side"), o1x2)
        c["gate_underdog"]={"passed":chk.passed,"reason":chk.reason}
        (qualified if chk.passed else blocked).append(c if chk.passed else (name,c))
    win = max(qualified,key=lambda c:c["score"]) if qualified else None
    m["winner"]=win; m["bet"]=bool(win)
    m["runner_up"]=None
    if win:
        others=[c for c in qualified if c is not win]
        if others: m["runner_up"]=max(others,key=lambda c:c["score"])
print(f"{len(data)} wedstrijden, {len(blocked)} selectie(s) tegengehouden door poort 8")
for name,c in blocked:
    print(f"  POORT8  {name[:34]:36s} {c['market']} — {c['selection']} @ {c['odds']} (edge {c['edge_pp']:+.2f}, score {c['score']})")
print()
bets=[(n,m) for n,m in data.items() if m.get("winner")]
print(f"=== {len(bets)} BETS ===")
for n,m in sorted(bets,key=lambda x:-x[1]["winner"]["score"]):
    w=m["winner"]
    print(f"  {n[:34]:36s} {m['tier']:5s} {w['market']:15s} {w['selection'][:44]:46s} @ {w['odds']:5.2f} edge {w['edge_pp']:+6.2f} score {w['score']:6.2f}")
    if m["runner_up"]:
        r=m["runner_up"]; print(f"      2e: {r['market']} — {r['selection'][:40]} @ {r['odds']} score {r['score']}")
json.dump(data, open("tmp-run/c_analysis.json","w"), ensure_ascii=False, indent=1)

# --- near_miss per wedstrijd zonder bet (§5 "Net niet"): de sterkste kandidaat met een echte
# --- edge, met alle drie de cijfers erbij zodat zichtbaar is of het één poort was of een breed tekort.
GATE_ORDER=["odds","tier","edge","tweede_methode","robuustheid","context","underdog"]
for name,m in data.items():
    if m.get("winner") or m["tier"]=="NONE": continue
    cands=[c for c in (m.get("candidates") or []) if c["gates"]["odds"] and c["edge_pp"]>0]
    if not cands: continue
    best=max(cands,key=lambda c:c["edge_pp"])
    g=dict(best["gates"]); g["underdog"]=(best.get("gate_underdog") or {}).get("passed",True)
    failed=next((k for k in GATE_ORDER if not g.get(k,True)), None)
    m["near_miss"]={"market":f'{best["market"]} — {best["selection"]}',"odds":best["odds"],
                    "edge_xg":best["edge_xg"],"edge_split":best["edge_split"],
                    "edge_robust_min":best["edge_robust_min"],"failed_gate":failed,
                    "edge_pp":best["edge_pp"],"side":best["side"]}
json.dump(data, open("tmp-run/c_analysis.json","w"), ensure_ascii=False, indent=1)
nm=[(n,m["near_miss"]) for n,m in data.items() if m.get("near_miss")]
print(f"\n=== NET NIET ({len(nm)}) ===")
for n,x in sorted(nm,key=lambda t:-t[1]["edge_pp"]):
    print(f'  {n[:34]:36s} {x["market"][:46]:48s} @ {x["odds"]:5.2f}  xG {x["edge_xg"]:+6.2f}  2e {x["edge_split"]:+6.2f}  '
          f'zwakst {str(x["edge_robust_min"]):>7}  valt af op {x["failed_gate"]}')

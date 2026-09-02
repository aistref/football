import json, sys
sys.path.insert(0,'.')
from scripts.model import selection_score
A=json.load(open("tmp-run/analysis.json"))
bets=[]; nearmiss=[]
for k,r in A.items():
    if r.get("tier")=="NONE": continue
    cs=r["candidates"]
    ok=[c for c in cs if all(c["gates"].values())]
    for c in cs: c["score"]=round(selection_score(c["edge_pp"], c["my_prob"], r["tier"]),2) if c["edge_pp"]>0 else 0.0
    if ok:
        ok.sort(key=lambda c: -selection_score(c["edge_pp"], c["my_prob"], r["tier"]))
        win=ok[0]; win["score"]=round(selection_score(win["edge_pp"],win["my_prob"],r["tier"]),2)
        second = ok[1] if len(ok)>1 else None
        rest=[c for c in cs if c is not win]
        rest.sort(key=lambda c:-c["score"])
        r["bet"]=True; r["winner"]=win
        r["second"]= second or (rest[0] if rest else None)
        r["second_qualified"]=bool(second)
        bets.append((k,r,win))
    else:
        pos=[c for c in cs if c["edge_pp"]>0]
        if pos:
            best=max(pos,key=lambda c:c["edge_pp"])
            failed=[g for g,v in best["gates"].items() if not v]
            order=["data","odds","tweede_methode","robuustheid","context","edge"]
            fmap={"tier":"data","odds":"odds","tweede_methode":"tweede_methode","robuustheid":"robuustheid","context":"context","edge":"edge"}
            fl=[fmap[f] for f in failed]
            first=next((o for o in order if o in fl), "edge")
            r["near_miss"]={"market":f"{best['market']} — {best['selection']}","odds":best["odds"],
                "edge_xg":best["edge_xg"],"edge_split":best["edge_split"],
                "edge_robust_min":best["edge_robust_min"],"edge_avg":best["edge_pp"],
                "failed_gate":first,"all_failed":fl}
            nearmiss.append((k,r,best,first))
        else:
            r["near_miss"]=None
json.dump(A, open("tmp-run/analysis.json","w"), ensure_ascii=False, indent=1)
print("=== BETS ===")
for k,r,w in sorted(bets,key=lambda x:-x[2]["score"]):
    print(f"{w['score']:6.2f}  {k}  [{r['tier']}]  {w['market']} — {w['selection']} @ {w['odds']} ({w['odds_source']})")
    print(f"        my {w['my_prob']*100:.1f}% impl {w['implied']*100:.1f}% edge {w['edge_pp']:+.2f} | xg {w['edge_xg']:+.2f} sp {w['edge_split']:+.2f} rob {w['edge_robust_min']:+.2f}")
    s=r.get("second")
    print(f"        tweede: {(s['market']+' — '+s['selection']+' score '+str(s['score'])) if s else 'geen'} ({'gekwalificeerd' if r.get('second_qualified') else 'haalde niet alle poorten'})")
print("\n=== NET NIET ===")
for k,r,b,f in nearmiss:
    print(f"{k[:36]:38s} {b['market'][:14]:15s} {b['selection'][:30]:32s} @{b['odds']:<5} xg {b['edge_xg']:+6.2f} sp {b['edge_split']:+6.2f} rob {str(b['edge_robust_min']):>7}  valt af op {f}")
print("\nbets:",len(bets)," near-miss:",len(nearmiss))

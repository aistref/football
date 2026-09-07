"""Controle op de vroeg-seizoenscorrectie: model tegen markt op P(Over 2.5), vóór en ná.

Meten tegen de markt mag hier — dat is controleren of de correctie werkt, niet fitten (§3 Stage 5).
"""
import json, sys, statistics as S
sys.path.insert(0, "tmp-run")
from scripts import oddsapi
from ra_names import resolve, best_pair

res = json.load(open("tmp-run/rb7_results.json"))
odds = json.load(open("tmp-run/rb7_odds.json"))

rows = []
for m in res["matches"]:
    if m["tier"] == "NONE":
        continue
    evs = (odds["raw"].get("totals") or {}).get(m["competition"]) or []
    ev = None
    for e in evs:
        if resolve(m["home"], {e["home_team"]: 1}) and resolve(m["away"], {e["away_team"]: 1}):
            ev = e; break
    if ev is None:
        ev = best_pair(m["home"], m["away"], evs, lambda e: e["home_team"], lambda e: e["away_team"])
    if ev is None:
        continue
    lines = oddsapi.best_by_line(ev, "totals")
    over = next((v for (o, l), v in lines.items() if o.lower() == "over" and abs(float(l) - 2.5) < 1e-9), None)
    under = next((v for (o, l), v in lines.items() if o.lower() == "under" and abs(float(l) - 2.5) < 1e-9), None)
    if not (over and under):
        continue
    po, pu = 1 / over[0], 1 / under[0]
    mkt = po / (po + pu)                       # de-vigd
    cand = next((c for c in m["all_candidates"]
                 if c["market"] == "Over/Under" and c["selection"].lower().startswith("over 2.5")), None)
    if cand is None:
        continue
    rows.append((m["match"], cand["p_xg"], mkt))

if rows:
    d = [(a - b) * 100 for _, a, b in rows]
    print(f"n = {len(rows)} duels met een O/U 2.5-lijn")
    print(f"gemiddelde afwijking model - markt op P(Over 2.5): {S.mean(d):+.2f} pp")
    print(f"gemiddelde ABSOLUTE afwijking: {S.mean([abs(x) for x in d]):.2f} pp")
    print(f"aantal keer boven de markt: {sum(x > 0 for x in d)} van {len(d)}")
    for (naam, a, b), x in zip(rows, d):
        print(f"  {naam[:36]:36s} model {a*100:5.1f}%  markt {b*100:5.1f}%  {x:+6.2f} pp")
else:
    print("geen enkel duel met een O/U 2.5-lijn")

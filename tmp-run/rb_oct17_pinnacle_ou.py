"""Stage 5 stap 2, doelpuntenkant — het Pinnacle-oordeel over de TOTALEN, niet over 1X2.

`rb_oct17_pinnacle.py` zet het eigen 1X2 naast Pinnacle's de-vigde 1X2. Dat is het beste
publieke expertoordeel over WIE er wint, en vandaag is de enige gepubliceerde regel een Under —
dus een markt waar die vergelijking niets over zegt.

§6g eist bij een gepubliceerde Under uitdrukkelijk dat erbij staat dat deze kant meetbaar scheef
staat. Dit script levert daar het onafhankelijke cijfer bij: Pinnacle's eigen Over/Under-lijnen,
per lijn de-vigd, naast de eigen kans uit hetzelfde scoregrid. Pinnacle heeft een marge van 3 tot
5% tegen 6 tot 10% bij de rest, dus een verschil tegen Pinnacle is een strengere toets dan een
verschil tegen de aanbieder waar de bet staat.

HARDE GRENS (§2 / §4): dit getal gaat niet in `my_prob` en niet in `prob_sources`. Het is
marktafgeleid en hoort in de vergelijking.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import model
from ra_names import resolve

odds = json.load(open("tmp-run/rb_oct17_odds.json"))
res = json.load(open("tmp-run/rb_oct17_results.json"))
grids = {m["match"]: m for m in res["matches"]}

# Pinnacle's totals per event, per lijn: {lijn: (over, under)}
pin = {}
for comp, events in (odds["raw"].get("totals") or {}).items():
    for e in events:
        for bm in e.get("bookmakers", []):
            if bm.get("key") != "pinnacle":
                continue
            for mk in bm.get("markets", []):
                if mk.get("key") != "totals":
                    continue
                per = {}
                for o in mk.get("outcomes", []):
                    pt = o.get("point")
                    if pt is None:
                        continue
                    per.setdefault(float(pt), {})[o["name"].lower()] = o["price"]
                if per:
                    pin[(e["home_team"], e["away_team"])] = per

print(f"Pinnacle-totalen gevonden voor {len(pin)} events\n")

rows = []
for m in res["matches"]:
    per = None
    for (h, a), v in pin.items():
        if resolve(m["home"], {h: 1}) and resolve(m["away"], {a: 1}):
            per = v
            break
    if not per:
        continue
    lam = (m.get("lambdas") or {}).get("xg")
    if not lam:
        continue
    grid = model.analyze_match.__wrapped__ if False else None
    # Het scoregrid zelf staat niet in het resultaatbestand; de twee lambdas wel. P(Under L) uit
    # een onafhankelijk Poisson-grid op diezelfde lambdas is de eigen kans op de xG-arm, en dat
    # is exact de grootheid die `totals_prob` ook gebruikt (rho raakt alleen de lage standen).
    import math
    lh, la = lam
    P = [[math.exp(-lh) * lh**i / math.factorial(i) * math.exp(-la) * la**j / math.factorial(j)
          for j in range(12)] for i in range(12)]
    for lijn, prijzen in sorted(per.items()):
        if "over" not in prijzen or "under" not in prijzen:
            continue
        o, u = prijzen["over"], prijzen["under"]
        vig = 1 / o + 1 / u
        pin_under = (1 / u) / vig
        mijn_under = sum(P[i][j] for i in range(12) for j in range(12) if i + j < lijn)
        rows.append({"match": m["match"], "lijn": lijn, "pin_over": o, "pin_under": u,
                     "marge_pct": round((vig - 1) * 100, 2),
                     "pin_under_devig": round(pin_under, 4),
                     "mijn_under_xg": round(mijn_under, 4),
                     "verschil_pp": round((mijn_under - pin_under) * 100, 2)})
        print(f"{m['match'][:28]:28s} lijn {lijn:4.2f}  Pinnacle {o:5.2f}/{u:5.2f} "
              f"(marge {(vig-1)*100:4.1f}%)  P(Under) Pinnacle {pin_under:.3f} / eigen "
              f"{mijn_under:.3f}  verschil {(mijn_under-pin_under)*100:+6.2f} pp")

json.dump(rows, open("tmp-run/rb_oct17_pinnacle_ou.json", "w"), ensure_ascii=False, indent=1)
if rows:
    import statistics as S
    print(f"\n{len(rows)} (duel, lijn)-paren · gemiddeld verschil op de Under-kant "
          f"{S.mean([r['verschil_pp'] for r in rows]):+.2f} pp · "
          f"{sum(1 for r in rows if r['verschil_pp'] > 0)} van {len(rows)} boven Pinnacle")

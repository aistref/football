"""Wat de reparatie met ALLE ZES de markten doet — de eis die §6g er zelf bij zet.

> *"Het is wel een ingreep in `score_grid` zelf en raakt élke markt, niet alleen Unders — reken
> dus eerst door wat het met de andere vijf doet."*

De tilt werkt per anti-diagonaal en laat de verdeling van het DOELSALDO GEGEVEN het totaal exact
zoals ze was. Dat betekent niet dat de andere markten ongemoeid blijven: anti-diagonalen hebben
verschillende saldoprofielen (totaal 0 is altijd een gelijkspel, totaal 1 nooit), dus wie massa
van 2 naar 4 schuift, verandert ook P(gelijkspel). Precies dat wordt hier gemeten.

Alles op de TOETSHELFT — de tweede helft van de periode, die bij het fitten geen rol speelde.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import model

MAXG = model.MAX_GOALS
B = json.loads(Path("tmp-run/grid_fit_result.json").read_text())["b_train"]


def tilted_grid(lh, la, b):
    g = model.score_grid(lh, la)
    if b == 0.0:
        return g
    mu = lh + la
    out = [[0.0] * (MAXG + 1) for _ in range(MAXG + 1)]
    z = 0.0
    for i in range(MAXG + 1):
        for j in range(MAXG + 1):
            d = (i + j) - mu
            v = g[i][j] * math.exp(b * d * d)
            out[i][j] = v
            z += v
    return [[v / z for v in r] for r in out]


def markets(g):
    """Alle zes de markten uit één grid, als kansen."""
    home = draw = away = btts = 0.0
    tot = [0.0] * (2 * MAXG + 1)
    for i, row in enumerate(g):
        for j, p in enumerate(row):
            tot[i + j] += p
            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p
            if i >= 1 and j >= 1:
                btts += p
    m = {"1": home, "X": draw, "2": away,
         "1X": home + draw, "X2": draw + away, "12": home + away,
         "BTTS ja": btts, "BTTS nee": 1 - btts}
    for line in (1.5, 2.5, 3.5):
        m[f"Under {line}"] = sum(tot[t] for t in range(len(tot)) if t < line)
    # Draw No Bet: winkans gegeven dat het gelijkspel wordt teruggegeven
    m["DNB thuis"] = home / (home + away) if home + away else 0.0
    # Asian Handicap, hele en halve lijnen, vanaf de thuiskant
    for h in (-1.5, -0.5, 0.5, 1.5):
        w = sum(p for i, row in enumerate(g) for j, p in enumerate(row) if (i - j) + h > 0)
        m[f"AH thuis {h:+}"] = w
    # AH 0.0 (= DNB) met push apart
    m["AH thuis 0.0 push"] = draw
    return m


def realised(r):
    hg, ag = r["hg"], r["ag"]
    t = hg + ag
    out = {"1": hg > ag, "X": hg == ag, "2": hg < ag,
           "1X": hg >= ag, "X2": hg <= ag, "12": hg != ag,
           "BTTS ja": hg >= 1 and ag >= 1, "BTTS nee": not (hg >= 1 and ag >= 1)}
    for line in (1.5, 2.5, 3.5):
        out[f"Under {line}"] = t < line
    out["DNB thuis"] = None if hg == ag else hg > ag
    for h in (-1.5, -0.5, 0.5, 1.5):
        out[f"AH thuis {h:+}"] = (hg - ag) + h > 0
    out["AH thuis 0.0 push"] = hg == ag
    return out


def main():
    rows = sorted(json.loads(Path("tmp-run/grid_data.json").read_text()),
                  key=lambda r: (r["date"], r["match"]))
    te = rows[len(rows) // 2:]
    print(f"TOETSHELFT: {len(te)} duels, {te[0]['date']} t/m {te[-1]['date']}")
    print(f"tilt b = {B:+.5f} (gefit op de EERSTE helft)\n")

    keys = list(markets(model.score_grid(1.4, 1.2)).keys())
    acc = {k: {"p0": 0.0, "p1": 0.0, "act": 0.0, "n": 0,
               "br0": 0.0, "br1": 0.0} for k in keys}
    ll0 = ll1 = 0.0
    for r in te:
        lh, la = r["lam"]
        g0 = tilted_grid(lh, la, 0.0)
        g1 = tilted_grid(lh, la, B)
        m0, m1 = markets(g0), markets(g1)
        act = realised(r)
        # multiclass log loss op 1X2
        for k, lab in (("1", "1"), ("X", "X"), ("2", "2")):
            if act[lab]:
                ll0 -= math.log(max(m0[k], 1e-12))
                ll1 -= math.log(max(m1[k], 1e-12))
        for k in keys:
            a = act[k]
            if a is None:
                continue
            A = acc[k]
            A["p0"] += m0[k]; A["p1"] += m1[k]; A["act"] += 1.0 if a else 0.0
            A["br0"] += (m0[k] - (1.0 if a else 0.0)) ** 2
            A["br1"] += (m1[k] - (1.0 if a else 0.0)) ** 2
            A["n"] += 1

    print(f"{'markt / selectie':22s} {'n':>5} {'huidig':>8} {'na fix':>8} {'werkelijk':>10} "
          f"{'fout nu':>9} {'fout na':>9} {'Brier Δ':>9}")
    print("-" * 92)
    order = ["1", "X", "2", "1X", "X2", "12", "DNB thuis",
             "AH thuis -1.5", "AH thuis -0.5", "AH thuis +0.5", "AH thuis +1.5",
             "AH thuis 0.0 push",
             "Under 1.5", "Under 2.5", "Under 3.5", "BTTS ja", "BTTS nee"]
    for k in order:
        A = acc[k]
        n = A["n"]
        p0, p1, ac = 100 * A["p0"] / n, 100 * A["p1"] / n, 100 * A["act"] / n
        d0, d1 = ac - p0, ac - p1
        dbr = (A["br1"] - A["br0"]) / n
        beter = "beter" if abs(d1) < abs(d0) else ("slechter" if abs(d1) > abs(d0) else "gelijk")
        print(f"{k:22s} {n:5d} {p0:7.2f}% {p1:7.2f}% {ac:9.2f}% "
              f"{d0:+8.2f} {d1:+8.2f} {dbr:+9.5f}  {beter}")

    print("\n1X2 multiclass log loss (lager is beter):")
    print(f"  huidig grid {ll0/len(te):.5f}   na de fix {ll1/len(te):.5f}   "
          f"({(ll0-ll1)/len(te):+.5f})")

    verbeterd = sum(1 for k in order
                    if abs(acc[k]['act'] / acc[k]['n'] - acc[k]['p1'] / acc[k]['n'])
                    < abs(acc[k]['act'] / acc[k]['n'] - acc[k]['p0'] / acc[k]['n']))
    print(f"\nKalibratie verbeterd op {verbeterd} van de {len(order)} gemeten selecties.")
    brier_beter = sum(1 for k in order if acc[k]["br1"] < acc[k]["br0"])
    print(f"Brier verbeterd op {brier_beter} van de {len(order)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

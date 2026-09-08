"""Controles op de inter-competitiemeting vóórdat er iets van in productie gaat.

Vier vragen, in volgorde van belang:
  1. Houdt de winst stand als je alleen naar duels kijkt die NIET door een tweeluik zijn
     vervuild (returns waarin een ploeg een stand verdedigt of moet jagen)?
  2. Vanaf hoeveel waarnemingen is de factor van een competitie te vertrouwen? Dat bepaalt de
     poort, net als `conversion_in_range` bij promotion.py.
  3. Is de factor STABIEL? Een factor die per periode heen en weer springt beschrijft ruis.
  4. Wat zegt het model over de wedstrijden van vandaag, naast de markt? Meten tegen de markt
     om te CONTROLEREN mag (§2/§6e); fitten erop niet.
"""
import json, math, sys
from collections import defaultdict
sys.path.insert(0, ".")
sys.path.insert(0, "tmp-run")
from il_fit import fit, evaluate, fold, build_rows, PRIORS

PRIOR = 5.0


def spearman(xs, ys):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        for pos, i in enumerate(order):
            r[i] = pos
        return r
    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else 0.0


def main() -> int:
    cross = json.load(open("tmp-run/il_rows.json"))
    seasons = sorted({r["season"] for r in cross})
    final = seasons[-1]
    train = [r for r in cross if r["season"] < final]
    test = [r for r in cross if r["season"] == final]
    f = fit(train, prior=PRIOR)
    base_hw = (sum(r["hg"] for r in train) / len(train), sum(r["ag"] for r in train) / len(train))

    # ---------- 1. per soort wedstrijd ----------
    print("=== 1. houdt de winst stand per soort wedstrijd? (uit-steekproef 2025/2026) ===")
    print(f"  {'groep':34s} {'n':>5s} {'Brier zonder':>13s} {'Brier met':>10s} {'verschil':>10s}")
    groups = {"alles": test,
              "league phase / groepsfase": [r for r in test if isinstance(r["round"], int)],
              "knock-out en voorrondes": [r for r in test if not isinstance(r["round"], int)],
              "Champions League": [r for r in test if "Champions" in r["competition"]],
              "Europa League": [r for r in test if "Europa League" in r["competition"]],
              "Conference League": [r for r in test if "Conference" in r["competition"]]}
    for name, rows in groups.items():
        if len(rows) < 25:
            print(f"  {name:34s} {len(rows):5d}  te weinig")
            continue
        b = evaluate(rows, None, base_hw)
        m = evaluate(rows, f)
        print(f"  {name:34s} {len(rows):5d} {b['brier']:13.5f} {m['brier']:10.5f} "
              f"{m['brier'] - b['brier']:+10.5f}")

    # ---------- 2. vanaf hoeveel waarnemingen is een factor te vertrouwen? ----------
    print("\n=== 2. poortdrempel: minimaal aantal Europese duels per competitie ===")
    n_per = f["n_per_league"]
    print(f"  {'drempel':>8s} {'testduels':>10s} {'Brier zonder':>13s} {'Brier met':>10s} {'verschil':>10s}")
    for thr in (0, 10, 20, 30, 40, 60, 80, 120):
        rows = [r for r in test
                if n_per.get(r["cc_home"], 0) >= thr and n_per.get(r["cc_away"], 0) >= thr]
        if len(rows) < 25:
            print(f"  {thr:8d} {len(rows):10d}  te weinig om te lezen")
            continue
        b = evaluate(rows, None, base_hw)
        m = evaluate(rows, f)
        print(f"  {thr:8d} {len(rows):10d} {b['brier']:13.5f} {m['brier']:10.5f} "
              f"{m['brier'] - b['brier']:+10.5f}")

    # ---------- 3. stabiliteit ----------
    print("\n=== 3. is de factor stabiel over de tijd? ===")
    early = [r for r in cross if r["season"] in seasons[:2]]
    late = [r for r in cross if r["season"] in seasons[-2:]]
    fe, fl = fit(early, prior=PRIOR), fit(late, prior=PRIOR)
    ne, nl = fe["n_per_league"], fl["n_per_league"]
    shared = sorted(set(fe["A"]) & set(fl["A"]), key=lambda c: -(fe["A"][c] / fe["D"][c]))
    for thr in (0, 20, 40):
        cs = [c for c in shared if min(ne.get(c, 0), nl.get(c, 0)) >= thr]
        if len(cs) < 5:
            continue
        xs = [fe["A"][c] / fe["D"][c] for c in cs]
        ys = [fl["A"][c] / fl["D"][c] for c in cs]
        rho = spearman(xs, ys)
        mad = sum(abs(math.log(a) - math.log(b)) for a, b in zip(xs, ys)) / len(cs)
        print(f"  competities met >= {thr:3d} duels in BEIDE perioden: {len(cs):2d}   "
              f"Spearman {rho:+.3f}   mediane log-afwijking {mad:.3f} "
              f"(= factor {math.exp(mad):.2f}x)")
    print(f"  {'cc':4s} {'2021-2023':>10s} {'2024-2026':>10s}   (sterkte-index A/D)")
    for c in shared:
        if min(ne.get(c, 0), nl.get(c, 0)) >= 40:
            print(f"  {c:4s} {fe['A'][c] / fe['D'][c]:10.3f} {fl['A'][c] / fl['D'][c]:10.3f}"
                  f"   n={ne.get(c,0)}/{nl.get(c,0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

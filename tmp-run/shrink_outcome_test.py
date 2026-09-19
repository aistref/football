"""19 sep 2026 — beantwoordt de openstaande spanning van §6e op UITSLAGEN.

De vraag: `shrink` trekt ploegsterktes naar het competitiegemiddelde, en dat maakt ploegen
onderling gelijker — precies de rekenstap waarvan de docstring van `team_strength` zegt dat hij
"de underdog meer kans geeft dan hij verdient". Op 3 sep is `shrink=0.8` op Brier-score gemeten
en goed bevonden, maar dat was een backtest over álle duels in vijf grote competities in één
seizoen. Deze routine speelt iets anders: 21 competities, veel omgerekende promovendi, vroeg
seizoen, en ze kiest juist de staart waar ze het meest van de markt afwijkt.

Dit script meet `shrink=0.8` tegen `shrink=1.0` op de 782 wedstrijden die de routine ZELF heeft
doorgerekend, tegen de werkelijke uitslag. Het kalibratielogboek bewaart beide kansen al per
wedstrijd (`p_xg` = standaard-shrink, `p_xg_noshrink` = 1.0), dus er hoeft niets opnieuw te
worden gemodelleerd; alleen de uitslagen komen erbij, via `settling.DayIndex` (één Fotmob-verzoek
per kalenderdag, geen credits).

Dit is een meting tegen UITKOMSTEN, niet tegen de markt: de marktkans wordt alleen gebruikt om
de bakken te maken, niet om iets op af te regelen. Dat is wat §6e "controleren, niet fitten"
noemt, en het is het onderscheid waarop de ingetrokken correctie van 31 aug sneuvelde.

Draaien: PYTHONPATH=. python3 tmp-run/shrink_outcome_test.py
"""
import json, math, collections
from datetime import date
from scripts.settling import DayIndex

OUT = "tmp-run/shrink_outcome_test.json"
KEYS = ("thuis", "gelijk", "uit")


def load_with_results():
    rows = [json.loads(l) for l in open("data/calibration.jsonl") if l.strip()]
    per = collections.defaultdict(dict)
    for r in rows:
        per[(r["date"], r["match"])][r["outcome"]] = r
    idx, out, miss = DayIndex(), [], 0
    for (d, match), o in per.items():
        if set(o) != set(KEYS) or " – " not in match:
            continue
        home, away = match.split(" – ", 1)
        hit = idx.lookup(date.fromisoformat(d), home, away)
        if not hit or not hit.get("finished") or not hit.get("score"):
            miss += 1
            continue
        try:
            hg, ag = [int(x) for x in hit["score"].replace("−", "-").split("-")]
        except Exception:
            miss += 1
            continue
        out.append({"date": d, "match": match, "tier": o["thuis"]["tier"],
                    "res": "thuis" if hg > ag else ("uit" if ag > hg else "gelijk"),
                    "m": {k: o[k]["market"] for k in KEYS},
                    "s08": {k: o[k]["p_xg"] for k in KEYS},
                    "s10": {k: o[k]["p_xg_noshrink"] for k in KEYS}})
    return out, miss


def brier_one(r, key):
    return sum((r[key][k] - (1.0 if r["res"] == k else 0.0)) ** 2 for k in KEYS)


def report(rs, label):
    n = len(rs)
    wins = sum(1 for r in rs if brier_one(r, "s08") > brier_one(r, "s10"))
    z = (wins - n / 2) / math.sqrt(n * 0.25)
    obs = [(r, k) for r in rs for k in KEYS if r["m"][k] < 0.25]
    act = sum(1 for r, k in obs if r["res"] == k) / len(obs)
    p8 = sum(r["s08"][k] for r, k in obs) / len(obs)
    p10 = sum(r["s10"][k] for r, k in obs) / len(obs)
    print(f"  {label:22s} n={n:4d}  shrink 1.0 beter in {wins:3d} ({wins/n*100:4.1f}%, "
          f"z={z:+.2f})  | longshotfout 0.8: {(p8-act)*100:+5.2f} pp  1.0: {(p10-act)*100:+5.2f} pp")


def main():
    out, miss = load_with_results()
    json.dump(out, open(OUT, "w"))
    print(f"wedstrijden met uitslag: {len(out)}  (niet gevonden / niet afgelopen: {miss})\n")

    print("=== 1X2-Brier over de wedstrijden die de routine zelf heeft doorgerekend ===")
    for lab, k in (("shrink 0.8 (was)", "s08"), ("shrink 1.0 (nu)", "s10")):
        print(f"  {lab:20s} {sum(brier_one(r, k) for r in out)/len(out):9.5f}")
    diff = [brier_one(r, "s08") - brier_one(r, "s10") for r in out]
    n = len(diff); mu = sum(diff) / n
    sd = math.sqrt(sum((d - mu) ** 2 for d in diff) / (n - 1))
    print(f"  gepaard verschil (0.8 - 1.0): {mu:+.5f}   t = {mu/(sd/math.sqrt(n)):+.2f}")

    print("\n=== Kansschatting tegen WERKELIJKE uitkomsten, per marktbak ===")
    print(f"{'marktbak':>12s} {'n':>5s} {'werkelijk':>10s} {'shrink 0.8':>11s} {'shrink 1.0':>11s} {'winst':>9s}")
    tot8 = tot10 = 0.0
    for lab, lo, hi in [("<15%", 0, .15), ("15-25%", .15, .25), ("25-35%", .25, .35),
                        ("35-50%", .35, .50), ("50-65%", .50, .65), (">=65%", .65, 1.01)]:
        obs = [(r, k) for r in out for k in KEYS if lo <= r["m"][k] < hi]
        if not obs:
            continue
        m = len(obs)
        act = sum(1 for r, k in obs if r["res"] == k) / m
        p8 = sum(r["s08"][k] for r, k in obs) / m
        p10 = sum(r["s10"][k] for r, k in obs) / m
        b8, b10 = abs(p8 - act) * 100, abs(p10 - act) * 100
        tot8 += b8 * m; tot10 += b10 * m
        print(f"{lab:>12s} {m:5d} {act*100:9.1f}% {p8*100:10.1f}% {p10*100:10.1f}% {b8-b10:+8.2f} pp")
    N = len(out) * 3
    print(f"\n  gewogen gemiddelde kalibratiefout: 0.8 = {tot8/N:.2f} pp, 1.0 = {tot10/N:.2f} pp")

    print("\n=== Uit-steekproefcontrole en uitsplitsing ===")
    ds = sorted({r["date"] for r in out}); mid = ds[len(ds) // 2]
    report([r for r in out if r["date"] < mid], f"t/m {mid}")
    report([r for r in out if r["date"] >= mid], f"vanaf {mid}")
    for t in ("FULL", "LIGHT"):
        report([r for r in out if r["tier"] == t], t)
    report(out, "hele periode")


if __name__ == "__main__":
    main()

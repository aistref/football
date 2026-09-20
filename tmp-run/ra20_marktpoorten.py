"""Hoeveel komt er per markt door de poorten? — nagerekend op verzoek van de gebruiker, 20 sep 2026.

Aanleiding: de vijf bets van vandaag zijn alle vijf een doelpuntenmarkt, en de vraag was of dat
toeval is. Het runrapport schreef het toe aan "de drie kantgebonden poorten (5, 7, 8), samen 846
keer dicht". Dat is fout op één punt en dat punt is precies het interessante: **poort 5 is niet
kantgebonden.** Hij sluit op elke markt ongeveer even hard. De scheefheid komt volledig van poort
7 en 8, en die twee staan bij `side = None` per definitie open (§1c).

Twee valkuilen die bij de eerste poging allebei misgingen, en die de uitkomst omkeerden:

1. **`poorten["robuustheid"]` is `None` voor 631 van de 689 selecties**, niet `False`. Poort 6
   draait alleen boven de NEAR-drempel. Wie `all(v is True ...)` schrijft, telt die `None` als
   dicht en meet dan de NEAR-drempel in plaats van de poorten.
2. **Tellen over álle selecties vertekent.** Onder de NEAR-drempel doet een selectie sowieso niet
   mee aan §5b. De juiste noemer is "kandidaten boven de ondergrens", en dan pas is de
   slaagkans per markt vergelijkbaar.

Draai: `PYTHONPATH=. python3 tmp-run/ra20_marktpoorten.py [datum run ...]`
"""
import json
import sys
from collections import Counter
from datetime import date

from scripts import toplist

# De vier markten waarin je een KANT speelt. Poort 7 (context) en poort 8 (underdog) kunnen
# alleen hier sluiten; bij Over/Under en BTTS is `side = None` en staan ze altijd open (§1c, §1e).
KANT = {"1X2", "Asian Handicap", "Draw No Bet", "Double Chance"}
NEAR = {"FULL": 3.0, "LIGHT": 6.0}          # de ondergrens van §5b, zie toplist.NEAR


def dicht(poorten, negeer):
    """Welke poorten staan aantoonbaar DICHT? `None` = niet geëvalueerd, dus niet dicht."""
    return [k for k, v in poorten.items() if v is False and k not in negeer]


def meet(state):
    """Per marktsoort: aanbod boven de ondergrens, en wat daarvan door de poorten komt."""
    n, nu, zonder8, zonder78 = Counter(), Counter(), Counter(), Counter()
    per_markt = {}
    for c in toplist._rows(state):
        tier = c["tier"]
        edge = c.get("edge_pp")
        if not isinstance(edge, (int, float)) or edge < NEAR.get(tier, 3.0):
            continue                                    # doet niet mee aan §5b
        p = c.get("poorten")
        if not isinstance(p, dict):
            continue
        soort = "kant" if c["market"] in KANT else "doelpunten"
        rij = per_markt.setdefault(c["market"], Counter())
        for teller, negeer in ((n, None), (nu, {"edge"}),
                               (zonder8, {"edge", "underdog"}),
                               (zonder78, {"edge", "underdog", "context"})):
            if negeer is None:
                teller[soort] += 1
                rij["n"] += 1
            elif not dicht(p, negeer):
                teller[soort] += 1
                rij["door" if negeer == {"edge"} else
                    ("zonder8" if "context" not in negeer else "zonder78")] += 1
        for k in dicht(p, {"edge"}):
            rij[f"dicht_{k}"] += 1
    return n, nu, zonder8, zonder78, per_markt


def toon(label, state):
    n, nu, z8, z78, per_markt = meet(state)
    print(f"\n=== {label} ===")
    print(f"{'':14s}{'kandidaten':>11s}{'door':>7s}{'slaagkans':>11s}"
          f"{'zonder p8':>11s}{'zonder p7+8':>13s}")
    for soort in ("kant", "doelpunten"):
        if not n[soort]:
            continue
        print(f"{soort:14s}{n[soort]:11d}{nu[soort]:7d}{nu[soort]/n[soort]*100:10.1f}%"
              f"{z8[soort]:11d}{z78[soort]:13d}")
    print(f"  per markt (kandidaten boven de ondergrens -> door alle poorten):")
    for mk, r in sorted(per_markt.items(), key=lambda x: -x[1]["n"]):
        soort = "KANT" if mk in KANT else "DOEL"
        redenen = {k[6:]: v for k, v in r.items() if k.startswith("dicht_")}
        top = ", ".join(f"{k} {v}" for k, v in sorted(redenen.items(), key=lambda x: -x[1])[:3])
        print(f"    [{soort}] {mk:16s} {r['n']:3d} -> {r['door']:3d}"
              f" ({r['door']/r['n']*100:5.1f}%)   dicht: {top}")
    return n, nu, z8, z78


if __name__ == "__main__":
    args = sys.argv[1:] or ["2026-09-20", "a", "2026-09-19", "a", "2026-09-19", "b",
                            "2026-09-18", "a", "2026-09-18", "b"]
    totaal = [Counter(), Counter(), Counter(), Counter()]
    for dag, run in zip(args[::2], args[1::2]):
        try:
            st = toplist.load(run, date.fromisoformat(dag))
        except FileNotFoundError:
            print(f"\n=== {dag} run {run.upper()} === geen voortgangsbestand")
            continue
        for teller, deel in zip(totaal, toon(f"{dag} run {run.upper()}", st)):
            teller.update(deel)
    n, nu, z8, z78 = totaal
    print(f"\n=== ALLE DAGEN SAMEN ===")
    print(f"{'':14s}{'kandidaten':>11s}{'door':>7s}{'slaagkans':>11s}"
          f"{'zonder p8':>11s}{'zonder p7+8':>13s}")
    for soort in ("kant", "doelpunten"):
        if n[soort]:
            print(f"{soort:14s}{n[soort]:11d}{nu[soort]:7d}{nu[soort]/n[soort]*100:10.1f}%"
                  f"{z8[soort]:11d}{z78[soort]:13d}")

#!/usr/bin/env python3
"""Klopt de vórm van de uitslagenverdeling, en niet alleen wie er wint?

`calibration.py` meet of `my_prob` scheef staat op de 1X2-uitkomsten. `ledger.py` en `shadow.py`
meten of de bets winnen. Geen van drieën beantwoordt de vraag die op 19 sep 2026 door de gebruiker
werd gesteld, en die vraag ging over de handicapmarkt:

    "Je bet voor Barcelona (en Bayern gisteren) verraadt eigenlijk de manier waarop je naar
     voetbal kijkt. Op dit moment zijn Barcelona en Bayern echt niet te stoppen. Je hebt meerdere
     handicap-bets voorgesteld. Ik heb het idee dat je rekenmodel nog te simpel is: niet wat valt
     er te halen uit alle markten rondom zo'n wedstrijd, maar gewoon 'de historische kans op een
     monsterscore is laag'."

Dat is een toetsbare bewering, en ze bleek te kloppen. De routine bouwt uit twee lambdas een
scoregrid met ónafhankelijke Poisson-verdelingen (plus de Dixon-Coles-correctie, die alleen de
lage standen bijstelt). Onafhankelijkheid betekent dat een sterke ploeg tegen een zwakke niet
"doorloopt": het grid kent geen wedstrijdverloop waarin de ene ploeg wordt vastgezet. Gemeten over
671 wedstrijden met een opgeslagen lambdapaar én een uitslag:

    alle wedstrijden          voorspeld   werkelijk
    wint met 3 of meer            17.4%       19.5%   (+2.2 pp)
    wint met 4 of meer             6.6%        8.9%   (+2.3 pp)

    duidelijke favoriet (lambda-ratio >= 1.8, n=155)
    favoriet wint                 65.5%       73.5%   (+8.0 pp)
    favoriet wint met 3+          24.1%       29.0%   (+4.9 pp)
    favoriet wint met 4+          11.6%       17.4%   (+5.8 pp)

Het TOTAAL aantal doelpunten klopt wél (0-1 doelpunten 19.8% voorspeld tegen 19.5% werkelijk;
6 of meer 9.7% tegen 8.2%). Het model weet dus prima hoeveel er gescoord wordt — het weet niet hoe
scheef die doelpunten verdeeld raken zodra één ploeg veel sterker is. Dat is precies waarom er
handicapbets op de underdog uit kwamen: `Sevilla +2.5` tegen Barcelona stond op een modelkans van
77.6% tegen 58.5% bij de markt, en dat hele verschil zit in de staart van de margeverdeling.

LET OP BIJ HET LEZEN — de lambdas in `data/run-state/` van vóór 19 sep 2026 zijn berekend met
`shrink = 0.80`. Die parameter is op die datum op 1.00 gezet (§0, §6e) en dat verbreedt het
lambdaverschil met mediaan factor 1.15, wat op zichzelf al ongeveer tweederde van het gat bij "3 of
meer" en veertig procent van het gat bij "4 of meer" dicht. Een tweede correctie bovenop die eerste
is daarom NIET ingevoerd: dat zou dezelfde dubbeltelling zijn waar het openstaande punt over
`early_season_uplift` voor waarschuwt. Wat dit script doet is de vraag meetbaar houden, zodat ze
over enkele weken op lambdas van ná de overstap opnieuw te beantwoorden is.

    python3 scripts/margins.py stats
    python3 scripts/margins.py stats --since 2026-09-20     # alleen shrink=1.00-runs
    python3 scripts/margins.py stats --min-ratio 2.0

Alleen de standaardbibliotheek plus `scripts/model.py` en `scripts/settling.py`.
"""

from __future__ import annotations

import argparse
import collections
import json
import math
from datetime import date
from pathlib import Path

try:
    from . import model, settling
except ImportError:
    import model          # type: ignore[no-redef]
    import settling       # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "data" / "run-state"

# Vanaf welk lambdaverschil een duel "een duidelijke favoriet" heet. 1.8 is geen gemeten optimum
# maar de waarde waarbij de bak groot genoeg blijft om iets te zien (155 van 671 wedstrijden).
DEFAULT_MIN_RATIO = 1.8


def load_matches(since: str | None = None, until: str | None = None) -> list[dict]:
    """Elke wedstrijd uit `data/run-state/` met een opgeslagen lambdapaar, ontdubbeld over runs."""
    seen: dict[tuple[str, str], dict] = {}
    for path in sorted(STATE_DIR.glob("*.json")):
        try:
            state = json.loads(path.read_text())
        except Exception:
            continue
        day = state.get("date")
        if not day or (since and day < since) or (until and day > until):
            continue
        for comp, block in (state.get("competitions") or {}).items():
            if not isinstance(block, dict):
                continue
            for m in block.get("matches") or []:
                if not isinstance(m, dict):
                    continue
                lam = (m.get("lambdas") or {}).get("xg")
                naam = m.get("match") or ""
                if not lam or len(lam) != 2 or " – " not in naam:
                    continue
                seen[(day, naam)] = {"date": day, "match": naam, "competition": comp,
                                     "tier": m.get("tier"), "lam": lam}
    return list(seen.values())


def attach_results(rows: list[dict]) -> tuple[list[dict], int]:
    """Werkelijke eindstanden erbij, via één Fotmob-verzoek per kalenderdag (geen credits)."""
    index, out, miss = settling.DayIndex(), [], 0
    for r in rows:
        home, away = r["match"].split(" – ", 1)
        hit = index.lookup(date.fromisoformat(r["date"]), home, away)
        if not hit or not hit.get("finished") or not hit.get("score"):
            miss += 1
            continue
        try:
            hg, ag = [int(x) for x in hit["score"].replace("−", "-").split("-")]
        except Exception:
            miss += 1
            continue
        out.append({**r, "hg": hg, "ag": ag})
    return out, miss


def margin_and_total(lam: list[float]) -> tuple[collections.Counter, collections.Counter]:
    """Voorspelde kansverdeling over (doelsaldo) en (totaal aantal doelpunten)."""
    grid = model.score_grid(lam[0], lam[1])
    marge: collections.Counter = collections.Counter()
    totaal: collections.Counter = collections.Counter()
    for i, row in enumerate(grid):
        for j, p in enumerate(row):
            marge[i - j] += p
            totaal[i + j] += p
    return marge, totaal


def _line(label: str, pred: float, act: float, n: int) -> str:
    # Binomiale standaardfout op de voorspelde kans; puur als leeshulp, geen toets.
    se = math.sqrt(max(pred * (1 - pred), 1e-9) / n) * 100 if n else 0.0
    ster = "  <--" if abs(act - pred) * 100 > 2 * se else ""
    return (f"  {label:34s} voorspeld {pred*100:5.1f}%   werkelijk {act*100:5.1f}%   "
            f"{(act-pred)*100:+5.1f} pp{ster}")


def report(rows: list[dict], min_ratio: float) -> None:
    n = len(rows)
    if not n:
        print("Geen wedstrijden met zowel een lambdapaar als een uitslag.")
        return

    pred_m: collections.Counter = collections.Counter()
    pred_t: collections.Counter = collections.Counter()
    act_m: collections.Counter = collections.Counter()
    act_t: collections.Counter = collections.Counter()
    for r in rows:
        mg, tt = margin_and_total(r["lam"])
        for k, v in mg.items():
            pred_m[k] += v
        for k, v in tt.items():
            pred_t[k] += v
        act_m[r["hg"] - r["ag"]] += 1
        act_t[r["hg"] + r["ag"]] += 1

    dagen = sorted({r["date"] for r in rows})
    print(f"MARGEKALIBRATIE — {n} wedstrijden, {len(dagen)} dag(en) "
          f"van {dagen[0]} t/m {dagen[-1]}")
    print("Voorspeld = het scoregrid van `model.score_grid` op de opgeslagen lambdas.")
    print("`<--` betekent: meer dan twee standaardfouten van de voorspelling af.\n")

    print("DOELSALDO (beide kanten samengenomen)")
    for label, keep in (("wint met 3 of meer", lambda k: abs(k) >= 3),
                        ("wint met 4 of meer", lambda k: abs(k) >= 4),
                        ("wint met 5 of meer", lambda k: abs(k) >= 5),
                        ("gelijkspel", lambda k: k == 0)):
        p = sum(v for k, v in pred_m.items() if keep(k)) / n
        a = sum(v for k, v in act_m.items() if keep(k)) / n
        print(_line(label, p, a, n))

    print("\nTOTAAL AANTAL DOELPUNTEN (de controle: hier hoort het wél te kloppen)")
    for label, keep in (("0 of 1 doelpunt", lambda k: k <= 1),
                        ("4 of meer", lambda k: k >= 4),
                        ("6 of meer", lambda k: k >= 6)):
        p = sum(v for k, v in pred_t.items() if keep(k)) / n
        a = sum(v for k, v in act_t.items() if keep(k)) / n
        print(_line(label, p, a, n))

    sub = [r for r in rows if max(r["lam"]) / min(r["lam"]) >= min_ratio]
    print(f"\nDUELS MET EEN DUIDELIJKE FAVORIET (lambda-ratio >= {min_ratio}, n={len(sub)})")
    if len(sub) < 20:
        print("  te weinig waarnemingen om te lezen.")
        return
    pf: collections.Counter = collections.Counter()
    af: collections.Counter = collections.Counter()
    for r in sub:
        mg, _ = margin_and_total(r["lam"])
        thuis_favoriet = r["lam"][0] > r["lam"][1]
        teken = 1 if thuis_favoriet else -1
        for k, v in mg.items():
            pf[teken * k] += v
        af[teken * (r["hg"] - r["ag"])] += 1
    m = len(sub)
    for label, keep in (("favoriet wint", lambda k: k >= 1),
                        ("favoriet wint met 2 of meer", lambda k: k >= 2),
                        ("favoriet wint met 3 of meer", lambda k: k >= 3),
                        ("favoriet wint met 4 of meer", lambda k: k >= 4),
                        ("underdog wint of speelt gelijk", lambda k: k <= 0)):
        p = sum(v for k, v in pf.items() if keep(k)) / m
        a = sum(v for k, v in af.items() if keep(k)) / m
        print(_line(label, p, a, m))

    print("\nLEESWIJZER. Staat hier een positief verschil bij 'favoriet wint met 3 of meer', dan")
    print("onderschat het scoregrid hoe scheef een duel met een duidelijke favoriet afloopt, en")
    print("ziet de routine daardoor waarde in een handicap op de underdog die er niet is. Lambdas")
    print("van vóór 2026-09-19 komen van `shrink = 0.80`; draai `--since 2026-09-20` voor een")
    print("meting op de nieuwe instelling, en lees die pas vanaf ~150 duels met een favoriet.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stats", help="margekalibratie over data/run-state/")
    s.add_argument("--since")
    s.add_argument("--until")
    s.add_argument("--min-ratio", type=float, default=DEFAULT_MIN_RATIO)
    args = ap.parse_args(argv)

    rows = load_matches(args.since, args.until)
    rows, miss = attach_results(rows)
    if miss:
        print(f"({miss} wedstrijd(en) zonder bruikbare eindstand overgeslagen)\n")
    report(rows, args.min_ratio)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

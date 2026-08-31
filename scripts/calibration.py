#!/usr/bin/env python3
"""Kalibratielogboek: zit het model systematisch scheef, en waar precies?

Bestaansreden (22 aug 2026). Run A publiceerde die dag dertien bets, en de vraag was of dat
dertien vondsten waren of één afwijking die dertien keer terugkwam. Nameten gaf het tweede: over
alle dertig doorgerekende duels lag het model **+4.19 pp boven** de de-vigde marktkans op
uitkomsten die de markt onder de 25% zet, en **-6.67 pp eronder** bij favorieten. Tien van de
dertien bets lagen daardoor in dezelfde hoek.

Belangrijker nog was wat de uitsplitsing liet zien, want die wees een andere oorzaak aan dan
verwacht:

    shrink 1.0 (compressie uit)  ->  longshots +3.11   favorieten -4.66
    shrink 0.8 (de standaard)    ->  longshots +4.19   favorieten -6.67

`shrink` versterkt de afwijking dus wel, maar veroorzaakt hem niet: hem helemaal uitzetten haalt
er 1.1 van de 4.2 pp af. Bij shrink=1.0 apart per methode gemeten:

    analyze_match (xG)           ->  longshots +0.47   favorieten +0.55   (vlak)
    analyze_match_from_splits    ->  longshots +5.75   favorieten -9.87   (hier zit het)

De oorzaak is rekenkundig en niet seizoensgebonden: `analyze_match` **vermenigvuldigt**
sterkteverhoudingen, terwijl `analyze_match_from_splits` twee doelpuntgemiddelden **optelt en door
twee deelt**. Middelen trekt naar het midden. Gemeten over die dertig duels gebruikte de
splitsmethode 62% van de spreiding in verwacht doelsaldo van de xG-methode.

DIT SCRIPT VERANDERT NIETS AAN DE REKENKERN OF AAN EEN DREMPEL. Het legt alleen vast, elke run,
zodat er over enkele weken genoeg waarnemingen zijn om met cijfers te besluiten of die
splitsmethode hersteld moet worden. Dat is precies wat §6d voorschrijft: één dag is geen bevinding.

    python3 scripts/calibration.py collect --run a --date 2026-08-22
    python3 scripts/calibration.py stats
    python3 scripts/calibration.py stats --since 2026-08-25 --run a

Wat de run moet vastleggen: per doorgerekende wedstrijd een `calibration`-blok in
`data/run-state/`, met de **de-vigde** marktkans en de modelkansen voor de drie 1X2-uitkomsten.
1X2 is met opzet de markt waarop dit gemeten wordt: die is er via BetExplorer elke run gratis voor
vrijwel elke wedstrijd, en de drie uitkomsten sommeren tot 1, zodat de marge proportioneel weg te
delen is.

    "calibration": {
      "market": [0.45, 0.27, 0.28],        # de-vigd, [thuis, gelijk, uit]
      "p_xg":   [0.41, 0.28, 0.31],        # analyze_match op de standaard-shrink
      "p_xg_noshrink": [0.43, 0.28, 0.29], # analyze_match met shrink=1.0
      "p_split": [0.38, 0.29, 0.33]        # analyze_match_from_splits
    }

`p_xg_noshrink` is één extra `analyze_match`-aanroep per wedstrijd en kost dus vrijwel niets; hij
is nodig om het aandeel van `shrink` van het aandeel van de splitsmethode te kunnen scheiden.
Ontbreekt een veld, dan slaat dit script die methode gewoon over — een run die alleen `market` en
`p_xg` heeft, levert nog steeds een bruikbare regel.

LET OP BIJ HET LEZEN. De marge is hier **proportioneel** weggedeeld, en dat overschat juist
longshotkansen: bookmakers laden meer marge op lange koersen dan op korte. Een gemeten
positieve afwijking op longshots is daardoor eerder een ondergrens dan een overschatting.

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import argparse
import json
import statistics
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "data" / "run-state"
LOG = ROOT / "data" / "calibration.jsonl"

OUTCOMES = ("thuis", "gelijk", "uit")
METHODS = (("p_xg", "xG-methode (standaard shrink)"),
           ("p_xg_noshrink", "xG-methode (shrink 1.0)"),
           ("p_split", "splitsmethode"),
           ("p_xg_understat", "xG-methode op Understat (2e xG-model)"),
           ("p_mean", "gemiddelde van beide (= my_prob)"))

# De grenzen waarop gebucket wordt. Longshot/favoriet is bewust ruim genomen: bij smallere
# buckets is er per run te weinig in elke bak om iets te zien.
BUCKETS = (("longshot (<25%)", 0.0, 0.25),
           ("middenmoot (25-50%)", 0.25, 0.50),
           ("favoriet (>50%)", 0.50, 1.01))


def devig(odds: list[float]) -> list[float]:
    """Marktkansen zonder marge, proportioneel geschaald. Zie de waarschuwing in de kop."""
    inv = [1.0 / o for o in odds]
    total = sum(inv)
    return [x / total for x in inv]


def load_log() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(line) for line in LOG.read_text().splitlines() if line.strip()]


def _rows_from_state(state: dict, run: str, day: str) -> list[dict]:
    rows = []
    for comp, block in (state.get("competitions") or {}).items():
        if not isinstance(block, dict):
            continue
        for match in block.get("matches", []):
            if not isinstance(match, dict):
                continue
            cal = match.get("calibration")
            if not cal or not cal.get("market"):
                continue
            market = cal["market"]
            if len(market) != 3:
                continue
            probs = {k: cal[k] for k in ("p_xg", "p_xg_noshrink", "p_split", "p_xg_understat")
                     if isinstance(cal.get(k), list) and len(cal[k]) == 3}
            if "p_xg" in probs and "p_split" in probs:
                probs["p_mean"] = [(a + b) / 2 for a, b in zip(probs["p_xg"], probs["p_split"])]
            for i, naam in enumerate(OUTCOMES):
                rows.append({
                    "date": day, "run": run.upper(), "competition": comp,
                    "match": match.get("match", "?"), "tier": match.get("tier"),
                    "outcome": naam, "market": market[i],
                    **{k: v[i] for k, v in probs.items()},
                })
    return rows


def cmd_collect(args: argparse.Namespace) -> int:
    path = STATE_DIR / f"{args.date}-run-{args.run.lower()}.json"
    if not path.exists():
        print(f"Geen voortgangsbestand voor run {args.run} op {args.date}.")
        return 1
    rows = _rows_from_state(json.loads(path.read_text()), args.run, args.date)
    if not rows:
        print("Geen calibration-blokken gevonden in het voortgangsbestand — niets vastgelegd.\n"
              "Zie de kop van dit script voor de vorm die de run moet wegschrijven.")
        return 0

    existing = load_log()
    seen = {(r["date"], r["run"], r["match"], r["outcome"]) for r in existing}
    fresh = [r for r in rows if (r["date"], r["run"], r["match"], r["outcome"]) not in seen]
    if not fresh:
        print(f"Alle {len(rows)} waarnemingen stonden er al in; niets toegevoegd.")
        return 0
    with LOG.open("a") as fh:
        for r in fresh:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(fresh)} waarneming(en) toegevoegd ({len(fresh) // 3} wedstrijden); "
          f"totaal {len(existing) + len(fresh)} in data/calibration.jsonl.")
    return 0


def _bucket_means(rows: list[dict], key: str) -> list[tuple[str, int, float | None]]:
    out = []
    for label, lo, hi in BUCKETS:
        devs = [(r[key] - r["market"]) * 100 for r in rows
                if key in r and lo <= r["market"] < hi]
        out.append((label, len(devs), statistics.mean(devs) if devs else None))
    return out


def _table(rows: list[dict], titel: str) -> None:
    print(f"\n{titel}")
    header = f"  {'methode':<34}" + "".join(f"{lbl.split(' ')[0]:>14}" for lbl, _, _ in BUCKETS)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for key, naam in METHODS:
        if not any(key in r for r in rows):
            continue
        cells = ""
        for _, n, mean in _bucket_means(rows, key):
            cells += f"{'—':>14}" if mean is None else f"{mean:>+13.2f}"
        print(f"  {naam:<34}{cells}")
    counts = "".join(f"{n:>14}" for _, n, _ in _bucket_means(rows, "market"))
    print(f"  {'aantal waarnemingen':<34}" + "".join(
        f"{sum(1 for r in rows if lo <= r['market'] < hi):>14}" for _, lo, hi in BUCKETS))


def cmd_stats(args: argparse.Namespace) -> int:
    rows = load_log()
    if args.since:
        rows = [r for r in rows if r["date"] >= args.since]
    if args.run:
        rows = [r for r in rows if r["run"] == args.run.upper()]
    if not rows:
        print("Nog geen waarnemingen in data/calibration.jsonl.")
        return 0

    dagen = sorted({r["date"] for r in rows})
    wedstrijden = len({(r["date"], r["run"], r["match"]) for r in rows})
    print(f"KALIBRATIE — {wedstrijden} wedstrijden, {len(rows)} uitkomsten, "
          f"{len(dagen)} dag(en) van {dagen[0]} t/m {dagen[-1]}")
    print("Afwijking van het model t.o.v. de de-vigde marktkans, in procentpunten.")
    print("Positief = het model geeft die uitkomst meer kans dan de markt.")

    _table(rows, "ALLE WAARNEMINGEN")

    xg = [r for r in rows if "p_xg" in r and "p_xg_noshrink" in r]
    if xg:
        lo = [r for r in xg if r["market"] < 0.25]
        if lo:
            met = statistics.mean((r["p_xg"] - r["market"]) * 100 for r in lo)
            zonder = statistics.mean((r["p_xg_noshrink"] - r["market"]) * 100 for r in lo)
            print(f"\n  Aandeel van `shrink` op longshots: {met - zonder:+.2f} pp van de "
                  f"{met:+.2f} pp die de xG-methode daar afwijkt.")
            print("  De rest is niet aan shrink toe te schrijven; vergelijk de regels hierboven.")

    if len(dagen) > 1:
        print("\nPER DAG (gemiddelde van beide methodes, longshots <25%):")
        for dag in dagen:
            drows = [r for r in rows if r["date"] == dag and "p_mean" in r and r["market"] < 0.25]
            if drows:
                m = statistics.mean((r["p_mean"] - r["market"]) * 100 for r in drows)
                print(f"  {dag}  {m:>+7.2f} pp   ({len(drows)} waarnemingen)")

    n_low = sum(1 for r in rows if r["market"] < 0.25)
    print(f"\nLEESWIJZER. {n_low} waarnemingen in de longshotbak. Onder de ~150 (ruwweg vijf volle "
          "\nrundagen) is een verschil van een paar procentpunt nog ruis. Pas geen drempel en geen "
          "\nrekenstap aan op grond van één of twee dagen — zie §6d van _shared-rules.md.")
    print("De marge is proportioneel weggedeeld, wat longshotkansen van de markt overschat; een "
          "\ngemeten positieve afwijking op longshots is daarom eerder een ondergrens.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    col = sub.add_parser("collect", help="haal de calibration-blokken uit een voortgangsbestand")
    col.add_argument("--run", required=True, choices=["A", "B", "a", "b"])
    col.add_argument("--date", required=True, help="YYYY-MM-DD")
    col.set_defaults(func=cmd_collect)

    st = sub.add_parser("stats", help="toon de afwijking per marktkans-bak")
    st.add_argument("--since", help="alleen dagen vanaf deze datum (YYYY-MM-DD)")
    st.add_argument("--run", choices=["A", "B", "a", "b"], help="alleen deze run")
    st.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

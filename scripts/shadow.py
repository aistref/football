#!/usr/bin/env python3
"""Schaduwlogboek: reken de afgewezen kandidaten alsnog af.

Bestaansreden (11 aug 2026). De poorten in _shared-rules.md §1 wijzen bets af, en tot nu toe
werd er van die afgewezen bets nooit meer iets vastgelegd. Daardoor was "strenger is beter" een
aanname die niet te toetsen viel: `picks.jsonl` bevat alleen wat er wél doorheen kwam, dus je
kunt er per definitie niet uit aflezen wat een poort je heeft bespaard of gekost.

Dit script vult dat gat. Elke kandidaat die in `data/run-state/` een `near_miss` heeft, gaat als
schaduwpick naar `data/shadow.jsonl` en wordt daarna net zo afgewikkeld als een echte pick. De
enige vraag die telt staat in `stats`:

    zou de afgewezen selectie hebben gewonnen, en wat was de ROI geweest?

Is die ROI structureel negatief, dan doen de poorten hun werk. Is hij structureel positief, dan
kost het filter geld en hoort de drempel omlaag. Beide antwoorden zijn bruikbaar; geen antwoord
is dat niet.

    python3 scripts/shadow.py collect --date 2026-08-11 --run a
    python3 scripts/shadow.py open [--hours 2] [--no-check]
    python3 scripts/shadow.py settle <id> won|lost|void [--score 2-1]
    python3 scripts/shadow.py stats [--gate tweede_methode]

Alleen de standaardbibliotheek — deze repo heeft geen installatiestap.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:                        # als pakket: `from scripts import shadow`
    from . import settling
except ImportError:         # als los script: `python3 scripts/shadow.py`
    import settling         # type: ignore[no-redef]

ROOT = Path(__file__).resolve().parent.parent
SHADOW = ROOT / "data" / "shadow.jsonl"
RUN_STATE = ROOT / "data" / "run-state"

OPEN = "pending"
CLOSED = ("won", "lost", "void")


def die(msg: str) -> None:
    print(f"fout: {msg}", file=sys.stderr)
    raise SystemExit(1)


def load() -> list[dict]:
    if not SHADOW.exists():
        return []
    rows = []
    for lineno, line in enumerate(SHADOW.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            die(f"{SHADOW.name}:{lineno}: ongeldige JSON: {exc}")
    return rows


def save(rows: list[dict]) -> None:
    SHADOW.parent.mkdir(parents=True, exist_ok=True)
    SHADOW.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


# ------------------------------------------------------------------- verzamelen

def cmd_collect(args: argparse.Namespace) -> int:
    """Haal de near_miss-regels van één run uit data/run-state/ en zet ze in het schaduwlogboek."""
    path = RUN_STATE / f"{args.date}-run-{args.run.lower()}.json"
    if not path.exists():
        die(f"geen voortgangsbestand: {path}")
    state = json.loads(path.read_text())

    existing = load()
    seen = {r["id"] for r in existing}
    new: list[dict] = []

    for comp, block in state.get("competitions", {}).items():
        if not isinstance(block, dict):
            continue
        for match in block.get("matches", []):
            if not isinstance(match, dict):
                continue
            # Eén match kan meer dan één schaduwkandidaat opleveren. `near_miss` is de sterkste
            # afgewezen kandidaat van een wedstrijd zonder bet; `poort8_geblokkeerd` (sinds
            # 4 sep 2026) zijn de selecties die alléén op poort 8 sneuvelden — die horen er ook in
            # als de wedstrijd daarna alsnog een andere bet opleverde, want anders is op 25
            # september niet te meten wat die poort heeft gekost. Zie §1e.
            kandidaten = []
            if isinstance(match.get("near_miss"), dict):
                kandidaten.append(("", match["near_miss"]))
            for i, blk in enumerate(match.get("poort8_geblokkeerd") or []):
                if isinstance(blk, dict):
                    kandidaten.append((f"-p8-{i}", blk))

            for suffix, nm in kandidaten:
                odds = nm.get("odds")
                if not isinstance(odds, (int, float)) or odds <= 1:
                    continue
                e_xg, e_split = nm.get("edge_xg"), nm.get("edge_split")
                edges = [v for v in (e_xg, e_split) if isinstance(v, (int, float))]
                if not edges:
                    continue

                implied = 1 / odds
                # my_prob volgens de herziene §1: het gemiddelde van beide methodes. Bestaat er maar
                # één methode (de competitie van één van beide ploegen heeft geen xG bij Fotmob), dan
                # telt die ene — de kandidaat wordt wél vastgelegd, maar met `methods: 1` gemarkeerd
                # zodat `stats` hem buiten de hoofdcijfers houdt. Tot 20 aug 2026 werd zo'n kandidaat
                # weggegooid; op 19 aug kostte dat 2 van de 5 rijen en op 20 aug 11 van de 20,
                # waaronder telkens de scherpste getallen van de dag. Weggooien is geen neutrale
                # keuze: het maakt de meting van poort `data` juist blind voor de wedstrijden waar
                # die poort het vaakst toeslaat.
                my_prob = implied + (sum(edges) / len(edges)) / 100
                slug = "".join(c if c.isalnum() else "-" for c in match.get("match", "")).strip("-").lower()
                pid = f"shadow-{state['date']}-{state['run'].lower()}-{slug}{suffix}"[:120]
                if pid in seen:
                    continue

                new.append({
                    "id": pid,
                    "date": state["date"],
                    "run": state["run"],
                    "competition": comp,
                    "match": match.get("match"),
                    "data_tier": match.get("tier"),
                    "market": nm.get("market"),
                    "odds": odds,
                    "implied_prob": round(implied, 4),
                    "my_prob": round(my_prob, 4),
                    "edge_pp": round((my_prob - implied) * 100, 2),
                    "edge_xg": e_xg,
                    "edge_split": e_split,
                    "methods": len(edges),
                    "edge_robust_min": nm.get("edge_robust_min"),
                    "failed_gate": nm.get("failed_gate"),
                    "result": OPEN,
                    "settled_at": None,
                })
                seen.add(pid)

    if not new:
        print(f"Geen nieuwe kandidaten in {path.name}.")
        return 0

    save(existing + new)
    print(f"{len(new)} schaduwpick(s) toegevoegd; totaal {len(existing) + len(new)}.")
    for r in new:
        print(f"  {r['id']}")
        print(f"     {r['match']} | {r['market']} @ {r['odds']} "
              f"| edge {r['edge_pp']:+.2f} pp | viel af op {r['failed_gate']}")
    return 0


# -------------------------------------------------------------------- afwikkelen

def cmd_open(args: argparse.Namespace) -> int:
    """Toon de schaduwpicks die afgewikkeld mogen worden.

    Tot 3 sep 2026 stond hier geen enkel filter: élke `pending` regel werd getoond,
    terwijl de docstring `--hours 12` adverteerde die niet bestond. Daardoor rekende de
    routine afgewezen kandidaten af terwijl de échte picks van dezelfde wedstrijden nog
    twaalf uur moesten wachten — zie `scripts/settling.py`. Beide gebruiken nu dezelfde
    regel, uit dezelfde module.
    """
    now = datetime.now(timezone.utc)
    index = None if args.no_check else settling.DayIndex()
    rows, wachten = [], []
    for r in load():
        if r.get("result") != OPEN:
            continue
        ok, reden = settling.settleable(r, index, args.hours, now)
        (rows if ok else wachten).append((r, reden))

    if index is not None and index.errors:
        for day, err in index.errors.items():
            print(f"  let op: uitslagen van {day} niet op te halen ({err}) — "
                  f"terugval op de klok van {args.hours:g} uur\n", file=sys.stderr)

    for r, reden in wachten:
        print(f"  wacht  {r['id']}\n         {reden}")

    if not rows:
        print("Geen schaduwpicks klaar om af te wikkelen.")
        return 0
    print(f"{len(rows)} schaduwpick(s) klaar om af te wikkelen:\n")
    for r, reden in rows:
        print(f"  {r['id']}")
        print(f"     {r['date']} · {r['match']} | {r['market']} @ {r['odds']} "
              f"| viel af op {r['failed_gate']}")
        print(f"     {reden}")
    return 0


def cmd_settle(args: argparse.Namespace) -> int:
    rows = load()
    for r in rows:
        if r.get("id") == args.id:
            if r.get("result") in CLOSED:
                die(f"{args.id} is al afgewikkeld als {r['result']}")
            r["result"] = args.result
            r["settled_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if args.score:
                r["settled_score"] = args.score
            if args.units is not None:
                r["settled_units"] = args.units
            save(rows)
            extra = f" ({args.units:+.2f}u)" if args.units is not None else ""
            print(f"{args.id} -> {args.result}{extra}")
            return 0
    die(f"schaduwpick niet gevonden: {args.id}")
    return 1


# ------------------------------------------------------------------------ meten

def ledger_units(row: dict) -> float:
    """Netto resultaat bij 1u inzet — zie ledger.pick_units.

    Een kwartlijn splitst in twee halve bets en kan dus half winnen of half verliezen. Staat er
    een expliciete `settled_units`, dan telt die; anders is het een hele win of een heel verlies.
    """
    units = row.get("settled_units")
    if units is not None:
        return float(units)
    return row["odds"] - 1 if row["result"] == "won" else -1.0


def summarise(rows: list[dict], label: str) -> None:
    decided = [r for r in rows if r.get("result") in ("won", "lost")]
    won = [r for r in decided if r["result"] == "won"]
    pending = sum(1 for r in rows if r.get("result") == OPEN)

    print(f"\n{label}")
    print(f"  kandidaten       {len(rows)}  ({pending} nog niet afgewikkeld)")
    if not decided:
        print("  Nog niets afgewikkeld — er valt nog niets te meten.")
        return

    profit = sum(ledger_units(r) for r in decided)
    print(f"  hit rate         {len(won)}/{len(decided)} = {100 * len(won) / len(decided):.1f}%")
    print(f"  ROI (1u flat)    {profit:+.2f}u over {len(decided)} = {100 * profit / len(decided):+.1f}%")
    print(f"  gem. odds        {sum(r['odds'] for r in decided) / len(decided):.2f}"
          f"   gem. geclaimde edge {sum(r['edge_pp'] for r in decided) / len(decided):+.1f} pp")

    verwacht = sum(r["my_prob"] for r in decided)
    print(f"  kalibratie       verwacht {verwacht:.1f} winnaars, werkelijk {len(won)} "
          f"({len(won) - verwacht:+.1f})")

    if profit > 0:
        print(f"  >> Deze afwijzingen kostten {profit:+.2f}u. Waren het er veel en blijft dit staan,")
        print("     dan is de poort te streng afgesteld.")
    else:
        print(f"  >> Deze afwijzingen bespaarden {-profit:.2f}u. De poort doet dan zijn werk.")


def cmd_stats(args: argparse.Namespace) -> int:
    rows = load()
    if args.gate:
        rows = [r for r in rows if r.get("failed_gate") == args.gate]
    if not rows:
        print("Schaduwlogboek is leeg. Nog niets te meten.")
        return 0

    # Rijen zonder `methods` komen van vóór 20 aug 2026 en hadden toen altijd twee methodes.
    single = [r for r in rows if r.get("methods") == 1]
    if not args.include_single:
        rows = [r for r in rows if r.get("methods", 2) >= 2]

    summarise(rows, "ALLE AFGEWEZEN KANDIDATEN")
    if not args.gate:
        for gate in sorted({r.get("failed_gate") for r in rows if r.get("failed_gate")}):
            summarise([r for r in rows if r.get("failed_gate") == gate], f"viel af op: {gate}")
    if single and not args.include_single:
        summarise(single, "APART GEHOUDEN: kandidaten met maar één methode (`--include-single`)")
        print("  Deze staan buiten de cijfers hierboven: hun my_prob komt uit één schatter in")
        print("  plaats van het gemiddelde van twee, dus ze zijn niet op dezelfde schaal.")
    print("\nLees dit naast `python3 scripts/ledger.py stats`: dat is wat er wél doorheen kwam,")
    print("dit is wat er is tegengehouden. Het verschil tussen die twee is wat de poorten doen.")
    return 0


# -------------------------------------------------------------------------- cli

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_col = sub.add_parser("collect", help="haal near_miss-regels uit een voortgangsbestand")
    p_col.add_argument("--date", required=True, help="YYYY-MM-DD")
    p_col.add_argument("--run", required=True, choices=["A", "B", "a", "b"])

    p_open = sub.add_parser("open", help="toon schaduwpicks die nog afgewikkeld moeten worden")
    p_open.add_argument("--hours", type=float, default=settling.FALLBACK_HOURS,
                        help="terugvalmarge in uren sinds de aftrap, alleen gebruikt als de "
                             f"bron geen status geeft (standaard {settling.FALLBACK_HOURS:g})")
    p_open.add_argument("--no-check", action="store_true",
                        help="vraag de bron niet om de wedstrijdstatus; gebruik alleen --hours")

    p_set = sub.add_parser("settle", help="leg de uitkomst van een schaduwpick vast")
    p_set.add_argument("id")
    p_set.add_argument("result", choices=CLOSED)
    p_set.add_argument("--score", help="eindstand, bv. 2-1")
    p_set.add_argument("--units", type=float, default=None,
                       help="netto eenheden bij 1u inzet, alleen bij een halve uitkomst op een "
                            "kwartlijn (half verlies = -0.5, half winst = (odds-1)/2)")

    p_st = sub.add_parser("stats", help="hit rate en ROI van wat er is tegengehouden")
    p_st.add_argument("--gate", help="filter op afwijsgrond, bv. tweede_methode")
    p_st.add_argument("--include-single", action="store_true",
                      help="tel kandidaten met maar één methode mee in de hoofdcijfers")

    args = parser.parse_args()
    return {"collect": cmd_collect, "open": cmd_open,
            "settle": cmd_settle, "stats": cmd_stats}[args.cmd](args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # `shadow.py stats | head` sluit de pijp; dat is geen fout van dit script.
        # stdout expliciet dichtzetten voorkomt dat Python er alsnog over klaagt bij afsluiten.
        try:
            sys.stdout.close()
        finally:
            raise SystemExit(0)

#!/usr/bin/env python3
"""Voortgangsbestand per run: overleeft een onderbreking (bv. een Claude-gebruikslimiet).

Zonder dit begint een hervatte run altijd weer bij wedstrijd 1, ook als hij al 25 van de 30 klaar
had. Het voortgangsbestand wordt tijdens Stage 4/5 na elke afgeronde wedstrijd/competitie
gecommit en gepusht — pas dát maakt hervatten mogelijk, want de container die de sessie draaide
is weg zodra de limiet toeslaat; alleen wat gepusht is overleeft.

    python3 scripts/progress.py show --run A --date 2026-08-08
    python3 scripts/progress.py reset --run A --date 2026-08-08   # forceer een verse start

Vanuit code (tijdens een run):

    from scripts.progress import load_or_start, save, is_done, mark

    state = load_or_start("A", date.today())
    if state["completed"]:
        raise SystemExit("deze run is vandaag al afgerond")
    for name in runlijst:
        if is_done(state, name):
            continue          # al gedaan vóór de onderbreking — niet opnieuw
        ... analyseer competitie `name` ...
        mark(state, name, resultaat)
        save(state)            # commit + push dit bestand meteen, niet pas aan het eind

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / "data" / "run-state"


def _path(run_id: str, day: date) -> Path:
    return STATE_DIR / f"{day.isoformat()}-run-{run_id.lower()}.json"


def new_state(run_id: str, day: date) -> dict:
    return {
        "run": run_id.upper(),
        "date": day.isoformat(),
        "resumed_count": 0,
        "competitions": {},  # naam -> {"status": ..., "matches": [...]}
        "completed": False,
    }


def load(run_id: str, day: date) -> dict | None:
    p = _path(run_id, day)
    if not p.exists():
        return None
    return json.loads(p.read_text())


def load_or_start(run_id: str, day: date) -> dict:
    """Geeft het bestaande voortgangsbestand van vandaag terug, of maakt een nieuwe aan.

    Bestond het al (dus dit is een hervatting na onderbreking)? Tel dat en meld het in het
    runrapport — een hervatte run is geen storing, maar wel iets om te vermelden.
    """
    state = load(run_id, day)
    if state is None:
        return new_state(run_id, day)
    if not state["completed"]:
        state["resumed_count"] += 1
    return state


def save(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _path(state["run"], date.fromisoformat(state["date"])).write_text(
        json.dumps(state, ensure_ascii=False, indent=1))


def is_done(state: dict, competition: str) -> bool:
    return competition in state["competitions"]


def mark(state: dict, competition: str, result: dict) -> None:
    """`result` bv. {"status": "GEANALYSEERD", "matches": [...]} of {"status": "GEEN WEDSTRIJD"}."""
    state["competitions"][competition] = result


def mark_completed(state: dict) -> None:
    state["completed"] = True


def is_completed(state: dict | None) -> bool:
    return bool(state and state.get("completed"))


def _cmd_show(args: argparse.Namespace) -> int:
    state = load(args.run, date.fromisoformat(args.date))
    if state is None:
        print(f"Geen voortgangsbestand voor run {args.run} op {args.date}.")
        return 0
    done = [n for n, r in state["competitions"].items() if r.get("status") == "GEANALYSEERD"]
    print(f"Run {state['run']} — {state['date']}")
    print(f"  compleet: {state['completed']}   hervat: {state['resumed_count']}x")
    print(f"  competities verwerkt: {len(state['competitions'])}  (waarvan geanalyseerd: {len(done)})")
    for name, result in state["competitions"].items():
        n_matches = len(result.get("matches", []))
        print(f"    {name:32s} {result['status']:20s} {n_matches or ''}")
    return 0


ALL_MARKETS = ("1X2", "DC", "DNB", "AH", "OU", "BTTS")
"""De zes markten uit _shared-rules.md §1. `markets_checked` in het voortgangsbestand hoort deze
namen te gebruiken; `verify` rekent af op deze lijst."""


def _cmd_verify(args: argparse.Namespace) -> int:
    """Controleer dat elke geanalyseerde wedstrijd alle zes markten heeft gehad.

    Bestaansreden (14 aug 2026). §1 schreef al vanaf het begin voor om 1X2, Double Chance, Draw No
    Bet, Asian Handicap, Over/Under en BTTS langs te gaan, en dat gebeurde een week lang niet: van
    de eerste 15 picks waren er 11 een 1X2 en 0 een handicap. Niemand merkte het, omdat er nergens
    werd vastgelegd wat er per wedstrijd was bekeken — alleen wat eruit kwam. Een regel die niemand
    kan nalopen is geen regel maar een voornemen.

    Dit is met opzet een controle op de **administratie**, niet op de uitkomst: nul bets is een
    geldige uitkomst, een wedstrijd waarbij vier markten niet eens zijn opgezocht niet.
    """
    state = load(args.run, date.fromisoformat(args.date))
    if state is None:
        print(f"Geen voortgangsbestand voor run {args.run} op {args.date}.")
        return 1

    gaten: list[str] = []
    gedekt = 0
    overgeslagen = {"NONE": 0, "afgekapt": 0}
    for comp, block in state["competitions"].items():
        if not isinstance(block, dict) or block.get("status") != "GEANALYSEERD":
            continue
        for match in block.get("matches", []):
            if not isinstance(match, dict):
                continue
            naam = match.get("match", "?")
            if match.get("tier") == "NONE":
                overgeslagen["NONE"] += 1
                continue  # geen kansbron, dus geen markt om te bekijken
            if match.get("afgekapt"):
                # Buiten MAX_DEEP_ANALYSES gevallen (§3, Stage 4). Zo'n duel is niet
                # doorgerekend, dus er valt geen markt te bekijken — net als bij tier NONE.
                # Dit is geen stille uitzondering: de afkapping staat met naam en aantal in het
                # runrapport en in `parameters.afkapping`, en het aantal staat hieronder.
                overgeslagen["afgekapt"] += 1
                continue
            checked = match.get("markets_checked")
            if not checked:
                gaten.append(f"{comp} · {naam}: geen markets_checked vastgelegd")
                continue
            mist = [m for m in ALL_MARKETS if m not in checked]
            if mist:
                gaten.append(f"{comp} · {naam}: niet bekeken: {', '.join(mist)}")
            else:
                gedekt += 1

    staart = (f" Overgeslagen: {overgeslagen['NONE']} zonder kansbron (tier NONE), "
              f"{overgeslagen['afgekapt']} afgekapt door MAX_DEEP_ANALYSES."
              if any(overgeslagen.values()) else "")
    if not gaten:
        print(f"Alle {gedekt} geanalyseerde wedstrijd(en) hebben alle zes markten gehad.{staart}")
        return 0
    print(f"{len(gaten)} wedstrijd(en) met onvolledige marktdekking "
          f"({gedekt} wel volledig).{staart}\n")
    for regel in gaten:
        print(f"  {regel}")
    print("\nZie _shared-rules.md §1: 'Ga alle markten langs'. Een markt waarvoor geen odds te")
    print("vinden waren telt ook als bekeken — noteer hem dan met de reden, niet als gat.")
    return 1


def _cmd_reset(args: argparse.Namespace) -> int:
    p = _path(args.run, date.fromisoformat(args.date))
    if p.exists():
        p.unlink()
        print(f"Voortgangsbestand voor run {args.run} op {args.date} verwijderd — volgende start is vers.")
    else:
        print("Er was geen voortgangsbestand om te verwijderen.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    show = sub.add_parser("show", help="toon de voortgang van een run")
    show.add_argument("--run", required=True, choices=["A", "B", "a", "b"])
    show.add_argument("--date", required=True, help="YYYY-MM-DD")
    show.set_defaults(func=_cmd_show)

    verify = sub.add_parser("verify", help="controleer of elke wedstrijd alle zes markten heeft gehad")
    verify.add_argument("--run", required=True, choices=["A", "B", "a", "b"])
    verify.add_argument("--date", required=True, help="YYYY-MM-DD")
    verify.set_defaults(func=_cmd_verify)

    reset = sub.add_parser("reset", help="verwijder het voortgangsbestand, forceer een verse start")
    reset.add_argument("--run", required=True, choices=["A", "B", "a", "b"])
    reset.add_argument("--date", required=True, help="YYYY-MM-DD")
    reset.set_defaults(func=_cmd_reset)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

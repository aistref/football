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

    reset = sub.add_parser("reset", help="verwijder het voortgangsbestand, forceer een verse start")
    reset.add_argument("--run", required=True, choices=["A", "B", "a", "b"])
    reset.add_argument("--date", required=True, help="YYYY-MM-DD")
    reset.set_defaults(func=_cmd_reset)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

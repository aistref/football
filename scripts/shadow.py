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
    python3 scripts/shadow.py open [--hours 12]
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
            nm = match.get("near_miss")
            if not isinstance(nm, dict):
                continue

            odds = nm.get("odds")
            if not isinstance(odds, (int, float)) or odds <= 1:
                continue
            e_xg, e_split = nm.get("edge_xg"), nm.get("edge_split")
            if not all(isinstance(v, (int, float)) for v in (e_xg, e_split)):
                continue

            implied = 1 / odds
            # my_prob volgens de herziene §1: het gemiddelde van beide methodes.
            my_prob = implied + ((e_xg + e_split) / 2) / 100
            slug = "".join(c if c.isalnum() else "-" for c in match.get("match", "")).strip("-").lower()
            pid = f"shadow-{state['date']}-{state['run'].lower()}-{slug}"[:120]
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
    rows = [r for r in load() if r.get("result") == OPEN]
    if not rows:
        print("Geen openstaande schaduwpicks.")
        return 0
    print(f"{len(rows)} schaduwpick(s) klaar om af te wikkelen:\n")
    for r in rows:
        print(f"  {r['id']}")
        print(f"     {r['date']} · {r['match']} | {r['market']} @ {r['odds']} "
              f"| viel af op {r['failed_gate']}")
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
            save(rows)
            print(f"{args.id} -> {args.result}")
            return 0
    die(f"schaduwpick niet gevonden: {args.id}")
    return 1


# ------------------------------------------------------------------------ meten

def summarise(rows: list[dict], label: str) -> None:
    decided = [r for r in rows if r.get("result") in ("won", "lost")]
    won = [r for r in decided if r["result"] == "won"]
    pending = sum(1 for r in rows if r.get("result") == OPEN)

    print(f"\n{label}")
    print(f"  kandidaten       {len(rows)}  ({pending} nog niet afgewikkeld)")
    if not decided:
        print("  Nog niets afgewikkeld — er valt nog niets te meten.")
        return

    profit = sum(r["odds"] - 1 for r in won) - (len(decided) - len(won))
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

    summarise(rows, "ALLE AFGEWEZEN KANDIDATEN")
    if not args.gate:
        for gate in sorted({r.get("failed_gate") for r in rows if r.get("failed_gate")}):
            summarise([r for r in rows if r.get("failed_gate") == gate], f"viel af op: {gate}")
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

    sub.add_parser("open", help="toon schaduwpicks die nog afgewikkeld moeten worden")

    p_set = sub.add_parser("settle", help="leg de uitkomst van een schaduwpick vast")
    p_set.add_argument("id")
    p_set.add_argument("result", choices=CLOSED)
    p_set.add_argument("--score", help="eindstand, bv. 2-1")

    p_st = sub.add_parser("stats", help="hit rate en ROI van wat er is tegengehouden")
    p_st.add_argument("--gate", help="filter op afwijsgrond, bv. tweede_methode")

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

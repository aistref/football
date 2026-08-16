#!/usr/bin/env python3
"""Ledger voor de betting-routine: valideren, afwikkelen en meten.

Zonder dit logboek is "gaat het goed of niet" niet te beantwoorden, alleen te voelen.

    python3 scripts/ledger.py validate
    python3 scripts/ledger.py add < pick.json
    python3 scripts/ledger.py open [--hours 12]
    python3 scripts/ledger.py settle <id> won|lost|void [--score 2-1]
    python3 scripts/ledger.py stats [--run A]

Alleen de standaardbibliotheek — deze repo heeft geen installatiestap.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PICKS = ROOT / "data" / "picks.jsonl"
SCHEMA = ROOT / "schema" / "pick.schema.json"

RESULTS_OPEN = "pending"
RESULTS_CLOSED = ("won", "lost", "void")


# --------------------------------------------------------------------------- io

def load_picks() -> list[dict]:
    if not PICKS.exists():
        return []
    picks = []
    for lineno, line in enumerate(PICKS.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        try:
            picks.append(json.loads(line))
        except json.JSONDecodeError as exc:
            die(f"{PICKS.name}:{lineno}: ongeldige JSON: {exc}")
    return picks


def save_picks(picks: list[dict]) -> None:
    PICKS.write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in picks))


def die(msg: str) -> None:
    print(f"fout: {msg}", file=sys.stderr)
    raise SystemExit(1)


def parse_dt(value: str) -> datetime:
    """ISO 8601 met offset; val terug op UTC als de offset ontbreekt."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# -------------------------------------------------------------------- validatie

def validate_pick(pick: dict, schema: dict, where: str) -> list[str]:
    """Minimale draft-07-subset: required, additionalProperties, type, enum, min/max, minItems, minLength."""
    errors: list[str] = []
    props: dict = schema["properties"]

    for field in schema["required"]:
        if field not in pick:
            errors.append(f"{where}: verplicht veld ontbreekt: {field}")

    if not schema.get("additionalProperties", True):
        for field in pick:
            if field not in props:
                errors.append(f"{where}: onbekend veld: {field}")

    type_map = {"string": str, "number": (int, float), "boolean": bool, "array": list, "object": dict}

    for field, value in pick.items():
        spec = props.get(field)
        if spec is None:
            continue

        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"{where}.{field}: {value!r} niet in {spec['enum']}")
            continue

        expected = spec.get("type")
        if expected is not None:
            allowed = [expected] if isinstance(expected, str) else expected
            if value is None:
                if "null" not in allowed:
                    errors.append(f"{where}.{field}: mag niet null zijn")
                continue
            py_types: tuple[type, ...] = ()
            for name in allowed:
                mapped = type_map.get(name)
                if mapped:
                    py_types += mapped if isinstance(mapped, tuple) else (mapped,)
            # bool is een subtype van int in Python; nooit als getal accepteren
            if isinstance(value, bool) and "boolean" not in allowed:
                errors.append(f"{where}.{field}: verwacht {allowed}, kreeg boolean")
                continue
            if py_types and not isinstance(value, py_types):
                errors.append(f"{where}.{field}: verwacht {allowed}, kreeg {type(value).__name__}")
                continue

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in spec and value < spec["minimum"]:
                errors.append(f"{where}.{field}: {value} < minimum {spec['minimum']}")
            if "maximum" in spec and value > spec["maximum"]:
                errors.append(f"{where}.{field}: {value} > maximum {spec['maximum']}")
        if isinstance(value, str) and "minLength" in spec and len(value) < spec["minLength"]:
            errors.append(f"{where}.{field}: te kort (min {spec['minLength']})")
        if isinstance(value, list) and "minItems" in spec and len(value) < spec["minItems"]:
            errors.append(f"{where}.{field}: minstens {spec['minItems']} item(s) vereist")

    return errors


def semantic_checks(pick: dict, where: str) -> list[str]:
    """Regels die het schema niet kan uitdrukken maar die de routine wel eist."""
    errors: list[str] = []
    odds, implied = pick.get("odds"), pick.get("implied_prob")
    my_prob, edge = pick.get("my_prob"), pick.get("edge_pp")

    if isinstance(odds, (int, float)) and isinstance(implied, (int, float)):
        if abs(implied - 1 / odds) > 0.005:
            errors.append(f"{where}: implied_prob {implied} wijkt af van 1/odds ({1 / odds:.4f})")

    if all(isinstance(v, (int, float)) for v in (my_prob, implied, edge)):
        if abs(edge - (my_prob - implied) * 100) > 0.15:
            errors.append(f"{where}: edge_pp {edge} wijkt af van (my_prob - implied_prob)*100 "
                          f"({(my_prob - implied) * 100:.2f})")

    # anti-circulariteitsregel: geen odds-bron als onderbouwing van my_prob
    banned = ("oddschecker", "oddsportal", "betexplorer", "bet365", "unibet", "pinnacle",
              "bookmaker", "the_odds_api", "toto", "bwin")
    for src in pick.get("prob_sources") or []:
        if any(b in src.lower() for b in banned):
            errors.append(f"{where}: prob_sources bevat een odds-bron ({src}) — "
                          f"circulaire onderbouwing, zie _shared-rules.md §2")

    tier, edge_val = pick.get("data_tier"), pick.get("edge_pp")
    if isinstance(edge_val, (int, float)):
        threshold = 3.0 if tier == "FULL" else 6.0
        if edge_val < threshold:
            errors.append(f"{where}: edge {edge_val} pp onder de drempel {threshold} pp voor tier {tier}")

    if isinstance(odds, (int, float)) and not (1.30 <= odds <= 6.00):
        errors.append(f"{where}: odds {odds} buiten de band 1.30-6.00")

    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    schema = json.loads(SCHEMA.read_text())
    picks = load_picks()
    errors: list[str] = []
    seen: dict[str, int] = {}

    for i, pick in enumerate(picks, 1):
        where = f"regel {i}"
        errors += validate_pick(pick, schema, where)
        errors += semantic_checks(pick, where)
        pid = pick.get("id")
        if isinstance(pid, str):
            if pid in seen:
                errors.append(f"{where}: dubbele id {pid} (ook op regel {seen[pid]})")
            else:
                seen[pid] = i

    if errors:
        for err in errors:
            print(err)
        print(f"\n{len(errors)} probleem(en) in {len(picks)} pick(s).")
        return 1

    print(f"{len(picks)} pick(s) geldig.")
    return 0


# ------------------------------------------------------------------- muteren

def cmd_add(args: argparse.Namespace) -> int:
    """Lees één pick (of een lijst picks) als JSON van stdin en voeg toe na validatie."""
    raw = sys.stdin.read().strip()
    if not raw:
        die("geen invoer op stdin")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        die(f"ongeldige JSON op stdin: {exc}")

    new = payload if isinstance(payload, list) else [payload]
    schema = json.loads(SCHEMA.read_text())
    picks = load_picks()
    existing = {p.get("id") for p in picks}

    errors: list[str] = []
    for i, pick in enumerate(new, 1):
        pick.setdefault("result", RESULTS_OPEN)
        pick.setdefault("settled_at", None)
        where = f"invoer {i}"
        errors += validate_pick(pick, schema, where)
        errors += semantic_checks(pick, where)
        if pick.get("id") in existing:
            errors.append(f"{where}: id {pick['id']} bestaat al")

    if errors:
        for err in errors:
            print(err)
        die("niets toegevoegd")

    save_picks(picks + new)
    print(f"{len(new)} pick(s) toegevoegd; totaal {len(picks) + len(new)}.")
    return 0


def cmd_settle(args: argparse.Namespace) -> int:
    picks = load_picks()
    for pick in picks:
        if pick.get("id") == args.id:
            if pick.get("result") in RESULTS_CLOSED:
                die(f"{args.id} is al afgewikkeld als {pick['result']}")
            pick["result"] = args.result
            pick["settled_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if args.score:
                pick["settled_score"] = args.score
            if args.units is not None:
                pick["settled_units"] = args.units
            save_picks(picks)
            extra = f" ({args.units:+.2f}u)" if args.units is not None else ""
            print(f"{args.id} -> {args.result}{extra}")
            return 0
    die(f"pick niet gevonden: {args.id}")
    return 1


def cmd_open(args: argparse.Namespace) -> int:
    now = datetime.now(timezone.utc)
    rows = []
    for pick in load_picks():
        if pick.get("result") != RESULTS_OPEN:
            continue
        try:
            age_h = (now - parse_dt(pick["kickoff"])).total_seconds() / 3600
        except (KeyError, ValueError):
            age_h = float("nan")
        if age_h != age_h or age_h >= args.hours:  # NaN = onbekend: altijd tonen
            rows.append((age_h, pick))

    if not rows:
        print(f"Geen openstaande picks ouder dan {args.hours} uur.")
        return 0

    print(f"{len(rows)} pick(s) klaar om af te wikkelen:\n")
    for age_h, pick in sorted(rows, key=lambda r: -(r[0] if r[0] == r[0] else 0)):
        age = f"{age_h:5.1f}u" if age_h == age_h else "  ?  "
        print(f"  {age}  {pick['id']}")
        print(f"         {pick['home']} - {pick['away']} | {pick['market']}: {pick['selection']} @ {pick['odds']}")
    return 0


# --------------------------------------------------------------------- meten

def brier(pairs: list[tuple[float, int]]) -> float | None:
    return sum((p - o) ** 2 for p, o in pairs) / len(pairs) if pairs else None


def pick_units(pick: dict) -> float:
    """Netto resultaat van een afgewikkelde pick bij 1u inzet.

    Een kwartlijn (AH +0.25, Over 2.25) splitst in twee halve bets en kan dus half winnen of
    half verliezen. Dat past niet in won/lost/void, en het als hele win of heel verlies boeken
    vertekent de ROI — sinds 15 aug 2026 is Asian Handicap de grootste markt in het logboek, dus
    dat is geen randgeval meer. Staat er een expliciete `settled_units`, dan telt die.
    """
    units = pick.get("settled_units")
    if units is not None:
        return float(units)
    return pick["odds"] - 1 if pick["result"] == "won" else -1.0


def summarise(picks: list[dict], label: str) -> None:
    closed = [p for p in picks if p.get("result") in RESULTS_CLOSED]
    decided = [p for p in closed if p["result"] != "void"]
    won = [p for p in decided if p["result"] == "won"]

    pending = sum(1 for p in picks if p.get("result") == RESULTS_OPEN)
    print(f"\n{label}")
    print(f"  picks            {len(picks)}  ({pending} open, {len(closed)} afgewikkeld, "
          f"{len(closed) - len(decided)} void)")

    if not decided:
        print("  Nog geen beslist resultaat — hit rate, ROI en Brier volgen zodra er afgewikkeld is.")
        return

    profit = sum(pick_units(p) for p in decided)
    partials = [p for p in decided if p.get("settled_units") is not None]
    avg_edge = sum(p["edge_pp"] for p in decided) / len(decided)
    avg_odds = sum(p["odds"] for p in decided) / len(decided)

    print(f"  hit rate         {len(won)}/{len(decided)} = {100 * len(won) / len(decided):.1f}%")
    print(f"  ROI (1u flat)    {profit:+.2f}u over {len(decided)} bets = {100 * profit / len(decided):+.1f}%")
    if partials:
        print(f"  waarvan {len(partials)} halve uitkomst(en) op een kwartlijn, geboekt op hun "
              f"werkelijke inzetdeel")
    print(f"  gem. odds        {avg_odds:.2f}   gem. geclaimde edge {avg_edge:+.1f} pp")

    mine = brier([(p["my_prob"], 1 if p["result"] == "won" else 0) for p in decided])
    market = brier([(p["implied_prob"], 1 if p["result"] == "won" else 0) for p in decided])
    print(f"  Brier eigen      {mine:.4f}")
    print(f"  Brier markt      {market:.4f}   -> {'eigen model beter' if mine < market else 'markt beter'}"
          f" (verschil {market - mine:+.4f})")
    print("  Dit is de enige regel die echt zegt of de edge-schatting iets waard is:")
    print("  is Brier eigen niet lager dan Brier markt, dan voegt de analyse geen kansinformatie toe.")

    verwacht = sum(p["my_prob"] for p in decided)
    print(f"  kalibratie       verwacht {verwacht:.1f} winnaars, werkelijk {len(won)} "
          f"({len(won) - verwacht:+.1f})")


def cmd_stats(args: argparse.Namespace) -> int:
    picks = load_picks()
    if args.run:
        picks = [p for p in picks if p.get("run") == args.run]
    if not picks:
        print("Geen picks in het logboek. Nog niets te meten.")
        return 0

    summarise(picks, f"ALLE PICKS{f' (run {args.run})' if args.run else ''}")

    for field, values in (("data_tier", ("FULL", "LIGHT")),
                          ("confidence", ("High", "Medium", "Low"))):
        for value in values:
            subset = [p for p in picks if p.get(field) == value]
            if subset:
                summarise(subset, f"{field} = {value}")

    short = [p for p in picks if p.get("shortlisted")]
    if short:
        summarise(short, "alleen topselectie")
    return 0


# ----------------------------------------------------------------------- cli

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("validate", help="controleer picks.jsonl tegen schema en regels")
    sub.add_parser("add", help="voeg pick(s) toe vanaf stdin (JSON-object of -lijst)")

    p_open = sub.add_parser("open", help="toon picks die afgewikkeld moeten worden")
    p_open.add_argument("--hours", type=float, default=12,
                        help="minimale leeftijd sinds aftrap (standaard 12)")

    p_settle = sub.add_parser("settle", help="leg de uitkomst van een pick vast")
    p_settle.add_argument("id")
    p_settle.add_argument("result", choices=RESULTS_CLOSED)
    p_settle.add_argument("--score", help="eindstand, bv. 2-1")
    p_settle.add_argument("--units", type=float, default=None,
                          help="netto eenheden bij 1u inzet, alleen bij een halve uitkomst op een "
                               "kwartlijn (half verlies = -0.5, half winst = (odds-1)/2)")

    p_stats = sub.add_parser("stats", help="hit rate, ROI, Brier en kalibratie")
    p_stats.add_argument("--run", choices=("A", "B"))

    args = parser.parse_args()
    return {"validate": cmd_validate, "add": cmd_add, "settle": cmd_settle,
            "open": cmd_open, "stats": cmd_stats}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())

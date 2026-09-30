#!/usr/bin/env python3
"""Klopt elk `fotmob_id` in `data/coverage.json` nog? Stage 3 van _shared-rules.md.

**Waarom dit bestaat (Run B, 29 sep 2026).** Stage 1 matcht competities op **id** en nooit op
naam — `runwindow.matches_for_run` documenteert dat met redenen (de Tsjechische beker heeft
`ccode = CZE`, de Braziliaanse Série B heet bijna hetzelfde als Série A). Die keuze is goed, maar
ze heeft een stille faalstand die niemand had gezien:

> Een verkeerd id levert geen foutmelding. Het levert nul wedstrijden, en nul wedstrijden is
> `GEEN WEDSTRIJD` — een volkomen normale uitkomst die elke dag tientallen keren in het
> runrapport staat.

Precies dat is gebeurd. `Serie B (ITA)` stond van de Run B van **17 september** tot en met die van
20 september op `56` in plaats van `86`. Id 56 is bij Fotmob "Serie B Qualification" en heeft
helemaal geen stand; id 86 is de echte Serie B, met xG voor alle twintig ploegen. De competitie
verdween daardoor uit de runlijst zonder één foutregel, en het kostte **tien duels**: 18 september
1, 19 september 5 en 20 september 4. Dat het daarna niet meer opviel, komt doordat het
interlandvenster van eind september begon — Serie B speelt weer op 9 oktober, en zonder deze
controle was de eerste run die dat merkt de run van 9 oktober geweest.

Waarom Stage 3 het niet ving: die haalt `fetch_league_stats` alleen op voor competities die
**wedstrijden in het venster hebben**. Bij een fout id zijn er geen wedstrijden, dus werd de
stand nooit opgevraagd en kon het kapotte id geen fout geven. De controle moet dus juist op de
competities draaien die vandaag níet spelen — het omgekeerde van wat Stage 3 doet.

    python3 scripts/idcheck.py            # alle competities met een fotmob_id
    python3 scripts/idcheck.py --quiet    # alleen de regels die fout zijn

Afsluitcode 0 = alles in orde, 1 = minstens één id levert geen bruikbare stand. Neem de uitvoer
op in het runrapport onder "Bronstatus deze run".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COVERAGE = ROOT / "data" / "coverage.json"

#: Welk seizoen we opvragen om te toetsen dat het id een stand heeft. Het laatst **afgeronde**
#: seizoen, want daar komen de teamsterktes uit (§4) en dat is het seizoen dat altijd gevuld is —
#: een lopend seizoen kan op speeldag 0 staan en dan zegt een lege stand niets over het id.
SEASONS = ("2025/2026", "2025")

# `python3 scripts/idcheck.py` draait dit bestand als script, en dan staat `scripts/` op
# `sys.path` in plaats van de repowortel — `from scripts import fotmob` valt dan om met
# ModuleNotFoundError. Run B van 30 sep 2026 liep daar op vast. Dat is hier niet alleen
# hinderlijk: afsluitcode 1 betekent volgens run-b.md "er is een competitie stil uit de
# runlijst verdwenen", en een importfout geeft diezelfde 1. Een kapotte controle zag er dus
# precies uit als de vondst waarvoor de controle is gebouwd.
sys.path.insert(0, str(ROOT))


def check_one(league_id: int) -> tuple[bool, str]:
    """`(ok, toelichting)` voor één id. Probeert beide seizoensnotaties (§ run-b.md: vier
    competities lopen op kalenderjaar en kennen `2025/2026` niet)."""
    from scripts import fotmob

    errors = []
    for season in SEASONS:
        try:
            stats = fotmob.fetch_league_stats(league_id, season, use_cache=False)
        except Exception as exc:                     # noqa: BLE001 - elke fout is hier "geen stand"
            errors.append(f"{season}: {type(exc).__name__}: {exc}")
            continue
        teams = stats.get("teams") or {}
        if not teams:
            errors.append(f"{season}: stand leeg")
            continue
        has_xg = any("xg" in t for t in teams.values())
        return True, f"{len(teams)} ploegen in {season}, xG={has_xg}"
    return False, " | ".join(errors)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quiet", action="store_true", help="alleen de kapotte id's afdrukken")
    args = ap.parse_args(argv)

    coverage = json.loads(COVERAGE.read_text())
    entries = {
        name: entry["fotmob_id"]
        for name, entry in (coverage.get("competitions") or {}).items()
        if isinstance(entry, dict) and entry.get("fotmob_id") is not None
    }
    if not entries:
        print("Geen enkele competitie in coverage.json heeft een fotmob_id. Niets te controleren.")
        return 0

    bad: list[tuple[str, int, str]] = []
    for name, league_id in sorted(entries.items()):
        ok, note = check_one(int(league_id))
        if ok:
            if not args.quiet:
                print(f"OK   {name:32s} id={league_id:<6} {note}")
        else:
            bad.append((name, int(league_id), note))
            print(f"FOUT {name:32s} id={league_id:<6} {note}")

    print()
    if bad:
        print(f"{len(bad)} van de {len(entries)} id's levert geen bruikbare stand. "
              f"Een fout id levert GEEN foutmelding in Stage 1 maar een stille `GEEN WEDSTRIJD` "
              f"— repareer dit vóór de volgende run en meld het in de notificatie.")
        return 1
    print(f"Alle {len(entries)} id's uit coverage.json leveren een bruikbare stand.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

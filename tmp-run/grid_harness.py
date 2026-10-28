"""Meetharnas voor de vormfout in `score_grid` (§6g, keuze (a) van 11 okt 2026).

Doel: één keer de lambdaparen uit `data/run-state/` en de werkelijke uitslagen uit Fotmob
ophalen en in `tmp-run/grid_data.json` zetten, zodat elke kandidaat-reparatie daarna zonder
netwerk en zonder credits te meten is.

Dit bestand MEET en WIJZIGT NIETS. De keuze tussen varianten gebeurt in `grid_fit.py`, op
uitkomsten en niet op een redenering (§6g: de vormfout is tegen uitslagen gemeten, dus §2 staat
een correctie toe — maar dan wel op diezelfde maatstaf).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import margins

OUT = Path("tmp-run/grid_data.json")


def main() -> int:
    rows = margins.load_matches()
    print(f"{len(rows)} wedstrijden met een opgeslagen lambdapaar in data/run-state/")
    with_res, miss = margins.attach_results(rows)
    print(f"{len(with_res)} met een werkelijke eindstand, {miss} zonder (nog niet gespeeld of niet gevonden)")
    OUT.write_text(json.dumps(with_res, ensure_ascii=False))
    print(f"-> {OUT} ({OUT.stat().st_size // 1024} KB)")

    # Snelle sanity: dekt dit de 1717 duels van `margins.py goalbias` van vandaag?
    per_dag: dict[str, int] = {}
    for r in with_res:
        per_dag[r["date"]] = per_dag.get(r["date"], 0) + 1
    print(f"dagen: {len(per_dag)}, van {min(per_dag)} t/m {max(per_dag)}")
    na_shrink = sum(n for d, n in per_dag.items() if d >= "2026-09-20")
    print(f"waarvan lambdas van ná de shrink-overstap (>= 2026-09-20): {na_shrink}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

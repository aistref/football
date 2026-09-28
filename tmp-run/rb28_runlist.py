"""Stage 1 — Run B 28 sep 2026: welke duels horen bij het inzetvenster van vandaag."""
import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 9, 28)
RUNLIST = {
    "Czech First League (CZE)": 122,
    "Greek Super League (GRE)": 135,
    "Eliteserien (NOR)": 59,
    "Allsvenskan (SWE)": 67,
    "Croatian HNL (CRO)": 252,
    "Hungarian NB I (HUN)": 212,
    "Romanian SuperLiga (ROU)": 189,
    "Segunda División (ESP)": 140,
    "Serie B (ITA)": 56,
    "2. Bundesliga (GER)": 146,
    "Swiss Super League (SUI)": 69,
    "Austrian Bundesliga (AUT)": 38,
    "Keuken Kampioen Divisie (NED)": 111,
    "English League One (ENG)": 108,
    "English League Two (ENG)": 109,
    "MLS (USA)": 130,
    "Série A (BRA)": 268,
}

fixtures = {}
for d in days_needed(DAY):
    try:
        fixtures[d] = fotmob.fetch_fixtures(d)
        print(f"daglijst {d}: ok")
    except Exception as exc:
        print(f"daglijst {d}: FOUT {type(exc).__name__}: {exc}")

per_comp = matches_for_run(DAY, fixtures, RUNLIST)
out = {}
for name, ms in per_comp.items():
    out[name] = [m.as_dict() for m in ms]
    if ms:
        print(f"\n{name} ({len(ms)}):")
        for m in ms:
            print(f"   {m.home} – {m.away}  {m.kickoff_nl} NL  daglijst={m.source_day} playable={m.playable} id={m.match_id}")
    else:
        print(f"\n{name}: GEEN WEDSTRIJD")
json.dump(out, open("tmp-run/rb28_matches.json", "w"), ensure_ascii=False, indent=1)
print("\ntotaal duels:", sum(len(v) for v in out.values()))

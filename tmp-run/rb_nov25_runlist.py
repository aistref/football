"""Stage 1+2 - Run B 25 nov 2026: welke duels van de runlijst vallen in het inzetvenster?
Venster: [08:00 NL 24 nov, 08:00 NL 25 nov). Twee daglijsten (days_needed)."""
import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 11, 25)
COV = json.load(open("data/coverage.json"))

RUNLIST_NAMES = [
    "Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
    "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
    "Romanian SuperLiga (ROU)", "Segunda División (ESP)", "Serie B (ITA)",
    "2. Bundesliga (GER)", "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
    "Keuken Kampioen Divisie (NED)", "English League One (ENG)", "English League Two (ENG)",
    "MLS (USA)", "Série A (BRA)",
]
comps = COV["competitions"] if "competitions" in COV else COV
RUNLIST = {}
for n in RUNLIST_NAMES:
    entry = comps.get(n)
    if entry is None:
        raise SystemExit(f"NIET IN coverage.json: {n}")
    RUNLIST[n] = entry["fotmob_id"]
print("id's uit coverage.json:", json.dumps(RUNLIST, ensure_ascii=False))

fixtures = {d: fotmob.fetch_fixtures(d) for d in days_needed(DAY)}
print("daglijsten:", [str(d) for d in fixtures])
per_comp = matches_for_run(DAY, fixtures, RUNLIST)

out = {}
for naam, _id in RUNLIST.items():
    ms = per_comp.get(naam, [])
    out[naam] = [m.as_dict() for m in ms]
    print(f"{naam:32s} {len(ms)}")

alle = {}
for d, fx in fixtures.items():
    for lg in fx.get("leagues", []):
        k = f'{lg.get("name")} [{lg.get("primaryId") or lg.get("id")}] ({lg.get("ccode")})'
        alle[k] = alle.get(k, 0) + len(lg.get("matches", []))
json.dump({"runlijst": out, "ids": RUNLIST, "daglijst_alle_competities": alle},
          open("tmp-run/rb_nov25_runlist.json", "w"), ensure_ascii=False, indent=1)
print("\ntotaal duels in venster:", sum(len(v) for v in out.values()))

"""Run B, 25 sep 2026 — de vijftien competities zonder wedstrijd in het voortgangsbestand zetten.

§5 eist een dekkingstabel met **elke** competitie uit de runlijst en precies één status. Zonder
deze stap staan alleen de twee geanalyseerde competities in `data/run-state/` en leest de
dekkingstabel op de HTML-pagina als een runlijst van twee — "doe niet alsof de dekking volledig is
als dat niet zo is" geldt ook omgekeerd.
"""
import json
from datetime import date
from scripts.progress import load_or_start, mark, save

DAG = date(2026, 9, 25)
RUNLIST = [
    "Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
    "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
    "Romanian SuperLiga (ROU)", "Segunda División (ESP)", "Serie B (ITA)",
    "2. Bundesliga (GER)", "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
    "Keuken Kampioen Divisie (NED)", "English League One (ENG)", "English League Two (ENG)",
    "MLS (USA)", "Série A (BRA)",
]

s3 = json.load(open("tmp-run/rb25_stage3.json"))
state = load_or_start("b", DAG)
for comp in RUNLIST:
    if comp in state.get("competitions", {}):
        continue
    st = s3["fixtures"].get(comp, {}).get("status", "GEEN WEDSTRIJD")
    mark(state, comp, {"status": "GEEN WEDSTRIJD" if st == "GEEN WEDSTRIJD" else st,
                       "matches": [],
                       "note": "geen wedstrijd in het inzetvenster [08:00 NL 25 sep, 08:00 NL "
                               "26 sep) — runwindow.matches_for_run over de daglijsten van 25 en "
                               "26 september"})
save(state)
print("competities in het voortgangsbestand:", len(state["competitions"]))
for c, v in state["competitions"].items():
    print(f"  {v['status']:20s} {c}")

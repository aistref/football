"""§5 Dekkingsrapportage: elke competitie uit de runlijst krijgt precies één status.

`rb30_publiceer.py` schrijft alleen de competities die wedstrijden hadden. De dekkingstabel van
§5 eist een regel voor álle zeventien — "doe niet alsof de dekking volledig is als dat niet zo
is" geldt ook omgekeerd: zestien competities die vandaag niet spelen horen zichtbaar als
GEEN WEDSTRIJD in de tabel, want anders leest een tabel met één regel als een runlijst van één.
"""
import json
from datetime import date
from scripts.progress import load_or_start, mark, save

s3 = json.load(open("tmp-run/rb30_stage3.json"))
state = load_or_start("b", date(2026, 9, 30))
n = 0
for comp, v in s3["fixtures"].items():
    if comp in state.get("done", {}) or comp in state.get("competitions", {}):
        continue
    if v["status"] == "GEEN WEDSTRIJD":
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        n += 1
save(state)
print(f"{n} competitie(s) als GEEN WEDSTRIJD vastgelegd")
st = json.load(open(f"data/run-state/2026-09-30-run-b.json"))
key = "done" if "done" in st else "competitions"
print("statussen:", {k: (v.get("status") if isinstance(v, dict) else v) for k, v in st[key].items()})

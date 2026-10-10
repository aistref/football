"""De vijf bekers in de dekkingstabel van de run-state zetten.

`ra_oct10_publiceer.py` vult de tabel uit `ra_oct10_stage3.json`, en daar staan alleen de
zestien competities MET een fotmob_id in. §5 eist een tabel met **elke** competitie uit de
runlijst en precies één status, dus de vijf bekers horen er ook in — met de bron erbij waarmee
ze zijn nagelopen, want "niet in de Fotmob-daglijst" is voor hen geen uitspraak (zie
`ra_oct10_cups.py`).
"""
import json
from datetime import date
from scripts.progress import load_or_start, mark, save

DAG = date(2026, 10, 10)
cups = json.load(open("tmp-run/ra_oct10_cups.json"))["cups"]
state = load_or_start("a", DAG)
for naam, v in cups.items():
    assert v["status"] == "GEEN WEDSTRIJD", f"{naam} heeft duels in het venster: {v['in_venster']}"
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "bron": ("geen fotmob_id in coverage.json, dus niet via de Fotmob-daglijst te filteren; "
                 f"nagelopen op BetExplorer ({v['slug']}): {v['teamparen']} teamparen, "
                 f"{v['koersen']} koersen, 0 in het inzetvenster"),
        "eerstvolgende_ronde": v["eerste_ronde"],
        "afgekeurde_slugs": v["afgekeurde_slugs"],
    })
save(state)
print(f"run-state bijgewerkt: {len(state['competitions'])} competities")
for n, b in state["competitions"].items():
    print(f"  {n:30s} {b['status']}")

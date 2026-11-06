"""Voeg de FA Cup toe aan de Stage 3-uitvoer van 6 nov 2026.

`ra_nov06_stage3.py` filtert de daglijst op de id's uit `coverage.json`, en de FA Cup heeft daar
geen `fotmob_id` (een beker heeft geen stand, dus `idcheck.py` zou er een vals alarm op geven).
`ra_nov06_facup.py` heeft hem met id **132** wél in de daglijst gevonden, en BetExplorer noemt
exact dezelfde twee duels — bevestiging door een tweede bron (§1, en het gat dat Run A op
6 oktober vijf duels kostte).

`primaryId` wordt hier de BASISDIVISIE (Premier League, id 47, uit `promotion.CUP_BASE`) en niet
132: `ra_nov06_cand.py` zoekt de ploegen op in de stand van die basis, en vindt het de divisie
eronder via `promotion.shared_lower_division` (§4, "In een beker ligt de basis per WEDSTRIJD").
"""
import json
from scripts import promotion

s3 = json.load(open("tmp-run/ra_nov06_stage3.json"))
fa = json.load(open("tmp-run/ra_nov06_facup.json"))

base = promotion.CUP_BASE["FA Cup (ENG)"]                 # "Premier League (ENG)"
base_id = json.load(open("data/coverage.json"))["competitions"][base]["fotmob_id"]

s3["fixtures"]["FA Cup (ENG)"] = {
    "status": "?",
    "primaryId": base_id,
    "fotmob_id_toernooi": fa["fotmob_id"],
    "betexplorer": "https://www.betexplorer.com/football/england/fa-cup/fixtures/",
    "sportkey": None,                  # soccer_england_fa_cup is vandaag niet actief (api_check)
    "understat": None,
    "s_prev": "2025/2026",
    "s_cur": "2026/2027",
    "crossborder": False,
    "cup": True,
    "basis": base,
    "matches": fa["matches"],
}
s3["cups"] = [c for c in s3["cups"] if c != "FA Cup (ENG)"]
s3.setdefault("cup_bron", {})["FA Cup (ENG)"] = (
    "Fotmob-daglijst id 132 (2 duels) EN BetExplorer /england/fa-cup/fixtures/ (2 duels in het "
    "venster) — twee bronnen, zelfde twee duels, zelfde aftraptijden")

json.dump(s3, open("tmp-run/ra_nov06_stage3.json", "w"), ensure_ascii=False, indent=1)
print("FA Cup toegevoegd, basis:", base, base_id)
print("actief nu:", [k for k, v in s3["fixtures"].items() if v["status"] == "?"])
print("totaal wedstrijden:", sum(len(v["matches"]) for v in s3["fixtures"].values()))

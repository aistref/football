import json
from datetime import datetime, timezone

competitions = json.load(open("tmp-run/rc04_competitions.json"))

state = {
    "run": "C",
    "date": "2026-10-04",
    "resumed_count": 0,
    "competitions": competitions,
    "completed": False,
    "duur": {
        "gestart": "2026-10-04T03:16:00+00:00",
        "afgerond": None,
        "minuten": None,
    },
    "parameters": {
        "MAX_DEEP_ANALYSES": 40,
        "MAX_SHORTLIST": 5,
        "dag_type": "weekend (zondag)",
        "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": "n.v.t. voor Run C (run-c.md, 24 sep 2026)",
    },
    "credits": {
        "markten_gekocht": {
            "soccer_uefa_nations_league": ("bulk h2h+spreads+totals (3 credits); BTTS per duel voor 2 kandidaat-duels "
                "(Nederland–Servië, Ierland–Israël), 4 credits"),
            "betexplorer": "1X2-marktgemiddelde voor oefeninterlands, CONCACAF NL, AFCON-kwal, ASEAN (gratis)",
        },
        "totaal_credits": 7,
    },
    "uitgesloten_competities": {
        "489": "Club Friendlies — clubteams (Dinamo Moskou–Rodina, CSKA–Arsenal Toela, Hamburger SV–FC København, Molde–Kristiansund, Zenit–BATE; 5 duels in het venster)",
        "344": "Friendlies U21 — U21 (0 duels in het venster)",
        "10437": "EURO U21 Qualification — U21 (0 duels in het venster)",
    },
}
json.dump(state, open("data/run-state/2026-10-04-run-c.json", "w"), indent=1, ensure_ascii=False)
print("weggeschreven.")

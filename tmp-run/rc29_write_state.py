import json
from datetime import datetime, timezone

competitions = json.load(open("tmp-run/rc29_competitions.json"))

state = {
    "run": "C",
    "date": "2026-09-29",
    "resumed_count": 0,
    "competitions": competitions,
    "completed": False,
    "duur": {
        "gestart": "2026-09-29T03:18:02+00:00",
        "afgerond": None,
        "minuten": None,
    },
    "parameters": {
        "MAX_DEEP_ANALYSES": 40,
        "MAX_SHORTLIST": 3,
        "dag_type": "doordeweeks (dinsdag)",
        "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": "n.v.t. voor Run C (run-c.md, 24 sep 2026)",
    },
    "credits": {
        "markten_gekocht": {
            "1X2/AH/DNB/DC/OU (bulk h2h+spreads+totals)": (
                "soccer_uefa_nations_league, 10 events van vandaag in het venster (Czechia-England, "
                "Spain-Croatia, Scotland-Switzerland, Slovenia-North Macedonia, Finland-Belarus, "
                "San Marino-Albania, Moldova-Faroe Islands, Slovakia-Kazakhstan, Bulgaria-Estonia, "
                "Luxembourg-Iceland) — 3 credits"
            ),
            "BTTS + Double Chance per-wedstrijd": (
                "7 duels met kandidaat-edge — 2 credits elk = 14"
            ),
        },
        "totaal_credits": 17,
    },
    "uitgesloten_competities": {
        "489": "Club Friendlies — clubteams, niet landenteams (run-c.md: NIET gebruiken); 0 duels in het venster",
        "9833": "Asian Games — U23 (30 sep, buiten het venster én jeugd)",
        "10437": "EURO U21 Qualification — U21 (6 duels in het venster, o.a. Iceland U21 – Switzerland U21)",
        "9375": "Women's Champions League — Women (0 duels in het venster)",
        "11129": "UEFA Women's Europa Cup — Women (0 duels in het venster)",
    },
}
json.dump(state, open("data/run-state/2026-09-29-run-c.json", "w"), indent=1, ensure_ascii=False)
print("weggeschreven.")

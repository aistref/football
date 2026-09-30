import json
from datetime import datetime, timezone

competitions = json.load(open("tmp-run/rc30_competitions.json"))

state = {
    "run": "C",
    "date": "2026-09-30",
    "resumed_count": 0,
    "competitions": competitions,
    "completed": False,
    "duur": {
        "gestart": "2026-09-30T03:18:02+00:00",
        "afgerond": None,
        "minuten": None,
    },
    "parameters": {
        "MAX_DEEP_ANALYSES": 40,
        "MAX_SHORTLIST": 3,
        "dag_type": "doordeweeks (woensdag)",
        "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": "n.v.t. voor Run C (run-c.md, 24 sep 2026)",
    },
    "credits": {
        "markten_gekocht": {
            "geen": ("geen enkele competitie in het venster had een sportkey bij The Odds API "
                     "(soccer_uefa_nations_league heeft vandaag geen duel in het venster: alle NL-duels "
                     "zijn op 1 okt 18:45 UTC, buiten [08:00 NL 30 sep, 08:00 NL 1 okt)); alleen BetExplorer 1X2, gratis"),
        },
        "totaal_credits": 0,
    },
    "uitgesloten_competities": {
        "489": "Club Friendlies — clubteams (DC United – Paderborn, 1 duel in het venster)",
        "9833": "Asian Games — U23 (2 duels in het venster)",
        "10437": "EURO U21 Qualification — U21 (8 duels in het venster)",
        "9375": "Women's Champions League — Women (5 duels in het venster)",
        "11129": "UEFA Women's Europa Cup — Women (16 duels in het venster)",
    },
}
json.dump(state, open("data/run-state/2026-09-30-run-c.json", "w"), indent=1, ensure_ascii=False)
print("weggeschreven.")

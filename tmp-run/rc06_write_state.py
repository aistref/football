import json
from datetime import datetime, timezone

competitions = json.load(open("tmp-run/rc06_competitions.json"))

state = {
    "run": "C",
    "date": "2026-10-06",
    "resumed_count": 0,
    "competitions": competitions,
    "completed": False,
    "duur": {
        "gestart": "2026-10-06T03:18:02+00:00",
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
            "soccer_uefa_nations_league": ("bulk h2h+spreads+totals (3 credits); BTTS+double_chance per duel voor 5 kandidaat-duels (10 credits)"),
        },
        "totaal_credits": 13,
    },
    "uitgesloten_competities": {
        "489": "Club Friendlies — clubteams (IFK Norrköping – Kalmar FF, 1 duel in het venster)",
        "10437": "EURO U21 Qualification — U21 (21 duels in het venster)",
    },
}
json.dump(state, open("data/run-state/2026-10-06-run-c.json", "w"), indent=1, ensure_ascii=False)
print("weggeschreven.")

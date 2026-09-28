import json
from datetime import datetime, timezone

competitions = json.load(open("tmp-run/rc28_competitions.json"))

state = {
    "run": "C",
    "date": "2026-09-28",
    "resumed_count": 0,
    "competitions": competitions,
    "completed": False,
    "duur": {
        "gestart": "2026-09-28T03:18:13.923890+00:00",
        "afgerond": None,
        "minuten": None,
    },
    "parameters": {
        "MAX_DEEP_ANALYSES": 40,
        "MAX_SHORTLIST": 3,
        "dag_type": "doordeweeks (maandag)",
        "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": "n.v.t. voor Run C (run-c.md, 24 sep 2026)",
    },
    "credits": {
        "markten_gekocht": {
            "1X2/AH/DNB/DC/OU (bulk h2h+spreads+totals)": (
                "soccer_uefa_nations_league, 8 events (Armenia-Montenegro, Latvia-Cyprus, "
                "Georgia-Ukraine, Belgium-France, Romania-Bosnia and Herzegovina, "
                "Northern Ireland-Hungary, Turkiye-Italy, Sweden-Poland) — 3 credits"
            ),
            "BTTS + Double Chance per-wedstrijd": (
                "4 duels met kandidaat-edge (Belgium-France, Turkiye-Italy, Sweden-Poland, "
                "Armenia-Montenegro) — 2 credits elk = 8"
            ),
        },
        "totaal_credits": 11,
    },
    "uitgesloten_competities": {
        "489": "Club Friendlies — clubteams, niet landenteams (run-c.md: NIET gebruiken)",
        "10369": "Women's World Cup U20 — Women + U20 (niet op de daglijst van vandaag)",
        "10437": "EURO U21 Qualification — U21 (Denmark U21 - Belarus U21, 18:30 NL)",
    },
}

json.dump(state, open("data/run-state/2026-09-28-run-c.json", "w"), indent=1, ensure_ascii=False)
print("weggeschreven.")

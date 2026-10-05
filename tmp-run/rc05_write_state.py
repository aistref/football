import json
from datetime import datetime, timezone

competitions = json.load(open("tmp-run/rc05_competitions.json"))

state = {
    "run": "C",
    "date": "2026-10-05",
    "resumed_count": 0,
    "competitions": competitions,
    "completed": False,
    "duur": {
        "gestart": "2026-10-05T03:16:00+00:00",
        "afgerond": None,
        "minuten": None,
    },
    "parameters": {
        "MAX_DEEP_ANALYSES": 40,
        "MAX_SHORTLIST": 3,
        "dag_type": "weekdag (maandag)",
        "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": "n.v.t. voor Run C (run-c.md, 24 sep 2026)",
    },
    "credits": {
        "markten_gekocht": {
            "soccer_uefa_nations_league": ("bulk h2h+spreads+totals (3 credits); BTTS+double_chance per duel voor 5 kandidaat-duels (10 credits)"),
            "betexplorer": "1X2-marktgemiddelde voor oefeninterlands, CONCACAF NL, AFCON-kwal, ASEAN (gratis)",
        },
        "totaal_credits": 13,
    },
    "uitgesloten_competities": {
        "344": "Friendlies U21 — U21 (2 duels in het venster: Oekraïne U21–Albanië U21, Servië U21–Rusland U21)",
        "10437": "EURO U21 Qualification — U21 (3 duels in het venster: Montenegro U21–Armenië U21, Italië U21–Polen U21, Zweden U21–Noord-Macedonië U21)",
    },
}
json.dump(state, open("data/run-state/2026-10-05-run-c.json", "w"), indent=1, ensure_ascii=False)
print("weggeschreven.")

"""Run A, 21 sep 2026 — run-state wegschrijven.

Bijzonder geval: geen enkele competitie uit de runlijst speelt vandaag. Stage 2 zegt dat dat
`GEEN WEDSTRIJD` is en geen storing, maar `find_league` geeft `None` ook terug als een naam niet
matcht — dus is het met een tweede bron nagetrokken (zie `bevestiging` hieronder) voordat het
als leeg is genoteerd.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking

DAY = date(2026, 9, 21)
STAGE3 = json.load(open("tmp-run/ra21_stage3.json"))

state = load_or_start("a", DAY)

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd op de Fotmob-daglijst van 21 sep 2026; bevestigd met BetExplorer",
    })

state["parameters"] = {
    "MAX_DEEP_ANALYSES": ranking.max_deep_analyses(DAY),
    "MAX_SHORTLIST": ranking.max_shortlist(DAY),
    "EDGE_THRESHOLD_FULL": 8.0,
    "EDGE_THRESHOLD_LIGHT": 16.0,
    "MAX_LIGHT_IN_SHORTLIST": 2,
    "MIN_ODDS": 1.30,
    "MAX_ODDS": 6.00,
    "SHRINK": 1.00,
    "XG_WEIGHT": 0.80,
    "CREDIBILITY_K": 8,
    "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
    "afgekapt": 0,
    "afkapping": {"cap": ranking.max_deep_analyses(DAY), "afgekapt": 0,
                  "laagste_die_het_haalde": None, "hoogste_die_afviel": None, "lijst": [],
                  "reden": "0 wedstrijden in de runlijst, dus de cap bond nergens"},
    "HERIJKING": "niet toegepast — er is geen wedstrijd doorgerekend. De fit zelf is wel gelezen "
                 "en staat in het runrapport onder 'Stand van het logboek'.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1": "Fotmob-daglijst 21 sep 2026: 37 competities, 68 wedstrijden, geen enkele uit de "
                 "runlijst. De grote competities ontbreken volledig in het antwoord — het is dus "
                 "geen naamkwestie (find_league kan None geven bij een afwijkende naam), want dan "
                 "zou de competitie er wél staan onder een andere naam.",
    "methode_2": "BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 "
                 "komende duels, Eredivisie 18, Serie A 10 — en geen daarvan staat op vandaag. "
                 "De eerstvolgende speelronde staat bij alle drie op 9/10 oktober.",
    "conclusie": "Beide bronnen zeggen hetzelfde: de hoogste divisies liggen stil. GEEN WEDSTRIJD "
                 "is de uitkomst, geen storing (Stage 2).",
    "context": "De daglijsten van 21 sep t/m 6 okt laten lagere divisies gewoon doorspelen "
               "(26 sep: 469 duels, 3 okt: 444) terwijl geen enkele runlijstcompetitie "
               "voorkomt, en het aandeel interland- en INT-duels loopt in die periode op. Dat "
               "past bij een interlandperiode; die hoort bij Run C en niet bij Run A.",
}

state["duur"] = {
    "gestart": "2026-09-21T02:15:00+00:00",
    "afgerond": datetime.now(timezone.utc).isoformat(),
}

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})

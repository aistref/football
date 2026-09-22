"""Run A, 22 sep 2026 — run-state wegschrijven.

Tweede dag op rij dat geen enkele competitie uit de runlijst speelt. Stage 2 zegt dat dat
`GEEN WEDSTRIJD` is en geen storing, maar `find_league` geeft `None` ook terug als een naam niet
matcht — dus opnieuw met een tweede bron nagetrokken (zie `bevestiging`) in plaats van de
conclusie van gisteren over te nemen.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking

DAY = date(2026, 9, 22)
STAGE3 = json.load(open("tmp-run/ra22_stage3.json"))
BEV = json.load(open("tmp-run/ra22_bevestiging.json"))

state = load_or_start("a", DAY)

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd op de Fotmob-daglijst van 22 sep 2026; bevestigd met BetExplorer",
        "eerstvolgende_betexplorer": (BEV.get(naam) or {}).get("eerste"),
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

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. "
             "The Odds API staat op 18.763 van de 20.000 over (api_check.py).",
    "marktbalans": "niet van toepassing — er is niets ingekocht. §1a eist minstens één "
                   "doelpunten- en één uitkomstmarkt zodra er wél wordt ingekocht.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1": "Fotmob-daglijst 22 sep 2026: 40 competities, 111 wedstrijden, geen enkele uit "
                 "de runlijst. De hoogste divisies ontbreken volledig in het antwoord — het is "
                 "dus geen naamkwestie (find_league geeft None ook bij een afwijkende naam), "
                 "want dan zou de competitie er wél staan onder een andere naam. Wat er wél "
                 "speelt: EFL Trophy (23 duels), Scottish Challenge Cup (18), Engelse regionale "
                 "divisies (22), Women's Champions League (5), Asian Games (3).",
    "methode_2": "BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 "
                 "komende duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Eredivisie "
                 "18, Championship 12, Scottish Premiership 12, Danish Superliga 6 — nul daarvan "
                 "op vandaag. Eerstvolgende speelronde 9/10 oktober; UCL 13 okt, UEL en UECL "
                 "15 okt, League Cup 27 okt.",
    "conclusie": "Beide bronnen zeggen hetzelfde: de hoogste divisies liggen stil. GEEN WEDSTRIJD "
                 "is de uitkomst, geen storing (Stage 2).",
    "context": "Tweede dag op rij. De daglijst is met 111 duels ruim twee keer zo vol als "
               "gisteren (68), maar uitsluitend met lagere divisies, bekertoernooien en "
               "vrouwen- en interlandvoetbal. Dat past bij een interlandperiode; die hoort bij "
               "Run C en niet bij Run A.",
}

state["duur"] = {
    "gestart": "2026-09-22T02:18:00+00:00",
    "afgerond": datetime.now(timezone.utc).isoformat(),
}

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})

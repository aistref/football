"""Run A, 23 sep 2026 — run-state wegschrijven.

Derde dag op rij zonder wedstrijd in de runlijst. Stage 2 noemt dat `GEEN WEDSTRIJD` en geen
storing, maar `find_league` geeft `None` ook terug bij een afwijkende naam — dus opnieuw met een
tweede bron nagetrokken in plaats van de conclusie van gisteren over te nemen.

Nieuw ten opzichte van 22 sep is wat de tweede bron laat zien zodra je niet alleen naar vandaag
kijkt maar naar de eerstvolgende speelronde: die ligt voor de héle runlijst op 9–13 oktober. De
stilte is dus geen losse dag maar een aaneengesloten interlandperiode van ruim twee weken, en dat
is iets wat de gebruiker hoort te weten voordat hij zich elke ochtend afvraagt of de routine nog
loopt.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking

DAY = date(2026, 9, 23)
STAGE3 = json.load(open("tmp-run/ra23_stage3.json"))
BEV = json.load(open("tmp-run/ra23_bevestiging.json"))

state = load_or_start("a", DAY)

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd op de Fotmob-daglijst van 23 sep 2026; bevestigd met BetExplorer",
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
    "methode_1": "Fotmob-daglijst 23 sep 2026: 28 competities, 83 wedstrijden, geen enkele uit de "
                 "runlijst. Wat er wél speelt is interland- en lager voetbal: vriendschappelijke "
                 "interlands, CONCACAF Nations League C, Asian Games, Gulf Cup, de Nigeriaanse "
                 "NPFL (10), UEFA Women's Europa Cup (15), Women's Champions League (4) en een "
                 "reeks nationale bekers. De hoogste divisies ontbreken volledig — het is dus "
                 "geen naamkwestie, want bij een afwijkende naam zou de competitie er wél staan.",
    "methode_2": "BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 "
                 "komende duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Eredivisie "
                 "18, Championship 12, Scottish Premiership 12, Primeira Liga 9, Pro League 9, "
                 "Süper Lig 9, Danish Superliga 6, UCL/UEL/UECL elk 18, League Cup 8 — nul "
                 "daarvan op vandaag.",
    "conclusie": "Beide bronnen zeggen hetzelfde: de hoogste divisies liggen stil. GEEN WEDSTRIJD "
                 "is de uitkomst, geen storing (Stage 2).",
    "context": "Derde dag op rij. Nieuw is wat de tweede bron over de kalender zegt: de "
               "eerstvolgende speelronde ligt voor de hele runlijst op 9–13 oktober (La Liga, "
               "Championship, Eredivisie, Primeira Liga, Pro League, Süper Lig en Danish "
               "Superliga op 9 okt; PL, Serie A, Bundesliga, Ligue 1 en Scottish Premiership op "
               "10 okt; UCL 13 okt, UEL en UECL 15 okt, League Cup 27 okt). Dat is een "
               "aaneengesloten interlandperiode van ruim twee weken, en die hoort bij Run C.",
    "eerstvolgende_speelronde": {
        "9 oktober": ["La Liga (ESP)", "Championship (ENG)", "Eredivisie (NED)",
                      "Primeira Liga (POR)", "Belgian Pro League (BEL)", "Süper Lig (TUR)",
                      "Danish Superliga (DEN)", "Bundesliga (GER)", "Ligue 1 (FRA)"],
        "10 oktober": ["Premier League (ENG)", "Serie A (ITA)", "Scottish Premiership (SCO)"],
        "13 oktober": ["UEFA Champions League"],
        "15 oktober": ["UEFA Europa League", "UEFA Conference League"],
        "27 oktober": ["League Cup (ENG)"],
        "onbekend": ["Ekstraklasa (POL)", "Coppa Italia (ITA)", "FA Cup (ENG)",
                     "KNVB Beker (NED)", "DFB Pokal (GER)"],
    },
    "ekstraklasa_coppa": "BetExplorer gaf voor Ekstraklasa en Coppa Italia 0 komende duels terug "
                         "(HTTP 200, lege fixturetabel). Dat is geen tegenspraak met Fotmob — "
                         "beide bronnen hebben daar vandaag niets — maar het betekent wel dat "
                         "voor die twee alleen Fotmob de dag bevestigt.",
}

state["duur"] = {
    "gestart": "2026-09-23T02:12:00+00:00",
    "afgerond": datetime.now(timezone.utc).isoformat(),
}

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})

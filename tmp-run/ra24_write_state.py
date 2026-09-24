"""Run A, 24 sep 2026 — run-state wegschrijven.

Vierde dag op rij zonder wedstrijd in de runlijst. Stage 2 noemt dat `GEEN WEDSTRIJD` en geen
storing, maar `find_league` geeft `None` ook terug bij een afwijkende naam — dus opnieuw met een
tweede bron nagetrokken in plaats van de conclusie van gisteren over te nemen.

Wat deze run toevoegt boven die van 23 sep: de kalender uit de tweede bron is een dag later
onveranderd (9–13 oktober voor de hele runlijst), en twee pagina's die gisteren leeg waren
gaven ook vandaag niets. De stilte blijft dus kalender en geen bron die wegvalt.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking

DAY = date(2026, 9, 24)
STAGE3 = json.load(open("tmp-run/ra24_stage3.json"))
BEV = json.load(open("tmp-run/ra24_bevestiging.json"))

state = load_or_start("a", DAY)

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd op de Fotmob-daglijst van 24 sep 2026; bevestigd met BetExplorer",
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
    "POORT8": "vandaag nog actief; sides.LAPSES_ON = 2026-09-25, dus dit is de laatste Run A "
              "waarin poort 8 bestaat. Hij heeft vandaag niets kunnen tegenhouden — er was geen "
              "selectie om aan toe te toetsen.",
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
    "methode_1": "Fotmob-daglijst 24 sep 2026: 29 competities, 48 wedstrijden, geen enkele uit de "
                 "runlijst. Wat er wél speelt is interlandvoetbal (UEFA Nations League A/B/D, "
                 "Africa Cup of Nations-kwalificatie in zes groepen, Gulf Cup, ASEAN Cup, "
                 "CONCACAF Nations League B, EURO U21-kwalificatie, vijf vriendschappelijke "
                 "interlands) plus kleinere competities: Israëlische Leumit League (4), "
                 "Marokkaanse Botola Pro (2), MLS (1), bekers in Chili en Paraguay, El Salvador "
                 "en Guatemala. De hoogste Europese divisies ontbreken volledig — het is dus geen "
                 "naamkwestie, want bij een afwijkende naam zou de competitie er wél staan.",
    "methode_2": "BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 "
                 "komende duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Eredivisie "
                 "18, Championship 12, Scottish Premiership 12, Primeira Liga 9, Pro League 9, "
                 "Süper Lig 9, Danish Superliga 6, UCL/UEL/UECL elk 18, League Cup 8 — nul "
                 "daarvan op vandaag.",
    "conclusie": "Beide bronnen zeggen hetzelfde: de hoogste divisies liggen stil. GEEN WEDSTRIJD "
                 "is de uitkomst, geen storing (Stage 2).",
    "context": "Vierde dag op rij. De kalender uit de tweede bron is onveranderd ten opzichte van "
               "gisteren: de eerstvolgende speelronde ligt voor de hele runlijst op 9–13 oktober. "
               "Dat is de bevestiging die telt — een bron die wegvalt verandert van dag tot dag, "
               "een kalender niet. Het interlandvoetbal dat vandaag wél speelt hoort bij Run C.",
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
    "ekstraklasa_coppa": "BetExplorer gaf voor Ekstraklasa en Coppa Italia opnieuw 0 komende "
                         "duels terug (HTTP 200, lege fixturetabel), net als gisteren. Dat is "
                         "geen tegenspraak met Fotmob — beide bronnen hebben daar vandaag niets — "
                         "maar het betekent wel dat voor die twee alleen Fotmob de dag bevestigt.",
}

state["duur"] = {
    "gestart": "2026-09-24T02:10:00+00:00",
    "afgerond": datetime.now(timezone.utc).isoformat(),
}

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})

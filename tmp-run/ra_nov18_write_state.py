"""Stage -1/6 - Run A 18 nov 2026: het voortgangs-/runstate-bestand schrijven.

De runlijst is vandaag volledig leeg: nul duels in het inzetvenster
[08:00 NL 18 nov, 08:00 NL 19 nov). Twee bronnen (Fotmob-daglijst van 18 en 19 nov,
BetExplorer-fixtures per competitie) geven hetzelfde antwoord.
"""
import json
from datetime import date
from scripts.progress import load_or_start, mark, save

DAY = date(2026, 11, 18)
rl = json.load(open("tmp-run/ra_nov18_runlist.json"))
bx = json.load(open("tmp-run/ra_nov18_bx.json"))

state = load_or_start("a", DAY)
print("resumed_count:", state.get("resumed_count"), "sessies:", state.get("sessies"))

FOTMOB_IDS = {
    "Premier League (ENG)": 47, "Serie A (ITA)": 55, "La Liga (ESP)": 87,
    "Bundesliga (GER)": 54, "Ligue 1 (FRA)": 53, "Championship (ENG)": 48,
    "Eredivisie (NED)": 57, "Primeira Liga (POR)": 61, "Belgian Pro League (BEL)": 40,
    "Super Lig (TUR)": 71, "Scottish Premiership (SCO)": 64, "Danish Superliga (DEN)": 46,
    "Ekstraklasa (POL)": 196, "UEFA Champions League": 42, "UEFA Europa League": 73,
    "UEFA Conference League": 10216, "FA Cup (ENG)": 132, "League Cup (ENG)": 133,
    "Coppa Italia (ITA)": 141, "KNVB Beker (NED)": 235, "DFB Pokal (GER)": 209,
}
EERSTVOLGEND = {
    "Premier League (ENG)": "21 nov 13:30 (Manchester City - Fulham)",
    "Serie A (ITA)": "21 nov 15:00 (Como - Cagliari)",
    "Eredivisie (NED)": "21 nov 16:30 (NEC Nijmegen - PSV)",
    "UEFA Champions League": "24 nov 18:45 (Bodo/Glimt - LASK)",
    "FA Cup (ENG)": "4 dec 20:30 (Wimborne - Bradford City)",
    "League Cup (ENG)": "15 dec 21:00 (Manchester City - Bradford City)",
    "Coppa Italia (ITA)": "2 dec 21:00 (Como - Cremonese)",
    "DFB Pokal (GER)": "1 dec 18:00 (Holstein Kiel - FC Koln)",
    "KNVB Beker (NED)": "geen fixtures op de BetExplorer-pagina; Fotmob-daglijst leeg",
}

comps = {}
for naam, fid in FOTMOB_IDS.items():
    b = bx.get(naam)
    tweede = None
    if b:
        tweede = {"bron": "BetExplorer fetch_league_fixtures", "status": b["status"],
                  "rijen_op_de_pagina": b["n"], "in_venster_18_19_nov": b["in_venster"]}
    comps[naam] = {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "bron": "Fotmob-daglijst 18 en 19 nov (runwindow.matches_for_run op fotmob_id)",
        "fotmob_id": fid,
        "tweede_bron": tweede,
        "eerstvolgende_wedstrijd": EERSTVOLGEND.get(naam),
    }
state["competitions"] = comps

state["parameters"] = {
    "MAX_DEEP_ANALYSES": 40,
    "MAX_SHORTLIST": 3,
    "dagsoort": "woensdag (ma-do)",
    "EDGE_THRESHOLD_FULL": 8.0,
    "EDGE_THRESHOLD_LIGHT": 16.0,
    "inzetvenster": "[08:00 NL 18 nov 2026, 08:00 NL 19 nov 2026)",
    "DE_RUNLIJST_IS_VANDAAG_VOLLEDIG_LEEG": (
        "EENENTWINTIG VAN DE EENENTWINTIG COMPETITIES EN TOERNOOIEN VAN DE RUNLIJST HEBBEN GEEN "
        "WEDSTRIJD IN HET INZETVENSTER. Dat is `GEEN WEDSTRIJD` en geen storing (Stage 2, §5): het "
        "FIFA-interlandvenster van november loopt tot en met 17/18 nov, dus de dertien "
        "clubcompetities liggen stil, de drie Europese toernooien spelen niet en de vijf bekers "
        "hebben hun eerstvolgende ronde pas in december. Nagetrokken bij TWEE bronnen: de "
        "Fotmob-daglijsten van 18 en 19 nov (47 competities, 122 duels, geen enkele uit de "
        "runlijst) en de BetExplorer-fixturepagina per competitie (nul rijen in het venster). "
        "Er is dus geen enkele selectie doorgerekend die een poort, een drempel of een rangorde "
        "kon halen of missen. De eerste echte Run A-speeldag is zaterdag 21 november."
    ),
    "geen_credits_uitgegeven": (
        "Nul credits bij The Odds API: zonder duel in het venster is er geen competitie om "
        "prijzen voor te kopen. Quota blijft 19385 over / 615 gebruikt deze maand. De "
        "marktbalans-controle van §1a is daarmee niet van toepassing - er is geen inkoop geweest."
    ),
}
for naam in FOTMOB_IDS:
    mark(state, naam, comps[naam])
save(state)
print("weggeschreven:", f"data/run-state/{DAY}-run-a.json")
print("competities:", len(comps), "| duels:", sum(len(c["matches"]) for c in comps.values()))

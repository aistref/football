"""Run A, 25 sep 2026 — run-state wegschrijven.

Vijfde dag op rij zonder wedstrijd in de runlijst. Twee dingen zijn vandaag anders dan op 24 sep,
en allebei horen ze in het bestand:

1. **Stage 1 loopt voor het eerst in Run A via `scripts/runwindow.py`.** Het inzetvenster
   [08:00 NL 25 sep, 08:00 NL 26 sep) vervangt de UTC-dagregel, en omdat dit de eerste Run A met
   die module is gaat `include_carry_over=True` eenmalig mee.
2. **Poort 8 vervalt vandaag** (`sides.LAPSES_ON = 2026-09-25`). Er was geen selectie om hem op
   toe te passen, dus de eerste echte waarneming daarvan komt pas op 9 oktober.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking, sides

DAY = date(2026, 9, 25)
STAGE3 = json.load(open("tmp-run/ra25_stage3.json"))
BEV = json.load(open("tmp-run/ra25_bevestiging.json"))
GAP = json.load(open("tmp-run/ra25_gap.json"))

state = load_or_start("a", DAY)

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    eerste = GAP["first"].get(naam)
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd in het inzetvenster [08:00 NL 25 sep, 08:00 NL 26 sep) — "
                 "nul op beide Fotmob-daglijsten (25 en 26 sep), bevestigd met BetExplorer",
        "eerstvolgende_betexplorer": (BEV.get(naam) or {}).get("eerste"),
        "eerstvolgende_fotmob": eerste[0] if eerste else "geen binnen 21 dagen",
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
    "POORT8": {
        "lapses_on": str(sides.LAPSES_ON),
        "actief_vandaag": sides.LAPSES_ON > DAY,
        "toelichting":
            "Vandaag is de vervaldatum uit §1e: vanaf 25 sep 2026 laat sides.check() elke kant "
            "door en zet hij alleen nog would_block. Deze run heeft daar niets van gemerkt — er "
            "was geen selectie om te toetsen. De eerste Run A waarin het vervallen van poort 8 "
            "werkelijk iets kan doen is die van 9 oktober; leg daar poort8_vervallen per selectie "
            "vast en zet poort8_zou_hebben_geblokkeerd in de pick zodra zo'n selectie een "
            "gepubliceerde bet wordt.",
    },
}

state["stage1"] = {
    "module": "scripts/runwindow.py",
    "venster_nl": "[08:00 25 sep 2026, 08:00 26 sep 2026)",
    "include_carry_over": True,
    "reden_carry_over":
        "Dit is de eerste Run A die runwindow gebruikt — Run B en Run C zijn er op 24 sep mee "
        "begonnen. De band [00:00, 08:00) NL van 25 sep is daardoor door niemand bekeken: de "
        "oude UTC-dagregel gaf hem aan de run van vandaag (te laat) en het venster geeft hem aan "
        "die van gisteren (die hem niet zocht). Eenmalig ingehaald; vanaf 26 sep weglaten.",
    "daglijsten": {"2026-09-25": 61, "2026-09-26": 118},
    "gevonden_in_venster": 0,
    "carry_over_opbrengst":
        "nul — er stond ook in de band [00:00, 08:00) NL van 25 sep geen enkele wedstrijd uit de "
        "runlijst. De overstap kost deze run dus niets en levert niets op; dat is te verwachten "
        "bij een runlijst die volledig uit Europese competities bestaat (§3 Stage 1: 'een "
        "Europese avondwedstrijd verschuift niet').",
    "source_day_plus_1": 0,
    "onspeelbaar": 0,
}

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. "
             "The Odds API staat op 18.719 van de 20.000 over (api_check.py).",
    "marktbalans": "niet van toepassing — er is niets ingekocht. §1a eist minstens één "
                   "doelpunten- en één uitkomstmarkt zodra er wél wordt ingekocht.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1": "Fotmob-daglijsten van 25 en 26 sep 2026 (61 respectievelijk 118 competities, "
                 "104 wedstrijden op 25 sep), per competitie uit de runlijst getoetst met "
                 "find_league op naam, ccode en aliassen — 21 van de 21 leeg, op beide dagen. Wat "
                 "er wél speelt is interlandvoetbal (UEFA Nations League A/B/C, "
                 "AFCON-kwalificatie in acht groepen, CONCACAF Nations League A/B, EURO "
                 "U21-kwalificatie in vijf groepen, Asian Games, FIFA ASEAN Cup, twee "
                 "vriendschappelijke interlands) plus lagere en buitenlandse competities "
                 "(Scottish Championship 4, Ierse First Division 4, Duitse Regionalliga's 13, "
                 "Deense 2. en 3. Division, LaLiga2 1, Eerste Divisie 1, Braziliaanse Série B 2, "
                 "USL Championship 2, NWSL 1). De hoogste Europese divisies ontbreken volledig — "
                 "het is dus geen naamkwestie, want bij een afwijkende naam zou de competitie er "
                 "wél staan, alleen onder een andere naam.",
    "methode_2": "Achttien BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League "
                 "20 komende duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Eredivisie "
                 "18, Championship 11, Scottish Premiership 12, Primeira Liga 9, Pro League 9, "
                 "Süper Lig 9, Danish Superliga 6, Ekstraklasa 2, UCL/UEL/UECL elk 18, League Cup "
                 "8 — nul daarvan op vandaag. Coppa Italia gaf HTTP 200 met een lege tabel.",
    "conclusie": "Beide bronnen zeggen hetzelfde: de hoogste divisies liggen stil. GEEN WEDSTRIJD "
                 "is de uitkomst, geen storing (Stage 2).",
    "context": "Vijfde dag op rij. Nieuw vandaag is dat de lengte van de onderbreking op beide "
               "bronnen is uitgemeten in plaats van alleen de dag van vandaag: de Fotmob-"
               "daglijsten van 26 september t/m 8 oktober geven samen nul wedstrijden uit de "
               "runlijst, en BetExplorer noemt dezelfde eerstvolgende speelronde. Dat is de "
               "bevestiging die telt — een bron die wegvalt verandert van dag tot dag, een "
               "kalender niet. Het interlandvoetbal dat vandaag wél speelt hoort bij Run C.",
    "lege_periode": {
        "eerste_lege_dag": "2026-09-21",
        "laatste_lege_dag": "2026-10-08",
        "lege_runs_nog_te_gaan": 13,
        "gemeten_met": "tmp-run/ra25_gap.py — 21 Fotmob-daglijsten van 26 sep t/m 16 okt, "
                       "per dag getoetst op alle 21 competities uit de runlijst",
    },
    "eerstvolgende_speelronde": {k: v[0] for k, v in GAP["first"].items()},
    "eerste_volle_dag": "2026-10-10 (56 wedstrijden uit de runlijst; 9 okt is de vrijdagavond "
                        "met 12 duels, 11 okt 41 en 12 okt 9)",
    "bekers": "FA Cup, League Cup, Coppa Italia, KNVB Beker en DFB Pokal staan in de hele "
              "gemeten periode t/m 16 oktober niet op een Fotmob-daglijst. BetExplorer zet de "
              "League Cup op 27 oktober. Dat is kalender, geen gat.",
}

state["duur"] = {
    "gestart": "2026-09-25T02:15:00+00:00",
    "afgerond": datetime.now(timezone.utc).isoformat(),
}

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})

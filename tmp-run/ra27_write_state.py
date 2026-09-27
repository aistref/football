"""Run A, 27 sep 2026 — run-state wegschrijven.

Zevende dag op rij zonder wedstrijd in de runlijst, en de dag verliep precies zoals de scan van
26 september voorspelde: de lege periode loopt van 21 september t/m 8 oktober. Nieuw vandaag is
alleen dat die voorspelling nu een dag ervaring heeft — de scan is onafhankelijk herhaald en geeft
opnieuw 9 oktober als eerste speeldag.

Wat wél opvalt en niet over deze rundag gaat: de afwikkeling van Stage 0 leverde zes verliezers op
acht picks. Dat is de reeks waarover §7 zegt dat hij vooraan in de notificatie hoort.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking, sides

DAY = date(2026, 9, 27)
STAGE3 = json.load(open("tmp-run/ra27_stage3.json"))
BEV = json.load(open("tmp-run/ra27_bevestiging.json"))
GAP = json.load(open("tmp-run/ra27_gap.json"))
SETTLE = json.load(open("tmp-run/ra27_settle.json"))

state = load_or_start("a", DAY)

# eerstvolgende speeldag per competitie uit de Fotmob-scan (16 daglijsten)
eerste_fotmob = {}
for d, hits in sorted(GAP["scan"].items()):
    for naam in hits:
        eerste_fotmob.setdefault(naam, d)

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    tweede = (BEV.get(naam) or GAP["cups"].get(naam) or {})
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd in het inzetvenster [08:00 NL 27 sep, 08:00 NL 28 sep) — "
                 "nul op beide Fotmob-daglijsten (27 en 28 sep), bevestigd met BetExplorer",
        "eerstvolgende_betexplorer": tweede.get("eerste"),
        "eerstvolgende_fotmob": eerste_fotmob.get(naam, "geen binnen 16 dagen"),
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
            "Tweede volle dag ná de vervaldatum van §1e: sides.check() laat elke kant door en zet "
            "alleen nog would_block. Opnieuw geen selectie om hem op toe te passen. De eerste "
            "Run A waarin het vervallen van poort 8 werkelijk iets kan doen blijft die van "
            "9 oktober; leg daar poort8_vervallen per selectie vast en zet "
            "poort8_zou_hebben_geblokkeerd in de pick zodra zo'n selectie een gepubliceerde bet "
            "wordt (§1e).",
    },
}

state["stage1"] = {
    "module": "scripts/runwindow.py",
    "venster_nl": "[08:00 27 sep 2026, 08:00 28 sep 2026)",
    "include_carry_over": False,
    "reden_carry_over":
        "Uit, zoals §3 Stage 1 voorschrijft na de eenmalige overstap van 25 september. Hem "
        "aanzetten zou de band [00:00, 08:00) NL in twee runrapporten zetten.",
    "daglijsten": {"2026-09-27": 85, "2026-09-28": 33},
    "gevonden_in_venster": 0,
    "source_day_plus_1": 0,
    "onspeelbaar": 0,
}

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. "
             "The Odds API staat op 18.666 van de 20.000 over (api_check.py deze run).",
    "marktbalans": "niet van toepassing — er is niets ingekocht. §1a eist minstens één "
                   "doelpunten- en één uitkomstmarkt zodra er wél wordt ingekocht.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1":
        "Fotmob-daglijsten van 27 en 28 sep 2026 (85 respectievelijk 33 competities), per "
        "competitie uit de runlijst getoetst met find_league op naam, ccode en aliassen — 21 van "
        "de 21 leeg, op beide dagen. Dat het geen naamkwestie is, is aan de daglijst zelf te zien: "
        "wat er vandaag wél staat is interlandvoetbal (UEFA Nations League A/B/D, CONCACAF "
        "Nations League A/B, Gulf Cup, negen friendlies) plus de lagere en buitenlandse divisies "
        "— MLS (10), Primera Nacional (10), DFB Pokal Frauen (9), NPFL (8), de Spaanse Segunda "
        "en Primera Federación, Serie C, LaLiga2 (5), de Nederlandse Eerste Divisie (1). Bij een "
        "afwijkende competitienaam zou de hoogste divisie er wél staan en zouden de lagere "
        "divisies van dezelfde landen niet als enige overblijven. Let op het spiegelbeeld van "
        "25 september: toen was het interlandvoetbal er en de club­competities niet; vandaag is "
        "het interlandvoetbal er nog steeds en zijn de clubcompetities uit déze runlijst nog "
        "steeds weg.",
    "methode_2":
        "Achttien BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 "
        "komende duels, Serie A 20, La Liga 19, Bundesliga 16, Ligue 1 18, Championship 12, "
        "Eredivisie 18, Primeira Liga 9, Pro League 9, Süper Lig 9, Scottish Premiership 12, "
        "Danish Superliga 6, Ekstraklasa 7, UCL/UEL/UECL elk 18, League Cup 8 — nul daarvan op "
        "vandaag, en de eerstvolgende staat overal op 9, 10 of 13 oktober. Coppa Italia gaf HTTP "
        "200 met een lege tabel. Plus de drie bekers zonder URL in de hoofdlijst: DFB Pokal 16 "
        "komende duels met de eerste op 27 oktober; FA Cup en KNVB Beker geven bij BetExplorer "
        "een lege tabel, dus voor die twee blijft Fotmob de enige bron — dat is een "
        "bronbeperking en geen bevestiging, en het hoort zo opgeschreven te staan.",
    "conclusie": "Beide bronnen zeggen hetzelfde: de hoogste divisies liggen stil tot 9 oktober. "
                 "GEEN WEDSTRIJD is de uitkomst, geen storing (Stage 2).",
    "context":
        "Zevende dag op rij, en de dag verliep exact zoals de scan van 26 september hem "
        "voorspelde. Wat vandaag speelt is interlandvoetbal (Run C) en de lagere club­divisies "
        "(Run B); hun aanwezigheid is geen gat in Run A en hun ontbreken hier evenmin (run-a.md).",
    "lege_periode": {
        "eerste_lege_dag": "2026-09-21",
        "laatste_lege_dag": "2026-10-08",
        "dag_in_de_reeks": 7,
        "lege_runs_nog_te_gaan": 11,
        "gemeten_met": "tmp-run/ra27_gap.py — 16 Fotmob-daglijsten van 27 sep t/m 12 okt, per dag "
                       "getoetst op alle 21 competities uit de runlijst. Onafhankelijk opgehaald "
                       "van de scans van 25 en 26 september, en met dezelfde uitkomst: dat is de "
                       "derde herhaling van hetzelfde antwoord.",
    },
    "eerstvolgende_speelronde": eerste_fotmob,
    "eerste_volle_dag": "2026-10-10 (56 wedstrijden uit de runlijst in 12 competities; 9 okt is "
                        "de vrijdagavond met 12 duels in 10 competities, 11 okt 41 in 13, "
                        "12 okt 9 in 7)",
    "bekers": "FA Cup, League Cup, Coppa Italia, KNVB Beker en DFB Pokal staan in de hele "
              "gemeten periode t/m 12 oktober niet op een Fotmob-daglijst. BetExplorer zet de "
              "League Cup en de DFB Pokal beide op 27 oktober. Dat is kalender, geen gat.",
}

state["afwikkeling"] = {
    "picks_afgewikkeld": len(SETTLE["picks"]),
    "schaduw_afgewikkeld": len(SETTLE["shadow"]),
    "niet_afgewikkeld": SETTLE["mis"],
    "picks_uitslag": {"gewonnen": sum(1 for x in SETTLE["picks"] if x["result"] == "won"),
                      "verloren": sum(1 for x in SETTLE["picks"] if x["result"] == "lost"),
                      "void": sum(1 for x in SETTLE["picks"] if x["result"] == "void")},
    "schaduw_uitslag": {"gewonnen": sum(1 for x in SETTLE["shadow"] if x["result"] == "won"),
                        "verloren": sum(1 for x in SETTLE["shadow"] if x["result"] == "lost"),
                        "void": sum(1 for x in SETTLE["shadow"] if x["result"] == "void")},
    "negentig_minuten":
        "Alle acht de picks en alle 27 schaduwrijen komen uit wedstrijden die Fotmob met "
        "reason.short = FT afsloot — geen verlenging, geen strafschoppen. De eindstand ís hier "
        "dus de stand na 90 minuten (§6d). Twee duels zijn expliciet nagekeken omdat ze anders in "
        "de knock-outval hadden kunnen lopen: Oman – Saudi Arabia staat in de Gulf Cup maar in "
        "groep A, en Stockport County – Peterborough United is League One en geen bekerduel. "
        "Beide FT.",
    "bevinding":
        "Zes verliezers op acht afgewikkelde picks, één winnaar (Plymouth Argyle – Burton "
        "Albion, AH Burton +1 @ 1.97) en één void (Tranmere Rovers – Walsall, DNB bij 1-1). Dat "
        "haalt de drempel van §7 voor een afwikkelingsreeks die opvalt (5+ verliezers), dus het "
        "staat vooraan in de notificatie. Wat het níet is, is een bevinding over de routine: het "
        "gaat om de picks van Run B en Run C van 26 september, niet om een beslissing van vandaag, "
        "en §6d zegt dat één dag bij deze aantallen ruis is. Het logboek als geheel schuift er "
        "dan ook nauwelijks van op — 311 picks, ROI -8,5%, hit rate 44,0%. Vier MLS-duels en "
        "Mexico – Colombia stonden nog niet op afgelopen en blijven openstaan voor de volgende run.",
}

state["duur"] = {
    "gestart": state.get("duur", {}).get("gestart") or datetime.now(timezone.utc).isoformat(),
    "afgerond": datetime.now(timezone.utc).isoformat(),
}

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})

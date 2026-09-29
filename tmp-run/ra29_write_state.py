"""Run A, 29 sep 2026 — run-state wegschrijven.

Negende dag op rij zonder wedstrijd in de runlijst, en opnieuw precies zoals de scans van 25 t/m
28 september hem voorspelden: de lege periode loopt van 21 september t/m 8 oktober. De scan is
vandaag voor de vijfde keer onafhankelijk herhaald en geeft opnieuw 9 oktober.

Wat deze run onderscheidt van die van gisteren gaat niet over de rundag zelf:

1. Stage -2 vond dit keer niets. Alle vijf de logboeken zijn over alle 41 takken per record
   vergeleken en `main` is een volledige superset. De enige afwijking in `source-health.json` is
   de `oddspapi`-bron, en die is op 30 augustus met opzet van `main` verwijderd (commit f342894,
   README) — een besluit en geen verlies. Dat is dezelfde constatering die Run B gisteren deed.
2. De afwikkeling leverde drie winnaars op vier picks. Dat haalt de drempel van §7 níet (die gaat
   over 5+ verliezers), dus de notificatie is een hartslag en geen alarm.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking, sides

DAY = date(2026, 9, 29)
STAGE3 = json.load(open("tmp-run/ra29_stage3.json"))
BEV = json.load(open("tmp-run/ra29_bevestiging.json"))
GAP = json.load(open("tmp-run/ra29_gap.json"))
SETTLE = json.load(open("tmp-run/ra29_settle.json"))

state = load_or_start("a", DAY)

eerste_fotmob = {}
for d, hits in sorted(GAP["scan"].items()):
    for naam in hits:
        eerste_fotmob.setdefault(naam, d)

BEV_ALIAS = {"Süper Lig (TUR)": "Super Lig (TUR)"}

RUNLIJST = list(STAGE3["fixtures"].keys())
assert len(RUNLIJST) == 21, len(RUNLIJST)

for naam in RUNLIJST:
    v = STAGE3["fixtures"][naam]
    assert v["status"] == "GEEN WEDSTRIJD", (naam, v["status"])
    tweede = (BEV.get(naam) or BEV.get(BEV_ALIAS.get(naam, "")) or GAP["cups"].get(naam) or {})
    mark(state, naam, {
        "status": "GEEN WEDSTRIJD",
        "matches": [],
        "reden": "geen wedstrijd in het inzetvenster [08:00 NL 29 sep, 08:00 NL 30 sep) — "
                 "nul op beide Fotmob-daglijsten (29 en 30 sep), bevestigd met BetExplorer",
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
            "Vierde volle dag ná de vervaldatum van §1e: sides.check() laat elke kant door en zet "
            "alleen nog would_block. Opnieuw geen selectie om hem op toe te passen. De eerste "
            "Run A waarin het vervallen van poort 8 werkelijk iets kan doen blijft die van "
            "9 oktober; leg daar poort8_vervallen per selectie vast en zet "
            "poort8_zou_hebben_geblokkeerd in de pick zodra zo'n selectie een gepubliceerde bet "
            "wordt (§1e).",
    },
}

state["stage1"] = {
    "module": "scripts/runwindow.py",
    "venster_nl": "[08:00 29 sep 2026, 08:00 30 sep 2026)",
    "include_carry_over": False,
    "reden_carry_over":
        "Uit, zoals §3 Stage 1 voorschrijft na de eenmalige overstap van 25 september. Hem "
        "aanzetten zou de band [00:00, 08:00) NL in twee runrapporten zetten.",
    "daglijsten": {"2026-09-29": 53, "2026-09-30": 35},
    "gevonden_in_venster": 0,
    "source_day_plus_1": 0,
    "onspeelbaar": 0,
}

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. "
             "The Odds API staat op 18.627 van de 20.000 over (api_check.py deze run).",
    "marktbalans": "niet van toepassing — er is niets ingekocht. §1a eist minstens één "
                   "doelpunten- en één uitkomstmarkt zodra er wél wordt ingekocht.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1":
        "Fotmob-daglijsten van 29 en 30 sep 2026 (53 respectievelijk 35 competities), per "
        "competitie uit de runlijst getoetst met find_league op naam, ccode en aliassen — 21 van "
        "de 21 leeg, op beide dagen. Dat het geen naamkwestie is, is aan de daglijst zelf te "
        "zien: wat er vandaag wél staat is interlandvoetbal (UEFA Nations League A/B/C, CONCACAF "
        "Nations League A/B/C, AFCON-kwalificatie in tien groepen, EURO U21-kwalificatie in vier "
        "groepen, FIFA ASEAN Cup, Gulf Cup, friendlies) plus lagere en buitenlandse divisies — "
        "Japanse League Cup (16 duels), National League en de drie Engelse regionale divisies "
        "(40 duels samen), Azadegan League, China League, Braziliaanse Série B, Colombiaanse "
        "Primera A en B, QSL Cup, Regionalliga Bayern, Noorse 3. Divisjon. Bij een afwijkende "
        "competitienaam zou de hoogste divisie er wél staan; hier staan de Engelse vijfde tot "
        "achtste niveaus op de lijst en de Premier League niet, en dat is precies het omgekeerde "
        "van wat een naamfout zou geven. Let op twee bijna-treffers die géén runlijstwedstrijd "
        "zijn: 'A-Liga' (DEN, id 256) is de Deense vrouwencompetitie en niet Superligaen (id 46), "
        "en 'Challenge Cup' (SCO) is niet de Scottish Premiership.",
    "methode_2":
        "Achttien BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 "
        "komende duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Championship 12, "
        "Eredivisie 18, Primeira Liga 9, Pro League 9, Süper Lig 9, Scottish Premiership 12, "
        "Danish Superliga 6, Ekstraklasa 9, UCL 18, UEL 18, UECL 18, League Cup 8 — nul daarvan "
        "op vandaag, en de eerstvolgende staat overal op 9, 10, 11, 13, 15 of 27 oktober. Coppa "
        "Italia gaf HTTP 200 met een lege tabel. Plus de drie bekers zonder URL in de hoofdlijst: "
        "DFB Pokal 8 komende duels met de eerste op 27 oktober; FA Cup en KNVB Beker geven bij "
        "BetExplorer een lege tabel, dus voor die twee blijft Fotmob de enige bron — dat is een "
        "bronbeperking en geen bevestiging, en het hoort zo opgeschreven te staan.",
    "methode_3_tegenproef":
        "De daglijsten van 1 t/m 8 oktober zijn met dezelfde toets nagelopen (30, 55, 104, 85, "
        "26, 57, 21 en 22 competities) en geven alle acht nul runlijstwedstrijden. Die lijsten "
        "zijn wél gevuld — op 3 oktober staan er 104 competities op, waaronder de lagere Engelse, "
        "Nederlandse, Spaanse en Duitse divisies. De daglijsten zijn dus gezond; het zijn "
        "werkelijk alleen de topdivisies die stilliggen. Een defecte of halflege dagrespons zou "
        "de lagere divisies net zo goed hebben gemist.",
    "conclusie": "Alle drie de ingangen zeggen hetzelfde: de hoogste divisies liggen stil tot "
                 "9 oktober. GEEN WEDSTRIJD is de uitkomst, geen storing (Stage 2).",
    "context":
        "Negende dag op rij, en de dag verliep exact zoals de scans van 25 t/m 28 september hem "
        "voorspelden. Wat vandaag speelt is interlandvoetbal (Run C) en de lagere clubdivisies "
        "(Run B); hun aanwezigheid is geen gat in Run A en hun ontbreken hier evenmin (run-a.md).",
    "lege_periode": {
        "eerste_lege_dag": "2026-09-21",
        "laatste_lege_dag": "2026-10-08",
        "dag_in_de_reeks": 9,
        "lege_runs_nog_te_gaan": 9,
        "gemeten_met": "tmp-run/ra29_gap.py — 16 Fotmob-daglijsten van 29 sep t/m 14 okt, per dag "
                       "getoetst op alle 21 competities uit de runlijst. Onafhankelijk opgehaald "
                       "van de scans van 25 t/m 28 september, en met dezelfde uitkomst: dat is "
                       "de vijfde herhaling van hetzelfde antwoord.",
    },
    "eerstvolgende_speelronde": eerste_fotmob,
    "eerste_volle_dag": "2026-10-10 (56 wedstrijden uit de runlijst in 12 competities; 9 okt is "
                        "de vrijdagavond met 12 duels in 10 competities, 11 okt 41 in 13, "
                        "12 okt 9 in 7, 13 okt 17 in 2 waaronder de eerste UCL-speelronde)",
    "bekers": "FA Cup, League Cup, Coppa Italia, KNVB Beker en DFB Pokal staan in de hele "
              "gemeten periode t/m 14 oktober niet op een Fotmob-daglijst. BetExplorer zet de "
              "League Cup en de DFB Pokal beide op 27 oktober. Dat is kalender, geen gat.",
}

state["stage_min2"] = {
    "ondiepe_kloon": True,
    "vals_alarm_voor_unshallow":
        "git rev-parse --is-shallow-repository gaf true, en dat gaf precies het beeld dat §3 "
        "Stage -2 beschrijft: 31 van de 41 takken leken 1 tot 315 eigen commits te hebben en "
        "git diff origin/main...<tak> gaf 'no merge base'. De vergelijking is daarom niet op de "
        "commitgraaf gedaan maar per record op de inhoud, zoals de tabel sinds 27 september eist.",
    "vergelijking_per_regel":
        "Alle vijf de logboeken per record vergeleken over alle 41 takken — picks.jsonl op 'id', "
        "shadow.jsonl op 'id', calibration.jsonl op (datum, run, wedstrijd, markt, methode), "
        "context-log.jsonl op 'id', en source-health.json plus coverage.json tot op de bladpaden.",
    "gevonden": {
        "data/picks.jsonl": "volledig — main heeft 323 id's, geen tak heeft er één die hier mist",
        "data/shadow.jsonl": "volledig — 728 records",
        "data/calibration.jsonl": "volledig — 3438 records",
        "data/context-log.jsonl": "volledig — 837 records",
        "data/coverage.json": "volledig — 251 bladpaden, geen tak met een afwijking",
        "data/source-health.json":
            "één afwijking: sources.oddspapi staat op negen oudere takken en niet op main. Dat is "
            "geen verlies maar een besluit — OddsPapi is op 30 aug 2026 verwijderd na de overstap "
            "naar het 20K-plan (commit f342894, en README 'OddsPapi — ingebouwd op 15 aug 2026, "
            "weer verwijderd op 30 aug 2026'). Niet teruggezet. Verder alleen last_run-stempels "
            "van oudere runs, en dat is geen meting.",
    },
    "verenigd": [],
    "les":
        "Twee dagen nadat de vergelijking per regel vier ontbrekende schaduwrijen vond, vindt "
        "dezelfde vergelijking niets. Dat is hoe het hoort te lopen: sinds §6a elke run naar main "
        "pusht komt er niets nieuws bij, en Stage -2 ruimt alleen op wat vóór die regel uiteen is "
        "gelopen. Wat blijft staan is dat de byte-vergelijking ruis geeft (18 takken lijken op "
        "picks.jsonl af te wijken) en de vergelijking op identiteit niet — het verschil zit in "
        "records die main in afgewikkelde vorm heeft en de tak nog als pending.",
    "branch": "main — de scheduler-prompt geeft expliciet toestemming (§6a), en de run staat "
              "op main. Niets te melden bovenaan het rapport.",
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
        "Alle vier de picks en alle vijftien schaduwrijen komen uit groeps- of competitieduels die "
        "Fotmob als afgelopen meldde zonder verlenging of strafschoppen, dus de eindstand ís hier "
        "de stand na 90 minuten (§6d). Nagekeken op de knock-outval: Belgium – France, "
        "Turkiye – Italy en Sweden – Poland zijn groepsduels in de UEFA Nations League, "
        "Leganés – Castellón is een competitiewedstrijd in de Segunda División, en de vijftien "
        "schaduwrijen komen uit Nations League-groepen, AFCON- en WK-kwalificatiegroepen en "
        "friendlies. Geen enkele rij komt uit een tweeluik of play-offduel waar 90 minuten en "
        "eindstand kunnen verschillen.",
    "bevinding":
        "Drie winnaars op vier afgewikkelde picks: Castellón wint bij Leganés (1X2 @ 2.38), Italië "
        "verliest niet in Turkije (Draw No Bet @ 1.99, het werd 1-4) en Zweden verslaat Polen "
        "(1X2 @ 2.16, 3-1). De enige verliezer is België of gelijk tegen Frankrijk (Double Chance "
        "@ 1.95, 0-1). Dat haalt de drempel van §7 voor een opvallende reeks niet — die gaat over "
        "5+ verliezers — dus de notificatie is een hartslag. En het is net zo goed geen bevinding "
        "over de routine als vijf verliezers dat gisteren was: het gaat om de picks van Run B en "
        "Run C van 28 september en §6d zegt dat één dag bij deze aantallen ruis is.",
    "schaduw_bevinding":
        "De schaduwkant liep de andere kant op: twaalf verliezers, twee winnaars en één void op "
        "vijftien rijen. Dat zijn de kandidaten die de poorten hebben tegengehouden, dus op één "
        "dag gelezen betekent het dat de poorten vandaag geld hebben bespaard — het spiegelbeeld "
        "van gisteren, toen elf van de zestien wonnen. Precies daarom zegt §6d dat één dag bij "
        "deze aantallen ruis is; twee opeenvolgende dagen die tegengesteld uitvallen zijn daar de "
        "illustratie van. Niet op grond hiervan een poort verruimen of aanscherpen.",
}

state["duur"] = {
    "gestart": state.get("duur", {}).get("gestart") or "2026-09-29T02:18:00+00:00",
    "afgerond": datetime.now(timezone.utc).isoformat(),
}
_g = datetime.fromisoformat(state["duur"]["gestart"])
_a = datetime.fromisoformat(state["duur"]["afgerond"])
state["duur"]["minuten"] = round((_a - _g).total_seconds() / 60, 1)

save(state)
print("geschreven:", len(state["competitions"]), "competities")
print("statussen:", {v["status"] for v in state["competitions"].values()})
print("duur:", state["duur"]["minuten"], "minuten")
print("betexplorer-bevestiging gevonden voor:",
      sum(1 for n in RUNLIJST if state["competitions"][n]["eerstvolgende_betexplorer"]))

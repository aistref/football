"""Run A, 30 sep 2026 — run-state wegschrijven.

Tiende dag op rij zonder wedstrijd in de runlijst. De lege periode loopt van 21 september t/m
8 oktober; de scan is vandaag voor de zesde keer onafhankelijk herhaald en geeft opnieuw
9 oktober als eerste speeldag.

Wat deze run onderscheidt:

1. De afwikkeling leverde drie verliezers op drie picks — alle drie Asian Handicaps op de
   underdog-kant, uit Run C van 29 september. Dat haalt de drempel van §7 (5+ verliezers) niet,
   maar de kant waarop ze stonden is wél de kant waarover §1e gaat, en dat hoort opgeschreven.
2. `idcheck.py` dekt de Run A-runlijst helemaal niet. Het script leest `data/coverage.json` en
   alle 21 competities van Run A staan daar zonder `fotmob_id` — de controle die juist gemaakt is
   om een stil verkeerd id te vangen bij competities die vandaag niet spelen, draait dus over
   zeventien Run B-competities en over nul van Run A. Na tien lege dagen op rij is dat precies de
   faalstand die het script beschrijft. Vandaag met de hand weerlegd (zie `id_controle`).
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking, sides

DAY = date(2026, 9, 30)
STAGE3 = json.load(open("tmp-run/ra30_stage3.json"))
BEV = json.load(open("tmp-run/ra30_bevestiging.json"))
GAP = json.load(open("tmp-run/ra30_gap.json"))
SETTLE = json.load(open("tmp-run/ra30_settle.json"))
IDC = json.load(open("tmp-run/ra30_idcontrole.json"))

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
        "reden": "geen wedstrijd in het inzetvenster [08:00 NL 30 sep, 08:00 NL 1 okt) — "
                 "nul op beide Fotmob-daglijsten (30 sep en 1 okt), bevestigd met BetExplorer "
                 "en met de Fotmob-competitiepagina",
        "eerstvolgende_betexplorer": tweede.get("eerste"),
        "eerstvolgende_fotmob": eerste_fotmob.get(naam, "geen binnen 16 dagen"),
        "id_controle": IDC.get(naam),
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
            "Vijfde volle dag ná de vervaldatum van §1e: sides.check() laat elke kant door en zet "
            "alleen nog would_block. Opnieuw geen selectie om hem op toe te passen. De eerste "
            "Run A waarin het vervallen van poort 8 werkelijk iets kan doen is die van "
            "9 oktober; leg daar poort8_vervallen per selectie vast en zet "
            "poort8_zou_hebben_geblokkeerd in de pick zodra zo'n selectie een gepubliceerde bet "
            "wordt (§1e). Wat de afwikkeling van vandaag daarover zegt staat onder 'afwikkeling'.",
    },
}

state["stage1"] = {
    "module": "scripts/runwindow.py",
    "venster_nl": "[08:00 30 sep 2026, 08:00 1 okt 2026)",
    "include_carry_over": False,
    "reden_carry_over":
        "Uit, zoals §3 Stage 1 voorschrijft na de eenmalige overstap van 25 september. Hem "
        "aanzetten zou de band [00:00, 08:00) NL in twee runrapporten zetten.",
    "daglijsten": {"2026-09-30": 36, "2026-10-01": 31},
    "gevonden_in_venster": 0,
    "source_day_plus_1": 0,
    "onspeelbaar": 0,
}

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. "
             "The Odds API staat op 18.610 van de 20.000 over (api_check.py deze run).",
    "marktbalans": "niet van toepassing — er is niets ingekocht. §1a eist minstens één "
                   "doelpunten- en één uitkomstmarkt zodra er wél wordt ingekocht.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1":
        "Fotmob-daglijsten van 30 sep en 1 okt 2026 (36 respectievelijk 31 competities), per "
        "competitie uit de runlijst getoetst met find_league op naam, ccode en aliassen — 21 van "
        "de 21 leeg, op beide dagen. Dat het geen naamkwestie is, is aan de daglijst zelf te "
        "zien: wat er vandaag wél staat is interlandvoetbal (AFCON-kwalificatie, EURO "
        "U21-kwalificatie in vijf groepen, CONCACAF Nations League B, Asian Games, Gulf Cup, "
        "FIFA ASEAN Cup, friendlies) plus vrouwenvoetbal (Women's Champions League, UEFA Women's "
        "Europa Cup met 16 duels, Women's League Cup) en lagere en buitenlandse divisies — "
        "National League, Isthmian en Southern Premier (Engelse vijfde tot achtste niveaus), "
        "Regionalliga West, USL Championship en League One, NPFL, Peruaanse Liga 1. Bij een "
        "afwijkende competitienaam zou de hoogste divisie er wél staan; hier staan de Engelse "
        "vijfde tot achtste niveaus op de lijst en de Premier League niet, en dat is precies het "
        "omgekeerde van wat een naamfout zou geven. Let op de bijna-treffers die géén "
        "runlijstwedstrijd zijn: 'Premier League' met ccode GHA (id 522) en CAN (id 9986) zijn "
        "Ghana en Canada, niet Engeland, en 'Cup' met ccode CZE/NOR/CHI/PAR zijn nationale bekers "
        "buiten de runlijst.",
    "methode_2":
        "Achttien BetExplorer-fixturepagina's, los van Fotmob opgehaald: nul daarvan op vandaag, "
        "en de eerstvolgende staat overal op 9 of 10 oktober, met UCL op 13 oktober, UEL en UECL "
        "op 15 oktober en de League Cup op 27 oktober. Coppa Italia gaf HTTP 200 met een lege "
        "tabel. Plus de drie bekers zonder URL in de hoofdlijst: DFB Pokal 8 komende duels met de "
        "eerste op 27 oktober; FA Cup en KNVB Beker geven bij BetExplorer een lege tabel, dus "
        "voor die twee blijft Fotmob de enige bron — dat is een bronbeperking en geen "
        "bevestiging, en het hoort zo opgeschreven te staan.",
    "methode_3_tegenproef":
        "De daglijsten van 1 t/m 8 oktober zijn met dezelfde toets nagelopen (31, 55, 105, 87, "
        "27, 57, 21 en 23 competities) en geven alle acht nul runlijstwedstrijden. Die lijsten "
        "zijn wél gevuld — op 3 oktober staan er 105 competities op, waaronder de lagere Engelse, "
        "Nederlandse, Spaanse en Duitse divisies. De daglijsten zijn dus gezond; het zijn "
        "werkelijk alleen de topdivisies die stilliggen. Een defecte of halflege dagrespons zou "
        "de lagere divisies net zo goed hebben gemist.",
    "methode_4_nieuw_vandaag":
        "De Fotmob-competitiepagina per competitie (api/data/leagues?id=<id>&tab=matches), een "
        "ingang die geen enkele eerdere Run A heeft gebruikt en die niet van de daglijst afhangt. "
        "Die geeft per competitie zowel de laatst gespeelde als de eerstvolgende wedstrijd, en "
        "dat maakt de lege periode van twee kanten dicht in plaats van alleen vooruit: alle negen "
        "getoetste competities (PL, Serie A, La Liga, Bundesliga, Ligue 1, Eredivisie, "
        "Championship, Danish Superliga, Ekstraklasa) speelden voor het laatst op 20 september en "
        "spelen weer op 9 of 10 oktober. Dat de laatste speeldag bij alle negen dezelfde is, is "
        "het sluitstuk van het bewijs: een fout id of een naamfout treft één competitie, geen "
        "negen tegelijk op dezelfde datum.",
    "conclusie": "Alle vier de ingangen zeggen hetzelfde: de hoogste divisies liggen stil van "
                 "21 september t/m 8 oktober. GEEN WEDSTRIJD is de uitkomst, geen storing "
                 "(Stage 2).",
    "context":
        "Tiende dag op rij, en de dag verliep exact zoals de scans van 25 t/m 29 september hem "
        "voorspelden. Wat vandaag speelt is interlandvoetbal (Run C) en de lagere clubdivisies "
        "(Run B); hun aanwezigheid is geen gat in Run A en hun ontbreken hier evenmin (run-a.md).",
    "lege_periode": {
        "eerste_lege_dag": "2026-09-21",
        "laatste_lege_dag": "2026-10-08",
        "dag_in_de_reeks": 10,
        "lege_runs_nog_te_gaan": 8,
        "gemeten_met": "tmp-run/ra30_gap.py — 16 Fotmob-daglijsten van 30 sep t/m 15 okt, per dag "
                       "getoetst op alle 21 competities uit de runlijst. Onafhankelijk opgehaald "
                       "van de scans van 25 t/m 29 september, en met dezelfde uitkomst: dat is "
                       "de zesde herhaling van hetzelfde antwoord.",
    },
    "eerstvolgende_speelronde": eerste_fotmob,
    "eerste_volle_dag": "2026-10-10 (56 wedstrijden uit de runlijst in 12 competities; 9 okt is "
                        "de vrijdagavond met 12 duels in 10 competities, 11 okt 41 in 13, "
                        "12 okt 9 in 7, 13 okt 17 in 2 waaronder de eerste UCL-speelronde, "
                        "15 okt 36 in 2 met de eerste UEL- en UECL-speelronde)",
    "bekers": "FA Cup, KNVB Beker en Coppa Italia staan in de hele gemeten periode t/m "
              "15 oktober niet op een Fotmob-daglijst. BetExplorer zet de League Cup en de DFB "
              "Pokal beide op 27 oktober. Dat is kalender, geen gat.",
}

state["id_controle"] = {
    "waarom":
        "scripts/idcheck.py bestaat precies voor de faalstand van vandaag: een verkeerd "
        "Fotmob-id geeft geen foutmelding maar nul wedstrijden, en nul wedstrijden is "
        "GEEN WEDSTRIJD — een normale uitkomst. Na tien lege dagen op rij is dat de enige "
        "controle die het verschil kan zien tussen een kalenderpauze en een stil kapot id.",
    "bevinding":
        "Het script dekt de Run A-runlijst niet. Het leest de competities met een fotmob_id uit "
        "data/coverage.json, en dat zijn zeventien Run B-competities; alle 21 Run A-competities "
        "staan in coverage.json zonder fotmob_id en worden dus overgeslagen. idcheck.py gaf "
        "vandaag 'Alle 17 id's uit coverage.json leveren een bruikbare stand' — een groene regel "
        "die over Run A niets zegt.",
    "vandaag_met_de_hand":
        "Alle 21 id's uit tmp-run/ra30_stage3.py zijn daarom met de hand tegen "
        "fetch_league_stats gehouden. De zestien competities met een eigen stand leveren alle "
        "zestien een bruikbare tabel mét xG: PL 20 ploegen, Serie A 20, La Liga 20, Bundesliga "
        "18, Ligue 1 18, Championship 24, Eredivisie 18, Primeira Liga 18, Pro League 16, "
        "Süper Lig 18, Scottish Premiership 12, Danish Superliga 12, Ekstraklasa 18, UCL 36, "
        "UEL 36, UECL 36. De vijf bekers hebben per ontwerp geen competitiestand (§4: in een "
        "beker ligt de basis per WEDSTRIJD) en draaien in de run op de primaryId van de "
        "moedercompetitie, niet op een eigen bekerid.",
    "resultaat": IDC,
    "openstaand":
        "Dit is een gat in de controle en niet in de run van vandaag. Het hoort opgelost te "
        "worden door de 21 Run A-id's in coverage.json te zetten, zodat idcheck.py ze meeneemt "
        "in plaats van dat elke Run A het met de hand doet. Werk voor de routine, niet voor de "
        "gebruiker.",
}

state["stage_min2"] = {
    "ondiepe_kloon": True,
    "unshallow_gedaan": True,
    "toelichting":
        "De kloon kwam ondiep binnen (afgekapt rond 20 september) en gaf daarmee exact het valse "
        "alarm dat §3 Stage -2 beschrijft: 31 van de 43 takken leken 1 tot 315 eigen commits te "
        "hebben. Dit keer is de kloon eerst volledig gemaakt (git fetch --unshallow, 75 -> 428 "
        "commits) in plaats van de vergelijking per record te doen. Daarna is de vraag "
        "rekenkundig beslist in plaats van beredeneerd: git rev-list --count HEAD..<tak> is nul "
        "voor alle 43 takken. main is dus een volledige superset en er valt niets te mergen.",
    "takken_getoetst": 43,
    "takken_met_eigen_commits": 0,
    "verenigd": [],
    "les":
        "Een ondiepe kloon maakt Stage -2 duurder dan nodig. De vergelijking per record van "
        "27 t/m 29 september was het juiste antwoord zolang de ancestry ontbrak, maar "
        "--unshallow haalt de ancestry gewoon terug en dan is één rev-list per tak genoeg. Doe "
        "dat eerst; het kostte vandaag één commando en vervangt de hele conflicttabel.",
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
        "Alle drie de picks en alle 32 schaduwrijen komen uit groeps- of competitieduels die "
        "Fotmob als afgelopen meldde zonder verlenging of strafschoppen, dus de eindstand ís hier "
        "de stand na 90 minuten (§6d). Nagekeken op de knock-outval: Czechia – England en "
        "Spain – Croatia zijn groepsduels in de UEFA Nations League A, San Marino – Albania in "
        "League C, en de 32 schaduwrijen komen uit Nations League-groepen, AFCON-kwalificatie- "
        "groepen, WK-kwalificatie en friendlies. Geen enkele rij komt uit een tweeluik of "
        "play-offduel waar 90 minuten en eindstand kunnen verschillen.",
    "open_gebleven":
        "Mexico – Peru (friendly, schaduwrij) blijft pending: Fotmob meldt het duel 2,3 uur na "
        "aftrap nog niet als afgelopen. Per §0 is de bronstatus leidend en de klok alleen een "
        "terugval als er géén status te krijgen is — die is er hier wel, dus de rij wacht op de "
        "volgende run. Dit is de regel die werkt zoals bedoeld, geen storing.",
    "bevinding":
        "Drie verliezers op drie afgewikkelde picks, en alle drie waren het Asian Handicaps op de "
        "underdog-kant: Czechia +1.5 (0-2, één doelpunt te kort), Croatia +2.5 (4-1, een halve "
        "goal te kort) en San Marino +2.5 (0-3, een halve goal te kort). Drie haalt de drempel "
        "van §7 voor een opvallende reeks niet — die gaat over 5+ verliezers — dus de notificatie "
        "is een hartslag. Wat het wél is: de eerste afwikkelingsdag van drie bets die alle drie "
        "op de kant stonden waarover §1e gaat, en alle drie op een handicap die binnen één "
        "doelpunt verloor. §6f noemt dat laatste met zoveel woorden de reden dat handicapbets op "
        "de underdog met argwaan gelezen moeten worden, en dit is daar een voorbeeld van. Eén "
        "dag is bij deze aantallen ruis (§6d) en er hoort dus niets aan verruimd of aangescherpt "
        "te worden; het hoort geteld te worden in de reeks van §1e, en dat gebeurt.",
    "poort8_reeks":
        "Deze drie picks zijn van Run C 29 september en dus van ná de vervaldatum van poort 8 "
        "(25 sep). Of ze het veld poort8_zou_hebben_geblokkeerd dragen is de vraag die §1e vanaf "
        "die datum wil meten; nagekeken in picks.jsonl staat het er bij alle drie niet op, omdat "
        "Run C met alleen LIGHT-data geen 1X2-prijzen als referentie had. Dat is een gat in die "
        "meting en het hoort bij Run C, niet hier — opgeschreven zodat het niet stil blijft.",
    "schaduw_bevinding":
        "De schaduwkant: acht winnaars, 23 verliezers en één void op 32 rijen. Dat zijn de "
        "kandidaten die de poorten hebben tegengehouden, dus op één dag gelezen betekent het dat "
        "de poorten vandaag geld hebben bespaard. Van de acht winnaars vielen er zeven af op "
        "'odds' of 'edge' en één op 'robuustheid'. Precies daarom zegt §6d dat één dag bij deze "
        "aantallen ruis is; niet op grond hiervan een poort verruimen of aanscherpen.",
}

state["duur"] = {
    "gestart": state.get("duur", {}).get("gestart") or "2026-09-30T02:17:00+00:00",
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

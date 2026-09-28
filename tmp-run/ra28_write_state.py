"""Run A, 28 sep 2026 — run-state wegschrijven.

Achtste dag op rij zonder wedstrijd in de runlijst, en opnieuw precies zoals de scans van 25, 26
en 27 september hem voorspelden: de lege periode loopt van 21 september t/m 8 oktober. De scan is
vandaag voor de vierde keer onafhankelijk herhaald en geeft opnieuw 9 oktober.

Twee dingen die deze run wél onderscheiden van die van gisteren, en die allebei niet over de
rundag zelf gaan:

1. Stage -2 vond echt werk dat `main` nooit had gekregen — vier schaduwrijen, drie ervan uit de
   `herijking`-reeks. Zie het commitbericht en het runrapport; het is de tweede keer in twee dagen
   dat de vergelijking per regel iets vindt wat de commitgraaf niet laat zien.
2. De afwikkeling leverde vijf verliezers op acht picks. Dat haalt de drempel van §7 (5+
   verliezers) en hoort daarom vooraan in de notificatie.
"""
import json
from datetime import date, datetime, timezone

from scripts.progress import load_or_start, mark, save
from scripts import ranking, sides

DAY = date(2026, 9, 28)
STAGE3 = json.load(open("tmp-run/ra28_stage3.json"))
BEV = json.load(open("tmp-run/ra28_bevestiging.json"))
GAP = json.load(open("tmp-run/ra28_gap.json"))
SETTLE = json.load(open("tmp-run/ra28_settle.json"))

state = load_or_start("a", DAY)

# eerstvolgende speeldag per competitie uit de Fotmob-scan (16 daglijsten)
eerste_fotmob = {}
for d, hits in sorted(GAP["scan"].items()):
    for naam in hits:
        eerste_fotmob.setdefault(naam, d)

# de namen in ra28_bevestiging.py wijken op één punt af van de runlijst (Super Lig vs Süper Lig)
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
        "reden": "geen wedstrijd in het inzetvenster [08:00 NL 28 sep, 08:00 NL 29 sep) — "
                 "nul op beide Fotmob-daglijsten (28 en 29 sep), bevestigd met BetExplorer",
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
                 "en staat in het runrapport onder 'Stand van het logboek': a=1.030, b=0.019 op "
                 "2346 afgerekende gevallen.",
    "POORT8": {
        "lapses_on": str(sides.LAPSES_ON),
        "actief_vandaag": sides.LAPSES_ON > DAY,
        "toelichting":
            "Derde volle dag ná de vervaldatum van §1e: sides.check() laat elke kant door en zet "
            "alleen nog would_block. Opnieuw geen selectie om hem op toe te passen. De eerste "
            "Run A waarin het vervallen van poort 8 werkelijk iets kan doen blijft die van "
            "9 oktober; leg daar poort8_vervallen per selectie vast en zet "
            "poort8_zou_hebben_geblokkeerd in de pick zodra zo'n selectie een gepubliceerde bet "
            "wordt (§1e).",
    },
}

state["stage1"] = {
    "module": "scripts/runwindow.py",
    "venster_nl": "[08:00 28 sep 2026, 08:00 29 sep 2026)",
    "include_carry_over": False,
    "reden_carry_over":
        "Uit, zoals §3 Stage 1 voorschrijft na de eenmalige overstap van 25 september. Hem "
        "aanzetten zou de band [00:00, 08:00) NL in twee runrapporten zetten.",
    "daglijsten": {"2026-09-28": 33, "2026-09-29": 51},
    "gevonden_in_venster": 0,
    "source_day_plus_1": 0,
    "onspeelbaar": 0,
}

state["credits"] = {
    "plafond": 0,
    "uitgegeven": 0,
    "markten_gekocht": {},
    "reden": "geen wedstrijd in de runlijst, dus geen enkele competitie om prijzen voor te kopen. "
             "The Odds API staat op 18.642 van de 20.000 over (api_check.py deze run).",
    "marktbalans": "niet van toepassing — er is niets ingekocht. §1a eist minstens één "
                   "doelpunten- en één uitkomstmarkt zodra er wél wordt ingekocht.",
}

state["bevestiging"] = {
    "vraag": "Speelt er vandaag werkelijk niets uit de runlijst, of matcht alleen de naam niet?",
    "methode_1":
        "Fotmob-daglijsten van 28 en 29 sep 2026 (33 respectievelijk 51 competities), per "
        "competitie uit de runlijst getoetst met find_league op naam, ccode en aliassen — 21 van "
        "de 21 leeg, op beide dagen. Dat het geen naamkwestie is, is aan de daglijst zelf te "
        "zien: wat er vandaag wél staat is interlandvoetbal (UEFA Nations League A/B/C, CONCACAF "
        "Nations League A/B, AFCON-kwalificatie in drie groepen, EURO U21-kwalificatie, FIFA "
        "ASEAN Cup, vijf friendlies) plus lagere en buitenlandse divisies — Azadegan League (5), "
        "Leumit League (4), Liga MX (2), Liga MX Femenil (3), Primera A en B in Colombia, "
        "LaLiga2 (1), Série B, Primera Nacional, QSL Cup (3). Bij een afwijkende competitienaam "
        "zou de hoogste divisie er wél staan; hier is LaLiga2 aanwezig en La Liga afwezig, en dat "
        "is precies het omgekeerde van wat een naamfout zou geven.",
    "methode_2":
        "Achttien BetExplorer-fixturepagina's, los van Fotmob opgehaald: Premier League 20 "
        "komende duels, Serie A 20, La Liga 20, Bundesliga 18, Ligue 1 18, Championship 12, "
        "Eredivisie 18, Primeira Liga 9, Pro League 9, Süper Lig 9, Scottish Premiership 12, "
        "Danish Superliga 6, Ekstraklasa 7, UCL 18, UEL 18, UECL 18, League Cup 8 — nul daarvan "
        "op vandaag, en de eerstvolgende staat overal op 9, 10, 11, 13 of 27 oktober. Coppa "
        "Italia gaf HTTP 200 met een lege tabel. Plus de drie bekers zonder URL in de hoofdlijst: "
        "DFB Pokal 16 komende duels met de eerste op 27 oktober; FA Cup en KNVB Beker geven bij "
        "BetExplorer een lege tabel, dus voor die twee blijft Fotmob de enige bron — dat is een "
        "bronbeperking en geen bevestiging, en het hoort zo opgeschreven te staan.",
    "methode_3_tegenproef":
        "Extra deze run, omdat een gat van elf dagen groot genoeg is om niet op één aanname te "
        "laten staan: de daglijsten van 3 en 4 oktober zijn met de hand nagekeken (104 en 84 "
        "competities). Daar spelen League One (11 en 12 duels), de Nederlandse Eerste en Tweede "
        "Divisie, LaLiga2, Serie C, de Duitse Regionalliga's en de Deense 2./3. Division wél, en "
        "staat er van de hoogste divisies niets. De daglijsten zijn dus gezond en gevuld; het "
        "zijn werkelijk alleen de topdivisies die stilliggen. Een defecte of halflege dagrespons "
        "zou de lagere divisies net zo goed hebben gemist.",
    "conclusie": "Alle drie de ingangen zeggen hetzelfde: de hoogste divisies liggen stil tot "
                 "9 oktober. GEEN WEDSTRIJD is de uitkomst, geen storing (Stage 2).",
    "context":
        "Achtste dag op rij, en de dag verliep exact zoals de scans van 25, 26 en 27 september "
        "hem voorspelden. Wat vandaag speelt is interlandvoetbal (Run C) en de lagere "
        "clubdivisies (Run B); hun aanwezigheid is geen gat in Run A en hun ontbreken hier "
        "evenmin (run-a.md).",
    "lege_periode": {
        "eerste_lege_dag": "2026-09-21",
        "laatste_lege_dag": "2026-10-08",
        "dag_in_de_reeks": 8,
        "lege_runs_nog_te_gaan": 10,
        "gemeten_met": "tmp-run/ra28_gap.py — 16 Fotmob-daglijsten van 28 sep t/m 13 okt, per dag "
                       "getoetst op alle 21 competities uit de runlijst. Onafhankelijk opgehaald "
                       "van de scans van 25, 26 en 27 september, en met dezelfde uitkomst: dat is "
                       "de vierde herhaling van hetzelfde antwoord.",
    },
    "eerstvolgende_speelronde": eerste_fotmob,
    "eerste_volle_dag": "2026-10-10 (56 wedstrijden uit de runlijst in 12 competities; 9 okt is "
                        "de vrijdagavond met 12 duels in 10 competities, 11 okt 41 in 13, "
                        "12 okt 9 in 7, 13 okt 17 in 2 waaronder de eerste UCL-speelronde)",
    "bekers": "FA Cup, League Cup, Coppa Italia, KNVB Beker en DFB Pokal staan in de hele "
              "gemeten periode t/m 13 oktober niet op een Fotmob-daglijst. BetExplorer zet de "
              "League Cup en de DFB Pokal beide op 27 oktober. Dat is kalender, geen gat.",
}

state["stage_min2"] = {
    "ondiepe_kloon": True,
    "vals_alarm_voor_unshallow":
        "git rev-parse --is-shallow-repository gaf true, en dat gaf precies het beeld dat §3 "
        "Stage -2 beschrijft: 31 van de 41 takken leken 27 tot 315 eigen commits te hebben en "
        "git merge-base main <tak> gaf niets terug. Na git fetch --unshallow (413 commits) is dat "
        "0 van de 41, op tak zealous-edison-elu4ga na, die één commit heeft die alleen een "
        "rapportlink vastlegt.",
    "vergelijking_per_regel":
        "Alle vijf de logboeken per record vergeleken over alle 41 takken, zoals de tabel sinds "
        "27 september eist — niet alleen picks.jsonl en niet op de commitgraaf.",
    "gevonden": {
        "data/picks.jsonl": "volledig — 319 records, niets ontbrak",
        "data/calibration.jsonl": "volledig — 3384 records (1128 wedstrijden × 3 uitkomsten)",
        "data/context-log.jsonl": "volledig — 836 records",
        "data/source-health.json": "geen tak met een afwijkende meting",
        "data/shadow.jsonl": "VIER RIJEN ONTBRAKEN, alle vier nog pending",
    },
    "verenigd": [
        "shadow-2026-09-15-a-elche---real-madrid (tak zealous-edison-6bbibv, failed_gate=edge)",
        "shadow-2026-09-19-b-gillingham---bristol-rovers-nocal-0 (elu4ga, herijking)",
        "shadow-2026-09-19-b-luzern---grasshopper-nocal-0 (elu4ga, herijking)",
        "shadow-2026-09-19-b-blackpool---plymouth-argyle-nocal-0 (elu4ga, herijking)",
    ],
    "les":
        "Tak elu4ga telde ná het unshallowen 0 eigen commits en zág er dus schoon uit, terwijl er "
        "drie metingen op stonden die hier ontbraken — exact de waarschuwing van 27 september dat "
        "'0 eigen commits' een uitspraak over de graaf is en niet over de metingen. Alle vier de "
        "rijen zijn in Stage 0 afgewikkeld en wonnen; de herijking-reeks krijgt er drie bij en "
        "staat nu op 64 kandidaten, 55 afgewikkeld, ROI -2,7%.",
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
        "Alle acht de picks en alle zestien schaduwrijen komen uit wedstrijden die Fotmob als "
        "afgelopen meldde zonder verlenging of strafschoppen, dus de eindstand ís hier de stand "
        "na 90 minuten (§6d). Nagekeken op de knock-outval: Gibraltar – Andorra (0-0) staat in "
        "Nations League D groep 2 en is geen tweeluik, en Serbia – Netherlands en Denmark – Wales "
        "zijn groepsduels in Nations League A. Geen enkele rij komt uit een beker- of "
        "play-offduel waar 90 minuten en eindstand kunnen verschillen.",
    "bevinding":
        "Vijf verliezers op acht afgewikkelde picks, twee winnaars (Real Oviedo – Sporting Gijón "
        "Under 2.5 @ 1.61, en Serbia – Netherlands AH +1.25 Serbia @ 2.07 dat op een kwartlijn "
        "half uitbetaalde) en één void (Gibraltar – Andorra, DNB bij 0-0). Dat haalt de drempel "
        "van §7 voor een afwikkelingsreeks die opvalt (5+ verliezers), dus het staat vooraan in "
        "de notificatie. Wat het níet is, is een bevinding over de routine: het gaat om de picks "
        "van Run B en Run C van 27 september, niet om een beslissing van vandaag, en §6d zegt dat "
        "één dag bij deze aantallen ruis is. Het logboek als geheel schuift er dan ook nauwelijks "
        "van op — 319 picks, 265 bets, ROI -9,4%, hit rate 43,8%. Niets bleef openstaan: alle "
        "acht de picks en alle zestien schaduwrijen zijn afgewikkeld, inclusief de vier rijen die "
        "Stage -2 vandaag heeft verenigd.",
    "schaduw_bevinding":
        "De schaduwkant liep de andere kant op: elf winnaars op zestien rijen. Dat zijn de "
        "kandidaten die de poorten hebben tegengehouden, dus op één dag gelezen betekent het dat "
        "de poorten vandaag geld hebben gekost. Over het hele logboek staat die rekening andersom "
        "(687 kandidaten, ROI -6,4%, oftewel 42,43u bespaard) en §6d zegt uitdrukkelijk dat één "
        "dag bij deze aantallen ruis is. Niet op grond hiervan een poort verruimen.",
}

state["duur"] = {
    "gestart": state.get("duur", {}).get("gestart") or "2026-09-28T02:13:00+00:00",
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

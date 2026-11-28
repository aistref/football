"""§6b-3 — data/source-health.json bijwerken met wat DEZE run gemeten heeft.

Alles wat hier wordt gezet is een eigen waarneming van Run B van 28 nov 2026, geen overname. Het
blok `last_run_run_b` wordt vervangen en zijn vorige inhoud schuift gedateerd naar `history`, zoals
de merge-regel van §3 Stage -2 eist: bewaren naast elkaar, niets overschrijven.
"""
import json
from datetime import datetime, timezone

PAD = "data/source-health.json"
d = json.load(open(PAD))

NU = datetime.now(timezone.utc).isoformat()

blok = {
    "run": "B",
    "date": "2026-11-28",
    "matches_in_window": 65,
    "analysed": 45,
    "truncated": 10,
    "bets": 5,
    "qualified_not_published": 0,
    "credits": ("60 van een plafond van 3119 (33 bulk voor 11 competities + 27 event-BTTS); "
                "18674 over, 1326 gebruikt deze maand na deze run"),
    "note": (
        "VIJFTIEN van de zeventien competities spelen, met 65 duels in het inzetvenster "
        "[08:00 NL 28 nov, 08:00 NL 29 nov): English League Two 12, English League One 11, MLS 6, "
        "Segunda División 5, Serie B 5, 2. Bundesliga 4, Czech First League 3, Greek Super League "
        "3, Hungarian NB I 3, Romanian SuperLiga 3, Swiss Super League 3, Croatian HNL 2, "
        "Eliteserien 2, Austrian Bundesliga 2, Série A (BRA) 1. Ruimste runlijstdag van de maand. "
        "DE ZATERDAGCAP VAN 55 BINDT, voor het eerst sinds 24 oktober: 10 duels afgekapt, bij naam "
        "genoemd in afkapping.lijst. De laagste die het haalde (Austria Lustenau - Rapid Wien) en "
        "de hoogste die afviel (VfL Osnabrück - Hannover 96) hebben EXACT dezelfde datarijkdom "
        "(5,5) en hetzelfde aantal markten (5), dus de aftrap heeft de knip gelegd en niet de "
        "informatie — bekend gedrag, §3 Stage 4 meet sinds 5 sep dat deze sortering niet scheidt. "
        "Elf spelende competities hebben xG bij Fotmob (54 duels), vier niet (11 duels: Czech "
        "First League, Croatian HNL, Hungarian NB I, Romanian SuperLiga); eindstand over de 51 "
        "duels met een tier: 30 FULL, 21 LIGHT, plus 14 op NONE. De 14 op NONE: 6 degradanten "
        "zonder stand in de divisie erboven (Ascoli, Vicenza, Benevento, VfL Osnabrück, York City, "
        "Rochdale), 7 promovendi buiten het gemeten bereik van conversion_in_range, en 1 om de "
        "bekende Hongaarse bronreden (id 9117 negeert de seizoensparameter, §4 11 okt 2026) — alle "
        "veertien GEMETEN weigeringen. 575 selecties doorgerekend over alle zes de markten op 45 "
        "duels; 451 (78%) sneuvelden op poort 5 (derde dag op rij in die orde), 46 op de "
        "edge-afkapping, 30 op poort 8, 21 op de koersband, 15 op poort 7, 5 op poort 6, 0 op "
        "poort 9 en 7 bleven open. "
        "VIJF GEPUBLICEERDE REGELS EN ALLE VIJF OP DE UNDER-KANT VAN OVER/UNDER — bij deze "
        "runlijst niet eerder voorgekomen. Twee halen hun eigen lat en ook de verzwaarde "
        "Under-lat van 10,0 (Rosenborg - Molde +16,16 pp, Bodø/Glimt - KFUM +10,82 pp); drie staan "
        "er volledig op rangorde met +7,56, +6,93 en +6,86 pp (§5b) en liggen daarmee ONDER de "
        "gewone drempel, waar poort 9 per ontwerp niet bijt. De lijstlengte bindt niet: maar twee "
        "duels hebben een selectie die alle negen poorten én de drempel haalt, dus geen enkele "
        "gekwalificeerd_niet_gepubliceerd. MAX_LIGHT_IN_SHORTLIST bindt niet: alle vijf FULL. "
        "ALLE ZES MLS-DUELS ZIJN KNOCK-OUTWEDSTRIJDEN (Fotmob: 'Major League Soccer Playoff', "
        "parentLeagueId 130, tournamentStage 1/8), apart benoemd in de dekkingstoelichting zoals "
        "Run B van 27 nov had aangekondigd. Los Angeles FC - St. Louis City is de tweede wedstrijd "
        "van die reeks: St. Louis won op 24 nov met 3-2. Drie duels staan op een Amerikaanse klok "
        "en komen van de daglijst van 29 november. De controle langs drie wegen op de twee stille "
        "competities: idcheck.py 33/33 met afsluitcode 0, BetExplorer 17 van 17 eens (65 tegen 65 "
        "duels), runwindow.py voor het venster. Stage 0 had niets te doen (Run A had om 02:46 al "
        "afgewikkeld); calibration.py settle en ctxlog.py settle zijn tóch gedraaid zoals §6b-5c/d "
        "van ELKE run eisen, en recalibrate.fitted_through staat op 2026-11-27, de vorige rundag. "
        "progress.py verify groen: 45 van 45 geanalyseerde duels hebben alle zes markten gehad."
    ),
    "bevinding": (
        "28 nov 2026, Run B — DE BEVINDING VAN RUN A IS PER RUN UITGESPLITST EN DE UITSPLITSING "
        "ZEGT IETS NIEUWS: HET MECHANISME IS GELIJK, DE BLOOTSTELLING SCHEELT EEN FACTOR VIJF. "
        "Run A heeft vanmorgen gemeten dat de routine aan BEIDE kanten van de doelpuntenmarkt de "
        "verkeerde duels kiest: 153 gespeelde Unders op +0,661 doelpunt per duel (z = +4,92), 87 "
        "gespeelde Overs op -0,368 (z = -1,87), terwijl de hele populatie van 2521 doorgerekende "
        "duels op +0,019 staat (z = +0,56) — selectie, geen rekenfout. Die bevinding staat en is "
        "hier niet overgedaan. NIEUW is de uitsplitsing per run. Per duel is de fout gelijk: "
        "Run A / Under n=65 op +0,620 (z = +2,96), Run B / Under n=88 op +0,692 (z = +3,95); "
        "Run A / Over n=72 op -0,386 (z = -1,77), Run B / Over n=15 op -0,280 (z = -0,61). "
        "HET VERSCHIL ZIT IN DE BLOOTSTELLING: Run B heeft 107 Unders tegen 21 Overs gepubliceerd, "
        "Run A 77 tegen 90. In november alleen: Run B 30 tegen 5, Run A 18 tegen 22. In geld: "
        "Run B / Under 107 gevallen op -14,3% (t = -1,56) en -15,25u; Run A / Under 77 op -21,9% "
        "(t = -2,03) en -16,89u; Run A / Over 90 op +6,3% (t = +0,63) en +5,63u. Vandaag staat "
        "Run B er VIJF VAN DE VIJF keer op. ONAFHANKELIJKE TOETS DIE DIT ONDERSTREEPT: over alle "
        "36 duels waarvoor Pinnacle zowel 1X2 als totalen gaf, staat de eigen P(Under) gemiddeld "
        "+1,51 pp boven Pinnacle's de-vigde P(Under) (23 van 36 erboven). De vijf gepubliceerde "
        "regels staan op +15,17, +9,31, +9,31, +6,26 en +5,50 pp boven Pinnacle — dus niet een "
        "greep uit die scheve verdeling maar de vijf uitersten ervan. Dat is §1g in zijn zuiverste "
        "vorm: het grootste geclaimde voordeel is de grootste modelfout. "
        "WAT NIET IS GEDAAN: geen poort, lat, gewicht of drempel aangeraakt, en geen marktquotum "
        "(§1 verbiedt forceren om een verdeling te halen, ook de andere kant op). De vraag of "
        "poort 9 breder moet gelden is op 22, 23, 24, 25 en 26 november voorgelegd en door Run B "
        "van 27 nov teruggetrokken naar owner=ik; §1h/§6c/§9 verbieden herhaling en ze is niet "
        "herhaald. Wat WEL als besluitpunt is voorgelegd, één keer en zonder voorstel: de "
        "blootstellingsvraag zelf. TWEEDE WAARNEMING: de niveaucorrectie van 2 nov is op haar "
        "eigen populatie DOOR NUL GESCHOTEN. Op de 545 duels met lambdas van ná 3 nov staat het "
        "gemiddelde totaal op -0,097 per duel (z = -1,29) waar het vóór de correctie +0,100 was "
        "(z = +1,93), en de fout op P(Under 2.5) is van -2,35 pp naar +1,94 pp gegaan (z = +0,92). "
        "Geen van beide haalt |z| = 2 en §6g punt 4 eist maanden; Run A heeft die vraag vandaag op "
        "januari gezet en Run B dupliceert hem niet. NIETS VERZET."
    ),
    "sources_deze_run": {
        "fotmob": ("ok; 2 daglijsten (28 en 29 nov), standen van 15 competities over 2 seizoenen, "
                   "context van 65 van 65 duels zonder fout (60 ervan volledig genoeg voor "
                   "ctxlog), marktvorm van 51, voorbeschouwing van 5 van 5"),
        "betexplorer": ("ok; fixturepagina voor alle 15 de spelende competities, en als tweede "
                        "bron 17 van 17 competities eens met Fotmob op 65 tegen 65 duels"),
        "the_odds_api": ("ok; 46 actieve voetbalcompetities, 18734 over bij de start. 11 "
                         "bulkaanroepen h2h+spreads+totals (33 credits) + 27 event-BTTS (27 "
                         "credits) = 60; 18674 over na deze run. 33 van 34 sportkeys van de repo "
                         "actief; alleen UEFA Conference League niet (Run A-competitie). Vijf "
                         "actieve sportkeys die de repo niet kent (Brazil Série B, Coupe de "
                         "France, 3. Liga, Superettan, UEFA Nations League) — geen daarvan staat "
                         "op een runlijst, dus informatie en geen gat"),
        "pinnacle_via_odds_api": ("ok; 1X2 voor 36 van de 65 duels (gemiddelde marge 4,07%) en "
                                  "totalen voor 36 (duel, lijn)-paren. Gemiddelde absolute "
                                  "afstand tot het Pinnacle-1X2-oordeel 3,72 pp. Op de totalen "
                                  "staat de eigen P(Under) gemiddeld +1,51 pp boven Pinnacle "
                                  "(23 van 36 erboven); op zuivere halve lijnen +0,15 pp over 11 "
                                  "paren en op lijnen met push +2,10 pp over 25. De vijf "
                                  "gepubliceerde regels staan op +15,17 (Rosenborg - Molde), "
                                  "+9,31 (Bodø/Glimt - KFUM), +9,31 (AFC Wimbledon - Barnsley), "
                                  "+6,26 (Las Palmas - FC Andorra) en +5,50 pp (Los Angeles FC - "
                                  "St. Louis City) boven Pinnacle"),
        "understat": ("niet nodig voor deze runlijst, maar tóch gemeten: alle vijf competities "
                      "(EPL, La_liga, Bundesliga, Serie_A, Ligue_1, seizoen 2026) geven HTTP 200 "
                      "met 26.719 bytes en geen JSON, 'UnderstatError: geen JSON terug'. EXACT "
                      "dezelfde bytelengte als op 26 en 27 nov en als Run A van vandaag — "
                      "elfde aaneengesloten meting met hetzelfde foutbeeld, wat op een "
                      "blokkadepagina lijkt en niet op een server die eruit ligt. KOSTTE DEZE RUN "
                      "NIETS: geen van de vijftien spelende competities van de Run B-lijst staat "
                      "bij Understat"),
        "api_football": ("sleutel ontbreekt — besluit van de gebruiker van 27 sep 2026, geen "
                         "storing en geen actiepunt (§3). De kanskant komt van Fotmob en "
                         "Understat; Fotmob leverde vandaag volledig, dus de uitzondering van §3 "
                         "punt 3 is niet aan de orde"),
    },
}

# Vorige snapshot gedateerd bewaren (§3 Stage -2: verenigen, niet overschrijven).
oud = {k: v for k, v in d.get("last_run_run_b", {}).items() if k != "history"}
hist = list(d.get("last_run_run_b", {}).get("history") or [])
if oud.get("date") and oud["date"] != blok["date"]:
    hist.insert(0, {"date": oud["date"],
                    "note": (f"Tekstblok van Run B van {oud['date']}, bewaard bij het bijwerken "
                             f"van {blok['date']}."),
                    "blok": oud})
d["last_run_run_b"] = {"history": hist, **blok}
d["last_run"] = NU
d["updated"] = NU
d["last_run_bevinding"] = blok["bevinding"]

# Scrape- en sleutelbronnen op het niveau van `sources` bijwerken met de eigen meting.
d["sources"].setdefault("fotmob", {})
d["sources"]["fotmob"].update({
    "status": "ok", "last_checked": blok["date"],
    "detail": ("28 nov (run B): ok. Twee daglijsten, standen van 15 competities over twee "
               "seizoenen, context van 65 van 65 duels zonder fout, marktvorm van 51 en "
               "voorbeschouwingsdata van 5 van 5. Geen enkele fout."),
})
d["sources"].setdefault("betexplorer", {})
d["sources"]["betexplorer"].update({
    "status": "ok", "last_checked": blok["date"],
    "detail": ("28 nov (run B): ok voor alle 15 de spelende competities van de Run B-lijst, en als "
               "tweede bron voor de vraag wélke duels er zijn 17 van 17 competities eens met "
               "Fotmob (65 tegen 65 duels)."),
})
d["sources"].setdefault("the_odds_api", {})
d["sources"]["the_odds_api"].update({
    "status": "ok", "last_checked": blok["date"],
    "detail": ("28 nov (run B): ok, 46 actieve competities, 18734 over bij de start en 18674 na "
               "deze run (60 credits: 11 bulk + 27 event-BTTS). 33 van de 34 sportkeys van de "
               "repo vandaag actief; alleen UEFA Conference League niet."),
})
d["sources"].setdefault("understat", {})
d["sources"]["understat"].update({
    "status": "geen_json", "last_checked": blok["date"],
    "detail": ("28 nov (run B): ELFDE AANEENGESLOTEN METING MET HETZELFDE FOUTBEELD. Alle vijf "
               "competities (EPL, La_liga, Bundesliga, Serie_A, Ligue_1, seizoen 2026) geven HTTP "
               "200 met 26.719 bytes en geen JSON — 'UnderstatError: geen JSON terug'. Exact "
               "dezelfde bytelengte als op 26 en 27 nov en als Run A van vanmorgen, wat op een "
               "blokkadepagina lijkt en niet op een server die eruit ligt. Voor Run B kostte het "
               "niets: geen van de vijftien spelende competities van deze lijst staat bij "
               "Understat."),
})

json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt; history van last_run_run_b heeft nu",
      len(d["last_run_run_b"]["history"]), "blokken")

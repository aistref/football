"""§6b-3 — data/source-health.json bijwerken met wat DEZE run gemeten heeft.

Alles wat hier wordt gezet is een eigen waarneming van Run B van 27 nov 2026, geen overname. Het
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
    "date": "2026-11-27",
    "matches_in_window": 19,
    "analysed": 18,
    "truncated": 0,
    "bets": 3,
    "qualified_not_published": 0,
    "credits": ("29 van een plafond van 2352 (15 bulk voor 5 competities + 2 x 7 BTTS per event: "
                "de tweede ronde is na de naamreparatie nog een keer gedraaid en kostte 7 credits "
                "extra die niets nieuws opleverden); 18809 over, 1191 gebruikt deze maand na deze run"),
    "note": (
        "TIEN van de zeventien competities spelen, met 19 duels in het inzetvenster "
        "[08:00 NL 27 nov, 08:00 NL 28 nov): Keuken Kampioen Divisie 7, Romanian SuperLiga 2, "
        "2. Bundesliga 2, MLS 2 en Czech First League, Croatian HNL, Hungarian NB I, Segunda "
        "División, Austrian Bundesliga en Série A (BRA) met elk 1. Ruimste runlijstdag sinds "
        "22 november. De vrijdagcap van 55 bindt NIET, niets afgekapt. Vijf spelende competities "
        "hebben xG bij Fotmob (7 duels), vijf niet (12 duels, waarvan de Keuken Kampioen Divisie "
        "alleen al 7); eindstand 5 FULL, 13 LIGHT, 1 NONE. Het duel op NONE is Artis Brno - "
        "Slovácko: Artis Brno is promovendus en promotion.convert weigert de omrekening op "
        "conversion_in_range, een GEMETEN weigering. 134 selecties doorgerekend over alle zes de "
        "markten op 18 duels; 104 (76%) sneuvelden op poort 5, 12 op de edge-afkapping, 6 op de "
        "koersband, 4 op poort 7, 4 op poort 8, 3 op poort 6, 2 op poort 9 en 2 bleven open. "
        "DRIE gepubliceerde regels uit DRIE verschillende markten (DNB, BTTS, Over/Under), "
        "waarvan ÉÉN boven zijn eigen lat (Real Salt Lake - Vancouver Whitecaps, +8,41 pp op een "
        "FULL-lat van 8,0); de andere twee op rangorde (§5b). De lijstlengte bindt niet: drie "
        "publiceerbare selecties op drie plekken, geen enkele gekwalificeerd_niet_gepubliceerd. "
        "DE TWEE MLS-DUELS ZIJN GEEN COMPETITIEDUELS maar de eerste knock-outronde: Fotmob zet ze "
        "onder league-id 957981 'Major League Soccer Playoff' met parentLeagueId 130 en "
        "tournamentStage 1/8, en runwindow matcht op primaryId. De rekensom is juist (beide "
        "ploegen uit dezelfde divisie, §4 'basis per WEDSTRIJD'), maar de dekkingstabel leest als "
        "een speelronde; vanaf vandaag apart benoemd in de dekkingstoelichting. Real Salt Lake - "
        "Vancouver is de return: Vancouver won op 23 nov thuis met 2-0. De controle langs drie "
        "wegen op de zeven stille competities: idcheck.py 33/33 met afsluitcode 0, BetExplorer "
        "17 van 17 eens (19 tegen 19 duels), runwindow.py voor het venster. "
        "GEREPAREERD DEZE RUN: twee duels kwamen binnen met NUL prijzen in alle zes de markten "
        "terwijl BetExplorer ze wel had. Jong AZ Alkmaar - TOP Oss stond daar als 'Jong AZ - Oss' "
        "en kwam op een paarscore van 0,618, twee duizendsten onder de vloer van 0,62; de "
        "woordterugval van 30 okt keek alleen naar de KOP en ['oss'] is de STAART van "
        "['top','oss']. ra_names._prefix_pair is _affix_pair geworden en kijkt nu ook naar de "
        "staart, met een rem op reserveaanduidingen (['psv'] is een staart van ['jong','psv'] en "
        "MVV - Jong PSV stond dezelfde ochtend op de lijst); selftest 26 van 26 groen. De analyse "
        "is daarna VOLLEDIG opnieuw gedraaid: 134 -> 137 selecties, geen van de drie nieuwe haalt "
        "de rangorde, gepubliceerde lijst ONGEWIJZIGD. Universitatea Cluj - Sepsi OSK blijft met "
        "opzet ongekoppeld ('U. Cluj' is een afkorting, 'Sepsi OSK' deelt alleen het eerste woord "
        "met 'Sepsi Sf. Gheorghe' - koppelen daarop is de Excelsior-val van 27 okt). progress.py "
        "verify STOND GROEN, voor en na: markets_checked had per markt een reden en die reden was "
        "onwaar. Vierde geval in deze familie na la galaxy (17 okt), red bull new york (30 sep) en "
        "Roda - Jong AZ (30 okt)."
    ),
    "bevinding": (
        "27 nov 2026, Run B — DE TRIGGER DIE §1h PUNT 2 VOOR ZICHZELF STELDE IS NU PER KANT EN "
        "TIER TE METEN, EN DE METING STEUNT DE UITBREIDING NIET. §1h houdt BTTS buiten poort 9 "
        "omdat 15 afgewikkelde BTTS-picks in beide richtingen samen geen meting is, en noemt dit "
        "'het eerste wat opnieuw bekeken hoort te worden zodra die reeks ~30 haalt'. Op 8 nov "
        "haalde de gepoolde reeks de 31 en is de vraag één keer aan de gebruiker voorgelegd (§6c "
        "verbiedt herhaling; niet herhaald). Stand vandaag: 39 BTTS-picks, 38 beslist, +32,6%. "
        "BTTS-nee 23 beslist op +11,8%; BTTS-nee op FULL 21 beslist op -2,4% bij t = -0,10. Naar "
        "band, niet cumulatief: 0-8 pp n=9 op -53,8% (t = -1,76), 8-10 pp n=8 op +27,4% "
        "(t = +0,73), 10-12 pp n=2 op +99,5%, 12-14 pp n=2 op +7,8%. Vergelijk de Under-kant van "
        "Over/Under op FULL, waarvoor poort 9 gebouwd is: 0-8 pp n=69 op -17,6%, 8-10 pp n=17 op "
        "-33,2%, hele reeks 152 gevallen op -16,2% bij t = -2,11 — de enige reeks hier die |t| = 2 "
        "haalt. IN DE BAND WAAR POORT 9 ZIJN BESTAANSRECHT AAN ONTLEENT STAAT BTTS-NEE MET HET "
        "OMGEKEERDE TEKEN. Geen gemeten grond om de rem uit te breiden, en ook geen grond om hem "
        "te verlichten: n=8 is ver onder de ~30 van §6d en de hele BTTS-nee-FULL-reeks staat op "
        "21. NIETS VERZET. ONGEMAKKELIJKE KANT: de tweede regel van vandaag staat zelf op BTTS-nee "
        "(Fluminense - Cruzeiro, +7,81 pp) en valt in de band 0-8 pp waar diezelfde reeks op "
        "-53,8% staat; die tegenspraak staat vooraan in de voorbeschouwing (§4 punt 2), naast de "
        "seizoensfrequenties (Cruzeiro uit 72% BTTS, Fluminense thuis 67%) die dezelfde kant op "
        "wijzen. Wat de andere kant op wijst is de onderlinge historie: 6 duels, 1,33 doelpunt per "
        "duel, BTTS 1 van 6. TWEEDE WAARNEMING: diezelfde regel leunt voor 75% op de splitsmethode "
        "(+2,21 pp op xG tegen +26,86 pp op de splits; poort 5 toetst het TEKEN en niet de "
        "AFSTAND). Nagerekend over 266 beslist afgewikkelde picks met beide methodecijfers wijst "
        "dat NIET de verkeerde kant op: splits levert >50% van de ruwe edge -> +15,0% over 38 bij "
        "t = +0,98; <=50% -> -10,3% over 228 bij t = -1,58. Geen van beide haalt |t| = 2. NIETS "
        "VERZET."
    ),
    "sources_deze_run": {
        "fotmob": ("ok; 2 daglijsten (157 duels op 27 nov, 573 op 28 nov), standen van 10 "
                   "competities over 2 seizoenen, context van 19 van 19 duels zonder fout, "
                   "marktvorm van 18, voorbeschouwing van 3 van 3"),
        "betexplorer": ("ok; fixturepagina voor alle 10 de spelende competities, en als tweede "
                        "bron 17 van 17 competities eens met Fotmob op 19 tegen 19 duels"),
        "the_odds_api": ("ok; 44 actieve voetbalcompetities, 18838 over bij de start. 5 "
                         "bulkaanroepen h2h+spreads+totals (15 credits) + 7 event-BTTS (7 "
                         "credits) = 22; 18816 over na deze run. 32 van 34 sportkeys van de repo "
                         "actief; Conference League en Europa League niet actief vandaag"),
        "pinnacle_via_odds_api": ("ok; 1X2 voor 7 van de 19 duels (marge 3,5-4,6%) en totalen "
                                  "voor 7 (duel, lijn)-paren. Gemiddelde absolute afstand tot het "
                                  "Pinnacle-oordeel 5,70 pp; grootste onenigheid FC Heidenheim - "
                                  "1. FC Nürnberg (+21,9 pp op de thuisploeg, geen bet) en op de "
                                  "totalen Leganés - Sabadell (-14,05 pp op de Under-kant, wél "
                                  "een bet)"),
        "understat": ("niet_bevraagd -> FAIL, zelf opnieuw gemeten: alle vijf competities (EPL, "
                      "La_liga, Bundesliga, Serie_A, Ligue_1, seizoen 2026) geven HTTP 200 met "
                      "26.719 bytes en geen JSON, 'UnderstatError: geen JSON terug'. EXACT "
                      "dezelfde bytelengte als op 26 nov en als Run A van vandaag — tiende "
                      "aaneengesloten meting met hetzelfde foutbeeld, wat op een blokkadepagina "
                      "lijkt en niet op een server die eruit ligt. KOSTTE DEZE RUN NIETS: geen "
                      "van de tien spelende competities van de Run B-lijst staat bij Understat"),
        "api_football": ("sleutel ontbreekt — besluit van de gebruiker van 27 sep 2026, geen "
                         "storing en geen actiepunt (§3). De kanskant komt van Fotmob en "
                         "Understat; Fotmob leverde vandaag volledig"),
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
    "detail": ("27 nov (run B): ok. Twee daglijsten, standen van 10 competities over twee "
               "seizoenen, context van 19 van 19 duels zonder fout, marktvorm van 18 en "
               "voorbeschouwingsdata van 3 van 3. Geen enkele fout."),
})
d["sources"].setdefault("betexplorer", {})
d["sources"]["betexplorer"].update({
    "status": "ok", "last_checked": blok["date"],
    "detail": ("27 nov (run B): ok voor alle 10 de spelende competities van de Run B-lijst, en als "
               "tweede bron voor de vraag wélke duels er zijn 17 van 17 competities eens met "
               "Fotmob (19 tegen 19 duels)."),
})
d["sources"].setdefault("the_odds_api", {})
d["sources"]["the_odds_api"].update({
    "status": "ok", "last_checked": blok["date"],
    "detail": ("27 nov (run B): ok, 44 actieve competities, 18838 over bij de start en 18816 na "
               "deze run (22 credits: 5 bulk + 7 event-BTTS). 32 van de 34 sportkeys van de repo "
               "vandaag actief."),
})
d["sources"].setdefault("understat", {})
d["sources"]["understat"].update({
    "status": "geen_json", "last_checked": blok["date"],
    "detail": ("27 nov (run B): TIENDE AANEENGESLOTEN METING MET HETZELFDE FOUTBEELD. Alle vijf "
               "competities (EPL, La_liga, Bundesliga, Serie_A, Ligue_1, seizoen 2026) geven HTTP "
               "200 met 26.719 bytes en geen JSON — 'UnderstatError: geen JSON terug'. Exact "
               "dezelfde bytelengte als op 26 nov en als Run A van vanmorgen, wat op een "
               "blokkadepagina lijkt en niet op een server die eruit ligt. Voor Run B kostte het "
               "niets: geen van de tien spelende competities van deze lijst staat bij Understat. "
               "Voor Run A kostte het op 27 nov wél iets (alle vijf speelden) — zie "
               "last_run_run_a."),
})

json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health bijgewerkt; history van last_run_run_b heeft nu",
      len(d["last_run_run_b"]["history"]), "blokken")

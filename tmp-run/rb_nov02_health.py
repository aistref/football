"""Run B, 2 nov 2026 — `data/source-health.json` bijwerken met wat DEZE run gemeten heeft (§3).

Alleen de bronnen die vandaag werkelijk zijn aangeroepen krijgen een nieuwe `detail` en een
nieuwe `last_checked`. De bronnen die al maanden dichtzitten (fbref, Forebet, FootyStats,
PredictZ, WhoScored) worden niet opnieuw geprobeerd — §3 verbiedt het omzeilen van hun
Cloudflare-challenge, dus er is niets nieuws te meten en hun regel blijft staan.
"""
import json
from datetime import datetime, timezone

PAD = "data/source-health.json"
d = json.load(open(PAD))
S = d["sources"]
VANDAAG = "2026-11-02"


def zet(key, status, detail):
    S[key]["status"] = status
    S[key]["last_checked"] = VANDAAG
    S[key]["detail"] = detail


zet("fotmob", "ok",
    "2 nov (run B): daglijsten 2 en 3 nov opgehaald (79 en 53 competities, 153 en 165 duels) en "
    "voor de afwikkeling die van 1 en 2 nov. idcheck.py gaf voor alle 33 fotmob_id's uit "
    "coverage.json een bruikbare stand, afsluitcode 0. Standen van alle zes spelende competities "
    "plus de divisie eronder of erboven voor de ACHT omgerekende ploegen geleverd: Super League 2 "
    "(8815, per groep) voor Kalamata en Iraklis, Superettan voor Kalmar FF, Liga II voor FC "
    "Voluntari, Primera Federacion voor Tenerife, La Liga voor Real Oviedo en Mallorca, en de "
    "Eredivisie voor Heracles en NAC Breda. Context voor ALLE VIJFTIEN duels opgehaald zonder een "
    "enkele fout. Bij vijf duels is het aandeel ontbrekende selectiewaarde niet te berekenen "
    "(selectiewaarde nul of afwezig aan minstens een kant), waardoor die vijf niet in het "
    "contextlogboek belanden (tien van de vijftien) en de datarijkdom er het middenpunt krijgt in "
    "plaats van nul (§1c: een meting die er niet is, is geen bewijs van een probleem). Fotmob is "
    "vandaag de ENIGE xG-bron: geen enkele competitie van de Run B-runlijst wordt door Understat "
    "gedekt, dus dat is geen storing maar de normale stand voor deze runlijst. EEN WAARNEMING OVER "
    "DE DAGLIJST ZELF: Tenerife - FC Andorra stond op de daglijst van 1 november op "
    "2026-11-01T20:00Z en staat vandaag op 2026-11-02T13:00Z. De fixture is dus een dag "
    "opgeschoven nadat Run B van 1 november hem al in zijn venster had meegenomen; de bron geeft "
    "daar geen signaal bij en de verschuiving is alleen te zien door de twee daglijsten te "
    "vergelijken.")

zet("the_odds_api", "ok",
    "2 nov (run B): api_check.py meldt 49 actieve voetbalcompetities en 19859 credits over van "
    "20.000 (141 verbruikt deze maand). 33 van de 34 sportkeys van de repo zijn vandaag actief; "
    "alleen Coppa Italia (soccer_italy_coppa_italia) staat op niet-actief, wat buiten de "
    "Run B-runlijst valt. Vijf actieve sportkeys kent de repo niet: soccer_brazil_serie_b, "
    "soccer_germany_liga3, soccer_spain_copa_del_rey, soccer_sweden_superettan en "
    "soccer_uefa_nations_league - geen van die vijf staat op de Run B-runlijst, dus het is geen "
    "gat in deze run. Plafond van de run 342 credits (suggest_cap(19859, 29), 2 runs per dag), "
    "verdeling split_budget(342, 4) -> 4 spreads / 4 totals, dus de bulk (3 credits per "
    "competitie) paste ruim. Vier bulk-aanroepen (Greek Super League 9 events, Allsvenskan 11, "
    "Segunda Division 14, Serie A BRA 10) en zes BTTS-aanroepen a 2 credits = 12 + 6 = 18 van 342. "
    "Marktbalans op de INKOOP gehaald voor 4 van de 4 inkoopbare competities: elke bulk levert "
    "zowel een uitkomst- als een doelpuntenmarkt. Romanian SuperLiga en Keuken Kampioen Divisie "
    "hebben geen sportkey en draaien op het gratis BetExplorer-gemiddelde; dat zijn dezelfde twee "
    "competities die ook geen xG hebben, dus hun zes duels zijn op beide assen de zwakste van de "
    "dag.")

zet("betexplorer", "ok",
    "2 nov (run B): fetch_league_fixtures voor alle zes spelende competities geleverd (Greek Super "
    "League 16 rijen, Allsvenskan 11, Romanian SuperLiga 18, Segunda Division 14, Keuken Kampioen "
    "Divisie 10, Serie A BRA 19) en daarnaast voor de elf stille competities, want de "
    "tweede-broncontrole moet juist dáár kijken. DE TWEEDE BRON IS HET OVER ALLE ZEVENTIEN "
    "COMPETITIES EENS MET FOTMOB: 15 duels in het inzetvenster tegen 15, met de eerstvolgende "
    "ronde van de stille competities erbij (4 t/m 14 november). Nul afwijkingen - de eerste dag "
    "deze week zonder. Het 1X2-marktgemiddelde (11 boeken bij Kalamata - Iraklis) is gebruikt voor "
    "het kalibratieblok van §6e en voor poort 8, en als enige 1X2-bron voor de zes duels in "
    "Romanian SuperLiga en Keuken Kampioen Divisie. Bij Serie A (BRA) labelt BetExplorer het duel "
    "van vanavond (23:00Z) niet als 'today'; dat is geen fout maar de paginadatum, en de prijs "
    "voor dat duel komt uit de bulk-aanroep.")

zet("pinnacle", "ok",
    "2 nov (run B): Pinnacle-prijzen in de respons voor 29 events. 1X2 te de-viggen voor ZEVEN van "
    "de vijftien duels, met een marge van 3,0 tot 4,9% (gemiddeld 3,96%) en een gemiddelde "
    "absolute afstand tot het eigen model van 4,05 pp. Totalen voor zeven (duel, lijn)-paren. DE "
    "BEVINDING VAN DEZE RUN AAN DEZE KANT: op de Under-kant staat het eigen model gemiddeld "
    "+3,69 pp boven Pinnacle en op 5 van de 7 paren erboven, en op de drie ZUIVERE HALVE LIJNEN "
    "(geen push) is dat +7,46 pp op 3 van 3 - Real Oviedo - Las Palmas +9,81, Mallorca - Cadiz "
    "+7,05 en Mjallby - Kalmar FF +5,51. Dat is dezelfde richting als de scheefstand die §6g op "
    "uitkomsten meet, nu in een onafhankelijke bron, en twee van die drie duels zijn vandaag een "
    "gepubliceerde regel. Atromitos - NFC Volos is NIET tegen Pinnacle te leggen: dat duel wordt "
    "door Pinnacle niet geprijsd, noch op 1X2 noch op totalen, en het is wel de derde "
    "gepubliceerde regel.")

zet("promotion_omrekening", "ok",
    "2 nov (run B): ACHT van de vijftien duels hadden een ploeg zonder stand in het vorige "
    "seizoen en gingen langs promotion.convert / convert_relegated. Zeven ervan rekenen door op "
    "LIGHT; EEN valt buiten het gemeten invoerbereik en komt daarmee op NONE: Kalamata, met een "
    "relatieve aanval van 2.105 tegen een gemeten bereik van 1.248-1.951 (Grieks divisiepaar, "
    "n=13). conversion_in_range doet daar precies wat §4 ervan vraagt. EN DIT IS DE BEVINDING VAN "
    "DEZE RUN: zonder promotion.match_tier was dat duel op LIGHT uitgekomen en met +21,59 pp "
    "bovenaan de dagranglijst gestaan. match_tier bestaat sinds 31 okt 2026 en is toen alleen in "
    "het RUN A-script doorgevoerd; het Run B-script rekende de tier van het duel nog met een kale "
    "toewijzing uit, twee keer achter elkaar (thuis, dan uit), dus de uitploeg overschreef de "
    "thuisploeg. Vandaag is die fix ook in het Run B-script gezet. Op 31 okt en 1 nov bond de fout "
    "bij Run B niet (geen duel met de buitenbereik-ploeg thuis); drie eerdere Run B-duels wel, "
    "waarvan twee een bet werden (Exeter City - Rotherham United 3 okt en Girona - Mallorca 4 okt, "
    "beide gewonnen). De andere zeven omrekeningen van vandaag vielen alle binnen bereik: "
    "Superettan -> Allsvenskan (n=22), Liga II -> Romanian SuperLiga (n=16), Primera Federacion -> "
    "LaLiga2 (n=28), La Liga -> LaLiga2 (SP1/SP2, n=33, twee keer) en Eredivisie -> Keuken "
    "Kampioen Divisie (gepoold, n=240, twee keer). Die laatste twee draaien nog op POOLED_GAP in "
    "de richting OMLAAG - §4 noemt dat openstaand en het is op 9 okt wel gemeten (x1.772 / x0.621, "
    "n=23) maar niet toegepast.")

zet("understat", "untested",
    "2 nov (run B): NIET aangeroepen, en dat is geen storing. Understat dekt vijf competities "
    "(Premier League, La Liga, Bundesliga, Serie A, Ligue 1) en geen enkele daarvan staat op de "
    "Run B-runlijst, dus er is voor deze run niets te halen. LET OP voor de volgende Run A: "
    "Understat was vanmorgen bij Run A onbereikbaar met een 502 op de CONNECT van de "
    "netwerkgateway, voor alle vier de gedekte competities die toen speelden. Die meting staat in "
    "de regel van Run A hierboven; deze run voegt er niets aan toe en trekt er niets van af.")

d["last_run"] = {
    "run": "B",
    "date": VANDAAG,
    "note": (
        "VIJFTIEN duels in het inzetvenster over ZES van de zeventien competities, tegen een "
        "maandagcap van 40 - niets afgekapt. Veertien duels doorgerekend (3 op FULL, 11 op LIGHT) "
        "en EEN op NONE. Czech First League, Eliteserien, Croatian HNL, Hungarian NB I, Serie B, "
        "2. Bundesliga, Swiss Super League, Austrian Bundesliga, English League One, English "
        "League Two en MLS hebben geen ronde; dat is bij TWEE bronnen nagetrokken en die zijn het "
        "over alle zeventien competities eens (15 tegen 15), zonder een enkele afwijking. GEEN "
        "ENKELE BRONSTORING: Fotmob, The Odds API, BetExplorer en Pinnacle leverden alle vier "
        "zonder fout. 18 van 342 credits (12 bulk + 6 BTTS), 19841 over. DE BEVINDING IS EEN "
        "REPARATIE DIE METEEN BOND: promotion.match_tier stond sinds 31 okt alleen in het Run "
        "A-script, en zonder die fix zou Kalamata - Iraklis vandaag met +21,59 pp bovenaan de "
        "dagranglijst hebben gestaan terwijl Kalamata's omrekening buiten het gemeten bereik valt "
        "(aanval 2.105 tegen 1.248-1.951, n=13). Met de fix is dat duel NONE en GEEN BET - precies "
        "de Coventry-val waarvoor conversion_in_range bestaat, en precies de orde van grootte die "
        "§4 ervoor noemt. DRIE REGELS GEPUBLICEERD EN GEEN VAN DE DRIE HAALT ZIJN EIGEN LAT; ze "
        "staan er alle drie op RANGORDE (§5b): Real Oviedo - Las Palmas Under 2,5 @1,9604 "
        "(+15,24 pp tegen een LIGHT-lat van 16,0), Mjallby - Kalmar FF Under 2,5 @1,9506 "
        "(+10,91 pp tegen diezelfde 16,0) en Atromitos - NFC Volos Under 2,5 @1,85 (+4,83 pp tegen "
        "een FULL-lat van 8,0 en de verzwaarde lat van 10,0 van poort 9). ALLE DRIE OP DE "
        "UNDER-KANT, en dat is de slechtst mogelijke samenstelling gegeven §6g. Drie metingen die "
        "daar vandaag bij horen: de regel 'Under gespeeld' van margins.py goalbias staat op n=117 "
        "met +0,660 doelpunt per duel boven de eigen lambda en z=+4,31 (op 11 okt was dat n=49, "
        "z=+2,91), de reeks doelpunten_onder staat op 35 afgewikkelde kandidaten met -30,4%, en de "
        "homogene gridfit-populatie is van 914 naar 1147 duels gegroeid met een niveaufout van "
        "+0,100 doelpunt per duel (z=+1,93, was +1,67). STAGE 0: niets af te wikkelen - Run A had "
        "vanmorgen alles van 1 november al gedaan, en de vijf open picks en twaalf open "
        "schaduwrijen zijn alle van wedstrijden die nog niet gespeeld of nog bezig zijn."
    ),
}
d["last_run_bevinding"] = (
    "`promotion.match_tier` was op 31 oktober alleen in het Run A-script doorgevoerd, niet in het "
    "Run B-script. Het Run B-script rekende de `data_tier` van een DUEL nog met een kale "
    "toewijzing uit, twee keer achter elkaar (thuis, dan uit), waardoor een omrekening buiten het "
    "gemeten bereik bij de THUISploeg werd overschreven door een omrekening binnen het bereik bij "
    "de UITploeg. Vandaag bond dat op de bovenste regel: Kalamata - Iraklis, +21,59 pp, "
    "selection_score 6,83, ruim boven zijn eigen LIGHT-lat van 16,0 - en Kalamata's relatieve "
    "aanval van 2.105 ligt buiten het gemeten invoerbereik 1.248-1.951 van het Griekse "
    "divisiepaar (n=13). Het faalde stil in dezelfde vorm als de toplist-fout die Run A vanmorgen "
    "vond: er kwam geen foutmelding, de tier stond netjes op LIGHT en de regel droeg netjes zijn "
    "label. Dat Pinnacle het duel 20,49 pp lager prijsde was het enige zichtbare signaal, en dat "
    "is een vergelijking en geen controle. Fix doorgevoerd in tmp-run/rb_nov02_analyze.py; "
    "scripts/promotion.match_tier zelf was al goed."
)
d["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", VANDAAG)
for k in ("fotmob", "the_odds_api", "betexplorer", "pinnacle", "promotion_omrekening", "understat"):
    print(f"  {k:24s} {S[k]['status']:12s} last_checked={S[k]['last_checked']}")

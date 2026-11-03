"""Run B, 3 nov 2026 — `data/source-health.json` bijwerken met wat DEZE run gemeten heeft (§3).

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
VANDAAG = "2026-11-03"


def zet(key, status, detail):
    S[key]["status"] = status
    S[key]["last_checked"] = VANDAAG
    S[key]["detail"] = detail


zet("fotmob", "ok",
    "3 nov (run B): daglijsten 3 en 4 nov opgehaald (52 en 41 competities, 163 en 115 duels) en "
    "voor de afwikkeling die van 2 en 3 nov. idcheck.py gaf voor alle 33 fotmob_id's uit "
    "coverage.json een bruikbare stand, afsluitcode 0. Standen van alle VIER de spelende "
    "competities geleverd (Allsvenskan 67, English League One 108, English League Two 109, "
    "Serie A BRA 268), vorig en lopend seizoen, alle vier met xG. Voor de drie duels met een "
    "ploeg zonder stand in het vorige seizoen is ook de divisie ERBOVEN of ERONDER opgevraagd: "
    "League One (108) voor Northampton Town, dat uit League One is gedegradeerd, en voor "
    "Chapecoense en Coritiba is er geen divisie om op te vragen — Fotmob kent voor Serie A (BRA) "
    "geen tweede divisie in promotion.TIER2 en er is geen gemeten factor voor dat divisiepaar "
    "(prompts/run-b.md). Context voor ALLE ZES duels opgehaald zonder een enkele fout; bij EEN "
    "duel is het aandeel ontbrekende selectiewaarde niet te berekenen, waardoor vijf van de zes "
    "in het contextlogboek belanden en de datarijkdom er het middenpunt krijgt in plaats van nul "
    "(§1c: een meting die er niet is, is geen bewijs van een probleem). Fotmob is vandaag de "
    "ENIGE xG-bron: geen enkele competitie van de Run B-runlijst wordt door Understat gedekt, dus "
    "dat is geen storing maar de normale stand voor deze runlijst.")

zet("the_odds_api", "ok",
    "3 nov (run B): api_check.py meldt 50 actieve voetbalcompetities en 19824 credits over van "
    "20.000 (176 verbruikt deze maand). 33 van de 34 sportkeys van de repo zijn vandaag actief; "
    "alleen Coppa Italia (soccer_italy_coppa_italia) staat op niet-actief, wat buiten de "
    "Run B-runlijst valt. Vijf actieve sportkeys kent de repo niet: soccer_brazil_serie_b, "
    "soccer_germany_liga3, soccer_spain_copa_del_rey, soccer_sweden_superettan en "
    "soccer_uefa_nations_league — geen van die vijf staat op de Run B-runlijst, dus het is geen "
    "gat in deze run. Plafond van de run 353 credits (suggest_cap(19824, 28), 2 runs per dag), "
    "verdeling split_budget(353, 4) -> 4 spreads / 4 totals, dus de bulk (3 credits per "
    "competitie) paste ruim. Vier bulk-aanroepen (Allsvenskan 9 events, English League One 3, "
    "English League Two 1, Serie A BRA 9) en vier BTTS-aanroepen = 12 + 4 = 16 van 353, 19808 "
    "over. MARKTBALANS OP DE INKOOP GEHAALD VOOR 4 VAN DE 4 INKOOPBARE COMPETITIES, en dat is "
    "alle vier die vandaag spelen: elke bulk levert zowel een uitkomstmarkt (1X2, AH, DNB, DC) "
    "als een doelpuntenmarkt (O/U). Geen enkele competitie van vandaag draait op het gratis "
    "BetExplorer-gemiddelde als enige 1X2-bron — de omgekeerde situatie van gisteren, toen zes "
    "van de vijftien duels op beide assen de zwakste van de dag waren.")

zet("betexplorer", "ok",
    "3 nov (run B): fetch_league_fixtures voor alle vier de spelende competities geleverd "
    "(Allsvenskan 9 rijen, English League One 13, English League Two 13, Serie A BRA 18) en "
    "daarnaast voor de dertien stille competities, want de tweede-broncontrole moet juist dáár "
    "kijken. DE TWEEDE BRON IS HET OVER ALLE ZEVENTIEN COMPETITIES EENS MET FOTMOB: 6 duels in "
    "het inzetvenster tegen 6, met de eerstvolgende ronde van de stille competities erbij (5 t/m "
    "14 november). Nul afwijkingen, de tweede dag op rij zonder. Het 1X2-marktgemiddelde is "
    "gebruikt voor het kalibratieblok van §6e en voor poort 8; als ENIGE 1X2-bron was het vandaag "
    "nergens nodig, want alle vier de spelende competities hebben een sportkey. Bij Serie A (BRA) "
    "labelt BetExplorer maar een van de twee duels in het venster als 'today'; dat is geen fout "
    "maar de paginadatum — Internacional - Coritiba trapt af op 2026-11-04T00:30Z, oftewel 01:30 "
    "NL, en hoort volgens runwindow.py bij de run van vandaag.")

zet("pinnacle", "ok",
    "3 nov (run B): Pinnacle-prijzen in de respons voor 20 events. 1X2 te de-viggen voor VIER van "
    "de zes duels — de twee Braziliaanse niet — met een marge van 4,2 tot 5,2% (gemiddeld 4,66%) "
    "en een gemiddelde absolute afstand tot het eigen model van 4,97 pp. Totalen voor vier "
    "(duel, lijn)-paren. DE BEVINDING AAN DEZE KANT: op de Under-kant staat het eigen model "
    "gemiddeld +0,38 pp boven Pinnacle en op 2 van de 4 paren erboven; op de ENE zuivere halve "
    "lijn (geen push) is dat +2,84 pp — Sirius - Halmstads BK, eigen P(Under 3,5) 51,0% tegen "
    "48,2% bij Pinnacle, en dat is de enige gepubliceerde regel van vandaag. Dezelfde richting "
    "als de scheefstand die §6g op uitkomsten meet, maar VEEL KLEINER dan gisteren (+7,46 pp over "
    "drie zuivere halve lijnen), en dat is wat de niveaucorrectie van vandaag hoort te doen. Lees "
    "het als een enkele waarneming en niet als een meting (§6d eist ~30). De drie pushlijnen "
    "staan juist onder Pinnacle (-0,43 pp). Grootste afwijking op 1X2: Northampton Town - Oldham "
    "Athletic, waar Pinnacle Northampton favoriet maakt (41,4% tegen 29,1% eigen) en het model "
    "Oldham (43,7% tegen 29,1% bij Pinnacle) — ruim 14 procentpunt op de uitwinst, en uitgerekend "
    "het duel waarvan poort 8 alle drie de bovenste selecties heeft tegengehouden.")

zet("promotion_omrekening", "ok",
    "3 nov (run B): DRIE van de zes duels hadden een ploeg zonder stand in het vorige seizoen en "
    "gingen langs promotion.convert / convert_relegated. EEN rekent door op LIGHT en TWEE komen "
    "op NONE uit, en die twee om een andere reden dan het gemeten bereik. Northampton Town is uit "
    "League One gedegradeerd en is omgerekend met het gemeten paar E2/E3 in de richting OMLAAG "
    "(x1.254 aanval / x0.814 verdediging, n=43): relatieve aanval 0.645 binnen 0.526-1.012 en "
    "verdediging 1.223 binnen 1.033-1.861, dus conversion_in_range laat hem door en het duel komt "
    "op LIGHT. Chapecoense en Coritiba zijn beide uit de Braziliaanse Serie B gepromoveerd en "
    "komen op NONE: er is GEEN GEMETEN FACTOR voor het divisiepaar Serie A (BRA) / Serie B, en "
    "prompts/run-b.md schrijft dat ook met zoveel woorden voor. Dat is geen gat in de "
    "administratie en geen openstaand werk — een gepoolde factor erop zetten zou het gat wel "
    "dichten en is precies wat §2 en §4 verbieden, dezelfde regel als bij de Kroatische en de "
    "Hongaarse tweede divisie. promotion.match_tier is in dit script aanwezig sinds de reparatie "
    "van 2 november en bond vandaag niet: geen enkel duel had een omrekening buiten het bereik.")

zet("understat", "untested",
    "3 nov (run B): NIET aangeroepen, en dat is geen storing. Understat dekt vijf competities "
    "(Premier League, La Liga, Bundesliga, Serie A, Ligue 1) en geen enkele daarvan staat op de "
    "Run B-runlijst, dus er is voor deze run niets te halen. LET OP voor de volgende Run A: "
    "Understat was vanmorgen bij Run A voor de TWEEDE dag op rij onbereikbaar. Die meting staat "
    "in de regel van Run A; deze run voegt er niets aan toe en trekt er niets van af. Wordt het "
    "een derde dag, dan hoort dat volgens §3 in de notificatie van Run A en niet in die van "
    "Run B — maar de regel die écht telt is Fotmob, en die leverde vandaag alles.")

d["last_run"] = {
    "run": "B",
    "date": VANDAAG,
    "note": (
        "ZES duels in het inzetvenster over VIER van de zeventien competities, tegen een "
        "dinsdagcap van 40 — niets afgekapt. Vier duels doorgerekend (3 op FULL, 1 op LIGHT) en "
        "TWEE op NONE. Dertien competities hebben geen ronde; dat is bij TWEE bronnen nagetrokken "
        "en die zijn het over alle zeventien competities eens (6 tegen 6), zonder een enkele "
        "afwijking. GEEN ENKELE BRONSTORING: Fotmob, The Odds API, BetExplorer en Pinnacle "
        "leverden alle vier zonder fout. 16 van 353 credits (12 bulk + 4 BTTS), 19808 over. "
        "DE BEVINDING IS DEZELFDE FAALVORM ALS GISTEREN, IN EEN ANDERE GEDAANTE: "
        "model.LEVEL_SCALE = 1.032 bindt vandaag voor het eerst (LEVEL_SCALE_BINDS_FROM = "
        "2026-11-03) en §6g eist daarbij `today=DAY` op elke aanroep van analyze_match en "
        "robustness_check. Het Run A-script van vandaag doet dat op negen plekken; dit Run "
        "B-script, overgenomen van 2 november toen de knop nog niet bond, gaf `today` op geen "
        "enkele plek mee. Gerepareerd VOOR de analyse. Wat het uitmaakt op de enige gepubliceerde "
        "regel: met de correctie staat Sirius - Halmstads BK Under 3,5 op +5,72 pp, zonder op "
        "+7,67 pp — de correctie haalt er 1,95 pp af en wijst dus de VOORZICHTIGE kant op, precies "
        "zoals §6g belooft. De gepubliceerde lijst verandert er niet door. EEN REGEL GEPUBLICEERD "
        "EN DIE HAALT ZIJN LAT NIET: Sirius - Halmstads BK Under 3,5 @1,99 (+5,72 pp tegen een "
        "FULL-lat van 8,0), dus op RANGORDE (§5b) en niet op gevonden voordeel. En hij staat op de "
        "Under-kant, de enige kant waarvan §6g op uitkomsten heeft gemeten dat ze structureel "
        "verliest. DRIE METINGEN DIE DAAR VANDAAG BIJ HOREN: de regel 'Under gespeeld' van "
        "margins.py goalbias staat op n=121 met +0,651 doelpunt per duel boven de eigen lambda en "
        "z=+4,32 (op 11 okt was dat n=49, z=+2,91) — dat is de controle op poort 9 zelf en ze "
        "blijft groeien; de edge van de gepubliceerde regel komt vrijwel volledig uit de "
        "splitsmethode (+22,72 pp tegen +0,77 pp voor de xG-methode, zwakste stand van het grid "
        "+0,77 pp); en de homogene gridfit-populatie staat op 1173 duels met een niveaufout van "
        "+0,099 doelpunt per duel (z=+1,92), nog zonder duels van ná vandaag. STAGE 0: niets af te "
        "wikkelen — Run A had vanmorgen alles van 2 november al gedaan, en de drie open picks en "
        "tien open schaduwrijen zijn alle van wedstrijden die vanavond nog moeten worden gespeeld."
    ),
}
d["last_run_bevinding"] = (
    "De niveaucorrectie `model.LEVEL_SCALE` = 1.032 bindt vanaf vandaag "
    "(`LEVEL_SCALE_BINDS_FROM` = 2026-11-03) en §6g punt 2 eist daarbij `today=DAY` bij ELKE "
    "aanroep van `analyze_match` en `robustness_check`: zonder dat argument kijkt `level_scale` "
    "naar de systeemklok, en dan krijgt een herberekening van een oudere dag stil de correctie van "
    "vandaag. Het Run A-script van 3 november doet dat op negen plekken. Het Run B-script is "
    "overgenomen van 2 november — de dag waarop de knop nog NIET bond en het verschil dus nul was "
    "— en gaf `today` op geen enkele plek mee. Dat is exact dezelfde faalvorm als de bevinding van "
    "gisteren, toen `promotion.match_tier` alleen in het Run A-script bleek te zitten: een "
    "reparatie die in een van de twee runscripts landt, in het andere niet, en die niet klaagt. "
    "Vandaag zou het geen foutmelding hebben gegeven maar stil de lambdas van 2 november: op de "
    "enige gepubliceerde regel +7,67 pp in plaats van +5,72 pp, en in `data/run-state/` lambdas "
    "zonder de correctie — precies de vervuiling waarvoor §6g punt 2 waarschuwt, want `margins.py` "
    "en `gridfit.py` rekenen op die opgeslagen lambdas en moeten juist meten of deze knop werkt. "
    "De negen aanroepen (vier `analyze_match`, vijf `robustness_check`) zijn vóór de analyse "
    "gerepareerd in tmp-run/rb_nov03_analyze.py; `scripts/model.py` zelf was al goed. DE "
    "STRUCTURELE LES IS NIET 'ik heb het gerepareerd' MAAR DAT DIT DE TWEEDE DAG OP RIJ IS: een "
    "wijziging in de rekenketen landt in het runscript van de run die haar invoert, en de andere "
    "run neemt de dag erna een kopie van zichzelf over. Zolang de twee runs een eigen kopie van "
    "het analysescript hebben, blijft dit terugkomen."
)
d["updated"] = datetime.now(timezone.utc).isoformat()

json.dump(d, open(PAD, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt:", VANDAAG)
for k in ("fotmob", "the_odds_api", "betexplorer", "pinnacle", "promotion_omrekening", "understat"):
    print(f"  {k:24s} {S[k]['status']:12s} last_checked={S[k]['last_checked']}")

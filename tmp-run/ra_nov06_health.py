"""Run A, 6 nov 2026 — `data/source-health.json` en `data/coverage.json` bijwerken (§6b-3).

Twee dingen die hier vastgelegd moeten worden en die een volgende run anders opnieuw moet
uitzoeken:

1. **Understat ligt er de vijfde dag uit** en raakt vandaag VOOR HET EERST deze week wel iets:
   alle vijf zijn competities speelden. Dat verschil met gisteren staat er expliciet bij, want
   de notitie van gisteren zei met zoveel woorden "het raakt vandaag niets".
2. **Het Fotmob-id van de FA Cup is 132.** Dat gaat onder `notes` en NIET onder `fotmob_id`:
   `idcheck.py` eist van elk id daar een bruikbare stand en een beker heeft er geen, dus het zou
   elke run een vals alarm geven op precies de controle die voor een stil verdwenen competitie
   is gebouwd. Zelfde constructie als bij 133 (League Cup), 209 (DFB Pokal) en 235 (KNVB Beker).
"""
import json

H = "data/source-health.json"
h = json.load(open(H))
S = h["sources"]


def hist(key, detail):
    """Oude detailtekst bewaren in detail_history voordat hij wordt overschreven."""
    oud = S[key].get("detail")
    if oud:
        S[key].setdefault("detail_history", []).insert(
            0, {"date": S[key].get("last_checked"), "detail": oud})
        S[key]["detail_history"] = S[key]["detail_history"][:8]
    S[key]["detail"] = detail
    S[key]["last_checked"] = "2026-11-06"


hist("understat",
     "6 nov (run A): VIJFDE dag op rij onbruikbaar, en voor het eerst deze week RAAKT HET WEL "
     "IETS. Alle vijf de competities geven exact dezelfde fout: `UnderstatError: geen JSON terug "
     "van https://understat.com/getLeagueData/<code>/2025 (26719 bytes)` — vijf verzoeken, vijf "
     "keer EXACT 26.719 bytes. Drie dagen op rij hetzelfde antwoord in dezelfde grootte wijst op "
     "een blokkadepagina of een permanent gewijzigde route, niet op een storing die voorbijgaat. "
     "De reeks: 1 nov HTTP 502 op de CONNECT van de netwerkgateway, 3 nov `Connection reset by "
     "peer`, 4/5/6 nov 26.719 bytes zonder JSON. "
     "WAT HET VANDAAG KOST, anders dan gisteren: Understat dekt PL, La Liga, Bundesliga, Serie A "
     "en Ligue 1, en die leveren vandaag 5 van de 15 duels in het venster (Everton - Coventry "
     "City, Venezia - Udinese, Sevilla - Deportivo Alaves, Hamburger SV - Borussia "
     "Monchengladbach, Toulouse - Strasbourg). Bij die vijf is er geen TWEEDE, onafhankelijk "
     "xG-model naast Fotmob; het kalibratieblok van 6e mist er zijn `p_xg_understat`-arm en die "
     "reeks groeit vandaag dus niet. "
     "WAT HET NIET KOST: geen enkel duel wordt hierdoor NONE en geen enkele tier verandert. "
     "Fotmob-xG is een geldige onafhankelijke kansinput (2) en xG plus doelpuntensplits leveren "
     "FULL (4). Dat Everton - Coventry en Venezia - Udinese op LIGHT staan komt doordat er een "
     "PROMOVENDUS is omgerekend, niet door Understat. "
     "DE UITZONDERING VAN 3 IS NIET INGETREDEN: die eist een melding vooraan in de notificatie "
     "zodra FOTMOB niet meer levert, en Fotmob leverde vandaag zonder een enkele fout.")

hist("fotmob",
     "6 nov (run A): daglijsten 6 en 7 nov opgehaald (93 competities / 180 duels en 168 / 648) en "
     "voor de afwikkeling die van 5 en 6 nov. Per competitie de stand van 2025/2026 en 2026/2027; "
     "idcheck.py groen op alle 33 id's uit coverage.json. Wedstrijdcontext (opstelling, "
     "uitvallers met marktwaarde, vorm, rustdagen, stadion, weer) voor ALLE 15 duels, inclusief "
     "het duel op tier NONE. Geen enkele fout, geen rate limit. "
     "NIEUWE BEVINDING: de FA CUP STAAT WEL IN DE DAGLIJST, onder primaryId 132, met 2 duels. "
     "Het duel-filter van de run zoekt op de fotmob_id's uit coverage.json en de FA Cup heeft "
     "daar geen id, dus het filter sloeg hem over en de competitiepoort schreef GEEN WEDSTRIJD. "
     "De daglijst-AUDIT (die elke competitie van de dag noteert, niet alleen de gefilterde) en "
     "BetExplorer vonden beide dezelfde twee duels, met dezelfde aftraptijden. Het id staat nu "
     "onder `notes` in coverage.json, niet onder fotmob_id - idcheck.py eist daar een bruikbare "
     "stand en een beker heeft er geen.")

hist("betexplorer",
     "6 nov (run A): fixturepagina's van alle dertien competities met een slug opgehaald als "
     "TWEEDE BRON op de vraag welke wedstrijden er zijn (Sec. 1, bevestiging door een tweede "
     "methode). 13 van 13 eens met de Fotmob-daglijst. "
     "EN BIJ DE FA CUP WAS DIT DE BRON DIE HET GAT VOND: /england/fa-cup/fixtures/ (158.987 "
     "bytes, 40 teamparen, 120 koersen) gaf 2 duels in het venster - Bristol Rovers - Cambridge "
     "Utd 20:30 en Oxford City - Leicester 20:45 - terwijl het id-filter van de run GEEN "
     "WEDSTRIJD had opgeschreven. Dat is precies het gat dat Run A op 6 oktober vijf duels "
     "kostte. De vier andere bekers gaven 0 duels in het venster, met hun eerstvolgende ronde "
     "erbij (League Cup 15.12, de rest 01.12). "
     "Marktgemiddelde 1X2 geleverd voor alle dertien competities; gebruikt voor poort 8 en "
     "Sec. 6e, en voor de FA Cup als ENIGE 1X2-bron omdat die geen actieve sportkey heeft.")

hist("pinnacle",
     "6 nov (run A): 1X2 gevonden voor 159 events in de responsen, 11 duels toetsbaar. "
     "Pinnacle-marge 3,0 tot 4,6% (gemiddeld 3,57%) tegen 6-10% bij de rest. Gemiddelde absolute "
     "afstand tot het Pinnacle-oordeel 3,95 pp. Grootste meningsverschillen: Sevilla - Deportivo "
     "Alaves -12,01 pp op de thuiskant (Pinnacle maakt Sevilla duidelijk favoriet, het model "
     "niet) en Toulouse - Strasbourg +9,54 pp de andere kant op; GEEN van beide staat in de "
     "lijst, beide sneuvelen op poort 5. "
     "OP DE UNDER-KANT IS HET TEKEN GEDRAAID, en dat is de waarneming van vandaag: over 11 "
     "(duel, lijn)-paren staat de eigen P(Under) gemiddeld 2,49 pp ONDER Pinnacle, en bij 3 van "
     "de 11 erboven. Op 4 november was dat +4,47 pp over vier paren en op 5 november +1,06 pp "
     "over een enkel paar. Vandaag is dus de grootste steekproef van de drie EN het andere "
     "teken. Dat wijst de kant op die model.LEVEL_SCALE = 1.032 moest opleveren (sinds 3 nov "
     "bindend, verlaagt P(Under) ongeveer twee procentpunt per duel). "
     "LEES HET ALS DIAGNOSE EN NIET ALS METING: Sec. 6e verbiedt een tegen de MARKT gemeten "
     "afwijking van my_prob af te trekken, en de vraag of de correctie werkt hoort op UITKOMSTEN "
     "beantwoord te worden met gridfit.py measure op de duels van na 3 november. Dat zijn er "
     "vanochtend 57 van 1230 - ruim te weinig (6d). Sec. 6g verbiedt uitdrukkelijk een "
     "vergelijking van twee ochtenden als vervanging daarvan.")

hist("poort_5_bevestiging",
     "6 nov (run A): DE POORT VAN DE DAG, VOOR DE TWEEDE DAG OP RIJ, en nu op een twintigmaal "
     "grotere steekproef dan gisteren. Van de 186 doorgerekende selecties sneuvelen er 149 "
     "(80,1%) op poort 5, verspreid over 14 van de 15 wedstrijden; de vijftiende is het enige "
     "duel op tier NONE en heeft dus geen selecties. Daarna komt `edge` met 21 (11,3%), "
     "`underdog` met 8, `context` met 5 en `odds` met 3. "
     "Het duidelijkste geval is Toulouse - Strasbourg: xG-methode +8,94 pp op de thuiszege, "
     "splitsmethode -14,87 pp op diezelfde selectie. De twee methodes zijn het dus oneens over "
     "de RICHTING en niet over de grootte - precies waar poort 5 voor is gebouwd. "
     "GISTEREN WAS HET HETZELFDE: Run B van 5 november kwam op nul bets uit doordat alle 17 "
     "selecties van haar enige analyseerbare duel (Cruzeiro - Bahia) hierop sneuvelden. "
     "EN DE REM: TWEE DAGEN ZIJN GEEN REEKS. Sec. 6d eist ~30 afgewikkelde gevallen en de reeks "
     "die deze vraag beantwoordt is het schaduwlogboek, niet het aandeel van vandaag. Die reeks "
     "staat op 263 kandidaten, 254 afgewikkeld, trefkans 46,1%, rendement -2,0% (-5,11u): de "
     "poort BESPAART geld. Sec. 1f zegt het scherper - als kansbron voegt de splitsmethode "
     "vrijwel niets toe (Brier .23674 tegen .23625), als VETO bespaart ze aantoonbaar geld. "
     "Er is vandaag geen poort, drempel of gewicht verzet. Een derde en vierde dag met dit "
     "aandeel maken het de moeite om te onderzoeken of de twee methodes systematisch uiteen zijn "
     "gaan lopen; vandaag is dag twee.")

S["herijking_fitted_through"] = {
    "status": "liep_achter_rechtgezet",
    "last_checked": "2026-11-06",
    "detail":
        "6 nov (run A): `recalibrate.load_fit().fitted_through` stond bij binnenkomst op "
        "2026-11-04, terwijl Sec. 6b-5c de VORIGE RUNDAG of later eist - dat is 5 november. De "
        "controle die die paragraaf op 30 september expliciet heeft bijgeschreven, sloeg dus aan. "
        "`calibration.py settle` heeft 66 waarnemingen afgewikkeld (7311 van 7341 compleet, 30 "
        "nog open) en fitted_through staat nu op 2026-11-05. "
        "DE ANALYSE IS DAARNA VOLLEDIG OPNIEUW GEDRAAID op de verse fit (van a=1,0290/b=0,0187 "
        "over 7038 gevallen naar a=1,0242/b=0,0156 over 7104). Dat kost rekentijd en NUL credits. "
        "De drie gepubliceerde regels zijn onder beide fits dezelfde drie in dezelfde orde; "
        "alleen de edges zakken een fractie (Famalicao +6,76 -> +6,68, Venezia +10,26 -> +10,14, "
        "Derby +8,20 -> +8,08). De picks dragen de nieuwe getallen. "
        "DIT IS STRUCTUREEL EN GEEN INCIDENT, en het is het openstaande punt van deze run. "
        "`calibration.py settle` staat in Sec. 6b-5c bij het VASTLEGGEN, dus NA de analyse, "
        "terwijl Stage 0 wel de picks en de schaduwpicks afwikkelt maar niet het "
        "kalibratielogboek. Elke run rekent daardoor per constructie met een fit van ongeveer een "
        "dag oud; de run van 5 november noteerde zelf een fit t/m 3 november. De nette oplossing "
        "is die regel naar Stage 0 te verplaatsen, naast ledger.py settle en shadow.py settle. "
        "DE OMVANG, EERLIJK: tienden van procentpunten (+0,2 pp op 40%, +0,5 op 50%, +0,9 op "
        "70%), waar de oude fit van voor 20 september er tien hele afhaalde. Geen bron van "
        "verkeerde bets, maar wel precies de stille faalvorm die Sec. 6b-5c beschrijft: een niet "
        "afgewikkeld logboek klaagt niet.",
}

S["fa_cup_id"] = {
    "status": "gevonden",
    "last_checked": "2026-11-06",
    "detail":
        "6 nov (run A): HET FOTMOB-ID VAN DE FA CUP IS 132, en twee bronnen bevestigen dat er "
        "vandaag twee duels waren terwijl de administratie GEEN WEDSTRIJD zei. Het duel-filter "
        "van de run zoekt per competitie op het fotmob_id uit coverage.json; de FA Cup heeft daar "
        "geen id, want idcheck.py eist van elk id een bruikbare stand en een beker heeft die niet "
        "- zonder die keuze zou de controle elke ochtend een vals alarm geven op precies het "
        "mechanisme dat voor een stil verdwenen competitie is gebouwd. "
        "GEVOLG: het filter sloeg de FA Cup over. BetExplorer vond 2 duels in het venster en de "
        "daglijst-AUDIT van Stage 1 (die elke competitie van de dag noteert) liet de FA Cup er "
        "gewoon in staan onder primaryId 132, met 2 wedstrijden. Dezelfde ploegen, dezelfde "
        "aftraptijden: Bristol Rovers - Cambridge United 20:30 en Oxford City - Leicester City "
        "20:45. "
        "WAT HET OPLEVERDE: Bristol Rovers - Cambridge United op FULL via "
        "promotion.shared_lower_division (beide in League Two, Fotmob 109, 3 divisies onder de "
        "basisdivisie Premier League - geen omrekening nodig, en League Two heeft xG). Oxford "
        "City - Leicester City blijft NONE: verschillende niveaus en conversion_in_range weigert. "
        "Geen van beide werd een bet, dus het gat kostte vandaag geen bet - maar op een volle "
        "bekerronde kost het de hele ronde en ziet het rapport er met een nette nul normaal uit. "
        "HET ID GAAT ONDER `notes` IN coverage.json EN NIET ONDER fotmob_id, zelfde constructie "
        "als 133 (League Cup), 209 (DFB Pokal) en 235 (KNVB Beker).",
}

S["the_odds_api"]["last_checked"] = "2026-11-06"
S["the_odds_api"]["detail"] = (
    "6 nov (run A): OK, 19.748 credits over en 252 verbruikt deze maand; 27 van de 34 sportkeys "
    "van de repo actief. De zeven inactieve spelen vandaag niet (Coppa Italia, League One/Two, "
    "Europa League, Conference League) - kalender, geen storing. "
    "Plafond deze run 394 (suggest_cap(19748, 25)), verdeling split_budget(394, 12) -> 12 spreads "
    "/ 12 totals, bulk mogelijk. 36 credits aan de bulk (12 competities x 3: h2h + spreads + "
    "totals) en 8 aan BTTS voor de 8 duels met een kandidaat-edge. Totaal 44 van 394; 19.704 over. "
    "MARKTBALANS RUIM GEHAALD: alle twaalf inkoopbare competities kregen in dezelfde aanroep "
    "zowel een uitkomstmarkt als een doelpuntenmarkt - twaalf op twaalf, de ruimst mogelijke "
    "marge - en de drie bets komen uit drie VERSCHILLENDE markten (1X2, Over/Under, Draw No Bet). "
    "DE FA CUP HAD GEEN SPORTKEY (soccer_england_fa_cup niet actief vandaag), dus daar is "
    "BetExplorer de enige 1X2-bron: marktgemiddelde, bookmaker niet herleidbaar, edge "
    "systematisch te laag. Raakt de twee FA Cup-duels; geen van beide werd een bet."
)
S["api_football"]["last_checked"] = "2026-11-06"
S["settling"]["last_checked"] = "2026-11-06"
S["settling"]["detail"] = (
    "6 nov (run A): 2 picks en 21 schaduwrijen van 5 november afgewikkeld, alle 23 op de "
    "statusregel van Sec. 0 (`finished` van de bron, klok alleen als terugval). Beide duels van "
    "de picks waren Conference League-LEAGUE PHASE, dus geen verlenging en de eindstand IS de "
    "stand na 90 minuten (6d). Na deze run staat picks.jsonl op NUL open picks. "
    "Beide picks VERLOREN: FC Midtjylland - Ajax (DNB Midtjylland @2,06) werd 1-6 tegen een "
    "verwachting van 2,196/1,170, en FC Twente - Pafos (Under 3.5 @1,8134) werd 3-1 tegen een "
    "verwacht totaal van 2,69. De 21 schaduwrijen: 14 gewonnen, 6 verloren, 1 void."
)
h["updated"] = "2026-11-06"
h["last_run"] = {
    "run": "A", "date": "2026-11-06",
    "note":
        "DERTIEN van de eenentwintig competities uit de runlijst speelden, met VIJFTIEN duels in "
        "het inzetvenster tegen een vrijdagcap van 55 - dus niets afgekapt. DRIE BETS, en geen "
        "van de drie haalt zijn eigen lat: ze staan alle drie op de rangorde van Sec. 5b. "
        "Famalicao - Arouca (1X2 Famalicao @2,2348, FULL, +6,68 pp tegen 8,0), Venezia - Udinese "
        "(Over 2.5 @1,9114, LIGHT, +10,14 tegen 16,0) en Derby County - Bolton Wanderers (DNB "
        "Derby @1,8918, LIGHT, +8,08 tegen 16,0). Alle drie de koersen komen van een beurs. "
        "MAX_LIGHT_IN_SHORTLIST bindt en houdt Everton - Coventry City (Over 2.5, LIGHT, +6,00 "
        "pp, rang 4) tegen; die staat ONDER zijn lat en is daarom GEEN "
        "gekwalificeerd_niet_gepubliceerd en krijgt geen lijstlengte-rij, maar een eigen veld "
        "max_light_geblokkeerd. "
        "DE BEVINDING IS POORT 5: 149 van de 186 selecties (80,1%) over 14 van de 15 wedstrijden, "
        "de tweede dag op rij dat die poort de dag bepaalt. En het gat in de administratie: de FA "
        "CUP SPEELDE WEL (id 132, twee bronnen eens) terwijl het id-filter GEEN WEDSTRIJD zei.",
}
h["last_run_bevinding"] = (
    "POORT 5 HIELD 149 VAN DE 186 SELECTIES TEGEN - VIER VAN DE VIJF, OVER 14 VAN DE 15 "
    "WEDSTRIJDEN - EN HET IS DE TWEEDE DAG OP RIJ DAT DEZE POORT DE DAG BEPAALT. Gisteren kwam "
    "Run B op nul bets uit doordat alle 17 selecties van haar enige analyseerbare duel hierop "
    "sneuvelden; vandaag is het dezelfde poort op een twintigmaal grotere steekproef. De poort "
    "eist dat de xG-methode en de splitsmethode de markt DEZELFDE KANT OP verslaan, dus dit zegt "
    "dat de twee kansmethodes het structureel oneens zijn over de RICHTING en niet over de "
    "grootte - Toulouse - Strasbourg staat op +8,94 pp (xG) tegen -14,87 pp (splits) op dezelfde "
    "selectie. "
    "EN DE REM EROP, WANT DIE IS HIER ONMISBAAR: TWEE DAGEN ZIJN GEEN REEKS. Sec. 6d eist ~30 "
    "afgewikkelde gevallen voordat een reeks gelezen mag worden, en de reeks die deze vraag "
    "beantwoordt is het schaduwlogboek en niet het aandeel van vandaag. Daar staat "
    "`tweede_methode` op 254 afgewikkelde kandidaten met een rendement van -2,0%: de poort "
    "BESPAART geld, en 'hij hield vandaag veel tegen' is dus een beschrijving en geen klacht. "
    "Sec. 1f zegt precies dit over de rol van de splitsmethode - als kansbron voegt ze vrijwel "
    "niets toe, als VETO bespaart ze aantoonbaar geld, en vandaag is dat veto vier vijfde van de "
    "run. Er is geen poort, drempel of gewicht verzet. Een derde en vierde dag met dit aandeel "
    "maken het de moeite om te onderzoeken of de twee methodes systematisch uiteen zijn gaan "
    "lopen; vandaag is dag twee."
)
json.dump(h, open(H, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")

C = "data/coverage.json"
c = json.load(open(C))
fa = c["competitions"].setdefault("FA Cup (ENG)", {})
notes = fa.get("notes") or ""
fa["notes"] = (notes + " " if notes else "") + (
    "Run A 6 nov 2026: HET FOTMOB-ID IS 132. De FA Cup staat gewoon in de daglijst (ccode ENG, "
    "primaryId 132, 2 duels op 6 november), en BetExplorer "
    "/england/fa-cup/fixtures/ noemde dezelfde twee duels met dezelfde aftraptijden. Het id "
    "staat hier onder `notes` en NIET onder `fotmob_id`, omdat idcheck.py van elk fotmob_id een "
    "bruikbare stand eist en een beker die niet heeft - zelfde constructie als 133 (League Cup), "
    "209 (DFB Pokal) en 235 (KNVB Beker). Een volgende run hoeft het dus niet opnieuw te zoeken: "
    "filter de daglijst op 132 en reken het duel door via promotion.CUP_BASE (Premier League) en "
    "promotion.shared_lower_division."
).strip()
c["updated"] = "2026-11-06"
json.dump(c, open(C, "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt — FA Cup notes")

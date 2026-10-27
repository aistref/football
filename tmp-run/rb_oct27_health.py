"""Run B, 27 okt 2026 — bronprobe voor source-health.json.

VIJFTIEN duels in het inzetvenster over VIJF competities, alle vijftien onder de dinsdagcap van
40. Alle vier de bronkanten werkelijk in gebruik. Fotmob voor de twee daglijsten, de 33 standen
van `idcheck.py`, de context van alle 15 duels, de voorbeschouwingsblokken van de drie bets en de
marktvormtelling van negen duels. The Odds API voor de bulk (vier competities) en BTTS (zeven
duels). BetExplorer voor het gratis 1X2-marktgemiddelde en als tweede bron op de vraag wélke
wedstrijden er zijn. Understat deed vandaag NIET mee: geen van zijn vijf competities speelt op
deze runlijst.

GEEN ENKELE BRONSTORING. `store["errors"]` is over de hele run leeg gebleven.

DE BRONBEVINDING VAN VANDAAG GAAT OVER DE STADIONCONTROLE, en ze corrigeert wat Run A vanochtend
over dezelfde bron schreef: daar was `venue.name` bij alle 22 duels leeg, hier is hij bij alle 15
gevuld. De leegte van Run A zit dus in de bekerinvoer en niet in Fotmob.
"""

import json, datetime

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
H = json.load(open("data/source-health.json"))
S = H["sources"]


def note(key, status, detail):
    prev = S.get(key, {})
    hist = prev.get("detail_history") or []
    if prev.get("detail") and prev.get("last_checked"):
        hist = (hist + [{"date": prev["last_checked"], "detail": prev["detail"]}])[-6:]
    S[key] = {**prev, "status": status, "last_checked": now[:10], "detail": detail,
              "detail_history": hist}
    print(f"{key:18} {status:12} {detail[:100]}")


note("fotmob", "ok",
     "27 okt (run B): daglijsten 27 en 28 okt opgehaald (221 en 271 duels over 72 competities per "
     "dag); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand, "
     "afsluitcode 0 - ook voor de twaalf competities van deze runlijst die vandaag stil zijn, en "
     "dat is precies de kant van de controle die iets kan opleveren. Standen van alle vijf de "
     "spelende competities geleverd (Allsvenskan, Croatian HNL, Serie B, English League One, "
     "English League Two), vier met xG en Croatian HNL zonder - vandaar dat die op doelpunten als "
     "sterktemaat draait en hoe dan ook op LIGHT uitkomt. Context voor alle 15 duels zonder fout, "
     "13 ervan in het contextlogboek: Dinamo Zagreb - Rijeka en York City geven squad_value 0, "
     "waardoor ctxlog.out_share None teruggeeft en de rij geen beschikbaarheidsverschil kan "
     "dragen. DE BEVINDING VAN VANDAAG ZIT IN DE STADIONVELDEN: Run A schreef vanochtend over "
     "dezelfde bron dat venue.name bij ALLE 22 duels None was, en dat was de derde dag op rij met "
     "die melding. Op deze runlijst is hij bij ALLE 15 duels gevuld, met voor 14 duels hetzelfde "
     "stadion als het eigen stadion van de thuisploeg. De leegte van Run A is dus geen "
     "Fotmob-storing maar een eigenschap van de bekerinvoer waarmee die run werkt - "
     "context.check_venue werkt gewoon, en 'niet verplaatst' betekent op deze lijst werkelijk "
     "niet verplaatst. EEN ALARM, en vermoedelijk een bronfout en geen verplaatsing: bij LR "
     "VICENZA - MODENA staat de wedstrijd in 'Stadio Romeo Menti, Vicenza' terwijl het eigen "
     "stadion van de genoteerde thuisploeg 'Stadio Comunale Rino Mercante' is. Romeo Menti IS het "
     "stadion van LR Vicenza en Rino Mercante hoort bij Bassano, dus het veld home_ground staat "
     "hier waarschijnlijk op de verkeerde club. Het duel staat op tier NONE (promovendus uit de "
     "Serie C, geen gemeten divisiepaar), dus het raakt geen enkele bet - maar §1c eist dat een "
     "alarm wordt genoemd ook als de poort opengaat. lineupType: 14 van de 15 op 'lastStarting11' "
     "en 1 op 'unavailable', geen enkel 'confirmed' - te verwachten om 04:00 NL bij aftrappen van "
     "18:00 tot 20:45. Voorbeschouwingsblokken (preview.py) voor alle drie de bets zonder fout, "
     "en marketform.match_block voor alle negen doorgerekende duels zonder fout.")

note("the_odds_api", "ok",
     "27 okt (run B): sleutel geldig, 49 actieve voetbalcompetities, quota 18.652 over en 1.348 "
     "verbruikt bij de start van de run. Geen afgewezen sleutel en geen quotaprobleem. EEN VAN DE "
     "VIJF SPELENDE COMPETITIES HEEFT GEEN SPORTKEY - Croatian HNL - en dat hoort als "
     "bronbevinding en niet als krap plafond: daar is het gratis BetExplorer-marktgemiddelde de "
     "enige 1X2-bron en is er geen enkele andere markt, dus valt de edge daar systematisch te "
     "laag uit (conservatief, maar niet vergelijkbaar met een duel waar de beste prijs bekend "
     "is). Dat raakt een duel met drie selecties. De vier andere competities kregen alle vier de "
     "volledige bulk-aanroep van 3 credits. LET OP DAT DE LIJST VAN api_check.py KRAPPER IS DAN "
     "DE WERKELIJKHEID: soccer_sweden_allsvenskan, soccer_england_league1 en "
     "soccer_england_league2 staan niet onder 'relevante sportkeys' en leverden toch gewoon "
     "events (16, 17 en 14). Lees die lijst dus niet als een uitspraak over wat de bron aanbiedt.")

note("oddsapi", "ok",
     "27 okt (run B): 19 van een plafond van 1863 credits gebruikt - 12 aan de bulk (h2h + "
     "spreads + totals voor vier competities, 3 per competitie) en 7 aan BTTS voor de zeven duels "
     "met een kandidaat-edge (§1a stap 2, de vereniging van beide schalen). split_budget(1863, 4) "
     "gaf (4, 4) en het plafond bond nergens. MARKTBALANS-CONTROLE GEHAALD EN ZEER RUIM: vier van "
     "de vier inkoopbare competities kregen zowel een uitkomstmarkt als een doelpuntenmarkt uit "
     "dezelfde bulk-aanroep, dus geen enkele competitie heeft alleen het een of het ander. Alle "
     "zes markten dongen mee: Over/Under 34 selecties, Asian Handicap 33, 1X2 27, BTTS 14, Draw "
     "No Bet 12 en Double Chance 3. DE TWEEDE RONDE HEEFT WAT OPGELEVERD: Virtus Entella - "
     "Avellino kwam in ronde 1 zonder BTTS als 'data conflicterend' uit de analyse en staat met "
     "BTTS erbij als derde regel op de lijst. net_price is op elke koers toegepast: twee van de "
     "drie gepubliceerde regels staan bij Matchbook (beurs) en zijn na 2% commissie gerekend.")

note("betexplorer", "ok",
     "27 okt (run B): fixturepagina's van alle zeventien competities van de runlijst opgehaald, "
     "geen enkele fout en geen enkele lege respons - en dat laatste is sinds de twee stille "
     "verhuizingen van de Braziliaanse slug (16 en 26 okt) het ding om op te letten. Rijen per "
     "spelende competitie: Serie B 20, English League One 17, English League Two 14, Allsvenskan "
     "10 en Croatian HNL 4. TWEEDE BRON OP DE VRAAG WELKE WEDSTRIJDEN ER ZIJN: 17 van de 17 "
     "competities bevestigd, 15 duels tegen 15 bij Fotmob, geen enkele afwijking - inclusief de "
     "twaalf competities die vandaag nul duels in het venster hebben, waar BetExplorer eveneens "
     "nul geeft en de eerstvolgende speeldag noemt (Eliteserien en MLS 29.10., 2. Bundesliga "
     "30.10., Keuken Kampioen Divisie en de meeste Europese lijsten 01.11., Serie A BRA 03.11.). "
     "Levert daarnaast het gratis 1X2-marktgemiddelde voor §6e en poort 8, en voor Croatian HNL "
     "is het de enige prijsbron.")

note("understat", "niet_bevraagd",
     "27 okt (run B): NIET bevraagd en dat is geen storing. Understat dekt vijf competities (PL, "
     "La Liga, Bundesliga, Serie A, Ligue 1) en geen van de vijf staat op de runlijst van Run B; "
     "er was vandaag dus niets voor hem te doen. De laatste geslaagde meting staat in "
     "detail_history. De redundantie waarvoor hij sinds 31 aug bestaat (§4) geldt voor Run A en "
     "niet voor deze runlijst: valt Fotmob om, dan heeft Run B geen tweede xG-bron en wordt elke "
     "wedstrijd data_tier NONE.")

note("api_football", "missing_key",
     "27 okt (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT VAN DE GEBRUIKER van 27 sep "
     "2026 en geen storing - hij wil hier geen geld aan uitgeven (§3, 'API_FOOTBALL_KEY komt er "
     "niet'). Niet als gat melden, niet als actiepunt en niet in de notificatie. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf, vandaag geen van de runlijst). Het wordt "
     "pas een echte vraag zodra Fotmob niet meer levert; dan is er geen onafhankelijke kansinput "
     "meer en levert elke run gegarandeerd nul bets. Fotmob leverde vandaag volledig.")

note("settling", "ok",
     "27 okt (run B): niets af te wikkelen en dat is de juiste uitkomst, geen overgeslagen stap. "
     "ledger.py open gaf drie wachtende picks, alle drie van Run A van vandaag (Serie A, aftrap "
     "vanavond, -14 tot -17 uur na aftrap); shadow.py open gaf een wachtende schaduwrij, "
     "eveneens van vandaag. Run A heeft om 02:50 de vier picks en tien schaduwrijen van 26 okt "
     "afgewikkeld, dus er stond voor deze run niets open. Het logboek heeft nu drie open picks, "
     "alle drie van vandaag, plus de drie van deze run. calibration.py settle en ctxlog.py settle "
     "zijn gedraaid: 0 nieuw afgewikkeld, 84 respectievelijk 32 nog open - alle van vandaag en "
     "gisteravond. recalibrate.load_fit().fitted_through staat op 2026-10-26, de vorige rundag, "
     "dus de controle van §6b-5c is groen.")

H["last_run"] = {
    "run": "B", "date": "2026-10-27",
    "note": (
        "VIJFTIEN duels in het inzetvenster over VIJF van de zeventien competities (Serie B 7, "
        "English League One 5, Allsvenskan 1, Croatian HNL 1, English League Two 1), 15 onder de "
        "dinsdagcap van 40 en dus niets afgekapt. ZES DUELS OP NONE, alle zes door de omrekening "
        "van §4: drie Italiaanse promovendi uit de Serie C en York City uit de National League "
        "hebben geen gemeten divisiepaar, en Leicester City en Cambridge United vallen buiten het "
        "gemeten bereik. DRIE REGELS. Boven zijn eigen lat: CESENA - EMPOLI, 1X2 Cesena wint "
        "@2,27 met +11,68 pp. Op rangorde eronder: Luton Town - Doncaster Rovers Under 3,5 "
        "@1,6272 (+5,05 pp) en Virtus Entella - Avellino 'beide ploegen scoren - nee' @1,9212 "
        "(+5,26 pp). TWEE ONAFHANKELIJKE METINGEN SPREKEN DE LIJST TEGEN EN DAT IS DE "
        "HOOFDWAARSCHUWING: Pinnacle zet Cesena op 43,2% waar dit model 55,7% zegt (+15,71 pp, de "
        "grootste afstand van de acht toetsbare duels), en de marktvormtelling van §4 spreekt de "
        "BTTS-nee van Virtus Entella tegen (beide ploegen op 62% BTTS dit seizoen). Twee van de "
        "drie regels staan op de minder-doelpunten-kant; goalbias meet die kant vandaag op +0,581 "
        "doelpunt per duel over 100 gespeelde Unders (z = +3,51), scherper dan de +0,68 waarop "
        "poort 9 op 11 oktober is gebouwd. BEVINDING: de stadionvelden van Fotmob zijn op deze "
        "runlijst wel gevuld (15 van 15) waar Run A ze drie dagen op rij leeg had - die leegte "
        "zit in de bekerinvoer en niet in de bron. Poort 5 vangt 89 van de 123 selecties weg "
        "(72,4%), poort 8 houdt er 13 tegen over vier duels, poort 7 vijf op een duel en poort 9 "
        "vandaag niets. Nul bronstoringen, 19 van 1863 credits."
    )}
H["updated"] = "2026-10-27"
H["last_run_bevinding"] = (
    "27 okt (run B): de stadioncontrole van §1c werkt, en dat is vandaag voor het eerst met "
    "cijfers te zien. Run A meldde vanochtend - en op 25 en 26 okt ook - dat venue.name bij ALLE "
    "duels van die run None was, met de conclusie dat 'niet verplaatst' daar 'geen verplaatsing "
    "gemeten' betekent. Op de runlijst van Run B is het veld bij ALLE 15 duels gevuld: 14 keer "
    "hetzelfde stadion als het eigen stadion van de thuisploeg en een keer een alarm (LR Vicenza "
    "- Modena in Stadio Romeo Menti tegen home_ground Stadio Comunale Rino Mercante). Daarmee is "
    "de leegte van Run A gelokaliseerd in de BEKERINVOER waarmee die run sinds 25 oktober werkt "
    "en niet in Fotmob zelf - een volgende Run A hoeft die diagnose dus niet over te doen en kan "
    "meteen de vraag stellen waarom de bekerroute geen venue meegeeft. Het alarm van vandaag is "
    "vermoedelijk zelf een bronfout en geen verplaatsing: Romeo Menti IS het stadion van LR "
    "Vicenza en Rino Mercante hoort bij Bassano, dus home_ground staat op de verkeerde club. Het "
    "duel staat op tier NONE en raakt geen bet, maar §1c eist dat een alarm wordt genoemd ook als "
    "de poort opengaat.")

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt")

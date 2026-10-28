"""Run B, 28 okt 2026 — bronprobe voor source-health.json.

ZESENTWINTIG duels in het inzetvenster over VIER competities, alle 26 onder de woensdagcap van 40.
Alle vier de bronkanten werkelijk in gebruik; Understat deed niet mee (geen van zijn vijf
competities staat op deze runlijst).

GEEN ENKELE BRONSTORING. `store["errors"]` is over de hele run leeg gebleven.

DE BRONBEVINDING VAN VANDAAG GAAT OVER DE SPORTKEY-REGISTRATIE, en ze is een vervolg op wat Run A
vanochtend vond. Drie competities van deze runlijst — Eliteserien, MLS en Série A (BRA) — stonden
actief bij The Odds API en níet in `oddsapi.SPORT_KEYS`, en de woordenlijst waarmee `api_check.py`
dat soort gaten vindt was Europees, zodat de twee Amerikaanse competities voor diezelfde controle
onzichtbaar waren. Beide zijn vandaag gerepareerd.
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
     "28 okt (run B): daglijsten 28 en 29 okt opgehaald (271 duels over 72 competities en 125 over "
     "51); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand, "
     "afsluitcode 0 - ook voor de dertien competities van deze runlijst die vandaag stil zijn, en "
     "dat is precies de kant van de controle die iets kan opleveren. Standen van alle vier de "
     "spelende competities geleverd (Allsvenskan, Serie B, MLS, Série A BRA), ALLE VIER MET xG - "
     "op een Run B-dag ongebruikelijk, want de vijf competities van deze runlijst zonder xG (CZE, "
     "CRO, HUN, ROU, KKD) spelen vandaag niet. Context voor alle 26 duels zonder fout en alle 26 "
     "in het contextlogboek, dus geen enkele squad_value 0 deze run. DE STADIONVELDEN ZIJN WEER "
     "VOLLEDIG GEVULD (26 van 26), wat de diagnose van gisteren bevestigt dat de leegte van Run A "
     "in de bekerinvoer zit en niet in Fotmob. TWEE ALARMEN, en een ervan raakt een GEPUBLICEERDE "
     "REGEL: NEW YORK CITY FC - ATLANTA UNITED staat in CITI FIELD terwijl het genoteerde eigen "
     "stadion Yankee Stadium is. Dat is bij NYCFC geen bronfout maar hun normale gang van zaken - "
     "ze spelen hun thuisduels verdeeld over beide stadions - en het is dus een ECHTE "
     "verplaatsing in de zin van §1c: de ploeg speelt niet op het veld waarop het model zijn "
     "thuisvoordeel baseert. De poort gaat open omdat de selectie een Over/Under is (side = None), "
     "maar §1c eist dat een verplaatsing wordt genoemd ook als de poort opengaat, en hier staat ze "
     "onder een regel die wordt gepubliceerd. Het tweede alarm is REMO - BOTAFOGO (Estádio Edgar "
     "Augusto Proença in plaats van Estádio Evandro Almeida), op een duel dat hoe dan ook op tier "
     "NONE staat. lineupType: 26 van de 26 op 'lastStarting11' en geen enkel 'confirmed' - te "
     "verwachten om 04:00 NL bij aftrappen van 19:00 tot 03:30 de volgende nacht, en bij de "
     "veertien MLS-duels nog ruimer. Voorbeschouwingsblokken (preview.py) voor alle drie de bets "
     "zonder fout, en marketform.match_block voor alle 23 doorgerekende duels zonder fout.")

note("the_odds_api", "ok",
     "28 okt (run B): sleutel geldig, 51 actieve voetbalcompetities, quota 18.607 over en 1.393 "
     "verbruikt bij de start van de run. Geen afgewezen sleutel en geen quotaprobleem. ALLE VIER "
     "DE SPELENDE COMPETITIES HEBBEN EEN SPORTKEY en kregen de volledige bulk-aanroep; er is "
     "vandaag dus geen enkele competitie die op het gratis BetExplorer-marktgemiddelde moet "
     "draaien. DAT IS NIET VANZELF ZO EN HET IS DE BRONBEVINDING VAN DEZE RUN: `MLS (USA)`, "
     "`Série A (BRA)` en `Eliteserien (NOR)` stonden actief bij de bron en NIET in "
     "oddsapi.SPORT_KEYS, en `English League One/Two (ENG)` stonden er wel maar onder een andere "
     "naam dan run-b.md en coverage.json gebruiken - een opzoeking op de runlijstnaam gaf daar "
     "None. De runscripts gaven die sleutels zelf mee, dus er is geen koers gemist; wat eraan "
     "vastzat is dat api_check.py ze niet kon controleren en dat een run die op de registratie "
     "vertrouwt stil op het marktgemiddelde terugvalt - precies hoe de Scottish Premiership zeven "
     "weken is weggezakt (Run A, vandaag). Alle vijf zijn vandaag aan SPORT_KEYS toegevoegd, de "
     "drie nieuwe bevestigd actief via /sports/ (0 credits). DE WOORDENLIJST VAN api_check.py IS "
     "OOK GEREPAREERD: Run A verving gisteren het veld waarop wordt gefilterd (sleutel -> sleutel "
     "+ titel + beschrijving) maar de landenlijst bleef Europees, zonder 'usa', 'brazil' of "
     "'hungar'. Daardoor waren juist de twee competities die vandaag 19 van de 26 duels leverden "
     "onzichtbaar voor die controle. Na de correctie telt de registratie 34 sleutels (33 actief, "
     "Coppa Italia niet) en komt er een sleutel uit die eerder onzichtbaar was: "
     "soccer_brazil_serie_b. Die laatste staat op geen enkele runlijst en is dus een constatering, "
     "geen actiepunt.")

note("oddsapi", "ok",
     "28 okt (run B): 28 van een plafond van 2323 credits gebruikt - 12 aan de bulk (h2h + spreads "
     "+ totals voor vier competities, 3 per competitie) en 16 aan BTTS voor de zestien duels met "
     "een kandidaat-edge (§1a stap 2, de vereniging van beide schalen). split_budget(2323, 4) gaf "
     "(4, 4) en het plafond bond nergens. MARKTBALANS-CONTROLE GEHAALD EN ZO RUIM ALS HET KAN: "
     "vier van de vier competities kregen zowel een uitkomstmarkt als een doelpuntenmarkt uit "
     "dezelfde bulk-aanroep, dus geen enkele competitie heeft alleen het een of het ander. Alle "
     "zes markten dongen mee: Over/Under 112 selecties, Asian Handicap 108, 1X2 66, BTTS 32, Draw "
     "No Bet 20 en Double Chance 15. DE TWEEDE RONDE HEEFT WAT OPGELEVERD: de BTTS-nee van Toronto "
     "- DC United kwam als vierde gekwalificeerde uitdrukking van dat duel binnen (+10,05 pp). "
     "net_price is op elke koers toegepast: ALLE DRIE de gepubliceerde regels staan bij Matchbook "
     "(beurs) en zijn na 2% commissie gerekend - 1,69/1,6762, 2,08/2,0584 en 1,66/1,6468.")

note("betexplorer", "ok",
     "28 okt (run B): fixturepagina's van alle zeventien competities van de runlijst opgehaald, "
     "geen enkele fout en geen enkele lege respons - en dat laatste is sinds de twee stille "
     "verhuizingen van de Braziliaanse slug (16 en 26 okt) het ding om op te letten; de "
     "Braziliaanse pagina gaf vandaag 20 rijen. Rijen per spelende competitie: Série A BRA 20, "
     "Allsvenskan 15, MLS 14 en Serie B 13. TWEEDE BRON OP DE VRAAG WELKE WEDSTRIJDEN ER ZIJN: 17 "
     "van de 17 competities bevestigd, 26 duels tegen 26 bij Fotmob, geen enkele afwijking - "
     "inclusief de dertien competities die vandaag nul duels in het venster hebben, waar "
     "BetExplorer eveneens nul geeft en de eerstvolgende speeldag noemt (elf op 01.11., English "
     "League Two en 2. Bundesliga op 30.10.). LET OP DE is_today-VLAG BIJ DE AMERIKAANSE "
     "COMPETITIES: bij MLS staat hij op nul van de veertien en noteert BetExplorer de duels als "
     "'Tomorrow 00:30' en verder. Dat is geen afwijking maar hetzelfde feit als de nachtband van "
     "het inzetvenster, en het bevestigt die onafhankelijk - de koppeling gebeurt op het "
     "namenpaar en niet op die vlag, dus alle veertien zijn gewoon gekoppeld. Levert daarnaast "
     "het gratis 1X2-marktgemiddelde voor §6e en poort 8.")

note("understat", "niet_bevraagd",
     "28 okt (run B): NIET bevraagd en dat is geen storing. Understat dekt vijf competities (PL, "
     "La Liga, Bundesliga, Serie A, Ligue 1) en geen van de vijf staat op de runlijst van Run B; "
     "er was vandaag dus niets voor hem te doen. De laatste geslaagde meting staat in "
     "detail_history. De redundantie waarvoor hij sinds 31 aug bestaat (§4) geldt voor Run A en "
     "niet voor deze runlijst: valt Fotmob om, dan heeft Run B geen tweede xG-bron en wordt elke "
     "wedstrijd data_tier NONE. Dat is de uitzondering van §3 die dan WEL vooraan in de "
     "notificatie hoort.")

note("api_football", "missing_key",
     "28 okt (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT VAN DE GEBRUIKER van 27 sep "
     "2026 en geen storing - hij wil hier geen geld aan uitgeven (§3, 'API_FOOTBALL_KEY komt er "
     "niet'). Niet als gat melden, niet als actiepunt en niet in de notificatie. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf, vandaag geen van de runlijst). Het wordt "
     "pas een echte vraag zodra Fotmob niet meer levert; dan is er geen onafhankelijke kansinput "
     "meer en levert elke run gegarandeerd nul bets. Fotmob leverde vandaag volledig.")

note("settling", "ok",
     "28 okt (run B): niets af te wikkelen en dat is de juiste uitkomst, geen overgeslagen stap. "
     "ledger.py open gaf drie wachtende picks, alle drie van Run A van vandaag (League Cup, DFB "
     "Pokal en Scottish Premiership, aftrap vanavond, -16,6 uur na aftrap); shadow.py open gaf "
     "achttien wachtende schaduwrijen, alle van Run A van vandaag. Run A heeft om 02:44 de zes "
     "picks en zeven schaduwrijen van 27 okt afgewikkeld, dus er stond voor deze run niets open. "
     "calibration.py settle en ctxlog.py settle zijn gedraaid zoals §6b-5c en 5d eisen: 0 nieuw "
     "afgewikkeld, 162 respectievelijk 54 nog open - alle van vandaag en vanavond. "
     "recalibrate.load_fit().fitted_through staat op 2026-10-27, de vorige rundag, dus de "
     "controle van §6b-5c is groen.")

H["last_run"] = {
    "run": "B", "date": "2026-10-28",
    "note": (
        "ZESENTWINTIG duels in het inzetvenster over VIER van de zeventien competities (MLS 14, "
        "Série A BRA 5, Allsvenskan 4, Serie B 3), 26 onder de woensdagcap van 40 en dus niets "
        "afgekapt. Alle vier de competities hebben xG, dus geen enkel duel op LIGHT wegens een "
        "ontbrekende xG-bron. DRIE DUELS OP NONE, alle drie door de omrekening van §4: twee "
        "Braziliaanse promovendi (Chapecoense, Remo) waarvoor er geen gemeten factor is voor het "
        "paar Série A/Série B, en Arezzo als promovendus uit de Serie C, waar promotion.TIER2 geen "
        "divisie onder Serie B heeft. HET INZETVENSTER DEED WAARVOOR HET IS GEMAAKT: 16 van de 26 "
        "duels liggen in de nachtband 00:00-08:00 NL en ELF stonden op de daglijst van 29 oktober. "
        "Onder de oude UTC-regel waren die aan de run van morgen toegewezen - te laat, want dan "
        "zijn ze gespeeld. Dit is de grootste dag van dat soort sinds runwindow.py op 24 september "
        "is ingevoerd, en alle drie de gepubliceerde regels zitten erin. DRIE REGELS, EN ALLE DRIE "
        "ZIJN EEN UNDER - dat is de hoofdwaarneming van deze run en het is de kant waarvan §6g op "
        "uitkomsten meet dat ze fout staat. Boven zijn eigen lat (en boven de verzwaarde Under-lat "
        "van 10,0): TORONTO FC - DC UNITED Under 3,5 @1,6762 met +13,95 pp. Op rangorde eronder: "
        "Santos - Palmeiras Under 2,5 @2,0584 (+7,70 pp) en New York City FC - Atlanta United "
        "Under 3,5 @1,6468 (+6,12 pp). TWEE ONAFHANKELIJKE METINGEN SPREKEN DE LIJST TEGEN: "
        "Pinnacle staat op de Under-kant gemiddeld 4,42 pp onder dit model over 23 (duel, "
        "lijn)-paren met 17 van de 23 erboven, en bij Toronto is dat +17,10 pp - de grootste "
        "afstand van alle 23. En goalbias meet de gespeelde Under-kant op +0,659 doelpunt per duel "
        "over 103 gevallen met z = +4,04, het hardste cijfer dat daar tot nu toe op staat. De "
        "marktvormtelling van §4 spreekt alle drie de regels op minstens een reeks tegen, het "
        "scherpst bij Toronto: 4,12 doelpunten per thuisduel dit seizoen en in alle zestien "
        "thuisduels scoorden beide ploegen. POORT 9 BOND VANDAAG VOOR HET EERST WERKELIJK en hield "
        "twee duels tegen (Austin FC +8,22 pp en St. Louis City +9,67 pp tegen de lat van 10,0); "
        "gisteren hield hij niets tegen. BEVINDING: vijf sportkeys van deze runlijst ontbraken in "
        "de registratie en de controle die ze had moeten vinden keek alleen naar Europa. Poort 5 "
        "vangt 275 van de 353 selecties weg (77,9%), poort 8 houdt er 11 tegen over vijf duels en "
        "poort 7 11 over vier duels. Nul bronstoringen, 28 van 2323 credits."
    )}
H["updated"] = "2026-10-28"
H["last_run_bevinding"] = (
    "28 okt (run B): een sleutel die alleen in een runscript staat, is voor de controle niet te "
    "zien - en de controle die dat had moeten vinden, keek alleen naar Europa. Run A vond vandaag "
    "dat de Scottish Premiership zeven weken op het marktgemiddelde had gedraaid omdat soccer_spl "
    "niet in oddsapi.SPORT_KEYS stond, repareerde het veld waarop api_check.py filtert, en liet "
    "twee sleutels liggen die niet op zijn runlijst stonden. Op de runlijst van Run B staan er "
    "VIJF: Eliteserien, MLS en Série A (BRA) ontbraken volledig, en English League One/Two stonden "
    "er onder een andere naam dan run-b.md en coverage.json gebruiken. BIJ RUN B IS GEEN KOERS "
    "GEMIST - de runscripts gaven die sleutels sinds 29 aug zelf mee - en dat is precies wat het "
    "zo lang kon laten staan: in rb_oct27_odds.py stond een alinea die uitlegde dat de lijst van "
    "api_check.py 'krapper is dan de werkelijkheid' en dat je hem niet moet lezen als 'deze "
    "competitie heeft geen prijzen'. Dat was feitelijk juist en het is de verkeerde conclusie: de "
    "controle was niet krap maar stuk, en een run die de uitkomst wegschrijft als bekende ruis "
    "haalt de prikkel weg om hem te repareren. De oorzaak van de blindheid is gevonden en "
    "verholpen: de landenlijst in api_check.py bevatte geen 'usa', geen 'brazil' en geen 'hungar', "
    "dus de twee competities die vandaag 19 van de 26 duels leverden waren voor die controle "
    "onzichtbaar. Na de correctie komt er een sleutel uit die eerder niet zichtbaar was "
    "(soccer_brazil_serie_b, op geen runlijst - constatering, geen actiepunt). Dezelfde stille "
    "faalvorm als het Serie B-id en als calibration.py settle, nu in de gedaante van een te korte "
    "woordenlijst: een controle kan groen staan omdat ze de verkeerde grootheid meet (§6g).")

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt")

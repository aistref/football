"""Run A, 4 nov 2026 — bronprobe voor source-health.json.

VEERTIEN duels in het inzetvenster over VIER competities (Champions League 9, Championship 3,
Europa League 1, Belgian Pro League 1), tegen een woensdagcap van 40: niets afgekapt. Geen beker
heeft een ronde en de Conference League speelt pas donderdag.

GEEN ENKELE BRONSTORING DIE DE RUN RAAKT. Fotmob, The Odds API, BetExplorer en Pinnacle leverden
alle vier zonder fout.

UNDERSTAT IS VOOR DE DERDE DAG OP RIJ ONBRUIKBAAR, EN NU MET EEN DERDE SYMPTOOM: 1 nov een 502 op
de CONNECT van de netwerkgateway, 3 nov een `Connection reset by peer`, en vandaag komt er wél een
antwoord van 26.719 bytes terug maar GEEN JSON op `getLeagueData/EPL/2025`. Drie dagen, drie
symptomen. Het raakt vandaag niets: geen van de vijf gedekte competities speelt. Zie `understat`.

DE BEVINDING VAN VANDAAG ZIT NIET IN EEN BRON MAAR IN DE SAMENLOOP VAN TWEE METINGEN: de rangorde
van §5b is vandaag gelijk aan de rangorde van de onenigheid met Pinnacle, en de koers van de
bovenste bet komt van Pinnacle zelf. Zie `last_run_bevinding`.
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
    print(f"{key:22} {status:12} {detail[:90]}")


note("fotmob", "ok",
     "4 nov (run A): daglijsten 4 en 5 nov opgehaald (45 competities / 120 duels en 37 / 93) en "
     "voor de afwikkeling die van 2, 3 en 4 nov (436 duels geindexeerd). idcheck.py gaf voor alle "
     "33 fotmob_id's uit coverage.json een bruikbare stand. Standen geleverd voor de vier "
     "spelende competitiebases (Champions League id 42, Championship id 48, Europa League id 73 "
     "en Belgian Pro League id 40, alle vier met xG) plus de divisies voor de VIER omgerekende "
     "ploegen van vandaag (Premier League voor West Ham United en Wolverhampton Wanderers, de "
     "Engelse en de Belgische tweede divisie voor Cardiff City en Kortrijk). Context opgehaald "
     "voor alle 14 duels zonder fout, en het wedstrijddossier voor de twee gepubliceerde. "
     "De drie bekers met een fotmob_id (League Cup 133, DFB Pokal 209, KNVB Beker 235) gaven nul "
     "duels in het venster.")

note("the_odds_api", "ok",
     "4 nov (run A): api_check.py gaf 19.808 credits over en 192 verbruikt deze maand; 49 actieve "
     "voetbalcompetities, en 31 van de 34 sportkeys van de repo actief. NIET actief: Coppa Italia "
     "(speelt vandaag niet, eerstvolgende ronde 1 dec - dezelfde bevinding langs twee wegen, geen "
     "storing) en English League Two / League Two (Run B). Zes actieve sportkeys die de repo niet "
     "kent: Brazil Serie B, Frauen-Bundesliga, 3. Liga, Copa del Rey, Superettan en UEFA Nations "
     "League - geen daarvan staat in de runlijst van Run A. "
     "Bulk-aanroep (h2h + spreads + totals) gelukt voor alle VIER de spelende competities, 12 "
     "credits; daarna 10 credits aan BTTS voor de 10 duels met een kandidaat-edge. 22 van een "
     "plafond van 366, nog 19.786 over. Marktbalans op de inkoop gehaald: 4 van 4 competities "
     "kregen zowel een uitkomst- als een doelpuntenmarkt.")

note("betexplorer", "ok",
     "4 nov (run A): fixturepagina's van alle 16 competities met een slug opgehaald, plus de vijf "
     "bekers. Marktgemiddelde 1X2 geleverd voor de vier spelende competities (15, 10, 9 en 18 "
     "rijen) en gebruikt waar het hoort - het kalibratieblok van §6e en poort 8, niet voor de bet "
     "zelf. Als TWEEDE BRON op de runlijst is hij het over alle 16 competities met Fotmob eens: "
     "14 duels tegen 14, zonder enig verschil. "
     "EEN WAARNEMING OVER DE TIJDZONE, want de docstring van het bevestigingsscript beweert dat "
     "`MatchOdds.when` UK-tijd is (NL -1 uur): vandaag geeft BetExplorer 'Today 18:45' / "
     "'Today 21:00' voor de Champions League en 'Today 16:30' voor de Europa League, en dat is "
     "EXACT de NL-klok van Fotmob (17:45Z / 20:00Z / 15:30Z). Op deze pagina's staat dus CET en "
     "geen UK-tijd. Het raakt vandaag niets - de gepubliceerde aftraptijden komen uit kickoff_utc "
     "via zoneinfo, en de venstertoets snijdt om 07:00 waar geen duel in de buurt komt - maar op "
     "een dag met een duel tussen 07:00 en 08:00 zou die aanname de tweede bron een duel laten "
     "missen. Niet gerepareerd: de aanname hoort per pagina gemeten te worden, niet per run "
     "geraden. Opgeschreven als openstaand punt.")

note("understat", "onbereikbaar",
     "4 nov (run A): DERDE dag op rij onbruikbaar en nu met een DERDE symptoom. 1 nov: HTTP 502 op "
     "de CONNECT van de netwerkgateway. 3 nov: `Connection reset by peer`. Vandaag: er komt wel "
     "een antwoord van 26.719 bytes terug op https://understat.com/getLeagueData/EPL/2025, maar "
     "het is GEEN JSON - `UnderstatError: geen JSON terug`. De host is dus bereikbaar en levert "
     "een pagina in plaats van de dataroute. "
     "HET RAAKT VANDAAG NIETS en dat is geen geluk maar de kalender: Understat dekt vijf "
     "competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) en geen van die vijf speelt vandaag. "
     "Er is dus geen duel waarbij de tweede, onafhankelijke xG-arm is weggevallen, en geen "
     "kalibratieblok met een lege `p_xg_understat`. "
     "WAT HET WEL BETEKENT, en dat hoort er drie dagen op rij bij te staan: de redundantie van §4 "
     "staat uit. Valt Fotmob om terwijl dit zo blijft, dan is er voor geen enkele wedstrijd een "
     "kansbron meer en levert elke run gegarandeerd nul bets (§3). Fotmob levert vandaag zonder "
     "fout, dus dat is een risico en geen storing. Drie symptomen op drie dagen wijzen eerder op "
     "de route dan op een incident; dat is iets om te blijven volgen, niet om vandaag op te "
     "handelen.")

note("api_football", "plan_limited",
     "4 nov (run A): API_FOOTBALL_KEY is niet gezet en dat blijft zo. Besluit van de gebruiker van "
     "27 sep 2026 ('Dat wil ik niet') - geen gat, geen actiepunt en niet in de notificatie (§3, "
     "'API_FOOTBALL_KEY komt er niet'). De kanskant komt van Fotmob (alle competities) en "
     "Understat (vijf, vandaag onbruikbaar). Dit wordt pas een reele vraag als Fotmob omvalt; "
     "dan hoort het vooraan in de notificatie met de aantekening dat het besluit van 27 september "
     "onder andere omstandigheden is genomen.")

note("pinnacle", "ok",
     "4 nov (run A): 1X2 gevonden voor 45 events in de responsen, doelpuntentotalen voor 45. "
     "Gemiddelde Pinnacle-marge 3,54% op het 1X2 (3,1-4,2%) en 2,8-3,4% op de totalen - opnieuw de "
     "scherpste van de dag. Gemiddelde absolute afstand tussen het eigen 1X2 en het de-vigde "
     "Pinnacle-oordeel over 13 duels: 5,11 pp; op de Under-kant staat de eigen kans gemiddeld "
     "+6,02 pp BOVEN Pinnacle en bij 10 van de 13 erboven. "
     "DIT IS DE BEVINDING VAN DE RUN. De drie grootste afstanden op de doelpuntenlijn zijn exact "
     "de drie duels die alle negen poorten haalden: AEK Athens - Real Madrid +20,05 pp, RB Leipzig "
     "- Manchester City +18,98 pp en FC Porto - Napoli +14,00 pp. Op het 1X2 wijst het dezelfde "
     "kant op: bij AEK Athens - Real Madrid geeft Pinnacle Real 0,793 en het model 0,565 "
     "(-22,88 pp, de grootste van de dag), bij PSV Eindhoven - Club Brugge geeft Pinnacle PSV "
     "0,482 en het model 0,649 (+16,66 pp, de tweede). Harde grens §2: geen van deze getallen "
     "gaat in my_prob of prob_sources; ze bepalen de LEZING en niet de kans.")

note("settling", "ok",
     "4 nov (run A): 4 picks en 13 schaduwrijen afgewikkeld, alle zeventien van 3 november. Picks "
     "3 gewonnen / 0 verloren / 1 void (West Bromwich Albion - Southampton 1-1, Draw No Bet "
     "Southampton -> inzet terug). Schaduwrijen 3 gewonnen / 10 verloren. "
     "ALLE ZEVENTIEN DUELS WAREN LEAGUE- OF COMPETITIEWEDSTRIJDEN ZONDER VERLENGING (Champions "
     "League-leaguefase, Championship, League One/Two, Allsvenskan), dus `status.scoreStr` IS de "
     "stand na 90 minuten en er hoefden geen doelpuntminuten te worden opgezocht (§0 / §6d). Dat "
     "is per duel nagegaan en niet aangenomen. De `abandoned()`-controle van 3 november is "
     "meegenomen en sloeg vandaag nul keer aan: alle zeventien stonden op een normale eindstand. "
     "`calibration.py settle` (60 waarnemingen) en `ctxlog.py settle` (22 wedstrijden) zijn beide "
     "gedraaid; `recalibrate.load_fit().fitted_through` staat daarna op 2026-11-03, de vorige "
     "rundag.")

note("marktvorm_lijn", "gerepareerd",
     "4 nov (run A): de frequentietelling van §4 liep vast op een KWARTLIJN. `marketform.LINES` "
     "telt alleen 1.5, 2.0, 2.5, 3.0, 3.5 en 4.5, en de gepubliceerde bet van vandaag staat op "
     "Under 3.75 - dus gaf de weergave een `KeyError: '3.75'` en stopte het script halverwege de "
     "gepubliceerde regels. Dit is GEEN stille faalvorm (het script viel luidruchtig om, en dat "
     "is de goede kant), maar het is wel de derde keer in een week dat de lijn van de bet en de "
     "tabel van de telling niet op elkaar passen - zie de reparatie van 3 november, die de lijn "
     "uit de selectie ging lezen in plaats van uit een tabel met vier ingangen. "
     "DE OPLOSSING: valt de lijn van de bet niet in `LINES`, dan wordt de naastgelegen getelde "
     "lijn getoond. Bij Under 3.75 is dat '>3.5 doelpunten', en dat is ook inhoudelijk de juiste "
     "keuze: het vierde doelpunt beslist die bet, en dat is precies wat die reeks telt. Zelfde "
     "redenering als de bestaande 3.0 -> 3.5 afbeelding. "
     "EN DE TELLING SPREEKT DE BET VAN VANDAAG TEGEN, wat de hele reden is dat §4 haar eist: AEK "
     "Athens kwam dit seizoen in 2 van zijn 3 Champions League-duels boven 3,5 doelpunt uit "
     "(gemiddeld 3,67) en Real Madrid ook in 2 van 3 (gemiddeld 5,00, uit 7,00), terwijl de bet "
     "een Under 3.75 is met een modelkans van 73,1%. Dat staat VOORAAN in de voorbeschouwing en "
     "niet in een voetnoot (§4 punt 2). Let wel op n: drie duels per ploeg is de leaguefase tot nu "
     "toe, en Real Madrid staat over heel vorig seizoen op 5 van 14 (36%).")

H["last_run_bevinding"] = (
    "De rangorde van §5b was vandaag GELIJK aan de rangorde van de onenigheid met Pinnacle. De "
    "drie duels met de grootste afstand tussen de eigen P(Under) en het de-vigde "
    "Pinnacle-oordeel zijn exact de drie duels die alle negen poorten haalden, en de koers van de "
    "bovenste bet (AEK Athens - Real Madrid, Under 3.75 @1,96) komt van PINNACLE ZELF - op "
    "precies de lijn waarop het model 20 procentpunt van diens oordeel af staat. Dat is geen "
    "bevestiging door een tweede bron maar het tegendeel. §1g zegt het met cijfers: wie "
    "selecteert op de grootste edge, selecteert op de grootste modelfout; vandaag is dat geen "
    "abstracte waarschuwing maar een meting op de lijst zelf. "
    "TWEE VAN DE DRIE GEKWALIFICEERDE REGELS STAAN BOVENDIEN OP DE UNDER-KANT, waar `margins.py "
    "goalbias` over 124 gespeelde gevallen +0,597 doelpunt per duel te weinig meet (z = +4,01) "
    "terwijl het model zelf goed staat (+0,046, z = +1,18) - het is de selectie die scheef staat, "
    "niet de lambdas. En de frequentietelling van §4 spreekt de bovenste bet tegen: beide ploegen "
    "kwamen dit seizoen in tweederde van hun duels boven de lijn uit. "
    "BEIDE REGELS ZIJN DAAROM OP RISICOKLASSE HIGH GEZET en de tegenspraak staat vooraan in de "
    "voorbeschouwing. Er is NIETS aan een kans, een poort of een drempel veranderd: dat zou de "
    "anti-circulariteitsregel breken (een eigen kans verlagen omdat Pinnacle iets anders zegt) en "
    "een run verzet geen parameter op een enkele dag (§6d). "
    "DAARNAAST BOND `MAX_LIGHT_IN_SHORTLIST` = 2 VOOR HET EERST ECHT: drie selecties haalden alle "
    "negen poorten EN hun lat, alle drie op LIGHT, dus er zijn er twee gepubliceerd en is RB "
    "Leipzig - Manchester City (Under 3.5, +18,73 pp, score 6,262) als "
    "`gekwalificeerd_niet_gepubliceerd` plus een `near_miss` met `failed_gate = lijstlengte` "
    "vastgelegd - dezelfde naam, want §5b verbiedt er een tweede te verzinnen.")
H["last_run"] = {
    "run": "A",
    "date": "2026-11-04",
    "note": (
        "VEERTIEN duels in het inzetvenster over VIER van de eenentwintig competities (Champions "
        "League 9, Championship 3, Europa League 1, Belgian Pro League 1), tegen een woensdagcap "
        "van 40 - niets afgekapt. Dertien duels doorgerekend (1 op FULL, 12 op LIGHT) en EEN op "
        "NONE (Slavia Prague - Arsenal: de omgerekende verdediging van Arsenal is 0,373 en valt "
        "buiten het gemeten bereik 0,388-1,446 - `in_range` doet precies waarvoor hij bestaat). "
        "Zeventien competities hebben geen ronde; dat is bij TWEE bronnen nagetrokken en die zijn "
        "het over alle zeventien eens (14 tegen 14), zonder een enkele afwijking. GEEN ENKELE "
        "BRONSTORING die de run raakt: Fotmob, The Odds API, BetExplorer en Pinnacle leverden alle "
        "vier zonder fout; Understat is voor de derde dag onbruikbaar maar dekt geen van de "
        "spelende competities. 22 van 366 credits (12 bulk + 10 BTTS), 19.786 over. "
        "TWEE BETS GEPUBLICEERD UIT DRIE GEKWALIFICEERDE SELECTIES, en de derde viel weg op "
        "`MAX_LIGHT_IN_SHORTLIST` = 2 en niet op de lijstlengte. DE BEVINDING: de rangorde van "
        "vandaag is de rangorde van de onenigheid met Pinnacle, en de bovenste koers komt van "
        "Pinnacle zelf op de lijn waarop het model 20 pp van hem af staat.")}
H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt")

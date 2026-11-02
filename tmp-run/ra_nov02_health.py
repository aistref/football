"""Run A, 2 nov 2026 — bronprobe voor source-health.json.

TWAALF duels in het inzetvenster over ACHT competities, tegen een maandagcap van 40: niets
afgekapt. Geen beker heeft een ronde en geen Europees toernooi speelt.

ÉÉN BRONSTORING, EN DIE IS NIEUW: Understat is onbereikbaar. Niet met een 403, een
Cloudflare-challenge of een lege respons, maar met een 502 op de CONNECT van de netwerkgateway van
de container — dus de verbinding komt er niet eens tot aan de site. Dat raakt het kalibratieblok
van §6e voor vier competities en geen enkele kansschatting (§2: Understat gaat per ontwerp niet in
`my_prob`). Zie `understat`.

DE BEVINDING VAN VANDAAG ZIT IN DE REPO EN NIET IN EEN BRON: de dagranglijst van §5b liet een
selectie die haar lat niet haalt een selectie verdringen die hem wél haalt. Zie
`toplist_dagranglijst` en `last_run_bevinding`.
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
     "2 nov (run A): daglijsten 2 en 3 nov opgehaald en voor de afwikkeling die van 1 en 2 nov. "
     "idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. Standen van "
     "alle benodigde competitiebases geleverd: de acht spelende competities plus de divisie "
     "eronder voor de TWEE omgerekende ploegen (LaLiga2 voor Deportivo A Coruna, de Poolse I liga "
     "voor Slask Wroclaw). Context voor ALLE TWAALF duels opgehaald zonder een enkele fout, "
     "waarvan acht met een voorspelde opstelling en drie met de laatste basiself; bij Rakow "
     "Czestochowa - Pogon Szczecin staat het opstellingsblok op 'unavailable', waardoor dat duel "
     "niet in het contextlogboek belandt (elf van de twaalf) en de datarijkdom er het middenpunt "
     "krijgt in plaats van nul (§1c: een meting die er niet is, is geen bewijs van een probleem). "
     "Dat duel kwam ook op de laagste datarijkdom van de run uit (4,5). Ook de bekertak liep "
     "hierlangs: de daglijst geeft voor League Cup (133), DFB Pokal (209) en "
     "KNVB Beker (235) nul duels in het venster. "
     "FOTMOB IS VANDAAG DE ENIGE XG-BRON VOOR ALLE ACHT SPELENDE COMPETITIES, want Understat lag "
     "eruit. De uitzondering van §3 punt 3 (melden zodra Fotmob omvalt) is dus niet aan de orde, "
     "maar de marge is vandaag nul: valt Fotmob ook om, dan is er geen kansinput meer.")

note("the_odds_api", "ok",
     "2 nov (run A): sleutel werkt. api_check.py: 48 actieve voetbalcompetities, 19893 credits "
     "over en 107 verbruikt deze maand, en 33 van de 34 sportkeys van de repo actief vandaag. "
     "DE ENIGE INACTIEVE IS COPPA ITALIA (soccer_italy_coppa_italia) en dat klopt met de tweede "
     "bron: BetExplorer zet de eerstvolgende ronde op 1 december. Vier actieve sportkeys kent de "
     "repo niet (soccer_brazil_serie_b, soccer_germany_liga3, soccer_sweden_superettan, "
     "soccer_uefa_nations_league); geen van vier staat op een runlijst van Run A. "
     "INKOOP: alle ACHT spelende competities hebben een sportkey en kregen de volledige bulk "
     "(h2h + spreads + totals, 3 credits per competitie, 24 in totaal), plus een tweede ronde "
     "BTTS van 10 credits voor de tien duels met een kandidaat-edge (§1a stap 2). 34 van een "
     "plafond van 342 (suggest_cap over 29 dagen tot de maandwissel, twee runs per dag), 19859 "
     "over. Geen enkel duel hoefde op het gratis BetExplorer-marktgemiddelde te leunen.")

note("betexplorer", "ok",
     "2 nov (run A): marktgemiddelde 1X2 voor alle acht spelende competities geleverd (7 tot 22 "
     "fixturerijen per competitie) en de fixturepagina's van alle vijf de bekers plus de drie "
     "Europese toernooien. Dat tweede is de bevestiging door een tweede methode van §1, en ze is "
     "het over ALLE ZESTIEN competities met Fotmob eens: 12 duels tegen 12, zonder enig verschil. "
     "Alle vijf bekerpagina's gaven teamparen (FA Cup 40, League Cup 4, Coppa Italia 8, KNVB "
     "Beker 16, DFB Pokal 8), dus er is nergens een lege pagina die als bevestiging zou kunnen "
     "worden gelezen - anders dan op 1 november, toen de DFB Pokal-pagina leeg was.")

note("understat", "onbereikbaar",
     "2 nov (run A): NIET BEREIKBAAR, en dat is nieuw. Alle vier de gedekte competities die "
     "vandaag spelen (Premier League, Serie A, La Liga, Ligue 1; Bundesliga speelt niet) gaven "
     "dezelfde fout: 'UnderstatError: URLError op https://understat.com/getLeagueData/<comp>/2025: "
     "<urlopen error Tunnel connection failed: 502 Bad Gateway>'. "
     "HET IS NIET HET SCRIPT EN NIET DE SITE-BEVEILIGING. Een losse curl naar hetzelfde adres "
     "geeft 'CONNECT tunnel failed, response 502', en de proxystatus van de container noteert het "
     "als 'connect_rejected - gateway answered 502 to CONNECT (policy denial or upstream "
     "failure)' voor understat.com:443. Dit is dus iets anders dan de Cloudflare-challenge van "
     "fbref/Forebet/FootyStats/PredictZ: daar antwoordt de site, hier komt de verbinding niet tot "
     "de site. De regel van §3 ('niet omzeilen') geldt hier niet eens - er is niets om langs te "
     "gaan. "
     "WAT HET KOST: het kalibratieblok van §6e krijgt vandaag geen Understat-arm voor die vier "
     "competities, dus de vergelijking tussen de eigen xG-arm en de Understat-arm (die sinds "
     "19 sep structureel scheever staat: +3,11 pp op longshots tegen +0,90 voor de eigen arm) kan "
     "over deze dag niet worden gemaakt. "
     "WAT HET NIET KOST: geen bet en geen kansschatting. Understat staat per ontwerp NAAST het "
     "eigen model in het kalibratieblok en gaat niet in `my_prob` of `prob_sources` (§2, §4). "
     "WAT ER GEBEURT ALS HET BLIJFT: dan is de redundantie waarvoor Understat sinds 31 aug 2026 "
     "bestaat weg, en wordt het kalibratielogboek voor die vijf competities eenarmig. Dat is "
     "verlies aan CONTROLE, niet aan kansinput. Een run repareert een netwerkpolicy niet zelf; "
     "een volgende run ziet hier of dit een dag was of een nieuwe toestand.")

note("api_football", "plan_limited",
     "2 nov (run A): API_FOOTBALL_KEY is niet gezet en dat is een BESLUIT van de gebruiker van "
     "27 september 2026 ('Dat wil ik niet'), geen storing en geen actiepunt (§3). api_check.py "
     "meldt hem feitelijk en dringt niet meer aan. De kanskant kwam vandaag volledig van Fotmob, "
     "want Understat lag eruit. Blijft in de prob_sources-lijsten van coverage.json staan met "
     "status plan_limited, zodat hij meedoet als er ooit toch een plan komt.")

note("pinnacle", "ok",
     "2 nov (run A): Pinnacle stond in de bulk-respons van alle acht competities. 1X2-oordeel "
     "voor ELF van de twaalf duels (Benfica - Alverca niet) met een marge van 3,0 tot 4,2% - "
     "scherper dan de 6 tot 10% van de rest, zoals §3 Stage 5 stap 2 beschrijft. Gemiddelde "
     "absolute afstand van het eigen model tot Pinnacle's de-vigde 1X2: 4,19 pp over elf duels. "
     "Totalenoordeel voor alle twaalf (duel, lijn)-paren, push-gecorrigeerd. "
     "DE GROOTSTE AFWIJKING ZIT OP DE GEPUBLICEERDE UNDER: bij Atalanta - Parma staat de eigen "
     "P(Under 2.75) op 60,6% tegen 45,4% bij Pinnacle, +15,18 pp. De bet staat op Under 3.5 en "
     "niet op 2,75, maar de richting is dezelfde en het is de scherpste bookmaker van de markt "
     "die het tegenspreekt. Noteer dat naast de bet en niet erin (§2): Pinnacle is andermans "
     "oordeel, geen kansinput.")

note("settling", "ok",
     "2 nov (run A): settling.DayIndex besliste over tien openstaande picks en 56 schaduwrijen op "
     "de status van de bron en niet op de klok. Acht picks en 53 schaduwrijen afgewikkeld; drie "
     "rijen bleven open omdat de bron ze als nog niet afgelopen meldt (Los Angeles FC - Minnesota "
     "United en Portland Timbers - Houston Dynamo, beide ongeveer een half uur onderweg bij de "
     "eerste aanroep, plus de schaduwrij Tenerife - FC Andorra). Dat is precies waarvoor de "
     "statusregel van §0 is gemaakt: een klok van twee uur na de aftrap zou die twee MLS-duels "
     "als afgelopen hebben geboekt. Alle afgewikkelde duels stonden op reason 'Full-Time', dus "
     "geen verlenging of strafschoppen om tot 90' terug te rekenen.")

note("toplist_dagranglijst", "gerepareerd",
     "2 nov (run A): `scripts/toplist.py` liet de dagranglijst van §5b een selectie die haar "
     "eigen lat NIET haalt een selectie verdringen die hem WEL haalt, en dat raakte vandaag een "
     "gepubliceerde bet. TWEE FOUTEN OP ELKAAR. (1) `_cut` toetste `if len(boven) > n`: met "
     "precies `MAX_SHORTLIST` selecties boven hun lat (vandaag drie, en n = 3) was dat onwaar en "
     "werd de lijst puur op selection_score gevuld. Ook bij MINDER dan n boven de lat kon een "
     "gekwalificeerde selectie volledig uit de lijst vallen zodra er genoeg hoger scorende "
     "kandidaten onder hun lat stonden. Gerepareerd als ORDENING (boven de lat eerst, de rest "
     "vult aan) en niet als `>=`, want de grens was niet het hele probleem. (2) De keuze BINNEN "
     "een wedstrijd liep uiteen met de analyse: `build` koos per duel de hoogste score onder alle "
     "publiceerbare selecties, dus ook onder de lat. Bij Zaglebie Lubin - Korona Kielce koos de "
     "analyse het 1X2 (+8,18 pp, score 3,780, lat gehaald) en toplist de DNB (+6,50 pp, score "
     "3,968, lat niet gehaald) - twee rapporten van dezelfde run die een andere bet noemen - en "
     "die sub-lat-DNB viel daarna op fout (1) uit de lijst. Vergelijkt nu op (lat gehaald, score). "
     "WAT HET VANDAAG VERANDERDE: de derde regel van de lijst, van Sassuolo - Fiorentina Under "
     "3.5 @1,64 (+7,39 pp) naar Zaglebie Lubin - Korona Kielce 1 @2,63 (+8,18 pp). Sassuolo gaat "
     "als near_miss met failed_gate = edge naar het schaduwlogboek. Bewijs: "
     "tmp-run/ra_nov02_toplist_fix_test.py, vijf gevallen zonder netwerk.")

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)

H["last_run"] = {"run": "A", "date": "2026-11-02", "note": (
    "TWAALF duels in het inzetvenster over ACHT competities, tegen een maandagcap van 40 - niets "
    "afgekapt, alle twaalf doorgerekend, 10 op FULL en 2 op LIGHT (omgerekende promovendi), geen "
    "enkele op NONE. Bundesliga, Championship, Eredivisie, Belgian Pro League en Scottish "
    "Premiership hebben geen ronde, de drie Europese toernooien spelen woensdag en donderdag en "
    "geen van de vijf bekers heeft een ronde; dat is bij TWEE bronnen nagetrokken en die zijn het "
    "over alle zestien competities eens (12 tegen 12). "
    "EEN BRONSTORING: Understat onbereikbaar met een 502 op de CONNECT van de netwerkgateway, "
    "voor alle vier de gedekte competities die vandaag spelen. Dat raakt het kalibratieblok van "
    "§6e en geen enkele bet (§2). Fotmob, The Odds API, BetExplorer en Pinnacle leverden zonder "
    "fout. 34 van 342 credits (24 bulk + 10 BTTS), 19859 over. "
    "DRIE REGELS GEPUBLICEERD EN ALLE DRIE HALEN HUN EIGEN LAT - sinds §5b van 20 september is "
    "dat uitzondering en geen regel: Atalanta - Parma Under 3.5 @1,55 (+14,80 pp tegen de "
    "verzwaarde lat van 10,0 van poort 9), Radomiak Radom - Slask Wroclaw 1 @2,2152 (+18,22 pp "
    "tegen de LIGHT-lat van 16,0; Betfair, beurs, 2,24 bruto) en Zaglebie Lubin - Korona Kielce 1 "
    "@2,63 (+8,18 pp tegen de FULL-lat van 8,0). Bij alle drie bet_beide = true. "
    "DE BEVINDING IS EEN REPARATIE IN toplist.py: de dagranglijst verdrong een gekwalificeerde "
    "bet ten gunste van een selectie die haar lat niet haalt, en de keuze binnen een wedstrijd "
    "liep uiteen met de analyse zelf. Zonder die reparatie zou de derde regel vandaag Sassuolo - "
    "Fiorentina Under 3.5 @1,64 (+7,39 pp) zijn geweest in plaats van Zaglebie Lubin. "
    "POORT 9 HAALT ZIJN MEETLAT: de reeks doelpunten_onder staat op 35 afgewikkelde kandidaten "
    "met -30,4% rendement, boven de ~30 die §6d eist. De rem doet zijn werk en blijft staan; over "
    "LIGHT zegt die meting niets. tweede_methode vangt 121 van de 173 doorgerekende selecties "
    "(70%), de vierde dag op rij rond de zeventig procent. "
    "STAGE 0: 8 picks afgewikkeld (4 gewonnen, 4 verloren) en 53 schaduwrijen (22 gewonnen, 30 "
    "verloren, 1 void).")}
H["last_run_bevinding"] = (
    "De dagranglijst van §5b kon een gekwalificeerde bet stil laten verdwijnen. `toplist._cut` "
    "toetste `len(boven) > n` in plaats van de lat als ordening te gebruiken, en `build` koos "
    "binnen een wedstrijd op score alleen in plaats van op (lat gehaald, score). Het faalde stil: "
    "de lijst had precies de juiste lengte, elke regel droeg netjes zijn eigen label, en het enige "
    "dat niet klopte was dat de analyse en de ranglijst van dezelfde run een andere bet noemden. "
    "Dezelfde faalvorm als calibration.py settle (§6b-5c), het Serie B-id en promotion.match_tier. "
    "Beide fouten gerepareerd, met vijf controles in tmp-run/ra_nov02_toplist_fix_test.py.")
H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

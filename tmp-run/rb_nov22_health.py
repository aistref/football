"""Run B, 22 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Zes dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **Een zondag met 44 duels in veertien van de zeventien competities**; de cap van 55 bindt niet.
2. **Twee naamkoppelingen in `scripts/teamnames.py` gerepareerd** — `fk` ontbrak in `_DROP` en
   BetExplorer schrijft Zbrojovka Brno kaal als "Brno". Samen kostten ze Pardubice – FC Zbrojovka
   Brno al zijn prijzen, in een competitie waar BetExplorer de enige 1X2-bron is.
3. **De vierde gepubliceerde regel is een FULL-Under onder de 8,0 pp**, dus door poort 9 niet
   getoetst: die rem bindt alleen tussen 8,0 en 10,0. Dat is de FULL-tegenhanger van het
   LIGHT-geval van 12 oktober en het is een gat in de opzet, niet in deze run.
4. **De Under-kant van de SELECTIE staat op z = +4,89** over 144 gespeelde Unders, de scherpste
   stand die `margins.py goalbias` ooit heeft gegeven; het MODEL staat op z = +0,56 over 2368.
5. **Pinnacle is het met beide bovenste regels het hardst van de dag oneens.**
6. **30 van de 44 duels vallen uit het contextlogboek** (`squad_value = 0` aan minstens één kant),
   14 geboekt. Geen bronfout maar een meting die niet bestaat.
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
    print(f"{key:30} {status:28} {detail[:80]}")


note("fotmob", "ok",
     "22 nov (run B): daglijsten 22 en 23 nov opgehaald (381 en 91 wedstrijden); idcheck.py gaf "
     "voor alle 33 fotmob_id's uit coverage.json een bruikbare stand, afsluitcode 0 - Serie B "
     "staat op het echte id 86 met 20 ploegen. Standen van alle VEERTIEN spelende competities "
     "geleverd, beide seizoenen. VIER VAN DE VIJF COMPETITIES ZONDER xG SPELEN VANDAAG en dat is "
     "de bekende, vastgelegde stand, geen storing: Czech First League (122), Croatian HNL (252), "
     "Hungarian NB I (212) en Romanian SuperLiga (189) staan in coverage.json met xG=False; de "
     "vijfde (Keuken Kampioen Divisie, 111) speelt niet. Die vier leveren 10 van de 44 duels en "
     "komen altijd op LIGHT uit (lat 16,0 pp). Context voor 43 van de 44 duels in één keer "
     "opgehaald; Nyíregyháza Spartacus FC - Debrecen gaf RemoteDisconnected en slaagde bij de "
     "tweede poging, dus er is geen duel zonder contextblok. context.check_venue SLOEG EEN KEER "
     "AAN: Chicago Fire FC - Charlotte FC wordt gespeeld in SeatGeek Stadium (Bridgeview, "
     "Illinois) en niet in Soldier Field. DERTIG VAN DE 44 DUELS HEBBEN AAN MINSTENS EEN KANT "
     "squad_value = 0 en vallen daardoor uit het contextlogboek: 14 van de 44 geboekt, 68% valt "
     "weg. Dat is geen bronfout maar een meting die niet bestaat - Fotmob noteert voor veel "
     "ploegen in deze runlijst geen marktwaarden, en vandaag raakt dat ELKE spelende competitie "
     "behalve Serie A (BRA) en de Greek Super League gedeeltelijk. Op 21 nov was het 26 van 71 "
     "(37%), vandaag 68%: dit is de kant van deze runlijst die het contextlogboek van Sec. 1c "
     "structureel klein houdt. lineupType: 4 'predicted', 13 'lastStarting11', geen enkele "
     "'confirmed' - te verwachten bij een run die om 04:20 NL de prijzen uitleest en aftrappen "
     "van 13:00 tot 02:30 NL. Voorbeschouwingsblokken (preview.py) voor alle vier de bets zonder "
     "fout, en marketform.match_block voor 36 duels zonder fout.")

note("the_odds_api", "ok",
     "22 nov (run B): api_check.py meldt OK, 46 actieve voetbalcompetities, quota 19.123 over en "
     "877 gebruikt deze maand bij het begin van de run. 33 van de 34 sportkeys van de repo "
     "actief; de uitzondering is Coppa Italia (soccer_italy_coppa_italia), een Run A-toernooi dat "
     "vandaag niet speelt. VIJF ACTIEVE SPORTKEYS DIE DE REPO NIET KENT: soccer_brazil_serie_b, "
     "soccer_england_efl_trophy, soccer_germany_bundesliga_women, soccer_germany_liga3 en "
     "soccer_uefa_nations_league. Geen van die vijf staat op een runlijst, dus het is geen gat; "
     "soccer_brazil_serie_b is wel de divisie waarvoor Sec. 4 GEEN gemeten promotiefactor heeft, "
     "en dat is de reden dat Athletico Paranaense - Remo vandaag op NONE komt. TIEN VAN DE "
     "VEERTIEN spelende competities hebben een sportkey en kregen elk één gebundelde aanroep "
     "(h2h+spreads+totals, 3 credits), daarna 21 losse BTTS-aanroepen voor de duels met een "
     "kandidaat-edge: 51 van een plafond van 1061 credits, 19.072 over. De vier zonder sportkey "
     "(dezelfde vier zonder xG) draaien op het gratis BetExplorer-marktgemiddelde. De "
     "marktbalans-controle van Sec. 1a is gehaald op de inkoop en met ruime marge: alle tien de "
     "inkoopbare competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt.")

note("betexplorer", "ok",
     "22 nov (run B): fixturepagina's van alle zeventien competities geleverd, samen 130 rijen "
     "met koers. De bevestigingspoort van Sec. 1 is op ALLE ZEVENTIEN eens: 44 duels bij Fotmob "
     "tegen 44 bij BetExplorer, per competitie gelijk, inclusief de drie competities die vandaag "
     "GEEN WEDSTRIJD hebben (English League One, English League Two, Keuken Kampioen Divisie - 0 "
     "tegen 0). De reparatie van de datumdoorschuiving van 21 nov houdt stand. LET OP DE DUNNE "
     "KANT VAN DEZE BRON: bij Nyíregyháza Spartacus FC - Debrecen, de enige LIGHT-regel van "
     "vandaag, is het marktgemiddelde over MAAR DRIE BOEKEN berekend. Dat is de dunste prijsbasis "
     "van de vier gepubliceerde regels en het staat als zodanig bij de bet.")

note("teamnames", "gerepareerd",
     "22 nov (run B): TWEE KOPPELINGEN GEREPAREERD IN scripts/teamnames.py, en samen kostten ze "
     "Pardubice - FC Zbrojovka Brno al zijn prijzen (nul doorgerekende markten bij de eerste "
     "analyse, 'geen prijzen gevonden', terwijl vijftien boeken een 1X2 noteerden). (1) `fk` "
     "stond NIET in _DROP terwijl fc, afc, sc, ac en as er vanaf het begin in staan: BetExplorer "
     "schrijft 'FK Pardubice', Fotmob 'Pardubice', en zonder die regel is dat {pardubice} tegen "
     "{fk, pardubice} - geen gelijkheid, dus is_abbreviation wijst het af. FK is in Tsjechie, "
     "Slowakije, Scandinavie en de Balkan net zo'n ruiswoord als FC in West-Europa. (2) "
     "BetExplorer laat de clubnaam weg en houdt de stad over: 'Brno' voor FC Zbrojovka Brno, "
     "terwijl er dit seizoen TWEE Brno-clubs in de Chance Liga staan (Artis Brno is de andere). "
     "Alleen de kale stad kreeg een alias; Artis Brno koppelt op zijn eigen genormaliseerde naam "
     "en wordt niet geraakt. In een competitie zonder sportkey is het BetExplorer-gemiddelde de "
     "ENIGE 1X2-bron, dus dit kostte drie dingen tegelijk: geen enkele markt doorgerekend, een "
     "leeg kalibratieblok (Sec. 6e) en poort 8 die opengaat op 'geen marktoordeel over wie de "
     "mindere is' zonder te zijn getoetst. Dezelfde stille faalstand als 'LA Galaxy' op 17 okt. "
     "NAGELOPEN OP BOTSINGEN over alle 33 competities uit coverage.json, beide seizoenen: er zijn "
     "elf botsingen en GEEN ervan komt van `fk`. Het zijn Manchester City tegen Manchester United "
     "(Premier League, Champions League) en Dundee United tegen Dundee FC (Scottish "
     "Premiership), die al botsten omdat 'city' en 'united' in _DROP staan. Ze zijn onschadelijk "
     "omdat resolve alleen koppelt bij precies EEN treffer - bij twee kandidaten geeft hij None - "
     "maar ze staan op de runlijst van Run A en horen daar opgeschreven te blijven. Verder viel "
     "de koppeling vandaag een paar keer terug op de genormaliseerde naam bij de "
     "Pinnacle-vergelijking (Levadiakos, Olympiacos, PAOK, KFUM, Kristiansund, Sarpsborg, Hacken, "
     "Sirius, Cordoba, Kaiserslautern, Lausanne, Altach, Austria Wien), alle met de juiste "
     "wedstrijd.")

note("understat", "niet_bevraagd",
     "22 nov (run B): niet opgevraagd. Understat dekt vijf competities (EPL, La Liga, Bundesliga, "
     "Serie A, Ligue 1) en geen enkele daarvan staat op de runlijst van Run B. Dat is geen "
     "storing en geen gat: de kanskant van deze runlijst komt van Fotmob.")

note("api_football", "niet_gezet",
     "22 nov (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker van 27 sep "
     "2026 en GEEN gat, geen actiepunt en niets voor de notificatie (Sec. 3). Alleen boekhouding: "
     "de kanskant komt van Fotmob (alle competities) en Understat (vijf, vandaag geen). De "
     "sleutel wordt pas een echt probleem zodra Fotmob niet meer levert; vandaag levert Fotmob "
     "alles.")

note("settling", "ok",
     "22 nov (run B): ledger.py open gaf vier picks met 'bron meldt nog niet afgelopen' en nul "
     "klaar om af te wikkelen - alle vier zijn de picks die Run A vanmorgen voor vandaag heeft "
     "gepubliceerd, met aftrappen die nog twaalf tot zeventien uur weg liggen. Geen enkele "
     "openstaande pick van voor de rundag, dus er is niets blijven liggen; Run A heeft vanmorgen "
     "10 picks en 93 schaduwrijen van 21 nov afgewikkeld. shadow.py open gaf hetzelfde beeld voor "
     "de zeven schaduwrijen van Run A van vandaag. calibration.py settle: 0 afgewikkeld, 8784 van "
     "8913 compleet, 129 open (de duels van vandaag en gisteravond). ctxlog.py settle: 0 "
     "afgewikkeld, 38 open. recalibrate.load_fit().fitted_through = 2026-11-21, oftewel de vorige "
     "rundag - de controle van Sec. 6b-5c is dus gehaald.")

note("poort_9_doelpunten_onder", "reeks_52_rem_werkt_maar_vangt_vandaag_niets",
     "22 nov (run B): de reeks `doelpunten_onder` staat op 52 kandidaten, 50 afgewikkeld, 18 "
     "winnaars (36,0%) en -33,3% rendement. De rem bespaart dus geld en de reeks heeft de ~30 van "
     "Sec. 6d gehaald. VANDAAG HIELD DE POORT NUL SELECTIES TEGEN, EN DAT IS JUIST HET PUNT: de "
     "vierde gepubliceerde regel is Basel - Luzern, Under 3.5 @1,95 op FULL met +7,58 pp, en die "
     "valt ONDER de gewone drempel van 8,0 - unders.check geeft daar zelf passed=True op terug, "
     "want de poort bindt uitsluitend in de band tussen 8,0 en de verzwaarde lat van 10,0. Sinds "
     "Sec. 5b de drempel van poort naar afkapping heeft gemaakt (20 sep 2026) kan zo'n selectie "
     "op rangorde gepubliceerd worden, en dan is er NIETS dat de Under-kant toetst. Dat is "
     "dezelfde constructie als Atalanta - Venezia op 12 oktober (toen op LIGHT, dat met opzet "
     "buiten de poort valt), nu voor het eerst op FULL. EEN RUN VERZET DEZE POORT NIET OP EIGEN "
     "INITIATIEF (Sec. 1h, stand 2 nov 2026) en ook Sec. 5b niet: de vraag staat in het "
     "dagrapport onder 'Wat er nog moet gebeuren' met owner = besluit.")

note("pinnacle_vergelijking", "let_op",
     "22 nov (run B): 27 toetsbare duels op de 1X2 en 27 (duel, lijn)-paren op de Over/Under. Op "
     "de 1X2 is de gemiddelde absolute afstand tot het de-vigde Pinnacle-oordeel 3,91 pp bij een "
     "gemiddelde Pinnacle-marge van 3,82%. BEIDE BOVENSTE REGELS VAN VANDAAG ZIJN DE GROOTSTE "
     "AFWIJKING IN HUN EIGEN MARKT. Levadiakos - Atromitos: eigen model 49,2% voor de thuiszege "
     "tegen 37,0% bij Pinnacle, +12,16 pp, de tweede grootste van de 27 (alleen Brommapojkarna - "
     "Halmstads BK staat verder op +16,85 pp, en die sneuvelde op poort 5). Wolfsberger AC - "
     "Ried: op lijn 3,00 geeft het eigen model P(Under) 40,5% tegen 53,1% bij Pinnacle, oftewel "
     "12,57 pp MEER kans op doelpunten dan de scherpste bookmaker van de markt bij een marge van "
     "3,0% - de grootste van alle 27 paren. Basel - Luzern staat op lijn 3,50 +3,84 pp boven "
     "Pinnacle op de Under-kant. Bij Nyiregyhaza - Debrecen heeft Pinnacle niets, want de "
     "Hongaarse competitie heeft geen sportkey. Over de hele doelpuntenkant: gemiddeld +0,77 pp "
     "op de Under-kant met 16 van 27 erboven; uitgesplitst +3,41 pp op de zes zuivere halve "
     "lijnen (6 van 6 erboven) en +0,02 pp op de 21 met push. DEZE GETALLEN GAAN NIET IN my_prob "
     "(Sec. 2).")

note("goalbias_selectie", "scherpste_stand_ooit",
     "22 nov (run B): margins.py goalbias staat op 2368 doorgerekende duels van 25 aug t/m 21 "
     "nov. Het MODEL staat op +0,020 doelpunt per duel (z = +0,56): de lambdas kloppen. De "
     "SELECTIE niet - over de 144 duels waar werkelijk een Under is gespeeld vielen er 0,677 "
     "doelpunt per duel MEER dan verwacht (z = +4,89), de scherpste stand die deze meting ooit "
     "heeft gegeven (21 nov: +4,74 over 139). De spiegel staat er ook: over de 78 gespeelde Overs "
     "vielen er 0,318 doelpunt per duel MINDER dan verwacht (z = -1,53, dus nog ruis bij deze "
     "aantallen). Beide gepubliceerde doelpuntenregels van vandaag staan dus op een kant waar de "
     "selectie tot nu toe de verkeerde kant op uitvalt: Wolfsberger AC Over 2.5 en Basel - Luzern "
     "Under 3.5. Deze twee regels mogen NOOIT bij elkaar worden opgeteld en geen van beide is een "
     "reden om op een enkele dag een lat te verzetten (Sec. 6d).")

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print(f"\n{len(S)} bronnen in data/source-health.json")

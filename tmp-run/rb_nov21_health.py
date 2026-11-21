"""Run B, 21 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Zes dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **De volle zaterdag is terug**: alle zeventien competities spelen, 71 duels in het venster, en
   de cap bindt voor het eerst sinds 24 oktober — 55 doorgerekend, 16 afgekapt.
2. **Een parserfout in `betexplorer.fetch_league_fixtures` is gerepareerd.** De doorschuiving van
   een lege tijdcel liep alleen over rijen MET koers, waardoor NAC Breda – Den Bosch (werkelijk
   27 nov) op "Today 16:30" kwam en de bevestigingspoort van §1 naar een spookduel wees.
3. **De Under-kant van de SELECTIE staat op z = +4,74** (139 gespeelde Unders, +0,668 doelpunt per
   duel boven de eigen lambda) terwijl het MODEL op z = +0,71 staat over 2266 duels. Dat is de
   scherpste stand die `margins.py goalbias` ooit heeft gegeven, en VIER van de vijf bets van
   vandaag staan op die kant.
4. **Pinnacle is het met alle vier die regels oneens**, en met drie ervan het hardst van de dag.
5. **26 van de 71 duels vallen uit het contextlogboek** (`squad_value = 0` aan minstens één kant),
   45 geboekt. Geen bronfout maar een meting die niet bestaat — en op deze runlijst veel groter dan
   op de hoogste divisies.
6. **Veertien duels komen op `NONE` uit langs de omrekening van §4**, waarvan acht binnen de cap.
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
     "21 nov (run B): daglijsten 21 en 22 nov opgehaald; idcheck.py gaf voor alle 33 fotmob_id's "
     "uit coverage.json een bruikbare stand, afsluitcode 0 - Serie B staat op het echte id 86 met "
     "20 ploegen. Standen van ALLE ZEVENTIEN spelende competities geleverd, beide seizoenen. VIJF "
     "VAN DE ZEVENTIEN HEBBEN GEEN xG EN DAT IS DE BEKENDE, VASTGELEGDE STAND, geen storing: Czech "
     "First League (122), Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189) en "
     "Keuken Kampioen Divisie (111) staan in coverage.json met xG=False en idcheck.py bevestigt dat "
     "per competitie. Die vijf leveren 14 van de 71 duels en komen altijd op LIGHT uit (lat 16,0 "
     "pp). Context voor alle 71 duels opgehaald zonder enkele fout; context.check_venue sloeg "
     "NERGENS aan (relocated = False overal). ZESENTWINTIG VAN DE 71 DUELS HEBBEN AAN MINSTENS EEN "
     "KANT squad_value = 0 en vallen daardoor uit het contextlogboek: 45 van de 71 geboekt. Dat is "
     "geen bronfout maar een meting die niet bestaat - Fotmob noteert voor veel ploegen in de "
     "Tsjechische, Kroatische, Hongaarse en Roemeense competitie, de Engelse League One/Two en de "
     "Duitse 2. Bundesliga geen marktwaarden. Op 20 nov waren het er 2 van 17 (de Jong-ploegen); op "
     "deze volle zaterdag is het 37% van de run, en dat is de kant van deze runlijst die het "
     "contextlogboek van §1c structureel klein houdt. lineupType: geen enkele 'confirmed' - te "
     "verwachten bij een run die om 04:30 NL de prijzen uitleest en aftrappen van 13:00 tot 01:00 "
     "NL. Voorbeschouwingsblokken (preview.py) voor alle vijf de bets zonder fout, en "
     "marketform.match_block voor 57 duels zonder fout.")

note("the_odds_api", "ok",
     "21 nov (run B): api_check.py meldt OK, 47 actieve voetbalcompetities, quota 19.250 over en "
     "750 gebruikt deze maand bij het begin van de run. 33 van de 34 sportkeys van de repo actief; "
     "de uitzondering is Coppa Italia (soccer_italy_coppa_italia), een Run A-toernooi dat vandaag "
     "niet speelt. VIJF ACTIEVE SPORTKEYS DIE DE REPO NIET KENT: soccer_brazil_serie_b, "
     "soccer_germany_bundesliga_women, soccer_germany_liga3, soccer_sweden_superettan en "
     "soccer_uefa_nations_league. Geen van die vijf staat op een runlijst, dus het is geen gat; "
     "soccer_brazil_serie_b is wel de divisie waarvoor §4 géén gemeten promotiefactor heeft, en "
     "dat is de reden dat twee Braziliaanse duels vandaag op NONE komen. TWAALF VAN DE ZEVENTIEN "
     "spelende competities hebben een sportkey en kregen elk één gebundelde aanroep "
     "(h2h+spreads+totals, 3 credits), daarna 29 losse BTTS-aanroepen voor de duels met een "
     "kandidaat-edge: 65 van een plafond van 961 credits, 19.185 over. De vijf zonder sportkey "
     "(dezelfde vijf zonder xG) draaien op het gratis BetExplorer-marktgemiddelde.")

note("betexplorer", "ok",
     "21 nov (run B): fixturepagina's van alle zeventien competities geleverd, samen 169 rijen met "
     "koers. NA EEN REPARATIE IN scripts/betexplorer.py IS DE BEVESTIGINGSPOORT VAN §1 OP ALLE "
     "ZEVENTIEN EENS: 71 duels bij Fotmob tegen 71 bij BetExplorer, per competitie gelijk. Vóór de "
     "reparatie was het 16 van 17 en wees de poort bij de Keuken Kampioen Divisie naar NAC Breda - "
     "Den Bosch als duel van vandaag 16:30 UK. Dat duel bestaat vandaag niet: de JSON-LD van "
     "diezelfde pagina zet hem op 27 nov 20:00, en beide ploegen speelden gisteravond nog (Almere "
     "City - NAC 1-4, Den Bosch - VVV 1-0). Zie de notitie `betexplorer_datum_doorschuiving`.")

note("betexplorer_datum_doorschuiving", "gerepareerd",
     "21 nov (run B): fetch_league_fixtures schoof de datum van een rij met een lege tijdcel "
     "(&nbsp;) door vanaf de laatste rij MET drie koersen, in plaats van vanaf de rij direct "
     "erboven - de lus sloeg een koersloze rij over vóórdat `carried` werd bijgewerkt. Op de "
     "fixturepagina van de Eerste Divisie stonden vijf rijen van het 27-novemberblok zonder koers; "
     "de eerste rij daarna MET koers (NAC Breda - Den Bosch) erfde daardoor 'Today 16:30' van FC "
     "Eindhoven - RKC. Gerepareerd door de doorschuiving over ELKE rij met teams te laten lopen en "
     "pas daarna op het aantal koersen te filteren; de koersloze rijen leveren nog steeds geen "
     "MatchOdds op, dus er komt geen rij bij. Na de reparatie geeft dezelfde pagina 5 rijen met de "
     "juiste datums, en de zestien andere competities zijn ongewijzigd (71 tegen 71). TWEE "
     "RICHTINGEN: een spookduel valt op omdat Fotmob het niet heeft, maar een ECHT duel dat zo naar "
     "een andere dag verschuift valt stil uit het venster, en dan meldt de poort 'eens' terwijl er "
     "een wedstrijd mist. Dat is dezelfde stille faalstand als het Serie B-id en als "
     "calibration.py settle.")

note("teamnames", "ok",
     "21 nov (run B): geen enkel duel kwam zonder prijzen binnen. Over 47 doorgerekende duels zijn "
     "582 selecties uit zes markten gevonden; de koppeling viel twee keer terug op de "
     "genormaliseerde naam (Catanzaro - Palermo, Lugano - Grasshopper) en drie keer bij de "
     "Pinnacle-vergelijking, alle vijf met de juiste wedstrijd. De vier aliasregels van 20 nov "
     "(TOP Oss, Roda JC Kerkrade) staan er nog; TOP Oss speelt vandaag niet.")

note("understat", "niet_bevraagd",
     "21 nov (run B): niet opgevraagd. Understat dekt vijf competities (EPL, La Liga, Bundesliga, "
     "Serie A, Ligue 1) en geen enkele daarvan staat op de runlijst van Run B. Dat is geen storing "
     "en geen gat: de kanskant van deze runlijst komt van Fotmob.")

note("api_football", "niet_gezet",
     "21 nov (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker van 27 sep "
     "2026 en GEEN gat, geen actiepunt en niets voor de notificatie (§3). Alleen boekhouding: de "
     "kanskant komt van Fotmob (alle competities) en Understat (vijf, vandaag geen). De sleutel "
     "wordt pas een echt probleem zodra Fotmob niet meer levert; vandaag levert Fotmob alles.")

note("settling", "ok",
     "21 nov (run B): ledger.py open gaf vijf picks met 'bron meldt nog niet afgelopen' en nul "
     "klaar om af te wikkelen - alle vijf zijn de picks die Run A vanmorgen heeft gepubliceerd "
     "voor vandaag. Geen enkele openstaande pick van vóór de rundag, dus er is niets blijven "
     "liggen. shadow.py open gaf hetzelfde beeld voor de schaduwrijen van Run A van vandaag. "
     "calibration.py settle: 0 afgewikkeld, 8481 van 8814 compleet, 333 open (de duels van vandaag "
     "en gisteravond). ctxlog.py settle: 0 afgewikkeld, 89 open.")

note("poort_9_doelpunten_onder", "reeks_47_rem_werkt",
     "21 nov (run B): de reeks `doelpunten_onder` staat op 47 kandidaten, 42 afgewikkeld, 15 "
     "winnaars (35,7%) en -33,1% rendement. De rem bespaart dus geld, en de reeks heeft de ~30 van "
     "§6d gehaald. Vandaag hield de poort ÉÉN selectie tegen (FC Dallas - Portland Timbers, Under "
     "3.5 @1,77 met +8,91 pp, onder de verzwaarde lat van 10,0). De drie gepubliceerde Unders halen "
     "die lat alle drie ruim: +11,35 / +11,08 / +11,85. LIGHT blijft met opzet buiten de poort "
     "(besluit van de gebruiker, 12 okt 2026) en BTTS 'nee' ook (§1h punt 2), dus de "
     "Carrarese-regel is door geen enkele rem op deze kant getoetst. EEN RUN VERZET DEZE POORT NIET "
     "OP EIGEN INITIATIEF (§1h, stand 2 nov 2026): de vraag hoort pas voorgelegd als de reeks duels "
     "van ná 3 november groot genoeg is om te zien wat LEVEL_SCALE met P(Under) heeft gedaan.")

note("pinnacle_vergelijking", "let_op",
     "21 nov (run B): 38 toetsbare (duel, lijn)-paren op de Over/Under en 38 op de 1X2. Op de "
     "Under-kant ligt het eigen model gemiddeld +1,60 pp boven het de-vigde Pinnacle-oordeel, met "
     "23 van de 38 erboven; uitgesplitst +1,35 pp op de negen zuivere halve lijnen en +1,68 pp op "
     "de 29 met push. DE VIER DOELPUNTENREGELS VAN VANDAAG STAAN ALLE VIER BOVEN PINNACLE EN DRIE "
     "ERVAN ZIJN DE GROOTSTE AFWIJKINGEN VAN DE DAG: Modena - Juve Stabia +14,25 pp op lijn 2,75 "
     "(de grootste van de 38), Tromsø - Viking +12,37 pp op lijn 3,25, Palmeiras - Flamengo +11,49 "
     "pp op lijn 2,50 en Carrarese - Virtus Entella +7,05 pp op lijn 2,25. Op de 1X2 is de "
     "gemiddelde absolute afstand 4,21 pp bij een gemiddelde Pinnacle-marge van 3,98%; de grootste "
     "is Palmeiras - Flamengo, waar het eigen model Flamengo 33,2% geeft tegen 49,5% bij Pinnacle "
     "(16,3 pp). Bij HamKam - Fredrikstad heeft Pinnacle geen 1X2. Deze getallen gaan NIET in "
     "my_prob (§2) en veranderen geen enkele pick; ze horen in de vergelijking.")

note("goalbias_selectie", "scherpste_stand_ooit",
     "21 nov (run B): margins.py goalbias scheidt het MODEL van de SELECTIE en die twee mogen nooit "
     "worden opgeteld. Over alle 2266 doorgerekende duels staat het model op +0,026 doelpunt per "
     "duel (z = +0,71): de lambdas kloppen. Over de 139 duels waar werkelijk een Under is gespeeld "
     "staat het op +0,668 doelpunt per duel, z = +4,74 - de scherpste stand die deze meting ooit "
     "heeft gegeven (20 nov: +4,63 over 138; 139 gevallen is ruim boven de ~30 van §6d). De "
     "Over-kant staat op -0,350 over 75 duels (z = -1,65). De vorm van de verdeling is intussen "
     "vlakker dan in oktober: P(Under 2.5) voorspeld 42,4% tegen werkelijk 40,8% (-1,6 pp) en "
     "P(Under 3.0) 63,9% tegen 63,2% (-0,8 pp). DE CONCLUSIE IS DUS NIET 'het model rekent de "
     "Under-kant te hoog' maar 'de routine kiest de Under juist daar waar haar lambda te laag "
     "staat'. Vier van de vijf bets van vandaag staan op die kant. Dit is een MELDING en geen "
     "ingreep: §6d verbiedt een lat te verzetten op grond van één dag, en §1h verbiedt een run om "
     "poort 9 op eigen initiatief te veranderen.")

note("lijstlengte_reeks", "meting loopt - 30 van de 100",
     "21 nov (run B): onveranderd op 30 afgewikkelde gevallen, 15 winnaars, +6,24u = +20,8%. "
     "Vandaag komt er NIETS bij: er zijn exact vijf gekwalificeerde selecties en MAX_SHORTLIST is "
     "op zaterdag 5, dus de lijstlengte bindt niet. De gebruiker kijkt opnieuw bij 100 gevallen "
     "(besluit 18 nov 2026); leg de vraag niet eerder voor. Een run verandert MAX_SHORTLIST nooit "
     "op eigen initiatief.")

note("herijking_fitted_through", "ok",
     "21 nov (run B): recalibrate.load_fit() geeft a=1,0443, b=0,0286 op 8082 afgerekende gevallen "
     "met fitted_through 2026-11-20 - de VORIGE RUNDAG, dus calibration.py settle is niet blijven "
     "liggen (de controle aan dit ene getal, §6b-5c). De fit VERHOOGT een kans over vrijwel de hele "
     "speelbare band (+0,3 pp op 40%, +0,7 op 50%, +1,4 op 70%), dus 'herijkt haalt de lat, dus ruw "
     "ook' is NIET automatisch waar. Vandaag staat bet_beide op False bij TWEE van de vijf regels: "
     "Modena (ruw +9,98 tegen +11,35 herijkt) en Tromsø (+9,76 tegen +11,08). Beide blijven boven "
     "de 8,0 op de ruwe schaal, dus de vlag is hier een waarschuwing en geen blokkade; dat is "
     "precies waarvoor hij bestaat (§5a). Over de hele run zijn er NUL selecties die alleen op §1g "
     "sneuvelden, dus de reeks `herijking` groeit vandaag niet.")

note("cap_afkapping", "bindt_voor_het_eerst_sinds_24_okt",
     "21 nov (run B): 71 duels op een zaterdagcap van 55 (ranking.max_deep_analyses), dus 16 "
     "afgekapt - de eerste keer sinds 24 oktober dat deze runlijst de cap raakt. De datarijkdom "
     "liep van 4,5 tot 8,0; de laagste die het haalde is Sampdoria - Benevento (5,0) en de hoogste "
     "die afviel Kalamata - AEK Athens (5,0), dezelfde score, dus de grens viel op het aantal "
     "markten en de aftrap en niet op de informatie. TWEE COMPETITIES ZIJN IN HUN GEHEEL AFGEKAPT "
     "en krijgen daarom status AFGEKAPT en niet GEANALYSEERD (Croatian HNL 2 van 2, Greek Super "
     "League 1 van 1); de Czech First League verliest er drie van de vijf en blijft GEANALYSEERD. "
     "De afkapping kost naar rato (§3 Stage 4, meting 5 sep: de betkans is vlak over de rangorde), "
     "dus lees de zestien niet als 'de zwakste zestien'. progress.py verify is groen: 47 "
     "doorgerekende duels met alle zes markten, 14 overgeslagen op tier NONE, 10 op de afkapping.")

note("ondiepe_kloon", "gerepareerd met --unshallow",
     "21 nov (run B): ondiepe kloon (`git rev-parse --is-shallow-repository` = true, 63 commits); "
     "na `git fetch --unshallow origin` 775 commits en 0 van de 95 takken met eigen commits, met "
     "een gewone merge-base met origin/main. HET VALS ALARM VAN §3 STAGE -2 IS VANDAAG EXACT "
     "OPGETREDEN EN HET IS HET VERMELDEN WAARD: op de ondiepe kloon telden 64 van de 95 takken "
     "tussen 1 en 691 'eigen' commits, en dat las als het echte geval van 10 augustus. Wat het "
     "weerlegde nog vóór het unshallowen was de INHOUDELIJKE vergelijking die §3 Stage -2 sinds "
     "27 sep eist: over alle 64 afwijkende takken is geen enkel pick-id gevonden dat main niet "
     "heeft (576 id's), en de schaduwrijen van de nieuwste afwijkende tak waren een deelverzameling "
     "van die van main (1684 tegen 2071 regels, nul regels die main mist). De graafmeting kwam "
     "daarna op hetzelfde uit. Doe dus BEIDE, en doe het unshallowen zoals de regel voorschrijft "
     "vóór je de takken telt, niet erna.")

H["last_run_run_b"] = {
    "run": "B", "date": "2026-11-21",
    "matches_in_window": 71, "analysed": 47, "truncated": 16,
    "bets": 5, "qualified_not_published": 0,
    "credits": ("65 van een plafond van 961 (36 bulk voor 12 competities + 29 BTTS); 19.250 over, "
                "750 gebruikt deze maand bij het begin van de run"),
    "note": (
        "ALLE ZEVENTIEN competities spelen - de eerste volle zaterdag van deze runlijst na het "
        "interlandvenster - met 71 duels in het venster. De cap bindt: 55 doorgerekend, 16 "
        "AFGEKAPT, en van die 55 komen er 8 op NONE uit, dus 47 duels met kandidaten. Op drie "
        "manieren nagetrokken dat de lijst klopt: idcheck.py 33/33 groen met afsluitcode 0, "
        "BetExplorer 17 van 17 eens (71 tegen 71 duels, NA de parserreparatie hieronder), en "
        "runwindow.py - dat bindt vandaag voor één duel, Chapecoense - Cruzeiro op de daglijst van "
        "22 nov met aftrap 01:00 NL. Alle 71 zijn playable. 582 selecties doorgerekend over zes "
        "markten; 444 ervan (76%) sneuvelden op poort 5. VIJF BETS, EN ALLE VIJF HALEN HUN EIGEN "
        "LAT - sinds 8 november niet gebeurd: Modena - Juve Stabia Under 3 @1,68 (+11,35), Tromsø - "
        "Viking Under 3.5 @1,735 (+11,08), Palmeiras - Flamengo Under 2.5 @2,078 (+11,85), "
        "Carrarese - Virtus Entella BTTS nee @1,98 (+9,94) en HamKam - Fredrikstad thuiswinst "
        "@2,5288 (+8,97). Exact MAX_SHORTLIST (5 op zaterdag), dus de lijstlengte bindt niet. "
        "VIER VAN DE VIJF STAAN OP DE KANT 'WEINIG DOELPUNTEN' EN DAT IS DE WAARSCHUWING VAN DEZE "
        "RUN: margins.py goalbias meet de selectie daar op z = +4,74 over 139 gespeelde Unders, de "
        "scherpste stand ooit, terwijl het model zelf op z = +0,71 staat. Pinnacle is het met alle "
        "vier oneens en met drie het hardst van de dag. Een parserfout in "
        "betexplorer.fetch_league_fixtures is gerepareerd (datum-doorschuiving over koersloze "
        "rijen). 26 van de 71 duels vallen uit het contextlogboek op squad_value = 0: 45 geboekt."),
    "history": ([{"date": H["last_run_run_b"].get("date"),
                  "blok": {k: v for k, v in H["last_run_run_b"].items() if k != "history"}}]
                + (H["last_run_run_b"].get("history") or []))[:6],
}

H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt")

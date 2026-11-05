"""Run A, 5 nov 2026 — bronprobe voor source-health.json.

VIJFENDERTIG duels in het inzetvenster over TWEE competities (Europa League 17, Conference League
18), tegen een donderdagcap van 40: niets afgekapt. Negentien competities en alle vijf de bekers
hebben geen ronde, bij twee bronnen nagetrokken.

ALLE 35 DUELS ZIJN KRUIS-GRENS, dus er is vandaag geen enkele FULL en gold de LIGHT-lat van
16,0 pp voor de hele dag. 22 duels halen de omrekening, 13 niet.

GEEN ENKELE BRONSTORING DIE DE RUN RAAKT. Fotmob, The Odds API, BetExplorer en Pinnacle leverden
alle vier zonder fout.

UNDERSTAT IS VOOR DE VIERDE DAG OP RIJ ONBRUIKBAAR, vandaag met hetzelfde symptoom als gisteren:
26.719 bytes zonder JSON op `getLeagueData/EPL/2025`. Twee identieke antwoorden op rij wijzen
eerder op een gewijzigde route dan op een voorbijgaande storing. Het raakt vandaag niets: geen van
de vijf gedekte competities speelt. Zie `understat`.

TWEE DINGEN DIE IN DEZE RUN ZIJN GEVONDEN EN HIER THUISHOREN: een hardgecodeerde datum in het
marktvormscript die stil in het voortgangsbestand van gisteren schreef (zie `marktvorm_dag`,
teruggedraaid voor de commit), en de bevinding dat beide gepubliceerde bets haaks op Pinnacle
staan - bij de bovenste aan de andere kant van de streep. Zie `last_run_bevinding`.
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
     "5 nov (run A): daglijsten 5 en 6 nov opgehaald (37 competities / 96 duels en 92 / 180) en "
     "voor de afwikkeling die van 3, 4 en 5 nov (377 duels geindexeerd). idcheck.py gaf voor alle "
     "33 fotmob_id's uit coverage.json een bruikbare stand. Standen geleverd voor de twee spelende "
     "competities (Europa League id 73, 36 ploegen met xG, en Conference League id 10216, idem) "
     "EN - omdat alle 35 duels kruis-grens zijn - voor de BINNENLANDSE competitie van elke ploeg "
     "afzonderlijk, via scripts/interleague.py. Dat laatste is de zwaarste Fotmob-dag van de week "
     "qua aantal verschillende standen, en er is geen enkele uitgevallen. Context opgehaald voor "
     "alle 35 duels zonder een enkele fout (`ctx_error` is nergens gezet), inclusief de 13 duels "
     "die op NONE uitkwamen - dat is wat §1c eist en het verdrievoudigt de steekproef van "
     "ctxlog.py. De drie bekers met een fotmob_id (League Cup 133, DFB Pokal 209, KNVB Beker 235) "
     "gaven nul duels in het venster.")

note("the_odds_api", "ok",
     "5 nov (run A): api_check.py gaf 19.776 credits over en 224 verbruikt deze maand; 47 actieve "
     "voetbalcompetities, en 28 van de 34 sportkeys van de repo actief. NIET actief: Coppa Italia, "
     "English League One/Two, League One/Two en UEFA CHAMPIONS LEAGUE - die laatste is geen "
     "storing maar de kalender: de UCL speelde GISTEREN en is vandaag uit de actieve lijst, "
     "terwijl Europa en Conference League er juist in staan. Zes actieve sportkeys die de repo "
     "niet kent: Brazil Serie B, Frauen-Bundesliga, 3. Liga, Copa del Rey, Superettan en UEFA "
     "Nations League - geen daarvan staat in de runlijst van Run A. "
     "Bulk-aanroep (h2h + spreads + totals) gelukt voor BEIDE spelende competities, 6 credits; "
     "daarna 19 credits aan BTTS voor de 19 duels met een kandidaat-edge (§1a stap 2). 25 van een "
     "plafond van 379 (`suggest_cap(19776, 26)`), nog 19.751 over. Marktbalans op de inkoop "
     "gehaald: 2 van 2 competities kregen zowel een uitkomst- als een doelpuntenmarkt.")

note("betexplorer", "ok",
     "5 nov (run A): fixturepagina's van alle 16 competities met een slug opgehaald, plus de vijf "
     "bekers. Marktgemiddelde 1X2 geleverd voor de twee spelende competities (17 en 18 rijen, alle "
     "van vandaag) en gebruikt waar het hoort - het kalibratieblok van §6e en poort 8, niet voor "
     "de bet zelf. "
     "ALS TWEEDE BRON IS HIJ HET OVER ALLE 16 COMPETITIES MET FOTMOB EENS: 35 duels tegen 35, "
     "zonder enig verschil, en voor de veertien competities die vandaag niet spelen bevestigt hij "
     "de nul met een eerstvolgende ronde op 7 nov (de tien binnenlandse competities) of 24 nov (de "
     "Champions League). Dat is de controle die Run A op 6 oktober vijf duels kostte toen hij "
     "ontbrak. Voor de vijf bekers idem: FA Cup eerstvolgende ronde morgen 20:30, League Cup "
     "15 dec, Coppa Italia 1 dec, KNVB Beker 1 dec, DFB Pokal 1 dec - alle vijf buiten het "
     "inzetvenster, en dus `GEEN WEDSTRIJD` op twee bronnen en niet op een. "
     "DE TIJDZONE-WAARNEMING VAN 4 NOVEMBER STAAT NOG OPEN en is vandaag opnieuw zichtbaar: "
     "BetExplorer geeft 'Today 18:45' en 'Today 21:00', wat EXACT de NL-klok van Fotmob is "
     "(17:45Z en 20:00Z), terwijl de docstring van het bevestigingsscript UK-tijd aanneemt (NL "
     "-1 uur). Op deze pagina's staat dus CET. Het raakt vandaag niets - de venstertoets snijdt om "
     "07:00 en geen duel komt in de buurt - maar op een dag met een aftrap tussen 07:00 en 08:00 "
     "zou die aanname de tweede bron een duel laten missen. Niet gerepareerd: de aanname hoort per "
     "pagina gemeten te worden, niet per run geraden.")

note("understat", "onbereikbaar",
     "5 nov (run A): VIERDE dag op rij onbruikbaar, en vandaag met HETZELFDE symptoom als "
     "gisteren - `UnderstatError: geen JSON terug van https://understat.com/getLeagueData/EPL/2025 "
     "(26719 bytes)`. De reeks: 1 nov HTTP 502 op de CONNECT van de netwerkgateway, 3 nov "
     "`Connection reset by peer`, 4 nov 26.719 bytes zonder JSON, 5 nov idem. Dat de laatste twee "
     "dagen hetzelfde antwoord geven in exact dezelfde grootte wijst eerder op een permanent "
     "gewijzigde route of een blokkadepagina dan op een storing die voorbijgaat. "
     "HET RAAKT VANDAAG NIETS, en dat is geen geluk maar de kalender: Understat dekt vijf "
     "competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) en geen van die vijf speelt vandaag "
     "- de runlijst levert alleen Europa en Conference League. Er is dus geen duel waarbij de "
     "tweede, onafhankelijke xG-arm is weggevallen en geen kalibratieblok met een lege "
     "`p_xg_understat`. "
     "WAT HET WEL BETEKENT, en dat hoort er vier dagen op rij bij te staan: de redundantie van §4 "
     "staat uit. Valt Fotmob om terwijl dit zo blijft, dan is er voor geen enkele wedstrijd een "
     "kansbron meer, wordt elk duel data_tier = NONE en levert elke run gegarandeerd nul bets "
     "(§3). Fotmob levert vandaag zonder een enkele fout, dus dat is vandaag geen dreiging maar "
     "een enkel punt van falen. "
     "NIET OMZEILD: er is geen headless browser, challenge-solver of proxy op gezet (§3, "
     "'Niet doen').")

note("api_football", "plan_limited",
     "5 nov (run A): API_FOOTBALL_KEY is niet gezet en dat blijft zo. Besluit van de gebruiker van "
     "27 sep 2026 ('Dat wil ik niet') - geen gat, geen actiepunt en niet in de notificatie (§3, "
     "'API_FOOTBALL_KEY komt er niet'). De kanskant komt van Fotmob (alle competities) en "
     "Understat (vijf, vandaag voor de vierde dag onbruikbaar). Dit wordt pas een reele vraag als "
     "Fotmob omvalt; dan hoort het vooraan in de notificatie met de aantekening dat het besluit "
     "van 27 september onder andere omstandigheden is genomen.")

note("pinnacle", "ok",
     "5 nov (run A): 1X2 gevonden voor 19 duels, doelpuntentotalen voor 20 (duel, lijn)-paren. "
     "Gemiddelde Pinnacle-marge 4,31% op het 1X2 (3,03-10,56%) en 2,72-7,86% op de totalen - "
     "opnieuw de scherpste van de dag, al is de spreiding breder dan gisteren omdat er kleine "
     "Europese ploegen bij zitten waar ook Pinnacle ruimer prijst. Gemiddelde absolute afstand "
     "tussen de eigen kansen en het de-vigde Pinnacle-oordeel op het 1X2: 6,62 pp. Op de "
     "Under-kant staat de eigen kans gemiddeld +3,59 pp BOVEN Pinnacle en bij 14 van de 20 "
     "erboven - een brede Under-lean, kleiner dan de +6,02 pp van gisteren maar met hetzelfde "
     "teken. "
     "DIT IS DE BEVINDING VAN DE RUN EN HET IS SCHERPER DAN GISTEREN. Beide gepubliceerde bets "
     "staan op een grote afstand van Pinnacle, en bij de bovenste aan de ANDERE KANT van de "
     "streep: bij FC Midtjylland - Ajax geeft Pinnacle de-vigd 0,366 thuis / 0,244 gelijk / 0,390 "
     "uit en maakt daarmee AJAX de lichte favoriet, terwijl het eigen model op 0,602 (xG) en "
     "0,673 (splits) thuis komt - +23,6 pp op de thuiskant, de grootste van de dag. De twee "
     "bronnen zijn het niet oneens over de GROOTTE van het thuisvoordeel maar over WIE de betere "
     "ploeg is. Bij FC Twente - Pafos staat de eigen P(Under) op de Pinnacle-lijn 3.25 op 0,662 "
     "tegen 0,487 (+17,50 pp), terwijl het model op het 1X2 van datzelfde duel juist LAGER staat "
     "dan Pinnacle (0,570 tegen 0,716 thuis, -14,6 pp): twee verschillen in tegengestelde "
     "richting op een duel. "
     "Harde grens §2: geen van deze getallen gaat in my_prob of prob_sources; ze bepalen de "
     "LEZING en niet de kans. Geen van de twee gepubliceerde koersen komt van Pinnacle zelf, "
     "anders dan gisteren.")

note("settling", "ok",
     "5 nov (run A): 3 picks en 12 schaduwrijen afgewikkeld, alle vijftien van 4 november. Picks "
     "1 gewonnen / 2 verloren / 0 void (gewonnen: Oxford United - Reading 2-0, DNB Oxford; "
     "verloren: AEK Athens - Real Madrid 2-3 op Under 3.75 en PSV Eindhoven - Club Brugge 1-2 op "
     "1X2 PSV). Schaduwrijen 9 gewonnen / 3 verloren. "
     "ALLE VIJFTIEN DUELS WAREN LEAGUE- OF COMPETITIEWEDSTRIJDEN ZONDER VERLENGING (Champions "
     "League-leaguefase, Championship, League One, Serie A BRA), dus `status.scoreStr` IS de stand "
     "na 90 minuten en er hoefden geen doelpuntminuten te worden opgezocht (§0 / §6d). Dat is per "
     "duel nagegaan en niet aangenomen. De `abandoned()`-controle sloeg nul keer aan. "
     "LENS - COMO 1-9 IS APART NAGETROKKEN. Een 1-9 in de Champions League is zo onwaarschijnlijk "
     "dat het eerst als bronfout is behandeld in plaats van overgenomen: de daglijst en het "
     "wedstrijddetail-endpoint geven dezelfde stand, het detail levert de doelpunten per speler "
     "met minuut (Aguilar 65' bij 0-7), `firstExtraHalfStarted` is leeg en `reason.long` is "
     "'Full-Time' - dus het is de stand na 90 minuten. De acht andere UCL-uitslagen van die avond "
     "zijn normaal. Het is ECHT, en het staat hier omdat zo'n uitschieter de doelpuntenmetingen "
     "van §6f en §6g merkbaar raakt. "
     "TWEE RIJEN BLIJVEN TERECHT OPEN, beide Braziliaans: Botafogo - Atletico-MG (pick, Under 3) "
     "stond 1,6 uur na de aftrap en de bron meldde hem nog niet afgelopen; Sao Paulo - Corinthians "
     "(schaduwrij) was in geen van de drie daglijsten te vinden. Ze gaan naar Stage 0 van de "
     "volgende run - dat is de statusregel van §0 die werkt zoals bedoeld. "
     "`calibration.py settle` (45 waarnemingen), `ctxlog.py settle` (18 wedstrijden) en "
     "`shadow.py collect` (6 nieuwe schaduwrijen) zijn alle drie gedraaid; "
     "`recalibrate.load_fit().fitted_through` staat op 2026-11-03.")

note("marktvorm_dag", "gerepareerd",
     "5 nov (run A): het marktvormscript had `DAG` HARDGECODEERD op 2026-11-04 en schreef daarmee "
     "bij de eerste aanroep in het voortgangsbestand van GISTEREN in plaats van dat van vandaag. "
     "Omdat de wedstrijdnamen van vandaag daar niet in voorkomen kwam het op '0 wedstrijden "
     "gezet' uit - een NETTE NUL, dus het script klaagde niet. Alleen het veld "
     "`marktvorm_toegevoegd` van 4 november kreeg de datum van vandaag; de matchblokken van die "
     "dag bleven ongemoeid. Teruggedraaid met `git checkout` voordat er iets gecommit is, datum "
     "gecorrigeerd, opnieuw gedraaid: 22 wedstrijden in het voortgangsbestand van VANDAAG. "
     "Dit is exact de stille faalvorm waar deze repo op meerdere plekken voor waarschuwt (het "
     "Serie B-id, `calibration.py settle`, de verhuisde BetExplorer-slug, de `\\s+` in het "
     "bevestigingsscript): een controle die groen staat omdat ze niets meet. Het is de reden dat "
     "elk overgenomen script op hardgecodeerde datums moet worden nagelopen en niet alleen op zijn "
     "bestandsnamen - de sed-vervanging van `ra_nov04_` naar `ra_nov05_` raakte de bestandsnamen "
     "wel en deze constante niet.")

note("marktvorm_lijn", "ok",
     "5 nov (run A): de reparatie van 4 november (valt de lijn van de bet niet in "
     "`marketform.LINES`, toon dan de naastgelegen getelde lijn) is vandaag niet aangesproken - de "
     "twee gepubliceerde regels staan op Under 3.5 en op een Draw No Bet, en 3.5 staat gewoon in "
     "de tabel. Geen KeyError, geen afbeelding nodig. "
     "WAT DE TELLING VANDAAG WEL LAAT ZIEN IS DAT ZE NIETS KAN ZEGGEN, en dat is zelf de "
     "bevinding: beide bets staan in een EUROPEES TOERNOOI in de league-fase, het lopende "
     "Conference League-seizoen staat op TWEE speeldagen en geen van de vier betrokken ploegen "
     "speelde het toernooi vorig seizoen. Alle acht reeksen komen daarmee op n=1 of n=2 en "
     "`vorig` geeft vier keer 'speelde die competitie niet'. Anders dan op 4 november, toen de "
     "telling bij beide Unders eenduidig TEGEN de bet in wees over drie tot twaalf duels, zegt ze "
     "vandaag niets - twee hoeken naar de bet, twee ertegen, alle vier op een of twee "
     "wedstrijden. Dat is als zodanig opgeschreven in plaats van als steun gelezen (§6d).")

H["last_run_bevinding"] = (
    "BEIDE GEPUBLICEERDE BETS STAAN HAAKS OP HET SCHERPSTE PUBLIEKE OORDEEL, en bij de bovenste "
    "aan de ANDERE KANT van de streep. FC Midtjylland - Ajax: Pinnacle de-vigd 0,366 thuis / "
    "0,244 gelijk / 0,390 uit, dus Pinnacle maakt AJAX de lichte favoriet, terwijl het eigen "
    "model op 0,602 (xG) en 0,673 (splits) thuis komt - +23,6 pp, de grootste afstand van de dag. "
    "Dat is geen verschil over de grootte van het thuisvoordeel maar over wie de betere ploeg is. "
    "FC Twente - Pafos: eigen P(Under) op de Pinnacle-lijn 3.25 staat op 0,662 tegen 0,487 "
    "(+17,50 pp), terwijl het model op het 1X2 van datzelfde duel juist 14,6 pp LAGER staat dan "
    "Pinnacle. §1g zegt het met cijfers: wie selecteert op de grootste edge, selecteert op de "
    "grootste modelfout - en vandaag rust de volledige edge van beide regels op onenigheid met "
    "de scherpste prijs, zonder tweede onafhankelijke bron die die onenigheid steunt. "
    "DE DAG IS BOVENDIEN VOLLEDIG LIGHT: alle 35 duels zijn kruis-grens (Europa en Conference "
    "League), dus ze gaan langs interleague.py en komen per ontwerp op LIGHT uit - er is vandaag "
    "GEEN ENKELE FULL. De lat was daarmee de hele dag 16,0 pp in plaats van 8,0, en dat is de "
    "voornaamste reden dat er van 22 doorgerekende duels maar twee regels overblijven. "
    "EEN VAN DE TWEE STAAT OP DE UNDER-KANT, waar `margins.py goalbias` over 125 gespeelde "
    "gevallen +0,609 doelpunt per duel te weinig meet (z = +4,10) terwijl het model zelf goed "
    "staat (+0,053, z = +1,38 over 2011 duels) - het is de selectie die scheef staat en niet de "
    "lambdas. POORT 9 RAAKT DIE BET NIET omdat `unders.TIERS` (\"FULL\",) is, een besluit van de "
    "gebruiker van 12 oktober en geen omissie; vandaag kan die poort per definitie nergens "
    "bijten. De frequentietelling van §4 kan de bet vandaag niet tegenspreken en ook niet steunen: "
    "de league-fase staat op twee speeldagen en geen van de vier ploegen speelde het toernooi "
    "vorig seizoen, dus alle reeksen zijn n=1 of n=2. "
    "ER IS NIETS AAN EEN KANS, EEN POORT OF EEN DREMPEL VERANDERD. Een eigen kans verlagen omdat "
    "Pinnacle iets anders zegt zou de anti-circulariteitsregel breken (§2), en een run verzet geen "
    "parameter op een enkele dag (§6d). "
    "`MAX_LIGHT_IN_SHORTLIST` = 2 IS VOL MAAR BINDT NIET, anders dan gisteren: er zijn precies "
    "twee gekwalificeerde selecties en beide zijn gepubliceerd, dus "
    "`gekwalificeerd_niet_gepubliceerd` is leeg en er is geen `near_miss` met "
    "`failed_gate = lijstlengte`. 'Grens vol' en 'grens bindt' zijn niet hetzelfde en dat staat "
    "er met zoveel woorden bij.")
H["last_run"] = {
    "run": "A",
    "date": "2026-11-05",
    "note": (
        "VIJFENDERTIG duels in het inzetvenster over TWEE van de eenentwintig competities (Europa "
        "League 17, Conference League 18), tegen een donderdagcap van 40 - niets afgekapt, en de "
        "afkapping is voor het eerst in dagen niet eens in de buurt gekomen. "
        "ALLE 35 ZIJN KRUIS-GRENS, dus er is vandaag GEEN ENKELE FULL: 22 duels komen via "
        "interleague.py op LIGHT uit en 13 op NONE (twaalf omdat een van beide landen minder dan "
        "40 Europese duels in de meting heeft - Kazachstan, Andorra, Finland, Gibraltar, Bosnie, "
        "Georgie, Litouwen, Albanie, Letland, Armenie, Slovenie - en drie omdat de omgerekende "
        "waarde buiten conversion_in_range valt). De lat was daarmee de hele dag 16,0 pp. "
        "NEGENTIEN competities en de VIJF BEKERS hebben geen ronde; dat is bij TWEE bronnen "
        "nagetrokken en die zijn het over alle 16 competities met een slug eens (35 tegen 35), "
        "zonder een enkele afwijking. GEEN ENKELE BRONSTORING die de run raakt: Fotmob, The Odds "
        "API, BetExplorer en Pinnacle leverden alle vier zonder fout; Understat is voor de VIERDE "
        "dag onbruikbaar maar dekt geen van de spelende competities. 25 van 379 credits (6 bulk + "
        "19 BTTS), 19.751 over. "
        "TWEE BETS GEPUBLICEERD UIT TWEE GEKWALIFICEERDE SELECTIES - de LIGHT-grens is vol maar "
        "houdt niets tegen. DE BEVINDING: beide bets staan haaks op Pinnacle, en bij FC "
        "Midtjylland - Ajax zelfs aan de andere kant van de streep (Pinnacle maakt Ajax de lichte "
        "favoriet, het model geeft Midtjylland 60-67%).")}
H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt")

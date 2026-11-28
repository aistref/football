"""Run A, 28 nov 2026 — bronprobe voor source-health.json (§6b-3).

EENENVIJFTIG duels in het inzetvenster over TWAALF competities, tegen een zaterdagcap van 55:
niets afgekapt, maar het scheelt vier duels en dat is het krapst van deze reeks.

GEEN ENKELE BRONSTORING AAN DE KANT VAN DEZE REPO. `store["errors"]` is over de hele run leeg
gebleven en de tweede-bronbevestiging van §1 is het over ALLE 22 competities eens: 51 tegen 51.
De enige bron die niet levert is Understat — TIENDE rundag op rij — en vandaag kostte dat wél
iets, want alle vijf zijn competities speelden, met twintig duels samen.
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
    print(f"{key:34} {status:14} {detail[:70]}")


note("fotmob", "ok",
     "28 nov (run A): daglijsten 28 en 29 nov opgehaald, en voor de afwikkeling die van 27 en 28 "
     "nov. Standen van TWAALF competities over twee seizoenen, alle twaalf met xG in BEIDE "
     "seizoenen. Wedstrijdcontext van ALLE EENENVIJFTIG duels opgehaald ZONDER EEN ENKELE FOUT, "
     "voor de afkapping zoals Stage 4 eist - het grootste aantal van deze reeks. "
     "Marktvormfrequenties via marketform.match_block op alle 51 doorgerekende duels, 0 fouten; "
     "voorbeschouwingsblokken via preview.match_block op de vijf gepubliceerde duels, 0 fouten, "
     "met onderlinge historie voor alle vijf. De statuscontrole voor de afwikkeling liep hier ook "
     "langs: alle 22 openstaande rijen waren binnenlandse competitieduels, dus zonder verlenging "
     "- scoreStr IS daar de stand na 90 minuten (Sec. 6d). ENIGE KANSBRON VAN DEZE RUN, want "
     "Understat ligt voor de tiende rundag eruit; alle 51 duels halen hun tier op Fotmob alleen "
     "(31 FULL, 20 LIGHT, NUL op NONE).")

note("the_odds_api", "ok",
     "28 nov (run A): api_check.py geeft 46 actieve voetbalcompetities en 18809 van 20000 credits "
     "over, 1191 verbruikt deze maand. 33 van de 34 sportkeys van de repo actief; de enige "
     "inactieve is soccer_uefa_europa_conference_league, en die competitie heeft vandaag geen "
     "duel, dus het kost niets. suggest_cap(18809, 3) gaf 3131 en split_budget(3131, 12) gaf "
     "(12, 12), dus de VOLLEDIGE bulk paste voor alle twaalf inkoopbare competities: 36 credits "
     "aan h2h + spreads + totals en 39 aan BTTS voor de 39 duels met een kandidaat-edge (de "
     "vereniging van beide schalen, Sec. 1a 13 sep 2026), samen 75 van 3131. Het plafond bond "
     "nergens. MARKTBALANS-CONTROLE GEHAALD EN ZO RUIM ALS HIJ KAN: twaalf van de twaalf "
     "competities kregen uit dezelfde bulk zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een "
     "doelpuntenmarkt (OU). Vijf actieve sportkeys kent de repo niet (Brazil Serie B, Coupe de "
     "France, 3. Liga, Superettan, Nations League) en geen van de vijf staat op de runlijst van "
     "Run A. De beste prijs levert gemiddeld 6,04 procent meer dan het marktgemiddelde.")

note("betexplorer", "ok",
     "28 nov (run A): fetch_league_fixtures leverde voor alle TWAALF spelende competities een "
     "pagina met het gratis marktgemiddelde over 8 tot 21 rijen, en voor alle 22 competities van "
     "de runlijst de fixturepagina voor de tweede-bronbevestiging. Nul fouten. Dat gemiddelde is "
     "de meetprijs voor het kalibratieblok van Sec. 6e en voor poort 8 (Sec. 1a: gemiddelde om te "
     "METEN, beste prijs om te SPELEN).")

note("understat", "geen_json_tiende_rundag_en_vandaag_met_gevolg",
     "28 nov (run A): TIENDE rundag op rij geen bruikbare JSON. Vandaag kost dat voor het eerst "
     "echt iets: ALLE VIJF de competities die Understat dekt (PL, Serie A, La Liga, Bundesliga, "
     "Ligue 1) spelen vandaag, met TWINTIG duels samen, dus het kalibratieblok van Sec. 6e mist "
     "bij die twintig de p_xg_understat-arm en er is vandaag geen tweede, onafhankelijk "
     "xG-model. DRIE van de vijf gepubliceerde regels staan in die vijf competities. Wat het NIET "
     "raakt: my_prob komt uit Fotmob-xG en Fotmob-splits en verandert hier niet door (Sec. 4, "
     "31 aug 2026 - Understat is redundantie en meting, geen invoer), en Sec. 2 blijft gedekt "
     "zolang Fotmob levert. Het wordt pas een echt probleem als Fotmob OOK omvalt; dan is er geen "
     "onafhankelijke kansinput meer, wordt elk duel NONE en is de betaalde bron een reele vraag "
     "(Sec. 3, punt 3 van het besluit van 27 sep 2026).")

note("goalbias_selectie", "beide_kanten_scheef_en_de_under_kant_is_nu_hard",
     "28 nov (run A): DIT IS DE BEVINDING VAN VANDAAG. margins.py goalbias meet nu op BEIDE "
     "kanten van de doelpuntenmarkt een selectie-effect, en op een ervan is het hard. UNDER "
     "GESPEELD: +0,661 doelpunt per duel over 153 gevallen, z = +4,92 (Sec. 6g noteerde op 11 okt "
     "n = 49 en z = +2,91). OVER GESPEELD: -0,368 over 87 gevallen, z = -1,87 (op 11 okt n = 38 "
     "en z = -0,54, met de conclusie 'op de Over-kant gebeurt dat niet'). Het MODEL staat "
     "daarentegen goed: +0,019 doelpunt per duel over 2521 doorgerekende duels, z = +0,56. Die "
     "twee regels mogen nooit worden opgeteld (de bovenste meet het model, de onderste de "
     "selectie), maar ze wijzen hetzelfde aan: dit is GEEN gerichte vormfout meer zoals Sec. 6g "
     "in oktober beschreef maar een ALGEMENE winner's curse op de doelpuntenas - de routine kiest "
     "aan beide uiteinden juist de duels waar haar lambda de verkeerde kant op staat. Het "
     "rendement beweegt mee: Under -15,2% over 192 picks, Over +6,4% over 114 (was +10,6% over 62 "
     "op 11 okt). NIETS VERZET: poort 9 blijft onveranderd (Sec. 1h, Sec. 6g - een run verzet die "
     "knop nooit op eigen initiatief), de Over-kant krijgt geen eigen lat, en |z| = 1,87 haalt de "
     "lat van deze repo niet. VIER VAN DE VIJF REGELS VAN VANDAAG STAAN OP DEZE MARKT.")

note("niveaucorrectie_meting", "teken_blijft_omgeslagen_nu_op_545_duels",
     "28 nov (run A): de bevinding van 27 november houdt stand op een grotere reeks. gridfit.py "
     "measure op de twee deelpopulaties (tmp-run/ra_nov28_gridfit_na_niveau.txt): op de 1173 "
     "duels van 20 sep t/m 2 nov, ZONDER model.LEVEL_SCALE, staat het gemiddelde totaal op +0,099 "
     "(z = +1,92) en de fout op P(Under 2.5) op -2,38 pp; op de 545 duels van 3 t/m 27 nov, MET "
     "de correctie, op -0,097 (z = -1,22) en +1,94 pp. Het teken is op alle drie de "
     "diagnoseregels omgeslagen en de absolute omvang is vergelijkbaar gebleven: de correctie "
     "heeft de fout GESPIEGELD en niet verkleind. Tweede aanwijzing dezelfde kant op: scale = "
     "1.032 nog een keer toepassen geeft op die 545 duels t = -1,91 tegen t = +0,92 op de 1173 "
     "ervoor. LET OP DE VAL: op de gemengde reeks van 1718 duels die gridfit.py measure STANDAARD "
     "laat zien lijkt alles juist goed (+0,037, z = +0,84), want 545 van die 1718 dragen de "
     "correctie al in zich - precies de populatiemenging waarvoor gridfit.py in zijn eigen kop "
     "waarschuwt, en de reden dat deze knip er is. NIETS VERZET EN DE VRAAG NIET VOORGELEGD: Run "
     "A heeft op 21 nov zelf de lat op 'ruim boven de ~900 duels' gezet en het zijn er 545. "
     "Verwacht in januari. Poort 9 hangt aan hetzelfde besluit.")

note("margekalibratie", "gelijkspel_derde_dag_op_rij_boven_twee_standaardfouten",
     "28 nov (run A): margins.py stats --since 2026-09-20 over 1718 homogene duels heeft precies "
     "EEN cel boven twee standaardfouten en dat is het gelijkspel: voorspeld 23,6% tegen "
     "werkelijk 20,8%, -2,8 pp. Derde dag op rij dezelfde cel. Op de volle reeks (2521 duels, "
     "beide shrink-instellingen door elkaar) is het -1,5 pp en haalt ze de grens niet. Raakt EEN "
     "bet van vandaag: Motherwell - Hibernian is een Draw No Bet, de markt waar het gelijkspel "
     "uit de berekening wordt gedeeld; het effect op de DNB-kans is tweede-orde en niet eenduidig "
     "van teken, maar het is niet nul, en bij een handicap op 0.0 geldt hetzelfde. De kant waar "
     "Sec. 6f oorspronkelijk over ging staat recht: 'favoriet wint met 3 of meer' op -0,9 pp en "
     "'met 4 of meer' op +0,3 pp over 483 duels met een duidelijke favoriet. Dat gat is dicht "
     "sinds de shrink-overstap en blijft dicht.")

note("poort_5_tweede_methode", "vangt_zesenzeventig_procent_weg",
     "28 nov (run A): tweede_methode is de eerste dichte poort bij 564 van de 740 doorgerekende "
     "selecties (76%). Lees het met de volgorde erbij - failed_gate geeft alleen de EERSTE dichte "
     "poort in ORDER en tweede_methode staat vooraan, dus 564 is een BOVENGRENS voor wat de poort "
     "alleen tegenhoudt. Scherper gemeten, en dat is de ONDERGRENS: bij 11 van de 46 duels zonder "
     "bet is tweede_methode de enige poort die bij ALLE kandidaten binnen de koersband dichtstaat. "
     "De overige poorten vangen veel minder: edge 74 selecties, underdog 53, odds 27, en "
     "robuustheid en context elk 6. Tien van de 740 selecties hadden alle negen poorten open. De "
     "reeks staat op 338 afgewikkelde kandidaten en -2,9%: de poort bespaart geld, maar "
     "nauwelijks.")

note("poort_7_context", "hield_een_duel_tegen_en_de_reeks_is_de_overtuigendste_van_negen",
     "28 nov (run A): poort 7 hield EEN van de 51 duels tegen, en het is een duidelijk geval - "
     "Widzew Lodz - Zaglebie Lubin, waar Zaglebie Lubin 62% van zijn selectiewaarde mist tegen "
     "21% bij Widzew Lodz (Marcel Regula terug begin januari 2027, Michal Nalepa en Pawel "
     "Kosmalski beiden twijfelachtig). De reeks context staat op 157 afgewikkelde kandidaten met "
     "-22,0%, de overtuigendste van alle negen poorten. De poort blijft asymmetrisch en grof en "
     "houdt alleen tegen (Sec. 1c).")

note("poort_9_doelpunten_onder", "hield_vandaag_niets_tegen_reeks_op_vierenvijftig",
     "28 nov (run A): poort 9 hield NUL selecties tegen. De enige Under op FULL-data die de "
     "rangorde haalde is Torino - Lazio met +12,59 pp, ruim boven de verzwaarde lat van 10,0 "
     "(unders.UNDER_EXTRA = 2,0 bovenop de 8,0 van Sec. 0). De reeks doelpunten_onder staat op 54 "
     "afgewikkelde kandidaten met -30,7%: van wat de poort tegenhoudt verliest bijna een derde, "
     "dus op WAT HIJ VANGT doet hij zijn werk. Het probleem van vandaag zit in wat er LANGS komt - "
     "zie goalbias_selectie. Blijft onveranderd staan; de vraag hoort pas voorgelegd als de reeks "
     "van na 3 november groot genoeg is (Sec. 1h, Sec. 6g).")

note("herijking_fitted_through", "op_de_vorige_rundag",
     "28 nov (run A): recalibrate.load_fit().fitted_through staat op 2026-11-27, de vorige "
     "rundag, zoals Sec. 6b-5c eist. Dat komt doordat calibration.py settle vandaag in Stage 0 "
     "is gedraaid VOORDAT load_fit() aan de analyse begon: 75 waarnemingen afgewikkeld, 9321 van "
     "9369 compleet, 48 nog open. De fit staat op a=1,037, b=0,024 over 8922 afgerekende gevallen "
     "en VERHOOGT een kans over vrijwel de hele speelbare band (-0,2 pp op 30%, +0,6 op 50%, "
     "+1,2 op 80%). Bij alle vijf de gepubliceerde regels tilt hij de kans op met ongeveer een "
     "procentpunt edge, en bij GEEN van de vijf is dat beslissend: bet_beide is bij ALLE VIJF "
     "waar. Nul selecties over de hele run sneuvelden alleen op Sec. 1g (zonder_herijking leeg), "
     "en nul op de omgekeerde route.")

note("lijstlengte_reeks", "vierendertig_gevallen_en_vandaag_bindt_de_lengte_niet",
     "28 nov (run A): VIJF selecties boven hun eigen lat en VIJF plekken in de zaterdaglijst "
     "(MAX_SHORTLIST = 5 sinds 19 nov 2026), dus de rangorde en de drempel wijzen EXACT dezelfde "
     "lijst aan, er valt niets buiten de lijst en er is vandaag geen enkele "
     "lijstlengte-schaduwrij. In deze reeks ongewoon: sinds Sec. 5b op 20 sep de drempel naar "
     "achteren trok staan op de meeste dagen regels op rangorde die hun eigen lat niet halen. De "
     "reeks staat onveranderd op 34 AFGEWIKKELDE gevallen met +4,60u = +13,5% (16 winnaars). De "
     "gebruiker kijkt bij 100 gevallen opnieuw (besluit 18 nov 2026); de vraag is vandaag NIET "
     "voorgelegd en MAX_SHORTLIST is niet aangeraakt.")

note("divisiekaart_promovendi", "twintig_omrekeningen_over_twaalf_competities_nul_geweigerd",
     "28 nov (run A): TWINTIG van de 51 duels hadden minstens een ploeg die niet in de stand van "
     "2025/2026 staat - het grootste aantal van deze reeks - en ze gingen alle twintig langs "
     "promotion.convert / convert_relegated (Sec. 4). Het komt NIET uit een competitie: alle "
     "TWAALF spelende competities hebben er minstens een, van vier op tien in de Championship tot "
     "twee op drie in de Premier League en de Ekstraklasa. TWEE duels hebben het aan BEIDE "
     "kanten: Paderborn - Schalke 04 (twee promovendi uit de 2. Bundesliga) en Lincoln City - "
     "Wolverhampton Wanderers (een promovendus uit League One tegen een degradant uit de Premier "
     "League, dus de opwaartse EN de neerwaartse tak in een duel). NUL op NONE: "
     "conversion_in_range heeft vandaag niets geweigerd, en dat is bij deze aantallen het "
     "vermelden waard omdat die poort er juist is om te weigeren (de Coventry-val). En nul werd "
     "FULL, want een omgerekende ploeg is dat nooit: 31 FULL en 20 LIGHT. Geen van de vijf bets "
     "komt uit de twintig; de hoogste LIGHT-edge is +14,97 pp (Frosinone - Parma) tegen een lat "
     "van 16,0.")

note("pinnacle_vergelijking", "vier_van_de_vier_vergelijkbare_regels_meer_dan_acht_pp_van_pinnacle",
     "28 nov (run A): Stage 5 stap 2 in de enige vorm die bereikbaar is. Over 48 duels met een "
     "Pinnacle-1X2 wijkt het model gemiddeld 3,93 pp af bij een gemiddelde Pinnacle-marge van "
     "3,61%; over 49 (duel, lijn)-paren totalen ligt het model gemiddeld 2,98 pp ONDER Pinnacle "
     "op de Under-kant (19 van 49 erboven). PER GEPUBLICEERDE REGEL, EN HET IS GEEN GUNSTIG "
     "BEELD: Manchester United - Brentford +14,54 pp MEER doelpunten dan Pinnacle (eigen "
     "P(Under 3.0) 34,8% tegen 49,4%), Hamburger SV - Bayern Munchen +11,50 pp meer, Torino - "
     "Lazio +11,20 pp meer UNDER (60,6% tegen 49,4%, en dat is de kant waar Sec. 6g de schade "
     "meet), Motherwell - Hibernian geeft Motherwell 44,1% waar Pinnacle 35,9% geeft (+8,18 pp). "
     "Bij Vitoria de Guimaraes - Estrela da Amadora noteert Pinnacle geen 1X2 en geen totaal, dus "
     "daar is geen vergelijking. Vier van de vier vergelijkbare regels liggen dus meer dan acht "
     "procentpunt van de scherpste bookmaker af, en Sec. 1g heeft op 552 gevallen gemeten dat de "
     "grootste geclaimde edge het SLECHTSTE rendement geeft. Dit getal gaat niet in my_prob en "
     "niet in prob_sources (Sec. 2, Sec. 4).")

note("cups_grens", "zes_bekers_buiten_de_runlijst_en_geen_van_zes_speelt",
     "28 nov (run A): cups.filter_runlist met de rundag zet FA Cup, League Cup, Coppa Italia, "
     "KNVB Beker, DFB Pokal en Copa del Rey op BUITEN DE RUNLIJST en NIET op GEEN WEDSTRIJD "
     "(Sec. 5 verbiedt dat laatste met zoveel woorden: er wordt gespeeld, het staat alleen niet "
     "op de lijst). Vandaag valt dat samen: nul duels in beide daglijsten voor alle zes. De "
     "eerstvolgende rondes staan op 1 dec (Coppa Italia, DFB Pokal), 4 dec (FA Cup) en 15 dec "
     "(League Cup) en die vallen alle vier nog buiten de lijst; alle zes doen weer mee op "
     "1 januari 2027.")

note("stage_min_2_branchaudit", "drieenhonderd_takken_na_unshallow_nul_eigen_commits_en_main_is_superset",
     "28 nov (run A): ondiepe kloon bij de start (--is-shallow-repository -> true) en VOOR het "
     "unshallowen meldden 90 van de 103 takken 'eigen commits', tot 730 stuks. Dat is het valse "
     "alarm waar Sec. 3 Stage -2 voor waarschuwt. Na git fetch --unshallow origin (main van 57 "
     "naar 806 commits) houden NUL van de 103 takken eigen commits over. DAARNA OP DE INHOUD "
     "VERGELEKEN EN NIET OP DE GRAAF, zoals Stage -2 sinds 27 sep eist: per unieke blobversie van "
     "alle logboeken zijn de record-id's tegen main gelegd - picks.jsonl (609 records, 77 "
     "blobvarianten), shadow.jsonl (2269, 94), context-log.jsonl (2637, 91), calibration.jsonl "
     "(9369, 94) en coverage.json (50 competities, 49 varianten). MAIN IS OP ALLE VIJF EEN "
     "SUPERSET: nul records die main mist. In source-health.json stond EEN sleutel die main niet "
     "heeft, oddspapi, en dat is GEEN verloren meting maar een bewuste verwijdering - commit "
     "f342894, 'OddsPapi-reserve verwijderd na overstap naar 20K-plan' - net als de vier dubbele "
     "schaduwrijen van 7 november die Stage -2 uitdrukkelijk NIET wil laten terugkomen. Niets "
     "gemerged, want er viel niets te mergen. De run staat op main (git push origin HEAD:main, "
     "Sec. 6a), met expliciete toestemming in de scheduler-tekst.")

note("settling", "vijf_picks_en_zeventien_schaduwrijen_vier_van_vijf_gewonnen",
     "28 nov (run A): VIJF picks en ZEVENTIEN schaduwrijen afgewikkeld, alle 22 binnenlandse "
     "competitieduels, dus zonder verlenging - scoreStr IS de stand na 90 minuten (Sec. 6d). "
     "PICKS: VIER GEWONNEN (Alanyaspor - Konyaspor Over 2.5 @2.43 op 1-2, Nottingham Forest - "
     "Chelsea Over 2.5 @1.93 op 3-2, Levante - Racing Santander Over 3.5 @2.10 op 1-3, "
     "Fluminense - Cruzeiro BTTS nee @2.32 op 0-1) en EEN VERLOREN (Leganes - Sabadell Over 2.0 "
     "@1.79 op 0-0). SCHADUW: 9 gewonnen, 7 verloren, 1 void (Jong AZ Alkmaar - TOP Oss, door de "
     "bron als afgelast gemeld). REFLECTIE (Sec. 3 Stage 0): het leerzaamste geval is de "
     "verliezer - bij Leganes - Sabadell verwachtte het model 2,6 doelpunt en er vielen er nul, "
     "en diezelfde wedstrijd hield OOK een schaduwrij op de underdog-kant tegen (Sabadell wint "
     "@3.40) die op 0-0 eveneens verloor, dus daar deed de poort zijn werk op een duel dat de "
     "analyse verkeerd had ingeschat. Het omgekeerde bij Sonderjyske - Brondby IF (1-1): drie "
     "poorten hielden daar elk een kandidaat tegen (herijking, poort 8, poort 9) en alle drie "
     "zouden ze GEWONNEN hebben. Drie van de vier winnende picks waren een Over, de kant die "
     "volgens goalbias_selectie juist terugloopt - een dag is geen reeks (Sec. 6d). Nul rijen "
     "MIS; na de afwikkeling staat er nog een pick open (Real Salt Lake - Vancouver Whitecaps, "
     "nog niet afgetrapt) en een schaduwrij (Columbus Crew - Inter Miami).")

note("contextlogboek_dekking", "helling_voor_het_eerst_aan_de_grens_en_de_richting_is_de_verwachte",
     "28 nov (run A): 51 van de 51 duels met context toegevoegd (nul afgekapt), 27 afgewikkeld, "
     "logboek op 2688 rijen waarvan 2629 afgewikkeld. De helling van de MODELfout tegen het "
     "beschikbaarheidsverschil staat op -11,8 pp per eenheid bij r = -0,042 en t = -1,99, en bij "
     "2629 wedstrijden is alleen een effect vanaf ~11 pp aantoonbaar - dus AAN de grens, en de "
     "richting is de verwachte (een ploeg die meer van zijn selectiewaarde mist doet het slechter "
     "dan het model zegt). De MARKT heeft dezelfde fout maar kleiner: t = -1,60, -9,3 pp per "
     "eenheid. Zet dat naast de meting van 5 sep 2026 (Sec. 1c), waar over 147 wedstrijden "
     "r = -0,007 en t = -0,08 stond en de tabel 4270 wedstrijden becijferde voor een effect van "
     "10 pp: met 2629 wedstrijden is het verband nu zichtbaar en ongeveer zo groot als de "
     "steekproef kan aantonen. NIETS VERZET: poort 7 blijft een REM en geen BIJSTELLING, en "
     "|t| = 1,99 haalt de lat van |t| = 2 net niet - laat staan de lat die deze repo elders "
     "aanhoudt (CREDIBILITY_K op t = +2,11 / +1,71). Tweede dag dat deze reeks iets zegt.")

H["last_run_run_a"] = {
    "date": "2026-11-28", "run": "A", "at": now,
    "matches_in_window": 51, "analysed": 51, "bets": 5, "truncated": 0,
    "qualified_not_published": 0,
    "credits": "36 aan de bulk (h2h + spreads + totals voor twaalf competities, 3 per "
               "competitie) + 39 aan BTTS (39 duels met een kandidaat-edge) = 75 van een plafond "
               "van 3131; 18809 van 20000 over bij de start",
    "artifact": "https://claude.ai/artifact/Nm1Ne8t3KUv2WdM9nsr7te",
    "dagrapport_markdown": "https://github.com/aistref/football/blob/main/runs/"
                           "2026-11-28-run-a.dagrapport.md",
    "sources_deze_run": {
        "fotmob": "ok; daglijsten 28 en 29 nov, standen van 12 competities over twee seizoenen, "
                  "context van alle 51 duels zonder fout, marktvorm op 51, voorbeschouwing op 5",
        "betexplorer": "ok; marktgemiddelde voor alle 12 spelende competities en de "
                       "fixturepagina voor alle 22 (tweede-bronbevestiging 22 van 22)",
        "the_odds_api": "ok; 75 van 3131 credits, 18809 van 20000 over, marktbalans 12 van 12",
        "understat": "geen JSON, TIENDE rundag op rij; vandaag WEL met gevolg, alle vijf zijn "
                     "competities speelden en de p_xg_understat-arm mist twintig duels",
        "api_football": "niet beschikbaar; besluit van de gebruiker 27 sep 2026, geen gat en geen "
                        "actiepunt (Sec. 3 Stage 3)",
        "pinnacle": "ok; 48 duels 1X2 (gem. afstand 3,93 pp) en 49 (duel, lijn)-paren totalen "
                    "(gem. -2,98 pp op P(Under)), gemiddelde marge 3,61 procent",
    },
    "note": "TWAALF van de ZESTIEN competities van de runlijst spelen in het venster "
            "[08:00 NL 28 nov, 08:00 NL 29 nov), samen EENENVIJFTIG duels - de volste Run A-dag "
            "van deze reeks. Championship 10, Bundesliga 5, Ligue 1 5, Scottish Premiership 5, "
            "La Liga 4, Primeira Liga 4, Belgian Pro League 4, Premier League 3, Serie A 3, "
            "Eredivisie 3, Ekstraklasa 3, Super Lig 2. Vier op GEEN WEDSTRIJD (Danish Superliga "
            "plus de drie Europese toernooien, die pas op 8 en 10 dec terugkomen) en de zes "
            "bekers op BUITEN DE RUNLIJST (cups.py, besluit 18/19 nov), geen van zes speelt "
            "werkelijk. Zaterdagcap 55, NIETS AFGEKAPT - het scheelt vier duels en dat is het "
            "krapst van deze reeks; datarijkdom 5,0 tot 8,0. GEEN ENKEL duel op NONE, bij TWINTIG "
            "promovendi-/degradantenomrekeningen die alle twintig binnen het gemeten bereik "
            "bleven. 740 selecties doorgerekend, 10 met alle poorten open; poort 5 ving er 564 "
            "weg (76%), poort 8 achttien, poort 7 een heel duel (Widzew Lodz - Zaglebie Lubin, "
            "62% van de selectiewaarde afwezig) en poort 9 nul. MAX_SHORTLIST is 5 op zaterdag; "
            "VIJF selecties boven hun eigen lat en vijf plekken, dus de lijstlengte bindt niet en "
            "er valt niets buiten de lijst. ALLE VIJF hebben bet_beide = True, dus geen enkele "
            "regel hangt aan de herijking. VIER VAN DE VIJF REGELS ZIJN EEN DOELPUNTENMARKT "
            "(drie Over, een Under) en de vijfde een Draw No Bet - zie goalbias_selectie, de "
            "bevinding van vandaag.",
}
hist = H.get("last_run_run_a_history") or []
H["last_run_run_a_history"] = (hist + [{"date": "2026-11-28", "bets": 5, "matches": 51,
                                        "note": "51 duels in 12 competities, vijf bets, vier "
                                                "ervan een doelpuntenmarkt; de selectie staat op "
                                                "beide kanten van die markt scheef"}])[-8:]
H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")

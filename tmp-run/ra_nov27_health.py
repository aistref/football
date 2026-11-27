"""Run A, 27 nov 2026 — bronprobe voor source-health.json (§6b-3).

VEERTIEN duels in het inzetvenster over TWAALF competities, tegen een vrijdagcap van 55: niets
afgekapt. De binnenlandse competities zijn na een Europese week weer begonnen; de drie Europese
toernooien hebben hun league phase op 25/26 november gesloten.

GEEN ENKELE BRONSTORING AAN DE KANT VAN DEZE REPO. `store["errors"]` is over de hele run leeg
gebleven en de tweede-bronbevestiging van §1 is het over ALLE 22 competities eens: 14 tegen 14.
De enige bron die niet levert is Understat — NEGENDE rundag op rij — en vandaag kostte dat wél
iets, want alle vijf zijn competities speelden.
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
     "27 nov (run A): daglijsten 27 en 28 nov opgehaald (92 competities/157 duels en 150/573), en "
     "voor de afwikkeling die van 26 en 27 nov (234 duels geindexeerd). Standen van TWAALF "
     "competities over twee seizoenen, alle twaalf met xG in BEIDE seizoenen. Wedstrijdcontext "
     "van ALLE VEERTIEN duels opgehaald ZONDER EEN ENKELE FOUT, voor de afkapping zoals Stage 4 "
     "eist. Marktvormfrequenties via marketform.match_block op alle veertien doorgerekende "
     "duels, 0 fouten. Voorbeschouwingsblokken via preview.match_block op de drie gepubliceerde "
     "duels, 0 fouten. De statuscontrole voor de afwikkeling liep hier ook langs: alle 36 "
     "openstaande rijen kwamen uit de league phase van de Europa en Conference League plus twee "
     "binnenlandse duels, dus zonder verlenging - scoreStr IS daar de stand na 90 minuten. "
     "ENIGE KANSBRON VAN DEZE RUN, want Understat ligt eruit; alle veertien duels halen hun "
     "kansinput hier. Dat is sinds 19 nov een enkel punt van falen in plaats van twee (Sec. 4), "
     "en vandaag raakte het voor het eerst echt iets: de vijf Understat-competities speelden "
     "alle vijf. Kost geen credits.")

note("the_odds_api", "ok",
     "27 nov (run A): api_check.py meldt OK, 44 actieve voetbalcompetities, quota 18884 over en "
     "1116 verbruikt deze maand, 32 van 34 sportkeys actief. De twee inactieve zijn "
     "soccer_uefa_europa_league en soccer_uefa_europa_conference_league, en dat is GEEN storing: "
     "beide toernooien sloten hun league phase op 26 november af en hervatten op 10 december, dus "
     "er is geen event om prijzen voor te noteren. Plafond suggest_cap(18884, 4) = 2358; "
     "split_budget(2358, 12) = 12 spreads / 12 totals, dus ALLE TWAALF spelende competities "
     "kregen de VOLLEDIGE bulk-aanroep (h2h + spreads + totals, 3 credits elk = 36). Tweede ronde "
     "BTTS voor de tien duels met een kandidaat-edge: 10 credits. TOTAAL 46 van 2358, 18.838 over "
     "met vier dagen tot de maandwissel. Nul fouten in store['errors']. Vier actieve sportkeys "
     "die de repo niet kent (soccer_brazil_serie_b, soccer_germany_liga3, "
     "soccer_sweden_superettan, soccer_uefa_nations_league) - geen van vier staat op de runlijst "
     "van Run A.")

note("betexplorer", "ok",
     "27 nov (run A): fetch_league_fixtures voor alle 22 competities van de runlijst, inclusief "
     "de vier zonder wedstrijd en de zes bekers. 22 VAN 22 EENS MET FOTMOB, 14 duels tegen 14, en "
     "ook per competitie gelijk. Dat is de bevestiging door een tweede methode van Sec. 1 op de "
     "vraag WELKE wedstrijden er zijn, en het is voor het eerst sinds 20 november op ALLE 22 "
     "competities gesloten. Levert daarnaast het gratis 1X2-marktgemiddelde voor het "
     "kalibratieblok van Sec. 6e en voor poort 8 (6 tot 22 rijen per competitie).")

note("betexplorer_slugs", "ok",
     "27 nov (run A): HET GAT DAT RUN A OP 26 NOVEMBER MELDDE BESTAAT NIET. Die run schreef dat "
     "er voor de Primeira Liga (POR) en de Super Lig (TUR) geen BetExplorer-adres in de lijst "
     "stond en dat die twee competities dus op EEN bron rustten. Vandaag leverden beide een "
     "fixturepagina: Primeira Liga 9 rijen (1 vandaag) en Super Lig 9 rijen (2 vandaag), en beide "
     "zijn het met Fotmob eens. De vermoedelijke oorzaak van de melding van 26 november is dat "
     "beide competities die dag stillagen, zodat de pagina nul duels in het inzetvenster gaf en "
     "dat als een ontbrekend adres is gelezen. Geen actie nodig; vastgelegd zodat het punt niet "
     "elke run opnieuw als gat wordt opgeschreven.")

note("understat", "niet_bevraagd", 
     "27 nov (run A): NEGENDE RUNDAG OP RIJ ZONDER CIJFERS, en de eerste waarop het iets kost. "
     "Alle vijf competities bevraagd (EPL, La_liga, Bundesliga, Serie_A, Ligue_1, seizoen 2026) "
     "en alle vijf geven HTTP 200 met 26.719 bytes en geen JSON - 'UnderstatError: geen JSON "
     "terug'. EXACT dezelfde bytelengte als op 26 november, negen dagen hetzelfde foutbeeld: dat "
     "lijkt op een blokkadepagina en niet op een server die eruit ligt. ANDERS DAN DE AFGELOPEN "
     "RUNDAGEN KOSTTE HET VANDAAG WEL IETS, want alle vijf die competities speelden in het "
     "inzetvenster (Nottingham Forest - Chelsea, Venezia - Bologna, Levante - Racing Santander, "
     "Werder Bremen - Borussia Monchengladbach, Brest - Paris FC). Twee gevolgen, geen van beide "
     "op een gepubliceerde bet: het kalibratieblok van Sec. 6e mist bij die vijf duels de arm "
     "p_xg_understat, en er was vandaag geen tweede onafhankelijk xG-model in prob_sources. "
     "Sec. 2 blijft gedekt door Fotmob-xG, Fotmob-splits en de wedstrijdcontext. Dit is NIET het "
     "geval waarvoor Sec. 3 punt 3 een notificatie vooraan eist - dat gaat over Fotmob, en Fotmob "
     "leverde alles.")

note("niveaucorrectie_meting", "teken_omgeslagen_na_3_november_519_duels",
     "27 nov (run A): DE NIVEAUCORRECTIE model.LEVEL_SCALE = 1.032 IS VOOR HET EERST APART "
     "GEMETEN EN HAAR FOUT IS GESPIEGELD IN PLAATS VAN VERKLEIND. gridfit.measure op de twee "
     "deelpopulaties (tmp-run/ra_nov27_gridfit_na_niveau.txt): op de 1173 duels van 20 sep t/m "
     "2 nov, ZONDER de correctie, staat het gemiddelde totaal op +0,099 (z = +1,92) en de fout op "
     "P(Under 2.5) op -2,38 pp; op de 519 duels van 3 t/m 26 nov, MET de correctie, op -0,116 "
     "(z = -1,43) en +2,22 pp. Het teken is op alle drie de diagnoseregels omgeslagen en de "
     "absolute omvang is op P(Under 2.5) vrijwel gelijk gebleven. Tweede aanwijzing dezelfde kant "
     "op: op die 519 duels geeft scale = 1.032 nog een keer toepassen t = -2,12, de ENIGE variant "
     "in die tabel die de lat van |t| = 2 haalt, en dan in de ongunstige richting (op de 1173 "
     "ervoor: t = +0,92). NIETS VERZET EN DE VRAAG NIET VOORGELEGD: Run A heeft op 21 nov zelf de "
     "lat op 'ruim boven de ~900 duels' gezet en het zijn er 519, en z = -1,43 haalt de lat niet. "
     "Verwacht rond de kerst. Poort 9 hangt aan hetzelfde besluit en blijft onveranderd staan "
     "(Sec. 1h, Sec. 6g: een run verzet die knop nooit op eigen initiatief).")

note("goalbias_selectie", "over_kant_begint_nu_ook_scheef_te_staan",
     "27 nov (run A): margins.py goalbias geeft op de OVER-kant -0,374 doelpunt per duel over 83 "
     "gevallen bij z = -1,85, waar Sec. 6g op 11 oktober n = 38 en z = -0,54 noteerde en daaruit "
     "concludeerde 'op de Over-kant gebeurt dat niet'. Dat is de SPIEGEL van de Under-kant "
     "(+0,661 over 153, z = +4,92): de routine kiest aan beide uiteinden juist die duels waar "
     "haar eigen schatting de verkeerde richting uit staat, oftewel wel een algemene winner's "
     "curse op de doelpuntenas. Het rendement beweegt mee: Over ging van +10,6% over 62 picks "
     "(11 okt) naar +4,4% over 110, terwijl Under op -15,2% over 192 blijft. Het MODEL zelf staat "
     "goed: +0,017 doelpunt per duel over 2495 duels, z = +0,48. |z| = 1,85 haalt de lat niet en "
     "er is niets verzet; het staat als openstaand punt en het hoort bij elke Over-regel genoemd "
     "te worden - vandaag zijn alle drie de gepubliceerde regels een Over.")

note("margekalibratie", "gelijkspel_drie_procentpunt_te_hoog_sinds_de_shrink_overstap",
     "27 nov (run A): margins.py stats --since 2026-09-20 over 1692 homogene duels heeft EEN cel "
     "boven twee standaardfouten en dat is het gelijkspel: voorspeld 23,6% tegen werkelijk 20,6%, "
     "-3,0 pp. Tweede dag op rij dezelfde cel. Op de volle reeks (2495 duels, beide "
     "shrink-instellingen door elkaar) is het -1,6 pp en haalt ze de grens niet. Raakt geen enkele "
     "bet van vandaag (alle drie doelpuntenmarkten zonder kant), maar wel elke Draw No Bet en elke "
     "handicap op 0.0, en dus de rangorde van Sec. 1a. De kant waar Sec. 6f oorspronkelijk over "
     "ging staat recht: 'favoriet wint met 3 of meer' op -0,7 pp over 476 duels met een duidelijke "
     "favoriet.")

note("poort_5_tweede_methode", "vangt_driekwart_weg_tweede_dag_op_rij",
     "27 nov (run A): tweede_methode is de eerste dichte poort bij 149 van de 202 doorgerekende "
     "selecties (74%), na 14 van de 15 op 26 november. Lees het met de volgorde erbij: "
     "failed_gate geeft alleen de EERSTE dichte poort in ORDER en tweede_methode staat vooraan, "
     "dus 149 is een bovengrens voor wat de poort alleen tegenhoudt. De reeks staat op 347 "
     "afgewikkelde kandidaten en -2,3%: de poort bespaart geld maar nauwelijks. Vier van de acht "
     "'Net niet'-rijen hebben de twee methodes meer dan tien procentpunt uit elkaar, met +40,68 "
     "tegen +1,52 bij Sonderjyske - Brondby IF als uitschieter. Niets verzet op twee dagen; als "
     "het een week zo scheef blijft liggen hoort er een eigen meting te komen.")

note("poort_7_context", "kostte_twee_hele_duels_waaronder_de_hoogste_edge_van_de_dag",
     "27 nov (run A): poort 7 hield twee van de veertien duels volledig tegen, en bij beide ging "
     "het om een forse uitvallerslijst. Brest - Paris FC had met +15,09 pp op de thuiszege "
     "(@3.548) de HOOGSTE edge van de dag; Brest mist 49% van zijn selectiewaarde (Doumbia, Lala, "
     "Le Guen) tegen 10% bij Paris FC. Bij Werder Bremen - Borussia Monchengladbach mist Gladbach "
     "38% (Hashioka, Leszczynski, Ullrich) tegen 28% bij Werder. De reeks is de scherpste die het "
     "schaduwlogboek heeft: 153 afgewikkelde gevallen op -23,8%.")

note("poort_9_doelpunten_onder", "reeks_52_rem_werkt_en_bond_vandaag_een_keer",
     "27 nov (run A): 52 afgewikkelde gevallen, -35,9% (18 winnaars op 52). Ruim voorbij de ~30 "
     "van Sec. 6d en de rem wijst dezelfde kant op als toen: hij bespaart geld. Vandaag bond hij "
     "een keer, op de enige Under die ver genoeg kwam: Sonderjyske - Brondby IF Under 3 @1.88 met "
     "+9,70 pp op een verzwaarde lat van 10,0. Bij hetzelfde duel haalde Under 2.5 @2.40 de lat "
     "wel op de herijkte schaal (+10,06 pp) maar niet op de ruwe (+9,35 pp), waardoor die rij als "
     "herijking_omgekeerd het schaduwlogboek inging. LET OP het verband met de niveaumeting "
     "hierboven: de rem bestaat omdat P(Under) te hoog stond, en op de reeks van na 3 november "
     "staat P(Under) juist te laag. Die twee horen samen opnieuw bekeken, niet apart.")

note("herijking_omgekeerd_gepubliceerd", "een_van_de_drie_regels_wordt_door_de_herijking_gedragen",
     "27 nov (run A): Levante - Racing Santander, Over 3.5 @2.10 op LIGHT, is de derde "
     "gepubliceerde regel en de enige met bet_beide = False: +16,84 pp herijkt tegen +15,71 pp "
     "ruw, op een LIGHT-lat van 16,0. Hij haalt zijn lat dus alleen nadat de fit van vandaag "
     "(a=1,041, b=0,027) zijn kans met 1,13 pp heeft OPGETILD. Sec. 5a heeft dit geval voorzien "
     "toen de fitbron op 20 september veranderde en schrijft: vertrouw de redenering niet meer, "
     "vertrouw de vlag. De publicatie gaat door omdat Sec. 1 en Sec. 5a de HERIJKTE kans als "
     "publicatieschaal aanwijzen en alle overige poorten open staan. Tegenreeks: "
     "herijking_omgekeerd staat op -70,9% over 7 afgewikkelde gevallen (1 winnaar) - veel te "
     "weinig om iets te zeggen (Sec. 6d eist ~30) en het wijst niet de kant op die de publicatie "
     "steunt. Genoteerd zodat deze regel bij de afwikkeling van morgen apart te lezen is.")

note("herijking_fitted_through", "ok",
     "27 nov (run A): fitted_through = 2026-11-26, de vorige rundag. Sec. 6b-5c eist dat dat "
     "getal op de vorige rundag staat of daarna en dat klopt, omdat calibration.py settle vandaag "
     "in Stage 0 is gedraaid voordat load_fit() aan de analyse begon: 72 waarnemingen afgewikkeld, "
     "9246 van 9276 compleet, 30 nog open. Fit a=1,041 b=0,027 op 8847 afgerekende gevallen; de "
     "correctie VERHOOGT een kans over vrijwel de hele speelbare band (+0,7 pp op 50%, +1,3 pp op "
     "70%).")

note("lijstlengte_reeks", "meting loopt - 34 van de 100",
     "27 nov (run A): 34 afgewikkelde gevallen, 16 winnaars, +4,60u = +13,5%. Op 20 november stond "
     "de reeks op 30 gevallen en +20,8%, dus gegroeid en in rendement gezakt. VANDAAG BOND DE "
     "LIJSTLENGTE NIET: twee selecties boven hun eigen lat en drie plekken in de vrijdaglijst, dus "
     "Sec. 5b stap 5 vulde de derde plek op rangorde aan en er viel niets buiten de lijst - geen "
     "lijstlengte-rij en geen groene regel bovenaan de dekkingsrapportage. De gebruiker kijkt bij "
     "100 gevallen; tot dan wordt de vraag niet voorgelegd.")

note("divisiekaart_promovendi", "vijf_omrekeningen_en_alle_vijf_kwamen_door",
     "27 nov (run A): vijf van de veertien duels hebben een ploeg die niet in de stand van "
     "2025/2026 van zijn huidige competitie staat - Venezia (Serie A), Racing Santander (La Liga), "
     "Willem II (Eredivisie), Maritimo (Primeira Liga) en Kortrijk (Belgian Pro League). "
     "conversion_in_range weigerde GEEN van de vijf, dus er is vandaag geen enkel duel op NONE "
     "uitgekomen. Bij vijf omrekeningen op veertien duels is dat niet triviaal; de Coventry-val "
     "heeft deze maand meerdere duels gekost. LET OP EEN RAND: de relatieve aanval van Racing "
     "Santander is 1.628 tegen een gemeten bovengrens van 1.651 voor SP1/SP2 omhoog, dus 0,023 "
     "onder de grens - en dat is de enige van de vijf die een gepubliceerde bet werd.")

note("pinnacle_vergelijking", "systematisch_boven_pinnacle_op_doelpunten_en_dat_verklaart_de_drie_overs",
     "27 nov (run A): Pinnacle beschikbaar voor 12 van de 14 duels (Levante - Racing Santander en "
     "Rizespor - Kasimpasa niet), marge 3,0 tot 4,8 procent. Op 1X2 staat het model gemiddeld "
     "4,20 pp van het Pinnacle-oordeel af en de twee grootste afwijkingen zitten precies bij de "
     "twee duels die poort 7 tegenhield (Brest +15,78 pp, Sonderjyske -9,19 pp). OP DE "
     "DOELPUNTENKANT IS HET SYSTEMATISCH: over 12 (duel, lijn)-paren staat het model gemiddeld "
     "4,96 pp ONDER Pinnacle op P(Under), oftewel het verwacht structureel MEER doelpunten dan de "
     "scherpste bookmaker (Nottingham Forest - Chelsea -11,44 pp op lijn 2,75, Alanyaspor - "
     "Konyaspor -9,16 pp op lijn 2,25). Dat is de reden dat er drie Overs staan EN precies de "
     "scheefstand die de scale-meting op de 519 duels van na 3 november terugvindt; waarschijnlijk "
     "hetzelfde verschijnsel van twee kanten gemeten. Niets hiervan gaat in my_prob (Sec. 2).")

note("cups_grens", "zes_bekers_buiten_de_runlijst_en_geen_van_zes_speelt",
     "27 nov (run A): FA Cup, League Cup, Coppa Italia, KNVB Beker, DFB Pokal en Copa del Rey "
     "vallen van 1 juli t/m 31 december buiten de runlijst (cups.filter_runlist met de rundag). "
     "Status BUITEN DE RUNLIJST en niet GEEN WEDSTRIJD, zoals Sec. 5 eist. Feitelijk maakt het "
     "vandaag niets uit: nul duels in beide daglijsten voor alle zes. Coppa Italia en DFB Pokal "
     "hebben hun eerstvolgende ronde op 1 december en de League Cup op 15 december, dus geen van "
     "drie valt in de tweede seizoenshelft; alle zes doen voor het eerst mee op 1 januari 2027.")

note("report_gate_label", "aangevuld_met_zes_poortnamen",
     "27 nov (run A): report.GATE_LABEL miste zes poortnamen (context, underdog, "
     "doelpunten_onder, herijking, herijking_omgekeerd, lijstlengte) en drukte ze via de "
     ".get(...)-terugval met hun INTERNE naam op de pagina af. In de eerste render van vandaag "
     "stond bij Sonderjyske - Brondby IF letterlijk 'herijking_omgekeerd' in de kolom 'Valt af "
     "op'. Sec. 6c verbiedt jargon in het dagrapport en een terugval die de interne sleutel "
     "afdrukt is de stille vorm daarvan: niets klaagt, de pagina rendert. Aangevuld met zes "
     "leesbare labels; de NAMEN zelf zijn niet veranderd, want die zijn in shadow.jsonl en "
     "meta.py de sleutel van een meetreeks. report.py selftest slaagt met 36 controles. Oudere "
     "dagrapporten zijn NIET opnieuw gerenderd (Sec. 6c).")

note("stage_min_2_branchaudit", "honderd_takken_zestien_meldingen_en_alle_zestien_geen_verlies",
     "27 nov (run A): ondiepe kloon bij de start (true), ge-unshallowed, daarna 100 takken per "
     "record op de INHOUD vergeleken. picks.jsonl (603), context-log.jsonl (2605), "
     "calibration.jsonl (9259) en coverage.json (339) VOLLEDIG op origin/main. Zestien records "
     "staan op een tak en niet op main, en alle zestien zijn bekend en geen verlies: vier "
     "shadow.jsonl-rijen van 3 oktober die op 7 november MET OPZET zijn verwijderd wegens "
     "dubbeltelling (Sec. 3 Stage -2 verbiedt ze aan te vullen) en twaalf bladpaden in "
     "source-health.json die per-run momentopnames van oudere Run B/C-takken zijn. NIEUW "
     "OPGESCHREVEN: de commitgraaf misleidt hier dubbel. rev-list geeft voor de meeste takken een "
     "getal in de honderden, maar merge-base met main geeft NIETS - de geschiedenis van main "
     "begint bij 957f17d (Run D, 16 nov 2026) en alles van voor die datum hangt aan een "
     "losgekoppelde geschiedenis waarvan de INHOUD wel is meegenomen. picks.jsonl staat op main "
     "op 603 regels tegen 555 op de laatste tak van voor de knip, en de twee regels die alleen "
     "daar staan zijn de pending-versies van twee picks die main al afgewikkeld heeft. Niets "
     "gemerged, want er viel niets te mergen.")

note("settling", "alles_afgewikkeld_niets_mis_en_niets_open",
     "27 nov (run A): twee picks en vierendertig schaduwrijen afgewikkeld, alle 36 uit de league "
     "phase van de Europa en Conference League van 26 november plus twee binnenlandse duels, dus "
     "zonder verlenging - scoreStr IS de stand na 90 minuten (Sec. 6d). PICKS: Lyon - Lillestrom "
     "Under 3.5 @1.89 GEWONNEN op 0-0, Union St.Gilloise - Lech Poznan Under 3.5 @1.76 VERLOREN "
     "op 2-2, netto -0,11u. SCHADUW: 22 gewonnen, 11 verloren, 1 push (Ajax - Thun, Under 4 bij "
     "exact vier doelpunten). Nul rijen MIS; ledger.py open en shadow.py open geven na de "
     "afwikkeling beide 'geen'. Het patroon van de avond: 11 van de 16 tegengehouden "
     "underdog-handicaps wonnen, op een avond met vier uitslagen van 4-0 of 4-1. Dat is een dag "
     "en geen reeks; de volle underdog-reeks staat op -1,3% over 441 gevallen.")

note("contextlogboek_dekking", "helling_voor_het_eerst_op_de_grens_van_aantoonbaar",
     "27 nov (run A): 14 van de 14 duels met context toegevoegd (nul afgekapt), 27 afgewikkeld, "
     "logboek op 2619 rijen waarvan 2602 afgewikkeld. De helling van de MODELfout tegen het "
     "beschikbaarheidsverschil staat op -11,4 pp per eenheid bij t = -1,92, en bij 2602 "
     "wedstrijden is alleen een effect vanaf ~11 pp aantoonbaar - dus net op de grens, en voor het "
     "eerst. De richting is de verwachte. Sec. 1c blijft onverkort gelden: poort 7 is een REM en "
     "geen BIJSTELLING tot er een echte meting ligt; een getal in my_prob stoppen op t = -1,92 is "
     "precies wat Sec. 2 en Sec. 4 verbieden.")

H["last_run_bevinding"] = (
    "27 nov 2026, Run A — TWEE BEVINDINGEN, EN ZE HANGEN SAMEN. (1) DE NIVEAUCORRECTIE "
    "model.LEVEL_SCALE = 1.032 IS VOOR HET EERST APART TE METEN EN HAAR FOUT IS GESPIEGELD IN "
    "PLAATS VAN VERKLEIND. Op de 519 duels van na 3 november staat het gemiddelde totaal op "
    "-0,116 (z = -1,43) waar het op de 1173 duels ervoor op +0,099 (z = +1,92) stond, en de fout "
    "op P(Under 2.5) ging van -2,38 naar +2,22 pp. Sec. 6g schreef voor dat die regel naar NUL "
    "hoorde te zakken; ze is doorgeschoten, en dat is een derde geval dat de regel niet voorzag. "
    "Op die 519 duels geeft scale = 1.032 nog een keer toepassen t = -2,12, de enige variant in "
    "de hele tabel die de lat van |t| = 2 haalt en dan in de ongunstige richting. NIETS VERZET EN "
    "DE VRAAG NIET VOORGELEGD: Run A heeft op 21 nov zelf de lat op 'ruim boven de ~900 duels' "
    "gezet en het zijn er 519. Poort 9 hangt aan hetzelfde besluit en blijft staan. "
    "(2) OOK DE OVER-KANT LAAT NU EEN SELECTIE-EFFECT ZIEN. margins.py goalbias geeft over de 83 "
    "duels waarin werkelijk een Over is gespeeld -0,374 doelpunt per duel (z = -1,85), waar "
    "Sec. 6g op 11 oktober n = 38 en z = -0,54 noteerde en daaruit concludeerde dat de Over-kant "
    "juist AAN de vormfout verdient. Met de Under-kant op +0,661 over 153 (z = +4,92) is dat de "
    "spiegel, en dus wel een algemene winner's curse op de doelpuntenas. Het rendement beweegt "
    "mee: Over van +10,6% over 62 naar +4,4% over 110, Under op -15,2% over 192. BEIDE "
    "BEVINDINGEN RAKEN DE DRIE REGELS VAN VANDAAG DIRECT, want alle drie zijn een OVER - en als "
    "het model sinds 3 november een tiende doelpunt per duel TE VEEL verwacht, is een Over "
    "precies de selectie die daar in de verkeerde richting van profiteert. Dat is een hypothese "
    "en geen meting, en ze hoort bij de vraag van punt 1. Niets aangepast; het MODEL zelf staat "
    "goed (+0,017 doelpunt per duel over 2495 duels, z = +0,48) en het is de SELECTIE die scheef "
    "staat."
)

_prev_a = H.get("last_run_run_a")
_hist_a = H.get("last_run_run_a_history") or []
if _prev_a:
    _hist_a = [{"date": _prev_a.get("date"),
                "note": f"Tekstblok van Run A van {_prev_a.get('date')}, bewaard bij het "
                        f"bijwerken van {now[:10]}.",
                "blok": _prev_a}] + _hist_a
H["last_run_run_a_history"] = _hist_a[:6]
H["last_run_run_a"] = {
    "run": "A", "date": "2026-11-27",
    "matches_in_window": 14, "analysed": 14, "truncated": 0, "bets": 3,
    "qualified_not_published": 0,
    "credits": "46 van een plafond van 2358 (36 bulk voor 12 competities + 10 BTTS); 18.884 over, "
               "1116 gebruikt deze maand bij het begin van de run",
    "bevinding": H["last_run_bevinding"],
    "sources_deze_run": {
        "fotmob": "ok; daglijsten 27+28 nov, standen 12 competities x 2 seizoenen, context 14/14 "
                  "zonder fout, marktvorm 14/14, voorbeschouwing 3/3",
        "the_odds_api": "ok, 44 actief, 18884 over, 46 credits verbruikt (36 bulk + 10 BTTS)",
        "betexplorer": "ok; 22 van 22 fixturepagina's, 14 tegen 14 duels eens met Fotmob, plus "
                       "het gratis 1X2-marktgemiddelde; de twee slugs die 26 nov als gat golden "
                       "leverden beide gewoon een pagina",
        "understat": "geen JSON, negende rundag op rij; vandaag WEL met gevolg, alle vijf zijn "
                     "competities speelden en de p_xg_understat-arm mist vijf waarnemingen",
        "api_football": "niet beschikbaar; besluit van de gebruiker 27 sep 2026, geen gat en geen "
                        "actiepunt (Sec. 3 Stage 3)",
        "pinnacle": "ok; 12 duels 1X2 (gem. afstand 4,20 pp) en 12 (duel, lijn)-paren totalen "
                    "(gem. -4,96 pp op P(Under)), marge 3,0 tot 4,8 procent",
    },
    "note": "TWAALF van de ZESTIEN competities van de runlijst spelen in het venster "
            "[08:00 NL 27 nov, 08:00 NL 28 nov): elf met een duel, de Super Lig en de Ekstraklasa "
            "met twee, samen 14. Vier op GEEN WEDSTRIJD (Scottish Premiership plus de drie "
            "Europese toernooien, die hun league phase op 25/26 nov sloten) en de zes bekers op "
            "BUITEN DE RUNLIJST (cups.py, besluit 18/19 nov), geen van zes speelt werkelijk. "
            "Vrijdagcap 55, niets afgekapt; datarijkdom 5,0 tot 6,5. GEEN ENKEL duel op NONE, bij "
            "vijf promovendi-omrekeningen die alle vijf binnen het gemeten bereik bleven. "
            "202 selecties doorgerekend, 7 met alle poorten open; poort 5 ving er 149 weg (74%), "
            "poort 7 hield twee hele duels tegen waaronder de hoogste edge van de dag (Brest, "
            "+15,09 pp, 49% van de selectiewaarde afwezig). MAX_SHORTLIST is 3 op vrijdag; twee "
            "selecties boven hun eigen lat en drie plekken, dus de lijstlengte bindt niet en de "
            "DERDE regel is op rangorde aangevuld (Sec. 5b stap 5). Die derde regel (Levante - "
            "Racing Santander) is de enige met bet_beide = False: hij haalt de LIGHT-lat van 16,0 "
            "alleen herijkt (+16,84) en niet ruw (+15,71). ALLE DRIE DE REGELS ZIJN EEN OVER.",
}
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")

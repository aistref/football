"""Run B, 20 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Vijf dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **De runlijst komt na acht dagen stilte weer op gang**: zeven van de zeventien competities
   spelen, met 17 duels in het venster. Alle zeventien doorgerekend, niets afgekapt.
2. **Een naamkoppeling is gerepareerd die TOP Oss - Roda JC Kerkrade al zijn prijzen kostte.**
   Vier aliasregels in `scripts/teamnames.py`; zie bevinding 1.
3. **De Under-kant van de SELECTIE staat voor het eerst op z = +4,63** (138 gespeelde Unders,
   +0,655 doelpunt per duel boven de eigen lambda) terwijl het MODEL op z = +0,79 staat. Dat is
   de scherpste stand die `margins.py goalbias` ooit heeft gegeven, en de enige bet van vandaag
   die haar lat haalt staat op die kant.
4. **Elf van de 17 duels staan in twee competities zonder xG EN zonder sportkey** (KKD, Romanian
   SuperLiga): op beide assen de zwakste van de dag.
5. **Twee Jong-ploegen vallen uit het contextlogboek** (Jong Ajax, Jong PSV, `squad_value = 0`),
   15 van 17 geboekt. Geen bronfout maar een meting die niet bestaat.
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
     "20 nov (run B): daglijsten 20 en 21 nov opgehaald (173 duels over 87 competities en 600 over "
     "156); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand, "
     "afsluitcode 0 - ook voor de tien competities van deze runlijst die vandaag stil zijn, en dat "
     "is precies de kant van de controle die iets kan opleveren. Serie B staat op het echte id 86 "
     "met 20 ploegen. Standen van alle zeven spelende competities geleverd, beide seizoenen. TWEE "
     "VAN DE ZEVEN HEBBEN GEEN xG EN DAT IS DE BEKENDE, VASTGELEGDE STAND, geen storing: Romanian "
     "SuperLiga (189) en Keuken Kampioen Divisie (111) staan in coverage.json met xG=False en "
     "idcheck.py bevestigt dat per competitie. Die twee leveren samen ELF van de zeventien duels, "
     "dus bijna tweederde van deze run draait op doelpunten als sterktemaat (LIGHT, lat 16,0 pp). "
     "Context voor alle zeventien duels zonder fout; context.check_venue sloeg NERGENS aan "
     "(relocated = False overal). TWEE SQUAD_VALUES OP NUL: Jong Ajax en Jong PSV, de reserveteams "
     "van Ajax en PSV, hebben geen genoteerde marktwaarden, dus ctxlog.out_share geeft daar None en "
     "die twee duels vallen uit het contextlogboek (15 van 17). Dat is geen bronfout maar een "
     "meting die niet bestaat; de KKD heeft vier Jong-ploegen en dit komt elke speelronde terug. "
     "lineupType: 16 van de 17 op 'lastStarting11' en 1 op 'predicted' (Molde - Bodo/Glimt), geen "
     "enkel 'confirmed' - te verwachten bij een run die om 04:20 NL de prijzen uitleest en "
     "aftrappen van 16:30 tot 21:00 NL. Voorbeschouwingsblokken (preview.py) voor alle drie de bets "
     "zonder fout, en marketform.match_block voor alle zeventien doorgerekende duels zonder fout.")

note("the_odds_api", "ok",
     "20 nov (run B): api_check.py meldt OK, 44 actieve voetbalcompetities, quota 19.344 over en "
     "656 gebruikt deze maand bij het begin van de run. 33 van de 34 sportkeys van de repo actief; "
     "de uitzondering is Coppa Italia (soccer_italy_coppa_italia), een Run A-toernooi dat vandaag "
     "niet speelt. VIER ACTIEVE SPORTKEYS DIE DE REPO NIET KENT en dat is onveranderd: "
     "soccer_brazil_serie_b, soccer_germany_bundesliga_women, soccer_germany_liga3 en "
     "soccer_sweden_superettan. Geen van de vier staat op een runlijst, dus het is geen gat in de "
     "dekking maar een mogelijk gat in SPORT_KEYS als een runlijst ooit wordt uitgebreid. "
     "UITGEGEVEN: 20 credits van een plafond van 878 (suggest_cap op 19.344 over en 11 dagen tot de "
     "maandwissel, 2 runs/dag) - 15 aan de bulk (h2h+spreads+totals voor Eliteserien, Segunda "
     "Division, Serie B, 2. Bundesliga en English League One) en 5 aan de tweede BTTS-ronde. Na de "
     "run 19.324 over. VIJF VAN DE ZEVEN SPELENDE COMPETITIES HEBBEN EEN SPORTKEY; Romanian "
     "SuperLiga en Keuken Kampioen Divisie niet, en die draaien op het gratis "
     "BetExplorer-marktgemiddelde. De marktbalans-controle van Sec. 1a is gehaald: voor alle vijf "
     "inkoopbare competities levert de bulk zowel een uitkomstmarkt als een doelpuntenmarkt, en "
     "progress.py verify geeft groen op alle zeventien duels voor alle zes de markten.")

note("betexplorer", "ok",
     "20 nov (run B): de bevestigingspoort van Sec. 1 komt op 17 VAN DE 17 COMPETITIES EENS MET "
     "Fotmob, zeventien duels tegen zeventien - ook op de tien competities die vandaag niets op de "
     "kalender hebben, waar BetExplorer eveneens nul duels in het venster geeft en 21 tot 24 "
     "november als eerstvolgende datum noemt. HET MARKTGEMIDDELDE IS VANDAAG VOOR TWEE COMPETITIES "
     "DE ENIGE 1X2-BRON (Romanian SuperLiga 16 rijen, Keuken Kampioen Divisie 13 rijen), en dat "
     "zijn elf van de zeventien duels. EEN KOPPELING FAALDE EN IS GEREPAREERD: 'Oss - Roda' "
     "koppelde niet aan 'TOP Oss - Roda JC Kerkrade' (BetExplorer kort de clubnaam in tot de "
     "PLAATS), waardoor dat duel met nul prijzen de analyse binnenkwam. De rij zelf was in orde - "
     "3,55/3,59/1,86 - dus dit is geen bronprobleem maar een koppelingsprobleem aan onze kant. Na "
     "de reparatie koppelen alle negen KKD-duels. Zie bevinding 1.")

note("teamnames", "aliassen_bijgeschreven",
     "20 nov (run B): vier regels toegevoegd aan ALIASES - 'top oss' <-> 'oss' en 'roda jc "
     "kerkrade' <-> 'roda'. Dezelfde soort als 'la galaxy' (17 okt) en 'red bull new york' "
     "(30 sep): een bron kort de clubnaam zo in dat er na _DROP geen token overblijft dat als "
     "VOORVOEGSEL op woordniveau koppelt, en best_pair haalt met 0,44 de vloer van 0,62 niet. Het "
     "raakt niet de tier maar de PRIJZEN, en het faalt stil - een duel zonder prijzen laat geen "
     "spoor na in het rapport. report.py selftest (36), preview.py selftest (32), prosecheck.py "
     "selftest (26) en progress.py selftest draaien alle vier groen na de wijziging.")

note("understat", "niet_bevraagd",
     "20 nov (run B): NIET bevraagd en dat is geen storing. Understat dekt vijf competities (PL, "
     "La Liga, Bundesliga, Serie A ITA, Ligue 1) en geen van die vijf staat op de Run B-runlijst, "
     "dus er was vandaag niets te halen. Run A van vandaag heeft de bron wel bevraagd; zie de "
     "regel hieronder in detail_history voor die waarneming. De redundantie die Sec. 4 beschrijft "
     "geldt voor Run A; voor Run B is Fotmob de enige xG-bron, en dat is precies waarom Sec. 3 "
     "voorschrijft dat een omgevallen Fotmob vooraan in de notificatie hoort. Vandaag leverde "
     "Fotmob zonder fout.")

note("api_football", "niet_gezet",
     "20 nov (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT VAN DE GEBRUIKER van 27 sep "
     "2026 en geen storing: hij wil hier geen geld aan uitgeven, en de kanskant komt van Fotmob en "
     "Understat (Sec. 3). Niet als gat melden, niet als actiepunt en niet in de notificatie. De "
     "uitzondering blijft staan: zodra Fotmob niet meer levert is er voor vrijwel elke competitie "
     "van deze runlijst geen onafhankelijke kansbron meer, wordt elk duel data_tier = NONE en "
     "levert elke run gegarandeerd nul bets - en pas dan is een betaald plan een reele vraag.")

note("settling", "ok",
     "20 nov (run B): twee schaduwrijen afgewikkeld en nul echte picks, en dat is de juiste "
     "uitkomst en geen overgeslagen stap. shadow.py open gaf twee rijen klaar, beide van Run B van "
     "19 nov: Orlando City - FC Cincinnati (1X2 FC Cincinnati @2,75, viel af op edge) GEWONNEN op "
     "1-3 en Sao Paulo - Fluminense (Over 2.5 @2,274, viel af op tweede_methode) VERLOREN op 0-1. "
     "Beide duels staan bij Fotmob op reason FT zonder verlenging, dus de eindstand IS de stand na "
     "90 minuten. ledger.py open gaf vier openstaande picks en geen van de vier is afwikkelbaar: "
     "drie zijn van Run A van vandaag met een aftrap die nog moet komen, en de vierde is "
     "Seattle Sounders FC - Real Salt Lake (Under 3.5, Run B van 19 nov, aftrap 04:00 NL) die bij "
     "het begin van deze run 0,1 uur onderweg was. DIE WIKKELT DE RUN VAN MORGEN AF; het is geen "
     "achterstand maar een duel dat tijdens de run speelt. calibration.py settle wikkelde 6 "
     "waarnemingen af, ctxlog.py settle 1. recalibrate.load_fit().fitted_through staat op "
     "2026-11-19, de VORIGE RUNDAG - de controle van Sec. 6b-5c is daarmee gehaald.")

note("poort_9_doelpunten_onder", "reeks_42_rem_werkt",
     "20 nov (run B): de reeks `doelpunten_onder` staat op 42 kandidaten (41 afgewikkeld) met "
     "-31,5% rendement en 36,6% trefkans. Boven de ~30 van Sec. 6d, en het teken is negatief: de "
     "rem houdt verliezers tegen en hoort te blijven zoals hij is. EN HIJ IS VANDAAG EXTRA "
     "RELEVANT, want margins.py goalbias geeft de scherpste stand die hij ooit heeft gegeven: over "
     "138 GESPEELDE Unders ligt het werkelijke doelpuntentotaal +0,655 per duel boven de eigen "
     "lambda bij z = +4,63, terwijl het MODEL over alle 2242 doorgerekende duels op z = +0,79 "
     "staat. Dat zijn twee verschillende fouten die Sec. 6g uitdrukkelijk NIET bij elkaar optelt: "
     "de bovenste meet het model, de onderste de selectie. De enige bet van vandaag die haar eigen "
     "lat haalt staat op de Under-kant en haalt de verzwaarde lat van 10,0 pp met +13,25 pp; poort "
     "9 hield vandaag nul selecties tegen. EEN RUN VERZET DEZE POORT NIET OP EIGEN INITIATIEF "
     "(Sec. 1h, stand van 2 nov 2026).")

note("pinnacle_vergelijking", "let_op",
     "20 nov (run B): zes duels met een Pinnacle-1X2 (gemiddelde absolute afstand tot het de-vigde "
     "Pinnacle-oordeel 3,59 pp, gemiddelde Pinnacle-marge 3,85%) en zes toetsbare (duel, "
     "lijn)-paren op de totalen. DE GEPUBLICEERDE UNDER IS DE GROOTSTE AFWIJKING VAN DE DAG: op "
     "lijn 4,0 van Molde - Bodo/Glimt zegt het eigen model P(Under) = 0,667 en Pinnacle 0,504, een "
     "verschil van +16,30 procentpunt bij een Pinnacle-marge van 3,4%. Over de hele run +2,04 pp op "
     "de Under-kant met 4 van de 6 erboven; uitgesplitst +4,71 pp op de vijf lijnen MET push en "
     "-11,34 pp op de ene zuivere halve lijn (FC Andorra - Leganes, waar het model juist ONDER "
     "Pinnacle zit). Op de 1X2 is de grootste afwijking Barnsley - Sheffield Wednesday (+7,76 pp op "
     "de thuiskant), en dat duel werd geen bet. Dit getal gaat NIET in my_prob (Sec. 2); het hoort "
     "in de vergelijking.")

note("lijstlengte_reeks", "meting loopt - 30 van de 100",
     "20 nov (run B): de reeks `lijstlengte` staat onveranderd op 30 afgewikkelde gevallen, "
     "15 winnaars, +6,24u = +20,8%. VANDAAG KOMT ER GEEN RIJ BIJ: er is precies EEN selectie die "
     "haar lat haalt en MAX_SHORTLIST is 3, dus er valt geen gekwalificeerde selectie buiten de "
     "lijst (publiceer-script: '0 gekwalificeerde selectie(s) buiten de lijst van Sec. 5b'). De "
     "gebruiker kijkt opnieuw bij 100 gevallen (besluit 18 nov 2026) en niet eerder; noem de stand "
     "elke run onder 'Stand van het logboek' en leg de vraag pas bij 100 voor. Een run verandert "
     "MAX_SHORTLIST nooit op eigen initiatief.")

note("herijking_fitted_through", "ok",
     "20 nov (run B): recalibrate.load_fit() geeft a=1,0566, b=0,0365 op 8001 afgerekende gevallen "
     "met fitted_through 2026-11-19 - de VORIGE RUNDAG, dus calibration.py settle is niet blijven "
     "liggen (de controle aan dit ene getal, Sec. 6b-5c). De fit VERHOOGT een kans over vrijwel de "
     "hele speelbare band (+0,3 pp op 40%, +0,9 op 50%, +1,7 op 70%), dus 'herijkt haalt de lat, "
     "dus ruw ook' is NIET automatisch waar: bij Molde staat de ruwe edge op +11,69 pp tegen +13,25 "
     "herijkt. Daarvoor bestaat de vlag bet_beide (Sec. 5a), en die staat op deze regel goed - hij "
     "haalt op beide schalen de lat. Van de drie gepubliceerde regels haalt er 1 de lat ook ruw; de "
     "andere twee staan in de lijst op rangorde (Sec. 5b).")

# LET OP: dit blok is NA het draaien van dit script rechtgezet (zie
# `rb_nov20_health_fix` in het runrapport). De eerste versie schreef "de container kreeg GEEN
# ondiepe kloon", en dat was ONWAAR: `git rev-parse --is-shallow-repository` gaf true met 64
# commits. De vervangende tekst staat in data/source-health.json onder `ondiepe_kloon`.
note("ondiepe_kloon", "gerepareerd met --unshallow",
     "20 nov (run B): ondiepe kloon (64 commits); na `git fetch --unshallow origin` 771 commits en "
     "0 van de 95 takken met eigen commits. Zie source-health.json voor de volledige tekst.")

H["last_run_run_b"] = {
    "run": "B", "date": "2026-11-20",
    "matches_in_window": 17, "analysed": 17, "truncated": 0,
    "bets": 3, "qualified_not_published": 0,
    "credits": ("20 van een plafond van 878 (15 bulk voor 5 competities + 5 BTTS); 19.344 over, "
                "656 gebruikt deze maand bij het begin van de run"),
    "note": (
        "Zeven van de zeventien competities spelen, 17 duels in het venster, NIETS afgekapt "
        "(vrijdagcap 55). Op drie manieren nagetrokken dat de tien stille competities werkelijk "
        "stil zijn: idcheck.py 33/33 groen met afsluitcode 0, BetExplorer 17 van 17 eens (17 tegen "
        "17 duels), en runwindow.py - dat bindt vandaag NIET, want alle zeventien duels komen van "
        "de daglijst van vandaag en alle zeventien zijn playable. ELF VAN DE ZEVENTIEN DUELS "
        "STAAN IN TWEE COMPETITIES ZONDER xG EN ZONDER SPORTKEY (Keuken Kampioen Divisie 9, "
        "Romanian SuperLiga 2): LIGHT met een lat van 16,0 pp EN een 1X2 zonder herleidbare "
        "bookmaker. Zeven duels hebben een ploeg zonder stand in vorig seizoen en gingen langs "
        "promotion.convert. DRIE BETS, en precies EEN haalt zijn eigen lat: Molde - Bodo/Glimt, "
        "Under 4 @1,92 op FULL met +13,25 pp (poort 9 eist 10,0). De andere twee staan er op "
        "rangorde (Sec. 5b, MAX_SHORTLIST = 3 op vrijdag): FC Volendam - Jong Ajax +15,10 pp op "
        "een LIGHT-lat van 16,0 en Arminia Bielefeld - Magdeburg +3,41 pp op een FULL-lat van 8,0. "
        "DE BET DIE ZIJN LAT HAALT IS OOK DE GROOTSTE AFWIJKING VAN PINNACLE VAN DE DAG "
        "(+16,30 pp op de Under-kant) en staat op de kant waar margins.py goalbias de selectie op "
        "z = +4,63 meet - dat is de waarschuwing van deze run en ze staat bij de bet in het "
        "runrapport. Een naamkoppeling is gerepareerd (TOP Oss - Roda JC Kerkrade, vier "
        "aliasregels in scripts/teamnames.py). Twee Jong-ploegen vallen uit het contextlogboek "
        "(squad_value = 0): 15 van 17 geboekt."),
    "history": ([{"date": H["last_run_run_b"].get("date"),
                  "blok": {k: v for k, v in H["last_run_run_b"].items() if k != "history"}}]
                + (H["last_run_run_b"].get("history") or []))[:6],
}

H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt")

"""Run A, 31 okt 2026 — bronprobe voor source-health.json.

DRIEENVIJFTIG duels in het inzetvenster over TWAALF competities: de drukste dag van de maand, en
met 53 tegen een zaterdagcap van 55 het dichtst bij de cap dat deze routine deze maand is gekomen.
Geen beker heeft een ronde en geen Europees toernooi speelt. Alle vier de bronkanten werkelijk in
gebruik.

GEEN ENKELE BRONSTORING. `store["errors"]` is over de hele run leeg gebleven.

DE BEVINDING VAN VANDAAG ZIT NIET IN EEN BRON MAAR IN `scripts/promotion.py`, en ze staat daarom
onder de rekenmodules: de `data_tier` van een DUEL werd met een kale toewijzing uit de twee kanten
gerekend, waardoor een omrekening buiten het gemeten bereik bij de THUISploeg stil werd
overschreven door een geldige omrekening bij de UITploeg.
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
     "31 okt (run A): daglijsten 31 okt en 1 nov opgehaald en voor de afwikkeling die van 30 en "
     "31 okt. idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. "
     "Standen van alle benodigde competitiebases geleverd: de twaalf spelende competities plus "
     "de divisies eronder en erboven voor de TWINTIG omgerekende ploegen (Championship, Serie B, "
     "LaLiga2, 2. Bundesliga, Ligue 2, League One, Eerste Divisie, First Division B, 1. Lig, "
     "Championship SCO, I Liga en de Premier League zelf voor de drie degradanten). Context voor "
     "ALLE 53 duels zonder een enkele fout, en alle 53 in het contextlogboek (1814 duels nu) - "
     "ook de twee duels die op NONE uitkwamen, zoals §1c eist. Het stadion is bij alle 53 duels "
     "gevuld, dus context.check_venue heeft werkelijk gemeten: NUL verplaatsingen, en dat is een "
     "meting en geen lege uitkomst. lineupType: 'predicted' en 'lastStarting11' door elkaar, geen "
     "enkele 'confirmed' - te verwachten om 03:10 NL bij aftrappen van 11:30 tot 21:30. "
     "Voorbeschouwingsblokken (preview.py) voor alle VIJF de bets zonder fout, en "
     "marketform.match_block voor alle 51 doorgerekende duels zonder fout. De vijf bekers hebben "
     "geen ronde: EFL Cup (id 133), DFB Pokal (209) en KNVB Cup (235) staan vandaag met nul duels "
     "in de daglijst, en dat is met BetExplorer bevestigd in plaats van eruit geconcludeerd "
     "(§5, de FA Cup-les van 6 oktober).")

note("the_odds_api", "ok",
     "31 okt (run A): sleutel geldig, 46 actieve voetbalcompetities, quota 18.530 over en 1.470 "
     "verbruikt bij de start van de run. Geen afgewezen sleutel en geen quotaprobleem. ALLE "
     "TWAALF spelende competities hebben een sportkey en kregen de volledige bulk (h2h + spreads "
     "+ totals, 3 credits per competitie); daarna BTTS voor 38 duels met een kandidaat-edge. "
     "Verbruik 36 + 38 = 74 credits van een plafond van 9255 (suggest_cap(18530, 1) - 31 okt is "
     "de LAATSTE DAG VAN DE MAAND, dus dat plafond is met opzet ruim: wat over is vervalt). Nog "
     "18.456 over van het maandplafond van 20.000. ALLE 53 DUELS HEBBEN EEN BESTE PRIJS met een "
     "herleidbare bookmaker; de winst op het marktgemiddelde ligt tussen +3,57% en +23,75%, "
     "gemiddeld +7,06% over 50 duels. Twee bekende sportkeys zijn vandaag niet actief: Coppa "
     "Italia en DFB Pokal, en dat klopt - die hebben geen ronde. VIER actieve sportkeys kent de "
     "repo niet: soccer_brazil_serie_b, soccer_germany_liga3, soccer_sweden_superettan en "
     "soccer_uefa_nations_league. Alle vier vallen buiten de Run A-runlijst en zijn dus werk voor "
     "Run B en Run C; ze staan hier zodat die runs ze niet opnieuw hoeven te zoeken. "
     "DE BESTE PRIJS KOMT VANDAAG OPVALLEND VAAK VAN EEN BEURS: twee van de vijf gepubliceerde "
     "regels staan op Matchbook na 2% commissie, en een derde op Pinnacle.")

note("betexplorer", "ok",
     "31 okt (run A): zestien fixturepagina's opgehaald met fetch_league_fixtures, geen enkele "
     "fout - Premier League 21 rijen, Championship 24, La Liga 19, Bundesliga 17, Ligue 1 15, "
     "Eredivisie 17, Serie A 11, Primeira Liga 9, Belgian Pro League 10, Super Lig 9, Scottish "
     "Premiership 9, Ekstraklasa 9, plus de vijf bekerpagina's. Het marktgemiddelde komt van 10 "
     "tot 16 boeken per duel en wordt gebruikt waarvoor het bedoeld is (§1a): het "
     "kalibratieblok van §6e en poort 8, niet de bet zelf - die loopt vandaag bij alle 53 duels "
     "op de beste prijs. De vijf bekers als TWEEDE BRON op de vraag of er een ronde is: FA Cup "
     "eerstvolgend 6 november, League Cup 15 december, Coppa Italia 1 december, KNVB Beker 15 "
     "december, DFB Pokal geen teamparen op de pagina. "
     "EEN AFWIJKING, EN DE RICHTING IS DE VEILIGE: `ra_oct31_bevestiging.py` legt de twee bronnen "
     "over alle 16 competities naast elkaar en ze zijn het 15 van de 16 keer eens, 53 duels tegen "
     "52. Het verschil is de Eredivisie: Fotmob heeft Cambuur - Go Ahead Eagles (21:00 NL) en de "
     "BetExplorer-fixturepagina niet. Opgelost met een DERDE bron in plaats van door een van de "
     "twee te geloven: The Odds API noteert het duel op 2026-10-31T20:00:00Z met tien boeken, dus "
     "het bestaat en het staat terecht in de run. De tweede bron ziet er dus een MINDER dan de "
     "eerste, en dat is de onschuldige kant - het gevaar van 6 oktober was het omgekeerde, toen "
     "BetExplorer vijf FA Cup-duels had die Fotmob niet had. Een duel dat de primaire bron wel "
     "heeft, kan niet door een gat in de tweede bron verdwijnen. GEEN ACTIE, wel genoteerd: als "
     "deze pagina structureel laat-toegevoegde duels mist, is ze als tweede bron zwakker dan ze "
     "lijkt.")

note("understat", "ok",
     "31 okt (run A): ALLE VIJF de gedekte competities spelen vandaag (Premier League, La Liga, "
     "Bundesliga, Serie A, Ligue 1) - de eerste keer deze maand dat dat zo is - en Understat "
     "leverde een tweede, onafhankelijk xG-model voor de duels waarin beide ploegen vorig seizoen "
     "in zijn tabel stonden. Voor de promovendi levert hij niets, wat te verwachten is. Geen "
     "fout, geen sleutel nodig. Blijft genormaliseerd op het EIGEN competitiegemiddelde van "
     "Understat (§4: die ligt structureel ~0,13 xG per ploeg per duel hoger dan Fotmob) en gaat "
     "mee in het kalibratieblok, niet in my_prob.")

note("api_football", "plan_limited",
     "31 okt (run A): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker van "
     "27 september 2026 en geen storing - hij wil hier geen geld aan uitgeven. Niet als gat en "
     "niet als actiepunt melden (§3). De kanskant komt van Fotmob (alle competities) en Understat "
     "(vijf, vandaag alle vijf spelend); zolang die twee leveren is §2 gedekt. Fotmob leverde "
     "vandaag voor alle 53 duels, dus de uitzondering van §3 punt 3 is niet aan de orde.")

note("settling", "ok",
     "31 okt (run A): gebruikt bij het afwikkelen van 7 picks en 5 schaduwrijen over de "
     "daglijsten van 30 en 31 oktober, zonder een enkele verkeerde koppeling - alle 12 rijen "
     "kregen een wedstrijd met een plausibele uitslag. ALLE TWAALF ZIJN COMPETITIEWEDSTRIJDEN, "
     "dus er is geen verlenging of strafschoppenreeks en de eindstand IS de stand na 90 minuten "
     "(§6d); er hoefde geen doelpuntminuut te worden opgezocht. Dat is nagetrokken en niet "
     "aangenomen. De picks stonden een dag open, zoals het hoort. OPENSTAAND, onveranderd: niet "
     "nagegaan of de oude, te soepele naamregel in het verleden al eens een verkeerde uitslag "
     "heeft weggeschreven - dat is een audit over 67 rundagen.")

note("promotion_omrekening", "gerepareerd",
     "31 okt (run A): DE BEVINDING VAN DEZE RUN, en ze raakt de rekencode en niet een bron. "
     "§4 ('Promovendi: eerst omrekenen, dan pas NONE') is per PLOEG ondubbelzinnig: LIGHT binnen "
     "het gemeten bereik van conversion_in_range, NONE erbuiten, nooit FULL. De stap van ploeg "
     "naar DUEL stond nergens in code: elk runscript rekende die zelf uit met een kale "
     "toewijzing, `tier_box[0] = \"NONE\" if not conv.in_range else \"LIGHT\"`, en side_stats "
     "wordt twee keer aangeroepen (thuis, dan uit). De tweede aanroep overschreef dus de eerste. "
     "Stond de buitenbereik-ploeg THUIS en de andere erbinnen, dan werd NONE stil weer LIGHT en "
     "was het duel speelbaar; stond hij UIT, dan ging het goed - en daardoor was de fout maar "
     "half zichtbaar. VANDAAG RAAKTE HET TWEE VAN DE 53 DUELS, beide met de buitenbereik-ploeg "
     "thuis: Hull City - Ipswich Town (Hull City verdediging 1.102 buiten 0.284-1.022) en "
     "Erzurumspor FK - Corum FK (Erzurumspor verdediging 0.483 buiten 0.497-1.124). Het eerste "
     "was met Over 2.5 @1,9212 en +17,13 pp DE HOOGSTE EDGE VAN DE DAG, hoger dan alle vijf de "
     "gepubliceerde regels, en het haalde de LIGHT-lat van 16,0 pp - het zou boven aan de lijst "
     "zijn gepubliceerd. GEREPAREERD: `promotion.match_tier()` is nieuw en voegt de tiers van de "
     "twee kanten samen met 'de zwakste wint'; het runscript roept die aan in plaats van zelf toe "
     "te wijzen. De reparatie zit in scripts/ en niet alleen in het wegwerpscript van vandaag, "
     "want anders kopieert de run van morgen de fout terug - dezelfde les als branchaudit.py "
     "(29 sep) en progress.resumed_count (16 okt). promotion.py selftest staat op ALLES OK, de "
     "doctest van de nieuwe functie slaagt, en de uitkomst van de run is bit-voor-bit gelijk aan "
     "de handmatige reparatie. DE HISTORIE IS NAGELOPEN: acht duels waar de twee kanten hierover "
     "van mening konden verschillen; bij vijf stond de buitenbereik-ploeg uit en kwam er correct "
     "NONE uit, bij drie stond hij thuis - Exeter City - Rotherham United (3 okt), Girona - "
     "Mallorca (4 okt) en Celta Fortuna - Tenerife (19 okt). De eerste twee zijn een "
     "GEPUBLICEERDE BET geworden en BEIDE GEWONNEN, dus er is geen geld mee verloren; ze hadden "
     "niet mogen worden gespeeld. Die rijen zijn NIET herschreven - historie, geen meting, "
     "dezelfde keuze als bij de resumed_count van voor 16 okt, en twee op 429 afgerekende bets "
     "verschuift geen cijfer in §6d. OPENSTAAND: of ze alsnog ongeldig moeten is een besluit "
     "voor de gebruiker en staat in het dagrapport.")

H["last_run"] = {"run": "A", "date": "2026-10-31",
                 "note": "DRIEENVIJFTIG duels in het inzetvenster over TWAALF competities - de "
                         "drukste dag van de maand, en met 53 tegen een zaterdagcap van 55 het "
                         "dichtst bij de cap dat deze routine deze maand is gekomen. Niets "
                         "afgekapt. Geen beker heeft een ronde en geen Europees toernooi speelt; "
                         "dat is bij TWEE bronnen nagetrokken. 33 duels op FULL, 18 op LIGHT en "
                         "TWEE op NONE. De twintig niet-FULL duels hebben allemaal een "
                         "omgerekende ploeg - bijna veertig procent van het programma en de "
                         "grootste groep van deze maand, dus de omrekening was vandaag de "
                         "hoofdroute en geen randgeval. VIJF REGELS, alle vijf een Over/Under "
                         "(drie Over, twee Under): Middlesbrough - Charlton Under 3.5 @1,87 "
                         "(+13,45 pp tegen de VERZWAARDE lat van 10,0), Bayer Leverkusen - VfB "
                         "Stuttgart Over 3.5 @1,87 (+10,74), AFC Bournemouth - Leeds United Over "
                         "2.5 @1,94 (+9,58), Moreirense - Estrela da Amadora Over 2.5 @2,1368 "
                         "(+9,41) en Anderlecht - Westerlo Under 3.5 @1,7742 (+7,77, OP RANGORDE "
                         "onder de lat). De eerste vier halen hun lat op BEIDE schalen, en dat is "
                         "ongewoon - sinds §5b op 20 september de drempel in een afkapping "
                         "veranderde stond er bijna elke dag minstens een regel eronder. "
                         "DE BEVINDING: de data_tier van een DUEL was die van zijn TWEEDE kant, "
                         "waardoor een omrekening buiten het gemeten bereik bij de thuisploeg "
                         "stil werd overschreven. Dat raakte vandaag Hull City - Ipswich Town, "
                         "met +17,13 pp DE HOOGSTE EDGE VAN DE DAG, die daardoor bijna was "
                         "gepubliceerd terwijl hij onder de regels niet mocht bestaan. "
                         "Gerepareerd in scripts/promotion.py (match_tier), en twee oudere "
                         "gepubliceerde picks van 3 en 4 oktober zijn er in het verleden langs "
                         "gekomen - beide gewonnen, niet herschreven. Poort 9 hield de Under 3.25 "
                         "van Anderlecht tegen (+8,14 pp tegen 10,0) en liet de 3.5 van dezelfde "
                         "wedstrijd door op rangorde met +7,77 pp: de selectie met de LAGERE edge "
                         "is de gepubliceerde, en dat gat tussen §5b en §1h staat sinds 28 "
                         "oktober bij de gebruiker - vandaag voor de derde keer in vier "
                         "rundagen. Poort 8 hield 35 selecties over TWAALF wedstrijden tegen, "
                         "waaronder Preston +0.75 met +16,67 pp (de hoogste geblokkeerde edge van "
                         "de dag); poort 8 ruw geen enkele. tweede_methode vangt 552 van de 778 "
                         "doorgerekende selecties - 71%, de derde dag op rij boven de 70%. "
                         "Pinnacle is het met alle vier de meetbare regels oneens, maar staat op "
                         "de Under-kant vandaag opvallend in balans met het eigen model (-0,07 pp "
                         "over 52 paren). STAGE 0: 7 picks afgewikkeld, 2 gewonnen en 5 verloren, "
                         "en 5 schaduwrijen die ALLE VIJF verloren zijn - de poorten deden hun "
                         "werk op de dag dat de lijst het slecht deed. Drie van de vier "
                         "doelpuntenverliezers waren Unders die uitliepen; die reeks staat nu op "
                         "+0,648 doelpunt per duel over 111 gevallen, z = +4,12. Nul "
                         "bronstoringen, 74 van 9255 credits."}
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

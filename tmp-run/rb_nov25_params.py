"""De `parameters`-tekst van Run B, 25 nov 2026 — apart gehouden zodat `rb_nov25_publiceer.py`
alleen de rekenlogica van 1 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **Twee regels, en GEEN VAN BEIDE haalt zijn eigen lat.** Beide staan volledig op rangorde (§5b).
* **Regel 2 is een LIGHT-Under en is daarmee door GEEN ENKELE rem op de doelpuntenkant getoetst** —
  poort 9 geldt sinds het besluit van 12 okt 2026 alleen op `FULL`.
* **Twee van de zeventien competities spelen**, met vijf duels; Serie B levert er vier en Série A
  (BRA) één. Dat is de kleinste runlijstdag van deze maand.
* **Poort 7 heeft voor het eerst sinds 17 november weer selecties tegengehouden** — drie, alle drie
  op de uitkant van Pisa – Modena.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0392, b=0,0253 op "
            "8724 afgerekende gevallen, fitted_through 2026-11-24. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band en verlaagt "
            "alleen onder ongeveer 35%; bij beide regels van vandaag tilt hij de edge ongeveer een "
            "vol procentpunt op (regel 1 van +6,47 naar +7,56 pp, regel 2 van +11,12 naar "
            "+12,11 pp). De vlag bet_beide is de controle en niet de redenering (§5a), maar ze "
            "zegt vandaag bij BEIDE regels weinig: geen van beide haalt zijn lat op geen van beide "
            "schalen, dus er is geen regel die bij de gratie van §1g bestaat. LEES DE FIT NIET ALS "
            "'het model is goed gekalibreerd en dus goed': hij is gekalibreerd op de "
            "ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit in "
            "de GESELECTEERDE groep — vandaag staat die op z = +4,99 over 150 gespeelde Unders. "
            "Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "GEEN_VAN_DE_TWEE_REGELS_HAALT_ZIJN_EIGEN_LAT": (
            "Dat is het verschil met gisteren, toen Bradford City – Barnsley Under 3 met +11,65 pp "
            "boven een verzwaarde lat van 10,0 uitkwam. Vandaag komen BEIDE gepubliceerde regels "
            "uitsluitend op rangorde: Atlético-MG – Corinthians Draw No Bet — Atlético Mineiro "
            "@1,75 (1xBet) staat op +7,56 pp bij een FULL-lat van 8,0 — 0,44 procentpunt tekort — "
            "en Pisa – Modena Under 2.5 @2,0388 (Matchbook, beurs: 2,06 bruto en 2,0388 na 2% "
            "commissie) op +12,11 pp bij een LIGHT-lat van 16,0, dus 3,89 procentpunt tekort. §5b "
            "laat de drempel sinds 20 sep 2026 aan het EIND snijden: staan er minder selecties "
            "boven de lat dan er regels in de lijst passen, dan bepaalt de rangorde de lijst en "
            "gaat de drempel mee als LABEL per regel. Lees deze twee regels dus zoals §5b ze "
            "bedoelt — een RANGSCHIKKING van wat het model vandaag het sterkst vindt, geen "
            "gevonden voordeel. MAX_SHORTLIST is op woensdag 2 sinds de wijziging van 18 nov 2026 "
            "(ranking.max_shortlist, bindt sinds 19 nov), er passen dus twee regels en er staan "
            "er twee: de lijstlengte bindt NIET en er is geen enkele "
            "gekwalificeerd_niet_gepubliceerd-regel. De reeks `lijstlengte` blijft daarmee op 32 "
            "kandidaten staan, alle 32 afgewikkeld, 16 winnaars, +6,60u = +20,6% — de gebruiker "
            "kijkt er bij 100 gevallen opnieuw naar (§5b) en een run verzet MAX_SHORTLIST nooit "
            "op eigen initiatief. MAX_LIGHT_IN_SHORTLIST (2) bindt ook niet: één van de twee "
            "regels is LIGHT."
        ),
        "REGEL_2_IS_EEN_LIGHT_UNDER_EN_DAARMEE_DOOR_GEEN_ENKELE_REM_GETOETST": (
            "Dit is het punt dat vandaag vooraan hoort. Pisa – Modena Under 2.5 staat op de kant "
            "waar §6g de schade meet, en poort 9 KIJKT ER NIET NAAR: `unders.TIERS = (\"FULL\",)` "
            "sinds het besluit van de gebruiker van 12 okt 2026 (\"Twee hoeft nog niet op de "
            "zwakke data; eerst kijken wat deze rem doet\"). Een LIGHT-Under die de rangorde van "
            "§5b haalt wordt dus gepubliceerd zonder dat de verzwaarde lat van 10,0 hem ooit heeft "
            "aangeraakt — dat is geen omissie maar die keuze, en het is exact hetzelfde geval als "
            "Atalanta – Venezia van 12 oktober en Lillestrøm – Molde van 11 oktober. Poort 9 hield "
            "vandaag NUL selecties tegen, want er was geen enkele FULL-Under boven de 8,0 pp: de "
            "twee FULL-Unders van Padova – Sampdoria (Under 2.5 @1,76 op +5,31 pp en Under 2.25 "
            "@1,98 op +4,69 pp) sneuvelden al eerder, op poort 6. De reeks `doelpunten_onder` "
            "blijft daarmee op 53 kandidaten, 52 afgewikkeld, 34,6% trefkans, -18,65u = -35,9% "
            "rendement — ruim boven de ~30 van §6d en het argument om de rem te laten staan. "
            "Een run breidt die poort niet op eigen initiatief uit naar LIGHT (§1h punt 3: de "
            "vraag is op 12 oktober gesteld en beantwoord; stel hem niet opnieuw)."
        ),
        "DE_UNDER_KANT_VAN_DE_SELECTIE_STAAT_OP_Z_IS_PLUS_4_99_EN_REGEL_2_STAAT_DAAROP": (
            "margins.py goalbias splitst het MODEL van de SELECTIE en die twee mogen nooit worden "
            "opgeteld. Over alle 2478 doorgerekende duels staat het model op +0,020 doelpunt per "
            "duel (z = +0,56, dus de lambdas kloppen), maar over de 150 duels waar werkelijk een "
            "Under is gespeeld op +0,677 doelpunt per duel (z = +4,99). De routine speelt Under "
            "dus juist daar waar haar eigen doelverwachting te laag staat, en regel 2 van vandaag "
            "staat op diezelfde kant — nu zonder dat poort 9 ernaar heeft gekeken. De VORM geeft "
            "op deze specifieke lijn beperkte steun: P(Under 2.5) staat voorspeld 42,3% tegen "
            "werkelijk 40,9% over 2478 duels, 1,4 pp te hoog. Het probleem zit in de SELECTIE en "
            "niet in het grid. Eén dag is geen reeks (§6d) en dit getal hoort in het rapport en "
            "niet in een parameter. De lambdas van regel 2: xG 1,253 + 1,205 = 2,458 verwachte "
            "doelpunten, splits 0,689 + 0,888 = 1,577 — beide onder de lijn van 2,5, de "
            "splitsmethode ruim."
        ),
        "PINNACLE_IS_HET_MET_REGEL_2_HET_MEEST_ONEENS_VAN_ALLE_VIER_DE_PAREN": (
            "De tweede toets van Stage 5 stap 2, en ze wijst dezelfde kant op als de meting "
            "hierboven. Op de doelpuntenkant zijn er vier toetsbare (duel, lijn)-paren; de "
            "GROOTSTE afwijking van alle vier is precies de gepubliceerde Under. PISA – MODENA: op "
            "lijn 2,50 geeft het eigen model P(Under) 55,5% tegen 48,5% bij Pinnacle, +7,01 pp, "
            "bij een Pinnacle-marge van 3,2%. Gemiddeld over alle vier staat het model +3,39 pp "
            "boven Pinnacle op de Under-kant, bij 3 van 4 erboven; over de twee zuivere halve "
            "lijnen (zonder push) +6,25 pp bij 2 van 2. De bet is dus niet alleen aan de verkeerde "
            "kant van de gemeten scheefstand, hij is er het uiterste geval van. Op de 1X2 zijn er "
            "vier toetsbare duels met een gemiddelde absolute afstand van 2,69 pp bij een "
            "gemiddelde Pinnacle-marge van 3,57% — dat is de KLEINSTE gemiddelde afstand van deze "
            "maand, en bij regel 1 is het eigen model het met Pinnacle óók vrij eens: "
            "Atlético-MG 44,4% tegen 40,2% bij Pinnacle (+4,14 pp), het grootste verschil van de "
            "vier maar in absolute zin klein. DEZE GETALLEN GAAN NIET IN my_prob en veranderen "
            "geen enkele pick van vandaag (§2) — ze horen in de vergelijking, en daarom staan ze "
            "hier en bij de bets in het runrapport."
        ),
        "POORT_5_VANGT_DRIE_VAN_DE_VIJF_SELECTIES_WEG_EN_POORT_7_BIJT_VOOR_HET_EERST_WEER": (
            "Over de 5 duels zijn 58 selecties doorgerekend, verdeeld over alle zes de markten: "
            "16 Asian Handicap, 12 1X2, 12 Over/Under, 8 Draw No Bet, 8 BTTS en 2 Double Chance. "
            "Daarvan sneuvelden er 35 op poort 5 ('data conflicterend' — de twee methodes "
            "verslaan de markt niet dezelfde kant op), oftewel 60% van alles; daarna 15 op de "
            "edge-afkapping, 3 op de koersband, 3 op poort 7 (context) en 2 op poort 6 "
            "(robuustheid). Poort 8 (underdog) en poort 9 (Under-lat) hielden NUL selecties tegen. "
            "POORT 7 IS HET VERMELDEN WAARD: hij ging dicht op de UITKANT van twee duels — "
            "Sampdoria mist 51% van zijn selectiewaarde tegen 11% bij Padova (Esposito, Di Pardo "
            "en Verschaeren), Modena 34% tegen 4% bij Pisa (Zampano, Tonoli, Caso) — en bij Pisa "
            "– Modena kostte dat drie selecties die anders waren doorgerekend: Asian Handicap "
            "Modena +0,25 @1,81 (+4,25 pp), 1X2 Modena wint @3,17 (+3,62 pp) en Draw No Bet "
            "Modena @2,14 (+3,11 pp). Dat is dezelfde wedstrijd die regel 2 levert, maar op de "
            "ANDERE kant: de gepubliceerde Under heeft side = None en daar staat poort 7 per "
            "ontwerp altijd open (§1c). De reeks `context` staat op 157 kandidaten, 152 "
            "afgewikkeld, 34,2% trefkans, -35,37u = -23,3% — de duidelijkst besparende poort van "
            "alle negen. NUL van de 58 selecties viel op poort 6 bij de gepubliceerde regels; de "
            "twee die er wél op sneuvelden zijn de FULL-Unders van Padova – Sampdoria, met een "
            "zwakste stand van -1,06 en -1,32 pp over het (shrink, rho)-grid."
        ),
        "DE_CAP_BINDT_NIET_EN_VIJFTIEN_COMPETITIES_SPELEN_NIET": (
            "TWEE van de zeventien competities spelen, met 5 duels in het inzetvenster, op een "
            "WOENSDAGcap van 40 (ranking.max_deep_analyses). Er is dus NIETS afgekapt en de "
            "dekkingstabel krijgt geen AFGEKAPT-regel. De vijftien die niets op de kalender hebben "
            "zijn Czech First League, Greek Super League, Eliteserien, Allsvenskan, Croatian HNL, "
            "Hungarian NB I, Romanian SuperLiga, Segunda División, 2. Bundesliga, Swiss Super "
            "League, Austrian Bundesliga, Keuken Kampioen Divisie, English League One, English "
            "League Two en MLS — alle vijftien GEEN WEDSTRIJD en geen gat (§3 Stage 2). Dat is "
            "langs DRIE wegen nagetrokken: idcheck.py geeft 33 van 33 groen met afsluitcode 0 "
            "(juist de stille competities, want een fout id geeft geen foutmelding maar nul "
            "wedstrijden — prompts/run-b.md, het Serie B-id van 18-20 september), BetExplorer "
            "bevestigt per competitie 0 duels in het venster en noemt de eerstvolgende ronde, en "
            "runwindow.py bepaalt het venster. De bevestiging door een tweede methode is daarmee "
            "17 van 17 eens, 5 duels tegen 5. Dit is de kleinste runlijstdag van november; de "
            "Engelse divisies en MLS spelen weer in het weekend, Serie B pas op 4 december."
        ),
        "BEIDE_SPELENDE_COMPETITIES_HEBBEN_xG_EN_EEN_SPORTKEY": (
            "Serie B (ITA, id 86) en Série A (BRA, id 268) hebben beide xG bij Fotmob in zowel het "
            "vorige als het lopende seizoen, en beide hebben een sportkey bij The Odds API "
            "(soccer_italy_serie_b, soccer_brazil_campeonato). Er is vandaag dus geen enkel duel "
            "dat op doelpunten-als-sterktemaat moet draaien en geen enkel duel waarvan de prijs "
            "het gratis BetExplorer-marktgemiddelde is met een niet-herleidbare bookmaker (§1a). "
            "De vijf competities zonder xG (Czech First League 122, Croatian HNL 252, Hungarian NB "
            "I 212, Romanian SuperLiga 189, Keuken Kampioen Divisie 111) spelen vandaag alle vijf "
            "niet. Beide competities kregen de volle bulk (h2h+spreads+totals, 3 credits elk = 6), "
            "en vier duels met een kandidaat-edge kregen in ronde twee BTTS (4 credits): 10 "
            "credits deze run, 18959 over en 1041 gebruikt deze maand op een plafond van 1579. De "
            "marktbalans van §1a is gehaald, 2 van 2 competities met zowel een uitkomst- als een "
            "doelpuntenmarkt: 20 selecties op een doelpuntenmarkt (12 O/U + 8 BTTS) tegen 38 op "
            "een uitkomstmarkt (16 AH + 12 1X2 + 8 DNB + 2 DC). Beste prijs tegen het "
            "BetExplorer-gemiddelde: +4,72% tot +6,82% per duel, precies de orde die §1a op 5 sep "
            "2026 heeft gemeten. api_check.py meldt wel dat Ligue 2 (FRA) vandaag niet actief is "
            "bij The Odds API en dat vijf actieve sportkeys niet in de repo staan (Brazil Série B, "
            "EFL Trophy, 3. Liga, Superettan, UEFA Nations League) — geen van die vijf staat op "
            "een runlijst, dus het is een aantekening en geen gat."
        ),
        "EEN_PROMOVENDUS_UIT_DE_SERIE_C_IS_NOG_ALTIJD_NIET_OM_TE_REKENEN": (
            "DRIE van de vijf duels hebben een ploeg zonder stand in het vorige seizoen en gingen "
            "langs de omrekening van §4; TWEE lukten en EEN kwam op data_tier = NONE. Cremonese en "
            "Pisa zijn degradanten uit de Serie A (TIER1-route) en zijn wél om te rekenen — beide "
            "duels komen daardoor op LIGHT. Arezzo niet: ONDER Serie B (ITA) KENT "
            "promotion.TIER2 GEEN DIVISIE, de Serie C ligt er wel onder maar is niet gemeten, dus "
            "Mantova – Arezzo is het enige duel van vandaag zonder kansbron. LET OP DE "
            "FOUTMELDING, want die leest de oorzaak verkeerd: hij zegt \"degradant: 'Arezzo' staat "
            "niet in de stand van Serie A (ITA) 2025/2026\" en noemt dus alleen de TIER1-tak, "
            "terwijl Arezzo juist van ONDEREN komt. Exact dezelfde misleidende melding als bij de "
            "Spaanse Primera Federación (notitie van 4 okt 2026 in coverage.json) en als bij "
            "Benevento, Ascoli en Vicenza gisteren. Dit is een STRUCTUREEL gat en geen incident: "
            "het kostte op 24 november drie van de zes Italiaanse duels en vandaag één van de "
            "vier. §4 verbiedt extrapoleren; de uitweg is de Serie C meten, niet de rand oprekken."
        ),
        "GEEN_VERPLAATSTE_WEDSTRIJD_EN_EEN_BRAZILIAANS_DUEL_NA_MIDDERNACHT": (
            "context.check_venue sloeg bij geen van de vijf duels aan: alle vijf worden in het "
            "eigen stadion van de thuisploeg gespeeld. Dat is een constatering en geen reden tot "
            "gerustheid: §1c zegt dat deze controle het geval vangt waarin een ploeg buiten de "
            "eigen deur speelt zonder dat de bronnen dat verwerken, en NIET dat een fixture van "
            "eigenaar is gewisseld — dat is nieuws en geen data, en een geplande run heeft geen "
            "nieuwsbron. Van de vijf duels leverden er vijf een contextblok op (0 ctx-fouten), met "
            "datarijkdom tussen 5,0 (de vier Italiaanse duels) en 7,5 (Atlético-MG – "
            "Corinthians). Atlético-MG – Corinthians trapt af om 00:00 NL in de nacht van 25 op "
            "26 november — dat is 20:00 lokale tijd in Belo Horizonte, en het duel staat op de "
            "daglijst van VANDAAG (RunMatch.source_day = 2026-11-25). playable = True: de "
            "gebruiker zet tussen 07:00 en 08:00 in en de aftrap ligt zestien uur daarna. Dat is "
            "precies waarom runwindow.py bestaat (§3 Stage 1, de MLS-fout van 24 sep 2026); de "
            "vier Italiaanse duels trappen af tussen 19:00 en 20:00 NL."
        ),
        "STAGE_0_HAD_NIETS_AF_TE_WIKKELEN_EN_DRIE_PICKS_STAAN_TERECHT_OPEN": (
            "ledger.py open en shadow.py open gaven vanochtend geen enkele afwikkelbare regel. Drie "
            "picks staan open en alle drie terecht. Twee zijn van Run A van VANDAAG (Paris "
            "Saint-Germain – Roma Under 3.5 en Atlético Madrid – Viking Under 4, aftrap 21:00 NL) "
            "en moeten nog beginnen. De derde is de MLS-pick van Run B van gisteren — San Jose "
            "Earthquakes – Houston Dynamo FC Over 2.5 — en die LIEP bij het begin van deze run "
            "werkelijk nog: Fotmob zet `finished` niet op true en meldt 0,1 uur na de aftrap. §0 "
            "zegt dan letterlijk wachten; de terugval op de klok (SETTLE_FALLBACK_HOURS = 2,0) "
            "geldt UITSLUITEND wanneer er géén bronstatus te krijgen was, en die is er hier wel. "
            "Elf schaduwrijen van Run A van vandaag staan om dezelfde reden open. De volgende run "
            "wikkelt ze af. Er is vandaag dus GEEN afwikkelingsreflectie te schrijven (§3 Stage 0, "
            "12 okt 2026) en dat is geen overgeslagen stap maar een lege dag."
        ),
        "STAGE_MIN_2_DE_TAKKEN_ZIJN_NAGELOPEN_NA_EEN_UNSHALLOW_EN_ER_VIEL_NIETS_TE_MERGEN": (
            "De container kreeg de repo opnieuw als ONDIEPE kloon ("
            "`git rev-parse --is-shallow-repository` gaf true, 58 commits lokaal, knip op 15 nov "
            "2026). In die stand toonden 89 van de 101 takken 'eigen' commits, tot 730 stuks, en "
            "gaf `git merge-base` niets terug — exact het valse alarm dat §3 Stage -2 beschrijft. "
            "Na `git fetch --unshallow origin` (797 commits) heeft GEEN ENKELE tak nog één commit "
            "die HEAD mist: 101 van 101 op nul. HEAD liep bij het begin van deze run gelijk met "
            "origin/main (4254f58, de afronding van Run A van vandaag). picks.jsonl bevatte geen "
            "openstaande pick van een run die op een andere tak nooit is afgewikkeld — de drie "
            "open regels zijn van vandaag en gisteren en staan hierboven. Dat is de volledige "
            "Stage -2: de ondiepe kloon is de reden dat deze controle elke run opnieuw moet, en de "
            "reden dat ze elke run opnieuw niets vindt."
        ),
    }

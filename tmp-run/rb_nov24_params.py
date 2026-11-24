"""De `parameters`-tekst van Run B, 24 nov 2026 — apart gehouden zodat `rb_nov24_publiceer.py`
alleen de rekenlogica van 1 november hoeft te zijn.

Vijf dingen die vandaag vooraan horen:

* **Twee regels, en ANDERS DAN GISTEREN haalt de eerste zijn eigen lat wél.** Bradford City –
  Barnsley Under 3 staat op +11,65 pp bij een verzwaarde lat van 10,0; de tweede regel (MLS) komt
  volledig op rangorde.
* **ALLE VIER de selecties die vandaag alle poorten én hun drempel haalden staan in ÉÉN wedstrijd.**
* **Poort 9 heeft de gepubliceerde Under wél getoetst** — het gat van 22 en 23 november speelt
  vandaag niet.
* **Pinnacle is het met precies die Under het meest oneens van alle negen toetsbare paren.**
* **Vijf van de veertien duels komen op NONE uit, door twee STRUCTURELE gaten in de
  divisiekaart** (Serie C onder Serie B, Série B onder Série A (BRA)).

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0378, b=0,0244 op "
            "8646 afgerekende gevallen, fitted_through 2026-11-23. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band en verlaagt "
            "alleen onder ongeveer 35%. De vlag bet_beide is de controle en niet de redenering "
            "(§5a): bij regel 1 staat ze op True — Bradford komt ruw op +10,56 pp en herijkt op "
            "+11,65 pp en haalt de lat van 10,0 op BEIDE schalen, dus die regel bestaat niet bij "
            "de gratie van §1g. Bij regel 2 staat ze op False, maar dat zegt daar weinig: die "
            "regel haalt zijn lat op geen enkele schaal (ruw +5,15 pp, herijkt +6,19 pp, lat "
            "8,0). LEES DE FIT NIET ALS 'het model is goed gekalibreerd en dus goed': hij is "
            "gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de "
            "scheefstand die telt zit in de GESELECTEERDE groep — vandaag staat die op z = +4,95 "
            "over 148 gespeelde Unders. Daarom staat poort 8 nog aan en is poort 9 niet geschrapt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_CAP_BINDT_NIET_EN_DE_LIJSTLENGTE_OOK_NIET": (
            "VIJF van de zeventien competities spelen, met 14 duels in het inzetvenster, op een "
            "DINSDAGcap van 40 (ranking.max_deep_analyses). Er is dus NIETS afgekapt en de "
            "dekkingstabel krijgt geen AFGEKAPT-regel. De twaalf die niets op de kalender hebben "
            "zijn Czech First League, Greek Super League, Eliteserien, Allsvenskan, Croatian HNL, "
            "Hungarian NB I, Romanian SuperLiga, Segunda División, 2. Bundesliga, Swiss Super "
            "League, Austrian Bundesliga en Keuken Kampioen Divisie — alle twaalf GEEN WEDSTRIJD "
            "en geen gat (§3 Stage 2). Dat is langs DRIE wegen nagetrokken: idcheck.py geeft 33 "
            "van 33 groen met afsluitcode 0 (juist de stille competities, want een fout id geeft "
            "geen foutmelding maar nul wedstrijden — prompts/run-b.md, het Serie B-id van 18-20 "
            "september), BetExplorer geeft per competitie een niet-lege fixturelijst met de "
            "eerstvolgende ronde, en runwindow.py bepaalt het venster. MAX_SHORTLIST is op "
            "dinsdag 2 sinds de wijziging van 18 nov 2026 (ranking.max_shortlist, bindt sinds 19 "
            "nov). Er staan twee regels op een lijst van twee, dus de lijstlengte bindt NIET en "
            "er is geen enkele gekwalificeerd_niet_gepubliceerd-regel. De reeks `lijstlengte` "
            "blijft daarmee op 32 kandidaten staan, 31 afgewikkeld, +24,5% — de gebruiker kijkt "
            "er bij 100 gevallen opnieuw naar (§5b) en een run verzet MAX_SHORTLIST nooit op "
            "eigen initiatief."
        ),
        "REGEL_1_HAALT_ZIJN_LAT_WEL_EN_DAT_IS_HET_VERSCHIL_MET_GISTEREN": (
            "Bradford City – Barnsley Under 3 @1,82 (Coolbet) staat op +11,65 pp herijkt en "
            "+10,56 pp ruw, bij een lat die door poort 9 is verzwaard naar 10,0 pp — hij haalt "
            "die op beide schalen (bet_beide = True). Dat is de eerste gepubliceerde regel van "
            "deze runlijst sinds 22 november die NIET volledig op rangorde staat. Regel 2, San "
            "Jose Earthquakes – Houston Dynamo FC Over 2.5 @1,7252 (Matchbook, beurs: 1,74 bruto "
            "en 1,7252 na 2% commissie), staat op +6,19 pp bij een FULL-lat van 8,0 en komt er "
            "dus uitsluitend omdat §5b de drempel sinds 20 sep 2026 aan het EIND laat snijden en "
            "`toplist._cut` de lijst dan aanvult op selection_score. Lees die tweede regel zoals "
            "§5b hem bedoelt: een RANGSCHIKKING van wat het model vandaag het sterkst vindt, geen "
            "gevonden voordeel. MAX_LIGHT_IN_SHORTLIST (2) bindt niet: beide regels zijn FULL en "
            "er staat geen enkele LIGHT-regel op de lijst."
        ),
        "ALLE_VIER_DE_GEKWALIFICEERDE_SELECTIES_STAAN_IN_EEN_WEDSTRIJD": (
            "Van de 133 doorgerekende selecties haalden er VIER alle poorten én hun eigen "
            "drempel, en alle vier staan in Bradford City – Barnsley: Under 2.5 @2,3524 "
            "(+11,93 pp), Under 3 @1,82 (+11,65 pp), Under 2.75 @2,05 (+11,07 pp) en 'beide "
            "ploegen scoren — nee' @2,2152 (+8,26 pp). Dat is ÉÉN mening — er wordt in Valley "
            "Parade weinig gescoord — vier keer uitgedrukt, op drie lijnen van dezelfde markt "
            "plus de doelpuntenmarkt ernaast. De 0-of-1-regel van §1 publiceert er precies één "
            "van, en dat is Under 3 op de hoogste selection_score (7,755 tegen 6,628 en 6,496 en "
            "4,408). De andere drie zijn GEEN lijstlengte-afwijzing en horen niet in die reeks: "
            "de wedstrijd kreeg zelf een regel (regel van 7 okt 2026, rb_oct04_publiceer.py). "
            "Wat dit wél betekent: de dag heeft precies ÉÉN wedstrijd waar het model een echt "
            "voordeel ziet, niet vier."
        ),
        "POORT_9_HEEFT_DE_GEPUBLICEERDE_UNDER_WEL_GETOETST": (
            "Dit is het verschil met 22 en 23 november, toen geen van de gepubliceerde regels "
            "door enige rem op de doelpuntenkant was gegaan. Regel 1 is een Over/Under op de "
            "Under-kant met data_tier = FULL en valt daarmee precies binnen het bereik waar poort "
            "9 bindt (§1h, unders.BINDS_FROM = 12 okt 2026): unders.check geeft lat 10,0 terug en "
            "de melding 'Under met +11,65 pp, boven de verzwaarde lat van 10,0 pp (poort 9)'. De "
            "rem heeft dus gemeten en doorgelaten, in plaats van buiten het bereik te vallen. "
            "Poort 9 hield vandaag NUL andere selecties tegen; zijn reeks blijft op 53 "
            "kandidaten, 52 afgewikkeld, 34,6% trefkans, -18,65u = -35,9% rendement — ruim boven "
            "de ~30 van §6d en het argument om hem te laten staan."
        ),
        "DE_UNDER_KANT_VAN_DE_SELECTIE_STAAT_OP_Z_IS_PLUS_4_95_EN_REGEL_1_STAAT_DAAROP": (
            "margins.py goalbias splitst het MODEL van de SELECTIE en die twee mogen nooit worden "
            "opgeteld. Over alle 2453 doorgerekende duels staat het model op +0,024 doelpunt per "
            "duel (z = +0,68, dus de lambdas kloppen), maar over de 148 duels waar werkelijk een "
            "Under is gespeeld op +0,676 doelpunt per duel (z = +4,95). De routine speelt Under "
            "dus juist daar waar haar eigen doelverwachting te laag staat, en regel 1 van vandaag "
            "staat op diezelfde kant — nu wél door poort 9 getoetst, wat de waarschuwing verzacht "
            "maar niet wegneemt. De VORM geeft op deze specifieke lijn weinig steun aan een "
            "Under-overschatting: P(Under 3.0) staat voorspeld 63,8% tegen werkelijk 63,0% over "
            "2453 duels, 0,9 pp te hoog, tegen 1,4 pp op de 2.5-lijn. Het probleem zit in de "
            "SELECTIE en niet in het grid. Eén dag is geen reeks (§6d) en dit getal hoort in het "
            "rapport en niet in een parameter. De lambdas van regel 1: xG 1,689 + 0,855 = 2,544 "
            "verwachte doelpunten, splits 1,588 + 0,872 = 2,460 — beide ruim onder de lijn van 3."
        ),
        "PINNACLE_IS_HET_MET_REGEL_1_HET_MEEST_ONEENS_VAN_ALLE_NEGEN_PAREN": (
            "De tweede toets van Stage 5 stap 2, en ze wijst dezelfde kant op als de meting "
            "hierboven. Op de doelpuntenkant zijn er negen toetsbare (duel, lijn)-paren; de "
            "GROOTSTE afwijking van alle negen is precies de gepubliceerde wedstrijd. BRADFORD "
            "CITY – BARNSLEY: op lijn 2,75 geeft het eigen model P(Under) 59,7% tegen 47,0% bij "
            "Pinnacle, +12,66 pp, bij een Pinnacle-marge van 3,7%. Gemiddeld over alle negen "
            "staat het model +1,42 pp boven Pinnacle op de Under-kant, bij 5 van 9 erboven — de "
            "bet is dus niet alleen aan de verkeerde kant van de scheefstand, hij is er het "
            "uiterste geval van. Op de 1X2 zijn er negen toetsbare duels met een gemiddelde "
            "absolute afstand van 3,64 pp bij een gemiddelde Pinnacle-marge van 4,45%; de "
            "grootste staat bij REGEL 2 — San Jose Earthquakes – Houston Dynamo FC, waar het "
            "eigen model de thuisploeg 59,4% geeft tegen 44,2% bij Pinnacle (+15,21 pp), bijna "
            "het dubbele van de tweede grootste. Beide gepubliceerde regels staan dus op het duel "
            "waar het scherpste publieke oordeel het meest van het eigen model afwijkt. DEZE "
            "GETALLEN GAAN NIET IN my_prob en veranderen geen enkele pick van vandaag (§2) — ze "
            "horen in de vergelijking, en daarom staan ze hier en bij de bets in het runrapport."
        ),
        "POORT_5_VANGT_VIER_VAN_DE_VIJF_SELECTIES_WEG": (
            "Over de 14 duels zijn 133 selecties doorgerekend, verdeeld over alle zes de markten: "
            "44 Over/Under, 34 Asian Handicap, 26 1X2, 13 Draw No Bet, 12 BTTS en 4 Double "
            "Chance. Daarvan sneuvelden er 106 op poort 5 ('data conflicterend' — de twee "
            "methodes verslaan de markt niet dezelfde kant op), oftewel 80% van alles; daarna 11 "
            "op de edge-afkapping, 9 op poort 8 (underdog) en 3 op de koersband. Poort 6 "
            "(robuustheid), poort 7 (context) en poort 9 (Under-lat) hielden NUL selecties tegen. "
            "Vier selecties haalden alle poorten én hun drempel en alle vier staan in dezelfde "
            "wedstrijd (zie hierboven). Twee duels sneuvelden op poort 5 als wedstrijduitkomst: "
            "Crawley Town – Barnet en San Jose Earthquakes – Houston Dynamo FC. Bij dat laatste "
            "duel is dat het vermelden waard, want het is óók de wedstrijd die regel 2 levert: de "
            "best scorende kandidaat was Asian Handicap San Jose -0,5 @2,32 op +13,1 pp, en die "
            "sneuvelde op poort 5 (edge_xg +16,26 maar edge_split -3,57 — de splitsmethode "
            "verslaat de markt daar NIET). De gepubliceerde Over 2.5 van datzelfde duel heeft wél "
            "beide methodes mee (p_xg 59,0% en p_split 79,5% tegen een marktkans van 58,0%), maar "
            "de xG-methode slechts met +1,05 pp — en edge_robust_min staat op exact diezelfde "
            "+1,05. Dat is de krapste van de twee regels op elke as."
        ),
        "VIJF_VAN_DE_VEERTIEN_DUELS_OP_NONE_DOOR_TWEE_STRUCTURELE_GATEN": (
            "NEGEN van de 14 duels hebben een ploeg zonder stand in het vorige seizoen en gingen "
            "langs de omrekening van §4; VIJF kwamen op data_tier = NONE uit. Twee oorzaken, en "
            "beide zijn STRUCTUREEL en geen incident. (1) ONDER Serie B (ITA) KENT "
            "promotion.TIER2 GEEN DIVISIE: de Serie C ligt er wel onder maar is niet gemeten, dus "
            "Benevento, Ascoli en Vicenza — alle drie promovendi uit de Serie C — zijn niet om te "
            "rekenen. Dat kostte vandaag DRIE van de zes Italiaanse duels. LET OP DE FOUTMELDING, "
            "want die leest de oorzaak verkeerd: hij zegt \"degradant: 'Benevento' staat niet in "
            "de stand van Serie A (ITA) 2025/2026\" en noemt dus alleen de TIER1-tak, terwijl "
            "Benevento juist van ONDEREN komt. Exact dezelfde misleidende melding als bij de "
            "Spaanse Primera Federación (notitie van 4 okt 2026 in coverage.json), en het is de "
            "reden dat dit hier met zoveel woorden staat. (2) Série A (BRA) STAAT IN GEEN VAN "
            "BEIDE KAARTEN — prompts/run-b.md zegt dat expliciet: er is geen gemeten factor voor "
            "het paar Série A/Série B, dus Chapecoense komt op NONE. Het vijfde geval is anders "
            "en het is de poort die wérkt: Blackpool – Leicester City viel op "
            "conversion_in_range, dus Leicester City IS om te rekenen (degradant uit de "
            "Championship, TIER1-route) maar zijn omgerekende sterkte valt buiten het gemeten "
            "bereik. §4 verbiedt extrapoleren; de uitweg is de meting vergroten, niet de rand "
            "oprekken. Vier van de negen omrekeningen lukten wél en leverden drie LIGHT-duels "
            "(Virtus Entella – Hellas Verona, Bromley – Wycombe Wanderers, Stevenage – Sheffield "
            "Wednesday) plus Port Vale – Northampton Town."
        ),
        "ALLE_VIJF_DE_SPELENDE_COMPETITIES_HEBBEN_xG_EN_EEN_SPORTKEY": (
            "Dat is ongewoon voor deze runlijst en het hoort erbij, want het is precies de as "
            "waarop deze lijst normaal het zwakst staat. De vijf competities zonder xG bij Fotmob "
            "(Czech First League 122, Croatian HNL 252, Hungarian NB I 212, Romanian SuperLiga "
            "189, Keuken Kampioen Divisie 111) spelen vandaag ALLE VIJF niet, en dezelfde vijf "
            "zijn ook de competities zonder sportkey bij The Odds API. Er is vandaag dus geen "
            "enkel duel dat op doelpunten-als-sterktemaat moet draaien en geen enkel duel waarvan "
            "de prijs het gratis BetExplorer-marktgemiddelde is met een niet-herleidbare "
            "bookmaker (§1a). Alle vijf de spelende competities kregen de volle bulk "
            "(h2h+spreads+totals, 3 credits elk = 15), en zes duels met een kandidaat-edge kregen "
            "in ronde twee BTTS (6 credits): 21 credits deze run, 18984 over en 1016 gebruikt "
            "deze maand. De marktbalans van §1a is gehaald: 56 selecties op een doelpuntenmarkt "
            "(44 O/U + 12 BTTS) tegen 77 op een uitkomstmarkt (34 AH + 26 1X2 + 13 DNB + 4 DC). "
            "Neem dekking nooit over van een andere competitie in hetzelfde land — dat die regel "
            "vandaag niet bijt, maakt hem niet minder waar."
        ),
        "HET_MLS_DUEL_KOMT_VAN_DE_DAGLIJST_VAN_MORGEN": (
            "San Jose Earthquakes – Houston Dynamo FC trapt af om 04:00 NL en staat op de "
            "daglijst van 2026-11-25, niet op die van vandaag (RunMatch.source_day). Dat is exact "
            "het geval waarvoor runwindow.py bestaat (§3 Stage 1): een duel hoort bij de run "
            "wiens inzetvenster het nog kan bedienen, [08:00 NL 24 nov, 08:00 NL 25 nov), en op "
            "de oude UTC-datumregel was dit duel aan de run van MORGEN toegewezen en daar al "
            "afgetrapt aangekomen. playable = True; de gebruiker zet tussen 07:00 en 08:00 in en "
            "de aftrap ligt daarna. De andere dertien duels staan op de daglijst van vandaag en "
            "trappen af tussen 19:00 en 22:00 NL. MLS speelt de play-offs: Fotmob zet die onder "
            "'Major League Soccer Playoff' (id 957981) met parentLeagueId 130, dus runwindow.py "
            "vindt ze op het id uit coverage.json en het is dezelfde competitie."
        ),
        "STAGE_0_HAD_NIETS_AF_TE_WIKKELEN_EN_EEN_SCHADUWRIJ_STAAT_TERECHT_OPEN": (
            "ledger.py open en shadow.py open gaven vanochtend geen enkele afwikkelbare regel. De "
            "twee openstaande picks (Bodø/Glimt – LASK 'beide ploegen scoren — nee' en RB Leipzig "
            "– Lens Under 3.75) zijn van Run A van VANDAAG en moeten nog beginnen. Eén schaduwrij "
            "van gisteren staat nog open en dat is de regel en geen fout: "
            "shadow-2026-11-23-b-st--louis-city---los-angeles-fc stond bij het begin van deze run "
            "3,1 uur na de aftrap nog op pending. Fotmob vindt het duel (MLS Playoff) maar zet "
            "`finished` nog niet op true — en dat is hier ook juist, want de tweede helft was om "
            "03:27:57 NL begonnen en de run begon om ~04:05 NL: het duel LIEP werkelijk nog. §0 "
            "zegt dan letterlijk wachten; de terugval op de klok (SETTLE_FALLBACK_HOURS = 2,0) "
            "geldt UITSLUITEND wanneer er géén bronstatus te krijgen was, en die is er hier wel. "
            "De volgende run wikkelt hem af."
        ),
        "STAGE_MIN_2_DE_TAKKEN_ZIJN_NAGELOPEN_EN_ER_VIEL_NIETS_TE_VERENIGEN": (
            "branchaudit.py over 98 takken meldt 21 bladpaden in source-health.json en 4 rijen in "
            "shadow.jsonl die niet op origin/main staan. Alle 25 zijn nagetrokken en geen van "
            "beide groepen is een vondst. De 21 bladpaden zijn afgehandeld door Run A van VANDAAG "
            "(zie _merge_note in source-health.json): 18 stonden al op main onder "
            "history/detail_history — het pad-gewijze oordeel van branchaudit ziet die nestlaag "
            "niet — en de vijf werkelijk ontbrekende gedateerde snapshotblokken (Run A 19 en 21 "
            "nov, Run B 10 nov, Run C 10 en 16 nov) zijn die run verenigd; dat is hier opnieuw "
            "gecontroleerd en de blokken staan er. De 4 schaduwrijen van 3 oktober blijven weg, "
            "en dat is nu op de INHOUD nagetrokken in plaats van op het besluit van 7 november "
            "alleen: alle vier staan op main onder een id met achtervoegsel `-p8-0` "
            "(canada---peru, croatia---england, switzerland---slovenia, estonia---luxembourg), "
            "met dezelfde wedstrijd, dezelfde markt en dezelfde koers. Ze toevoegen zou "
            "dubbeltellen. picks.jsonl, coverage.json, calibration.jsonl en context-log.jsonl "
            "staan op VOLLEDIG. HEAD liep gelijk met origin/main bij het begin van deze run; de "
            "oudere takken tellen in de graaf honderden 'eigen' commits doordat main ooit is "
            "herschreven (geen merge-base), maar hun inhoud zit erin."
        ),
        "GEEN_VERPLAATSTE_WEDSTRIJD_EN_GEEN_CONTEXTBLOKKADE": (
            "context.check_venue sloeg vandaag bij geen van de 14 duels aan en poort 7 hield nul "
            "selecties tegen. Dat is een constatering en geen reden tot gerustheid: §1c zegt dat "
            "deze controle het geval vangt waarin een ploeg buiten de eigen deur speelt zonder "
            "dat de bronnen dat verwerken, en NIET dat een fixture van eigenaar is gewisseld — "
            "dat is nieuws en geen data, en een geplande run heeft geen nieuwsbron. Van de 14 "
            "duels leverden er 14 een contextblok op (0 ctx-fouten), met datarijkdom tussen 4,5 "
            "(San Jose Earthquakes – Houston Dynamo FC) en 6,5 (Vicenza – Carrarese)."
        ),
    }

"""De `parameters`-tekst van Run B, 18 nov 2026 — apart gehouden zodat `rb_nov18_publiceer.py`
alleen de rekenlogica van 8 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **ZESTIEN VAN DE ZEVENTIEN COMPETITIES HEBBEN NIETS OP DE KALENDER.** De interlandperiode liep
  tot 17 november en de Europese competities hervatten op 20 en 21 november. Dat is `GEEN
  WEDSTRIJD` en geen gat (§3 Stage 2), maar het is wél de uitkomst die `prompts/run-b.md` als
  STILLE FAALSTAND beschrijft — en dus op drie manieren nagetrokken.
* **BEIDE GEPUBLICEERDE REGELS STAAN OP DE UNDER-KANT, en het zijn precies de twee duels waar het
  model het verst boven het Pinnacle-oordeel op die kant staat** (+8,53 en +7,71 pp). Dat is het
  patroon waar §1g voor waarschuwt, en `margins.py goalbias` staat vandaag op de hardste stand van
  deze hele reeks: +0,658 doelpunt per duel over 136 gespeelde Unders, z = +4,62.
* **DE TWEEDE REGEL HAALT DE LAT VAN 8,0 PP NIET** en staat er op rangorde (§5b): Cruzeiro –
  Palmeiras Under 2,75 op +5,69 pp. Er passen drie regels in een woensdaglijst en er stonden er
  twee boven de ondergrens, dus de drempel snijdt niet en gaat als label mee.
* **DRIE VAN DE ZES DUELS KOMEN OP `data_tier = NONE`**, alle drie om de reden die
  `prompts/run-b.md` met zoveel woorden voorschrijft: een Braziliaanse promovendus heeft geen
  gemeten divisiepaar, dus `NONE` is daar de eerlijke uitkomst en geen storing.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0541, b=0,0349 op "
            "7983 afgerekende gevallen, fitted_through 2026-11-17. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over de hele speelbare band: +0,3 pp op 40%, +0,9 pp "
            "op 50%, +1,4 pp op 60%, +1,7 pp op 70%. Het ruwe model zei gemiddeld 33,3% en het "
            "gebeurde 33,3%. LEES DAT NIET ALS 'het model is goed gekalibreerd en dus goed': het is "
            "gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de scheefstand "
            "die telt zit in de GESELECTEERDE groep — zie `ledger.py stats`, waar het model over "
            "498 afgewikkelde bets 297,0 winnaars verwachtte en er 232 werden."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "ZESTIEN_VAN_DE_ZEVENTIEN_COMPETITIES_SPELEN_NIET_EN_DAT_IS_OP_DRIE_MANIEREN_NAGETROKKEN": (
            "LEES DIT EERST. Alleen Série A (BRA) heeft wedstrijden in het inzetvenster; de zestien "
            "andere competities van de runlijst staan op GEEN WEDSTRIJD. De oorzaak is bekend en "
            "geen storing: de interlandperiode liep tot en met 17 november en de Europese "
            "competities hervatten op 20 en 21 november. Run A van vanochtend had hetzelfde beeld "
            "(21 van 21 leeg). TOCH IS DIT DE UITKOMST DIE `prompts/run-b.md` ALS STILLE FAALSTAND "
            "BESCHRIJFT — een fout fotmob_id geeft geen foutmelding maar nul wedstrijden, en nul "
            "wedstrijden leest als GEEN WEDSTRIJD — dus op drie manieren nagetrokken. (1) "
            "`scripts/idcheck.py` bevindt alle 33 id's groen met een bruikbare stand, afsluitcode 0; "
            "dat is de controle die juist draait op de competities die vandaag stil zijn. (2) DE "
            "TWEEDE BRON IS HET OVER DE HELE LIJN EENS: BetExplorer geeft voor alle zestien stille "
            "competities nul duels in het venster en voor Série A (BRA) zes — 17 van 17 competities "
            "eens, 6 tegen 6 duels (`rb_nov18_bevestiging.py`). De eerstvolgende speelronde staat "
            "daar per competitie bij en valt steeds op 20 of 21 november, met English League One op "
            "20.11 21:00 als vroegste. (3) MLS is het geval waarvoor `scripts/runwindow.py` bestaat "
            "en het staat er vandaag netjes in: de reguliere competitie is afgelopen, BetExplorer "
            "geeft als eerstvolgende duels 20.11 01:30 en 20.11 04:00 (de play-offs), en "
            "`api_check.py` meldt `soccer_usa_mls` vandaag als actieve sportkey zonder duels in het "
            "venster. Geen enkele competitie krijgt BUITEN DATADEKKING of AFGEKAPT."
        ),
        "BEIDE_REGELS_STAAN_OP_DE_UNDER_KANT_EN_PRECIES_DAAR_WAAR_PINNACLE_LAGER_ZIT": (
            "DIT IS HET BELANGRIJKSTE VOORBEHOUD VAN VANDAAG en §6g eist dat het bij elke "
            "gepubliceerde Under staat. Beide regels zijn een Under op FULL-data: Corinthians – "
            "Botafogo Under 2,5 @2,00 en Cruzeiro – Palmeiras Under 2,75 @1,87. DRIE METINGEN DIE "
            "ALLE DRIE DEZELFDE KANT OP WIJZEN. (1) `margins.py goalbias` geeft over 136 gespeelde "
            "Unders +0,658 doelpunt per duel MEER dan de eigen lambda zei, z = +4,62 — DE HARDSTE "
            "STAND VAN DEZE REEKS (bij de invoering van poort 9 op 11 okt 2026 was dat +0,68 over "
            "49 duels bij z = +2,91, en op 8 november +0,612 over 130 bij z = +4,20). Op de "
            "Over-kant gebeurt dat niet: 73 duels, -0,341, z = -1,58. En over ALLE 2239 "
            "doorgerekende duels staat het model vlak (+0,029 per duel, z = +0,78), dus dit is een "
            "fout van de SELECTIE en niet van de lambdas — precies het onderscheid dat de leeswijzer "
            "van `goalbias` maakt. (2) De vormfout staat er bovenop: P(Under 2.5) is over die 2239 "
            "duels 1,5 pp te hoog (voorspeld 42,4%, werkelijk 40,9%) en P(Under 3.0) 0,9 pp. (3) OP "
            "DE PINNACLE-TOETS VAN STAGE 5 STAP 2 ZIJN DE TWEE GEPUBLICEERDE REGELS PRECIES DE TWEE "
            "GROOTSTE GATEN: Corinthians – Botafogo +8,53 pp op de Under-kant (eigen 0,576 tegen "
            "Pinnacle 0,491) en Cruzeiro – Palmeiras +7,71 pp (eigen 0,594 tegen 0,517), terwijl de "
            "derde doorgerekende wedstrijd — Grêmio – Bahia — er 3,03 pp ONDER staat. Gemiddeld "
            "+4,40 pp over drie (duel, lijn)-paren, 2 van 3 erboven. DAT IS EXACT HET PATROON WAAR "
            "§1g VOOR WAARSCHUWT: wie selecteert op de grootste edge, selecteert op de grootste "
            "modelfout. Van de geclaimde edge van beide Unders gaat ruwweg één tot twee procentpunt "
            "al op aan een gemeten fout die niets met deze ploegen te maken heeft. DAT MAAKT DE "
            "REGELS NIET ONGELDIG: Corinthians haalt zijn eigen lat van 8,0 pp EN de verzwaarde lat "
            "van poort 9 (10,0 pp op FULL) met +12,70 pp, en haalt beide schalen (`bet_beide` = "
            "True). Maar het voorbehoud is vandaag zwaarder dan op 8 november en er wordt op grond "
            "hiervan geen enkele lat verzet (§1h, §6d): een dag is geen reeks."
        ),
        "DE_TWEEDE_REGEL_HAALT_DE_LAT_NIET_EN_STAAT_ER_OP_RANGORDE": (
            "Cruzeiro – Palmeiras (Over/Under, Under 2,75 @1,87 bij Pinnacle, FULL) staat op +5,69 "
            "pp HERIJKT en +4,43 pp RUW, dus hij haalt de lat van 8,0 op geen van beide schalen: "
            "`failed_gate` = `edge`, `bet_ruw` = False en `bet_beide` = False. HIJ WORDT TOCH "
            "GEPUBLICEERD, EN DAT IS §5b EN GEEN VERSOEPELING. Sinds 20 september is de drempel geen "
            "poort meer maar een AFKAPPING: eerst per wedstrijd de sterkste selectie, dan één "
            "ranglijst over de hele runlijst, dan de bovenste MAX_SHORTLIST, en de drempel snijdt "
            "pas als er MEER selecties boven staan dan er regels passen. Vandaag passen er DRIE "
            "regels in een woensdaglijst en stonden er TWEE boven de ondergrens van 3,0 pp, dus "
            "bepaalt de rangorde de lijst en gaat de lat als LABEL mee. Deze regel haalt wel alle "
            "ZEVEN overgebleven poorten op de herijkte schaal — koersband, anti-circulariteit, "
            "datatier, tweede methode, robuustheid, context en underdog — plus poort 9, die bij een "
            "Under onder de 8,0 pp zelf `passed = True` geeft omdat `edge` daar de bindende poort is "
            "en niet poort 9. LEES HEM DUS ALS 'het beste wat er na Corinthians nog stond' en niet "
            "als een gevonden voordeel: zijn `selection_score` is 3,367 tegen 7,963 voor de regel "
            "erboven, en zijn eigen koers KOMT VAN PINNACLE — de scherpste bookmaker van de markt — "
            "terwijl Pinnacle's eigen de-vigde P(Under 2,75) 7,71 pp LAGER staat dan de onze. Dat is "
            "de zwakste van de twee op elke as die vandaag te meten was."
        ),
        "DRIE_VAN_DE_ZES_DUELS_OP_NONE_EN_ALLE_DRIE_OM_EEN_VOORGESCHREVEN_REDEN": (
            "Drie van de zes duels komen op data_tier = NONE uit en worden dus niet geanalyseerd "
            "(§2): Coritiba – Santos, Remo – Chapecoense en Flamengo – Athletico Paranaense. ALLE "
            "DRIE om dezelfde reden en die staat letterlijk in `prompts/run-b.md`: vier ploegen "
            "(Coritiba, Remo, Chapecoense en Athletico Paranaense) staan niet in de Série A-stand "
            "van 2025 en zijn dus promovendi uit de Série B, en voor dat divisiepaar is er GEEN "
            "GEMETEN FACTOR — `promotion.TIER2` kent geen Braziliaans paar, dus `convert` weigert "
            "met 'geen divisie boven of onder Série A (BRA) bekend'. §4 verbiedt daar een gepoolde "
            "factor op te zetten, en run-b.md noemt die uitkomst met zoveel woorden de eerlijke. Dit "
            "is GEEN lacune die vandaag is ontstaan: het is dezelfde route waarlangs Internacional – "
            "Coritiba op 3 november op NONE kwam. Van alle drie is de context wél opgehaald en "
            "gelogd (§1c eist dat ook bij tier NONE). WAT DAT MET DE DEKKINGSTABEL DOET, per "
            "competitie en niet per duel: Série A (BRA) heeft ook drie duels die wél zijn "
            "doorgerekend en staat dus op GEANALYSEERD."
        ),
        "POORT_5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
            "Van de 45 doorgerekende selecties sneuvelen er 31 op POORT 5, de bevestiging door een "
            "tweede methode (§1, voorwaarde 5) — 68,9% van alles. De rest: 7 op context (poort 7), 4 "
            "op `edge`, 1 op de koersband, en 2 selecties over 1 wedstrijd haalden alle negen "
            "poorten (beide op Corinthians – Botafogo, waarvan de Under 2,5 de hoogste score had en "
            "de BTTS-nee van 4,596 de 0-of-1-bet-regel niet overleefde). DAT IS DE POORT DIE GELD "
            "BESPAART: `shadow.py stats` meet `tweede_methode` vandaag op -1,9% over 293 "
            "afgewikkelde kandidaten — licht negatief, dus de afgewezen groep verliest. ER WORDT "
            "NIETS VERZET (§6d eist een richting over weken en niet een getal van een dag). En let "
            "op de omvang vandaag: bij 45 selecties over drie wedstrijden is 68,9% een handvol "
            "rijen, geen reeks."
        ),
        "ALLE_ZES_MARKTEN_HEBBEN_MEEGEDONGEN_EN_DE_LIJST_KOMT_UIT_DE_DATA": (
            "§1a eist dat zichtbaar is of een eenzijdige lijst uit de portemonnee komt of uit de "
            "data, en vandaag komt hij uit de data. De inkoop was zo breed als hij kon zijn: Série A "
            "(BRA) is de ENIGE spelende competitie en kreeg de volledige bulk-aanroep met h2h + "
            "spreads + totals (3 credits), plus BTTS in de tweede ronde voor alle DRIE de duels met "
            "een kandidaat-edge (3 credits). Alle ZES markten hebben werkelijk meegedongen: van de "
            "45 doorgerekende selecties waren er 13 Asian Handicap, 10 Over/Under, 9 1X2, 6 BTTS, 4 "
            "Draw No Bet en 3 Double Chance. Dat beide regels uit de Over/Under-markt komen is dus "
            "de uitkomst van `selection_score` over zes concurrerende markten en geen quotum; bets "
            "forceren om een verdeling te halen is precies wat §1 verbiedt. Credits: 3 aan de bulk "
            "plus 3 aan BTTS = 6 van een plafond van 744, en er staan nog 19379 van de 20000 van "
            "deze maand."
        ),
        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "6 duels in één van de zeventien competities op een WOENSDAGcap van 40 "
            "(`ranking.max_deep_analyses`), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. De datarijkdom liep van 4,5 tot 7,0; omdat er niet is afgekapt zijn "
            "'laagste die het haalde' en 'hoogste die afviel' per definitie leeg. Alle zes duels "
            "staan op `playable = True`. TWEE VAN DE ZES KOMEN VAN DE DAGLIJST VAN MORGEN "
            "(`source_day` = 2026-11-19): Corinthians – Botafogo en Grêmio – Bahia, beide om 01:30 "
            "NL. Dat is exact waarvoor `runwindow.py` bestaat — ze trappen af binnen het "
            "inzetvenster [18.11 08:00 NL, 19.11 08:00 NL) en horen dus bij DEZE run, niet bij die "
            "van morgen. Zonder die module was de best scorende bet van vandaag buiten beeld "
            "gebleven. De context is voor alle zes opgehaald (§1c), ook voor de drie op tier NONE."
        ),
        "HET_NIVEAU_KOMT_UIT_HET_LOPENDE_SEIZOEN_EN_DE_GEPOOLDE_CORRECTIE_IS_LEEG": (
            "Série A (BRA) loopt op kalenderjaar en staat op 35 van de 38 speeldagen, dus ver over "
            "`SEASON_MATURE_SHARE`: `model.league_level` kiest de route `lopend` en haalt het niveau "
            "rechtstreeks uit het lopende seizoen, ongeschaald — thuis 1,531 / uit 1,132 / basis "
            "1,338. `uplift_observations` houdt die competitie daarmee uit de gepoolde correctie, en "
            "omdat zij vandaag de ENIGE spelende competitie is blijft er niets over om te poolen: de "
            "factor staat op 1,0000 over 0 speeldagen en 0 competities. Dat is geen storing maar de "
            "constructie van §3 Stage 5, en het is het vermelden waard omdat de vroeg-seizoenscorrectie "
            "vandaag dus letterlijk niets doet. De notatie is `\"2025\"` / `\"2026\"` en niet "
            "`\"2025/2026\"`, zoals `prompts/run-b.md` voor de vier kalenderjaarcompetities eist."
        ),
        "DE_NIVEAUCORRECTIE_IS_VIJFTIEN_DAGEN_OUD_EN_ER_IS_NIETS_TE_BESLISSEN": (
            "LEVEL_SCALE = 1.032 bindt sinds 3 november (§6g, besluit van de gebruiker van 2 "
            "november) en is vandaag met `today=DAY` aan `analyze_match` en `robustness_check` "
            "meegegeven, bij elke aanroep. Hij raakt alleen de xG-methode en werkt dus voor 80% door "
            "in `my_prob` (§1f); de splitsmethode blijft ongemoeid. LET OP DE RICHTING, want die is "
            "vandaag relevant: deze correctie wijst de voorzichtige kant op (meer verwachte "
            "doelpunten, dus een LAGERE P(Under)), en er staan vandaag twee Unders op de lijst — "
            "zonder de correctie waren die twee edges ongeveer twee procentpunt HOGER geweest. ER IS "
            "NIETS TE BESLISSEN en de vraag hoort niet gesteld (§1h, §6g): de reeks van na 3 november "
            "is nog veel te klein en een gemengde reeks beantwoordt de vraag niet, want een duel dat "
            "de correctie al draagt verlaagt de gemeten fout per definitie."
        ),
        "DE_AFWIKKELING_WAS_AL_GEDAAN_DOOR_RUN_A_EN_EEN_SCHADUWRIJ_STAAT_TERECHT_OPEN": (
            "Stage 0 vond NUL picks en NUL schaduwrijen klaar om af te wikkelen, en dat is hier de "
            "juiste uitkomst en geen overgeslagen stap: Run A heeft vanochtend om 02:34 UTC de drie "
            "picks en 41 schaduwrijen van 17 november al afgewikkeld. `ledger.py open` geeft 'geen "
            "picks klaar om af te wikkelen' en in `picks.jsonl` staan 0 van de 561 regels op "
            "pending. ÉÉN SCHADUWRIJ STAAT NOG OPEN EN TERECHT: shadow-2026-11-17-c-mexico---jamaica "
            "(Run C, CONCACAF Nations League). Die wedstrijd was tijdens deze run LIVE — Fotmob geeft "
            "`finished: false`, `ongoing: true`, 41e minuut, 1-0, aftrap 18.11 02:30 UTC — dus de "
            "statusregel van §0 houdt hem correct tegen. Hij hoort bij Stage 0 van de volgende run. "
            "De reflectie van §3 Stage 0 (12 okt 2026) heeft daarmee vandaag voor deze run geen "
            "materiaal; die staat in het rapport van Run A."
        ),
    }

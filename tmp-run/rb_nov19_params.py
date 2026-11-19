"""De `parameters`-tekst van Run B, 19 nov 2026 — apart gehouden zodat `rb_nov19_publiceer.py`
alleen de rekenlogica hoeft te zijn (zelfde opzet als `rb_nov18_params.py`).

Vier dingen die vandaag vooraan horen:

* **VIJFTIEN VAN DE ZEVENTIEN COMPETITIES HEBBEN NIETS OP DE KALENDER.** De interlandperiode liep
  tot 17 november en de Europese competities hervatten pas op 21 november (zaterdag). Dat is
  `GEEN WEDSTRIJD` en geen gat (§3 Stage 2), maar het is wél de uitkomst die `prompts/run-b.md`
  als STILLE FAALSTAND beschrijft — en dus op drie manieren nagetrokken.
* **BEIDE GEPUBLICEERDE REGELS STAAN OP DE UNDER-KANT** en halen hun lat van 8,0 pp NIET; ze
  staan er op rangorde (§5b). Dat is de tweede dag op rij dat de hele lijst uit Unders bestaat,
  en `margins.py goalbias` staat op de hardste stand van deze hele reeks.
* **MAAR DE PINNACLE-TOETS WIJST VANDAAG DE ANDERE KANT OP DAN GISTEREN.** De Under-kant staat
  over de hele populatie in evenwicht (−0,95 pp over vijf paren, 3 van 5 erboven), waar die
  populatie op 18 november nog +3,77 pp over 27 paren stond met 21 van 27 erboven.
* **POORT 5 VANGT 74 VAN DE 87 SELECTIES WEG** (85,1%) — het hoogste aandeel van deze reeks.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0556, b=0,0359 op "
            "7989 afgerekende gevallen, fitted_through 2026-11-18. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over de hele speelbare band: ongeveer +0,3 pp op 40%, "
            "+0,9 pp op 50%, +1,4 pp op 60%. Het ruwe model zei gemiddeld 33,3% en het gebeurde "
            "33,3%. LEES DAT NIET ALS 'het model is goed gekalibreerd en dus goed': het is "
            "gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de scheefstand "
            "die telt zit in de GESELECTEERDE groep — zie `ledger.py stats`, waar het model over "
            "500 afgewikkelde bets 298,2 winnaars verwachtte en er 232 werden (−66,2), met een "
            "Brier van 0,2615 tegen 0,2427 voor de markt. De markt schat nog steeds scherper."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "DE_NIEUWE_MAX_SHORTLIST_BINDT_VANDAAG_VOOR_RUN_B_VOOR_HET_EERST": (
            "MAX_SHORTLIST staat op 2 en niet op 3. De tabel van §0 is op 18 november door de "
            "gebruiker gewijzigd naar 2 (ma–do) · 3 (vr) · 5 (za) · 4 (zo) en bindt vanaf 19 "
            "november (`ranking.SHORTLIST_BINDS_FROM`); Run A van vanochtend was de eerste run "
            "onder de nieuwe tabel en dit is de eerste Run B eronder. Het getal komt uit "
            "`ranking.max_shortlist(DAY)` met de rundag meegegeven en is hier niet uitgeschreven — "
            "`weekday() >= 4` is sinds die wijziging geen geldige lezing meer, want de zondag "
            "splitst van de zaterdag. DAT IS VANDAAG GEEN BINDENDE AFKAPPING: er stonden vier "
            "selecties boven de ondergrens van 3,0 pp en er passen twee regels, dus twee "
            "selecties vallen buiten de lijst — maar GEEN van de vier haalde de drempel van 8,0 "
            "pp, dus het zijn geen `lijstlengte`-rijen en er komt geen groene regel in de "
            "dekkingsrapportage (§5, 18 nov 2026: groen is voor een selectie die haar drempel WEL "
            "haalde en alleen op de lengte strandde). De reeks `lijstlengte` blijft daarmee op 30 "
            "afgewikkelde gevallen staan, +20,8%; de gebruiker kijkt opnieuw bij 100."
        ),
        "VIJFTIEN_VAN_DE_ZEVENTIEN_COMPETITIES_SPELEN_NIET_EN_DAT_IS_OP_DRIE_MANIEREN_NAGETROKKEN": (
            "LEES DIT EERST. Alleen MLS (USA) en Série A (BRA) hebben wedstrijden in het "
            "inzetvenster; de vijftien andere competities van de runlijst staan op GEEN WEDSTRIJD. "
            "De oorzaak is bekend en geen storing: de interlandperiode liep tot en met 17 november "
            "en de Europese competities hervatten pas op 21 november (zaterdag) — één dag later dan "
            "het rapport van 18 november schatte, wat vandaag per competitie is nagegaan. TOCH IS "
            "DIT DE UITKOMST DIE `prompts/run-b.md` ALS STILLE FAALSTAND BESCHRIJFT — een fout "
            "fotmob_id geeft geen foutmelding maar nul wedstrijden, en nul wedstrijden leest als "
            "GEEN WEDSTRIJD — dus op drie manieren nagetrokken. (1) `scripts/idcheck.py` bevindt "
            "alle 33 id's groen met een bruikbare stand, afsluitcode 0; dat is de controle die "
            "juist draait op de competities die vandaag stil zijn, en hij geeft English League One "
            "en Two elk 24 ploegen en Serie B het echte id 86 met 20 ploegen. (2) DE TWEEDE BRON IS "
            "HET OVER DE HELE LIJN EENS: BetExplorer geeft voor alle vijftien stille competities "
            "nul duels in het venster, voor MLS twee en voor Série A (BRA) drie — 17 van 17 "
            "competities eens, 5 tegen 5 duels (`rb_nov19_bevestiging.py`). De eerstvolgende "
            "speelronde staat er per competitie bij en valt op 21, 22 of 23 november. (3) MLS IS "
            "HET GEVAL WAARVOOR `scripts/runwindow.py` BESTAAT en het bindt vandaag: beide "
            "MLS-duels komen van de daglijst van MORGEN (20 november) en trappen af om 01:30 en "
            "04:00 NL — binnen het inzetvenster [19.11 08:00 NL, 20.11 08:00 NL), dus ze horen bij "
            "DEZE run. Het rapport van Run A van 18 november had ze al als zodanig aangewezen. "
            "Geen enkele competitie krijgt BUITEN DATADEKKING of AFGEKAPT."
        ),
        "DE_TWEE_MLS_DUELS_ZIJN_PLAY_OFFDUELS_EN_DAT_RAAKT_DE_AFWIKKELING": (
            "Beide MLS-duels staan bij Fotmob onder de competitie 'Major League Soccer Playoff' "
            "(id 957981) met `parentLeagueId` = 130, en `matches_for_run` pakt ze dus via het "
            "runlijst-id 130 op. Dat is juist: de play-offs zijn hoe de MLS zijn kampioen bepaalt, "
            "zelfde competitie en zelfde ploegen, en de reguliere competitie staat op 34 van 34 "
            "speeldagen. TWEE DINGEN DIE DAARUIT VOLGEN. (1) `model.league_level` kiest voor MLS de "
            "route `lopend` omdat het seizoen ver over `SEASON_MATURE_SHARE` is — niveau thuis "
            "1,843 / uit 1,406 / basis 1,557, ongeschaald. (2) HET ZIJN KNOCK-OUTDUELS, dus er kan "
            "verlenging en een strafschoppenserie komen. §0 en §6d schrijven voor dat er wordt "
            "afgerekend op de stand NA 90 MINUTEN inclusief blessuretijd en NIET op `status.scoreStr`, "
            "die de eindstand inclusief verlenging en strafschoppen geeft. De Under 3.5 van Seattle "
            "– Real Salt Lake moet dus op de 90-minutenstand worden afgewikkeld; zoek bij die "
            "afwikkeling de doelpuntminuten op, zoals bij Sassuolo – Frosinone op 3 sep 2026."
        ),
        "BEIDE_REGELS_STAAN_OP_DE_UNDER_KANT_EN_DAT_IS_DE_TWEEDE_DAG_OP_RIJ": (
            "DIT IS HET BELANGRIJKSTE VOORBEHOUD VAN VANDAAG en §6g eist dat het bij elke "
            "gepubliceerde Under staat. Beide regels zijn een Under op FULL-data: Vitória – RB "
            "Bragantino Under 2,75 @1,83 (Pinnacle) en Seattle Sounders FC – Real Salt Lake Under "
            "3,5 @1,70 (1xBet). DE GEMETEN SCHEEFSTAND OP DIE KANT IS DE HARDSTE VAN DEZE HELE "
            "REEKS: `margins.py goalbias` geeft over 137 gespeelde Unders +0,657 doelpunt per duel "
            "MEER dan de eigen lambda zei, z = +4,63 (bij de invoering van poort 9 op 11 okt 2026 "
            "was dat +0,68 over 49 duels bij z = +2,91). Op de Over-kant gebeurt dat niet: 73 "
            "duels, −0,341, z = −1,58. En over ALLE 2240 doorgerekende duels staat het model vlak "
            "(+0,029 per duel, z = +0,78), dus dit is een fout van de SELECTIE en niet van de "
            "lambdas — precies het onderscheid dat de leeswijzer van `goalbias` maakt. De vormfout "
            "staat er bovenop: P(Under 2.5) is over die 2240 duels 1,5 pp te hoog (voorspeld "
            "42,4%, werkelijk 40,9%) en P(Under 3.0) 0,9 pp. DE AFWIKKELING VAN VANDAAG IS ER EEN "
            "GEVAL VAN: Corinthians – Botafogo (Under 2,5, gisteren gepubliceerd) verwachtte 2,375 "
            "doelpunten en het werden er VIER. ER WORDT OP GROND HIERVAN GEEN ENKELE LAT VERZET "
            "(§1h, §6d): een dag is geen reeks, en poort 9 hoort pas opnieuw ter discussie als "
            "`gridfit.py measure` op een grotere homogene reeks iets anders zegt."
        ),
        "MAAR_DE_PINNACLE_TOETS_WIJST_VANDAAG_DE_ANDERE_KANT_OP_DAN_GISTEREN": (
            "EN DIT HOORT ER IN DEZELFDE ADEM BIJ, want het is het enige onafhankelijke cijfer van "
            "vandaag en het relativeert de alinea hierboven. Op de Pinnacle-toets van Stage 5 stap "
            "2 staat de Under-kant vandaag OVER DE HELE POPULATIE IN EVENWICHT: gemiddeld −0,95 pp "
            "over vijf (duel, lijn)-paren, met 3 van 5 boven Pinnacle. Op 18 november stond die "
            "populatie nog op +3,77 pp over 27 paren met 21 van 27 erboven, en dát was de dag "
            "waarop de twee gepubliceerde Unders ook precies de twee grootste gaten tegenover "
            "Pinnacle waren (+8,53 en +7,71 pp). Vandaag is dat niet zo. De twee gepubliceerde "
            "regels staan +4,04 pp (Vitória, eigen 0,569 tegen Pinnacle 0,528 op lijn 2,75) en "
            "+3,14 pp (Seattle, eigen 0,505 tegen 0,474 op lijn 3,00) boven het Pinnacle-oordeel, "
            "en twee van de drie niet-gepubliceerde duels staan er ONDER (Orlando City −7,46 pp, "
            "São Paulo −4,59 pp). Gemiddelde Pinnacle-marge 3,89% tegen 6 tot 10% bij de rest, dus "
            "dit is de strengere toets. WAT DAT SAMEN BETEKENT: de scheefstand van §6g is een "
            "eigenschap van de REEKS en staat recht overeind, maar de twee regels van vandaag zijn "
            "niet het extreme geval dat die van gisteren waren. Dat is een verschil in graad en "
            "geen vrijbrief — HARDE GRENS (§2/§4): dit getal gaat niet in `my_prob` en niet in "
            "`prob_sources`, het hoort in de vergelijking."
        ),
        "GEEN_VAN_DE_TWEE_REGELS_HAALT_DE_LAT_EN_ZE_STAAN_ER_BEIDE_OP_RANGORDE": (
            "Vitória – RB Bragantino (Under 2,75 @1,83, FULL) staat op +5,93 pp HERIJKT en +4,57 pp "
            "RUW; Seattle – Real Salt Lake (Under 3,5 @1,70, FULL) op +3,91 pp herijkt. GEEN VAN "
            "BEIDE haalt de lat van 8,0 op enige schaal: `failed_gate` = `edge` bij allebei, "
            "`bet_ruw` = False en `bet_beide` = False. ZE WORDEN TOCH GEPUBLICEERD, EN DAT IS §5b "
            "EN GEEN VERSOEPELING. Sinds 20 september is de drempel geen poort meer maar een "
            "AFKAPPING: eerst per wedstrijd de sterkste selectie, dan één ranglijst over de hele "
            "runlijst, dan de bovenste MAX_SHORTLIST, en de drempel snijdt pas als er MEER "
            "selecties boven staan dan er regels passen. Vandaag staat er NUL boven de 8,0, dus "
            "bepaalt de rangorde de lijst en gaat de lat als LABEL mee. Beide regels halen wel alle "
            "ZEVEN overgebleven poorten op de herijkte schaal — koersband, anti-circulariteit, "
            "datatier, tweede methode, robuustheid, context en underdog — plus poort 9, die bij een "
            "Under ONDER de 8,0 pp zelf `passed = True` geeft omdat `edge` daar de bindende poort "
            "is en niet poort 9 (`unders.check` zegt dat met zoveel woorden; de poort mikt op de "
            "gemeten band 8–10 pp). LEES ZE DUS ALS 'het beste wat er vandaag stond' en niet als "
            "een gevonden voordeel: `selection_score` 3,592 en 2,453, waar de regels van 18 "
            "november op 7,963 en 3,367 stonden. Dit is een zwakke dag, en dat hoort er zo in te "
            "staan."
        ),
        "POORT_5_VANGT_74_VAN_DE_87_SELECTIES_WEG_EN_DAT_IS_HET_HOOGSTE_AANDEEL_VAN_DEZE_REEKS": (
            "Van de 87 doorgerekende selecties sneuvelen er 74 op POORT 5, de bevestiging door een "
            "tweede methode (§1, voorwaarde 5) — 85,1% van alles, tegen 68,9% op 18 november. De "
            "rest: 8 op `edge`, 4 op de koersband en 1 op poort 8 (underdog). TWEE VAN DE VIJF "
            "DUELS VERDWIJNEN DAARDOOR VOLLEDIG: bij Vasco da Gama – Internacional en São Paulo – "
            "Fluminense wijzen de twee methodes op élke selectie tegengesteld, dus die twee leveren "
            "geen enkele publiceerbare kandidaat en komen op `data conflicterend` uit. Bij Vasco is "
            "dat scherp te zien: Asian Handicap Internacional +1 staat op +6,39 pp op de "
            "xG-methode en op −4,24 pp op de splitsmethode. DAT DE POORT GELD BESPAART IS GEMETEN: "
            "`shadow.py stats` meet `tweede_methode` op −2,3% over 294 afgewikkelde kandidaten. ER "
            "WORDT NIETS VERZET (§6d eist een richting over weken en niet een getal van een dag), "
            "en let op de omvang: 85,1% over 87 selecties uit vijf wedstrijden is een handvol "
            "rijen, geen reeks. Wél het opschrijven waard als dit aandeel blijft stijgen — valt er "
            "een week lang alles af op `tweede_methode`, dan is de vraag of de twee methodes "
            "systematisch uiteenlopen, en dat is een bevinding (§5, 'Net niet')."
        ),
        "ALLE_ZES_MARKTEN_HEBBEN_MEEGEDONGEN_EN_DE_LIJST_KOMT_UIT_DE_DATA": (
            "§1a eist dat zichtbaar is of een eenzijdige lijst uit de portemonnee komt of uit de "
            "data, en vandaag komt hij uit de data. De inkoop was zo breed als hij kon zijn: BEIDE "
            "spelende competities hebben een sportkey bij The Odds API en kregen de volledige "
            "bulk-aanroep met h2h + spreads + totals (3 credits elk), plus BTTS in de tweede ronde "
            "voor ALLE VIJF de duels met een kandidaat-edge (1 credit elk). Alle ZES markten hebben "
            "werkelijk meegedongen: van de 87 doorgerekende selecties waren er 26 Over/Under, 25 "
            "Asian Handicap, 15 1X2, 10 BTTS, 6 Draw No Bet en 5 Double Chance. Dat beide regels "
            "uit de Over/Under-markt komen is dus de uitkomst van `selection_score` over zes "
            "concurrerende markten en geen quotum; bets forceren om een verdeling te halen is "
            "precies wat §1 verbiedt. Bij Vitória is dat na te rekenen: de BTTS-nee stond op een "
            "HOGERE edge (+6,33 pp) dan de gepubliceerde Under 2,75 (+5,93 pp), maar op een lagere "
            "kans, en `selection_score` geeft de voorkeur aan de hogere trefkans (3,592 tegen "
            "3,129) — §1a, en de 0-of-1-bet-regel laat er één over. Credits: 6 aan de bulk plus 5 "
            "aan BTTS = 11 van een plafond van 806, en er staan nog 19368 van de 20000 van deze "
            "maand."
        ),
        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "5 duels in twee van de zeventien competities op een DONDERDAGcap van 40 "
            "(`ranking.max_deep_analyses`), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "AFGEKAPT-regel. De datarijkdom liep van 4,5 tot 8,0; omdat er niet is afgekapt zijn "
            "'laagste die het haalde' en 'hoogste die afviel' per definitie leeg. Alle vijf duels "
            "staan op `playable = True` en ALLE VIJF ZIJN FULL — geen enkel duel op LIGHT of NONE, "
            "en geen enkele promovendus die langs `promotion.convert` moest. DRIE VAN DE VIJF KOMEN "
            "VAN DE DAGLIJST VAN MORGEN (`source_day` = 2026-11-20): beide MLS-duels (01:30 en "
            "04:00 NL) en São Paulo – Fluminense (01:30 NL). Dat is exact waarvoor `runwindow.py` "
            "bestaat — ze trappen af binnen het inzetvenster [19.11 08:00 NL, 20.11 08:00 NL) en "
            "horen dus bij DEZE run, niet bij die van morgen. Zonder die module waren drie van de "
            "vijf duels buiten beeld gebleven, inclusief één van de twee gepubliceerde regels. De "
            "context is voor alle vijf opgehaald (§1c), poort 7 staat overal open en er is geen "
            "enkele verplaatsing: `context.check_venue` geeft `relocated = False` op alle vijf."
        ),
        "HET_NIVEAU_KOMT_BIJ_BEIDE_UIT_HET_LOPENDE_SEIZOEN_EN_DE_GEPOOLDE_CORRECTIE_IS_LEEG": (
            "Beide spelende competities lopen op KALENDERJAAR en staan ver over "
            "`SEASON_MATURE_SHARE`: MLS op 34 van 34 speeldagen en Série A (BRA) op 35 van 38. "
            "`model.league_level` kiest bij beide de route `lopend` en haalt het niveau "
            "rechtstreeks uit het lopende seizoen, ongeschaald — MLS thuis 1,843 / uit 1,406 / "
            "basis 1,557 en Série A thuis 1,533 / uit 1,121 / basis 1,334. `uplift_observations` "
            "houdt beide daarmee uit de gepoolde correctie, en omdat zij vandaag de ENIGE spelende "
            "competities zijn blijft er niets over om te poolen: de factor staat op 1,0000 over 0 "
            "speeldagen en 0 competities. Dat is geen storing maar de constructie van §3 Stage 5, "
            "en het is het vermelden waard omdat de vroeg-seizoenscorrectie vandaag dus letterlijk "
            "niets doet. De notatie is `\"2025\"` / `\"2026\"` en niet `\"2025/2026\"`, zoals "
            "`prompts/run-b.md` voor de vier kalenderjaarcompetities eist — Fotmob geeft op een "
            "onbekende seizoensnotatie geen fout maar valt stil terug op het lopende seizoen."
        ),
        "DE_NIVEAUCORRECTIE_IS_ZESTIEN_DAGEN_OUD_EN_ER_IS_NIETS_TE_BESLISSEN": (
            "LEVEL_SCALE = 1.032 bindt sinds 3 november (§6g, besluit van de gebruiker van 2 "
            "november) en is vandaag met `today=DAY` aan `analyze_match` en `robustness_check` "
            "meegegeven, bij elke aanroep. Hij raakt alleen de xG-methode en werkt dus voor 80% "
            "door in `my_prob` (§1f); de splitsmethode blijft ongemoeid. LET OP DE RICHTING, want "
            "die is vandaag opnieuw relevant: deze correctie wijst de voorzichtige kant op (meer "
            "verwachte doelpunten, dus een LAGERE P(Under)), en er staan vandaag twee Unders op de "
            "lijst — zonder de correctie waren die twee edges ongeveer twee procentpunt HOGER "
            "geweest, en had de bovenste de lat van 8,0 pp bijna gehaald. ER IS NIETS TE BESLISSEN "
            "en de vraag hoort niet gesteld (§1h, §6g): de reeks van ná 3 november is nog te klein "
            "en een gemengde reeks beantwoordt de vraag niet, want een duel dat de correctie al "
            "draagt verlaagt de gemeten fout per definitie."
        ),
        "STAGE_0_WIKKELDE_TWEE_REGELS_AF_EN_FOTMOBS_DAGLIJST_STOND_DAARBIJ_VAST": (
            "LEES DIT, WANT HET IS EEN BRONSTORING DIE NIET KLAAGT. Stage 0 vond één openstaande "
            "pick (Corinthians – Botafogo, Under 2,5 @2,00 van Run B van 18 nov) en één openstaande "
            "schaduwrij (Grêmio – Bahia, 1X2 Bahia @3,107, `failed_gate` = `tweede_methode`). "
            "`ledger.py open` en `shadow.py open` hielden ze BEIDE tegen met 'bron meldt nog niet "
            "afgelopen', en dat was onjuist: de DAGLIJST van Fotmob (`fetch_fixtures`, waar "
            "`settling.DayIndex` uit leest) gaf voor beide duels `finished: false`, `ongoing: true` "
            "en een KLOK VAN 136 MINUTEN op een `maxTime` van 90 — een onmogelijke stand, identiek "
            "voor beide duels, dus een vastgelopen statusveld en niet een doorlopende wedstrijd. "
            "De WEDSTRIJDDETAILS (`fetch_match_details`) gaven wél het juiste antwoord: `finished: "
            "true`, reason `FT`, met `secondHalfEnded` om 03:21 en 03:26 NL en lege velden voor "
            "verlenging. Op dat gezag zijn beide regels afgewikkeld: Corinthians – Botafogo 4–0 "
            "(doelpunten 28', 34', 60', 67' — Under 2,5 VERLOREN, en dat staat al vast bij het "
            "vierde doelpunt) en Grêmio – Bahia 0–0 (1X2 Bahia VERLOREN op een gelijkspel). WAT "
            "HIER DE LES IS: `settling.DayIndex` leest de daglijst, en die kan achterlopen op de "
            "wedstrijddetails. Dat is dezelfde stille faalstand als het Serie B-id en "
            "`calibration.py settle` — de klok liep door en niets klaagde. Dit is één ochtend op "
            "één competitie en dus GEEN grond om `settling.py` te verbouwen; het hoort als "
            "besluitpunt in het dagrapport (§6c, `owner = besluit`) en niet als een wijziging die "
            "deze run zelf doorvoert."
        ),
        "DE_REFLECTIE_OP_DE_TWEE_AFGEWIKKELDE_REGELS": (
            "§3 Stage 0 (12 okt 2026) vraagt bij elke afgewikkelde regel of de REDENERING klopte en "
            "niet alleen de uitkomst. (1) Corinthians – Botafogo, Under 2,5, VERLOREN op 4–0: de "
            "xG-methode verwachtte 2,375 doelpunten en de splitsmethode 1,693, en het werden er "
            "VIER — ruim anderhalf doelpunt boven de eigen schatting. Dit is dus verloren ÉN "
            "verkeerd ingeschat, en het is precies het geval dat `goalbias` meet: de Under-kant "
            "staat op +0,657 doelpunt per duel over 137 gevallen. (2) Grêmio – Bahia, schaduwrij "
            "1X2 Bahia @3,107, VERLOREN op 0–0: hier verwachtte de xG-methode 3,074 doelpunten en "
            "vielen er NUL. Poort 5 hield deze kandidaat tegen omdat de splitsmethode hem afwees "
            "(+9,68 pp op xG tegen −13,75 pp op de splits), en de poort had het bij het juiste "
            "eind — Bahia won niet. Maar hij had het goed op een wedstrijd die volledig buiten de "
            "voorspelling viel, en dat is een andere waarneming dan een poort die een verliezer "
            "tegenhoudt op een duel dat precies liep zoals verwacht. WAT DIT NIET BETEKENT: twee "
            "regels is geen reeks. De twee totalen zitten er in TEGENGESTELDE richting naast "
            "(+1,6 en −3,07 doelpunt), wat bij n=2 ruis is, en §6d eist ~30 gevallen voordat een "
            "reeks gelezen mag worden. Er is vandaag niets verzet."
        ),
        "STAGE_MIN_2_IS_SCHOON_EN_DE_ELF_GEMELDE_RECORDS_STAAN_ER_AL_IN": (
            "`scripts/branchaudit.py` liep over 94 takken en meldde 11 records die op een tak staan "
            "en niet op HEAD. ALLE ELF BLIJKEN ER AL IN TE ZITTEN, onder een andere sleutel of op "
            "een ander pad, en er is dus NIETS gemerged. (1) De zeven bladpaden in "
            "`source-health.json` (zes `last_run_run_c.detail.betexplorer_*` en "
            "`last_run_run_b.samenvatting`) zijn op 18 november door de vorige run verenigd en "
            "verhuisd naar `last_run_run_c.detail_history[0].detail` en "
            "`last_run_run_b.history[0].blok`; het audit-script vergelijkt bladpaden letterlijk en "
            "meldt ze daarom opnieuw. (2) De vier schaduwrijen van 3 oktober (Canada – Peru, "
            "Croatia – England, Switzerland – Slovenia, Estonia – Luxembourg) staan in `main` met "
            "de `-p8-0`-suffix, met identieke markt, koers, `my_prob`, poort en uitslag. DIE MOGEN "
            "NIET WORDEN AANGEVULD: §3 Stage -2 beschrijft precies deze vier bij naam — ze zijn op "
            "7 november door Run D verwijderd omdat elk van hen er twee keer in stond (één keer via "
            "`near_miss`, één keer via `poort8_geblokkeerd`), en §1e punt 2 verbiedt dezelfde "
            "selectie twee keer. Verenigen zou vier metingen dubbel tellen. De regels en de scripts "
            "staan op `main` in de nieuwste versie: de 38 tot 44 regels die oudere takken in "
            "`prompts/` en `scripts/` hebben zijn OUDERE versies van regels die `main` sindsdien "
            "heeft gewijzigd (MAX_SHORTLIST, de kopjes in de voorbeschouwing, de vijf bekers). "
            "Deze run staat op `main`."
        ),
    }

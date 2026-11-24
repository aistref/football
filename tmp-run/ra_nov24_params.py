"""De `parameters`-tekst van Run A, 24 nov 2026 — apart gehouden zodat `ra_nov24_publiceer.py`
alleen de rekenlogica hoeft te zijn (zelfde opzet als `ra_nov23_params.py`).

Vier dingen die vandaag vooraan horen:

* **ALLE DRIE DE GEKWALIFICEERDE SELECTIES ZIJN KRUIS-GRENSDUELS OP `LIGHT`**, en §4 waarschuwt
  bij precies deze groep dat de grootste geclaimde edge de grootste modelfout is.
* **BEIDE GEPUBLICEERDE REGELS WEDDEN OP MINDER DOELPUNTEN** (BTTS-nee en een Under), en dat is
  de kant waar §6g vandaag op z = +4,95 staat — de scherpste stand die die meting ooit gaf.
* **HET MODEL STAAT BIJ BEIDE REGELS VER BOVEN PINNACLE OP P(UNDER)** (+12,5 en +20,8 pp), en bij
  RB Leipzig – Lens 24,9 pp ONDER Pinnacle op de thuiszege.
* **DE LIJSTLENGTE BINDT VOOR HET EERST SINDS 18 NOVEMBER**: drie gekwalificeerde selecties, twee
  plekken, dus Manchester City – Napoli valt op `lijstlengte` buiten de lijst.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,037, b=0,024 op "
            "8589 afgerekende gevallen, fitted_through 2026-11-22 OP HET MOMENT VAN DE ANALYSE. "
            "§6b-5c eist dat dat getal op de vorige rundag staat of daarna; de vorige rundag is "
            "23 november, dus de fit liep bij het rekenen één dag achter op de kalender. Dat is "
            "GEEN overgeslagen `settle` maar de normale volgorde: `load_fit()` draait aan het "
            "begin van de run en `calibration.py settle` pas in Stage 6, dus de waarnemingen van "
            "23 november worden door DEZE run afgewikkeld en gaan pas in de fit van morgen mee. "
            "Het getal na de settle van vandaag staat in het runrapport onder 'Stand van het "
            "logboek'. DE FIT VERHOOGT EEN KANS OVER VRIJWEL DE HELE SPEELBARE BAND: -0,2 pp op "
            "30%, +0,2 pp op 40%, +0,6 pp op 50%, +0,9 pp op 60%, +1,2 pp op 70%, +1,2 pp op 80%. "
            "Dat is vandaag geen detail: hij heeft TWEE selecties over hun lat getild die er ruw "
            "onder stonden, en die zijn daarom NIET gepubliceerd maar als "
            "`herijking_omgekeerd` geboekt (zie hieronder). Het ruwe model zei gemiddeld 33,3% en "
            "het gebeurde 33,3%. LEES DAT NIET ALS 'het model is goed': het is gekalibreerd op de "
            "ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit in "
            "de GESELECTEERDE groep — `ledger.py stats` verwachtte over 529 afgewikkelde bets "
            "316,7 winnaars en er werden er 244 (-72,7), met een Brier van 0,2627 tegen 0,2429 "
            "voor de markt. De markt schat nog steeds scherper, en dat is de regel die telt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",

        "ALLE_DRIE_DE_GEKWALIFICEERDE_SELECTIES_ZIJN_KRUIS_GRENSDUELS_OP_LIGHT": (
            "LEES DIT EERST. Dit is de eerste Champions League-avond van deze runlijst sinds "
            "4 november, en de hele dagranglijst bestaat eruit. Van de 263 doorgerekende selecties "
            "haalden er DRIE alle poorten EN hun eigen drempel, en alle drie zijn een kruis-"
            "grensduel op `LIGHT` met een lat van 16,0 pp: Bodø/Glimt – LASK (+26,11 pp), "
            "Manchester City – Napoli (+17,30 pp) en RB Leipzig – Lens (+17,17 pp). De hoogste "
            "FULL-edge van de dag is +8,49 pp (Sheffield United – Southampton, Over 2,5) en die is "
            "op de RUWE schaal tegengehouden. "
            "WAAROM DIT HET ZWAARSTE VOORBEHOUD VAN DE RUN IS: §4 ('Kruis-grens', 8 sep 2026) "
            "punt 4 beschrijft letterlijk deze situatie. Op de zes Champions League-duels van "
            "8 september week het model na omrekening gemiddeld 11,9 pp van de de-vigde marktkans "
            "af, kwam er NUL bets uit, en zouden zonder de herijking zeven selecties zijn "
            "gekwalificeerd die alle zeven op het duel stonden waar het model 20,4 pp van de markt "
            "af zat. Vandaag staat de omrekening wél edge toe, en de drie duels waar ze dat doet "
            "zijn precies de drie waar het model het verst van Pinnacle af zit (+12,5 tot +20,8 pp "
            "op P(Under)). Dat patroon is niet een reden om een regel te verzetten — de poorten "
            "staan zoals ze staan en de omrekening is op 2111 duels gemeten — maar het is wel de "
            "reden dat deze twee regels met minder vertrouwen gelezen horen te worden dan hun "
            "edge-getal suggereert. "
            "DE OMREKENING IS GEEN AANTEKENING MAAR EEN POORT, en dat bond vandaag twee keer: "
            "Arsenal – Borussia Dortmund kwam op `NONE` omdat Arsenals omgerekende verdediging "
            "0,373 ONDER de gemeten vloer van 0,388 valt (`in_range`, de Coventry-val van §4 punt "
            "3), en Slovan Bratislava – Real Betis omdat Slowakije geen gemeten competitiefactor "
            "heeft (minder dan 40 Europese duels in de meting, §4 punt 2). Stil terugvallen op "
            "factor 1,0 is precies wat die module wegneemt; twee van de negen duels op NONE is de "
            "prijs daarvan en geen gat in de dekking."
        ),

        "BEIDE_REGELS_WEDDEN_OP_MINDER_DOELPUNTEN_EN_DAT_IS_DE_SCHEVE_KANT": (
            "`margins.py goalbias` staat vandaag op de SCHERPSTE STAND DIE DEZE METING OOIT GAF. "
            "Over alle 2453 doorgerekende duels staat het MODEL op +0,024 doelpunt per duel "
            "(z = +0,68): de lambdas kloppen. Over de 148 duels waar werkelijk een UNDER is "
            "gespeeld staat het op +0,676 doelpunt per duel, z = +4,95 — gisteren was dat +0,668 "
            "en z = +4,74. De SELECTIE staat daar dus meetbaar scheef en de reeks wordt strakker, "
            "niet losser. "
            "BEIDE GEPUBLICEERDE REGELS VAN VANDAAG WEDDEN OP MINDER DOELPUNTEN: RB Leipzig – Lens "
            "is letterlijk een Under 3,75, en Bodø/Glimt – LASK is BTTS-nee, wat dezelfde kant op "
            "wedt met een andere markt. Dat is geen toeval van vandaag maar het patroon dat §6g "
            "beschrijft, en het hoort bij ELKE lezing van deze twee regels te staan. "
            "WAT DIT NIET IS: een reden om vandaag een lat te verzetten. Poort 9 (§1h) verzwaart "
            "de Under-kant met 2,0 pp en raakt per besluit van 11 okt 2026 alleen `FULL` — beide "
            "regels staan op `LIGHT`, dus hij bindt hier niet. Dat is een bekende, met opzet "
            "gekozen grens en geen vergeetachtigheid; of hij naar LIGHT en naar BTTS moet, is een "
            "vraag voor de gebruiker en niet voor een run. Hij staat als openstaand punt in het "
            "dagrapport. De schaduwreeks `doelpunten_onder` staat op 53 kandidaten, 52 "
            "afgewikkeld, -35,9% rendement: waar hij bindt, bespaart hij geld."
        ),

        "HET_MODEL_STAAT_VER_VAN_PINNACLE_AF_OP_BEIDE_REGELS": (
            "Stage 5 stap 2 zet de de-vigde Pinnacle-prijs naast de eigen kans — de scherpste "
            "bookmaker van de markt, vandaag met een marge van 2,8 tot 4,3% op de totalen tegen 6 "
            "tot 10% bij de rest. Over 17 (duel, lijn)-paren staat het model gemiddeld +4,19 pp "
            "BOVEN Pinnacle op P(Under), met 11 van de 17 erboven; op de vier zuivere halve lijnen "
            "is dat +10,84 pp. "
            "DE ZES CHAMPIONS LEAGUE-DUELS DRAGEN DAT VERSCHIL VRIJWEL ALLEEN: Bodø/Glimt – LASK "
            "+12,52 pp, Como – AEK Athens +18,89 pp, Feyenoord – FC Porto +12,90 pp, Manchester "
            "City – Napoli +18,01 pp en RB Leipzig – Lens +20,77 pp, tegen een band van -5,2 tot "
            "+2,7 pp over de tien Championship- en Scottish Premiership-duels. Het model verwacht "
            "op de Europese avond dus systematisch MINDER doelpunten dan de scherpste prijs, en de "
            "twee gepubliceerde regels staan aan die kant. "
            "OP DE 1X2-KANT IS DE UITSCHIETER NOG GROTER EN HIJ STAAT OP EEN GEPUBLICEERD DUEL: "
            "bij RB Leipzig – Lens geeft Pinnacle de thuiszege 69,5% en het model 44,6% — 24,9 pp "
            "verschil, de grootste die deze vergelijking in weken gaf. Bij Bodø/Glimt – LASK staat "
            "het 16,6 pp de ANDERE kant op (model 81,1% tegen Pinnacle 64,5%). Gemiddelde absolute "
            "afstand over 17 duels: 4,61 pp bij een gemiddelde Pinnacle-marge van 3,80%. "
            "HARDE GRENS §2/§4: dit getal zit niet in `my_prob` en niet in `prob_sources`. Het is "
            "marktafgeleid en hoort in de vergelijking, niet in de kansschatting. Wat het wél "
            "zegt: bij RB Leipzig – Lens is het verschil zo groot dat minstens één van de twee "
            "zich grof vergist, en §1g heeft gemeten dat dat vaker het model is."
        ),

        "DE_LIJSTLENGTE_BINDT_EN_MANCHESTER_CITY_NAPOLI_VALT_BUITEN_DE_LIJST": (
            "`MAX_SHORTLIST` is 2 op dinsdag (§0, besluit van de gebruiker van 18 nov 2026) en er "
            "staan DRIE gekwalificeerde selecties. Voor het eerst sinds die verkorting bindt de "
            "lijstlengte dus werkelijk: MANCHESTER CITY – NAPOLI, Under 3,5 @2,078 (Matchbook, "
            "+17,30 pp, modelkans 65,4%, selection_score 5,660) valt op rang 3 buiten de lijst. "
            "Die selectie is GEEN afgewezen kandidaat — geen enkele poort heeft haar "
            "tegengehouden — en wordt daarom vastgelegd als `gekwalificeerd_niet_gepubliceerd` op "
            "de wedstrijd én als `near_miss` met `failed_gate = 'lijstlengte'` (§5b, 26 sep 2026). "
            "DIT IS PRECIES DE VRAAG DIE DE REEKS MOET BEANTWOORDEN. `lijstlengte` staat vóór "
            "vandaag op 31 afgewikkelde gevallen, 16 winnaars, +7,60u = +24,5% — dus de selecties "
            "die de lijstlengte tot nu toe heeft afgesneden, hebben als groep geld OPGELEVERD. Dat "
            "is een reeks van 31 en §6d eist er ~30 voordat ze gelezen mag worden, dus ze is net "
            "leesbaar en zegt: deze afkapping kost mogelijk geld. DE GEBRUIKER KIJKT BIJ 100 "
            "GEVALLEN EN DE VRAAG HOORT TOT DAN NIET GESTELD (§5b, 18 nov 2026). Vandaag komt er "
            "één geval bij, dus de stand gaat naar 32 open+afgewikkeld. "
            "`MAX_LIGHT_IN_SHORTLIST` = 2 BOND NIET ALS EXTRA GRENS maar valt er wel precies "
            "samen: beide gepubliceerde regels zijn LIGHT, en dat is het maximum. Was de "
            "lijstlengte 3 geweest, dan had deze grens de derde regel alsnog tegengehouden."
        ),

        "POORT_5_VANGT_TWEEDERDE_WEG_EN_POORT_7_KOSTTE_REAL_MADRID": (
            "De 263 selecties vielen af op: `tweede_methode` 177 (de twee methodes wijzen "
            "tegengesteld, poort 5 — 67% van alles), `edge` 37, `odds` 18 (buiten de band "
            "1,30-6,00), `context` 12 (poort 7), `robuustheid` 7 (poort 6) en `underdog` 1 "
            "(poort 8). Elf selecties kwamen door alles heen; daarvan zijn er drie de sterkste van "
            "hun wedstrijd (§1, 0-of-1-bet) en twee gepubliceerd. "
            "POORT 5 IS VOOR DE VIJFDE DAG OP RIJ DE GROOTSTE ZEEF, en op een Europese avond is "
            "dat te verwachten: de splitsmethode en de xG-methode staan bij een omgerekende ploeg "
            "verder uit elkaar dan binnen één competitie. De reeks `tweede_methode` staat op 344 "
            "kandidaten, 330 afgewikkeld, -1,1%: de poort bespaart geld, met de kleinste marge van "
            "alle poorten. "
            "POORT 7 KOSTTE REAL MADRID – PSV EINDHOVEN, en dat is het duel met de hoogste "
            "LIGHT-edge die niet op de lijst staat: AH PSV +2,5 @ +15,77 pp. PSV mist 24% van zijn "
            "selectiewaarde tegen 14% bij Real Madrid — Adamo Nagalo (uit voor het seizoen), Jerdy "
            "Schouten en Mauro Júnior (terug begin januari) — en dat verschil van 10 procentpunt "
            "is precies de drempel van §1c. Alle twaalf contextafwijzingen van vandaag zitten in "
            "dat ene duel. De reeks `context` staat op 155 kandidaten, 151 afgewikkeld, -22,8%: "
            "van alle poorten is dit de poort die het meest aantoonbaar geld bespaart. "
            "TWEE DUELS VIELEN AF OP `herijking_omgekeerd` EN DAT IS EEN ZELDZAME CATEGORIE: "
            "Sheffield United – Southampton (Over 2,5: ruw +7,42 pp, herijkt +8,49 pp, lat 8,0) en "
            "Como – AEK Athens (Under 3,5: ruw +15,04 pp, herijkt +16,08 pp, lat 16,0). Bij beide "
            "tilt de herijking de selectie over haar lat in plaats van eronder, en de regel "
            "publiceert dan niet. Die reeks staat op 5 gevallen, 0 winnaars, -100% — vijf is veel "
            "te weinig om iets te zeggen (§6d eist ~30), maar het is wel de richting die de regel "
            "zou rechtvaardigen."
        ),

        "DRIE_VAN_DE_ZESTIEN_COMPETITIES_SPELEN_EN_DAT_IS_OP_TWEE_BRONNEN_NAGETROKKEN": (
            "Drie van de zestien competities op de runlijst hebben een duel in het inzetvenster "
            "[08:00 NL 24 nov, 08:00 NL 25 nov): de Champions League met NEGEN duels (speelronde "
            "5 van de leaguefase), de Championship met ACHT en de Scottish Premiership met TWEE. "
            "Dertien competities staan op GEEN WEDSTRIJD; dat is de dinsdag van een Europese week, "
            "waarin de binnenlandse topcompetities stilliggen. "
            "DE TWEEDE BRON BEVESTIGT HET VOLLEDIG: de BetExplorer-fixturepagina geeft voor alle "
            "22 competities (de zestien van de runlijst plus de zes bekers) hetzelfde aantal duels "
            "in het venster als de Fotmob-daglijst — 22 van 22 eens, 19 duels aan beide kanten, en "
            "per competitie gelijk (9-9, 8-8, 2-2). Dat is de bevestiging door een tweede methode "
            "die §1 eist, op de vraag WELKE wedstrijden er zijn in plaats van op de kansschatting. "
            "ALLE NEGENTIEN DUELS ZIJN SPEELBAAR (`RunMatch.playable`): de vroegste trapt om 18:45 "
            "NL af (Bodø/Glimt – LASK en Galatasaray – Aston Villa), de laatste om 21:00. Geen "
            "enkel duel komt van de daglijst van 25 november, dus het venster heeft vandaag geen "
            "nachtduel opgevangen."
        ),

        "DE_ZES_BEKERS_STAAN_BUITEN_DE_RUNLIJST_EN_GEEN_VAN_ZES_SPEELT_VANDAAG": (
            "FA Cup, Coppa Italia, KNVB Beker, DFB Pokal, Copa del Rey en League Cup staan van "
            "1 juli t/m 31 december niet op de runlijst (`cups.filter_runlist` met de rundag; "
            "besluit van de gebruiker van 18 en 19 nov 2026, zie `prompts/run-a.md`). Ze krijgen "
            "daarom de status BUITEN DE RUNLIJST en NIET `GEEN WEDSTRIJD` — §5 verbiedt dat laatste "
            "met zoveel woorden, want dat zou hetzelfde zijn als een stille truncatie in Stage 4. "
            "NAGETROKKEN IN DE DAGLIJSTEN: geen van de zes speelt vandaag ook werkelijk (nul duels "
            "in beide daglijsten van het venster), dus het verschil tussen de twee statussen kost "
            "vandaag feitelijk niets. De eerstvolgende ronden staan volgens de BetExplorer-"
            "fixturepagina op 1 december (Coppa Italia, DFB Pokal), 4 december (FA Cup) en "
            "15 december (League Cup) — alle vier nog in de eerste seizoenshelft. De zes doen weer "
            "mee vanaf 1 januari 2027."
        ),

        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "Negentien duels op een DINSDAGcap van 40 (`ranking.max_deep_analyses` geeft 40 op "
            "ma-do en 55 op vr-zo), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "`AFGEKAPT`-regel. De datarijkdom-scores liepen van 5,0 (Charlton – Lincoln City, "
            "Middlesbrough – Swansea en Wolverhampton – Derby) tot 8,0 (Bodø/Glimt – LASK en "
            "Slovan Bratislava – Real Betis). Omdat er niets afviel zijn 'de laagste die het "
            "haalde' en 'de hoogste die afviel' allebei leeg; dat is de juiste lege stand en geen "
            "ontbrekende meting. De context is voor ALLE NEGENTIEN duels opgehaald zonder één "
            "fout, ook voor de twee duels die op `NONE` uitkwamen, dus `ctxlog.py` krijgt vandaag "
            "negentien waarnemingen en niet zeventien (§1c, §3 Stage 4)."
        ),

        "HET_NIVEAU_KOMT_BIJ_TWEE_COMPETITIES_UIT_VORIG_SEIZOEN_EN_DE_CL_STAAT_BUITEN_DE_POOL": (
            "`league_level` koos bij de Championship en de Scottish Premiership de route "
            "`vorig+uplift`: de Championship staat op 16 van zijn 46 speeldagen (35%) en de "
            "Scottish Premiership op 14 van 33 (42%), beide onder `SEASON_MATURE_SHARE`, dus hun "
            "niveau komt uit vorig seizoen met de vroeg-seizoenscorrectie erop. Championship "
            "1,577 thuis / 1,357 uit (basis 1,413); Scottish Premiership 1,780 / 1,303 (basis "
            "1,568). "
            "DE GEPOOLDE FACTOR IS 1,1263 (gepoold 1,1600 over 30 speeldagen, TWEE competities). "
            "DE CHAMPIONS LEAGUE IS UIT DIE POOL GELATEN en dat weglaten is zelf de meting: hij "
            "staat halverwege zijn leaguefase (4 van 8 speeldagen), dus zijn niveau komt uit het "
            "LOPENDE seizoen zelf. Een stil overgeslagen waarneming is hetzelfde probleem als een "
            "stille truncatie in Stage 4 (§3 Stage 5, 24 sep 2026), vandaar deze regel. "
            "VOOR DE NEGEN CHAMPIONS LEAGUE-DUELS KOMT HET NIVEAU HELEMAAL ERGENS ANDERS VANDAAN: "
            "`interleague.reference_league()` geeft het gemeten Europese niveau (1,572 thuis / "
            "1,179 uit) en elke ploeg wordt met de competitiefactor van zijn eigen land omgerekend "
            "(§4, 8 sep 2026). De uplift en `LEVEL_SCALE` = 1.032 staan daar LOS van en worden er "
            "nooit mee samengevoegd (§6g); beide zijn met `today=DAY` aangeroepen."
        ),

        "DE_INKOOP_IS_VOLLEDIG_EN_DE_MARKTBALANS_SLAAGT_RUIM": (
            "Alle drie de spelende competities hebben een sportkey bij The Odds API en alle drie "
            "kregen de VOLLEDIGE bulk-aanroep (h2h + spreads + totals, 3 credits elk): 9 credits "
            "op een plafond van 1357, plus 13 credits BTTS voor de dertien duels die een "
            "kandidaat-edge toonden. Totaal 22 van 1357; er staan nog 19.005 van de 20.000 open, "
            "met 7 dagen tot de maandwissel. "
            "DE MARKTBALANS-CONTROLE SLAAGT ZO RUIM ALS HIJ KAN: drie van de drie competities "
            "hebben zowel een doelpuntenmarkt (Over/Under) als uitkomstmarkten (1X2, AH, DNB, DC), "
            "en alle zes markten zijn bij alle zeventien doorgerekende duels werkelijk doorgerekend "
            "(`progress.py verify` groen). De twee duels op `NONE` hebben per definitie geen markt: "
            "daar valt niets door te rekenen. "
            "WAT ERUIT KWAM IS TÓCH EENZIJDIG, en dat hoort er zo bij te staan: beide regels zitten "
            "op de doelpuntenkant (een Over/Under en een BTTS). Dat is deze keer NIET de inkoop "
            "(29 aug 2026) maar de analyse — de uitkomstmarkten lagen bij Bodø/Glimt lager op "
            "`selection_score` (1X2 7,507 tegen 7,611 voor BTTS) en bij RB Leipzig stond geen "
            "enkele uitkomstmarkt door de poorten. Een verdeling afdwingen is precies wat §1 "
            "verbiedt. "
            "BEIDE GEPUBLICEERDE KOERSEN ZIJN HERLEIDBAAR TOT EEN BOOKMAKER MET NAAM: Bodø/Glimt – "
            "LASK staat bij MATCHBOOK, een BEURS, en is door `oddsapi.net_price` met 2% commissie "
            "doorgerekend — 3,15 bruto wordt 3,107 netto, en dat laatste getal is de koers in "
            "picks.jsonl. RB Leipzig – Lens staat bij PINNACLE, een gewone bookmaker, dus daar is "
            "bruto gelijk aan netto. Geen enkele competitie draaide op een marktgemiddelde zonder "
            "herleidbare bookmaker."
        ),

        "UNDERSTAT_LIGT_ER_VOOR_DE_ZESDE_RUNDAG_UIT_EN_KOSTTE_VANDAAG_NIETS": (
            "`understat.fetch_league` geeft voor alle drie de competities die eerder werden getoetst "
            "(EPL, Serie_A, La_liga) dezelfde UnderstatError: 'geen JSON terug van "
            "https://understat.com/getLeagueData/<comp>/2025 (26719 bytes)'. Exact dezelfde respons "
            "en exact dezelfde bytegrootte als op 19, 20, 21, 22 en 23 november, dus geen nieuwe "
            "storing maar een voortdurende — vermoedelijk een onderhouds- of blokkadepagina op een "
            "gewijzigde route, en NIET OMZEILD (§3, 'Niet doen': geen headless browser, geen "
            "challenge-solver, geen proxy). "
            "VANDAAG KOST HET FEITELIJK NIETS, en dat hoort er precies zo bij te staan: geen van "
            "Understats vijf competities (Premier League, La Liga, Bundesliga, Serie A, Ligue 1) "
            "speelt vandaag, dus ook een werkende Understat had aan geen enkel duel van deze run "
            "iets toegevoegd. WAT HET WEL KOST: de reeks die moet uitwijzen of het ene xG-model "
            "beter voorspelt dan het andere (`p_xg_understat` in §6e) groeit voor de zesde rundag "
            "niet. WAT HET NIET RAAKT: `my_prob`, de tiers en de poorten. §4 noemt Understat "
            "redundantie en een tweede xG-model, geen invoer in `my_prob`. DIT IS DUS GEEN GEVAL "
            "VAN DE UITZONDERING IN §3 PUNT 3 — die gaat over Fotmob — en het hoort niet vooraan in "
            "de notificatie. WEL IN DE GATEN HOUDEN: Understat is er juist als tweede been voor het "
            "geval Fotmob omvalt, en dat been staat nu zes rundagen niet onder de routine."
        ),

        "STAGE_0_WIKKELDE_VIER_PICKS_EN_TWAALF_SCHADUWRIJEN_AF_EN_ALLE_VIER_VERLOREN": (
            "Alle openstaande rijen van 23 november zijn afgewikkeld: VIER picks (0 gewonnen, "
            "4 verloren, 0 void) en TWAALF schaduwrijen (4 gewonnen, 6 verloren, 2 void). Alle "
            "rijen komen uit competitie- of leaguefaseduels zonder verlenging — per duel nagegaan "
            "op `status.reason` ('FT' en niet 'AET' of 'Pen'), ook bij Vancouver Whitecaps – Real "
            "Salt Lake (MLS-playoff) en Başakşehir – Çorum FK — dus `status.scoreStr` van Fotmob IS "
            "de stand na 90 minuten (§6d). "
            "EEN HALVE UITKOMST OP EEN KWARTLIJN IS ALS HALVE UITKOMST GEBOEKT, en dat is de "
            "bevinding van 20 november die vandaag meteen opnieuw voorbijkwam: Wieczysta Kraków – "
            "Motor Lublin stond op OVER 3,25 en werd 2-1. Een kwartlijn valt uiteen in twee halve "
            "bets (3,0 en 3,5); bij exact drie doelpunten is de eerste helft een PUSH en verliest "
            "de tweede, dus de netto uitkomst is -0,50u en niet -1,00u. Geboekt met "
            "`settled_units = -0.5` via `ledger.py settle --units`. Zonder die correctie zou het "
            "dagresultaat -4,00u zijn in plaats van -3,50u. "
            "`ledger.py open` en `shadow.py open` geven na afloop allebei niets meer terug, dus er "
            "is niets blijven liggen. DE REFLECTIE OP DE UITSLAGEN STAAT IN HET RUNRAPPORT ONDER "
            "'Afwikkeling' (§3 Stage 0, 12 okt 2026)."
        ),

        "STAGE_MIN_2_VIJF_SNAPSHOTBLOKKEN_VERENIGD_EN_DE_VIER_SCHADUWRIJEN_BEWUST_NIET": (
            "`origin/main` stond bij het begin van deze run op 7fe1594 en HEAD stond daar exact "
            "gelijk aan: 0 commits heen, 0 commits terug. `git branch -r` geeft 97 takken. "
            "DE CONTAINER KREEG DE REPO ALS ONDIEPE KLOON en dat gaf eerst het bekende valse alarm: "
            "87 van de 96 overige takken leken 'eigen' commits te hebben (27 tot 730 stuks) terwijl "
            "hun `merge-base` met main leeg was. Alle takken met een tip ná 10 november tellen 0 "
            "eigen commits; de takken die er honderden lijken te hebben, hebben een tip van 10 "
            "november of eerder en een geschiedenis van vóór de knip. "
            "DE CONTROLE IS OP INHOUD GEDAAN EN NIET OP DE COMMITGRAAF (§3 Stage -2, 27 sep 2026), "
            "met `scripts/branchaudit.py` over alle 97 takken en per record. "
            "`picks.jsonl` (593), `coverage.json` (339), `calibration.jsonl` (9061) en "
            "`context-log.jsonl` (2530) staan alle vier op VOLLEDIG. "
            "`shadow.jsonl` meldt VIER ontbrekende rijen en die zijn BEWUST NIET AANGEVULD: Canada "
            "– Peru, Croatia – England, Estonia – Luxembourg en Switzerland – Slovenia van "
            "3 oktober, alle vier in de categorie `underdog` en in hun KALE vorm zonder de "
            "`-p8-0`-suffix. Dat zijn precies de vier dubbeltellingen die Run D op 7 november heeft "
            "verwijderd (§1e punt 2: 'nooit dezelfde selectie twee keer'), en §3 Stage -2 schrijft "
            "met zoveel woorden voor ze bij een merge niet terug te zetten. "
            "`source-health.json` MELDDE 21 BLADPADEN EN DAAR IS WÉL IETS MEE GEDAAN. Achttien van "
            "die 21 stonden al op main, maar genest onder `history` / `detail_history` in plaats van "
            "op het pad waar branchaudit ze zoekt — het pad-gewijze oordeel ziet die nestlaag niet, "
            "en dat is een eigenschap van de controle en niet van de data. Wat werkelijk ontbrak "
            "zijn VIJF GEDATEERDE SNAPSHOTBLOKKEN: Run A van 19 en 21 nov, Run B van 10 nov en Run "
            "C van 10 en 16 nov. Die zijn verenigd in `last_run_run_a_history`, "
            "`last_run_run_b.history` en `last_run_run_c.detail_history`, gedateerd en met de tak "
            "erbij, volgens het precedent dat `_merge_note` van 18 november vastlegt. NIETS VAN "
            "MAIN IS OVERSCHREVEN: dat is per bladpad nagemeten (560 bladpaden oud, 596 nieuw, "
            "alleen `_merge_note` zelf gewijzigd). "
            "DE RUN STAAT OP `main` (§6a): de scheduler-prompt geeft daar expliciet toestemming "
            "voor, de sessie draait op `claude/stoic-davinci-n96p7a` en er is met "
            "`git push origin HEAD:main` gepusht. Stage -2 en Stage 0 zijn apart gecommit en gepusht "
            "voordat de analyse begon, zodat de merge en de afwikkeling van gisteren niet aan deze "
            "run vastzitten."
        ),
    }

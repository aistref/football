"""De `parameters`-tekst van Run A, 23 nov 2026 — apart gehouden zodat `ra_nov23_publiceer.py`
alleen de rekenlogica hoeft te zijn (zelfde opzet als `ra_nov22_params.py`).

Vier dingen die vandaag vooraan horen:

* **GEEN ENKELE SELECTIE HAALDE ZIJN EIGEN DREMPEL.** Beide gepubliceerde regels staan er op
  RANGORDE (§5b) en onder de lat; dat hoort per regel te worden meegelezen.
* **DE MARKTVORM SPREEKT BEIDE REGELS TEGEN**, en bij Wieczysta Kraków hard.
* **BEIDE REGELS ZIJN OVERS EN HET MODEL STAAT DAAR VER ONDER PINNACLE OP P(UNDER)** — de twee
  gepubliceerde duels zijn precies de twee waar het model het meest doelpuntrijk denkt.
* **RUN A VERLOOR GISTEREN VIER VAN DE VIER**, en de dag viel vijf doelpunten lager uit dan het
  model verwachtte.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,033, b=0,021 op "
            "8385 afgerekende gevallen, fitted_through 2026-11-21 OP HET MOMENT VAN DE ANALYSE. "
            "§6b-5c eist dat dat getal op de vorige rundag staat of daarna; de vorige rundag is "
            "22 november, dus de fit liep bij het rekenen één dag achter op de kalender. Dat is "
            "GEEN overgeslagen `settle` maar de normale volgorde: `load_fit()` draait aan het "
            "begin van de run en `calibration.py settle` pas in Stage 6, dus de waarnemingen van "
            "22 november worden door DEZE run afgewikkeld en gaan pas in de fit van morgen mee. "
            "Na de settle van vandaag staat `fitted_through` op 2026-11-22 — dat getal staat in "
            "het runrapport onder 'Stand van het logboek'. De fit VERHOOGT een kans over vrijwel "
            "de hele speelbare band: −0,1 pp op 30%, +0,2 pp op 40%, +0,5 pp op 50%, +0,8 pp op "
            "60%, +1,0 pp op 70%. Het ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. LEES "
            "DAT NIET ALS 'het model is goed': het is gekalibreerd op de ONGESELECTEERDE "
            "ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit in de GESELECTEERDE "
            "groep — `ledger.py stats` verwachtte over 525 afgewikkelde bets 314,3 winnaars en er "
            "werden er 244 (−70,3), met een Brier van 0,2620 tegen 0,2428 voor de markt. De markt "
            "schat nog steeds scherper, en dat is de regel die telt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",

        "GEEN_ENKELE_SELECTIE_HAALDE_ZIJN_EIGEN_DREMPEL_EN_BEIDE_REGELS_STAAN_OP_RANGORDE": (
            "LEES DIT EERST. Van de 102 doorgerekende selecties haalde er VANDAAG GEEN ENKELE "
            "zijn eigen drempel — 8,0 pp op FULL, 16,0 pp op LIGHT. De hoogste FULL-edge van de "
            "dag is +7,70 pp (Levante – Elche, Over 2,5) en de hoogste LIGHT-edge +12,58 pp "
            "(Wieczysta Kraków – Motor Lublin, 1X2 op Motor Lublin), allebei onder hun lat. "
            "BEIDE GEPUBLICEERDE REGELS STAAN ER DUS OP RANGORDE EN NIET OP VOORDEEL. Dat is "
            "precies wat §5b sinds 20 sep 2026 voorschrijft: staan er minder selecties boven de "
            "drempel dan er regels in de lijst passen, dan bepaalt de rangorde de lijst en gaat "
            "de drempel mee als LABEL per regel, niet als veto. `toplist.build` zet dat label er "
            "zelf bij ('BET op rangorde — onder de lat van 8.0 pp'). "
            "WAT DAT BETEKENT VOOR HOE JE DE LIJST LEEST: dit is niet 'twee gevonden voordelen' "
            "maar 'het beste van zes wedstrijden'. §1g heeft op 552 afgerekende gevallen gemeten "
            "dat er geen drempel op de herijkte edge bestaat die geld oplevert en dat het "
            "rendement het slechtst is bij de HOOGSTE geclaimde edge, dus een lagere edge is hier "
            "niet per se een slechter vooruitzicht — maar het is wel minder dan de lat waarop de "
            "drempel van 31 aug 2026 is gemeten. "
            "DE LIJSTLENGTE BINDT VANDAAG NIET: `MAX_SHORTLIST` is 2 op maandag (§0, besluit van "
            "de gebruiker van 18 nov 2026) en er zijn precies twee regels, dus er valt geen "
            "gekwalificeerde selectie buiten de lijst en de reeks `lijstlengte` groeit vandaag "
            "niet. Die staat op 31 afgewikkelde gevallen, 16 winnaars, +7,60u = +24,5%. DE "
            "GEBRUIKER KIJKT BIJ 100 GEVALLEN en de vraag hoort tot dan niet gesteld (§5b, "
            "18 nov 2026)."
        ),

        "DE_MARKTVORM_SPREEKT_BEIDE_REGELS_TEGEN_EN_BIJ_WIECZYSTA_HARD": (
            "§4 ('Hoe vaak ging deze markt eerder op?') eist dat een telling die de bet "
            "TEGENSPREEKT vooraan in de onderbouwing staat en niet in een voetnoot. Vandaag geldt "
            "dat voor ALLEBEI de regels, en dat is het zwaarste voorbehoud van deze run. "
            "WIECZYSTA KRAKÓW – MOTOR LUBLIN, OVER 3,25, modelkans 64,2%: Wieczysta Kraków kwam "
            "dit seizoen in 4 van zijn 14 competitieduels boven de drie doelpunten uit (29%), in "
            "zijn laatste vijf 1 van 5, en THUIS 1 van 5 (20%), met een gemiddelde van 3,29 over "
            "het seizoen en 3,00 thuis. Motor Lublin staat er anders voor: 7 van 14 (50%) en 4 "
            "van de laatste 5 (80%), gemiddeld 4,40 in die vijf. Het model zet de kans op meer "
            "dan 3,25 doelpunt dus boven de 64% terwijl de thuisploeg daar dit seizoen in één op "
            "de vijf thuisduels aan kwam. LEVANTE – ELCHE, OVER 2,5, modelkans 65,5%: Elche heeft "
            "in zijn laatste vijf duels GEMIDDELD 1,20 DOELPUNT PER WEDSTRIJD, één van de vijf "
            "boven 2,5 en NUL keer dat beide ploegen scoorden. Levante haalde in zijn laatste "
            "vijf 2 van 5 (gemiddeld 2,20). Daar staat tegenover dat Levante THUIS wél hoog zit "
            "(4 van 5 boven 2,5, gemiddeld 5,00 over vijf thuisduels) en dat beide ploegen over "
            "het hele lopende seizoen rond de 50-58% boven 2,5 staan. "
            "DIT GAAT NIET IN `my_prob` EN HET VERANDERT GEEN ENKELE KANS OF RANGORDE (§2, §4): "
            "het is de waarneming waartegen de zwakste aanname van het model te toetsen is, en ze "
            "hoort erbij te staan — ook, en juist, als ze tegenspreekt."
        ),

        "BEIDE_REGELS_ZIJN_OVERS_EN_HET_MODEL_STAAT_DAAR_VER_ONDER_PINNACLE": (
            "Stage 5 stap 2 zet de de-vigde Pinnacle-prijs naast de eigen kans — de scherpste "
            "bookmaker van de markt, vandaag met een marge van 2,7 tot 3,9% op de totalen tegen 6 "
            "tot 10% bij de rest. Over de zes duels staat het model gemiddeld 2,87 pp ONDER "
            "Pinnacle op P(Under), dus het verwacht meer doelpunten dan de scherpste prijs. "
            "DE TWEE GEPUBLICEERDE REGELS ZIJN TWEE VAN DE DRIE GROOTSTE AFWIJKINGEN VAN DE DAG: "
            "bij Wieczysta Kraków – Motor Lublin (lijn 3,25) staat het model 11,13 pp onder "
            "Pinnacle op de Under-kant en bij Levante – Elche (lijn 2,75) 7,89 pp. Alleen "
            "Brentford – Everton (−8,74 pp) ligt daartussen, en dat duel is door poort 7 "
            "tegengehouden. Twee duels wijzen de ANDERE kant op: Monza – Fiorentina (+8,30 pp) en "
            "Brøndby – Midtjylland (+6,17 pp). "
            "OP DE 1X2-KANT is de dag rustiger: gemiddelde absolute afstand tot het Pinnacle-"
            "oordeel 4,57 pp over zes duels, met Monza – Fiorentina als uitschieter (+11,37 pp op "
            "de thuiszege, en juist dáár hield poort 8 de hele wedstrijd tegen). "
            "HARDE GRENS §2/§4: dit getal zit niet in `my_prob` en niet in `prob_sources`. Het is "
            "marktafgeleid en hoort in de vergelijking, niet in de kansschatting. Wat het wél "
            "zegt: de twee regels van vandaag zijn precies de twee duels waar de routine het "
            "meest van de scherpste prijs af zit, en §1g heeft gemeten dat de grootste geclaimde "
            "afwijking vaker de grootste modelfout is dan de grootste marktfout."
        ),

        "RUN_A_VERLOOR_GISTEREN_VIER_VAN_DE_VIER_EN_DE_DAG_VIEL_LAAG_UIT": (
            "§3 Stage 0 eist sinds 12 okt 2026 dat de uitslagen worden GELEZEN en niet alleen "
            "geteld. Van de acht picks die vandaag zijn afgewikkeld waren er VIER van Run A, en "
            "ALLE VIER VERLOREN. KLOPTE DE REDENERING, OF ALLEEN DE UITKOMST? Drie van de vier "
            "verloren doordat de wedstrijd ONDER de eigen doelverwachting bleef: Lorient – Rennes "
            "1–1 tegen een verwachting van 3,27 doelpunt (Over 2,5), Osasuna – Málaga 1–0 tegen "
            "3,22 (Over 2,5), en Go Ahead Eagles – Fortuna Sittard 0–1 tegen 2,42 voor de "
            "thuisploeg alleen. De vierde ging precies andersom: Getafe – Atlético werd 0–3 tegen "
            "een verwachting van 2,15 doelpunt, en dat was een UNDER 2,5. Over de vier duels "
            "samen verwachtte het model 12,1 doelpunt en vielen er 7. "
            "WAT DIT NIET IS: een richting. Twee Overs verloren omdat er te weinig viel en de "
            "Under verloor omdat er te veel viel; dat is een dag waarop niets uitkwam, geen "
            "gemeten scheefstand. Over alle acht afgewikkelde picks van beide runs verwachtte het "
            "model 24,9 doelpunt en vielen er 22 — binnen de ruis. "
            "DEDEN DE POORTEN HUN WERK? De 64 schaduwrijen van 22 november kwamen uit op 30 "
            "gewonnen, 31 verloren en 3 void: de tegengehouden kandidaten deden het als groep "
            "niet beter dan de gespeelde bets. EN DE REM: één dag is geen reeks (§6d eist er ~30) "
            "en er is op grond van gisteren geen enkele parameter, drempel of poort aangeraakt."
        ),

        "TWEE_REGELS_UIT_102_SELECTIES_EN_WAT_ERACHTER_STAAT": (
            "De twee gepubliceerde regels, op `selection_score`: "
            "(1) LEVANTE – ELCHE, Over 2,5 @1,73 (1xBet), +7,70 pp, modelkans 65,5%, "
            "selection_score 5,044, FULL — xG-methode +6,34 pp, splitsmethode +8,48 pp, zwakste "
            "stand van het (shrink, rho)-grid +5,57 pp. De twee methodes liggen hier DICHT bij "
            "elkaar en de robuustheidsvloer is ruim positief; van de twee regels is dit de best "
            "onderbouwde. "
            "(2) WIECZYSTA KRAKÓW – MOTOR LUBLIN, Over 3,25 @1,93 (Pinnacle), +12,43 pp, "
            "modelkans 64,2%, selection_score 3,993, LIGHT — xG-methode +8,27 pp, splitsmethode "
            "+24,50 pp, zwakste stand van het grid +3,59 pp. LET OP DAT VERSCHIL: de splitsmethode "
            "claimt hier DRIE KEER zoveel voordeel als de xG-methode, en §6e heeft gemeten dat de "
            "splitsmethode de scheefste van de twee schatters is. Omdat `my_prob` voor 80% op xG "
            "leunt (§1f) telt dat maar beperkt door, maar het betekent wel dat het grootste deel "
            "van de geclaimde edge van deze regel uit de zwakste arm komt. Wieczysta Kraków is "
            "bovendien een PROMOVENDUS en daarmee een omgerekende ploeg: `LIGHT` is daar geen "
            "aantekening maar de regel (§4, 'een omgerekende ploeg is nooit FULL'). "
            "DE TWEEDE SELECTIE PER DUEL (§1a, 14 aug 2026): bij Levante is dat Over 2,75 @1,88 "
            "(Pinnacle, +7,04 pp) en bij Wieczysta Over 3,5 @2,1368 (Matchbook, +12,44 pp). Bij "
            "beide duels is de gepubliceerde regel dus DEZELFDE MENING in een andere lijn, en "
            "`selection_score` kiest de hogere trefkans boven een paar honderdsten extra edge."
        ),

        "POORT_5_VANGT_TWEEDERDE_WEG_EN_POORT_7_KOSTTE_DE_PREMIER_LEAGUE": (
            "De 102 selecties vielen af op: `tweede_methode` 63 (de twee methodes wijzen "
            "tegengesteld, poort 5), `edge` 26, `context` 5 (poort 7), `underdog` 4 (poort 8), "
            "`robuustheid` 2 (poort 6) en `odds` 2 (buiten de band 1,30–6,00). POORT 9 BOND "
            "VANDAAG NIET: er stond geen enkele Under op FULL-data in de band waar de verzwaarde "
            "lat van 10,0 pp snijdt. "
            "POORT 7 KOSTTE HET ENIGE PREMIER LEAGUE-DUEL. Brentford – Everton had met +7,23 pp "
            "op de thuiszege de op twee na hoogste FULL-edge van de dag, maar Brentford mist 30% "
            "van zijn selectiewaarde tegen 0% bij Everton — Fábio Carvalho, Aaron Hickey en "
            "Nathan Collins — en dat is ruim boven de drempel van 10 procentpunt verschil (§1c). "
            "Alle vijf de contextafwijzingen van vandaag zitten in dat ene duel. De reeks "
            "`context` staat op 152 kandidaten, 148 afgewikkeld, −22,8% rendement: van alle "
            "poorten is dit de poort die het meest aantoonbaar geld bespaart. "
            "POORT 8 HIELD MONZA – FIORENTINA HELEMAAL TEGEN. Alle vier de underdog-afwijzingen "
            "zitten daar: Monza is promovendus, de markt zet hem onder `UNDERDOG_FLOOR` (0,35), "
            "en de vier sterkste selecties van dat duel stonden allemaal op de Monza-kant "
            "(Double Chance +13,87 pp, AH +1 +12,27 pp, 1X2 +12,09 pp). De reeks `underdog` staat "
            "op 437 kandidaten, 417 afgewikkeld, −2,2%; `underdog_ruw` op 17 gevallen en −8,8%. "
            "Die twee blijven twee populaties en worden nooit opgeteld (§1e)."
        ),

        "ZES_VAN_DE_ZESTIEN_COMPETITIES_SPELEN_EN_DAT_IS_OP_TWEE_BRONNEN_NAGETROKKEN": (
            "Zes van de zestien competities op de runlijst van vandaag hebben een duel in het "
            "inzetvenster [08:00 NL 23 nov, 08:00 NL 24 nov): Premier League, Serie A, La Liga, "
            "Süper Lig, Danish Superliga en Ekstraklasa, met elk PRECIES ÉÉN duel. Dat is de "
            "maandag van een interlandvrije week: de speelronden van het weekend zijn voorbij en "
            "wat er maandag nog staat is per competitie het afsluitende duel. "
            "DE TWEEDE BRON BEVESTIGT HET VOLLEDIG: de BetExplorer-fixturepagina geeft voor alle "
            "22 competities (de zestien van de runlijst plus de zes bekers) hetzelfde aantal "
            "duels in het venster als de Fotmob-daglijst — 22 van 22 eens, zes duels aan beide "
            "kanten. Dat is de bevestiging door een tweede methode die §1 eist, nu op de vraag "
            "WELKE wedstrijden er zijn in plaats van op de kansschatting. "
            "Alle zes duels zijn SPEELBAAR (`RunMatch.playable`): de vroegste trapt om 18:00 NL "
            "af (Başakşehir – Çorum FK), de laatste om 21:00 (Brentford – Everton en "
            "Levante – Elche). Geen enkel duel komt van de daglijst van 24 november, dus het "
            "venster heeft vandaag geen nachtduel opgevangen."
        ),

        "DE_ZES_BEKERS_STAAN_BUITEN_DE_RUNLIJST_EN_GEEN_VAN_ZES_SPEELT_VANDAAG": (
            "FA Cup, Coppa Italia, KNVB Beker, DFB Pokal, Copa del Rey en League Cup staan van "
            "1 juli t/m 31 december niet op de runlijst (`cups.filter_runlist` met de rundag; "
            "besluit van de gebruiker van 18 en 19 nov 2026, zie `prompts/run-a.md`). Ze krijgen "
            "daarom de status BUITEN DE RUNLIJST en NIET `GEEN WEDSTRIJD` — §5 verbiedt dat laatste "
            "met zoveel woorden, want dat zou hetzelfde zijn als een stille truncatie in Stage 4. "
            "NAGETROKKEN IN DE DAGLIJSTEN: geen van de zes speelt vandaag ook werkelijk (nul duels "
            "in beide daglijsten van het venster), dus het verschil tussen de twee statussen kost "
            "vandaag feitelijk niets. Dat is geen reden om de status te laten vallen — de "
            "eerstvolgende bekerronde staat volgens de BetExplorer-fixturepagina op 1 december "
            "(Coppa Italia, DFB Pokal), 4 december (FA Cup) en 15 december (League Cup), en die "
            "vallen alle vier nog in de eerste seizoenshelft. De zes doen weer mee vanaf "
            "1 januari 2027."
        ),

        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "Zes duels op een MAANDAGcap van 40 (`ranking.max_deep_analyses` geeft 40 op ma–do en "
            "55 op vr–zo), dus er is NIETS afgekapt en de dekkingstabel krijgt geen "
            "`AFGEKAPT`-regel. De datarijkdom-scores liepen van 4,5 (Başakşehir – Çorum FK en "
            "Wieczysta Kraków – Motor Lublin, beide zonder opstellingsblok) tot 7,5 "
            "(Brentford – Everton). Omdat er niets afviel zijn 'de laagste die het haalde' en 'de "
            "hoogste die afviel' allebei leeg; dat is de juiste lege stand en geen ontbrekende "
            "meting. De context is voor alle zes duels opgehaald, dus `ctxlog.py` krijgt vandaag "
            "zes waarnemingen en niet twee (§1c)."
        ),

        "HET_NIVEAU_KOMT_BIJ_VIJF_VAN_DE_ZES_UIT_VORIG_SEIZOEN_PLUS_UPLIFT": (
            "`league_level` koos bij VIJF van de zes competities de route `vorig+uplift` en bij "
            "ÉÉN de route `lopend`: de Danish Superliga staat op 15 van zijn 22 speeldagen en is "
            "daarmee over `SEASON_MATURE_SHARE` heen, dus zijn niveau komt uit het LOPENDE seizoen "
            "zelf en ongeschaald (1,674 thuis / 1,382 uit). Diezelfde competitie is daarom ook "
            "WEGGELATEN uit de gepoolde vroeg-seizoenscorrectie (`uplift_observations`), en dat "
            "weglaten is zelf de meting — een stil overgeslagen waarneming is hetzelfde probleem "
            "als een stille truncatie in Stage 4 (§3 Stage 5, 24 sep 2026). "
            "DE GEPOOLDE FACTOR IS 1,1178 (gepoold 1,1328 over 63 speeldagen, vijf competities). "
            "Dat is hoog, en het hoort bij een lijstje competities dat grotendeels op eenderde van "
            "het seizoen staat: Premier League 11 speeldagen, Serie A 12, La Liga 13, Süper Lig "
            "12, Ekstraklasa 15. `LEVEL_SCALE` = 1.032 staat daar LOS van en wordt er nooit mee "
            "samengevoegd (§6g): de uplift rekent vorig seizoen om naar dit seizoen en dooft uit, "
            "de niveaucorrectie is een residu op uitkomsten en dooft niet uit. Beide zijn met "
            "`today=DAY` aangeroepen."
        ),

        "DE_INKOOP_IS_VOLLEDIG_EN_DE_MARKTBALANS_SLAAGT_RUIM": (
            "Alle zes spelende competities hebben een sportkey bij The Odds API en alle zes "
            "kregen de VOLLEDIGE bulk-aanroep (h2h + spreads + totals, 3 credits elk): 18 credits "
            "op een plafond van 1190, plus 6 credits BTTS voor alle zes de duels, die alle zes een "
            "kandidaat-edge toonden. Totaal 24 van 1190; er staan nog 19.048 van de 20.000 open. "
            "DE MARKTBALANS-CONTROLE SLAAGT ZO RUIM ALS HIJ KAN: zes van de zes competities hebben "
            "zowel een doelpuntenmarkt (Over/Under) als uitkomstmarkten (1X2, AH, DNB, DC), en "
            "alle zes de markten zijn bij alle zes de duels werkelijk doorgerekend. Er is dus geen "
            "enkele markt die vandaag niet heeft kunnen meedingen. "
            "WAT ERUIT KWAM IS TÓCH EENZIJDIG, en dat hoort er zo bij te staan: BEIDE regels zijn "
            "een Over/Under. Dat is deze keer NIET de inkoop (29 aug 2026) maar de analyse — de "
            "uitkomstmarkten lagen vandaag lager op `selection_score`, en de twee duels waar ze "
            "bovenaan stonden zijn door poort 7 (Brentford) en poort 8 (Monza) tegengehouden. Een "
            "verdeling afdwingen is precies wat §1 verbiedt. "
            "GEEN ENKELE COMPETITIE DRAAIT OP EEN MARKTGEMIDDELDE ZONDER HERLEIDBARE BOOKMAKER: "
            "alle zes hadden een sportkey, dus alle zes de gepubliceerde en afgewezen koersen zijn "
            "de BESTE prijs met naam. Vier van de zes beste prijzen van vandaag stonden bij een "
            "BEURS (Betfair of Matchbook) en zijn door `oddsapi.net_price` met 2% commissie "
            "doorgerekend; de twee gepubliceerde regels staan allebei bij een gewone bookmaker "
            "(1xBet en Pinnacle), dus daar is bruto gelijk aan netto."
        ),

        "UNDERSTAT_LIGT_ER_VOOR_DE_VIJFDE_RUNDAG_UIT_EN_DAT_RAAKT_ALLEEN_DE_METING": (
            "`understat.py` geeft voor alle drie zijn competities die vandaag spelen (EPL, "
            "Serie_A, La_liga) dezelfde UnderstatError: 'geen JSON terug van "
            "https://understat.com/getLeagueData/<comp>/2025 (26719 bytes)'. Exact dezelfde "
            "respons en exact dezelfde bytegrootte als op 19, 20, 21 en 22 november, dus geen "
            "nieuwe storing maar een voortdurende — vermoedelijk een onderhouds- of blokkadepagina "
            "op een gewijzigde route, en NIET OMZEILD (§3, 'Niet doen': geen headless browser, "
            "geen challenge-solver, geen proxy). "
            "WAT HET KOST: `p_xg_understat` blijft leeg in het kalibratieblok van §6e, dus de "
            "reeks die moet uitwijzen of het ene xG-model beter voorspelt dan het andere groeit "
            "voor de vijfde rundag niet. WAT HET NIET RAAKT: `my_prob`, de tiers en de poorten. "
            "§4 noemt Understat redundantie en een tweede xG-model, geen invoer in `my_prob`, en "
            "alle zes duels halen hun kansinput bij Fotmob, dat vandaag zonder één fout leverde. "
            "DIT IS DUS GEEN GEVAL VAN DE UITZONDERING IN §3 PUNT 3 — die gaat over Fotmob — en "
            "het hoort niet vooraan in de notificatie. WEL IN DE GATEN HOUDEN: Understat is er "
            "juist als tweede been voor het geval Fotmob omvalt, en dat been staat nu vijf "
            "rundagen niet onder de routine. Het staat daarom vanaf vandaag als openstaand punt in "
            "het dagrapport, met `owner = 'ik'`."
        ),

        "STAGE_0_WIKKELDE_ACHT_PICKS_EN_VIERENZESTIG_SCHADUWRIJEN_AF": (
            "Alle openstaande rijen van 22 november zijn afgewikkeld: ACHT picks (3 gewonnen, 5 "
            "verloren, 0 void) en VIERENZESTIG schaduwrijen (30 gewonnen, 31 verloren, 3 void). "
            "Alle rijen komen uit competitieduels zonder verlenging, dus `status.scoreStr` van "
            "Fotmob is de stand na 90 minuten (§6d). "
            "ÉÉN RIJ BLIJFT OPEN en dat is correct gedrag: de schaduwrij Vancouver Whitecaps – "
            "Real Salt Lake (MLS, Run B) meldt 2,1 uur na de aftrap nog niet afgelopen, dus de "
            "statusregel van §0 laat hem staan in plaats van hem op de klok af te wikkelen. "
            "`ledger.py open` en `shadow.py open` geven na afloop allebei 'geen rijen klaar om af "
            "te wikkelen', dus er is niets blijven liggen. "
            "DE VIER PICKS VAN RUN A VAN GISTEREN VERLOREN ALLE VIER; zie de reflectie hierboven."
        ),

        "STAGE_MIN_2_DE_KLOON_WAS_ONDIEP_EN_NA_HET_UNSHALLOWEN_VALT_ER_NIETS_TE_MERGEN": (
            "`origin/main` stond bij het begin van deze run op f7553f5 en HEAD stond daar exact "
            "gelijk aan: 0 commits heen, 0 commits terug. `git branch -r` geeft 97 takken. "
            "DE CONTAINER KREEG DE REPO ALS ONDIEPE KLOON (`--is-shallow-repository` -> true), EN "
            "DAT GAF EERST EEN VALS ALARM: 84 van de 96 overige takken leken 'eigen' commits te "
            "hebben (39 tot 691 stuks), terwijl hun `merge-base` met HEAD leeg was. Dat is exact "
            "het beeld dat §3 Stage -2 beschrijft — bij een ondiepe kloon ontbreekt alles van voor "
            "de knip, dus telt elke commit van daarvoor als 'nog niet hier'. NA "
            "`git fetch --unshallow origin` (783 commits lokaal in plaats van 60) hebben "
            "**0 van de 96 takken** nog eigen commits. Er valt dus niets te mergen, en de les van "
            "die paragraaf geldt onverkort: unshallow eerst, anders meet je iets anders dan je "
            "denkt. "
            "DE CONTROLE IS DAARNAAST OP INHOUD GEDAAN EN NIET ALLEEN OP DE COMMITGRAAF (§3 "
            "Stage -2, 27 sep 2026: '0 eigen commits is een uitspraak over de graaf'). Van elke "
            "tak zijn `picks.jsonl`, `shadow.jsonl`, `calibration.jsonl` en `context-log.jsonl` "
            "per regel-id vergeleken met main. UITKOMST: geen enkele tak heeft een pick, een "
            "kalibratierij of een contextrij die hier ontbreekt. WEL staan er op 38 takken "
            "VIER schaduwrijen die main niet heeft, en die horen er NIET bij te komen: het zijn "
            "Canada – Peru, Croatia – England, Estonia – Luxembourg en Switzerland – Slovenia van "
            "3 oktober, alle vier in de categorie `underdog`, in hun KALE vorm zonder de "
            "`-p8-0`-suffix. Dat zijn precies de vier dubbeltellingen die Run D op 7 november "
            "heeft verwijderd omdat §1e punt 2 ze verbiedt ('nooit dezelfde selectie twee keer'), "
            "en §3 Stage -2 schrijft met zoveel woorden voor ze bij een merge NIET aan te vullen. "
            "Ze zijn dus bewust niet teruggezet. "
            "DE RUN STAAT OP `main` (§6a): de scheduler-prompt geeft daar expliciet toestemming "
            "voor, de sessie draait op `claude/stoic-davinci-0n54ct` en er is met "
            "`git push origin HEAD:main` gepusht. Stage 0 is apart gecommit en gepusht voor de "
            "analyse begon, zodat de afwikkeling van gisteren niet aan deze run vastzit."
        ),
    }

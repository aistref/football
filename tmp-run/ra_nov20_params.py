"""De `parameters`-tekst van Run A, 20 nov 2026 — apart gehouden zodat `ra_nov20_publiceer.py`
alleen de rekenlogica hoeft te zijn (zelfde opzet als `rb_nov19_params.py`).

Vier dingen die vandaag vooraan horen:

* **DRIE REGELS, EN DE BOVENSTE TWEE HALEN HUN EIGEN LAT.** Dat is in deze reeks ongewoon: op
  18 en 19 november haalde geen enkele gepubliceerde regel de drempel.
* **TWEE VAN DE DRIE STAAN OP DE OVER-KANT**, de kant waar `goalbias` het selectie-effect juist
  de ANDERE kant op meet dan bij Under: −0,341 doelpunt per duel over 73 gespeelde Overs.
* **DE BOVENSTE REGEL STAAT 15 PROCENTPUNT VAN HET PINNACLE-OORDEEL AF**, en dat is het patroon
  waar §1g voor waarschuwt: de grootste geclaimde edge is vaak de grootste modelfout.
* **UNDERSTAT LIGT ERUIT** (onderhoudspagina). Dat raakt alleen het kalibratieblok van §6e.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0566, b=0,0365 "
            "op 8001 afgerekende gevallen, fitted_through 2026-11-19. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over de hele speelbare band: ongeveer +0,3 pp op "
            "40%, +0,9 pp op 50%, +1,4 pp op 60%, +1,8 pp op 70%. Het ruwe model zei gemiddeld "
            "33,3% en het gebeurde 33,3%. LEES DAT NIET ALS 'het model is goed gekalibreerd en "
            "dus goed': het is gekalibreerd op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep "
            "2026), en de scheefstand die telt zit in de GESELECTEERDE groep — zie `ledger.py "
            "stats`, waar het model over 501 afgewikkelde bets 298,8 winnaars verwachtte en er "
            "232 werden (−66,8), met een Brier van 0,2617 tegen 0,2428 voor de markt. De markt "
            "schat nog steeds scherper, en dat is de regel die telt."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "DRIE_REGELS_EN_DE_BOVENSTE_TWEE_HALEN_HUN_EIGEN_LAT": (
            "LEES DIT EERST, want het is de eerste dag in deze reeks waarop het geldt. (1) Pogoń "
            "Szczecin – Śląsk Wrocław, Over 2,75 @1,83 (Pinnacle), LIGHT, +18,59 pp herijkt en "
            "+16,82 pp ruw — boven de LIGHT-lat van 16,0 op BEIDE schalen, `bet_beide` = True. "
            "(2) Bayern München – 1. FC Köln, BTTS ja @1,9212 (Matchbook, beurs: 1,94 bruto), "
            "FULL, +9,74 pp herijkt en +8,31 pp ruw — boven de FULL-lat van 8,0 op beide schalen, "
            "`bet_beide` = True. (3) AGF – Lyngby, Over 2,5 @1,6272 (Matchbook, beurs: 1,64 "
            "bruto), LIGHT, +13,43 pp — die haalt zijn lat van 16,0 NIET en staat er op rangorde "
            "(§5b), met `failed_gate` = `edge` en `zou_bet_zijn_ruw` = False. Op 18 en 19 november "
            "haalde GEEN ENKELE gepubliceerde regel zijn drempel; vandaag twee van de drie. "
            "selection_score 6,807 / 6,018 / 5,029, tegen 3,592 en 2,453 gisteren. DAT MAAKT HET "
            "GEEN GEVONDEN VOORDEEL: §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN "
            "drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het "
            "SLECHTST is bij de hoogste geclaimde edge. De lat halen is een label, geen belofte."
        ),
        "DE_BOVENSTE_REGEL_STAAT_VIJFTIEN_PROCENTPUNT_VAN_PINNACLE_AF_EN_DAT_HOORT_VOORAAN": (
            "DIT IS HET BELANGRIJKSTE VOORBEHOUD VAN VANDAAG. Op de Pinnacle-toets van Stage 5 "
            "stap 2 — de scherpste bookmaker van de markt, marge 3,9% op dit duel tegen 6 tot 10% "
            "bij de rest — staat onze P(Under 2,75) bij Pogoń – Śląsk Wrocław op 0,324 tegen "
            "Pinnacle's 0,474. Op de Over-kant waarop de bet staat is dat dus +15,05 pp BOVEN het "
            "Pinnacle-oordeel, en het is het grootste gat van alle zeven duels van vandaag. "
            "Precies hetzelfde geldt voor de derde regel: AGF – Lyngby staat op lijn 3,0 +15,49 pp "
            "boven Pinnacle. §1g waarschuwt daar met zoveel woorden voor — 'wie selecteert op de "
            "grootste edge, selecteert op de grootste modelfout' — en op de kruis-grensduels van "
            "8 september was de hoogste claim (20,4 pp) ook de grootste fout. HET IS GEEN REDEN OM "
            "DE REGELS WEG TE LATEN: de drempel is sinds 20 september een afkapping en geen poort "
            "(§5b), de zeven overige poorten staan bij alle drie open, en de Pinnacle-prijs is "
            "marktafgeleid en mag per §2 nooit in `my_prob` of `prob_sources`. Het is wél de reden "
            "om de lijst te lezen als 'dit is het beste wat er vandaag stond' in plaats van als "
            "een vondst. Over alle zeven duels staat het eigen 1X2 gemiddeld 2,67 pp van Pinnacle "
            "af; bij Pogoń is dat 8,50 pp op de thuiszege, ook daar de grootste van de dag."
        ),
        "TWEE_VAN_DE_DRIE_REGELS_STAAN_OP_DE_OVER_KANT_EN_GOALBIAS_WIJST_DAAR_DE_ANDERE_KANT_OP": (
            "`margins.py goalbias` over 2242 doorgerekende duels: het MODEL staat vlak (+0,029 "
            "doelpunt per duel, z = +0,79), de Under-SELECTIE staat +0,655 doelpunt per duel "
            "boven de eigen lambda (138 duels, z = +4,63) en de Over-SELECTIE staat −0,341 "
            "(73 duels, z = −1,58). Vandaag staan er twee Overs op de lijst, dus de relevante "
            "regel is die derde: in de duels waarin deze routine Over speelde, vielen er MINDER "
            "doelpunten dan haar eigen lambda zei. Dat wijst de ongunstige kant op voor beide "
            "Over-regels van vandaag en het hoort erbij te staan. Twee dingen die het "
            "relativeren zonder het weg te nemen: z = −1,58 is onder de twee en dus geen harde "
            "meting, en op RENDEMENT staat de Over-kant juist positief (99 afgewikkelde picks, "
            "55,6% trefkans, +6,5%) tegen Under (176 picks, 45,5%, −13,6%). Die twee cijfers "
            "meten niet hetzelfde: goalbias meet de doelpuntenas, het rendement de uitbetaling. "
            "ER WORDT NIETS VERZET (§1h, §6d): poort 9 raakt alleen de Under-kant, een dag is "
            "geen reeks, en een run verzet geen lat op eigen initiatief."
        ),
        "DE_DERDE_REGEL_IS_DE_DERDE_MARKT_MET_EEN_POSITIEF_RENDEMENT_EN_DAT_IS_GEEN_KEUZE_GEWEEST": (
            "Over de hele reeks staan maar drie markten op een positief rendement: Draw No Bet "
            "(18 picks, +29,4%), BTTS (35 picks, +23,9%) en Over (99 picks, +6,5%). De lijst van "
            "vandaag bestaat uit twee Overs en een BTTS. DAT IS GEEN SELECTIE OP RENDEMENT en mag "
            "ook niet zo gelezen worden: `selection_score` kent het rendement van een markt niet "
            "en rangschikt uitsluitend op voordeel × kans × datatier (§1a). Het is toeval op één "
            "dag met zeven duels, en bij n = 18 en n = 35 is het rendement van die markten "
            "bovendien ruis (§6d eist ~30 gevallen en dan nog een richting over weken). Het staat "
            "hier omdat het anders na drie dagen als een patroon wordt gelezen dat niemand heeft "
            "gemeten."
        ),
        "DE_SPLITSMETHODE_IS_BIJ_DE_BOVENSTE_REGEL_EXTREEM_EN_DAT_MOET_ERBIJ": (
            "Bij Pogoń Szczecin – Śląsk Wrocław geeft de xG-methode lambdas van 2,409 en 1,266 "
            "(3,68 doelpunten verwacht) en de SPLITSMETHODE 4,416 en 1,659 (6,08 doelpunten). Dat "
            "tweede getal is niet geloofwaardig als voorspelling, en het zet de twee edges ver "
            "uiteen: +11,64 pp op xG tegen +37,53 pp op de splits. DRIE DINGEN DIE DAARUIT "
            "VOLGEN. (1) De weging beperkt de schade tot wat ze mag zijn: §1f geeft de splits 20% "
            "en de xG-methode 80%, dus `my_raw` = 0,8 × 0,663 + 0,2 × 0,922 = 0,715. (2) De bet "
            "overleeft OOK op de xG-methode alleen: +11,64 pp is boven de LIGHT-lat van 16,0 niet, "
            "maar de rangorde van §5b wordt bepaald op de gewogen kans en de robuustheidstoets "
            "geeft `min_edge` = +8,59 pp over het hele (shrink, rho)-grid — dus de edge draait "
            "nergens in dat grid om. (3) Śląsk Wrocław is een PROMOVENDUS en zijn splits komen uit "
            "de I Liga, omgerekend met de eigen gemeten factor (×0,680 aanval / ×1,743 "
            "verdediging, n=24, binnen bereik). Een omgerekende ploeg is daarom nooit FULL (§4), "
            "en dat is precies waarom deze regel op de LIGHT-lat van 16,0 wordt afgerekend en niet "
            "op 8,0. §1d zegt het zelf: de splitsmethode is de scheefste van de twee en blijft "
            "staan als VETO (poort 5), niet als kansbron — meerekenen voor een vijfde, "
            "meebeslissen over ja/nee."
        ),
        "ZES_VAN_DE_ZESTIEN_COMPETITIES_SPELEN_EN_DAT_IS_OP_TWEE_BRONNEN_NAGETROKKEN": (
            "Het FIFA-interlandvenster van november is afgelopen en de clubcompetities hervatten "
            "vanavond. Zes competities hebben duels in het inzetvenster [08:00 NL 20 nov, 08:00 NL "
            "21 nov): La Liga, Bundesliga, Ligue 1, Belgian Pro League en Danish Superliga elk "
            "één, Ekstraklasa twee. De tien andere staan op GEEN WEDSTRIJD en hervatten op "
            "zaterdag 21 november. DAT IS OP TWEE BRONNEN NAGETROKKEN, zoals §5 eist: 'niet in de "
            "daglijst' mag nooit als GEEN WEDSTRIJD worden opgeschreven zonder tweede bron (het "
            "gat van 6 okt 2026, dat Run A vijf duels kostte). BetExplorer geeft voor alle tien "
            "stille competities nul duels in het venster en noemt per competitie de eerstvolgende "
            "ronde (Manchester City – Fulham 21 nov 13:30, Como – Cagliari 21 nov 15:00, "
            "Nijmegen – PSV 21 nov 16:30, en zo verder); voor de zes spelende competities geeft "
            "hij exact dezelfde zeven duels. 16 van 16 competities eens, 7 tegen 7 duels. "
            "`idcheck.py` bevindt bovendien alle 33 id's uit coverage.json groen met een bruikbare "
            "stand, afsluitcode 0 — dat is de controle die juist draait op de competities die "
            "vandaag stil zijn, want een fout id geeft geen foutmelding maar nul wedstrijden."
        ),
        "DE_ZES_BEKERS_STAAN_BUITEN_DE_RUNLIJST_EN_DE_LEAGUE_CUP_VOOR_HET_EERST": (
            "FA Cup, Coppa Italia, KNVB Beker, DFB Pokal, Copa del Rey én League Cup krijgen "
            "vandaag de status BUITEN DE RUNLIJST en niet GEEN WEDSTRIJD (§5; `cups.reason` met de "
            "rundag). VANDAAG BINDT DE LEAGUE CUP VOOR HET EERST: zijn eigen ingangsdatum staat in "
            "`cups.BINDS_FROM_PER_COMPETITION` op 20 november, een dag later dan de andere vijf, "
            "omdat Run A van 19 november op het moment van het besluit al had gedraaid MET de "
            "League Cup op de runlijst (§run-a.md punt 4). Het zijn er dus vanaf nu zes. HET KOST "
            "VANDAAG NIETS en dat is nagetrokken in plaats van aangenomen: BetExplorer geeft voor "
            "alle zes nul duels in het venster, met als eerstvolgende ronde 1 december (Coppa "
            "Italia, DFB Pokal), 4 december (FA Cup) en 15 december (League Cup) — precies de "
            "ronde die `prompts/run-a.md` noemt. KNVB Beker en Copa del Rey hebben helemaal geen "
            "rijen. Er is dus geen enkel duel dat door deze grens buiten beeld valt."
        ),
        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "7 duels op een VRIJDAGcap van 55 (`ranking.max_deep_analyses` met de rundag), dus er "
            "is NIETS afgekapt en de dekkingstabel krijgt geen AFGEKAPT-regel. De datarijkdom liep "
            "van 5,0 tot 8,0; omdat er niet is afgekapt zijn 'laagste die het haalde' en 'hoogste "
            "die afviel' per definitie leeg. Alle zeven duels staan op `playable = True` en komen "
            "van de daglijst van de RUNDAG ZELF — er is vandaag geen enkel duel van de daglijst van "
            "morgen, anders dan gisteren bij Run B. VIER van de zeven zijn FULL en DRIE zijn "
            "LIGHT, alle drie vanwege een omgerekende ploeg: Troyes (Ligue 2 → Ligue 1), Lyngby "
            "(1. Division → Danish Superliga) en Śląsk Wrocław (I Liga → Ekstraklasa). Alle drie "
            "vallen BINNEN het gemeten bereik van `conversion_in_range`, dus geen enkel duel komt "
            "op NONE uit en geen competitie krijgt BUITEN DATADEKKING. De context is voor alle "
            "zeven opgehaald (§1c), en `context.check_venue` geeft `relocated = False` op alle "
            "zeven: geen verplaatsing."
        ),
        "POORT_8_HEEFT_EEN_SELECTIE_TEGENGEHOUDEN_EN_HET_IS_DE_STERKSTE_VAN_LA_LIGA": (
            "Bij Athletic Club – Espanyol haalt Espanyol +1,5 @1,63 alle andere poorten en staat "
            "op +8,08 pp, maar poort 8 houdt hem tegen: de markt zet Espanyol op een de-vigde "
            "kans onder `UNDERDOG_FLOOR` = 0,35 (marktgemiddelde 1,49 / 4,37 / 6,54). Die rij gaat "
            "als `failed_gate = underdog` naar het schaduwlogboek en wordt afgerekend (§1e), op "
            "beide schalen. DE REEKS WORDT GENOEMD EN ER WORDT NIETS AAN VERANDERD: de vraag is op "
            "5 oktober 2026 aan de gebruiker voorgelegd en zijn antwoord was 'rem blijft zoals die "
            "nu is', en §1e verbiedt met zoveel woorden hem elke dag opnieuw te stellen. De "
            "gemeten kalibratiefout die de rem afdekt staat er nog."
        ),
        "UNDERSTAT_LIGT_ERUIT_EN_DAT_RAAKT_ALLEEN_DE_METING": (
            "`understat.com/getLeagueData/...` geeft HTTP 200 met een onderhoudspagina (26.719 "
            "bytes, geen JSON) voor alle drie de Understat-competities die vandaag spelen: La "
            "Liga, Bundesliga en Ligue 1. Dat staat al zo in `data/source-health.json` sinds "
            "19 november en is dus geen nieuwe storing. WAT HET RAAKT: `p_xg_understat` blijft leeg "
            "in het kalibratieblok van §6e, dus de reeks die moet uitwijzen of het ene xG-model "
            "beter voorspelt dan het andere groeit vandaag niet. WAT HET NIET RAAKT: `my_prob`, de "
            "tiers en de poorten. §4 noemt Understat redundantie en een tweede xG-model — "
            "uitdrukkelijk niet een invoer in `my_prob` — en de kanskant komt bij alle zeven duels "
            "van Fotmob, dat voor beide seizoenen xG levert. Dit is dus GEEN geval van de "
            "uitzondering in §3 punt 3 (die gaat over Fotmob, de enige xG-bron voor vrijwel elke "
            "competitie), en het hoort niet vooraan in de notificatie."
        ),
        "ALLE_ZES_MARKTEN_HEBBEN_MEEGEDONGEN_EN_DE_LIJST_KOMT_UIT_DE_DATA": (
            "§1a eist dat zichtbaar is of een eenzijdige lijst uit de portemonnee komt of uit de "
            "data, en vandaag komt hij uit de data. Alle ZES spelende competities hebben een "
            "sportkey bij The Odds API en kregen de volledige bulk-aanroep met h2h + spreads + "
            "totals (3 credits elk, 18 totaal), plus BTTS in de tweede ronde voor ZES van de zeven "
            "duels met een kandidaat-edge (1 credit elk, 6 totaal) — 24 van een plafond van 879, "
            "en er staan nog 19.344 van de 20.000 van deze maand. Van de 91 doorgerekende "
            "selecties waren er 32 Over/Under, 23 Asian Handicap, 17 1X2, 12 BTTS, 5 Draw No Bet en "
            "2 Double Chance. Bij Bayern is de uitkomst na te rekenen: de BTTS-ja (+9,74 pp, kans "
            "0,618, score 6,018) verslaat de sterkste handicap (Köln +3 op +5,34 pp, die bovendien "
            "op poort 5 sneuvelt), en de 0-of-1-bet-regel laat er één over. Alleen Piast Gliwice – "
            "Korona Kielce kreeg geen BTTS: dat duel toonde geen kandidaat-edge en kwam de tweede "
            "ronde dus niet in — zo genoteerd in `markets_checked`, niet als 'opgevraagd maar niet "
            "gevonden' (§1a)."
        ),
        "HET_NIVEAU_KOMT_BIJ_VIJF_VAN_DE_ZES_UIT_VORIG_SEIZOEN_PLUS_UPLIFT": (
            "`model.league_level` kiest de route per competitie en legt hem vast in "
            "`data/run-state/` onder `niveau`; reken het niveau niet zelf uit. Vijf van de zes "
            "competities staan onder `SEASON_MATURE_SHARE` en krijgen de route `vorig+uplift`: La "
            "Liga (12 van 38 speeldagen, thuis 1,730 / uit 1,232 / basis 1,405), Bundesliga (9 van "
            "34, 1,954 / 1,602 / 1,674), Ligue 1 (10 van 34, 1,738 / 1,361 / 1,521), Belgian Pro "
            "League (11 van 30, 1,525 / 1,351 / 1,547) en Ekstraklasa (14 van 34, 1,731 / 1,275 / "
            "1,565). DE DANISH SUPERLIGA STAAT OP 14 VAN 22 SPEELDAGEN en dus boven de helft: daar "
            "kiest de functie de route `lopend` (1,643 / 1,417 / 1,531, ongeschaald) en houdt "
            "`uplift_observations` hem UIT de gepoolde correctie. Dat weglaten is zelf de meting en "
            "staat daarom expliciet in het rapport (§3 Stage 5): een stil overgeslagen waarneming "
            "is hetzelfde probleem als een stille truncatie in Stage 4. De gepoolde factor komt "
            "daarmee op 1,0991 over 56 speeldagen en vijf competities (ongewogen gepoold 1,1133)."
        ),
        "DE_NIVEAUCORRECTIE_IS_ZEVENTIEN_DAGEN_OUD_EN_ER_IS_NIETS_TE_BESLISSEN": (
            "LEVEL_SCALE = 1.032 bindt sinds 3 november (§6g, besluit van de gebruiker van 2 "
            "november) en is vandaag met `today=DAY` aan `analyze_match` en `robustness_check` "
            "meegegeven, bij élke aanroep. Hij raakt alleen de xG-methode en werkt dus voor 80% "
            "door in `my_prob` (§1f); `analyze_match_from_splits` blijft ongemoeid. LET OP DE "
            "RICHTING, want die is vandaag omgekeerd ten opzichte van gisteren: de correctie "
            "verhoogt het verwachte totaal, dus ze VERHOOGT P(Over) en verlaagt P(Under). Twee van "
            "de drie regels van vandaag staan op de Over-kant, dus deze knop heeft hun edge "
            "ongeveer twee procentpunt OMHOOG gezet in plaats van omlaag. Dat is de onvoorzichtige "
            "kant van dezelfde knop, en het hoort erbij te staan. ER IS NIETS TE BESLISSEN en de "
            "vraag hoort niet gesteld (§1h, §6g): de homogene reeks van ná 3 november is nog te "
            "klein, en `gridfit.py measure` meldt zelf luidruchtig zodra er duels in zitten die de "
            "correctie al dragen."
        ),
        "STAGE_0_WIKKELDE_EEN_PICK_AF_EN_VOND_EEN_REKENFOUT_VAN_GISTEREN": (
            "LEES DIT, WANT ER IS EEN REGEL IN HET LOGBOEK GECORRIGEERD. Stage 0 vond één "
            "afwikkelbare pick: Vitória – RB Bragantino (Under 2,75 @1,83, Run B van 19 nov), "
            "uitslag 2–1 met doelpunten in 4', 24' en 73' — dus drie doelpunten, alle drie binnen "
            "90 minuten. EEN KWARTLIJN SPLITST IN TWEE HALVE BETS (`ledger.pick_units`): bij "
            "exact 3 doelpunten verliest de 2,5-helft en is de 3,0-helft een PUSH, dus dit is een "
            "HALF verlies van −0,50u en niet een heel verlies van −1,00u. Zo geboekt, met "
            "`settled_units = -0.5`. DEZELFDE CONTROLE OVER HET HELE LOGBOEK VOND PRECIES ÉÉN "
            "TWEEDE GEVAL: Cruzeiro – Palmeiras van 18 november (Under 2,75, ook 2–1) stond als "
            "HEEL verlies geboekt; dat is dezelfde rekenfout en is gecorrigeerd naar −0,50u. Alle "
            "overige kwartlijnen in `picks.jsonl` en `shadow.jsonl` zijn goed geboekt (12 halve "
            "uitkomsten, alle met een expliciete `settled_units`). Verder afgewikkeld: twee "
            "schaduwrijen van Vasco da Gama – Internacional (2–1) — de Asian Handicap "
            "Internacional +1 is een PUSH en dus void, de 1X2 op Internacional verloren. Eén pick "
            "blijft open: Seattle Sounders FC – Real Salt Lake (Under 3,5), die trapt pas om 04:00 "
            "NL af en stond bij `ledger.py open` op −0,9 uur na aftrap."
        ),
        "DE_REFLECTIE_OP_DE_AFGEWIKKELDE_REGELS": (
            "§3 Stage 0 (12 okt 2026) vraagt bij elke afgewikkelde regel of de REDENERING klopte "
            "en niet alleen de uitkomst. (1) Vitória – RB Bragantino, Under 2,75, HALF VERLOREN op "
            "2–1: de xG-methode verwachtte 2,32 doelpunten en het werden er drie. Dat is binnen "
            "0,7 doelpunt van de eigen schatting, dus dit is half verloren en NIET verkeerd "
            "ingeschat — de wedstrijd liep ongeveer zoals voorgerekend en de kwartlijn lag precies "
            "op de grens. (2) De twee schaduwrijen van Vasco da Gama – Internacional, 2–1: de "
            "Asian Handicap Internacional +1 (tegengehouden op poort 5, xG +6,39 pp tegen splits "
            "−4,24 pp) eindigt op een PUSH, dus de poort heeft daar geen geld bespaard en ook geen "
            "geld gekost — dat is de minst informatieve uitkomst die er is. De 1X2 op Internacional "
            "@5,508 (poort 8, underdog) verloor, dus die poort deed zijn werk op dit duel. WAT DIT "
            "NIET BETEKENT: drie regels is geen reeks, en één van de drie is een push. §6d eist "
            "~30 gevallen en er is vandaag niets verzet."
        ),
        "STAGE_MIN_2_WAS_OPNIEUW_EEN_ONDIEPE_KLOON_EN_DAT_VERANDERT_DE_TELLING_VOLLEDIG": (
            "`git rev-parse --is-shallow-repository` gaf bij de start `true`, voor de derde "
            "opeenvolgende dag. Dezelfde repo, vóór en ná één commando: ondiep 64 commits lokaal "
            "en 90 van de 93 takken met 'eigen' commits (1 tot 691 stuks); na `git fetch "
            "--unshallow origin` 767 commits en NUL takken met eigen commits. Dat is exact het "
            "valse alarm waarvoor §3 Stage -2 zelf waarschuwt. DAARBOVENOP DE INHOUDELIJKE "
            "CONTROLE, want '0 eigen commits' is een uitspraak over de graaf en niet over de "
            "metingen (§3 Stage -2, 27 sep 2026): per logboek de identiteiten van álle takken "
            "verenigd en tegen `main` gelegd. `picks.jsonl` 565 van 565, `calibration.jsonl` 8439 "
            "van 8439 op sleutel (datum, run, wedstrijd, uitkomst), `context-log.jsonl` 2378 van "
            "2378, en `shadow.jsonl` 2000 van 2004 — DE VIER DIE ONTBREKEN ZIJN DE KALE "
            "ID-VORMEN VAN 3 OKTOBER (Canada – Peru, Croatia – England, Estonia – Luxembourg, "
            "Switzerland – Slovenia), die §3 Stage -2 bij naam noemt als dubbeltelling en MET "
            "OPZET weg houdt. Niet aangevuld. Geen tak is nieuwer dan `main` voor "
            "`source-health.json` of `coverage.json`. Er was dus niets te mergen. Deze run staat "
            "op `main` en pusht daarheen (§6a)."
        ),
    }

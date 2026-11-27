"""De `parameters`-tekst van Run B, 27 nov 2026 — apart gehouden zodat
`rb_nov27_publiceer.py` alleen de rekenlogica van 1 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **DRIE regels, waarvan ÉÉN boven zijn eigen lat.** Real Salt Lake – Vancouver Whitecaps staat op
  +8,41 pp tegen een `FULL`-drempel van 8,0; de andere twee komen volledig op rangorde (§5b).
* **De trigger die §1h punt 2 voor zichzelf stelde is nu ook per KANT EN TIER te meten, en de
  meting steunt het vermoeden niet.** BTTS-nee op `FULL` staat op −2,4% over 21 gevallen bij
  t = −0,10, en in de band 8–10 pp — precies de band waarvoor poort 9 op de Under-kant is gemaakt
  — staat hij op **+27,4% over 8 gevallen** in plaats van op de −33,2% die de Under-kant daar
  laat zien. De vraag is op 8 nov één keer aan de gebruiker voorgelegd (§6c) en wordt niet
  herhaald; de stand gaat als meting het runrapport in.
* **De tweede regel van vandaag staat zelf op BTTS-nee en in de slechtste band van die reeks.**
  Fluminense – Cruzeiro, +7,81 pp, dus de band 0–8 pp waar BTTS-nee op `FULL` op −53,8% over
  negen gevallen staat. Dat is een tegenspraak en §4 punt 2 zet die vooraan.
* **Diezelfde regel leunt voor driekwart op de splitsmethode** (+2,21 pp op xG tegen +26,86 pp op
  de splits; 0,2 × 26,86 is 75% van de ruwe +7,14 pp). Nagerekend over 266 beslist afgewikkelde
  picks met beide methodecijfers wijst dat NIET de verkeerde kant op — de groep waarin de splits
  meer dan de helft van de ruwe edge levert staat op +15,0% over 38 gevallen tegen −10,3% over
  228 — maar geen van beide haalt |t| = 2 en §6d geldt onverkort.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,041, b=0,027 op "
            "8847 afgerekende gevallen, fitted_through 2026-11-26. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band (+0,7 pp op 50%, "
            "+1,3 pp op 70%) en verlaagt alleen onder ongeveer 35%. Vandaag draagt hij de BOVENSTE "
            "regel: Real Salt Lake – Vancouver Whitecaps staat ruw op +7,31 pp en herijkt op "
            "+8,41 pp, en haalt dus pas door de herijking zijn eigen lat van 8,0. `bet_beide` is "
            "voor alle drie de regels FALSE, en dat is precies het geval waarvoor §5a die vlag "
            "heeft gebouwd: sinds de fit verhoogt in plaats van verlaagt, is 'herijkt haalt de lat, "
            "dus ruw ook' niet langer waar. Omdat de drempel sinds 20 sep geen poort meer is maar "
            "een afkapping (§5b), houdt die vlag geen enkele regel tegen — maar hij hoort wel "
            "genoemd. De selectie die ALLEEN op de ruwe schaal strandde gaat met "
            "`failed_gate = herijking_omgekeerd` naar het schaduwlogboek; die reeks staat nu op 8 "
            "kandidaten, 7 afgewikkeld, −70,9%. LEES DE FIT NIET ALS 'het model is goed "
            "gekalibreerd en dus goed': hij is gefit op de ONGESELECTEERDE ijksteekproef (§1g, "
            "20 sep 2026), en de scheefstand die telt zit in de GESELECTEERDE groep — die staat "
            "vandaag op z = +4,92 over 153 gespeelde Unders. Daarom staan poort 8 en poort 9 aan."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8, "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "DRIE_REGELS_EN_EEN_HAALT_ZIJN_EIGEN_LAT": (
            "MAX_SHORTLIST is 3 op vrijdag (ranking.max_shortlist; de wijziging van 18 nov 2026 "
            "bindt sinds 19 nov). Er staan precies drie publiceerbare selecties en de lijst is dus "
            "exact vol, zonder dat de LIJSTLENGTE iets heeft afgekapt: er is geen enkele "
            "`gekwalificeerd_niet_gepubliceerd`-regel en de reeks `lijstlengte` blijft op 35 "
            "kandidaten, 34 afgewikkeld, 16 winnaars, +4,60u = +13,5% staan. Van de drie haalt "
            "alleen Real Salt Lake – Vancouver Whitecaps zijn eigen drempel (+8,41 pp op FULL, lat "
            "8,0). Fluminense – Cruzeiro staat op +7,81 pp (lat 8,0) en Leganés – Sabadell op "
            "+10,11 pp op LIGHT (lat 16,0). Die twee staan er dus op RANGORDE en niet omdat er een "
            "voordeel is aangetoond — §5b schrijft voor dat dat er per regel bij staat, en dat is "
            "de enige lezing die klopt: dit is het beste van vandaag, geen gevonden voordeel. "
            "MAX_LIGHT_IN_SHORTLIST = 2 bindt niet: er is één LIGHT-regel."
        ),
        "DE_BTTS_TRIGGER_VAN_1H_IS_NU_PER_KANT_TE_METEN_EN_ZE_STEUNT_DE_REM_NIET": (
            "§1h punt 2 houdt BTTS buiten poort 9 met als reden dat 15 afgewikkelde BTTS-picks in "
            "beide richtingen samen geen meting is, en noemt dit 'het eerste wat opnieuw bekeken "
            "hoort te worden zodra die reeks ~30 haalt'. Op 8 nov 2026 haalde de gepoolde reeks de "
            "31 en is de vraag één keer aan de gebruiker voorgelegd met owner=besluit; §6c verbiedt "
            "hem te herhalen en dat gebeurt hier dus niet. Wat er sinds die dag bij is gekomen is "
            "dat de reeks nu ook PER KANT EN TIER boven de ~30 van §6d uit begint te komen, en dat "
            "verandert de lezing. Stand vandaag: 39 BTTS-picks, 38 beslist, +32,6%. Op de kant "
            "waar het vermoeden over gaat: BTTS-nee 23 beslist op +11,8%, en BTTS-nee op FULL 21 "
            "beslist op −2,4% bij t = −0,10. Naar band, niet cumulatief: 0–8 pp n=9 op −53,8% "
            "(t = −1,76), 8–10 pp n=8 op +27,4% (t = +0,73), 10–12 pp n=2 op +99,5%, 12–14 pp n=2 "
            "op +7,8%. Vergelijk met de Under-kant van Over/Under op FULL, waarvoor poort 9 "
            "gebouwd is: 0–8 pp n=69 op −17,6%, 8–10 pp n=17 op −33,2%, en de hele reeks 152 "
            "gevallen op −16,2% bij t = −2,11 — de enige van al deze reeksen die |t| = 2 haalt. "
            "HET MECHANISME DAT OP DE UNDER-KANT GEMETEN IS, IS OP BTTS-NEE NIET TERUG TE VINDEN: "
            "in de band waar poort 9 zijn bestaansrecht aan ontleent staat BTTS-nee met het "
            "OMGEKEERDE teken. Dat is geen pleidooi om BTTS alsnog onder de rem te brengen en ook "
            "geen pleidooi om poort 9 te verlichten — n=8 is ver onder de ~30 van §6d en de hele "
            "BTTS-nee-FULL-reeks staat op 21. Het is wél het antwoord op de vraag die §1h voor "
            "zichzelf opschreef: er is op dit moment geen gemeten grond om de rem uit te breiden. "
            "NIETS VERZET, en de vraag niet opnieuw voorgelegd."
        ),
        "DE_TWEEDE_REGEL_STAAT_IN_DE_SLECHTSTE_BAND_VAN_ZIJN_EIGEN_REEKS": (
            "Fluminense – Cruzeiro, BTTS beide ploegen scoren NEE @2,32, +7,81 pp op FULL. Die "
            "+7,81 valt in de band 0–8 pp, en dat is op BTTS-nee-FULL de SLECHTSTE band van de "
            "reeks: negen gevallen, twee winnaars, −53,8% bij t = −1,76. De regel is niet door een "
            "poort tegengehouden — poort 9 raakt BTTS met opzet niet (§1h punt 2) en alle zeven "
            "overige poorten staan open — maar hij staat in de ongunstigste hoek van zijn eigen "
            "logboek en dat hoort vooraan en niet in een voetnoot (§4 punt 2). Dezelfde kant op "
            "wijzen de frequenties van §4: Cruzeiro uit 72% BTTS dit seizoen (13 van 18), "
            "Fluminense thuis 67% (12 van 18), Cruzeiro lopend seizoen 69% en Fluminense 67%. "
            "Alleen de laatste vijf duels wijzen de kant van de bet op (Fluminense 2 van 5). Het "
            "model zet P(geen BTTS) op 50,9% tegen 43,1% voor de markt; de uitslagenreeks van "
            "beide ploegen zegt eerder het omgekeerde."
        ),
        "DIEZELFDE_REGEL_LEUNT_VOOR_DRIEKWART_OP_DE_SPLITSMETHODE_EN_DAT_IS_NAGEREKEND": (
            "Op Fluminense – Cruzeiro staat de xG-methode op +2,21 pp en de splitsmethode op "
            "+26,86 pp. Poort 5 is gehaald omdat beide boven de markt liggen — de poort toetst het "
            "TEKEN en niet de AFSTAND — maar met de weging van §1f (0,80 op xG) levert de "
            "splitsmethode 0,2 × 26,86 = 5,37 van de ruwe 7,14 pp, dus 75%. De methode met een "
            "vijfde van het gewicht levert driekwart van het voordeel, en §6e noemt juist die "
            "methode de scheefste van de twee. DAT IS NAGEREKEND EN HET WIJST NIET DE VERKEERDE "
            "KANT OP. Over 266 beslist afgewikkelde picks waarvan beide methodecijfers in het "
            "logboek staan: de groep waarin de splitsmethode MEER dan de helft van de ruwe edge "
            "levert staat op 38 gevallen, 23 winnaars, +15,0% bij t = +0,98; de groep waarin ze "
            "de helft of minder levert op 228 gevallen, 106 winnaars, −10,3% bij t = −1,58. Naar "
            "aandeel: 0–25% n=119 op −10,1%, 25–50% n=109 op −10,5%, 50–75% n=35 op +7,9%, boven "
            "75% n=3 op +98,3%. Geen van die reeksen haalt |t| = 2 en de bovenste band is n=3, dus "
            "hier valt niets te besluiten (§6d). Wat er wél staat: de zorg is redelijk, de cijfers "
            "steunen haar niet, en poort 5 blijft een tekenpoort. NIETS VERZET."
        ),
        "DE_BOVENSTE_REGEL_HEEFT_DE_SMALSTE_ROBUUSTHEIDSMARGE_VAN_DE_DRIE": (
            "Real Salt Lake – Vancouver Whitecaps, Draw No Bet op Vancouver @1,8232 "
            "(Matchbook-beurs: 1,84 bruto, 1,8232 na 2% commissie — §5 eist beide getallen). "
            "Poort 6 eist dat de edge nergens op het (shrink, rho)-grid omdraait, en het zwakste "
            "punt staat op +0,84 pp. Dat is open, maar het is de smalste van de drie: Leganés "
            "staat daar op +9,31 pp en Fluminense op +1,61 pp. De reeks `robuustheid` in het "
            "schaduwlogboek staat op 90 kandidaten, 88 afgewikkeld, −12,5% — de poort doet dus zijn "
            "werk, en een regel die hem met acht tienden van een procentpunt haalt is een regel die "
            "bij een iets andere parameterkeuze was afgevallen. Dat hoort in het rapport te staan "
            "en niet alleen in de JSON."
        ),
        "POORT_5_VANGT_DRIEKWART_WEG_EN_POORT_7_KOSTTE_TWEE_DUELS": (
            "137 selecties doorgerekend over alle zes de markten op 18 van de 19 duels "
            "(Artis Brno – Slovácko komt op NONE uit). De poortverdeling: 104 van de 137 (76%) "
            "sneuvelden op poort 5, de bevestiging door de tweede methode — de twee methodes "
            "sloegen de markt niet dezelfde kant op. Verder 12 op de edge-afkapping, 6 op de "
            "koersband, 4 op poort 7 (context), 4 op poort 8 (underdog), 3 op poort 6 "
            "(robuustheid), 2 op poort 9 (doelpunten_onder) en 2 bleven volledig open. POORT 7 "
            "KOSTTE TWEE HELE DUELS: Grazer AK – Altach (Grazer AK mist 31% van de selectiewaarde "
            "tegen 11% bij Altach — Liam Hermesh geschorst, Tobias Koch en Ludwig Vraa-Jensen "
            "geblesseerd) en MVV Maastricht – Jong PSV (Jong PSV mist 59% van de selectiewaarde "
            "tegen 0% bij MVV; Sami Ouaissa day to day). Beide stonden op een kandidaat met een "
            "ruime edge — Grazer AK 1 @3,53 op +7,50/+9,93 pp en Jong PSV 2 @3,03 op "
            "+11,29/+19,42 pp — en beide gaan met `failed_gate = context` het schaduwlogboek in. "
            "Die reeks staat op 159 kandidaten, 153 afgewikkeld, −23,8%: van alle poorten de "
            "meest overtuigend negatieve, dus dit is de poort die zijn werk doet."
        ),
        "TIEN_VAN_DE_ZEVENTIEN_COMPETITIES_SPELEN_EN_DAT_IS_OP_DRIE_WEGEN_NAGETROKKEN": (
            "Negentien duels in het venster [08:00 NL 27 nov, 08:00 NL 28 nov), verdeeld over tien "
            "competities: Keuken Kampioen Divisie 7, Romanian SuperLiga 2, 2. Bundesliga 2, MLS 2 "
            "en Czech First League, Croatian HNL, Hungarian NB I, Segunda División, Austrian "
            "Bundesliga en Série A (BRA) met elk 1. Dat is de ruimste runlijstdag sinds 22 "
            "november. De zeven stille competities — Greek Super League, Eliteserien, Allsvenskan, "
            "Serie B, Swiss Super League, English League One en English League Two — zijn GEEN "
            "WEDSTRIJD en geen gat (§3 Stage 2). Langs drie wegen nagetrokken: (1) idcheck.py "
            "geeft 33 van 33 bruikbare standen met afsluitcode 0, dus geen enkele competitie is "
            "stil uit de runlijst verdwenen zoals het Serie B-id in september; (2) runwindow.py "
            "over twee daglijsten (157 wedstrijden op 27 nov, 573 op 28 nov); (3) BetExplorer per "
            "competitie, dat 17 van 17 met Fotmob eens is en op hetzelfde totaal van 19 duels "
            "uitkomt. Alle negentien duels zijn `playable = True`. Drie staan op een Amerikaanse "
            "klok: Fluminense – Cruzeiro om 00:00 NL en Columbus Crew – Inter Miami CF om 02:00 NL "
            "en Real Salt Lake – Vancouver Whitecaps om 04:00 NL, alle drie op 28 november. Onder "
            "de oude UTC-lezing van vóór 24 sep 2026 waren die drie bij de verkeerde run beland."
        ),
        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "Negentien duels op een vrijdagcap van 55 (`ranking.max_deep_analyses`), dus de "
            "afkapping van Stage 4 bindt niet en de dekkingstabel krijgt geen AFGEKAPT-regel. "
            "Datarijkdom van 5,0 (Györi ETO – Debrecen, Leganés – Sabadell en Bochum – Darmstadt) "
            "tot 8,0 (Jong AZ Alkmaar – TOP Oss); omdat er niets afviel is er geen laagste die het "
            "haalde en geen hoogste die afviel te noemen. De context is voor alle negentien duels "
            "opgehaald, dus ook voor het duel op NONE — dat is wat §1c eist en het kost geen "
            "credits."
        ),
        "VIJF_COMPETITIES_HEBBEN_GEEN_XG_EN_DAT_ZIJN_TWAALF_VAN_DE_NEGENTIEN_DUELS": (
            "Fotmob levert xG voor Segunda División (140), 2. Bundesliga (146), Austrian "
            "Bundesliga (38), MLS (130) en Série A (BRA) (268) — samen zeven duels — en GEEN xG "
            "voor Czech First League (122), Croatian HNL (252), Hungarian NB I (212), Romanian "
            "SuperLiga (189) en Keuken Kampioen Divisie (111), samen twaalf duels. Die vijf draaien "
            "op doelpunten als sterktemaat en komen dus op LIGHT uit met de lat van 16,0 pp "
            "(`prompts/run-b.md`). De Keuken Kampioen Divisie alleen al is zeven van die twaalf. "
            "NEEM DEKKING NOOIT OVER VAN EEN ANDERE COMPETITIE IN HETZELFDE LAND: Duitsland heeft "
            "xG in de 2. Bundesliga en Nederland niet in de Keuken Kampioen Divisie, terwijl beide "
            "landen het in hun hoogste divisie wel hebben. Per competitie nagetrokken in Stage 3 "
            "en vastgelegd in coverage.json. Eindstand: 5 FULL, 13 LIGHT, 1 NONE."
        ),
        "EEN_DUEL_OP_NONE_OM_EEN_GEMETEN_REDEN": (
            "Artis Brno – Slovácko (Czech First League) komt op data_tier = NONE uit. Artis Brno "
            "staat niet in de Tsjechische stand van 2025/2026 en is dus een promovendus; "
            "`promotion.convert` weigert de omrekening omdat ze buiten het gemeten bereik valt "
            "(`conversion_in_range`). Dat is een GEMETEN weigering en geen ontbrekende bron: §4 "
            "schrijft voor dat een promovendus eerst wordt omgerekend en pas op NONE komt als die "
            "omrekening niet te onderbouwen is. Er is voor dit duel dus niets doorgerekend, het "
            "heeft geen enkele kandidaat, en het staat met een STREEPJE in de scorekolom van de "
            "rangschikking en niet met een nul (§5, punt 3). De zes andere promovendi-duels van "
            "vandaag kwamen de omrekening wél door: Sepsi OSK, Sabadell, FC Heidenheim, Heracles, "
            "NAC Breda en de tegenstanders van Jong Ajax."
        ),
        "DE_INKOOP_EN_DE_MARKTBALANS": (
            "Vijf van de tien spelende competities hebben een sportkey bij The Odds API — Segunda "
            "División, 2. Bundesliga, Austrian Bundesliga, MLS en Série A (BRA) — en kregen alle "
            "vijf de bulkaanroep h2h+spreads+totals: 15 credits. Daarna een tweede ronde BTTS per "
            "event voor de duels met een kandidaat-edge, zeven keer met een sportkey: 7 credits. NA "
            "DE NAAMREPARATIE HIERONDER IS DE ANALYSE OPNIEUW GEDRAAID EN IS DIE TWEEDE RONDE NOG "
            "EEN KEER UITGEVOERD, wat 7 credits EXTRA kostte die niets nieuws opleverden (de twee "
            "duels die er bij kwamen hebben geen sportkey). Totaal 29 van een plafond van 2352 "
            "(`suggest_cap` op 18838 over en 4 dagen tot de maandwissel); 18809 over na deze run. "
            "Dat de herhaling niet gratis was hoort hier te staan en niet verzwegen. De vijf competities zonder "
            "sportkey draaien op het gratis BetExplorer-marktgemiddelde, dat voor alle tien de "
            "competities een fixturepagina gaf. MARKTBALANS: 1X2 45 selecties over 9 competities, "
            "Over/Under 34 over 5, Asian Handicap 26 over 5, BTTS 14 over 5, Draw No Bet 11 over 5 "
            "en Double Chance 4 over 3. Alle zes de markten hebben dus werkelijk meegedongen, en "
            "de drie regels komen uit drie VERSCHILLENDE markten (DNB, BTTS, Over/Under). Dat is "
            "geen quotum dat is gehaald maar de uitkomst; §5 eist alleen dat de inkoop zichtbaar "
            "is naast het resultaat."
        ),
        "PINNACLE_IS_HET_OP_DE_BOVENSTE_REGEL_HET_MEEST_ONEENS": (
            "Stap 2 van Stage 5: Pinnacle's de-vigde 1X2 naast de eigen kans, los van de beste "
            "prijs. Zeven van de negentien duels hebben een Pinnacle-1X2, met een marge van 3,5 tot "
            "4,6% tegen 6 tot 10% bij de rest. Gemiddelde absolute afstand tot het "
            "Pinnacle-oordeel 5,70 pp. De uitersten: FC Heidenheim – 1. FC Nürnberg (het model zet "
            "Heidenheim 21,9 pp hoger dan Pinnacle — en dat duel is géén bet), en Fluminense – "
            "Cruzeiro, waar het model en Pinnacle op de 1X2 vrijwel exact samenvallen (−0,01 / "
            "+0,37 / −0,35 pp). Op de BOVENSTE regel is Pinnacle het juist oneens: bij Real Salt "
            "Lake – Vancouver geeft Pinnacle de thuisploeg 35,0% en het model 27,9%, en Vancouver "
            "39,4% tegen 48,8% — een afstand van 9,4 pp op precies de kant waarop gewed wordt. Op "
            "de totalen (zeven paren) staat het model gemiddeld +0,27 pp boven Pinnacle op de "
            "Under-kant, met Leganés – Sabadell als enige grote uitschieter de ANDERE kant op: "
            "−14,05 pp, dus het model verwacht daar aanzienlijk meer doelpunten dan Pinnacle. Dat "
            "is de onderbouwing van de derde regel én de grootste onenigheid van de dag. §2 blijft "
            "hard: niets hiervan zit in my_prob of in prob_sources."
        ),
        "STAGE_0_HAD_NIETS_AF_TE_WIKKELEN_EN_DRIE_PICKS_STAAN_TERECHT_OPEN": (
            "`ledger.py open` en `shadow.py open` geven beide 'geen enkele klaar om af te "
            "wikkelen'. Dat is de juiste uitkomst en geen overgeslagen stap: Run A van vandaag "
            "heeft om 02:40 UTC de twee picks en 34 schaduwrijen van 26 november afgewikkeld "
            "(Union St.Gilloise – Lech Poznań 2–2, Over 2.5 verloren; Lyon – Lillestrøm 0–0, Under "
            "gewonnen). Wat nu openstaat zijn de DRIE picks van Run A van vandaag — Nottingham "
            "Forest – Chelsea, Alanyaspor – Konyaspor en Levante – Racing Santander — en die "
            "trappen alle drie pas vanavond af; de bron meldt ze 14 tot 17 uur vóór de aftrap, "
            "dus `settleable` zegt terecht nee. Tien schaduwrijen van vandaag staan om dezelfde "
            "reden open. De reflectie van §3 Stage 0 hoort dus bij Run A van vandaag en niet hier; "
            "`report.py` vult de afrekentabel van het dagrapport zelf uit picks.jsonl (§6c, 4 okt "
            "2026) en die blijft vandaag leeg."
        ),
        "STAGE_MIN_2_NEGENNEGENTIG_TAKKEN_NAGELOPEN_EN_ZEVENTIEN_MELDINGEN_DIE_GEEN_VERLIES_ZIJN": (
            "De repo kwam als ONDIEPE kloon binnen (`--is-shallow-repository` → true), dus eerst "
            "`git fetch --unshallow origin`: zonder die stap telt elke commit van vóór de knip als "
            "'nog niet hier' en krijg je het valse alarm van 20 aug 2026. HEAD stond al gelijk aan "
            "origin/main (0 commits beide kanten op) en de remote tak van deze sessie bestond niet "
            "meer. `branchaudit.py` over 99 takken, per record op de inhoud: picks.jsonl (606), "
            "context-log.jsonl (2619), calibration.jsonl (9301) en coverage.json (339) staan "
            "VOLLEDIG. Er zijn 17 meldingen en geen van de 17 is verlies. (1) VIER schaduwrijen van "
            "3 oktober — Canada – Peru, Croatia – England, Switzerland – Slovenia en Estonia – "
            "Luxembourg in de kale vorm. Die zijn op 7 nov 2026 met opzet VERWIJDERD omdat ze een "
            "dubbeltelling waren (elk stond er twee keer in, via near_miss én via "
            "poort8_geblokkeerd, wat §1e punt 2 verbiedt); de bewaarde rijen zijn die met de "
            "-p8-0-suffix en die staan alle vier op main met identieke inhoud. §3 Stage -2 zegt "
            "met zoveel woorden: vul ze bij een merge NIET aan. (2) DERTIEN bladpaden in "
            "source-health.json. Alle dertien zijn per waarde vergeleken en staan al op main, één "
            "nestlaag dieper dan het padgewijze oordeel van branchaudit kijkt: de zes "
            "`betexplorer_*` van Run C onder detail_history[1] (16 nov) en [2] (14 nov), "
            "`samenvatting` onder last_run_run_b.history[7] (8 nov), de vier `fotmob_*` onder "
            "history[4] (19 nov), en `pinnacle_via_odds_api` en `interleague` onder "
            "last_run_run_a_history[2] (24 nov). Dat is dezelfde bevinding die het `_merge_note` "
            "van 24 nov al vastlegde. (3) `sources.oddspapi` is een bekend besluit van 30 aug "
            "2026. ER VIEL DUS NIETS TE MERGEN, en de run staat op main."
        ),
        "HET_NIVEAU_KOMT_BIJ_ZES_COMPETITIES_UIT_VORIG_SEIZOEN_EN_BIJ_VIER_UIT_HET_LOPENDE": (
            "`model.league_level` kiest per competitie de route en legt die vast onder `niveau`. "
            "Route `lopend` (seizoen op of boven de helft, niveau ongeschaald uit het lopende "
            "seizoen): Czech First League, Romanian SuperLiga, Austrian Bundesliga, MLS en Série A "
            "(BRA). Route `vorig+uplift`: Croatian HNL, Hungarian NB I, Segunda División, "
            "2. Bundesliga en Keuken Kampioen Divisie. De gepoolde vroeg-seizoenscorrectie staat op "
            "factor 1,0330 (gepoold 1,0428 over 27 speeldagen, 2 competities), en ACHT van de tien "
            "competities zijn uit die pool GEHOUDEN — zes omdat ze geen xG hebben en dus geen "
            "bruikbare waarneming leveren (Czech, Croatian, Hungarian, Romanian, Keuken Kampioen "
            "Divisie) en drie omdat hun seizoen over de helft is (Austrian Bundesliga 13 van 22, "
            "MLS 34 van 34, Série A 37 van 38). Dat weglaten is zelf de meting en staat daarom "
            "integraal in het rapport; een stil overgeslagen waarneming is hetzelfde probleem als "
            "een stille truncatie in Stage 4. De vier kalenderjaarcompetities krijgen de notatie "
            "'2025'/'2026' en niet '2025/2026', want Fotmob valt op een onbekende notatie stil "
            "terug op het lopende seizoen (`run-b.md`). `LEVEL_SCALE` = 1,032 staat in de "
            "lambdaketen van de xG-methode met `today` = de rundag, en NIET in de splitsmethode."
        ),
        "DE_DOELPUNTENKALIBRATIE_EN_WAAROM_GEEN_VAN_DE_DRIE_REGELS_EEN_UNDER_IS": (
            "`margins.py goalbias` over 2495 doorgerekende duels: het model als geheel staat op "
            "+0,017 doelpunt per duel bij z = +0,48, dus de lambdas kloppen. De SELECTIE niet: de "
            "153 duels waarin werkelijk een Under is gespeeld staan op +0,661 doelpunt per duel bij "
            "z = +4,92, en de 83 waarin een Over is gespeeld op −0,374 bij z = −1,85. Dat zijn twee "
            "verschillende fouten en ze mogen niet worden opgeteld. VANDAAG IS GEEN VAN DE DRIE "
            "REGELS EEN OVER/UNDER OP DE UNDER-KANT, en dat is geen toeval maar het werk van poort "
            "9: die hield twee selecties tegen (reeks `doelpunten_onder`: 54 kandidaten, 52 "
            "afgewikkeld, −35,9%). Wat er wél staat is één OVER (Leganés – Sabadell, Over 2) en één "
            "BTTS-nee, en die laatste leunt dezelfde kant op als een Under zonder door poort 9 te "
            "zijn getoetst. De vormtabel: P(Under 2.5) voorspeld 42,3% tegen werkelijk 41,0% "
            "(−1,3 pp), P(Under 3.0) 63,8% tegen 63,1%. Die fout is sinds de niveaucorrectie van "
            "2 november klein; Run A heeft vandaag gemeten dat ze op de 519 duels van ná 3 november "
            "van teken is OMGESLAGEN (−0,116 per duel, z = −1,43) en daar terecht niets aan verzet, "
            "want 519 is onder de lat van ~900 die Run A zelf op 21 november heeft gezet."
        ),
        "GEREPAREERD_TWEE_DUELS_VERLOREN_AL_HUN_PRIJZEN_AAN_EEN_NAAMKOPPELING": (
            "GEMETEN, GEREPAREERD EN DE RUN IS DAARNA OPNIEUW GEDRAAID. Twee van de negentien "
            "duels kwamen de analyse binnen met NUL prijzen in alle zes de markten en werden "
            "gerapporteerd als 'geen prijzen gevonden voor deze wedstrijd' — terwijl de prijzen op "
            "precies de BetExplorer-pagina stonden die deze run al had opgehaald. (1) JONG AZ "
            "ALKMAAR - TOP OSS: BetExplorer schrijft 'Jong AZ - Oss'. De paarscore van "
            "`ra_names.best_pair` is (0,636 + 0,600) / 2 = 0,618, TWEE DUIZENDSTEN onder de vloer "
            "van 0,62, en de woordterugval van 30 okt 2026 redde alleen de thuisploeg: "
            "['jong','az'] is een KOP van ['jong','az','alkmaar'], maar ['oss'] is geen kop van "
            "['top','oss'] — het is de STAART. (2) UNIVERSITATEA CLUJ - SEPSI OSK: BetExplorer "
            "schrijft 'U. Cluj - Sepsi Sf. Gheorghe'. Paarscore (0,500 + 0,538) / 2 = 0,519. "
            "DE REPARATIE: `_prefix_pair` is `_affix_pair` geworden en kijkt nu ook naar de "
            "staartrichting, met dezelfde drie eisen eromheen (fuzzy moet eerst hebben gefaald, "
            "BEIDE ploegen moeten koppelen, precies ÉÉN rij mag overblijven) plus een eigen rem: "
            "de woorden die in de staartrichting wegvallen mogen geen RESERVEAANDUIDING zijn "
            "(`_RESERVE`: jong, ii, b, u21, u23, reserves...), want ['psv'] is een staart van "
            "['jong','psv'] en MVV Maastricht - Jong PSV stond dezelfde ochtend op de runlijst. "
            "`python3 tmp-run/ra_names.py` telt nu 26 controles, allemaal groen, inclusief de "
            "Excelsior-val van 27 okt 2026 en de nieuwe PSV-tegenproef. GEVAL 2 BLIJFT MET OPZET "
            "ONGEKOPPELD: 'U. Cluj' is een AFKORTING (geen kop en geen staart) en 'Sepsi OSK' "
            "deelt met 'Sepsi Sf. Gheorghe' alleen het eerste woord; koppelen op één gedeeld "
            "woord is exact de Excelsior-val. Liever geen prijs dan de verkeerde. WAT DE REPARATIE "
            "OPLEVERDE: de analyse is volledig opnieuw gedraaid, Jong AZ Alkmaar - TOP Oss heeft "
            "nu drie doorgerekende selecties (1X2 op het BetExplorer-marktgemiddelde; deze "
            "competitie heeft geen sportkey) en het selectietotaal gaat van 134 naar 137. GEEN "
            "ENKELE van die drie haalt de rangorde, dus DE GEPUBLICEERDE LIJST IS ONGEWIJZIGD. "
            "DRIE DINGEN DIE HIERBIJ HOREN. (a) `progress.py verify` STOND GROEN, zowel voor als "
            "na de reparatie: `markets_checked` had per markt een reden, en die reden was "
            "onwaar. Een controle op de administratie slaagt dus op een onjuiste reden — dezelfde "
            "stille faalstand als het Serie B-id, `calibration.py settle` en `settled_note`. (b) "
            "DIT IS DE VIERDE KEER IN DEZE FAMILIE: 'la galaxy' (17 okt), 'red bull new york' "
            "(30 sep), 'Roda - Jong AZ' (30 okt) en nu deze twee, en Jong AZ is voor de tweede "
            "keer betrokken. (c) EEN TWEEDE RISICO IS GEVONDEN EN NIET AANGERAAKT: de FUZZY laag "
            "koppelt 'Jong PSV' op een paarscore van 0,773 wél aan een rij die 'PSV' noemt, want "
            "0,545 op de naam plus 1,000 op de tegenstander ligt boven de vloer van 0,62. Dat is "
            "een bestaande eigenschap van die laag en niet van deze reparatie, het kostte vandaag "
            "niets (een reserveploeg en zijn hoofdmacht staan nooit op dezelfde "
            "competitiepagina), en de vloer verlagen of verhogen is een parameterkeuze. EEN RUN "
            "VERZET DIE NIET OP EIGEN INITIATIEF; hij staat hier gemeld."
        ),
        "DE_STAND_VAN_DE_LOGBOEKEN": (
            "`ledger.py stats`: 606 picks, 3 open, 603 afgewikkeld, 66 void; 249 van 537 = 46,4% "
            "trefkans; −31,39u = −5,8% ROI; Brier eigen 0,2630 tegen markt 0,2433, dus DE MARKT IS "
            "NOG STEEDS BETER (verschil −0,0197) en dat is de enige regel die zegt of de "
            "edge-schatting iets toevoegt. FULL 456 picks op −6,6%, LIGHT 150 op −3,7%. "
            "`shadow.py stats`: 2125 afgewezen kandidaten, 2027 afgewikkeld, −3,8% — de poorten "
            "samen bespaarden 77,06u. Per poort: context −23,8% (n=153), doelpunten_onder −35,9% "
            "(n=52), odds −56,6% (n=51), robuustheid −12,5% (n=88), tweede_methode −2,3% (n=334), "
            "underdog −1,3% (n=441), data −8,5% (n=55), herijking −3,3% (n=59), "
            "herijking_omgekeerd −70,9% (n=7). TWEE REEKSEN STAAN POSITIEF en dat betekent dat die "
            "afwijzing geld kostte: `edge` op +5,4% over 736 gevallen en `lijstlengte` op +13,5% "
            "over 34. De eerste is precies waarom §5b de drempel van poort naar afkapping heeft "
            "verplaatst; de tweede is de reeks waarnaar de gebruiker bij 100 gevallen opnieuw "
            "kijkt (§5b) — hij staat op 34 en een run verzet MAX_SHORTLIST nooit op eigen "
            "initiatief. `calibration.py stats` over 3106 wedstrijden: my_prob staat +1,74 pp boven "
            "de markt op longshots en −3,60 pp eronder op favorieten, en de splitsmethode (+1,75 / "
            "−3,70) is daar nog altijd iets scheever dan de xG-methode op shrink 1,0 (+1,01 / "
            "−2,03). `ctxlog.py stats`: 2602 afgewikkelde wedstrijden, r = −0,040 bij t = −1,92 "
            "voor de modelfout tegen het beschikbaarheidsverschil — nog steeds onder de lat, maar "
            "het teken is al weken hetzelfde en de drempel van aantoonbaarheid staat nu op ~11 pp "
            "per eenheid. Poort 7 blijft een rem en geen bijstelling (§1c)."
        ),
    }

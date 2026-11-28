"""De `parameters`-tekst van Run B, 28 nov 2026 — apart gehouden zodat
`rb_nov28_publiceer.py` alleen de rekenlogica van 1 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **VIJF regels, en alle vijf op de UNDER-kant van Over/Under.** Dat is niet eerder voorgekomen
  bij Run B. Twee ervan halen hun eigen lat (Rosenborg – Molde +16,16 pp en Bodø/Glimt – KFUM
  +10,82 pp, beide boven de verzwaarde Under-lat van 10,0), drie staan er volledig op rangorde
  (§5b) met +7,56, +6,93 en +6,86 pp.
* **De bevinding van Run A van vandaag is per run uitgesplitst en de uitsplitsing zegt iets
  nieuws.** De fout per wedstrijd is op beide runs even groot (Run A +0,620 doelpunt per duel over
  65 Unders, z = +2,96; Run B +0,692 over 88, z = +3,95), maar de BLOOTSTELLING verschilt een
  factor vijf: Run B speelde 107 Unders tegen 21 Overs, Run A 77 tegen 90. Het mechanisme is dus
  niet van Run B; de blootstelling eraan wel.
* **Poort 9 hield vandaag nul selecties tegen, en dat is per ontwerp.** Hij bindt alleen in de band
  8–10 pp op FULL; de twee regels erboven halen hem en de drie eronder raakt hij niet. Zijn eigen
  reeks staat op 54 afgewikkelde gevallen op −30,7%, dus de rem doet wat hij doet — het probleem
  zit in wat er langs hem komt.
* **De vraag of poort 9 ook onder de gewone drempel en op `LIGHT` moet gelden is op 22, 23, 24, 25
  en 26 november voorgelegd en wordt hier NIET opnieuw gesteld.** §1h, §6c en §9 (rem 3) verbieden
  dat met zoveel woorden, en Run B van 27 november heeft hem al teruggezet naar `owner = ik`. De
  stand van de reeks gaat als meting het rapport in en niet als besluitpunt.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,037, b=0,024 op "
            "8922 afgerekende gevallen, fitted_through 2026-11-27. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band (+0,6 pp op 50%, "
            "+1,1 pp op 70%) en verlaagt alleen onder ongeveer 35%. Vandaag tilt hij alle vijf de "
            "regels: Rosenborg – Molde van +15,02 naar +16,16 pp, Bodø/Glimt – KFUM van +9,71 naar "
            "+10,82 pp — en díe tweede is de enige die er iets aan verandert, want zonder de "
            "herijking haalt hij de verzwaarde Under-lat van 10,0 niet. `bet_beide` is voor vier "
            "van de vijf regels FALSE; alleen Rosenborg – Molde haalt beide schalen. Dat is precies "
            "het geval waarvoor §5a die vlag heeft gebouwd: sinds de fit verhoogt in plaats van "
            "verlaagt, is 'herijkt haalt de lat, dus ruw ook' niet langer waar. Omdat de drempel "
            "sinds 20 sep geen poort meer is maar een afkapping (§5b), houdt die vlag geen enkele "
            "regel tegen — maar hij hoort wel genoemd. LEES DE FIT NIET ALS 'het model is goed "
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
        "VIJF_REGELS_EN_ALLE_VIJF_OP_DEZELFDE_KANT": (
            "MAX_SHORTLIST is 5 op zaterdag (ranking.max_shortlist; de wijziging van 18 nov 2026 "
            "bindt sinds 19 nov). Er staan precies vijf regels en alle vijf zijn een Over/Under op "
            "de UNDER-kant: Rosenborg – Molde Under 4 @1,83 (+16,16 pp), Bodø/Glimt – KFUM "
            "Under 4.5 @1,7252 (+10,82 pp), Los Angeles FC – St. Louis City Under 3.5 @1,69 "
            "(+7,56 pp), AFC Wimbledon – Barnsley Under 3 @1,92 (+6,93 pp) en Las Palmas – FC "
            "Andorra Under 2.5 @2,23 (+6,86 pp). Alle vijf op FULL, dus MAX_LIGHT_IN_SHORTLIST = 2 "
            "bindt niet. VAN DE VIJF HALEN ER TWEE EEN AANGETOOND VOORDEEL en drie staan er op "
            "RANGORDE: §5b schrijft voor dat dat er per regel bij staat, en dat is de enige lezing "
            "die klopt — dit is het beste van vandaag, geen gevonden voordeel. DE LIJSTLENGTE "
            "BINDT NIET: er is geen enkele `gekwalificeerd_niet_gepubliceerd`-regel, want er zijn "
            "maar twee wedstrijden met een selectie die alle negen poorten én de drempel haalt "
            "(Rosenborg – Molde en Bodø/Glimt – KFUM, beide Eliteserien). De reeks `lijstlengte` "
            "blijft daarmee op 35 kandidaten, 34 afgewikkeld, 16 winnaars, +4,60u = +13,5% staan. "
            "De gebruiker kijkt bij 100 afgewikkelde gevallen opnieuw (§5b, 18 nov 2026); het zijn "
            "er 34, dus die vraag hoort vandaag niet gesteld."
        ),
        "DE_BEVINDING_VAN_RUN_A_PER_RUN_UITGESPLITST_EN_DAT_ZEGT_IETS_NIEUWS": (
            "Run A heeft vanmorgen vastgesteld dat de routine aan BEIDE kanten van de "
            "doelpuntenmarkt de verkeerde wedstrijden kiest: over 153 gespeelde Unders vielen er "
            "+0,661 doelpunt per duel méér dan de eigen lambda zei (z = +4,92) en over 87 gespeelde "
            "Overs −0,368 minder (z = −1,87), terwijl de hele populatie van 2521 doorgerekende "
            "duels op +0,019 staat (z = +0,56). Dat is dus selectie en geen rekenfout, en die "
            "bevinding staat en wordt hier niet overgedaan. WAT ER VANDAAG BIJ KOMT, is de "
            "uitsplitsing per run, en die is niet eerder gemaakt. Per wedstrijd is de fout op "
            "beide runs even groot: Run A +0,620 doelpunt per duel over 65 Unders (z = +2,96), "
            "Run B +0,692 over 88 (z = +3,95); op de Over-kant Run A −0,386 over 72 (z = −1,77) en "
            "Run B −0,280 over 15 (z = −0,61). HET VERSCHIL ZIT IN DE BLOOTSTELLING EN NIET IN HET "
            "MECHANISME: Run B heeft 107 Unders tegen 21 Overs gepubliceerd en Run A 77 tegen 90. "
            "In november alleen: Run B 30 Unders tegen 5 Overs, Run A 18 tegen 22. In geld: "
            "Run B / Under 107 gevallen op −14,3% (t = −1,56) en −15,25u, Run A / Under 77 op "
            "−21,9% (t = −2,03) en −16,89u, Run A / Over 90 op +6,3% (t = +0,63) en +5,63u. "
            "Run B staat dus vijf keer zo vaak op de kant waar de fout het grootst is, en vandaag "
            "staat hij er vijf van de vijf keer. WAT HIER NIET UIT VOLGT: geen poort erbij, geen "
            "lat verzet, geen quotum op markten (§1 verbiedt bets forceren om een verdeling te "
            "halen, en dat geldt ook de andere kant op). Het is een meting over de blootstelling "
            "van déze runlijst en ze hoort over weken gelezen (§6d), niet op één dag. NIETS "
            "VERZET."
        ),
        "POORT_9_HIELD_NUL_SELECTIES_TEGEN_EN_DAT_IS_PER_ONTWERP": (
            "`unders.check` bindt uitsluitend in de band tussen de gewone drempel (8,0) en de "
            "verzwaarde lat (10,0) op FULL, en vandaag zit daar geen enkele selectie in: de twee "
            "bovenste regels staan op +16,16 en +10,82 pp en halen de lat van 10,0 dus ruim, de "
            "drie onderste staan op +7,56, +6,93 en +6,86 pp en liggen onder de 8,0 — daar geeft "
            "`unders.check` zelf `passed = True` met als reden dat `edge` de bindende poort is en "
            "niet poort 9. ONDER §5b IS `edge` GEEN POORT MEER MAAR EEN AFKAPPING, dus die drie "
            "regels zijn langs geen enkele doelpuntenrem gegaan. Dat is geen nieuwe bevinding en "
            "geen defect: het is de vraag die op 22, 23, 24, 25 en 26 november aan de gebruiker is "
            "voorgelegd (`owner = besluit`) en die Run B van 27 november heeft teruggezet naar "
            "`owner = ik` omdat de meting de uitbreiding niet steunt. §1h, §6c en §9 (rem 3) "
            "verbieden het opnieuw stellen van een voorgelegde vraag, en dat gebeurt hier dus niet. "
            "De stand van de reeksen, als meting: `doelpunten_onder` 55 kandidaten, 54 afgewikkeld, "
            "20 winnaars, −16,58u = −30,7% — de poort bespaart geld en doet zijn werk. Op de "
            "FULL-Under-kant van picks.jsonl per band, niet cumulatief: 0–8 pp n=69 op −17,6% "
            "(t = −1,51), 8–10 pp n=17 op −33,2%, 10–12 pp n=27 op −8,7%, 12–14 pp n=19 op −10,0%, "
            "14+ pp n=20 op −12,8%. De hele FULL-Under-reeks staat op 152 gevallen, −16,2%, "
            "t = −2,11 en is daarmee de ENIGE reeks in dit logboek die |t| = 2 haalt. NIETS "
            "VERZET."
        ),
        "DE_NIVEAUCORRECTIE_HEEFT_HAAR_OMGESLAGEN_TEKEN_GEHOUDEN_EN_IS_NOG_NIET_TE_BEOORDELEN": (
            "§6g eist dat op de duels van ná 3 november de regel 'gemiddeld totaal' van "
            "`gridfit.py measure` naar nul zakt en de fout op P(Under 2.5) klein blijft. Stand "
            "vandaag op die 545 duels: gemiddeld totaal voorspeld 3,095 tegen werkelijk 2,998, dus "
            "−0,097 per duel bij z = −1,29, en P(Under 2.5) voorspeld 41,18% tegen werkelijk "
            "43,12%, dus +1,94 pp bij z = +0,92. Vóór de correctie stond datzelfde gemiddelde op "
            "+0,100 (z = +1,93) en P(Under 2.5) op −2,35 pp. DE FOUT IS DUS NIET NAAR NUL GEZAKT "
            "MAAR ER DOORHEEN GESCHOTEN, met ongeveer dezelfde omvang in de andere richting — en "
            "geen van beide getallen haalt |z| = 2. Op de gemengde reeks van 1718 duels staat het "
            "gemiddelde op +0,037 (z = +0,84) en P(Under 2.5) op −1,01 pp, maar die reeks mengt "
            "545 duels die de correctie al in zich dragen met 1173 die dat niet doen, en "
            "`gridfit.py` waarschuwt daar zelf luidruchtig voor. §6g punt 4 zegt op enkele maanden "
            "te rekenen voordat de nieuwe reeks te lezen is; Run A heeft die vraag vanmorgen op "
            "januari gezet. DIT IS DUS GEEN BESLUITPUNT EN DE VRAAG WORDT HIER NIET GESTELD — het "
            "is de meting die §6g zelf voorschrijft, met het teken erbij. NIETS VERZET."
        ),
        "POORT_5_VANGT_OPNIEUW_BIJNA_VIER_VIJFDE_WEG": (
            "575 selecties doorgerekend over alle zes de markten op 51 van de 65 duels (14 komen op "
            "NONE uit). De poortverdeling: 451 van de 575 (78%) sneuvelden op poort 5, de "
            "bevestiging door de tweede methode — de twee methodes sloegen de markt niet dezelfde "
            "kant op. Verder 46 op de edge-afkapping, 30 op poort 8 (underdog), 21 op de koersband, "
            "15 op poort 7 (context), 5 op poort 6 (robuustheid), 0 op poort 9 en 7 bleven volledig "
            "open. Die 78% is de derde dag op rij in dezelfde orde (27 nov 76%, 26 nov vergelijkbaar) "
            "en dat is het punt dat §5 bij de 'Net niet'-tabel maakt: valt er dagenlang alles af op "
            "één poort, dan is de vraag of de twee methodes systematisch uiteenlopen. Die vraag "
            "staat bij Run A sinds 27 november open met `owner = ik` en wordt hier niet gedupliceerd. "
            "POORT 7 KOSTTE VIER HELE DUELS: Bodø/Glimt – KFUM op de AH-kant (KFUM mist 19% van de "
            "selectiewaarde tegen 8%), Real Valladolid – Real Sociedad B (33% tegen 20%, drie "
            "schorsingen), FC Vaduz – FC Zürich (29% tegen 16%) en Servette – Lausanne (41% tegen "
            "27%, keeper Gertmonas out for season). Bij Bodø/Glimt kostte dat het duel NIET: de "
            "Under 4.5 heeft geen kant, dus poort 7 staat daar open en de wedstrijd levert alsnog "
            "een regel. Die reeks `context` staat op 159+ kandidaten en blijft de meest overtuigend "
            "negatieve van alle poorten."
        ),
        "VIJFTIEN_VAN_DE_ZEVENTIEN_COMPETITIES_SPELEN_EN_DAT_IS_OP_DRIE_WEGEN_NAGETROKKEN": (
            "65 duels in het venster [08:00 NL 28 nov, 08:00 NL 29 nov), verdeeld over vijftien "
            "competities: English League Two 12, English League One 11, MLS 6, Segunda División 5, "
            "Serie B 5, 2. Bundesliga 4, Czech First League 3, Greek Super League 3, Hungarian NB I "
            "3, Romanian SuperLiga 3, Swiss Super League 3, Croatian HNL 2, Eliteserien 2, Austrian "
            "Bundesliga 2 en Série A (BRA) 1. Dat is de ruimste runlijstdag van de maand. De twee "
            "stille competities — Allsvenskan (seizoen afgelopen) en Keuken Kampioen Divisie — zijn "
            "GEEN WEDSTRIJD en geen gat (§3 Stage 2). Langs drie wegen nagetrokken: (1) idcheck.py "
            "geeft 33 van 33 bruikbare standen met afsluitcode 0, dus geen enkele competitie is "
            "stil uit de runlijst verdwenen zoals het Serie B-id in september; (2) runwindow.py "
            "over twee daglijsten (28 en 29 november); (3) BetExplorer per competitie, dat 17 van 17 "
            "met Fotmob eens is en op hetzelfde totaal van 65 duels uitkomt — dat is de bevestiging "
            "door een tweede methode die §1 eist. Alle 65 duels zijn `playable = True`. Drie staan "
            "op een Amerikaanse klok en komen van de daglijst van 29 november: Los Angeles FC – "
            "St. Louis City om 02:30 NL, Portland Timbers – FC Dallas om 04:30 NL en Botafogo – "
            "Bahia om 01:00 NL. Onder de oude UTC-lezing van vóór 24 sep 2026 waren die drie bij de "
            "verkeerde run beland, en één ervan is vandaag een gepubliceerde regel."
        ),
        "DE_CAP_BINDT_EN_HEEFT_TIEN_DUELS_AFGEKAPT": (
            "65 duels op een zaterdagcap van 55 (`ranking.max_deep_analyses`), dus de afkapping van "
            "Stage 4 bindt en tien duels zijn niet doorgerekend. STILLE TRUNCATIE IS VERBODEN, dus "
            "ze staan bij naam in `afkapping.lijst`: VfL Osnabrück – Hannover 96, Osijek – Rijeka, "
            "Empoli – Hellas Verona, Iraklis – Panetolikos, Albacete – Tenerife, Eldense – Girona, "
            "Kifisia FC – Kalamata, Palermo – Benevento, NK Lokomotiva – Slaven en Luton Town – "
            "Oxford United. De laagste die het nog haalde is Austria Lustenau – Rapid Wien "
            "(datarijkdom 5,5 / 5 markten) en de hoogste die afviel VfL Osnabrück – Hannover 96 "
            "(5,5 / 5 markten) — EXACT DEZELFDE SCORE, dus de aftrap heeft de knip gelegd en niet "
            "de informatie. Dat is precies wat §3 Stage 4 van deze score zegt ('de sortering "
            "scheidt niet, gemeten 5 sep 2026') en het hoort erbij te staan in plaats van te worden "
            "gepresenteerd als een gemotiveerde keuze. Datarijkdom in de run liep van 4,5 tot 8,0. "
            "De context is voor alle 65 duels opgehaald, dus ook voor de tien afgekapte en de "
            "veertien op NONE — dat is wat §1c eist en het kost geen credits. Vier competities "
            "verliezen hierdoor duels maar houden GEANALYSEERD omdat er andere duels wél zijn "
            "doorgerekend; Croatian HNL en Greek Super League zijn de twee waar de afkapping het "
            "hardst aankomt (2 van 2 respectievelijk 2 van 3)."
        ),
        "VIER_COMPETITIES_HEBBEN_GEEN_XG_EN_DAT_ZIJN_ELF_VAN_DE_65_DUELS": (
            "Fotmob levert xG voor Greek Super League (135), Eliteserien (59), Segunda División "
            "(140), Serie B (86), 2. Bundesliga (146), Swiss Super League (69), Austrian Bundesliga "
            "(38), English League One (108), English League Two (109), MLS (130) en Série A (BRA) "
            "(268) — samen 54 duels — en GEEN xG voor Czech First League (122), Croatian HNL (252), "
            "Hungarian NB I (212) en Romanian SuperLiga (189), samen 11 duels. Die vier draaien op "
            "doelpunten als sterktemaat en komen dus op LIGHT uit met de lat van 16,0 pp "
            "(`prompts/run-b.md`). De vijfde competitie zonder xG, Keuken Kampioen Divisie (111), "
            "speelt vandaag niet. NEEM DEKKING NOOIT OVER VAN EEN ANDERE COMPETITIE IN HETZELFDE "
            "LAND: Duitsland heeft xG in de 2. Bundesliga en Nederland niet in de Keuken Kampioen "
            "Divisie, terwijl beide landen het in hun hoogste divisie wel hebben. Per competitie "
            "nagetrokken in Stage 3 en vastgelegd in coverage.json. Eindstand over de 51 "
            "doorgerekende duels: 30 FULL, 21 LIGHT; daarnaast 14 op NONE."
        ),
        "VEERTIEN_DUELS_OP_NONE_EN_ELK_OM_EEN_GEMETEN_REDEN": (
            "Veertien van de 65 duels komen op data_tier = NONE uit, en in alle veertien gevallen "
            "is dat een GEMETEN weigering en geen ontbrekende bron (§4). Twee soorten. (1) ZES "
            "DEGRADANTEN die niet in de stand van de divisie erboven staan: Ascoli, Vicenza en "
            "Benevento (Serie A 2025/2026), VfL Osnabrück (Bundesliga), York City en Rochdale "
            "(League One). (2) ZEVEN PROMOVENDI buiten het gemeten bereik van de omrekening "
            "(`conversion_in_range`, de Coventry-val): Kifisia FC – Kalamata, Eldense – Girona, "
            "Austria Lustenau – Rapid Wien, Peterborough United – Cambridge United, Leicester City "
            "– Mansfield Town, Exeter City – Crawley Town en Port Vale – Newport County. En (3) "
            "ÉÉN om de bekende bronreden: Vasas Budapest – Kispest Honvéd, want voor Hongarije is "
            "er geen factor — de NB II bestaat wél bij Fotmob (id 9117) maar dat id negeert de "
            "seizoensparameter, dus er is niets te meten (§4, 11 okt 2026). Dat is geen openstaand "
            "werk en hoeft niet opnieuw uitgezocht. Deze veertien hebben geen enkele kandidaat en "
            "staan met een STREEPJE in de scorekolom van de rangschikking en niet met een nul "
            "(§5, punt 3)."
        ),
        "DE_INKOOP_EN_DE_MARKTBALANS": (
            "Plafond `suggest_cap(18734, 3)` = 3119 credits; `split_budget(3119, 11)` geeft 11 "
            "spreads / 11 totals, dus de bulk kon voor alle inkoopbare competities. ELF van de "
            "vijftien spelende competities hebben een sportkey bij The Odds API en kregen alle elf "
            "de bulkaanroep h2h+spreads+totals: 33 credits. Daarna een tweede ronde BTTS per event "
            "voor de duels met een kandidaat-edge — 29 duels kwalificeerden, 27 kregen BTTS en 2 "
            "niet (Kisvárda – Nyíregyháza Spartacus FC en FC Voluntari – CFR Cluj, beide zonder "
            "sportkey): 27 credits. Totaal 60 van 3119, nog 18674 over. DE MARKTBALANS-CONTROLE VAN "
            "§1a IS RUIM GEHAALD OP DE INKOOP: elk van de elf competities kreeg zowel een "
            "uitkomstmarkt (1X2 op beste prijs, AH, DNB, DC) als een doelpuntenmarkt (O/U) — 11 van "
            "11 op beide, niet 1 van 12 zoals op 30 augustus. De vier competities zonder sportkey "
            "(Czech First League, Croatian HNL, Hungarian NB I, Romanian SuperLiga) hebben alleen "
            "het gratis BetExplorer-marktgemiddelde voor 1X2; daar is de bookmaker niet herleidbaar "
            "en valt de edge systematisch te laag uit — conservatief, maar niet vergelijkbaar met "
            "een duel waar de beste prijs bekend is. EN TOCH KOMEN ALLE VIJF DE REGELS UIT ÉÉN "
            "MARKT. Dat is deze keer dus NIET de inkoop (29 aug 2026) maar de analyse: alle zes de "
            "markten konden meedingen in elf van de vijftien competities, en Over/Under won "
            "`selection_score` vijf keer. §1a noemt dat expliciet een geldige uitkomst — bets "
            "forceren om een verdeling te halen is wat §1 verbiedt. Van de 575 doorgerekende "
            "selecties waren er 174 Over/Under, 154 Asian Handicap, 130 1X2, 54 BTTS, 44 Draw No "
            "Bet en 19 Double Chance."
        ),
        "TWEE_VAN_DE_VIJF_REGELS_LEUNEN_ZWAAR_OP_DE_SPLITSMETHODE": (
            "Bij Rosenborg – Molde staat de xG-methode op +10,86 pp en de splitsmethode op "
            "+31,65 pp; bij Bodø/Glimt – KFUM +6,51 tegen +22,50 pp. Poort 5 is in beide gevallen "
            "gehaald omdat beide boven de markt liggen — de poort toetst het TEKEN en niet de "
            "AFSTAND — maar met de weging van §1f (0,80 op xG) levert de splitsmethode bij "
            "Rosenborg 0,2 × 31,65 = 6,33 van de ruwe 15,02 pp (42%) en bij Bodø/Glimt 4,50 van de "
            "9,71 pp (46%). §6e noemt juist die methode de scheefste van de twee. Nagerekend op "
            "27 november over 266 beslist afgewikkelde picks met beide methodecijfers: de groep "
            "waarin de splits méér dan de helft van de ruwe edge levert staat op +15,0% over 38 "
            "gevallen (t = +0,98), de groep eronder op −10,3% over 228 (t = −1,58). Geen van beide "
            "haalt |t| = 2 en de twee regels van vandaag zitten net ónder die helftsgrens. De zorg "
            "is redelijk, de cijfers steunen haar niet, poort 5 blijft een tekenpoort. NIETS "
            "VERZET. Wat er wél bijhoort voor de lezer: de lambdas van Bodø/Glimt – KFUM staan op "
            "3,23 tegen 0,689 — een verwacht doelsaldo van tweeënhalf doelpunt — en de "
            "de-vigde markt zet de thuiszege daar op 87,3%. Dat is het soort duel waar §6f "
            "beschrijft dat het scoregrid de VORM van de uitslag niet goed heeft, en de Under 4.5 "
            "leunt op precies die staart."
        ),
        "DRIE_REGELS_HEBBEN_EEN_SMALLE_ROBUUSTHEIDSMARGE": (
            "Poort 6 eist dat de edge nergens op het (shrink, rho)-grid omdraait. De zwakste "
            "standen: Rosenborg – Molde +10,43 pp, Bodø/Glimt – KFUM +6,51 pp, Las Palmas – FC "
            "Andorra +3,66 pp, Los Angeles FC – St. Louis City +3,28 pp en AFC Wimbledon – Barnsley "
            "+5,07 pp. Alle vijf open, maar de twee van rond drie procentpunt zijn regels die bij "
            "een iets andere parameterkeuze flink dunner waren geworden. De reeks `robuustheid` in "
            "het schaduwlogboek staat op 90+ kandidaten rond −12,5%, dus de poort doet zijn werk. "
            "Dat hoort in het rapport te staan en niet alleen in de JSON."
        ),
        "BRONSTATUS_EN_WAT_ER_NIET_GEMELD_HOEFT": (
            "api_check.py: The Odds API OK met 46 actieve competities en 18734 credits over "
            "(1266 verbruikt deze maand); 33 van 34 sportkeys van de repo actief, alleen UEFA "
            "Conference League niet — dat is een Run A-competitie en raakt deze runlijst niet. "
            "API_FOOTBALL_KEY ontbreekt en dat is een BESLUIT van de gebruiker van 27 sep 2026, "
            "geen gat en geen actiepunt (§3): het staat hier als boekhouding, niet als vraag. De "
            "kanskant komt van Fotmob (alle competities) en Understat (vijf, en geen daarvan staat "
            "op deze runlijst). Fotmob leverde vandaag voor alle 65 duels een contextblok zonder "
            "één fout, dus de uitzondering van §3 punt 3 — melden zodra Fotmob niet meer levert — "
            "is niet aan de orde. idcheck.py: 33 van 33, afsluitcode 0. Vijf actieve sportkeys die "
            "de repo niet kent (Brazil Série B, Coupe de France, 3. Liga, Superettan, UEFA Nations "
            "League); geen daarvan staat op een runlijst, dus dat is informatie en geen gat."
        ),
        "STAGE_0_HAD_NIETS_TE_DOEN_EN_DAT_IS_GEEN_OVERSLAAN": (
            "`ledger.py open` en `shadow.py open` geven beide 'niets klaar om af te wikkelen': Run A "
            "heeft vanmorgen om 02:46 al afgewikkeld wat afgewikkeld kon worden, en de zes nog open "
            "picks zijn allemaal van vandaag of trappen pas vanavond af — de MLS-pick van 27 "
            "november (Real Salt Lake – Vancouver Whitecaps) stond bij het openen 0,1 uur na aftrap "
            "en is dus nog onderweg. `calibration.py settle` en `ctxlog.py settle` zijn tóch "
            "gedraaid, zoals §6b-5c en §6b-5d eisen van ELKE run, ook een run zonder iets open: nul "
            "waarnemingen afgewikkeld, 9321 van 9519 compleet en 198 open; contextlogboek 2629 "
            "afgewikkeld, 59 open. De controle van §6b-5c staat groen: "
            "`recalibrate.load_fit().fitted_through` is 2026-11-27, de vorige rundag. Er is dus "
            "vandaag geen afwikkelingsreflectie te schrijven over eigen picks (§3 Stage 0); de "
            "tabel in het dagrapport vult `report.py` zelf uit picks.jsonl."
        ),
    }

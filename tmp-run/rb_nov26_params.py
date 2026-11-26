"""De `parameters`-tekst van Run B, 26 nov 2026 — apart gehouden zodat
`rb_nov26_publiceer.py` alleen de rekenlogica van 1 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **NUL regels, en dat is de uitkomst van een ONDERGRENS en niet van de drempel.** De sterkste
  selectie met alle zeven overige poorten open staat op +0,83 pp, en `toplist._publiceerbaar`
  eist minstens de NEAR-drempel van 3,0 pp op `FULL`. Wat te zwak is om te loggen, is te zwak om
  te spelen (§5b).
* **Er is vandaag precies ÉÉN duel doorgerekend.** Twee van de zeventien competities spelen in het
  inzetvenster, en van die twee duels komt São Paulo – Remo op `NONE` uit omdat Remo een
  promovendus uit de Série B is en er voor dat Braziliaanse divisiepaar geen gemeten factor
  bestaat (`prompts/run-b.md`).
* **Er gaat GEEN enkele schaduwrij het logboek in.** Geen kandidaat haalt de NEAR-drempel, dus er
  is geen `near_miss` en de "Net niet"-tabel staat vandaag leeg — uitgeschreven, niet weggelaten
  (§5, 19 nov 2026).
* **Poort 5 is de bindende poort op de sterkste kandidaat van de dag**, met een marge van twee
  duizendsten: de xG-methode zet Doncaster +0,75 op 50,49% en de markt op 50,51%.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0390, b=0,0252 "
            "op 8775 afgerekende gevallen, fitted_through 2026-11-25. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit VERHOOGT een kans over vrijwel de hele speelbare band (+0,6 pp op 50%, "
            "+1,2 pp op 70%) en verlaagt alleen onder ongeveer 35%. Vandaag tilt hij de sterkste "
            "kandidaat van -0,28 pp ruw naar +0,45 pp herijkt (Under 3) en Doncaster +0,75 van "
            "+1,45 naar +2,15 pp — allebei ver onder de ondergrens van 3,0 waaronder §5b niet "
            "publiceert. Er is dus geen enkele regel die bij de gratie van §1g zou hebben bestaan, "
            "en ook geen regel die er door de herijking aan is gegaan: `herijking_omgekeerd` is "
            "vandaag leeg. LEES DE FIT NIET ALS 'het model is goed gekalibreerd en dus goed': hij "
            "is gefit op de ONGESELECTEERDE ijksteekproef (§1g, 20 sep 2026), en de scheefstand "
            "die telt zit in de GESELECTEERDE groep — die staat vandaag op z = +4,92 over 153 "
            "gespeelde Unders. Daarom staan poort 8 en poort 9 nog aan."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8, "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "NUL_REGELS_EN_DE_ONDERGRENS_VAN_5B_IS_DE_REDEN": (
            "Vandaag publiceert deze run NIETS, en het is belangrijk dat dat om de juiste reden "
            "gebeurt. Sinds 20 sep 2026 is EDGE_THRESHOLD_FULL geen poort meer maar een afkapping "
            "(§5b): staan er minder selecties boven de lat dan er regels in de lijst passen, dan "
            "bepaalt de RANGORDE de lijst en gaat de drempel mee als label. Op 45 van de 103 picks "
            "sinds 1 november staat daarom een edge onder de eigen lat, tot 3,41 pp bij FULL. Maar "
            "die rangorde heeft een ondergrens, en die bindt vandaag: `toplist._publiceerbaar` "
            "eist de NEAR-drempel — 3,0 pp op FULL, 6,0 op LIGHT — omdat de eerste herdraai onder "
            "§5b anders selecties met een NEGATIEVE edge publiceerde. Dat is aanvullen, en §5 "
            "verbiedt dat met zoveel woorden: 'zijn er minder gekwalificeerde bets dan "
            "MAX_SHORTLIST, lever er dan minder'. De enige selectie waarvan geen enkele GETOETSTE poort dichtstond is "
            "het GELIJKSPEL in Doncaster – Huddersfield (X @4,52 bij Pinnacle, "
            "+0,83 pp, kans 22,96%), en die staat 2,17 procentpunt onder die ondergrens. LET OP "
            "DAT HIJ OOK OP EEN TWEEDE GROND NIET PUBLICEERBAAR IS: poort 6 is voor hem nooit "
            "geevalueerd, want `robustness_check` draait in de analyse alleen bij "
            "`e_pp >= NEAR of e_raw >= thresh` en hij zit onder beide grenzen. "
            "`toplist._poorten_open` eist dat ELKE poort op True staat en leest een "
            "niet-geevalueerde poort dus als dicht — met opzet, want een run mag geen open "
            "poort claimen die nooit is getoetst (de les van 20 sep 2026, Athletic Club – "
            "Alavés). Van de vijftien doorgerekende selecties haalt er geen enkele 3,0 pp, en "
            "VEERTIEN sneuvelen al op poort 5. MAX_SHORTLIST is op "
            "donderdag 2 sinds de wijziging van 18 nov 2026 (ranking.max_shortlist, bindt sinds "
            "19 nov); de lijstlengte bindt dus NIET en er is geen enkele "
            "gekwalificeerd_niet_gepubliceerd-regel. De reeks `lijstlengte` blijft daarmee op 35 "
            "kandidaten staan, 32 afgewikkeld, 16 winnaars, +6,60u = +20,6%. De gebruiker kijkt er "
            "bij 100 gevallen opnieuw naar (§5b) en een run verzet MAX_SHORTLIST nooit op eigen "
            "initiatief."
        ),
        "POORT_5_BINDT_OP_DE_STERKSTE_KANDIDAAT_MET_TWEE_DUIZENDSTEN": (
            "De hoogste herijkte edge van de dag is Doncaster Rovers +0,75 @1,98 (Pinnacle) met "
            "+2,15 pp, en die sneuvelt op poort 5: de twee methodes moeten de markt DEZELFDE kant "
            "op verslaan, en de xG-methode zet deze selectie op 50,49% tegen een marktkans van "
            "50,51%. Twee honderdsten van een procentpunt de verkeerde kant op. De splitsmethode "
            "staat er met 57,80% ruim boven (+7,29 pp). Dat is geen willekeur maar het patroon van "
            "dit duel: op elke kant waar Doncaster de underdog is, zegt de splitsmethode veel meer "
            "dan de xG-methode (1X2 thuis +7,24 tegen -0,14 pp; +1 handicap +4,59 tegen -2,05 pp). "
            "De reden staat in de seizoensweging: Huddersfield staat dit seizoen op 2,073 xG per "
            "duel tegen 1,476 vorig seizoen, en dat tilt de xG-kant van Huddersfield op terwijl de "
            "doelpuntensplits van vorig seizoen dat niet doen. VEERTIEN van de vijftien selecties vallen "
            "vandaag op poort 5; de reeks `tweede_methode` staat over 334 afgewikkelde kandidaten "
            "op -2,3% en doet dus zijn werk, maar het is een smalle marge en geen comfortabele."
        ),
        "GEEN_ENKELE_SCHADUWRIJ_VANDAAG_EN_DAT_IS_NIET_HETZELFDE_ALS_STILTE": (
            "De NEAR-drempel is ook de grens waarboven een afgewezen kandidaat als `near_miss` in "
            "het schaduwlogboek komt (§6d). Geen enkele kandidaat van vandaag haalt 3,0 pp, dus er "
            "gaat NUL rijen naar data/shadow.jsonl en de 'Net niet'-tabel is leeg. Dat is een "
            "geldige uitkomst en geen vergeetachtigheid: §5 eist sinds 19 nov 2026 dat de sectie "
            "dan een UITGESCHREVEN lege stand krijgt in plaats van te verdwijnen, en hetzelfde "
            "geldt voor de rangschikking op geschiktheid. Beide secties staan vandaag met tekst op "
            "de pagina. Het verschil tussen 'geen enkele kandidaat' en 'drie die net afvielen' is "
            "precies wat die secties moeten laten zien."
        ),
        "EEN_DUEL_OP_NONE_OM_EEN_GEMETEN_REDEN_EN_POORT_7_ZOU_HET_OOK_HEBBEN_GEBLOKKEERD": (
            "São Paulo – Remo (Série A BRA, 00:00 NL) komt op data_tier = NONE. Remo staat niet in "
            "de Série A-stand van 2025 en is dus een promovendus uit de Série B; `promotion.TIER2` "
            "kent voor Brazilië geen divisie en `MEASURED_TIER2_GAP` geen factor, dus er is niets "
            "om hem mee om te rekenen. `prompts/run-b.md` zegt dat expliciet, dus dit is de gemeten "
            "stand van zaken en geen omissie van deze run. Twee dingen die er wél bij horen. (1) "
            "Poort 7 zou dit duel aan de THUISKANT hebben geblokkeerd: São Paulo mist 43,0% van zijn "
            "selectiewaarde met zeven uitvallers (Wendell geschorst, Rafael Tolói, Sabino, Marcos "
            "Antônio, Domingos Duarte, Nicolas en Aurélio Buta geblesseerd, twee van hen voor de "
            "rest van het seizoen) tegen 24,6% bij Remo, en de ploeg heeft drie dagen rust tegen "
            "ruim vier. Dat verandert niets aan de uitkomst — NONE is NONE — maar het hoort "
            "vastgelegd, want de steekproef van ctxlog.py is de enige weg naar een meting over "
            "blessures (§1c). (2) De prijzen voor deze competitie zijn WEL ingekocht (bulk, 3 "
            "credits) voordat de tier bekend was; dat is de volgorde van §1a en geen verspilling om "
            "recht te zetten, maar het betekent dat de marktbalans-tabel voor Série A (BRA) prijzen "
            "noemt waar geen enkele selectie is doorgerekend."
        ),
        "DE_CAP_BINDT_NIET_EN_VIJFTIEN_COMPETITIES_SPELEN_NIET": (
            "Twee duels op een donderdagcap van 40 (ranking.max_deep_analyses), dus er is NIETS "
            "afgekapt en de dekkingstabel krijgt geen AFGEKAPT-regel. De vijftien overige "
            "competities hebben niets in het inzetvenster [08:00 NL 26 nov, 08:00 NL 27 nov); dat "
            "is GEEN WEDSTRIJD en geen gat (§3 Stage 2). Het is langs drie onafhankelijke wegen "
            "nagetrokken: idcheck.py geeft 33 van 33 id's groen met afsluitcode 0 (dus geen "
            "competitie is stil uit de runlijst verdwenen), runwindow.py werkt op twee daglijsten, "
            "en de BetExplorer-fixturepagina's zijn per competitie nagelopen — 17 van 17 eens, "
            "beide bronnen op 2 duels. LET OP WAT ER MORGEN STAAT: op de daglijst van 27 november "
            "staan negentien runlijstduels (Keuken Kampioen Divisie 7, 2. Bundesliga 2, Romanian "
            "SuperLiga 2, en één elk bij Czech First League, Croatian HNL, Hungarian NB I, Segunda "
            "División, Austrian Bundesliga en Série A BRA). Die trappen alle negentien ná 08:00 NL "
            "op 27 november af en horen dus bij de run van morgen, niet bij deze. Dat is exact het "
            "onderscheid waarvoor runwindow.py bestaat; de vrijdagcap is 55 en MAX_SHORTLIST 3."
        ),
        "PINNACLE_IS_HET_OPMERKELIJK_EENS_MET_HET_MODEL": (
            "Stage 5 stap 2 (§3): de gemiddelde absolute afstand tussen de eigen xG-kansen en "
            "Pinnacle's de-vigde 1X2 is 1,38 procentpunt op het ene toetsbare duel, bij een "
            "Pinnacle-marge van 4,48%. Het model houdt Huddersfield 1,7 pp minder sterk dan "
            "Pinnacle en het gelijkspel 2,1 pp waarschijnlijker. Op de doelpuntenkant staat het "
            "model +2,91 pp boven Pinnacle op de Under-kant van lijn 3,0 (eigen 53,8% tegen 50,9%) "
            "— dezelfde richting als de scheefstand van §6g, en precies de reden dat een Under hier "
            "niet gepubliceerd wordt zonder marge. Deze getallen gaan NIET in my_prob of "
            "prob_sources (§2): ze zijn marktafgeleid en horen in de vergelijking."
        ),
        "DE_BESTE_PRIJS_STAAT_7_4_PROCENT_BOVEN_HET_MARKTGEMIDDELDE": (
            "De beste 1X2-prijs per uitkomst ligt 7,4% boven het BetExplorer-marktgemiddelde over "
            "vijf boeken (4,70 / 4,52 / 1,74 tegen 4,32 / 4,02 / 1,68). Twee van de drie beste "
            "prijzen staan bij Betfair en zijn dus BEURSkoersen: na 2% commissie wordt 4,70 een "
            "4,626 en 1,74 een 1,7252, en met die netto-koersen is gerekend (§5, oddsapi.net_price). "
            "Zonder die commissie zou de thuiszege op +1,30 pp hebben gestaan in plaats van "
            "+0,95 pp — nog altijd ver onder de ondergrens, maar het verschil is groter dan de "
            "edge zelf."
        ),
        "STAGE_0_HAD_NIETS_AF_TE_WIKKELEN_EN_TWEE_PICKS_STAAN_TERECHT_OPEN": (
            "ledger.py open en shadow.py open geven beide 'niets klaar om af te wikkelen'. Run A "
            "van vanochtend (±03:00 NL) heeft de vier picks van 25 november al afgerekend: twee van "
            "Run A (PSG – Roma Under 3.5 verloren, Atlético Madrid – Viking Under 4 gewonnen) en "
            "twee van Run B (Atlético-MG – Corinthians Draw No Bet void, Pisa – Modena Under 2.5 "
            "gewonnen). De twee openstaande picks zijn de Europa League-regels van Run A van "
            "vandaag; die trappen vanavond pas af en staan dus terecht op pending. Er is geen pick "
            "van vóór vandaag die nog open staat."
        ),
        "STAGE_MIN_2_DE_TAKKEN_ZIJN_NAGELOPEN_EN_ER_VIEL_NIETS_TE_MERGEN": (
            "101 remote branches nagelopen, en de UITKOMST IS PAS GELDIG NA `--unshallow`. De "
            "container kreeg de repo opnieuw als ondiepe kloon (58 commits lokaal), en in die "
            "stand gaf `git merge-base HEAD <tak>` voor 88 van de 101 takken NIETS terug — wat "
            "eruitzag als 88 takken met een eigen rootcommit en samen duizenden eigen commits. "
            "Dat is het valse alarm dat §3 Stage -2 beschrijft, hier in zijn scherpste vorm: het "
            "lijkt niet op achterlopende takken maar op een tweede repo. Na `git fetch "
            "--unshallow origin` staat de geschiedenis op 801 commits, delen ALLE 101 takken "
            "geschiedenis met main en hebben ALLE 101 nul eigen commits. Er viel dus niets te "
            "mergen. De inhoudelijke controle van branchaudit.py (per record, niet op de graaf) "
            "meldt 16 records die niet op main staan en alle zestien zijn nagegaan: vier "
            "schaduwrijen van 3 oktober in de KALE vorm, exact de vier die op 7 nov 2026 met "
            "opzet zijn verwijderd omdat ze dubbel stonden (§3 Stage -2: 'vul ze bij een merge "
            "dus niet aan'), en twaalf leafpaden van source-health.json die in main onder "
            "`last_run_run_b.history[].blok` en `last_run_run_c.detail_history[]` staan — de "
            "ingedikte vorm die het health-script zelf gebruikt. Nagekeken op drie van de twaalf: "
            "het blok van 19 nov bevat sources_deze_run met alle vier de fotmob-sleutels, dat van "
            "8 nov bevat `samenvatting` (met de aantekening dat het op 18 nov uit tak "
            "bold-curie-i16v98 is verenigd), en detail_history van 14 nov bevat betexplorer_saff "
            "en betexplorer_kings_cup. picks.jsonl (603), context-log.jsonl (2603), "
            "calibration.jsonl (9256) en coverage.json (339) staan VOLLEDIG op main. Deze run "
            "staat op main en pusht naar main (§6a)."
        ),
    }

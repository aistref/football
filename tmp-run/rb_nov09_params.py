"""De `parameters`-tekst van Run B, 9 nov 2026 — apart gehouden zodat `rb_nov09_publiceer.py`
alleen de rekenlogica van 8 november hoeft te zijn.

Vier dingen die vandaag vooraan horen:

* **NUL BETS, en de kalender bepaalt de dag en niet een poort.** Het interlandvenster is begonnen:
  DRIE van de zeventien competities spelen, met samen DRIE duels in het inzetvenster op een
  maandagcap van 40.
* **Poort 5 (de bevestiging door een tweede methode) vangt 21 van de 25 selecties weg** — zesde dag
  op rij de poort die de dag bepaalt.
* **De tweede bron is het over alle zeventien competities eens, maar de controle meldt 16 van 17**,
  en dat verschil zit in de controle en niet in de data: BetExplorer HEEFT Sabadell – Real Sociedad B
  met 1X2-prijzen, maar met een LEEG tijdlabel, en `in_window("")` is False.
* **De vroeg-seizoenscorrectie staat vandaag op ÉÉN waarneming** (alleen Segunda División), want de
  twee andere competities zijn door `uplift_observations` overgeslagen.
"""


def parameters(res, max_shortlist_waarde):
    return {
        "HERIJKING": (
            "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1,0319, b=0,0206 op "
            "7734 afgerekende gevallen, fitted_through 2026-11-08. DAT IS DE VORIGE RUNDAG, dus "
            "calibration.py settle is niet blijven liggen (§6b-5c eist die controle aan dit ene "
            "getal). De fit staat vrijwel op de identiteit en VERHOOGT een kans licht over de hele "
            "speelbare band: +0,2 pp op 40%, +0,5 pp op 50%, +0,8 pp op 60%, +1,0 pp op 70%. Het "
            "ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. LEES DAT NIET ALS 'het model is "
            "goed gekalibreerd en dus goed': het is gekalibreerd op de ONGESELECTEERDE "
            "ijksteekproef (§1g, 20 sep 2026), en de scheefstand die telt zit in de GESELECTEERDE "
            "groep — zie `ledger.py stats`, waar het model over 488 afgewikkelde bets 291,3 "
            "winnaars verwachtte en er 225 werden."
        ),
        "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
        "MAX_SHORTLIST": max_shortlist_waarde,
        "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
        "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
        "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
        "LEVEL_SCALE": 1.032,
        "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
        "NUL_BETS_EN_HET_IS_DE_KALENDER_EN_NIET_EEN_POORT": (
            "LEES DIT EERST. Het interlandvenster is begonnen en DRIE van de zeventien competities "
            "van de runlijst spelen: Eliteserien (1 duel), Romanian SuperLiga (1) en Segunda "
            "Division (1). Veertien staan op GEEN WEDSTRIJD en dat is geen gat (§3 Stage 2). ALLE "
            "DRIE DE DUELS ZIJN VOLLEDIG DOORGEREKEND - geen enkele op data_tier = NONE, geen "
            "enkele afgekapt - en er komt nul uit. DE DRIE REDENEN, want ze zijn verschillend. (1) "
            "Kristiansund - Valerenga (FULL): negen selecties over vier markten, de hoogste edge "
            "is +2,83 pp op Under 3,5 @1,8722 en dat is onder de lat van 8,0; acht van de negen "
            "sneuvelen bovendien al op poort 5. (2) Botosani - Otelul Galati (LIGHT): drie "
            "selecties, alleen 1X2, en de thuiszege @2,09 staat op +7,43 pp HERIJKT - maar de twee "
            "methodes wijzen tegengesteld (xG +10,30 pp, splits -7,36 pp), dus poort 5 houdt hem "
            "tegen. Hij zou de LIGHT-lat van 16,0 ook niet hebben gehaald. (3) Sabadell - Real "
            "Sociedad B (LIGHT): dertien selecties over drie markten, de hoogste is +3,97 pp op "
            "Real Sociedad B +0,75, en de drie beste staan alle drie op de underdog-kant die poort "
            "8 dichtzet (de markt geeft Real Sociedad B 19,4% tegen 54,3%, onder de ondergrens van "
            "35%). NUL BETS IS EEN GELDIGE UITKOMST en er is niets geforceerd om de lijst van drie "
            "plekken te vullen (§1)."
        ),
        "POORT_5_VANGT_VOOR_DE_ZESDE_DAG_OP_RIJ_HET_MEESTE_WEG": (
            "Van de 25 doorgerekende selecties sneuvelen er 21 op POORT 5, de bevestiging door een "
            "tweede methode (§1, voorwaarde 5) - 84,0% van alles, en het hoogste aandeel van deze "
            "reeks (73,3% gisteren, 77,5% eergisteren). De rest: 3 op poort 8 (underdog) en 1 op "
            "`edge`. ZES DAGEN OP RIJ IS DE RICHTING DIE §6d VRAAGT, maar de aantallen van vandaag "
            "zijn te klein om er iets aan toe te voegen: 25 selecties over drie duels. `shadow.py "
            "stats` meet de reeks `tweede_methode` op -1,0% over 287 afgewikkelde kandidaten - "
            "vlak, dus de afgewezen groep verliest niet maar wint ook niet. ER WORDT NIETS VERZET: "
            "draait die reeks positief bij deze aantallen, dan is dat een vraag voor de gebruiker "
            "en niet voor een run."
        ),
        "DE_TWEEDE_BRON_IS_HET_OVER_ALLE_ZEVENTIEN_EENS_MAAR_DE_CONTROLE_MELDT_16_VAN_17": (
            "DIT IS DE ENIGE BEVINDING VAN VANDAAG EN HET GAT ZIT IN DE CONTROLE, NIET IN DE DATA. "
            "`rb_nov09_bevestiging.py` meldt 'eens: 16 van 17' met Segunda Division als afwijking: "
            "fotmob=1, betexplorer=0. NAGETROKKEN EN HET IS GEEN GEMISTE WEDSTRIJD. BetExplorer "
            "HEEFT Sabadell - Real Sociedad B - het is de eerste rij van zijn fixturepagina, met "
            "1X2-prijzen over 17 boeken (1,71 / 3,54 / 4,78) - maar het veld `when` is LEEG, en "
            "`in_window(\"\")` geeft False, dus de rij valt buiten het venster en wordt niet "
            "geteld. DEZELFDE STILLE FAALSTAND ALS DE `\\s+`-REGEX VAN 14 OKTOBER EN HET "
            "HARDGECODEERDE VENSTER VAN 5 NOVEMBER: een controle die het verkeerde meet en daarom "
            "niet klaagt - alleen valt hij deze keer de VOORZICHTIGE kant op (hij meldt een "
            "afwijking die er niet is) in plaats van groen te blijven over een gat. De wedstrijd "
            "is ook nog op een derde manier bevestigd: `fotmob.fetch_match_details(5868534)` geeft "
            "LaLiga2, ronde 13, 9 november 20:30 NL, started=False. ER IS NIETS GEREPAREERD aan "
            "`in_window` - dat is een wijziging in een controle op de dag dat die controle juist "
            "iets meldt, en de regel hoort eerst voorgelegd (zie `todo` in het dagrapport)."
        ),
        "DE_VROEG_SEIZOENSCORRECTIE_STAAT_OP_EEN_ENKELE_WAARNEMING": (
            "`early_season_uplift` komt vandaag op factor 1,0255 uit, en die staat op EEN "
            "waarneming: alleen Segunda Division (13 speeldagen) draagt de pool. "
            "`uplift_observations` heeft de twee andere met opzet overgeslagen - Eliteserien omdat "
            "het lopende seizoen op 26 van 30 speeldagen staat en het niveau daar rechtstreeks uit "
            "het lopende seizoen komt (route `lopend`), en Romanian SuperLiga omdat er in geen van "
            "beide seizoenen xG is. HET WEGLATEN ZELF IS DE METING (§3 Stage 5) en dus staat het "
            "hier, maar lees de 1,0255 met dezelfde terughoudendheid als elke reeks van n=1: de "
            "gepoolde waarneming is 1,0412 en de factor is daar met krimp naartoe getrokken. Ze "
            "raakt vandaag precies EEN duel - Sabadell - Real Sociedad B, de enige competitie op "
            "de route `vorig+uplift` - en daar is de uitkomst nul bets. De twee andere "
            "competities nemen de route `lopend` en worden door deze factor niet geraakt."
        ),
        "DRIE_DUELS_DRIE_TIERS_EN_EEN_PROMOVENDUS_DIE_WEL_OMREKENBAAR_BLEEK": (
            "Kristiansund - Valerenga staat op FULL (Fotmob heeft xG in de Eliteserien). Botosani - "
            "Otelul Galati staat op LIGHT omdat Fotmob voor de Romanian SuperLiga (189) GEEN xG "
            "levert; die competitie draait op doelpunten als sterktemaat en komt dus altijd op "
            "LIGHT uit met een lat van 16,0 pp (`prompts/run-b.md`). Sabadell - Real Sociedad B "
            "staat op LIGHT om een ANDERE reden: Sabadell staat niet in de LaLiga2-stand van "
            "2025/2026 en is omgerekend uit de Primera Federacion (Fotmob 8968, Group 2) met de "
            "factor die Run B op 5 oktober 2026 zelf heeft gemeten (n=28), en "
            "`conversion_in_range` liet hem door - aanval 1,238 binnen 1,019-1,905, verdediging "
            "0,631 binnen 0,498-0,925. DAT IS DE POORT WAAR DRIE DUELS GISTEREN OP NONE KWAMEN EN "
            "DEZE NIET, en het is het verschil tussen 'niet gemeten' en 'gemeten en binnen bereik' "
            "(§4). NEEM DEKKING NOOIT OVER VAN EEN ANDERE COMPETITIE IN HETZELFDE LAND: Spanje "
            "heeft xG in LaLiga2 en Roemenie niet in zijn hoogste divisie."
        ),
        "DE_MARKTBALANS_SLAAGT_OP_TWEE_VAN_DE_DRIE_EN_DE_DERDE_HEEFT_GEEN_SPORTKEY": (
            "§1a eist dat zichtbaar is of een eenzijdige lijst uit de portemonnee komt of uit de "
            "data. Vandaag is er geen lijst, dus de vraag is wat er te koop WAS. TWEE van de drie "
            "spelende competities hebben een sportkey bij The Odds API - Eliteserien en Segunda "
            "Division - en beide kregen de volledige bulk-aanroep met h2h + spreads + totals, dus "
            "beide hadden zowel een uitkomstmarkt als een doelpuntenmarkt. Romanian SuperLiga heeft "
            "GEEN sportkey en draait op het gratis BetExplorer-marktgemiddelde over 17 boeken; daar "
            "is de bookmaker niet herleidbaar en valt de edge systematisch te laag uit (§1a) - "
            "conservatief, dus geen risico op te veel bets. Voor dat duel staan AH, DNB, DC, OU en "
            "BTTS alle vijf als 'niet opgevraagd - geen sportkey' in `markets_checked`, met de "
            "reden erbij en niet als gat (§6b-5b). VAN DE 25 SELECTIES waren er 8 Over/Under, 8 "
            "1X2, 8 Asian Handicap en 1 Draw No Bet. BTTS is NIET gekocht: §1a stap 2 koopt die "
            "alleen voor duels met een kandidaat-edge, en het enige duel dat er een had (Botosani) "
            "heeft geen sportkey. DC viel bij beide inkoopbare duels weg omdat er geen +0,5-lijn in "
            "de spreads-respons zat. CREDITS: 6 van een plafond van 441, en er staan nog 19.438 "
            "van de 20.000 van deze maand."
        ),
        "DE_CAP_BINDT_NIET_EN_ER_IS_NIETS_AFGEKAPT": (
            "3 duels op een MAANDAGcap van 40 (`ranking.max_deep_analyses`), dus er is NIETS "
            "afgekapt en de dekkingstabel krijgt geen AFGEKAPT-regel. De datarijkdom liep van 6,0 "
            "tot 8,0; omdat er niet is afgekapt zijn 'laagste die het haalde' en 'hoogste die "
            "afviel' per definitie leeg. Alle drie de duels staan op `playable = True` en komen "
            "van de daglijst van de rundag zelf - er is vandaag geen enkel duel van de daglijst van "
            "morgen. De context is voor alle drie opgehaald (§1c) en `ctxlog.py collect` heeft ze "
            "alle drie gelogd; het logboek staat nu op 2281 wedstrijden."
        ),
        "POORT_9_HEEFT_VANDAAG_NIETS_TE_DOEN_EN_DE_REEKS_IS_WEL_LEESBAAR_GEWORDEN": (
            "Poort 9 (§1h) heeft vandaag NUL selecties geblokkeerd, en dat is geen omissie: er is "
            "maar EEN FULL-duel en de enige Under-selectie daar staat op +2,83 pp, ver onder de "
            "gewone lat van 8,0 - de poort bindt met opzet alleen in de band tussen 8,0 en 10,0 pp "
            "op FULL. WAT WEL NIEUW IS: de reeks `doelpunten_onder` staat nu op 41 AFGEWIKKELDE "
            "KANDIDATEN met -31,5% rendement (15 winnaars, 36,6% trefkans), en haalt daarmee de ~30 "
            "die §6d eist. Duidelijk negatief, dus de poort houdt verliezers tegen en doet zijn "
            "werk; er is geen aanleiding hem te verlagen en geen vraag om voor te leggen (§1h punt "
            "3). De oorzaakkant staat er ook nog: `margins.py goalbias` geeft over 136 gespeelde "
            "Unders +0,658 doelpunt per duel MEER dan de eigen lambda zei, z = +4,62 - de hardste "
            "stand van deze reeks (+0,612 bij z = +4,20 gisteren). Op de Over-kant gebeurt dat "
            "niet: 73 duels, -0,341, z = -1,58. En over ALLE 2236 doorgerekende duels staat het "
            "model vlak: +0,031 per duel, z = +0,85. DIE TWEE MOGEN NOOIT ALS EEN GETAL WORDEN "
            "GELEZEN - de bovenste meet het model, de onderste de selectie."
        ),
        "DE_NIVEAUCORRECTIE_IS_ZES_DAGEN_OUD_EN_HET_SIGNAAL_ERONDER_ZAKT_VERDER": (
            "LEVEL_SCALE = 1.032 bindt sinds 3 november (§6g, besluit van de gebruiker van 2 "
            "november) en is vandaag met `today=DAY` aan `analyze_match` en `robustness_check` "
            "meegegeven, bij elke aanroep. `gridfit.py measure` zegt opnieuw zelf dat de reeks nog "
            "niet te lezen is: 260 van de 1433 homogene duels dragen de correctie al in zich, dus "
            "de regel `scale = 1.032` toetst op die duels een DUBBELE correctie. De diagnose die "
            "eronder ligt staat vandaag op +0,058 doelpunt per duel (z = +1,23) over 1433 duels, "
            "tegen +0,062 (z = +1,28) over 1347 gisteren, +0,089 (z = +1,78) over 1257 op 7 "
            "november en +0,100 (z = +1,93) over 1147 op 2 november. HET SIGNAAL ZAKT DUS VERDER, "
            "en dat is precies wat je zou verwachten als de correctie doet wat ze moet doen - maar "
            "het is op deze gemengde reeks GEEN bewijs daarvan. ER IS NIETS TE BESLISSEN en de "
            "vraag hoort niet gesteld (§1h, §6g); reken op enkele maanden voordat de reeks van na "
            "3 november alleen groot genoeg is (§6d)."
        ),
        "PINNACLE_IS_HET_VANDAAG_VRIJWEL_MET_HET_MODEL_EENS": (
            "Stap 2 van Stage 5 (§3) is ingevuld met de de-vigde Pinnacle-prijs naast de eigen "
            "kans. TWEE van de drie duels hebben zowel een Pinnacle-1X2 als een eigen 1X2 - "
            "Botosani niet, want die competitie zit niet in de respons. De gemiddelde absolute "
            "afstand tot het Pinnacle-oordeel is 2,08 pp over die twee, bij een gemiddelde "
            "Pinnacle-marge van 3,74%. DAT IS KLEIN, en het is de spiegel van gisteren: toen stond "
            "de Under-kant over de hele populatie +3,77 pp boven Pinnacle met 21 van de 27 paren "
            "erboven, en vandaag staat de Under-kant op -1,95 pp over twee (duel, lijn)-paren met "
            "1 van de 2 erboven. TWEE PAREN IS GEEN POPULATIE en daar hoort geen gevolgtrekking "
            "bij; het staat hier omdat §6g eist dat deze toets elke run wordt gemeld, ook als er "
            "niets uit komt. Geschreven voorspellingen van derden waren opnieuw niet te halen "
            "(§3 Stage 5, gemeten 20 sep 2026)."
        ),
        "STAGE_0_VOND_NIETS_OPEN_EN_RUN_A_HAD_DE_AFWIKKELING_AL_GEDAAN": (
            "`ledger.py open` en `shadow.py open` geven beide 'geen enkele regel klaar om af te "
            "wikkelen', en dat is de normale gang van zaken en niet een gat: Run A heeft vannacht "
            "om 02:45 de hele afwikkeling van 8 november gedaan. NUL van de 550 picks en NUL van de "
            "1848 schaduwrijen staan nog open. VAN DE VIJF PICKS VAN RUN B VAN GISTEREN GINGEN ER "
            "TWEE GOED: Tromso - Bodo/Glimt (Under 3,5, 0-2) en Virtus Entella - Modena (Under 2,5, "
            "0-2) wonnen; Viking - KFUM (Under 3,75, 5-1), Sandefjord - Molde (Under 3,5, 5-5) en "
            "Carrarese - Sampdoria (1X2 thuis, 0-1) verloren. De reflectie op die uitslagen (§3 "
            "Stage 0, 12 okt 2026) staat in het runrapport onder Afwikkeling en in gewone taal in "
            "`settled_note` van het dagrapport - met de kanttekening dat deze run ze niet zelf "
            "heeft afgewikkeld en dus geen nieuwe uitslagen heeft gelezen."
        ),
        "DE_BRANCHCONTROLE_IS_EERST_HET_VALSE_ALARM_VAN_DE_ONDIEPE_KLOON_INGELOPEN": (
            "ZIE `runs/2026-11-09-run-b.md` onder Branchcontrole voor de volledige meting, EN LEES "
            "DIT ALS HET VOORBEELD WAAR §3 STAGE -2 LETTERLIJK VOOR WAARSCHUWT. De eerste telling "
            "van deze run gaf 79 van de 86 remote takken met 'eigen' commits, tot 647 stuks per "
            "tak, en `main` op 57 commits met een wortel van 31 oktober 2026 - een beeld dat "
            "precies lijkt op een geschiedenis die herschreven is. HET WAS DE ONDIEPE KLOON: "
            "`git rev-parse --is-shallow-repository` gaf `true`, en bij een ondiepe kloon telt "
            "`rev-list --count HEAD..<tak>` elke commit van voor de knip als 'nog niet hier'. NA "
            "`git fetch --unshallow origin` staat main op 721 commits met een wortel van 8 augustus "
            "2026 en hebben NUL van de 86 takken eigen commits. Dat is exact de tabel van 20 "
            "augustus 2026 in §3 Stage -2, nu met 79 in plaats van 7. DOE DIE STAP DUS ECHT EERST; "
            "hij is deze run te laat gedaan en dat heeft een onware tussenconclusie opgeleverd. "
            "DE INHOUD IS OOK VERGELEKEN EN NIET ALLEEN DE GRAAF (§3 Stage -2, 27 sep 2026), met "
            "`scripts/branchaudit.py` over alle 85 takken per record: `picks.jsonl` (550), "
            "`context-log.jsonl` (2278), `calibration.jsonl` (7958), `source-health.json` en "
            "`coverage.json` staan alle vijf op VOLLEDIG. `shadow.jsonl` meldt 4 ONTBREKENDE "
            "rijen - Canada-Peru, Croatia-England, Estonia-Luxembourg en Switzerland-Slovenia van "
            "3 oktober, in de KALE vorm - en DIE HOREN NIET TERUG. Het zijn de vier dubbeltellingen "
            "die Run D op 7 november heeft gevonden en die met opzet zijn verwijderd; §3 Stage -2 "
            "noemt ze met naam en verbiedt ze bij een merge aan te vullen. ER IS DUS NIETS TE "
            "MERGEN. De run staat op `main`."
        ),
    }

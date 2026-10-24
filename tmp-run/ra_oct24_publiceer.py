"""Run A 24 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct23_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWAALF van de eenentwintig competities uit de runlijst speelden, met 51 duels in het
inzetvenster: een volle zaterdag en de grootste Run A-lijst in weken (de Championship alleen al
elf duels, de Bundesliga zes).

GEEN ENKEL duel is kruis-grens en PRECIES ÉÉN komt op NONE uit (Gaziantep FK – Erzurumspor FK,
buiten conversion_in_range), dus 50 van de 51 zijn doorgerekend. 33 staan op FULL; de 17 andere
hebben een omgerekende ploeg (promovendus of degradant) en staan daarom op LIGHT met de lat van
16,0 pp.

VOOR HET EERST IN WEKEN BINDT DE LIJSTLENGTE en niet het aantal kandidaten: er zijn VEERTIEN
duels met een publiceerbare selectie en er passen VIJF regels in (MAX_SHORTLIST = 5, zaterdag).
Drie van de vijf halen hun eigen lat, twee LIGHT-regels staan eronder en zijn op rangorde
gepubliceerd (§5b). Eén gekwalificeerde selectie valt af op lijstlengte — Chelsea – Tottenham
BTTS 'nee', rang 6 — en die krijgt een `gekwalificeerd_niet_gepubliceerd`-blok plus een
`near_miss` met failed_gate = 'lijstlengte', zoals §5b sinds 26 september voorschrijft. Zie
VIJF_REGELS_WAARVAN_DRIE_HUN_LAT_HALEN_EN_TWEE_OP_RANGORDE en
EEN_GEKWALIFICEERDE_SELECTIE_VALT_AF_OP_LIJSTLENGTE_EN_DAT_IS_OPMERKELIJK.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-24"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-24T04:13:51+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")


def state_uit(res, run):
    st = {"date": DAG, "run": run, "competitions": {}}
    for m in res["matches"]:
        st["competitions"].setdefault(m["competition"],
                                      {"status": "GEANALYSEERD", "matches": []})["matches"].append(m)
    return st


def bronnen_van(m, cand):
    """De onafhankelijke kansinputs van dit duel, met de bron per cijfer (§2)."""
    uit = []
    lam = (m.get("lambdas") or {}).get("xg") or []
    sw = m.get("seizoensweging") or {}
    if m.get("promovendi"):
        uit.append(
            "Fotmob team-xG, met de omgerekende ploeg via scripts/promotion.py (§4 Promovendi: "
            "relatieve sterkte uit de divisie eronder, omgerekend met een gemeten divisiefactor "
            "en getoetst aan conversion_in_range) en daarna geblend met het lopende seizoen "
            f"(§4, k=8)" + (f"; doelverwachting {lam[0]:.3f} thuis / {lam[1]:.3f} uit"
                            if len(lam) == 2 else ""))
    else:
        uit.append(
            "Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, "
            f"k=8)" + (f"; doelverwachting {lam[0]:.3f} thuis / {lam[1]:.3f} uit"
                       if len(lam) == 2 else ""))
    sp = (m.get("lambdas") or {}).get("split") or []
    uit.append("Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d "
               "multiplicatief en op het competitiegemiddelde genormaliseerd)"
               + (f"; doelverwachting {sp[0]:.3f} / {sp[1]:.3f}" if len(sp) == 2 else ""))
    if m.get("understat"):
        u = m["understat"]
        uit.append(f"Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): "
                   f"doelverwachting {u['lambdas'][0]:.3f} / {u['lambdas'][1]:.3f}, "
                   f"rollende xG over 8 duels {u['rolling_xg_8']}")
    uit.append("Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met "
               "marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole")
    if sw:
        uit.append("seizoensweging per ploeg: " + json.dumps(sw, ensure_ascii=False))
    return uit


def bouw(run, pad):
    res = json.load(open(pad))
    st = state_uit(res, run)
    top = toplist.build(st)
    idx = {m["match"]: m for m in res["matches"]}
    picks = []
    for r in top["herijkt"]:
        m = idx[r["match"]]
        home, away = r["match"].split(" – ", 1)
        cand = next((c for c in m["all_candidates"]
                     if c["market"] == r["market"] and c["selection"] == r["selection"]), {})
        onder = (r["market"] == "Over/Under" and r["selection"].startswith("Under"))
        picks.append({
            "id": f"{DAG}-{slug(m['competition'])}-{slug(home)}-{slug(away)}-{slug(r['market'])}-{slug(r['selection'])}",
            "run": run, "run_date": DAG, "kickoff": m["kickoff_utc"],
            "competition": m["competition"], "home": home, "away": away,
            "market": r["market"], "selection": r["selection"], "odds": r["odds"],
            "odds_source": r["odds_source"], "odds_captured_at": CAPTURED,
            "implied_prob": round(1 / r["odds"], 4), "my_prob": r["prob"],
            "edge_pp": r["edge_pp"], "data_tier": r["tier"],
            "confidence": "Medium" if r["tier"] == "FULL" else "Low",
            "prob_sources": bronnen_van(m, cand), "shortlisted": True, "result": "pending",
            "notes": (f"Gepubliceerd op rangorde (§5b): plek {top['herijkt'].index(r)+1} van "
                      f"{len(top['herijkt'])} over {len(res['matches'])} doorgerekende wedstrijden. "
                      f"{r['status']}. selection_score {r['score']}. "
                      f"Ruwe kans {cand.get('my_raw')}, ruwe edge {cand.get('edge_raw')} pp; "
                      f"xG-methode {cand.get('edge_xg')} pp, splitsmethode {cand.get('edge_split')} pp, "
                      f"zwakste stand van het (shrink, rho)-grid {cand.get('edge_robust_min')} pp. "
                      f"shrink staat sinds 19 sep op 1.00 (§6e). "
                      + ("OMGEREKENDE PLOEG: een ploeg in dit duel komt uit de divisie eronder of "
                         "erboven en is via scripts/promotion.py omgerekend (§4), dus data_tier is "
                         "LIGHT en de lat 16,0 pp — nooit FULL, want de omrekening haalt de "
                         "systematische fout eruit en niet de onzekerheid. "
                         if m.get("promovendi") else "")
                      + ("ONDER-KANT: §6g meet dat P(Under) bij élk duel ruim twee procentpunt "
                         "te hoog staat door een vormfout in score_grid (gemeten vandaag over "
                         "1515 doorgerekende duels: P(Under 3.0) voorspeld 64,0% tegen werkelijk "
                         "61,8%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de "
                         "gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,590 "
                         "doelpunt per duel over 90 gevallen (z = +3,39), terwijl de Over-kant op "
                         "-0,243 staat (z = -0,97 over 53 gevallen). "
                         "Poort 9 (§1h) BINDT hier wél, want dit duel staat op FULL, en deze "
                         "selectie haalt de verzwaarde lat van 10,0 pp ruim. Dat is de rem die er "
                         "is; de oorzaak — keuze (a) van 11 oktober, de vormfout zelf repareren — "
                         "staat nog open. Trek dus ongeveer twee procentpunt van de genoemde kans "
                         "af voordat je haar leest. "
                         if onder else "")
                      + ("" if cand.get("bet_beide") else
                         "bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide "
                         "schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel "
                         "(§5b). ")),
        })
    return st, top, picks, res


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("A", "tmp-run/ra_oct24_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0.985865, "
                "b=-0.009152 over 5487 afgerekende gevallen, fitted_through 2026-10-23, oftewel "
                "de vorige rundag zoals §6b-5c eist. calibration.py settle is deze run vóór de "
                "tweede analysepas gedraaid (87 waarnemingen afgewikkeld, 5694 van 5721 "
                "compleet, 27 nog open), dus er is geen regel gepubliceerd op een verouderde "
                "correctie. DE FIT IS OPNIEUW VRIJWEL DE IDENTITEIT: a wijkt 1,4% van 1 af en b "
                "0,9 procentpunt van nul, en over de speelbare koersband haalt hij tussen 0,1 en "
                "0,5 procentpunt van een kans af (30% -> 30,1%, 50% -> 49,8%, 70% -> 69,6%). Bij "
                "alle vier de gepubliceerde regels vallen de herijkte en de ruwe edge daardoor "
                "binnen vier tienden van een procentpunt samen (Lazio +14,13 tegen +14,53; Como "
                "+11,58 tegen +12,01). Dat is geen defect maar precies wat §1e punt 3 beschrijft: "
                "op de ongeselecteerde ijksteekproef is het ruwe model al goed gekalibreerd — het "
                "zei gemiddeld 33,333% en het gebeurde 33,333%. GEVOLG DAT HOORT MEE TE WEGEN: de "
                "bescherming waarop het vervallen van poort 8 in september werd verantwoord is er "
                "ook vandaag niet, en dat is de gemeten reden dat poort 8 sinds 1 oktober weer "
                "bindt. `bet_beide` staat op TRUE bij alle vier de regels: ze halen hun lat op "
                "BEIDE schalen, en poort8_ruw is dus leeg."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWAALF van de eenentwintig competities uit de runlijst speelden, samen 51 duels "
                "in het inzetvenster — de grootste Run A-lijst in weken en bijna vier keer die "
                "van gisteren (13). Het is een volle zaterdag: Championship 11 duels, Bundesliga "
                "6, Premier League / Serie A / La Liga / Scottish Premiership / Belgian Pro "
                "League / Ekstraklasa elk 4, Eredivisie / Primeira Liga / Super Lig elk 3 en "
                "Ligue 1 één. De NEGEN competities zonder wedstrijd zijn de Danish Superliga, de "
                "drie Europese toernooien (UCL hervat 3 november, UEL en UECL 5 november) en de "
                "vijf bekers. Dat is geen storing (§3 Stage 2) maar de kalender. Alle zestien "
                "competities met een fotmob_id zijn door een tweede bron bevestigd — zie "
                "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven — dat kostte Run A op 6 oktober vijf duels. "
                "Alle vijf zijn daarom langs BetExplorer gegaan (tmp-run/ra_oct24_cups.py) en "
                "alle vijf leveren teamparen op de fixturepagina (FA Cup 40, League Cup 8, Coppa "
                "Italia 8, KNVB Beker 26, DFB Pokal 16), dus geen van de drie faalmodi van die "
                "bron is opgetreden. NUL ervan valt in het inzetvenster: League Cup 27.10. 20:45, "
                "KNVB Beker 27.10. 18:45, DFB Pokal 27.10. 18:00, FA Cup 06.11. 20:45 en Coppa "
                "Italia 01.12. 21:00. De Fotmob-daglijst van 24 oktober noemt geen van deze vijf. "
                "Twee bronnen, hetzelfde antwoord."),
            "GEEN_KRUIS_GRENSDUEL_EN_EEN_ENKELE_NONE": (
                "Alle 51 duels zijn binnenlands, dus scripts/interleague.py komt deze run niet "
                "aan de orde (§4, Kruis-grens). 33 duels staan op FULL, 17 op LIGHT met een "
                "omgerekende ploeg, en PRECIES ÉÉN komt op NONE uit: Gaziantep FK – Erzurumspor "
                "FK, waar Erzurumspor FK buiten het gemeten bereik van de Turkse omrekening valt "
                "(conversion_in_range). Dat is de Coventry-val zoals §4 hem beschrijft en de "
                "juiste uitkomst: buiten het waargenomen bereik is er geen meting, en dan is "
                "doorrekenen raden. 50 van de 51 duels zijn dus werkelijk doorgerekend."),
            "TWINTIG_OMGEREKENDE_PLOEGEN_IN_ZEVENTIEN_DUELS": (
                "Zeventien duels hebben een ploeg die vorig seizoen niet in deze divisie speelde "
                "(drie duels hebben er twee), en negentien van de twintig zijn omgerekend in "
                "plaats van op NONE gezet (§4, 'Promovendi: eerst omrekenen, dan pas NONE'). "
                "OMHOOG, via TIER2: Coventry City (E0/E1), Racing Santander en Deportivo A "
                "Coruña (SP1/SP2), Schalke 04, Paderborn en Elversberg (D1/D2), Cardiff City en "
                "Lincoln City (E1/E2), St. Johnstone (SC0/SC1), Willem II en Cambuur (eigen "
                "meting NED), Lommel en SK Beveren (eigen meting BEL), Amed Sportif (eigen "
                "meting TUR) en Wisła Kraków (eigen meting POL). OMLAAG, via TIER1: Burnley, "
                "West Ham United en Wolverhampton Wanderers (E0/E1 down) en ADO Den Haag (NED). "
                "EEN ervan strandt: Erzurumspor FK valt buiten conversion_in_range. Acht van de "
                "tien gebruikte paren staan op football-data.co.uk en de rest op een eigen "
                "meting; lees `GapResult.direction` per selectie voor de stand, want een "
                "samenvattende zin daarover is in dit bestand al een keer achterhaald geraakt "
                "(§4, 9 okt 2026). De omgerekende sterkte is daarna geblend met het lopende "
                "seizoen (§4, k=8); de SPLITS blijven ongeblend. EN HET VERKLAART WAAROM ER GEEN "
                "LIGHT-REGEL OP DE LIJST STAAT: op LIGHT ligt de lat op 16,0 pp en de hoogste "
                "LIGHT-edge van de dag is +13,38 pp."),
            "VIJF_REGELS_WAARVAN_DRIE_HUN_LAT_HALEN_EN_TWEE_OP_RANGORDE": (
                "MAX_SHORTLIST = 5 (zaterdag) en de lijst is VOL — voor het eerst in weken "
                "bindt de lijstlengte in plaats van het aantal kandidaten. Er zijn VEERTIEN "
                "duels met een publiceerbare selectie (alle acht andere poorten open en edge "
                "boven de NEAR-ondergrens) en er passen vijf regels in. De lijst, op "
                "selection_score: 1. Lazio – Parma Under 2.5 @2.04 (+14,13 pp, FULL, score "
                "8,92), 2. Como – Sassuolo Under 3.5 @1.8232 na commissie (+11,58 pp, FULL, "
                "7,69), 3. Alverca – Arouca Over 2.5 @1.9212 na commissie (+8,74 pp, FULL, "
                "5,31), 4. Racing Santander – Espanyol Over 2.5 @1.73 (+12,84 pp, LIGHT, 4,54) "
                "en 5. Lincoln City – Burnley Over 2.5 @1.9212 na commissie (+12,82 pp, LIGHT, "
                "4,16). DRIE halen hun eigen lat van 8,0 pp op FULL; de TWEE LIGHT-regels staan "
                "onder hun lat van 16,0 en zijn op rangorde gepubliceerd (§5b). "
                "MAX_LIGHT_IN_SHORTLIST = 2 raakt zijn bovengrens exact maar sluit niets uit: er "
                "is geen derde LIGHT-kandidaat binnen de eerste vijf plekken."),
            "EEN_GEKWALIFICEERDE_SELECTIE_VALT_AF_OP_LIJSTLENGTE_EN_DAT_IS_OPMERKELIJK": (
                "Chelsea – Tottenham Hotspur, BTTS 'nee' @2.6856 na commissie (+8,38 pp op "
                "FULL, score 3,82), staat op RANG 6 en valt daarmee buiten de lijst. Dat is een "
                "`gekwalificeerd_niet_gepubliceerd`-blok plus een `near_miss` met failed_gate = "
                "'lijstlengte' (§5b, 26 sep 2026) — geen afgewezen kandidaat, want er is geen "
                "enkele poort die haar heeft tegengehouden, en ook geen bet. De reeks "
                "`lijstlengte` groeit daarmee vandaag van 17 naar 18; ze staat op +10,1% over 17 "
                "afgewikkelde gevallen, en dat is de enige schaduwreeks die positief staat met "
                "aantallen eronder. Tel haar nooit bij `edge` op (§5b). "
                "EN HIER ZIT EEN UITKOMST DIE EERLIJK BENOEMD HOORT, want ze leest op het eerste "
                "gezicht als een fout: een selectie die haar eigen lat WEL haalt valt af, "
                "terwijl twee selecties die hun lat NIET halen worden gepubliceerd. Dat is geen "
                "fout maar precies wat §5b voorschrijft, en het volgt uit twee regels samen. "
                "(1) De drempel is sinds 20 september geen poort meer maar een afkapping, en hij "
                "bindt alleen wanneer er MEER selecties boven hun lat staan dan er regels in de "
                "lijst passen. Er staan er VIER boven hun lat (Lazio, Como, Alverca, Chelsea) en "
                "er passen er vijf, dus de drempel bindt niet en de RANGORDE bepaalt de lijst. "
                "(2) Die rangorde is `selection_score` = edge x kans x (FULL 1,0 | LIGHT 0,5), en "
                "daarin verslaat +12,84 pp op LIGHT (x0,5) een +8,38 pp op FULL. §5b zegt het "
                "zelf: de lijst is 'een rangschikking van wat het model het sterkst vindt' en "
                "niet 'een selectie van winnaars'. Dit is de eerste Run A-dag waarop die twee "
                "regels elkaar zichtbaar kruisen, en het is daarmee een waarneming over de "
                "weegregel en niet over deze wedstrijd. Deze run verandert er NIETS aan — "
                "`selection_score` is per §1a een besluit van de gebruiker over "
                "risicobereidheid en geen keuze van de run — en legt het als één punt voor in "
                "het dagrapport."),
            "ALLE_VIER_DE_REGELS_STAAN_VER_VAN_PINNACLE_EN_DRIE_OP_DE_SCHEVE_KANT": (
                "DIT IS DE BELANGRIJKSTE WAARSCHUWING VAN DEZE RUN en ze hoort bij de bets in "
                "plaats van in een voetnoot. Alle vier de gepubliceerde regels liggen op de "
                "doelpuntenas ver van het scherpste publieke boek, en bij drie van de vier staat "
                "het eigen model aan de LAGE kant — precies de kant waarvan §6g de scheefstand "
                "heeft gemeten. Eigen P(Under) tegen Pinnacle's de-vigde P(Under), op Pinnacle's "
                "eigen lijn: Lazio – Parma 63,6% tegen 49,6% (+14,0 pp), Como – Sassuolo 61,0% "
                "tegen 48,4% (+12,6 pp) en Chelsea – Tottenham 58,9% tegen 47,6% (+11,3 pp). "
                "Alverca – Arouca staat juist 10,3 pp ONDER Pinnacle op de Under en dus even ver "
                "boven hem op de Over. Dat zijn de vier grootste afwijkingen van de 45 gemeten "
                "(duel, lijn)-paren, terwijl het dagcijfer op +0,52 pp staat met 26 van 45 boven "
                "Pinnacle. Op de 1X2-as is het dagcijfer 3,64 pp gemiddelde absolute afstand bij "
                "een Pinnacle-marge van 3,74%. Dat is exact het patroon waarvoor §1g waarschuwt: "
                "de grootste geclaimde edge is doorgaans de grootste MODELfout en niet de "
                "grootste marktfout. HARDE GRENS §2/§4: dit getal zit niet in my_prob en niet in "
                "prob_sources; het staat in de vergelijking."),
            "POORT_9_BINDT_EN_DUWT_DE_SELECTIE_IN_EEN_ONGEDEKTE_MARKT": (
                "Dertiende bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke "
                "selectie aangeroepen met today=2026-10-24. De poort bindt vandaag ECHT: er zijn "
                "60 FULL-Unders doorgerekend en VIER vallen in de band 8–10 pp waar de "
                "verzwaarde lat van 10,0 pp snijdt — Chelsea – Tottenham Under 3.5 (+9,02), "
                "Under 3 (+8,44) en Under 2.5 (+8,25), en Como – Sassuolo Under 3 (+9,70). Twee "
                "duels krijgen daarmee een `doelpunten_onder`-rij in het schaduwlogboek, dat "
                "vandaag van 10 naar 12 afgewikkelde-plus-open gevallen gaat (de reeks staat op "
                "10 afgewikkeld, 50,0% trefkans, −11,0%). De 48 LIGHT-Unders blijven per besluit "
                "van 12 oktober buiten de poort; hun hoogste edge is +7,13 pp, dus de poort zou "
                "daar vandaag hoe dan ook niets hebben geraakt. "
                "EN NU DE BEVINDING DIE ERBIJ HOORT, want ze is nieuw en ze is niet te zien zonder "
                "ernaar te kijken: BIJ CHELSEA – TOTTENHAM HEEFT DE POORT DE SELECTIE NIET "
                "TEGENGEHOUDEN MAAR VERPLAATST. De drie Unders van dat duel zijn alle drie "
                "geblokkeerd, en wat er daarna werd gepubliceerd is BTTS 'nee' @2.6856 — dezelfde "
                "mening over hetzelfde duel (weinig doelpunten), uitgedrukt in de enige "
                "doelpuntenmarkt waar §1h punt 2 de poort MET OPZET niet laat gelden. Dat is geen "
                "fout en geen omzeiling: §1h houdt BTTS erbuiten omdat er geen meting voor is, en "
                "de 0-of-1-bet-regel kiest per duel de sterkste selectie die alle poorten haalt. "
                "Maar het betekent wel dat een rem op één markt-en-kant de scheefstand van §6g "
                "niet wegneemt zodra er een naburige markt is die hij niet raakt. De "
                "BTTS-reeks staat op 21 afgewikkelde gevallen in beide richtingen samen (13 "
                "gewonnen, +31,7% — de best renderende markt van het logboek) en op 10 in de "
                "'nee'-richting; §1h punt 2 noemt ~30 als de grens waarop die vraag opnieuw hoort "
                "te worden bekeken, en die is niet gehaald. Deze run verandert dus NIETS aan de "
                "poort en legt ook geen besluit voor — §1h legt vast dat een run dat nooit op "
                "eigen initiatief doet, en §1h ('gevraagd en beantwoord op 12 oktober') dat de "
                "vraag niet elke dag opnieuw wordt gesteld. Ze schrijft de waarneming op zodat ze "
                "er staat als de reeks de grens wél haalt."),
            "POORT_8_HOUDT_ELF_DUELS_TEGEN_EN_KOST_TWEE_KEER_DE_BESTE": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), aangeroepen "
                "met today=2026-10-24 zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van geraden. 33 "
                "selecties over ELF duels sneuvelen op deze poort — de breedste dag sinds hij "
                "terugkwam, wat bij 51 duels te verwachten is. BIJ TWEE DUELS KOST HIJ DE HOOGST "
                "SCORENDE SELECTIE VAN DE HELE DAG: Eyüpspor – Kasımpaşa (Eyüpspor +1.5 @1.48, "
                "+12,73 pp, score 10,22 — hoger dan elke gepubliceerde regel; de markt geeft "
                "Eyüpspor 17,4% tegen 58,2%) en Lazio – Parma (Parma +1.5 @1.74, +13,40 pp, "
                "score 9,50 — de markt geeft Parma 12,0% tegen 67,9%). Bij Lazio – Parma kwam de "
                "Under er alsnog door en is er dus wél een regel; bij Eyüpspor – Kasımpaşa bleef "
                "er niets over en is 'edge onder drempel' de reden van het duel. poort8_ruw is "
                "LEEG: geen enkele kandidaat sneuvelde alleen op de ruwe schaal, wat logisch is "
                "bij een fit die vrijwel de identiteit is. De twee reeksen blijven twee "
                "populaties die nooit worden opgeteld — `underdog` staat op 183 afgewikkelde "
                "gevallen (49,2% trefkans, −2,4%) en `underdog_ruw` op 17 (41,2%, −8,8%). Hun "
                "stand staat in het runrapport onder 'Stand van het logboek' en wordt daar NIET "
                "als besluit voorgelegd (§1e, 5 oktober: stel de vraag niet elke dag opnieuw)."),
            "POORT_7_HOUDT_52_SELECTIES_TEGEN_OVER_ZESTIEN_DUELS": (
                "context.check sloot bij 52 van de 705 doorgerekende selecties de poort, "
                "verdeeld over ZESTIEN duels — en bij TIEN van die zestien was de tegengehouden "
                "selectie de hoogst scorende van dat duel, zodat de poort de hele regel kost. De "
                "zwaarste gevallen: Lens – Paris FC (DNB Lens @ +12,51 pp, score 8,59 — Lens had "
                "3 dagen rust tegen 6 bij Paris FC), Preston North End – West Bromwich Albion "
                "(Double Chance Preston of gelijk, +10,08 pp, score 6,69 — Preston mist 41% van "
                "de selectiewaarde tegen 25%), Sheffield United – Derby County (Derby +0.75, "
                "+7,38 pp — Derby mist 54% tegen 4%) en Aston Villa – Manchester City (Aston "
                "Villa +1.5, +6,85 pp — Villa mist 33% tegen 20%). Tien duels komen op 'context "
                "spreekt de bet tegen' uit als reden van de hele wedstrijd. GEEN van de vier "
                "gepubliceerde regels is door deze poort geraakt, en dat is geen toeval: alle "
                "vier zijn een totaal of een BTTS, dus side = None, en dan staat poort 7 per §1c "
                "altijd open — er is geen kant om te benadelen. Dat de doelpuntenmarkten de lijst "
                "vullen op een dag dat poort 7 zo breed bindt, is dus deels een gevolg van de "
                "poortconstructie en niet alleen van de analyse; het hoort genoemd."),
            "GEEN_VERPLAATSTE_WEDSTRIJD_EN_GEEN_ENKELE_STADIONNAAM": (
                "context.check_venue is voor alle 51 duels gedraaid en zet nergens relocated = "
                "True. Daar hoort hetzelfde voorbehoud bij als op 23 oktober, en het is eerlijker "
                "dan 'alles in orde': de Fotmob-respons gaf voor GEEN ENKEL van de 51 duels een "
                "stadionnaam (venue.name is overal None), dus de controle heeft niets kunnen "
                "vergelijken en 'niet verplaatst' betekent hier 'geen verplaatsing gemeten' en "
                "niet 'gemeten dat er geen verplaatsing is'. Dat is dezelfde soort stille leegte "
                "als §1c beschrijft. Het is ook het verwachte beeld voor binnenlandse "
                "competitieduels; op 22 oktober, een Europese avond, sloeg dezelfde controle bij "
                "vijf van de 36 duels wél aan."),
            "OPSTELLINGEN": (
                "lineup_type over de 51 duels: 25 op 'predicted', 22 op 'lastStarting11' en VIER "
                "op 'unavailable'. Bevestigde elftallen ('confirmed') zijn er bij geen enkel duel; "
                "voor aftrappen tussen 12:15 en 21:30 NL is dat om 04:15 NL te verwachten. Bij de "
                "vier zonder opstellingsblok kan poort 7 niets meten en staat hij dus OPEN, "
                "precies zoals §1c voorschrijft (ontbrekende data laat de poort open, want een "
                "meting die er niet is, is geen bewijs van een probleem). Geen van die vier "
                "levert een regel op. Dit zit in de datarijkdom (§3 Stage 4) en niet in my_prob."),
            "DE_CAP_BINDT_NIET_MAAR_HET_SCHEELT_VIER_DUELS": (
                "51 duels op een zaterdagcap van 55 (ranking.max_deep_analyses, vr-zo), dus er "
                "is NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel. Het is wel de "
                "krapste marge sinds de cap op 40/55 is gezet: vier duels meer en hij had "
                "gebonden. De datarijkdom liep van 4,50 (de vier Belgische duels) tot 8,00 "
                "(Valencia – Villarreal); omdat er niets afviel is er geen 'laagste die het "
                "haalde' en geen 'hoogste die afviel' te noemen (§3 Stage 4). De context is voor "
                "alle 51 duels opgehaald zoals §1c eist, en alle 51 hebben een contextblok zonder "
                "fout — nul ctx-fouten op 51 verzoeken."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [24.10. 08:00 NL, 25.10. 08:00 NL). "
                "Alle 51 duels stonden op de daglijst van 24 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 51 zijn playable: de "
                "vroegste aftrap is 12:15 NL (Piast Gliwice – Cracovia) en de laatste 21:30 NL "
                "(Gil Vicente – FC Porto). Er is dus geen enkel duel dat al was afgetrapt voordat "
                "de gebruiker kon inzetten, en geen carry-over-band. LET OP DE TIJDWISSEL: de "
                "wintertijd gaat in in de nacht van zaterdag 24 op zondag 25 oktober, dus deze "
                "run rekent nog met UTC+2 en dat is de LAATSTE rundag waarop dat klopt. "
                "`runwindow.kickoff_nl` gebruikt zoneinfo en heeft daar geen last van; de rest "
                "van de repo gebruikt nog een hardgecodeerde +02:00, en dat wordt vanaf morgen "
                "een uur fout. Dat staat als actiepunt in het dagrapport."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert "
                "de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van de zestien "
                "competities met een fotmob_id zijn het eens, inclusief de vier die vandaag GEEN "
                "WEDSTRIJD hebben: 51 duels bij Fotmob, 51 bij BetExplorer, nul afwijkingen en "
                "geen enkele bron die faalde (tmp-run/ra_oct24_bevestiging.py). Per competitie "
                "bevestigd op het aantal, inclusief de elf Championship-duels en de zes van de "
                "Bundesliga. De vijf bekers hebben geen fotmob_id en gaan langs hun eigen tweede "
                "bron — zie DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN."),
            "ELF_VAN_DE_TWAALF_SPELENDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Elf van de twaalf competities met een duel vandaag hebben een sportkey bij The "
                "Odds API. DE SCOTTISH PREMIERSHIP HEEFT ER GEEN, en die speelt vandaag vier "
                "duels: daar is BetExplorer de enige 1X2-bron, is de bookmaker niet herleidbaar, "
                "zijn er geen spreads en geen totals, en valt de edge systematisch te laag uit "
                "(§1a). Conservatief, dus geen risico op te veel bets, maar niet vergelijkbaar "
                "met de andere 47 duels — en het is de verklaring waarom alle vier die duels op "
                "'edge onder drempel' of 'context' uitkomen met maar drie selecties per duel. "
                "BESTE PRIJS TEGEN MARKTGEMIDDELDE over de 46 duels waar beide bekend zijn: "
                "gemiddeld +5,66% (van +3,38% tot +8,49%), wat in edge ruwweg anderhalf "
                "procentpunt per selectie scheelt — gratis, en de enige verbetering in dit hele "
                "bestand waarvan de omvang vooraf vaststaat. BEURZEN: DRIE van de vier "
                "gepubliceerde regels staan op Matchbook en zijn dus met oddsapi.net_price "
                "doorgerekend (Como 1.84 bruto / 1.8232 netto, Alverca 1.94 / 1.9212, Chelsea "
                "2.72 / 2.6856); alleen Lazio – Parma komt van een gewone bookmaker (Unibet SE "
                "@2.04). Noteer die twee getallen naast elkaar in het dagrapport, want de "
                "gebruiker ziet op de site de bruto koers."),
            "MARKTBALANS": (
                "Plafond suggest_cap(18945, 8) = 1182 credits. split_budget(1182, 11) geeft 11 "
                "spreads / 11 totals, en omdat 3 x 11 = 33 ruim onder 1182 blijft is de volle "
                "BULK-aanroep gedaan voor ALLE ELF inkoopbare competities: h2h + spreads + "
                "totals, dus vijf van de zes markten in één keer. Daarna BTTS voor 28 van de 30 "
                "duels met een kandidaat-edge (§1a stap 2, de vereniging van beide schalen); de "
                "twee die afvielen zijn Dundee United – Aberdeen en Falkirk – Kilmarnock, en die "
                "vielen af omdat de Scottish Premiership geen sportkey heeft — dat staat zo in "
                "markets_checked en niet als gat. De 21 duels zonder kandidaat-edge staan er als "
                "'niet opgevraagd — geen kandidaat-edge in dit duel'. Totaal 61 van 1182 credits "
                "(33 bulk + 28 BTTS), 18.884 over. De marktbalans-controle slaagt ZO RUIM ALS HET "
                "KAN: alle elf gekochte competities hebben zowel een uitkomstmarkt (1X2, AH, DNB, "
                "DC) als een doelpuntenmarkt (O/U) — 11 van 11, waar de controle er één eist. "
                "Doorgerekend over de 50 duels: 216 Over/Under, 202 Asian Handicap, 147 1X2, 56 "
                "BTTS, 55 Draw No Bet en 29 Double Chance, samen 705 selecties — meer dan drie "
                "en een half keer het aantal van gisteren. DE GEPUBLICEERDE LIJST IS GEEN "
                "INKOOPEFFECT: alle zes markten deden overal mee. Dat alle vier de regels uit de "
                "doelpuntenmarkt komen is wél opvallend en het heeft twee verklaringen "
                "die beide in dit bestand staan: poort 7 en poort 8 raken uitsluitend selecties "
                "MET een kant (33 + 52 tegengehouden selecties), en bij side = None staan ze per "
                "§1c altijd open."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Gevonden voor 45 van de 51 duels, zowel op 1X2 als op de "
                "totalen, met een gemiddelde Pinnacle-marge van 3,74% tegen 6 à 10% bij de rest. "
                "De zes zonder Pinnacle-1X2 zijn de vier Schotse duels (geen sportkey) en twee "
                "Turkse (Eyüpspor – Kasımpaşa en Gaziantep FK – Erzurumspor FK, waar Pinnacle de "
                "markt niet noteerde). Gemiddelde absolute afstand tussen het eigen model en het "
                "Pinnacle-1X2: 3,64 procentpunt — het laagste cijfer in weken, wat te verwachten "
                "is op een dag zonder enkele omrekening tussen landen. De grootste 1X2-"
                "afwijkingen: Wisła Kraków – Raków +14,67 pp op de thuiszege, Gil Vicente – FC "
                "Porto −14,41 pp op de uitzege en Lazio – Parma −11,17 pp op de thuiszege. Op de "
                "doelpuntenkant staat het model gemiddeld 0,52 pp BOVEN Pinnacle met 26 van 45 "
                "erboven. Zie "
                "ALLE_VIER_DE_REGELS_STAAN_VER_VAN_PINNACLE_EN_DRIE_OP_DE_SCHEVE_KANT. HARDE "
                "GRENS §2/§4: dit getal zit NIET in my_prob en NIET in prob_sources."),
            "UNDERSTAT_DEKT_DERTIEN_VAN_DE_VIJFTIG": (
                "Alle VIJF Understat-competities spelen vandaag (PL, Serie A, La Liga, "
                "Bundesliga, Ligue 1), samen 13 duels met een stand in beide bronnen. Daar is "
                "dus een tweede, ONAFHANKELIJK xG-model naast Fotmob (§4), inclusief rollende xG "
                "over acht duels. DAT RAAKT DRIE VAN DE VIER GEPUBLICEERDE REGELS: Chelsea – "
                "Tottenham, Como – Sassuolo en Lazio – Parma hebben een kansinput uit twee "
                "verschillende xG-modellen in plaats van twee doorsnedes van één. Alverca – "
                "Arouca (Primeira Liga) heeft dat niet en leunt volledig op Fotmob, in twee "
                "doorsnedes (team-xG en de thuis/uit-splits). Dat is genoeg voor §2 — de twee "
                "methodes zijn twee methodes, geen twee bronnen — maar het is minder redundantie, "
                "en het hoort genoemd in plaats van stilzwijgend overgeslagen. LET OP bij het "
                "naast elkaar leggen: Understat ligt structureel ~0,13 xG per ploeg per duel "
                "hoger dan Fotmob, dus normaliseer altijd op het eigen competitiegemiddelde van "
                "de bron (§4)."),
            "VROEG_SEIZOEN_EN_NIVEAU": (
                "early_season_uplift geeft factor 1.1084, gepoold 1.1163 over 110 speeldagen in "
                "TWAALF competities — de breedste pool die deze routine tot nu toe heeft gehad. "
                "GEEN ENKELE competitie is uit de pool gelaten (`overgeslagen` is leeg), want "
                "geen van de twaalf staat op of boven SEASON_MATURE_SHARE: het lopende seizoen "
                "loopt van 7 speeldagen (Bundesliga) tot 12 (Championship en Ekstraklasa), en de "
                "langste competitie heeft 46 speeldagen. Alle twaalf lopen daarom op de route "
                "`vorig+uplift` en er is deze run geen enkele `lopend`-route — anders dan "
                "gisteren, toen de Danish Superliga op zijn lopende seizoen draaide. Een uplift "
                "van 10,8% is hoog maar in oktober verwacht: de teamsterktes komen uit vorig "
                "seizoen en begin seizoen wordt er meer gescoord — de correctie dooft vanzelf "
                "uit. De niveaus per competitie staan in `niveau`, met de route en de reden erbij."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn vier publiceerbare selecties en vijf
        # plekken beschikbaar. Deze lus blijft staan omdat ze de enige plek is waar een
        # gekwalificeerde selectie die niet in de lijst past wordt vastgelegd
        # (`failed_gate = "lijstlengte"`, bewust dezelfde naam — §5b, 26 sep 2026).
        alles_op_score = sorted(
            [{"match": m["match"], "score": (m.get("pick") or {}).get("score") or 0.0}
             for m in res["matches"] if m.get("bet")], key=lambda r: -r["score"])
        gepubliceerd_scores = [r["score"] for r in top["herijkt"] if r.get("score") is not None]
        drempel_score = min(gepubliceerd_scores) if gepubliceerd_scores else None
        buiten = 0
        gepubliceerde_duels = {mm for mm, _, _ in gespeeld}
        for m in res["matches"]:
            if not m.get("bet"):
                continue
            pick = m.get("pick") or {}
            if (m["match"], pick.get("market"), pick.get("selection")) in gespeeld:
                continue
            if m["match"] in gepubliceerde_duels:
                m["binnen_wedstrijd_niet_gekozen"] = {
                    "selection": pick.get("selection"), "market": pick.get("market"),
                    "odds": pick.get("odds"), "edge_pp": pick.get("edge_pp"),
                    "score": pick.get("score"),
                    "reden": ("alle negen poorten open en boven de drempel, maar een andere "
                              "selectie van DEZELFDE wedstrijd scoorde hoger op "
                              "selection_score (§1a); gepubliceerd is die andere"),
                }
                continue
            rang = next((i for i, r in enumerate(alles_op_score, 1) if r["match"] == m["match"]), None)
            m["near_miss"] = {
                "match": m["match"],
                "market": f"{pick.get('market')} — {pick.get('selection')}",
                "odds": pick.get("odds"), "my_prob": pick.get("my_prob"),
                "my_raw": pick.get("my_raw"), "edge_pp": pick.get("edge_pp"),
                "edge_xg": pick.get("edge_xg"), "edge_split": pick.get("edge_split"),
                "edge_robust_min": pick.get("edge_robust_min"),
                "failed_gate": "lijstlengte"}
            m["gekwalificeerd_niet_gepubliceerd"] = {
                "selection": pick.get("selection"), "market": pick.get("market"),
                "odds": pick.get("odds"), "edge_pp": pick.get("edge_pp"),
                "score": pick.get("score"), "rang": rang,
                "reden": (f"alle negen poorten open en {pick.get('edge_pp'):+.2f} pp boven de "
                          f"drempel, maar rang {rang} en niet in de lijst van "
                          f"{len(top['herijkt'])} regels; laagste gepubliceerde selection_score "
                          f"{drempel_score}")}
            buiten += 1
        print(f"{buiten} gekwalificeerde selectie(s) buiten de lijst van §5b")

        for comp, blok in st["competitions"].items():
            entry = {"status": "GEANALYSEERD", "matches": []}
            for m in blok["matches"]:
                e = dict(m)
                sleutel_bet = any((m["match"], mk, se) in gespeeld
                                  for mk, se in [(c["market"], c["selection"])
                                                 for c in m.get("all_candidates", [])])
                # §6d/§1a: is er op dit duel gepubliceerd, dan is een andere selectie van
                # dezelfde wedstrijd dezelfde mening en geen afgewezen kandidaat.
                nm = m.get("near_miss")
                if nm and any(mm == m["match"] for mm, _, _ in gespeeld):
                    e["near_miss_gepubliceerd"] = e.pop("near_miss")
                e["bet"] = sleutel_bet
                entry["matches"].append(e)
            mark(state, comp, entry)

        # Dekkingstabel: óók de competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/ra_oct24_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct24_cups.json"))["cups"]
        for comp, v in cups.items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": v["status"], "matches": [],
                               "bron": "BetExplorer (geen fotmob_id; §5)",
                               "eerstvolgende_ronde": v.get("eerste_ronde"),
                               "teamparen_op_de_fixturepagina": v.get("teamparen")})

        save(state)   # mark_completed pas na het runrapport en de push (Stage -1)
        print(f"run-state Run {run} weggeschreven ({len(state['competitions'])} competities)")

    # schaduwrijen van vanochtend die nu een gepubliceerde bet zijn
    sel = {(p["home"] + " – " + p["away"], p["market"] + " — " + p["selection"]) for p in alle_picks}
    rijen = [json.loads(l) for l in open("data/shadow.jsonl") if l.strip()]
    houden = [r for r in rijen if not (r["date"] == DAG and (r["match"], r["market"]) in sel)]
    weg = len(rijen) - len(houden)
    with open("data/shadow.jsonl", "w") as f:
        for r in houden:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{weg} schaduwrij(en) verwijderd die nu een echte bet zijn")

    with open("data/picks.jsonl", "a") as f:
        for p in alle_picks:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{len(alle_picks)} picks toegevoegd aan data/picks.jsonl")


if __name__ == "__main__":
    if "--schrijf" in sys.argv:
        wegschrijven()
    else:
        for run, pad in (("A", "tmp-run/ra_oct24_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct24_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct24_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

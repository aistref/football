"""Run A 25 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct24_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWAALF van de eenentwintig competities uit de runlijst speelden, met 46 duels in het
inzetvenster: een volle zondag met vijf duels in de Premier League, de Serie A en de Eredivisie,
zes in de Ligue 1 en vier in de La Liga, de Primeira Liga, de Belgian Pro League en de Danish
Superliga.

DE WINTERTIJD IS VANNACHT INGEGAAN en dat raakt dit bestand twee keer: `NL` is hier
`ZoneInfo("Europe/Amsterdam")` geworden in plaats van een hardgecodeerde +02:00, en `CAPTURED`
staat op +01:00. Zie DE_KLOK_IS_VANNACHT_TERUGGEZET_EN_DAT_IS_VANDAAG_GEREPAREERD.

GEEN ENKEL duel is kruis-grens en TWEE komen op NONE uit (Hull City – Brentford en AC Horsens –
Sønderjyske, beide buiten conversion_in_range), dus 44 van de 46 zijn doorgerekend. 36 staan op
FULL; de 8 andere hebben een omgerekende ploeg en staan daarom op LIGHT met de lat van 16,0 pp.

DE LIJSTLENGTE BINDT, voor de tweede dag op rij: er zijn ZES duels met een publiceerbare
selectie en er passen VIJF regels in (MAX_SHORTLIST = 5, zondag). Alle vijf gepubliceerde regels
staan op FULL en halen hun eigen lat van 8,0 pp — dat is de eerste Run A-dag in weken waarop de
hele lijst dat doet. De zesde, Śląsk Wrocław – Wieczysta Kraków Over 3.5, haalt zijn LIGHT-lat van
16,0 pp óók (+17,12 pp) en valt tóch af, omdat `selection_score` LIGHT met 0,5 weegt. Zie
EEN_GEKWALIFICEERDE_SELECTIE_VALT_AF_OP_LIJSTLENGTE en
VIER_VAN_DE_VIJF_REGELS_STAAN_OP_DE_OVER_KANT_EN_ALLE_VIJF_VER_VAN_PINNACLE.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-25"
NL = ZoneInfo("Europe/Amsterdam")   # 25 okt 2026: wintertijd (+01:00), zie de kop
CAPTURED = "2026-10-25T03:33:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok — WINTERTIJD


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
                      + ("ONDER-KANT: §6g meet dat P(Under) bij élk duel ruim anderhalf procentpunt "
                         "te hoog staat door een vormfout in score_grid (gemeten vandaag over "
                         "1611 doorgerekende duels: P(Under 3.0) voorspeld 64,1% tegen werkelijk "
                         "62,4%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de "
                         "gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,607 "
                         "doelpunt per duel over 93 gevallen (z = +3,55), terwijl de Over-kant op "
                         "-0,243 staat (z = -0,99 over 56 gevallen). "
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
    for run, pad in (("A", "tmp-run/ra_oct25_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "DE_KLOK_IS_VANNACHT_TERUGGEZET_EN_DAT_IS_VANDAAG_GEREPAREERD": (
                "In de nacht van zaterdag 24 op zondag 25 oktober ging de Nederlandse klok van "
                "03:00 CEST naar 02:00 CET. Dit is de eerste rundag op wintertijd, en Run A van "
                "24 oktober noteerde als actiepunt dat de hardgecodeerde +02:00 in de runscripts "
                "er 'vanaf morgen een uur naast' zou zitten. DAT IS VANDAAG UITGEVOERD: "
                "`ra_oct25_analyze.py` en `ra_oct25_publiceer.py` gebruiken nu "
                "ZoneInfo('Europe/Amsterdam') in plaats van timezone(timedelta(hours=2)), en "
                "`odds_captured_at` staat op +01:00. Het veld `kickoff_nl` in picks.jsonl komt "
                "uit die omrekening en staat dus in échte NL-tijd: Śląsk Wrocław – Wieczysta "
                "Kraków om 12:15 en niet 13:15, Sunderland – Leeds United om 17:30 en niet "
                "18:30. §5 ('Aftraptijden') noemt een aftraptijd die er een uur naast zit "
                "terecht een bet die onbruikbaar is, dus dit was geen cosmetisch punt. "
                "WAT ER AL GOED STOND: `scripts/runwindow.py` en `scripts/report.py` rekenden al "
                "met zoneinfo, dus het inzetvenster en de HTML-pagina hadden er geen last van — "
                "nagetrokken aan één getal: een aftrap van 14:00 UTC komt op 15:00 NL uit en "
                "niet op 16:00. De terugval `timezone(timedelta(hours=2))` in runwindow.py blijft "
                "staan voor een host zonder tzdata; die is op deze container niet gebruikt."),
            "EEN_STILLE_VERKEERDE_AFWIKKELING_IS_VANDAAG_GEVONDEN_EN_GEREPAREERD": (
                "DIT IS DE BELANGRIJKSTE BEVINDING VAN DEZE RUN en ze zat niet in de analyse maar "
                "in Stage 0. `scripts/shadow.py open` meldde de schaduwrij van Portland Timbers – "
                "Charlotte FC (MLS, Run B van 24 oktober) als afwikkelbaar met 'bron meldt "
                "afgelopen — 4 - 1', terwijl dat duel op dat moment nog niet was begonnen. De "
                "uitslag 4-1 kwam van Portland Hearts of Pine – Charlotte Independence uit de USL "
                "League One, een heel andere competitie. OORZAAK: de tweede stap van "
                "`settling.DayIndex.lookup` vergeleek alleen de eerste ZES letters van beide "
                "clubnamen ('portla', 'charlo') en accepteerde de koppeling omdat er op die "
                "daglijst precies één zo'n wedstrijd stond. 'Precies één kandidaat' is geen "
                "bescherming als die ene kandidaat een andere club is. REPARATIE: de stap eist nu "
                "dat één genormaliseerde naam een echt VOORVOEGSEL van de andere is "
                "(`settling._prefix_pair`), wat 'Swansea' aan 'Swansea City' en 'Grazer AK' aan "
                "'Grazer AK 1902' blijft koppelen en 'Portland Timbers' niet meer aan 'Portland "
                "Hearts of Pine'. Spellingvarianten die ná het gedeelde begin uiteenlopen horen "
                "in de aliastabel van `scripts/teamnames.py` — dat is stap 3 en die is er precies "
                "voor. NA DE REPARATIE wacht de rij correct ('bron meldt nog niet afgelopen'). "
                "Er is deze run GEEN enkele regel op een verkeerde uitslag afgewikkeld: het "
                "settle-script van Stage 0 koppelt zelf op een exacte naam plus voorvoegsel per "
                "dag en gaf voor beide MLS-duels 'MIS', dus de fout is gevonden vóórdat ze iets "
                "heeft weggeschreven. Dit is dezelfde stille faalvorm als `calibration.py settle` "
                "(§6b-5c) en het Serie B-id: een stap die fout kan gaan zonder dat iets klaagt, "
                "en §6d zegt dat één verkeerd afgerekende regel bij deze aantallen zwaarder weegt "
                "dan alles wat de stap goed doet. WAT ER OPEN BLIJFT: er is niet nagegaan of deze "
                "regel in het verleden al eens een verkeerde uitslag heeft weggeschreven. Dat is "
                "een audit over 61 rundagen en staat als actiepunt in het dagrapport."),
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0.977473, "
                "b=-0.014593 over 5778 afgerekende gevallen, fitted_through 2026-10-24, oftewel "
                "de vorige rundag zoals §6b-5c eist. `calibration.py settle` is deze run vóór de "
                "tweede analysepas gedraaid (291 waarnemingen afgewikkeld, 5985 van 6033 "
                "compleet, 48 nog open), dus er is geen regel gepubliceerd op een verouderde "
                "correctie — de eerste pas liep nog op fitted_through 2026-10-23 en is daarom "
                "overgedaan. DE FIT IS OPNIEUW VRIJWEL DE IDENTITEIT: a wijkt 2,3% van 1 af en b "
                "1,5 procentpunt van nul, en over de speelbare koersband haalt hij tussen 0,1 en "
                "0,7 procentpunt van een kans af (30% -> 30,1%, 50% -> 49,6%, 70% -> 69,3%). Het "
                "ruwe model zei gemiddeld 33,333% en het gebeurde 33,333%. Bij alle zes de "
                "gekwalificeerde selecties vallen de herijkte en de ruwe edge daardoor binnen vier "
                "tienden van een procentpunt samen. Dat is precies wat §1e punt 3 beschrijft: op "
                "de ongeselecteerde ijksteekproef is het ruwe model al goed gekalibreerd. GEVOLG "
                "DAT HOORT MEE TE WEGEN: de bescherming waarop het vervallen van poort 8 in "
                "september werd verantwoord is er ook vandaag niet, en dat is de gemeten reden dat "
                "poort 8 sinds 1 oktober weer bindt. `bet_beide` staat op TRUE bij alle zes, en "
                "`poort8_ruw` is daarom LEEG."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWAALF van de eenentwintig competities uit de runlijst speelden, samen 46 duels "
                "in het inzetvenster — een volle zondag, negen minder dan de recordzaterdag van "
                "gisteren (51). Per competitie: Premier League 5, Serie A 5, Eredivisie 5, Ligue "
                "1 6, La Liga 4, Primeira Liga 4, Belgian Pro League 4, Danish Superliga 4, "
                "Ekstraklasa 3, Bundesliga 2, Super Lig 2 en Scottish Premiership 2. De NEGEN "
                "competities zonder wedstrijd zijn de Championship (hervat 30 oktober), de drie "
                "Europese toernooien (UCL 3 november, UEL en UECL 5 november) en de vijf bekers. "
                "Dat is geen storing (§3 Stage 2) maar de kalender. Alle zestien competities met "
                "een fotmob_id zijn door een tweede bron bevestigd — zie "
                "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON. ALLE 46 DUELS ZIJN SPEELBAAR: de vroegste "
                "aftrap is 12:15 NL (Śląsk Wrocław – Wieczysta Kraków en Fortuna Sittard – "
                "Excelsior) en de laatste 21:30 NL (Sporting CP – Académico Viseu), dus geen "
                "enkel duel was al afgetrapt voordat de gebruiker kon inzetten. Alle 46 stonden "
                "op de daglijst van 25 oktober (source_day = DAY), dus er is geen enkel duel uit "
                "de band 00:00-08:00 van morgen en geen carry-over."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven — dat kostte Run A op 6 oktober vijf duels. "
                "Alle vijf zijn daarom langs BetExplorer gegaan (tmp-run/ra_oct25_cups.py) en "
                "alle vijf leveren teamparen op de fixturepagina (FA Cup 40, League Cup 8, Coppa "
                "Italia 8, KNVB Beker 26, DFB Pokal 16), dus geen van de drie faalmodi van die "
                "bron is opgetreden. NUL ervan valt in het inzetvenster: DFB Pokal 27.10. 18:00, "
                "KNVB Beker 27.10. 18:45, League Cup 27.10. 20:45, FA Cup 06.11. 20:45 en Coppa "
                "Italia 01.12. 21:00. De Fotmob-daglijst van 25 oktober noemt geen van deze vijf. "
                "Twee bronnen, hetzelfde antwoord. LET OP: drie van de vijf spelen OVERMORGEN, "
                "dus de run van 27 oktober krijgt ze wel."),
            "GEEN_KRUIS_GRENSDUEL_EN_TWEE_KEER_NONE": (
                "Alle 46 duels zijn binnenlands, dus scripts/interleague.py komt deze run niet "
                "aan de orde (§4, Kruis-grens). 36 duels staan op FULL, 8 op LIGHT met een "
                "omgerekende ploeg, en TWEE komen op NONE uit: Hull City – Brentford en "
                "AC Horsens – Sønderjyske, beide omdat een ploeg buiten het gemeten bereik van de "
                "omrekening valt (conversion_in_range). Dat is de Coventry-val zoals §4 hem "
                "beschrijft en de juiste uitkomst: buiten het waargenomen bereik is er geen "
                "meting, en dan is doorrekenen raden. 44 van de 46 duels zijn dus werkelijk "
                "doorgerekend, met 636 selecties over zes markten."),
            "TIEN_OMGEREKENDE_DUELS_WAARVAN_ACHT_OP_LIGHT_UITKOMEN": (
                "Tien duels hebben een ploeg die vorig seizoen niet in deze divisie speelde en "
                "zijn via scripts/promotion.py omgerekend in plaats van op NONE gezet (§4, "
                "'Promovendi: eerst omrekenen, dan pas NONE'): Hull City – Brentford, Atalanta – "
                "Frosinone, Genoa – Venezia, Auxerre – Le Mans, Toulouse – Troyes, Sporting CP – "
                "Académico Viseu, Göztepe – Çorum FK, FC Midtjylland – Lyngby, AC Horsens – "
                "Sønderjyske en Śląsk Wrocław – Wieczysta Kraków. ACHT lukken en komen op LIGHT "
                "uit met de lat van 16,0 pp; TWEE stranden op conversion_in_range (Hull City en "
                "AC Horsens). Lees `GapResult.direction` per selectie voor de stand omhoog of "
                "omlaag, want een samenvattende zin daarover is in dit bestand al een keer "
                "achterhaald geraakt (§4, 9 okt 2026). De omgerekende sterkte is daarna geblend "
                "met het lopende seizoen (§4, k=8); de SPLITS blijven ongeblend."),
            "VIJF_REGELS_DIE_ALLE_VIJF_HUN_EIGEN_LAT_HALEN": (
                "MAX_SHORTLIST = 5 (zondag) en de lijst is VOL. De lijst, op selection_score: "
                "1. Sunderland – Leeds United Over 2.5 @2.2544 na commissie (+13,19 pp, FULL, "
                "score 7,590), 2. Real Sociedad – Levante Over 2.5 @1.64 (+9,37 pp, FULL, 6,591), "
                "3. NEC Nijmegen – FC Groningen Over 3.5 @2.15 (+11,14 pp, FULL, 6,426), "
                "4. Manchester United – AFC Bournemouth Over 2.5 @1.71 (+9,45 pp, FULL, 6,421) "
                "en 5. Lecce – Juventus BTTS 'nee' @1.8918 na commissie (+9,53 pp, FULL, 5,943). "
                "ALLE VIJF STAAN OP FULL EN HALEN ALLE VIJF HUN EIGEN LAT van 8,0 pp — dat is de "
                "eerste Run A-dag in weken waarop de hele lijst dat doet, en het is het "
                "tegenovergestelde van gisteren, toen drie van de vijf hun lat haalden en twee op "
                "rangorde werden gepubliceerd. MAX_LIGHT_IN_SHORTLIST = 2 bindt NIET en kan niets "
                "uitsluiten: er staat geen enkele LIGHT-regel in de lijst, want de enige "
                "LIGHT-kandidaat van de dag viel af op lijstlengte."),
            "EEN_GEKWALIFICEERDE_SELECTIE_VALT_AF_OP_LIJSTLENGTE": (
                "Śląsk Wrocław – Wieczysta Kraków, Over 3.5 @2.4308 na commissie (+17,12 pp op "
                "LIGHT, score 4,987), staat op RANG 6 en valt daarmee buiten de lijst. Dat is een "
                "`gekwalificeerd_niet_gepubliceerd`-blok plus een `near_miss` met failed_gate = "
                "'lijstlengte' (§5b, 26 sep 2026) — geen afgewezen kandidaat, want geen enkele "
                "poort heeft haar tegengehouden, en ook geen bet. De reeks `lijstlengte` groeit "
                "daarmee van 19 naar 20; ze staat op +30,7% over 19 afgewikkelde gevallen (10 van "
                "19 gewonnen) en is daarmee de enige schaduwreeks die duidelijk positief staat met "
                "aantallen eronder die §6d's grens van ~30 naderen. Tel haar nooit bij `edge` op "
                "(§5b). "
                "WAT HIER OPVALT, en het is het spiegelbeeld van gisteren: deze selectie haalt "
                "haar eigen lat van 16,0 pp met ruime marge (+17,12 pp) en valt tóch af, terwijl "
                "ze gisteren juist twee LIGHT-regels ONDER hun lat gepubliceerd zag worden. Beide "
                "uitkomsten volgen uit dezelfde twee regels samen. (1) De drempel is sinds "
                "20 september geen poort meer maar een afkapping; er staan ZES selecties boven hun "
                "eigen lat en er passen er vijf, dus de drempel bindt hier WEL als grens — maar "
                "hij snijdt alle zes door, dus de rangorde beslist alsnog. (2) Die rangorde is "
                "`selection_score` = edge x kans x (FULL 1,0 | LIGHT 0,5), en daarin verslaat "
                "+9,53 pp op FULL (score 5,943) een +17,12 pp op LIGHT (4,987). Deze run verandert "
                "er NIETS aan — `selection_score` is per §1a een besluit van de gebruiker over "
                "risicobereidheid en geen keuze van de run. Het punt is op 24 oktober al één keer "
                "als besluit voorgelegd en wordt vandaag dus niet opnieuw voorgelegd, alleen "
                "opgeschreven."),
            "VIER_VAN_DE_VIJF_REGELS_STAAN_OP_DE_OVER_KANT_EN_ALLE_VIJF_VER_VAN_PINNACLE": (
                "DIT IS DE BELANGRIJKSTE WAARSCHUWING BIJ DE BETS ZELF en ze hoort niet in een "
                "voetnoot. Alle vijf de gepubliceerde regels liggen op de DOELPUNTENAS — vier "
                "Overs en één BTTS 'nee' — en bij alle vijf staat het eigen model verder van het "
                "scherpste publieke boek dan het dagcijfer suggereert. Eigen P(Under) tegen "
                "Pinnacle's de-vigde P(Under) op Pinnacle's eigen lijn: Sunderland – Leeds "
                "34,8% tegen 48,6% (-13,8 pp), NEC Nijmegen – FC Groningen 36,0% tegen 48,2% "
                "(-12,2 pp), Real Sociedad – Levante 41,5% tegen 49,1% (-7,6 pp) en Manchester "
                "United – AFC Bournemouth 46,5% tegen 52,8% (-6,3 pp). Alle vier staan dus "
                "MINDER Under en dus MEER Over dan Pinnacle: het model verwacht structureel meer "
                "doelpunten dan het scherpste boek. Lecce – Juventus staat de andere kant op, "
                "+6,4 pp boven Pinnacle op de Under, en is daarmee de enige regel op de kant "
                "waarvan §6g de scheefstand heeft gemeten. HET DAGCIJFER IS +0,14 pp met 24 van "
                "41 (duel, lijn)-paren boven Pinnacle, dus de vijf regels zijn precies de STAART "
                "van die verdeling en niet het midden — en drie van de vijf grootste afwijkingen "
                "van de dag zijn gepubliceerde regels. Op de 1X2-as is het dagcijfer 3,94 pp "
                "gemiddelde absolute afstand bij een Pinnacle-marge van 3,72% tegen 6 à 10% bij "
                "de rest. Dat is exact het patroon waarvoor §1g waarschuwt: de grootste geclaimde "
                "edge is doorgaans de grootste MODELfout en niet de grootste marktfout. HARDE "
                "GRENS §2/§4: dit getal zit niet in my_prob en niet in prob_sources; het staat in "
                "de vergelijking."),
            "DE_ENE_BTTS_REGEL_STAAT_IN_DE_MARKT_DIE_POORT_9_MET_OPZET_NIET_RAAKT": (
                "Lecce – Juventus BTTS 'nee' @1.8918 is een weddenschap op WEINIG doelpunten, en "
                "dat is de richting waarvan §6g de scheefstand meet. Poort 9 raakt hem niet: §1h "
                "punt 2 houdt BTTS er MET OPZET buiten omdat er geen meting voor is. Anders dan "
                "bij Chelsea – Tottenham op 24 oktober is dit GEEN verplaatsing door de poort — "
                "de twee Unders van dit duel (+7,59 en +5,56 pp) vielen af op de gewone drempel "
                "van 8,0 pp en niet op poort 9, dus er was hier niets om te verplaatsen. Wat wél "
                "geldt: deze regel is door geen enkele doelpuntenrem getoetst. De eigen "
                "doelverwachting is 0,568 thuis tegen 1,916 uit — Lecce dat niet scoort is de kern "
                "van de bet, niet een laag totaal. De BTTS-reeks staat op 22 afgewikkelde gevallen "
                "in beide richtingen samen; §1h punt 2 noemt ~30 als de grens waarop die vraag "
                "opnieuw hoort te worden bekeken, en die is niet gehaald. Deze run verandert dus "
                "NIETS aan de poort en legt ook geen besluit voor (§1h, 'gevraagd en beantwoord op "
                "12 oktober': stel de vraag niet elke dag opnieuw)."),
            "POORT_9_BINDT_OP_DRIE_DUELS": (
                "Veertiende bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke "
                "selectie aangeroepen met today=2026-10-25. Er zijn 83 FULL-Unders doorgerekend en "
                "VIER vallen in de band 8–10 pp waar de verzwaarde lat van 10,0 pp snijdt, "
                "verdeeld over DRIE duels: Legia Warszawa – Lech Poznań Under 2.5 (+8,88) en "
                "Under 2.75 (+8,28), Athletic Club – Getafe Under 2.5 (+8,27) en Union "
                "St.Gilloise – Cercle Brugge Under 3.25 (+8,12). Bij Legia Warszawa – Lech Poznań "
                "is 'poort 9' de reden van de HELE wedstrijd: er bleef daarna geen enkele "
                "selectie over. De reeks `doelpunten_onder` staat op 12 afgewikkelde gevallen "
                "(58,3% trefkans, +6,9%) en gaat vandaag naar 15 open-plus-afgewikkeld. DIE +6,9% "
                "IS GEEN SIGNAAL: §6d eist ~30 gevallen en het waren er gisteren nog 10 met "
                "−11,0% — een reeks die binnen één dag van −11% naar +7% beweegt is per definitie "
                "ruis. De 21 LIGHT-Unders blijven per besluit van 12 oktober buiten de poort; hun "
                "hoogste edge is +7,80 pp, dus de poort zou daar vandaag hoe dan ook niets hebben "
                "geraakt."),
            "POORT_8_HOUDT_VEERTIEN_DUELS_TEGEN_EN_KOST_DE_HOOGSTE_SCORE_VAN_DE_DAG": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), aangeroepen "
                "met today=2026-10-25 zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van geraden. 29 selecties "
                "over VEERTIEN duels sneuvelen op deze poort. HIJ KOST DE HOOGST SCORENDE "
                "SELECTIE VAN DE HELE DAG: Sparta Rotterdam – Ajax, Sparta Rotterdam +1.5 @1.75 "
                "(+11,71 pp, score 8,064) — hoger dan elke gepubliceerde regel, want de beste "
                "daarvan staat op 7,590. De markt geeft Sparta 20,1% en het model 68,9% op de "
                "+1.5. Daarnaast Celta Vigo – Real Betis (Celta Vigo wint @3.352, +12,33 pp, score "
                "5,198; markt 29,8% tegen model 42,2%) en Union St.Gilloise – Cercle Brugge "
                "(Cercle Brugge +1.5 @1,9702, +7,79 pp, score 4,560). Bij alle drie bleef er na de "
                "poort niets over, dus het zijn drie duels waarvan de reden van de hele wedstrijd "
                "elders ligt. `poort8_ruw` is LEEG: geen enkele kandidaat sneuvelde alléén op de "
                "ruwe schaal, wat logisch is bij een fit die vrijwel de identiteit is. De twee "
                "reeksen blijven twee populaties die nooit worden opgeteld — `underdog` staat op "
                "209 afgewikkelde gevallen (49,3% trefkans, −3,4%) en `underdog_ruw` op 17 (41,2%, "
                "−8,8%). Hun stand staat in het runrapport onder 'Stand van het logboek' en wordt "
                "daar NIET als besluit voorgelegd (§1e, 5 oktober: stel de vraag niet elke dag "
                "opnieuw)."),
            "POORT_7_HOUDT_28_SELECTIES_TEGEN_OVER_ACHT_DUELS": (
                "context.check sloot bij 28 van de 636 doorgerekende selecties de poort, verdeeld "
                "over ACHT duels. Bij ÉÉN duel is het de reden van de hele wedstrijd: Monaco – "
                "Lille, waar Lille 32% van zijn selectiewaarde mist tegen 8% bij Monaco (Osame "
                "Sahraoui, Tiago Santos en Ayase Ueda) en de uitzege @+12,17 pp daarmee de poort "
                "niet haalt. De andere zware gevallen: Udinese – Milan (Milan 3 dagen rust tegen 7 "
                "bij Udinese, vijf selecties geblokkeerd), Rennes – Strasbourg (Strasbourg mist "
                "40% tegen 21%), Crystal Palace – Newcastle United (3 dagen rust tegen 8) en "
                "Śląsk Wrocław – Wieczysta Kraków (16% tegen 3%). "
                "GEEN van de vijf gepubliceerde regels is door deze poort geraakt, en dat is geen "
                "toeval: alle vijf zijn een totaal of een BTTS, dus side = None, en dan staat "
                "poort 7 per §1c altijd open — er is geen kant om te benadelen. Dat de "
                "doelpuntenmarkten de hele lijst vullen op een dag dat poort 7 en poort 8 samen "
                "57 selecties MET een kant tegenhouden, is dus deels een gevolg van de "
                "poortconstructie en niet alleen van de analyse; het hoort genoemd. De reeks "
                "`context` staat op 88 afgewikkelde gevallen met −22,7%, de slechtst renderende "
                "van het logboek, wat betekent dat deze poort zijn werk doet."),
            "GEEN_VERPLAATSTE_WEDSTRIJD_EN_GEEN_ENKELE_STADIONNAAM": (
                "context.check_venue is voor alle 46 duels gedraaid en zet nergens relocated = "
                "True. Daar hoort hetzelfde voorbehoud bij als op 23 en 24 oktober, en het is "
                "eerlijker dan 'alles in orde': de Fotmob-respons gaf voor GEEN ENKEL van de 46 "
                "duels een stadionnaam (venue.name is overal None), dus de controle heeft niets "
                "kunnen vergelijken en 'niet verplaatst' betekent hier 'geen verplaatsing "
                "gemeten' en niet 'gemeten dat er geen verplaatsing is'. Dat is dezelfde soort "
                "stille leegte als §1c beschrijft. Het is ook het verwachte beeld voor "
                "binnenlandse competitiewedstrijden, en §1c zegt zelf dat de controle een "
                "fixture die van eigenaar is gewisseld niet kan vangen — dat is nieuws en geen "
                "data, en een geplande run heeft geen nieuwsbron."),
            "MARKTBALANS_ALLE_ZES_MARKTEN_DEDEN_MEE": (
                "Alle zes markten zijn werkelijk doorgerekend, en dat is bij The Odds API geen "
                "automatisme: de bulk-aanroep (h2h + spreads + totals, 3 credits per competitie) "
                "dekt 1X2, AH, DNB en DC en O/U in één keer, en BTTS is in een tweede ronde per "
                "duel gekocht voor de 30 wedstrijden met een kandidaat-edge (§1a stap 2). "
                "Selecties doorgerekend per markt: Over/Under 208 in 11 competities, Asian "
                "Handicap 175 in 11, 1X2 127 in 12, BTTS 60 in 11, Draw No Bet 42 in 10 en Double "
                "Chance 24 in 10 — samen 636. Bets: Over/Under 4, BTTS 1, de rest nul. "
                "INKOOPEFFECT: alle zes markten deden overal mee, dus de eenzijdige uitkomst is "
                "deze keer GEEN inkoopeffect. Dat alle vijf de regels uit de doelpuntenmarkt "
                "komen heeft de verklaring die in POORT_7 en POORT_8 staat: die twee poorten "
                "raken uitsluitend selecties MET een kant (28 + 29 tegengehouden selecties), en "
                "bij side = None staan ze per §1c altijd open. De Scottish Premiership heeft geen "
                "sportkey bij The Odds API (coverage.json), dus daar is BetExplorer de enige "
                "1X2-bron en is er geen AH, DNB, DC, O/U of BTTS gekocht; haar twee duels hebben "
                "daarom alleen 1X2. Credits: 33 voor de bulk plus 30 voor BTTS = 63 van een "
                "dagplafond van 1341, en 18743 van 20000 over voor de rest van de maand."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Gevonden voor 40 van de 46 duels op 1X2 en voor 41 "
                "(duel, lijn)-paren op de totalen, met een gemiddelde Pinnacle-marge van 3,72% "
                "tegen 6 à 10% bij de rest. De zes zonder Pinnacle-1X2 zijn de twee Schotse duels "
                "(geen sportkey), Sporting CP – Académico Viseu, Club Brugge – St.Truiden en de "
                "twee duels op NONE. Gemiddelde absolute afstand tussen het eigen model en het "
                "Pinnacle-1X2: 3,94 procentpunt. De grootste 1X2-afwijkingen: Sparta Rotterdam – "
                "Ajax +15,68 pp op de thuiszege (en −18,93 op de uitzege), FC Midtjylland – "
                "Lyngby −15,02 pp op de thuiszege en Celta Vigo – Real Betis +14,71 pp op de "
                "thuiszege — alle drie duels waar poort 8 of de tweede methode de selectie heeft "
                "tegengehouden. Op de doelpuntenkant staat het model gemiddeld 0,14 pp BOVEN "
                "Pinnacle op de Under met 24 van 41 erboven. Zie "
                "VIER_VAN_DE_VIJF_REGELS_STAAN_OP_DE_OVER_KANT_EN_ALLE_VIJF_VER_VAN_PINNACLE. "
                "HARDE GRENS §2/§4: dit getal zit NIET in my_prob en NIET in prob_sources."),
            "UNDERSTAT_DEKT_ZESTIEN_VAN_DE_VIERENVEERTIG": (
                "Alle VIJF Understat-competities spelen vandaag (PL, Serie A, La Liga, "
                "Bundesliga, Ligue 1), samen 16 duels met een stand in beide bronnen. Daar is dus "
                "een tweede, ONAFHANKELIJK xG-model naast Fotmob (§4), inclusief rollende xG over "
                "acht duels. DAT RAAKT VIER VAN DE VIJF GEPUBLICEERDE REGELS: Sunderland – Leeds "
                "United, Manchester United – AFC Bournemouth, Real Sociedad – Levante en Lecce – "
                "Juventus hebben een kansinput uit twee verschillende xG-modellen in plaats van "
                "twee doorsnedes van één. NEC Nijmegen – FC Groningen (Eredivisie) heeft dat niet "
                "en leunt volledig op Fotmob, in twee doorsnedes (team-xG en de thuis/uit-splits). "
                "Dat is genoeg voor §2 — de twee methodes zijn twee methodes, geen twee bronnen — "
                "maar het is minder redundantie, en het hoort genoemd in plaats van stilzwijgend "
                "overgeslagen. LET OP bij het naast elkaar leggen: Understat ligt structureel "
                "~0,13 xG per ploeg per duel hoger dan Fotmob, dus normaliseer altijd op het "
                "eigen competitiegemiddelde van de bron (§4)."),
            "VROEG_SEIZOEN_EN_NIVEAU": (
                "early_season_uplift geeft factor 1.1046, gepoold 1.1130 over 100 speeldagen in "
                "ELF competities. ÉÉN competitie is uit de pool gelaten en dat is de meting zelf "
                "(§3 Stage 5, 24 sep 2026): de Danish Superliga staat op 12 van zijn 22 "
                "speeldagen en is daarmee op of boven SEASON_MATURE_SHARE, dus zij draait op de "
                "route `lopend` — haar niveau komt uit het lopende seizoen zelf, ongeschaald, en "
                "haar niveauverschil drukt niet in de gepoolde factor van de andere elf. De "
                "overige elf lopen op `vorig+uplift`, met een lopend seizoen van 7 speeldagen "
                "(Bundesliga) tot 12 (Ekstraklasa). Een uplift van 10,5% is hoog maar in oktober "
                "verwacht: de teamsterktes komen uit vorig seizoen en begin seizoen wordt er meer "
                "gescoord — de correctie dooft vanzelf uit. DIT IS DE DERDE DAG OP RIJ MET EEN "
                "`lopend`-route voor Denemarken (gisteren niet: toen speelde de Danish Superliga "
                "niet), en het is de competitie waar die route het eerst bindt omdat haar seizoen "
                "maar 22 speeldagen lang is. De niveaus per competitie staan in `niveau`, met de "
                "route en de reden erbij."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert "
                "de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van de zestien "
                "competities met een fotmob_id zijn het eens, inclusief de vier die vandaag GEEN "
                "WEDSTRIJD hebben: 46 duels bij Fotmob, 46 bij BetExplorer, nul afwijkingen en "
                "geen enkele bron die faalde (tmp-run/ra_oct25_bevestiging.py). Per competitie "
                "bevestigd op het aantal, inclusief de zes van de Ligue 1 en de vijf van de "
                "Eredivisie. De vijf bekers hebben geen fotmob_id en gaan langs hun eigen tweede "
                "bron — zie DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN. LET OP DE "
                "TIJDZONE: BetExplorer labelt in UK-tijd, en sinds vannacht is dat GMT tegen CET "
                "in Nederland — nog steeds precies één uur verschil, dus het venster "
                "[25.10. 08:00 NL, 26.10. 08:00 NL) is in UK-tijd [25.10. 07:00, 26.10. 07:00) en "
                "de filter hoefde niet te veranderen."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [25.10. 08:00 NL, 26.10. 08:00 NL). "
                "Alle 46 duels stonden op de daglijst van 25 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 46 zijn playable: de "
                "vroegste aftrap is 12:15 NL en de laatste 21:30 NL. Er is dus geen enkel duel "
                "dat al was afgetrapt voordat de gebruiker kon inzetten, en geen carry-over-band. "
                "DE KLOK IS VANNACHT TERUGGEZET en runwindow rekent met zoneinfo, dus het venster "
                "is in échte NL-tijd gemeten: een aftrap van 14:00 UTC komt op 15:00 NL uit (CET) "
                "en niet op 16:00 (CEST). Zie "
                "DE_KLOK_IS_VANNACHT_TERUGGEZET_EN_DAT_IS_VANDAAG_GEREPAREERD voor wat er in de "
                "runscripts zelf aan is veranderd."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag WEL: er zijn ZES publiceerbare selecties en vijf
        # plekken beschikbaar, dus er valt er precies één af. Deze lus legt zo'n
        # gekwalificeerde selectie vast als `gekwalificeerd_niet_gepubliceerd` plus een
        # `near_miss` met `failed_gate = "lijstlengte"` — bewust dezelfde naam, zodat de
        # populatie niet in twee reeksen uiteenvalt (§5b, 26 sep 2026).
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
        s3 = json.load(open("tmp-run/ra_oct25_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct25_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct25_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct25_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct25_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

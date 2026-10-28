"""Run A 28 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct27_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. VIJF van de eenentwintig competities uit de runlijst speelden, met DRIEENDERTIG duels in
het inzetvenster, en TWEEENTWINTIG daarvan zijn bekerwedstrijden: een bekerwoensdag, en het
drukste Run A-programma van deze maand. Serie A heeft vijf midweekse duels, de Scottish
Premiership een volle ronde van zes, de League Cup vijf duels tussen Premier League-clubs
onderling, de DFB Pokal acht en de KNVB Beker negen.

ELF VAN DE 33 DUELS KREGEN VANDAAG VOOR HET EERST EEN BESTE PRIJS, en dat is de bevinding van
deze run — zie ELF_VAN_DE_33_DUELS_KREGEN_VANDAAG_VOOR_HET_EERST_EEN_BESTE_PRIJS.

ELF VAN DE 33 DUELS KOMEN OP NONE UIT, en dat is bij een beker normaal en geen storing: de
amateurclubs van de KNVB Beker en de Regionalliga-ploeg van de DFB Pokal staan in geen divisie
waarvoor een gemeten omrekenfactor bestaat, en vijf duels vallen op `conversion_in_range`.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-28"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-10-28T03:35:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok (wintertijd)


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
                      + ("ONDER-KANT: §6g meet dat P(Under) bij élk duel ongeveer twee procentpunt "
                         "te hoog staat door een vormfout in score_grid (gemeten vandaag over "
                         "1686 doorgerekende duels: P(Under 2.5) voorspeld 42,4% tegen werkelijk "
                         "40,3%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de "
                         "gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,587 "
                         "doelpunt per duel over 96 gevallen (z = +3,48), terwijl de Over-kant op "
                         "-0,296 staat (z = -1,25 over 60 gevallen). Dit duel staat op FULL, dus "
                         "poort 9 (§1h) kan hier bijten; of hij dat werkelijk doet hangt af van "
                         "de band waarin de edge valt — hij bindt ALLEEN tussen 8,0 en 10,0 pp, "
                         "en laat een Under daaronder met opzet door omdat `edge` daar de "
                         "bindende poort hoort te zijn. Dat is de rem die er is; de oorzaak — "
                         "keuze (a) van 11 oktober, de vormfout zelf repareren — staat nog open. "
                         "Trek dus ongeveer twee procentpunt van de genoemde kans af voordat je "
                         "haar leest. "
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
    for run, pad in (("A", "tmp-run/ra_oct28_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "EEN_BEKERWOENSDAG_VAN_33_DUELS_WAARVAN_22_IN_EEN_BEKER": (
                "VIJF van de eenentwintig competities uit de runlijst hebben vandaag een duel in "
                "het inzetvenster, samen DRIEENDERTIG wedstrijden — het drukste Run A-programma "
                "van deze maand, en tweeentwintig duels zitten in een beker. Serie A speelt een "
                "midweekse ronde met vijf duels (Milan - Bologna, Parma - Udinese, Venezia - "
                "Inter, Genoa - Juventus, Monza - Napoli); de Scottish Premiership heeft een "
                "volle speelronde van zes; de League Cup heeft zijn vierde ronde met VIJF duels "
                "tussen Premier League-clubs onderling (Manchester City - Brighton, Bournemouth - "
                "Aston Villa, Fulham - Crystal Palace, Sunderland - Brentford, Liverpool - "
                "Chelsea); de DFB Pokal de tweede ronde met acht en de KNVB Beker de tweede ronde "
                "met negen. De Premier League, La Liga, Bundesliga, Ligue 1, Championship, "
                "Eredivisie, Primeira Liga, Belgian Pro League, Super Lig, Danish Superliga en "
                "Ekstraklasa hebben niets op de kalender: hun volgende ronde begint 30 oktober of "
                "1 november. De drie Europese toernooien spelen 3 t/m 5 november, de FA Cup "
                "6 november en de Coppa Italia 1 december. Dat is GEEN WEDSTRIJD en geen storing "
                "(§3 Stage 2)."),
            "ELF_VAN_DE_33_DUELS_KREGEN_VANDAAG_VOOR_HET_EERST_EEN_BESTE_PRIJS": (
                "DIT IS DE BELANGRIJKSTE BEVINDING VAN DE RUN en ze gaat over de inkoop, niet "
                "over de analyse. De runscripts van oktober gaven voor de SCOTTISH PREMIERSHIP en "
                "de LEAGUE CUP `sportkey = None` mee, dus die twee competities draaiden op het "
                "gratis BetExplorer-marktgemiddelde terwijl de beste prijs te koop was. BEIDE "
                "SLEUTELS BESTAAN. `soccer_england_efl_cup` staat sinds 10 augustus 2026 in "
                "`oddsapi.SPORT_KEYS`; voor de Scottish Premiership noteert `coverage.json` bij "
                "die competitie AL SINDS 9 SEPTEMBER dat `soccer_spl` werkte ('5 events op "
                "h2h+spreads+totals'), maar die bevinding is nooit in `SPORT_KEYS` geland. "
                "WAAROM NIEMAND HET ZAG: `api_check.py` filterde zijn lijst 'relevante sportkeys' "
                "op de SLEUTEL en zocht daar het woord 'scot' in — en `soccer_spl` bevat dat "
                "woord alleen in zijn `title` ('Premiership - Scotland') en `description` "
                "('Scottish Premiership'). De controle stond dus elke ochtend groen terwijl ze de "
                "verkeerde grootheid mat: dezelfde stille faalvorm als het Serie B-id en als "
                "`calibration.py settle`, en niets klaagt — er staat alleen een minder gunstige "
                "koers in het rapport. WAT HET KOSTTE: de Scottish Premiership heeft van 9 "
                "september t/m 27 oktober uitsluitend op het marktgemiddelde gedraaid. §1a meet "
                "dat verschil op +7,78% prijs en +1,84 procentpunt edge per selectie, en vandaag "
                "ligt het bij de zes Schotse duels tussen +4,90% en +11,95% (gemiddelde over maar "
                "DRIE boeken bij BetExplorer, dus daar is het gat het grootst) en bij de vijf "
                "League Cup-duels tussen +4,09% en +6,02%. TWEE REPARATIES, vanmorgen vóór de "
                "analyse en niet erna (§4): `soccer_spl` staat nu in `oddsapi.SPORT_KEYS` naast "
                "de drie Europese toernooien die er ook nog niet in stonden, en `api_check.py` "
                "noemt vanaf nu PER BEKENDE SLEUTEL of hij vandaag actief is én welke actieve "
                "sleutels de repo niet kent, gefilterd op sleutel, titel EN beschrijving. Die "
                "tweede lijst wijst meteen nog vijf gaten aan die buiten de Run A-runlijst "
                "vallen en dus voor Run B en C zijn: `soccer_norway_eliteserien`, "
                "`soccer_sweden_superettan`, `soccer_germany_liga3`, `soccer_spain_copa_del_rey` "
                "en `soccer_uefa_nations_league`. GEVOLG VOOR VANDAAG: 20 van de 22 doorgerekende "
                "duels hebben een beste prijs met een herleidbare bookmaker, tegen 11 van de 22 "
                "gisteren. Alleen de twee KNVB Beker-duels die niet op NONE uitkomen (Sparta "
                "Rotterdam - Fortuna Sittard en VVV-Venlo - Vitesse) draaien nog op het "
                "marktgemiddelde; die competitie heeft werkelijk geen sportkey bij de bron."),
            "DE_BEKERS_KOMEN_UIT_DE_DAGLIJST_EN_ZIJN_DOOR_TWEE_BRONNEN_BEVESTIGD": (
                "De drie bekers met een ronde staan in de Fotmob-daglijst: EFL Cup onder id 133 "
                "met 5 duels, DFB Pokal onder 209 met 8 en KNVB Cup onder 235 met 9. Dezelfde "
                "aantallen als BetExplorer (5, 8, 9), dus de dag is met twee methodes vastgesteld "
                "(§1) — en dat is precies de poort waar de duurste fouten van oktober zaten: in "
                "de vraag wélke wedstrijden er zijn, niet in de analyse. Via de daglijst komen de "
                "duels mét `match_id`, dus mét context, opstelling, uitvallers en poort 7; via "
                "BetExplorer alleen met namen en een koers, en dat is wat het op 6 oktober "
                "kostte toen vier van de vijf FA Cup-duels niet door te rekenen waren. DE DRIE "
                "ID'S STAAN NU IN coverage.json ONDER `notes` EN NIET ONDER `fotmob_id`: "
                "`idcheck.py` eist van elk id in dat veld een bruikbare stand en een beker heeft "
                "er geen, dus daar zou elke run een vals alarm van krijgen op precies de controle "
                "die voor een stil verdwenen competitie is gebouwd. De twee bekers zonder ronde "
                "(FA Cup, Coppa Italia) zijn bij BetExplorer nagetrokken en niet uit de daglijst "
                "geconcludeerd: eerstvolgende ronde 6 november en 1 december."),
            "ELF_VAN_DE_33_DUELS_OP_NONE_EN_DAT_IS_BIJ_EEN_BEKER_NORMAAL": (
                "ZEVENTIEN duels komen op FULL uit, VIJF op LIGHT en ELF op NONE. Dat laatste is "
                "bij een bekerronde de verwachting en geen storing: een beker heeft zelf geen "
                "stand, dus de basis ligt per WEDSTRIJD (§4, 15 sep 2026) en een ploeg die niet "
                "in de basisdivisie staat moet uit de divisie eronder worden omgerekend — één "
                "divisie diep, want verder is er geen meting. Van de elf NONE-duels zijn er ZES "
                "waar een ploeg in geen enkele divisie staat waarvoor een factor bestaat: SSV "
                "Jeddeloh (Regionalliga, twee divisies onder de Bundesliga) en de vijf "
                "amateurclubs van de KNVB Beker — Genemuiden, JOS Watergraafsmeer, Quick Boys, "
                "VVSB en Excelsior Maassluis, allemaal onder de Eerste Divisie. De andere VIJF "
                "vallen op `promotion.conversion_in_range`, en dat is de Coventry-val die §4 "
                "beschrijft: 1. FC Nürnberg (relatieve aanval 0.943 tegen een gemeten bereik van "
                "0.999-1.673), Magdeburg (verdediging 1.164 tegen 0.613-0.996), Holstein Kiel "
                "(aanval 0.883), MVV Maastricht en TOP Oss zijn wél omgerekend, maar hun "
                "relatieve sterkte valt buiten het gemeten invoerbereik — en buiten dat bereik is "
                "er geen meting en dus geen onafhankelijke kansinput op het niveau waarop "
                "gespeeld wordt. DRIE DUELS ZIJN DOOR `shared_lower_division` GERED: Dynamo "
                "Dresden - Schalke 04 en Hannover 96 - Kaiserslautern staan beide in de 2. "
                "Bundesliga (FULL, want die divisie heeft xG bij Fotmob) en VVV-Venlo - Vitesse "
                "beide in de Eerste Divisie (LIGHT, want die heeft geen xG). Daar valt niets te "
                "overbruggen, dus wordt het duel in die divisie doorgerekend zonder omrekening — "
                "en dan geldt 'een omgerekende ploeg is nooit FULL' niet, want er is niets "
                "omgerekend. EN EEN VAN DIE DRIE IS EEN BET GEWORDEN: Hannover 96 - "
                "Kaiserslautern, de tweede regel van de dag."),
            "DE_NAAMKOPPELING_VAN_GISTEREN_BEET_VANDAAG_METEEN": (
                "`ra_names.resolve` koppelt sinds 27 oktober op een VOORVOEGSELregel en niet meer "
                "op een deelverzameling van tokens. Vandaag is dat geen theorie: de zelftest "
                "(`ra_oct28_namecheck.py`, 66 namen) laat precies één verschil met de oude regel "
                "zien, en dat is EXCELSIOR MAASSLUIS uit de KNVB Beker. De oude regel koppelde "
                "die amateurclub uit Maassluis aan EXCELSIOR in de Eredivisie-stand; de nieuwe "
                "regel weigert, en het duel komt op NONE uit. Zonder die reparatie was Excelsior "
                "Maassluis - SC Heerenveen doorgerekend met de xG van Excelsior Rotterdam achter "
                "de thuisploeg, en GEEN ENKELE VAN DE NEGEN POORTEN KAN DAT ZIEN — het is geen te "
                "ruime kans maar een verkeerde ploeg. Dezelfde faalvorm als de Jong "
                "Ajax-koppeling waarop `promotion.measure_gap` op 31 augustus een factor van "
                "1.010 vond. Dat een reparatie van gisteren vandaag meteen bijt, is de reden dat "
                "§4 zegt: meet een nieuwe factor liever vóór de analyse van de dag dan erna."),
            "HERIJKING": (
                "§1g, één fit per run uit data/calibration.jsonl: a=0.9928, b=-0.0047 op 6117 "
                "afgerekende gevallen t/m 2026-10-27 — het ruwe model zei gemiddeld 33,3% en het "
                "gebeurde 33,3%. `fitted_through` staat dus op de vórige rundag, zoals §6b-5c "
                "eist; de 57 waarnemingen die nog open stonden zijn vanmorgen door "
                "`calibration.py settle` afgewikkeld voordat de fit is gelezen. De correctie "
                "VERLAAGT vandaag over vrijwel de hele speelbare band, maar nauwelijks: 0,0 pp op "
                "30%, -0,1 pp op 50%, -0,2 pp op 70%. Gevolg voor §5a: een selectie die de "
                "herijkte lat haalt, haalt hem ook ruw, en dat is vandaag bij de twee regels "
                "bóven de lat ook zo (`bet_beide = true` bij Bournemouth, +15,39 pp herijkt tegen "
                "+15,57 ruw, en bij Hannover 96, +11,14 tegen +11,32). De derde regel staat op "
                "`bet_beide = false`: die haalt zijn lat op geen van beide schalen en is op "
                "rangorde gepubliceerd (§5b). Vertrouw die vlag en niet de redenering — §5a "
                "waarschuwt daar uitdrukkelijk voor, omdat de fit elke run een ander getal is."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "De eenentwintig competities van `prompts/run-a.md`, ongewijzigd: dertien "
                "competities en acht toernooien. Vijf hebben vandaag een duel in het venster "
                "(Serie A, Scottish Premiership, League Cup, DFB Pokal, KNVB Beker), zestien "
                "niet. De Fotmob-id's komen uit `data/coverage.json` en zijn deze run alle 33 "
                "groen bevonden door `scripts/idcheck.py`; de drie bekerid's komen uit de "
                "daglijst zelf (zie "
                "DE_BEKERS_KOMEN_UIT_DE_DAGLIJST_EN_ZIJN_DOOR_TWEE_BRONNEN_BEVESTIGD)."),
            "DRIE_REGELS_WAARVAN_TWEE_HUN_EIGEN_LAT_HALEN": (
                "De dagranglijst van §5b heeft DRIE regels en `MAX_SHORTLIST` is 3 (woensdag), "
                "dus de lijstlengte bindt NIET: er valt geen gekwalificeerde selectie buiten de "
                "lijst en `failed_gate = lijstlengte` krijgt vandaag geen enkele rij. Van de drie "
                "halen er TWEE de lat van 8,0 pp — AFC Bournemouth wint tegen Aston Villa @2,32 "
                "(+15,39 pp, score 9,003) en Hannover 96 -0,25 tegen Kaiserslautern @2,06 "
                "(+11,14 pp, score 6,649). De derde staat ERONDER en is op rangorde gepubliceerd: "
                "St. Mirren - Hibernian, Under 3 @1,71 (+6,43 pp, score 4,174). Dat is precies "
                "wat §5b sinds 20 september voorschrijft — de drempel snijdt aan het eind en is "
                "voor de regels eronder een LABEL en geen veto — en het hoort gelezen te worden "
                "als 'dit is het beste van vandaag' en niet als 'dit is een gevonden voordeel'. "
                "§1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op de herijkte "
                "edge bestaat die geld oplevert, en dat het rendement het slechtst is bij de "
                "hóógste geclaimde edge."),
            "DE_DERDE_REGEL_IS_EEN_UNDER_EN_DAT_IS_DE_SCHEVE_KANT": (
                "St. Mirren - Hibernian, Under 3 @1,71, staat op de kant waarvan §6g meet dat ze "
                "structureel te hoog wordt ingeschat, en dat moet erbij staan in plaats van "
                "weggelaten. Vandaag gemeten over 1717 doorgerekende duels: het GEMIDDELDE aantal "
                "doelpunten klopt (voorspeld 3,031 tegen werkelijk 3,075, z = +1,05) maar de "
                "VERDELING niet — er is massa verschoven van 2 doelpunten (-1,5 pp) naar 4 (+1,0) "
                "en 5 (+1,4), waardoor P(Under 2.5) 2,2 pp en P(Under 3.0) 1,7 pp te hoog staat "
                "bij ÉLK duel, vóór er iets is gekozen. Daar bovenop het selectie-effect: in de "
                "103 duels waarin de routine werkelijk een Under speelde vielen er +0,659 "
                "doelpunt per duel méér dan haar eigen lambda zei, z = +4,04 — de hoogste stand "
                "die deze reeks tot nu toe heeft gehad (op 11 oktober was het +0,68 over 49 "
                "gevallen bij z = +2,91). Op de Over-kant gebeurt dat niet (-0,296 over 60, "
                "z = -1,25). TREK DUS ONGEVEER TWEE PROCENTPUNT VAN DE GENOEMDE KANS AF. En het "
                "onafhankelijke cijfer erbij: Pinnacle zet P(Under 2.75) bij dit duel op 47,4% en "
                "het eigen model op 53,2% — 5,75 pp hoger, dezelfde kant op als de gemeten "
                "scheefstand. De rem die er is, is poort 9, en de oorzaak — keuze (a) van "
                "11 oktober, de vormfout in `score_grid` zelf repareren — staat nog open."),
            "POORT_9_BLOKKEERDE_DE_2_75_EN_LIET_DE_3_0_VAN_DEZELFDE_WEDSTRIJD_DOOR": (
                "Dat ziet eruit als een tegenstrijdigheid en het is er geen; het hoort hier "
                "uitgelegd omdat het anders volgend jaar als een fout wordt gelezen. Poort 9 "
                "(§1h) HIELD vandaag twee selecties tegen, allebei van St. Mirren - Hibernian: "
                "Under 2.75 @2,04 met +8,81 pp tegen de verzwaarde lat van 10,0 pp, plus één "
                "selectie in dezelfde wedstrijd die daarnaast werd geblokkeerd. Ze gaan als "
                "`failed_gate = doelpunten_onder` naar het schaduwlogboek. De GEPUBLICEERDE Under "
                "van dezelfde wedstrijd staat op de 3.0-lijn met +6,43 pp, en die is door poort 9 "
                "HEENGEKOMEN omdat `unders.check` met opzet alleen in de band 8,0-10,0 pp bindt: "
                "een Under die de gewone drempel van §0 al niet haalt wordt door `edge` "
                "tegengehouden en niet hierdoor, want anders loopt de reeks `doelpunten_onder` "
                "vol met kandidaten die nooit een bet konden worden en meet ze niets meer (de "
                "'twee populaties'-fout van §1e). Sinds §5b de drempel van een poort in een "
                "afkapping heeft veranderd, betekent dat echter dat een Under ONDER de 8,0 wél "
                "gepubliceerd kan worden en door geen van beide latten wordt getoetst. DAT IS "
                "GEEN OMISSIE VAN VANDAAG MAAR EEN GEVOLG VAN TWEE REGELS DIE ELKAAR RAKEN, en "
                "het is dezelfde constructie die §1h punt 1 bij `LIGHT` expliciet heeft gekozen "
                "(een LIGHT-Under die de rangorde haalt wordt gepubliceerd, ook zonder zijn lat "
                "van 16,0 te halen). Het hoort als vraag bij de gebruiker en niet bij een run — "
                "zie het actiepunt met owner = besluit in het dagrapport."),
            "POORT_8_HIELD_VIJF_WEDSTRIJDEN_TEGEN_EN_POORT_8_RUW_GEEN_ENKELE": (
                "Poort 8 bindt in de lichte vorm (ondergrens `sides.UNDERDOG_FLOOR` = 0,35, §1e) "
                "en is met `today=DAY` aangeroepen, zodat het venster van 25 t/m 30 september uit "
                "`sides.LAPSED_FROM`/`LAPSED_UNTIL` wordt gelezen in plaats van geraden. Hij "
                "hield vandaag NEGENTIEN selecties tegen, verdeeld over vijf wedstrijden: Milan - "
                "Bologna (Bologna +1.5 @1,46, +7,78 pp), Monza - Napoli (Monza +0.75 @1,93, "
                "+9,12 pp), St. Johnstone - Motherwell (Motherwell wint @2,862, +1,94 pp), "
                "Heart of Midlothian - Rangers (Hearts +0.25 @2,07, +5,92 pp) en Sunderland - "
                "Brentford (Double Chance Sunderland of gelijk @1,872, +5,04 pp). Per wedstrijd "
                "gaat de sterkste op `selection_score` als `underdog`-rij het schaduwlogboek in "
                "(§1e, 15 sep 2026); de rest staat als aantal in `ook_geblokkeerd`. De tweede "
                "schaal, `underdog_ruw`, krijgt vandaag GEEN ENKELE rij: er is geen selectie die "
                "op de ruwe kans alle eerdere poorten haalde en alleen op poort 8 sneuvelde. Dat "
                "is bij een herijking die vrijwel de identiteit is (a=0,9928) te verwachten — de "
                "twee schalen liggen dan bijna op elkaar — en het betekent dat de reeks die de "
                "vraag van 25 september moet beantwoorden vandaag alleen aan de herijkte kant "
                "groeit. Tel die twee nooit bij elkaar op; het zijn twee populaties."),
            "TWEEDE_METHODE_VANGT_234_VAN_DE_299_SELECTIES_EN_DAT_IS_EEN_WAARNEMING": (
                "Over de 33 wedstrijden zijn 299 selecties doorgerekend. De verdeling over de "
                "poorten: `tweede_methode` 234, `edge` 20, `underdog` 19, `context` 9, `odds` 7, "
                "`doelpunten_onder` 2, `robuustheid` 1, en 7 selecties haalden alles. DAT EERSTE "
                "GETAL IS GEEN DETAIL: poort 5 vangt 78% van alles wat er doorgerekend wordt, en "
                "§5 zegt met zoveel woorden dat als er een week lang alles op `tweede_methode` "
                "afvalt, de vraag is of de twee methodes systematisch uiteenlopen — en dat is een "
                "bevinding en geen ruis. Wat er tegenover staat: §1f heeft op 392 afgerekende "
                "gevallen gemeten dat de splitsmethode als KANSBRON vrijwel niets toevoegt "
                "(Brier .23625 bij gewicht 0,80 tegen .23674 voor alleen xG) en dat haar waarde "
                "juist in dit veto zit, dat aantoonbaar geld bespaart (§6d). Noem het getal dus, "
                "lees het over weken en niet vandaag, en verzet er niets op. Twee van de vijf "
                "Serie A-duels en drie van de vijf League Cup-duels vielen hierop af — Milan - "
                "Bologna, Genoa - Juventus, Manchester City - Brighton, Sunderland - Brentford en "
                "Liverpool - Chelsea, allemaal FULL met vijftien tot eenentwintig doorgerekende "
                "selecties."),
            "CONTEXT_HIELD_TWEE_WEDSTRIJDEN_TEGEN_EN_BEIDE_KEREN_OP_BLESSURES": (
                "Poort 7 (§1c) sloot bij twee duels, en in beide gevallen op het "
                "beschikbaarheidsverschil en niet op rust. PARMA - UDINESE: Udinese mist 32% van "
                "de selectiewaarde tegen 1% bij Parma — David Alaba, Oumar Solet en Alessandro "
                "Zanoli, alle drie terug begin november. DUNDEE FC - KILMARNOCK: Dundee mist 34% "
                "tegen 6% — Finlay Robertson (de rest van het seizoen), Bobby Wales en Joe "
                "Westley (eind oktober). De poort houdt alleen tegen en stelt `my_prob` niet bij, "
                "want er is geen enkele meting die zegt hoeveel procentpunt een uitvaller waard "
                "is (§1c, en de poging om er een bijstelling van te maken vond op 147 "
                "wedstrijden niets). De volledige context van alle 33 duels staat in het "
                "`context`-blok, ook van de duels waar de poort openging en van de elf "
                "NONE-duels: dat is wat §1c eist en het is de steekproef van `ctxlog.py`."),
            "TWEE_VERPLAATSTE_WEDSTRIJDEN_EN_BEIDE_IN_EEN_BEKER": (
                "`context.check_venue` zette vandaag TWEE keer `relocated`, en §1c eist dat ze "
                "worden genoemd ook als de poort opengaat. SSV JEDDELOH - HERTHA BSC wordt "
                "gespeeld in het Marschwegstadion in Oldenburg en niet in de HASKAMP-Arena: een "
                "Regionalliga-club die een tweededivisionist ontvangt en daarvoor naar een groter "
                "stadion in de buurt verhuist. JOS WATERGRAAFSMEER - NAC BREDA staat op Sportpark "
                "Goed Genoeg in Amsterdam en niet op Sportpark Drieburg. BEIDE DUELS KOMEN OP "
                "NONE UIT, dus de verplaatsing raakt geen gepubliceerde bet — maar het is precies "
                "de controle die op 23 augustus bij Rennes - PSG is gebouwd, en thuisvoordeel is "
                "de aanname waar het model het zwaarst op leunt. Wat deze controle NIET vangt "
                "blijft hetzelfde: een fixture die van eigenaar is gewisseld, want dat is nieuws "
                "en geen data."),
            "MARKTBALANS_VIER_VAN_DE_VIJF_COMPETITIES_GEKOCHT": (
                "De marktbalans-controle van §1a is gehaald op de INKOOP en niet op de uitkomst, "
                "en ruim: van de vijf competities die vandaag spelen hebben er VIER een sportkey "
                "en alle vier kregen de volledige bulk (h2h + spreads + totals, 3 credits per "
                "competitie) — dus elke gekochte competitie heeft zowel een uitkomstmarkt (1X2, "
                "AH, DNB, DC) als een doelpuntenmarkt (O/U). Plafond `suggest_cap(18633, 4)` = "
                "2326 credits, `split_budget(2326, 4)` = 4 spreads / 4 totals, werkelijk "
                "verbruikt 12 credits voor de bulk plus 14 voor BTTS = 26 van 2326, en er staan "
                "nog 18607 credits van het maandplafond van 20000 open. Alleen de KNVB Beker "
                "heeft geen sportkey bij de bron; dat is een ontbrekende competitie en geen krap "
                "plafond, en het raakt vandaag twee doorgerekende duels. BTTS is gekocht voor 14 "
                "van de 15 duels met een kandidaat-edge (§1a stap 2, de vereniging van beide "
                "schalen sinds 13 sep); het vijftiende was Sparta Rotterdam - Fortuna Sittard, "
                "waar geen sportkey is en de markt dus niet te koop was — dat staat als zodanig "
                "in `markets_checked` en niet als 'geen boek noteerde deze markt'. Wat eruit "
                "kwam: over 299 doorgerekende selecties 100 Over/Under, 78 Asian Handicap, 62 "
                "1X2, 28 BTTS, 22 Draw No Bet en 9 Double Chance, en de drie gepubliceerde "
                "regels zijn een 1X2, een Asian Handicap en een Over/Under — één uit elke hoek, "
                "en dat is de uitkomst en geen quotum."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2, in de enige vorm die bereikbaar is (§3 Stage 5 heeft op 20 sep "
                "gemeten dat geschreven voorspellingen vrijwel niet te halen zijn: Forebet 403, "
                "Pinnacle-artikelen 404, Matchbook 530). Wat er wél is, is de PRIJS VAN PINNACLE "
                "APART: de scherpste bookmaker van de markt, en zijn de-vigde 1X2 is het beste "
                "publieke expertoordeel dat beschikbaar is. Over 20 duels met zowel een "
                "Pinnacle-1X2 als een eigen 1X2: gemiddelde absolute afstand 4,01 procentpunt, "
                "gemiddelde Pinnacle-marge 4,18% (tegen 6 à 10% bij de rest). Geen systematische "
                "kant, maar twee uitschieters die de moeite van het noemen waard zijn: bij "
                "Hannover 96 - Kaiserslautern staat het eigen model 14,2 pp BOVEN Pinnacle op de "
                "thuiszege (55,1% tegen 40,9%) en dat is precies het duel dat de tweede regel van "
                "de dag levert, en bij Paderborn - VfB Stuttgart 8,6 pp boven Pinnacle op de "
                "thuiszege. Lees die eerste als een waarschuwing en niet als een bevestiging: "
                "§1g meet dat de bookmaker scherper schat dan het model (Brier 0,2449 tegen "
                "0,2657 over het hele logboek), dus de grootste afstand tot Pinnacle is eerder "
                "de grootste modelfout dan de grootste vondst. Op de doelpuntenkant: over 20 "
                "(duel, lijn)-paren staat het eigen model gemiddeld +1,65 pp boven Pinnacle op de "
                "Under-kant, 11 van de 20 keer erboven — dezelfde richting als de gemeten "
                "vormfout van §6g. HARDE GRENS: niets hiervan gaat in `my_prob` of in "
                "`prob_sources` (§2); het staat in de lezing en in de vergelijking."),
            "UNDERSTAT_DEKT_TWEE_VAN_DE_33": (
                "Understat dekt vijf competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) en "
                "daarvan speelt vandaag alleen Serie A. Van de vijf Serie A-duels hebben TWEE een "
                "Understat-blok (Milan - Bologna en Genoa - Juventus); bij de andere drie staat "
                "minstens één ploeg niet in de Understat-tabel van vorig seizoen (Venezia en "
                "Monza zijn promovendus, Parma en Udinese ontbreken op naam). Het blok gaat mee "
                "in het kalibratieblok van §6e als `p_xg_understat`, zodat over enkele weken met "
                "cijfers te zeggen is of het ene xG-model beter voorspelt dan het andere. LET OP "
                "HET NIVEAUVERSCHIL: Understat ligt structureel ~0,13 xG per ploeg per duel hoger "
                "dan Fotmob, en dat valt pas weg als je op het EIGEN competitiegemiddelde van die "
                "bron normaliseert (§4). De League Cup, de DFB Pokal, de KNVB Beker en de "
                "Scottish Premiership hebben geen Understat-dekking; daar is Fotmob de enige "
                "xG-bron, en dat is de reden dat §3 een uitvallende Fotmob vooraan in de "
                "notificatie wil hebben."),
            "VROEG_SEIZOEN_EN_NIVEAU": (
                "`early_season_uplift` geeft vandaag factor 1,1146, gepoold over 44 speeldagen "
                "uit 5 competities. LET OP DAT DIE FACTOR HOGER IS DAN DE 1,0606 VAN EERDER DEZE "
                "MAAND: de pool is competitie-overstijgend en beweegt mee met wie erin zit, en "
                "vandaag zitten er drie bekerbases in (Premier League, Bundesliga, Eredivisie) "
                "naast Serie A en de Scottish Premiership. §3 Stage 5 waarschuwt daar "
                "uitdrukkelijk voor. Alle ZEVEN competitiebases lopen de route `vorig+uplift` "
                "(Serie A, Scottish Premiership, League Cup/Premier League, 2. Bundesliga, DFB "
                "Pokal/Bundesliga, KNVB Beker/Eredivisie en Eerste Divisie): elk lopend seizoen "
                "staat op 7 tot 10 speeldagen van een seizoen van 33 tot 38, dus ruim onder de "
                "helft van `SEASON_MATURE_SHARE`. De niveaus per competitie staan in `niveau`, "
                "met de route en de reden erbij. En de meting naast de markt (controleren, niet "
                "fitten — §2): de gemiddelde afstand van het eigen 1X2 tot het Pinnacle-oordeel "
                "is 4,01 pp over 20 duels, zonder systematische kant."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn — "
                "de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert de "
                "daglijst, BetExplorer de fixturepagina per competitie. NEGENTIEN van de "
                "negentien competities met een slug zijn het eens, inclusief de dertien die "
                "vandaag GEEN WEDSTRIJD hebben: 33 duels bij Fotmob, 33 bij BetExplorer, nul "
                "afwijkingen en geen enkele bron die faalde (`ra_oct28_bevestiging.py`). DE DRIE "
                "BEKERS MET EEN RONDE ZIJN ÓÓK DOOR TWEE BRONNEN BEVESTIGD: BetExplorer geeft 5, "
                "8 en 9 duels in het venster en de Fotmob-daglijst geeft dezelfde 5, 8 en 9. De "
                "twee bekers zonder ronde (FA Cup, Coppa Italia) staan alleen op BetExplorer, met "
                "als eerstvolgende ronde 6 november en 1 december. LET OP DE TIJDZONE: "
                "BetExplorer labelt in UK-tijd, en dat is sinds de wintertijd GMT tegen CET in "
                "Nederland — nog steeds precies één uur verschil, dus het venster [28.10. 08:00 "
                "NL, 29.10. 08:00 NL) is in UK-tijd [28.10. 07:00, 29.10. 07:00)."),
            "INZETVENSTER": (
                "`runwindow.matches_for_run` met het venster [28.10. 08:00 NL, 29.10. 08:00 NL), "
                "en voor de drie bekers dezelfde band met de hand in `ra_oct28_cupmatches.py`. "
                "Alle 33 duels stonden op de daglijst van 28 oktober (`source_day` = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 33 zijn `playable`: de "
                "vroegste aftrap is 18:00 NL (vier DFB Pokal-duels) en de laatste 21:00 NL "
                "(Liverpool - Chelsea en Excelsior Maassluis - SC Heerenveen). Er is dus geen "
                "enkel duel dat al was afgetrapt voordat de gebruiker kon inzetten, en geen "
                "carry-over-band. `runwindow` rekent met `zoneinfo`, dus het venster is in échte "
                "NL-tijd gemeten: nu de wintertijd in is, komt een aftrap van 19:45 UTC op 20:45 "
                "NL uit (CET) en niet op 21:45 (CEST). Dat is de reparatie van 25 oktober; "
                "`ra_oct28_analyze.py` en dit bestand gebruiken allebei "
                "ZoneInfo('Europe/Amsterdam') en `odds_captured_at` staat op +01:00."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn DRIE publiceerbare selecties en drie
        # plekken beschikbaar (MAX_SHORTLIST = 3, maandag), dus er valt er geen enkele af en
        # deze lus legt vandaag niets vast. Hij blijft staan omdat hij op de eerste dag dat de
        # lijstlengte wél bindt het verschil is tussen een gemeten reeks en een stille
        # weglating. Deze lus legt zo'n
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
        s3 = json.load(open("tmp-run/ra_oct28_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers zonder ronde vandaag; de drie MET een ronde staan al in s3["fixtures"]
        # omdat `ra_oct28_merge_cups.py` ze daar heeft neergezet (zie de kop).
        cups = json.load(open("tmp-run/ra_oct28_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct28_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct28_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct28_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

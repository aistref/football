"""Run A 22 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct21_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWEE van de eenentwintig competities uit de runlijst speelden, met 36 duels in het
inzetvenster: een volle Europa League- en Conference League-avond, 18 duels elk.

ALLE 36 duels zijn kruis-grens en dus hoogstens LIGHT; dertien komen op NONE uit omdat er voor
hun land geen gemeten Europese competitiefactor is of de omrekening buiten het gemeten bereik
valt. VIJF selecties haalden alle negen poorten én hun lat van 16,0 pp, en er worden er TWEE
gepubliceerd: MAX_LIGHT_IN_SHORTLIST = 2 bindt, want er is geen enkel FULL-duel. De drie die
afvallen gaan als `lijstlengte` het schaduwlogboek in (§5b). Zie
TWEE_REGELS_EN_MAX_LIGHT_IN_SHORTLIST_BINDT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-22"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-22T04:11:38+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok


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
                         "1463 doorgerekende duels: P(Under 3.0) voorspeld 63,9% tegen werkelijk "
                         "61,9%), en dat de gespeelde Under-kant daar bovenop een selectie-effect "
                         "heeft van +0,592 doelpunt per duel over 87 gevallen (z = +3,34), terwijl "
                         "de Over-kant op -0,197 staat (z = -0,75). Poort 9 (§1h) bindt hier NIET — op LIGHT geldt hij per "
                         "besluit van 12 okt 2026 niet, en op FULL bindt hij alleen in de band "
                         "8-10 pp. Lees deze regel dus met die scheefstand erbij. "
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
    for run, pad in (("A", "tmp-run/ra_oct22_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.015365, "
                "b=0.009940 over 5331 afgerekende gevallen, fitted_through 2026-10-21, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle "
                "gedraaid vóórdat de definitieve analyse liep (33 waarnemingen afgewikkeld, "
                "5538 van 5562 compleet, 24 nog open); de eerste doorloop van de analyse werkte "
                "nog met de fit van fitted_through 2026-10-20 en is daarna in zijn geheel "
                "overgedaan, zodat er geen regel is gepubliceerd op een verouderde correctie. "
                "De fit VERHOOGT een kans over vrijwel de hele speelbare band (+0,2 pp op 50%, "
                "+0,5 pp op 70%) en verlaagt alleen onder ~35%; het ruwe model zei gemiddeld "
                "33,333% en het gebeurde 33,333%. Bij BEIDE gepubliceerde regels staat de "
                "herijkte edge daardoor boven de ruwe, en bij beide staat `bet_beide` op TRUE: "
                "ze halen hun lat van 16,0 pp op BEIDE schalen."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de eenentwintig competities uit de runlijst speelden, en samen "
                "leveren ze 36 duels in het inzetvenster: de UEFA EUROPA LEAGUE met 18 en de "
                "UEFA CONFERENCE LEAGUE met 18 (beide speelronde 3 van de competitiefase). Dat "
                "is de grootste dag die Run A tot nu toe heeft gehad en het is een dag met een "
                "uitzonderlijk profiel: ALLE 36 duels zijn kruis-grens, dus er is deze run geen "
                "enkel binnenlands duel en geen enkel FULL-duel. De Champions League speelde "
                "gisteren en eergisteren en is vandaag GEEN WEDSTRIJD; de volgende ronde is "
                "3 november. De overige achttien competities hebben eveneens GEEN WEDSTRIJD, en "
                "dat is geen storing (§3 Stage 2): de binnenlandse competities hervatten op "
                "24 oktober (Serie A, Primeira Liga, Belgian Pro League, Championship, "
                "Ekstraklasa, Super Lig, Scottish Premiership), 25 oktober (Danish Superliga) "
                "of 1 november (Premier League, La Liga, Bundesliga, Ligue 1, Eredivisie). Alle "
                "zestien competities met een fotmob_id zijn door een tweede bron bevestigd — "
                "zie RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven — dat kostte Run A op 6 oktober vijf duels. "
                "Alle vijf zijn daarom langs BetExplorer gegaan (tmp-run/ra_oct22_cups.py) en "
                "alle vijf leveren teamparen op de fixturepagina (40, 8, 8, 26 en 16), dus geen "
                "van de drie faalmodi van die bron is opgetreden. NUL ervan valt in het "
                "inzetvenster: League Cup op 27.10. 20:45, KNVB Beker op 27.10. 18:45, "
                "DFB Pokal op 27.10. 18:00, FA Cup op 07.11. 16:00 en Coppa Italia op "
                "01.12. 21:00."),
            "ALLE_36_DUELS_ZIJN_KRUIS_GRENS": (
                "Elke wedstrijd van vandaag zet ploegen uit verschillende LANDEN tegenover "
                "elkaar, en dan staan hun sterktes op onvergelijkbare schalen — elke ploeg is "
                "genormaliseerd op het gemiddelde van zijn eigen competitie (§4, Kruis-grens). "
                "Alle 36 lopen daarom langs scripts/interleague.py, dat beide ploegen naar de "
                "Europese referentieschaal omrekent. DRIEËNTWINTIG duels komen daar doorheen en "
                "zijn LIGHT — nooit FULL, want de omrekening haalt de systematische fout eruit "
                "en niet de onzekerheid. DERTIEN duels komen op NONE uit en zijn NIET "
                "doorgerekend (§2), in twee soorten: (a) GEEN GEMETEN COMPETITIEFACTOR voor het "
                "land, omdat er minder dan interleague.MIN_MATCHES = 40 Europese duels van zijn "
                "— Armenië, Slovenië, Kazachstan, Litouwen, Georgië, Andorra, Letland, Albanië, "
                "Bosnië, Finland en Gibraltar; (b) BUITEN HET GEMETEN BEREIK van de omgerekende "
                "aanval (0,585–2,432) of verdediging (0,388–1,446), de Coventry-val waarvoor "
                "`in_range` een poort is en geen aantekening — OFI Crete (verdediging 1,685), "
                "CSKA Sofia (aanval 0,581) en Mjällby (aanval 0,550 én verdediging 1,468). Eén "
                "geval staat los: Torreense speelt in Liga Portugal 2 en niet in de hoogste "
                "Portugese divisie waarop de factor is gemeten, dus daar is geen schaal om op "
                "om te rekenen. Dat 36% van de kalender op NONE uitkomt is bij een Europese "
                "avond met dit deelnemersveld het verwachte beeld en geen storing: juist de "
                "kleine competities zijn de competities waarvan het minst gemeten is."),
            "ER_IS_VANDAAG_GEEN_ENKEL_FULL_DUEL": (
                "Alle 23 doorgerekende duels staan op LIGHT en dus op de lat van 16,0 pp (§0), "
                "omdat ze alle 23 kruis-grens en dus omgerekend zijn. GEVOLG VOOR POORT 9: die "
                "bindt alleen op FULL (§1h, besluit van 12 oktober dat LIGHT erbuiten blijft), "
                "dus hij heeft deze run geen enkele selectie kunnen toetsen — ook niet de twee "
                "Unders die de rangorde haalden. Dat is geen omissie maar die keuze. Zie "
                "EEN_VAN_DE_TWEE_REGELS_IS_EEN_UNDER."),
            "DE_CAP_BINDT_NIET_MAAR_SCHEELT_WEINIG": (
                "36 duels op een donderdagcap van 40 (ranking.max_deep_analyses, ma-do), dus er "
                "is NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel — maar het "
                "scheelt vier duels, en dat is de krapste marge die Run A tot nu toe heeft "
                "gehad. Was dit een vrijdag geweest dan had de cap op 55 gestaan en was het "
                "verschil groter; viel er één extra Europees duel in het venster, dan was de "
                "marge drie. De datarijkdom liep van 4,33 tot 6,17 over de 23 doorgerekende "
                "duels; omdat er niets afviel is er geen 'laagste die het haalde' en geen "
                "'hoogste die afviel' te noemen (§3 Stage 4). De context is voor alle 36 duels "
                "opgehaald, zoals §1c eist — ook voor de dertien op NONE — en alle 36 hebben "
                "een contextblok zonder fout."),
            "TWEE_REGELS_EN_MAX_LIGHT_IN_SHORTLIST_BINDT": (
                "MAX_SHORTLIST = 3 (donderdag) en er staan TWEE regels op de lijst. De derde "
                "plek blijft leeg en dat is GEEN gebrek aan kandidaten maar "
                "MAX_LIGHT_IN_SHORTLIST = 2 (§0): omdat er vandaag geen enkel FULL-duel is, "
                "zijn alle kandidaten LIGHT en mogen er maximaal twee in de lijst. Dat is "
                "vandaag een DURE grens, en dat hoort er eerlijk bij: VIJF selecties hadden "
                "alle negen poorten open én stonden bóven hun eigen lat van 16,0 pp, waar er "
                "twee passen. De drie die afvallen staan als `gekwalificeerd_niet_gepubliceerd` "
                "in dit bestand en als `failed_gate = lijstlengte` in het schaduwlogboek (§5b, "
                "26 sep 2026): Union St.Gilloise – Hapoel Beer Sheva (Under 3.5 @1.67, "
                "+16,57 pp, rang 3), Sturm Graz – Marseille (Marseille wint @2.0584 na "
                "commissie, +17,32 pp, rang 4) en Celtic – Celta Vigo (Celta Vigo wint @2.5876 "
                "na commissie, +16,66 pp, rang 5). Let op de volgorde: de rangorde loopt op "
                "selection_score (edge × kans × datafactor) en niet op edge, dus Sturm Graz "
                "staat met een HOGERE edge lager dan Union SG met een hogere kans. Dit is de "
                "eerste dag waarop de lijstlengte op deze schaal bindt, en het is precies de "
                "situatie die §5b voorzag. Lees de lijst niet als een gevonden voordeel: §1g "
                "heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op de herijkte "
                "edge bestaat die geld oplevert."),
            "EEN_VAN_DE_TWEE_REGELS_IS_EEN_UNDER": (
                "Omonia Nicosia – Benfica, Under 3 @1.93, staat op precies de markt-en-kant "
                "waarvan §6g de scheefstand meet: een vormfout in het scoregrid zet P(Under) "
                "bij élk duel 1,6 tot 2,4 procentpunt te hoog, en daar bovenop zit een "
                "selectie-effect in de duels waar werkelijk een Under is gespeeld. Poort 9 "
                "(§1h) is juist voor deze kant gebouwd en bindt hier NIET, omdat het duel op "
                "LIGHT staat en LIGHT per besluit van 12 oktober buiten de poort blijft. Er "
                "staat op deze regel dus geen rem. Dat is geen fout in de uitvoering maar het "
                "gat dat §1h zelf benoemt, en de vraag hoort NIET opnieuw aan de gebruiker "
                "gesteld — hij heeft op 12 oktober besloten dat LIGHT erbuiten blijft tot de "
                "reeks `doelpunten_onder` iets zegt. Wat een run wél moet doen is het noemen, "
                "en dat gebeurt hier en in het dagrapport. De ANDERE regel (Braga – Gent, "
                "Over 2.5) staat op de kant die volgens §6g juist meebetaalt aan diezelfde "
                "vormfout, en de twee staan dus niet op dezelfde voet. De echte oplossing "
                "blijft keuze (a) van 11 oktober: de vormfout zelf repareren."),
            "POORT_9_HEEFT_VANDAAG_NIETS_KUNNEN_TOETSEN": (
                "Tiende bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke selectie "
                "aangeroepen met today=2026-10-22. poort9_geblokkeerd is voor alle duels leeg, "
                "en vandaag is dat niet omdat er geen Unders waren — er zijn er 55 doorgerekend "
                "— maar omdat er GEEN ENKEL FULL-duel is en de poort alleen op FULL bindt. De "
                "reeks `doelpunten_onder` groeit vandaag dus niet. Deze run verandert NIETS aan "
                "de poort — §1h legt vast dat een run dat nooit op eigen initiatief doet."),
            "POORT_8_HOUDT_ZEVEN_DUELS_TEGEN_EN_EEN_ERVAN_VOERT_DE_RUWE_LIJST_AAN": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), "
                "aangeroepen met today=2026-10-22 zodat het vervallen venster van 25 t/m 30 "
                "september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van "
                "geraden. ZEVEN duels hebben een poort-8-rij op de herijkte schaal: Beşiktaş – "
                "Crystal Palace (Crystal Palace +0.25 @2.00, +19,54 pp, score 6,80), "
                "Jagiellonia Białystok – Anderlecht (Jagiellonia +0.25 @1.90, +18,29 pp), "
                "Trabzonspor – Heart of Midlothian (Hearts +1.75 @1.83, +14,64 pp), Thun – "
                "Hajduk Split (Thun +0.25 @1.79, +13,61 pp), Lillestrøm – Real Sociedad "
                "(Lillestrøm +1.5 @1.64, +12,28 pp), Jablonec – Brighton (Jablonec +1.75 "
                "@1.96, +12,17 pp) en Lech Poznań – Sunderland (Lech +0.75 @1.91, +4,26 pp). "
                "poort8_ruw is leeg, want geen enkele kandidaat sneuvelde ALLEEN op de ruwe "
                "schaal — §1e eist dat dezelfde selectie nooit in beide reeksen belandt. EN LET "
                "OP WAT DAT BETEKENT VOOR DE RUWE LIJST: de Crystal Palace-handicap staat derde "
                "op de ruwe top drie, dus zonder deze poort had de routine vandaag op een "
                "underdog-handicap gezet in een duel waar het eigen model 16,2 procentpunt "
                "ONDER het Pinnacle-oordeel op de thuiszege staat. De twee reeksen blijven twee "
                "populaties die nooit worden opgeteld."),
            "POORT_7_HOUDT_VIJFTIEN_SELECTIES_TEGEN": (
                "context.check sloot bij 15 van de 326 doorgerekende selecties de poort, en bij "
                "TWEE duels was dat de hoogst scorende selectie: Getafe – Lugano (Getafe mist "
                "35% van de selectiewaarde tegen 4% bij Lugano — Orel Mangala, Zaid Abner "
                "Romero en Christantus Uche) en FC Midtjylland – St.Truiden (28% tegen 8% — "
                "Victor Bak, Elías Ólafsson, Magnus Jensen). In beide gevallen kwam er daarna "
                "een andere selectie bovendrijven die op de edge sneuvelde, dus geen van beide "
                "duels levert een regel op. De poort houdt alleen tegen en stelt my_prob niet "
                "bij; bij side = None (Over/Under, BTTS, gelijkspel) staat hij per ontwerp "
                "open. BEIDE gepubliceerde regels zijn een totaal en geen kant, dus voor beide "
                "stond de poort open."),
            "VIJF_VERPLAATSTE_WEDSTRIJDEN": (
                "context.check_venue is voor alle 36 duels gedraaid en zet bij VIJF duels "
                "relocated = True — veruit het hoogste aantal dat deze routine heeft gezien, en "
                "dat is het normale patroon voor een Europese avond: het eigen stadion van een "
                "kleine club haalt de UEFA-eisen niet. Ararat Armenia – AZ Alkmaar (Vazgen "
                "Sargsyan-stadion in Jerevan in plaats van Kotaik Stadium), UNION ST.GILLOISE – "
                "HAPOEL BEER SHEVA (Merkur Spiel-Arena in DÜSSELDORF in plaats van Stade Joseph "
                "Mariën), Inter Club d'Escaldes – Universitatea Craiova (Estadi de la FAF "
                "d'Encamp), Pafos FC – Riga FC (Alphamega Stadium in Kolossi) en AGF – Egnatia "
                "(Cepheus Park Randers in plaats van Ceres Park). De tweede is de belangrijkste "
                "en hij hoort genoemd ook al gaat de poort open (§1c): Union Saint-Gilloise "
                "speelt zijn 'thuiswedstrijd' 350 kilometer verderop in Duitsland, en "
                "thuisvoordeel is de aanname waar het model het zwaarst op leunt. Dat duel "
                "leverde de derde selectie op de dagranglijst op (Under 3.5 @1.67) en is op "
                "lijstlengte afgevallen; hád het de lijst gehaald, dan was dit voorbehoud de "
                "eerste zin van zijn onderbouwing geweest. De overige 31 duels staan op "
                "relocated = False."),
            "OPSTELLINGEN": (
                "lineup_type: 32 duels op 'lastStarting11' en 4 op 'predicted'. Bevestigde "
                "elftallen (lineupType 'confirmed') zijn er om 04:00 NL — het moment van de "
                "contextophaling — bij geen enkel duel; voor avondwedstrijden om 16:30, 18:45 "
                "en 21:00 NL is dat te verwachten. Dat zit in de datarijkdom (§3 Stage 4) en "
                "niet in my_prob."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [22.10. 08:00 NL, 23.10. 08:00 NL). "
                "Alle 36 duels stonden op de daglijst van 22 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 36 zijn playable: de "
                "vroegste aftrap is 16:30 NL (Kairat Almaty – Panathinaikos) en de laatste "
                "21:00 NL. Er is dus geen enkel duel dat al was afgetrapt voordat de gebruiker "
                "kon inzetten, en geen carry-over-band."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob "
                "levert de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van "
                "de zestien competities met een fotmob_id zijn het eens, inclusief de veertien "
                "die vandaag GEEN WEDSTRIJD hebben: 36 duels bij Fotmob, 36 bij BetExplorer, "
                "nul afwijkingen en geen enkele bron die faalde "
                "(tmp-run/ra_oct22_bevestiging.py). Beide spelende competities zijn op het "
                "aantal bevestigd: Europa League 18 en 18, Conference League 18 en 18."),
            "BEIDE_SPELENDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "UEFA Europa League (soccer_uefa_europa_league) en UEFA Conference League "
                "(soccer_uefa_europa_conference_league) hebben beide een sportkey bij The Odds "
                "API, dus er is deze run GEEN enkel duel waar BetExplorer de enige 1X2-bron is "
                "en de edge systematisch te laag uitvalt (§1a). LET OP de beurzen: van de vijf "
                "selecties die hun lat haalden staan er DRIE op een beurs (Betfair of "
                "Matchbook) en is er dus met oddsapi.net_price gerekend — Sturm Graz – "
                "Marseille (Betfair 2.08 bruto / 2.0584 na 2% commissie), Celtic – Celta Vigo "
                "(Matchbook 2.62 / 2.5876) en Braga – Gent (Matchbook 2.24 / 2.2152). Van de "
                "twee GEPUBLICEERDE regels is dat er één: Braga – Gent. De andere, Omonia "
                "Nicosia – Benfica Under 3 @1.93, komt van Pinnacle en is dus een gewone "
                "bookmakerprijs zonder commissie."),
            "MARKTBALANS": (
                "Plafond suggest_cap(19038, 10) = 950 credits. split_budget(950, 2) geeft 2 "
                "spreads / 2 totals, en omdat 3 x 2 = 6 onder 950 blijft is de volle "
                "BULK-aanroep gedaan: h2h + spreads + totals voor beide inkoopbare "
                "competities, dus vijf van de zes markten in één keer. Daarna BTTS voor 19 van "
                "de 20 duels met een kandidaat-edge (§1a stap 2, de vereniging van beide "
                "schalen); het twintigste, FK Crvena Zvezda – FC København, stond niet in de "
                "spreads-respons van The Odds API en kon dus niet op event-id worden "
                "opgevraagd. Totaal 25 van 950 credits (6 bulk + 19 BTTS), 19013 over. De "
                "marktbalans-controle slaagt: beide inkoopbare competities hebben zowel een "
                "uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U). Doorgerekend "
                "over de 23 duels met data: 110 Over/Under, 82 Asian Handicap, 64 1X2, 38 BTTS, "
                "22 Draw No Bet en 10 Double Chance, samen 326 selecties — de breedste "
                "marktdekking van een Run A tot nu toe. BEIDE gepubliceerde regels komen uit de "
                "doelpuntenmarkt, en dat is geen inkoopeffect: alle zes markten deden mee."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Voor 20 van de 36 duels gevonden (de overige zestien "
                "staan op NONE of hebben geen volledig Pinnacle-1X2), gemiddelde "
                "Pinnacle-marge 4,33% tegen 6 à 10% bij de rest. Gemiddelde absolute afstand "
                "tussen het eigen model en het Pinnacle-oordeel: 6,44 procentpunt — ruimer dan "
                "de 4,77 van gisteren, en dat is te verwachten op een dag waarop élk duel via "
                "een omrekening loopt en er geen enkel binnenlands ijkpunt is. De grootste "
                "afwijkingen: Celtic – Celta Vigo +20,04 pp op de UITzege (eigen model 57,6%, "
                "Pinnacle 37,6%) — en dat is precies de derde van de drie selecties die op "
                "lijstlengte afvielen, dus de duurste niet-gepubliceerde regel is óók de regel "
                "waar het model het verst van het scherpste boek af staat; daarna Jagiellonia – "
                "Anderlecht +17,23 pp en Trabzonspor – Hearts -16,21 pp. Bij Braga – Gent staat "
                "het model +14,60 pp boven Pinnacle op de thuiszege; de gepubliceerde regel "
                "daar is een TOTAAL en geen kant, maar die afstand hoort erbij genoemd. Voor "
                "Omonia Nicosia – Benfica geeft Pinnacle geen volledig 1X2, dus daar is geen "
                "vergelijking te maken — de koers van de bet zelf komt wél van Pinnacle. HARDE "
                "GRENS §2/§4: dit getal zit NIET in my_prob en NIET in prob_sources."),
            "UNDERSTAT_DEKT_GEEN_ENKEL_DUEL": (
                "Geen van de vijf Understat-competities (Premier League, La Liga, Bundesliga, "
                "Serie A, Ligue 1) speelt vandaag — het zijn twee Europese toernooien — dus er "
                "is deze run geen tweede, onafhankelijk xG-model naast Fotmob. De kansinput "
                "komt voor alle 23 doorgerekende duels van één bron, in twee doorsnedes "
                "(team-xG en de thuis/uit-splits), plus de omrekening van interleague daarop. "
                "Dat is genoeg voor §2 (de twee methodes zijn twee methodes, geen twee bronnen) "
                "maar het is minder redundantie dan op een binnenlandse speeldag, en het hoort "
                "genoemd in plaats van stilzwijgend overgeslagen."),
            "VROEG_SEIZOEN_EN_NIVEAU": (
                "early_season_uplift geeft factor 1.0383, gepoold 1.1405 over 3 speeldagen in "
                "TWEE competities (Europa League 2 speeldagen, Conference League 1). Geen "
                "enkele competitie is uit de pool gelaten (uplift_observations gaf nul "
                "overgeslagen), dus er is geen weggelaten waarneming te melden. LET OP hoe dun "
                "die pool is: DRIE speeldagen is het kleinste aantal waarop deze correctie ooit "
                "is bepaald, en de gepoolde verhouding van 1,1405 wordt door de regularisatie "
                "naar 1,0383 teruggetrokken juist omdat er zo weinig onder zit. Het maakt voor "
                "deze run echter vrijwel niets uit: `niveau` is LEEG, want league_level wordt "
                "alleen aangeroepen voor binnenlandse duels en die zijn er niet. Alle 23 "
                "doorgerekende duels krijgen hun doelpuntenniveau van de Europese "
                "referentieschaal van scripts/interleague.py (thuis 1,572 / uit 1,179), die op "
                "2111 kruis-grensduels is gefit en niet op de uplift. De uplift-factor raakt "
                "vandaag dus alleen de Understat-tak, en die is leeg."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn drie publiceerbare selecties en drie
        # plekken gebruikt. Deze lus blijft staan omdat ze de enige plek is waar een
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
        s3 = json.load(open("tmp-run/ra_oct22_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct22_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct22_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct22_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct22_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

"""Run A 20 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct19_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWEE van de eenentwintig competities uit de runlijst speelden, met 10 duels in het
inzetvenster: een Champions League-avond (9 duels) plus één ingehaalde Championship-wedstrijd.

TWEE regels gepubliceerd in plaats van de drie die een dinsdag toestaat, en dat is
MAX_LIGHT_IN_SHORTLIST = 2 die bindt: er is vandaag geen enkel FULL-duel. ÉÉN van de twee haalt
zijn eigen lat. Zie TWEE_REGELS_EN_MAX_LIGHT_IN_SHORTLIST_BINDT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-20"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-20T04:09:12+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok


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
                      + ("ONDER-KANT: §6g meet dat P(Under) bij élk duel 1,6 tot 2,4 procentpunt "
                         "te hoog staat door een vormfout in score_grid, en dat de gespeelde "
                         "Under-kant daar bovenop een selectie-effect van +0,68 doelpunt per duel "
                         "heeft (z = +2,91). Over het logboek: Under 76 picks op -16,5%, Over 62 "
                         "picks op +10,6%. Poort 9 (§1h) bindt hier NIET — op LIGHT geldt hij per "
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
    for run, pad in (("A", "tmp-run/ra_oct20_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.020169, "
                "b=0.013049 over 5220 afgerekende gevallen, fitted_through 2026-10-19, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle vóór "
                "de analyse gedraaid (48 waarnemingen afgewikkeld, 5427 van 5451 compleet, 24 "
                "nog open). De fit VERHOOGT een kans over vrijwel de hele speelbare band "
                "(+0,3 pp op 50%, +0,6 pp op 70%) en verlaagt alleen onder ~35%; het ruwe model "
                "zei gemiddeld 33,333% en het gebeurde 33,333%. Bij BEIDE gepubliceerde regels "
                "staat de herijkte edge daardoor boven de ruwe. Bij ÉÉN van de twee staat "
                "`bet_beide` op TRUE (Paris Saint-Germain – Barcelona); bij de andere op FALSE, "
                "want die haalt haar lat op geen van beide schalen en is op rangorde "
                "gepubliceerd (§5b)."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de eenentwintig competities uit de runlijst speelden, met 10 duels "
                "samen in het inzetvenster: de UEFA CHAMPIONS LEAGUE met 9 duels (speelronde 3) "
                "en de Championship met 1 (Wolverhampton Wanderers – Portsmouth, een "
                "ingehaalde dinsdagavondwedstrijd). Dat is een CHAMPIONS LEAGUE-AVOND, en "
                "daarmee een dag met een heel ander profiel dan de gewone runlijstdag: negen "
                "van de tien duels zijn kruis-grens en dus per definitie LIGHT. De overige "
                "negentien competities hebben GEEN WEDSTRIJD, en dat is geen storing (§3 "
                "Stage 2): de vijf grote binnenlandse competities spelen hun volgende ronde op "
                "23 oktober (Serie A, Primeira Liga, Belgian Pro League, Danish Superliga, "
                "Ekstraklasa, Championship) of op 1 november (Premier League, La Liga, "
                "Bundesliga, Ligue 1, Eredivisie), de Scottish Premiership op 24 oktober, en "
                "de Europa League en Conference League op 22 oktober. Alle zestien competities "
                "met een fotmob_id zijn door een tweede bron bevestigd — zie "
                "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven — dat kostte Run A op 6 oktober vijf duels. "
                "Alle vijf zijn daarom langs BetExplorer gegaan (tmp-run/ra_oct20_cups.py) en "
                "alle vijf leveren teamparen op de fixturepagina (29, 8, 8, 26 en 16), dus geen "
                "van de drie faalmodi van die bron is opgetreden. NUL ervan valt in het "
                "inzetvenster: de FA Cup staat op 07.11. 16:00, League Cup op 27.10. 20:45, "
                "KNVB Beker op 27.10. 18:45, DFB Pokal op 27.10. 18:00 en Coppa Italia op "
                "01.12. 21:00. De elf FA Cup-replays die gisteren op 'Tomorrow 19:45' stonden "
                "zijn inmiddels gespeeld en staan niet meer op de fixturepagina; de eerste "
                "nieuwe ronde is 7 november."),
            "EEN_DEGRADANT_EN_NEGEN_KRUIS_GRENSDUELS": (
                "Het ENIGE binnenlandse duel heeft een omgerekende ploeg, en die gaat OMLAAG: "
                "Wolverhampton Wanderers staat niet in de Championship-stand van 2025/2026 "
                "omdat de ploeg uit de Premier League is gedegradeerd, en loopt dus langs "
                "promotion.convert_relegated in plaats van langs TIER2. Let op wat §4 daarover "
                "zegt: de richting OMLAAG is nog NIET af — MEASURED_TIER2_GAP meet uitsluitend "
                "omhoog, en voor het paar Premier League -> Championship komt de factor van "
                "football-data.co.uk (E0/E1) in de omgekeerde richting. Lees de stand per "
                "selectie uit GapResult.direction, zoals §4 sinds 9 oktober eist; die tekst "
                "staat per wedstrijd in het veld `promovendi`. De negen Champions "
                "League-duels gaan langs scripts/interleague.py (§4, Kruis-grens): ploegen uit "
                "verschillende LANDEN staan op onvergelijkbare schalen en worden naar de "
                "Europese referentieschaal omgerekend. ACHT van de negen vallen binnen het "
                "gemeten bereik en zijn LIGHT; Roma – Slovan Bratislava niet, want voor SVK is "
                "geen Europese competitiefactor gemeten (minder dan 40 Europese duels in de "
                "meting). Dat duel is daarom data_tier NONE en is NIET doorgerekend (§2)."),
            "ER_IS_VANDAAG_GEEN_ENKEL_FULL_DUEL": (
                "Alle negen doorgerekende duels staan op LIGHT en dus op de lat van 16,0 pp "
                "(§0) — negen omdat ze kruis-grens of omgerekend zijn, en in beide gevallen "
                "haalt de omrekening de systematische fout eruit en niet de onzekerheid. "
                "GEVOLG VOOR POORT 9: die bindt alleen op FULL (§1h, besluit van 12 oktober dat "
                "LIGHT erbuiten blijft), dus hij heeft deze run geen enkele selectie kunnen "
                "toetsen — ook niet de twee Unders die zijn gepubliceerd. Dat is geen omissie "
                "maar die keuze, en het is precies het geval dat §1h op 12 oktober beschrijft "
                "(Atalanta – Venezia). Zie TWEE_REGELS_EN_BEIDE_ZIJN_EEN_UNDER."),
            "DE_CAP_BINDT_NIET": (
                "10 duels op een dinsdagcap van 40 (ranking.max_deep_analyses, ma-do), dus er "
                "is NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel. De "
                "datarijkdom liep van 5,0 (Wolverhampton Wanderers – Portsmouth) tot 7,67 "
                "(Liverpool – Villarreal) over de 10 duels; omdat er niets afviel is er geen "
                "'laagste die het haalde' en geen 'hoogste die afviel' te noemen (§3 Stage 4). "
                "De context is voor alle 10 duels opgehaald, zoals §1c eist — ook voor het duel "
                "op NONE — en alle 10 hebben een contextblok zonder fout."),
            "TWEE_REGELS_EN_MAX_LIGHT_IN_SHORTLIST_BINDT": (
                "MAX_SHORTLIST = 3 (dinsdag) en er staan TWEE regels op de lijst. De derde plek "
                "blijft leeg en dat is GEEN gebrek aan kandidaten maar "
                "MAX_LIGHT_IN_SHORTLIST = 2 (§0): omdat er vandaag geen enkel FULL-duel is, "
                "zijn alle kandidaten LIGHT en mogen er maximaal twee in de lijst. De "
                "eerstvolgende op rangorde was Fenerbahçe – Slavia Prague, Over 2.5 @1.64 met "
                "+8,35 pp (boven de NEAR-ondergrens van 6,0 die §5b als vloer gebruikt, ruim "
                "onder de LIGHT-lat van 16,0). Die grens is dus vandaag bindend en hij hoort "
                "genoemd: zonder hem had de lijst drie regels gehad. ÉÉN van de twee "
                "gepubliceerde regels haalt zijn EIGEN lat, en ook op de ruwe schaal "
                "(`bet_beide` = TRUE): Paris Saint-Germain – Barcelona, Under 4.5 @1.82, "
                "+21,39 pp tegen een LIGHT-lat van 16,0 (ruw +20,73). De tweede staat op "
                "rangorde: Napoli – Bodø/Glimt, Under 3.5 @1.78, +15,62 pp — 0,38 pp onder die "
                "lat. Beide hebben alle negen poorten open. Omdat er maar één boven de drempel "
                "staat, is de DREMPEL vandaag geen afkapping (§5b stap 5) en valt er geen "
                "gekwalificeerde selectie af op `lijstlengte`. Lees de rangorderegel niet als "
                "een gevonden voordeel: §1g heeft op 552 afgerekende gevallen gemeten dat er "
                "GEEN drempel op de herijkte edge bestaat die geld oplevert."),
            "TWEE_REGELS_EN_BEIDE_ZIJN_EEN_UNDER": (
                "DIT IS HET BELANGRIJKSTE VOORBEHOUD VAN DEZE RUN. Beide gepubliceerde regels "
                "staan op de Over/Under UNDER-kant, precies de markt-en-kant waarvan §6g de "
                "scheefstand meet: een vormfout in het scoregrid zet P(Under) bij élk duel 1,6 "
                "tot 2,4 procentpunt te hoog, en daar bovenop zit een selectie-effect van +0,68 "
                "doelpunt per duel in de duels waar werkelijk een Under is gespeeld (z = "
                "+2,91). Over het logboek: Under 76 picks op -16,5% tegen Over 62 picks op "
                "+10,6%. Poort 9 (§1h) is juist voor deze kant gebouwd en bindt hier NIET, "
                "omdat beide duels op LIGHT staan en LIGHT per besluit van 12 oktober buiten de "
                "poort blijft. Er staat vandaag dus GEEN ENKELE rem op twee Unders. Dat is geen "
                "fout in de uitvoering maar het gat dat §1h zelf benoemt, en het is de tweede "
                "keer deze maand dat het zich voordoet (de eerste was Atalanta – Venezia op "
                "12 oktober). Het hoort als constatering in het runrapport en als vraag NIET "
                "opnieuw aan de gebruiker: hij heeft op 12 oktober besloten dat LIGHT erbuiten "
                "blijft tot de reeks `doelpunten_onder` iets zegt, en §1h verbiedt een run die "
                "vraag elke dag opnieuw te stellen. Wat een run wél moet doen is het noemen, en "
                "dat gebeurt hier en in het dagrapport. De echte oplossing blijft keuze (a) van "
                "11 oktober: de vormfout zelf repareren."),
            "POORT_9_HEEFT_VANDAAG_NIETS_KUNNEN_TOETSEN": (
                "Negende bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke selectie "
                "aangeroepen met today=2026-10-20. poort9_geblokkeerd is voor alle duels leeg, "
                "en vandaag is dat niet omdat er geen Unders waren — er zijn er juist twee "
                "gepubliceerd — maar omdat er GEEN ENKEL FULL-duel is en de poort alleen op "
                "FULL bindt. De reeks `doelpunten_onder` groeit vandaag dus niet; §6d eist er "
                "~30 en het zijn er een handvol, dus lees hem niet. Deze run verandert NIETS "
                "aan de poort — §1h legt vast dat een run dat nooit op eigen initiatief doet."),
            "POORT_8_HOUDT_TWEE_SELECTIES_TEGEN_EN_EEN_ERVAN_VOERT_DE_RUWE_LIJST_AAN": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), "
                "aangeroepen met today=2026-10-20 zodat het vervallen venster van 25 t/m 30 "
                "september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van "
                "geraden. TWEE duels hebben een poort-8-rij op de herijkte schaal: VfB "
                "Stuttgart – Atlético Madrid (Stuttgart +0.25 @2.078, +23,36 pp, score 8,349) "
                "en Sabah FK – Borussia Dortmund (Sabah FK +1.5 @2.08, +8,14 pp, score 2,288). "
                "poort8_ruw is leeg, want geen enkele kandidaat sneuvelde ALLEEN op de ruwe "
                "schaal — §1e eist dat dezelfde selectie nooit in beide reeksen belandt. EN LET "
                "OP WAT DAT BETEKENT VOOR DE RUWE LIJST: de Stuttgart-handicap VOERT DE RUWE "
                "TOP DRIE AAN, bóven de PSG-regel die wél is gepubliceerd. De routine zou "
                "vandaag zonder deze poort dus op een underdog-handicap hebben gezet waar het "
                "model 22,04 procentpunt boven het Pinnacle-oordeel staat (eigen model "
                "Stuttgart 51,0%, Pinnacle 29,0%) — het grootste verschil van de hele run, en "
                "precies de groep waarvan §1e op uitkomsten heeft gemeten dat het model er "
                "structureel naast zit (z = -3,14 over 89 gevallen). De twee reeksen blijven "
                "twee populaties die nooit worden opgeteld."),
            "POORT_7_HOUDT_EEN_SELECTIE_TEGEN": (
                "context.check sloot bij één selectie de poort (één van de 148 doorgerekende "
                "selecties kreeg failed_gate = context). De poort houdt alleen tegen en stelt "
                "my_prob niet bij; bij side = None (Over/Under, BTTS, gelijkspel) staat hij per "
                "ontwerp open, omdat er dan geen kant is om te benadelen en in welke richting "
                "ontbrekende spelers een TOTAAL verschuiven zonder meting niet te zeggen is "
                "(§1c, gemeten op 147 wedstrijden: geen effect te vinden). Beide gepubliceerde "
                "regels zijn een totaal en geen kant, dus voor beide stond de poort open."),
            "EEN_VERPLAATSTE_WEDSTRIJD_SABAH_FK": (
                "context.check_venue is voor alle 10 duels gedraaid en zet bij ÉÉN duel "
                "relocated = True: SABAH FK – Borussia Dortmund wordt niet in het eigen "
                "stadion van Sabah gespeeld maar in het Bakı Olimpiya Stadionu, het nationale "
                "stadion van Azerbeidzjan. Dat is het normale patroon voor een "
                "Champions League-thuiswedstrijd van een kleine club — het eigen stadion haalt "
                "de UEFA-eisen niet — maar het raakt wél de aanname waar het model het zwaarst "
                "op leunt (§1c). Het duel levert geen gepubliceerde regel op: de hoogst "
                "scorende selectie was de Sabah-handicap +1.5 en die is door poort 8 "
                "tegengehouden. §1c eist dat een verplaatsing in het runrapport wordt genoemd "
                "ook als de poort opengaat, en dat gebeurt hier. De overige negen duels staan "
                "op relocated = False: elke thuisploeg speelt in haar eigen stadion."),
            "OPSTELLINGEN": (
                "lineup_type: 9 duels op 'predicted' en 1 op 'lastStarting11' (Wolverhampton "
                "Wanderers – Portsmouth). Bevestigde elftallen (lineupType 'confirmed') zijn er "
                "om 04:07 NL — het moment van de contextophaling — bij geen enkel duel; voor "
                "een avondwedstrijd om 18:45 of 21:00 NL is dat te verwachten. Dat zit in de "
                "datarijkdom (§3 Stage 4) en niet in my_prob."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [20.10. 08:00 NL, 21.10. 08:00 NL). "
                "Alle 10 duels stonden op de daglijst van 20 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 10 zijn playable: de "
                "vroegste aftrap is 18:45 NL (Fenerbahçe – Slavia Prague en Sabah FK – "
                "Borussia Dortmund) en de laatste 21:00 NL (zeven duels), met de Championship "
                "om 20:45 NL. Er is dus geen enkel duel dat al was afgetrapt voordat de "
                "gebruiker kon inzetten, en geen carry-over-band."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob "
                "levert de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van "
                "de zestien competities met een fotmob_id zijn het eens, inclusief de veertien "
                "die vandaag GEEN WEDSTRIJD hebben: 10 duels bij Fotmob, 10 bij BetExplorer, "
                "nul afwijkingen en geen enkele bron die faalde "
                "(tmp-run/ra_oct20_bevestiging.py). Beide spelende competities zijn op het "
                "aantal bevestigd: Champions League 9 en 9, Championship 1 en 1."),
            "BEIDE_SPELENDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Championship (soccer_efl_champ) en UEFA Champions League "
                "(soccer_uefa_champs_league) hebben beide een sportkey bij The Odds API, dus er "
                "is deze run GEEN enkel duel waar BetExplorer de enige 1X2-bron is en de edge "
                "systematisch te laag uitvalt (§1a). Beide gepubliceerde koersen komen van een "
                "bookmaker en niet van een beurs, dus EXCHANGE_COMMISSION komt niet aan de orde "
                "en de genoteerde koers is de koers waarop is gerekend."),
            "MARKTBALANS": (
                "Plafond suggest_cap(19091, 12) = 794 credits. split_budget(794, 2) geeft 2 "
                "spreads / 2 totals, en omdat 3 x 2 = 6 onder 794 blijft is de volle "
                "BULK-aanroep gedaan: h2h + spreads + totals voor beide inkoopbare "
                "competities, dus vijf van de zes markten in één keer. Daarna BTTS voor 7 van "
                "de 10 duels met een kandidaat-edge (§1a stap 2, de vereniging van beide "
                "schalen); de drie overige zijn het NONE-duel (niets door te rekenen) en twee "
                "duels zonder kandidaat-edge. Totaal 13 van 794 credits (6 bulk + 7 BTTS), "
                "19078 over. De marktbalans-controle slaagt: beide inkoopbare competities "
                "hebben zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt "
                "(O/U). Doorgerekend over de negen duels met data: 62 Over/Under, 38 Asian "
                "Handicap, 26 1X2, 14 BTTS, 4 Double Chance en 4 Draw No Bet, samen 148 "
                "selecties. LET OP de scheve verdeling van Double Chance en Draw No Bet (4 "
                "elk): die twee markten zijn afgeleid van de 1X2-prijzen en bestaan alleen waar "
                "een volledig 1X2-boek is; bij de Champions League-duels met een zware favoriet "
                "vallen ze bovendien grotendeels buiten de koersband 1.30-6.00 — negen "
                "selecties sneuvelden op poort 2 (`odds`)."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Voor 9 van de 10 duels gevonden (niet voor Roma – "
                "Slovan Bratislava, dat op NONE staat en geen eigen 1X2 heeft), gemiddelde "
                "Pinnacle-marge 3,78% tegen 6 à 10% bij de rest. Gemiddelde absolute afstand "
                "tussen het eigen model en het Pinnacle-oordeel: 4,77 procentpunt — beter dan "
                "de 6,35 van gisteren, en dat op een dag waarop alle negen duels via een "
                "omrekening lopen. De grootste afwijking is VfB Stuttgart – Atlético Madrid met "
                "+22,04 pp op de thuiszege (eigen model 51,0%, Pinnacle 29,0%), en dat is "
                "precies het duel waar poort 8 de underdog-handicap tegenhield; daarna "
                "Wolverhampton Wanderers – Portsmouth met -9,45 pp op de thuiszege (model "
                "50,0%, Pinnacle 59,5% — de omrekening omlaag maakt Wolves hier minder sterk "
                "dan de markt vindt) en Fenerbahçe – Slavia Prague met -7,80 pp. Bij de "
                "gepubliceerde PSG-regel staat het model dicht bij Pinnacle op de 1X2 (-5,32 pp "
                "op de uitzege), dus de afwijking zit daar in het TOTAAL en niet in wie er "
                "wint. HARDE GRENS §2/§4: dit getal zit NIET in my_prob en NIET in "
                "prob_sources; het is andermans lezing en marktafgeleid, en het hoort in de "
                "vergelijking."),
            "UNDERSTAT_DEKT_GEEN_ENKEL_DUEL": (
                "Geen van de vijf Understat-competities (Premier League, La Liga, Bundesliga, "
                "Serie A, Ligue 1) speelt vandaag, dus er is deze run geen tweede, "
                "onafhankelijk xG-model naast Fotmob. De kansinput komt dus voor alle negen "
                "doorgerekende duels van één bron — Fotmob — in twee doorsnedes (team-xG en de "
                "thuis/uit-splits), plus de omrekening van interleague/promotion daarop. Dat is "
                "genoeg voor §2 (de twee methodes zijn twee methodes, geen twee bronnen) maar "
                "het is minder redundantie dan op een gewone binnenlandse speeldag, en het "
                "hoort genoemd in plaats van stilzwijgend overgeslagen."),
            "VROEG_SEIZOEN": (
                "early_season_uplift geeft factor 1.0567, gepoold 1.0916 over 13 speeldagen in "
                "TWEE competities (Championship 11 speeldagen, Champions League 2). Geen enkele "
                "competitie is uit de pool gelaten (uplift_observations gaf nul overgeslagen), "
                "dus er is geen weggelaten waarneming te melden. De Championship loopt via de "
                "route `vorig+uplift`: 11 van de 46 speeldagen (24%), onder SEASON_MATURE_SHARE, "
                "dus het niveau komt uit 2025/2026 met de correctie erop — thuis 1,480 / uit "
                "1,273 / basis 1,378. De negen Champions League-duels krijgen hun niveau niet "
                "van league_level maar van de Europese referentieschaal van "
                "scripts/interleague.py, want een toernooi met 36 ploegen uit 36 competities "
                "heeft geen eigen doelpuntenniveau dat op de binnenlandse sterktes past. LET OP "
                "dat de pool daardoor klein is: dertien speeldagen over twee competities is "
                "weinig, en de factor is dus onnauwkeuriger dan op een dag met zeven "
                "competities in de pool."),
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
        s3 = json.load(open("tmp-run/ra_oct20_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct20_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct20_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct20_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct20_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

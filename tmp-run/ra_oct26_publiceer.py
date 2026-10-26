"""Run A 26 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct26_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. VIJF van de eenentwintig competities uit de runlijst speelden, met ZEVEN duels in het
inzetvenster: een maandag, en dat is de hele vorm van deze dag. Drie van de zeven staan in de
Super Lig (de Istanbul-derby Galatasaray – Fenerbahçe erbij), de andere vier zijn Sevilla –
Osasuna, PSG – Lyon, Santa Clara – Benfica en FC København – OB.

ALLE ZEVEN DUELS KOMEN OP FULL UIT. Geen ploeg valt buiten de stand van 2025/2026, dus
`promotion.TIER1/TIER2` komt deze run niet aan de orde, en geen duel is kruis-grens.

DE LIJSTLENGTE BINDT NIET: er zijn DRIE duels met een publiceerbare selectie en er passen DRIE
regels in (MAX_SHORTLIST = 3, maandag). Eén van de drie haalt zijn eigen lat van 8,0 pp
(Santa Clara – Benfica, +11,92 pp); de andere twee staan erónder en zijn op rangorde
gepubliceerd. ALLE DRIE STAAN OP DE UNDER-KANT, en dat is de kant die §6g als scheef meet —
lees TWEE_VAN_DE_DRIE... (nu DRIE van de drie) vóór de regels zelf.

EN ER IS VANDAAG EEN FOUT IN DE REPO GEVONDEN DIE EEN BET HEEFT TEGENGEHOUDEN, geen fout die
een bet heeft gekost: `OB` koppelde niet aan BetExplorers `Odense`, dus FC København – OB had
geen marktgemiddelde, poort 8 stond daar OPEN ZONDER TE ZIJN GETOETST, en de selectie die
daardoor doorliep (Asian Handicap OB Odense BK +1 @2,15) stond in de eerste doorrekening van
vanmorgen op plek 2 van de lijst. Na de alias in `scripts/teamnames.py` zet de markt OB op
15,6% — ver onder de ondergrens van 35% — en houdt poort 8 hem tegen. Zie
DE_OB_ALIAS_IS_VANDAAG_GEVONDEN_EN_HIELD_EEN_GEPUBLICEERDE_REGEL_TEGEN.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-26"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-10-26T04:05:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok (wintertijd)


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
    for run, pad in (("A", "tmp-run/ra_oct26_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "EEN_MAANDAG_VAN_ZEVEN_DUELS_EN_DAT_IS_DE_HELE_VORM_VAN_DEZE_DAG": (
                "VIJF van de eenentwintig competities uit de runlijst hebben vandaag een duel in "
                "het inzetvenster, samen ZEVEN wedstrijden. De Premier League, Serie A, "
                "Bundesliga, Championship, Eredivisie, Belgian Pro League, Scottish Premiership "
                "en Ekstraklasa hebben niets op de kalender — hun speelronde liep zondag af en de "
                "volgende begint 30 oktober of 1 november. De drie Europese toernooien spelen "
                "dinsdag, woensdag en donderdag. Dat is GEEN WEDSTRIJD en geen storing (§3 "
                "Stage 2). Wat er wél is, is zwaar: Galatasaray – Fenerbahçe is de Istanbul-derby, "
                "PSG – Lyon is de klassieker van de Ligue 1, en Santa Clara – Benfica is een "
                "kampioenskandidaat op bezoek op de Azoren."),
            "ALLE_ZEVEN_DUELS_OP_FULL_GEEN_OMREKENING_GEEN_KRUIS_GRENS": (
                "Geen van de veertien ploegen valt buiten de stand van 2025/2026, dus "
                "`scripts/promotion.py` komt deze run niet aan de orde en er is geen enkele "
                "LIGHT-regel: alle zeven duels staan op FULL met de lat van 8,0 pp (§0). Geen "
                "duel is kruis-grens, want de drie Europese toernooien spelen niet, dus "
                "`scripts/interleague.py` is vandaag niet gebruikt. Alle vijf competities hebben "
                "xG in zowel 2025/2026 als 2026/2027 (`ra_oct26_stage3.py`), en alle 33 id's uit "
                "coverage.json leveren een bruikbare stand (`scripts/idcheck.py`, 33 van 33 "
                "groen)."),
            "HERIJKING": (
                "§1g, één fit per run uit data/calibration.jsonl: a=0.9808, b=-0.0124 op 6024 "
                "afgerekende gevallen t/m 2026-10-25 — het ruwe model zei gemiddeld 33,3% en het "
                "gebeurde 33,3%. `fitted_through` staat dus op de vórige rundag, zoals §6b-5c "
                "eist; de 237 waarnemingen van 24 en 25 oktober zijn vanmorgen door "
                "`calibration.py settle` afgewikkeld voordat de fit is gelezen. De correctie "
                "VERLAAGT vandaag over vrijwel de hele speelbare band: -0,1 pp op 40%, -0,3 pp op "
                "50%, -0,6 pp op 70%. Gevolg voor §5a: een selectie die de herijkte lat haalt, "
                "haalt hem ook ruw, en dat is vandaag voor de enige regel bóven de lat ook zo "
                "(`bet_beide = true` bij Santa Clara – Benfica). De twee regels eronder staan op "
                "`bet_beide = false`, want zij halen hun lat op geen van beide schalen en zijn op "
                "rangorde gepubliceerd (§5b). Vertrouw die vlag en niet de redenering — §5a "
                "waarschuwt daar uitdrukkelijk voor, omdat de fit elke run een ander getal is."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "prompts/run-a.md: dertien competities en acht toernooien. GEANALYSEERD: La Liga "
                "(1), Ligue 1 (1), Primeira Liga (1), Super Lig (3), Danish Superliga (1). GEEN "
                "WEDSTRIJD: Premier League, Serie A, Bundesliga, Championship, Eredivisie, "
                "Belgian Pro League, Scottish Premiership, Ekstraklasa, UEFA Champions League, "
                "UEFA Europa League, UEFA Conference League, FA Cup, League Cup, Coppa Italia, "
                "KNVB Beker en DFB Pokal. Geen enkele competitie viel op BUITEN DATADEKKING en "
                "geen enkele op AFGEKAPT: de cap is 40 (maandag) en er zijn zeven duels."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen `fotmob_id` in coverage.json en zijn "
                "daarom niet uit de Fotmob-daglijst te filteren; ze gaan langs BetExplorer "
                "(`ra_oct26_cups.py`). Uitkomst: nul teamparen in het inzetvenster bij alle vijf, "
                "met als eerstvolgende ronde DFB Pokal 27 okt 18:00, KNVB Beker 27 okt 18:45, "
                "League Cup 27 okt 20:45, FA Cup 6 nov 20:45 en Coppa Italia 1 dec 21:00 — alle "
                "vijf dus ná het venster [26.10. 08:00 NL, 27.10. 08:00 NL). Alle vijf slugs "
                "leveren teamparen (40, 8, 8, 26 en 16), dus geen van de drie faalmodi van "
                "`scripts/betexplorer.py` is aan de orde: geen homepage-redirect met nul paren en "
                "geen pagina zonder koersen bij een ronde die wél in het venster valt. Dat is het "
                "gat dat Run A op 6 oktober geld kostte — de FA Cup-kwalificatie stond toen niet "
                "in de daglijst en wél bij BetExplorer — en het is daarom met twee bronnen "
                "gemeten in plaats van aangenomen."),
            "DRIE_REGELS_WAARVAN_EEN_ZIJN_EIGEN_LAT_HAALT": (
                "MAX_SHORTLIST = 3 (maandag) en er zijn precies DRIE duels met een publiceerbare "
                "selectie, dus de lijstlengte bindt NIET en er valt geen gekwalificeerde selectie "
                "af. De lijst, op selection_score: (1) Santa Clara – Benfica, Under 2.5 @2,0976 "
                "(Matchbook, beurs: 2,12 bruto), +11,92 pp, score 7,103 — de enige regel die zijn "
                "eigen lat van 8,0 pp haalt, en met 11,92 pp haalt hij óók de verzwaarde lat van "
                "poort 9 (10,0 pp voor een Under op FULL). (2) PSG – Lyon, Under 2.5 @3,15 "
                "(Betsson), +7,06 pp, score 2,740 — ONDER de lat, op rangorde gepubliceerd. "
                "(3) Beşiktaş – Başakşehir, Under 3.5 @1,80 (Pinnacle), +4,00 pp, score 2,382 — "
                "ONDER de lat, op rangorde gepubliceerd, en net boven de ondergrens van 3,0 pp "
                "die `toplist._publiceerbaar` aanhoudt (wat te zwak is om te loggen, is te zwak "
                "om te spelen). §5b is uitdrukkelijk dat zo'n lijst GEEN selectie van winnaars is "
                "maar een rangschikking van wat het model vandaag het sterkst vindt; §1g heeft op "
                "552 afgerekende gevallen gemeten dat er géén drempel op de herijkte edge bestaat "
                "die geld oplevert, en dat het rendement het slechtst is bij de hóógste geclaimde "
                "edge. MAX_LIGHT_IN_SHORTLIST = 2 bindt niet en kan vandaag niets binden: er is "
                "geen enkele LIGHT-kandidaat, want alle zeven duels staan op FULL."),
            "DE_OB_ALIAS_IS_VANDAAG_GEVONDEN_EN_HIELD_EEN_GEPUBLICEERDE_REGEL_TEGEN": (
                "Dit is de belangrijkste bevinding van de run, en ze gaat over de PRIJSkant en "
                "niet over de analyse. Fotmob schrijft de Deense club als `OB` (Odense Boldklub) "
                "en BetExplorer als `Odense`; na `norm` blijft {ob} tegen {odense} over, dus geen "
                "gedeeld token en een naamgelijkenis van 0,25 — ruim onder de vloer van 0,62 van "
                "`best_pair`. The Odds API schrijft `OB Odense BK` en kwam wél door, want {ob} is "
                "een deelverzameling van {ob, odense, bk}: de wedstrijd kreeg dus gewoon spreads, "
                "totals en BTTS, en ALLEEN het gratis BetExplorer-marktgemiddelde viel weg. "
                "PRECIES DAT GEMIDDELDE IS WAAR POORT 8 OP DRAAIT. FC København – OB kwam in de "
                "eerste doorrekening van vanmorgen uit op `underdog_reason = \"geen 1X2-prijzen "
                "— geen marktoordeel over wie de mindere is\"`, dus poort 8 stond OPEN zonder te "
                "zijn getoetst, en de selectie die daardoor doorliep — Asian Handicap OB Odense "
                "BK +1 @2,15, +5,71 pp — stond op plek 2 van de lijst en was gepubliceerd. Met de "
                "alias erin zet de markt OB op 15,6% tegen 64,1% voor FC København, ver onder "
                "`sides.UNDERDOG_FLOOR` = 0,35, en houdt poort 8 alle vier de OB-selecties tegen. "
                "DE RUN IS DAAROM VOLLEDIG HERDRAAID: de drie regels van vanochtend zijn uit "
                "picks.jsonl, shadow.jsonl, calibration.jsonl en context-log.jsonl verwijderd en "
                "de analyse is opnieuw gedraaid met dezelfde, al ingekochte prijzen "
                "(`ra_oct26_analyze_log3.txt`), dus dit heeft nul extra credits gekost. Wat de "
                "fout verder kostte: het kalibratieblok van dit duel bleef leeg — 3 van de 21 "
                "waarnemingen van vandaag, nu 7 van 7 duels met een blok in plaats van 6. "
                "DIT IS DE DERDE KEER DIT MAANDE DAT DEZELFDE STILLE FAALSTAND TOESLAAT: `qpr` "
                "op 9 oktober (ook een initiaalwoord tegen een plaatsnaam, ook poort 8 open "
                "zonder toetsing), de `is_today`-filter op 7 oktober (ook een ontbrekend "
                "marktgemiddelde, ook een gepubliceerde regel eronder) en vandaag `ob`. Alle "
                "drie faalden zonder foutmelding: de run slaagt, het rapport ziet er compleet "
                "uit, en alleen een mens die de getallen naloopt ziet het. De alias staat in "
                "`scripts/teamnames.py` met de volledige diagnose erbij, zodat ze niet in "
                "`tmp-run/` blijft hangen waar `scripts/settling.py` er niet bij kan."),
            "ALLE_DRIE_DE_REGELS_STAAN_OP_DE_UNDER_KANT_EN_DAT_IS_DE_KANT_DIE_SCHEEF_STAAT": (
                "Lees dit vóór de regels zelf. §6g meet dat de Under-kant de verliezende kant van "
                "dit logboek is, en vandaag staan er DRIE van de drie regels op — Under 2.5, "
                "Under 2.5 en Under 3.5. `margins.py "
                "goalbias` van vanmorgen, over 1686 doorgerekende duels: het model als geheel "
                "klopt (verwacht 3,035 doelpunten per duel tegen werkelijk 3,063, z = +0,65), "
                "maar de duels waar werkelijk een Under is GESPEELD leverden 3,323 doelpunten "
                "tegen 2,736 verwacht — +0,587 per duel over 96 gevallen, z = +3,48. De Over-kant "
                "staat op -0,296 (z = -1,25 over 60 gevallen). Daar bovenop staat de vormfout in "
                "`score_grid`: massa verschoven van 2 doelpunten (voorspeld 22,4%, werkelijk "
                "20,8%) naar 4 en 5 (+1,0 en +1,2 pp), waardoor P(Under 2.5) over alle duels 2,1 "
                "pp te hoog staat (voorspeld 42,4%, werkelijk 40,3%). TREK DUS ONGEVEER TWEE "
                "PROCENTPUNT van de genoemde Under-kansen af voordat je ze leest. Poort 9 (§1h) "
                "is de rem die er IS; de oorzaak — keuze (a) van 11 oktober, de vormfout zelf "
                "repareren — staat nog open en is geen werk dat een run op eigen initiatief doet. EN LEES "
                "DIT ER OOK BIJ: §5b waarschuwt dat een lijst die dagen achtereen uit één hoek "
                "komt een signaal is over het MODEL en niet over de rangorderegel. Drie van drie "
                "op dezelfde kant van dezelfde markt is precies die eentonigheid, en ze is "
                "vandaag niet door een poort te wijten: poort 9 bindt alleen in de band 8–10 pp "
                "en twee van de drie regels staan daaronder. Ook de telling van §4 spreekt twee "
                "van de drie tegen — zie `marktvorm` per wedstrijd."),
            "POORT_9_BINDT_OP_EEN_DUEL_EN_DAT_DUEL_LEVERT_ALSNOG_EEN_ZWAKKERE_UNDER": (
                "Vijftiende bindende dag van poort 9 (`unders.BINDS_FROM` = 2026-10-12, §1h), "
                "voor elke selectie aangeroepen met `today=2026-10-26`. De poort BINDT vandaag op "
                "één selectie: PSG – Lyon, Under 3.5 @1,94, +9,11 pp op FULL — in de band 8–10 pp "
                "die §6g op -47,7% over 15 gevallen meet, dus tegengehouden met de verzwaarde lat "
                "van 10,0 pp en als `doelpunten_onder` naar data/shadow.jsonl. EN DAN HET PUNT "
                "DAT ERONDER ZIT, want vandaag staat het voor het eerst BINNEN ÉÉN WEDSTRIJD: "
                "dezelfde PSG – Lyon levert alsnog een gepubliceerde regel op de Under-kant, "
                "Under 2.5 @3,15 met +7,06 pp — MINDER voordeel dan de selectie die de poort "
                "tegenhield. Dat is geen fout in de code maar de vorm van de poort: "
                "`unders.check` laat met opzet elke Under ONDER de gewone drempel van 8,0 door, "
                "op de aanname dat `edge` daar de bindende poort is, en sinds §5b (20 sep 2026) "
                "is `edge` geen poort meer maar een afkapping. Run A schreef deze niet-monotonie "
                "op 16 en 17 oktober op met gepubliceerde regels in ándere wedstrijden; vandaag "
                "is het dezelfde wedstrijd, dezelfde markt en dezelfde kant, alleen een andere "
                "lijn — de scherpste vorm die deze bevinding tot nu toe heeft gehad. DEZE RUN "
                "VERANDERT ER NIETS AAN: §1h punt 3 en §6g leggen vast dat een run een poort "
                "nooit op eigen initiatief verzet en dat de vraag pas opnieuw wordt voorgelegd "
                "als de reeks `doelpunten_onder` van teken draait of als de vormfout is "
                "gerepareerd. Geen van beide is gebeurd: de reeks staat op 18 afgewikkelde rijen "
                "(trefkans 44,4%, rendement -15,5%) waar §6d er ~30 eist, en de vormfout is er "
                "nog. Het staat hier als bevinding en in het dagrapport onder 'Wat er nog moet "
                "gebeuren' met owner = ik."),
            "POORT_8_HOUDT_24_SELECTIES_TEGEN_OVER_ALLE_ZEVEN_DUELS_EN_KOST_DE_HOOGSTE_RUWE_SCORE": (
                "Poort 8 (§1e) bindt in de lichte vorm — ondergrens `sides.UNDERDOG_FLOOR` = "
                "0,35 — en is voor elke selectie met `today=2026-10-26` aangeroepen, zodat het "
                "stilstandvenster van 25 t/m 30 september uit `sides.LAPSED_FROM`/`LAPSED_UNTIL` "
                "wordt gelezen in plaats van geraden. Hij houdt vandaag 24 selecties tegen over "
                "ALLE ZEVEN duels, en dat is de duurste poort van de dag: de hoogste RUWE "
                "selection_score van de hele run is Santa Clara +1.5 @1,74 (+14,77 pp, score "
                "10,67) en die staat op de underdog-kant van een duel waarin de markt Santa Clara "
                "ver onder 35% zet. Nummer twee van de ruwe lijst, Başakşehir +1.5 @1,88 "
                "(+13,41 pp, score 8,932), is hetzelfde geval. Dat alle zeven duels geraakt "
                "worden is nieuw sinds de herdraai van vanmorgen: tot de `ob`-alias raakte poort "
                "8 zes duels, omdat FC København – OB geen marktgemiddelde had en de poort daar "
                "dus niets te toetsen had — zie "
                "DE_OB_ALIAS_IS_VANDAAG_GEVONDEN_EN_HIELD_EEN_GEPUBLICEERDE_REGEL_TEGEN. De "
                "reeks `underdog` staat op 232 afgewikkelde gevallen met een rendement van "
                "-4,5%, dus de poort heeft tot nu toe geld bespaard."),
            "POORT_7_HOUDT_18_SELECTIES_TEGEN_OVER_VIJF_DUELS_EN_EEN_ERVAN_KOST_DE_DERDE_RUWE_PLEK": (
                "Poort 7 (§1c) hield vandaag 18 selecties tegen over 5 van de 7 duels, en het "
                "zwaarste geval is Sevilla – Osasuna: Osasuna mist 31% van zijn selectiewaarde "
                "(19,0 van 42,1 miljoen) tegen 2% bij Sevilla — Aimar Oroz, Jorge Herrando en "
                "Romain Del Castillo — en dat is ruim boven de drempel van 10 procentpunt "
                "verschil. Gevolg: Double Chance — Osasuna of gelijk @1,9996 (+13,31 pp, ruwe "
                "score 8,428, de derde plek van de ruwe lijst) is niet gepubliceerd. De poort "
                "houdt alleen tegen en stelt `my_prob` niet bij (§1c, en de meting van 5 sep 2026 "
                "vond geen bijstelling die bestaat); bij `side = None` — Over/Under en BTTS — "
                "staat hij altijd open, want er is geen kant om te benadelen. De reeks `context` "
                "staat op 91 afgewikkelde gevallen met -25,2%: van alle negen poorten is dit de "
                "poort die het meest heeft bespaard."),
            "GEEN_VERPLAATSTE_WEDSTRIJD_EN_GEEN_ENKELE_STADIONNAAM": (
                "`context.check_venue` is voor alle zeven duels gedraaid en gaf zeven keer "
                "`relocated = false`. Lees dat met de beperking die §1c er zelf bij zet: de "
                "respons gaf voor GEEN van de zeven duels een stadionnaam (`venue.name = null`), "
                "dus de controle vergeleek twee keer niets en kon niets vinden. Dat is dezelfde "
                "stand als op 25 oktober en het is geen storing van deze run, maar het betekent "
                "wel dat `relocated = false` vandaag 'niet gemeten' betekent en niet 'gemeten en "
                "in orde'. Wat de controle hoe dan ook níet vangt, is dat een fixture van "
                "eigenaar is gewisseld — dat is nieuws en geen data, en een geplande run heeft "
                "geen nieuwsbron (Rennes – PSG, 23 aug 2026). Drie van de zeven duels gaven een "
                "voorspelde opstelling (`predicted`) en vier de laatste elf (`lastStarting11`): "
                "de drie Turkse duels en Beşiktaş – Başakşehir."),
            "MARKTBALANS_ALLE_ZES_MARKTEN_DEDEN_MEE": (
                "103 selecties over zes markten en zeven duels, en §1a is vandaag ruim gehaald: "
                "alle vijf competities kregen de bulk-aanroep (h2h + spreads + totals, 3 credits "
                "per competitie, 15 in totaal) en zes van de zeven duels kregen daarna de tweede "
                "ronde BTTS (1 credit per duel, 6 in totaal). Per markt: 1X2 21 selecties in 5 "
                "competities, Asian Handicap 25 in 5, Over/Under 36 in 5, BTTS 12 in 5, Draw No "
                "Bet 6 in 2 en Double Chance 3 in 2. DNB en DC zijn geen aparte inkoop maar de "
                "0.0- en +0.5-lijn uit dezelfde spreads-respons; dat die er bij vier van de zeven "
                "duels niet in zaten is een eigenschap van het boek en geen gat — het staat per "
                "duel in `markets_checked` met de reden erbij. Het enige duel zonder BTTS is "
                "Galatasaray – Fenerbahçe, omdat daar na de eerste ronde geen kandidaat-edge "
                "stond en §1a stap 2 BTTS alleen koopt waar die er wél is. Totaal verbruik deze "
                "run: 21 van de 18695 credits, plafond 1556 (`suggest_cap`). De gepubliceerde "
                "regels komen uit twee verschillende markten (Over/Under en Asian Handicap), dus "
                "de eenzijdigheid van 29 aug 2026 doet zich vandaag niet voor; wél staan twee van "
                "de drie op dezelfde KANT van dezelfde markt — zie "
                "ALLE_DRIE_DE_REGELS_STAAN_OP_DE_UNDER_KANT_EN_DAT_IS_DE_KANT_DIE_SCHEEF_STAAT."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn niet te halen — §3 Stage 5 meet "
                "sinds 20 sep 2026 dat Forebet 403 geeft, de Pinnacle-artikelroute 404, Matchbook "
                "530 en voetbalwedden.net de duels van de dag niet noemt — dus wat deze stap "
                "vandaag invult, is de prijs van PINNACLE APART, los van de beste prijs waarop "
                "wordt gespeeld. 1X2 (`ra_oct26_pinnacle.py`): 5 van de 7 duels hebben een "
                "Pinnacle-1X2, gemiddelde marge 4,00% en gemiddelde absolute afstand tot het "
                "eigen oordeel 6,20 pp. De grootste afstanden: Rizespor – Trabzonspor (+12,51 pp "
                "op de thuiskant — het model vindt Rizespor veel sterker dan Pinnacle) en "
                "Sevilla – Osasuna (-15,03 pp op de thuiskant, +14,56 pp op Osasuna). Op de "
                "doelpuntenkant (`ra_oct26_pinnacle_ou.py`, push-gecorrigeerd zoals op 25 okt "
                "gerepareerd): alle 7 duels hebben een Pinnacle-totaal, gemiddeld verschil op de "
                "Under-kant +3,35 pp en 5 van de 7 duels bóven Pinnacle. De twee gepubliceerde "
                "Unders staan daar allebei in de staart: Santa Clara – Benfica +10,98 pp boven "
                "Pinnacle op lijn 2.50 en PSG – Lyon +9,12 pp op lijn 3.50. HARDE GRENS (§2/§4): "
                "geen van deze getallen gaat in `my_prob` of `prob_sources`; ze horen in de "
                "vergelijking en niet in de kansschatting."),
            "UNDERSTAT_DEKT_TWEE_VAN_DE_ZEVEN": (
                "Understat levert team-xG voor vijf competities (§4) en twee ervan spelen "
                "vandaag: La Liga en Ligue 1. Sevilla – Osasuna en PSG – Lyon hebben daarmee een "
                "ECHT onafhankelijk tweede xG-model in `prob_sources` — Fotmob-xG en "
                "Fotmob-splits zijn twee doorsnedes van dezelfde meting, Understat is een ander "
                "model. Voor de vijf andere duels (Primeira Liga, Super Lig en Danish Superliga) "
                "is Fotmob de enige xG-bron, en dat is precies de afhankelijkheid die §3 "
                "noemt als het enige geval waarin de ontbrekende API_FOOTBALL_KEY alsnog een "
                "echte vraag wordt: valt Fotmob om, dan is er voor die competities geen "
                "onafhankelijke kansinput meer. Fotmob leverde vandaag zonder fout."),
            "VROEG_SEIZOEN_EN_NIVEAU": (
                "`model.uplift_observations` + `early_season_uplift` (§3 Stage 5): gepoolde "
                "factor 1,0606, berekend uit 1,0741 over 36 speeldagen in VIER competities. "
                "ÉÉN competitie is overgeslagen in de pool en dat weglaten is zelf de meting: "
                "Danish Superliga staat op 12 van 22 speeldagen en is dus over de helft, dus haar "
                "niveau komt uit het LOPENDE seizoen (route `lopend`) in plaats van uit vorig "
                "seizoen × factor. Dat is de route die §3 Stage 5 op 24 sep 2026 heeft toegevoegd, "
                "en de Danish Superliga is de competitie waar hij het eerst bindt omdat haar "
                "seizoen maar 22 speeldagen lang is. De vier andere lopen de route "
                "`vorig+uplift`: La Liga (10 speeldagen), Ligue 1 (8), Primeira Liga (9) en Super "
                "Lig (9). De niveaus per competitie staan in `niveau`, met de route en de reden "
                "erbij. En de meting naast de markt (controleren, niet fitten — §2): de "
                "gemiddelde afstand van het eigen 1X2 tot het Pinnacle-oordeel is 6,20 pp over 5 "
                "duels, zonder systematische kant."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert "
                "de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van de zestien "
                "competities met een fotmob_id zijn het eens, inclusief de elf die vandaag GEEN "
                "WEDSTRIJD hebben: 7 duels bij Fotmob, 7 bij BetExplorer, nul afwijkingen en geen "
                "enkele bron die faalde (`ra_oct26_bevestiging.py`). Per competitie bevestigd op "
                "het aantal, inclusief de drie van de Super Lig. De vijf bekers hebben geen "
                "fotmob_id en gaan langs hun eigen tweede bron — zie "
                "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN. LET OP DE TIJDZONE: "
                "BetExplorer labelt in UK-tijd, en dat is sinds de wintertijd GMT tegen CET in "
                "Nederland — nog steeds precies één uur verschil, dus het venster "
                "[26.10. 08:00 NL, 27.10. 08:00 NL) is in UK-tijd [26.10. 07:00, 27.10. 07:00)."),
            "INZETVENSTER": (
                "`runwindow.matches_for_run` met het venster [26.10. 08:00 NL, 27.10. 08:00 NL). "
                "Alle 7 duels stonden op de daglijst van 26 oktober (`source_day` = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 7 zijn `playable`: de "
                "vroegste aftrap is 17:00 NL (Beşiktaş – Başakşehir en Rizespor – Trabzonspor) en "
                "de laatste 21:00 NL (Sevilla – Osasuna). Er is dus geen enkel duel dat al was "
                "afgetrapt voordat de gebruiker kon inzetten, en geen carry-over-band. "
                "`runwindow` rekent met `zoneinfo`, dus het venster is in échte NL-tijd gemeten: "
                "nu de wintertijd in is, komt een aftrap van 18:45 UTC op 19:45 NL uit (CET) en "
                "niet op 20:45 (CEST). Dat is de reparatie van 25 oktober; `ra_oct26_analyze.py` "
                "en dit bestand gebruiken allebei ZoneInfo('Europe/Amsterdam') en "
                "`odds_captured_at` staat op +01:00."),
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
        s3 = json.load(open("tmp-run/ra_oct26_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct26_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct26_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct26_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct26_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

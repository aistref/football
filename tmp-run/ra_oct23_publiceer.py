"""Run A 23 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct22_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWAALF van de eenentwintig competities uit de runlijst speelden, met 13 duels in het
inzetvenster: een vrijdagavond met in vrijwel elke competitie één openingsduel (de Ekstraklasa
heeft er twee).

GEEN ENKEL duel is kruis-grens en GEEN ENKEL duel komt op NONE uit — alle 13 zijn doorgerekend.
Zeven staan op FULL; de zes andere hebben een omgerekende ploeg (promovendus of degradant) en
staan daarom op LIGHT met de lat van 16,0 pp. VIER selecties zijn publiceerbaar en alle vier
worden gepubliceerd: MAX_SHORTLIST = 5 (vrijdag) en de vijfde plek blijft leeg bij gebrek aan
kandidaten, niet door een grens. Twee van de vier halen hun lat; twee staan erónder en zijn op
rangorde gepubliceerd (§5b). Zie VIER_REGELS_WAARVAN_TWEE_OP_RANGORDE.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-23"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-23T04:11:15+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok


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
                         "1486 doorgerekende duels: P(Under 3.0) voorspeld 64,0% tegen werkelijk "
                         "61,9%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de "
                         "gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,616 "
                         "doelpunt per duel over 88 gevallen (z = +3,49 — gegroeid van +0,592 en "
                         "z = +3,34 gisteren), terwijl de Over-kant op -0,221 staat (z = -0,85). "
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
    for run, pad in (("A", "tmp-run/ra_oct23_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.000591, "
                "b=0.000382 over 5400 afgerekende gevallen, fitted_through 2026-10-22, oftewel de "
                "vorige rundag zoals §6b-5c eist. calibration.py settle is deze run vóór de "
                "analyse gedraaid (69 waarnemingen afgewikkeld, 5607 van 5631 compleet, 24 nog "
                "open), dus er is geen regel gepubliceerd op een verouderde correctie. DE FIT IS "
                "VANDAAG VRIJWEL DE IDENTITEIT: a wijkt 0,06% van 1 af en b 0,04 procentpunt van "
                "nul, zodat de herijkte en de ruwe edge bij alle vier de regels tot op twee "
                "honderdsten van een procentpunt samenvallen (Randers +15,58 tegen +15,56; Brest "
                "+16,29 tegen +16,27). Dat is geen defect maar precies wat §1e punt 3 beschrijft: "
                "op de ongeselecteerde ijksteekproef is het ruwe model al goed gekalibreerd — het "
                "zei gemiddeld 33,333% en het gebeurde 33,333%. GEVOLG DAT HOORT MEE TE WEGEN: de "
                "bescherming waarop het vervallen van poort 8 in september werd verantwoord is er "
                "ook vandaag niet, en dat is de gemeten reden dat poort 8 sinds 1 oktober weer "
                "bindt. `bet_beide` staat op TRUE bij de twee regels die hun lat halen "
                "(Randers en Brest) en op FALSE bij de twee die op rangorde zijn "
                "gepubliceerd (Deportivo Alaves en Ipswich Town) - die halen hun lat van "
                "16,0 pp op GEEN van beide schalen, en dat staat zo in hun `notes`."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWAALF van de eenentwintig competities uit de runlijst speelden, samen 13 duels "
                "in het inzetvenster: Premier League, Serie A, La Liga, Bundesliga, Ligue 1, "
                "Championship, Eredivisie, Primeira Liga, Belgian Pro League, Super Lig en Danish "
                "Superliga elk één duel, en de Ekstraklasa twee. Dat is het spiegelbeeld van "
                "gisteren: 22 oktober had 36 duels in twee competities en álles kruis-grens, "
                "vandaag 13 duels in twaalf competities en niets kruis-grens. De NEGEN "
                "competities zonder wedstrijd zijn de Scottish Premiership, de drie Europese "
                "toernooien (de league phase van UEL en UECL was gisteren; UCL hervat 3 november, "
                "UEL en UECL 5 november) en de vijf bekers. Dat is geen storing (§3 Stage 2) maar "
                "de kalender. Alle zestien competities met een fotmob_id zijn door een tweede "
                "bron bevestigd — zie RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven — dat kostte Run A op 6 oktober vijf duels. "
                "Alle vijf zijn daarom langs BetExplorer gegaan (tmp-run/ra_oct23_cups.py) en "
                "alle vijf leveren teamparen op de fixturepagina (FA Cup 40, League Cup 8, Coppa "
                "Italia 8, KNVB Beker 26, DFB Pokal 16), dus geen van de drie faalmodi van die "
                "bron is opgetreden. NUL ervan valt in het inzetvenster: League Cup 27.10. 20:45, "
                "KNVB Beker 27.10. 18:45, DFB Pokal 27.10. 18:00, FA Cup 06.11. 20:45 en Coppa "
                "Italia 01.12. 21:00. KRUISCONTROLE op de Fotmob-daglijst van 23 oktober (112 "
                "competities, 220 duels): daar komt geen van deze vijf in voor; het enige "
                "bekertoernooi met 'FA Cup' in de naam is de SCHOTSE (id 137, ccode SCO), een "
                "andere competitie die niet in de runlijst staat. Twee bronnen, hetzelfde "
                "antwoord."),
            "ER_IS_GEEN_ENKEL_KRUIS_GRENSDUEL_EN_GEEN_ENKELE_NONE": (
                "Alle 13 duels zijn binnenlands, dus scripts/interleague.py komt deze run niet "
                "aan de orde en er is geen duel dat op een onvergelijkbare schaal moet worden "
                "omgerekend (§4, Kruis-grens). En even belangrijk: GEEN ENKEL duel komt op "
                "data_tier NONE uit, dus alle 13 zijn werkelijk doorgerekend — de eerste Run A "
                "sinds weken zonder één enkel duel dat op §2 strandt. ZEVEN duels zijn FULL en "
                "lopen de gewone weg; de ZES andere hebben een ploeg die niet in de stand van "
                "2025/2026 staat en zijn via scripts/promotion.py omgerekend, wat per definitie "
                "LIGHT geeft met de lat van 16,0 pp — zie ZES_OMGEREKENDE_PLOEGEN."),
            "ZES_OMGEREKENDE_PLOEGEN": (
                "Zes duels hebben een ploeg die vorig seizoen niet in deze divisie speelde, en "
                "alle zes zijn omgerekend in plaats van op NONE gezet (§4, 'Promovendi: eerst "
                "omrekenen, dan pas NONE'): Ipswich Town (Premier League, paar E0/E1 bij "
                "football-data.co.uk), Monza (Serie A, I1/I2), Málaga (La Liga, SP1/SP2), Bolton "
                "Wanderers (Championship, E1/E2), Marítimo (Primeira Liga, eigen meting POR) en "
                "Kortrijk (Belgian Pro League, eigen meting BEL, n=13 — het kleinste van de "
                "twaalf gemeten paren op één na, dus met navenante terughoudendheid te lezen). "
                "Alle zes vallen binnen conversion_in_range, dus geen van de zes strandt op de "
                "Coventry-val. De omgerekende sterkte is daarna geblend met het lopende seizoen "
                "(§4, k=8; de reparatie van 9 okt 2026) — dat is bij een promovendus het enige "
                "directe bewijs op het niveau waarop hij nu speelt. De SPLITS blijven ongeblend. "
                "EN HET VERKLAART DE SAMENSTELLING VAN DE LIJST: de twee regels die hun lat NIET "
                "halen zijn precies twee van deze zes duels, want op LIGHT staat de lat op 16,0 "
                "in plaats van 8,0."),
            "VIER_REGELS_WAARVAN_TWEE_OP_RANGORDE": (
                "MAX_SHORTLIST = 5 (vrijdag) en er staan VIER regels op de lijst. De vijfde plek "
                "blijft leeg en dat is deze keer GEEN grens maar een gebrek aan kandidaten: er "
                "zijn precies vier publiceerbare selecties — vier duels waarbij alle acht de "
                "andere poorten openstonden. MAX_LIGHT_IN_SHORTLIST = 2 raakt de bovengrens "
                "exact (twee LIGHT-regels van maximaal twee) maar heeft niets uitgesloten, want "
                "er was geen derde LIGHT-kandidaat. Er is dus ook GEEN gekwalificeerde selectie "
                "die op lijstlengte afvalt en de reeks `lijstlengte` groeit vandaag niet. "
                "TWEE van de vier halen hun eigen lat: Randers FC – Brøndby IF (Under 3 @1.88, "
                "+15,58 pp op FULL, lat 8,0 — en met poort 9 erbij 10,0) en Brest – Nice (Brest "
                "wint @2.31, +16,29 pp op FULL). TWEE staan erónder en zijn op rangorde "
                "gepubliceerd: Deportivo Alavés – Málaga (Over 2.5 @2.14, +10,07 pp op LIGHT, lat "
                "16,0) en Ipswich Town – Nottingham Forest (Over 2.5 @1.83, +8,41 pp op LIGHT, "
                "lat 16,0). Lees die twee dus als 'het beste van vandaag' en niet als een "
                "gevonden voordeel — §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN "
                "drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het "
                "slechtst is bij de hóógste geclaimde edge."),
            "BEIDE_FULL_REGELS_STAAN_HET_VERST_VAN_PINNACLE": (
                "Dit is de belangrijkste waarschuwing van deze run en ze hoort bij de bets in "
                "plaats van in een voetnoot. De twee regels die hun lat hálen zijn óók precies de "
                "twee duels waar het eigen model het verst van het scherpste publieke boek af "
                "staat. Brest – Nice: eigen kans op de thuiszege 59,6%, Pinnacle de-vigd 42,3% — "
                "+17,5 procentpunt, de grootste 1X2-afwijking van de dertien duels (gemiddelde "
                "absolute afstand 4,46 pp). Randers FC – Brøndby IF: eigen P(Under 3) 68,8% tegen "
                "Pinnacle 51,4% — +17,4 procentpunt, en op de xG-arm alleen nog +11,8 pp, "
                "veruit de grootste van de dertien (gemiddeld −1,08 pp, vijf van dertien boven "
                "Pinnacle). Dat is exact het patroon waarvoor §1g en §4 (Kruis-grens, punt 4) "
                "waarschuwen: de grootste geclaimde edge is doorgaans de grootste MODELfout en "
                "niet de grootste marktfout. HARDE GRENS §2/§4: dit getal zit niet in my_prob en "
                "niet in prob_sources; het staat in de vergelijking."),
            "DE_UNDER_LEUNT_OP_DE_SPLITSMETHODE_EN_DAT_IS_EXTREEM": (
                "Randers FC – Brøndby IF, Under 3 @1.88, is de hoogst scorende regel van de dag "
                "(selection_score 10,71) en de onderbouwing is scheef verdeeld over de twee "
                "methodes: de xG-arm geeft +10,06 pp en de splitsmethode +37,56 pp. Die tweede is "
                "het hoogste getal dat deze routine op een splitsmethode heeft gezien, en de "
                "oorzaak is na te rekenen: §1d is sinds 23 aug MULTIPLICATIEF, en hier worden twee "
                "ver onder het gemiddelde liggende verhoudingen met elkaar vermenigvuldigd — "
                "Randers maakte vorig seizoen 11 doelpunten in 11 thuisduels (1,00 tegen een "
                "competitiegemiddelde van 1,68 thuis) en Brøndby kreeg er 8 tegen in 11 "
                "uitduels. Dat geeft een doelverwachting van 0,41 thuis / 0,90 uit, oftewel 1,32 "
                "doelpunt in totaal, tegen 2,61 op de xG-arm. §1f weegt die arm voor een vijfde, "
                "dus hij tilt my_prob van 63,3% naar 68,8%. POORT 5 IS GEHAALD — beide methodes "
                "verslaan de markt dezelfde kant op — maar de spreiding tussen de twee is de "
                "grootste van de run, en §5 eist dat conflicterende of onzekere data wordt "
                "benoemd. Zonder de splitsmethode zou deze regel nog steeds publiceerbaar zijn "
                "(+10,06 pp boven de lat van 8,0 en boven de verzwaarde lat van 10,0 van poort 9, "
                "met 0,06 pp marge), maar hij zou de dagranglijst niet hebben aangevoerd."),
            "POORT_9_BINDT_EN_HEEFT_VANDAAG_NIETS_TEGENGEHOUDEN": (
                "Elfde bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke selectie "
                "aangeroepen met today=2026-10-23. poort9_geblokkeerd is leeg, en dat is hier "
                "WEL een echt oordeel in plaats van een gevolg van ontbrekende FULL-duels zoals "
                "gisteren: er zijn 17 FULL-Unders doorgerekend en geen ervan ligt in de band "
                "8-10 pp waar de poort bindt. De twee Randers-Unders staan er ruim boven (+15,58 "
                "en +15,31 pp) en halen dus ook de verzwaarde lat van 10,0; de hoogste overige "
                "FULL-Under is Widzew Łódź – Górnik Zabrze met +5,26 pp en die wordt door poort 6 "
                "(robuustheid, zwakste stand −0,83 pp) tegengehouden, niet door poort 9. De tien "
                "LIGHT-Unders blijven per besluit van 12 oktober buiten de poort. De reeks "
                "`doelpunten_onder` groeit vandaag dus niet. Deze run verandert NIETS aan de "
                "poort — §1h legt vast dat een run dat nooit op eigen initiatief doet."),
            "POORT_8_HOUDT_EEN_DUEL_TEGEN": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), aangeroepen "
                "met today=2026-10-23 zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van geraden. ÉÉN duel "
                "heeft een poort-8-rij: Go Ahead Eagles – Telstar, '2 (SC Telstar wint)' @5.508, "
                "+2,20 pp, score 0,45 — de markt geeft Telstar 18,3% tegen 59,2% voor Go Ahead "
                "Eagles, ruim onder de ondergrens van 35%. Die selectie had de lijst op eigen "
                "kracht nooit gehaald (score 0,45 tegen 2,65 voor de laagste gepubliceerde "
                "regel), dus de poort kost vandaag niets. poort8_ruw is leeg: geen enkele "
                "kandidaat sneuvelde ALLEEN op de ruwe schaal — logisch bij een fit die vrijwel "
                "de identiteit is. De twee reeksen (`underdog` en `underdog_ruw`) blijven twee "
                "populaties die nooit worden opgeteld; hun stand staat in het runrapport onder "
                "'Stand van het logboek' en wordt daar NIET als besluit voorgelegd (§1e, "
                "5 oktober: stel de vraag niet elke dag opnieuw)."),
            "POORT_7_HOUDT_ACHT_SELECTIES_TEGEN_EN_DRIE_DUELS_KOST_HET_DE_BESTE": (
                "context.check sloot bij 8 van de 191 doorgerekende selecties de poort, verdeeld "
                "over vier duels: Bolton Wanderers – Middlesbrough (4), Randers FC – Brøndby IF "
                "(2), Torino – Monza (1) en VfB Stuttgart – Borussia Mönchengladbach (1). Bij "
                "DRIE duels was de tegengehouden selectie de hoogst scorende van die wedstrijd en "
                "kost de poort dus de hele regel: Torino – Monza (Monza wint @3.646, +9,05 pp — "
                "Monza mist 41% van de selectiewaarde tegen 20% bij Torino, met Ngonge, Maye, "
                "Ziólkowski, Touré en Pessina eruit), VfB Stuttgart – Borussia Mönchengladbach "
                "(Gladbach +1.5 @1.941, +7,59 pp — Gladbach mist de HELFT van zijn "
                "selectiewaarde tegen 14% bij Stuttgart, met negen namen op de lijst waaronder "
                "Kleindienst, Honorat en Itakura) en Bolton Wanderers – Middlesbrough "
                "(Middlesbrough -1 @2.019, +6,18 pp — 20% tegen 2%, met Strelec, Pukštas en "
                "Jones eruit). Bij Randers bleef de poort voor de doelpuntenmarkt open en kwam de "
                "Under er gewoon door; dat is geen inconsistentie maar §1c: bij side = None is er "
                "geen kant om te benadelen. GEEN van de vier gepubliceerde regels is door deze "
                "poort geraakt — drie zijn een totaal (side = None) en bij Brest – Nice is de "
                "thuisploeg niet de benadeelde kant ('geen materieel nadeel gemeten')."),
            "GEEN_VERPLAATSTE_WEDSTRIJD_EN_GEEN_STADIONNAAM": (
                "context.check_venue is voor alle 13 duels gedraaid en zet nergens relocated = "
                "True. Daar hoort een voorbehoud bij dat eerlijker is dan 'alles in orde': de "
                "Fotmob-respons gaf voor GEEN ENKEL van de 13 duels een stadionnaam (venue.name "
                "is overal None), dus de controle heeft niets kunnen vergelijken en 'niet "
                "verplaatst' betekent hier 'geen verplaatsing gemeten' en niet 'gemeten dat er "
                "geen verplaatsing is'. Dat is dezelfde soort stille leegte als §1c beschrijft: "
                "een meting die er niet is, is geen bewijs dat er niets aan de hand is. Het is "
                "ook het verwachte beeld voor binnenlandse competitieduels, waar een "
                "verplaatsing zeldzaam is — op 22 oktober, een Europese avond, sloeg dezelfde "
                "controle bij vijf van de 36 duels wél aan."),
            "OPSTELLINGEN_EN_EEN_LEEG_CONTEXTBLOK": (
                "lineup_type: 8 duels op 'predicted', 4 op 'lastStarting11' en ÉÉN op "
                "'unavailable' — Kortrijk – KV Mechelen, waar Fotmob om 04:05 NL geen opstelling "
                "en ook geen selectiewaarde gaf (squad_value 0 voor beide ploegen). Gevolg: poort "
                "7 kan daar niets meten en staat dus OPEN, precies zoals §1c voorschrijft "
                "(ontbrekende data laat de poort open, want een meting die er niet is, is geen "
                "bewijs van een probleem). De uitvallerslijsten zijn er wél — Kortrijk twee "
                "namen, KV Mechelen zeven — maar zonder noemer is hun aandeel niet te bepalen. "
                "Dat duel levert geen regel op (edge onder de LIGHT-drempel), dus het heeft geen "
                "gevolg voor de lijst. Bevestigde elftallen ('confirmed') zijn er bij geen enkel "
                "duel; voor avondwedstrijden om 18:00 tot 21:45 NL is dat om 04:05 te verwachten. "
                "Dit zit in de datarijkdom (§3 Stage 4) en niet in my_prob. OPVALLEND BIJ "
                "KORTRIJK: 13 dagen rust tegen 5 voor KV Mechelen, het grootste rustverschil van "
                "de run — maar rust in het VOORDEEL van de gespeelde kant is voor poort 7 geen "
                "criterium, die kijkt alleen naar een nadeel."),
            "DE_CAP_BINDT_RUIM_NIET": (
                "13 duels op een vrijdagcap van 55 (ranking.max_deep_analyses, vr-zo), dus er is "
                "NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel. Het is de ruimste "
                "marge in weken — gisteren scheelde het vier duels op een cap van 40. De "
                "datarijkdom liep van 4,50 (Kortrijk – KV Mechelen, geen opstelling en geen "
                "selectiewaarde) tot 7,50 (VfB Stuttgart – Borussia Mönchengladbach); omdat er "
                "niets afviel is er geen 'laagste die het haalde' en geen 'hoogste die afviel' te "
                "noemen (§3 Stage 4). De context is voor alle 13 duels opgehaald zoals §1c eist, "
                "en alle 13 hebben een contextblok zonder fout."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [23.10. 08:00 NL, 24.10. 08:00 NL). "
                "Alle 13 duels stonden op de daglijst van 23 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 13 zijn playable: de "
                "vroegste aftrap is 18:00 NL (Motor Lublin – Zagłębie Lubin) en de laatste 21:45 "
                "NL (Vitória de Guimarães – Marítimo). Er is dus geen enkel duel dat al was "
                "afgetrapt voordat de gebruiker kon inzetten, en geen carry-over-band. LET OP DE "
                "ZOMERTIJD: de wintertijd gaat in op zondag 25 oktober, dus deze run rekent nog "
                "met UTC+2 en dat is de laatste vrijdag waarop dat klopt."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert "
                "de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van de zestien "
                "competities met een fotmob_id zijn het eens, inclusief de vier die vandaag GEEN "
                "WEDSTRIJD hebben: 13 duels bij Fotmob, 13 bij BetExplorer, nul afwijkingen en "
                "geen enkele bron die faalde (tmp-run/ra_oct23_bevestiging.py). Per competitie "
                "bevestigd op het aantal, inclusief de twee Poolse duels. De vijf bekers hebben "
                "geen fotmob_id en gaan langs hun eigen tweede bron — zie "
                "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_TWEE_KEER_GEMETEN."),
            "ALLE_TWAALF_SPELENDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Alle twaalf competities met een duel vandaag hebben een sportkey bij The Odds "
                "API, dus er is deze run GEEN enkel duel waar BetExplorer de enige 1X2-bron is en "
                "de edge systematisch te laag uitvalt (§1a). De Scottish Premiership is de enige "
                "competitie van de runlijst zonder sportkey en die speelt niet. BESTE PRIJS "
                "TEGEN MARKTGEMIDDELDE: gemiddeld +5,79% over de dertien duels (van +3,42% bij "
                "Kortrijk – KV Mechelen tot +7,69% bij Go Ahead Eagles – Telstar), wat in edge "
                "ruwweg anderhalf procentpunt per selectie scheelt — gratis, en de enige "
                "verbetering in dit hele bestand waarvan de omvang vooraf vaststaat. BEURZEN: "
                "geen van de VIER gepubliceerde regels staat op een beurs, dus er is nergens met "
                "oddsapi.net_price hoeven worden gerekend bij de bets zelf — Randers komt van "
                "Pinnacle, Brest van 1xBet, en de twee Over 2.5-regels van gewone bookmakers. "
                "Binnen de 191 doorgerekende selecties zitten wél beurskoersen en die zijn alle "
                "net gerekend."),
            "MARKTBALANS": (
                "Plafond suggest_cap(19013, 9) = 1055 credits. split_budget(1055, 12) geeft 12 "
                "spreads / 12 totals, en omdat 3 x 12 = 36 ruim onder 1055 blijft is de volle "
                "BULK-aanroep gedaan voor ALLE TWAALF inkoopbare competities: h2h + spreads + "
                "totals, dus vijf van de zes markten in één keer. Daarna BTTS voor 10 van de 13 "
                "duels met een kandidaat-edge (§1a stap 2, de vereniging van beide schalen); de "
                "drie zonder kandidaat-edge zijn Vitória de Guimarães – Marítimo, Kortrijk – KV "
                "Mechelen en Motor Lublin – Zagłębie Lubin, en die staan als 'niet opgevraagd — "
                "geen kandidaat-edge' in markets_checked en niet als gat. Totaal 46 van 1055 "
                "credits (36 bulk + 10 BTTS), 18967 over. De marktbalans-controle slaagt ZO RUIM "
                "ALS HET KAN: alle twaalf de competities hebben zowel een uitkomstmarkt (1X2, AH, "
                "DNB, DC) als een doelpuntenmarkt (O/U) — 12 van 12, waar de controle er één "
                "eist. Doorgerekend over de 13 duels: 54 Over/Under, 53 Asian Handicap, 39 1X2, "
                "20 BTTS, 16 Draw No Bet en 9 Double Chance, samen 191 selecties. DE "
                "GEPUBLICEERDE LIJST IS DAARMEE GEEN INKOOPEFFECT: alle zes markten deden overal "
                "mee, en dat er drie van de vier regels uit de doelpuntenmarkt komen is de "
                "analyse die spreekt en niet de portemonnee (§1a, 29 aug 2026)."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Voor ALLE DERTIEN duels gevonden, zowel op 1X2 als op de "
                "totalen, met een gemiddelde Pinnacle-marge van 3,96% tegen 6 à 10% bij de rest. "
                "Gemiddelde absolute afstand tussen het eigen model en het Pinnacle-1X2: 4,46 "
                "procentpunt — ruim onder de 6,44 van gisteren, wat te verwachten is op een dag "
                "zonder enkele omrekening tussen landen. De grootste afwijkingen: Brest – Nice "
                "+17,5 pp op de thuiszege, Alanyaspor – Kocaelispor -12,0 pp en Torino – Monza "
                "-10,1 pp. Op de doelpuntenkant staat het model gemiddeld 1,08 pp ONDER Pinnacle "
                "en bij vijf van de dertien erboven, met Randers FC – Brøndby IF als uitschieter "
                "op +11,8 pp. Zie BEIDE_FULL_REGELS_STAAN_HET_VERST_VAN_PINNACLE. HARDE GRENS "
                "§2/§4: dit getal zit NIET in my_prob en NIET in prob_sources."),
            "EEN_PUSH_FOUT_IN_DE_PINNACLE_VERGELIJKING_GEREPAREERD": (
                "Bevinding van deze run, en ze raakt de rapportage en niet de analyse. Het script "
                "dat de eigen Under-kans naast het Pinnacle-oordeel zet "
                "(tmp-run/rb_oct21_pinnacle_ou.py, overgenomen sinds 21 oktober) vergeleek twee "
                "getallen die niet op dezelfde schaal staan: de KALE kans dat het totaal onder de "
                "lijn blijft tegen de PUSH-GECORRIGEERDE de-vigde Pinnacle-kans. Op een halve "
                "lijn (2.5) is er geen push en klopte het; op een hele lijn (3.0) en op elke "
                "kwartlijn (2.25, 2.75, 3.25) niet. Dat raakt vandaag precies de gepubliceerde "
                "Under: de oude meting gaf 'Pinnacle 0,514 / eigen 0,517, verschil +0,25 pp' en "
                "dat zou in het dagrapport als EXTERNE BEVESTIGING zijn beland van de kant waarvan "
                "§6g de scheefstand meet. Met model.totals_prob op Pinnacle's eigen koers — "
                "dezelfde functie die de poorten gebruiken, §1a: 'gebruik voor markten met push "
                "altijd asian_prob / dnb_prob / totals_prob en nooit de kale winkans' — wordt het "
                "'Pinnacle 0,514 / eigen 0,633, verschil +11,83 pp'. Het dagcijfer kantelt mee: "
                "gemiddeld -1,08 pp in plaats van -2,77 pp. GEEN ENKELE pick, kans, edge of "
                "rangorde van vandaag verandert hierdoor — het is een diagnosescript en geen "
                "poort — en een herberekening van 21 oktober geeft nog steeds de regels van die "
                "dag. Wat er wél verandert is wat er in het dagrapport staat."),
            "UNDERSTAT_DEKT_TWEE_VAN_DE_DERTIEN": (
                "Twee van de vijf Understat-competities spelen vandaag met een duel dat ook een "
                "stand heeft: VfB Stuttgart – Borussia Mönchengladbach (Bundesliga) en Brest – "
                "Nice (Ligue 1). Daar is dus een tweede, ONAFHANKELIJK xG-model naast Fotmob "
                "(§4), inclusief rollende xG over acht duels. BIJ BREST – NICE IS DAT DIRECT VAN "
                "BELANG, want dat duel levert een gepubliceerde regel op: het is de enige van de "
                "vier bets met een kansinput uit twee verschillende xG-modellen in plaats van "
                "twee doorsnedes van één. De drie Engelse en Spaanse duels van vandaag spelen in "
                "de Championship en de Primera/Segunda-mix en vallen buiten de vijf competities "
                "die Understat dekt; de overige negen duels hebben hun kansinput uitsluitend van "
                "Fotmob, in twee doorsnedes (team-xG en de thuis/uit-splits). Dat is genoeg voor "
                "§2 — de twee methodes zijn twee methodes, geen twee bronnen — maar het is minder "
                "redundantie dan bij die twee, en het hoort genoemd in plaats van stilzwijgend "
                "overgeslagen."),
            "VROEG_SEIZOEN_EN_NIVEAU": (
                "early_season_uplift geeft factor 1.1029, gepoold 1.1119 over 91 speeldagen in "
                "ELF competities — de breedste pool die deze routine tot nu toe heeft gehad, en "
                "een stuk steviger dan de drie speeldagen van gisteren. ÉÉN competitie is uit de "
                "pool gelaten en dat is de meting zelf en geen stille omissie (§3 Stage 5): de "
                "DANISH SUPERLIGA staat op 11 van de 22 speeldagen en is dus op of boven "
                "SEASON_MATURE_SHARE, waardoor league_level daar de route `lopend` neemt — het "
                "niveau komt uit het lopende seizoen zelf (thuis 1,606 / uit 1,409 / basis 1,512) "
                "in plaats van uit vorig seizoen maal de factor. DAT IS PRECIES DE COMPETITIE "
                "WAAR DE HOOGST SCORENDE REGEL VAN DE DAG STAAT (Randers FC – Brøndby IF), dus "
                "die route is hier geen detail. De andere elf competities lopen op "
                "`vorig+uplift`; hun niveaus staan per competitie in `niveau`. Een uplift van "
                "10,3% is hoog maar in oktober verwacht: de teamsterktes komen uit vorig seizoen "
                "en begin seizoen wordt er meer gescoord — de correctie dooft vanzelf uit."),
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
        s3 = json.load(open("tmp-run/ra_oct23_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct23_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct23_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct23_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct23_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

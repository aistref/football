"""Run A 4 nov 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_nov03_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag en twee aanpassingen in de vastlegging (zie hieronder). VIER van de eenentwintig
competities uit de runlijst speelden, met VEERTIEN duels in het inzetvenster: negen Champions
League-duels van speelronde 4, drie Championship-duels, een Europa League-duel (Rennes –
Olympiacos, 16:30 NL) en een Belgische. De overige competities, de vijf bekers en de Conference
League spelen vandaag niet.

DRIE GEKWALIFICEERDE REGELS, TWEE GEPUBLICEERD — EN DAT IS DE EERSTE KEER DAT
`MAX_LIGHT_IN_SHORTLIST` IETS TEGENHOUDT. Alle drie halen alle negen poorten én hun eigen
LIGHT-lat van 16,0 pp, er zijn drie plekken (woensdag), en er worden er twee gepubliceerd omdat
alle drie op LIGHT staan en er maar twee LIGHT-regels in de lijst mogen. Zie
MAX_LIGHT_IN_SHORTLIST_BINDT_VANDAAG_ECHT_EN_HOUDT_EEN_VOLLEDIG_GEKWALIFICEERDE_BET_TEGEN.

DE BEVINDING VAN DEZE RUN IS DAT DE RANGORDE VAN VANDAAG DE RANGORDE VAN DE ONENIGHEID MET
PINNACLE IS. De drie duels met de grootste afstand tot het scherpste publieke oordeel zijn exact
de drie duels die alle poorten haalden, en de koers van de bovenste bet komt van Pinnacle zelf —
op precies de lijn waarop het model 20 procentpunt van diens oordeel af staat. Zie
DE_BEVINDING_VAN_DEZE_RUN_ALLE_DRIE_DE_GEKWALIFICEERDE_REGELS_STAAN_OP_DE_GROOTSTE_AFSTAND_VAN_PINNACLE.

TWEE VAN DE DRIE GEKWALIFICEERDE REGELS STAAN OP DE UNDER-KANT, waar `margins.py goalbias`
vanochtend over 124 gespeelde gevallen +0,597 doelpunt per duel te weinig meet (z = +4,01). Zie
TWEE_VAN_DE_DRIE_GEKWALIFICEERDE_REGELS_STAAN_OP_DE_UNDER_KANT_WAAR_DE_SCHEEFSTAND_GEMETEN_IS.

TWEE AANPASSINGEN IN DE VASTLEGGING, allebei omdat de LIGHT-grens vandaag voor het eerst bindt:
de §5b-lus legt de weggevallen selectie vast als `gekwalificeerd_niet_gepubliceerd` plus een
`near_miss` met `failed_gate = "lijstlengte"` (dezelfde naam, want §5b verbiedt een tweede), en
de `reden`-tekst van dat blok noemt nu de werkelijke oorzaak — de LIGHT-grens en niet de lengte —
in plaats van alleen "rang 3 en niet in de lijst". Zonder dat tweede leest het blok als een
lijstlengte die niet bond.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-11-05"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-05T03:30:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


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
        tier_light = r["tier"] != "FULL"
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
                      + (("ONDER-KANT, EN DIT IS DE KANT MET DE GEMETEN SCHEEFSTAND. §6g meet "
                          "dat de gespeelde Under-kant scheef staat, en dat is vanmorgen opnieuw "
                          "gemeten over 1996 doorgerekende duels: P(Under 2.5) voorspeld 42,5% "
                          "tegen werkelijk 40,5% (-2,1 pp), massa verschoven van 0-2 "
                          "doelpunten naar 4 en 5, en op de duels waar werkelijk een Under is "
                          "gespeeld +0,597 doelpunt per duel over 124 gevallen (z = +4,01) "
                          "terwijl de Over-kant op -0,268 staat (z = -1,19 over 66 gevallen). "
                          "HET MODEL ZELF STAAT GOED (+0,046 doelpunt per duel, z = +1,18); het "
                          "is de SELECTIE die scheef staat, en die twee regels mogen nooit als "
                          "een getal worden gelezen. "
                          "WAT ER AL IN ZIT: `model.LEVEL_SCALE` = 1.032 bindt sinds gisteren "
                          "(§0, §6g 'Het besluit van 2 november 2026') en schroeft de "
                          "lambdas van de xG-methode 3,2% op, wat P(Under) ongeveer twee "
                          "procentpunt VERLAAGT. De kans hierboven is dus AL gecorrigeerd - trek "
                          "er niet nog eens twee procentpunt af, want dan tel je dezelfde "
                          "correctie twee keer. De cijfers in deze alinea komen juist uit de "
                          "lambdas van VOOR die knop (alles t/m 2 november is ongecorrigeerd, "
                          "3 november is de eerste gecorrigeerde rundag) en beschrijven de "
                          "fout die de knop moet wegnemen, niet de stand erna. Of dat gelukt is, "
                          "is pas te zien zodra er genoeg duels van na 3 november liggen; §1h "
                          "zegt met zoveel woorden dat poort 9 tot die tijd onveranderd blijft "
                          "staan en dat een run hem niet op eigen initiatief verzet. "
                          + ("DIT DUEL STAAT OP LIGHT EN POORT 9 RAAKT HET DUS NIET: "
                             "`unders.TIERS` is (\"FULL\",) en dat is een besluit van de "
                             "gebruiker van 12 oktober 2026 ('twee hoeft nog niet op de zwakke "
                             "data; eerst kijken wat deze rem doet'), geen omissie. Deze Under "
                             "is daarmee alleen aan zijn eigen LIGHT-lat van 16,0 pp getoetst "
                             "en door geen enkele extra rem. "
                             if tier_light else
                             "Dit duel staat op FULL, dus poort 9 (§1h) kan hier bijten; of hij "
                             "dat werkelijk doet hangt af van de band waarin de edge valt - hij "
                             "bindt ALLEEN tussen 8,0 en 10,0 pp, en laat een Under daaronder met "
                             "opzet door omdat `edge` daar de bindende poort hoort te zijn. ")
                          + "De oorzaakkant - keuze (a) van 11 oktober - is op 28 oktober "
                            "gemeten en AFGEWEZEN (§6g: de voorgeschreven vormcorrectie "
                            "verergert het symptoom en de vormfout bleek grotendeels een "
                            "nalatenschap van shrink = 0.80, op 19 sep opgelost); de "
                            "niveaucorrectie van 2 november is wat daarvoor in de plaats is "
                            "gekomen. ")
                         if onder else "")
                      # `bet_beide = False` heeft DRIE oorzaken en ze zijn niet hetzelfde. Op
                      # 2 november stonden er twee: de lat op geen van beide schalen halen, en
                      # hem ruw wél en herijkt niet halen. De DERDE is op 3 november voor het
                      # eerst voorgekomen (Barcelona - Aston Villa, Under 4.5: herijkt +16,23 pp
                      # boven de LIGHT-lat van 16,0 en ruw +15,39 pp eronder) en kreeg de tekst
                      # van het geval "haalt hem nergens". Dat is onwaar, en het is dezelfde
                      # stille faalvorm als de twee eerdere: de tekst klaagt niet. De drie
                      # gevallen zijn uit `failed_gate` en `failed_gate_ruw` te lezen en niet
                      # uit `bet_beide` alleen — dat veld is één bit voor drie standen.
                      + ("" if cand.get("bet_beide") else
                         (f"bet_beide = FALSE, maar alleen op de HERIJKTE schaal: ruw haalt deze "
                          f"selectie haar lat met {cand.get('edge_raw')} pp wél en herijkt met "
                          f"{cand.get('edge_pp')} pp niet. Dat is de reeks `herijking` van §5a, "
                          f"en de rij is hier geen schaduwpick maar een gepubliceerde bet omdat "
                          f"de rangorde van §5b erover gaat. "
                          if cand.get("bet_ruw") else
                          (f"bet_beide = FALSE, maar alleen op de RUWE schaal: HERIJKT haalt deze "
                           f"selectie haar lat met {cand.get('edge_pp')} pp WEL (alle negen "
                           f"poorten open) en ruw met {cand.get('edge_raw')} pp niet. Dat is de "
                           f"spiegel van de reeks `herijking` - `herijking_omgekeerd` in §5a, "
                           f"mogelijk sinds de fit van 20 september een kans in deze band juist "
                           f"VERHOOGT. Publiceren gebeurt op de herijkte schaal (§1 en §5a: "
                           f"'vertrouw de vlag, niet de redenering'), dus dit is een "
                           f"gekwalificeerde bet en geen rangorderegel. "
                           if cand.get("failed_gate") is None else
                           "bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide "
                           "schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel "
                           "(§5b). ")))),
        })
    return st, top, picks, res


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("A", "tmp-run/ra_nov05_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "DE_BEVINDING_VAN_DEZE_RUN_BEIDE_GEPUBLICEERDE_BETS_STAAN_HAAKS_OP_PINNACLE": (
                "DIT IS DE BEVINDING VAN DEZE RUN EN HET IS EEN WAARSCHUWING BIJ DE LIJST, GEEN "
                "REPARATIE EN GEEN REDEN OM NIET TE PUBLICEREN. Stage 5 stap 2 zet het scherpste "
                "publieke expertoordeel naast de eigen kans, en vandaag staan BEIDE gepubliceerde "
                "regels op een grote afstand van dat oordeel - en bij de bovenste aan de ANDERE "
                "KANT van de streep, niet alleen verder weg. "
                "FC MIDTJYLLAND - AJAX, DNB FC MIDTJYLLAND. De de-vigde 1X2 van Pinnacle staat op "
                "0,366 thuis / 0,244 gelijk / 0,390 uit (marge 4,26%). PINNACLE MAAKT AJAX DUS DE "
                "LICHTE FAVORIET. De eigen xG-methode komt op 0,602 thuis en de splitsmethode op "
                "0,673 - een verschil van +23,6 procentpunt op de thuiskant, de grootste van de "
                "dag. Dat is geen randje: de twee bronnen zijn het niet oneens over hoe GROOT het "
                "thuisvoordeel is, ze zijn het oneens over WIE de betere ploeg is. De bet is DNB "
                "en niet 1X2, dus het gelijke spel kost niets, maar de kant blijft dezelfde kant. "
                "FC TWENTE - PAFOS, UNDER 3.5. Op de Pinnacle-lijn 3.25 staat P(Under) bij "
                "Pinnacle op 0,487 en bij het eigen model op 0,662: +17,50 procentpunt. Op de 1X2 "
                "van datzelfde duel staat het model juist LAGER dan Pinnacle (eigen 0,570 tegen "
                "Pinnacle 0,716 op de thuiskant, -14,6 pp), dus het model vindt Twente minder sterk "
                "EN de wedstrijd doelpuntarmer. Dat zijn twee verschillen in tegengestelde "
                "richting op hetzelfde duel. "
                "WAT DIT NIET IS. Het is geen poort en §2 verbiedt uitdrukkelijk om Pinnacle in "
                "`my_prob` of in `prob_sources` te laten meewegen - dan meet `edge_pp` alleen nog "
                "de afstand tot een getal dat zelf uit de markt komt. Het is ook geen bewijs dat "
                "de bets fout zijn: de hele routine bestaat bij de gratie van soms van de markt te "
                "verschillen, en zonder verschil is er geen edge. Wat het WEL is: de volledige "
                "edge van beide regels van vandaag rust op onenigheid met de scherpste publieke "
                "prijs, en bij geen van de twee is er een tweede, onafhankelijke bron die die "
                "onenigheid steunt. Lees de twee regels dus als wat ze zijn - de uiterste staart "
                "van de eigen verdeling, niet twee gevonden fouten in de markt. "
                "EN DE BREDE STAND ERACHTER: over 20 (duel, lijn)-paren staat de eigen P(Under) "
                "gemiddeld +3,59 pp boven Pinnacle en bij 14 van de 20 erboven. Er is dus een "
                "brede Under-lean EN FC Twente is de grootste uitschieter erin."),

            "ALLE_35_DUELS_VAN_VANDAAG_ZIJN_KRUIS_GRENS_DUS_ER_IS_VANDAAG_GEEN_ENKELE_FULL": (
                "DIT IS DE BEPALENDE EIGENSCHAP VAN DEZE RUNDAG EN HET VERANDERT WELKE LAT ER "
                "GELDT. Twee van de eenentwintig competities van de runlijst spelen: UEFA Europa "
                "League (17 duels) en UEFA Conference League (18). Beide zetten ploegen uit "
                "VERSCHILLENDE LANDEN tegenover elkaar, dus hun sterktes staan op onvergelijkbare "
                "schalen en ze gaan alle 35 langs `scripts/interleague.py` in plaats van langs de "
                "stand van het toernooi (§4, 'Kruis-grens', 8 sep 2026). Die route levert per "
                "ontwerp `LIGHT` en NOOIT `FULL`. "
                "GEVOLG: de lat van vandaag is 16,0 pp (EDGE_THRESHOLD_LIGHT) voor ELKE selectie "
                "van de hele dag, niet 8,0. Dat is tweemaal de gewone drempel, en §0 zegt er "
                "uitdrukkelijk bij dat die verhouding geen keuze is maar een afhankelijkheid van "
                "`model.DATA_WEIGHT`. Een dag als deze levert daarom weinig bets, en dat is het "
                "bedoelde gedrag en geen storing. "
                "22 van de 35 duels halen de omrekening (`LIGHT`), 13 niet (`NONE`). De oorzaak "
                "is bij twaalf daarvan dat er voor een van de twee landen GEEN GEMETEN "
                "competitiefactor is - Kazachstan, Andorra, Finland, Gibraltar, Bosnie, Georgie, "
                "Litouwen, Albanie, Letland, Armenie en Slovenie hebben minder dan 40 Europese "
                "duels in de meting - en bij drie dat de omgerekende waarde buiten "
                "`conversion_in_range` valt (Griekenland bij Hapoel Beer Sheva - OFI Crete, "
                "Zweden bij Mjallby - Borac, Bulgarije bij Panathinaikos - CSKA Sofia). Torreense "
                "valt af omdat de ploeg in Liga Portugal 2 speelt en de factor op de hoogste "
                "divisie is gemeten. Dat die dertien op `NONE` staan is poort 4 die werkt, geen "
                "gat in de dekking: er is voor die duels geen onafhankelijke kansbron op een "
                "vergelijkbare schaal, en dan hoort er niet gerekend te worden. "
                "WAT HIER OOK UIT VOLGT EN WAT NIET IN HET OOG LOOPT: `state['niveau']` IS LEEG, "
                "en dat is correct. `league_level` wordt alleen aangeroepen voor duels binnen een "
                "competitie; de kruis-grenstak gebruikt `interleague.reference_league()`. De "
                "vroeg-seizoenscorrectie is wel BEREKEND (factor 1,0269, gepoold 1,1343 over 2 "
                "speeldagen van 1 competitie, met de Europa League overgeslagen omdat die "
                "halverwege zijn seizoen is: 4 van 8 speeldagen) maar ze voedt vandaag GEEN ENKELE "
                "wedstrijd. Dat staat hier zodat een volgende run dat lege blok niet als een "
                "weggevallen meting leest."),

            "MAX_LIGHT_IN_SHORTLIST_IS_VOL_MAAR_HOUDT_VANDAAG_NIETS_TEGEN": (
                "TWEE GEKWALIFICEERDE REGELS, TWEE GEPUBLICEERD - EN DE GRENS BINDT VANDAAG NIET, "
                "ANDERS DAN GISTEREN. `MAX_LIGHT_IN_SHORTLIST` = 2 (Run A) en beide gepubliceerde "
                "regels staan op `LIGHT`, dus de grens is tot op de rand VOL. Maar er is geen "
                "derde gekwalificeerde selectie die erdoor wegvalt: er zijn er precies twee die "
                "alle negen poorten halen EN boven de LIGHT-lat van 16,0 pp uitkomen. "
                "`MAX_SHORTLIST` = 3 (donderdag), dus er blijft een plek leeg - en die blijft leeg "
                "omdat er niets voor is, niet omdat een grens hem dichthoudt. "
                "DIT IS EXPLICIET ANDERS DAN 4 NOVEMBER, toen er drie gekwalificeerde regels waren "
                "en de LIGHT-grens er voor het eerst echt een tegenhield. Het verschil staat hier "
                "met zoveel woorden omdat 'grens vol' en 'grens bindt' in een runrapport makkelijk "
                "als hetzelfde gelezen worden, en dat zou een stille onwaarheid zijn van precies "
                "de soort waar §6b-5b voor waarschuwt: de tekst klaagt niet. "
                "`gekwalificeerd_niet_gepubliceerd` is daarom LEEG vandaag, en `near_miss` met "
                "`failed_gate = \"lijstlengte\"` komt niet voor."),

            "BEIDE_BETS_ZIJN_SCHOON_OP_BEIDE_SCHALEN": (
                "`bet_beide` is bij beide regels TRUE: ze halen hun lat zowel op de RUWE als op de "
                "HERIJKTE schaal. Midtjylland DNB staat ruw op +22,83 pp en herijkt op +23,77; "
                "Twente Under 3.5 ruw en herijkt beide boven 16,0. Er is dus geen rij van de reeks "
                "`herijking` (§5a) in de lijst van vandaag, en `alleen_herijking` = 0. Dat is de "
                "schoonste van de drie mogelijke standen en het is de moeite van het noteren waard "
                "omdat §5a juist die reeks volgt: de herijking voegt vandaag niets toe en haalt "
                "ook niets weg. De fit zelf staat op a=1,030 / b=0,019 over 6987 afgerekende "
                "gevallen t/m 3 november; het model zei gemiddeld 33,3% en werkelijk was 33,3%."),

            "DE_ONDER_KANT_IS_EEN_VAN_DE_TWEE_BETS_EN_POORT_9_RAAKT_HEM_NIET": (
                "EEN VAN DE TWEE GEPUBLICEERDE REGELS STAAT OP DE UNDER-KANT, en dat is de kant "
                "waar de scheefstand van §6g gemeten is. `margins.py goalbias` van vanochtend, "
                "over 2011 doorgerekende duels: op de duels waar werkelijk een Under is GESPEELD "
                "staat de werkelijkheid +0,609 doelpunt per duel boven de verwachting over 125 "
                "gevallen (z = +4,10), terwijl de Over-kant op -0,268 staat (z = -1,19 over 66 "
                "gevallen). HET MODEL ZELF STAAT GOED: over alle 2011 duels +0,053 doelpunt per "
                "duel (z = +1,38). Die twee regels mogen nooit als een getal gelezen worden - het "
                "is de SELECTIE die scheef staat en niet de lambdas. Op de gangbare lijnen: "
                "P(Under 2.5) voorspeld 42,5% tegen werkelijk 40,3% (-2,2 pp), met massa "
                "verschoven van 0-2 doelpunten naar 4 en 5 (+1,4 pp op 5 doelpunten). "
                "POORT 9 RAAKT DEZE BET NIET, en dat is een besluit en geen omissie. "
                "`unders.TIERS` is (\"FULL\",) - de verzwaarde lat van 10,0 pp geldt alleen op "
                "FULL-data, op besluit van de gebruiker van 12 oktober 2026 ('twee hoeft nog niet "
                "op de zwakke data; eerst kijken wat deze rem doet'). Vandaag staat ELK duel op "
                "LIGHT (zie ALLE_35_DUELS...), dus poort 9 kan vandaag per definitie niet bijten "
                "en de Under van FC Twente is alleen aan zijn eigen LIGHT-lat van 16,0 pp getoetst. "
                "Met +17,60 pp haalt hij die met 1,6 pp marge. "
                "WAT ER AL IN DE KANS ZIT: `model.LEVEL_SCALE` = 1.032 bindt sinds 3 november (§0, "
                "§6g) en schroeft de lambdas van de xG-methode 3,2% op, wat P(Under) ongeveer twee "
                "procentpunt VERLAAGT. De 0,7275 hierboven is dus AL gecorrigeerd - trek er niet "
                "nog eens twee procentpunt af, want dan tel je dezelfde correctie twee keer. De "
                "cijfers in deze alinea komen uit de lambdas van VOOR die knop (alles t/m 2 "
                "november is ongecorrigeerd) en beschrijven de fout die de knop moet wegnemen, "
                "niet de stand erna. Vandaag is de derde gecorrigeerde rundag; drie dagen is veel "
                "te weinig om te zien of het gelukt is, en §1h zegt met zoveel woorden dat poort 9 "
                "tot die tijd onveranderd blijft staan en dat een run hem niet op eigen initiatief "
                "verzet."),

            "DE_CREDITS_EN_DE_MARKTBALANS": (
                "25 van de 379 credits gebruikt, 19751 over bij The Odds API. De opbouw: 2 "
                "bulk-aanroepen van 3 credits (h2h + spreads + totals, een per competitie) = 6, "
                "plus 19 losse BTTS-aanroepen van 1 credit voor de duels met een kandidaat-edge "
                "(§1a stap 2) = 19. Het plafond van 379 komt uit `suggest_cap(19776, 26)`. "
                "MARKTBALANS (§1a, verplicht elke run): beide competities leverden zowel een "
                "uitkomstmarkt (1X2, AH, DNB, DC uit h2h + spreads) als een doelpuntenmarkt (O/U "
                "uit totals, BTTS apart), dus de balans is gehaald en geen enkel duel hoefde op "
                "het BetExplorer-marktgemiddelde alleen te worden gespeeld. De twee gepubliceerde "
                "regels komen uit twee VERSCHILLENDE marktsoorten - een uitkomstmarkt (DNB) en een "
                "doelpuntenmarkt (O/U) - dus de lijst van vandaag leunt niet op een enkele "
                "markt. BetExplorer leverde het gratis marktgemiddelde voor §6e en poort 8 voor "
                "beide competities (17 en 18 rijen, alle van vandaag)."),

            "DE_TWEE_KOERSEN_KOMEN_VAN_EEN_BOOKMAKER_EN_EEN_BEURS": (
                "Midtjylland DNB @2,06 staat bij 1xBet, een gewone bookmaker - geen commissie, de "
                "koers is de koers. Twente Under 3.5 @1,8134 staat bij MATCHBOOK, een BEURS: de "
                "brutokoers is 1,83 en na `EXCHANGE_COMMISSION` van 2% over de nettowinst blijft "
                "1,8134 (§0, `oddsapi.net_price`). De gepubliceerde koers is de NETTOKOERS, dus de "
                "edge van +17,60 pp is al na commissie gemeten en niet ervoor. Dat is het verschil "
                "tussen wel en niet boven de lat staan en het hoort daarom expliciet in de "
                "vastlegging: op de brutokoers van 1,83 zou de edge ~0,5 pp hoger uitvallen. "
                "Geen van de twee koersen komt van Pinnacle zelf, anders dan gisteren."),

            "WAT_ER_AFGEWIKKELD_IS": (
                "STAGE 0, en de reflectie van 12 oktober hoort hierbij. DRIE echte picks "
                "afgewikkeld (1 gewonnen, 2 verloren) en TWAALF schaduwrijen (9 gewonnen, 3 "
                "verloren). "
                "DE GEWONNEN BET: Oxford United - Reading, DNB Oxford @1,9702, 2-0. "
                "DE TWEE VERLOREN BETS, en bij beide klopte de REDENERING minder dan de uitslag "
                "suggereert: AEK Athens - Real Madrid, Under 3.75 @1,96, werd 2-3 (5 doelpunten, "
                "dus ruim eroverheen); PSV Eindhoven - Club Brugge, 1X2 PSV @2,13, werd 1-2. Bij "
                "de eerste is zowel de uitkomst als de inschatting mis - het model verwachtte een "
                "doelpuntarme wedstrijd en er vielen vijf. "
                "HET PATROON VAN DE DAG, EN HET IS GROOT GENOEG OM TE NOEMEN: van de twaalf "
                "schaduwrijen wonnen er NEGEN. Alle drie de verliezers zijn Unders (FC Porto - "
                "Napoli Under 2.5 bij 4-1, Lens - Como Under 3.5 bij 1-9, RB Leipzig - Manchester "
                "City Under 3.5 bij 2-3) en de vierde Under won juist (Rennes - Olympiacos Under "
                "2.5 bij 0-0). Dat is 1 uit 4 op de Under-kant tegen 8 uit 8 op al het andere. "
                "WAT DIT NIET BETEKENT: vier Unders is geen reeks. §6d eist ~30 gevallen voordat "
                "een reeks gelezen mag worden, en de lopende Under-reeks van §6g staat op 125 "
                "gevallen - deze vier zijn er ruim drie procent van en veranderen het beeld niet. "
                "Er is op grond van deze dag GEEN drempel, gewicht of poort aangeraakt. "
                "LENS - COMO 1-9 IS NAGETROKKEN EN HET IS ECHT. Een 1-9 in de Champions League is "
                "zo onwaarschijnlijk dat het eerst als bronfout is behandeld: twee endpoints van "
                "Fotmob geven dezelfde stand, de wedstrijddetails leveren de doelpunten per speler "
                "met minuut (Aguilar 65' bij 0-7) en `firstExtraHalfStarted` is leeg, dus het is "
                "de stand na 90 minuten en niet na verlenging. De acht andere UCL-uitslagen van "
                "die avond zijn normaal. Het staat hier omdat zo'n uitschieter de "
                "doelpuntenmetingen van §6f en §6g merkbaar raakt en een volgende run moet kunnen "
                "zien dat hij is gecontroleerd in plaats van overgenomen. "
                "TWEE RIJEN BLIJVEN OPEN, beide Braziliaans en beide correct open: Botafogo - "
                "Atletico-MG (pick, Under 3) stond bij het afwikkelen 1,6 uur na de aftrap en de "
                "bron meldde hem nog niet afgelopen; Sao Paulo - Corinthians (schaduwrij) was niet "
                "in de daglijsten te vinden. Ze gaan naar Stage 0 van de volgende run. Dat is de "
                "statusregel van §0 die werkt zoals bedoeld - niet afrekenen op een klok maar op "
                "wat de bron meldt."),

            "DE_STAND_VAN_DE_ROUTINE_EN_DE_BRANCHES": (
                "DE EERLIJKE STAND, na de afwikkeling van vanochtend: 524 picks, waarvan 523 "
                "afgewikkeld en 1 open. Trefkans 211/461 = 45,8%, rendement -33,44u over 461 bets "
                "= -7,3% bij 1u flat. Brier eigen 0,2601 tegen Brier markt 0,2406: DE MARKT IS "
                "BETER met 0,0195, en dat is de enige regel die echt zegt of de edge-schatting "
                "iets waard is. Kalibratie: verwacht 274,1 winnaars, werkelijk 211 (-63,1). Het "
                "model is dus nog steeds systematisch te optimistisch, en vandaag zijn er twee "
                "bets gepubliceerd die beide van de scherpste publieke prijs afwijken. Die twee "
                "feiten horen naast elkaar gelezen te worden. "
                "Op `LIGHT` alleen (de categorie van beide bets van vandaag): 161 picks, trefkans "
                "41,7%, rendement -11,8%, Brier eigen 0,2648 tegen markt 0,2391. De zwakke-datakant "
                "staat dus slechter dan het geheel, en dat is precies waarom de lat daar op 16,0 pp "
                "staat in plaats van op 8,0. "
                "CONTEXTLOGBOEK: 1995 afgewikkelde wedstrijden. De fout van het model tegen het "
                "beschikbaarheidsverschil staat op r = -0,042, t = -1,75, helling -11,9 pp per "
                "eenheid; de markt op r = -0,036, t = -1,50. Met 1995 wedstrijden is alleen een "
                "effect vanaf ~12 pp per eenheid aantoonbaar, en de helling zit daar net onder. Het "
                "TEKEN wijst wel consistent de verwachte kant op. Poort 7 blijft daarmee een REM en "
                "geen bijstelling, precies zoals §1c eist zolang de meting er niet is. "
                "DE BRANCHES, EN DIT IS DE UITKOMST VAN STAGE -2. De repo kwam als ONDIEPE KLOON "
                "binnen (`--is-shallow-repository` = true, knip op 27 oktober). Voor het "
                "unshallowen leken 80 van de 89 remote branches eigen commits te hebben, 3 tot 604 "
                "stuks - exact het valse alarm dat §3 Stage -2 beschrijft, want `merge-base` gaf "
                "leeg terug. NA `git fetch --unshallow`: NUL van de 89 branches heeft ook maar een "
                "commit die `origin/main` niet heeft. Er was dus niets te mergen, en dat is "
                "vastgesteld op de volledige geschiedenis en niet op de knip. "
                "DE RUN STAAT OP `main`. De sessie is op branch `claude/stoic-davinci-425pwa` "
                "gezet en die stond bij binnenkomst exact gelijk aan `origin/main` (761e202); er "
                "wordt gepusht met `git push origin HEAD:main` zoals §6a voorschrijft, met "
                "expliciete toestemming uit de scheduler-tekst."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. BINDT VANDAAG NIET, anders dan gisteren: er zijn TWEE wedstrijden met
        # een selectie die alle negen poorten haalt EN boven haar eigen LIGHT-lat van 16,0 pp
        # staat, er zijn drie plekken (MAX_SHORTLIST = 3, donderdag), en beide worden
        # gepubliceerd. `MAX_LIGHT_IN_SHORTLIST` = 2 is daarmee tot de rand VOL — beide regels
        # staan op LIGHT — maar hij houdt niets tegen, want er is geen derde gekwalificeerde
        # selectie. Deze lus levert vandaag dus NUL rijen, en dat hoort zo.
        # Hij blijft onveranderd staan omdat hij het verschil is tussen een gemeten reeks en een
        # stille weglating zodra de grens wél bindt. Hij legt zo'n gekwalificeerde selectie vast als
        # `gekwalificeerd_niet_gepubliceerd` plus een `near_miss` met
        # `failed_gate = "lijstlengte"` — bewust dezelfde naam, ook nu de oorzaak de LIGHT-grens
        # is, zodat de populatie niet in twee reeksen uiteenvalt (§5b, 26 sep 2026: "gebruik
        # precies die naam en verzin geen tweede"). De werkelijke oorzaak staat in `reden`.
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
                          f"{drempel_score}. "
                          + (f"DE OORZAAK IS `MAX_LIGHT_IN_SHORTLIST` = 2 (§0) EN NIET DE LENGTE "
                             f"VAN DE LIJST: er passen {max_shortlist(date.fromisoformat(DAG))} "
                             f"regels in en er staan er {len(top['herijkt'])}, maar alle "
                             f"gekwalificeerde selecties van vandaag staan op LIGHT en daar mogen "
                             f"er maar twee van in de lijst. `failed_gate` blijft `lijstlengte`, "
                             f"omdat §5b (26 sep 2026) verbiedt hiervoor een tweede naam te "
                             f"verzinnen - het is een vraag en twee namen zouden een populatie "
                             f"splitsen waarna geen van beide ooit de ~30 afgewikkelde gevallen "
                             f"van §6d haalt."
                             if len(top['herijkt']) < max_shortlist(date.fromisoformat(DAG))
                             else ""))}
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
        s3 = json.load(open("tmp-run/ra_nov05_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov05_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov05_cups.json"))["cups"]
        for comp, v in cups.items():
            if comp in state["competitions"]:
                continue
            bxv = v.get("betexplorer") or {}
            mark(state, comp, {"status": v["status"], "matches": [],
                               "bron": v.get("bron", "BetExplorer (§5)") + " + BetExplorer",
                               "eerstvolgende_ronde": bxv.get("eerste_ronde"),
                               "teamparen_op_de_fixturepagina": bxv.get("teamparen")})

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
        for run, pad in (("A", "tmp-run/ra_nov05_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov05_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov05_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

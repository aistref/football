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

DAG = "2026-11-06"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-06T03:15:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


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
    for run, pad in (("A", "tmp-run/ra_nov06_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "DE_BEVINDING_VAN_DEZE_RUN_POORT_5_HIELD_80_PROCENT_VAN_ALLE_SELECTIES_TEGEN": (
                "POORT 5 — DE BEVESTIGING DOOR EEN TWEEDE METHODE — IS VANDAAG DE POORT DIE DE "
                "DAG BEPAALT, EN HET IS DE TWEEDE DAG OP RIJ. Van de 186 doorgerekende selecties "
                "sneuvelen er 149 op poort 5 (80,1%), verspreid over 14 van de 15 wedstrijden. "
                "Daarna komt `edge` met 21 selecties (11,3%), `underdog` met 8 (4,3%), `context` "
                "met 5 (2,7%) en `odds` met 3 (1,6%). Er is geen enkele wedstrijd waarin poort 5 "
                "niets tegenhield behalve Oxford City - Leicester City, en dat duel staat op NONE "
                "en heeft dus helemaal geen selecties. "
                "WAT POORT 5 TOETST: de xG-methode en de splitsmethode moeten de markt DEZELFDE "
                "KANT OP verslaan (§1, poort 5). Zakt een van de twee onder de marktkans, dan "
                "wijzen ze tegengesteld en gaat de selectie eruit met reden `data conflicterend`. "
                "Dat de poort op vier vijfde van alle selecties dichtstaat betekent dus niet dat "
                "de selecties zwak zijn maar dat de twee kansmethodes het structureel oneens zijn "
                "over de RICHTING, en dat is iets anders dan oneens over de grootte. "
                "GISTEREN WAS HET HETZELFDE EN DAT IS DE REDEN DAT HET HIER STAAT. Run B van "
                "5 november kwam op nul bets uit doordat alle ZEVENTIEN selecties van haar enige "
                "analyseerbare duel op poort 5 sneuvelden (zie `source-health.json`, "
                "`poort_5_bevestiging`). Vandaag is het dezelfde poort op een twintigmaal grotere "
                "steekproef: 186 selecties over 15 duels in 13 competities in plaats van 17 over "
                "een. "
                "EN DE REM EROP, WANT DIE IS HIER ONMISBAAR. TWEE DAGEN IS GEEN REEKS. §5 "
                "waarschuwt dat een poort structureel alles kan wegvangen en noemt dat een "
                "BEVINDING, maar §6d eist ~30 afgewikkelde gevallen voordat een reeks gelezen mag "
                "worden, en de reeks die deze vraag moet beantwoorden is de SCHADUWREEKS en niet "
                "het aandeel van vandaag. Die reeks staat er, en ze zegt dat de poort zijn werk "
                "doet: `tweede_methode` staat op 263 kandidaten, 254 afgewikkeld, trefkans 46,1% "
                "en een rendement van -2,0% (-5,11u). Een poort met een negatief rendement op 254 "
                "gevallen bespaart geld, en dan is 'hij hield vandaag veel tegen' geen klacht maar "
                "een beschrijving. §1f zegt het nog scherper: als KANSBRON voegt de splitsmethode "
                "vrijwel niets toe (Brier .23674 tegen .23625), als VETO bespaart ze aantoonbaar "
                "geld - en dat veto is vandaag vier vijfde van de run. "
                "WAT HIER NIET UIT VOLGT: er wordt vandaag geen enkele poort, drempel of gewicht "
                "verzet. Dat zou precies de fout zijn die §6d en §1g beschrijven - een anekdote "
                "van twee dagen tot regel verheffen. Wat er WEL uit volgt is dat een derde en "
                "vierde dag met dit aandeel het waard zijn om de vraag te stellen of de twee "
                "methodes systematisch uiteenlopen; §5 noemt dat met zoveel woorden een bevinding "
                "en geen ruis. Dit is dag twee."),

            "DE_FA_CUP_SPEELDE_WEL_EN_STOND_NIET_IN_DE_ADMINISTRATIE_ID_132": (
                "TWEE DUELS ZOUDEN ZIJN GEMIST ALS ER MAAR EEN BRON WAS GEWEEST, EN DIT IS EXACT "
                "HET GAT DAT RUN A OP 6 OKTOBER 2026 VIJF DUELS KOSTTE. `ra_nov06_stage3.py` "
                "filtert de Fotmob-daglijst op de `fotmob_id`s uit `coverage.json`, en de FA Cup "
                "heeft daar geen id - een beker heeft geen stand, dus `idcheck.py` zou er elke run "
                "een vals alarm op geven (§5, en de notitie bij 133/209/235). Het duel-filter sloeg "
                "de FA Cup dus over en de competitiepoort schreef `GEEN WEDSTRIJD`. "
                "DAT WAS ONWAAR, EN TWEE BRONNEN ZEGGEN HET ONAFHANKELIJK VAN ELKAAR. BetExplorer "
                "(`/england/fa-cup/fixtures/`, 40 teamparen) vond twee duels in het inzetvenster: "
                "Bristol Rovers - Cambridge Utd om 20:30 en Oxford City - Leicester om 20:45. En de "
                "daglijst-audit van Stage 1 - die ELKE competitie van de dag noteert en niet alleen "
                "de gefilterde - laat de FA Cup er gewoon in staan, onder `primaryId` 132, met "
                "2 wedstrijden. Beide bronnen: twee duels, dezelfde ploegen, dezelfde aftraptijden. "
                "`ra_nov06_facup.py` haalt ze daarna via id 132 op, met match_id, ploeg-id's en de "
                "aftrap in UTC - wat een BetExplorer-rij niet geeft en wat Stage 4 en 5 wel nodig "
                "hebben. "
                "HET ID GAAT ONDER `notes` IN `coverage.json` EN NIET ONDER `fotmob_id`, om "
                "dezelfde reden als hierboven: `idcheck.py` eist van elk `fotmob_id` een bruikbare "
                "stand en een beker heeft er geen. Zo hoeft een volgende run hem niet opnieuw te "
                "zoeken zonder dat de controle elke ochtend een vals alarm geeft. "
                "WAT DIT OPLEVERDE, EERLIJK: een van de twee duels is doorgerekend en het andere "
                "niet. Bristol Rovers - Cambridge United staat op FULL via "
                "`promotion.shared_lower_division` - beide ploegen staan in League Two (Fotmob 109), "
                "dus er valt niets te overbruggen en het duel is in die divisie doorgerekend (§4, "
                "15 sep 2026), en League Two heeft xG. Oxford City - Leicester City blijft NONE: "
                "daar staan de ploegen WEL op verschillende niveaus en is juist dat niveauverschil "
                "de vraag; de omrekening valt buiten `conversion_in_range`. Nul van beide werd een "
                "bet. Het gat kostte vandaag dus geen bet - maar dat is de uitkomst en niet de "
                "reden om het niet te dichten, want op een volle bekerronde kost het de hele ronde "
                "en ziet het runrapport er met een nette nul normaal uit."),

            "UNDERSTAT_VALT_VOOR_DE_VIJFDE_DAG_UIT_EN_VANDAAG_RAAKT_HET_WEL_IETS": (
                "DIT IS DE ENIGE BRONSTORING VAN DE RUN EN HIJ IS VANDAAG VOOR HET EERST DEZE WEEK "
                "RELEVANT. `scripts/understat.py` geeft voor alle vijf zijn competities exact "
                "dezelfde fout: `UnderstatError: geen JSON terug van "
                "https://understat.com/getLeagueData/<code>/2025 (26719 bytes)`. Vijf competities, "
                "vijf verzoeken, vijf keer EXACT 26.719 bytes - dat is geen storing die voorbijgaat "
                "maar een blokkadepagina of een permanent gewijzigde route. De reeks: 1 nov HTTP 502 "
                "op de CONNECT van de netwerkgateway, 3 nov `Connection reset by peer`, 4 nov 26.719 "
                "bytes zonder JSON, 5 nov idem, vandaag idem. Vijfde dag. "
                "GISTEREN RAAKTE HET NIETS EN VANDAAG WEL, EN DAT IS PUUR DE KALENDER. Understat "
                "dekt PL, La Liga, Bundesliga, Serie A en Ligue 1 (§4). Op 5 november speelde geen "
                "van die vijf - de runlijst gaf alleen Europa en Conference League - en stond er in "
                "`source-health.json` dus met zoveel woorden dat het niets raakte. VANDAAG SPELEN "
                "ALLE VIJF, met samen 5 van de 15 duels in het venster: Everton - Coventry City, "
                "Venezia - Udinese, Sevilla - Deportivo Alaves, Hamburger SV - Borussia "
                "Monchengladbach en Toulouse - Strasbourg. "
                "WAT HET CONCREET KOST. Bij die vijf duels is er geen TWEEDE, onafhankelijk "
                "xG-model naast Fotmob. §4 noemt dat precies zo: Fotmob-xG en Fotmob-splits zijn "
                "twee doorsnedes van DEZELFDE meting, Understat is een ander xG-model. Het "
                "kalibratieblok van §6e mist daardoor zijn `p_xg_understat`-arm bij deze vijf, en "
                "dat is de arm die de vraag moet beantwoorden of het ene xG-model beter voorspelt "
                "dan het andere. De reeks groeit vandaag dus niet. "
                "WAT HET NIET KOST, EN DAT IS BELANGRIJKER. Geen enkel duel wordt hierdoor NONE en "
                "geen enkele tier verandert. §2 eist minstens een onafhankelijke kansinput die geen "
                "bookmaker is, en Fotmob-xG is dat; §4 geeft FULL bij twee onafhankelijke inputs "
                "waarvan een uit categorie 1, en de xG-methode plus de doelpuntensplits leveren dat "
                "- precies zoals op elke dag sinds 1 november. De vijf duels staan dan ook niet "
                "allemaal op FULL om deze reden: Everton - Coventry en Venezia - Udinese zijn LIGHT "
                "omdat er een PROMOVENDUS is omgerekend (§4), niet omdat Understat eruit ligt. "
                "EN DE UITZONDERING VAN §3 IS NIET INGETREDEN. `api_check.py` zegt: meld de "
                "ontbrekende `API_FOOTBALL_KEY` vooraan in de notificatie ZODRA FOTMOB niet meer "
                "levert, want dan is er geen onafhankelijke kansbron meer en levert elke run "
                "gegarandeerd nul bets. Fotmob levert vandaag zonder een enkele fout (twee "
                "daglijsten, 33 van 33 id's groen bij `idcheck.py`, stand van beide seizoenen per "
                "competitie, context voor alle 15 duels inclusief het NONE-duel). De sleutel blijft "
                "dus een besluit van 27 september en geen actiepunt."),

            "DRIE_REGELS_EN_GEEN_ENKELE_HAALT_ZIJN_EIGEN_LAT": (
                "ALLE DRIE DE GEPUBLICEERDE REGELS STAAN ONDER HUN EIGEN DREMPEL EN ZIJN OP "
                "RANGORDE GEPUBLICEERD (§5b). Dat is geen tekortkoming maar precies wat §5b sinds "
                "20 september voorschrijft: de drempel snijdt aan het EIND van de dag, in de "
                "rangorde over alle wedstrijden, en staan er MINDER selecties boven de lat dan er "
                "regels in de lijst passen - wat sinds 5 september vrijwel altijd zo is - dan "
                "bepaalt de rangorde de lijst en gaat de drempel mee als LABEL per regel. "
                "1. FAMALICAO - AROUCA, 1X2 Famalicao wint @2,2348 (Betfair, beurs: 2,26 bruto / "
                "2,2348 na 2% commissie), FULL, +6,68 pp tegen een lat van 8,0. "
                "2. VENEZIA - UDINESE, Over 2.5 @1,9114 (Matchbook, beurs: 1,93 bruto), LIGHT, "
                "+10,14 pp tegen een lat van 16,0. "
                "3. DERBY COUNTY - BOLTON WANDERERS, Draw No Bet Derby County @1,8918 (Matchbook, "
                "beurs: 1,91 bruto), LIGHT, +8,08 pp tegen een lat van 16,0. "
                "LEES DE LIJST DUS ALS 'DIT IS HET BESTE VAN VANDAAG' EN NIET ALS 'DIT IS EEN "
                "GEVONDEN VOORDEEL'. §5b staat deze wijziging toe op grond van de meting in §1g: "
                "over 552 afgerekende gevallen is er GEEN drempel op de herijkte edge die geld "
                "oplevert, en het rendement is het SLECHTST bij de hoogste geclaimde edge. Een lijst "
                "van drie is daarmee een rangschikking van wat het model het sterkst vindt. "
                "DE PRIJS KOMT BIJ ALLE DRIE VAN EEN BEURS, en dat is zeldzaam genoeg om te "
                "noteren. `oddsapi.net_price` haalt er 2% commissie over de nettowinst af, dus de "
                "koers in het rapport is LAGER dan de koers op het scherm van de gebruiker. Beide "
                "getallen staan er daarom bij, zoals §5 eist. "
                "ALLE DRIE DE PLEKKEN DIE OVERBLIJVEN BLIJVEN LEEG: `MAX_SHORTLIST` = 5 (vrijdag) "
                "en er staan drie regels. §5 zegt het expliciet: lever er minder, vul niet aan."),

            "MAX_LIGHT_IN_SHORTLIST_BINDT_VANDAAG_EN_DE_WEGGEVALLEN_REGEL_STAAT_ONDER_HAAR_LAT": (
                "DE LIGHT-GRENS HOUDT VANDAAG EEN VIERDE REGEL TEGEN, EN HET IS BELANGRIJK HOE DIE "
                "REGEL MOET WORDEN GEBOEKT - WANT HET IS NIET HET GEVAL VAN §5b VAN 26 SEPTEMBER. "
                "`MAX_LIGHT_IN_SHORTLIST` = 2 (§0, Run A en B). De lijst is 1 FULL + 2 LIGHT, dus de "
                "grens is VOL. De eerstvolgende regel op `selection_score` is EVERTON - COVENTRY "
                "CITY, Over 2.5 @1,8134 (Matchbook), LIGHT, +6,13 pp, score 1,878 - en die valt weg "
                "omdat er geen derde LIGHT-regel in de lijst mag. Narekenen kan: `toplist.build` met "
                "de LIGHT-grens uit (de Run C-route, waar de gebruiker hem op 24 sep heeft "
                "geschrapt) geeft vier regels in plaats van drie, met Everton als vierde. "
                "WAAROM DIT GEEN `gekwalificeerd_niet_gepubliceerd` IS, EN DAAROM OOK GEEN "
                "`near_miss` MET `failed_gate = lijstlengte`. §5b (26 sep 2026) beschrijft "
                "uitdrukkelijk het geval dat er MEER SELECTIES BOVEN DE DREMPEL staan dan er regels "
                "passen, en noemt zo'n selectie 'geen afgewezen kandidaat: er is geen enkele poort "
                "die haar heeft tegengehouden'. Everton - Coventry haalt zijn drempel NIET: +6,13 pp "
                "tegen een LIGHT-lat van 16,0, en zijn `failed_gate` is `edge`. Hij hoort dus in de "
                "schaduwreeks `edge` waar hij ook in terechtkomt, en niet in de reeks `lijstlengte`. "
                "Die twee bij elkaar zetten zou precies de populatiesplitsing zijn die §5b verbiedt, "
                "maar dan in de andere richting: `edge` betekent 'te weinig voordeel' en "
                "`lijstlengte` betekent 'genoeg voordeel, maar andere wedstrijden hadden er meer'. "
                "Everton is het eerste en niet het tweede. "
                "DIT IS DUS ANDERS DAN 4 NOVEMBER, toen de LIGHT-grens een VOLLEDIG "
                "GEKWALIFICEERDE bet tegenhield (boven haar lat van 16,0) en de rij wel als "
                "`lijstlengte` is geboekt. Het verschil staat hier met zoveel woorden omdat 'de "
                "grens bindt' in een runrapport makkelijk als 'er is een gekwalificeerde bet "
                "weggevallen' gelezen wordt, en dat zou een stille onwaarheid zijn van precies de "
                "soort waar §6b-5b voor waarschuwt: de tekst klaagt niet. "
                "`gekwalificeerd_niet_gepubliceerd` is daarom LEEG vandaag, en de weggevallen regel "
                "staat hieronder vastgelegd als `max_light_geblokkeerd` - een eigen veld, met opzet "
                "GEEN tweede schaduwreeks, zodat er niets wordt opgeteld wat niet bij elkaar hoort. "
                "EN DE STAND VAN DE REEKS DIE HIER WEL OVER GAAT: `lijstlengte` staat op 22 "
                "kandidaten, alle 22 afgewikkeld, trefkans 45,5% en +12,9% rendement (+2,83u). Dat "
                "is positief - de lijstlengte kost ons dus mogelijk geld - maar het zijn 22 gevallen "
                "waar §6d er ~30 eist, en het is geen reden om vandaag iets te verzetten."),

            "GEEN_ENKELE_UNDER_IN_DE_LIJST_TERWIJL_DE_UNDER_SCHEEFSTAND_OP_Z_4_16_STAAT": (
                "DE DOELPUNTENKANT VAN DE LIJST IS VANDAAG VOLLEDIG OVER, EN DAT IS DE EERSTE KEER "
                "DEZE WEEK DAT DE SCHEEFSTAND VAN §6g NIET IN DE LIJST STAAT. Van de drie regels is "
                "er een doelpuntenmarkt (Venezia - Udinese, OVER 2.5) en zijn de andere twee "
                "uitkomstmarkten (1X2 en Draw No Bet). Nul Unders. "
                "WAAROM DAT OPVALT. `margins.py goalbias` meet vanochtend over 2033 doorgerekende "
                "duels dat het MODEL goed staat (+0,048 doelpunt per duel, z = +1,25) terwijl de "
                "duels waarin werkelijk een UNDER is gespeeld +0,614 doelpunt per duel hoger "
                "uitvallen dan de eigen lambda zei - 126 gevallen, z = +4,16. De Over-kant staat op "
                "-0,268 (z = -1,19 over 66 gevallen). Dat zijn TWEE REGELS DIE NOOIT ALS EEN GETAL "
                "MOGEN WORDEN GELEZEN: de bovenste meet het model, de onderste de selectie. En de "
                "onderste is vandaag harder dan gisteren (z = +4,16 tegen +4,01 over 124 gevallen). "
                "DE AFWIKKELING VAN VANOCHTEND ZIT ER ZELF IN. FC Twente - Pafos stond als Under 3.5 "
                "op de lijst van gisteren, de eigen lambdas zeiden 2,69 doelpunt en het werden er "
                "4 (3-1). Dat is een verloren Under op een duel dat precies de kant op viel die deze "
                "reeks meet. "
                "EN POORT 9 BLIJFT ONVERANDERD STAAN. Hij bindt alleen op FULL en alleen in de band "
                "8,0-10,0 pp (§1h), en er is vandaag geen enkele FULL-Under die daar in valt - de "
                "poort hield nul selecties tegen. Dat is geen aanleiding om hem te verzetten: §1h en "
                "§6g zeggen beide dat een run dat niet op eigen initiatief doet, en de vraag hoort "
                "pas gesteld zodra de reeks duels van NA 3 november groot genoeg is. Die staat "
                "vanochtend op 57 van de 1230 homogene duels (`gridfit.py measure` zegt dat zelf, "
                "luidruchtig), dus er is nog niets te beslissen. De reeks `doelpunten_onder` zelf "
                "staat op 35 kandidaten, -30,4% rendement: de rem bespaart geld."),

            "PINNACLE_STAAT_VANDAAG_AAN_DE_ANDERE_KANT_DAN_GISTEREN_OP_DE_UNDER_KANT": (
                "STAGE 5 STAP 2 ZET HET SCHERPSTE PUBLIEKE EXPERTOORDEEL NAAST DE EIGEN KANS, EN DE "
                "UNDER-KANT IS VANDAAG VAN TEKEN GEDRAAID. Over 11 (duel, lijn)-paren staat de eigen "
                "`P(Under)` gemiddeld 2,49 pp ONDER die van Pinnacle, en bij 3 van de 11 erboven. "
                "Dinsdag 4 november was dat +4,47 pp over vier paren en gisteren +1,06 pp over een "
                "enkel paar - vandaag is het de grootste steekproef van de drie EN het andere teken. "
                "DAT WIJST DE KANT OP DIE `model.LEVEL_SCALE` MOEST OPLEVEREN. De knop staat sinds "
                "3 november aan, schroeft de lambdas van de xG-methode 3,2% op en VERLAAGT "
                "`P(Under)` daarmee ongeveer twee procentpunt bij elk duel (§6g, 'Het besluit van "
                "2 november 2026'). Een eigen `P(Under)` die van boven Pinnacle naar onder Pinnacle "
                "verschuift is precies het gedrag dat daarbij hoort. "
                "EN DAN DE REM, WANT DIT IS GEEN METING MAAR EEN DIAGNOSE. §6e is er ondubbelzinnig "
                "over: een afwijking die tegen de MARKT is gemeten mag nooit van `my_prob` worden "
                "afgetrokken en is geen correctiefactor - dan hangt de kansschatting af van de koers "
                "waartegen ze wordt afgezet en meet `edge_pp` niets meer (§2). De vraag 'werkt de "
                "niveaucorrectie' hoort op UITKOMSTEN beantwoord te worden, met `gridfit.py measure` "
                "op de duels van na 3 november, en dat zijn er vanochtend 57 van 1230. Drie "
                "ochtenden Pinnacle-vergelijking zijn geen antwoord op die vraag; §6g verbiedt "
                "uitdrukkelijk 'een vergelijking van twee ochtenden' als vervanging. "
                "DE BREDE STAND. 11 duels met een Pinnacle-1X2, gemiddelde absolute afstand tot zijn "
                "oordeel 3,95 pp, gemiddelde Pinnacle-marge 3,57% tegen 6 tot 10% bij de rest. De "
                "twee grootste meningsverschillen van de dag zijn Sevilla - Deportivo Alaves "
                "(-12,01 pp op de thuiskant: Pinnacle maakt Sevilla duidelijk favoriet, het model "
                "niet) en Toulouse - Strasbourg (+9,54 pp de andere kant op). GEEN VAN DIE TWEE "
                "STAAT IN DE LIJST - beide sneuvelen op poort 5 - en dat is de gunstige vorm van "
                "vandaag: de drie gepubliceerde regels staan op 1,55 pp (Famalicao), 8,9 pp "
                "(Venezia) en 5,1 pp (Derby) van het Pinnacle-oordeel, dus de bovenste bet van de "
                "dag is juist de regel waar het scherpste publieke oordeel het MEEST mee eens is. "
                "Dat is uitdrukkelijk anders dan gisteren, toen beide gepubliceerde regels op de "
                "grootste afstand van Pinnacle stonden en de bovenste zelfs aan de andere kant van "
                "de streep."),

            "DE_HERIJKING_LIEP_EEN_DAG_ACHTER_EN_DE_ANALYSE_IS_OPNIEUW_GEDRAAID": (
                "`recalibrate.load_fit().fitted_through` STOND BIJ BINNENKOMST OP 2026-11-04, EN "
                "§6b-5c EIST DE VORIGE RUNDAG OF LATER - DAT IS 5 NOVEMBER. De controle die die "
                "paragraaf op 30 september expliciet heeft bijgeschreven, sloeg dus aan. "
                "`calibration.py settle` heeft daarna 66 waarnemingen afgewikkeld (7311 van 7341 "
                "compleet, 30 nog open) en `fitted_through` staat nu op 2026-11-05. "
                "WAT ER MIS HAD KUNNEN GAAN EN WAT ER IS GEDAAN. De eerste analyse van vandaag "
                "draaide op de oude fit (a=1,0290 / b=0,0187 over 7038 gevallen t/m 4 november). Na "
                "het settelen staat de fit op a=1,0242 / b=0,0156 over 7104 gevallen t/m "
                "5 november, en de ANALYSE IS DAARNA VOLLEDIG OPNIEUW GEDRAAID op die verse fit - "
                "dat kost rekentijd en NUL credits, want de prijzen zaten al in "
                "`ra_nov06_odds.json` en Fotmob cachet per dag. De drie gepubliceerde regels zijn "
                "onder beide fits dezelfde drie, in dezelfde orde; alleen de edges zakken een "
                "fractie (Famalicao +6,76 -> +6,68, Venezia +10,26 -> +10,14, Derby +8,20 -> "
                "+8,08). De gepubliceerde picks dragen de NIEUWE getallen. "
                "WAAROM DIT STRUCTUREEL IS EN GEEN INCIDENT - EN DIT IS HET OPENSTAANDE PUNT VAN "
                "DEZE RUN. `calibration.py settle` staat in §6b-5c, bij het VASTLEGGEN, en dus NA de "
                "analyse in de pipeline. Stage 0 wikkelt de picks en de schaduwpicks af maar niet "
                "het kalibratielogboek. Het gevolg is dat elke run per constructie met een fit van "
                "ONGEVEER EEN DAG OUD rekent, en dat is ook gisteren zo geweest (de run van "
                "5 november noteerde zelf een fit t/m 3 november). Vandaag is dat opgelost door "
                "handmatig te settelen en opnieuw te rekenen; de nette oplossing is "
                "`calibration.py settle` naar Stage 0 te verplaatsen, naast `ledger.py settle` en "
                "`shadow.py settle`, zodat de fit van de dag de uitslagen van gisteren al kent. "
                "DE OMVANG, EERLIJK: het gaat om tienden van procentpunten. De fit verhoogt een "
                "kans met +0,2 pp op 40%, +0,5 pp op 50% en +0,9 pp op 70%, waar de oude fit van "
                "voor 20 september er tien hele afhaalde (§5a). Dit is dus een administratief "
                "gebrek en geen bron van verkeerde bets - maar het is precies de stille faalvorm "
                "die §6b-5c beschrijft: een niet-afgewikkeld logboek klaagt niet, `load_fit()` "
                "levert gewoon een geldige fit op de laatste stand die hij heeft, en elke run "
                "schrijft netjes op dat hij is toegepast."),

            "DE_AFWIKKELING_VAN_VANOCHTEND_TWEE_BETS_VERLOREN_EN_EEN_SCHADUWDAG_DIE_NAAR_DE_ANDERE_KANT_VIEL": (
                "STAGE 0 - DE REFLECTIE VAN §3, NIET ALLEEN DE BOEKHOUDING. Twee picks van Run A "
                "van 5 november zijn afgewikkeld en BEIDE VERLOREN, en 21 schaduwrijen van dezelfde "
                "dag (14 gewonnen, 6 verloren, 1 void). "
                "1. KLOPTE DE REDENERING, OF KLOPTE ALLEEN DE UITKOMST? Bij beide picks klopte de "
                "redenering ook niet, en bij de eerste fors niet. FC MIDTJYLLAND - AJAX, DNB "
                "Midtjylland @2,06: de eigen lambdas stonden op 2,196 voor Midtjylland en 1,170 "
                "voor Ajax, en het werd 1-6. Ajax scoorde zes waar het model er 1,17 verwachtte. "
                "Dat is niet 'verloren maar goed ingeschat' - het model had de VERKEERDE PLOEG als "
                "de betere, en Pinnacle noteerde dat gisteren al: die maakte Ajax de lichte "
                "favoriet terwijl het model Midtjylland op 60,2% zette. Het runrapport van gisteren "
                "noemde dat verschil van +23,6 pp zelf de grootste van de dag en schreef erbij dat "
                "de twee bronnen het niet oneens waren over de GROOTTE van het thuisvoordeel maar "
                "over WIE de betere ploeg is. Die waarschuwing is uitgekomen. "
                "FC TWENTE - PAFOS, Under 3.5 @1,8134: lambdas 1,773 en 0,916, samen 2,69 "
                "verwachte doelpunten; het werd 3-1, dus 4. De RICHTING was goed (Twente won als "
                "favoriet) en het TOTAAL niet, en de bet zat op het totaal. Een doelpunt te veel en "
                "de bet was gewonnen. "
                "2. DEDEN DE POORTEN DIE DE ANDERE KANDIDATEN TEGENHIELDEN HUN WERK? Op deze dag "
                "overwegend NIET, en dat hoort er net zo eerlijk bij te staan: 14 van de 21 "
                "schaduwrijen zijn GEWONNEN. De poort `edge` hield onder meer Milan - Ferencvaros "
                "(Under 2.5, 0-2), Anderlecht - Salzburg (1, 2-0), Levski Sofia - Jagiellonia "
                "(Under 2.5, 1-0) en Thun - Hearts (1, 3-1) tegen, alle vier winnaars. Poort 8 hield "
                "Sunderland - Dinamo Zagreb (Dinamo +1.5, 0-2) en Getafe - Brighton (Getafe +1.5, "
                "0-1) tegen - ook winnaars. Poort 5 hield AZ - Juventus (2, 1-2) en Leverkusen - "
                "Marseille (Marseille +1.5, 0-1) tegen - winnaars - en AGF - Braga (Over 2.5, 0-0) "
                "- verliezer. "
                "3. ZAT ER EEN PATROON IN DE DAG? Ja, en het is groot genoeg om te noemen: op een "
                "dag dat de twee GESPEELDE bets beide verloren, wonnen 14 van de 21 TEGENGEHOUDEN "
                "kandidaten (66,7%). De dag was dus niet slecht voor de wedstrijden maar slecht "
                "voor de selectie - de routine zat op de twee regels die eruit kwamen, en de "
                "regels die ze wegfilterde deden het beter. Daar komt bij dat vijf van de zes "
                "Unders in de schaduwlijst wonnen (Milan, Palace, Levski, Lillestrom, Getafe; "
                "alleen Celta Vigo verloor) terwijl de gespeelde Under juist verloor. "
                "4. EN DE REM: WAT BETEKENT DIT NIET? EEN DAG IS GEEN REEKS, en dit is exact het "
                "geval waarvoor §6d die rem heeft. 21 schaduwrijen op een dag tegen de ~30 "
                "AFGEWIKKELDE gevallen PER POORT die §6d eist voordat een reeks gelezen mag worden. "
                "De lopende reeksen zeggen iets anders dan deze dag: `edge` staat over 602 "
                "afgewikkelde gevallen op +3,7% (de poort kost geld - en dat is precies waarom §5b "
                "hem sinds 20 september een label maakt en geen veto), `tweede_methode` op -2,0% "
                "over 254 en `underdog` op -3,8% over 307 (beide poorten besparen geld). Een dag "
                "waarop tweederde van de tegengehouden kandidaten wint, past binnen die ruis en is "
                "geen reden om vandaag iets te verzetten. "
                "WAT ER WEL IN DE GATEN GEHOUDEN HOORT: de `underdog`-reeks staat sinds de meting "
                "van 5 oktober van TEKEN GEDRAAID. Toen was het +16,9% over 36 afgewikkelde "
                "gevallen en dat was de meting waarop de gebruiker gevraagd is of poort 8 eruit "
                "kon; nu is het -3,8% over 307. §1e noemt 'de reeks draait van teken' met zoveel "
                "woorden een aanleiding om de vraag opnieuw voor te leggen - maar het teken is "
                "gedraaid NAAR de kant die de poort STEUNT, dus er is niets te beslissen en de "
                "vraag hoort niet gesteld. Genoteerd als stand, niet als besluit."),

            "DE_STAND_VAN_DE_ROUTINE_EN_DE_BRANCHES": (
                "DE EERLIJKE STAND, na de afwikkeling van vanochtend: 526 picks, alle 526 "
                "afgewikkeld en NUL open. Trefkans 212/464 = 45,7%, rendement -34,61u over 464 bets "
                "= -7,5% bij 1u flat, gemiddelde koers 2,17 en gemiddelde geclaimde edge +10,2 pp. "
                "Brier eigen 0,2610 tegen Brier markt 0,2406: DE MARKT IS BETER met 0,0204, en dat "
                "is de enige regel die echt zegt of de edge-schatting iets waard is. Kalibratie: "
                "verwacht 276,2 winnaars, werkelijk 212 (-64,2). Het model is dus nog steeds "
                "systematisch te optimistisch, en vandaag worden er drie regels gepubliceerd die "
                "geen van drieen hun eigen lat halen. Die twee feiten horen naast elkaar gelezen te "
                "worden. "
                "OP LIGHT (de categorie van twee van de drie regels van vandaag): 120 picks, "
                "trefkans 41,6%, rendement -13,0%, Brier eigen 0,2787 tegen markt 0,2405. Op FULL: "
                "406 picks, trefkans 47,0%, rendement -5,7%, Brier eigen 0,2553 tegen markt 0,2407. "
                "De zwakke-datakant staat dus ruim slechter dan de sterke, en dat is precies waarom "
                "de lat daar op 16,0 pp staat in plaats van op 8,0. "
                "SCHADUWLOGBOEK: 1634 kandidaten, alle 1572 beslisbare afgewikkeld, rendement "
                "-5,0% (-78,56u). De poorten besparen dus samen geld. Per poort: `edge` +3,7% over "
                "602 (kost geld), `lijstlengte` +12,9% over 22 (kost geld, maar onder de ~30 van "
                "§6d), `tweede_methode` -2,0% over 254, `underdog` -3,8% over 307, `context` -24,8% "
                "over 115, `odds` -57,8% over 38, `doelpunten_onder` -30,4% over 35, `herijking` "
                "-3,3% over 59, `underdog_ruw` -8,8% over 17. "
                "KALIBRATIELOGBOEK: 2447 wedstrijden, 7341 uitkomsten over 74 dagen. `my_prob` "
                "staat +1,63 pp boven de markt op longshots en -3,31 pp eronder bij favorieten; de "
                "scheefstand die poort 8 afdekt is er dus nog, en dat is de gemeten reden dat de "
                "rem staat (§1e). De Understat-arm staat op +3,11 / -6,02 en groeit vandaag niet, "
                "want de bron ligt eruit. "
                "CONTEXTLOGBOEK: zie `ctxlog.py stats` in het runrapport. Poort 7 blijft een REM en "
                "geen bijstelling, precies zoals §1c eist zolang de meting er niet is. "
                "DE BRANCHES, EN DIT IS DE UITKOMST VAN STAGE -2. De repo kwam opnieuw als ONDIEPE "
                "KLOON binnen (`--is-shallow-repository` = true, met de knip op 27 oktober en een "
                "tweede op 21 oktober). VOOR het unshallowen leken 76 van de 85 remote branches "
                "eigen commits te hebben, 3 tot 604 stuks - exact het valse alarm dat §3 Stage -2 "
                "beschrijft, want `git merge-base origin/main <tak>` gaf LEEG terug en "
                "`rev-list --count` telde elke commit van voor de knip als 'nog niet hier'. NA "
                "`git fetch --unshallow`: NUL van de 85 branches heeft ook maar een commit die "
                "`origin/main` niet heeft. "
                "EN DE CONTROLE OP DE INHOUD IS APART GEDAAN, want §3 eist die sinds 27 september "
                "uitdrukkelijk NAAST de commitgraaf ('0 eigen commits is een uitspraak over de "
                "graaf; alleen een vergelijking per regel is een uitspraak over de metingen'). Alle "
                "VIJF de logboeken zijn per tak op regelaantal vergeleken met `origin/main`: "
                "picks.jsonl 526, shadow.jsonl 1707, calibration.jsonl 7341, context-log.jsonl "
                "2045 - en op GEEN ENKELE tak staat er een hoger aantal dan op main. Er was dus "
                "niets te verenigen, en dat is vastgesteld op de volledige geschiedenis en op de "
                "inhoud, niet op de knip. Er stonden ook geen openstaande picks van een run die op "
                "een andere tak nooit is afgewikkeld: `ledger.py open` gaf precies de twee picks "
                "van Run A van gisteren. "
                "DE RUN STAAT OP `main`. De sessie is op branch `claude/stoic-davinci-1wru23` "
                "gezet en die stond bij binnenkomst exact gelijk aan `origin/main` (d748985); er "
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
        idx_match = {m["match"]: m for m in res["matches"]}
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

        # `MAX_LIGHT_IN_SHORTLIST` = 2 BINDT VANDAAG, en de weggevallen regel staat ONDER haar
        # eigen lat. Dat is NIET het geval van §5b van 26 september (dat gaat uitdrukkelijk over
        # selecties BOVEN de drempel, "geen afgewezen kandidaat: er is geen enkele poort die haar
        # heeft tegengehouden"), dus er komt hier GEEN `gekwalificeerd_niet_gepubliceerd` en GEEN
        # `near_miss` met `failed_gate = "lijstlengte"`. De selectie sneuvelt op `edge` en komt in
        # die schaduwreeks terecht; haar in `lijstlengte` zetten zou twee populaties optellen die
        # twee verschillende vragen beantwoorden ("te weinig voordeel" tegen "genoeg voordeel,
        # maar anderen hadden meer").
        #
        # Hij wordt wel VASTGELEGD, in een eigen veld, want anders is van buitenaf niet te zien
        # dat de lijst drie regels heeft omdat een grens bond en niet omdat er niets meer was.
        # Dat onderscheid is precies wat §5 en §6b-5b eisen: geen stille weglating.
        zonder_light = toplist.build({**st, "run": "C"},
                                     n=max_shortlist(date.fromisoformat(DAG)))["herijkt"]
        in_lijst = {(r["match"], r["market"], r["selection"]) for r in top["herijkt"]}
        geblokt = [r for r in zonder_light if (r["match"], r["market"], r["selection"]) not in in_lijst]
        for r in geblokt:
            m = idx_match[r["match"]]
            m["max_light_geblokkeerd"] = {
                "market": r["market"], "selection": r["selection"], "odds": r["odds"],
                "tier": r["tier"], "edge_pp": r["edge_pp"], "score": r["score"],
                "rang_zonder_de_grens": zonder_light.index(r) + 1,
                "failed_gate": r.get("failed_gate"),
                "reden": (
                    f"`MAX_LIGHT_IN_SHORTLIST` = 2 is vol (de lijst heeft "
                    f"{sum(1 for x in top['herijkt'] if x['tier'] != 'FULL')} LIGHT-regels van de "
                    f"{len(top['herijkt'])}) en deze selectie zou als nummer "
                    f"{zonder_light.index(r) + 1} in de rangorde staan. Er passen "
                    f"{max_shortlist(date.fromisoformat(DAG))} regels in de lijst, dus het is de "
                    f"LIGHT-grens die hem tegenhoudt en niet de lengte. "
                    f"GEEN `lijstlengte`-rij: deze selectie haalt haar eigen lat NIET "
                    f"({r['edge_pp']:+.2f} pp tegen 16,0) en sneuvelt op `{r.get('failed_gate')}`, "
                    f"terwijl §5b (26 sep 2026) `lijstlengte` reserveert voor selecties die alle "
                    f"poorten EN hun drempel halen. Twee namen voor een vraag zijn verboden, maar "
                    f"een naam voor twee vragen net zo goed."),
            }
            print(f"max_light_geblokkeerd: {r['match']} {r['market']} — {r['selection']} "
                  f"({r['edge_pp']:+.2f} pp, rang {zonder_light.index(r) + 1})")
        if not geblokt:
            print("MAX_LIGHT_IN_SHORTLIST houdt vandaag niets tegen")

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
        s3 = json.load(open("tmp-run/ra_nov06_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov06_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov06_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_nov06_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov06_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov06_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

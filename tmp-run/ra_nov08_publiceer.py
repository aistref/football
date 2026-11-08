"""Run A 8 nov 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_nov08_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWAALF van de eenentwintig competities uit de runlijst speelden, plus de FA Cup, met
55 duels in het inzetvenster op een zondagcap van 55: nul afgekapt en nul marge.

ZES SELECTIES HALEN ALLE NEGEN POORTEN EN ER PASSEN VIJF REGELS IN DE LIJST. De zesde valt op
`lijstlengte` (§5b, 26 sep 2026). Zie ZES_GEKWALIFICEERD_VIJF_GEPUBLICEERD_DE_LIJSTLENGTE_BINDT.

ALLE ZES STAAN OP EEN DOELPUNTENMARKT — vier Over/Under en twee BTTS, en geen enkele
uitkomstmarkt. Zie
ALLE_ZES_DE_GEKWALIFICEERDE_SELECTIES_STAAN_OP_DE_DOELPUNTENMARKT_EN_DAT_IS_DE_ANALYSE.

TWEE VAN DE VIJF GEPUBLICEERDE REGELS STAAN OP DE UNDER-KANT, EN ZE STAAN VER BOVEN PINNACLE.
Zie DE_TWEE_UNDERS_STAAN_VER_BOVEN_HET_SCHERPSTE_PUBLIEKE_OORDEEL.

POORT 9 HEEFT VOOR HET EERST MEER DAN EEN SELECTIE TEGENGEHOUDEN. Zie
POORT_9_HIELD_TWEE_SELECTIES_TEGEN_EN_ZIJN_EIGEN_REEKS_IS_NU_GROOT_GENOEG_OM_TE_LEZEN.

POORT 5 HOUDT VOOR DE VIERDE DAG OP RIJ RUIM DRIEKWART VAN ALLES TEGEN: 554 van de 720
selecties (76,9%). Zie POORT_5_HOUDT_VOOR_DE_VIERDE_DAG_OP_RIJ_RUIM_DRIEKWART_TEGEN.

DE CAP KOMT EXACT OP NUL MARGE UIT. Zie DE_CAP_BOND_NIET_MAAR_HIJ_HAD_NUL_MARGE.

UNDERSTAT VALT VOOR DE ZEVENDE DAG UIT en raakt vandaag 24 van de 49 doorgerekende duels — de
duurste dag van de reeks. Zie UNDERSTAT_VALT_VOOR_DE_ZEVENDE_DAG_UIT.

EEN PICK VAN GISTEREN BLEEK EEN DAG OPGESCHOVEN. Zie
DE_PICK_VAN_GISTEREN_OP_NACIONAL_ACADEMICO_VISEU_IS_EEN_DAG_OPGESCHOVEN.

DE BTTS-REEKS HAALT DE ~30 DIE §1h VOOR ZICHZELF HEEFT GESTELD. Zie
DE_BTTS_REEKS_HAALT_DE_DERTIG_EN_DAT_IS_EEN_VRAAG_VOOR_DE_GEBRUIKER.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-11-08"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-08T03:20:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


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
    for run, pad in (("A", "tmp-run/ra_nov08_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "ZES_GEKWALIFICEERD_VIJF_GEPUBLICEERD_DE_LIJSTLENGTE_BINDT": (
                "ZES SELECTIES HALEN VANDAAG ALLE NEGEN POORTEN EN STAAN BOVEN HUN EIGEN LAT, EN "
                "ER PASSEN VIJF REGELS IN DE ZONDAGLIJST (`MAX_SHORTLIST` = 5, §0). De zesde is "
                "Union St.Gilloise - Genk, BTTS 'beide ploegen scoren - nee' @2,274, `FULL`, "
                "+8,85 pp en `selection_score` 4,677 - rang 6 van 6. "
                "HIJ IS GEEN AFGEWEZEN KANDIDAAT EN DAT IS HET HELE PUNT VAN §5b (26 sep 2026): "
                "er is geen enkele poort die hem heeft tegengehouden, hij haalt de drempel van "
                "8,0, en toch is hij geen bet. Hij is vastgelegd als "
                "`gekwalificeerd_niet_gepubliceerd` op de wedstrijd in `data/run-state/` EN als "
                "`near_miss` met `failed_gate = \"lijstlengte\"`, zodat `shadow.py collect` hem "
                "afrekent. De naam is met opzet precies die ene naam: twee namen zouden een "
                "populatie splitsen waarna geen van beide ooit de ~30 afgewikkelde gevallen van "
                "§6d haalt. "
                "DE REEKS DIE DAARDOOR GROEIT STAAT NU OP 25 AFGEWIKKELDE GEVALLEN, 44,0% "
                "trefkans en +11,0% rendement (+2,76u). Dat is POSITIEF - de lijstlengte kost dus "
                "geld in plaats van het te besparen - en het is nog steeds onder de ~30 die §6d "
                "eist voordat zo'n reeks gelezen mag worden. Niet lezen, wel opschrijven. "
                "WAT HIER NIET UIT VOLGT: `MAX_SHORTLIST` wordt niet verhoogd. De 3/5 staat in §0 "
                "en een run verzet die niet op eigen initiatief; de lijstlengte is bovendien de "
                "reden dat het dagrapport leesbaar blijft (§5b: 'een lijst van vijf is geen "
                "selectie van winnaars maar een rangschikking van wat het model het sterkst "
                "vindt'). "
                "DE RANGORDE VAN VANDAAG, op `selection_score`: Napoli - Lazio 14,548 · "
                "Fiorentina - Juventus 10,014 · AZ Alkmaar - FC Groningen 7,080 · Sunderland - "
                "Chelsea 5,664 · Villarreal - Getafe 5,545 · Union St.Gilloise - Genk 4,677."),

            "ALLE_ZES_DE_GEKWALIFICEERDE_SELECTIES_STAAN_OP_DE_DOELPUNTENMARKT_EN_DAT_IS_DE_ANALYSE": (
                "VIER OVER/UNDER EN TWEE BTTS. Nul 1X2, nul Asian Handicap, nul Draw No Bet, nul "
                "Double Chance. Dat is de eerste keer in deze reeks dat de hele lijst uit de "
                "doelpuntenhoek komt EN er geen enkele uitkomstmarkt meedingt in de einduitslag. "
                "WAAROM DIT GEEN INKOOPARTEFACT IS, EN DAT IS HIER DE HELE VRAAG. §1a heeft de "
                "marktbalans-controle juist hiervoor gebouwd: op 29 augustus 2026 kwamen 12 van de "
                "14 bets uit een markt en dat was de portemonnee en niet de analyse, omdat "
                "Over/Under in negen van de elf competities de enige betaalde markt was. Vandaag "
                "is het omgekeerde waar. De bulk-aanroep (h2h + spreads + totals, 3 credits per "
                "competitie) is voor ALLE TWAALF inkoopbare competities gelukt, 36 van 424 "
                "credits, dus elke competitie had zowel een uitkomstmarkt (1X2, AH, DNB, DC) als "
                "een doelpuntenmarkt. 12 van 12. Daarbovenop is BTTS in een tweede ronde gekocht "
                "voor 38 duels met een kandidaat-edge (§1a stap 2), 38 credits; 39 duels hadden "
                "een kandidaat-edge en bij een duel (Heart of Midlothian - Falkirk) was er geen "
                "event-id in de spreads-respons, wat in `markets_checked` ook zo staat en niet als "
                "'geen kandidaat-edge'. Alle zes de markten dongen dus mee. "
                "WAT ER WERKELIJK IS DOORGEREKEND: 720 selecties over 49 duels met een tier, "
                "verdeeld als Over/Under 242, Asian Handicap 197, 1X2 133, BTTS 76, Draw No Bet 40 "
                "en Double Chance 32. De doelpuntenmarkten zijn samen 318 van de 720 (44%) en de "
                "uitkomstmarkten 402 (56%) - de scheefstand zit dus in wat eruit komt en niet in "
                "wat erin ging. "
                "WAT DE LOGBOEKEN OVER DEZE MARKTEN ZEGGEN, en het is de reden dat dit meer is dan "
                "een curiositeit. Over 477 afgewikkelde bets staat `Over/Under - Over` op +5,0% "
                "rendement over 94 gevallen (trefkans 55,3%) en `Over/Under - Under` op -12,5% "
                "over 164. `BTTS - nee` staat op -6,2% over 20 en `BTTS - ja` op +37,9% over 11. "
                "Van de vijf gepubliceerde regels staan er twee op de Over-kant (de kant die "
                "historisch heeft opgeleverd), twee op de Under-kant (de kant die heeft gekost) en "
                "een op BTTS-nee. Dat is geen voorspelling - §1g heeft op 552 gevallen gemeten dat "
                "er GEEN drempel bestaat die geld oplevert - maar het is wel de juiste manier om "
                "deze lijst te lezen. "
                "WAT HIER NIET UIT VOLGT: er wordt geen quotum ingevoerd en geen bet geforceerd om "
                "de verdeling recht te trekken. §1a zegt het met zoveel woorden: dit is een "
                "rapportageplicht en geen quotum, en als alle zes de markten meedingen en er komt "
                "toch een eenzijdige lijst uit, dan IS dat de uitkomst. Bets forceren om een "
                "verdeling te halen is precies wat §1 verbiedt."),

            "DE_TWEE_UNDERS_STAAN_VER_BOVEN_HET_SCHERPSTE_PUBLIEKE_OORDEEL": (
                "DIT IS HET GROOTSTE VOORBEHOUD VAN DE RUN EN HET HOORT VOORAAN IN PLAATS VAN "
                "ERONDER. De twee Unders van vandaag - Napoli - Lazio Under 3 @1,94 en "
                "Fiorentina - Juventus Under 2.5 @2,10 - staan niet een beetje maar heel ver boven "
                "wat Pinnacle, de scherpste bookmaker van de markt, van diezelfde lijnen vindt. "
                "DE CIJFERS. Napoli - Lazio: Pinnacle noteert 1,94/1,94 op lijn 3,0, wat "
                "de-vigd en push-gecorrigeerd P(Under 3) = 0,500 geeft; het model zegt 0,6845. "
                "Verschil +18,45 procentpunt. Fiorentina - Juventus: Pinnacle 1,88/2,00 op lijn "
                "2,5, de-vigd P(Under 2.5) = 0,4845; het model zegt 0,6359. Verschil +15,13 "
                "procentpunt. Over alle 47 (duel, lijn)-paren van vandaag staat het model gemiddeld "
                "-0,81 pp ONDER Pinnacle op de Under-kant en in 19 van de 47 gevallen erboven. Deze "
                "twee zijn dus niet de regel maar de twee grootste uitschieters van de dag, en het "
                "is precies waarop gepubliceerd wordt. "
                "WAT DAT WAARSCHIJNLIJK BETEKENT. §1g heeft op 552 afgerekende gevallen gemeten dat "
                "de bookmaker scherper schat dan dit model (Brier markt 0,2412 tegen eigen 0,2605 "
                "over 477 bets), en dat het rendement het SLECHTST is bij de hoogste geclaimde "
                "edge. Een afstand van achttien procentpunt tot het scherpste publieke oordeel is "
                "daarmee eerder een eigen fout dan een gevonden voordeel. "
                "EN ER LIGT EEN TWEEDE, ONAFHANKELIJKE METING ONDER DIE DEZELFDE KANT OP WIJST. "
                "`margins.py goalbias` meet vanochtend over 130 gespeelde Unders +0,612 doelpunt "
                "per duel MEER dan de eigen lambda zei, met z = +4,20 - de hardste stand die deze "
                "reeks heeft gehad. Op de Over-kant gebeurt dat niet: 71 gevallen, -0,359 "
                "doelpunt, z = -1,65. De modelkant zelf staat recht (2150 duels, +0,032 doelpunt, "
                "z = +0,86), dus dit is het SELECTIE-effect van §6g: de routine speelt Under juist "
                "daar waar haar lambda te laag staat. Dat is exact het mechanisme dat vandaag twee "
                "keer op de lijst staat. "
                "POORT 9 HEEFT ZE NIET TEGENGEHOUDEN EN DAT IS ZIJN ONTWERP. `unders.check` eist "
                "sinds 12 oktober 10,0 pp in plaats van 8,0 voor een Under op `FULL`-data; Napoli "
                "haalt +20,26 pp en Fiorentina +15,79 pp, dus ruim boven de verzwaarde lat. De rem "
                "van §1h mikt op de band 8-10 pp, de slechtste van de reeks, en niet op de "
                "bovenkant. "
                "WAT HIER NIET UIT VOLGT: er wordt geen poort, lat of gewicht verzet op grond van "
                "een dag. Wat er WEL uit volgt is dat dit voorbehoud in het dagrapport bij beide "
                "regels hoort te staan en niet in een voetnoot (§6c, §4 punt 2)."),

            "POORT_9_HIELD_TWEE_SELECTIES_TEGEN_EN_ZIJN_EIGEN_REEKS_IS_NU_GROOT_GENOEG_OM_TE_LEZEN": (
                "POORT 9 BINDT VANDAAG OP TWEE SELECTIES, EN DAT IS ER EEN MEER DAN HIJ OOIT OP "
                "EEN DAG HEEFT GEHAD. Inter - Como (Under 3.5 @1,69, +8,13 pp) en Besiktas - "
                "Genclerbirligi (Under 3.5 @2,0192, +8,51 pp) staan beide in de band 8-10 pp op "
                "`FULL`, precies waar `unders.UNDER_EXTRA` = 2,0 pp voor is gebouwd (§1h). Zonder "
                "de poort waren het twee extra selecties in de rangorde geweest. "
                "DE REEKS `doelpunten_onder` STAAT OP 36 KANDIDATEN, ALLE 36 AFGEWIKKELD, 36,1% "
                "trefkans en -32,3% rendement (-11,63u). Dat is boven de ~30 die §6d eist en het "
                "is duidelijk negatief: de rem houdt verliezers tegen en doet zijn werk. De twee "
                "van vandaag maken het er 38 zodra ze zijn afgewikkeld. "
                "WAT HIER NIET UIT VOLGT: poort 9 wordt niet verzet, niet verzwaard en niet naar "
                "`LIGHT` uitgebreid. §1h heeft die vraag op 12 oktober gesteld en de gebruiker "
                "heeft hem beantwoord met 'twee hoeft nog niet op de zwakke data; eerst kijken wat "
                "deze rem doet', en §1h en §6g verbieden een run uitdrukkelijk de poort op eigen "
                "initiatief te verzetten. "
                "DE OORZAAKKANT. De niveaucorrectie `LEVEL_SCALE` = 1.032 van 2 november is de "
                "enige ingreep die aan de oorzaak iets doet. `gridfit.py measure` zegt vanochtend "
                "dat 174 van de 1347 homogene duels lambdas van na 3 november dragen - gisteren 84 "
                "- en dat is nog te weinig om te lezen (§6d). De vraag of poort 9 daardoor "
                "overbodig wordt hoort dus nog niet gesteld."),

            "POORT_5_HOUDT_VOOR_DE_VIERDE_DAG_OP_RIJ_RUIM_DRIEKWART_TEGEN": (
                "POORT 5 - DE BEVESTIGING DOOR EEN TWEEDE METHODE - IS VOOR DE VIERDE DAG OP RIJ "
                "DE POORT DIE DE DAG BEPAALT. Van de 720 doorgerekende selecties sneuvelen er 554 "
                "op poort 5 (76,9%). Daarna komt `edge` met 53 (7,4%), `underdog` met 38 (5,3%), "
                "`context` met 35 (4,9%), `odds` met 22 (3,1%), `robuustheid` met 6 (0,8%) en "
                "`doelpunten_onder` met 2 (0,3%); 10 selecties (1,4%) halen alle poorten, verdeeld "
                "over zes wedstrijden. "
                "DE REEKS: 5 november alle 17 selecties van het enige analyseerbare duel, 6 "
                "november 149 van 186 (80,1%), 7 november 395 van 510 (77,5%), vandaag 554 van 720 "
                "(76,9%). Vier dagen, vier keer rond driekwart, en de steekproef wordt elke dag "
                "groter in plaats van kleiner. "
                "WAT POORT 5 TOETST: de xG-methode en de splitsmethode moeten de markt DEZELFDE "
                "KANT OP verslaan (§1, poort 5). Zakt een van de twee onder de marktkans, dan "
                "wijzen ze tegengesteld en gaat de selectie eruit met reden `data conflicterend`. "
                "Dat de poort op ruim driekwart van alle selecties dichtstaat betekent dus niet dat "
                "de selecties zwak zijn maar dat de twee kansmethodes het structureel oneens zijn "
                "over de RICHTING - en dat is iets anders dan oneens over de grootte. "
                "EN DE REM EROP, WANT DIE IS HIER ONMISBAAR. VIER DAGEN IS GEEN REEKS. §5 "
                "waarschuwt dat een poort structureel alles kan wegvangen en noemt dat een "
                "BEVINDING, maar §6d eist ~30 afgewikkelde gevallen voordat een reeks gelezen mag "
                "worden, en de reeks die deze vraag moet beantwoorden is de SCHADUWREEKS en niet "
                "het aandeel van vandaag. Die reeks staat er: `tweede_methode` staat op 281 "
                "kandidaten, 271 afgewikkeld, trefkans 46,5% en een rendement van +0,1% (+0,34u). "
                "Dat is rond nul - de poort bespaart dus geen geld en kost het ook niet, en dan is "
                "'hij hield vandaag veel tegen' een beschrijving en geen klacht. §1f zegt het nog "
                "scherper: als KANSBRON voegt de splitsmethode vrijwel niets toe (Brier .23674 "
                "tegen .23625), als VETO is ze vandaag ruim driekwart van de run. "
                "WAT HIER NIET UIT VOLGT: er wordt vandaag geen enkele poort, drempel of gewicht "
                "verzet. Dat zou precies de fout zijn die §6d en §1g beschrijven."),

            "DE_CAP_BOND_NIET_MAAR_HIJ_HAD_NUL_MARGE": (
                "55 DUELS IN HET INZETVENSTER OP EEN ZONDAGCAP VAN 55 (`ranking.max_deep_analyses`). "
                "Er is dus NUL afgekapt en elk duel in het venster is doorgerekend - en er was ook "
                "nul marge. Dat is de krapste stand die deze reeks heeft gehad: 7 november had drie "
                "duels marge op 52 van 55, vandaag nul op 55 van 55. "
                "WAAROM DIT HIER STAAT TERWIJL ER NIETS IS AFGEKAPT. §3 Stage 4 verbiedt stille "
                "truncatie, en het spiegelbeeld daarvan is een cap die net niet bond en daarom "
                "nergens wordt genoemd. Eén extra duel vandaag - een FA Cup-replay, een verschoven "
                "aftrap - en de dekkingstabel had een `AFGEKAPT`-regel gehad. "
                "HET BEREIK VAN DE DATARIJKDOM IN DE RUN liep van 3,5 (de vier FA Cup-duels) tot "
                "8,0 (Brighton - Brentford en Vitoria de Guimaraes - FC Porto). De laagste "
                "wedstrijd die het haalde is Wimborne Town - Crawley Town met 3,5 en één markt; er "
                "is geen hoogste die afviel, want er viel niets af. "
                "WAT HIER NIET UIT VOLGT: de cap gaat niet omhoog. Hij is een TIJDSgrens en geen "
                "creditgrens (§0) - de rapporten moeten om 06:30 klaar staan - en de 55 is op "
                "5 september bewust zo gezet."),

            "UNDERSTAT_VALT_VOOR_DE_ZEVENDE_DAG_UIT": (
                "DIT IS DE ENIGE BRONSTORING VAN DE RUN. `scripts/understat.py` geeft voor alle "
                "vijf zijn competities exact dezelfde fout: `UnderstatError: geen JSON terug van "
                "https://understat.com/getLeagueData/<code>/2025 (26719 bytes)`. Vijf competities, "
                "vijf verzoeken, vijf keer EXACT 26.719 bytes - dat is geen storing die voorbijgaat "
                "maar een blokkadepagina of een permanent gewijzigde route. De reeks: 1 nov HTTP "
                "502 op de CONNECT van de netwerkgateway, 3 nov `Connection reset by peer`, 4, 5, "
                "6 en 7 nov 26.719 bytes zonder JSON, vandaag idem. Zevende dag. "
                "WAT HET VANDAAG CONCREET KOST, EN HET IS DE DUURSTE DAG VAN DE REEKS. Understat "
                "dekt PL, La Liga, Bundesliga, Serie A en Ligue 1 (§4), en die vijf hebben vandaag "
                "ALLE VIJF een volle zondagronde: 5 + 5 + 5 + 3 + 6 = 24 van de 55 duels in het "
                "venster. Bij die 24 is er geen TWEEDE, onafhankelijk xG-model naast Fotmob. §4 "
                "noemt dat precies zo: Fotmob-xG en Fotmob-splits zijn twee doorsnedes van DEZELFDE "
                "meting, Understat is een ander xG-model. Het kalibratieblok van §6e mist daardoor "
                "zijn `p_xg_understat`-arm bij alle 24, en die arm groeit vandaag dus niet. Drie "
                "van de vijf gepubliceerde bets staan in die vijf competities (Napoli - Lazio, "
                "Fiorentina - Juventus, Sunderland - Chelsea; Villarreal - Getafe is de vierde). "
                "WAT HET NIET KOST, EN DAAROM STAAT HET NIET VOORAAN IN DE NOTIFICATIE. §2 blijft "
                "gedekt: Fotmob levert en is voor vrijwel elke competitie de xG-bron, dus er is "
                "voor elk duel een onafhankelijke kansinput en geen enkel duel wordt hierdoor "
                "`NONE`. §3 (27 sep 2026) schrijft voor dat de ontbrekende statistiekensleutel pas "
                "vooraan in de notificatie hoort zodra FOTMOB niet meer levert. Dat is vandaag niet "
                "het geval: Fotmob leverde 55 wedstrijdcontexten zonder een enkele fout. "
                "WAT ER WEL UIT VOLGT: de redundantie waarvoor Understat op 31 augustus is "
                "toegevoegd, is zeven dagen weg. Dat is geen actiepunt voor de gebruiker (het is "
                "een bron die zichzelf dichtzet, net als fbref, Forebet, FootyStats en PredictZ - "
                "§3: niet omheen werken) maar het hoort geteld te worden, want als Fotmob ook "
                "omvalt is er niets meer."),

            "DE_PICK_VAN_GISTEREN_OP_NACIONAL_ACADEMICO_VISEU_IS_EEN_DAG_OPGESCHOVEN": (
                "STAGE 0 VOND VANOCHTEND EEN PICK DIE AFWIKKELBAAR LEEK EN DAT NIET WAS, EN DAT IS "
                "HET SOORT FOUT DAT NIET KLAAGT. Run A publiceerde op 7 november Nacional - "
                "Academico Viseu, Over 2.25 @1,85, met aftrap 2026-11-07T15:30Z - zo stond het duel "
                "gisteren in de Fotmob-daglijst van 7 november, met `source_day` 2026-11-07 en "
                "`playable` True, en dat staat zo in `tmp-run/ra_nov07_stage3.json` en "
                "`ra_nov07_cands.json`. Vandaag geeft Fotmob hetzelfde `match_id` 5887676 in de "
                "daglijst van 8 NOVEMBER met aftrap 2026-11-08T15:30Z: exact 24 uur later, en nog "
                "niet gespeeld. "
                "WAAROM DAT GEVAARLIJK WAS. `ledger.py open` kon op de oude datum geen bronstatus "
                "vinden - de wedstrijd stond daar niet meer - en viel daarom terug op "
                "`SETTLE_FALLBACK_HOURS` = 2 uur na de aftrap (§0). Hij bood de pick dus aan als "
                "'klaar om af te wikkelen, 10,6u na aftrap', terwijl er geen uitslag bestond. Was "
                "die klokterugval gevolgd, dan stond er nu een uitkomst in het logboek voor een "
                "wedstrijd die nog moest beginnen. Precies waartegen §0 de statusregel heeft "
                "ingevoerd: `finished` van de bron beslist, de klok is alleen de terugval. "
                "WAT ER IS GEDAAN. Het veld `kickoff` van de pick is bijgewerkt naar de werkelijke "
                "aftrap (2026-11-08T15:30:00.000Z) met de hele toedracht in `notes`; `run_date` "
                "blijft 2026-11-07, want dat is de run die hem publiceerde. Daarna meldt "
                "`ledger.py open` hem weer als 'bron meldt nog niet afgelopen' en wikkelt de run "
                "van morgen hem af op de bron. De pick blijft `pending`. "
                "EN HIJ IS VANDAAG GEEN TWEEDE KEER GEPUBLICEERD. Het duel staat vandaag gewoon in "
                "het venster en is doorgerekend, maar het kwam niet als bet uit de poorten (poort "
                "7: Nacional mist 24% van de selectiewaarde tegen 0% bij Academico Viseu). Had het "
                "wel gekwalificeerd, dan had §1 (0-of-1-bet per wedstrijd) een tweede pick op "
                "hetzelfde duel verboden. "
                "WAT HIER NIET UIT VOLGT: er wordt geen code aangepast op een geval van een. Een "
                "uitgestelde wedstrijd is geen bug in `settling.py` maar de werkelijkheid, en de "
                "terugval van 2 uur is met opzet krap (§0). Wat het wel waard is om te weten: de "
                "klokterugval is in deze situatie onveilig, en een volgende run die hem ziet hoort "
                "eerst te controleren of het duel vandaag of morgen in de daglijst staat voordat "
                "hij hem volgt."),

            "DE_BTTS_REEKS_HAALT_DE_DERTIG_EN_DAT_IS_EEN_VRAAG_VOOR_DE_GEBRUIKER": (
                "§1h HEEFT OP 11 OKTOBER EEN DREMPEL VOOR ZICHZELF GESTELD EN DIE IS VANDAAG "
                "GEHAALD. Punt 2 van die paragraaf houdt BTTS buiten poort 9 met als reden: '15 "
                "afgewikkelde BTTS-picks in beide richtingen samen is geen meting. Dit is het "
                "eerste wat opnieuw bekeken hoort te worden zodra die reeks ~30 haalt.' "
                "DE STAND VANDAAG: 31 afgewikkelde BTTS-picks. Uitgesplitst - en dat is de "
                "uitsplitsing die hier telt, want poort 9 gaat over een KANT en niet over een "
                "markt - staat `BTTS - nee` op 20 gevallen, 45,0% trefkans en -6,2% rendement "
                "(-1,24u), en `BTTS - ja` op 11 gevallen, 63,6% en +37,9% (+4,17u). Gepoold is BTTS "
                "dus POSITIEF (+2,93u over 31, +9,5%), en de kant waar het vermoeden over gaat - "
                "'nee', dezelfde richting als een Under - staat licht negatief op 20 gevallen. "
                "WAT DAT WEL EN NIET ZEGT. De 20 op de 'nee'-kant halen de ~30 van §6d NIET, dus de "
                "uitgesplitste reeks is nog geen meting; alleen de gepoolde haalt de 31, en die "
                "wijst de andere kant op dan het vermoeden. Vergelijk het met de Under-kant: daar "
                "staat -12,5% over 164 gevallen en een gemeten doelpuntenafwijking van +0,612 per "
                "duel bij z = +4,20. Voor BTTS-nee bestaat die tweede, onafhankelijke meting niet - "
                "`margins.py goalbias` splitst op Over/Under en niet op BTTS. "
                "WAAROM DIT ALS VRAAG EN NIET ALS WIJZIGING WORDT OPGESCHREVEN. §1h en §1e "
                "verbieden een run uitdrukkelijk een poort op eigen initiatief te verzetten: 'een "
                "aanleiding om de vraag te stellen is geen automatisme dat een run zelf mag "
                "uitvoeren'. De aanleiding is er nu wel - de drempel die de paragraaf zelf noemde - "
                "en twee van de zes gekwalificeerde selecties van vandaag staan op BTTS-nee. De "
                "vraag gaat daarom EEN keer naar het dagrapport met `owner = \"besluit\"` en wordt "
                "daarna niet herhaald (§6c, §1e). "
                "DE VRAAG ZELF, in een zin: moet poort 9 ook gaan gelden voor BTTS 'nee' op "
                "`FULL`-data, nu de BTTS-reeks de 31 haalt maar de 'nee'-kant op 20 gevallen staat "
                "en licht negatief is - of wachten tot die kant zelf ~30 haalt?"),

            "DE_PINNACLE_VERGELIJKING_VAN_STAP_2": (
                "STAP 2 VAN STAGE 5 - 'wat anderen voorspellen' - is vandaag ingevuld met de enige "
                "vorm die bereikbaar is: de prijs van Pinnacle apart, de-vigd, naast de eigen kans "
                "(§3 Stage 5, 20 sep 2026). Over 46 duels met zowel een Pinnacle-1X2 als een eigen "
                "1X2 is de gemiddelde absolute afstand tot het Pinnacle-oordeel 4,88 pp, bij een "
                "gemiddelde Pinnacle-marge van 3,34%. Op de doelpuntenkant: 47 (duel, lijn)-paren, "
                "gemiddeld verschil op de Under-kant -0,81 pp, en in 19 van de 47 gevallen staat "
                "het model BOVEN Pinnacle. "
                "DE TWEE GEPUBLICEERDE UNDERS ZIJN DE TWEE GROOTSTE UITSCHIETERS VAN DIE 47 "
                "(+18,45 en +15,13 pp boven Pinnacle). Zie "
                "DE_TWEE_UNDERS_STAAN_VER_BOVEN_HET_SCHERPSTE_PUBLIEKE_OORDEEL - dat is het "
                "voorbehoud van de dag en het staat daar uitgeschreven. "
                "HET GROOTSTE 1X2-VERSCHIL ZIT BIJ EEN ANDERE GEPUBLICEERDE REGEL: Union "
                "St.Gilloise - Genk, waar het model de thuisploeg 14,27 pp LAGER zet dan Pinnacle "
                "(0,4535 tegen 0,5962) terwijl de splitsmethode er 0,8694 van maakt. Die twee "
                "methodes staan daar dus ver uiteen in GROOTTE terwijl ze dezelfde richting op "
                "wijzen, en de zwakste stand van het (shrink, rho)-grid is er +1,74 pp. Dat is de "
                "dunste onderbouwing van de zes, en het is ook de regel die op rang 6 buiten de "
                "lijst valt. "
                "HARDE GRENS §2: dit getal staat NIET in `my_prob` en NIET in `prob_sources`. Het "
                "is marktafgeleid en het is andermans lezing; het hoort in de vergelijking en niet "
                "in de kansschatting. Het staat daarom in een eigen blok in `data/run-state/`."),
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
        s3 = json.load(open("tmp-run/ra_nov08_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov08_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov08_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_nov08_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov08_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov08_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

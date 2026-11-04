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

DAG = "2026-11-04"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-04T03:20:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


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
    for run, pad in (("A", "tmp-run/ra_nov04_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "DE_BEVINDING_VAN_DEZE_RUN_ALLE_DRIE_DE_GEKWALIFICEERDE_REGELS_STAAN_OP_DE_GROOTSTE_AFSTAND_VAN_PINNACLE": (
                "DIT IS DE BEVINDING VAN DEZE RUN EN HET IS EEN WAARSCHUWING BIJ DE LIJST, GEEN "
                "REPARATIE EN GEEN BET. Stage 5 stap 2 zet het scherpste publieke expertoordeel "
                "naast de eigen kans, en vandaag valt dat samen met de rangorde van §5b op een "
                "manier die precies niet toevallig is: de DRIE duels met de grootste afstand tot "
                "Pinnacle op de doelpuntenlijn zijn exact de drie duels die alle negen poorten "
                "haalden. "
                "OP DE DOELPUNTENLIJN, 13 (duel, lijn)-paren gemeten: AEK Athens - Real Madrid "
                "P(Under 3.75) Pinnacle 0,494 tegen eigen 0,694 (+20,05 pp, de grootste van de "
                "dag); RB Leipzig - Manchester City P(Under 3.5) Pinnacle 0,465 tegen eigen 0,655 "
                "(+18,98 pp, de tweede); FC Porto - Napoli P(Under 2.75) +14,00 pp (de derde, en "
                "die sneuvelde op de edge-poort). Gemiddeld staat de eigen P(Under) +6,02 pp boven "
                "Pinnacle en bij 10 van de 13 erboven - er is dus een brede Under-lean EN deze "
                "twee zijn de uitschieters erin. "
                "EN LET OP WAAR DE KOERS VAN DE EERSTE BET VANDAAN KOMT, want dat maakt het "
                "scherper dan gisteren: de gepubliceerde koers van AEK Athens - Real Madrid is "
                "Under 3.75 @1,96 van PINNACLE ZELF. De bet wordt dus gespeeld tegen de prijs van "
                "de scherpste bookmaker van de markt, op precies de lijn waarop het model 20 "
                "procentpunt van diens oordeel af staat. Dat is geen bevestiging door een tweede "
                "bron maar het tegendeel ervan. "
                "OP HET 1X2 WIJST HET DEZELFDE KANT OP, EN DAT IS DE OORZAAKKANT. Bij AEK Athens "
                "- Real Madrid geeft Pinnacle Real 0,793 en het model 0,565 - een verschil van "
                "-22,88 pp, het grootste van alle dertien gemeten duels. Het model ziet dus een "
                "veel gelijkwaardiger duel dan de markt, en een gelijkwaardiger duel is een "
                "LAGER scorend duel: daar komt de Under-kans van 69,4% vandaan. Bij PSV Eindhoven "
                "- Club Brugge geeft Pinnacle PSV 0,482 en het model 0,649 (+16,66 pp) - de "
                "tweede grootste afstand, en precies de kant waarop bet twee staat. Gemiddelde "
                "absolute afstand tot het Pinnacle-oordeel over 13 duels: 5,11 pp, bij een "
                "gemiddelde Pinnacle-marge van 3,54%. "
                "WAT DIT BETEKENT VOOR DE LEZING VAN DE DAG. §1g zegt het met cijfers: de "
                "bookmaker schat scherper dan dit model, en wie selecteert op de grootste edge "
                "selecteert op de grootste modelfout. Vandaag is dat geen abstracte waarschuwing "
                "maar een meting op de lijst zelf - de rangorde van vandaag IS de rangorde van de "
                "onenigheid met Pinnacle. Beide gepubliceerde regels krijgen daarom risicoklasse "
                "HIGH en niet Medium, en het staat in de voorbeschouwing onder 'wat de "
                "weddenschap kan slopen'. "
                "HARDE GRENS (§2 / §4): geen van deze Pinnacle-getallen gaat in `my_prob` of in "
                "`prob_sources`. Ze zijn marktafgeleid en horen in de vergelijking, niet in de "
                "kansschatting. Ze veranderen vandaag dus geen enkele kans en geen enkele poort - "
                "ze bepalen alleen hoe de lijst gelezen hoort te worden. Een run verlaagt een "
                "eigen kans niet omdat Pinnacle iets anders zegt; dat zou de anti-circulariteits"
                "regel breken en is precies de fout waarop de correctie van 31 augustus is "
                "ingetrokken."),
            "MAX_LIGHT_IN_SHORTLIST_BINDT_VANDAAG_ECHT_EN_HOUDT_EEN_VOLLEDIG_GEKWALIFICEERDE_BET_TEGEN": (
                "DRIE wedstrijden leverden een selectie op die alle negen poorten haalt EN boven "
                "haar eigen lat staat, en er zijn er TWEE gepubliceerd. Niet omdat de lijst vol "
                "was - `MAX_SHORTLIST` is 3 op woensdag en er staan twee regels in - maar omdat "
                "alle drie op LIGHT staan en `MAX_LIGHT_IN_SHORTLIST` = 2 is (§0). De derde is RB "
                "Leipzig - Manchester City, Under 3.5 @2,078 (Matchbook, beurs, 2,10 bruto), "
                "+18,73 pp tegen de LIGHT-lat van 16,0 en `selection_score` 6,262 - hoger dan "
                "niets in de lijst, want hij is derde op score. Hij is dus niet afgewezen door een "
                "poort en niet verdrongen door een betere bet; hij is weggevallen op de "
                "SAMENSTELLING van de lijst. "
                "DIT IS DE EERSTE KEER DAT DIE GRENS WERKELIJK IETS TEGENHOUDT, en gisteren stond "
                "hij voor het eerst op de rand (twee LIGHT-regels, geen derde kandidaat). Vandaag "
                "is er wel een derde en kost de grens hem. "
                "HIJ IS VASTGELEGD EN NIET STIL WEGGELATEN. De selectie staat als "
                "`gekwalificeerd_niet_gepubliceerd` op de wedstrijd in `data/run-state/` met de "
                "koers, de edge, de score en de rang erbij, EN als `near_miss` met "
                "`failed_gate = \"lijstlengte\"`, zodat `shadow.py collect` hem afrekent. "
                "WAAROM `lijstlengte` EN NIET EEN NIEUWE NAAM. §5b (26 sep 2026) schrijft dat met "
                "zoveel woorden voor: *'Gebruik precies die naam en verzin geen tweede'*, omdat "
                "het EEN vraag is - wat kost de samenstelling van de lijst ons - en twee namen "
                "een populatie in twee reeksen zouden splitsen waarna geen van beide ooit de ~30 "
                "afgewikkelde gevallen haalt die §6d eist. De oorzaak is hier de LIGHT-grens en "
                "niet de lengte, en dat staat in de `reden`-tekst van het blok; de reeks blijft "
                "een reeks. De reeks `lijstlengte` staat vandaag op 21 afgewikkelde gevallen met "
                "+18,3% rendement - boven nul, dus deze afkapping kostte tot nu toe geld in "
                "plaats van dat ze het bespaarde, maar met 21 gevallen is dat onder de ~30 van "
                "§6d en dus nog niet te lezen. "
                "EN TEL `lijstlengte` NOOIT BIJ `edge` OP: `edge` betekent te weinig voordeel, "
                "deze rij betekent genoeg voordeel maar geen plek. "
                "WAT ER NIET IS GEBEURD: de grens is niet verzet. `MAX_LIGHT_IN_SHORTLIST` = 2 "
                "staat in §0 en een run verandert hem niet op eigen initiatief - dat is dezelfde "
                "regel als bij poort 8 (§1e) en poort 9 (§1h). Dat hij vandaag een regel kostte "
                "die op papier gekwalificeerd was, is een aanleiding om de vraag ooit voor te "
                "leggen en geen reden om hem vandaag te negeren. Hij staat er bovendien om een "
                "gemeten reden: LIGHT staat in het logboek op -10,8% over 108 bets tegen -5,9% "
                "over 350 bets op FULL."),
            "TWEE_VAN_DE_DRIE_GEKWALIFICEERDE_REGELS_STAAN_OP_DE_UNDER_KANT_WAAR_DE_SCHEEFSTAND_GEMETEN_IS": (
                "`margins.py goalbias` van vanochtend, over 1996 doorgerekende duels t/m "
                "3 november: het MODEL staat goed (+0,046 doelpunt per duel, z = +1,18) maar de "
                "SELECTIE niet - op de duels waar werkelijk een Under is gespeeld vallen er "
                "+0,597 doelpunt per duel MEER dan de eigen lambda zei, over 124 gevallen, "
                "z = +4,01. De Over-kant staat op -0,268 (z = -1,19 over 66 gevallen). Die twee "
                "regels mogen nooit als een getal worden gelezen: de bovenste meet het model, de "
                "onderste de selectie. "
                "DE VORM: er is massa verschoven van 0-2 naar 4-5 doelpunten, en `P(Under 2.5)` "
                "staat voorspeld 42,5% tegen werkelijk 40,5% - 2,1 procentpunt te hoog bij ELK "
                "duel, voor er iets is gekozen. "
                "VANDAAG STAAN ER TWEE UNDERS BIJ DE DRIE GEKWALIFICEERDE REGELS (AEK Athens - "
                "Real Madrid en de niet-gepubliceerde RB Leipzig - Manchester City) en ze zijn "
                "allebei precies de uitschieter in de Pinnacle-vergelijking hierboven. Dat is "
                "hetzelfde patroon dat §6g beschrijft, nu op een dag waarop het aan twee kanten "
                "tegelijk zichtbaar is. "
                "WAT ER VANDAAG AL IN ZIT: `model.LEVEL_SCALE` = 1.032 bindt sinds gisteren en "
                "schroeft de lambdas van de xG-methode 3,2% op, wat `P(Under)` ongeveer twee "
                "procentpunt VERLAAGT. De kansen hierboven zijn dus AL gecorrigeerd - trek er "
                "niet nog eens twee procentpunt af, want dan tel je dezelfde correctie twee keer. "
                "De gemeten scheefstand in deze alinea komt juist uit de lambdas van VOOR die "
                "knop (alles t/m 2 november levert ongecorrigeerde lambdas, 3 november de eerste "
                "gecorrigeerde) en beschrijft de fout die de knop moet wegnemen, niet de stand "
                "erna. Met twee rundagen gecorrigeerde lambdas is daarover nog niets te zeggen; "
                "reken op maanden (§6g punt 4, `gridfit.LEVEL_SWITCH`). "
                "EN DE REM DIE ER NIET BIJ KOMT: beide Unders staan op LIGHT en `unders.TIERS` is "
                "`(\"FULL\",)`, dus poort 9 raakt ze niet. Zie "
                "POORT_9_RAAKT_GEEN_VAN_DE_TWEE_UNDERS_VAN_VANDAAG_EN_DAT_IS_EEN_BESLUIT."),
            "POORT_9_RAAKT_GEEN_VAN_DE_TWEE_UNDERS_VAN_VANDAAG_EN_DAT_IS_EEN_BESLUIT": (
                "Beide Under-regels van vandaag staan op LIGHT en `unders.TIERS` is "
                "`(\"FULL\",)`, dus poort 9 komt er niet aan. Dat is geen omissie maar het besluit "
                "van de gebruiker van 12 oktober 2026 (§1h, '`LIGHT` blijft erbuiten - gevraagd "
                "en beantwoord'): *'Twee hoeft nog niet op de zwakke data; eerst kijken wat deze "
                "rem doet.'* De vraag is gesteld en beantwoord en hoort niet opnieuw te worden "
                "gesteld; deze regel legt vast dat de stilte een keuze is. "
                "DE REEKS DIE DIE VRAAG MOET BEANTWOORDEN IS INMIDDELS LEESBAAR EN ZEGT DAT DE "
                "REM WERKT. `doelpunten_onder` staat op 35 afgewikkelde kandidaten met een "
                "trefkans van 37,1% en -30,4% rendement. Dat is boven de ~30 die §6d eist, en het "
                "teken zegt dat de poort verliezers tegenhoudt in plaats van winnaars. Dat is een "
                "aanleiding om de vraag over LIGHT ooit opnieuw voor te leggen, GEEN automatisme "
                "dat een run zelf mag uitvoeren (§1e en §1h zeggen dat allebei expliciet). Hij "
                "wordt vandaag dus alleen genoemd onder 'Stand van het logboek', zoals elke "
                "andere reeks. "
                "WAT HET VANDAAG CONCREET KOST OF OPLEVERT IS NUL: poort 9 heeft vandaag nul "
                "selecties tegengehouden, want er was geen enkele FULL-Under met een edge in de "
                "band 8-10 pp waarin hij bindt. De enige FULL-wedstrijd van de dag (Wrexham - "
                "Middlesbrough) sneuvelde op poort 5."),
            "DE_VIJF_POORTEN_VAN_PARAGRAAF_1_ZIJN_ALLE_VIJF_NAGELOPEN": (
                "De bevestiging door een tweede methode is OP DE RUNLIJST ZELF gedaan en niet "
                "alleen op de analyse, zoals Run A sinds 11 oktober doet: de Fotmob-daglijst "
                "naast de BetExplorer-fixturepagina per competitie, twee losse bronnen. Ze zijn "
                "het over ALLE ZESTIEN competities eens en over het totaal: 14 duels tegen 14, "
                "zonder enig verschil - negen in de Champions League, drie in de Championship, "
                "een in de Europa League en een in de Belgian Pro League. "
                "DE VIJF BEKERS SPELEN NIET, EN OOK DAT IS BIJ TWEE BRONNEN NAGETROKKEN. De "
                "Fotmob-daglijst geeft voor League Cup (133), DFB Pokal (209) en KNVB Beker (235) "
                "nul duels in het venster, en BetExplorer bevestigt dat voor alle vijf met de "
                "eerstvolgende ronde erbij: FA Cup 6 nov, Coppa Italia 1 dec, KNVB Beker 1 dec, "
                "DFB Pokal 1 dec, League Cup 15 dec. Alle vijf fixturepagina's gaven vandaag "
                "teamparen (40, 4, 8, 16 en 8), dus er is nergens een lege pagina die als "
                "bevestiging zou kunnen worden gelezen. 'Niet in de daglijst' mag nooit als GEEN "
                "WEDSTRIJD worden opgeschreven zonder tweede bron; dat is het gat dat Run A op "
                "6 oktober 2026 vijf duels kostte. "
                "EEN WAARNEMING OVER DE TIJDZONE VAN BETEXPLORER, want de docstring van "
                "`ra_nov04_bevestiging.py` beweert iets anders dan de cijfers. Die tekst zegt dat "
                "`MatchOdds.when` UK-tijd is (NL -1 uur). Vandaag geeft BetExplorer voor de "
                "Champions League 'Today 18:45' en 'Today 21:00' en voor de Europa League "
                "'Today 16:30' - exact dezelfde klok als de Fotmob-tijden in NL (17:45Z = 18:45 "
                "NL, 20:00Z = 21:00 NL, 15:30Z = 16:30 NL). Op deze pagina's staat dus CET en "
                "geen UK-tijd. Dat raakt vandaag niets: de gepubliceerde aftraptijden komen uit "
                "`kickoff_utc` van Fotmob via `zoneinfo` en niet uit BetExplorer, en de "
                "venstertoets van dat script werkt met een grens om 07:00 waar geen duel van "
                "vandaag in de buurt komt. Maar het is wel een onware regel in een docstring, en "
                "op een dag met een duel tussen 07:00 en 08:00 zou ze de tweede bron een duel "
                "laten missen. Opgeschreven als openstaand punt, niet gerepareerd - de aanname "
                "hoort per pagina gemeten te worden en niet per run geraden. "
                "DE TWEE ANDERE EUROPESE TOERNOOIEN: de Conference League speelt donderdag "
                "(5 november) en de Europa League heeft vandaag EEN duel in het venster "
                "(Rennes - Olympiacos, 16:30 NL) en de rest donderdag. De Premier League, Serie "
                "A, La Liga, Bundesliga, Ligue 1, Eredivisie, Primeira Liga, Super Lig, Scottish "
                "Premiership, Danish Superliga en Ekstraklasa hebben vandaag geen ronde - die "
                "spelen in het weekend van 6-8 november. Dat is `GEEN WEDSTRIJD` en geen gat. "
                "DE DERDE POORT, DE ANTI-CIRCULARITEIT (§2), IS PER BET NAGELOPEN: de kansinputs "
                "van beide regels komen uit Fotmob team-xG, de Fotmob-doelpuntensplits en de "
                "Fotmob-wedstrijdcontext, en bij beide Champions League-duels uit de omgerekende "
                "binnenlandse verhoudingen van `scripts/interleague.py`. Geen van die getallen is "
                "van een bookmaker of een odds-aggregator afgeleid. Het Pinnacle-oordeel en het "
                "BetExplorer-marktgemiddelde staan ERNAAST en in geen enkele `prob_sources`-lijst "
                "- ook niet bij AEK Athens - Real Madrid, waar de gepubliceerde KOERS van "
                "Pinnacle komt. Een koers is geen kansinput; dat onderscheid is precies wat §2 "
                "hard maakt."),
            "DE_AFKAPPING_VAN_STAGE_4_BINDT_VANDAAG_NIET": (
                "Veertien duels in het inzetvenster tegen een cap van 40 (`MAX_DEEP_ANALYSES`, "
                "woensdag), dus er is NUL afgekapt en alle veertien zijn doorgerekend. De "
                "datarijkdom-score liep van 5,0 tot 7,5; die twee getallen staan hier omdat §3 "
                "Stage 4 ze eist zodra de cap knelt, en ze staan er ook als hij dat niet doet - "
                "anders is achteraf niet na te gaan of de afkapping ergens op sloeg. De Europese "
                "duels scoren met 5,0 tot 7,5 hoger dan de vier binnenlandse met 5,0 tot 6,0, en "
                "dat komt vrijwel helemaal uit het opstellingsblok: om 03:00 NL staat er voor een "
                "avondduel in de Champions League al een voorspelde opstelling en voor de "
                "Championship nog niet. "
                "EEN DUEL VIEL AF OP `data_tier = NONE`: Slavia Prague - Arsenal, op de "
                "kruis-grensomrekening van §4. De omgerekende VERDEDIGING van Arsenal is 0,373 en "
                "valt BUITEN het gemeten bereik 0,388-1,446 (binnenlandse verhouding 0,517 over "
                "38 duels, Europese competitiefactor x1,623/0,609 over 400 Europese duels). Dat is "
                "`in_range` die precies doet waarvoor hij bestaat - de Coventry-val - en §2 zegt "
                "dat een ontbrekende onafhankelijke input GEEN BET betekent en niet 'LIGHT met "
                "lage confidence'. Het kost wel het duel waar vandaag veel publiek naar kijkt, en "
                "dat hoort erbij te staan in plaats van als een nette nul in de tabel te "
                "verdwijnen. Let op de richting: Arsenal valt eruit omdat het model hem na "
                "omrekening STERKER inschat dan alles wat ooit gemeten is (een verdediging van "
                "0,373 is beter dan het beste gemeten punt), niet zwakker. "
                "DE ANDERE NEGEN EUROPESE DUELS STAAN OP LIGHT EN NOOIT OP FULL, want de "
                "omrekening haalt de systematische fout eruit en niet de onzekerheid (§4, "
                "8 september). Daar geldt de lat van 16,0 pp, en drie van de negen halen hem. "
                "DRIE VAN DE VIER BINNENLANDSE DUELS STAAN OP LIGHT omdat er een omgerekende "
                "ploeg in staat: West Ham United en Wolverhampton Wanderers (degradanten uit de "
                "Premier League), Cardiff City (promovendus naar de Championship) en Kortrijk "
                "(promovendus in Belgie). Geen van die drie haalt de LIGHT-lat. Het vierde, "
                "Wrexham - Middlesbrough, is de ENIGE FULL-wedstrijd van de dag en sneuvelde op "
                "poort 5: de twee methodes verslaan de markt niet dezelfde kant op ('data "
                "conflicterend')."),
            "HET_NIVEAU_KOMT_VOOR_TWEE_COMPETITIES_UIT_DE_UPLIFT_EN_VOOR_DE_EUROPESE_DUELS_NIET_UIT_EEN_COMPETITIE": (
                "`league_level` is vandaag voor TWEE competities aangeroepen, beide route "
                "`vorig+uplift` (lopend seizoen onder de helft van `SEASON_MATURE_SHARE`): de "
                "Championship op niveau 1,511 thuis / 1,300 uit / basis 1,389 (14 van 46 "
                "speeldagen) en de Belgian Pro League op 1,497 / 1,326 / basis 1,534 (10 van 30). "
                "DE CHAMPIONS LEAGUE EN DE EUROPA LEAGUE GAAN NIET LANGS `league_level` maar langs "
                "`scripts/interleague.py`: een toernooi met ploegen uit verschillende landen heeft "
                "geen eigen competitieniveau om op te normaliseren, en zijn eigen stand zou een "
                "mengsel van zeventien competities zijn (§4, Kruis-grens). Het Europese "
                "referentieniveau is thuis 1,572 / uit 1,179. "
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP factor 1,0790 (gepoold 1,1024) OVER "
                "27 SPEELDAGEN IN DRIE COMPETITIES. Met drie waarnemingen is de pool smal - "
                "normaal zijn het zeven tot dertien competities - dus de correctie is gevoeliger "
                "voor wat deze drie doen dan op een gewone dag. Dat is geen fout en vraagt geen "
                "ingreep (de correctie is op xG-waarnemingen gemeten en wordt nooit op de markt "
                "bijgeregeld, §3 Stage 5), maar het is wel de reden dat de niveaukeuze vandaag met "
                "minder zekerheid staat dan het getal suggereert. "
                "`vroeg_seizoen.overgeslagen` IS NIET LEEG, en dat hoort hier te staan: de "
                "Champions League is uit de pool gelaten omdat hij halverwege zijn seizoen is "
                "(4 van 8 speeldagen), dus zijn niveau komt uit het lopende seizoen zelf en niet "
                "uit de gepoolde correctie. Een stil weggelaten waarneming is hetzelfde probleem "
                "als een stille truncatie in Stage 4, dus dat staat er met de reden erbij."),
            "DE_CREDITS_EN_DE_MARKTBALANS": (
                "`api_check.py` gaf 19.808 credits over en 192 verbruikt deze maand; "
                "`suggest_cap(19808, 27)` geeft een plafond van 366 voor deze run. Uitgegeven: 12 "
                "aan de bulk-aanroep (h2h + spreads + totals, 3 credits per competitie, voor alle "
                "vier de inkoopbare competities) en 10 aan BTTS per wedstrijd, samen 22 van 366. "
                "Daarna nog 19.786 over. "
                "DE MARKTBALANS VAN §1a IS OP DE INKOOP GEHAALD, EN RUIM: alle vier de "
                "competities kregen zowel een uitkomstmarkt (1X2 op de beste prijs, Asian "
                "Handicap, Draw No Bet uit de 0.0-lijn, Double Chance uit de +-0.5-lijn) als een "
                "doelpuntenmarkt (Over/Under). Vier van de vier, niet een van de twaalf zoals op "
                "30 augustus. `split_budget(366, 4)` gaf (4, 4), dus het plafond was ruim genoeg "
                "om elke competitie beide kanten te geven. "
                "GEEN ENKEL DUEL LEUNT OP HET GRATIS BETEXPLORER-MARKTGEMIDDELDE voor de bet "
                "zelf: alle vier de competities hebben een sportkey, dus alle veertien duels "
                "hebben een beste prijs met een herleidbare bookmaker. Het BetExplorer-gemiddelde "
                "is voor alle vier opgehaald en gebruikt waar het hoort - het kalibratieblok van "
                "§6e en poort 8 (wie de markt de mindere ploeg vindt). Gemiddelde om te meten, "
                "beste prijs om te spelen. "
                "BTTS IS VOOR 10 VAN DE 14 DUELS GEKOCHT, op de vereniging van beide schalen "
                "(§1a stap 2, 13 september): een duel krijgt BTTS zodra minstens een selectie de "
                "herijkte NEAR-drempel of de volle drempel op de RUWE schaal haalt. De vier duels "
                "die geen BTTS kregen staan in `markets_checked` met de reden erbij - 'niet "
                "opgevraagd - geen kandidaat-edge in dit duel' - en niet als gat. Daaronder het "
                "NONE-duel Slavia Prague - Arsenal, waar per definitie geen markt door te rekenen "
                "valt. "
                "DRIE SPORTKEYS VAN DE REPO STONDEN VANDAAG NIET ACTIEF bij The Odds API: Coppa "
                "Italia, English League Two en League Two. Die eerste staat in deze runlijst en "
                "speelt vandaag niet (eerstvolgende ronde 1 december), dus het is dezelfde "
                "bevinding langs twee wegen en geen storing. De andere twee horen bij Run B. "
                "`api_check.py` noemt daarnaast zes actieve sportkeys die de repo niet kent "
                "(Brazil Serie B, Frauen-Bundesliga, 3. Liga, Copa del Rey, Superettan, UEFA "
                "Nations League); geen daarvan staat in de runlijst van Run A."),
            "DE_TWEE_GEPUBLICEERDE_KOERSEN_STAAN_BEIDE_BIJ_EEN_GEWONE_BOOKMAKER_EN_NIET_BIJ_EEN_BEURS": (
                "Anders dan gisteren, toen alle drie de regels bij Matchbook stonden: vandaag "
                "komt geen van beide gepubliceerde koersen van een beurs, dus er gaat GEEN "
                "commissie af en de koers op het scherm van de gebruiker is de koers waarmee "
                "`edge_pp` is gerekend. AEK Athens - Real Madrid, Under 3.75 @1,96 bij PINNACLE; "
                "PSV Eindhoven - Club Brugge, 1 @2,13 bij 1xBet (beste prijs over alle "
                "aanbieders). "
                "DAT DE EERSTE KOERS VAN PINNACLE KOMT IS GEEN TOEVAL EN GEEN GERUSTSTELLING. "
                "Pinnacle is de scherpste bookmaker van de markt en zet de laagste marge (vandaag "
                "3,4% op deze lijn, 3,54% gemiddeld over de dag); dat hij hier de beste prijs "
                "heeft, betekent dat de rest van de markt er NOG verder van af staat dan het "
                "model - niet dat Pinnacle het met het model eens is. Hij is het juist maximaal "
                "oneens: 20 procentpunt op precies deze lijn. Zie "
                "DE_BEVINDING_VAN_DEZE_RUN_ALLE_DRIE_DE_GEKWALIFICEERDE_REGELS_STAAN_OP_DE_"
                "GROOTSTE_AFSTAND_VAN_PINNACLE. "
                "DE ZWAKSTE STAND VAN HET (shrink, rho)-GRID STAAT BIJ BEIDE RUIM BOVEN NUL: "
                "+17,96 pp bij AEK Athens - Real Madrid en +13,45 pp bij PSV Eindhoven - Club "
                "Brugge. Poort 6 gaat dus bij beide met marge open, en bij de niet-gepubliceerde "
                "derde regel ook (+13,25 pp). Let op wat poort 6 hier NIET zegt (§6e, slotalinea): "
                "het grid varieert alleen `analyze_match`, en dat is juist de methode die vlak "
                "blijkt. 'Deze bet overleeft het hele grid' zegt dus niets over de splitsmethode, "
                "en die staat bij AEK Athens - Real Madrid op +31,9 pp tegen +18,4 pp voor de "
                "xG-methode - een verschil van dertien procentpunt tussen de twee schatters van "
                "dezelfde grootheid. Poort 5 is gehaald (beide verslaan de markt dezelfde kant "
                "op), maar de spreiding hoort gelezen te worden."),
            "WAT_ER_AFGEWIKKELD_IS": (
                "Stage 0 heeft VIER picks en DERTIEN schaduwrijen afgewikkeld, alle zeventien van "
                "3 november. Bij de picks: 3 gewonnen en 1 VOID, nul verloren. Bij de "
                "schaduwrijen: 3 gewonnen en 10 verloren. "
                "DE VIER PICKS. Bodo/Glimt - Lille 0-0, Under 3.5 -> gewonnen. Barcelona - Aston "
                "Villa 3-0, Under 4.5 -> gewonnen. Sirius - Halmstads BK 2-0, Under 3.5 -> "
                "gewonnen (dat was de Run B-pick van gisteren). West Bromwich Albion - "
                "Southampton 1-1, Draw No Bet Southampton -> VOID: bij een gelijkspel komt de "
                "inzet terug, dus dit is geen verlies maar een teruggave. "
                "ALLE VIER DE DUELS WAREN LEAGUE- OF COMPETITIEWEDSTRIJDEN ZONDER VERLENGING "
                "(Champions League-leaguefase, Championship, Allsvenskan), dus `status.scoreStr` "
                "van Fotmob IS de stand na 90 minuten en er hoefden geen doelpuntminuten te "
                "worden opgezocht (§0 / §6d). Dat is per duel nagegaan en niet aangenomen. "
                "DE REFLECTIE (§3 Stage 0, 12 okt 2026) STAAT IN HET DAGRAPPORT, maar het "
                "feitelijke deel hier: de drie gewonnen picks waren alle DRIE Unders, en twee van "
                "de drie wonnen op een uitslag die VER onder de eigen verwachting lag - 0-0 waar "
                "het model op 2,6 doelpunten zat en 2-0 waar het op 3,0 zat. Dat is gewonnen EN "
                "verkeerd ingeschat, precies het onderscheid dat Stage 0 sinds 12 oktober vraagt. "
                "Barcelona - Aston Villa 3-0 lag met drie doelpunten wel dicht bij de 3,5 die het "
                "model verwachtte. Lees dit niet als een reeks: drie Unders op een dag is geen "
                "waarneming over de Under-kant, en de lopende reeks van 124 gevallen zegt het "
                "tegenovergestelde (+0,597 doelpunt per duel TE WEINIG voorspeld, z = +4,01). Een "
                "dag die de andere kant op valt verandert daar niets aan (§6d). "
                "BIJ DE SCHADUWRIJEN deed de dag wat hij hoorde te doen: 10 van de 13 verloren, "
                "dus de poorten hielden overwegend verliezers tegen. De drie die wonnen: "
                "Manchester United - Roma (DNB United, viel af op `edge`), Wigan Athletic - "
                "Mansfield Town 0-0 (AH +0.25, viel af op `underdog`, HALVE winst op de kwartlijn) "
                "en Northampton Town - Oldham Athletic 0-1 (AH +0.25, idem). De duurste misser van "
                "de poorten is er geen: Villarreal - Paris Saint-Germain werd 0-6 en zowel de "
                "Under 3.5 als de handicap Villarreal +1.5 ging daar kansloos onderuit - twee "
                "rijen die de poorten terecht hebben tegengehouden. "
                "`calibration.py settle` EN `ctxlog.py settle` ZIJN BEIDE GEDRAAID, en dat is geen "
                "formaliteit (§6b-5c): 60 kalibratiewaarnemingen en 22 contextwedstrijden "
                "afgewikkeld. `recalibrate.load_fit().fitted_through` staat daarna op 2026-11-03 - "
                "de vorige rundag, dus de herijking van §1g rekent niet op een oude stand. Dat "
                "getal staat hier omdat het in september elf dagen stil is weggevallen."),
            "STAGE_MIN_2_DE_BRANCHES_WAREN_SCHOON_EN_DE_RUN_STAAT_OP_MAIN": (
                "De container kreeg de repo als ONDIEPE KLOON (`--is-shallow-repository` -> true, "
                "met twee grafted roots in `.git/shallow`), en dat is precies de val die §3 Stage "
                "-2 beschrijft: voor het unshallowen telde `git rev-list --count HEAD..<tak>` "
                "voor 77 van de 84 takken tientallen tot 604 'eigen' commits, met een LEGE "
                "`merge-base` - het ziet er dan uit als het echte geval van 10 augustus. Na "
                "`git fetch --unshallow origin` (53 -> 689 commits lokaal) heeft GEEN ENKELE van "
                "de 84 takken nog een eigen commit en is elke tak een voorouder van HEAD. "
                "EN DE CONTROLE IS OP DE INHOUD GEDAAN EN NIET OP DE COMMITGRAAF, want §3 Stage "
                "-2 (27 sep 2026) zegt met zoveel woorden dat '0 eigen commits' een uitspraak "
                "over de graaf is en niet over de metingen. Alle vier de regelgebaseerde "
                "logboeken zijn per RECORD-ID vergeleken over alle 84 takken tegen HEAD: "
                "`picks.jsonl` 520 id's, `shadow.jsonl` 1673, `calibration.jsonl` 2407, "
                "`context-log.jsonl` 1997 - en de vereniging over alle takken is in alle vier de "
                "gevallen exact gelijk aan wat HEAD al heeft. Nul ontbrekende records. Er is ook "
                "in de andere richting gekeken: geen enkele tak heeft een rij die daar is "
                "AFGEWIKKELD terwijl HEAD hem nog op `pending` heeft. Er viel dus niets te "
                "verenigen - niet op de graaf en niet op de inhoud. "
                "DE RUN STAAT OP `main`. De sessie is op branch `claude/stoic-davinci-kdt8hq` "
                "gezet en die stond bij binnenkomst exact gelijk aan `origin/main` (c88ba81); er "
                "wordt gepusht met `git push origin HEAD:main` zoals §6a voorschrijft, met "
                "expliciete toestemming uit de scheduler-tekst."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. BINDT VANDAAG WEL, en voor het eerst om de LIGHT-grens en niet om de
        # lengte: er zijn DRIE wedstrijden met een selectie die alle negen poorten haalt EN boven
        # haar eigen lat staat, er zijn drie plekken (MAX_SHORTLIST = 3, woensdag), en er worden er
        # TWEE gepubliceerd — want alle drie staan op LIGHT en MAX_LIGHT_IN_SHORTLIST = 2 (§0).
        # `toplist._cap_light` laat de derde stil vallen; deze lus is het verschil tussen een
        # gemeten reeks en een stille weglating. Hij legt zo'n gekwalificeerde selectie vast als
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
        s3 = json.load(open("tmp-run/ra_nov04_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov04_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov04_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_nov04_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov04_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov04_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

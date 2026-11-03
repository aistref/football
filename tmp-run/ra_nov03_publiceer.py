"""Run A 3 nov 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_nov02_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag en twee reparaties in de tekstopbouw (zie hieronder). TWEE van de eenentwintig
competities uit de runlijst speelden, met ACHTTIEN duels in het inzetvenster: de volledige
Championship-speelronde van negen en de negen Champions League-duels van speelronde 4. De
overige elf competities, de vijf bekers en de twee andere Europese toernooien spelen vandaag
niet.

DRIE REGELS, WAARVAN TWEE HUN EIGEN LAT HALEN. Beide Unders op LIGHT in de Champions League
halen de lat van 16,0 pp; de Draw No Bet in de Championship staat op rangorde in de lijst met
+4,88 pp tegen een lat van 8,0. Zie DRIE_REGELS_WAARVAN_TWEE_HUN_LAT_HALEN.

DE NIVEAUCORRECTIE VAN §6g BINDT VANDAAG VOOR HET EERST (`model.LEVEL_SCALE` = 1.032,
`LEVEL_SCALE_BINDS_FROM` = 3 nov 2026). Zie DE_NIVEAUCORRECTIE_BINDT_VANDAAG_VOOR_HET_EERST.

DE BEVINDING VAN DEZE RUN IS EEN ONWARE TEKST BIJ EEN GEPUBLICEERDE BET, NIET EEN BET.
`bet_beide = False` heeft DRIE standen en de notes-tekst had er twee; de derde kwam vandaag voor
het eerst voor en kreeg daardoor de verkeerde. Zie
DE_BEVINDING_VAN_DEZE_RUN_EEN_DERDE_STAND_VAN_bet_beide_DIE_EEN_ONWARE_TEKST_KREEG.

EN EEN GESTAAKT DUEL DAT GEEN UITSLAG IS. Tenerife - FC Andorra staat bij Fotmob op
`finished = true` met een tussenstand en `reason.long = Abandoned`; twee schaduwrijen zijn
daardoor `void` in plaats van `lost`. Zie
WAT_ER_AFGEWIKKELD_IS_EN_EEN_GESTAAKT_DUEL_DAT_GEEN_UITSLAG_IS.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-11-03"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-03T03:05:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


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
                      + (("ONDER-KANT, EN VANDAAG MET EEN KNOP ERBIJ. §6g meet dat de "
                          "gespeelde Under-kant scheef staat, en dat is vanmorgen opnieuw "
                          "gemeten over 1976 doorgerekende duels: P(Under 2.5) voorspeld 42,5% "
                          "tegen werkelijk 40,3% (-2,2 pp), massa verschoven van 0 en 2 "
                          "doelpunten naar 4 en 5, en op de duels waar werkelijk een Under is "
                          "gespeeld +0,651 doelpunt per duel over 121 gevallen (z = +4,32) "
                          "terwijl de Over-kant op -0,268 staat (z = -1,19 over 66 gevallen). "
                          "WAT ER VANDAAG VERANDERT: `model.LEVEL_SCALE` = 1.032 bindt vanaf "
                          "vandaag (§0, §6g 'Het besluit van 2 november 2026') en schroeft de "
                          "lambdas van de xG-methode 3,2% op, wat P(Under) ongeveer twee "
                          "procentpunt VERLAAGT. De kans hierboven is dus AL gecorrigeerd - trek "
                          "er niet nog eens twee procentpunt af, want dan tel je dezelfde "
                          "correctie twee keer. De cijfers in deze alinea komen juist uit de "
                          "lambdas van VOOR die knop (alles t/m 2 november) en beschrijven de "
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
                            "niveaucorrectie van vandaag is wat daarvoor in de plaats is "
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
    for run, pad in (("A", "tmp-run/ra_nov03_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "DE_NIVEAUCORRECTIE_BINDT_VANDAAG_VOOR_HET_EERST": (
                "`model.LEVEL_SCALE` = 1.032 met `LEVEL_SCALE_BINDS_FROM` = 3 november 2026, dus "
                "VANDAAG is de eerste rundag waarop de lambdas van de xG-methode 3,2% hoger "
                "staan (§0 en §6g, 'Het besluit van 2 november 2026'). Elke aanroep van "
                "`analyze_match` en `robustness_check` in `ra_nov03_analyze.py` krijgt "
                "`today=DAY` mee - NEGEN plekken, en ze zijn met een assert per plek nagelopen "
                "in plaats van geteld. Zonder dat argument kijkt `model.level_scale` naar de "
                "systeemklok, en dan krijgt een herberekening van een oudere dag stil de "
                "correctie van vandaag; `margins.py` en `gridfit.py` rekenen op de OPGESLAGEN "
                "lambdas, dus dat zou juist de meting vervuilen waarmee deze knop beoordeeld "
                "moet worden. "
                "DE SPLITSMETHODE KRIJGT HEM NIET. `analyze_match_from_splits` kent geen "
                "`scale` en hoort die niet te krijgen (§6g punt 1), dus de correctie werkt voor "
                "80% door in `my_prob` - het gewicht van de xG-methode uit §1f. "
                "DE UNDERSTAT-ARM KRIJGT HEM WEL, en dat is een keuze van deze run die hier "
                "staat zodat ze na te lopen is: §6e vergelijkt twee xG-modellen, en een van de "
                "twee schalen zou die vergelijking over de correctie laten gaan in plaats van "
                "over het model. Vandaag maakt het niets uit - Championship en Champions League "
                "zitten niet in de vijf competities van Understat, dus er is vandaag geen "
                "Understat-arm. "
                "WAT DE KNOP VANDAAG DOET IS NIET TE ZIEN EN DAT HOORT ERBIJ. Hij verlaagt "
                "`P(Under)` ongeveer twee procentpunt bij elk duel, en de twee Under-regels van "
                "vandaag staan dus al LAGER dan ze gisteren hadden gestaan. Of dat de scheefstand "
                "van §6g werkelijk wegneemt is pas te meten als er genoeg duels van NA vandaag "
                "liggen; `margins.py goalbias` meet op opgeslagen lambdas en die zijn t/m "
                "2 november allemaal ongecorrigeerd. §1h zegt met zoveel woorden dat poort 9 tot "
                "die tijd onveranderd blijft en dat een run hem niet op eigen initiatief verzet."),
            "DRIE_REGELS_WAARVAN_TWEE_HUN_LAT_HALEN": (
                "De dagranglijst van §5b heeft DRIE regels en `MAX_SHORTLIST` is 3 (dinsdag), dus "
                "de lijst is precies vol. TWEE van de drie halen hun eigen lat: Bodo/Glimt - "
                "Lille, Under 3.5 @1,7154 (Matchbook, beurs, 1,73 bruto) met +16,87 pp tegen de "
                "LIGHT-lat van 16,0 pp, score 6,341; en Barcelona - Aston Villa, Under 4.5 "
                "@1,7448 (Matchbook, beurs, 1,76 bruto) met +16,23 pp tegen diezelfde lat, score "
                "5,968. DE DERDE STAAT ER OP RANGORDE: West Bromwich Albion - Southampton, Draw "
                "No Bet Southampton @2,0388 (Matchbook, beurs, 2,06 bruto) met +4,88 pp tegen de "
                "FULL-lat van 8,0 pp, score 2,632 - ruim drie procentpunt onder de lat, en hij "
                "staat in de lijst omdat §5b sinds 20 september de rangorde laat beslissen zodra "
                "er minder dan `MAX_SHORTLIST` selecties boven hun lat staan. "
                "`MAX_LIGHT_IN_SHORTLIST` = 2 bindt vandaag EXACT: er staan twee LIGHT-regels in "
                "de lijst en dat is het maximum, dus een derde LIGHT had er niet bij gekund. Dat "
                "is vandaag geen beperking die iets heeft tegengehouden - er was geen derde "
                "LIGHT-kandidaat die de lijst haalde - maar het is het eerste moment sinds "
                "26 oktober dat de grens op de rand staat. "
                "DE ZWAKSTE STAND VAN HET (shrink, rho)-GRID STAAT BIJ ALLE DRIE BOVEN NUL: "
                "+13,77, +14,04 en +1,30 pp. Die laatste is krap en dat hoort erbij - bij West "
                "Bromwich - Southampton zakt de edge over het grid tot anderhalve procentpunt, "
                "dus poort 6 gaat open met de kleinst mogelijke marge. "
                "LEES DE LIJST ALS 'DIT IS HET BESTE VAN VANDAAG' EN NIET ALS 'DIT IS EEN "
                "GEVONDEN VOORDEEL': §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN "
                "drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het "
                "slechtst is bij de hoogste geclaimde edge. Het logboek staat vandaag op -7,7% "
                "over 455 afgewikkelde bets, en §5b zegt zelf dat ongeveer -10% is wat je van "
                "deze lijst mag verwachten."),
            "DE_BEVINDING_VAN_DEZE_RUN_EEN_DERDE_STAND_VAN_bet_beide_DIE_EEN_ONWARE_TEKST_KREEG": (
                "DIT IS DE BEVINDING VAN DEZE RUN EN HET IS EEN REPARATIE IN DE VASTLEGGING, GEEN "
                "BET. Barcelona - Aston Villa, Under 4.5, is de eerste GEPUBLICEERDE bet met "
                "`failed_gate = None` en `bet_ruw = False`: herijkt haalt hij zijn LIGHT-lat met "
                "+16,23 pp WEL en ruw met +15,39 pp NIET. Dat is de spiegel van de reeks "
                "`herijking` - `herijking_omgekeerd`, mogelijk sinds de fit van 20 september een "
                "kans in deze band juist VERHOOGT in plaats van verlaagt (vandaag a=1,026, "
                "b=+0,017: +0,8 pp op 70%). "
                "WAT ER STUK WAS. De `notes`-tekst bij een pick had TWEE takken voor "
                "`bet_beide = False` - 'haalt hem ruw wel en herijkt niet' en 'haalt hem nergens' "
                "- en deze derde stand kreeg daardoor de tweede tekst: *'deze selectie haalt haar "
                "lat op GEEN van beide schalen en is op rangorde gepubliceerd, niet op een "
                "gevonden voordeel'*. Dat is ONWAAR voor deze bet: hij haalt zijn lat op de "
                "schaal waarop gepubliceerd wordt, en hij staat niet op rangorde in de lijst maar "
                "op zijn eigen voordeel. Erger dan onnauwkeurig: de notes van een pick zijn wat "
                "een latere run en het dagrapport teruglezen, en een pick die zichzelf te laag "
                "aanslaat is net zo misleidend als een die zichzelf te hoog aanslaat. "
                "`bet_beide` is EEN BIT VOOR DRIE STANDEN, en dat is de les. De drie zijn alleen "
                "uit `failed_gate` EN `failed_gate_ruw` samen te lezen. De tekst heeft nu drie "
                "takken, op precies die twee velden. "
                "DEZELFDE STILLE FAALVORM ALS TWEE KEER EERDER, en dat is waarom dit de bevinding "
                "is en geen voetnoot: niets klaagde. `scripts/ledger.py validate` is groen, "
                "`progress.py verify` is groen, de pick is geldig volgens het schema en de pagina "
                "rendert. Precies zoals bij `calibration.py settle` (§6b-5c, elf dagen), bij het "
                "Serie B-id en bij de `notes`-tekst van 2 november zelf - die werd toen voor "
                "Lille - Lens gerepareerd en kreeg daarbij twee takken waar er drie nodig waren. "
                "WAT HET NIET IS: geen wijziging in welke bets er worden gepubliceerd. De "
                "rekenregels, de poorten en de rangorde zijn ongemoeid; alleen de tekst die "
                "erbij staat is waar geworden."),
            "DE_TWEE_UNDERS_STAAN_VER_BOVEN_HET_PINNACLE_OORDEEL_EN_DAT_IS_DE_GROOTSTE_WAARSCHUWING_VAN_VANDAAG": (
                "Stage 5 stap 2 zet het scherpste publieke expertoordeel naast de eigen kans, en "
                "vandaag wijst dat precies op de twee bets die bovenaan staan. Op de "
                "doelpuntenlijn van Pinnacle (marge 2,9%, de scherpste van de dag): "
                "Bodo/Glimt - Lille P(Under 3.25) Pinnacle 0,512 tegen eigen 0,703, een verschil "
                "van +19,11 pp; Barcelona - Aston Villa P(Under 4.0) Pinnacle 0,454 tegen eigen "
                "0,627, +17,35 pp. Dat zijn de twee GROOTSTE afstanden van alle zestien gemeten "
                "paren, en ze staan beide op de Under-kant - de kant waarvan §6g meet dat de "
                "routine er structureel naast zit. Gemiddeld over alle zestien paren staat de "
                "eigen P(Under) +3,02 pp boven Pinnacle en bij 9 van de 16 erboven; deze twee "
                "zijn dus geen uitdrukking van een algemene scheefstand maar uitschieters erin. "
                "OP HET 1X2 WIJST HET DEZELFDE KANT OP. Bij Bodo/Glimt - Lille geeft Pinnacle de "
                "thuisploeg 0,534 en het model 0,397 (-13,70 pp): het model ziet een veel "
                "gelijkwaardiger en veel lager scorend duel dan de scherpste bookmaker. Bij "
                "Barcelona - Aston Villa geeft Pinnacle Barcelona 0,764 en het model 0,582 "
                "(-18,16 pp). Gemiddelde absolute afstand tot het Pinnacle-oordeel over 16 duels: "
                "5,25 pp. "
                "HARDE GRENS (§2 / §4): geen van deze getallen gaat in `my_prob` of in "
                "`prob_sources`. Ze zijn marktafgeleid en ze horen in de vergelijking, niet in de "
                "kansschatting. Wat ze WEL doen is de lezing van de dag bepalen: twee "
                "Under-regels op zwakke data, beide ver boven het scherpste oordeel in de markt, "
                "beide op een kant met een gemeten scheefstand, en geen van beide door poort 9 "
                "getoetst omdat die alleen op FULL geldt. Dat staat met zoveel woorden in de "
                "voorbeschouwing onder 'wat de weddenschap kan slopen', en het is de reden dat de "
                "risicoklasse van beide High is en niet Medium."),
            "POORT_9_RAAKT_GEEN_VAN_DE_TWEE_UNDERS_VAN_VANDAAG_EN_DAT_IS_EEN_BESLUIT": (
                "Beide Under-regels staan op LIGHT en `unders.TIERS` is `(\"FULL\",)`, dus poort 9 "
                "komt er niet aan. Dat is geen omissie maar het besluit van de gebruiker van "
                "12 oktober 2026 (§1h, '`LIGHT` blijft erbuiten - gevraagd en beantwoord'): "
                "*'Twee hoeft nog niet op de zwakke data; eerst kijken wat deze rem doet.'* De "
                "vraag is gesteld en beantwoord en hoort niet opnieuw te worden gesteld; deze "
                "regel is er om vast te leggen dat de stilte een keuze is. "
                "DE REEKS DIE DIE VRAAG MOET BEANTWOORDEN IS INMIDDELS LEESBAAR. "
                "`doelpunten_onder` staat op 35 afgewikkelde kandidaten met een trefkans van "
                "37,1% en -30,4% rendement; dat is boven de ~30 die §6d eist, en het teken zegt "
                "dat de poort doet wat hij moet doen. Dat is een aanleiding om de vraag over "
                "LIGHT ooit opnieuw voor te leggen, GEEN automatisme dat een run zelf mag "
                "uitvoeren (§1e en §1h zeggen dat allebei expliciet). Hij wordt vandaag dus "
                "alleen genoemd onder 'Stand van het logboek', zoals elke andere reeks. "
                "WAT HET VANDAAG CONCREET KOST OF OPLEVERT IS NUL: poort 9 heeft vandaag nul "
                "selecties tegengehouden, want er was geen enkele FULL-Under met een edge in de "
                "band 8-10 pp. De enige FULL-Unders van de dag stonden op een negatieve edge."),
            "WAT_ER_AFGEWIKKELD_IS_EN_EEN_GESTAAKT_DUEL_DAT_GEEN_UITSLAG_IS": (
                "Stage 0 heeft ACHT picks en ACHTTIEN schaduwrijen afgewikkeld: 4 gewonnen en 4 "
                "verloren bij de picks, 9 gewonnen / 7 verloren / 2 VOID bij de schaduwrijen. "
                "DIE TWEE VOIDS ZIJN EEN REPARATIE IN DE AFWIKKELING EN GEEN UITSLAG. Tenerife - "
                "FC Andorra (LaLiga2, 2 november) staat bij Fotmob op `finished = true` met "
                "`scoreStr` 2-2 en `reason.long` = **Abandoned**: het duel is GESTAAKT en heeft "
                "de 90 minuten niet gehaald. §0 en §6d rekenen af op de stand NA 90 MINUTEN, en "
                "een tussenstand van een gestaakt duel is die stand niet - precies wat de oude "
                "12-uursmarge moest voorkomen. `finished = true` zegt alleen dat je MAG "
                "afwikkelen, niet dat er een uitslag is. Zonder deze controle waren twee "
                "schaduwrijen van Run B (1 november en 2 november, beide `failed_gate = context`, "
                "1X2 op Andorra @3,78 en @3,499) als VERLOREN geboekt - twee onware rijen in de "
                "`context`-reeks, die op 115 gevallen staat. "
                "`ra_nov03_settle.py` heeft daarom een `abandoned()`-controle op `reason.long` "
                "(abandoned, postponed, cancelled, awarded, afgebroken, uitgesteld) die zo'n rij "
                "op `void` zet. Alle 26 andere rijen van vandaag stonden op `Full-Time` en zijn "
                "normaal afgerekend; de controle is per rij gedraaid en niet alleen op de twee die "
                "opvielen. "
                "DIT HOORT IN `scripts/settling.py` EN NIET IN EEN RUNSCRIPT, en dat is een "
                "openstaand punt van deze run: zolang de controle in `tmp-run/` staat, doet de "
                "volgende run hem alleen als zij hem overneemt. Dat is dezelfde reden waarom de "
                "aliastabel op 5 oktober van `tmp-run/ra_names.py` naar `scripts/teamnames.py` is "
                "verhuisd (§3 Stage -2). Ik pak dat op in de run van 4 november."),
            "DE_VIJF_POORTEN_VAN_PARAGRAAF_1_ZIJN_ALLE_VIJF_NAGELOPEN": (
                "De bevestiging door een tweede methode is OP DE RUNLIJST ZELF gedaan en niet "
                "alleen op de analyse, zoals Run A sinds 11 oktober doet: de Fotmob-daglijst naast "
                "de BetExplorer-fixturepagina per competitie, twee losse bronnen. Ze zijn het over "
                "ALLE ZESTIEN competities eens en over het totaal: 18 duels tegen 18, zonder enig "
                "verschil, met negen in de Championship en negen in de Champions League. "
                "DE VIJF BEKERS SPELEN NIET, EN OOK DAT IS BIJ TWEE BRONNEN NAGETROKKEN. De "
                "Fotmob-daglijst geeft voor League Cup (133), DFB Pokal (209) en KNVB Beker (235) "
                "nul duels in het venster, en BetExplorer bevestigt dat voor alle vijf met de "
                "eerstvolgende ronde erbij: FA Cup 6 nov, Coppa Italia 1 dec, KNVB Beker 1 dec, "
                "DFB Pokal 1 dec, League Cup 15 dec. Alle vijf fixturepagina's gaven vandaag "
                "teamparen (40, 4, 8, 16 en 8), dus er is nergens een lege pagina die als "
                "bevestiging zou kunnen worden gelezen. 'Niet in de daglijst' mag nooit als GEEN "
                "WEDSTRIJD worden opgeschreven zonder tweede bron; dat is het gat dat Run A op "
                "6 oktober 2026 vijf duels kostte. "
                "DE TWEE ANDERE EUROPESE TOERNOOIEN spelen donderdag (UEL en UECL, 5 november) en "
                "de Premier League, Serie A, La Liga, Bundesliga, Ligue 1, Eredivisie, Primeira "
                "Liga, Belgian Pro League, Super Lig, Scottish Premiership en Ekstraklasa hebben "
                "vandaag geen ronde - die spelen in het weekend van 6-8 november. Dat is `GEEN "
                "WEDSTRIJD` en geen gat. "
                "DE DERDE POORT, DE ANTI-CIRCULARITEIT (§2), IS PER BET NAGELOPEN: de kansinputs "
                "van alle drie de regels komen uit Fotmob team-xG, de Fotmob-doelpuntensplits en "
                "de Fotmob-wedstrijdcontext, en bij de twee Champions League-duels uit de "
                "omgerekende binnenlandse verhoudingen van `scripts/interleague.py`. Geen van die "
                "getallen is van een bookmaker of een odds-aggregator afgeleid. Het "
                "Pinnacle-oordeel en het BetExplorer-marktgemiddelde staan ERNAAST en in geen "
                "enkele `prob_sources`-lijst."),
            "DE_AFKAPPING_VAN_STAGE_4_BINDT_VANDAAG_NIET": (
                "Achttien duels in het inzetvenster tegen een cap van 40 (`MAX_DEEP_ANALYSES`, "
                "dinsdag), dus er is NUL afgekapt en alle achttien zijn doorgerekend. De "
                "datarijkdom-score liep van 5,0 tot 8,0; die twee getallen staan hier omdat §3 "
                "Stage 4 ze eist zodra de cap knelt, en ze staan er ook als hij dat niet doet - "
                "anders is achteraf niet na te gaan of de afkapping ergens op sloeg. De negen "
                "Champions League-duels scoren met 7,0 tot 8,0 hoger dan de negen "
                "Championship-duels met 5,0 tot 5,5, en dat komt vrijwel helemaal uit het "
                "opstellingsblok: om 03:00 NL staat er voor een avondduel in de Champions League "
                "al een voorspelde opstelling en voor de Championship nog niet. "
                "TWEE DUELS VIELEN AF OP `data_tier = NONE`, beide in de Champions League en beide "
                "op de kruis-grensomrekening van §4. Atletico Madrid - Bayern Munchen: Bayern komt "
                "met een omgerekende aanval van 2,742 BUITEN het gemeten bereik 0,585-2,432 "
                "(binnenlandse verhouding 2,218 over 34 duels, Europese competitiefactor "
                "x1,389/0,745 over 359 duels). LASK - Slovan Bratislava: voor Slowakije is er GEEN "
                "gemeten competitiefactor (minder dan 40 Europese duels in de meting). Dat is de "
                "regel die werkt zoals hij hoort - §2 zegt dat een ontbrekende onafhankelijke "
                "input GEEN BET betekent en niet 'LIGHT met lage confidence' - maar het kost wel "
                "de twee duels waar vandaag het meeste publiek naar kijkt, en dat hoort erbij te "
                "staan in plaats van als een nette nul in de tabel te verdwijnen. "
                "DE ZEVEN ANDERE CHAMPIONS LEAGUE-DUELS STAAN OP LIGHT EN NOOIT OP FULL, want de "
                "omrekening haalt de systematische fout eruit en niet de onzekerheid (§4, "
                "8 september). Daar geldt de lat van 16,0 pp, en twee van de zeven halen hem. "
                "DRIE CHAMPIONSHIP-DUELS STAAN OP LIGHT omdat er een omgerekende ploeg in staat: "
                "Burnley (uit de Premier League), Lincoln City en Bolton Wanderers (uit League "
                "One). Geen van die drie haalt de LIGHT-lat; Queens Park Rangers - Burnley viel "
                "bovendien op poort 7 af - Burnley mist 54% van zijn selectiewaarde tegen 30% bij "
                "QPR, met Armando Broja, Zeki Amdouni en Hannibal Mejbri eruit. Sinds de "
                "reparatie van 31 oktober (`promotion.match_tier`, 'de zwakste kant wint') kan de "
                "tier van een duel niet meer stil door de andere kant worden overschreven."),
            "HET_NIVEAU_KOMT_VOOR_DE_CHAMPIONSHIP_UIT_DE_UPLIFT_EN_VOOR_DE_CHAMPIONS_LEAGUE_NIET_UIT_EEN_COMPETITIE": (
                "`league_level` is vandaag voor EEN competitie aangeroepen: de Championship, route "
                "`vorig+uplift` (13 van 46 speeldagen = 28%, onder de helft van "
                "`SEASON_MATURE_SHARE`), niveau 1,500 thuis / 1,291 uit / basis 1,395. De "
                "Champions League gaat NIET langs `league_level` maar langs "
                "`scripts/interleague.py`: een toernooi met ploegen uit verschillende landen heeft "
                "geen eigen competitieniveau om op te normaliseren, en zijn eigen stand zou een "
                "mengsel van zeventien competities zijn (§4, Kruis-grens). "
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP factor 1,0713 (gepoold 1,1069) OVER "
                "16 SPEELDAGEN IN TWEE COMPETITIES, en dat is de smalste pool sinds de correctie "
                "bestaat - normaal zijn het zeven tot dertien competities. Met twee waarnemingen "
                "is de pool nauwelijks een pool, en de correctie is daarmee gevoeliger voor wat "
                "deze twee competities doen dan op een gewone dag. Dat is geen fout en vraagt geen "
                "ingreep - de correctie is op xG-waarnemingen gemeten en wordt nooit op de markt "
                "bijgeregeld (§3 Stage 5) - maar het is wel de reden dat de niveaukeuze vandaag "
                "met minder zekerheid staat dan het getal suggereert. "
                "`vroeg_seizoen.overgeslagen` IS LEEG: geen van de twee competities is rijp genoeg "
                "om uit de pool te vallen. Een stil weggelaten waarneming is hetzelfde probleem "
                "als een stille truncatie in Stage 4, dus dat staat er ook als het niets is."),
            "DE_CREDITS_EN_DE_MARKTBALANS": (
                "`api_check.py` gaf 19.841 credits over en 159 verbruikt deze maand; "
                "`suggest_cap(19841, 28)` geeft een plafond van 353 voor deze run. Uitgegeven: 6 "
                "aan de bulk-aanroep (h2h + spreads + totals, 3 credits per competitie, voor "
                "beide inkoopbare competities) en 11 aan BTTS per wedstrijd, samen 17 van 353. "
                "DE MARKTBALANS VAN §1a IS OP DE INKOOP GEHAALD, EN RUIM: beide competities "
                "kregen zowel een uitkomstmarkt (1X2 op de beste prijs, Asian Handicap, Draw No "
                "Bet uit de 0.0-lijn, Double Chance uit de +-0.5-lijn) als een doelpuntenmarkt "
                "(Over/Under). Twee van de twee, niet een van de twaalf zoals op 30 augustus. "
                "GEEN ENKEL DUEL LEUNT OP HET GRATIS BETEXPLORER-MARKTGEMIDDELDE voor de bet "
                "zelf: beide competities hebben een sportkey, dus alle achttien duels hebben een "
                "beste prijs met een herleidbare bookmaker. Het BetExplorer-gemiddelde is "
                "opgehaald voor beide competities en gebruikt waar het hoort - het kalibratieblok "
                "van §6e en poort 8 (wie de markt de mindere ploeg vindt). Gemiddelde om te "
                "meten, beste prijs om te spelen. "
                "BTTS IS VOOR 11 VAN DE 18 DUELS GEKOCHT, op de vereniging van beide schalen "
                "(§1a stap 2, 13 september): een duel krijgt BTTS zodra minstens een selectie de "
                "herijkte NEAR-drempel of de volle drempel op de RUWE schaal haalt. De zeven "
                "duels die geen BTTS kregen staan in `markets_checked` met de reden erbij - "
                "'niet opgevraagd - geen kandidaat-edge in dit duel' - en niet als gat. Daaronder "
                "de twee NONE-duels, waar per definitie geen markt door te rekenen valt."),
            "ALLE_DRIE_DE_REGELS_STAAN_BIJ_EEN_BEURS_EN_DAT_IS_VANDAAG_DRIE_VAN_DE_DRIE": (
                "Alle drie de gepubliceerde koersen komen van Matchbook, een BEURS, dus er gaat "
                "2% commissie van de nettowinst af (`EXCHANGE_COMMISSION`, §0). De bruto koersen "
                "zijn 1,73 / 1,76 / 2,06 en de koersen NA commissie 1,7154 / 1,7448 / 2,0388; "
                "`edge_pp` en `selection_score` rekenen met die tweede reeks (`oddsapi.net_price`). "
                "WAT DE GEBRUIKER MOET WETEN: zet hij in bij Matchbook, dan ziet hij 1,73 / 1,76 / "
                "2,06 op zijn scherm staan. De edges hierboven zijn al verrekend met de commissie "
                "en hij hoeft dus niets zelf af te trekken. Drie van drie bij een beurs is boven "
                "de 61% die §0 als normale stand noemt, maar met drie regels is dat geen "
                "waarneming over de markt - het is een klein getal."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn DRIE wedstrijden met een selectie die
        # alle negen poorten haalt en drie plekken (MAX_SHORTLIST = 3, maandag), dus er valt er
        # geen enkele af en
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
        s3 = json.load(open("tmp-run/ra_nov03_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov03_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov03_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_nov03_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov03_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov03_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

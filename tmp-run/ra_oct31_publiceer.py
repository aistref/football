"""Run A 31 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct31_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWAALF van de eenentwintig competities uit de runlijst speelden, met DRIEENVIJFTIG duels
in het inzetvenster: de drukste dag van de maand. De Championship speelt een volle ronde (11), de
Premier League acht, de Bundesliga zes, La Liga, Eredivisie, Belgian Pro League en Ekstraklasa elk
vier, Serie A en de Super Lig drie, Primeira Liga en de Scottish Premiership twee, Ligue 1 een.
De Danish Superliga speelt niet, de vijf bekers hebben geen ronde en de drie Europese toernooien
spelen pas 3 t/m 5 november.

VIJF REGELS, WAARVAN VIER HUN LAT HALEN EN EEN OP RANGORDE STAAT. Die vijfde is een Under die
door GEEN VAN BEIDE latten is getoetst, en dat is precies het gat tussen §5b en §1h dat op
28 oktober als besluit aan de gebruiker is voorgelegd en nog open staat — zie
VIJF_REGELS_WAARVAN_VIER_HUN_LAT_HALEN en POORT_9.

DE BEVINDING VAN DEZE RUN IS EEN REPARATIE, NIET EEN BET. De tier van een DUEL werd in elk
runscript met een kale toewijzing uit de twee kanten gerekend, waardoor een omrekening buiten het
gemeten bereik bij de THUISploeg stil werd overschreven door een geldige omrekening bij de
UITploeg. Dat raakte vandaag twee duels, en het duurste ervan zou de HOOGSTE EDGE VAN DE DAG zijn
geweest. Zie DE_TIER_VAN_EEN_DUEL_WAS_DIE_VAN_ZIJN_TWEEDE_KANT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-31"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-10-31T03:25:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok (wintertijd)


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
                         "1752 doorgerekende duels: P(Under 2.5) voorspeld 42,5% tegen werkelijk "
                         "40,3%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de "
                         "gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,609 "
                         "doelpunt per duel over 107 gevallen (z = +3,81), terwijl de Over-kant op "
                         "-0,296 staat (z = -1,25 over 60 gevallen). Dit duel staat op FULL, dus "
                         "poort 9 (§1h) kan hier bijten; of hij dat werkelijk doet hangt af van "
                         "de band waarin de edge valt — hij bindt ALLEEN tussen 8,0 en 10,0 pp, "
                         "en laat een Under daaronder met opzet door omdat `edge` daar de "
                         "bindende poort hoort te zijn. Dat is de rem die er is; de oorzaak — "
                         "keuze (a) van 11 oktober — is op 28 oktober gemeten en AFGEWEZEN (§6g: "
                         "de voorgeschreven correctie verergert het symptoom en de vormfout bleek "
                         "grotendeels een nalatenschap van shrink = 0.80, op 19 sep opgelost). "
                         "Trek dus ongeveer twee procentpunt van de genoemde kans af voordat je "
                         "haar leest. "
                         if onder else "")
                      # `bet_beide = False` heeft TWEE oorzaken en ze zijn niet hetzelfde: de lat
                      # op geen van beide schalen halen, of hem ruw wél en herijkt niet halen.
                      # Tot vandaag stond hier één tekst voor beide, en bij Lille – Lens (ruw
                      # +8,37 pp, herijkt +7,99915 pp) was die tekst onwaar.
                      + ("" if cand.get("bet_beide") else
                         (f"bet_beide = FALSE, maar alleen op de HERIJKTE schaal: ruw haalt deze "
                          f"selectie haar lat met {cand.get('edge_raw')} pp wél en herijkt met "
                          f"{cand.get('edge_pp')} pp niet. Dat is de reeks `herijking` van §5a, "
                          f"en de rij is hier geen schaduwpick maar een gepubliceerde bet omdat "
                          f"de rangorde van §5b erover gaat. "
                          if cand.get("bet_ruw") else
                          "bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide "
                          "schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel "
                          "(§5b). "))),
        })
    return st, top, picks, res


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("A", "tmp-run/ra_oct31_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "DE_TIER_VAN_EEN_DUEL_WAS_DIE_VAN_ZIJN_TWEEDE_KANT": (
                "DIT IS DE BEVINDING VAN DEZE RUN EN ZE KOSTTE BIJNA EEN BET DIE NIET MOCHT. "
                "Elk runscript rekende de `data_tier` van een duel zelf uit de twee kanten, met "
                "deze regel, twee keer achter elkaar: `tier_box[0] = \"NONE\" if not "
                "conv.in_range else \"LIGHT\"`. Dat is een KALE TOEWIJZING en geen samenvoeging, "
                "en `side_stats` wordt twee keer aangeroepen: eerst thuis, dan uit. Stond de "
                "omgerekende ploeg BUITEN het gemeten bereik van `conversion_in_range` THUIS en de "
                "andere ploeg erbinnen, dan overschreef de tweede aanroep de `NONE` van de eerste "
                "met `LIGHT` en was het duel gewoon speelbaar. Stond de buitenbereik-ploeg UIT, "
                "dan ging het goed — en dat is precies waarom de fout maandenlang half zichtbaar "
                "was. §4 ('Promovendi: eerst omrekenen, dan pas NONE') zegt per PLOEG dat het "
                "LIGHT is binnen het bereik en NONE erbuiten; de stap van ploeg naar DUEL stond "
                "nergens in code. En die stap is niet vrij: beide sterktes gaan in dezelfde "
                "`lambda`, dus een onbetrouwbare omrekening aan een kant maakt de doelverwachting "
                "van het hele duel onbetrouwbaar. VANDAAG RAAKTE HET TWEE VAN DE 53 DUELS, beide "
                "met de buitenbereik-ploeg thuis: HULL CITY - IPSWICH TOWN (Hull City verdediging "
                "1.102 buiten 0.284-1.022) en ERZURUMSPOR FK - CORUM FK (Erzurumspor verdediging "
                "0.483 buiten 0.497-1.124). Het eerste is het duurste: met Over 2.5 @1,9212 en "
                "+17,13 pp was dat DE HOOGSTE EDGE VAN DE DAG en het zou als LIGHT-bet zijn "
                "gepubliceerd (de lat van 16,0 pp werd gehaald). Na de reparatie staan beide op "
                "`data_tier = NONE` en vallen ze af op poort 4 — nul doorgerekende selecties. "
                "WAT ER IS GEREPAREERD: `scripts/promotion.match_tier()` is nieuw en voegt de "
                "tiers van de twee kanten samen met 'de zwakste wint'; het runscript roept die "
                "aan in plaats van zelf toe te wijzen. De reparatie zit dus in `scripts/` en niet "
                "alleen in het wegwerpscript van vandaag, want anders kopieert de run van morgen "
                "de fout gewoon terug — dezelfde les als `branchaudit.py` (29 sep) en "
                "`progress.resumed_count` (16 okt). `promotion.py selftest` staat op ALLES OK en "
                "de uitkomst van de run is bit-voor-bit gelijk aan de handmatige reparatie. "
                "WAT HET IN HET VERLEDEN HEEFT GEKOST: een scan over alle 'data/run-state/' vond "
                "ACHT duels waar de twee kanten hierover van mening konden verschillen. Bij vijf "
                "stond de buitenbereik-ploeg UIT en kwam er correct `NONE` uit. Bij DRIE stond hij "
                "THUIS en werd het dus ten onrechte `LIGHT`: Exeter City - Rotherham United "
                "(3 okt, Run B), Girona - Mallorca (4 okt, Run B) en Celta Fortuna - Tenerife "
                "(19 okt, Run B). DE EERSTE TWEE ZIJN EEN GEPUBLICEERDE BET GEWORDEN — DNB Exeter "
                "City @1,882 (+11,68 pp) en Under 2.5 @2,0192 (+7,35 pp) — en ze zijn BEIDE "
                "GEWONNEN. Er is dus geen geld mee verloren; ze hadden alleen niet mogen worden "
                "gespeeld. DIE TWEE RIJEN ZIJN NIET HERSCHREVEN: ze staan in de runrapporten van "
                "3 en 4 oktober en in `picks.jsonl`, en zijn daarmee historie en geen meting — "
                "dezelfde keuze als bij de `resumed_count` van voor 16 oktober. Twee op 490 "
                "afgewikkelde picks verschuift geen enkel cijfer in §6d. OPENSTAAND PUNT VOOR DE "
                "GEBRUIKER: of die twee rijen alsnog uit het logboek moeten. Dat is een keuze over "
                "de administratie en niet over de data, dus hij hoort bij hem."),
            "VIJF_REGELS_WAARVAN_VIER_HUN_LAT_HALEN_EN_EEN_OP_RANGORDE_STAAT": (
                "De dagranglijst van §5b heeft VIJF regels en `MAX_SHORTLIST` is 5 (zaterdag), dus "
                "de lijst is EXACT VOL en de lijstlengte bindt op het randje niet: er valt geen "
                "gekwalificeerde selectie buiten de lijst en `failed_gate = lijstlengte` krijgt "
                "vandaag geen enkele rij. Had er een zesde selectie boven de drempel gestaan, dan "
                "was die er wel uit gevallen. VIER VAN DE VIJF HALEN HUN LAT ONDUBBELZINNIG: "
                "Middlesbrough - Charlton Athletic, Under 3.5 @1,87 (Pinnacle) met +13,45 pp tegen "
                "de VERZWAARDE lat van 10,0 pp, score 9,002; Bayer Leverkusen - VfB Stuttgart, "
                "Over 3.5 @1,87 (1xBet) met +10,74 pp tegen 8,0, score 6,897; AFC Bournemouth - "
                "Leeds United, Over 2.5 @1,94 (1xBet) met +9,58 pp tegen 8,0, score 5,856; en "
                "Moreirense - Estrela da Amadora, Over 2.5 @2,1368 (Matchbook, beurs, na 2% "
                "commissie) met +9,41 pp tegen 8,0, score 5,289. Alle vier staan op `FULL` en alle "
                "vier hebben `bet_beide = true` — ze halen hun lat op de herijkte EN op de ruwe "
                "schaal. Dat is met een fit die vrijwel de identiteit is (a=0,987, b=-0,008) te "
                "verwachten, maar het is per selectie met de vlag gecontroleerd en niet "
                "beredeneerd (§5a waarschuwt daar uitdrukkelijk voor). "
                "DE VIJFDE REGEL STAAT ONDER DE LAT EN IS OP RANGORDE GEPUBLICEERD: Anderlecht - "
                "Westerlo, Under 3.5 @1,7742 (Matchbook, beurs) met +7,77 pp, score 4,983, "
                "`failed_gate = edge` en `bet_beide = false`. Onder §5b is de drempel sinds "
                "20 september geen poort meer maar een afkapping: staan er minder selecties boven "
                "de lat dan er plekken zijn, dan bepaalt de rangorde de lijst en gaat de drempel "
                "mee als LABEL per regel. Die regel draagt dat label dus ook. De zeven andere "
                "poorten zijn bij haar WEL allemaal opengegaan — koersband, anti-circulariteit, "
                "datatier, tweede methode, robuustheid (zwakste stand van het grid +9,15 pp), "
                "context en underdog — dus er is geen poort die haar afwees; alleen de drempel. "
                "LEES DE LIJST ALS 'DIT IS HET BESTE VAN VANDAAG' EN NIET ALS 'DIT IS EEN GEVONDEN "
                "VOORDEEL': §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op "
                "de herijkte edge bestaat die geld oplevert en dat het rendement het SLECHTST is "
                "bij de hoogste geclaimde edge. Het logboek staat vandaag op -8,7% over 429 "
                "bets, en §5b zegt zelf dat ongeveer -10% is wat je van deze lijst mag verwachten."),
            "ALLE_VIJF_DE_REGELS_ZIJN_EEN_OVER_UNDER_EN_DAT_IS_GEEN_INKOOPARTEFACT": (
                "De marktbalans-controle van §1a is gehaald op de INKOOP en zo ruim als ze kan: "
                "van de TWAALF competities die vandaag spelen hebben ALLE TWAALF een sportkey en "
                "kregen alle twaalf de volledige bulk (h2h + spreads + totals, 3 credits per "
                "competitie). Elke gekochte competitie heeft dus zowel een uitkomstmarkt (1X2, AH, "
                "DNB, DC) als een doelpuntenmarkt (O/U), en GEEN ENKEL DUEL draait op het gratis "
                "BetExplorer-marktgemiddelde voor de bet zelf — anders dan op 30 oktober, waar de "
                "negen KNVB Beker-duels dat wel moesten. Wat eruit kwam: over 778 doorgerekende "
                "selecties 262 Over/Under, 220 Asian Handicap, 144 1X2, 74 BTTS, 48 Draw No Bet en "
                "30 Double Chance — en ALLE VIJF de gepubliceerde regels zijn een Over/Under, drie op "
                "de Over-kant en twee op de Under-kant. DAT IS EENZIJDIG EN HET IS GEEN "
                "INKOOPARTEFACT: alle zes markten dongen in elk duel mee, BTTS is voor 38 duels "
                "met een kandidaat-edge apart gekocht, en de uitkomstmarkten vielen af op poort 5 "
                "(tweede methode) en poort 8 (underdog). Het is de uitkomst, en bets forceren om "
                "een verdeling te halen is precies wat §1 verbiedt — maar het is wel het soort "
                "eentonigheid waar de gebruiker op 19 september over viel, en het is nu TWEE "
                "RUNDAGEN OP RIJ volledig zo (30 okt vier van vier, vandaag vijf van vijf). Dat "
                "hoort hier te staan en het is een signaal over het model en niet over §5b (§5b, "
                "laatste alinea): de uitkomstmarkten sneuvelen stelselmatig op de tweede methode, "
                "en dat staat hieronder apart. NIET ELKE MARKT WAS BIJ ELK DUEL TE KOOP: de "
                "spreads-respons levert per competitie verschillende handicaplijnen, dus het "
                "aantal doorgerekende selecties per duel loopt van 7 tot 19. Dat staat per duel "
                "in `markets_checked` met de reden erbij en niet als gat (§6b-5b)."),
            "TWEEDE_METHODE_VANGT_552_VAN_DE_778_SELECTIES_EN_DAT_IS_71_PROCENT": (
                "Over de 51 doorgerekende wedstrijden zijn 778 selecties langs de poorten gegaan. "
                "De verdeling: `tweede_methode` 552, `edge` 108, `underdog` 35, `context` 34, "
                "`odds` 34, `robuustheid` 9, `doelpunten_onder` 1, en 5 selecties haalden alles "
                "(verdeeld over vier wedstrijden — bij een ervan scoorden twee selecties van "
                "DEZELFDE wedstrijd door, en §1 publiceert dan de hoogste op `selection_score`). "
                "DAT EERSTE GETAL IS GEEN DETAIL: poort 5 vangt 71% van alles wat er wordt "
                "doorgerekend, net als gisteren (77%) en de dag ervoor (78%), en §5 zegt met "
                "zoveel woorden dat als er een week lang alles op `tweede_methode` afvalt, de "
                "vraag is of de twee methodes systematisch uiteenlopen — en dat is een BEVINDING "
                "en geen ruis. Dit is nu de derde rundag op rij boven de 70%, en het is dezelfde "
                "groep die de eenzijdigheid hierboven veroorzaakt. Wat er tegenover staat: §1f "
                "heeft op 392 afgerekende gevallen gemeten dat de splitsmethode als KANSBRON "
                "vrijwel niets toevoegt (Brier .23625 bij gewicht 0,80 tegen .23674 voor alleen "
                "xG) en dat haar waarde juist in dit veto zit, dat aantoonbaar geld bespaart: "
                "`tweede_methode` staat in het schaduwlogboek op -8,4% over 219 afgewikkelde "
                "gevallen. OPVALLEND VANDAAG, EN HET WIJST DE ANDERE KANT OP: bij de twee regels "
                "met de grootste edge is het juist de SPLITSMETHODE die veel optimistischer is dan "
                "de xG-methode — Middlesbrough - Charlton +26,82 pp tegen +10,60 pp op xG, en "
                "Leverkusen - Stuttgart +16,31 pp tegen +9,81 pp. Bij de andere drie staat ze "
                "juist LAGER (Bournemouth +7,05 tegen +10,64, Moreirense +6,02 tegen +10,62, "
                "Anderlecht +4,07 tegen +9,15), dus er zit geen vaste richting in. De twee "
                "methodes wijzen daar dezelfde kant op maar liggen ver uiteen, en `combine_probs` "
                "weegt 80/20 naar xG, dus de gepubliceerde kans leunt op de voorzichtiger van de "
                "twee. Noem die getallen, lees ze over weken en niet vandaag, en verzet er niets "
                "op (§6d)."),
            "WAT_ANDEREN_VOORSPELLEN_PINNACLE_IS_HET_MET_ELKE_GEPUBLICEERDE_REGEL_ONEENS": (
                "Stage 5 stap 2, in de enige vorm die bereikbaar is (§3 Stage 5 heeft op 20 sep "
                "gemeten dat geschreven voorspellingen vrijwel niet te halen zijn: Forebet 403, "
                "Pinnacle-artikelen 404, Matchbook 530). Wat er wel is, is DE PRIJS VAN PINNACLE "
                "APART: de scherpste bookmaker van de markt, en zijn de-vigde prijs is het beste "
                "publieke expertoordeel dat beschikbaar is. Over 51 duels: gemiddelde absolute "
                "afstand op 1X2 4,41 procentpunt, gemiddelde Pinnacle-marge 3,70% (tegen 6 a 10% "
                "bij de rest). Op de doelpuntenkant is het eigen model vandaag OPVALLEND GOED IN "
                "BALANS met Pinnacle: gemiddeld -0,07 pp op de Under-kant over 52 (duel, "
                "lijn)-paren, en 25 van de 52 erboven. Dat is de vlakste stand van deze maand en "
                "het is een los argument tegen de scheefstand die §6g op de Under-kant meet — als "
                "waarneming, niet als weerlegging. MAAR DE GEPUBLICEERDE REGELS ZIJN PRECIES "
                "DE DUELS WAAR DE AFSTAND TOT PINNACLE HET GROOTST IS, en alle vier de meetbare wijzen de "
                "VERKEERDE KANT OP: bij Bournemouth - Leeds zet Pinnacle P(Under 2.5) op 48,7% en "
                "het eigen model op 37,8% (10,9 pp meer Over); bij Leverkusen - Stuttgart P(Under "
                "3.5) op 45,4% tegen 36,7% eigen (8,7 pp meer Over); bij Middlesbrough - Charlton "
                "P(Under 3.5) op 51,4% tegen 64,1% eigen (12,7 pp meer Under); en bij Anderlecht - "
                "Westerlo P(Under 3.25) op 48,8% tegen 60,0% eigen (11,2 pp meer Under, de grootste "
                "Under-afwijking van de dag). Voor Moreirense - Estrela noteert Pinnacle geen "
                "O/U-lijn, dus daar is geen vergelijking — die regel staat zonder tweede oordeel. "
                "LEES DAT ALS EEN "
                "WAARSCHUWING EN NIET ALS EEN BEVESTIGING: §1g meet dat de bookmaker scherper "
                "schat dan het model (Brier 0,2393 voor de markt tegen 0,2602 eigen over 429 "
                "afgerekende bets), dus de grootste afstand tot Pinnacle is eerder de grootste "
                "modelfout dan de grootste vondst. HARDE GRENS: niets hiervan gaat in `my_prob` of "
                "in `prob_sources` (§2); het staat in de lezing en in de vergelijking."),
            "POORT_8_HIELD_TWAALF_WEDSTRIJDEN_TEGEN_EN_POORT_8_RUW_GEEN_ENKELE": (
                "Poort 8 bindt in de lichte vorm (ondergrens `sides.UNDERDOG_FLOOR` = 0,35, §1e) "
                "en is met `today=DAY` aangeroepen, zodat het venster van 25 t/m 30 september uit "
                "`sides.LAPSED_FROM`/`LAPSED_UNTIL` wordt gelezen in plaats van geraden. Hij hield "
                "vandaag 35 selecties tegen, verdeeld over TWAALF wedstrijden — de breedste "
                "poort-8-dag van de maand, en dat is te verwachten op een dag met 53 duels waarvan "
                "een derde een duidelijke favoriet heeft. DE DUURSTE IS STOKE CITY - PRESTON NORTH "
                "END: Preston +0.75 @1,931 met +16,67 pp, de hoogste geblokkeerde edge van de dag "
                "en hoger dan drie van de vier gepubliceerde regels. Daarna Bologna - Monza (Monza "
                "+1.5 @1,45, +11,98 pp) en SK Beveren - Union St.Gilloise (Beveren +1.25 @1,88, "
                "+11,67 pp). Dat is precies het geval waarvoor de poort is gebouwd: §1e meet over "
                "89 gevallen dat de routine op de underdog-kant 47,1 winnaars verwachtte, de markt "
                "38,0, en het 33,0 werden (z = -3,14). De tweede schaal, `underdog_ruw`, krijgt "
                "vandaag GEEN ENKELE rij: er is geen selectie die op de ruwe kans alle eerdere "
                "poorten haalde en alleen op poort 8 sneuvelde. Dat is bij een herijking die "
                "vrijwel de identiteit is te verwachten. Tel die twee reeksen nooit bij elkaar op; "
                "het zijn twee populaties."),
            "POORT_9_HIELD_DE_3_25_VAN_ANDERLECHT_TEGEN_EN_LIET_DE_3_5_VAN_DEZELFDE_WEDSTRIJD_DOOR": (
                "DIT IS HET GAT TUSSEN §5B EN §1H, EN VANDAAG BIJT HET. Poort 9 (§1h) bindt sinds "
                "12 oktober en hield vandaag EEN selectie tegen: ANDERLECHT - WESTERLO, Under 3.25 "
                "@1,98 (Pinnacle) met +8,14 pp tegen de verzwaarde lat van 10,0 pp (8,0 + 2,0 voor "
                "de gemeten scheefstand op deze kant). Die gaat als `failed_gate = "
                "doelpunten_onder` naar het schaduwlogboek; de reeks staat daarmee op 24 "
                "afgewikkelde gevallen en -13,1%, nog onder de ~30 die §6d eist. "
                "EN DE GEPUBLICEERDE UNDER VAN DIEZELFDE WEDSTRIJD STAAT OP DE 3.5-LIJN met "
                "+7,77 pp en is door poort 9 HEENGEKOMEN. Dat ziet eruit als een tegenstrijdigheid "
                "en het is er geen: `unders.check` bindt met opzet alleen in de band 8,0-10,0 pp. "
                "Een Under die de gewone drempel van §0 al niet haalt wordt door `edge` "
                "tegengehouden en niet hierdoor, want anders loopt de reeks `doelpunten_onder` vol "
                "met kandidaten die nooit een bet konden worden en meet ze niets meer (de 'twee "
                "populaties'-fout van §1e). MAAR sinds §5b de drempel van een poort in een "
                "afkapping heeft veranderd, betekent dat dat een Under ONDER de 8,0 wel "
                "gepubliceerd kan worden en door GEEN VAN BEIDE LATTEN wordt getoetst — en dat is "
                "vandaag precies wat er gebeurt, bij dezelfde wedstrijd waar poort 9 de strengere "
                "lijn wel tegenhield. De 3.25 met +8,14 pp valt af; de 3.5 met +7,77 pp wordt "
                "gespeeld. DE SELECTIE MET DE LAGERE EDGE OP DEZELFDE WEDSTRIJD IS DUS DE "
                "GEPUBLICEERDE. DAT IS GEEN OMISSIE VAN VANDAAG MAAR HET GEVOLG VAN TWEE REGELS "
                "DIE ELKAAR RAKEN, en het is dezelfde constructie die §1h punt 1 bij `LIGHT` "
                "expliciet heeft gekozen. Het is op 28 oktober als besluit aan de gebruiker "
                "voorgelegd en dat punt staat nog open; het wordt vandaag niet opnieuw als nieuwe "
                "vraag gesteld (§1h, 12 okt: stel hem niet elke dag opnieuw), maar het is nu de "
                "DERDE keer in vier rundagen dat het voorkomt (30 okt twee keer, vandaag een keer) "
                "en dat hoort in het runrapport. "
                "WAT ER BOVENOP KOMT: §6g meet dat P(Under) bij ELK duel ongeveer twee procentpunt "
                "te hoog staat door een vormfout in `score_grid`, vóór er iets is gekozen, en dat "
                "de gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,609 "
                "doelpunt per duel over 107 gevallen (z = +3,81). TREK DUS ONGEVEER TWEE "
                "PROCENTPUNT VAN DE +7,77 pp AF en er blijft bijna niets over. Voor de ANDERE "
                "gepubliceerde Under maakt het het verschil niet: Middlesbrough - Charlton staat "
                "op +13,45 pp tegen een lat van 10,0 en houdt ook na die aftrek ruimte. "
                "TEGENWICHT, EN HET IS EERLIJK OM HET TE NOEMEN: de Pinnacle-vergelijking van "
                "vandaag ziet die scheefstand NIET terug — gemiddeld -0,07 pp op de Under-kant "
                "over 52 (duel, lijn)-paren, 25 van de 52 erboven. Bij Anderlecht - Westerlo zelf "
                "staat het eigen model wel 11,15 pp BOVEN Pinnacle op P(Under 3.25), en dat is de "
                "grootste Under-afwijking van de dag. Dat is een los argument tegen deze regel en "
                "niet tegen de poort."),
            "CONTEXT_HIELD_VIER_WEDSTRIJDEN_TEGEN_DRIE_OP_BLESSURES_EN_EEN_OP_RUST": (
                "Poort 7 (§1c) sloot bij VIER duels, en bij een ervan is het verschil zo groot dat "
                "het het noemen waard is. AJAX - AZ ALKMAAR: AZ mist 52% van de selectiewaarde "
                "tegen 28% bij Ajax — Wouter Goes (blessure, terug begin november), Kees Smit "
                "(blessure, dag tot dag) en Jeroen Zoet (blessure, half november). Dat is het "
                "grootste beschikbaarheidsverschil van de maand, en let op dat BEIDE ploegen zwaar "
                "zijn getroffen; de poort meet het VERSCHIL en niet de hoogte. COVENTRY CITY - "
                "SUNDERLAND: Coventry mist 31% tegen 18% (Bobby Thomas, Aurele Amenda, Luke "
                "Woolfenden). LEVANTE - ATLETICO MADRID: Levante mist 16% tegen 5% (Enzo Bardeli). "
                "En TOTTENHAM HOTSPUR - CRYSTAL PALACE op RUST: Palace had 3 dagen tegen 7 bij "
                "Tottenham, precies het criterium (ten hoogste 4 dagen rust en minstens 2 dagen "
                "minder dan de tegenstander). De poort houdt alleen tegen en stelt `my_prob` niet "
                "bij, want er is geen enkele meting die zegt hoeveel procentpunt een uitvaller of "
                "een rustdag waard is (§1c; de poging om er een bijstelling van te maken vond op "
                "147 wedstrijden niets). De volledige context van ALLE 53 duels staat in het "
                "`context`-blok, ook van de duels waar de poort openging en ook van de twee die op "
                "`NONE` uitkwamen: dat is wat §1c eist en het is de steekproef van `ctxlog.py`. "
                "`context` staat in het schaduwlogboek op -26,6% over 98 gevallen; dat is de poort "
                "die het meeste geld bespaart."),
            "GEEN_VERPLAATSTE_WEDSTRIJD_VANDAAG": (
                "`context.check_venue` zette vandaag bij geen van de 53 duels `relocated`: elk "
                "duel staat in het eigen stadion van de genoteerde thuisploeg. §1c eist dat een "
                "verplaatsing wordt genoemd ook als de poort opengaat; vandaag is er niets te "
                "noemen, en dat is ook een uitkomst. Wat deze controle NIET vangt blijft hetzelfde: "
                "een fixture die van eigenaar is gewisseld, want dat is nieuws en geen data (de "
                "Rennes - PSG-les van 23 augustus)."),
            "TWINTIG_OMGEREKENDE_DUELS_IS_DE_HOOFDROUTE_EN_NIET_EEN_RANDGEVAL": (
                "DRIEENDERTIG duels komen op FULL uit, ACHTTIEN op LIGHT en TWEE op NONE. Die "
                "twintig niet-FULL duels hebben allemaal een promovendus of degradant die via "
                "`scripts/promotion.py` uit de divisie eronder of erboven is omgerekend (§4). Dat "
                "is bijna veertig procent van het programma en daarmee de grootste groep van deze "
                "maand: de omrekening is vandaag geen randgeval maar de hoofdroute, en dat is ook "
                "de reden dat de fout hierboven juist vandaag opviel. Een omgerekende ploeg is per "
                "regel NOOIT FULL — de omrekening haalt de systematische fout eruit en niet de "
                "onzekerheid — dus hun lat is 16,0 pp in plaats van 8,0, en geen van de achttien "
                "komt in de buurt. TWEE duels vallen op `conversion_in_range` en komen daardoor op "
                "NONE uit (zie DE_TIER_VAN_EEN_DUEL). Lees de stand van de divisiefactor per "
                "selectie uit `GapResult.direction` en niet uit een samenvattende zin (§4, 9 okt "
                "2026): vandaag lopen er omrekeningen langs football-data.co.uk (E0/E1, I1/I2, "
                "SP1/SP2, D1/D2, F1/F2, E1/E2, SC0/SC1) en langs eigen metingen van 31 aug 2026 "
                "(NED, BEL, TUR, POL). Geen enkele selectie draait vandaag op `POOLED_GAP`. En "
                "let op de richting OMLAAG: Burnley, West Ham United en Wolverhampton Wanderers "
                "zijn DEGRADANTEN uit de Premier League en gaan langs `convert_relegated` met "
                "gap_for(E0,E1,down) — dat paar heeft wel een `fd_pair`, dus ook die drie staan "
                "niet op de pool."),
            "GEEN_AFKAPPING_MAAR_HET_SCHEELDE_TWEE_DUELS": (
                "DRIEENVIJFTIG duels in het inzetvenster tegen een cap van 55 (zaterdag), dus "
                "`MAX_DEEP_ANALYSES` bindt NIET en er is niets afgekapt — stille truncatie is "
                "verboden (§3 Stage 4). MAAR HET SCHEELDE TWEE DUELS, en dat is het dichtst bij de "
                "cap dat deze routine deze maand is gekomen; op een dag met een volle Championship- "
                "EN Premier League-ronde erbij was er wel afgekapt. De datarijkdom liep van 4,5 "
                "(KV Mechelen - Genk en Standard Liege - Kortrijk) tot 7,5 (Bournemouth - Leeds, "
                "Barcelona - Alaves en Bayern - Dortmund); omdat er niets afvalt zijn 'de laagste "
                "die het haalde' en 'de hoogste die afviel' allebei leeg. Alle 53 duels komen van "
                "de daglijst van de rundag zelf (`source_day = 2026-10-31`), alle 53 staan op "
                "`playable = True` — de vroegste aftrap is 11:30 NL (Erzurumspor - Corum) — en er "
                "is geen carry-over-band. `runwindow` rekent met `zoneinfo`, dus het venster is in "
                "echte NL-tijd gemeten: nu de wintertijd in is, komt een aftrap van 20:00 UTC op "
                "21:00 NL uit (CET) en niet op 22:00 (CEST). Dat is de reparatie van 25 oktober; "
                "`ra_oct31_analyze.py` en dit bestand gebruiken allebei "
                "ZoneInfo('Europe/Amsterdam') en `odds_captured_at` staat op +01:00."),
            "BRONSTATUS_EN_DE_BEVESTIGING_DOOR_EEN_TWEEDE_METHODE": (
                "`api_check.py` van deze run: The Odds API OK met 18530 credits over en 1470 "
                "verbruikt deze maand, 46 actieve voetbalcompetities, en 32 van de 34 sportkeys "
                "van de repo vandaag actief (Coppa Italia en DFB Pokal niet — die hebben geen "
                "ronde). GEEN SLEUTEL IS AFGEWEZEN. `API_FOOTBALL_KEY` ontbreekt en dat is een "
                "BESLUIT van de gebruiker van 27 september 2026 en geen gat: de kanskant komt van "
                "Fotmob (alle competities) en Understat (vijf, waarvan er vandaag vijf spelen). "
                "Fotmob heeft deze run voor alle 53 duels een context geleverd zonder een enkele "
                "fout, dus de uitzondering van §3 punt 3 (melden zodra Fotmob niet meer levert) is "
                "niet aan de orde. Verbruik deze run: 36 credits voor de bulk over twaalf "
                "competities plus 38 voor BTTS = 74 van een plafond van 9255, en er staan nog "
                "18456 credits van het maandplafond van 20000 open. 31 oktober is de LAATSTE DAG "
                "VAN DE MAAND, dus `suggest_cap(18530, 1)` is met opzet ruim — wat over is vervalt. "
                "DE DAG IS MET TWEE METHODES VASTGESTELD (§1): `ra_oct31_bevestiging.py` legt de "
                "Fotmob-daglijst naast de BetExplorer-fixturepagina's en ze zijn het over 15 van "
                "de 16 competities eens, 53 duels tegen 52. HET ENE VERSCHIL IS DE EREDIVISIE: "
                "Fotmob heeft CAMBUUR - GO AHEAD EAGLES (21:00 NL) en de BetExplorer-fixturepagina "
                "niet. Dat is NIET opgelost door een van de twee te geloven maar door een DERDE "
                "bron: The Odds API noteert het duel op 2026-10-31T20:00:00Z met tien boeken, dus "
                "het bestaat en het staat terecht in de run. Let op de RICHTING van dit verschil, "
                "want die is de veilige: de tweede bron ziet er een MINDER dan de eerste, en het "
                "gevaar van 6 oktober was het omgekeerde — BetExplorer had toen vijf FA Cup-duels "
                "die Fotmob niet had, en zonder die tweede bron was er 'GEEN WEDSTRIJD' "
                "opgeschreven bij duels die er gewoon waren. Een duel dat de primaire bron wel "
                "heeft, kan niet door een gat in de tweede bron verdwijnen."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn VIER publiceerbare selecties en vijf
        # plekken beschikbaar (MAX_SHORTLIST = 5, vrijdag), dus er valt er geen enkele af en
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
        s3 = json.load(open("tmp-run/ra_oct31_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_oct31_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_oct31_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct31_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct31_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct31_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

"""Run A 2 nov 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_nov02_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. ACHT van de eenentwintig competities uit de runlijst speelden, met TWAALF duels in het
inzetvenster: een maandag, en de rustigste dag sinds het interlandvenster. De Ekstraklasa sluit
zijn ronde af met drie duels, Serie A en de Primeira Liga hebben er twee, en de Premier League,
La Liga, Ligue 1, de Super Lig en de Danish Superliga elk een. Bundesliga, Championship,
Eredivisie, Belgian Pro League en de Scottish Premiership spelen niet, de vijf bekers hebben geen
ronde en de drie Europese toernooien spelen pas 4 en 5 november.

DRIE REGELS, EN ALLE DRIE HALEN HUN EIGEN LAT. Dat is sinds 20 september (§5b) niet de normale
stand: meestal staat er minstens een regel op rangorde in de lijst zonder haar drempel te halen.
Vandaag niet — zie DRIE_REGELS_EN_ALLE_DRIE_HALEN_HUN_EIGEN_LAT.

DE BEVINDING VAN DEZE RUN IS EEN REPARATIE IN `toplist.py`, NIET EEN BET. De dagranglijst van §5b
liet een selectie die haar eigen lat NIET haalt een selectie verdringen die hem WEL haalt, en dat
raakte vandaag een gepubliceerde bet. Zie DE_DAGRANGLIJST_VERDRONG_EEN_GEKWALIFICEERDE_BET.

EN EEN LOGBOEK DAT ZIJN MEETLAT HAALT. De reeks `doelpunten_onder` van poort 9 staat vandaag op 35
afgewikkelde kandidaten, en daarmee boven de ~30 die §6d eist voordat een reeks gelezen mag worden.
Zie POORT_9_HEEFT_ZIJN_MEETLAT_GEHAALD.

UNDERSTAT IS ONBEREIKBAAR en dat is nieuw vandaag. Zie UNDERSTAT_IS_VANDAAG_NIET_BEREIKBAAR.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-11-02"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-02T03:10:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


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
    for run, pad in (("A", "tmp-run/ra_nov02_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "DRIE_REGELS_EN_ALLE_DRIE_HALEN_HUN_EIGEN_LAT": (
                "De dagranglijst van §5b heeft DRIE regels en `MAX_SHORTLIST` is 3 (maandag), dus "
                "de lijst is exact vol. De lijstlengte BINDT VANDAAG NIET: er zijn precies DRIE "
                "wedstrijden waarop een selectie alle negen poorten haalt en er zijn drie plekken, "
                "dus er valt geen gekwalificeerde selectie buiten de lijst en `failed_gate = "
                "lijstlengte` krijgt vandaag geen enkele rij. DAT KLOPT PAS NA DE REPARATIE VAN "
                "VANDAAG - zie DE_DAGRANGLIJST_VERDRONG_EEN_GEKWALIFICEERDE_BET; ervoor viel de "
                "derde gekwalificeerde selectie wel uit de lijst, zonder dat iets dat meldde. "
                "ALLE DRIE HALEN HUN LAT, en dat is sinds 20 september uitzondering en geen regel: "
                "Atalanta - Parma, Under 3.5 @1,55 (Tipico) met +14,80 pp tegen de VERZWAARDE lat "
                "van 10,0 pp van poort 9, score 11,737; Radomiak Radom - Slask Wroclaw, 1 "
                "@2,2152 (Betfair, beurs, 2,24 bruto) met +18,22 pp tegen de LIGHT-lat van 16,0 "
                "pp, score 5,772; en Zaglebie Lubin - Korona Kielce, 1 @2,63 (Unibet SE) met "
                "+8,18 pp tegen de FULL-lat van 8,0 pp, score 3,782. Bij alle drie is `bet_beide "
                "= true` - ze halen hun lat op de herijkte EN op de ruwe schaal - en bij alle "
                "drie staat de zwakste stand van het (shrink, rho)-grid boven nul: +10,69, +9,69 "
                "en +6,52 pp. Dat die vlag bij een fit die vrijwel de identiteit is (a=0,994, "
                "b=-0,004) klopt, is te verwachten, maar hij is per selectie gecontroleerd en niet "
                "beredeneerd (§5a waarschuwt daar uitdrukkelijk voor). "
                "DE DERDE REGEL STAAT KRAP EN DAT HOORT ERBIJ. Zaglebie Lubin haalt zijn lat met "
                "0,18 procentpunt over; de xG-methode zegt +7,14 pp en haalt hem dus NIET, de "
                "splitsmethode zegt +12,72 pp, en de gewogen 80/20-combinatie komt op +8,18 pp "
                "uit. Poort 5 gaat open omdat beide methodes dezelfde kant van de markt kiezen "
                "(45,2% en 50,8% tegen een marktkans van 38,0%), maar het verschil tussen de twee "
                "is vijf en een half procentpunt en de uitkomst hangt aan het gewicht. "
                "LEES DE LIJST ALS 'DIT IS HET BESTE VAN VANDAAG' EN NIET ALS 'DIT IS EEN GEVONDEN "
                "VOORDEEL': §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel op "
                "de herijkte edge bestaat die geld oplevert, en dat het rendement het slechtst is "
                "bij de hoogste geclaimde edge. Het logboek staat vandaag op -7,9% over 447 "
                "afgewikkelde bets, en §5b zegt zelf dat ongeveer -10% is wat je van deze lijst "
                "mag verwachten."),
            "DE_DAGRANGLIJST_VERDRONG_EEN_GEKWALIFICEERDE_BET": (
                "DIT IS DE BEVINDING VAN DEZE RUN EN HET IS EEN REPARATIE IN `scripts/toplist.py`. "
                "De dagranglijst van §5b koos vandaag Sassuolo - Fiorentina (Under 3.5 @1,64, "
                "+7,39 pp, score 5,052) BOVEN Zaglebie Lubin - Korona Kielce (1 @2,63, +8,18 pp, "
                "score 3,780). De eerste haalt zijn lat van 8,0 pp NIET, de tweede WEL. Zo'n ruil "
                "is precies wat §5 verbiedt: 'zijn er minder gekwalificeerde bets dan "
                "MAX_SHORTLIST, lever er dan minder - vul niet aan'. "
                "ER ZATEN TWEE FOUTEN OP ELKAAR EN ZE ZIJN BEIDE GEREPAREERD. "
                "(1) `_cut` toetste `if len(boven) > n`, met `boven` de selecties boven hun lat. "
                "Vandaag stonden er DRIE boven de lat en was `MAX_SHORTLIST` DRIE, dus `3 > 3` was "
                "onwaar en de lijst werd puur op `selection_score` gevuld. De grens stond een "
                "plek verkeerd. Erger dan de grens: ook bij MINDER dan n boven de lat kon een "
                "gekwalificeerde selectie volledig uit de lijst vallen zodra er genoeg hoger "
                "scorende kandidaten onder hun lat stonden - dan verdwijnt de gemeten bet en "
                "blijft de rangorde over. De reparatie is daarom geen `>=` maar een ORDENING: "
                "eerst alles boven de lat (op score onderling), daarna de rest om de lijst aan te "
                "vullen. Staan er meer dan n boven de lat, dan is het resultaat identiek aan de "
                "oude regel. "
                "(2) De keuze BINNEN een wedstrijd liep uiteen met de analyse zelf. `build` koos "
                "per duel de hoogste `selection_score` onder alle publiceerbare selecties, dus "
                "ook onder de lat. Bij Zaglebie Lubin koos de analyse het 1X2 (+8,18 pp, score "
                "3,780, lat gehaald) en koos `toplist` de DNB (+6,50 pp, score 3,968, lat NIET "
                "gehaald): TWEE RAPPORTEN VAN DEZELFDE RUN DIE EEN ANDERE BET NOEMEN, wat §5b "
                "('report.py rendert ze uit data/run-state, dus niet overtypen') juist moet "
                "voorkomen. En die sub-lat-DNB ging daarna de dagranglijst in, waar hij op fout "
                "(1) uit de lijst viel - zo verdween een gekwalificeerde bet stil. §1a kiest 'van "
                "alle selecties die alle poorten halen die met de hoogste score', en een selectie "
                "boven de lat haalt ook de drempel; een eronder niet. De lus vergelijkt nu op "
                "(lat gehaald, score) in plaats van op score alleen. Haalt geen enkele selectie "
                "van een duel haar lat, dan verandert er niets. "
                "WAT HET VANDAAG VERANDERT: de derde regel van de lijst. Voor de reparatie stond "
                "er Sassuolo - Fiorentina Under 3.5 @1,64; erna Zaglebie Lubin - Korona Kielce 1 "
                "@2,63. Sassuolo gaat als `near_miss` met `failed_gate = edge` naar het "
                "schaduwlogboek, precies waar hij hoort. "
                "WAAROM EEN RUN DIT WEL MAG REPAREREN: dit is geen parameter en geen poort, en er "
                "zit geen afweging over risicobereidheid in - dan zou het bij de gebruiker horen "
                "(§1a, §1e). Het is een grensgeval in de code dat twee regels uit hetzelfde "
                "bestand tegen elkaar in laat lopen, en het faalt STIL: de lijst had precies de "
                "juiste lengte en elke regel droeg netjes zijn eigen label. Dezelfde faalvorm als "
                "`calibration.py settle` (§6b-5c), het Serie B-id en `promotion.match_tier` van "
                "31 oktober. Het bewijs staat in `tmp-run/ra_nov02_toplist_fix_test.py`: vijf "
                "gevallen, geen netwerk, waarvan drie de grens en twee de keuze binnen een duel."),
            "POORT_9_HEEFT_ZIJN_MEETLAT_GEHAALD_EN_DE_REM_BLIJFT": (
                "Poort 9 (§1h, de verzwaarde lat van 10,0 pp voor een Under op `FULL`-data) heeft "
                "vandaag NUL selecties tegengehouden: er was geen enkele FULL-Under in de band "
                "8,0-10,0 pp waar hij met opzet bijt. Wat er wel is gebeurd, is dat de reeks "
                "waarmee die poort beoordeeld moet worden zijn eigen meetlat heeft gehaald. "
                "`doelpunten_onder` staat op 35 AFGEWIKKELDE kandidaten met -30,4% rendement "
                "(37,1% trefkans, 13 van 35, gemiddelde geclaimde edge +8,9 pp). §6d eist ~30 "
                "gevallen voordat een reeks gelezen mag worden, en op 12 oktober stond in deze "
                "regels dat dat 'eerder een vraag voor december dan voor deze week' zou zijn. Het "
                "is 2 november en het zijn er 35. "
                "WAT DE REEKS ZEGT: de poort houdt verliezers tegen. -30,4% over 35 gevallen is "
                "de SLECHTSTE reeks van alle elf categorieen in het schaduwlogboek op een na "
                "(`odds` staat op -57,8%), en hij is slechter dan het logboek van de gespeelde "
                "bets (-7,9%). De rem doet dus wat hij moest doen, en er is geen grond om hem te "
                "verlagen of te schrappen. "
                "WAT DE REEKS NIET ZEGT: dat de LIGHT-kant er ook bij hoort. Die vraag is op "
                "12 oktober aan de gebruiker voorgelegd en beantwoord met 'eerst kijken wat deze "
                "rem doet' (§1h). Die meting is er nu, maar ze is gedaan op `FULL` en zegt over "
                "`LIGHT` niets - daar staan nog steeds tien afgewikkelde gevallen tegenover, met "
                "een rendement dat de andere kant op wijst. Een gemeten rem uitbreiden naar een "
                "populatie waar de meting hem niet steunt is wat §1c en §4 verbieden. Dit is dus "
                "een BEVINDING voor het runrapport en geen besluit dat een run zelf neemt: de "
                "poort blijft staan zoals hij staat. "
                "DE METING ERONDER IS VANDAAG OPNIEUW BEVESTIGD: `margins.py goalbias` zegt over "
                "1950 doorgerekende duels dat het model op het TOTAAL vrijwel klopt (+0,052 "
                "doelpunt per duel, z = +1,32) maar dat de GESPEELDE Under-kant op +0,660 "
                "doelpunt staat over 117 gevallen (z = +4,31), tegen -0,268 op de Over-kant (66 "
                "gevallen, z = -1,19). Die twee regels zijn twee populaties - het model en de "
                "selectie - en mogen nooit worden opgeteld. De vormfout zit er ook nog: P(Under "
                "2.5) voorspeld 42,5% tegen werkelijk 40,3%, met massa verschoven van 2 naar 4 en "
                "5 doelpunten. "
                "DE GEPUBLICEERDE UNDER VAN VANDAAG valt ruim BOVEN de band: Atalanta - Parma "
                "staat op +14,80 pp tegen een lat van 10,0. Hij is dus door poort 9 getoetst en "
                "niet langsgelaten. Trek wel ongeveer twee procentpunt van de genoemde 79,3% af "
                "voordat je haar leest - dat is de vormfout hierboven, en die staat los van de "
                "poort."),
            "UNDERSTAT_IS_VANDAAG_NIET_BEREIKBAAR": (
                "Understat is de TWEEDE, onafhankelijke xG-bron voor vijf competities (PL, La "
                "Liga, Bundesliga, Serie A, Ligue 1; §4, sinds 31 aug 2026) en hij was vandaag "
                "voor alle vier die vandaag spelen onbereikbaar. De fout is bij alle vier "
                "dezelfde en komt niet van de site maar van de netwerkgateway van de container: "
                "`URLError ... Tunnel connection failed: 502 Bad Gateway` op "
                "`https://understat.com/getLeagueData/<comp>/2025`. De proxy-status noteert hem "
                "als `connect_rejected - gateway answered 502 to CONNECT (policy denial or "
                "upstream failure)` voor `understat.com:443`. Een losse `curl` naar hetzelfde "
                "adres geeft `CONNECT tunnel failed, response 502`, dus het is niet het script. "
                "WAT DIT WEL KOST: het kalibratieblok van §6e krijgt vandaag geen Understat-arm "
                "voor de Premier League, Serie A, La Liga en Ligue 1, en de vergelijking tussen de "
                "eigen xG-arm en de Understat-arm (die sinds 19 sep structureel scheever staat: "
                "+3,11 pp op longshots tegen +0,90 voor de eigen arm) kan over deze dag niet "
                "worden gemaakt. "
                "WAT DIT NIET KOST: geen enkele bet en geen enkele kansschatting. Understat gaat "
                "per ontwerp NIET in `my_prob` - hij staat naast het eigen model in het "
                "kalibratieblok (§2, de harde grens). De kanskant van alle twaalf duels komt van "
                "Fotmob, en Fotmob leverde vandaag zonder fout: twaalf van twaalf duels met "
                "contextblok, acht van acht competitiestanden. Dat is de bron die volgens §3 "
                "('API_FOOTBALL_KEY komt er niet', punt 3) WEL vooraan in de notificatie moet "
                "zodra hij uitvalt, en dat is vandaag niet het geval. "
                "WAT ER GEBEURT ALS DIT BLIJFT: dan verliest de routine haar enige tweede "
                "xG-model en wordt het kalibratielogboek voor die vijf competities eenarmig. Dat "
                "is een verlies aan CONTROLE en niet aan kansinput. Een run repareert een "
                "netwerkpolicy niet zelf; dit hoort als constatering in `source-health.json` en "
                "als regel in de notificatie, zodat een volgende run ziet of het een dag was of "
                "een nieuwe toestand."),
            "TWEEDE_METHODE_VANGT_121_VAN_DE_173_SELECTIES_EN_DAT_IS_70_PROCENT": (
                "Over de twaalf doorgerekende wedstrijden zijn 173 selecties langs de poorten "
                "gegaan. De verdeling van de eerste dichte poort: `tweede_methode` 121, `edge` 20, "
                "`underdog` 10, `odds` 8, `context` 3, `robuustheid` 1, `doelpunten_onder` 0, en "
                "10 selecties haalden alles - die tien liggen op DRIE wedstrijden, want de "
                "0-of-1-bet-regel laat er per duel een door. "
                "ZEVENTIG PROCENT VAN ALLES VALT DUS OP POORT 5, EN DAT IS EEN REEKS EN GEEN "
                "NIEUWS: 71% op 31 oktober, 74% op 1 november, 70% vandaag. §5 ('Net niet') zegt "
                "dat een poort die een week lang alles wegvangt een BEVINDING is en geen ruis, en "
                "dit is die bevinding - maar hij hoort met zijn eigen cijfer gelezen te worden. "
                "Het schaduwlogboek meet die poort nu op 252 kandidaten, waarvan 243 afgewikkeld: "
                "46,1% trefkans en -1,7% rendement. Dat is MINDER SLECHT dan het logboek van de "
                "gespeelde bets (-7,9%) en slechter dan nul. De poort bespaart dus geld, maar "
                "weinig, en hij is met afstand de grofste zeef in de routine. "
                "WAT DIT NIET IS: een reden om hem vandaag te verzetten. §6d eist een richting "
                "over weken en verbiedt uitdrukkelijk een parameterwijziging op grond van een dag. "
                "De vraag welke van de twee methodes er stelselmatig naast zit is nog steeds niet "
                "gemeten, en vandaag is ze opnieuw goed te zien: bij Radomiak Radom - Slask "
                "Wroclaw zegt de xG-methode +12,20 pp en de splitsmethode +43,08 pp, en bij "
                "Atalanta - Parma +12,29 tegen +25,78. De splitsmethode is stelselmatig de "
                "optimistische van de twee en weegt met 0,20 mee (§1f, op uitslagen gemeten). Dat "
                "verschil is het onderzoek waard en het is openstaand punt van deze run, geen "
                "conclusie ervan."),
            "DE_INZET_IS_OP_EEN_VAN_DE_DRIE_REGELS_EEN_BEURSKOERS": (
                "EEN van de drie gepubliceerde regels heeft zijn beste prijs bij een BEURS: "
                "Radomiak Radom - Slask Wroclaw bij Betfair. §5 ('Odds') eist dat bij een "
                "beurskoers BEIDE getallen in het rapport staan, want de gebruiker ziet op de site "
                "de koers VOOR commissie en de edge is gerekend op de koers ERNA: 2,24 bruto / "
                "2,2152 na 2% commissie. De andere twee staan bij een gewone bookmaker: Atalanta - "
                "Parma bij Tipico (1,55) en Zaglebie Lubin - Korona Kielce bij Unibet SE (2,63). "
                "WAT DE GEBRUIKER MOET WETEN: zet hij in bij Betfair, dan ziet hij 2,24 staan; de "
                "+18,22 pp hierboven is al verrekend met de commissie en hij hoeft dus niets zelf "
                "af te trekken. Een op drie is vandaag minder dan de 61% die §0 "
                "(`EXCHANGE_COMMISSION`) als normale stand noemt - met drie regels is dat geen "
                "waarneming over de markt maar een klein getal."),
            "DE_VIJF_POORTEN_VAN_PARAGRAAF_1_ZIJN_ALLE_VIJF_NAGELOPEN": (
                "De bevestiging door een tweede methode is OP DE RUNLIJST ZELF gedaan en niet "
                "alleen op de analyse, zoals Run A sinds 11 oktober doet: de Fotmob-daglijst naast "
                "de BetExplorer-fixturepagina per competitie, twee losse bronnen. Ze zijn het over "
                "ALLE ZESTIEN competities eens en over het totaal: 12 duels tegen 12, zonder enig "
                "verschil. "
                "DE VIJF BEKERS SPELEN NIET, EN OOK DAT IS BIJ TWEE BRONNEN NAGETROKKEN. De "
                "Fotmob-daglijst geeft voor League Cup (133), DFB Pokal (209) en KNVB Beker (235) "
                "nul duels in het venster, en BetExplorer bevestigt dat voor alle vijf met de "
                "eerstvolgende ronde erbij: FA Cup 6 nov, Coppa Italia 1 dec, KNVB Beker 1 dec, "
                "DFB Pokal 1 dec, League Cup 15 dec. Alle vijf fixturepagina's gaven vandaag "
                "teamparen (40, 4, 8, 16 en 8), dus er is nergens een lege pagina die als "
                "bevestiging zou kunnen worden gelezen. 'Niet in de daglijst' mag nooit als GEEN "
                "WEDSTRIJD worden opgeschreven zonder tweede bron; dat is het gat dat Run A op "
                "6 oktober 2026 vijf duels kostte. "
                "DE DRIE EUROPESE TOERNOOIEN spelen deze week van woensdag tot donderdag (UCL "
                "4 nov, UEL 4-5 nov, UECL 5 nov) en de Bundesliga, Championship, Eredivisie, "
                "Belgian Pro League en Scottish Premiership hebben vandaag geen ronde. Dat is "
                "`GEEN WEDSTRIJD` en geen gat."),
            "DE_AFKAPPING_VAN_STAGE_4_BINDT_VANDAAG_NIET": (
                "Twaalf duels in het inzetvenster tegen een cap van 40 (`MAX_DEEP_ANALYSES`, "
                "maandag), dus er is NUL afgekapt en alle twaalf zijn doorgerekend. De "
                "datarijkdom-score liep van 4,5 (Rakow Czestochowa - Pogon Szczecin) tot 7,0 "
                "(Lorient - Brest); die twee getallen staan hier omdat §3 Stage 4 ze eist zodra de "
                "cap knelt, en ze staan er ook als hij dat niet doet - anders is achteraf niet na "
                "te gaan of de afkapping ergens op sloeg. "
                "GEEN ENKEL DUEL VIEL AF OP `data_tier = NONE`. TWEE duels staan op `LIGHT` omdat "
                "er een omgerekende promovendus in staat: Deportivo A Coruna (uit de Segunda "
                "Division) en Slask Wroclaw (uit de Poolse I liga). Daar geldt de lat van 16,0 pp, "
                "en een van de twee haalt hem - Radomiak Radom - Slask Wroclaw met +18,22 pp. Dat "
                "is de eerste LIGHT-bet van Run A sinds 26 oktober. Sinds de reparatie van "
                "31 oktober (`promotion.match_tier`, 'de zwakste kant wint') kan de tier van een "
                "duel niet meer stil door de andere kant worden overschreven."),
            "HET_NIVEAU_KOMT_VOOR_ZEVEN_COMPETITIES_UIT_DE_UPLIFT_EN_VOOR_EEN_UIT_HET_LOPENDE_SEIZOEN": (
                "`league_level` koos voor zeven van de acht competities de route `vorig+uplift` en "
                "voor de Danish Superliga de route `lopend`: die staat op 13 van 22 speeldagen en "
                "is daarmee over de helft, dus het niveau komt uit het lopende seizoen zelf en "
                "ongeschaald (§3 Stage 5, `SEASON_MATURE_SHARE`). De gepoolde "
                "vroeg-seizoenscorrectie is gemeten over 72 speeldagen in zeven competities en "
                "staat op factor 1,0970 (gepoold 1,1078). De Danish Superliga is bij die pool "
                "OVERGESLAGEN en dat staat met zoveel woorden in `vroeg_seizoen.overgeslagen` - "
                "een stil weggelaten waarneming is hetzelfde probleem als een stille truncatie in "
                "Stage 4 (§3 Stage 5)."),
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
        s3 = json.load(open("tmp-run/ra_nov02_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov02_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov02_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_nov02_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov02_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov02_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

"""Run A 31 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_nov01_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
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

DAG = "2026-11-01"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-01T03:12:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


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
    for run, pad in (("A", "tmp-run/ra_nov01_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "VIJF_REGELS_WAARVAN_TWEE_HUN_LAT_HALEN_EN_DRIE_OP_RANGORDE_STAAN": (
                "De dagranglijst van §5b heeft VIJF regels en `MAX_SHORTLIST` is 5 (zondag), dus "
                "de lijst is exact vol. De lijstlengte BINDT VANDAAG NIET: er zijn maar TWEE "
                "wedstrijden waarop een selectie alle negen poorten haalt, en er zijn vijf "
                "plekken — dus er valt geen gekwalificeerde selectie buiten de lijst en "
                "`failed_gate = lijstlengte` krijgt vandaag geen enkele rij. "
                "TWEE VAN DE VIJF HALEN HUN LAT ONDUBBELZINNIG: Juventus - Napoli, BTTS nee "
                "@2,1564 (Matchbook, beurs, 2,18 bruto) met +12,75 pp tegen 8,0, score 7,538; en "
                "Kasimpasa - Besiktas, BTTS nee @2,4896 (Matchbook, beurs, 2,52 bruto) met "
                "+13,22 pp tegen 8,0, score 7,058. Beide staan op `FULL`, beide hebben "
                "`bet_beide = true` — ze halen hun lat op de herijkte EN op de ruwe schaal — en "
                "bij beide staat de zwakste stand van het (shrink, rho)-grid nog ruim boven nul "
                "(+9,16 en +8,17 pp). Dat `bet_beide` bij een fit die vrijwel de identiteit is "
                "(a=0,994, b=-0,004) klopt, is te verwachten, maar het is per selectie met de "
                "vlag gecontroleerd en niet beredeneerd (§5a waarschuwt daar uitdrukkelijk voor). "
                "DRIE REGELS STAAN ONDER DE LAT EN ZIJN OP RANGORDE GEPUBLICEERD: Lyon - Angers, "
                "Under 3.5 @1,60 (Tipico) met +6,74 pp, score 4,667; Getafe - Sevilla, BTTS nee "
                "@1,784 (Matchbook, beurs) met +7,35 pp, score 4,660; en Liverpool - Arsenal, "
                "DNB Arsenal @1,8134 (Matchbook, beurs) met +6,26 pp, score 3,844. Alle drie "
                "dragen `failed_gate = edge` en `bet_beide = false`, en bij alle drie zijn de "
                "ZEVEN ANDERE POORTEN WEL opengegaan — koersband, anti-circulariteit, datatier, "
                "tweede methode, robuustheid, context en underdog. Er is dus geen poort die ze "
                "afwees; alleen de drempel, en die is sinds 20 september geen poort meer maar een "
                "afkapping (§5b). TWEE VAN DE DRIE STAAN ROBUUST KRAP: Getafe - Sevilla op +1,06 "
                "pp en Liverpool - Arsenal op +0,73 pp in de zwakste hoek van het grid. Dat is "
                "boven nul en poort 6 gaat dus open, maar het is wel het randje, en bij Getafe "
                "komt daar bij dat de splitsmethode op +0,03 pp staat: de twee methodes zijn het "
                "net eens over de richting en verder nergens over. LEES DE LIJST ALS 'DIT IS HET "
                "BESTE VAN VANDAAG' EN NIET ALS 'DIT IS EEN GEVONDEN VOORDEEL': §1g heeft op 552 "
                "afgerekende gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die "
                "geld oplevert en dat het rendement het slechtst is bij de hoogste geclaimde edge. "
                "Het logboek staat vandaag op -8,0% over 439 bets, en §5b zegt zelf dat ongeveer "
                "-10% is wat je van deze lijst mag verwachten."),
            "DRIE_MARKTEN_IN_DE_LIJST_NA_TWEE_DAGEN_WAARIN_ALLES_EEN_OVER_UNDER_WAS": (
                "De marktbalans-controle van §1a is gehaald op de INKOOP en zo ruim als ze kan: "
                "van de ELF competities die vandaag spelen hebben ALLE ELF een sportkey en kregen "
                "alle elf de volledige bulk (h2h + spreads + totals, 3 credits per competitie, 33 "
                "in totaal). Elke gekochte competitie heeft dus zowel een uitkomstmarkt (1X2, AH, "
                "DNB, DC) als een doelpuntenmarkt (O/U), en GEEN ENKEL DUEL draait voor de bet "
                "zelf op het gratis BetExplorer-marktgemiddelde. BTTS is daarna in de tweede ronde "
                "van §1a stap 2 voor 23 duels met een kandidaat-edge apart gekocht (23 credits), "
                "en dat is vandaag beslissend geweest: ZONDER DIE TWEEDE RONDE HADDEN DE TWEE "
                "ENIGE SELECTIES DIE HUN LAT HALEN NIET BESTAAN. De eerste doorrekening, vóór de "
                "BTTS-ronde, gaf voor Juventus - Napoli Under 2.5 @1,91 (+11,69 pp, score 7,485) "
                "en voor Kasimpasa - Besiktas Under 2.75 @2,01 (+10,72 pp, score 6,48); met BTTS "
                "erbij scoort op beide duels de BTTS-nee hoger en is dát de gepubliceerde "
                "selectie. Dezelfde mening, een andere markt, een hogere score (§1a, "
                "`selection_score` beslist binnen de wedstrijd). "
                "WAT ERUIT KWAM: over 479 doorgerekende selecties 174 Over/Under, 123 Asian "
                "Handicap, 90 1X2, 46 BTTS, 29 Draw No Bet en 17 Double Chance. De vijf "
                "gepubliceerde regels zijn DRIE BTTS, EEN OVER/UNDER en EEN DRAW NO BET. Dat is "
                "het noemen waard omdat de twee voorgaande rundagen voor honderd procent uit "
                "Over/Under bestonden (30 okt vier van vier, 31 okt vijf van vijf) en de gebruiker "
                "daar op 19 september terecht over viel. Het is geen maatregel en geen quotum — er "
                "is niets veranderd in de regels of de weging — maar het laat zien dat de "
                "eentonigheid van die twee dagen een uitkomst was en geen structurele vorm. "
                "NIET ELKE MARKT WAS BIJ ELK DUEL TE KOOP: de spreads-respons levert per "
                "competitie verschillende handicaplijnen, dus het aantal doorgerekende selecties "
                "per duel loopt van 7 tot 21. Dat staat per duel in `markets_checked` met de reden "
                "erbij en niet als gat (§6b-5b)."),
            "TWEEDE_METHODE_VANGT_356_VAN_DE_479_SELECTIES_EN_DAT_IS_74_PROCENT": (
                "Over de 37 doorgerekende wedstrijden zijn 479 selecties langs de poorten gegaan. "
                "De verdeling van de eerste dichte poort: `tweede_methode` 356, `edge` 60, `odds` "
                "16, `context` 15, `underdog` 14, `robuustheid` 7, `doelpunten_onder` 6, en 5 "
                "selecties haalden alles — die vijf liggen op twee wedstrijden, want de "
                "0-of-1-bet-regel laat er per duel één door. "
                "DRIEKWART VAN ALLES VALT DUS OP POORT 5, EN DAT IS GEEN NIEUWS MAAR EEN REEKS: "
                "het was 71% op 31 oktober en het is 74% vandaag. §5 ('Net niet') zegt dat een "
                "poort die een week lang alles wegvangt een BEVINDING is en geen ruis, en dit is "
                "die bevinding — maar hij hoort met zijn eigen cijfer gelezen te worden en niet "
                "met een vermoeden. Het schaduwlogboek meet die poort nu op 246 kandidaten, "
                "waarvan 237 afgewikkeld: 45,6% trefkans en -3,0% rendement. Dat is MINDER SLECHT "
                "dan het logboek van de gespeelde bets (-8,0%) en slechter dan nul. De poort "
                "bespaart dus geld, maar niet veel, en hij is met afstand de grofste zeef in de "
                "routine. WAT DIT NIET IS: een reden om hem vandaag te verzetten. §6d eist een "
                "richting over weken en verbiedt uitdrukkelijk een parameterwijziging op grond van "
                "één dag, en de vraag welke van de twee methodes er stelselmatig naast zit is een "
                "meting die nog niet is gedaan — de splitsmethode staat vandaag bij Getafe - "
                "Sevilla op +0,03 pp waar de xG-methode +9,38 pp zegt, en bij Juventus - Napoli "
                "op +2,34 tegen +15,53. Dat verschil is het onderzoek waard en het is openstaand "
                "punt van deze run, geen conclusie ervan."),
            "DE_INZET_IS_OP_VIER_VAN_DE_VIJF_REGELS_EEN_BEURSKOERS": (
                "VIER VAN DE VIJF gepubliceerde regels hebben hun beste prijs bij MATCHBOOK, een "
                "beurs, en de vijfde (Lyon - Angers) bij Tipico. §5 ('Odds') eist dat bij een "
                "beurskoers BEIDE getallen in het rapport staan, want de gebruiker ziet op de site "
                "de koers VOOR commissie en de edge is gerekend op de koers ERNA: Juventus - "
                "Napoli 2,18 bruto / 2,1564 na 2% commissie; Kasimpasa - Besiktas 2,52 / 2,4896; "
                "Getafe - Sevilla 1,80 / 1,784; Liverpool - Arsenal 1,83 / 1,8134. Dat is geen "
                "randgeval maar de normale stand sinds 5 september, toen bleek dat de beste prijs "
                "in 61% van de gevallen bij een beurs staat (§0, `EXCHANGE_COMMISSION`). WAT DE "
                "GEBRUIKER MOET WETEN: zet hij in bij Matchbook, dan ziet hij de bruto koers "
                "staan; de edge hierboven is al verrekend met de commissie en hij hoeft dus niets "
                "zelf af te trekken."),
            "DE_DREMPEL_VAN_POORT_9_HEEFT_VANDAAG_ZES_SELECTIES_TEGENGEHOUDEN": (
                "Poort 9 (§1h, de verzwaarde lat van 10,0 pp voor een Under op `FULL`-data) heeft "
                "vandaag ZES selecties als eerste dichte poort tegengehouden, en twee daarvan "
                "stonden bovenaan de RUWE dagranglijst: Excelsior - FC Twente Under 3.5 @1,72 "
                "(+9,22 pp) en Eintracht Frankfurt - Hamburger SV Under 3.5 @1,84 (+9,35 pp). "
                "Beide zitten in de band 8,0-10,0 pp waar die poort met opzet bijt. De reeks staat "
                "nu op 29 afgewikkelde kandidaten met -22,0% rendement (41,4% trefkans): de poort "
                "doet zijn werk, en hij nadert de ~30 gevallen die §6d eist voordat die reeks "
                "gelezen mag worden. DE METING ERONDER IS VANDAAG OPNIEUW BEVESTIGD: `margins.py "
                "goalbias` zegt over 1870 doorgerekende duels dat het model op het TOTAAL klopt "
                "(+0,041 doelpunt per duel, z = +1,01) maar dat de GESPEELDE Under-kant op +0,668 "
                "doelpunt staat over 115 gevallen (z = +4,32), tegen -0,245 op de Over-kant (65 "
                "gevallen, z = -1,08). Die twee regels zijn twee populaties — het model en de "
                "selectie — en mogen nooit worden opgeteld. De gepubliceerde Under van vandaag "
                "(Lyon - Angers, +6,74 pp) valt ONDER die band en poort 9 laat hem met opzet door: "
                "daar hoort `edge` de bindende poort te zijn, en dat is hij ook — de regel staat "
                "op rangorde in de lijst en niet op een gehaalde lat."),
            "DE_VIJF_POORTEN_VAN_PARAGRAAF_1_ZIJN_ALLE_VIJF_NAGELOPEN": (
                "De bevestiging door een tweede methode is OP DE RUNLIJST ZELF gedaan en niet "
                "alleen op de analyse, zoals Run A sinds 11 oktober doet: de Fotmob-daglijst naast "
                "de BetExplorer-fixturepagina per competitie, twee losse bronnen. Ze zijn het over "
                "ALLE ZESTIEN competities eens en over het totaal: 37 duels tegen 37. Dat is de "
                "eerste run in weken zonder enig verschil tussen de twee bronnen. "
                "DE VIJF BEKERS SPELEN NIET, EN OOK DAT IS BIJ TWEE BRONNEN NAGETROKKEN. De "
                "Fotmob-daglijst geeft voor League Cup (133), DFB Pokal (209) en KNVB Beker (235) "
                "nul duels in het venster, en BetExplorer bevestigt dat voor alle vijf met de "
                "eerstvolgende ronde erbij: FA Cup 6 nov, League Cup 15 dec, Coppa Italia 1 dec, "
                "KNVB Beker 1 dec. De DFB Pokal-fixturepagina van BetExplorer is vandaag leeg (0 "
                "teamparen), dus daar is Fotmob de enige bron die iets zegt — noteer dat als "
                "zodanig en niet als bevestiging. 'Niet in de daglijst' mag nooit als GEEN "
                "WEDSTRIJD worden opgeschreven zonder tweede bron; dat is het gat dat Run A op "
                "6 oktober 2026 vijf duels kostte. "
                "DE DRIE EUROPESE TOERNOOIEN spelen deze week van dinsdag tot donderdag (UCL "
                "3 nov, UEL 4-5 nov, UECL 5 nov) en de Championship en de Ekstraklasa hebben "
                "vandaag geen ronde. Dat is `GEEN WEDSTRIJD` en geen gat."),
            "DE_AFKAPPING_VAN_STAGE_4_BINDT_VANDAAG_NIET": (
                "37 duels in het inzetvenster tegen een cap van 55 (`MAX_DEEP_ANALYSES`, zondag), "
                "dus er is NUL afgekapt en alle 37 zijn doorgerekend. De datarijkdom-score liep "
                "van 4,75 tot 8,5; die twee getallen staan hier omdat §3 Stage 4 ze eist zodra de "
                "cap knelt, en ze staan er ook als hij dat niet doet — anders is achteraf niet na "
                "te gaan of de afkapping ergens op sloeg. EEN DUEL VIEL AF OP `data_tier = NONE`: "
                "Viborg - AC Horsens, omdat de omrekening van AC Horsens buiten het gemeten bereik "
                "van `conversion_in_range` valt (§4, Promovendi). Dat is geen storing maar precies "
                "wat die regel voorschrijft, en sinds de reparatie van 31 oktober "
                "(`promotion.match_tier`, 'de zwakste kant wint') kan de tier van het duel niet "
                "meer stil door de andere kant worden overschreven. ACHT duels staan op `LIGHT` "
                "omdat er een omgerekende promovendus of degradant in staat; daar geldt de lat van "
                "16,0 pp en geen van de acht komt er in de buurt."),
            "HET_NIVEAU_KOMT_VOOR_TIEN_COMPETITIES_UIT_DE_UPLIFT_EN_VOOR_EEN_UIT_HET_LOPENDE_SEIZOEN": (
                "`league_level` koos voor tien van de elf competities de route `vorig+uplift` en "
                "voor de Danish Superliga de route `lopend`: die staat op 13 van 22 speeldagen en "
                "is daarmee over de helft, dus het niveau komt uit het lopende seizoen zelf en "
                "ongeschaald (§3 Stage 5, `SEASON_MATURE_SHARE`). De gepoolde "
                "vroeg-seizoenscorrectie is gemeten over 100 speeldagen in tien competities en "
                "staat op factor 1,0966 (gepoold 1,1044). De Danish Superliga is bij die pool "
                "OVERGESLAGEN en dat staat met zoveel woorden in `vroeg_seizoen.overgeslagen` — "
                "een stil weggelaten waarneming is hetzelfde probleem als een stille truncatie in "
                "Stage 4 (§3 Stage 5)."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn TWEE wedstrijden met een selectie die
        # alle negen poorten haalt en vijf plekken (MAX_SHORTLIST = 5, zondag), dus er valt er
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
        s3 = json.load(open("tmp-run/ra_nov01_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov01_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov01_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_nov01_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov01_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov01_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

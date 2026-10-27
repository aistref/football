"""Run A 27 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct27_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. VIER van de eenentwintig competities uit de runlijst speelden, met TWEEENTWINTIG duels
in het inzetvenster, en NEGENTIEN daarvan zijn bekerwedstrijden: een bekerdinsdag, en dat is de
hele vorm van deze dag. Serie A heeft drie midweekse duels, de DFB Pokal acht, de KNVB Beker
negen en de League Cup twee.

DE BEKERS STONDEN DEZE KEER IN DE FOTMOB-DAGLIJST, en dat is de bevinding van vandaag — zie
DE_BEKERS_STAAN_WEL_IN_DE_DAGLIJST_EN_HET_GAT_ZAT_IN_DE_ADMINISTRATIE.

ELF VAN DE 22 DUELS KOMEN OP NONE UIT, en dat is bij een beker normaal en geen storing: de
amateurclubs van de KNVB Beker en de Regionalliga-ploegen van de DFB Pokal staan in geen
divisie waarvoor een gemeten omrekenfactor bestaat.

EN ER IS VANMORGEN EEN FOUT IN DE REPO GEVONDEN DIE EEN SCHIJNEDGE ZOU HEBBEN OPGELEVERD, vóór
de analyse en niet erna: `ra_names.resolve` koppelde FC Eindhoven aan PSV Eindhoven. Zie
DE_NAAMKOPPELING_IS_VANMORGEN_GEREPAREERD_EN_DAT_SCHEELDE_EEN_SCHIJNEDGE.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-27"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-10-27T03:35:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok (wintertijd)


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
    for run, pad in (("A", "tmp-run/ra_oct27_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "EEN_BEKERDINSDAG_VAN_22_DUELS_WAARVAN_19_IN_EEN_BEKER": (
                "VIER van de eenentwintig competities uit de runlijst hebben vandaag een duel in "
                "het inzetvenster, samen TWEEENTWINTIG wedstrijden — het drukste Run A-programma "
                "van de maand, en negentien duels zitten in een beker. Serie A speelt een "
                "midweekse ronde met drie duels in het venster (Sassuolo - Lazio, Roma - Cagliari "
                "en Torino - Como); de DFB Pokal heeft de tweede ronde met acht duels, de KNVB "
                "Beker negen en de League Cup twee. De Premier League, La Liga, Bundesliga, "
                "Ligue 1, Championship, Eredivisie, Primeira Liga, Belgian Pro League, Super Lig, "
                "Scottish Premiership, Danish Superliga en Ekstraklasa hebben niets op de "
                "kalender: hun volgende ronde begint 30 oktober of 1 november. De drie Europese "
                "toernooien spelen pas 3 en 5 november, de FA Cup 6 november en de Coppa Italia "
                "1 december. Dat is GEEN WEDSTRIJD en geen storing (§3 Stage 2)."),
            "DE_BEKERS_STAAN_WEL_IN_DE_DAGLIJST_EN_HET_GAT_ZAT_IN_DE_ADMINISTRATIE": (
                "DIT IS DE BELANGRIJKSTE BEVINDING VAN DE RUN en ze gaat over het vinden van "
                "wedstrijden, niet over de analyse. De vijf bekers van `prompts/run-a.md` hebben "
                "geen `fotmob_id` in `data/coverage.json`, dus `runwindow.matches_for_run` kan ze "
                "niet filteren, en elke run van oktober heeft ze daarom langs BetExplorer gedaan. "
                "Vandaag levert die route 19 duels in het venster (League Cup 2, DFB Pokal 8, "
                "KNVB Beker 9) — EN DE FOTMOB-DAGLIJST VAN 27 OKTOBER HEEFT ZE ALLE DRIE GEWOON "
                "STAAN: EFL Cup onder id 133 met 2 duels, DFB Pokal onder 209 met 8 en KNVB Cup "
                "onder 235 met 9. Dezelfde aantallen als BetExplorer, dus de twee bronnen zijn "
                "het over alle drie eens en de dag is met twee methodes vastgesteld (§1). "
                "HET GAT ZAT DUS NIET IN DE BRON MAAR IN DE ADMINISTRATIE, en dat is precies de "
                "stille faalvorm van §6b-5b: een controle die groen staat omdat ze een rij niet "
                "meet. Wat het verschil praktisch uitmaakt: via de daglijst komen de duels mét "
                "`match_id`, dus mét context, opstelling, uitvallers en poort 7 — via BetExplorer "
                "alleen met namen en een koers. Dat is wat het op 6 oktober kostte, toen de FA "
                "Cup-kwalificatie alleen bij BetExplorer stond en vier van de vijf duels niet "
                "door te rekenen waren. `ra_oct27_cupmatches.py` haalt ze nu uit de daglijst. "
                "DE DRIE ID'S ZIJN NIET IN coverage.json GEZET: ze zijn vandaag voor het eerst "
                "gemeten, een beker heeft geen stand (dus `idcheck.py` kan ze niet groen "
                "verklaren zoals de 33 competitie-id's), en de voor-de-hand-liggende volgende "
                "stap is nagaan of die id's ook op dagen buiten een bekerronde kloppen. Het "
                "staat als actiepunt met owner = ik in het dagrapport."),
            "DE_NAAMKOPPELING_IS_VANMORGEN_GEREPAREERD_EN_DAT_SCHEELDE_EEN_SCHIJNEDGE": (
                "Tweede bevinding, gevonden VOOR de analyse en daarom ook meteen toegepast (§4: "
                "meet een nieuwe factor liever vóór de analyse van de dag dan erna, dan hoeft de "
                "afweging over terugwerkende kracht niet). `tmp-run/ra_names.resolve` koppelde op "
                "een DEELVERZAMELING van tokens: `tokens(a) <= tokens(b) or tokens(b) <= "
                "tokens(a)`. Dat zegt alleen dat alle woorden van de korte naam in de lange "
                "voorkomen en niet WAAR ze staan. `fc` staat in `_DROP`, dus FC Eindhoven houdt "
                "het ene token `eindhoven` over, en dat is een deelverzameling van {psv, "
                "eindhoven}: DE EERSTE-DIVISIECLUB FC EINDHOVEN KOPPELDE AAN PSV EINDHOVEN IN DE "
                "EREDIVISIE-STAND. Precies één treffer, dus de veiligheidsregel 'alleen bij één "
                "kandidaat' ving het niet, en FC Eindhoven - FC Volendam kwam op FULL uit met de "
                "xG van de kampioen achter de thuisploeg. GEEN ENKELE VAN DE NEGEN POORTEN KAN "
                "DAT ZIEN — het is geen te ruime kans maar een verkeerde ploeg. Dezelfde faalvorm "
                "als de Jong Ajax-koppeling waarop `promotion.measure_gap` op 31 augustus een "
                "factor van 1.010 vond, en de eis is daarom ook dezelfde die §4 al aan "
                "`promotion.find_team` stelt: een afkorting laat de STAART weg, nooit de KOP. "
                "MAAR DIE EERSTE REPARATIE WAS NIET GENOEG, en dat is de tweede helft van deze "
                "bevinding. Een voorvoegselregel op woordniveau liet er een door die even erg is: "
                "Excelsior '31 (Tweede Divisie, Rijssen) koppelde aan Excelsior (Eredivisie, "
                "Rotterdam), want het ene token `excelsior` is een LEIDEND voorvoegsel van "
                "`excelsior 31` — daar zit het onderscheidende deel juist in de STAART. De les van "
                "die twee samen: er is geen POSITIEregel die beide gevallen vangt, want het "
                "onderscheidende deel kan vooraan staan (PSV, Jong) of achteraan ('31, II). Wat "
                "deze lus werkelijk hoort op te vangen is alleen het verschil in RUISWOORDEN — de "
                "daglijst schrijft `Wigan` en de tabel `Wigan Athletic`. De eis is daarom: gelijk "
                "NA het weglaten van `_DROP`, en anders niet. Een echte afkorting die meer weglaat "
                "dan een ruiswoord (QPR, M'gladbach) hoort in ALIASES te staan, waar ze expliciet "
                "en na te lopen is, en niet in een regel die raadt. `teamnames.is_abbreviation` "
                "doet dat nu, en de functie staat in "
                "`scripts/` en niet in `tmp-run/`, zodat er één implementatie is en geen twee die "
                "uiteenlopen (dezelfde les als de `ob`-alias van gisteren). REGRESSIE "
                "NAGELOPEN over alle 44 teamnamen van vandaag: precies TWEE verschillen, en dat "
                "zijn exact deze twee ploegen — FC Eindhoven (nu langs de promovendi-omrekening "
                "van §4, waar hij op `conversion_in_range` alsnog op NONE uitkomt) en "
                "Excelsior '31 (nu NONE, want hij staat niet in de Eerste Divisie-stand). Geen "
                "enkele andere koppeling verandert. Zelftest in "
                "`ra_oct27_namecheck.py`, 24 gevallen. NIET AANGERAAKT: `scripts/settling.py` heeft dezelfde "
                "deelverzamelingsregel, maar daar is ze met opzet ruim ('ruim, niet streng') en "
                "beslist `lookup` op het PAAR thuis-en-uit plus de eis van precies één kandidaat. "
                "Dat is een ander codepad met een eigen rem; het staat als waarneming in het "
                "runrapport en niet als reparatie, want een poort verzetten die niet knelt is "
                "geen werk dat een run op eigen initiatief doet."),
            "TWAALF_VAN_DE_22_DUELS_OP_NONE_EN_DAT_IS_BIJ_EEN_BEKER_NORMAAL": (
                "ACHT duels komen op FULL uit, TWEE op LIGHT en TWAALF op NONE. Dat laatste is bij "
                "een bekerronde de verwachting en geen storing: een beker heeft zelf geen stand, "
                "dus de basis ligt per WEDSTRIJD (§4, 15 sep 2026) en een ploeg die niet in de "
                "basisdivisie staat moet uit de divisie eronder worden omgerekend — één divisie "
                "diep, want verder is er geen meting. Van de twaalf NONE-duels zijn er ACHT waar "
                "de ploeg in geen enkele divisie staat waarvoor een factor bestaat: Fleetwood Town "
                "(League One/Two, twee divisies onder de Premier League), RW Essen en Sonnenhof "
                "Großaspach (3. Liga en Regionalliga, onder de 2. Bundesliga), en de vijf clubs "
                "onder de Eerste Divisie — Excelsior '31, Barendrecht, Kloetinge, Rijnsburgse Boys "
                "en Koninklijke HFC. De andere VIER vallen op "
                "`promotion.conversion_in_range`, en dat is de Coventry-val die §4 beschrijft: "
                "Bochum, Karlsruher SC, FC Eindhoven en Almere City FC zijn wél omgerekend, maar "
                "hun relatieve sterkte valt buiten het gemeten invoerbereik, en buiten dat bereik "
                "is er geen meting en dus geen onafhankelijke kansinput op het niveau waarop "
                "gespeeld wordt. VIER DUELS ZIJN DOOR `shared_lower_division` GERED: Bradford "
                "City - Peterborough United staan beide in League One (FULL), Elversberg - "
                "Darmstadt beide in de 2. Bundesliga (FULL), en Helmond Sport - Willem II en "
                "Roda JC - De Graafschap beide in de Eerste Divisie (LIGHT, want die divisie "
                "heeft geen xG bij Fotmob). Daar valt niets te overbruggen, dus wordt het duel in "
                "die divisie doorgerekend zonder omrekening — en dan geldt 'een omgerekende ploeg "
                "is nooit FULL' niet, want er is niets omgerekend."),
            "HERIJKING": (
                "§1g, één fit per run uit data/calibration.jsonl: a=0.9828, b=-0.0112 op 6060 "
                "afgerekende gevallen t/m 2026-10-26 — het ruwe model zei gemiddeld 33,3% en het "
                "gebeurde 33,3%. `fitted_through` staat dus op de vórige rundag, zoals §6b-5c "
                "eist; de 33 waarnemingen van 26 oktober zijn vanmorgen door `calibration.py "
                "settle` afgewikkeld voordat de fit is gelezen. De correctie VERLAAGT vandaag "
                "over vrijwel de hele speelbare band: ongeveer -0,1 pp op 40%, -0,3 pp op 50% en "
                "-0,6 pp op 70%. Gevolg voor §5a: een selectie die de herijkte lat haalt, haalt "
                "hem ook ruw, en dat is vandaag voor de enige regel bóven de lat ook zo "
                "(`bet_beide = true` bij Sassuolo - Lazio, +15,15 pp herijkt tegen +15,64 ruw). "
                "De twee regels eronder staan op `bet_beide = false`: zij halen hun lat op geen "
                "van beide schalen en zijn op rangorde gepubliceerd (§5b). Vertrouw die vlag en "
                "niet de redenering — §5a waarschuwt daar uitdrukkelijk voor, omdat de fit elke "
                "run een ander getal is."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "prompts/run-a.md: dertien competities en acht toernooien. GEANALYSEERD: Serie A "
                "(3 duels), League Cup (2), DFB Pokal (8) en KNVB Beker (9). GEEN WEDSTRIJD: "
                "Premier League, La Liga, Bundesliga, Ligue 1, Championship, Eredivisie, "
                "Primeira Liga, Belgian Pro League, Super Lig, Scottish Premiership, Danish "
                "Superliga, Ekstraklasa, UEFA Champions League, UEFA Europa League, UEFA "
                "Conference League, FA Cup en Coppa Italia. Geen enkele competitie viel op "
                "BUITEN DATADEKKING en geen enkele op AFGEKAPT: de cap is 40 (dinsdag) en er zijn "
                "22 duels, dus de cap bindt nergens. De laagste datarijkdom in de run is 4,5 en "
                "de hoogste 7,0; omdat er niets is afgekapt zijn er geen twee scores rond de "
                "grens te noemen."),
            "DRIE_REGELS_WAARVAN_EEN_ZIJN_EIGEN_LAT_HAALT": (
                "MAX_SHORTLIST = 3 (dinsdag) en er zijn precies DRIE duels met een publiceerbare "
                "selectie, dus de lijstlengte bindt NIET en er valt geen gekwalificeerde selectie "
                "af. De lijst, op selection_score: (1) Sassuolo - Lazio, Under 2.75 @2,06 "
                "(Pinnacle), +15,15 pp, score 9,649 — de enige regel die zijn eigen lat van 8,0 pp "
                "haalt, en met 15,15 pp haalt hij ruim de verzwaarde lat van poort 9 (10,0 pp "
                "voor een Under op FULL). (2) Torino - Como, BTTS nee @2,3524 (Matchbook, beurs: "
                "2,38 bruto), +5,28 pp, score 2,523 — ONDER de lat, op rangorde gepubliceerd. "
                "(3) Roma - Cagliari, Under 3 @1,84 (Coolbet), +3,82 pp, score 2,222 — ONDER de "
                "lat, op rangorde gepubliceerd. Alle drie boven de ondergrens van "
                "3,0 pp die `toplist._publiceerbaar` aanhoudt (wat te zwak is om te loggen, is te "
                "zwak om te spelen). §5b is uitdrukkelijk dat zo'n lijst GEEN selectie van "
                "winnaars is maar een rangschikking van wat het model vandaag het sterkst vindt; "
                "§1g heeft op 552 afgerekende gevallen gemeten dat er géén drempel op de herijkte "
                "edge bestaat die geld oplevert, en dat het rendement het slechtst is bij de "
                "hóógste geclaimde edge. MAX_LIGHT_IN_SHORTLIST = 2 bindt niet: alle drie de "
                "regels staan op FULL. EN LET OP WAT DE DRIE GEMEEN HEBBEN: alle drie zijn "
                "Serie A, alle drie zijn een doelpuntenmarkt en alle drie wedden op WEINIG "
                "doelpunten — zie "
                "ALLE_DRIE_DE_REGELS_WEDDEN_OP_WEINIG_DOELPUNTEN_EN_DAT_IS_DE_SCHEVE_KANT."),
            "ALLE_DRIE_DE_REGELS_WEDDEN_OP_WEINIG_DOELPUNTEN_EN_DAT_IS_DE_SCHEVE_KANT": (
                "Lees dit vóór de regels zelf. §6g meet dat de Under-kant de verliezende kant van "
                "dit logboek is, en vandaag staan alle DRIE de regels op de weinig-doelpuntenkant "
                "— Under 2.75, Under 3 en BTTS 'nee', en die laatste is dezelfde wedding in een "
                "andere markt. `margins.py goalbias` van vanmorgen over 1697 doorgerekende duels: het "
                "model als geheel klopt, maar de duels waar werkelijk een Under is GESPEELD "
                "leverden meer doelpunten dan verwacht. Daar bovenop staat de vormfout in "
                "`score_grid`: massa verschoven van 2 doelpunten naar 4 en 5, waardoor P(Under) "
                "bij élk duel ongeveer twee procentpunt te hoog staat. TREK DUS ONGEVEER TWEE "
                "PROCENTPUNT van de genoemde kansen af voordat je ze leest. "
                "EN DIT IS HET PUNT DAT VANDAAG SCHERPER STAAT DAN GISTEREN: poort 9 (§1h) dekt "
                "maar één van de drie vormen van deze wedding. Hij geldt alleen voor "
                "Over/Under op de Under-kant op FULL-data, en alleen in de band 8-10 pp. De twee "
                "Unders van vandaag vallen daar buiten (+15,15 pp staat erboven, +3,82 pp "
                "eronder) en BTTS 'nee' is er met opzet buiten gehouden — §1h punt 2: 15 "
                "afgewikkelde BTTS-picks in beide richtingen samen is geen meting, en dat is "
                "'het eerste wat opnieuw bekeken hoort te worden zodra die reeks ~30 haalt'. "
                "Vandaag is dus een dag waarop de rem op geen van de drie gepubliceerde regels "
                "iets doet, terwijl alle drie op de kant staan waar de meting de schade vindt. "
                "DEZE RUN VERANDERT ER NIETS AAN: §1h punt 3 en §6g leggen vast dat een run een "
                "poort nooit op eigen initiatief verzet en dat de vraag pas opnieuw wordt "
                "voorgelegd als de reeks van teken draait of als de vormfout is gerepareerd. Het "
                "staat als bevinding in het runrapport en in het dagrapport onder 'Wat er nog "
                "moet gebeuren'. En lees §5b erbij: een lijst die dagen achtereen uit één hoek "
                "komt is een signaal over het MODEL en niet over de rangorderegel — gisteren "
                "stonden alle drie de regels ook op de Under-kant, dus dit is de tweede dag op "
                "rij."),
            "POORT_8_EN_POORT_9_BINDEN_VANDAAG_NERGENS_EN_DAT_KOMT_DOOR_DE_POORTVOLGORDE": (
                "Poort 8 (§1e, ondergrens `sides.UNDERDOG_FLOOR` = 0,35) en poort 9 (§1h, "
                "`unders.BINDS_FROM` = 2026-10-12) zijn voor elke selectie aangeroepen met "
                "`today=2026-10-27`, zodat het stilstandvenster van 25 t/m 30 september en de "
                "ingangsdatum van poort 9 uit de code worden gelezen in plaats van geraden. "
                "BEIDE HOUDEN VANDAAG NUL SELECTIES TEGEN, op geen van beide schalen — "
                "`poort8_geblokkeerd`, `poort8_ruw` en `poort9_geblokkeerd` zijn alle drie leeg. "
                "Dat is geen versoepeling maar de POORTVOLGORDE, en het is precies het mechanisme "
                "dat §1e op 15 september beschrijft voor de reeks die niet wilde groeien: "
                "`tweede_methode` staat vóór `underdog`, en die poort vangt vandaag 62 van de 79 "
                "selecties af over 9 van de 10 doorgerekende duels. Wat poort 8 anders zou "
                "hebben getoetst, komt er dus niet eens aan. De twee schaduwreeksen groeien "
                "vandaag daarom niet: `underdog` staat op 232 afgewikkelde gevallen en "
                "`underdog_ruw` op 17, en die twee blijven twee populaties die nooit mogen worden "
                "opgeteld."),
            "TWEEDE_METHODE_VANGT_62_VAN_DE_79_SELECTIES_EN_DAT_IS_EEN_WAARNEMING": (
                "De poortverdeling van vandaag is scheef: van de 79 doorgerekende selecties "
                "sneuvelen er 62 op `tweede_methode` (poort 5: de twee methodes moeten de markt "
                "dezelfde kant op verslaan), 6 op `context` (poort 7), 2 op de koersband "
                "(poort 2) en 5 op `edge`; 4 selecties halen alle negen poorten. §5 'Net niet' "
                "zegt met zoveel woorden dat dit de waarneming is om op te letten: 'valt er een "
                "week lang alles af op tweede_methode, dan is de vraag of de twee methodes "
                "systematisch uiteenlopen — en dat is een bevinding, geen ruis'. EEN DAG IS GEEN "
                "WEEK en vandaag is er een voor de hand liggende verklaring die geen bevinding is: "
                "negentien van de 22 duels zijn bekerwedstrijden tussen ploegen van ONGELIJKE "
                "sterkte, en juist daar lopen een xG-model en een thuis/uit-doelpuntensplitsing "
                "het verst uiteen. De splitsmethode is bovendien al sinds §6e (22 aug) de scheefste "
                "van de twee. HET STAAT HIER ALS WAARNEMING MET EEN GETAL, zodat een volgende run "
                "ziet of het aanhoudt op een gewone competitiedag; er wordt vandaag geen poort en "
                "geen gewicht op verzet (§6d: niet lezen onder ~30 gevallen, en zeker niet op één "
                "dag). De reeks `tweede_methode` staat in `shadow.py stats` en bespaart tot nu toe "
                "aantoonbaar geld."),
            "DE_SCHIJNEDGE_VAN_38_PROCENTPUNT_IS_WEG_EN_ALLEEN_DE_KOERSBAND_STOND_ERVOOR": (
                "Dit is het scherpste gevolg van de naamreparatie van vanmorgen, en het hoort hier "
                "omdat het laat zien hoe dun de bescherming was. In de EERSTE doorrekening van "
                "vandaag stond de hoogste RUWE edge van de hele run niet bij een bet maar bij "
                "Excelsior '31 - ADO Den Haag: 1X2 op de thuisploeg @12,66, +37,85 pp met een ruwe "
                "selection_score van 8,658 — de TWEEDE plek van de ruwe dagranglijst, vlak onder "
                "Sassuolo - Lazio. DAT GETAL BESTOND ALLEEN omdat Excelsior '31 (Tweede Divisie) "
                "aan Excelsior (Eredivisie) was gekoppeld. Na de reparatie is het duel NONE en is "
                "de regel uit de ruwe lijst verdwenen; die lijst wordt nu aangevoerd door "
                "Sassuolo - Lazio met Torino - Como op twee. LEES WAT ER TUSSEN DIE SCHIJNEDGE EN "
                "EEN GEPUBLICEERDE REGEL STOND: alleen poort 2, de koersband MAX_ODDS = 6,00. Die "
                "poort bestaat om een andere reden — buiten de band is de kansschatting te "
                "onnauwkeurig om edge zinvol te noemen (§0) — en hij is GEEN verdediging tegen een "
                "verkeerde PLOEG; hij hield deze selectie bij toeval tegen, omdat de koers van een "
                "amateurclub tegen een profclub nu eenmaal hoog is. Was het een Eerste-Divisieclub "
                "geweest met een koers van 4,50, dan had niets hem tegengehouden. Van de 79 "
                "selecties van ná de reparatie vallen er nog TWEE op `odds`, beide een 1X2 op een "
                "buitenstaander (Cagliari @10,80 en Werder Bremen @7,20) — tegen zes vóór de "
                "reparatie. En de les die blijft staan: dat de grootste geclaimde edge van de dag "
                "bij de zwakste ploeg op de hoogste koers stond, is precies het patroon waar §1g "
                "voor waarschuwt — alleen was het hier niet eens een modelfout maar een verkeerde "
                "ploeg."),
            "GEEN_VERPLAATSTE_WEDSTRIJD_EN_GEEN_ENKELE_STADIONNAAM": (
                "`context.check_venue` is voor alle 22 duels gedraaid en gaf 22 keer "
                "`relocated = false`. Lees dat met de beperking die §1c er zelf bij zet: de "
                "respons gaf voor geen enkel duel een stadionnaam (`venue.name = null`), dus de "
                "controle vergeleek twee keer niets en kon niets vinden. Dat is dezelfde stand "
                "als op 25 en 26 oktober en het is geen storing van deze run, maar het betekent "
                "wel dat `relocated = false` vandaag 'niet gemeten' betekent en niet 'gemeten en "
                "in orde'. Wat de controle hoe dan ook níet vangt, is dat een fixture van "
                "eigenaar is gewisseld — dat is nieuws en geen data, en een geplande run heeft "
                "geen nieuwsbron (Rennes - PSG, 23 aug 2026)."),
            "MARKTBALANS_ZES_MARKTEN_MAAR_ELF_DUELS_ZONDER_BESTE_PRIJS": (
                "79 selecties over zes markten en 10 doorgerekende duels. Per markt: 1X2 29 "
                "selecties in 4 competities, Over/Under 26 in 2, Asian Handicap 14 in 1, BTTS 6 "
                "in 1, Draw No Bet 2 in 1 en Double Chance 2 in 1. De marktbalans-controle van "
                "§1a is GEHAALD OP DE INKOOP: beide inkoopbare competities (Serie A en DFB Pokal) "
                "kregen de bulk-aanroep met zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een "
                "doelpuntenmarkt (O/U), 3 credits per competitie. Daarna kregen 4 duels de tweede "
                "ronde BTTS (1 credit per duel). Totaal 9 van de 18.661 credits, plafond 1864 "
                "(`suggest_cap`). MAAR LEES DIT ERBIJ, want het is vandaag de grootste beperking "
                "van de run: ELF VAN DE 22 DUELS HEBBEN GEEN BESTE PRIJS. De League Cup en de "
                "KNVB Beker hebben geen sportkey bij The Odds API — `api_check.py` noemt 49 "
                "actieve competities en geen van beide staat erbij — dus daar is het gratis "
                "BetExplorer-MARKTGEMIDDELDE de enige 1X2-bron en zijn er geen spreads, geen "
                "totals en geen BTTS. Dat is GEEN krap plafond maar een ontbrekende competitie "
                "bij de bron, en het hoort als zodanig gemeld (§1a): de edge valt daar "
                "systematisch te laag uit, dus conservatief en zonder risico op te veel bets, "
                "maar niet vergelijkbaar met een duel waar de beste prijs wél bekend is, en de "
                "bookmaker is er niet herleidbaar. Alle drie de gepubliceerde regels komen uit "
                "Serie A, waar de beste prijs er wél is."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn niet te halen — §3 Stage 5 meet "
                "sinds 20 sep 2026 dat Forebet 403 geeft, de Pinnacle-artikelroute 404, Matchbook "
                "530 en voetbalwedden.net de duels van de dag niet noemt — dus wat deze stap "
                "vandaag invult, is de prijs van PINNACLE APART, los van de beste prijs waarop "
                "wordt gespeeld. 1X2 (`ra_oct27_pinnacle.py`): 3 van de 22 duels hebben een "
                "Pinnacle-1X2, alle drie in Serie A, met een gemiddelde marge van 3,51% en een "
                "gemiddelde absolute afstand tot het eigen oordeel van 3,95 pp — dicht bij "
                "Pinnacle, en dus geen van de grote afwijkingen die op 26 oktober in de Super Lig "
                "stonden. Op de doelpuntenkant (`ra_oct27_pinnacle_ou.py`, push-gecorrigeerd "
                "zoals op 25 okt gerepareerd): dezelfde 3 duels hebben een Pinnacle-totaal, en "
                "ALLE DRIE STAAN BOVEN PINNACLE OP DE UNDER-KANT, gemiddeld +9,93 pp. De "
                "gepubliceerde Sassuolo - Lazio staat daar met +14,26 pp op lijn 2.75 het verst "
                "vanaf. DAT IS EEN ONAFHANKELIJKE AANWIJZING IN DEZELFDE RICHTING als de "
                "vormfout van §6g — de scherpste bookmaker van de markt zet P(Under) lager dan "
                "dit model, bij alle drie de duels — en het is de tweede meting die dat vandaag "
                "zegt. HARDE GRENS (§2/§4): geen van deze getallen gaat in `my_prob` of "
                "`prob_sources`; ze horen in de vergelijking en niet in de kansschatting."),
            "UNDERSTAT_DEKT_DRIE_VAN_DE_22": (
                "Understat levert team-xG voor vijf competities (§4) en één ervan speelt vandaag: "
                "Serie A. De drie Serie A-duels hebben daarmee een ECHT onafhankelijk tweede "
                "xG-model in `prob_sources` — Fotmob-xG en Fotmob-splits zijn twee doorsnedes van "
                "dezelfde meting, Understat is een ander model. Voor de negentien bekerduels is "
                "Fotmob de enige xG-bron, en dat is precies de afhankelijkheid die §3 noemt als "
                "het enige geval waarin de ontbrekende API_FOOTBALL_KEY alsnog een echte vraag "
                "wordt: valt Fotmob om, dan is er voor die duels geen onafhankelijke kansinput "
                "meer en levert elke run gegarandeerd nul bets. Fotmob leverde vandaag zonder "
                "fout, voor alle 22 duels inclusief de context."),
            "VROEG_SEIZOEN_EN_NIVEAU": (
                "`model.uplift_observations` + `early_season_uplift` (§3 Stage 5): factor 1,0949, "
                "berekend uit een gepoolde 1,1179 over 33 speeldagen in VIER competities. GEEN "
                "ENKELE competitie is overgeslagen in de pool (`overgeslagen` is leeg), en dat is "
                "vandaag vanzelfsprekend: de vier zijn Serie A en de drie basisdivisies van de "
                "bekers (Premier League, Bundesliga, Eredivisie), en alle vier staan op 7 tot 10 "
                "speeldagen van een seizoen van 34 of 38 — dus ruim onder de helft van "
                "`SEASON_MATURE_SHARE`. Alle ZEVEN competitiebases lopen daarom de route "
                "`vorig+uplift`: Serie A, League One, League Cup/Premier League, DFB "
                "Pokal/Bundesliga, 2. Bundesliga, KNVB Beker/Eredivisie en Eerste Divisie. De "
                "niveaus per competitie staan in `niveau`, met de route en de reden erbij. LET OP "
                "DE FACTOR, want hij is hoger dan de 1,0606 van gisteren: de pool bestaat vandaag "
                "uit andere competities (de drie bekerbases in plaats van vijf Zuid-Europese "
                "competities), en §3 Stage 5 waarschuwt dat de pool competitie-overstijgend is en "
                "dus meebeweegt met wie erin zit. En de meting naast de markt (controleren, niet "
                "fitten — §2): de gemiddelde afstand van het eigen 1X2 tot het Pinnacle-oordeel "
                "is 3,95 pp over 3 duels, zonder systematische kant."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert "
                "de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van de zestien "
                "competities met een fotmob_id zijn het eens, inclusief de vijftien die vandaag "
                "GEEN WEDSTRIJD hebben: 3 duels bij Fotmob, 3 bij BetExplorer, nul afwijkingen en "
                "geen enkele bron die faalde (`ra_oct27_bevestiging.py`). EN DE DRIE BEKERS MET "
                "EEN RONDE ZIJN ÓÓK DOOR TWEE BRONNEN BEVESTIGD, wat deze run voor het eerst kan: "
                "BetExplorer geeft 2, 8 en 9 duels in het venster en de Fotmob-daglijst geeft "
                "dezelfde 2, 8 en 9 — zie "
                "DE_BEKERS_STAAN_WEL_IN_DE_DAGLIJST_EN_HET_GAT_ZAT_IN_DE_ADMINISTRATIE. De twee "
                "bekers zonder ronde (FA Cup, Coppa Italia) staan alleen op BetExplorer, met als "
                "eerstvolgende ronde 6 november en 1 december. LET OP DE TIJDZONE: BetExplorer "
                "labelt in UK-tijd, en dat is sinds de wintertijd GMT tegen CET in Nederland — "
                "nog steeds precies één uur verschil, dus het venster [27.10. 08:00 NL, 28.10. "
                "08:00 NL) is in UK-tijd [27.10. 07:00, 28.10. 07:00)."),
            "INZETVENSTER": (
                "`runwindow.matches_for_run` met het venster [27.10. 08:00 NL, 28.10. 08:00 NL), "
                "en voor de drie bekers dezelfde band met de hand in `ra_oct27_cupmatches.py`. "
                "Alle 22 duels stonden op de daglijst van 27 oktober (`source_day` = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 22 zijn `playable`: de "
                "vroegste aftrap is 18:00 NL (vier DFB Pokal-duels) en de laatste 21:00 NL "
                "(Fleetwood - Arsenal en Koninklijke HFC - Go Ahead Eagles). Er is dus geen "
                "enkel duel dat al was afgetrapt voordat de gebruiker kon inzetten, en geen "
                "carry-over-band. `runwindow` rekent met `zoneinfo`, dus het venster is in échte "
                "NL-tijd gemeten: nu de wintertijd in is, komt een aftrap van 19:45 UTC op 20:45 "
                "NL uit (CET) en niet op 21:45 (CEST). Dat is de reparatie van 25 oktober; "
                "`ra_oct27_analyze.py` en dit bestand gebruiken allebei "
                "ZoneInfo('Europe/Amsterdam') en `odds_captured_at` staat op +01:00."),
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
        s3 = json.load(open("tmp-run/ra_oct27_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers zonder ronde vandaag; de drie MET een ronde staan al in s3["fixtures"]
        # omdat `ra_oct27_merge_cups.py` ze daar heeft neergezet (zie de kop).
        cups = json.load(open("tmp-run/ra_oct27_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct27_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct27_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct27_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

"""Run B 10 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct08_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. Negentien duels in het inzetvenster over acht van de zeventien competities, nul afgekapt
(cap 55), en vier gepubliceerde regels die alle vier op RANGORDE staan: geen enkele selectie
haalde vandaag haar eigen drempel. `mark_completed` gebeurt pas na het runrapport en de push
(Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-11"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-11T05:20:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")


def state_uit(res, run):
    st = {"date": DAG, "run": run, "competitions": {}}
    for m in res["matches"]:
        st["competitions"].setdefault(m["competition"],
                                      {"status": "GEANALYSEERD", "matches": []})["matches"].append(m)
    return st


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
        bronnen = m.get("prob_sources") or cand.get("prob_sources") or []
        if not bronnen:
            lam = (m.get("lambdas") or {}).get("xg") or []
            bronnen = [
                f"Fotmob team-xG {m['competition']} — gewogen over vorig en lopend seizoen "
                f"(§4 blend_seasons); doelverwachting {lam[0]:.3f} thuis / {lam[1]:.3f} uit"
                if len(lam) == 2 else f"Fotmob team-xG {m['competition']}",
                f"Fotmob thuis/uit-splits {m['competition']} (tweede methode, §1d)",
                "Fotmob wedstrijdcontext: opstelling, uitvallers met marktwaarde, vorm en rustdagen",
            ]
        picks.append({
            "id": f"{DAG}-{slug(m['competition'])}-{slug(home)}-{slug(away)}-{slug(r['market'])}-{slug(r['selection'])}",
            "run": run, "run_date": DAG, "kickoff": m["kickoff_utc"],
            "competition": m["competition"], "home": home, "away": away,
            "market": r["market"], "selection": r["selection"], "odds": r["odds"],
            "odds_source": r["odds_source"], "odds_captured_at": CAPTURED,
            "implied_prob": round(1 / r["odds"], 4), "my_prob": r["prob"],
            "edge_pp": r["edge_pp"], "data_tier": r["tier"],
            "confidence": "Medium" if r["tier"] == "FULL" else "Low",
            "prob_sources": bronnen, "shortlisted": True, "result": "pending",
            "notes": (f"Gepubliceerd op rangorde (§5b): plek {top['herijkt'].index(r)+1} van "
                      f"{len(top['herijkt'])} over {len(res['matches'])} doorgerekende wedstrijden. "
                      f"{r['status']}. selection_score {r['score']}. "
                      f"Ruwe kans {cand.get('my_raw')}, ruwe edge {cand.get('edge_raw')} pp; "
                      f"xG-methode {cand.get('edge_xg')} pp, splitsmethode {cand.get('edge_split')} pp, "
                      f"zwakste stand van het (shrink, rho)-grid {cand.get('edge_robust_min')} pp. "
                      f"shrink staat sinds 19 sep op 1.00 (§6e)."
                      + (" poort8_zou_hebben_geblokkeerd: JA — deze selectie staat op de "
                         "underdog-kant onder UNDERDOG_FLOOR (0.35). Let op: de poort BINDT "
                         "sinds 1 okt 2026 weer (§1e), dus zo'n selectie kan geen gepubliceerde "
                         "bet meer zijn; staat deze regel er toch, dan is er iets mis met de "
                         "poortvolgorde en hoort dat uitgezocht."
                         if cand.get("poort8_vervallen") else "")),
        })
    return st, top, picks, res


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("B", "tmp-run/rb_oct11_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.008482, "
                "b=0.005494 op 4119 afgerekende gevallen, fitted_through 2026-10-10. Die datum "
                "is de vorige rundag, dus calibration.py settle is niet blijven liggen (de "
                "controle die §6b-5c sinds 30 sep eist); deze run wikkelde er zelf 9 af. De "
                "correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,333% en "
                "het gebeurde 33,333% — maar ze wijst vandaag de ANDERE kant op dan in de "
                "voorbeelden van §5a: deze fit VERHOOGT een kans boven ongeveer 40%, met +0,1 "
                "tot +0,3 pp. Op de vijf gepubliceerde regels telde ze er dus edge BIJ in plaats "
                "van af: 11,13 -> 11,37 (Altach), 10,98 -> 11,23 (St. Gallen), 17,39 -> 17,66 "
                "(Lillestrøm), 8,91 -> 9,12 (LASK) en 7,71 -> 7,94 (Palmeiras). Dat is precies "
                "het geval waarvoor §5a de `bet_beide`-vlag heeft gebouwd, en hij bindt vandaag "
                "ook echt: bij Palmeiras – Corinthians staat bet_beide op False omdat die regel "
                "op geen van beide schalen de lat van 8,0 haalt (7,94 herijkt, 7,71 ruw). Hij is "
                "daarom gepubliceerd op RANGORDE met dat label erbij en niet als 'gevonden "
                "voordeel' (§5b). Lees de identiteit zoals §1e punt 3 van 30 sep voorschrijft: "
                "de reeks is de ONGESELECTEERDE ijksteekproef en breder dan de staart waarop "
                "deze routine speelt, dus 'de fit is de identiteit' betekent niet dat het model "
                "recht staat op die staart — §6e meet daar nog +1,83 pp te veel kans op "
                "longshots en -3,58 pp te weinig op favorieten over 4473 uitkomsten."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "VEERTIEN van de zeventien competities speelden, met 42 duels in het "
                "inzetvenster. DRIE hadden GEEN WEDSTRIJD: Keuken Kampioen Divisie, English "
                "League One en English League Two — alle drie Engelse/Nederlandse "
                "zaterdagcompetities die op zondag stilliggen, dus geen storing en geen "
                "dekkingsgat. scripts/idcheck.py gaf voor alle 33 fotmob_id's uit "
                "coverage.json een bruikbare stand (afsluitcode 0), dus geen enkele competitie "
                "is stil uit de lijst verdwenen — ook niet de vier die vandaag geen xG hebben. "
                "VIER competities draaien per prompts/run-b.md op doelpunten als sterktemaat en "
                "komen dus op LIGHT met een lat van 16,0 pp uit: Czech First League, Croatian "
                "HNL, Hungarian NB I en Romanian SuperLiga. De vijfde van dat rijtje (Keuken "
                "Kampioen Divisie) speelde niet. Tiers over de 42 duels: 22 FULL, 17 LIGHT, "
                "3 NONE."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 11 okt, 08:00 NL 12 okt). ALLE 42 duels stonden op de "
                "daglijst van 2026-10-11 zelf; geen enkel duel kwam van de daglijst van "
                "2026-10-12 (source_day = DAY + 1). Dat is anders dan gisteren, toen er zes van "
                "de daglijst van morgen kwamen, en de reden is de klok: de MLS-wedstrijd van "
                "vandaag trapt om 23:00 UTC af, en dat is 01:00 NL op 12 oktober — nog steeds "
                "binnen hetzelfde inzetvenster, maar wél op de UTC-daglijst van vandaag. Vijf "
                "Braziliaanse duels zitten in dezelfde band (21:00 tot 00:30 NL). Alle 42 duels "
                "hebben RunMatch.playable = True; de vroegste aftrap is 13:00 NL (Slovan Liberec "
                "– Slovácko) en de run begon om 05:05 NL, ruim zeven uur daarvoor. "
                "ONDER DE OUDE UTC-DAGREGEL zou het MLS-duel (St. Louis City – LA Galaxy) aan "
                "de run van vandaag zijn toegewezen en dus goed zijn gegaan; het is dus geen dag "
                "waarop runwindow.py een duel heeft gered, maar wel een dag waarop het "
                "zichtbaar maakt dat 'vandaag' en 'de UTC-dag' niet hetzelfde zijn."),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                "today=2026-10-11 aangeroepen zoals §1e eist, zodat het vervallen venster van 25 "
                "t/m 30 september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet "
                "geraden. Hij hield 22 selecties tegen, verdeeld over 9 wedstrijden. "
                "EN VANDAAG KOST DAT VOOR HET EERST BIJ RUN B AANTOONBAAR DE KOP VAN DE LIJST. "
                "Twee van die 22 zouden op de herijkte schaal boven élke gepubliceerde regel "
                "zijn uitgekomen: Grasshopper – Young Boys, Asian Handicap Grasshopper +1.25 "
                "@1,89 (+13,84 pp, selection_score 9,238) en Padova – Carrarese, Double Chance "
                "'Carrarese of gelijk' @1,9702 (+11,87 pp, score 7,433). De hoogste "
                "gepubliceerde score is 7,340 (Altach), dus zonder deze poort was de "
                "dagranglijst aangevoerd door Grasshopper en had Padova plek 2 of 3 gehad. Dat "
                "staat ook zo in de RUWE lijst van §5a, waar die twee op 1 en 2 staan. "
                "WAT ER TEGENOVER STAAT, en daarom blijft de poort staan: de "
                "`underdog`-schaduwreeks is verder van teken gedraaid en staat nu op 84 "
                "kandidaten, 79 afgewikkeld, -8,7% rendement (45,6% trefkans). Op 5 oktober was "
                "dat nog +16,9% over 36, op 9 oktober +4,6% over 45 en op 10 oktober -2,5% over "
                "50. De uitweg van 25 september — 'positieve ROI over >= 30 afgewikkelde "
                "kandidaten' — is daarmee niet langer waar, dus er is GEEN grond om de poort te "
                "verruimen, en §1e verbiedt de vraag dagelijks opnieuw te stellen. De gemeten "
                "kalibratiefout die de rem verantwoordt staat er nog: +1,83 pp te veel kans op "
                "longshots en -3,58 pp te weinig op favorieten over 4473 uitkomsten. "
                "`underdog_ruw` staat onveranderd op 17 gevallen met -8,8%; poort8_ruw is leeg "
                "omdat alle 22 al op de herijkte schaal sneuvelden en §1e verbiedt dezelfde "
                "selectie twee keer te boeken, en poort8_vervallen is leeg omdat het venster van "
                "zes dagen voorbij is. Die twee reeksen blijven twee populaties en worden nooit "
                "opgeteld."),
            "BEVINDING_1_DRIE_HOOGSTE_DIVISIES_ZONDER_DIVISIEPAAR": (
                "DRIE van de 42 duels komen op data_tier = NONE uit, en alle drie om dezelfde "
                "reden: Iraklis – Levadiakos (Greek Super League), Kispest Honvéd – Újpest "
                "(Hungarian NB I) en Hartberg – Austria Lustenau (Austrian Bundesliga). In alle "
                "drie staat één ploeg niet in de stand van vorig seizoen (Iraklis, Kispest "
                "Honvéd, Austria Lustenau) en luidt de melding 'geen divisie boven of onder "
                "[competitie] bekend'. "
                "DIT IS GEEN BRONPROBLEEM MAAR EEN LACUNE IN promotion.TIER2, en anders dan de "
                "acht gevallen van gisteren is de MELDING hier wél juist. Gisteren meldde de "
                "keten acht promovendi als 'degradant die niet in de divisie boven staat'; hier "
                "zegt ze gewoon dat de competitie zelf in geen van beide kaarten voorkomt, en "
                "dat is waar: TIER2 heeft twintig paren en Griekenland, Hongarije en Oostenrijk "
                "zitten er niet bij. De uitkomst NONE is daarmee correct — §4 verbiedt een "
                "gepoolde of verzonnen factor — maar het is 'nog niet gemeten' en niet 'niet te "
                "meten'. "
                "WAT HET KOST, EN HET IS TERUGKEREND. Drie duels vandaag, en het raakt juist de "
                "promovendi van drie competities die elk jaar twee tot vier ploegen wisselen. "
                "Het is dezelfde categorie als Roemenië vóór 9 oktober, de Spaanse derde divisie "
                "vóór 5 oktober en de acht duels van gisteren: een meetbaar gat dat een run "
                "iedere keer opnieuw als NONE afschrijft. "
                "NIET VANDAAG GEMETEN EN NIET MET TERUGWERKENDE KRACHT TOEGEPAST: §4 zegt sinds "
                "9 oktober uitdrukkelijk een nieuwe factor liever VÓÓR de analyse van de dag te "
                "meten dan erna, omdat een al gepubliceerde run aanvullen een herberekening een "
                "andere uitkomst zou geven dan de run zelf gaf. Het staat als besluit bij de "
                "gebruiker, en het is dezelfde vraag die gisteren voor Serie C, 3. Liga en de "
                "National League is neergelegd — nu met drie landen erbij. Wie het gaat meten "
                "moet eerst in api/data/allLeagues nakijken óf Fotmob de tweede divisie van die "
                "drie landen heeft; is dat niet zo, dan is het Kroatië en niet Roemenië, en dan "
                "is NONE het definitieve antwoord in plaats van een openstaande meting."),
            "BEVINDING_2_POORT_5_VANGT_VOOR_DE_ZESDE_DAG_OP_RIJ_DRIEKWART_WEG": (
                "447 selecties over zes markten, en de tweede methode is voor de ZESDE DAG OP "
                "RIJ de poort die vrijwel alles wegvangt: 341 van de 447 (76,3%) sneuvelden op "
                "'tweede_methode' — de twee methodes verslaan de markt niet dezelfde kant op. "
                "Daarna 51 op de edge, 22 op de underdog-poort, 14 op de koersband, 5 op context "
                "en 4 op robuustheid; 10 selecties over 5 wedstrijden haalden alle poorten. De "
                "reeks: 40 van 60 (7 okt), 29 van 37 (8 okt), 84 van 110 (9 okt), 553 van 754 "
                "(Run A 10 okt), 538 van 703 (Run B 10 okt) en nu 341 van 447. Dat is zes dagen "
                "rond driekwart, over ruim 2100 selecties, en §5 ('Net niet') zegt dat zoiets "
                "dagen achtereen een BEVINDING is over de splitsmethode en geen ruis. §6e wijst "
                "die methode al sinds 22 augustus aan als de scheefste van de twee, en "
                "calibration.py stats van vandaag bevestigt dat opnieuw: de xG-methode wijkt op "
                "longshots +2,23 pp af en de splitsmethode +1,42 pp, maar op favorieten -4,28 "
                "tegen -2,85 pp — twee schatters die op dezelfde grootheid structureel "
                "verschillend scheef staan, en dat is precies wat poort 5 als 'tegenstrijdig' "
                "ziet. "
                "WAT HET SCHADUWLOGBOEK ERVAN ZEGT: 'tweede_methode' staat op 129 kandidaten, "
                "119 afgewikkeld, -5,2% rendement. DAT IS EEN OMSLAG TEN OPZICHTE VAN GISTEREN "
                "(+2,1% over 103) en het wijst nu de andere kant op: de poort bespaart geld in "
                "plaats van dat hij het kost. Lees dat met §6d-terughoudendheid — 16 extra "
                "afgewikkelde gevallen draaien hier een teken om, en dat is zelf het bewijs dat "
                "deze reeks nog te klein is om een drempel op te verzetten. NIET VANDAAG EEN "
                "DREMPEL VERZETTEN (§6d: niet op één dag, en zeker niet op zes)."),
            "BEVINDING_3_DE_HELE_LIJST_IS_EEN_DOELPUNTENMARKT_EN_WIJST_EEN_KANT_OP": (
                "ALLE VIJF de gepubliceerde regels zijn een doelpuntenmarkt, en alle vijf wijzen "
                "DEZELFDE kant op: vier keer Under (Under 3 bij Altach, Under 3.5 bij St. "
                "Gallen, Lillestrøm en LASK) en één keer 'beide ploegen scoren — nee' bij "
                "Palmeiras. Er staat geen enkele uitkomstmarkt in de lijst, terwijl 1X2, Asian "
                "Handicap, Draw No Bet en Double Chance samen 273 van de 447 doorgerekende "
                "selecties leveren. "
                "DIT IS GEEN INKOOPARTEFACT, en dat is precies waarom het opgeschreven hoort te "
                "worden. §1a eist die controle op de inkoop en vandaag slaagt ze ruim: tien van "
                "de veertien spelende competities kregen de volledige bulk met h2h, spreads én "
                "totals, dus vijf van de zes markten op de beste prijs. De eenzijdigheid komt "
                "dus uit de ANALYSE: het model verwacht vandaag systematisch minder doelpunten "
                "dan de markt, en het doet dat terwijl de vroeg-seizoenscorrectie het "
                "doelpuntenniveau juist OPTILT (factor 1,0563). §5b zegt hierover: blijft de "
                "lijst dagen achtereen uit één hoek komen, dan is dat een signaal over het model "
                "en niet over de selectieregel. Vandaag is het één dag — gisteren kwamen de vijf "
                "regels uit drie markten — dus dit is een reeks om te volgen en geen bevinding "
                "om op te handelen. "
                "EN HET MARGELOGBOEK ZEGT ER IETS OVER DAT DE ANDERE KANT OP WIJST: margins.py "
                "stats meet op 1076 wedstrijden dat het totaal aantal doelpunten juist te HOOG "
                "wordt voorspeld in de staart ('6 of meer' voorspeld 9,8% tegen werkelijk 7,3%, "
                "meer dan twee standaardfouten). Dat is geen bevestiging van vandaag — het is "
                "een andere grootheid — maar het betekent wel dat een Under-overwicht niet "
                "zonder meer als modelfout te lezen is."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug), en "
                "vandaag slaagt ze ruim. TIEN van de veertien spelende competities hebben een "
                "sportkey bij The Odds API en ALLE TIEN kregen de volledige bulk-aanroep met "
                "h2h, spreads en totals — dus vijf van de zes markten, op de beste prijs per "
                "aanbieder. split_budget(466, 10) gaf (10, 10), dus niemand viel buiten de bulk "
                "en de losse totals-stap was niet nodig. De VIER zonder sportkey (Czech First "
                "League, Croatian HNL, Hungarian NB I, Romanian SuperLiga) draaien op het "
                "gratis BetExplorer-marktgemiddelde; daar is 1X2 de enige markt en staan de "
                "andere vijf in markets_checked met de reden erbij. Dat is 10 van de 42 duels "
                "met één markt in plaats van zes, en bij die tien is de bookmaker niet "
                "herleidbaar (§1a). "
                "447 selecties doorgerekend: Over/Under 132, Asian Handicap 117, 1X2 114, BTTS "
                "42, Draw No Bet 30, Double Chance 12. Alle zes markten dingen dus werkelijk "
                "mee, en de controle SLAAGT met doelpuntenmarkten (OU 132, BTTS 42) én "
                "uitkomstmarkten (1X2 114, AH 117, DNB 30, DC 12). Double Chance en Draw No Bet "
                "blijven laag omdat de spreads-respons bij een deel van de duels geen +0,5- of "
                "0,0-lijn had — dat staat zo in markets_checked en is iets anders dan 'niet "
                "bekeken'. WAT ERUIT KOMT IS WEL EENZIJDIG: alle vijf de regels zijn een "
                "doelpuntenmarkt. Zie BEVINDING_3; dat is geen quotumovertreding (§1 verbiedt "
                "bets forceren om een verdeling te halen) maar het hoort genoemd."),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie staat op factor 1,0563, gepoold 1,0712 -> 1,0661 "
                "over 46 speeldagen en ZES competities. ACHT van de veertien spelende "
                "competities vallen uit de pool, en de reden is per competitie vastgelegd zoals "
                "Stage 5 eist (een stil weggelaten waarneming is hetzelfde probleem als een "
                "stille truncatie): VIER omdat er in geen van beide seizoenen xG is (Czech First "
                "League, Croatian HNL, Hungarian NB I, Romanian SuperLiga) en VIER omdat hun "
                "seizoen over de helft is, waardoor league_level route 'lopend' kiest — "
                "Eliteserien (22 van 30 speeldagen), Allsvenskan (23 van 30), MLS (29 van 34) en "
                "Série A BRA (30 van 38). Dat is exact de constructie van 24 september: die vier "
                "kalenderjaarcompetities zouden de gepoolde factor van de andere optillen en ze "
                "halen hun niveau nu rechtstreeks uit het lopende seizoen (Eliteserien thuis "
                "1,836 / uit 1,316; Allsvenskan 1,622 / 1,333; MLS 1,840 / 1,401; Série A 1,529 "
                "/ 1,134). TWEE VAN DE VIJF GEPUBLICEERDE REGELS STAAN IN DIE VIER COMPETITIES "
                "(Lillestrøm in de Eliteserien, Palmeiras in de Série A), dus de route 'lopend' "
                "is ook vandaag geen voetnoot. De zes competities die wél in de pool zitten "
                "draaien op route 'vorig+uplift'."),
            "CONTEXT_EN_VERPLAATSING": (
                "context.check_venue zet relocated bij GEEN ENKEL duel — nul van de 42. Dat is "
                "het vermelden waard omdat de controle gisteren drie meldingen gaf waarvan twee "
                "een eigenschap van de bron bleken (een transliteratieverschil en een foutieve "
                "stamkaart) en niet van de wedstrijd. Vandaag is er niets te melden en dat is "
                "dus ook geen bevinding. "
                "POORT 7 hield 5 selecties tegen, verdeeld over TWEE wedstrijden, beide op de "
                "blessurekant: Cádiz – Sporting Gijón (Sporting Gijón mist 38% van de "
                "selectiewaarde tegen 26% bij Cádiz — Juan Otero, Nacho Martín en Konrad de la "
                "Fuente, alle drie terug eind oktober) en Atlético-MG – Santos (Atlético-MG mist "
                "47% tegen 35% — Tomás Pérez en Tomás Cuello geschorst, Fred geblesseerd). Die "
                "twee duels verliezen daarmee hun enige kandidaat. De rustkant van de poort bond "
                "nergens, en dat is te begrijpen: het interlandvenster is net voorbij, dus "
                "vrijwel elke ploeg komt met twintig dagen rust de wedstrijd in. "
                "EEN AANTEKENING OVER DE OPSTELLINGEN, want die bepaalt hoeveel poort 7 vandaag "
                "kón doen: van de 42 duels had er geen enkele een bevestigde opstelling om 05:10 "
                "NL. Vier stonden op 'predicted', negen op 'lastStarting11', twee op 'standard' "
                "en 22 op 'unavailable'; bij vijf was het veld leeg. Dat is dezelfde "
                "klokbevinding als gisteren en het is geen competitie-eigenschap: Run B draait "
                "zeven tot zestien uur voor de aftrap en de opstellingen komen een uur ervoor. "
                "Het contextlogboek staat nu op 998 afgewikkelde wedstrijden en meet nog steeds "
                "NIETS: de fout van het model tegen het beschikbaarheidsverschil staat op "
                "r = -0,026 en t = -0,77 (helling -7,5 pp per eenheid), de fout van de MARKT op "
                "r = -0,023 en t = -0,67 (-6,4 pp). Die twee hellingen liggen vrijwel op elkaar, "
                "en dat is zelf een waarneming: het model gaat met ontbrekende spelers niet "
                "aantoonbaar slechter om dan de bookmaker. Bij 998 wedstrijden is alleen een "
                "effect vanaf ~18 pp per eenheid aantoonbaar, dus de poort blijft een rem en "
                "wordt geen bijstelling (§1c)."),
            "BEURSKOERS": (
                "VIER van de vijf gepubliceerde regels staan op een BEURS — Matchbook — en §5 "
                "eist dan beide getallen, want de gebruiker ziet op de site de koers vóór "
                "commissie: St. Gallen – Lausanne Under 3.5 1,87 bruto / 1,8526 netto; "
                "Lillestrøm – Molde Under 3.5 1,93 / 1,9114; LASK – Rapid Wien Under 3.5 1,78 / "
                "1,7644; Palmeiras – Corinthians BTTS nee 1,82 / 1,8036. edge_pp en "
                "selection_score rekenen met de NETTO koers (oddsapi.net_price). Dat vier van de "
                "vijf bij één beurs staan is geen toeval maar wat §1a op 5 september al meet: in "
                "61% van de gevallen staat de beste prijs bij een beurs. "
                "De vijfde, Altach – Wolfsberger AC Under 3 @1,88, staat bij PINNACLE en is "
                "daarmee de regel die met de meeste argwaan gelezen hoort te worden: §5 (Stage "
                "5, stap 2) noemt Pinnacle het scherpste publieke expertoordeel dat er is, dus "
                "een edge tegen Pinnacle is een stevigere claim dan dezelfde edge tegen een "
                "ruimere aanbieder — niet een betere. Alle vijf de regels komen van The Odds API "
                "op de beste prijs per uitkomst; geen van de vijf leunt op het "
                "BetExplorer-marktgemiddelde."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("51 credits van een plafond van 466 (19.604 over bij api_check.py, 396 "
                       "verbruikt deze maand, 21 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: TIEN bulk-aanroepen à 3 credits (h2h + spreads + totals) voor "
                       "alle tien spelende competities MET sportkey, samen 30 credits; "
                       "split_budget(466, 10) -> (10, 10) dus niemand viel buiten de bulk en de "
                       "losse totals-stap was niet nodig. Stap 2: BTTS voor de 22 duels met een "
                       "kandidaat-edge — de vereniging van beide schalen zoals §1a sinds "
                       "13 september voorschrijft — waarvan 21 ook werkelijk gekocht à 1 credit, "
                       "samen 21 credits. Het 22e duel (Györi ETO – Puskás FC Academy) kon niet: "
                       "Hungarian NB I heeft geen sportkey, dus er is geen event-id om BTTS op "
                       "te vragen; dat staat zo in markets_checked. "
                       "EN DIE TWEEDE RONDE HEEFT DE LIJST VANDAAG WERKELIJK VERANDERD, wat op "
                       "de meeste dagen niet zo is. De vijfde gepubliceerde regel — Palmeiras – "
                       "Corinthians, 'beide ploegen scoren — nee' @1,8036 — bestaat alleen "
                       "doordat BTTS in ronde twee is gekocht; zonder die ronde was plek 5 naar "
                       "Catanzaro – Mantova gegaan (Asian Handicap -0.25, score 4,863). Bij "
                       "Altach – Wolfsberger AC leverde ronde twee een derde gekwalificeerde "
                       "selectie op (BTTS nee @2,4504, +9,83 pp) die het binnen de wedstrijd "
                       "verloor van Under 3. De 20 duels zonder kandidaat-edge staan in "
                       "markets_checked als 'niet opgevraagd — geen kandidaat-edge in dit duel', "
                       "niet als gat. Na deze run staat het maandverbruik op 447 van 20.000: het "
                       "budget is op geen enkele manier de beperkende factor, en de tijdsgrens "
                       "van §0 bond vandaag ook niet (42 duels op een cap van 55, nul "
                       "afgekapt)."),
            "p_xg_shrink08": "Vastgelegd per doorgerekende wedstrijd, zoals §6e sinds 19 sep eist.",
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping op LIJSTLENGTE — bindt vandaag niet (één regel op drie plekken), maar de
        # lus blijft staan: ze is de enige plek waar een gekwalificeerde selectie die niet in de
        # lijst past wordt vastgelegd (`failed_gate = "lijstlengte"`, bewust dezelfde naam).
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
            # 7 okt 2026 — DIT IS GEEN LIJSTLENGTE als de wedstrijd zelf wél een regel kreeg.
            # Sinds §5b de edge-drempel uit de poorten heeft gehaald, kiest `toplist.build` de
            # sterkste selectie van een wedstrijd onder de ZEVEN overgebleven poorten, en dat kan
            # een andere zijn dan de selectie die óók de drempel haalde: vandaag staat bij
            # Internacional – Corinthians het 1X2 op +8,04 pp (score 4,127) en de Draw No Bet op
            # +6,64 pp (score 4,515), en `selection_score` geeft de voorkeur aan de hogere
            # trefkans (§1a). Die niet-gekozen selectie is dezelfde mening in een andere markt
            # (§1, 0-of-1-bet), geen gekwalificeerde selectie die door de LIJSTLENGTE afviel —
            # de lijst had vandaag drie plekken voor twee regels. Ze apart boeken zou de reeks
            # `lijstlengte` vervuilen met een vraag die ze niet beantwoordt (§5b, 26 sep 2026).
            if m["match"] in gepubliceerde_duels:
                m["binnen_wedstrijd_niet_gekozen"] = {
                    "selection": pick.get("selection"), "market": pick.get("market"),
                    "odds": pick.get("odds"), "edge_pp": pick.get("edge_pp"),
                    "score": pick.get("score"),
                    "reden": ("alle acht poorten open en boven de drempel, maar een andere "
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
                "reden": (f"alle acht poorten open en {pick.get('edge_pp'):+.2f} pp boven de "
                          f"drempel, maar rang {rang} bij MAX_SHORTLIST = "
                          f"{len(top['herijkt'])}; laagste gepubliceerde selection_score "
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
                # dezelfde wedstrijd dezelfde mening en geen afgewezen kandidaat — die hoort
                # niet in het schaduwlogboek (regel van 2 okt 2026, `rb_oct04_publiceer.py`).
                # De regel wordt hernoemd in plaats van weggegooid, zodat hij in
                # `data/run-state/` na te lezen blijft; hij verdwijnt daarmee uit de "Net
                # niet"-tabel en wordt in het runrapport onder de bet zelf genoemd.
                nm = m.get("near_miss")
                if nm and any(mm == m["match"] for mm, _, _ in gespeeld):
                    e["near_miss_gepubliceerd"] = e.pop("near_miss")
                e["bet"] = sleutel_bet
                entry["matches"].append(e)
            mark(state, comp, entry)

        # Dekkingstabel: óók de zestien competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/rb_oct11_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
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
        for run, pad in (("B", "tmp-run/rb_oct11_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct11_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct11_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

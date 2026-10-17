"""Run B 16 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct17_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. Tien van de zeventien competities speelden, met vijftien duels in
het inzetvenster en nul afgekapt (cap 55 op vrijdag). VIER gepubliceerde regels, waarvan ÉÉN zijn
eigen lat haalt.

Drie dingen die vandaag in de parameters horen:

* **Eén regel haalt de drempel, drie staan er op rangorde.** Rapid Wien - Hartberg Under 3,5 @1,90
  haalt +16,12 pp én de verzwaarde lat van poort 9 (10,0 pp). De andere drie staan onder hun lat en
  zijn er per §5b als rangorde en niet als vondst.
* **De BetExplorer-slug van Série A (BRA) is verhuisd**, en dat is dezelfde stille faalstand als
  het Serie B-id: HTTP 200 met nul rijen. Gerepareerd in `rb_oct17_bxfix.py`, zonder credits.
* **De stadioncontrole gaf één echt alarm en één vals**, en het valse is in `scripts/context.py`
  gerepareerd (`_norm_ground` liet "Stadium" tegen "Stadion" staan).

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-17"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-17T05:05:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct17_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.025, b=0.016 op 4671 "
                "afgerekende gevallen, fitted_through 2026-10-16. Die datum is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist). De "
                "correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,3% en het gebeurde "
                "33,3% — en ze VERHOOGT een kans over vrijwel de hele speelbare band: +0,1 pp op 40%, +0,4 pp "
                "op 50%, +0,6 pp op 60%, +0,8 pp op 70%, en ze verlaagt alleen onder ongeveer 35%. OP ALLE "
                "VIJF DE GEPUBLICEERDE REGELS TELDE ZE DUS EDGE BIJ IN PLAATS VAN AF (Bradford +14,32 ruw -> "
                "+15,12 herijkt; Levadiakos +17,33 -> +17,98). DAT BINDT VANDAAG NIET: bet_beide staat op "
                "True bij de twee regels die hun lat halen, dus die halen hem op de ruwe én de herijkte "
                "kans. Lees de identiteit zoals §1e punt 3 voorschrijft: de reeks is de ONGESELECTEERDE "
                "ijksteekproef en breder dan de staart waarop deze routine speelt, dus 'de fit is de "
                "identiteit' betekent niet dat het model recht staat op die staart — §6e meet daar nog "
                "+1,76 pp te veel kans op longshots en -3,48 pp te weinig op favorieten over 5037 uitkomsten."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ZESTIEN van de zeventien competities speelden, met 74 duels in het inzetvenster — de "
                "drukste Run B-dag van deze maand. MLS (14), English League Two (12), English League One "
                "(11), Serie B (6), Czech First League (4), Segunda División (4), 2. Bundesliga (4), Série A "
                "BRA (4), Eliteserien (3), Hungarian NB I (3), Croatian HNL (2), Romanian SuperLiga (2), "
                "Austrian Bundesliga (2) en Greek Super League, Allsvenskan en Keuken Kampioen Divisie elk 1. "
                "ÉÉN had GEEN WEDSTRIJD: Swiss Super League (speelt zondag). scripts/idcheck.py gaf voor alle "
                "33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode 0), dus geen enkele "
                "competitie is stil uit de lijst verdwenen — ook niet de Zwitserse die vandaag niet speelt, "
                "en dat is precies waarom die controle bestaat (prompts/run-b.md: een fout id geeft geen "
                "foutmelding maar nul wedstrijden, en nul wedstrijden leest als GEEN WEDSTRIJD). VIJF van de "
                "spelende competities draaien per prompts/run-b.md op doelpunten als sterktemaat en komen dus "
                "op LIGHT met een lat van 16,0 pp uit: Czech First League, Croatian HNL, Hungarian NB I, "
                "Romanian SuperLiga en Keuken Kampioen Divisie — Fotmob geeft daar geen xG, niet in 2025/2026 "
                "en niet in 2026/2027, per competitie nagetrokken en niet van de buurlanden overgenomen. "
                "Tiers over de 74 duels: 39 FULL, 22 LIGHT, 13 NONE. ZESENTWINTIG DUELS HEBBEN EEN PLOEG "
                "ZONDER STAND IN HET VORIGE SEIZOEN en gingen langs de omrekening van §4; DERTIEN lukten "
                "(alle dertien LIGHT, nooit FULL) en DERTIEN niet. De dertien die niet lukten vallen in drie "
                "soorten, alle drie met NONE als eerlijke uitkomst: VIJF buiten het gemeten bereik van de "
                "omrekenfactor (conversion_in_range: Austria Lustenau, Barnsley – Cambridge United, Leicester "
                "City – Doncaster Rovers, Colchester – Exeter City, Port Vale – Chesterfield), VIER met een "
                "degradant die ook in de divisie BOVEN hem niet in de stand staat (Ascoli, Benevento, "
                "Rochdale, York City — die komen van nóg een niveau lager) en VIER waar het divisiepaar zelf "
                "niet gemeten is: Hungarian NB I (§4, 'voor Hongarije is er geen factor') en de drie "
                "Braziliaanse duels (Série B ligt onder Série A maar staat niet in promotion.TIER2, en §4 "
                "verbiedt een factor te verzinnen)."
            ),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 17 okt, 08:00 NL 18 okt) en runwindow.py levert 74 duels, alle 74 "
                "met RunMatch.playable = True. ZESENZESTIG stonden op de daglijst van 2026-10-17 en ACHT op "
                "die van 2026-10-18 — de nachtband waar prompts/run-b.md over gaat: vier MLS-duels om 02:30 "
                "NL (Austin FC, Houston Dynamo, Sporting Kansas City) en 04:30 NL (LA Galaxy, Portland "
                "Timbers, San Jose Earthquakes, Seattle Sounders) plus São Paulo – Vasco da Gama om 02:00 NL. "
                "DIE ACHT ZIJN PRECIES DE GROEP DIE DE OUDE UTC-DAGREGEL AAN DE VERKEERDE RUN GAF, en één "
                "ervan levert vandaag een gepubliceerde regel op (Sporting Kansas City – Real Salt Lake, "
                "02:30 NL). Omgekeerd kwam er geen enkel duel uit de band [00:00, 08:00) NL van vandaag zelf "
                "— dat venster is door de run van gisteren bediend. De run begon om 05:04 NL, ruim tien uur "
                "voor de vroegste aftrap (13:00 NL, Eliteserien)."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "ALLE ZEVENTIEN COMPETITIES ZIJN DOOR EEN TWEEDE, ONAFHANKELIJKE BRON BEVESTIGD, en de twee "
                "bronnen zijn het over de hele runlijst exact eens: Fotmob 74 duels in het venster, "
                "BetExplorer 74, en per competitie gelijk (MLS 14-14, League Two 12-12, League One 11-11, "
                "Serie B 6-6, en zo verder). Dat geldt óók voor de Swiss Super League, die vandaag GEEN "
                "WEDSTRIJD heeft — juist daar moet de tweede bron kijken, want 'nul wedstrijden' is de "
                "uitkomst die een kapot id en een lege speeldag niet van elkaar onderscheidt. Dit is de poort "
                "uit §1 die de scheduler expliciet noemt, en ze staat vandaag op 17 van 17. BetExplorer "
                "labelt in UK-tijd (NL −1 uur), dus het venster is daar [17.10. 07:00, 18.10. 07:00); dat is "
                "omgerekend en de omrekening staat in rb_oct17_bevestiging.py."
            ),
            "STILLE_FAALSTAND_VAN_VANDAAG_LA_GALAXY": (
                "DE DUURSTE BEVINDING VAN DEZE RUN IS EEN NAAMKOPPELING, EN ZE HAD EEN BET LATEN DOORGAAN DIE "
                "POORT 8 HOORT TEGEN TE HOUDEN. Fotmob schrijft 'LA Galaxy', BetExplorer 'Los Angeles "
                "Galaxy'; na _DROP blijft {la, galaxy} tegen {los, angeles, galaxy} over en dat is in geen van "
                "beide richtingen een deelverzameling, dus `resolve` koppelde niet. De SOEPELE terugval kon "
                "het duel niet eens zien, want die zocht alleen in de dagpool van BetExplorer — en MLS had 2 "
                "van de 16 rijen met een vandaag-label, precies de scheefstand waarvoor de `is_today`-filter "
                "op 7 oktober uit de exacte lus is gehaald. Resultaat: LA Galaxy – San Diego FC was het enige "
                "van de 74 doorgerekende duels zonder marktgemiddelde, dus ZONDER kalibratieblok (§6e) en met "
                "POORT 8 OP 'geen 1X2-prijzen, geen marktoordeel over wie de mindere is' — de poort stond open "
                "zonder te zijn getoetst. EN DAT WAS NIET ONSCHULDIG: in de eerste doorrekening stond 1X2 San "
                "Diego FC @3,25 (+10,11 pp) als GEPUBLICEERDE REGEL op plek 5 van de dagranglijst. Met de "
                "prijzen erbij is de de-vigde marktkans van San Diego 0,322 — onder sides.UNDERDOG_FLOOR "
                "(0,35) — dus poort 8 hoort dicht en de regel hoort er niet te staan. TWEE REPARATIES, beide "
                "blijvend: (1) scripts/teamnames.py krijgt het alias 'la galaxy' <-> 'los angeles galaxy', "
                "zodat ook scripts/settling.py en het kalibratielogboek het duel koppelen; (2) de soepele "
                "terugval in find_1x2 zoekt vanaf nu in ALLE rijen van de competitie in plaats van in de "
                "dagpool — `best_pair` eist 0,62 gelijkenis over beide kanten én 0,05 afstand tot de tweede "
                "kandidaat, dus de val waar de oude beperking voor was bedoeld (een retourwedstrijd uit de "
                "seizoenslijst) wordt daar afgevangen en niet door de poolkeuze. NA DE REPARATIE is de hele "
                "analyse opnieuw gedraaid: LA Galaxy valt uit de lijst en Las Palmas – Castellón schuift op "
                "naar plek 5. Dezelfde stille faalvorm als het Serie B-id, de verhuisde BetExplorer-slug van "
                "Série A en calibration.py settle: geen foutmelding, alleen een leeg veld."
            ),
            "POORT7": (
                "BINDT EN HOUDT DERTIEN SELECTIES TEGEN, verdeeld over DRIE wedstrijden die daarmee hun hele "
                "kant kwijt zijn: San Jose Earthquakes – Nashville SC (San Jose mist 43% van de "
                "selectiewaarde tegen 2% bij Nashville — Niko Tsakiris, Jack Skahan, Jonathan González), "
                "Seattle Sounders FC – CF Montréal (Montréal 30% tegen 19%) en FC Emmen – Almere City FC "
                "(Almere 10% tegen 0% — Mees Hoedemakers). DAT IS DE DUURSTE POORT VAN VANDAAG IN "
                "RANGORDETERMEN: San Jose – Nashville staat op plek 3 van de RUWE lijst (Double Chance San "
                "Jose @1,93, +14,65 pp, selection_score 9,736) en komt er niet in. WAT ER WEL IS OPGEHAALD en "
                "wat §1c eist vast te leggen: de context van ÉLK van de 74 duels, ook de 13 op tier NONE en "
                "de 19 die de cap afkapte — dat is de steekproef van ctxlog.py, en die staat nu op 1145 "
                "afgewikkelde wedstrijden. DE STADIONCONTROLE GAF NUL ALARMEN: alle 74 duels spelen in het "
                "eigen stadion van de genoteerde thuisploeg, geen enkele relocated-vlag. GEEN ENKEL DUEL HAD "
                "OM 05:30 NL EEN BEVESTIGDE OPSTELLING (alle 74 op lineupType = lastStarting11). Dat is "
                "dezelfde klokbevinding als de afgelopen weken en geen competitie-eigenschap: Run B draait "
                "acht tot twintig uur voor de aftrap en de opstellingen komen een uur ervoor."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met today=2026-10-17 "
                "aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. Hij hield 30 selecties tegen "
                "en kost vandaag plek 4 én plek 5 van de RUWE lijst (Crawley Town +1.5 @1,8624, +12,67 pp; "
                "Carrarese +0.75 @1,85, +10,74 pp). EN HIJ IS DE REDEN DAT DE LIJST VAN VANDAAG ÉÉN REGEL "
                "ANDERS IS DAN IN DE EERSTE DOORREKENING — zie STILLE_FAALSTAND_VAN_VANDAAG_LA_GALAXY: "
                "zonder marktgemiddelde stond de poort open zonder te zijn getoetst en haalde San Diego FC "
                "de lijst. WAT ER TEGENOVER STAAT: de `underdog`-schaduwreeks staat nu op 138 kandidaten, 118 "
                "afgewikkeld, -6,4% rendement (46,6% trefkans) — negatief, dus de poort bespaart geld, en de "
                "uitweg van 25 september ('positieve ROI over >= 30 afgewikkelde kandidaten') is daarmee niet "
                "de ja die hij op 5 oktober was. §1e verbiedt de vraag dagelijks opnieuw te stellen en er is "
                "niets wezenlijk veranderd. De gemeten kalibratiefout die de rem verantwoordt staat er nog: "
                "+1,76 pp te veel kans op longshots en -3,48 pp te weinig op favorieten over 5037 uitkomsten. "
                "`underdog_ruw` staat onveranderd op 17 gevallen met -8,8%; die twee reeksen blijven twee "
                "populaties en worden nooit opgeteld. poort8_vervallen is leeg omdat het venster van zes "
                "dagen voorbij is."
            ),
            "POORT9_BINDT_VOOR_HET_EERST_OP_VIER_SELECTIES": (
                "POORT 9 (§1h, unders.BINDS_FROM = 2026-10-12) HOUDT VANDAAG VIER SELECTIES TEGEN — de "
                "ruimste oogst sinds hij bestaat. Alle vier zijn een Under op FULL-data in de band 8-10 pp, "
                "precies de band die §6g als de slechtste van de hele reeks meet (-47,7% over 15 gevallen): "
                "Viking – Fredrikstad Under 3,5 (+8,30 pp), Carrarese – Modena Under 2,5 (+9,12), Salford "
                "City – Crawley Town Under 3,25 (+9,47) en Under 3,5 (+8,38). DE NIET-MONOTONIE VAN 16 "
                "OKTOBER STAAT ER VANDAAG WEER, EN SCHERPER: drie van de vijf gepubliceerde regels zijn een "
                "FULL-Under ONDER de gewone drempel van 8,0 pp (+7,74, +7,07 en +6,93) en die laat "
                "unders.check met opzet vrij, terwijl een FULL-Under van +9,47 pp wordt geblokkeerd. De "
                "redenering achter die vrijstelling (elke Under onder 8,0 pp wordt toch door de edge-poort "
                "gestopt, dus de reeks `doelpunten_onder` moet niet vollopen met kandidaten die nooit een bet "
                "konden worden) berust erop dat `edge` een poort is, en sinds §5b (20 sep) is het een "
                "afkapping. DIT IS GEEN NIEUWE VRAAG EN WORDT NIET OPNIEUW VOORGELEGD: §1h en §6g verbieden "
                "een run deze poort op eigen initiatief te verzetten, en de vraag is op 14 oktober één keer "
                "aan de gebruiker voorgelegd en nog niet beantwoord. Hij staat hier als feit en in het "
                "dagrapport onder de regels zelf als voorbehoud. De reeks `doelpunten_onder` staat op 1 "
                "afgewikkeld geval (gewonnen, +65%); lees hem niet onder ~30 (§6d)."
            ),
            "VIER_VAN_DE_VIJF_REGELS_STAAN_OP_DE_GEMETEN_SCHEVE_KANT": (
                "VIER VAN DE VIJF GEPUBLICEERDE REGELS ZIJN EEN UNDER OP FULL-DATA, EN DAT IS EXACT DE "
                "MARKT-EN-KANT WAARVAN §6g OP UITKOMSTEN HEEFT GEMETEN DAT ZE SCHEEF STAAT. Dat hoort "
                "vooraan in het rapport en niet in een voetnoot. Twee metingen van vandaag, beide uit "
                "margins.py goalbias over 1249 doorgerekende duels: (1) de VORMFOUT — het gemiddelde aantal "
                "doelpunten klopt (voorspeld 3,047 / werkelijk 3,062, z = +0,29) maar de verdeling niet: "
                "-2,2 pp massa op 2 doelpunten en +2,3 pp op 4 doelpunten (boven twee standaardfouten), "
                "waardoor P(Under 2,5) 2,4 pp en P(Under 3,5) 2,2 pp te hoog staat bij ÉLK duel, vóór er iets "
                "gekozen is; en (2) het SELECTIE-EFFECT — in de 68 duels waarin de routine werkelijk een "
                "Under speelde vielen er +0,550 doelpunt per duel méér dan haar eigen lambda zei (z = +2,74), "
                "terwijl de Over-kant op z = -0,61 staat over 43 duels. WAT DAT VAN DE EDGES AFHAALT: "
                "Bradford +15,12 -> ongeveer +12,7 pp, Sporting Kansas City +7,74 -> +5,5, Las Palmas +7,07 "
                "-> +4,7 en Minnesota +6,93 -> +4,7. Alleen Bradford blijft dan boven de verzwaarde lat. "
                "EN DE ONAFHANKELIJKE CONTROLE WIJST DEZELFDE KANT OP: tegen Pinnacle — volgens §5 (Stage 5, "
                "stap 2) het scherpste publieke expertoordeel dat er is, vandaag met een marge van 3,2 tot "
                "4,5% — staat het model op de Under-kant +24,43 pp boven de markt bij Bradford (lijn 2,25: "
                "eigen 77,0% tegen Pinnacle 52,6%), +11,37 pp bij Minnesota (lijn 3,25) en +10,27 pp bij "
                "Sporting Kansas City (lijn 3,25). Las Palmas staat op -0,03 pp, dus op die ene regel zegt "
                "Pinnacle hetzelfde. Over alle 43 (duel, lijn)-paren is het gemiddelde verschil +0,86 pp met "
                "20 van 43 boven Pinnacle — de scheefstand is dus NIET dagbreed, en juist de drie "
                "gepubliceerde Unders zijn de uitschieters. DAT MAAKT HET GEVAL ERNSTIGER EN NIET MILDER. "
                "WAT HET NIET IS: geen reden om de rangorde te negeren of de lijst leeg te laten — §5b "
                "schrijft de rangorde voor en §1 verbiedt zowel bets forceren als bets achterhouden buiten "
                "de poorten om."
            ),
            "BEVINDING_POORT5_TWINTIGSTE_DAG": (
                "POORT 5 VANGT OPNIEUW RUIM DRIEKWART WEG: 549 van de 725 selecties (75,7%) sneuvelden op "
                "'tweede_methode' — de twee methodes verslaan de markt niet dezelfde kant op. Daarna 76 op de "
                "edge, 30 op de underdog-poort, 29 op de koersband, 13 op context, 13 op robuustheid en 4 op "
                "poort 9; ELF selecties haalden alle negen poorten, verdeeld over twee wedstrijden "
                "(Levadiakos – NFC Volos en Bradford City – Stevenage), en §1a koos daar de hoogste "
                "selection_score. De reeks staat nu bijna drie weken rond twee derde tot vier vijfde, en §5 "
                "('Net niet') zegt dat zoiets dagen achtereen een BEVINDING is over de splitsmethode en geen "
                "ruis. WAT HET SCHADUWLOGBOEK ERVAN ZEGT: 'tweede_methode' staat op 150 kandidaten, 137 "
                "afgewikkeld, -5,6% rendement (43,8% trefkans) — de poort bespaart dus geld, al is het bedrag "
                "klein. DE TWEE REGELS DIE HUN LAT HALEN LEUNEN OP TEGENGESTELDE ARMEN, en dat is het "
                "vermelden waard: Bradford City – Stevenage komt van de xG-arm (+16,67 pp) en de "
                "splitsmethode geeft daar maar +4,96 pp, terwijl Levadiakos – NFC Volos op xG +13,63 pp "
                "staat en op splits +32,13 pp. Beide halen de lat op de xG-arm alleen, dus geen van beide "
                "staat óp de zwakke arm — maar bij Levadiakos komt de sprong van 13,6 naar 18,0 pp er wel "
                "vandaan, en §1f heeft op 392 afgerekende gevallen gemeten dat de splitsmethode als kansbron "
                "vrijwel niets toevoegt. De zwakste stand van het (shrink, rho)-grid is 8,20 pp bij Bradford "
                "en 9,48 pp bij Levadiakos, dus poort 6 heeft bij beide ruimte. NIET VANDAAG EEN WEGING "
                "VERANDEREN (§6d, en §1f noemt de curve tussen 0,7 en 1,0 vlak)."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0625 (gepoold 1,0708 over 60 speeldagen, 7 "
                "competities), en NEGEN van de zestien spelende competities zijn uit de pool weggelaten — dat "
                "weglaten is zélf de meting (§3 Stage 5) en hoort daarom integraal in het rapport. VIER "
                "wegens een seizoen over de helft, waardoor league_level route 'lopend' kiest: Eliteserien "
                "(22 van 30 speeldagen), Allsvenskan (24 van 30), MLS (30 van 34) en Série A BRA (31 van 38). "
                "VIJF wegens het ontbreken van xG in beide seizoenen: Czech First League, Croatian HNL, "
                "Hungarian NB I, Romanian SuperLiga en Keuken Kampioen Divisie. WAT DE FACTOR VOOR DE "
                "OVERIGEN DOET: de twaalf competities op route 'vorig+uplift' krijgen het niveau van vorig "
                "seizoen × 1,0625; de vier op route 'lopend' rekenen rechtstreeks met het lopende seizoen, "
                "ongeschaald (MLS thuis 1,855 / uit 1,405 / basis 1,549 en Série A thuis 1,540 / uit 1,133 / "
                "basis 1,321). DE SEIZOENSNOTATIE VAN DIE VIER IS '2025'/'2026' EN NIET '2025/2026', zoals "
                "prompts/run-b.md eist — anders valt Fotmob stil terug op het lopende seizoen en rekent de "
                "run zijn prior op de stand van vandaag. DE COMPETITIES VAN DE GEPUBLICEERDE REGELS: English "
                "League One en Segunda División en Greek Super League op route 'vorig+uplift' (niveau thuis "
                "1,571 / 1,543 / 1,506), MLS op route 'lopend'."
            ),
            "BEURSKOERS": (
                "TWEE van de vijf gepubliceerde regels staan op een BEURS en §5 eist dan beide getallen, want "
                "de gebruiker ziet op de site de koers vóór commissie: Bradford City – Stevenage Under 2,5 "
                "@1,67 BRUTO / 1,6566 NETTO bij MATCHBOOK, en Levadiakos – NFC Volos 1X2 @2,26 BRUTO / "
                "2,2348 NETTO bij BETFAIR. edge_pp en selection_score rekenen met de NETTO koers "
                "(oddsapi.net_price). DE ANDERE DRIE STAAN NIET OP EEN BEURS: Sporting Kansas City – Real "
                "Salt Lake Under 3,5 @1,83 bij 1XBET, Minnesota United – St. Louis City Under 3,5 @1,78 bij "
                "1XBET en Las Palmas – Castellón Under 2,75 @2,05 bij PINNACLE. DIE LAATSTE VERDIENT EEN "
                "AANTEKENING VAN POSITIEF TEKEN: Pinnacle is volgens §5 (Stage 5, stap 2) het scherpste "
                "publieke expertoordeel dat er is, dus een edge tegen Pinnacle is een STERKERE claim dan "
                "dezelfde edge tegen een ruimere aanbieder — en inderdaad zegt Pinnacle op de Under-kant van "
                "dat duel vrijwel precies hetzelfde als het model (-0,03 pp verschil), wat betekent dat de "
                "+7,07 pp daar uit de LIJN komt (2,75 tegen Pinnacle's 2,75 op een andere prijs) en niet uit "
                "een meningsverschil. ELF van de zestien spelende competities hebben een sportkey; VIJF "
                "hebben er geen en draaien volledig op het gratis BetExplorer-marktgemiddelde als enige "
                "1X2-bron: Czech First League, Croatian HNL, Hungarian NB I, Romanian SuperLiga en Keuken "
                "Kampioen Divisie. Die vijf hebben dus ook geen handicap-, doelpunten- of BTTS-markt, en dat "
                "staat per duel met die reden in markets_checked. Eén duel kreeg helemaal geen prijzen "
                "(Petrolul Ploiești – Sepsi OSK) en staat daarmee als GEEN BET met die reden."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": (
                "74 CREDITS VAN EEN PLAFOND VAN 643 (19.311 over bij api_check.py, 689 verbruikt deze maand, "
                "15 dagen tot de maandwissel, 2 runs per dag). Stap 0: ELF bulk-aanroepen à 3 credits (h2h + "
                "spreads + totals = 33) voor de elf spelende competities MET sportkey — Greek Super League "
                "(11 events), Eliteserien (8), Allsvenskan (9), Segunda División (11), Serie B (10), 2. "
                "Bundesliga (9), Austrian Bundesliga (11), English League One (23), English League Two (24), "
                "MLS (16) en Série A BRA (19); split_budget(643, 11) -> (11, 11) dus niemand viel buiten de "
                "bulk en de losse totals-stap was niet nodig. Stap 2: BTTS voor 41 van de 42 duels met een "
                "kandidaat-edge (41 credits à 1). ÉÉN duel met een kandidaat-edge kreeg geen BTTS, met die "
                "reden in markets_checked: FC Emmen – Almere City FC speelt in de Keuken Kampioen Divisie en "
                "die heeft geen sportkey bij The Odds API. MARKTBALANS-CONTROLE: GEHAALD, EN RUIM — ELF van "
                "de elf inkoopbare competities kregen via de bulk álle zes de markten (1X2, AH, DNB, DC, OU, "
                "BTTS), dus er is geen enkele competitie met alléén een uitkomstmarkt of alléén een "
                "doelpuntenmarkt. §1a eist dat je meldt HOE RUIM die controle slaagt, en dat is hier elf op "
                "elf in plaats van de één-op-twaalf van 30 augustus. DAT MAAKT DE MARKTVERDELING VAN DE "
                "UITKOMST BETEKENISVOL: van de vijf gepubliceerde regels komen VIER uit de doelpuntenmarkt "
                "(Over/Under) en ÉÉN uit een uitkomstmarkt (1X2). Dat is geen inkoopartefact — alle zes "
                "markten dongen mee in elf van de zestien competities — maar de uitkomst van "
                "selection_score, en zie VIER_VAN_DE_VIJF_REGELS_STAAN_OP_DE_GEMETEN_SCHEVE_KANT voor waarom "
                "juist die kant vandaag een voorbehoud verdient."
            ),
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

        # Dekkingstabel: óók de vijftien competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/rb_oct17_stage3.json"))
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

    # IDEMPOTENT (16 okt 2026). Een correctie in de `parameters`-tekst is een reden om dit script
    # nog een keer te draaien, en dan mogen de picks niet dubbel in het logboek komen: `ledger.py`
    # telt per regel en een dubbele pick verschuift hit rate en ROI zonder dat iets klaagt.
    # Dezelfde stille faalstand als de rest van deze ochtend, dus hier een harde controle.
    bestaand = {json.loads(l)["id"] for l in open("data/picks.jsonl") if l.strip()}
    nieuw = [p for p in alle_picks if p["id"] not in bestaand]
    with open("data/picks.jsonl", "a") as f:
        for p in nieuw:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{len(nieuw)} picks toegevoegd aan data/picks.jsonl "
          f"({len(alle_picks) - len(nieuw)} stonden er al in en zijn overgeslagen)")


if __name__ == "__main__":
    if "--schrijf" in sys.argv:
        wegschrijven()
    else:
        for run, pad in (("B", "tmp-run/rb_oct17_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct17_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct17_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

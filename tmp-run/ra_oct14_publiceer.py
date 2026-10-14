"""Run A 14 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct13_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. Twee van de eenentwintig competities uit de runlijst speelden, met DERTIEN duels in het
inzetvenster: de Championship (vier) en de Champions League (negen). DRIE gepubliceerde regels
onder §5b, en vandaag halen er TWEE wél hun lat (beide een LIGHT-Under boven 16,0 pp) en ÉÉN niet.
De bindende grens is vandaag niet de lijstlengte maar MAX_LIGHT_IN_SHORTLIST = 2: zie
VIERDE_GEKWALIFICEERDE_SELECTIE_VALT_OP_DE_LIGHT_CAP.

Twee van de drie regels zijn opnieuw een Under, voor de tweede dag op rij, en beide op LIGHT waar
poort 9 per besluit van 12 oktober met opzet niet geldt — zie TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-14"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-14T04:40:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
                      + ("" if cand.get("bet_beide") else
                         " bet_beide = FALSE. §5a houdt die vlag bij voor het geval een selectie "
                         "de lat ALLEEN op de herijkte schaal haalt; lees hem samen met de twee "
                         "edges hierboven, want de vlag zelf zegt niet welk van de twee gevallen "
                         "het is. Staat de herijkte edge onder de lat, dan haalt deze selectie "
                         "haar lat op GEEN van beide schalen en staat ze er op rangorde (§5b) — "
                         "dat is dan geen grensgeval maar precies wat §5b beschrijft.")
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
    for run, pad in (("A", "tmp-run/ra_oct14_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.020685, "
                "b=0.013396 over 4455 afgerekende gevallen, fitted_through 2026-10-13, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle vóór "
                "de analyse gedraaid (45 waarnemingen afgewikkeld, 4662 van 4686 compleet, 24 "
                "nog open). De fit VERHOOGT een kans over vrijwel de hele speelbare band en "
                "verlaagt alleen onder ~35%; het ruwe model zei gemiddeld 33,333% en het "
                "gebeurde 33,333%. Bij alle drie de gepubliceerde regels staat de herijkte edge "
                "daardoor BOVEN de ruwe (+26,13 tegen +25,45 pp bij Bodø/Glimt – Borussia "
                "Dortmund, +17,61 tegen +16,95 bij Roma – Real Madrid, +6,97 tegen +6,34 bij "
                "Norwich City – Southampton). `bet_beide` staat bij de derde op FALSE, en dat is "
                "geen grensgeval: die regel haalt zijn lat van 8,0 pp op GEEN van beide schalen "
                "en staat er op rangorde (§5b). Bij de twee Unders staat hij op TRUE — ze halen "
                "de LIGHT-lat van 16,0 pp herijkt én ruw."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de eenentwintig competities uit de runlijst speelden, met DERTIEN "
                "duels samen in het inzetvenster: de CHAMPIONSHIP (ENG) met vier duels en de "
                "UEFA CHAMPIONS LEAGUE met negen. NEGENTIEN competities hadden GEEN WEDSTRIJD: "
                "elf competities (Premier League, Serie A, La Liga, Bundesliga, Ligue 1, "
                "Eredivisie, Primeira Liga, Belgian Pro League, Super Lig, Scottish "
                "Premiership, Danish Superliga, Ekstraklasa — allemaal met hun eerstvolgende "
                "ronde op 16 oktober of later), de twee andere Europese toernooien (UEL en UECL "
                "op 15 okt) en de vijf bekers. Een woensdag in een Europese speelweek is daarmee "
                "een smalle maar scherpe dag: weinig competities, en tweederde van de duels op "
                "het hoogste niveau dat er is. Dat is geen storing (§3 Stage 2). LET OP de "
                "Championship-lijst: vier duels, waarvan LINCOLN CITY – WEST HAM UNITED er een "
                "is met twee ploegen die beide niet in de Championship-stand van 2025/2026 "
                "staan — Lincoln City kwam uit League One en West Ham uit de Premier League. "
                "Dat duel gaat dus langs BEIDE richtingen van §4 tegelijk; zie "
                "TWEE_OMREKENINGEN_IN_EEN_WEDSTRIJD."),
            "DE_CAP_BINDT_NIET": (
                "Dertien duels op een woensdagcap van 40 (`ranking.max_deep_analyses`), dus er "
                "is NIETS afgekapt (afgekapt = 0) en de hele runlijst is doorgerekend. Stille "
                "truncatie is verboden (§3 Stage 4) en het omgekeerde hoort er net zo expliciet "
                "te staan. De datarijkdom liep van 5,0 (Portsmouth – Sheffield United, Queens "
                "Park Rangers – Derby County en Lincoln City – West Ham United) tot 7,67 "
                "(Shakhtar Donetsk – AEK Athens). Omdat niets afviel zijn "
                "`laagste_die_het_haalde` en `hoogste_die_afviel` leeg — er is geen grens om te "
                "noemen."),
            "NEGEN_KRUIS_GRENSDUELS": (
                "De negen Champions League-duels zijn allemaal kruis-grens en gaan langs "
                "`scripts/interleague.py` (§4, 'Kruis-grens'): beide ploegen worden met de op "
                "2111 Europese duels gemeten aanval- en verdedigingsfactor van hun eigen land "
                "naar de Europese referentieschaal omgerekend, waarna ze op dezelfde grootheid "
                "staan. ACHT komen op data_tier LIGHT uit (een omgerekende ploeg is nooit FULL, "
                "dus lat 16,0 pp) en ÉÉN op NONE: SLOVAN BRATISLAVA – VFB STUTTGART valt af op "
                "Slovan, want voor SVK bestaat er geen gemeten competitiefactor (minder dan 40 "
                "Europese duels in de meting). Dat is geen tekort in de analyse maar de module "
                "die weigert te raden — stil terugvallen op factor 1.0 is precies de fout die "
                "`interleague` wegneemt. Het duel staat met zijn volledige omrekennotitie in "
                "`kruis_grens` en als GEEN BET in het rapport. Anders dan op 13 oktober viel er "
                "vandaag géén duel af op `in_range` (de Coventry-val); de acht omgerekende "
                "duels liggen alle acht binnen het gemeten bereik."),
            "TWEE_OMREKENINGEN_IN_EEN_WEDSTRIJD": (
                "ÉÉN van de vier Championship-duels heeft een ploeg die niet in de stand van "
                "2025/2026 staat, en het zijn er meteen TWEE in hetzelfde duel: LINCOLN CITY – "
                "WEST HAM UNITED. Lincoln City gaat OMHOOG (TIER2, promovendus uit League One, "
                "`gap_for('E1','E2',up)`) en West Ham OMLAAG (TIER1, degradant uit de Premier "
                "League, `gap_for('E0','E1',down)`). Het duel komt daarmee op data_tier LIGHT "
                "uit — lat 16,0 pp — en haalt die niet: de sterkste selectie staat op +6,33 pp. "
                "LET OP de waarschuwing van §4 bij de richting OMLAAG: die valt hier op het "
                "gemeten paar ('E0','E1') bij football-data.co.uk terug en niet op POOLED_GAP, "
                "maar er bestaat nog geen aparte neerwaartse meting, dus lees West Ham met meer "
                "terughoudendheid dan Lincoln. §4 eist dat de stand per selectie uit "
                "GapResult.direction wordt gelezen in plaats van uit een samenvattende zin, en "
                "die teksten staan integraal in `promovendi` per wedstrijd. De andere drie "
                "Championship-duels staan met beide ploegen in de stand en zijn FULL."),
            "DRIE_REGELS_WAARVAN_TWEE_HUN_LAT_HALEN": (
                "Anders dan op 13 oktober halen er vandaag WÉL regels hun lat. De lijst van "
                "drie: (1) BODØ/GLIMT – BORUSSIA DORTMUND, Under 3.5 @2.00 (Pinnacle), LIGHT, "
                "+26,13 pp tegen een lat van 16,0 — de hoogste selection_score van de dag "
                "(9,946) en ruim boven zijn lat; (2) ROMA – REAL MADRID, Under 3.5 @1.8134 "
                "(Matchbook-beurskoers 1.83 bruto, 1.8134 na 2% commissie), LIGHT, +17,61 pp "
                "tegen 16,0 (score 6,407), óók boven zijn lat; (3) NORWICH CITY – SOUTHAMPTON, "
                "Double Chance — Southampton of gelijk @1.60 (GTbets), FULL, +6,97 pp tegen 8,0 "
                "(score 4,842) — die staat er OP RANGORDE en haalt zijn lat niet, op geen van "
                "beide schalen. MAX_LIGHT_IN_SHORTLIST = 2 is exact gehaald en niet "
                "overschreden, en hij is vandaag de BINDENDE grens; zie "
                "VIERDE_GEKWALIFICEERDE_SELECTIE_VALT_OP_DE_LIGHT_CAP. Dat twee van de drie hun "
                "lat halen is geen belofte: §1g heeft op 552 afgerekende gevallen gemeten dat er "
                "geen drempel op de herijkte edge bestaat die geld oplevert en dat het rendement "
                "het SLECHTST is bij de hoogste geclaimde edge. Een edge van +26 pp is dus geen "
                "sterker signaal dan een van +17 — lees de lijst als rangschikking van wat het "
                "model het sterkst vindt."),
            "VIERDE_GEKWALIFICEERDE_SELECTIE_VALT_OP_DE_LIGHT_CAP": (
                "MANCHESTER CITY – PARIS SAINT-GERMAIN, Asian Handicap Manchester City −0.25 "
                "@1.9506, LIGHT, +17,13 pp (score 5,857) haalde alle acht poorten ÉN zijn lat "
                "van 16,0 pp, en staat tóch niet in de lijst. De reden is niet de rangorde en "
                "niet de lijstlengte: op score is hij derde van vier, en er waren drie plekken. "
                "Het is MAX_LIGHT_IN_SHORTLIST = 2 (§0): de twee LIGHT-plekken waren door "
                "Bodø/Glimt (9,946) en Roma (6,407) bezet, dus de derde plek ging naar de "
                "hoogste FULL-regel — Norwich City – Southampton op 4,842, met een kleinere "
                "edge. Zo'n selectie is geen afgewezen kandidaat (geen poort hield hem tegen) en "
                "ook geen bet, dus ze is vastgelegd zoals §5b (26 sep 2026) eist: een "
                "`gekwalificeerd_niet_gepubliceerd`-blok op de wedstrijd in data/run-state/ MET "
                "de rang erin, en een near_miss met failed_gate = 'lijstlengte' zodat "
                "shadow.py collect hem afrekent. Die naam is met opzet niet nieuw — §5b zegt "
                "'gebruik precies die naam en verzin geen tweede', omdat twee namen één "
                "populatie in twee reeksen splitsen die nooit de ~30 afgewikkelde gevallen van "
                "§6d halen. Noteer wél in het rapport dat de bindende grens vandaag de "
                "LIGHT-cap was en niet de lengte; dat is een eigenschap van deze dag (drie van "
                "de vier gekwalificeerde selecties op LIGHT) en niet van de regel. En let op wat "
                "het kost: de weggelaten regel had +17,13 pp en de regel die zijn plek nam "
                "+6,97 pp — de cap ruilt hier een grotere geclaimde edge op zwakke data in voor "
                "een kleinere op sterke data, en dat is precies waarvoor hij bestaat."),
            "BINNEN_DE_WEDSTRIJD_NIET_GEKOZEN": (
                "Bij NORWICH CITY – SOUTHAMPTON stond óók het 1X2 op de uitzege (Southampton "
                "@2.80, LeoVegas) met alle poorten open en +9,90 pp — BOVEN de FULL-lat van "
                "8,0, waar de gepubliceerde Double Chance op +6,97 pp eronder blijft. Toch is "
                "de Double Chance gepubliceerd, en dat is `selection_score` die kiest (§1a): "
                "6,97 × 0,695 = 4,842 tegen 9,90 × 0,456 = 4,508, dus de hogere trefkans weegt "
                "zwaarder dan de grotere edge. Die niet-gekozen selectie is dezelfde mening in "
                "een andere markt (§1, 0-of-1-bet) en dus GEEN gekwalificeerde selectie die op "
                "de lijstlengte afviel; ze is vastgelegd als "
                "`binnen_wedstrijd_niet_gekozen` en gaat niet het schaduwlogboek in, want ze "
                "apart boeken zou de reeks `lijstlengte` vervuilen met een vraag die ze niet "
                "beantwoordt (regel van 7 okt 2026). Het is wel het vermelden waard dat de "
                "lijst hierdoor één regel bevat die zijn lat niet haalt terwijl er in diezelfde "
                "wedstrijd een selectie lag die dat wél deed."),
            "TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS": (
                "Voor de TWEEDE dag op rij zijn twee van de drie gepubliceerde regels een "
                "Under, en §6g meet de Under-kant over het hele logboek fors negatief tegen een "
                "positieve Over-kant. POORT 9 (§1h) heeft vandaag opnieuw NUL selecties "
                "tegengehouden, en opnieuw correct: beide Unders staan op LIGHT (Bodø/Glimt en "
                "Roma zijn kruis-grensduels en dus per definitie LIGHT), en per besluit van de "
                "gebruiker op 12 oktober geldt poort 9 uitsluitend op FULL "
                "(`unders.TIERS = ('FULL',)`). Dat is dus niet hetzelfde gat als gisteren: op "
                "13 oktober ging het om een FULL-Under ónder de 8,0 pp die buiten de "
                "bindingsband van de poort viel; vandaag gaat het om twee LIGHT-Unders die de "
                "poort per besluit niet raakt. Van de 58 doorgerekende Over/Under-selecties "
                "staat geen enkele FULL-Under in de band 8–10 pp waar de poort bindt, dus de "
                "reeks `doelpunten_onder` groeit vandaag niet. DIT IS GEEN REDEN OM DE POORT OP "
                "EIGEN INITIATIEF TE VERBREDEN (§1h punt 1, §1e: risicobereidheid hoort bij de "
                "gebruiker) en deze run heeft dat dus niet gedaan — de vraag is op 12 oktober "
                "gesteld en beantwoord met 'eerst kijken wat deze rem doet', en §1h schrijft "
                "voor hem niet opnieuw te stellen. Het staat als feitelijke meting in het "
                "runrapport en niet als wijziging. De vormfout in het scoregrid die hieronder "
                "ligt — keuze (a) van 11 oktober — staat nog open en blijft het echte werk; "
                "zolang die er is staat P(Under) bij élk duel 1,6 tot 2,4 pp te hoog, op élk "
                "datatier, en dat raakt deze twee regels rechtstreeks."),
            "POORT9": (
                "Derde bindende dag (`unders.BINDS_FROM` = 2026-10-12, §1h) en voor elke "
                "selectie aangeroepen met today=2026-10-14 zoals §1h eist. HIJ HEEFT NIETS "
                "TEGENGEHOUDEN: `poort9_geblokkeerd` is voor alle dertien duels leeg en de reeks "
                "`doelpunten_onder` in shadow.jsonl staat nog op nul rijen. Zie "
                "TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS voor waarom dat correct is en wat het niet "
                "betekent. §1h punt 2 rekent zelf op ongeveer één rij per paar dagen en noemt "
                "dit eerder een vraag voor december dan voor deze week."),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e, teruggezet per 1 okt 2026); "
                "sides.check() is met today=2026-10-14 aangeroepen zoals §1e eist. Vandaag houdt "
                "hij VIER selecties tegen over TWEE wedstrijden, en dat zijn precies de twee "
                "duels die daarna mét een Over/Under in de lijst zijn gekomen: BODØ/GLIMT – "
                "BORUSSIA DORTMUND en ROMA – REAL MADRID. De duurste van de vier is ROMA OF "
                "GELIJK (Double Chance, AH +0.5 @1.96 bruto / 1.9408 netto) op +20,21 pp ruw met "
                "selection_score 7,249 — op de ruwe schaal de tweede regel van de dag. De poort "
                "heeft daar dus geen wedstrijd maar een KANT tegengehouden, precies wat hij "
                "hoort te doen: Pinnacle geeft Roma 26,7% tegen 49,1% voor Real Madrid. Die "
                "rijen gaan als `underdog` het schaduwlogboek in — één rij per wedstrijd per "
                "categorie (§1e), dus twee rijen en niet vier. `poort8_ruw` is vandaag LEEG: "
                "beide kandidaten worden op de RUWE schaal al door een eerdere poort gestopt, "
                "dus de reeks `underdog_ruw` groeit vandaag niet. Die twee reeksen zijn en "
                "blijven twee populaties die volgens §1e NOOIT bij elkaar mogen worden "
                "opgeteld. De reeks blijft volgens §1e een reden om de vraag te stellen "
                "en geen automatisme om de poort te schrappen; de kalibratiefout die de rem "
                "afdekt is er nog (zie `calibration.py stats` in het runrapport), en §1e zegt "
                "uitdrukkelijk de vraag niet elke dag opnieuw te stellen."),
            "POORT7": (
                "Voor alle dertien duels gedraaid en in `context` vastgelegd, ook waar hij "
                "opengaat (§1c). Hij houdt TIEN selecties tegen en is bij DRIE duels de bindende "
                "poort, alle drie op blessures: QUEENS PARK RANGERS – DERBY COUNTY (Derby mist "
                "48% van de selectiewaarde tegen 16% bij QPR — Max Johnston, Eiran Cashin en "
                "Charlie Taylor), LASK – LIVERPOOL (Liverpool mist 42% tegen 26% bij LASK — "
                "Dominik Szoboszlai, Cody Gakpo en Alexander Isak, alle drie 'terug: a few "
                "days') en ASTON VILLA – FENERBAHÇE (Aston Villa mist 30% tegen 14% — George "
                "Hemmings, Matteo Ruggeri en Ian Maatsen). Bij de overige tien duels staat de "
                "poort aan beide kanten open. Bij `side = None` — Over/Under en BTTS — staat hij "
                "altijd open; dat is geen meting maar de regel van §1c, want er is geen kant om "
                "te benadelen. LET OP: twee van de drie gepubliceerde regels zijn Over/Under en "
                "dus `side = None`, dus daar heeft poort 7 niets kunnen zeggen. Alleen bij "
                "Norwich City – Southampton (Double Chance, side = away) is de poort werkelijk "
                "langs de bet gegaan en opengebleven. De drie tegengehouden duels zijn het "
                "scherpst bij LASK – Liverpool: een poort die 42% ontbrekende selectiewaarde bij "
                "de favoriet meet, houdt daar een bet op diezelfde favoriet tegen, en dat is "
                "exact waarvoor hij in augustus is gebouwd."),
            "POORT5_IS_OPNIEUW_DE_GROOTSTE_ZEEF": (
                "135 van de 200 doorgerekende selecties (67,5%) sneuvelen op poort 5 — de twee "
                "methodes verslaan de markt niet dezelfde kant op. Dat is de ACHTSTE dag op rij "
                "boven tweederde (Run A 13 okt: 160 van 229, 69,9%; 12 okt: 103 van 141, 73,0%; "
                "11 okt: 417 van 550, 75,8%) en het is daarmee geen dageffect meer. Zie de "
                "bevinding in het runrapport: het aandeel is zo stabiel dat het eerder iets over "
                "de twee schatters zegt dan over de wedstrijden van een dag. De overige poorten: "
                "edge 36, context 10, odds 5, underdog 4, robuustheid 0, en TIEN selecties met "
                "alle poorten open — anders dan op 13 oktober, toen dat er nul waren."),
            "VROEG_SEIZOENSCORRECTIE_SCHIET_VOOR_DE_VIERDE_DAG_DOOR": (
                "factor x1.0510 (gepoold 1.0849 over 12 speeldagen in de twee spelende "
                "competities; `uplift_observations` sloeg er NUL over — beide hebben xG in beide "
                "seizoenen en geen van beide is op of boven de helft van zijn speeldagen). De "
                "Championship staat op 10 van 46 speeldagen (22%) en neemt daarmee de route "
                "`vorig+uplift` van `league_level`. EN HIER ZIT IETS DAT HARDOP MOET: de negen "
                "Champions League-duels leveren wél een waarneming AAN de gepoolde factor (ze "
                "staan in `vroeg_seizoen.competities`), maar ze krijgen die correctie zelf NIET. "
                "Kruis-grensduels lopen langs `interleague.reference_league()` en niet langs "
                "`league_level`, dus hun niveau komt van de Europese referentieschaal en er is "
                "geen uplift op toegepast — `niveau` is voor de Champions League daarom leeg. "
                "Dat is geregeld gedrag van de kruis-grenstak (§4) en geen fout, maar het "
                "betekent dat de correctie vandaag feitelijk alleen de VIER Championship-duels "
                "raakt, terwijl de UCL meeweegt in het getal. Noteer dat als openstaand punt: "
                "een competitie die de factor mede bepaalt en er zelf niet door wordt geraakt, "
                "hoort de vraag op te roepen of ze in `uplift_observations` thuishoort. De "
                "controlemeting "
                "die §3 Stage 5 eist wijst opnieuw de verkeerde kant op, voor de VIERDE dag op "
                "rij: P(Over 2.5) tegen de de-vigde marktkans staat op +0,15 pp ZONDER de "
                "correctie en op +3,36 pp MET (gemiddelde absolute fout 3,78 → 4,88 pp) over de "
                "DRIE duels met een 2.5-lijn aan beide kanten — alle drie Championship-duels, "
                "want alleen die hebben een competitiestand en dus deze invoerweg. Run A mat op 13 okt −0,63 → "
                "+2,11, op 12 okt +3,83 → +8,02 en op 11 okt −2,06 → +3,03. Het patroon is dus "
                "consistent: zonder correctie zit het model er dichter op. LET OP WAT DIT NIET "
                "MAG WORDEN: dit is een vergelijking met de MARKT en dus een diagnose, nooit een "
                "knop om de correctie op af te regelen (§2, §6e). En let op de omvang voordat "
                "iemand hier iets op bouwt: n=3 vandaag, tegen n=5 gisteren. Het hoort als "
                "openstaand punt in het runrapport en niet als wijziging in deze run — vier "
                "dagen op rij dezelfde richting is wél de aanleiding om het op UITKOMSTEN te "
                "gaan meten in plaats van tegen de markt, en dat is waar het margelogboek (§6f) "
                "en het doelpuntenlogboek (§6g) voor zijn."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 14 okt, 08:00 NL 15 okt). Alle dertien duels komen van "
                "de daglijst van 2026-10-14 (source_day = DAY, geen enkele DAY+1) en alle "
                "dertien staan op RunMatch.playable = True: de vroegste aftrap is Feyenoord – "
                "Como en LASK – Liverpool om 18:45 NL. De nachtband waarvoor runwindow.py op "
                "24 september is gebouwd is vandaag leeg; deze runlijst heeft geen competitie in "
                "een Amerikaanse tijdzone. De aftraptijden zijn met twee bronnen bevestigd — "
                "Fotmob in UTC en BetExplorer in UK-tijd, dus NL −1 uur: 'Today 17:45' en "
                "'Today 20:00' bij de Champions League komen uit op 18:45 en 21:00 NL, precies "
                "wat Fotmob geeft."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1 eist bevestiging door een tweede methode, en dat geldt ook voor de vraag "
                "wélke wedstrijden er zijn. PER COMPETITIE EENS, niet alleen op het totaal: voor "
                "alle ZESTIEN competities met een BetExplorer-slug geeft de fixturepagina exact "
                "hetzelfde aantal duels in het venster als de Fotmob-daglijst (13 tegen 13), "
                "inclusief de nullen bij de veertien competities die vandaag niet spelen. Dat is "
                "vandaag niet vrijblijvend: de Championship-lijst bevat LINCOLN CITY – WEST HAM "
                "UNITED, een paar dat voor deze competitie ongebruikelijk is, en BetExplorer "
                "noteert datzelfde duel op de Championship-fixturepagina. Twee losse bronnen die "
                "hetzelfde zeggen is hier dus het antwoord op 'staat dit wel in de goede "
                "competitie'. De twee bulk-responsen van The Odds API dekken dezelfde twee "
                "spelende competities."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "Geen van de vijf bekers op de Run A-runlijst heeft een fotmob_id in "
                "coverage.json, dus runwindow.matches_for_run kan ze niet filteren en 'niet in "
                "de daglijst' is voor hen geen uitspraak — dat is het gat dat Run A op "
                "6 oktober trof. Alle vijf zijn daarom apart langs BetExplorer gegaan "
                "(tmp-run/ra_oct14_cups.py) en alle vijf hebben hun eerstvolgende ronde NA het "
                "inzetvenster: FA Cup 17 okt (32 teamparen, nog geen koersen), League Cup 27 okt "
                "(8 duels mét 24 koersen), KNVB Beker 27 okt (26 teamparen), DFB Pokal 27 okt "
                "(16 duels mét 48 koersen), Coppa Italia 1 dec (8 teamparen). Vijf keer GEEN "
                "WEDSTRIJD met een tweede bron eronder in plaats van met een stilte."),
            "BEIDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Geen enkel duel draait vandaag op het gratis BetExplorer-marktgemiddelde "
                "alleen: beide spelende competities hebben een sportkey bij The Odds API en "
                "kregen de bulk-aanroep (h2h + spreads + totals, 3 credits elk). Vijf van de zes "
                "markten liggen dus bij elk duel op de BESTE PRIJS, en die lag vandaag gemiddeld "
                "5,29% boven het marktgemiddelde van BetExplorer (3,11% tot 9,27% over de twaalf "
                "doorgerekende duels) — in edge is dat de orde van +1,5 pp per selectie, gratis "
                "(§1a). Elke koers is door oddsapi.net_price gehaald, dus beurzen staan er na 2% "
                "commissie in; bij de tweede gepubliceerde regel is dat zichtbaar (Matchbook "
                "1.83 bruto wordt 1.8134 netto). Creditverbruik deze run: 6 voor de twee "
                "bulk-aanroepen plus 12 voor twaalf keer BTTS = 18 van een plafond van 540, en "
                "19.469 van 20.000 over voor de rest van de maand."),
            "MARKTBALANS": (
                "De controle van §1a is een controle op de INKOOP en hij slaagt ruim: BEIDE "
                "spelende competities hebben zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een "
                "doelpuntenmarkt (Over/Under) — twee op twee. BTTS is er voor TWAALF van de "
                "dertien duels bij gekocht (§1a stap 2, op de vereniging van beide schalen van "
                "`kandidaat_edge`); het dertiende is Slovan Bratislava – VfB Stuttgart met "
                "tier = NONE, waar §6b-5b het doorrekenen van markten overslaat. De 200 "
                "doorgerekende selecties verdelen zich over Over/Under 58, Asian Handicap 57, "
                "1X2 36, BTTS 24, Draw No Bet 14 en Double Chance 11. DE DRIE GEPUBLICEERDE "
                "REGELS KOMEN UIT TWEE MARKTEN (twee Over/Under, één Double Chance), en dat is "
                "geen inkoopeffect — alle zes markten dongen bij elk duel mee. Het is "
                "`selection_score` die kiest. Dat is de uitkomst en geen quotumfout (§1a: bets "
                "forceren om een verdeling te halen is verboden), maar het is wel de reden dat "
                "TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS hierboven staat."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stap 2 van §3 Stage 5, in de enige vorm die bereikbaar is: de de-vigde 1X2 van "
                "PINNACLE apart gezet, LOS van de beste prijs waarop gespeeld wordt. Gevonden "
                "voor alle TWAALF duels met een eigen 1X2 (18 events in de responsen); het "
                "dertiende duel zonder Pinnacle-regel is precies het NONE-duel, dat geen eigen "
                "1X2 heeft. Gemiddelde Pinnacle-marge 3,76% — scherper dan de 6 tot 10% van de "
                "rest van de markt. Het eigen xG-1X2 staat gemiddeld 5,43 procentpunt van dat "
                "oordeel af. DRIE uitschieters, alle drie in de Champions League en alle drie "
                "dezelfde kant op — het model vindt de thuisploeg sterker dan Pinnacle: ROMA – "
                "REAL MADRID (+15,41 pp op de thuiszege; eigen model 42,1%, Pinnacle 26,7%), "
                "MANCHESTER CITY – PARIS SAINT-GERMAIN (+14,79 pp; 59,6% tegen 44,8%) en ASTON "
                "VILLA – FENERBAHÇE (+14,32 pp; 72,9% tegen 58,6%). Twee daarvan raken vandaag "
                "een regel: bij Roma is de gepubliceerde selectie een Under en niet de "
                "thuiszege, dus Pinnacle spreekt die bet niet tegen — maar het is wel een "
                "waarschuwing dat de doelverwachting bij dit duel scheef kan staan in dezelfde "
                "richting, en een te hoge thuisaanval verschuift een totaal naar Over en niet "
                "naar Under. Bij Manchester City is de selectie die op de LIGHT-cap afviel juist "
                "de kant die Pinnacle 15 procentpunt lager inschat. DIT GETAL ZIT NIET IN "
                "my_prob EN NIET IN prob_sources (§2, §4): het is andermans lezing en "
                "marktafgeleid, dus het hoort in de vergelijking en niet in de kansschatting."),
            "EEN_VERPLAATSTE_WEDSTRIJD": (
                "context.check_venue is voor alle dertien duels gedraaid en zet ÉÉN keer "
                "relocated: SHAKHTAR DONETSK – AEK ATHENS wordt niet in Donetsk gespeeld maar in "
                "het uitwijkstadion dat Fotmob noteert. §1c eist dat een verplaatsing wordt "
                "genoemd ook als de poort opengaat, en dat is hier het geval: de poort houdt "
                "niets tegen, maar thuisvoordeel is de aanname waar het model het zwaarst op "
                "leunt en dit duel speelt op neutraal terrein. Het duel levert geen gepubliceerde "
                "regel op (de sterkste selectie staat op +6,71 pp tegen een LIGHT-lat van 16,0), "
                "dus de verplaatsing raakt vandaag geen bet. De overige twaalf duels staan in het "
                "eigen stadion van de genoteerde thuisploeg. Let op wat deze controle niet "
                "vangt (§1c): dat een fixture van eigenaar is gewisseld is nieuws en geen data, "
                "en een geplande run heeft geen nieuwsbron."),
            "OPSTELLINGEN": (
                "Negen van de dertien duels hebben een VOORSPELDE opstelling en vier de laatste "
                "basiself; GEEN ENKEL duel mist het opstellingsblok. Poort 7 kon dus bij elk "
                "duel werkelijk werken in plaats van door te laten bij gebrek aan meting (§1c). "
                "De negen voorspelde zijn alle negen de Champions League-duels — dat is de "
                "gewone stand van zaken bij een aftrap zeven uur na de run."),
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
                          f"drempel, maar rang {rang} en niet in de lijst van "
                          f"{len(top['herijkt'])} regels; laagste gepubliceerde selection_score "
                          f"{drempel_score}. BINDENDE GRENS: "
                          + ("MAX_LIGHT_IN_SHORTLIST = 2 — deze selectie staat op LIGHT en de "
                             "twee LIGHT-plekken waren door hoger scorende regels bezet, "
                             "terwijl de derde plek naar de hoogste FULL-regel ging. Geboekt "
                             "onder failed_gate = 'lijstlengte' zoals §5b (26 sep 2026) eist: "
                             "'gebruik precies die naam en verzin geen tweede', want het is "
                             "dezelfde vraag (wat kost de lijstlengte ons) en twee namen "
                             "splitsen één populatie in twee reeksen die nooit de ~30 "
                             "afgewikkelde gevallen van §6d halen."
                             if pick.get("tier") != "FULL"
                             else f"MAX_SHORTLIST = {len(top['herijkt'])} op de rangorde"))}
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
        s3 = json.load(open("tmp-run/ra_oct14_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        # §5 eist een dekkingsregel voor ELKE competitie uit de runlijst; zonder deze lus telt de
        # tabel 16 van de 21 en leest een onvolledige dekking als een volledige. Hun status komt
        # uit de tweede bron (`ra_oct14_cups.json`), niet uit de stilte van de daglijst.
        cups = json.load(open("tmp-run/ra_oct14_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct14_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct14_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct14_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

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

DAG = "2026-10-10"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-10T05:12:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct10_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0.996150, "
                "b=-0.002498 op 3819 afgerekende gevallen, fitted_through 2026-10-09. Die datum "
                "is de vorige rundag, dus calibration.py settle is niet blijven liggen (de "
                "controle die §6b-5c sinds 30 sep eist). Deze run wikkelde er zelf 0 af en dat "
                "is de juiste uitkomst, niet een overgeslagen stap: alle 186 openstaande "
                "waarnemingen horen bij de wedstrijden van vandaag, die nog niet gespeeld zijn. "
                "De correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,333% "
                "en het gebeurde 33,333% — en haalde op de vijf gepubliceerde regels 0,10 tot "
                "0,13 pp van de edge af: 16,50 -> 16,38 (Toronto), 12,13 -> 12,03 (Sporting KC), "
                "9,41 -> 9,28 (AIK), 11,07 -> 10,97 (Magdeburg) en 10,70 -> 10,60 (Austria "
                "Wien). De herijkte en de ruwe dagranglijst zijn daardoor regel voor regel "
                "identiek, in dezelfde orde. Lees die identiteit zoals §1e punt 3 van 30 sep "
                "voorschrijft: de reeks is de ONGESELECTEERDE ijksteekproef en breder dan de "
                "selecties waarop gespeeld wordt, dus 'de fit is de identiteit' betekent niet "
                "dat het model recht staat op de staart die deze routine kiest."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ZESTIEN van de zeventien competities speelden, met 77 duels in het "
                "inzetvenster — met afstand de grootste Run B-dag tot nu toe (19 op 9 oktober, "
                "en dat was toen al de breedste). Alleen de Keuken Kampioen Divisie had GEEN "
                "WEDSTRIJD. De drie Engelse en Amerikaanse competities leveren samen 38 van de "
                "77 duels: English League One 12, English League Two 12 en MLS 14. "
                "scripts/idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare "
                "stand (afsluitcode 0), dus geen enkele competitie is stil uit de lijst "
                "verdwenen — ook niet de vijf die vandaag geen xG hebben. VIJF competities "
                "draaien per prompts/run-b.md op doelpunten als sterktemaat en komen dus op "
                "LIGHT met een lat van 16,0 pp uit: Czech First League, Croatian HNL, Hungarian "
                "NB I, Romanian SuperLiga en de Keuken Kampioen Divisie (die laatste speelde "
                "niet). Dat is geen storing en geen dekkingsgat."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 10 okt, 08:00 NL 11 okt). 71 van de 77 duels stonden "
                "op de daglijst van 2026-10-10 zelf; ZES stonden op de daglijst van 2026-10-11 "
                "(source_day = DAY + 1) en horen tóch bij deze run omdat ze in NL-tijd tussen "
                "02:30 en 04:30 in de nacht ná de rundag aftrappen: Austin FC – Nashville SC, "
                "Minnesota United – Houston Dynamo FC, Sporting Kansas City – Portland Timbers, "
                "Colorado Rapids – San Jose Earthquakes, Los Angeles FC – Vancouver Whitecaps "
                "(alle MLS) en São Paulo – Vitória (Série A BRA). DIT IS PRECIES HET GEVAL "
                "WAARVOOR runwindow.py OP 24 SEPTEMBER IS GEBOUWD, en vandaag is het geen "
                "theorie: één van die zes — Sporting Kansas City – Portland Timbers, aftrap "
                "02:30 NL — is een GEPUBLICEERDE BET geworden, de nummer 2 van de dagranglijst. "
                "Onder de oude UTC-dagregel was dat duel aan de run van morgen toegewezen en dan "
                "al gespeeld geweest voordat iemand het kon inzetten. Alle 77 duels hebben "
                "RunMatch.playable = True; de vroegste aftrap is 13:00 NL (Magdeburg – Hannover "
                "96) en de run begon om 05:06 NL, ruim acht uur daarvoor."),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                "today=2026-10-10 aangeroepen zoals §1e eist, zodat het vervallen venster van 25 "
                "t/m 30 september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet "
                "geraden. Hij hield vandaag 33 selecties tegen, verdeeld over 12 wedstrijden — "
                "het hoogste aantal van welke Run B tot nu toe. Geen van die 33 zou de lijst "
                "hebben aangevoerd: de hoogste geblokkeerde edge is +9,83 pp (Córdoba bij "
                "Eldense, 1X2) en die haalt zijn LIGHT-lat van 16,0 niet eens. De poort heeft "
                "vandaag dus geen bet gekost. poort8_ruw is leeg omdat alle 33 al op de herijkte "
                "schaal sneuvelden en §1e verbiedt dezelfde selectie twee keer te boeken; "
                "poort8_vervallen is leeg omdat het venster van zes dagen voorbij is. "
                "STAND VAN DE TWEE REEKSEN, EN DIE IS WEZENLIJK VERANDERD: `underdog` staat nu "
                "op 50 afgewikkelde gevallen met -2,5% rendement (48,0% trefkans), tegen +4,6% "
                "over 45 op 9 oktober en +16,9% over 36 op 5 oktober. DE REEKS IS VAN TEKEN "
                "GEDRAAID. Dat is één van de twee gebeurtenissen waarop §1e zegt de vraag "
                "opnieuw voor te leggen — maar ze draait de verkeerde kant op om er een vraag "
                "van te maken: de uitweg van 25 september was 'positieve ROI over >= 30 "
                "afgewikkelde kandidaten', en die is nu juist NIET meer waar. De poort houdt met "
                "andere woorden geen winnaars meer tegen, en er is dus geen grond om hem te "
                "verruimen. De gemeten kalibratiefout die de rem verantwoordt staat er nog: "
                "+1,89 pp te veel kans op longshots en -3,64 pp te weinig op favorieten over "
                "4212 uitkomsten. `underdog_ruw` staat onveranderd op 17 gevallen met -8,8%. "
                "Die twee blijven twee populaties en worden nooit opgeteld."),
            "BEVINDING_1_ACHT_DUELS_OP_NONE_DOOR_EEN_ONTBREKENDE_DERDE_DIVISIE": (
                "DE BELANGRIJKSTE BEVINDING VAN DEZE RUN, en ze bestaat uit twee delen: een "
                "echte lacune en een foutieve foutmelding die haar maskeert. "
                "WAT ER GEBEURT: ZESTIEN van de 77 duels komen op data_tier = NONE uit, en ACHT "
                "daarvan om dezelfde reden — een ploeg die dit seizoen in de tweede divisie "
                "speelt en vorig seizoen in de DERDE divisie, waarvoor promotion.TIER2 geen "
                "divisiepaar heeft. Het gaat om Benevento – Cesena, Südtirol – Ascoli, LR "
                "Vicenza – Pisa en Arezzo – Cremonese (alle vier Serie B, met Benevento, Ascoli, "
                "Vicenza en Arezzo uit de Serie C), Darmstadt – Energie Cottbus en VfL Osnabrück "
                "– Dynamo Dresden (2. Bundesliga, promovendi uit de 3. Liga) en Tranmere Rovers "
                "– Rochdale en York City – Northampton Town (English League Two, promovendi uit "
                "de National League). "
                "DE FOUTMELDING IS FOUT EN DAT IS HET DEEL DAT OPGESCHREVEN MOET WORDEN. Alle "
                "acht staan in data/run-state met de reden \"degradant: 'X' staat niet in de "
                "stand van [de divisie BOVEN deze competitie]\" — dus Benevento wordt gemeld als "
                "degradant die niet in de Serie A-stand staat, terwijl hij promovendus uit de "
                "Serie C is. De oorzaak zit in de keten van het analysescript: promotion.TIER2 "
                "heeft geen ingang voor 'Serie B (ITA)', '2. Bundesliga (GER)' of 'League Two "
                "(ENG)', dus de promovendi-tak wordt OVERGESLAGEN ZONDER EEN FOUT TE PLAATSEN, "
                "waarna alleen de degradanten-tak nog een melding achterlaat en die melding de "
                "hele uitkomst beschrijft. De uitkomst NONE is correct — §4 verbiedt een "
                "verzonnen of gepoolde factor — maar de reden wijst de verkeerde richting en de "
                "verkeerde divisie aan. Dat is dezelfde soort stille administratiefout als het "
                "Serie B-id (vier dagen op 56), settled_note op 27 september en de ontbrekende "
                "calibration.py settle van 18 t/m 29 september: niets klaagt, en een latere run "
                "die dit leest gaat op zoek naar een kapotte Serie A-stand die niet kapot is. "
                "EN DIT IS GEEN KROATIË. §4 legt voor Croatian HNL vast dat het gat NIET "
                "MEETBAAR is omdat Fotmob de Kroatische tweede divisie simpelweg niet heeft. "
                "Hier is dat anders en het is nagetrokken in api/data/allLeagues: Serie C (ITA) "
                "staat er met id 147, 3. Liga (GER) met id 208 en National League (ENG) met id "
                "117, en alle drie leveren een bruikbare stand van 2025/2026 met de acht ploegen "
                "van hierboven erin. Dit is dus 'nog niet gemeten', net als Roemenië vóór "
                "9 oktober en de Spaanse derde divisie vóór 5 oktober — niet 'niet te meten'. "
                "EEN WAARSCHUWING VOOR WIE HET GAAT METEN: 3. Liga en National League zijn één "
                "tabel (20 respectievelijk 24 ploegen, allebei zonder xG), maar SERIE C SPEELT "
                "IN DRIE PARALLELLE GROEPEN en fetch_league_stats(147) geeft er stil ÉÉN van "
                "terug — 20 ploegen, met LR Vicenza erin en Benevento, Ascoli en Arezzo erbuiten. "
                "Dat is exact de val die §4 op 5 oktober voor de Primera Federación beschrijft, "
                "en de machinerie ervoor bestaat al (promotion.lower_table + "
                "fotmob.fetch_league_stats(..., group=...) + measure_gap per groep). "
                "NIET VANDAAG GEMETEN EN NIET MET TERUGWERKENDE KRACHT TOEGEPAST: §4 zegt sinds "
                "9 oktober uitdrukkelijk een nieuwe factor liever VÓÓR de analyse van de dag te "
                "meten dan erna, omdat een al gepubliceerde run aanvullen een herberekening een "
                "andere uitkomst zou geven dan de run zelf gaf. Het staat als besluit bij de "
                "gebruiker. Wat het kost is wel te noemen: acht van de 77 duels vandaag, en het "
                "is een terugkerende post — Serie B heeft vier van zijn zes duels in deze "
                "categorie."),
            "BEVINDING_2_POORT_5_VANGT_VOOR_DE_VIJFDE_DAG_OP_RIJ_DRIEKWART_WEG": (
                "703 selecties over zes markten, en de tweede methode is voor de VIJFDE DAG OP "
                "RIJ de poort die vrijwel alles wegvangt: 538 van de 703 (76,5%) sneuvelden op "
                "'tweede_methode' — de twee methodes verslaan de markt niet dezelfde kant op. "
                "Daarna 55 op de edge, 33 op de underdog-poort, 32 op de koersband, 15 op "
                "context en 13 op robuustheid; 17 selecties haalden alle poorten. De reeks: "
                "40 van 60 (7 okt), 29 van 37 (8 okt), 84 van 110 (9 okt), 553 van 754 (Run A "
                "10 okt) en nu 538 van 703. Dat is vijf dagen rond driekwart, over inmiddels "
                "ruim 1600 selecties, en §5 ('Net niet') zegt dat zoiets dagen achtereen een "
                "BEVINDING is over de splitsmethode en geen ruis. §6e wijst die methode al sinds "
                "22 augustus aan als de scheefste van de twee. "
                "WAT HET SCHADUWLOGBOEK ERVAN ZEGT, en het is onveranderd ongunstig voor de "
                "poort: 'tweede_methode' staat op 116 kandidaten, 103 afgewikkeld, +2,1% "
                "rendement. Een poort die driekwart van het werk wegvangt en daarbij per saldo "
                "GELD KOST in plaats van bespaart, is geen filter maar een rem op de hele "
                "routine. Twee dingen die dat relativeren voordat iemand eraan sleutelt: +2,1% "
                "over 103 gevallen is binnen de ruis die §6d beschrijft, en de poort is er niet "
                "om geld te besparen maar om tegenstrijdige schatters tegen te houden (§1, "
                "herzien 11 aug). Maar het cijfer wijst nu voor de derde meting op rij dezelfde "
                "kant op en de aantallen groeien, dus dit is de reeks om te volgen. Vandaag is "
                "de oorzaak op de gepubliceerde regels zelf te zien: bij Magdeburg – Hannover 96 "
                "geeft de xG-methode 1,470 / 1,841 en de splitsmethode 1,089 / 2,613 — dezelfde "
                "richting maar een factor twee verschil in het doelsaldo, en bij de duels die "
                "sneuvelden draait dat verschil net over de nul. NIET VANDAAG EEN DREMPEL "
                "VERZETTEN (§6d: niet op één dag, en zeker niet op vijf)."),
            "WAAROM_VIJF_REGELS_EN_VOOR_HET_EERST_ALLEMAAL_BOVEN_DE_LAT": (
                "VIJF regels op vijf plekken (zaterdag, MAX_SHORTLIST = 5) en ALLE VIJF HALEN "
                "HUN EIGEN DREMPEL — dat is voor Run B de eerste keer. Op 9 oktober stonden alle "
                "vier de regels op RANGORDE en haalde geen enkele selectie haar lat; vandaag "
                "staat er bij elke regel 'BET — en haalt ook de lat van 8,0 pp'. Alle vijf zijn "
                "FULL, dus MAX_LIGHT_IN_SHORTLIST (2) bond niet en kon niet binden. "
                "EN DAAROM BINDT DE LIJSTLENGTE VOOR HET EERST SINDS 26 SEPTEMBER. Er waren "
                "ACHT selecties die alle acht de poorten haalden én boven hun drempel stonden, "
                "en er passen vijf regels in de lijst. §5b stap 5 zegt dan dat de drempel de "
                "grens is en niet de rangorde — maar de lijst blijft vijf lang, dus DRIE "
                "gekwalificeerde selecties vallen af op niets anders dan de lengte van de lijst: "
                "Rosenborg – Sandefjord Under 3.5 @1,85 (+8,42 pp, score 5,261, rang 6), "
                "Wycombe Wanderers – Luton Town BTTS nee @3,107 (+11,89 pp, score 5,242, rang 7) "
                "en Bradford City – Leyton Orient BTTS nee @1,9996 (+8,29 pp, score 4,834, rang "
                "8). Die drie zijn GEEN afgewezen kandidaten — er is geen poort die ze "
                "tegenhield — en ze gaan daarom als gekwalificeerd_niet_gepubliceerd in "
                "data/run-state en als near_miss met failed_gate = 'lijstlengte' het "
                "schaduwlogboek in, precies zoals §5b dat op 26 september heeft vastgelegd. "
                "Let op de rangorde-anomalie die dit blootlegt en die geen fout is: Wycombe "
                "heeft met +11,89 pp een HOGERE edge dan drie van de vijf gepubliceerde regels, "
                "en valt er toch buiten. Dat komt doordat selection_score edge x kans weegt "
                "(§1a) en de kans op die BTTS-nee maar 0,43 is tegen 0,61 tot 0,75 bij de vijf "
                "die het haalden — de weegregel geeft met opzet de voorkeur aan een hogere "
                "trefkans boven een paar procentpunt extra edge. De reeks 'lijstlengte' stond op "
                "5 gevallen (5 afgewikkeld, +14,9%) en groeit vandaag naar 8. Lees hem niet: §6d "
                "eist ~30 gevallen, en §5b verbiedt uitdrukkelijk 'lijstlengte' bij 'edge' op te "
                "tellen — het zijn twee populaties."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug), en "
                "vandaag slaagt ze met de ruimste marge van elke Run B tot nu toe. TWAALF van de "
                "zestien spelende competities hebben een sportkey bij The Odds API en ALLE TWAALF "
                "kregen de volledige bulk-aanroep met h2h, spreads en totals — dus vijf van de "
                "zes markten, op de beste prijs per aanbieder. split_budget(448, 12) gaf (12, "
                "12), dus niemand viel buiten de bulk en er was geen rotatie nodig. De VIER "
                "zonder sportkey (Czech First League, Croatian HNL, Hungarian NB I, Romanian "
                "SuperLiga) draaien op het gratis BetExplorer-marktgemiddelde; daar is 1X2 de "
                "enige markt en staan de andere vijf in markets_checked met de reden erbij. Dat "
                "is elf van de 77 duels met één markt in plaats van zes. "
                "703 selecties doorgerekend: Over/Under 220, Asian Handicap 199, 1X2 143, BTTS "
                "66, Draw No Bet 52, Double Chance 23. Alle zes markten dingen dus werkelijk "
                "mee, en de controle SLAAGT ruim: doelpuntenmarkten (OU 220, BTTS 66) én "
                "uitkomstmarkten (1X2 143, AH 199, DNB 52, DC 23). Double Chance en Draw No Bet "
                "blijven laag omdat de spreads-respons bij 25 respectievelijk 22 duels geen "
                "+0,5- of 0,0-lijn had — dat staat zo in markets_checked en is iets anders dan "
                "'niet bekeken'. DE VIJF GEPUBLICEERDE REGELS KOMEN UIT DRIE MARKTEN: drie "
                "Over/Under, één Draw No Bet, één Asian Handicap. Vier van de vijf zijn dus "
                "push-beschermd of een doelpuntenmarkt en maar één is een kant-op-de-uitkomst; "
                "dat is geen quotum en ook niet nagestreefd (§1 verbiedt bets forceren om een "
                "verdeling te halen), maar het past wel bij wat §1a over selection_score zegt — "
                "de weegregel kiest de minst aan gelijkspel blootgestelde uitdrukking van "
                "dezelfde mening."),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie staat op factor 1,0629, gepoold 1,0712 over 60 "
                "speeldagen en ACHT competities. ACHT van de zestien spelende competities vallen "
                "uit de pool, en de reden is per competitie vastgelegd zoals Stage 5 eist (een "
                "stil weggelaten waarneming is hetzelfde probleem als een stille truncatie): "
                "VIER omdat er in geen van beide seizoenen xG is (Czech First League, Croatian "
                "HNL, Hungarian NB I, Romanian SuperLiga) en VIER omdat hun seizoen over de "
                "helft is, waardoor league_level route 'lopend' kiest — Eliteserien (22 van 30 "
                "speeldagen), Allsvenskan (23 van 30), MLS (28 van 34) en Série A BRA (29 van "
                "38). Dat is exact de constructie van 24 september: die vier "
                "kalenderjaarcompetities zouden de gepoolde factor van de andere optillen en ze "
                "halen hun niveau nu rechtstreeks uit het lopende seizoen (Eliteserien thuis "
                "1,834 / uit 1,320; Allsvenskan 1,616 / 1,311; MLS 1,835 / 1,390; Série A 1,533 "
                "/ 1,138). DRIE VAN DE VIJF GEPUBLICEERDE REGELS STAAN IN DIE VIER COMPETITIES "
                "(AIK, Toronto FC, Sporting Kansas City), dus de route 'lopend' is vandaag geen "
                "voetnoot maar de invoer onder de halve lijst. De acht competities die wél in de "
                "pool zitten draaien op route 'vorig+uplift'."),
            "CONTEXT_EN_VERPLAATSING": (
                "context.check_venue zet relocated = True bij DRIE duels, en §1c eist dat een "
                "verplaatsing wordt genoemd ook als de poort opengaat. Geen van de drie heeft "
                "een bet opgeleverd (twee staan op NONE, één is afgekapt), maar lees ze goed "
                "want ze zijn niet hetzelfde: "
                "(1) Vasas Budapest – Kisvárda, gemeld als 'gespeeld in Stadion Illovsky Rudolf, "
                "niet in Illovszky Rudolf Stadion'. DIT IS GEEN VERPLAATSING MAAR EEN "
                "SPELLINGSVERSCHIL — het is hetzelfde stadion, in twee transliteraties van "
                "dezelfde Hongaarse naam. De controle vergelijkt stadionnamen als tekst en kan "
                "dat niet zien. Dat is een valse positieve van de controle zelf en hoort hier "
                "als zodanig te staan, niet als bevinding over de wedstrijd. "
                "(2) LR Vicenza – Pisa, gemeld als 'gespeeld in Stadio Romeo Menti, Vicenza, "
                "niet in Stadio Rino Mercante'. Hier ligt de fout bij de stamkaart van de "
                "bron: het Stadio Romeo Menti ís het stadion van Vicenza; Fotmob noteert als "
                "eigen stadion het Stadio Rino Mercante, dat in Bassano del Grappa staat. Ook "
                "geen verplaatsing. "
                "(3) Paksi SE – MTK Budapest, gemeld als 'gespeeld in Fehervari uti Stadion, "
                "niet in Paksi FC Stadion'. Dit is de enige van de drie die eruitziet als een "
                "echte verplaatsing: Paks speelt dan niet in Paks maar in Boedapest. De poort "
                "staat open (het duel is hoe dan ook afgekapt) en zonder nieuwsbron is niet vast "
                "te stellen waarom. "
                "WAT HIERUIT VOLGT: twee van de drie meldingen zijn eigenschappen van de bron en "
                "niet van de wedstrijd, en dat is dezelfde soort valse positieve als de vier "
                "Nederlandse beloftenploegen op 9 oktober. De controle MELDT met opzet alleen en "
                "houdt niets tegen (§1c), dus het kost niets — maar wie hier ooit een poort van "
                "maakt, moet eerst de namen normaliseren. "
                "POORT 7 hield vandaag 15 selecties tegen, verdeeld over zes wedstrijden, "
                "allemaal op de blessurekant: de duidelijkste is Colorado Rapids – San Jose "
                "Earthquakes, waar San Jose 18% van zijn selectiewaarde mist tegen 6% bij "
                "Colorado (Reid Roberts geschorst, Darius Johnson en Nonso Adimabua geblesseerd) "
                "— dat duel verliest daarmee zijn enige kandidaat. De rustkant van de poort bond "
                "nergens. Het contextlogboek staat nu op 943 afgewikkelde wedstrijden en meet "
                "nog steeds NIETS: de fout van het model tegen het beschikbaarheidsverschil "
                "staat op r = -0,039 en t = -1,12 (helling -11,2 pp per eenheid), de fout van de "
                "MARKT op r = -0,037 en t = -1,07 (-10,5 pp). Die twee hellingen liggen nu "
                "vrijwel op elkaar, en dat is zelf een waarneming: het model gaat met "
                "ontbrekende spelers niet aantoonbaar slechter om dan de bookmaker. Bij 943 "
                "wedstrijden is alleen een effect vanaf ~19 pp per eenheid aantoonbaar, dus de "
                "poort blijft een rem en wordt geen bijstelling (§1c)."),
            "BEURSKOERS": (
                "TWEE van de vijf gepubliceerde regels staan op een beurs en §5 eist dan beide "
                "getallen. Regel 2, Sporting Kansas City – Portland Timbers Under 3.5 bij "
                "MATCHBOOK: 2,02 bruto en 1,9996 na 2% commissie, en edge_pp en selection_score "
                "rekenen met die 1,9996 (oddsapi.net_price). Regel 4, Magdeburg – Hannover 96 "
                "Draw No Bet op Hannover bij MATCHBOOK: 1,98 bruto en 1,9604 netto. De andere "
                "drie zijn gewone bookmakers zonder commissie: Toronto FC – CF Montréal Under "
                "3.5 bij 1XBET @1,71, AIK – Brommapojkarna Under 3.5 bij TIPICO @1,55 en Austria "
                "Wien – Sturm Graz handicap Sturm Graz -0.25 bij PINNACLE @1,98. Die laatste is "
                "het vermelden waard omdat Pinnacle volgens §5 (Stage 5, stap 2) de scherpste "
                "bookmaker van de markt is: een edge tegen Pinnacle is een stevigere claim dan "
                "dezelfde edge tegen een ruimere aanbieder, en hoort met meer argwaan gelezen te "
                "worden, niet met meer vertrouwen. Alle vijf de regels komen van The Odds API op "
                "de beste prijs per uitkomst; geen van de vijf leunt op het "
                "BetExplorer-marktgemiddelde, dus er is vandaag geen regel waarbij de bookmaker "
                "niet herleidbaar is."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("69 credits van een plafond van 448 (19.735 over bij api_check.py, 265 "
                       "verbruikt deze maand, 22 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: TWAALF bulk-aanroepen à 3 credits (h2h + spreads + totals) voor "
                       "alle twaalf spelende competities MET sportkey, samen 36 credits; "
                       "split_budget(448, 12) -> (12, 12) dus niemand viel buiten de bulk en de "
                       "losse totals-stap was niet nodig. Stap 2: BTTS voor ALLE 33 duels met "
                       "een kandidaat-edge, 33 credits — de vereniging van beide schalen zoals "
                       "§1a sinds 13 september voorschrijft, en de tweede analyseronde leverde "
                       "er twee extra gekwalificeerde selecties op (Bradford City – Leyton "
                       "Orient en Wycombe Wanderers – Luton Town, beide BTTS nee). Zonder die "
                       "tweede ronde had de dag zes in plaats van acht gekwalificeerde selecties "
                       "gehad; beide vielen vervolgens op de lijstlengte af, dus ze hebben de "
                       "gepubliceerde lijst niet veranderd — maar ze staan nu wél in de reeks "
                       "'lijstlengte' en dat is waar §5b ze voor wil. De 15 duels zonder "
                       "kandidaat-edge staan in markets_checked als 'niet opgevraagd — geen "
                       "kandidaat-edge in dit duel', niet als gat. Na deze run staat het "
                       "maandverbruik op 334 van 20.000: het budget is op geen enkele manier de "
                       "beperkende factor, en de tijdsgrens van §0 is dat vandaag wél (zie "
                       "afkapping)."),
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
        s3 = json.load(open("tmp-run/rb_oct10_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct10_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct10_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct10_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

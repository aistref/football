"""Run B 6 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct04_publiceer.py` — dezelfde mechaniek, alleen de `parameters`-tekst is
die van vandaag. Eén duel in het inzetvenster (MLS, Chicago Fire FC – Vancouver Whitecaps,
02:30 NL op 7 okt) en één regel op rangorde: geen enkele selectie haalde de lat van 8,0 pp.
`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-08"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-08T05:12:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct08_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.991766, b=-0.005345 op 3726 afgerekende gevallen, fitted_through "
                          "2026-10-07. Die datum is de vórige rundag, dus calibration.py settle "
                          "is niet blijven liggen (§6b-5c); deze run wikkelde er zelf nog 3 af, "
                          "waarmee 3933 van 3957 waarnemingen compleet zijn. De correctie is "
                          "praktisch de identiteit: het ruwe model zei gemiddeld 33,333% en het "
                          "gebeurde 33,333%. Op de twee gepubliceerde regels haalde ze 0,24 "
                          "respectievelijk 0,14 pp van de edge af (7,89 -> 7,65 en 4,25 -> 4,11). "
                          "Let op wat die identiteit wél en niet zegt: de reeks is de "
                          "ONGESELECTEERDE ijksteekproef, breder dan de selecties waarop "
                          "gespeeld wordt — zie §1e, punt 3 van 30 sep."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "Vijftien van de zeventien competities uit de runlijst hadden GEEN WEDSTRIJD. "
                "Twee speelden: Romanian SuperLiga (ROU) met één duel en Série A (BRA) met vier. "
                "Dat is geen storing: scripts/idcheck.py gaf voor alle 33 fotmob_id\'s uit "
                "coverage.json een bruikbare stand (afsluitcode 0), dus geen enkele competitie is "
                "stil uit de lijst verdwenen. Dat is precies de controle waarvoor idcheck.py op "
                "29 september is gebouwd — op een dag als vandaag is GEEN WEDSTRIJD de normale "
                "uitkomst en zou een kapot id er niet van te onderscheiden zijn. Serie B (ITA) "
                "speelt weer op 9 oktober, en het id staat op 86 met xG voor alle twintig "
                "ploegen; morgen wordt dat id voor het eerst in een echte wedstrijd gebruikt."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 8 okt, 08:00 NL 9 okt). CFR Cluj – Universitatea Cluj "
                "is een gewoon Europees avondduel (17:30 UTC = 19:30 NL) en schuift niet. De vier "
                "Braziliaanse duels trappen af in de NACHT NA de rundag en vallen in de band "
                "waarvoor scripts/runwindow.py op 24 september is gebouwd: Santos – Flamengo "
                "22:30 UTC (00:30 NL) en Athletico Paranaense – Atlético-MG 23:00 UTC (01:00 NL) "
                "stonden op de daglijst van 2026-10-08, en Fluminense – Coritiba en Palmeiras – "
                "Bahia op 00:30 UTC van 2026-10-09 (02:30 NL) — source_day DAY+1, en toch horen "
                "ze bij DEZE run. Op de UTC-datum filteren zou die laatste twee aan de run van "
                "morgen hebben gegeven, die ze om 05:15 al gespeeld aantreft. Alle vijf hebben "
                "RunMatch.playable = True; de run begon om 05:05 NL, ruim voor de vroegste "
                "aftrap."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                       "today=2026-10-08 aangeroepen zoals §1e eist. Hij hield vandaag NIETS "
                       "tegen, en dat is geen toeval maar een gevolg van welke markten bovenaan "
                       "kwamen: beide gepubliceerde regels zijn Over/Under, dus side = None, en "
                       "dan staat de poort per definitie open (\'geen kant om te benadelen\'). "
                       "poort8_geblokkeerd en poort8_ruw zijn voor alle vijf de duels leeg, dus "
                       "de twee reeksen die de vraag van 25 september moeten beantwoorden groeien "
                       "deze run NIET. Ze staan op 36 afgewikkelde `underdog`-gevallen (+16,9%) "
                       "en 17 `underdog_ruw`; de meetlat van 30 is daarmee gehaald en de "
                       "gebruiker heeft op 5 oktober besloten de rem te laten staan. Die vraag "
                       "wordt hier dus NIET opnieuw gesteld (§1e: niet elke dag opnieuw "
                       "voorleggen), alleen de stand genoemd. poort8_vervallen.gepubliceerd "
                       "staat op False bij beide regels."),
            "WAAROM_TWEE_REGELS": (
                "Twee regels op drie plekken (donderdag, MAX_SHORTLIST = 3), en ze staan er op "
                "RANGORDE en niet omdat ze de lat halen: Under 3 bij Palmeiras – Bahia met "
                "+7,65 pp en Under 2.5 bij Santos – Flamengo met +4,11 pp, tegen een lat van "
                "8,0. §5b snijdt sinds 20 september aan het EIND van de dag: staan er minder "
                "selecties boven de drempel dan er regels in de lijst passen, dan bepaalt de "
                "rangorde de lijst en gaat de drempel mee als label. Er is geen derde regel "
                "geworden omdat de overige drie duels niets publiceerbaars opleverden — twee op "
                "data_tier = NONE (promovendi) en CFR Cluj op poort 5 (de twee methodes wijzen "
                "tegengesteld). Aanvullen is precies wat §5 verbiedt. De §5b-afkapping op "
                "LIJSTLENGTE bond dus niet en de reeks \'lijstlengte\' groeit deze run niet."),
            "WAT_1A_EN_5B_HIER_DOEN": (
                "Bij Palmeiras – Bahia haalde Under 2.5 @2,2936 (Matchbook, beurs) álle acht de "
                "poorten ÉN de lat van 8,0 pp (+8,93 pp, my_prob 52,53%, zwakste stand van het "
                "grid +8,98 pp) — en het is tóch niet de gepubliceerde regel. Dat is geen fout "
                "maar de regel van §1a: van alle selecties die de poorten halen publiceer je die "
                "met de hoogste selection_score (= edge × kans × tier), en sinds §5b de "
                "edge-drempel uit de poorten heeft gehaald, dingen ook de selecties eronder mee. "
                "Under 3 @1,75 wint dan op de hogere trefkans: 7,65 × 0,6479 = 4,956 tegen "
                "8,93 × 0,5253 = 4,693. §1a noemt dat met zoveel woorden een keuze over "
                "risicobereidheid. Dit is exact dezelfde situatie als bij Internacional – "
                "Corinthians op 7 oktober, en de twee TEKSTEN die daar als openstaand punt zijn "
                "genoteerd staan nog steeds verkeerd: het §5b-label (\'BET op rangorde — onder de "
                "lat van 8,0 pp\') leest nu alsof dit duel geen enkele selectie boven de lat had, "
                "en dat is niet waar; en de §1a-tekst \'alle acht de poorten\' noemt de edge nog "
                "als poort terwijl §5b hem eruit heeft gehaald. Tweede dag op rij dezelfde "
                "verwarring op dezelfde twee plekken — dat maakt het een regeltekst die bijgewerkt "
                "hoort en niet een eenmalige samenloop. De niet-gekozen selectie staat vast onder "
                "binnen_wedstrijd_niet_gekozen en gaat NIET het schaduwlogboek in: het is "
                "dezelfde mening in een andere markt (§1, 0-of-1-bet), geen afgewezen kandidaat."),
            "WAT_DE_POORTEN_DEDEN": (
                "37 selecties over zes markten, en de tweede methode is opnieuw de poort die "
                "vrijwel alles wegvangt: 29 van de 37 sneuvelden op \'tweede_methode\' (de twee "
                "methodes verslaan de markt niet dezelfde kant op), 7 op de edge, en 1 hield "
                "alles open. Poort 2 (koersband), 6 (robuustheid), 7 (context) en 8 (underdog) "
                "hielden vandaag niets tegen. Dat die ene poort viervijfde wegvangt is te "
                "begrijpen uit de lambdas: bij Palmeiras – Bahia geeft de xG-methode 1,486 / "
                "1,030 en de splitsmethode 2,269 / 0,506 — dezelfde richting, maar de "
                "splitsmethode maakt het verschil ruim twee keer zo groot; bij CFR Cluj – "
                "Universitatea Cluj wijzen ze zelfs tegengesteld (xG 1,642 / 1,548 tegen splits "
                "1,416 / 2,044), en daar is de enige kandidaat van het duel op afgeketst. DIT IS "
                "DE TWEEDE DAG OP RIJ dat deze poort in Série A tweederde of meer wegvangt (7 "
                "okt: 40 van 60). §5 (\'Net niet\') zegt dat zoiets dagen achtereen een bevinding "
                "is over de splitsmethode in deze competitie en geen ruis — en §6e wijst de "
                "splitsmethode al sinds 22 augustus aan als de scheefste van de twee. Dit is nu "
                "een reeks om in de gaten te houden en op te schrijven, niet om op te sleutelen."),
            "DRIE_DINGEN_DIE_BRAZILIE_EIGEN_ZIJN": (
                "1. PROMOVENDI OP NONE. Athletico Paranaense – Atlético-MG en Fluminense – "
                "Coritiba komen op data_tier = NONE uit omdat Athletico Paranaense en Coritiba "
                "niet in de Série A-stand van 2025 staan: ze zijn gepromoveerd uit Série B, en "
                "voor dat divisiepaar bestaat GEEN gemeten factor (promotion.TIER2 heeft geen "
                "Braziliaanse ingang). De foutmelding is letterlijk \'geen divisie boven of onder "
                "Série A (BRA) bekend\'. Dat is exact wat prompts/run-b.md voorschrijft — \'een "
                "Braziliaanse promovendus komt eveneens op NONE uit\' — en geen omissie om op te "
                "lossen met een gepoolde factor. Het kostte vandaag twee van de vijf duels, de "
                "helft van de Braziliaanse lijst; op 7 oktober waren het er ook twee van de zes. "
                "2. GEEN MARKTWAARDEN. Fotmob geeft voor Braziliaanse ploegen squad_value = 0 en "
                "out_value = 0, dus het criterium van poort 7 (≥ 10 pp méér ontbrekende "
                "selectiewaarde dan de tegenstander) is hier NIET MEETBAAR en de poort staat per "
                "definitie open op de blessurekant. De uitvallers zijn wél bij naam bekend "
                "(Fluminense 6, Flamengo 6, Atlético-MG 5, Athletico Paranaense 4, Coritiba 3, "
                "Santos 3, Palmeiras 3, Bahia 2) en staan in het contextblok; wat er niet is, is "
                "hun gewicht. Dat is een ontbrekende meting en geen bewijs dat het niet uitmaakt "
                "(§1c). De rustkant van poort 7 werkt wel en bond vandaag nergens, maar lag bij "
                "één duel dicht bij de grens: de meeste ploegen liggen rond 18 à 19 dagen rust "
                "(het interlandvenster), maar Santos staat op 6,0 tegen 18,0 voor Flamengo en "
                "Atlético-MG op 5,1 tegen 18,0 voor Athletico Paranaense. Dat is ruim twaalf "
                "dagen verschil, en het criterium (≤ 4 dagen rust ÉN ≥ 2 dagen minder dan de "
                "tegenstander) bindt niet omdat 6,0 en 5,1 bóven de vier liggen — de poort kijkt "
                "naar absolute rust en niet naar het verschil. Bij Santos – Flamengo is dat "
                "zichtbaar in de uitkomst: de gepubliceerde regel is een doelpuntenmarkt met "
                "side = None, dus de poort stond hoe dan ook open. "
                "3. GEEN VERPLAATSTE WEDSTRIJD. context.check_venue zet relocated = False bij "
                "alle vijf de duels; elk duel wordt in het eigen stadion van de thuisploeg "
                "gespeeld (Urbano Caldeira, Mário Celso Petraglia, Maracanã, Nubank Parque en "
                "Stadionul Dr. Constantin Rădulescu). §1c eist dat een verplaatsing wordt "
                "genoemd; er is er vandaag geen."),
            "ROEMENIE_HEEFT_GEEN_PLOEGNAMEN_IN_DE_CONTEXT": (
                "Een waarneming om vast te leggen, geen blokkade. Bij CFR Cluj – Universitatea "
                "Cluj geeft Fotmob in de matchDetails-respons GEEN ploegidentiteit terug: het "
                "contextblok staat op team_id = 0 met name = \'thuis\' en \'uit\', en out_count = 0 "
                "voor beide. Vorm (WWDLW thuis) en rust (19,1 dagen) zijn er wél, en de "
                "stadioncontrole werkt ook. Poort 7 stond dus open op de blessurekant omdat er "
                "niets te meten was — wat §1c expliciet toestaat (\'een meting die er niet is, is "
                "geen bewijs van een probleem\') — maar het is iets anders dan \'niemand ontbreekt\'. "
                "Het duel viel hoe dan ook op poort 5 af, dus er hing geen bet aan. Houd in de "
                "gaten of dit structureel is voor de vijf competities zonder xG; is dat zo, dan "
                "is de datarijkdom-score daar systematisch op het middenpunt aan het gokken in "
                "plaats van te meten."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug). Voor "
                "Série A (BRA) hebben alle zes markten werkelijk meegedongen: de bulk-aanroep "
                "leverde 1X2 op de beste prijs, Asian Handicap, Double Chance (de ±0,5-lijn) en "
                "Over/Under, en de tweede ronde kocht BTTS voor de twee duels met een "
                "kandidaat-edge. Draw No Bet is de uitzondering en het is GEEN gat maar een "
                "ontbrekende lijn: de spreads-respons bevatte voor geen van de Braziliaanse "
                "duels een 0.0-lijn, en dat staat zo in markets_checked (\'geen 0.0-lijn in de "
                "spreads-respons\'). Romanian SuperLiga heeft geen sportkey bij The Odds API en "
                "draait dus op het gratis BetExplorer-marktgemiddelde over 4 boeken; daar is 1X2 "
                "de enige markt en staan de vijf andere in markets_checked met \'niet opgevraagd "
                "— geen sportkey\'. 37 selecties: Asian Handicap 12, Over/Under 10, 1X2 9, BTTS 4, "
                "Double Chance 2, Draw No Bet 0. De marktbalans-controle SLAAGT — er is een "
                "competitie met een doelpuntenmarkt (Série A) en een met een uitkomstmarkt (beide "
                "zelfs) — maar met twee competities waarvan één zonder sportkey is dat een smalle "
                "marge, en dat hoort er zo bij te staan. Beide gepubliceerde regels komen uit de "
                "doelpuntenmarkt; met twee regels is over de verdeling van de uitkomst niets te "
                "zeggen, en een quotum is er niet (§1)."),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie is vandaag LEEG — factor 1,0000 over 0 speeldagen en "
                "0 competities — en hier zit een punt dat opgeschreven moet worden. Beide "
                "spelende competities vallen uit de pool: Série A (BRA) omdat 29 van de 38 "
                "speeldagen ruim over de helft is (league_level kiest route \'lopend\' en haalt "
                "het niveau rechtstreeks uit het lopende seizoen: thuis 1,523 / uit 1,140 / basis "
                "1,307), en Romanian SuperLiga (ROU) omdat er in geen van beide seizoenen xG is. "
                "Daarmee is de pool LEEG en valt de factor terug op 1,0000 — en Roemenië draait "
                "wél op route \'vorig+uplift\' (10 van de 30 speeldagen, dus onder de helft). Die "
                "route vermenigvuldigt het niveau van vorig seizoen dus met 1,0000 en doet "
                "feitelijk NIETS, terwijl de doelpunten dit seizoen hoger liggen dan vorig (thuis "
                "1,785 tegen 1,413, uit 0,848 tegen 1,142 over 10 speeldagen). De correctie is "
                "daarmee niet verkeerd toegepast maar leeg, en dat is zichtbaar gemaakt in plaats "
                "van stil gelaten (§3 Stage 5: een stil weggelaten waarneming is hetzelfde "
                "probleem als een stille truncatie). Het duel viel op poort 5 af, dus het heeft "
                "vandaag niets gekost. Wat het wél betekent: op een dag waarop alleen "
                "competities zonder xG vroeg in hun seizoen zitten, is er geen gepoolde correctie "
                "om op terug te vallen. Dat is een eigenschap van de constructie (de pool is "
                "competitie-overstijgend en xG-gebaseerd) en geen bug; het hoort op te vallen "
                "zodra zo\'n dag een bet oplevert."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("5 credits van een plafond van 413 (19.862 over bij api_check.py, 138 "
                       "verbruikt deze maand, 24 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: één bulk-aanroep à 3 credits (h2h + spreads + totals) voor Série "
                       "A (BRA) — de enige spelende competitie MET sportkey "
                       "(soccer_brazil_campeonato), dus split_budget(413, 1) -> (1, 1) en niemand "
                       "viel buiten de bulk; 19 events terug. Stap 2: BTTS voor de twee duels met "
                       "een kandidaat-edge, 2 credits. Let op: api_check.py noemt "
                       "soccer_brazil_campeonato niet onder \'Relevante sportkeys\' — die lijst is "
                       "een handmatige selectie in het script en geen uitspraak over wat er "
                       "actief is; de sportenlijst van The Odds API geeft de key wél als actief. "
                       "Na deze run staat het maandverbruik op 143 van 20.000, dus het budget is "
                       "op geen enkele manier de beperkende factor."),
            "BEURSKOERS": (
                "De twee gepubliceerde regels staan aan verschillende kanten van deze regel en "
                "§5 eist bij een beurs beide getallen. Regel 1, Palmeiras – Bahia Under 3 @1,75 "
                "bij BetOnline.ag: GEEN beurs, geen commissie, dus 1,75 is de koers die de "
                "gebruiker krijgt. Regel 2, Santos – Flamengo Under 2.5 bij Matchbook: WEL een "
                "beurs — 2,16 bruto en 2,1368 na 2% commissie, en edge_pp en selection_score "
                "rekenen met die 2,1368 (oddsapi.net_price). Matchbook komt vandaag vaker als "
                "beste boek voor en elke keer staan bruto én netto in markets_checked. "
                "BetExplorer leverde het gratis marktgemiddelde (3 tot 4 boeken per duel) voor "
                "het kalibratieblok van §6e en voor poort 8 — §1a: gemiddelde om te MÉTEN, beste "
                "prijs om te SPELEN. De beste prijs lag bij Palmeiras – Bahia 4,71% en bij "
                "Santos – Flamengo 4,11% boven het marktgemiddelde, in lijn met de +5,63% tot "
                "+7,78% die §1a op 5 september mat."),
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
        s3 = json.load(open("tmp-run/rb_oct08_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct08_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct08_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct08_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

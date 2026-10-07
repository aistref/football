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

DAG = "2026-10-07"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-07T05:20:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct07_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.991977, b=-0.005208 op 3711 afgerekende gevallen, fitted_through "
                          "2026-10-06. Die datum is de vórige rundag, dus calibration.py settle "
                          "is niet blijven liggen (§6b-5c). De correctie is praktisch de "
                          "identiteit: het ruwe model zei gemiddeld 33,333% en het gebeurde "
                          "33,333%. Op de twee gepubliceerde regels haalde ze 0,24 respectievelijk "
                          "0,21 pp van de edge af (6,88 -> 6,64 en 6,55 -> 6,34). Let op wat die "
                          "identiteit wél en niet zegt: de reeks is de ONGESELECTEERDE "
                          "ijksteekproef, breder dan de selecties waarop gespeeld wordt — zie "
                          "§1e, punt 3 van 30 sep."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "Zestien van de zeventien competities uit de runlijst hadden GEEN WEDSTRIJD; "
                "alleen Série A (BRA) speelt, met zes duels in het inzetvenster. Dat is geen "
                "storing: scripts/idcheck.py gaf voor alle zeventien fotmob_id\'s een bruikbare "
                "stand (afsluitcode 0), dus geen enkele competitie is stil uit de lijst "
                "verdwenen. Dat is precies de controle waarvoor idcheck.py op 29 september is "
                "gebouwd — op een dag als vandaag is GEEN WEDSTRIJD de normale uitkomst en zou "
                "een kapot id er niet van te onderscheiden zijn. Serie B (ITA) speelt weer op "
                "9 oktober, dus het id 86 (en niet 56) wordt dan voor het eerst in een echte "
                "wedstrijd gebruikt."),
            "INZETVENSTER": (
                "Alle zes duels spelen in Brazilië en vallen daarmee in de band waarvoor "
                "scripts/runwindow.py op 24 september is gebouwd: ze trappen af tussen 00:30 en "
                "02:30 NL in de NACHT NA de rundag. Vijf stonden op de daglijst van 2026-10-07 "
                "(aftrap 22:30 en 23:30 UTC) en Cruzeiro – São Paulo op die van 2026-10-08 "
                "(00:30 UTC, 02:30 NL) — source_day DAY+1, en toch hoort het bij deze run, want "
                "het inzetvenster is [08:00 NL 7 okt, 08:00 NL 8 okt). Op de UTC-datum filteren "
                "zou dat ene duel aan de run van morgen hebben gegeven, die het om 05:15 al "
                "gespeeld aantreft. Alle zes hebben RunMatch.playable = True."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                       "today=2026-10-07 aangeroepen zoals §1e eist. Hij hield vandaag VIJF "
                       "selecties tegen, verdeeld over twee wedstrijden, en bij één daarvan is "
                       "dat beslissend geweest voor de dag. Als EERSTE dichte poort: bij Botafogo "
                       "– Vasco da Gama de drie sterkste selecties op de THUISkant (Asian "
                       "Handicap Botafogo +0,25 @1,8134 met +6,34 pp en score 3,898; 1X2 Botafogo "
                       "wint @2,9404 met +8,78 pp; Draw No Bet Botafogo @2,08 met +6,29 pp), want "
                       "het marktgemiddelde geeft Botafogo 33,8% tegen 38,9% voor Vasco — ONDER "
                       "de 0,35; en bij RB Bragantino – Mirassol 1X2 Mirassol wint @4,50 (+3,75 "
                       "pp, 21,9% tegen 52,6%). Per wedstrijd gaat de sterkste als failed_gate = "
                       "\'underdog\' naar data/shadow.jsonl (§1e, één rij per wedstrijd per "
                       "categorie), dus de reeks die de vraag van 25 september moet beantwoorden "
                       "groeit deze run met TWEE. poort8_ruw is leeg: op de ruwe schaal sneuvelen "
                       "diezelfde selecties op dezelfde poort, dus ze staan al in de eerste "
                       "categorie en mogen er niet nóg eens bij (§1e, punt 2). De gepubliceerde "
                       "regel staat niet op zo\'n kant: Internacional is met 42,6% tegen 28,4% de "
                       "favoriet, en poort8_vervallen.gepubliceerd staat op False."),
            "WAAROM_EEN_REGEL": (
                "Eén regel op drie plekken (woensdag), en hij staat er op RANGORDE en niet omdat "
                "hij de lat haalt: Draw No Bet Internacional @1,63 met +6,64 pp, tegen een lat "
                "van 8,0. §5b snijdt sinds 20 september aan het EIND van de dag: staan er minder "
                "selecties boven de drempel dan er regels in de lijst passen, dan bepaalt de "
                "rangorde de lijst en gaat de drempel mee als label. Er zijn geen drie regels "
                "geworden omdat de overige vijf duels niets publiceerbaars opleverden — twee op "
                "data_tier = NONE (promovendi), Botafogo – Vasco op poort 8 en daarna poort 6, en "
                "RB Bragantino en Cruzeiro onder de NEAR-ondergrens van 3,0 pp. Aanvullen is "
                "precies wat §5 verbiedt. De §5b-afkapping op LIJSTLENGTE bond dus niet en de "
                "reeks \'lijstlengte\' groeit deze run niet."),
            "DE_REPARATIE_VAN_VANDAAG": (
                "DIT IS DE BELANGRIJKSTE BEVINDING VAN DEZE RUN EN ZE RAAKT ELKE EERDERE RUN MET "
                "AMERIKAANSE OF BRAZILIAANSE DUELS. `find_1x2` in het analysescript koos het "
                "BetExplorer-marktgemiddelde uit `[r for r in rows if r[\'is_today\']] or rows`, en "
                "dat is dezelfde fout als de UTC-datumfilter die §3 Stage 1 op 24 september heeft "
                "vervangen — nu aan de PRIJSkant. BetExplorer zet `is_today` naar zijn eigen "
                "pagina-datum, dus een duel dat om 23:30 UTC afrapt staat daar als \'morgen\' "
                "terwijl het in het inzetvenster van vandaag valt. Van de vier doorrekenbare "
                "duels van vandaag stonden er maar twee in die dagpool. Wat dat kostte, gemeten "
                "door de run eerst fout en daarna goed te laten lopen: (1) Botafogo – Vasco da "
                "Gama en Cruzeiro – São Paulo kregen GEEN kalibratieblok — vier van de twaalf "
                "waarnemingen van vandaag, oftewel een derde, viel stil weg uit de reeks waarop "
                "§1g de herijking fit; en (2) poort 8 kwam bij diezelfde twee duels uit op \'geen "
                "1X2-prijzen — geen marktoordeel over wie de mindere is\' en stond dus OPEN zonder "
                "te zijn getoetst. Punt 2 is geen formaliteit: in de eerste doorloop was de "
                "gepubliceerde topregel van de dag Asian Handicap Botafogo +0,25 @1,8134, en met "
                "het marktgemiddelde erbij blijkt Botafogo met 33,8% juist de kant te zijn die "
                "poort 8 sinds 1 oktober moet tegenhouden. De routine stond dus op het punt een "
                "bet te publiceren die een van haar acht poorten expliciet verbiedt — precies de "
                "stille faalstand van het Serie B-id en van `calibration.py settle`: een stap die "
                "overgeslagen kan worden zonder dat iets klaagt. De nieuwe `find_1x2` koppelt "
                "eerst exact binnen de dagpool, dan exact over alle rijen van de competitie, en "
                "pas daarna soepel binnen de dagpool — strikt nauwkeuriger en niet ruimer, want "
                "`resolve` eist thuis én uit in de juiste volgorde, dus een retourwedstrijd uit de "
                "seizoenslijst komt er niet via een naamgok in. De reparatie staat in "
                "tmp-run/rb_oct07_analyze.py en hoort in het volgende runscript van Run A en Run "
                "C ook te staan: zij hebben dezelfde regel en Run C heeft bij uitstek duels in "
                "Amerikaanse tijdzones."),
            "WAT_1A_EN_5B_HIER_DOEN": (
                "Bij Internacional – Corinthians haalde het 1X2 op de thuisploeg álle acht de "
                "poorten ÉN de lat van 8,0 pp (Internacional wint @2,31, +8,04 pp, score 4,127) — "
                "en het is tóch niet de gepubliceerde regel. Dat is geen fout maar de regel van "
                "§1a: van alle selecties die de poorten halen publiceer je die met de hoogste "
                "selection_score (= edge × kans × tier), en sinds §5b de edge-drempel uit de "
                "poorten heeft gehaald, dingen ook de selecties eronder mee. De push-beschermde "
                "uitdrukking van dezelfde mening wint dan op de hogere trefkans: Draw No Bet "
                "Internacional 4,515 tegen 4,127 voor het 1X2. §1a noemt dat met zoveel woorden "
                "een keuze over risicobereidheid, en wijst er bovendien op dat een DNB "
                "ongevoelig is voor de bekende zwakte van dit model (kansmassa tussen winst en "
                "gelijkspel): bij een gelijkspel komt de inzet terug in plaats van weg te zijn. "
                "Wat hier wél opvalt en wat de gebruiker moet weten: de LABELTEKST van §5b "
                "(\'BET op rangorde — onder de lat van 8,0 pp\') leest nu alsof dit duel geen "
                "enkele selectie boven de lat had, en dat is niet waar. En de §1a-tekst \'alle "
                "acht de poorten\' is bij de wijziging van 20 september niet meegeschreven: ze "
                "noemt de edge nog als poort terwijl §5b hem eruit heeft gehaald. Beide teksten "
                "horen bijgewerkt; de uitkomst van vandaag verandert daar niet door. De "
                "niet-gekozen 1X2-selectie staat vast onder binnen_wedstrijd_niet_gekozen en gaat "
                "NIET het schaduwlogboek in: het is dezelfde mening in een andere markt (§1, "
                "0-of-1-bet), geen afgewezen kandidaat."),
            "WAT_DE_POORTEN_DEDEN": (
                "60 selecties over zes markten, en de tweede methode is de poort die vandaag "
                "vrijwel alles wegvangt: 40 van de 60 sneuvelden op \'tweede_methode\' (de twee "
                "methodes verslaan de markt niet dezelfde kant op), 9 op de edge, 5 op poort 8, 3 "
                "op de koersband, 2 op de robuustheid, en 1 hield alles open. Dat die ene poort "
                "tweederde wegvangt is te begrijpen uit de lambdas: bij Botafogo – Vasco geeft de "
                "xG-methode 1,483 / 1,434 (vrijwel gelijk) en de splitsmethode 2,698 / 1,549 "
                "(Botafogo veel sterker), bij Cruzeiro – São Paulo 1,507 / 1,089 tegen 2,136 / "
                "0,602. De twee methodes lopen in deze competitie dus ver uiteen, en §5 vangt dat "
                "af zoals het hoort. Blijft dit dagen achtereen zo, dan is dat een bevinding over "
                "de splitsmethode in Série A en geen ruis (§5, \'Net niet\'). Poort 6 hield bij "
                "Botafogo – Vasco de twee doelpuntenmarkten tegen die ná poort 8 nog overbleven "
                "(Over 2,5 @1,8036 met min_edge −1,48 pp en Over 2,75 @2,01 met −1,39 pp); die "
                "laatste staat als near_miss in het schaduwlogboek. Poort 7 (context) hield "
                "vandaag niets tegen."),
            "DRIE_DINGEN_DIE_BRAZILIE_EIGEN_ZIJN": (
                "1. PROMOVENDI OP NONE. Remo – Grêmio en Vitória – Chapecoense komen op "
                "data_tier = NONE uit omdat Remo en Chapecoense niet in de Série A-stand van "
                "2025 staan: ze zijn gepromoveerd uit Série B, en voor dat divisiepaar bestaat "
                "GEEN gemeten factor (promotion.TIER2 heeft geen Braziliaanse ingang). Dat is "
                "exact wat prompts/run-b.md voorschrijft — \'een Braziliaanse promovendus komt "
                "eveneens op NONE uit\' — en geen omissie om op te lossen met een gepoolde "
                "factor. 2. GEEN MARKTWAARDEN. Fotmob geeft voor Braziliaanse ploegen "
                "squad_value = 0 en out_value = 0, dus het criterium van poort 7 (≥ 10 pp méér "
                "ontbrekende selectiewaarde dan de tegenstander) is hier NIET MEETBAAR en de "
                "poort staat per definitie open op de blessurekant. De uitvallers zijn wél bij "
                "naam bekend (Internacional 6, Corinthians 4, Botafogo 4, Vasco 3) en staan in "
                "het contextblok; wat er niet is, is hun gewicht. Dat is een ontbrekende meting "
                "en geen bewijs dat het niet uitmaakt (§1c). De rustkant van poort 7 werkt wel: "
                "alle duels liggen rond 17 à 18 dagen rust, behalve RB Bragantino (4,0 dagen) en "
                "São Paulo (5,1 dagen). 3. EEN VERPLAATSTE WEDSTRIJD. context.check_venue zet "
                "relocated = True bij Remo – Grêmio: er wordt gespeeld in het Estádio Estadual "
                "Jornalista Edgar Augusto Proença (Mangueirão, Belém) en niet in Remo\'s eigen "
                "Estádio Evandro Almeida. §1c eist dat een verplaatsing in het runrapport wordt "
                "genoemd ook als de poort opengaat; hier is het duel toch al NONE, dus er hing "
                "geen bet aan. De andere vijf stadions zijn het eigen stadion van de thuisploeg."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug). Alle zes "
                "markten hebben werkelijk meegedongen: de bulk-aanroep leverde 1X2 op de beste "
                "prijs, Asian Handicap, Draw No Bet (de 0.0-lijn), Double Chance (de ±0,5-lijn) "
                "en Over/Under, en de tweede ronde kocht BTTS voor de drie duels met een "
                "kandidaat-edge. 60 selecties: Asian Handicap 16, Over/Under 14, 1X2 12, Draw No "
                "Bet 8, BTTS 6, Double Chance 4. De marktbalans-controle slaagt — de enige "
                "spelende competitie heeft zowel de uitkomstmarkten als de doelpuntenmarkt — maar "
                "met één competitie is dat de smalst mogelijke manier om te slagen, en dat hoort "
                "er zo bij te staan. De gepubliceerde regel is een uitkomstmarkt (Draw No Bet); "
                "met één regel is over de verdeling van de uitkomst niets te zeggen."),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie is vandaag LEEG — factor 1,0000 over 0 speeldagen en "
                "0 competities — en dat is correct gedrag en geen defect. Série A (BRA) is de "
                "enige spelende competitie en uplift_observations laat haar weg: 28 van de 38 "
                "speeldagen is ruim over de helft, dus league_level kiest de route \'lopend\' en "
                "haalt het niveau rechtstreeks uit het lopende seizoen (thuis 1,516 / uit 1,147 / "
                "basis 1,299) in plaats van vorig seizoen × factor. Dat is precies wat "
                "prompts/run-b.md voor de vier kalenderjaarcompetities voorschrijft sinds 24 "
                "september, en de seizoensnotatie is \'2025\'/\'2026\' en niet \'2025/2026\'. Het "
                "weglaten zelf is de meting en staat daarom in het rapport (§3 Stage 5)."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("6 credits van een plafond van 396 (19.868 over bij api_check.py, 132 "
                       "verbruikt deze maand, 25 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: één bulk-aanroep à 3 credits (h2h + spreads + totals) voor Série "
                       "A (BRA) — de enige spelende competitie, met sportkey "
                       "soccer_brazil_campeonato, dus split_budget(396, 1) -> (1, 1) en niemand "
                       "viel buiten de bulk. Stap 2: BTTS voor de drie duels met een "
                       "kandidaat-edge, 3 credits. Let op: api_check.py noemt "
                       "soccer_brazil_campeonato niet onder \'Relevante sportkeys\' — die lijst is "
                       "een handmatige selectie in het script en geen uitspraak over wat er "
                       "actief is; de sportenlijst van The Odds API geeft de key wél als actief, "
                       "en de bulk-aanroep leverde 21 events. Na deze run staat het maandverbruik "
                       "op 138 van 20.000."),
            "BEURSKOERS": (
                "De gepubliceerde regel staat NIET op een beurs: Draw No Bet Internacional @1,63 "
                "bij 1xBet, geen commissie, dus de koers in het rapport is de koers die de "
                "gebruiker krijgt. Waar de beste prijs wél bij een beurs stond, is "
                "oddsapi.net_price gebruikt — Matchbook komt vandaag zes keer als beste boek voor "
                "en elke keer staat de brutokoers én de koers na 2% commissie in markets_checked "
                "(bijvoorbeeld Botafogo +0,25 1,83 bruto / 1,8134 netto, de regel die poort 8 "
                "tegenhield). BetExplorer leverde het gratis marktgemiddelde over 21 rijen voor "
                "het kalibratieblok (§6e) en voor poort 8 (§1a: gemiddelde om te meten, beste "
                "prijs om te spelen) — zie DE_REPARATIE_VAN_VANDAAG voor waarom die twee rollen "
                "vanochtend bijna waren weggevallen."),
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
        s3 = json.load(open("tmp-run/rb_oct07_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct07_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct07_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct07_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

"""Run A 16 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct15_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. NEGEN van de eenentwintig competities uit de runlijst speelden, met TIEN duels in het
inzetvenster: de vrijdagavond-openingsronde van Serie A, La Liga, Bundesliga, Ligue 1, de
Championship, de Eredivisie, de Süper Lig, de Danish Superliga en de Ekstraklasa (twee).

DRIE regels gepubliceerd, alle drie uit de doelpuntenmarkt, en GEEN ENKELE haalt zijn eigen lat.
Dat is §5b in zijn zuiverste vorm: de rangorde bepaalt de lijst en de drempel gaat als label mee.
MAX_SHORTLIST = 5 (vrijdag) en MAX_LIGHT_IN_SHORTLIST = 2 binden allebei NIET — er zijn maar drie
publiceerbare selecties en twee ervan staan op LIGHT. Zie DRIE_REGELS_GEEN_HAALT_ZIJN_LAT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-16"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-16T04:28:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
                      + ("ONDER-KANT: §6g meet dat P(Under) bij élk duel 1,6 tot 2,4 procentpunt "
                         "te hoog staat door een vormfout in score_grid, en dat de gespeelde "
                         "Under-kant daar bovenop een selectie-effect van +0,68 doelpunt per duel "
                         "heeft (z = +2,91). Over het logboek: Under 76 picks op -16,5%, Over 62 "
                         "picks op +10,6%. Poort 9 (§1h) bindt hier NIET — op LIGHT geldt hij per "
                         "besluit van 12 okt 2026 niet, en op FULL bindt hij alleen in de band "
                         "8-10 pp. Lees deze regel dus met die scheefstand erbij. "
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
    for run, pad in (("A", "tmp-run/ra_oct16_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.022634, "
                "b=0.014649 over 4608 afgerekende gevallen, fitted_through 2026-10-15, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle vóór "
                "de analyse gedraaid (69 waarnemingen afgewikkeld, 4815 van 4839 compleet, 24 "
                "nog open). De fit VERHOOGT een kans over vrijwel de hele speelbare band en "
                "verlaagt alleen onder ~35%; het ruwe model zei gemiddeld 33,333% en het "
                "gebeurde 33,333%. Bij alle DRIE de gepubliceerde regels staat de herijkte edge "
                "daardoor BOVEN de ruwe (+12,95 tegen +12,25 pp bij Wieczysta Kraków, +8,17 "
                "tegen +7,52 bij Frosinone, +3,10 tegen +2,68 bij Eintracht Frankfurt) en staat "
                "`bet_beide` op FALSE — ze halen hun lat op GEEN van beide schalen en zijn op "
                "rangorde gepubliceerd (§5b)."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "NEGEN van de eenentwintig competities uit de runlijst speelden, met TIEN duels "
                "samen in het inzetvenster: Serie A, La Liga, Bundesliga, Ligue 1, Championship, "
                "Eredivisie, Süper Lig en Danish Superliga met elk één, en de Ekstraklasa met "
                "twee. Het is de vrijdagavond-openingsronde van het Europese weekend; de drie "
                "Europese toernooien speelden donderdag (Run A van 15 oktober) en de Premier "
                "League, Primeira Liga, Belgian Pro League en Scottish Premiership beginnen pas "
                "zaterdag. Dat is GEEN WEDSTRIJD en geen storing (§3 Stage 2)."),
            "ACHT_VAN_DE_TIEN_DUELS_HEBBEN_EEN_OMGEREKENDE_PLOEG": (
                "Dit is vandaag de hoofdzaak en de reden dat er maar twee FULL-duels zijn. Het "
                "is de achtste speelronde van 2026/2027 en de promovendi staan er massaal in. "
                "OMHOOG langs promotion.TIER2 (zeven ploegen): Frosinone (Serie B, gemeten paar "
                "I1/I2, aanval 1.562 in bereik 1.004-1.667), Deportivo A Coruña (LaLiga2, "
                "SP1/SP2), Le Mans (Ligue 2, F1/F2), Çorum FK (1. Lig, eigen meting 31 aug), "
                "Wieczysta Kraków en Wisła Kraków (I Liga, eigen meting 31 aug) en AC Horsens "
                "(1. Division, eigen meting 31 aug). OMLAAG langs promotion.TIER1 (twee "
                "ploegen): Burnley EN Wolverhampton Wanderers, beide uit de Premier League naar "
                "de Championship, met het gemeten fd_pair (E0,E1) x1.830/0.634. §4 waarschuwt "
                "dat de richting OMLAAG nog niet apart is gemeten; dat geldt voor het "
                "NEDERLANDSE paar (Keuken Kampioen Divisie, dat op POOLED_GAP terugvalt) en "
                "NIET voor het Engelse, dat gewoon bij football-data.co.uk staat. Lees het "
                "Burnley-duel dus niet met een extra voorbehoud dat er niet is. GEEN ENKELE "
                "omrekening van vandaag draait op POOLED_GAP: lees de stand per selectie uit "
                "GapResult.direction, zoals §4 sinds 9 oktober eist."),
            "WIECZYSTA_KRAKOW_PASSEERT_CONVERSION_IN_RANGE_OP_DE_GRENS": (
                "De relatieve verdediging van Wieczysta Kraków is 0.929 en de bovengrens van het "
                "gemeten bereik is EXACT 0.929 (eigen meting 31 aug 2026, Ekstraklasa/I Liga, "
                "n=24). De poort gaat dus open met een marge van 0.000, en dit is de "
                "hoogst-rangschikkende bet van de dag. Dat hoort er zo bij te staan in plaats "
                "van als 'binnen het bereik': één waarneming minder in die meting en dit duel "
                "was NONE geweest, net als AC Horsens hieronder. Zelfde soort grensgeval als "
                "Västerås SK op 9 oktober, dat de rangorde met 0,04 procentpunt miste."),
            "AC_HORSENS_IS_NONE_EN_DAT_IS_GEEN_TEKORT": (
                "AC Horsens – Randers FC is het enige duel op data_tier NONE, en de reden is "
                "een GEMETEN poort en geen gat: de relatieve aanval van AC Horsens is 0.860 en "
                "het gemeten invoerbereik van het Deense paar (Danish Superliga/1. Division, "
                "eigen meting 31 aug 2026, n=18) loopt van 0.989 tot 1.747. "
                "conversion_in_range weigert dus, en dat is precies de Coventry-val waarvoor "
                "die poort bestaat (§4): een promovendus met een aanval zwakker dan alles wat "
                "ooit is gemeten, is geen geval om op te extrapoleren. Nul van de zes markten "
                "is doorgerekend, zoals §6b-5b voor tier NONE voorschrijft."),
            "DE_CAP_BINDT_NIET": (
                "Tien duels op een vrijdagcap van 55 (ranking.max_deep_analyses, vr-zo), dus er "
                "is NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel. De datarijkdom "
                "liep van 5.0 tot 7.0 over de tien duels; omdat er niets afviel is er geen "
                "'laagste die het haalde' en geen 'hoogste die afviel' te noemen (§3 Stage 4). "
                "De context is voor alle tien duels opgehaald, ook voor AC Horsens op NONE, "
                "zoals §1c eist."),
            "DRIE_REGELS_GEEN_HAALT_ZIJN_LAT": (
                "Er zijn drie publiceerbare selecties en alle drie zijn gepubliceerd. GEEN "
                "ENKELE haalt de drempel van §0: Wieczysta Kraków Over 3 staat op +12,95 pp "
                "tegen een LIGHT-lat van 16,0, Frosinone Under 3.5 op +8,17 tegen 16,0, en "
                "Eintracht Frankfurt Under 3.5 op +3,10 tegen een FULL-lat van 8,0. Alle drie "
                "staan wél boven de NEAR-ondergrens die §5b als vloer gebruikt (3,0 op FULL, "
                "6,0 op LIGHT) en hebben alle acht overige poorten open. MAX_SHORTLIST = 5 "
                "(vrijdag) en MAX_LIGHT_IN_SHORTLIST = 2 binden dus BEIDE niet: er zijn maar "
                "drie kandidaten en precies twee staan op LIGHT. Er valt daarom geen enkele "
                "gekwalificeerde selectie op de lijstlengte en er is geen lijstlengte-rij in het "
                "schaduwlogboek. Lees deze lijst als 'het beste van vandaag' en niet als een "
                "gevonden voordeel — dat is letterlijk waarvoor §5b het label per regel eist."),
            "ALLE_DRIE_DE_REGELS_ZIJN_EEN_DOELPUNTENMARKT": (
                "Over/Under levert alle drie de regels, en dat is vandaag GEEN inkoopartefact — "
                "de marktbalans-controle slaagt ruim (zie MARKTBALANS): negen van de negen "
                "competities kregen de volle bulk met zowel uitkomst- als doelpuntenmarkt, en er "
                "zijn 46 Over/Under-selecties tegen 26 1X2, 34 Asian Handicap, 15 Draw No Bet, "
                "7 Double Chance en 10 BTTS doorgerekend. De uitkomstmarkten dongen dus volop "
                "mee en selection_score koos deze drie. Twee van de drie staan op de "
                "UNDER-kant, en §6g meet die kant op -16,5% over 76 picks tegen +10,6% voor "
                "Over — dat staat bij elke pick in `notes` en hoort ook in het dagrapport."),
            "POORT_9_RAAKT_GEEN_VAN_DE_DRIE_UNDERS_EN_DAT_IS_EEN_BEVINDING": (
                "Vijfde bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke selectie "
                "aangeroepen met today=2026-10-16. poort9_geblokkeerd is voor alle tien duels "
                "leeg. Bij Frosinone (Under 3.5, LIGHT) is dat het besluit van 12 oktober: de "
                "poort geldt alleen op FULL. Bij Eintracht Frankfurt (Under 3.5, FULL, +3,10 pp) "
                "is het de VORM van de poort: unders.check geeft passed=True met de reden 'onder "
                "de gewone drempel van 8,0 pp, dus edge is de bindende poort en niet poort 9'. "
                "Onder §5b is `edge` echter GEEN poort meer maar een afkapping, dus er bindt "
                "hier niets. Gevolg, en dit is de bevinding: een FULL-Under met 8,5 pp WORDT "
                "geblokkeerd en een FULL-Under met 3,10 pp niet, terwijl de tweede minder "
                "voordeel claimt. Dat is niet-monotoon. Deze run verandert daar NIETS aan — "
                "§1h en §1e leggen vast dat een run een poort nooit op eigen initiatief "
                "verzet en dat de vraag niet opnieuw wordt gesteld zolang de reeks niet van "
                "teken draait of de vormfout niet is gerepareerd. Het staat als bevinding in "
                "het runrapport."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [16.10. 08:00 NL, 17.10. 08:00 NL). "
                "Alle tien duels stonden op de daglijst van 16 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle tien zijn playable: de "
                "vroegste aftrap is Wieczysta Kraków – Raków Częstochowa om 18:00 NL en de "
                "laatste Deportivo A Coruña – Levante en Burnley – Wolverhampton om 21:00 NL. "
                "Er is dus geen enkel duel dat al was afgetrapt voordat de gebruiker kon "
                "inzetten, en geen carry-over-band."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert "
                "de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van de "
                "zestien competities met een fotmob_id zijn het eens, inclusief de zeven die "
                "vandaag GEEN WEDSTRIJD hebben: tien duels bij Fotmob, tien bij BetExplorer, "
                "nul afwijkingen (tmp-run/ra_oct16_bevestiging.json)."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "De vijf bekers van de runlijst (FA Cup, League Cup, Coppa Italia, KNVB Beker, "
                "DFB Pokal) hebben geen fotmob_id in coverage.json, dus runwindow kan ze niet "
                "filteren en 'niet in de daglijst' mag voor hen nooit als GEEN WEDSTRIJD worden "
                "opgeschreven (dat kostte Run A op 6 oktober vijf duels). Ze zijn daarom langs "
                "BetExplorer gegaan: alle vijf leveren teamparen op de fixturepagina (32, 8, 8, "
                "26 en 16) en bij alle vijf valt de eerstvolgende ronde BUITEN het inzetvenster. "
                "De FA Cup zit er het dichtst bij met 'Tomorrow 12:30' UK, oftewel 17 oktober "
                "13:30 NL — ruim na het einde van het venster om 08:00 NL. Apart nagegaan dat er "
                "geen enkel bekerduel in de band 17.10. 00:00-08:00 NL staat; de vroegste is "
                "12:30 UK. Alle vijf dus GEEN WEDSTRIJD, met een tweede bron eronder."),
            "ALLE_NEGEN_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Negen van de negen spelende competities hebben een sportkey bij The Odds API, "
                "dus er valt geen enkele buiten de betaalde inkoop en er is vandaag geen "
                "competitie waar BetExplorer de enige 1X2-bron is (§1a). De beste prijs is "
                "overal opgehaald; de winst van de beste prijs boven het marktgemiddelde liep "
                "van +4,07% (Serie A) tot +6,29% (Bundesliga) per selectie."),
            "MARKTBALANS": (
                "Plafond suggest_cap(19427, 16) = 606 credits. split_budget(606, 9) geeft 9 "
                "spreads / 9 totals, en omdat 3 x 9 = 27 onder 606 blijft is de volle "
                "BULK-aanroep gedaan: h2h + spreads + totals voor alle negen competities, dus "
                "vijf van de zes markten in één keer. Daarna BTTS voor de vijf duels met een "
                "kandidaat-edge (2 credits per duel, §1a stap 2 met de vereniging van beide "
                "schalen): Frosinone, Eintracht Frankfurt, SC Heerenveen, Çorum FK en Wieczysta "
                "Kraków. Totaal 32 van 606 credits, 19395 over. De marktbalans-controle slaagt "
                "RUIM: negen van de negen competities hebben zowel een uitkomstmarkt (1X2, AH, "
                "DNB, DC) als een doelpuntenmarkt (O/U) — niet één op negen zoals op 30 "
                "augustus, maar negen op negen. Doorgerekend: 46 Over/Under, 34 Asian Handicap, "
                "26 1X2, 15 Draw No Bet, 10 BTTS en 7 Double Chance, samen 138 selecties over "
                "negen duels (AC Horsens staat op NONE en is niet doorgerekend)."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Voor negen van de tien duels gevonden (AC Horsens niet, "
                "en daar is ook geen eigen 1X2), gemiddelde Pinnacle-marge 3,91% tegen 6 à 10% "
                "bij de rest. Gemiddelde absolute afstand tussen het eigen model en het "
                "Pinnacle-oordeel: 3,79 procentpunt — DICHTER dan gebruikelijk. De grootste "
                "afwijkingen: Çorum FK – Rizespor (-12,88 pp op de thuiszege; precies het duel "
                "dat poort 7 heeft tegengehouden) en Eintracht Frankfurt – 1. FC Köln (-9,15 pp "
                "op de thuiszege, +10,05 op de uitzege). HARDE GRENS §2/§4: dit getal zit NIET "
                "in my_prob en NIET in prob_sources; het is andermans lezing en marktafgeleid, "
                "en het hoort in de vergelijking."),
            "UNDERSTAT_KWAM_ER_NA_EEN_NAAMREPARATIE_BIJ": (
                "Understat dekt vijf competities en vier ervan speelden vandaag (Serie A, La "
                "Liga, Bundesliga, Ligue 1), maar bij zes van de acht ploegen in die vier duels "
                "is er geen stand van 2025/2026: Frosinone, Deportivo A Coruña en Le Mans zijn "
                "promovendus en stonden er terecht niet in. Bij het ZEVENDE geval lag het aan de "
                "naam: Understat noemt 1. FC Köln in het Engels 'FC Cologne', en "
                "scripts/teamnames.ALIASES kende alleen de korte Duitse vorm. understat_pair "
                "gaf daardoor None ZONDER foutmelding en het kalibratieblok van Eintracht "
                "Frankfurt – 1. FC Köln miste p_xg_understat — dezelfde stille faalstand als "
                "'Sheff Wed' (1 sep) en de æ-ligatuur (13 sep), nu aan de kant van de tweede "
                "xG-bron. De alias is vandaag bijgeschreven en de analyse opnieuw gedraaid; de "
                "rangorde is er niet door veranderd. Wat het WEL oplevert: dit duel heeft nu "
                "twee onafhankelijke xG-modellen naast elkaar, en ze zijn het oneens over Köln "
                "— Fotmob komt op een doelverwachting van 1.767 voor Köln, Understat op 1.418. "
                "Understat zou de gepubliceerde Under 3.5 dus STERKER steunen dan Fotmob. Dat "
                "verschil gaat per §4 NIET in my_prob; het gaat als p_xg_understat het "
                "kalibratielogboek in, waar over enkele weken te meten is welk xG-model beter "
                "voorspelt."),
            "GEEN_VERPLAATSTE_WEDSTRIJD": (
                "context.check_venue is voor alle tien duels gedraaid en relocated is overal "
                "False: elke thuisploeg speelt in haar eigen stadion (Stadio Benito Stirpe, "
                "Deutsche Bank Park, enzovoort). Dat is een controle die ook bij een open poort "
                "wordt gemeld (§1c)."),
            "OPSTELLINGEN": (
                "lineup_type: vijf duels op 'predicted' (Frosinone, Deportivo, Eintracht "
                "Frankfurt, Le Mans, SC Heerenveen, AC Horsens) en vier op 'lastStarting11' "
                "(Burnley, Çorum FK, Wieczysta Kraków, Widzew Łódź). Een vroege vrijdagavond "
                "betekent dat de bevestigde elftallen er nog niet zijn; dat zit in de "
                "datarijkdom (§3 Stage 4) en niet in my_prob."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn drie publiceerbare selecties en drie
        # plekken gebruikt. Deze lus blijft staan omdat ze de enige plek is waar een
        # gekwalificeerde selectie die niet in de lijst past wordt vastgelegd
        # (`failed_gate = "lijstlengte"`, bewust dezelfde naam — §5b, 26 sep 2026).
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
        s3 = json.load(open("tmp-run/ra_oct16_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct16_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct16_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct16_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct16_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

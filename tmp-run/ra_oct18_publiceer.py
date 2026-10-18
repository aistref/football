"""Run A 18 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct17_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TIEN van de eenentwintig competities uit de runlijst speelden, met 35 duels in het
inzetvenster: de zondag van hetzelfde weekend, met de Ligue 1 en de Eredivisie (elk vijf duels)
als grootste blokken.

VIJF regels gepubliceerd — de volle MAX_SHORTLIST van een zondag — en VIER ervan halen hun eigen
lat, op beide schalen. Dat is ongewoon veel: de afgelopen weken stond er doorgaans één of twee
boven de drempel en de rest op rangorde. Zie VIJF_REGELS_EN_VIER_HALEN_HUN_LAT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-18"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-18T04:13:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("A", "tmp-run/ra_oct18_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.015580, "
                "b=0.010084 over 4929 afgerekende gevallen, fitted_through 2026-10-17, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle vóór "
                "de analyse gedraaid (258 waarnemingen afgewikkeld, 5136 van 5181 compleet, 45 "
                "nog open). De fit VERHOOGT een kans over vrijwel de hele speelbare band "
                "(+0,3 pp op 50%, +0,5 pp op 70%) en verlaagt alleen onder ~35%; het ruwe model "
                "zei gemiddeld 33,333% en het gebeurde 33,333%. Bij alle VIJF de gepubliceerde "
                "regels staat de herijkte edge daardoor boven de ruwe. Bij VIER van de vijf "
                "staat `bet_beide` op TRUE — die halen hun lat op BEIDE schalen, en dat is "
                "ongewoon veel voor deze maand. Bij de vijfde (Başakşehir – Gaziantep FK) staat "
                "hij op FALSE omdat die regel zijn lat op geen van beide schalen haalt en op "
                "rangorde is gepubliceerd (§5b)."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TIEN van de eenentwintig competities uit de runlijst speelden, met 35 duels "
                "samen in het inzetvenster: Ligue 1 5, Eredivisie 5, Premier League 4, "
                "Serie A 4, La Liga 4, Danish Superliga 4, Super Lig 3, Ekstraklasa 3, "
                "Bundesliga 2 en Scottish Premiership 1. GEEN WEDSTRIJD, en dat is geen storing "
                "(§3 Stage 2): de Championship speelt dit weekend zaterdag en dinsdag, de "
                "Primeira Liga en de Belgian Pro League hebben hun ronde later in de week, en "
                "de drie Europese toernooien spelen 20 en 22 oktober. Alle zes die nul duels "
                "hebben zijn door een tweede bron bevestigd — zie "
                "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven — dat kostte Run A op 6 oktober vijf duels. "
                "Alle vijf zijn daarom langs BetExplorer gegaan "
                "(tmp-run/ra_oct18_cups.py) en alle vijf leveren teamparen op de fixturepagina "
                "(11, 8, 8, 26 en 16), dus geen van de drie faalmodi van die bron is opgetreden. "
                "NUL ervan valt in het inzetvenster: FA Cup 20.10. 19:45, League Cup 27.10. "
                "20:45, Coppa Italia 01.12. 21:00, KNVB Beker 27.10. 18:45 en DFB Pokal 27.10. "
                "18:00 (UK-tijd). Dat is het verschil met gisteren, toen de FA Cup 32 ties in "
                "het venster had die alle 32 op NONE uitkwamen; vandaag is er dus geen "
                "cupcheck nodig en geen enkele bekerwedstrijd in de analyse."),
            "VIER_VAN_DE_35_DUELS_HEBBEN_EEN_OMGEREKENDE_PLOEG": (
                "Alle vier gaan OMHOOG langs promotion.TIER2 en alle vier op een EIGEN GEMETEN "
                "divisiefactor, niet op POOLED_GAP: Racing Santander en Málaga (LaLiga2, gemeten "
                "paar SP1/SP2), Cambuur (Eerste Divisie, eigen meting 31 aug 2026) en Lyngby "
                "(Deense 1. Division, eigen meting 31 aug 2026 — de verdedigingsfactor is daar "
                "1.807 in plaats van de gepoolde 1.513). Alle vier vallen binnen het gemeten "
                "invoerbereik, dus conversion_in_range weigert vandaag geen enkele keer en er "
                "is GEEN duel op data_tier NONE. Lees de stand per selectie uit "
                "GapResult.direction, zoals §4 sinds 9 oktober eist; die tekst staat per "
                "wedstrijd in het veld `promovendi`. Een omgerekende ploeg levert per definitie "
                "LIGHT en dus de lat van 16,0 pp — nooit FULL, want de omrekening haalt de "
                "systematische fout eruit en niet de onzekerheid. Eén van de vier levert een "
                "regel: Osasuna – Racing Santander."),
            "GEEN_KRUIS_GRENSDUEL_EN_GEEN_DUEL_OP_NONE": (
                "De drie Europese toernooien spelen niet, dus scripts/interleague.py komt deze "
                "run niet aan de orde. En er is geen enkel duel op data_tier NONE: 31 duels op "
                "FULL (xG in beide seizoenen bij alle tien de competities) en 4 op LIGHT (de "
                "omgerekende ploegen hierboven). Dat is ongewoon — gisteren waren het twee op "
                "NONE plus 32 bekerties — en het komt doordat alle tien spelende competities xG "
                "bij Fotmob hebben en de vier promovendi alle vier binnen hun gemeten bereik "
                "vallen."),
            "DE_CAP_BINDT_NIET": (
                "35 duels op een zondagcap van 55 (ranking.max_deep_analyses, vr-zo), dus er is "
                "NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel. De datarijkdom "
                "liep van 5.0 (Kasımpaşa – Samsunspor, Celtic – Heart of Midlothian, Górnik "
                "Zabrze – Piast Gliwice) tot 7.5 (AFC Bournemouth – Sunderland, Leeds United – "
                "Manchester United) over de 35 duels; omdat er niets afviel is er geen 'laagste "
                "die het haalde' en geen 'hoogste die afviel' te noemen (§3 Stage 4). De "
                "context is voor alle 35 duels opgehaald, zoals §1c eist, en alle 35 hebben een "
                "contextblok zonder fout."),
            "VIJF_REGELS_EN_VIER_HALEN_HUN_LAT": (
                "MAX_SHORTLIST = 5 (zondag) en de lijst is vol. VIER regels halen hun EIGEN "
                "drempel, en alle vier ook op de ruwe schaal (`bet_beide` = TRUE): Juventus – "
                "Lazio BTTS nee +11,88 pp (FULL, lat 8,0; ruw +11,45), FC Twente – FC Utrecht "
                "Under 3.5 +11,03 pp (FULL, en als Under de VERZWAARDE lat van 10,0 uit poort "
                "9; ruw +10,63), Osasuna – Racing Santander Over 2.5 +17,40 pp (LIGHT, lat "
                "16,0; ruw +16,89) en Paris FC – Rennes Over 2.5 +9,80 pp (FULL, lat 8,0; ruw "
                "+9,33). De VIJFDE staat op rangorde: Başakşehir – Gaziantep FK Over 2.5 op "
                "+6,54 pp tegen een FULL-lat van 8,0, boven de NEAR-ondergrens van 3,0 die §5b "
                "als vloer gebruikt en met alle negen poorten open. Omdat er vier boven de "
                "drempel staan en vijf plekken zijn, is de DREMPEL vandaag geen afkapping (§5b "
                "stap 5): de rangorde vult de vijfde plek. Er is dus ook geen gekwalificeerde "
                "selectie die op `lijstlengte` afvalt. Vier van de vijf boven hun lat is veel "
                "voor deze maand — gisteren waren het twee van vijf — maar lees dat niet als "
                "een belofte: §1g heeft op 552 afgerekende gevallen gemeten dat er GEEN drempel "
                "op de herijkte edge bestaat die geld oplevert, en dat het rendement het "
                "slechtst is bij de hoogste geclaimde edge. MAX_LIGHT_IN_SHORTLIST = 2 bindt "
                "niet: er staat precies één LIGHT-regel in de lijst."),
            "ALLE_VIJF_DE_REGELS_ZIJN_EEN_DOELPUNTENMARKT_EN_EEN_STAAT_OP_UNDER": (
                "Over/Under levert vier regels en BTTS één; de uitkomstmarkten leveren er nul. "
                "Dat is GEEN inkoopartefact — de marktbalans-controle slaagt ruim (zie "
                "MARKTBALANS): negen van de negen inkoopbare competities kregen de volle bulk "
                "met zowel uitkomst- als doelpuntenmarkt, en er zijn 160 Over/Under-selecties "
                "doorgerekend tegen 159 Asian Handicap, 103 1X2, 58 BTTS, 37 Draw No Bet en 25 "
                "Double Chance — samen 542 selecties over 35 duels. De uitkomstmarkten dongen "
                "dus volop mee en selection_score koos deze vijf. ÉÉN van de vijf staat op de "
                "UNDER-kant (FC Twente – FC Utrecht), en §6g meet die kant op -16,5% over 76 "
                "picks tegen +10,6% voor Over. Dat staat bij die pick in `notes` en hoort ook in "
                "het dagrapport: het is geen slag om de arm maar de stand van zaken. Bij "
                "Juventus – Lazio is BTTS 'nee' de hoogst scorende uitdrukking van dezelfde "
                "mening; Under 2.5 stond daar op +10,59 pp met score 6,635 tegen 7,501 voor "
                "BTTS, dus de 0-of-1-bet-regel van §1 publiceert de BTTS en laat de Under "
                "liggen. Dat is dezelfde bevinding, twee keer uitgedrukt (§1a) en niet twee "
                "bevindingen."),
            "POORT_9_BINDT_EN_LAAT_EEN_UNDER_DOOR_OP_DE_VERZWAARDE_LAT": (
                "Zevende bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke selectie "
                "aangeroepen met today=2026-10-18. poort9_geblokkeerd is voor alle 35 duels "
                "leeg, en vandaag is dat voor het eerst deze week GEEN gevolg van de "
                "niet-monotonie die Run A op 16 en 17 oktober opschreef: FC Twente – FC Utrecht "
                "is een FULL-Under met +11,03 pp en haalt de verzwaarde lat van 10,0 pp gewoon "
                "(unders.check geeft passed=True met de reden 'Under met +11.03 pp, boven de "
                "verzwaarde lat van 10.0 pp'). De poort heeft dus niets tegengehouden omdat er "
                "niets in de band 8-10 pp op FULL stond, niet omdat hij de vraag niet kreeg. De "
                "reeks `doelpunten_onder` groeit vandaag niet; ze staat sinds 12 oktober op een "
                "handvol rijen en §6d eist er ~30, dus lees hem niet. Deze run verandert NIETS "
                "aan de poort — §1h legt vast dat een run dat nooit op eigen initiatief doet."),
            "POORT_8_HOUDT_NEGEN_SELECTIES_TEGEN": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), "
                "aangeroepen met today=2026-10-18 zodat het vervallen venster van 25 t/m 30 "
                "september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van "
                "geraden. NEGEN duels hebben een poort-8-rij op de herijkte schaal: Brighton & "
                "Hove Albion – Crystal Palace, Udinese – Lecce, Celta Vigo – Deportivo Alavés, "
                "Lorient – Monaco, Cambuur – AZ Alkmaar, FC Groningen – Ajax, Kasımpaşa – "
                "Samsunspor, Lyngby – Nordsjælland en FC København – AGF. poort8_ruw is leeg, "
                "want geen enkele kandidaat sneuvelde ALLEEN op de ruwe schaal — §1e eist dat "
                "dezelfde selectie nooit in beide reeksen belandt. De reeksen staan op 141 "
                "(`underdog`) en 17 (`underdog_ruw`) rijen en blijven twee populaties die nooit "
                "worden opgeteld."),
            "POORT_7_HOUDT_ZEVEN_DUELS_TEGEN_EN_DAT_IS_DE_GROOTSTE_POORT_VAN_DE_DAG": (
                "context.check sloot bij ZEVEN duels de poort — meer dan welke andere poort ook "
                "een eigen categorie oplevert, en ruim boven de twee van gisteren. VIER op de "
                "blessurelijst: Manchester United mist 34% van de selectiewaarde tegen 13% bij "
                "Leeds United (Luke Shaw, Kobbie Mainoo en Noussair Mazraoui alle drie "
                "twijfelgeval), Le Havre mist 34% tegen 17% bij Auxerre (Lionel Mpasi-Nzau en "
                "Elias Jelert tot eind oktober, Ayumu Seko geschorst), Angers mist 24% tegen 9% "
                "bij Marseille (Jordan Lefort geschorst, Usman Simbakoli tot eind oktober) en "
                "PEC Zwolle mist 20% tegen 7% bij Go Ahead Eagles (Filip Krastev en Younes "
                "Namli, beide dag-tot-dag). DRIE op de RUSTREGEL, en dat is het gevolg van de "
                "Europese week: Lyon had 3 dagen rust tegen 7 bij Nice, NEC Nijmegen 3 tegen 8 "
                "bij Fortuna Sittard en Real Madrid 4 tegen 6 bij Sevilla. §1c: de poort houdt "
                "alleen tegen en stelt my_prob niet bij — die drie duels zijn dus niet "
                "'slechter ingeschat' maar niet gepubliceerd."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [18.10. 08:00 NL, 19.10. 08:00 NL). "
                "Alle 35 duels stonden op de daglijst van 18 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 35 zijn playable: de "
                "vroegste aftrap is Górnik Zabrze – Piast Gliwice en PEC Zwolle – Go Ahead "
                "Eagles om 12:15 NL en de laatste Real Madrid – Sevilla om 21:00 NL. Er is dus "
                "geen enkel duel dat al was afgetrapt voordat de gebruiker kon inzetten, en "
                "geen carry-over-band."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob "
                "levert de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van "
                "de zestien competities met een fotmob_id zijn het eens, inclusief de zes die "
                "vandaag GEEN WEDSTRIJD hebben: 35 duels bij Fotmob, 35 bij BetExplorer, nul "
                "afwijkingen en geen enkele bron die faalde "
                "(tmp-run/ra_oct18_bevestiging.py)."),
            "NEGEN_VAN_DE_TIEN_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Negen van de tien spelende competities hebben een sportkey bij The Odds API. "
                "De SCOTTISH PREMIERSHIP heeft er geen, dus daar is BetExplorer de enige "
                "1X2-bron (§1a): het marktgemiddelde over 17 boeken, géén beste prijs, en dus "
                "systematisch een te lage edge — conservatief, maar niet vergelijkbaar met een "
                "duel waar de beste prijs wél bekend is. Dat is ook de reden dat Celtic – Heart "
                "of Midlothian maar DRIE selecties heeft (de drie 1X2-uitkomsten) tegen 11 tot "
                "21 elders, en dat er geen BTTS voor dat duel is gekocht. Het levert geen "
                "regel: de hoogste edge daar staat onder de drempel. De winst van de beste "
                "prijs boven het marktgemiddelde liep bij de negen andere competities van "
                "+4,38% (Serie A) tot +7,81% (Eredivisie) per selectie, gemeten over 34 duels."),
            "MARKTBALANS": (
                "Plafond suggest_cap(19237, 14) = 686 credits. split_budget(686, 9) geeft 9 "
                "spreads / 9 totals, en omdat 3 x 9 = 27 onder 686 blijft is de volle "
                "BULK-aanroep gedaan: h2h + spreads + totals voor alle negen inkoopbare "
                "competities, dus vijf van de zes markten in één keer. Daarna BTTS voor 29 van "
                "de 29 duels met een kandidaat-edge (§1a stap 2, de vereniging van beide "
                "schalen) — geen enkel duel is overgeslagen, want geen van de 29 viel buiten de "
                "spreads-respons. Totaal 56 van 686 credits (27 bulk + 29 BTTS), 19181 over. De "
                "marktbalans-controle slaagt RUIM: negen van de negen inkoopbare competities "
                "hebben zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt "
                "(O/U). Doorgerekend: 160 Over/Under, 159 Asian Handicap, 103 1X2, 58 BTTS, 37 "
                "Draw No Bet en 25 Double Chance, samen 542 selecties over alle 35 duels."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Voor 31 van de 35 duels gevonden (Celtic – Heart of "
                "Midlothian heeft geen sportkey en dus geen eigen 1X2; bij Kasımpaşa – "
                "Samsunspor, Başakşehir – Gaziantep FK en OB – Brøndby IF noteerde Pinnacle "
                "geen 1X2), gemiddelde Pinnacle-marge 3,75% tegen 6 à 10% bij de rest. "
                "Gemiddelde absolute afstand tussen het eigen model en het Pinnacle-oordeel: "
                "4,33 procentpunt. De grootste afwijkingen: FC København – AGF (-15,22 pp op de "
                "thuiszege, het enige duel waar het model de favoriet LAGER zet dan Pinnacle), "
                "Osasuna – Racing Santander (+14,68 pp) en NEC Nijmegen – Fortuna Sittard "
                "(+13,11 pp). Bij Paris FC – Rennes, dat wél een regel levert, staat het model "
                "+12,56 pp boven Pinnacle op de thuiszege — maar de gepubliceerde bet is daar "
                "een doelpuntenmarkt en niet de 1X2. HARDE GRENS §2/§4: dit getal zit NIET in "
                "my_prob en NIET in prob_sources; het is andermans lezing en marktafgeleid, en "
                "het hoort in de vergelijking."),
            "UNDERSTAT_DEKT_ZESTIEN_VAN_DE_NEGENTIEN_DUELS": (
                "Alle VIJF de Understat-competities speelden vandaag (Premier League, Serie A, "
                "La Liga, Bundesliga, Ligue 1), samen 19 duels, en 16 ervan hebben een tweede, "
                "onafhankelijk xG-model naast Fotmob. De drie die het niet hebben: Osasuna – "
                "Racing Santander en Málaga – Real Sociedad (promovendus, staat terecht niet in "
                "de Understat-tabel van 2025/2026) en Borussia Mönchengladbach – Hoffenheim "
                "(naamkoppeling). Understat ligt structureel ~0.13 xG per ploeg per duel hoger "
                "dan Fotmob (§4), dus er is uitsluitend genormaliseerd op het EIGEN "
                "competitiegemiddelde van Understat. Dat verschil gaat per §4 NIET in my_prob; "
                "het gaat als p_xg_understat het kalibratielogboek in."),
            "GEEN_VERPLAATSTE_WEDSTRIJD": (
                "context.check_venue is voor alle 35 duels gedraaid en relocated is overal "
                "False: elke thuisploeg speelt in haar eigen stadion. Dat is een controle die "
                "ook bij een open poort wordt gemeld (§1c)."),
            "OPSTELLINGEN": (
                "lineup_type: 28 duels op 'predicted' en 7 op 'lastStarting11'. Bevestigde "
                "elftallen (lineupType 'confirmed') zijn er om 04:10 NL bij geen enkel duel. "
                "Dat zit in de datarijkdom (§3 Stage 4) en niet in my_prob."),
            "VROEG_SEIZOEN_EN_DE_DEENSE_ROUTE": (
                "early_season_uplift geeft factor 1.1128, gepoold 1.1252 over 73 speeldagen in "
                "NEGEN competities. De DANISH SUPERLIGA is uit de pool gelaten en loopt via de "
                "route `lopend`: 11 van de 22 speeldagen gespeeld, dus op of boven "
                "SEASON_MATURE_SHARE, en dan meet lopend/vorig een echt niveauverschil tussen "
                "twee seizoenen in plaats van een tijdseffect binnen één seizoen (§3 Stage 5, "
                "league_level). Dat is een weggelaten waarneming en die hoort genoemd, net als "
                "een stille truncatie in Stage 4. De negen andere competities lopen via "
                "`vorig+uplift`."),
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
        s3 = json.load(open("tmp-run/ra_oct18_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct18_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct18_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct18_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct18_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

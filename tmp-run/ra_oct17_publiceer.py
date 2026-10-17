"""Run A 17 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct16_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TIEN van de eenentwintig competities uit de runlijst speelden, met 47 duels in het
inzetvenster: de volle Europese zaterdag, met de Championship (elf duels) en de Bundesliga (zes)
als grootste blokken.

VIJF regels gepubliceerd — de volle MAX_SHORTLIST van een zaterdag — en alle vijf uit de
doelpuntenmarkt. TWEE halen hun eigen lat (Strasbourg +10,02 en Villarreal +8,87 op een FULL-lat
van 8,0), de andere DRIE staan op rangorde. Zie VIJF_REGELS_TWEE_HALEN_HUN_LAT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-17"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-17T04:28:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("A", "tmp-run/ra_oct17_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.024508, "
                "b=0.015863 over 4671 afgerekende gevallen, fitted_through 2026-10-16, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle vóór "
                "de analyse gedraaid (63 waarnemingen afgewikkeld, 4878 van 4902 compleet, 24 "
                "nog open). De fit VERHOOGT een kans over vrijwel de hele speelbare band "
                "(+0,4 pp op 50%, +0,8 pp op 70%) en verlaagt alleen onder ~35%; het ruwe model "
                "zei gemiddeld 33,333% en het gebeurde 33,333%. Bij alle VIJF de gepubliceerde "
                "regels staat de herijkte edge daardoor BOVEN de ruwe, en bij alle vijf staat "
                "`bet_beide` op FALSE. Bij VIER daarvan omdat ze hun lat op geen van beide "
                "schalen halen; bij Strasbourg – Paris Saint-Germain om een andere reden, zie "
                "STRASBOURG_HAALT_POORT_9_HERIJKT_EN_NIET_RUW."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TIEN van de eenentwintig competities uit de runlijst speelden, met 47 duels "
                "samen in het inzetvenster: Championship 11, Bundesliga 6, Premier League 5, "
                "Scottish Premiership 5, La Liga 4, Super Lig 4, Serie A 3, Ligue 1 3, "
                "Eredivisie 3 en Ekstraklasa 3. Dit is de volle Europese zaterdag en de "
                "grootste rundag van deze maand. GEEN WEDSTRIJD, en dat is geen storing (§3 "
                "Stage 2): Primeira Liga, Belgian Pro League en Danish Superliga spelen dit "
                "weekend later, en de drie Europese toernooien hebben donderdag gespeeld."),
            "DE_FA_CUP_HEEFT_32_TIES_IN_HET_VENSTER_EN_ALLE_32_ZIJN_NONE": (
                "Dit is vandaag de grootste afweging en ze is GEMETEN en niet aangenomen. De "
                "FA Cup staat met 32 ties in het inzetvenster (vierde kwalificatieronde, "
                "aftrap 12:30 en 15:00 NL), gevonden via BetExplorer omdat de beker geen "
                "fotmob_id heeft en de daglijst haar dus niet kent — precies het gat dat Run A "
                "op 6 oktober vijf duels kostte. §4 ('In een beker ligt de basis per WEDSTRIJD') "
                "geeft de FA Cup via promotion.CUP_BASE de Premier League als basis, en een "
                "ploeg die daar niet in staat wordt één divisie omgerekend; staan beide ploegen "
                "in dezelfde lagere divisie, dan rekent het duel in die divisie door "
                "(shared_lower_division, keten drie diep: Championship, League One, League Two). "
                "Voor ALLE 32 ties geeft die functie None: deze ronde speelt zich af in de "
                "National League en daaronder, en de Engelse TIER2-keten houdt op bij League "
                "Two. Er is dus geen gemeten niveauverschil om te overbruggen en geen "
                "onafhankelijke kansinput op het niveau waarop gespeeld wordt: data_tier NONE "
                "voor alle 32, oftewel BUITEN DATADEKKING. Dat is exact wat prompts/run-a.md "
                "voor een lage-divisie bekerronde voorspelt, en het is ook de goede uitkomst "
                "voor de cap: 32 ties die MAX_DEEP_ANALYSES hadden kunnen vullen ten koste van "
                "beter gedocumenteerde competities. Nagegaan in tmp-run/ra_oct17_cupcheck.py; "
                "de vier andere bekers van de runlijst (League Cup, Coppa Italia, KNVB Beker, "
                "DFB Pokal) hebben hun eerstvolgende ronde buiten het venster (27.10, 01.12, "
                "27.10, 27.10)."),
            "ZEVENTIEN_VAN_DE_47_DUELS_HEBBEN_EEN_OMGEREKENDE_PLOEG": (
                "Het is vroeg in 2026/2027 en de promovendi staan er massaal in. ZESTIEN gaan "
                "OMHOOG langs promotion.TIER2: Hull City en Ipswich Town (Championship, gemeten "
                "paar E0/E1), Venezia (Serie B, I1/I2), Elversberg, Schalke 04 en Paderborn "
                "(2. Bundesliga, D1/D2), Troyes (Ligue 2, F1/F2), Cardiff City, Lincoln City en "
                "Bolton Wanderers (League One, E1/E2), ADO Den Haag en Willem II (Eerste "
                "Divisie, eigen meting 31 aug), Erzurumspor FK en Amed Sportif (1. Lig, eigen "
                "meting 31 aug), St. Johnstone (Championship SCO, SC0/SC1) en Śląsk Wrocław "
                "(I Liga, eigen meting 31 aug). ÉÉN gaat OMLAAG langs promotion.TIER1: West Ham "
                "United, uit de Premier League naar de Championship, met het gemeten fd_pair "
                "(E0,E1) x1.830/0.634. §4 waarschuwt dat de richting OMLAAG nog niet apart is "
                "gemeten; dat geldt voor het NEDERLANDSE paar dat op POOLED_GAP terugvalt en "
                "NIET voor het Engelse, dat gewoon bij football-data.co.uk staat. GEEN ENKELE "
                "omrekening van vandaag draait op POOLED_GAP — lees de stand per selectie uit "
                "GapResult.direction, zoals §4 sinds 9 oktober eist."),
            "TWEE_DUELS_OP_NONE_EN_BEIDE_OM_EEN_GEMETEN_REDEN": (
                "Fulham – Hull City en Erzurumspor FK – Eyüpspor zijn de enige twee duels op "
                "data_tier NONE, en in beide gevallen is het een GEMETEN poort en geen gat. De "
                "relatieve verdediging van Hull City is 1.102 en het gemeten invoerbereik van "
                "het Engelse paar (E0/E1 omhoog, n=33) loopt tot 1.022; de relatieve "
                "verdediging van Erzurumspor FK is 0.483 tegen een ondergrens van 0.497 (eigen "
                "meting 31 aug 2026, Süper Lig/1. Lig, n=27). conversion_in_range weigert dus "
                "tweemaal, en dat is precies de Coventry-val waarvoor die poort bestaat (§4): "
                "een promovendus met een verdediging buiten alles wat ooit is gemeten, is geen "
                "geval om op te extrapoleren. Erzurumspor mist de ondergrens met 0,014 — een "
                "grensgeval, en dat hoort er zo bij te staan. Nul van de zes markten is voor "
                "deze twee doorgerekend, zoals §6b-5b voor tier NONE voorschrijft."),
            "DE_CAP_BINDT_NIET_MAAR_HET_WAS_DICHTBIJ": (
                "47 duels op een zaterdagcap van 55 (ranking.max_deep_analyses, vr-zo), dus er "
                "is NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel. Dat het niet "
                "bindt is wél de uitkomst van de datadekkingspoort en niet van ruimte: met de "
                "32 FA Cup-ties erbij waren het 79 kandidaten geweest en had de cap 24 duels "
                "weggesneden. De datarijkdom liep van 5.0 tot 7.5 over de 47 duels; omdat er "
                "niets afviel is er geen 'laagste die het haalde' en geen 'hoogste die afviel' "
                "te noemen (§3 Stage 4). De context is voor alle 47 duels opgehaald, ook voor "
                "de twee op NONE, zoals §1c eist."),
            "VIJF_REGELS_TWEE_HALEN_HUN_LAT": (
                "MAX_SHORTLIST = 5 (zaterdag) en de lijst is vol. TWEE regels halen hun eigen "
                "drempel: Strasbourg – Paris Saint-Germain Under 3.5 op +10,02 pp en "
                "Villarreal – Elche Over 3 op +8,87 pp, beide tegen een FULL-lat van 8,0. De "
                "andere DRIE staan op rangorde: Union Berlin – Borussia Dortmund Under 3.5 op "
                "+7,64 pp (FULL, lat 8,0), Motor Lublin – Śląsk Wrocław Over 2.5 op +12,29 pp "
                "(LIGHT, lat 16,0) en Roma – Genoa Under 3.5 op +5,76 pp (FULL, lat 8,0). Alle "
                "vijf staan boven de NEAR-ondergrens die §5b als vloer gebruikt (3,0 op FULL, "
                "6,0 op LIGHT) en bij alle vijf staan de overige poorten open. "
                "MAX_LIGHT_IN_SHORTLIST = 2 bindt NIET: er staat precies één LIGHT-regel in de "
                "lijst. Er is ook geen gekwalificeerde selectie die op de lijstlengte afvalt — "
                "er waren er niet meer dan vijf. Lees deze lijst als 'het beste van vandaag' en "
                "niet als een gevonden voordeel; dat is letterlijk waarvoor §5b het label per "
                "regel eist."),
            "STRASBOURG_HAALT_POORT_9_HERIJKT_EN_NIET_RUW": (
                "De hoogst-rangschikkende regel van de dag is een FULL-Under die poort 9 op de "
                "HERIJKTE schaal haalt (+10,02 pp tegen de verzwaarde lat van 10,0) en op de "
                "RUWE schaal niet (+9,44 pp). Dat is de spiegel van `herijking`: sinds de fit "
                "van 20 september een kans VERHOOGT in plaats van verlaagt, kan een selectie de "
                "herijkte lat halen en de ruwe missen — precies het geval waarvoor §5a "
                "`bet_beide` als controle heeft neergezet in plaats van als aanname. §1 en §5a "
                "laten de poorten op de HERIJKTE my_prob binden, dus deze selectie is "
                "publiceerbaar en is gepubliceerd; `bet_beide` staat op FALSE en dat staat in "
                "`notes`. De analyse boekt de wedstrijd daarnaast als near_miss met "
                "failed_gate = herijking_omgekeerd, en omdat dezelfde selectie nu een echte bet "
                "is wordt die rij door het publiceren omgezet in near_miss_gepubliceerd — hij "
                "gaat dus NIET nog eens als schaduwpick het logboek in. De reeks "
                "`herijking_omgekeerd` staat op 3 afgewikkelde gevallen; §6d eist er ~30, dus "
                "lees hem niet. Deze run verandert hier NIETS aan."),
            "ALLE_VIJF_DE_REGELS_ZIJN_EEN_DOELPUNTENMARKT_EN_DRIE_STAAN_OP_UNDER": (
                "Over/Under levert alle vijf de regels, en dat is GEEN inkoopartefact — de "
                "marktbalans-controle slaagt ruim (zie MARKTBALANS): negen van de negen "
                "inkoopbare competities kregen de volle bulk met zowel uitkomst- als "
                "doelpuntenmarkt, en er zijn 190 Over/Under-selecties doorgerekend tegen 173 "
                "Asian Handicap, 132 1X2, 66 BTTS, 36 Draw No Bet en 26 Double Chance — samen "
                "623 selecties. De uitkomstmarkten dongen dus volop mee en selection_score koos "
                "deze vijf. DRIE van de vijf staan op de UNDER-kant, en §6g meet die kant op "
                "-16,5% over 76 picks tegen +10,6% voor Over. Dat staat bij elke betrokken pick "
                "in `notes` en hoort ook in het dagrapport: het is geen slag om de arm maar de "
                "stand van zaken."),
            "POORT_9_HOUDT_NIETS_TEGEN_EN_DE_NIET_MONOTONIE_VAN_GISTEREN_STAAT_ER_WEER": (
                "Zesde bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke selectie "
                "aangeroepen met today=2026-10-17. poort9_geblokkeerd is voor alle 47 duels "
                "leeg. Bij Motor Lublin is dat het besluit van 12 oktober (de poort geldt alleen "
                "op FULL); bij Union Berlin (+7,64 pp) en Roma (+5,76 pp) is het de VORM van de "
                "poort: unders.check geeft passed=True met de reden 'onder de gewone drempel "
                "van 8,0 pp, dus edge is de bindende poort en niet poort 9', terwijl `edge` "
                "onder §5b geen poort meer is maar een afkapping. Gevolg, en dit is precies de "
                "bevinding die Run A op 16 oktober ook opschreef: een FULL-Under met 8,5 pp "
                "WORDT geblokkeerd en twee FULL-Unders met 7,64 en 5,76 pp niet, terwijl die "
                "minder voordeel claimen. Dat is niet-monotoon, het is nu twee dagen op rij "
                "zichtbaar, en deze run verandert er NIETS aan — §1h en §1e leggen vast dat een "
                "run een poort nooit op eigen initiatief verzet. Het staat als bevinding in het "
                "runrapport."),
            "POORT_8_HOUDT_VEERTIEN_SELECTIES_TEGEN": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), "
                "aangeroepen met today=2026-10-17 zodat het vervallen venster van 25 t/m 30 "
                "september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van "
                "geraden. VEERTIEN duels hebben een poort-8-rij op de herijkte schaal: Venezia, "
                "Espanyol, Real Betis, Valencia, Hamburger SV, Werder Bremen, Troyes, Millwall, "
                "Bristol City, Norwich City, West Bromwich Albion, Wrexham, ADO Den Haag en "
                "Cracovia. poort8_ruw is leeg, want geen enkele kandidaat sneuvelde ALLEEN op de "
                "ruwe schaal — §1e eist dat dezelfde selectie nooit in beide reeksen belandt. De "
                "twee sterkste rijen van de RUWE dagranglijst zijn poort-8-rijen (Espanyol +0.75 "
                "op +13,78 pp en Preston North End +0.75 op +13,64 pp), dus de poort kost "
                "vandaag de kop van die lijst. De reeksen staan op 132 (`underdog`) en 17 "
                "(`underdog_ruw`) rijen en blijven twee populaties die nooit worden opgeteld."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [17.10. 08:00 NL, 18.10. 08:00 NL). "
                "Alle 47 duels stonden op de daglijst van 17 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 47 zijn playable: de "
                "vroegste aftrap is Erzurumspor FK – Eyüpspor om 12:30 NL en de laatste "
                "Valencia – Athletic Club, Sparta Rotterdam – Willem II en Dundee FC – Rangers "
                "om 21:00 NL. Er is dus geen enkel duel dat al was afgetrapt voordat de "
                "gebruiker kon inzetten, en geen carry-over-band."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob levert "
                "de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van de "
                "zestien competities met een fotmob_id zijn het eens, inclusief de zes die "
                "vandaag GEEN WEDSTRIJD hebben: 47 duels bij Fotmob, 47 bij BetExplorer, nul "
                "afwijkingen. De Ekstraklasa gaf bij de eerste poging een TimeoutError en is "
                "apart opnieuw opgevraagd (tmp-run/ra_oct17_bev_pol.py); dat is een ONTBREKENDE "
                "meting en geen afwijking, en het verschil hoort opgeschreven in plaats van als "
                "'15 van 16' te worden afgedaan. Na de hermeting: 3 bij Fotmob, 3 bij "
                "BetExplorer."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven (dat kostte Run A op 6 oktober vijf duels). "
                "Alle vijf zijn langs BetExplorer gegaan en leveren teamparen op de "
                "fixturepagina (32, 8, 8, 26 en 16). De FA Cup valt WEL in het venster met 32 "
                "ties — zie DE_FA_CUP_HEEFT_32_TIES_IN_HET_VENSTER_EN_ALLE_32_ZIJN_NONE. De "
                "andere vier hebben hun eerstvolgende ronde buiten het venster: League Cup "
                "27.10. 20:45, Coppa Italia 01.12. 21:00, KNVB Beker 27.10. 18:45 en DFB Pokal "
                "27.10. 18:00 (UK-tijd). Voor die vier dus GEEN WEDSTRIJD, met een tweede bron "
                "eronder."),
            "NEGEN_VAN_DE_TIEN_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Negen van de tien spelende competities hebben een sportkey bij The Odds API. "
                "De SCOTTISH PREMIERSHIP heeft er geen, dus daar is BetExplorer de enige "
                "1X2-bron (§1a): het marktgemiddelde over een niet-herleidbaar aantal boeken, "
                "géén beste prijs, en dus systematisch een te lage edge — conservatief, maar "
                "niet vergelijkbaar met een duel waar de beste prijs wél bekend is. Dat is ook "
                "de reden dat die vijf duels maar DRIE selecties per duel hebben (de drie "
                "1X2-uitkomsten) tegen 11 tot 19 elders, en dat er geen BTTS voor St. Johnstone "
                "– Dundee United is gekocht. Geen van de vijf levert een regel. De winst van de "
                "beste prijs boven het marktgemiddelde liep bij de negen andere competities van "
                "+5,59% (Ekstraklasa) tot +10,52% (Eredivisie) per selectie, gemeten over 40 "
                "duels."),
            "MARKTBALANS": (
                "Plafond suggest_cap(19371, 15) = 645 credits. split_budget(645, 9) geeft 9 "
                "spreads / 9 totals, en omdat 3 x 9 = 27 onder 645 blijft is de volle "
                "BULK-aanroep gedaan: h2h + spreads + totals voor alle negen inkoopbare "
                "competities, dus vijf van de zes markten in één keer. Daarna BTTS voor 33 van "
                "de 34 duels met een kandidaat-edge (§1a stap 2, de vereniging van beide "
                "schalen); het 34e is St. Johnstone – Dundee United, dat geen sportkey heeft. "
                "Totaal 60 van 645 credits, 19311 over. De marktbalans-controle slaagt RUIM: "
                "negen van de negen inkoopbare competities hebben zowel een uitkomstmarkt (1X2, "
                "AH, DNB, DC) als een doelpuntenmarkt (O/U). Doorgerekend: 190 Over/Under, 173 "
                "Asian Handicap, 132 1X2, 66 BTTS, 36 Draw No Bet en 26 Double Chance, samen "
                "623 selecties over 45 duels (de twee op NONE zijn niet doorgerekend)."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Voor 40 van de 47 duels gevonden (de zes Schotse duels "
                "en Erzurumspor FK niet, en daar is ook geen eigen 1X2), gemiddelde "
                "Pinnacle-marge 3,79% tegen 6 à 10% bij de rest. Gemiddelde absolute afstand "
                "tussen het eigen model en het Pinnacle-oordeel: 4,10 procentpunt. De grootste "
                "afwijkingen: Wrexham – Preston North End (-14,9 pp op de thuiszege), Norwich "
                "City – Portsmouth (-11,9 pp) en Derby County – Stoke City (+10,68 pp; precies "
                "het duel dat poort 7 heeft tegengehouden). HARDE GRENS §2/§4: dit getal zit "
                "NIET in my_prob en NIET in prob_sources; het is andermans lezing en "
                "marktafgeleid, en het hoort in de vergelijking."),
            "UNDERSTAT_DEKT_DERTIEN_VAN_DE_EENENTWINTIG_DUELS": (
                "Alle VIJF de Understat-competities speelden vandaag (Premier League, Serie A, "
                "La Liga, Bundesliga, Ligue 1), samen 21 duels, en 13 ervan hebben een tweede, "
                "onafhankelijk xG-model naast Fotmob. De acht die het niet hebben zijn de duels "
                "met een promovendus: die staat terecht niet in de Understat-tabel van "
                "2025/2026. Understat ligt structureel ~0.13 xG per ploeg per duel hoger dan "
                "Fotmob (§4), dus er is uitsluitend genormaliseerd op het EIGEN "
                "competitiegemiddelde van Understat. Dat verschil gaat per §4 NIET in my_prob; "
                "het gaat als p_xg_understat het kalibratielogboek in, waar over enkele weken "
                "te meten is welk xG-model beter voorspelt."),
            "GEEN_VERPLAATSTE_WEDSTRIJD": (
                "context.check_venue is voor alle 47 duels gedraaid en relocated is overal "
                "False: elke thuisploeg speelt in haar eigen stadion. Dat is een controle die "
                "ook bij een open poort wordt gemeld (§1c)."),
            "OPSTELLINGEN": (
                "lineup_type: 24 duels op 'predicted' en 23 op 'lastStarting11'. De vroege "
                "aftrappen (12:30 tot 14:00 NL) hebben hun voorspelde elftal al, de late nog "
                "niet; bevestigde elftallen (lineupType 'confirmed') zijn er om 04:30 NL bij "
                "geen enkel duel. Dat zit in de datarijkdom (§3 Stage 4) en niet in my_prob."),
            "POORT_7_HOUDT_TWEE_DUELS_TEGEN": (
                "context.check sloot bij twee duels de poort, en in beide gevallen op de "
                "blessurelijst: Derby County mist 51% van de selectiewaarde tegen 5% bij Stoke "
                "City (Sondre Klingen Langås tot begin januari, Max Johnston en Eiran Cashin "
                "tot eind oktober) en Alanyaspor mist 40% tegen 19% bij Fenerbahçe (Maestro, "
                "twijfelgeval). Dat zijn allebei ruime overschrijdingen van de drempel van 10 "
                "procentpunt verschil. Derby County – Stoke City is bovendien de vierde regel "
                "van de RUWE dagranglijst (+11,22 pp op Derby +0.25), dus de poort kost daar "
                "een kandidaat die het anders had gehaald. §1c: de poort houdt alleen tegen en "
                "stelt my_prob niet bij."),
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
        s3 = json.load(open("tmp-run/ra_oct17_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct17_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct17_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct17_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct17_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

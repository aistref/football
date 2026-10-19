"""Run A 19 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct18_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. ZEVEN van de eenentwintig competities uit de runlijst speelden, met 8 duels in het
inzetvenster: de maandag na het weekend, met de Serie A (twee duels) als enige competitie met
meer dan één wedstrijd.

DRIE regels gepubliceerd — de volle MAX_SHORTLIST van een maandag — en ÉÉN ervan haalt zijn
eigen lat. Zie DRIE_REGELS_EN_EEN_HAALT_ZIJN_LAT.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-19"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-19T04:34:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("A", "tmp-run/ra_oct19_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.019514, "
                "b=0.012623 over 5172 afgerekende gevallen, fitted_through 2026-10-18, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle vóór "
                "de analyse gedraaid (234 waarnemingen afgewikkeld, 5379 van 5403 compleet, 24 "
                "nog open) en de analyse daarna OPNIEUW gedraaid, want de eerste doorloop stond "
                "nog op fitted_through 2026-10-17. De fit VERHOOGT een kans over vrijwel de hele "
                "speelbare band (+0,3 pp op 50%, +0,6 pp op 70%) en verlaagt alleen onder ~35%; "
                "het ruwe model zei gemiddeld 33,333% en het gebeurde 33,333%. Bij alle DRIE de "
                "gepubliceerde regels staat de herijkte edge daardoor boven de ruwe. Bij ÉÉN van "
                "de drie staat `bet_beide` op TRUE (Trabzonspor – Beşiktaş); bij de twee andere "
                "op FALSE, want die halen hun lat op geen van beide schalen en zijn op rangorde "
                "gepubliceerd (§5b)."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ZEVEN van de eenentwintig competities uit de runlijst speelden, met 8 duels "
                "samen in het inzetvenster: Serie A 2 en Premier League, La Liga, Primeira "
                "Liga, Super Lig, Danish Superliga en Ekstraklasa elk 1. Dat is een MAANDAG na "
                "een volle speelronde, en de kleinste runlijstdag sinds 13 oktober. GEEN "
                "WEDSTRIJD, en dat is geen storing (§3 Stage 2): de Bundesliga en de Ligue 1 "
                "spelen hun volgende ronde op 1 november, de Championship op 23 oktober, de "
                "Eredivisie en de Belgian Pro League op 23 oktober, de Scottish Premiership op "
                "24 oktober, en de drie Europese toernooien op 21 en 22 oktober. Alle negen die "
                "nul duels hebben zijn door een tweede bron bevestigd — zie "
                "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON."),
            "DE_VIJF_BEKERS_SPELEN_NIET_EN_DAT_IS_GEMETEN": (
                "De vijf bekers van de runlijst hebben geen fotmob_id in coverage.json, dus "
                "runwindow kan ze niet filteren en 'niet in de daglijst' mag voor hen nooit als "
                "GEEN WEDSTRIJD worden opgeschreven — dat kostte Run A op 6 oktober vijf duels. "
                "Alle vijf zijn daarom langs BetExplorer gegaan (tmp-run/ra_oct19_cups.py) en "
                "alle vijf leveren teamparen op de fixturepagina (11, 8, 8, 26 en 16), dus geen "
                "van de drie faalmodi van die bron is opgetreden. NUL ervan valt in het "
                "inzetvenster: de FA Cup heeft ELF replays op 'Tomorrow 19:45' UK — dat is "
                "20 oktober 20:45 NL en dus de run van MORGEN, niet deze — en League Cup, KNVB "
                "Beker en DFB Pokal staan op 27.10. (20:45, 18:45 en 18:00 UK), Coppa Italia op "
                "01.12. 21:00. Alle elf FA Cup-rijen zijn op het label nagekeken: er staat geen "
                "enkele in de band 00:00-07:00 UK van 20 oktober, de band die wél bij deze run "
                "zou horen. Zie OPENSTAAND_LABEL_TOMORROW voor wat daar niettemin aan "
                "ontbreekt."),
            "OPENSTAAND_LABEL_TOMORROW": (
                "Het venstersfilter in ra_oct19_cups.py vergelijkt op 'Today', '19.10.' en "
                "'20.10.' en kent het label 'Tomorrow' NIET, terwijl BetExplorer de dag ná de "
                "pagina-datum zo labelt in plaats van met een datum. Vandaag kost dat niets — "
                "alle elf FA Cup-rijen staan op 'Tomorrow 19:45' en vallen op elke lezing "
                "buiten het venster — maar een bekerduel op 'Tomorrow 06:00' zou stil zijn "
                "weggevallen. Dat is dezelfde stille faalvorm als §6b-5b beschrijft. Het is met "
                "de hand gecontroleerd in plaats van met code, en het hoort in de code; "
                "ra_oct19_bevestiging.py doet het al wél goed (regel 31). Vastgelegd als "
                "actiepunt voor de run van morgen."),
            "TWEE_VAN_DE_8_DUELS_HEBBEN_EEN_OMGEREKENDE_PLOEG": (
                "Beide gaan OMHOOG langs promotion.TIER2 en beide op een GEMETEN divisiefactor "
                "van football-data.co.uk, niet op POOLED_GAP: Coventry City (Championship, paar "
                "E0/E1) en Monza (Serie B, paar I1/I2). Beide vallen binnen het gemeten "
                "invoerbereik, dus conversion_in_range weigert vandaag geen enkele keer en er "
                "is GEEN duel op data_tier NONE. Lees de stand per selectie uit "
                "GapResult.direction, zoals §4 sinds 9 oktober eist; die tekst staat per "
                "wedstrijd in het veld `promovendi`. Een omgerekende ploeg levert per definitie "
                "LIGHT en dus de lat van 16,0 pp — nooit FULL, want de omrekening haalt de "
                "systematische fout eruit en niet de onzekerheid. Eén van de twee levert een "
                "regel: Monza – Cagliari."),
            "GEEN_KRUIS_GRENSDUEL_EN_GEEN_DUEL_OP_NONE": (
                "De drie Europese toernooien spelen niet (UCL 21 okt, UEL en UECL 22 okt), dus "
                "scripts/interleague.py komt deze run niet aan de orde. En er is geen enkel "
                "duel op data_tier NONE: 6 duels op FULL (xG in beide seizoenen bij alle zeven "
                "competities) en 2 op LIGHT (de omgerekende ploegen hierboven)."),
            "DE_CAP_BINDT_NIET": (
                "8 duels op een maandagcap van 40 (ranking.max_deep_analyses, ma-do), dus er is "
                "NIETS afgekapt en de dekkingstabel heeft geen AFGEKAPT-regel. De datarijkdom "
                "liep van 5,0 (Trabzonspor – Beşiktaş) tot 6,0 (vijf duels) over de 8 duels; "
                "omdat er niets afviel is er geen 'laagste die het haalde' en geen 'hoogste die "
                "afviel' te noemen (§3 Stage 4). De context is voor alle 8 duels opgehaald, "
                "zoals §1c eist, en alle 8 hebben een contextblok zonder fout."),
            "DRIE_REGELS_EN_EEN_HAALT_ZIJN_LAT": (
                "MAX_SHORTLIST = 3 (maandag) en de lijst is vol. ÉÉN regel haalt zijn EIGEN "
                "drempel, en ook op de ruwe schaal (`bet_beide` = TRUE): Trabzonspor – Beşiktaş "
                "Draw No Bet op Beşiktaş +9,49 pp (FULL, lat 8,0; ruw +9,00). De TWEE andere "
                "staan op rangorde: Viborg – FC Midtjylland BTTS nee op +5,35 pp tegen een "
                "FULL-lat van 8,0 (boven de NEAR-ondergrens van 3,0 die §5b als vloer gebruikt) "
                "en Monza – Cagliari BTTS nee op +7,18 pp tegen een LIGHT-lat van 16,0 (boven "
                "de NEAR-ondergrens van 6,0). Alle drie hebben alle negen poorten open. Omdat "
                "er maar één boven de drempel staat en er drie plekken zijn, is de DREMPEL "
                "vandaag geen afkapping (§5b stap 5): de rangorde vult plek 2 en 3. Er is dus "
                "geen gekwalificeerde selectie die op `lijstlengte` afvalt. Lees de twee "
                "rangorderegels niet als een gevonden voordeel: §1g heeft op 552 afgerekende "
                "gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die geld "
                "oplevert, en dat het rendement het slechtst is bij de hoogste geclaimde edge. "
                "MAX_LIGHT_IN_SHORTLIST = 2 bindt niet: er staat precies één LIGHT-regel in de "
                "lijst."),
            "TWEE_VAN_DE_DRIE_REGELS_ZIJN_BTTS_NEE_EN_GEEN_ENKELE_IS_EEN_UNDER": (
                "BTTS levert twee regels en Draw No Bet één; Over/Under, 1X2, Asian Handicap en "
                "Double Chance leveren er nul. Dat is GEEN inkoopartefact — de "
                "marktbalans-controle slaagt ruim (zie MARKTBALANS): zeven van de zeven "
                "inkoopbare competities kregen de volle bulk met zowel uitkomst- als "
                "doelpuntenmarkt, en er zijn 40 Over/Under-selecties doorgerekend tegen 32 "
                "Asian Handicap, 24 1X2, 16 BTTS, 12 Draw No Bet en 6 Double Chance — samen 130 "
                "selecties over 8 duels. De uitkomstmarkten dongen dus volop mee en "
                "selection_score koos deze drie. GEEN ENKELE regel staat op de Over/Under "
                "Under-kant, waar §6g de scheefstand meet (Under 76 picks op -16,5% tegen Over "
                "62 picks op +10,6%) — voor het eerst deze week. Dat de twee rangorderegels "
                "BTTS 'nee' zijn is wél dezelfde richting: §1h legt vast dat BTTS 'nee' per "
                "besluit van 11 oktober BUITEN poort 9 blijft omdat 15 afgewikkelde BTTS-picks "
                "in beide richtingen samen geen meting zijn. Lees die twee regels dus met dat "
                "voorbehoud: ze zitten in de markt-en-kant die vermoedelijk dezelfde vormfout "
                "deelt, en er is geen rem op. Dit is het eerste wat opnieuw bekeken hoort te "
                "worden zodra de BTTS-reeks ~30 haalt."),
            "POORT_9_BINDT_EN_HEEFT_VANDAAG_NIETS_TE_TOETSEN": (
                "Achtste bindende dag (unders.BINDS_FROM = 2026-10-12, §1h), voor elke selectie "
                "aangeroepen met today=2026-10-19. poort9_geblokkeerd is voor alle 8 duels "
                "leeg, en vandaag is dat omdat er GEEN ENKELE FULL-Under in de band 8-10 pp "
                "stond — de band waarin de poort als enige bindt. De 40 doorgerekende "
                "Over/Under-selecties leverden geen Under op die de rangorde haalde. De reeks "
                "`doelpunten_onder` groeit vandaag dus niet; ze staat sinds 12 oktober op een "
                "handvol rijen en §6d eist er ~30, dus lees hem niet. Deze run verandert NIETS "
                "aan de poort — §1h legt vast dat een run dat nooit op eigen initiatief doet."),
            "POORT_8_HOUDT_TWEE_SELECTIES_TEGEN_EN_DIE_TWEE_VOEREN_DE_RUWE_LIJST_AAN": (
                "De lichte vorm bindt (ondergrens sides.UNDERDOG_FLOOR = 0,35; §1e), "
                "aangeroepen met today=2026-10-19 zodat het vervallen venster van 25 t/m 30 "
                "september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen in plaats van "
                "geraden. TWEE duels hebben een poort-8-rij op de herijkte schaal: Tottenham "
                "Hotspur – Coventry City (Coventry City +1, de markt geeft de promovendus 15,7% "
                "tegen 63,5%) en Braga – Gil Vicente (Gil Vicente +1, 15,6% tegen 60,5% volgens "
                "Pinnacle). poort8_ruw is leeg, want geen enkele kandidaat sneuvelde ALLEEN op "
                "de ruwe schaal — §1e eist dat dezelfde selectie nooit in beide reeksen "
                "belandt. EN LET OP WAT DAT BETEKENT VOOR DE RUWE LIJST: diezelfde twee duels "
                "staan op plek 1 en 3 van de ruwe top drie (Coventry City +1.5 @1.67 met +14,52 "
                "pp en Gil Vicente +1 @1.8428 met +8,18 pp). De routine zou vandaag zonder deze "
                "poort dus twee van de drie regels op een underdog-handicap hebben gezet. Dat "
                "is precies de groep waarvan §1e op uitkomsten heeft gemeten dat het model er "
                "structureel naast zit (z = -3,14 over 89 gevallen). De reeksen staan op 143 "
                "(`underdog`) en 17 (`underdog_ruw`) rijen en blijven twee populaties die nooit "
                "worden opgeteld."),
            "POORT_7_HOUDT_EEN_DUEL_TEGEN_EN_DAT_DUEL_LEVERT_ALSNOG_EEN_REGEL": (
                "context.check sloot bij ÉÉN duel de poort: Monza – Cagliari, waar MONZA 36% "
                "van de selectiewaarde mist tegen 11% bij Cagliari — Jan Ziólkowski "
                "(blessure, terug eind oktober), Lorenzo Lucchesi (schorsing, terug half "
                "oktober) en Idrissa Touré (blessure, weer in training). De hoogst scorende "
                "selectie daar was 1X2 op een Monza-zege (+12,76 pp op de xG-methode) en die is "
                "geblokkeerd. DAT HETZELFDE DUEL TOCH EEN REGEL LEVERT is geen omzeiling maar "
                "§1c zoals die is opgeschreven: de poort staat per ontwerp OPEN bij side = None "
                "(Over/Under, BTTS, gelijkspel), omdat er dan geen kant is om te benadelen en "
                "in welke richting ontbrekende spelers een TOTAAL verschuiven zonder meting "
                "niet te zeggen is. De gepubliceerde regel is BTTS 'nee' — een totaal, geen "
                "kant. Het is eerlijk om te noemen dat de richting hier wel plausibel oogt (een "
                "uitgedunde ploeg scoort eerder niet), maar §1c en §4 verbieden een getal te "
                "verzinnen waarvoor geen meting bestaat, en §1c meet op 147 wedstrijden dat er "
                "van het beschikbaarheidsverschil geen effect te vinden is. De poort houdt dus "
                "alleen tegen en stelt my_prob niet bij."),
            "INZETVENSTER": (
                "runwindow.matches_for_run met het venster [19.10. 08:00 NL, 20.10. 08:00 NL). "
                "Alle 8 duels stonden op de daglijst van 19 oktober (source_day = DAY, geen "
                "enkel duel uit de band 00:00-08:00 van morgen) en alle 8 zijn playable: de "
                "vroegste aftrap is Monza – Cagliari om 18:30 NL en de laatste Braga – Gil "
                "Vicente om 21:15 NL. Er is dus geen enkel duel dat al was afgetrapt voordat de "
                "gebruiker kon inzetten, en geen carry-over-band."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1, bevestiging door een tweede methode, op de vraag wélke wedstrijden er zijn "
                "— de duurste fouten van oktober zaten daar en niet in de analyse. Fotmob "
                "levert de daglijst, BetExplorer de fixturepagina per competitie. ZESTIEN van "
                "de zestien competities met een fotmob_id zijn het eens, inclusief de negen die "
                "vandaag GEEN WEDSTRIJD hebben: 8 duels bij Fotmob, 8 bij BetExplorer, nul "
                "afwijkingen en geen enkele bron die faalde "
                "(tmp-run/ra_oct19_bevestiging.py)."),
            "ALLE_ZEVEN_SPELENDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Alle zeven spelende competities hebben een sportkey bij The Odds API, dus er "
                "is deze run GEEN enkel duel waar BetExplorer de enige 1X2-bron is en de edge "
                "systematisch te laag uitvalt (§1a). Dat is anders dan gisteren, toen de "
                "Scottish Premiership daarin viel. De winst van de beste prijs boven het "
                "marktgemiddelde liep van +4,46% (Wisła Płock – Radomiak Radom) tot +7,24% "
                "(Viborg – FC Midtjylland) per selectie, gemeten over alle 8 duels."),
            "MARKTBALANS": (
                "Plafond suggest_cap(19131, 13) = 735 credits. split_budget(735, 7) geeft 7 "
                "spreads / 7 totals, en omdat 3 x 7 = 21 onder 735 blijft is de volle "
                "BULK-aanroep gedaan: h2h + spreads + totals voor alle zeven inkoopbare "
                "competities, dus vijf van de zes markten in één keer. Daarna BTTS voor 8 van "
                "de 8 duels met een kandidaat-edge (§1a stap 2, de vereniging van beide "
                "schalen) — geen enkel duel is overgeslagen, want geen van de 8 viel buiten de "
                "spreads-respons. Totaal 29 van 735 credits (21 bulk + 8 BTTS), 19102 over. De "
                "marktbalans-controle slaagt RUIM: zeven van de zeven inkoopbare competities "
                "hebben zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt "
                "(O/U), en alle 8 duels hebben alle ZES markten. Doorgerekend: 40 Over/Under, "
                "32 Asian Handicap, 24 1X2, 16 BTTS, 12 Draw No Bet en 6 Double Chance, samen "
                "130 selecties over alle 8 duels."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stage 5 stap 2. Geschreven voorspellingen zijn grotendeels onbereikbaar (§3 "
                "Stage 5, meting 20 sep 2026: Forebet 403, Pinnacle-artikelen 404, Matchbook "
                "530). Wat er wél is, is de prijs van Pinnacle apart, de-vigd — het scherpste "
                "publieke expertoordeel. Voor ALLE 8 duels gevonden, gemiddelde Pinnacle-marge "
                "3,81% tegen 6 à 10% bij de rest. Gemiddelde absolute afstand tussen het eigen "
                "model en het Pinnacle-oordeel: 6,35 procentpunt — ruim boven de 4,33 van "
                "gisteren, en dat is een kleine steekproef van acht duels. De grootste "
                "afwijkingen: Tottenham Hotspur – Coventry City (-14,39 pp op de thuiszege; het "
                "model zet Spurs op 49,1% waar Pinnacle 63,5% noteert, en dat is precies het "
                "duel waar poort 8 de underdog-kant tegenhield), Monza – Cagliari (+13,75 pp op "
                "de thuiszege) en Trabzonspor – Beşiktaş (+11,75 pp op de UITzege). Dat laatste "
                "duel is de enige regel die zijn lat haalt, en daar staat het model dus ruim "
                "boven Pinnacle op precies de kant die is gepubliceerd — Pinnacle noemt het een "
                "pick'em (37,2% om 37,8%) en het model geeft Beşiktaş 49,5%. Lees die regel met "
                "dat verschil erbij. HARDE GRENS §2/§4: dit getal zit NIET in my_prob en NIET "
                "in prob_sources; het is andermans lezing en marktafgeleid, en het hoort in de "
                "vergelijking."),
            "UNDERSTAT_DEKT_TWEE_VAN_DE_VIER_DUELS": (
                "Drie van de vijf Understat-competities speelden vandaag (Premier League 1, "
                "Serie A 2, La Liga 1 — de Bundesliga en de Ligue 1 niet), samen 4 duels, en "
                "2 ervan hebben een tweede, onafhankelijk xG-model naast Fotmob: Parma – Torino "
                "en Getafe – Rayo Vallecano. De twee die het niet hebben zijn precies de twee "
                "met een omgerekende ploeg — Tottenham Hotspur – Coventry City en Monza – "
                "Cagliari — en dat is terecht: een promovendus staat niet in de "
                "Understat-tabel van 2025/2026. Understat ligt structureel ~0.13 xG per ploeg "
                "per duel hoger dan Fotmob (§4), dus er is uitsluitend genormaliseerd op het "
                "EIGEN competitiegemiddelde van Understat. Dat verschil gaat per §4 NIET in "
                "my_prob; het gaat als p_xg_understat het kalibratielogboek in."),
            "GEEN_VERPLAATSTE_WEDSTRIJD": (
                "context.check_venue is voor alle 8 duels gedraaid en relocated is overal "
                "False: elke thuisploeg speelt in haar eigen stadion. Dat is een controle die "
                "ook bij een open poort wordt gemeld (§1c)."),
            "OPSTELLINGEN": (
                "lineup_type: 6 duels op 'predicted' en 2 op 'lastStarting11' (Trabzonspor – "
                "Beşiktaş en Wisła Płock – Radomiak Radom). Bevestigde elftallen (lineupType "
                "'confirmed') zijn er om 04:30 NL bij geen enkel duel. Dat zit in de "
                "datarijkdom (§3 Stage 4) en niet in my_prob."),
            "VROEG_SEIZOEN_EN_DE_DEENSE_ROUTE": (
                "early_season_uplift geeft factor 1.0940, gepoold 1.1091 over 50 speeldagen in "
                "ZES competities. De DANISH SUPERLIGA is uit de pool gelaten en loopt via de "
                "route `lopend`: 11 van de 22 speeldagen gespeeld, dus op of boven "
                "SEASON_MATURE_SHARE, en dan meet lopend/vorig een echt niveauverschil tussen "
                "twee seizoenen in plaats van een tijdseffect binnen één seizoen (§3 Stage 5, "
                "league_level). Dat is een weggelaten waarneming en die hoort genoemd, net als "
                "een stille truncatie in Stage 4. De zes andere competities lopen via "
                "`vorig+uplift`. LET OP dat Viborg – FC Midtjylland — een van de drie "
                "gepubliceerde regels — precies die Deense route gebruikt: niveau thuis 1,615 / "
                "uit 1,400 / basis 1,514, uit het LOPENDE seizoen en ongeschaald."),
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
        s3 = json.load(open("tmp-run/ra_oct19_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct19_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct19_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct19_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct19_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

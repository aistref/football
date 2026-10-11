"""Run A 11 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct10_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. Eenentwintig van de 21 competities uit de runlijst zijn nagelopen, dertien speelden en
er staan 41 duels in het inzetvenster. Vijf gepubliceerde regels, waarvan VIER hun eigen drempel
op beide schalen halen en één (FC Midtjylland – FC København) alleen op de herijkte; zie
VIJFDE_REGEL_HAALT_DE_LAT_ALLEEN_HERIJKT. `mark_completed` gebeurt pas na het runrapport en de
push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-11"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-11T04:15:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
                         " LET OP — bet_beide = FALSE: deze selectie haalt de drempel van 8,0 pp "
                         "ALLEEN op de herijkte schaal; ruw blijft hij eronder. §5a beslist "
                         "publicatie op de herijkte my_prob, dus dit is geregeld gedrag, maar het "
                         "label van toplist.build ('haalt ook de lat') zegt dat niet.")
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
    for run, pad in (("A", "tmp-run/ra_oct11_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=1.010225, b=0.006622 over 4110 afgerekende gevallen, fitted_through "
                          "2026-10-10, oftewel de vorige rundag zoals §6b-5c eist. Deze run heeft "
                          "calibration.py settle gedraaid vóór de analyse (291 waarnemingen "
                          "afgewikkeld, 4317 van 4356 compleet, 39 nog open). De fit VERHOOGT een "
                          "kans over vrijwel de hele speelbare band — het ruwe model zei gemiddeld "
                          "33,333% en het gebeurde 33,333% — en dat is precies de situatie waar "
                          "§5a voor waarschuwt: 'herijkt haalt de drempel, dus ruw ook' is niet "
                          "langer automatisch waar. Op de vijf gepubliceerde regels zet de "
                          "herijking tussen +0,22 en +0,34 procentpunt bij de edge op, en bij één "
                          "van de vijf is dat het verschil met de lat; zie "
                          "VIJFDE_REGEL_HAALT_DE_LAT_ALLEEN_HERIJKT."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "DERTIEN van de eenentwintig competities uit de runlijst speelden, met 41 duels "
                "samen in het inzetvenster. Acht competities hadden GEEN WEDSTRIJD: de drie "
                "Europese toernooien (UCL, UEL, UECL) en de vijf bekers (FA Cup, League Cup, "
                "Coppa Italia, KNVB Beker, DFB Pokal). De drie toernooien staan niet in de "
                "Fotmob-daglijst; de vijf bekers hebben geen fotmob_id en zijn daarom apart langs "
                "BetExplorer gegaan — zie BEKERS_GAAN_LANGS_BETEXPLORER. Het is de eerste volle "
                "zondag van de maand met alle vijf de grote competities tegelijk: Premier League "
                "3, Serie A 5, La Liga 4, Bundesliga 2, Ligue 1 3, Championship 1, Eredivisie 4, "
                "Primeira Liga 3, Belgian Pro League 4, Super Lig 3, Scottish Premiership 2, "
                "Danish Superliga 4, Ekstraklasa 3."),
            "DE_CAP_BINDT_NIET": (
                "41 duels op een zondagcap van 55, dus er is NIETS afgekapt (afgekapt = 0) en de "
                "hele runlijst is doorgerekend. Stille truncatie is verboden (§3 Stage 4) en het "
                "omgekeerde hoort er net zo expliciet te staan: er valt vandaag niets te melden "
                "omdat er niets wegviel. De datarijkdom liep van 4,5 tot 7,5; gisteren bond de "
                "cap voor het eerst (56 duels op 55) en vandaag weer niet."),
            "VEERTIEN_OMREKENINGEN": (
                "Veertien van de 41 duels hebben een ploeg die niet in de stand van 2025/2026 "
                "staat, en de §4-route 'Promovendi: eerst omrekenen, dan pas NONE' is daarmee "
                "opnieuw de hoofdroute en geen randgeval. TWAALF kwamen er door op data_tier "
                "LIGHT (een omgerekende ploeg is nooit FULL) en TWEE sneuvelden op "
                "promotion.conversion_in_range, die de omrekening buiten het gemeten bereik legt: "
                "HULL CITY – EVERTON (Premier League; Hull City staat niet in de Engelse stand "
                "van vorig seizoen) en SILKEBORG – AC HORSENS (Danish Superliga; AC Horsens). "
                "Beide komen op data_tier NONE uit en zijn niet doorgerekend. Dat is correct "
                "gedrag en precies de Coventry-val waarvoor die poort bestaat (§4). De andere "
                "twaalf omrekeningen: Monza (Serie A), Deportivo A Coruña en Racing Santander "
                "(La Liga), Schalke 04 (Bundesliga), Troyes (Ligue 1), Willem II, Cambuur en "
                "ADO Den Haag (Eredivisie), Çorum FK (Super Lig), St. Johnstone (Scottish "
                "Premiership), Lyngby (Danish Superliga) en Wisła Kraków (Ekstraklasa). GEEN VAN "
                "DE VEERTIEN is een gepubliceerde regel geworden — alle vijf de regels zijn FULL."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 11 okt, 08:00 NL 12 okt). Alle 41 duels komen van de "
                "daglijst van 2026-10-11 (source_day = DAY, geen enkele DAY+1) en alle 41 staan "
                "op RunMatch.playable = True: de vroegste aftrap is FC Utrecht – Willem II om "
                "12:15 NL en de run begon om 04:15 NL. De nachtband waarvoor runwindow.py op "
                "24 september is gebouwd is vandaag leeg; deze runlijst heeft geen competitie in "
                "een Amerikaanse tijdzone. De aftraptijden zijn met twee bronnen bevestigd "
                "(Fotmob in UTC, BetExplorer in UK-tijd) en komen op hetzelfde NL-tijdstip uit — "
                "de controle die §5 'Aftraptijden' eist."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1 eist bevestiging door een tweede methode, en dat geldt ook voor de vraag "
                "wélke wedstrijden er zijn — de duurste fouten van deze maand zaten twee keer in "
                "die vraag en niet in de analyse (6 okt: FA Cup niet in de daglijst; 7 okt: de "
                "is_today-filter aan de prijskant). DE DRIE BRONNEN ZIJN VANDAAG PER COMPETITIE "
                "EENS, niet alleen op het totaal: Fotmob-daglijst en de BetExplorer-fixturepagina "
                "geven voor alle dertien spelende competities EXACT hetzelfde aantal duels van "
                "vandaag (3/5/4/2/3/1/4/3/4/3/2/4/3 = 41 tegen 41), en de twaalf bulk-responsen "
                "van The Odds API dekken dezelfde twaalf competities (4 tot 25 events elk). Over "
                "de afwezigheid van de drie Europese toernooien zijn Fotmob en BetExplorer het "
                "ook eens."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "Geen van de vijf bekers op de Run A-runlijst heeft een fotmob_id in "
                "coverage.json, dus runwindow.matches_for_run kan ze niet filteren en 'niet in de "
                "daglijst' is voor hen geen uitspraak. Dat is het gat dat Run A op 6 oktober "
                "trof. Alle vijf zijn daarom opnieuw langs BetExplorer gegaan "
                "(tmp-run/ra_oct11_cups.py) en alle vijf hebben hun eerstvolgende ronde NA het "
                "inzetvenster: FA Cup 17 okt (32 teamparen, nog geen koersen), League Cup 27 okt "
                "(8 duels mét koersen), KNVB Beker 27 okt (26 teamparen), DFB Pokal 27 okt (16 "
                "mét koersen), Coppa Italia vanaf 1 dec (8 teamparen). Vijf keer GEEN WEDSTRIJD, "
                "met een tweede bron eronder in plaats van met een stilte."),
            "SCOTTISH_PREMIERSHIP_ZONDER_SPORTKEY": (
                "De Scottish Premiership is de enige spelende competitie ZONDER sportkey bij The "
                "Odds API en heeft vandaag twee duels (Motherwell – Celtic, Aberdeen – "
                "St. Johnstone), dus die twee draaien op het gratis BetExplorer-MARKTGEMIDDELDE "
                "alleen. Gevolg per duel, en het staat zo in markets_checked: drie selecties in "
                "plaats van dertien tot negentien (alleen 1X2), en Asian Handicap, Draw No Bet, "
                "Double Chance, Over/Under en BTTS allemaal als 'niet opgevraagd — geen sportkey "
                "bij The Odds API voor deze competitie'. Dat is bekeken met een reden en geen gat "
                "(§1a), maar het betekent óók dat de edge daar systematisch te laag uitvalt: een "
                "marktgemiddelde over vijf boeken is geen beste prijs, en de beste prijs lag "
                "vandaag over de 37 duels met beide bronnen gemiddeld 6,26% hoger (3,82% tot "
                "13,34%). Motherwell – Celtic viel af op 'data conflicterend' (poort 5) en "
                "Aberdeen – St. Johnstone op de edge; geen van de twee zat in de buurt van de "
                "lijst."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e, teruggezet per "
                       "1 okt 2026); sides.check() is met today=2026-10-11 aangeroepen zoals §1e "
                       "eist, zodat een herberekening van het vervallen venster (25 t/m 30 sep) "
                       "niet stil de poort van vandaag krijgt. Vandaag houdt hij 12 selecties "
                       "tegen over VIER wedstrijden, die elk één rij in poort8_geblokkeerd "
                       "krijgen — de selectie met de hoogste selection_score, met de rest als "
                       "aantal in ook_geblokkeerd (§1e: één rij per wedstrijd, want dezelfde "
                       "mening in een andere markt is één bevinding). Dat is veel minder dan de "
                       "41 van gisteren, en de reden is de aard van de dag: op de uitkomstmarkten "
                       "vangt poort 5 vandaag al bijna alles weg vóórdat poort 8 aan bod komt. "
                       "poort8_ruw is LEEG — geen enkele selectie sneuvelde alléén op de ruwe "
                       "schaal. poort8_vervallen is leeg omdat sides.has_lapsed(2026-10-11) "
                       "onwaar is. Geen van de vijf gepubliceerde regels staat op een "
                       "underdog-kant onder de ondergrens: vier hebben side = None (twee Under, "
                       "twee Over) en de vijfde is een 1X2 op de THUISFAVORIET 1. FC Köln. De "
                       "stand van de twee reeksen wordt alleen GENOEMD en niet opnieuw als "
                       "besluit voorgelegd (§1e, 5 okt)."),
            "WAAROM_VIJF_REGELS": (
                "Vijf regels op vijf plekken (zondag, MAX_SHORTLIST = 5), en er is NIET "
                "aangevuld: de lijst is vol omdat er precies vijf kandidaten de zeven "
                "overgebleven poorten haalden, niet omdat er naar vijf is toegewerkt. Alle vijf "
                "staan ÓÓK boven hun eigen drempel op de herijkte schaal — dat is op deze "
                "routine ongewoon en het is twee dagen op rij nu de rangorde en de drempel "
                "dezelfde lijst opleveren. Beşiktaş – Kocaelispor Under 3.5 @1,6468 (+15,80 pp), "
                "Arouca – Estrela da Amadora Over 2.5 @1,9114 (+10,90 pp), Union St.Gilloise – "
                "OH Leuven Under 3.5 @1,75 (+9,75 pp), 1. FC Köln – Borussia Mönchengladbach "
                "1X2 thuis @2,18 (+10,17 pp) en FC Midtjylland – FC København Over 2.5 @1,686 "
                "(+8,30 pp), alle vijf FULL bij een lat van 8,0. Omdat er precies vijf boven de "
                "lat staan en er vijf plekken zijn, BINDT DE §5b-AFKAPPING OP LIJSTLENGTE NIET "
                "en groeit die reeks deze run niet. MAX_LIGHT_IN_SHORTLIST = 2 bindt ook niet: "
                "alle vijf regels zijn FULL, en dat is op een dag met veertien omgerekende "
                "ploegen het noemen waard."),
            "VIJFDE_REGEL_HAALT_DE_LAT_ALLEEN_HERIJKT": (
                "FC MIDTJYLLAND – FC KØBENHAVN (Over 2.5 @1,686) staat op +8,30 pp HERIJKT en op "
                "+7,99 pp RUW, bij een lat van 8,0 — dus `bet_beide` is FALSE en de regel haalt "
                "de drempel alleen nadat de herijking eroverheen is gegaan. §5a beschrijft exact "
                "dit geval: sinds de fit van 20 september VERHOOGT recalibrate.apply een kans "
                "over vrijwel de hele speelbare band, en daarmee is 'herijkt haalt de drempel, "
                "dus ruw ook' niet langer automatisch waar. De regel van §5a is dat publicatie "
                "op de HERIJKTE my_prob wordt beslist, en dat is hier gedaan; onder §5b bepaalt "
                "bovendien de rangorde de lijst en is de drempel een label. Twee dingen die "
                "daarbij horen en die niet mogen wegvallen. (1) `toplist.build` schrijft bij deze "
                "regel 'BET — en haalt ook de lat van 8.0 pp' en vermeldt NIET dat de ruwe schaal "
                "er met +7,99 pp net onder blijft; dat is een onvolledig label op precies het "
                "geval waarvoor `bet_beide` is gebouwd, en het staat als openstaand punt in het "
                "runrapport. (2) Lecce – Bologna is hetzelfde geval (ruw +7,89, herijkt +8,13) "
                "maar scoorde te laag voor de lijst, dus de dag telt er twee en niet één."),
            "WAT_DE_POORTEN_DEDEN": (
                "550 selecties over alle zes markten, en de tweede methode (poort 5) vangt "
                "opnieuw het overgrote deel weg: 417 van de 550 sneuvelden op 'tweede_methode', "
                "oftewel 76%. Daarnaast 59 op de edge, 23 op context, 22 op de koersband, 12 op "
                "de underdog-regel, 6 op robuustheid en 11 die alle poorten open hielden. DIT IS "
                "DE VIJFDE DAG OP RIJ dat poort 5 tweederde of meer wegvangt (7 okt 40 van 60, "
                "8 okt 29 van 37, 9 okt 130 van 174, 10 okt 553 van 754, vandaag 417 van 550). "
                "Het is dus geen eigenschap van één competitie, geen eigenschap van één "
                "kalenderdag en geen ruis. Het patroon in de lambdas is hetzelfde als de vier "
                "dagen ervoor en het is bij de gepubliceerde regels direct te zien: de "
                "SPLITSMETHODE zet een ander doelpuntenNIVEAU neer dan de xG-methode, niet een "
                "andere winnaar. Bij FC Midtjylland – FC København geeft xG 1,59 / 1,63 en de "
                "splits 3,25 / 1,70 — de splitsarm verwacht bijna twee doelpunten méér — en de "
                "edge staat daar op +27,84 pp (splits) tegen +3,03 pp (xG). Bij Arouca – Estrela "
                "da Amadora xG 1,74 / 1,39 tegen splits 2,16 / 1,61 (+20,29 tegen +8,21 pp), bij "
                "Union St.Gilloise – OH Leuven xG 2,24 / 0,65 tegen splits 2,77 / 0,27 (+6,57 "
                "tegen +10,16 pp) en bij 1. FC Köln juist de andere kant op: xG 2,32 / 1,39 "
                "tegen splits 1,83 / 1,39 (+12,03 tegen +1,65 pp). Poort 5 eist dat beide "
                "methodes de markt dezelfde kant op verslaan, en op een totaal is dat precies "
                "waar een niveauverschil tussen de twee methodes doorslaat. §6e wijst de "
                "splitsmethode sinds 22 augustus aan als de scheefste van de twee en §1f heeft "
                "haar gewicht daarom op 0,20 gezet; dit is de vijfde dag met cijfers die dezelfde "
                "kant op wijzen. OPSCHRIJVEN EN VOLGEN, niet vandaag aan sleutelen (§6d: niet op "
                "één dag een drempel verzetten)."),
            "POORT7_HIELD_DRIEENTWINTIG_SELECTIES_TEGEN": (
                "De contextpoort houdt vandaag 23 selecties tegen over ACHT wedstrijden — de "
                "breedste dag van deze poort tot nu toe — en alle acht op de BLESSUREKANT, geen "
                "enkele op rust. Per wedstrijd, met het verschil in ontbrekende selectiewaarde: "
                "REAL BETIS – OSASUNA (Osasuna mist 35% tegen 3%), NICE – STRASBOURG (Strasbourg "
                "35% tegen 20%), LAZIO – MONZA (Monza 33% tegen 22%), RIO AVE – NACIONAL "
                "(Nacional 33% tegen 20%), LIVERPOOL – MANCHESTER CITY (Liverpool 31% tegen 14%, "
                "met Conor Bradley, Giovanni Leoni en Alexander Isak), AROUCA – ESTRELA DA "
                "AMADORA (Estrela 31% tegen 4%), RACING SANTANDER – VALENCIA (Valencia 20% tegen "
                "5%) en RENNES – AUXERRE (Auxerre 11% tegen 0%). In alle acht gevallen stond de "
                "selectie op de kant van de ploeg die de spelers mist, en de poort doet dus "
                "precies wat §1c beschrijft: hij houdt alleen tegen, hij stelt my_prob niet bij "
                "en hij staat open bij side = None. Dat laatste is vandaag zichtbaar bij AROUCA – "
                "ESTRELA DA AMADORA: de poort hield daar één selectie met een kant tegen en de "
                "GEPUBLICEERDE regel van diezelfde wedstrijd is een Over 2.5 zonder kant, die dus "
                "terecht door de poort gaat. Op de RUWE dagranglijst (§5a) staan Rio Ave – "
                "Nacional (plek 2, Nacional +0,25 @1,931, +11,09 pp) en Rennes – Auxerre (plek 4, "
                "Auxerre +1,5 @1,77, +9,73 pp): dat zijn de twee selecties die poort 7 vandaag "
                "heeft gekost, en dat hoort erbij te staan."),
            "POORT7_NIET_MEETBAAR_IN_DERTIEN_DUELS": (
                "Fotmob geeft squad_value = 0 voor ALLE ploegen in 13 van de 41 duels, verdeeld "
                "over vijf competities: Belgian Pro League (4 van 4), Super Lig (3 van 3), "
                "Ekstraklasa (3 van 3), Scottish Premiership (2 van 2) en Championship (1 van 1). "
                "Bij de andere 28 is de selectiewaarde voor beide ploegen bekend. context.check "
                "komt in die 13 correct uit op 'geen materieel nadeel gemeten' — de poort staat "
                "open omdat er niets te meten valt, wat §1c expliciet toestaat. De uitvallers "
                "zijn er wél bij naam bekend (Kocaelispor mist er zes, Union St.Gilloise twee) "
                "en staan in het contextblok; wat ontbreekt is hun gewicht. LET OP ÉÉN GEVOLG "
                "DAT HIER EERLIJK MOET STAAN: bij squad_value = 0 en out_value > 0 komt "
                "ctxlog.out_share op out/(0+out) = 100% uit, en dat is een rekenkundig artefact "
                "en geen meting. Twee van de vijf gepubliceerde regels liggen in die groep "
                "(Beşiktaş – Kocaelispor en Union St.Gilloise – OH Leuven); beide zijn een "
                "Over/Under met side = None, dus de blessurekant van poort 7 kon daar hoe dan "
                "ook niet binden en het artefact heeft op geen van beide beslissingen invloed "
                "gehad. In de RANGSCHIKKING van Stage 4 kost het die 13 duels wél twee punten op "
                "de component 'afwezigen', omdat ranking._absence_points de aanwezigheid van het "
                "opstellingsblok aan squad_value > 0 afleest — daarom staan ze alle 13 op "
                "datarijkdom 4,5 en dus onderaan de sortering. Vandaag kostte dat niets, want de "
                "cap bond niet. GOED NIEUWS BIJ DAT ARTEFACT, en het hoort erbij: "
                "ctxlog.out_share LAAT DIE 13 DUELS WEG in plaats van ze op 100% te boeken (hij "
                "geeft None zodra squad_value = 0), dus de meting van §1c wordt er niet door "
                "vervuild. Van de 28 duels mét noemer zijn er vandaag 27 in het contextlogboek "
                "beland; bij het 28e is de waarde van één van de twee ploegen 0. Het artefact zit "
                "dus alleen in het contextBLOK in run-state en niet in de reeks waarop later "
                "gemeten wordt."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug). Alle zes "
                "markten hebben werkelijk meegedongen: de bulk-aanroep leverde voor elk van de "
                "twaalf competities MET sportkey 1X2 op de beste prijs, Asian Handicap, Draw No "
                "Bet en Over/Under, en de tweede ronde kocht BTTS voor de 27 duels met een "
                "kandidaat-edge (26 gelukt; Motherwell – Celtic viel af omdat de Scottish "
                "Premiership geen spreads-respons heeft). 550 selecties: Over/Under 182, Asian "
                "Handicap 137, 1X2 113, BTTS 52, Draw No Bet 44, Double Chance 22. De twee dunne "
                "markten zijn geen gat maar een ontbrekende lijn, en dat staat zo in "
                "markets_checked (Double Chance bestaat alleen waar de spreads-respons een "
                "+0,5-lijn had, Draw No Bet alleen waar er een 0,0-lijn was). De 14 duels zonder "
                "kandidaat-edge dragen bij BTTS 'niet opgevraagd' MET de reden, niet "
                "'opgevraagd' — §6b-5b eist dat onderscheid. DE UITKOMST IS VANDAAG MINDER "
                "EENZIJDIG DAN GISTEREN en dat is het noemen waard, omdat de eenzijdigheid van "
                "10 oktober (vier Unders op vijf regels) toen als punt is opgeschreven: nu staan "
                "er twee Unders, twee Overs en één 1X2 op de thuisfavoriet. Nul Asian Handicap, "
                "nul BTTS, nul Draw No Bet, nul Double Chance. Dat de handicaps met 137 "
                "selecties de tweede breedste markt waren en toch niets leverden is geen "
                "inkoopeffect maar de uitkomst van poort 5 en poort 8 samen. Geen quotum (§1 "
                "verbiedt bets forceren om een verdeling te halen); wel iets om te volgen."),
            "UPLIFT": (
                "Factor 1,0815 (gepoold 1,0880 over 99 speeldagen, ALLE DERTIEN spelende "
                "competities in de pool, NUL overgeslagen door uplift_observations). Alle "
                "dertien draaien op route 'vorig+uplift': geen enkel lopend seizoen is over de "
                "helft van zijn speeldagen (2 tot 10 gespeeld van 22 tot 46), dus league_level "
                "kiest nergens de route 'lopend'. De correctie doet dus écht iets: 8,2% meer "
                "doelpunten op het niveau van vorig seizoen, iets minder dan de 9,7% van "
                "gisteren omdat de pool vandaag dertien in plaats van twaalf competities bevat "
                "en de Danish Superliga (10 van 22 speeldagen, de rijpste van de dertien) de "
                "factor naar beneden trekt. Gemeten tegen de markt als CONTROLE en niet als fit "
                "(§3 Stage 5 verbiedt afregelen op de markt): zie het runrapport."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("62 credits van een plafond van 467 (19.666 over bij api_check.py, 334 "
                       "verbruikt deze maand, 21 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: twaalf bulk-aanroepen à 3 credits (h2h + spreads + totals), één "
                       "per spelende competitie MET sportkey — split_budget(467, 12) -> (12, 12), "
                       "dus niemand viel buiten de bulk; 4 tot 25 events per competitie. Stap 2: "
                       "BTTS voor 26 van de 27 duels met een kandidaat-edge, 26 credits. De "
                       "dertiende spelende competitie, de Scottish Premiership, heeft geen "
                       "sportkey en draaide op het gratis BetExplorer-marktgemiddelde — zie "
                       "SCOTTISH_PREMIERSHIP_ZONDER_SPORTKEY. Na deze run staat het maandverbruik "
                       "op 396 van 20.000. Het budget is op geen enkele manier de beperkende "
                       "factor, en MAX_DEEP_ANALYSES is dat vandaag ook niet (41 van 55)."),
            "BEURSKOERS": (
                "§5 eist bij een beurs beide getallen, en DRIE van de vijf regels staan op een "
                "beurs, alle drie bij Matchbook: Beşiktaş – Kocaelispor Under 3.5 1,66 bruto / "
                "1,6468 na 2% commissie, Arouca – Estrela da Amadora Over 2.5 1,93 bruto / "
                "1,9114 netto, en FC Midtjylland – FC København Over 2.5 1,70 bruto / 1,686 "
                "netto. edge_pp en selection_score rekenen met de NETTO koers "
                "(oddsapi.net_price); de gebruiker ziet de bruto koers op zijn scherm. De andere "
                "twee zijn geen beurs en dus commissievrij: Union St.Gilloise – OH Leuven Under "
                "3.5 @1,75 en 1. FC Köln – Borussia Mönchengladbach 1X2 thuis @2,18, beide bij "
                "1xBet. BetExplorer leverde het gratis marktgemiddelde voor het kalibratieblok "
                "van §6e en voor poort 8 — §1a: gemiddelde om te MÉTEN, beste prijs om te SPELEN. "
                "De beste prijs lag over de 37 duels met beide bronnen gemiddeld 6,26% boven het "
                "marktgemiddelde (3,82% tot 13,34%), in lijn met de +5,63% tot +7,78% die §1a op "
                "5 september mat."),
            "KALIBRATIE_SETTLE": (
                "§6b-5c eist calibration.py settle ELKE run, ook bij nul bets, en eist dat "
                "fitted_through in het runrapport staat. Deze run heeft settle gedraaid vóór de "
                "analyse (291 waarnemingen afgewikkeld, 4317 van 4356 compleet) en fitted_through "
                "staat op 2026-10-10, de vorige rundag. Zie HERIJKING. Het kalibratieblok is "
                "vandaag voor 39 van de 41 duels gevuld; de twee die het niet kregen zijn de "
                "NONE-duels Hull City – Everton en Silkeborg – AC Horsens, en daar is geen "
                "modelkansverdeling om naast de markt te zetten."),
            "UNDERSTAT": (
                "Het tweede, onafhankelijke xG-model dekte vandaag TIEN duels, omdat alle vijf de "
                "Understat-competities speelden (Premier League 3, Serie A 5, La Liga 4, "
                "Bundesliga 2, Ligue 1 3 = 17 duels, min de zeven waarin een ploeg niet in de "
                "Understat-tabel van 2025 staat). p_xg_understat gaat mee in het kalibratieblok "
                "van §6e, zodat over enkele weken met cijfers te zeggen is of het ene xG-model "
                "beter voorspelt dan het andere. Het verandert my_prob niet (§4)."),
            "VERPLAATSTE_WEDSTRIJDEN": (
                "context.check_venue is voor alle 41 duels gedraaid en zet NUL keer relocated: "
                "elk duel staat in het eigen stadion van de genoteerde thuisploeg. §1c eist dat "
                "dit ook bij een open poort wordt vastgelegd en genoemd, want thuisvoordeel is de "
                "aanname waar het model het zwaarst op leunt."),
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
        s3 = json.load(open("tmp-run/ra_oct11_stage3.json"))
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
        for run, pad in (("A", "tmp-run/ra_oct11_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct11_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct11_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

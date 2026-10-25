"""Run B 24 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct20_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. TWEE van de zeventien competities speelden, met samen twee duels
in het inzetvenster en nul afgekapt (cap 40 op woensdag). ÉÉN gepubliceerde regel, en die haalt
zowel de drempel van 8,0 als de verzwaarde lat van poort 9.

Drie dingen die vandaag in de parameters horen:

* **De bet bestaat alleen dank zij `runwindow.py`.** FC Cincinnati – DC United trapt af om 01:00
  NL op 22 oktober en stond op de UTC-daglijst van 21 oktober; onder de oude UTC-regel was dit
  duel in de run van morgen beland en dan al gespeeld geweest.
* **Pinnacle spreekt de bet tegen**, en dat is het zwaarste voorbehoud: op zijn eigen lijn 3,75
  staat het model +6,87 pp meer aan de Under-kant dan de scherpste bookmaker — precies de richting
  waarvan §6g meet dat ze fout staat.
* **De vroeg-seizoenspool bestaat uit één competitie**, omdat MLS halverwege zijn seizoen is en
  route `lopend` krijgt. Een pool van één is geen pool; dat hoort erbij te staan.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-25"
# 24 okt 2026 — DE KLOK GAAT VANNACHT TERUG, dus de hardgecodeerde +02:00 die hier tot vandaag
# stond klopt niet meer voor de late duels. De EU zet de klok om op de laatste zondag van oktober
# om 01:00 UTC; dat is in de nacht NA deze rundag, en acht duels van het inzetvenster trappen
# daarna af (vijf MLS om 01:30Z, twee om 02:30Z en Santos - Bahia om 01:00Z). Met +02:00 komen
# die er een uur TE LAAT uit, en Sec. 5 zegt: "een aftraptijd die er een uur naast zit maakt de
# hele bet onbruikbaar". `runwindow.kickoff_nl` deed het al goed (zoneinfo); dit was het
# openstaande punt uit de docstring van `runwindow.NL`, en vandaag is het de eerste dag dat het
# bindt. Dus hier ook zoneinfo, met dezelfde vaste +02:00 alleen nog als terugval.
try:
    from zoneinfo import ZoneInfo
    NL = ZoneInfo("Europe/Amsterdam")
except Exception:
    NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-25T04:15:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer); +01:00, eerste rundag op wintertijd


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
    for run, pad in (("B", "tmp-run/rb_oct25_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0.977, b=-0.015 "
                "op 5778 afgerekende gevallen, fitted_through 2026-10-24. Dat is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die Sec. 6b-5c sinds 30 sep "
                "eist). DE CORRECTIE IS OPNIEUW VRIJWEL DE IDENTITEIT, maar nu net aan de verlagende "
                "kant: -0,4 pp op 50%, -0,6 pp op 60% en -0,7 pp op 70%, en +0,1 pp op 30% — het ruwe "
                "model zei gemiddeld 33,3% en het gebeurde 33,3%. Op de vijf gepubliceerde regels haalt "
                "ze tussen 0,4 en 0,7 pp van de kans af, en bet_beide is bij alle vijf FALSE omdat geen "
                "van de vijf zijn lat op beide schalen haalt. Lees die identiteit zoals Sec. 1e punt 3 "
                "voorschrijft: de reeks is de ONGESELECTEERDE ijksteekproef en breder dan de staart "
                "waarop deze routine speelt. Dat ze bijna niets corrigeert betekent niet dat er niets "
                "scheef staat."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "Sec. 5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "DERTIEN VAN DE ZEVENTIEN COMPETITIES SPELEN, met samen ZESENDERTIG duels in het "
                "inzetvenster. Per competitie: Eliteserien 6, Greek Super League 4, Segunda Division 4, "
                "Czech First League 3, Hungarian NB I 3, 2. Bundesliga 3, Swiss Super League 3, "
                "Allsvenskan 2, Romanian SuperLiga 2, Serie B 2, Austrian Bundesliga 2, Croatian HNL 1 "
                "en MLS 1. VIER COMPETITIES OP `GEEN WEDSTRIJD`: Keuken Kampioen Divisie, English "
                "League One, English League Two en Serie A (BRA) — de twee Engelse divisies spelen "
                "zaterdag en hadden gisteren hun ronde, de Braziliaanse speelt pas 3 november. Dat is "
                "geen gat (Sec. 3 Stage 2). scripts/idcheck.py gaf voor alle 33 fotmob_id\'s uit "
                "coverage.json een bruikbare stand (afsluitcode 0), ook voor de vier competities die "
                "vandaag stil zijn — dat is precies de controle die op naam noch op uitkomst zou zijn "
                "opgevallen. De tweede bron bevestigde de daglijst voor 17 van de 17 competities "
                "(BetExplorer tegen Fotmob, 36 duels tegen 36, geen enkele afwijking)."
            ),
            "DE_CAP_BINDT_VANDAAG_NIET": (
                "MAX_DEEP_ANALYSES = 55 (zondag) EN ER STAAN 36 DUELS, DUS ER IS NIETS AFGEKAPT en de "
                "dekkingstabel heeft geen AFGEKAPT-regel. De datarijkdom over de hele run loopt van 4,5 "
                "(Basel - Grasshopper, Sion - Lausanne, Aris - Atromitos) tot 8,0 (Vasas Budapest - "
                "Paksi SE en Puskas FC Academy - Nyiregyhaza); omdat er niets afvalt zijn er geen twee "
                "getallen rond de capgrens te noemen. De looptijd is daarmee vandaag ook niet de grens: "
                "48 van 1337 credits gebruikt, 36 duels doorgerekend, ruim binnen de 06:30 van Sec. 0."
            ),
            "DE_LIJST_IS_EEN_RANGORDE_EN_GEEN_VONDST": (
                "VIJF REGELS, WAARVAN ER PRECIES EEN ZIJN EIGEN LAT HAALT EN VIER OP RANGORDE OP DE "
                "LIJST STAAN (Sec. 5b). Boven de lat van 8,0: alleen SION - LAUSANNE, Under 3,5 @1,77 "
                "met +11,16 pp — en die haalt ook de verzwaarde lat van poort 9 (10,0 pp voor een Under "
                "op FULL). Eronder, en dus puur op rangorde: Thun - Lugano Under 3,5 @1,8624 (+7,57 "
                "pp), Molde - Fredrikstad \'beide ploegen scoren - nee\' @2,38 (+7,91 pp), Holstein Kiel "
                "- Dynamo Dresden Under 3 @1,95 (+5,48 pp) en Los Angeles FC - LA Galaxy Under 3,5 "
                "@1,86 (+4,66 pp). Van de 404 doorgerekende selecties over 36 duels haalden er TWEE "
                "alle negen poorten inclusief de drempel, en die twee zijn dezelfde wedstrijd (Sion - "
                "Lausanne, twee uitdrukkingen van een mening) — dus er is EEN duel dat de volle lat "
                "haalt. Er passen vijf regels in de zondaglijst, dus de drempel bindt vandaag niet als "
                "grens maar staat als label per regel. Lees de lijst als \'dit is het sterkste dat het "
                "model vandaag ziet\' en niet als \'hier ligt waarde\'."
            ),
            "ALLE_VIJF_DE_REGELS_STAAN_OP_DE_MINDER_DOELPUNTEN_KANT": (
                "DIT IS DE ZWAARSTE WAARSCHUWING VAN DEZE RUN EN ZE HOORT VOORAAN. VIER UNDERS EN EEN "
                "\'BEIDE PLOEGEN SCOREN - NEE\': VIJF VAN DE VIJF REGELS WEDDEN OP MINDER DOELPUNTEN, EN "
                "DAT IS PRECIES DE KANT WAARVAN Sec. 6g MEET DAT ZE FOUT STAAT. Het logboek staat daar "
                "op Under 76 picks / -16,5% tegen Over 62 picks / +10,6%, met twee gemeten oorzaken: "
                "een vormfout in het scoregrid die P(Under) bij elk duel 1,6 tot 2,4 pp te hoog zet, en "
                "een selectie-effect daarbovenop. GEEN VAN DE VIJF WORDT DOOR POORT 9 GERAAKT, en dat "
                "is geen toeval maar het ontwerp: Sion haalt de 10,0 ruim (+11,16 pp) en de vier andere "
                "komen niet eens aan de 8,0, dus liggen ONDER de band 8-10 pp waarin de poort werkt. "
                "Diezelfde scheefheid stond gisteren ook in het rapport en ze is er nog: de rem pakt de "
                "band 8-10 pp, terwijl Sec. 5b sinds 20 september regels publiceert die helemaal onder "
                "de drempel liggen, en daar meet Sec. 6g -34,1% over 26 gevallen. POORT 9 BINDT WEL "
                "TWEE KEER VANDAAG, op twee andere lijnen in dezelfde twee duels: Molde - Fredrikstad "
                "Under 3,5 (+9,09 pp) en Sion - Lausanne Under 3,25 (+9,70 pp) gaan als "
                "`doelpunten_onder` het schaduwlogboek in. Dat Sion met zijn 3,5-lijn wel wordt "
                "gepubliceerd en met zijn 3,25-lijn wordt tegengehouden is correct - een andere lijn is "
                "een andere bet - maar het laat zien hoe dicht deze regel bij de rem staat. DIT IS GEEN "
                "REDEN OM VANDAAG EEN DREMPEL OF EEN POORT TE VERZETTEN (Sec. 1h en Sec. 6d verbieden "
                "dat uitdrukkelijk); het is de waarneming die bij deze vijf regels hoort."
            ),
            "PINNACLE_BEVESTIGT_HET_MODEL_OP_1X2_EN_SPREEKT_HET_TEGEN_OP_DE_TOTALEN": (
                "STAP 2 VAN STAGE 5 - het scherpste publieke expertoordeel, LOS van de beste prijs "
                "waarop gespeeld wordt en nooit in my_prob (Sec. 2). Pinnacle noteerde 25 van de 36 "
                "duels op 1X2 en 25 (duel, lijn)-paren op de totalen; de elf duels uit de vier "
                "competities zonder sportkey (Czech, Croatian, Hungarian, Romanian) zijn niet te "
                "toetsen. OP 1X2 STAAT HET MODEL GEMIDDELD 3,16 pp VAN PINNACLE AF bij een gemiddelde "
                "Pinnacle-marge van 4,07% - krapper dan de 4,03 pp van gisteren. Bij de bovenste regel "
                "is die afstand opvallend klein: SION - LAUSANNE staat op 1X2 op 0,39 / 1,12 / -1,52 pp "
                "van Pinnacle, dus over WIE er wint zijn ze het praktisch eens. OP DE TOTALEN NIET: op "
                "Pinnacle\'s eigen lijn van 3,25 staat het model +8,93 pp boven Pinnacle op de "
                "Under-kant. Dat is de tweede grootste afstand van de 25 paren (Viking - Tromso +12,13 "
                "pp is de grootste) en het is precies de richting waarvan Sec. 6g zegt dat ze fout is. "
                "Ook de drie andere Under-regels staan erboven: Thun - Lugano +7,37 pp (lijn 3,50, "
                "dezelfde lijn als de bet), Holstein Kiel - Dynamo Dresden +9,14 pp (lijn 3,00) en Los "
                "Angeles FC - LA Galaxy +5,72 pp (lijn 3,25). OVER DE HELE DAG: gemiddeld +1,87 pp "
                "boven Pinnacle op de Under-kant, met 15 van de 25 paren erboven - en die +1,87 pp ligt "
                "midden in de 1,6-2,4 pp die Sec. 6g als vormfout meet. Dat is een onafhankelijke "
                "bevestiging van die meting, op de prijzen van vandaag in plaats van op het logboek. "
                "LET OP DE REKENWIJZE, DIE VANDAAG IS GEREPAREERD - zie de bevinding daarover."
            ),
            "POORT5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
                "POORT 5 VANGT 313 VAN DE 404 SELECTIES WEG (77,5%) - \'tweede_methode\', de twee "
                "methodes verslaan de markt niet dezelfde kant op. Daarna 36 op de edge (8,9%), 20 op "
                "poort 8 (5,0%), 13 op de koersband (3,2%), 9 op poort 7 (2,2%), 6 op robuustheid "
                "(1,5%), 4 op poort 9 (1,0%) en 1 op de herijking (0,2%). TWEE selecties kwamen door "
                "alles heen, en het zijn twee uitdrukkingen van hetzelfde duel. Die 77,5% ligt in "
                "dezelfde band als de afgelopen weken (gisteren 73,7%) en voegt er geen nieuwe "
                "waarneming aan toe. ZES DUELS VALLEN VOLLEDIG OP DEZE POORT (\'data conflicterend\' als "
                "reden van het hele duel): Aris Thessaloniki - Atromitos, Viking - Tromso, GAIS - IFK "
                "Goteborg, Mjallby - Hammarby en Eintracht Braunschweig - Hannover 96. Op de RUWE "
                "schaal staat Mjallby - Hammarby als vijfde van de dag (AH +1,25 @1,931, +7,69 pp ruw) "
                "en die rij gaat als `tweede_methode` het schaduwlogboek in."
            ),
            "POORT7": (
                "BINDT EN HOUDT NEGEN SELECTIES TEGEN OVER DRIE DUELS, EN HIJ RAAKT EEN VAN DE VIJF "
                "GEPUBLICEERDE REGELS NIET MAAR WEL HET DUEL ERACHTER. THUN - LUGANO: Thun mist 21% van "
                "de selectiewaarde tegen 2% bij Lugano (Marco Burki en Jan Bamert geschorst tot eind "
                "oktober, Fabio Saiz de rest van het seizoen) - VIER selecties op de Thun-kant eruit, "
                "waaronder de Double Chance @2,0976 die op de RUWE lijst als tweede van de dag staat "
                "(+11,01 pp ruw). De Under 3,5 van datzelfde duel staat WEL op de lijst, en dat is "
                "correct: een totaal heeft geen kant, dus poort 7 staat daar open (Sec. 1c). HELLAS "
                "VERONA - PISA: Verona mist 40% tegen 5% (Tomas Suslov tot begin november, Giacomo "
                "Toniolo en Mattia Compagnon van dag tot dag) - DRIE selecties eruit, en dit duel "
                "levert daardoor als geheel geen bet. HOLSTEIN KIEL - DYNAMO DRESDEN twee selecties; de "
                "Under 3 van dat duel staat om dezelfde reden als bij Thun wel op de lijst. "
                "STADIONCONTROLE: 36 duels, NUL ALARMEN - en dat is vandaag een bevinding op zichzelf, "
                "want de ongerepareerde controle gaf er twee (zie de bevinding over same_ground). "
                "OPSTELLINGEN: 27 van de 36 op \'lastStarting11\', 6 voorspeld en 3 op \'unavailable\' - "
                "de gewone klokbevinding, tien tot vierentwintig uur voor de aftrap. De context van "
                "ALLE 36 duels is opgehaald en vastgelegd, ook van de vier op tier NONE, zoals Sec. 1c "
                "eist; de steekproef van ctxlog.py is dus volledig."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (Sec. 1e); sides.check() is met "
                "today=2026-10-25 aangeroepen zoals Sec. 1e eist, zodat het vervallen venster van 25 "
                "t/m 30 september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. HIJ "
                "HOUDT 20 SELECTIES TEGEN OVER NEGEN DUELS: vier bij Kristiansund - KFUM, drie elk bij "
                "Sabadell - Tenerife, Sturm Graz - Ried en LASK - Salzburg, twee elk bij Cadiz - AD "
                "Ceuta FC en Castellon - Sporting Gijon, en een elk bij NFC Volos - Panathinaikos, Aris "
                "- Atromitos en Sion - Lausanne. OP DE RUWE LIJST STAAT EEN VAN DE VIJF BOVENSTE REGELS "
                "OP DEZE POORT: Sturm Graz - Ried AH Ried +0,75 @2,02 (+8,02 pp ruw, score 4,61). Dat "
                "is wat de poort vandaag kost en het staat daarom in het runrapport. GEEN VAN DE VIJF "
                "GEPUBLICEERDE REGELS WORDT ERDOOR GERAAKT: vier zijn een Under en een is een BTTS, dus "
                "alle vijf hebben side = None en staat de poort per ontwerp open. Dit is geen aanleiding "
                "om de vraag van 25 september opnieuw te stellen (Sec. 1e verbiedt dat zolang er niets "
                "wezenlijk verandert); de stand van beide reeksen staat in het runrapport onder \'Stand "
                "van het logboek\'. Die twee blijven twee populaties en mogen nooit worden opgeteld."
            ),
            "POORT9": (
                "BINDT EN HOUDT VIER SELECTIES TEGEN OVER TWEE DUELS. `unders.BINDS_FROM` is 12 oktober "
                "en `unders.TIERS` is (\'FULL\',), dus een Under op FULL moet 10,0 pp halen in plaats van "
                "8,0. De twee sterkste gevallen: MOLDE - FREDRIKSTAD Under 3,5 op +9,09 pp en SION - "
                "LAUSANNE Under 3,25 op +9,70 pp - beide midden in de band 8-10 pp die Sec. 6g op "
                "-47,7% over vijftien gevallen meet, de slechtste band van de hele reeks. Die rijen "
                "gaan als `doelpunten_onder` het schaduwlogboek in. LET OP DE TWEEDE: Sion - Lausanne "
                "is OOK de bovenste regel van de lijst, maar dan op de 3,5-lijn met +11,16 pp. Dezelfde "
                "wedstrijd, dezelfde kant, twee lijnen, en de poort scheidt ze - dat is correct, want "
                "een andere lijn is een andere bet (Sec. 1a), maar het betekent dat de gepubliceerde "
                "regel maar 1,16 pp boven de rem staat. En Molde staat WEL op de lijst, met zijn BTTS "
                "in plaats van zijn Under: poort 9 raakt BTTS per ontwerp niet (Sec. 1h punt 2, te "
                "weinig afgewikkelde BTTS-picks om iets te zeggen), dus het duel dat op de Under-kant "
                "wordt tegengehouden komt op de minder-doelpunten-kant alsnog binnen via een andere "
                "markt. Dat is geen omzeiling - het zijn twee verschillende markten met twee "
                "verschillende reeksen - maar het hoort hier te staan, want het effect op de "
                "doelpuntenkant van de dag is hetzelfde."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0645 (gepoold 1,0736 over 57 "
                "speeldagen) EN RUST OP ZES COMPETITIES: Greek Super League, Segunda Division, Serie B, "
                "2. Bundesliga, Swiss Super League en Austrian Bundesliga. uplift_observations sloeg er "
                "ZEVEN over, alle zeven met reden, en dat staat hier omdat een stil weggelaten "
                "waarneming hetzelfde probleem is als een stille truncatie (Sec. 3 Stage 5): VIER "
                "wegens \'geen xG in vorig of lopend seizoen\' (Czech First League, Croatian HNL, "
                "Hungarian NB I, Romanian SuperLiga) en DRIE wegens \'halverwege het seizoen\' - "
                "Eliteserien (24 van 30), Allsvenskan (25 van 30) en MLS (31 van 34). DIE DRIE KRIJGEN "
                "ROUTE \'lopend\' van league_level en halen hun niveau rechtstreeks uit het lopende "
                "seizoen, ongeschaald: Eliteserien thuis 1,812 / uit 1,382 / basis 1,681, Allsvenskan "
                "1,606 / 1,323 / 1,473 en MLS 1,824 / 1,402 / 1,541. DAT RAAKT TWEE VAN DE VIJF REGELS "
                "RECHTSTREEKS: Molde - Fredrikstad (Eliteserien) en Los Angeles FC - LA Galaxy (MLS) "
                "komen NIET uit de uplift-route maar uit het lopende seizoen zelf. De drie andere "
                "regels (twee in de Swiss Super League, een in de 2. Bundesliga) komen uit "
                "\'vorig+uplift\' en worden door de factor 1,0645 rechtstreeks geraakt."
            ),
            "BEURSKOERS": (
                "EEN VAN DE VIJF GEPUBLICEERDE REGELS STAAT OP EEN BEURS en daar is met "
                "oddsapi.net_price gerekend zoals Sec. 1a eist: THUN - LUGANO Under 3,5 staat bij "
                "MATCHBOOK op 1,88 bruto, na 2% commissie 1,8624 - en dat is de koers waarmee edge_pp "
                "en selection_score rekenen. Sec. 5 eist beide getallen naast elkaar omdat de gebruiker "
                "op de site 1,88 ziet; de edge van +7,57 pp is op 1,8624 gerekend en zou op de bruto "
                "koers hoger uitvallen. De vier andere regels staan bij gewone bookmakers zonder "
                "commissie: Unibet (SE) 1,77 voor Sion, William Hill 2,38 voor Molde, Pinnacle 1,95 "
                "voor Holstein Kiel en 1xBet 1,86 voor Los Angeles FC. Elke koers van de run is door "
                "net_price gehaald voordat er edge op is gemeten."
            ),
            "EERSTE_VOLLE_RUNDAG_OP_WINTERTIJD": (
                "DE KLOK IS VANNACHT TERUGGEGAAN - 03:00 CEST werd 02:00 CET - en dit is de eerste Run "
                "B die volledig op wintertijd draait. Run A van vanochtend heeft de hardgecodeerde "
                "+02:00 in de runscripten vervangen door ZoneInfo(\'Europe/Amsterdam\'); deze run doet "
                "hetzelfde en `odds_captured_at` staat dus op +01:00. NAGETROKKEN AAN EEN GETAL: Sion - "
                "Lausanne trapt af op 15:30Z en komt op 16:30 NL uit, niet op 17:30. Het raakt een "
                "gepubliceerde regel echt: LOS ANGELES FC - LA GALAXY trapt af op 01:00Z op 26 oktober, "
                "oftewel 02:00 NL in de nacht naar maandag - onder de oude +02:00 had daar 03:00 "
                "gestaan. Sec. 5 is daar onomwonden over: \'een aftraptijd die er een uur naast zit "
                "maakt de hele bet onbruikbaar\'. BetExplorer labelt in UK-tijd en dat is sinds "
                "vannacht GMT tegen CET, nog steeds precies een uur verschil, dus het venster "
                "[25.10. 08:00 NL, 26.10. 08:00 NL) is daar [25.10. 07:00, 26.10. 07:00) en de filter "
                "van de tweede bron hoefde niet te veranderen."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "INZETVENSTER": (
                "Het venster is [08:00 NL 25 okt, 08:00 NL 26 okt) en runwindow.py levert ZESENDERTIG "
                "duels, alle 36 met RunMatch.playable = True - er is dus geen enkel duel dat al was "
                "afgetrapt voordat de gebruiker kon inzetten. De eerste aftrap is 13:00 NL (Hradec "
                "Kralove - Jablonec) en de laatste 02:00 NL in de nacht naar maandag. EEN DUEL ZIT IN "
                "DE NACHTBAND WAARVOOR DEZE MODULE BESTAAT en stond op de UTC-daglijst van 26 oktober: "
                "LOS ANGELES FC - LA GALAXY, de Californische derby, om 02:00 NL. Onder de regel van "
                "voor 24 september was dat duel aan de run van morgen toegewezen en dan morgenochtend "
                "al gespeeld geweest - EN HET IS EEN GEPUBLICEERDE BET. Dat is de duurste les van deze "
                "runlijst (Sec. run-b.md, 24 september) en vandaag is het een van de vijf regels waard. "
                "include_carry_over is niet gebruikt (die is eenmalig geweest op 24 september); "
                "RunMatch.source_day staat op 2026-10-25 voor 35 duels en op 2026-10-26 voor LAFC - LA "
                "Galaxy."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "17 VAN DE 17 COMPETITIES BEVESTIGD, 36 duels tegen 36. Fotmob levert de daglijst en "
                "BetExplorer de fixturepagina per competitie - twee losse bronnen - en de controle slaat "
                "vandaag ook aan op de VIER competities die niets op de kalender hebben: BetExplorer "
                "geeft daar eveneens nul duels in het venster en noemt de eerstvolgende speeldag "
                "(Keuken Kampioen Divisie 30.10., English League One 27.10., English League Two 27.10., "
                "Serie A BRA 03.11.). Dat is juist de kant van de controle die iets kan opleveren, want "
                "een competitie die stil wegvalt door een fout id leest als GEEN WEDSTRIJD; hier zeggen "
                "twee bronnen hetzelfde. Geen enkele afwijking in de aantallen per competitie."
            ),
            "inkoop": (
                "48 CREDITS VAN EEN PLAFOND VAN 1337 (18.743 over bij 7 dagen tot de maandwissel, twee "
                "runs per dag). NEGEN van de dertien spelende competities hebben een sportkey en kregen "
                "ALLE NEGEN de volledige bulk-aanroep van 3 credits (h2h + spreads + totals = 27 "
                "credits), dus vijf van de zes markten; daarna 21 credits voor BTTS op de 21 duels met "
                "een kandidaat-edge (Sec. 1a stap 2, de vereniging van beide schalen). DIE TWEEDE RONDE "
                "HEEFT WAT OPGELEVERD: Molde - Fredrikstad staat op de lijst MET een BTTS, en in ronde "
                "1 zonder BTTS was dat duel op poort 9 gesneuveld met zijn Under. VIER spelende "
                "competities hebben GEEN sportkey - Czech First League, Croatian HNL, Hungarian NB I en "
                "Romanian SuperLiga - en draaien dus volledig op het gratis BetExplorer-marktgemiddelde "
                "als enige 1X2-bron, zonder enige andere markt. Dat raakt negen duels met samen twaalf "
                "selecties, alle twaalf een 1X2, en de edge valt daar systematisch te laag uit omdat "
                "een marktgemiddelde geen beste prijs is (conservatief, dus geen risico op te veel "
                "bets, maar niet vergelijkbaar). Dat die vier competities zonder prijzen ook precies "
                "vier van de vijf zonder xG zijn is geen toeval maar hetzelfde onderliggende feit: het "
                "zijn de kleinste competities van de lijst. MARKTBALANS-CONTROLE GEHAALD EN ZEER RUIM: "
                "negen van de negen inkoopbare competities kregen zowel een uitkomstmarkt als een "
                "doelpuntenmarkt uit dezelfde bulk, dus er is geen enkele competitie met alleen het een "
                "of het ander. split_budget(1337, 9) gaf (9, 9) en het plafond bond nergens. DAT IS HET "
                "PUNT BIJ DE EENZIJDIGE UITKOMST VAN VANDAAG: alle zes markten dongen mee - Over/Under "
                "126 selecties, Asian Handicap 106, 1X2 95, BTTS 42, Draw No Bet 25 en Double Chance 10 "
                "- en toch staan alle vijf de regels op de minder-doelpunten-kant. Die eenzijdigheid "
                "komt dus NIET uit de portemonnee maar uit de analyse, en dat is precies het verschil "
                "dat deze tabel zichtbaar moet maken (Sec. 5, Marktbalans)."
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

        # 24 okt 2026 — EEN COMPETITIE WAARVAN DE CAP ALLE DUELS HEEFT AFGEKAPT, KRIJGT
        # `AFGEKAPT` EN NIET `GEANALYSEERD`. Sec. 5 geeft vier statussen en eist er precies een per
        # competitie; `AFGEKAPT` is er een van ("wel dekking, maar buiten MAX_DEEP_ANALYSES
        # gevallen"). Op 24 oktober bond dat voor het eerst: 88 duels tegen een cap van 55, en bij
        # Czech First League (4 duels), Croatian HNL (2) en Keuken Kampioen Divisie (1) was er geen
        # enkel duel doorgerekend. Die als GEANALYSEERD neerzetten is precies de stille truncatie
        # die Stage 4 verbiedt: de dekkingstabel leest dan als volledige dekking.
        #
        # GEREPAREERD 25 okt 2026 (Run B), WANT DE REGEL VAN GISTEREN TOETSTE HET VERKEERDE.
        # Hij leidde de status af uit "nul duels met kandidaten", en dat is niet hetzelfde als
        # "afgekapt": een duel krijgt óók geen kandidaten als het op `data_tier = NONE` uitkomt,
        # en dan is de juiste status `BUITEN DATADEKKING` ("wedstrijden vandaag, maar geen
        # werkende onafhankelijke kansbron"). Vandaag kapt de cap NIETS af (36 duels op een
        # zondagcap van 55) en tóch kreeg Croatian HNL `AFGEKAPT`, puur omdat zijn enige duel
        # (Osijek – Rudes) op NONE staat: Kroatië heeft bij Fotmob geen tweede divisie, dus een
        # promovendus is daar niet om te rekenen (Sec. 4). Dat is een onware status — hij zegt dat
        # de cap iets heeft weggegooid wat de cap niet heeft aangeraakt — en hij verbergt
        # bovendien een duel: `progress.py verify` sloeg de hele AFGEKAPT-competitie over en
        # meldde "3 zonder kansbron" waar er 4 op NONE staan.
        #
        # De status wordt daarom bepaald op de REDEN en niet op de uitkomst: eerst de
        # afkappingslijst van Stage 4 (die noemt de duels bij naam), dan de tier.
        afgekapt_namen = {m for m in (res["afkapping"].get("lijst") or [])}
        for comp, blok in st["competitions"].items():
            n_door = sum(1 for m in blok["matches"] if m.get("all_candidates"))
            n_trunc = sum(1 for m in blok["matches"] if m["match"] in afgekapt_namen)
            n_none = sum(1 for m in blok["matches"] if m.get("tier") == "NONE")
            if n_door:
                status = "GEANALYSEERD"
            elif n_trunc:
                status = "AFGEKAPT"
            elif n_none == len(blok["matches"]):
                status = "BUITEN DATADEKKING"
            else:
                status = "AFGEKAPT"
            entry = {"status": status, "matches": []}
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
        s3 = json.load(open("tmp-run/rb_oct25_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct25_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct25_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct25_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

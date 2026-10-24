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

DAG = "2026-10-24"
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
CAPTURED = "2026-10-24T05:15:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct24_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=0.986, b=-0.009 "
                "op 5487 afgerekende gevallen, fitted_through 2026-10-23. Dat is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die Sec. 6b-5c sinds 30 sep "
                "eist). DE CORRECTIE IS OPNIEUW VRIJWEL DE IDENTITEIT: ze haalt 0,1 pp af op 30%, "
                "0,2 pp op 50% en 0,5 pp op 80% — het ruwe model zei gemiddeld 33,3% en het gebeurde "
                "33,3%. Op de vijf gepubliceerde regels verschuift ze de kans met minder dan een halve "
                "procentpunt, en bet_beide is bij alle vijf FALSE omdat geen van de vijf zijn lat op "
                "beide schalen haalt. Lees die identiteit zoals Sec. 1e punt 3 voorschrijft: de reeks "
                "is de ONGESELECTEERDE ijksteekproef en breder dan de staart waarop deze routine "
                "speelt. Dat ze niets corrigeert betekent niet dat er niets scheef staat — ledger.py "
                "zegt over 290 afgerekende topselectie-bets dat het model 178,2 winnaars verwachtte en "
                "er 133 kwamen."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "Sec. 5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ALLE ZEVENTIEN COMPETITIES VAN DE RUNLIJST SPELEN VANDAAG, met samen ACHTENTACHTIG "
                "duels in het inzetvenster — de volste dag die deze runlijst tot nu toe heeft gehad en "
                "ruim boven de cap. Per competitie: MLS 14, English League One 12, English League Two "
                "11, Serie B 7, Serie A BRA 7, Segunda Division 5, Czech First League 4, Allsvenskan 4, "
                "2. Bundesliga 4, Greek Super League 3, Hungarian NB I 3, Romanian SuperLiga 3, Swiss "
                "Super League 3, Austrian Bundesliga 3, Eliteserien 2, Croatian HNL 2 en Keuken "
                "Kampioen Divisie 1. GEEN ENKELE COMPETITIE OP `GEEN WEDSTRIJD`. scripts/idcheck.py gaf "
                "voor alle 33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode 0); dat de "
                "controle vandaag niets te melden heeft komt doordat er geen stille competitie is, niet "
                "doordat hij niet heeft gekeken. De tweede bron bevestigde de daglijst voor 17 van de "
                "17 competities (BetExplorer tegen Fotmob, 88 duels tegen 88, geen enkele afwijking)."
            ),
            "DE_CAP_BINDT_VANDAAG_HARD_EN_DAT_IS_DE_EERSTE_BEVINDING": (
                "MAX_DEEP_ANALYSES = 55 (zaterdag) EN ER STAAN 88 DUELS, DUS ER ZIJN 33 DUELS "
                "AFGEKAPT — bijna vier op de tien. Dat is geen detail en het is geen stille truncatie: "
                "de volledige lijst staat in run-state onder `afkapping.lijst`. De laagste wedstrijd die "
                "het nog haalde is Djurgarden – Orgryte met datarijkdom 7,0; de hoogste die afviel is "
                "Stevenage – Milton Keynes Dons met 6,5. De spreiding over de hele run is 4,5 tot 8,0, "
                "dus de scheiding bij de cap is een halve punt op een schaal van tien — met andere "
                "woorden: de afkapping snijdt door een vlakke verdeling, precies wat Sec. 3 Stage 4 op "
                "5 september heeft gemeten (de betkans is vlak over de hele rangorde, dus een afgekapt "
                "duel is niet slechter maar gewoon weg). DRIE COMPETITIES ZIJN ER VOLLEDIG DOOR "
                "WEGGEVALLEN en krijgen daarom status AFGEKAPT in plaats van GEANALYSEERD: Czech First "
                "League (4 duels), Croatian HNL (2) en Keuken Kampioen Divisie (1) — alle drie "
                "competities zonder xG, die op de primaire sorteersleutel (FULL boven LIGHT) achteraan "
                "beginnen. DE LOOPTIJD IS DE ECHTE GRENS, niet de credits: 78 van 1179 credits "
                "gebruikt, dus het plafond bond nergens; wat bindt is dat de rapporten om 06:30 klaar "
                "moeten staan (Sec. 0)."
            ),
            "DE_LIJST_IS_EEN_RANGORDE_EN_GEEN_VONDST": (
                "VIJF REGELS, WAARVAN TWEE HUN EIGEN LAT HALEN EN DRIE OP RANGORDE OP DE LIJST STAAN "
                "(Sec. 5b). Boven de lat van 8,0: Columbus Crew – Toronto FC Under 3,5 @1,79 met "
                "+16,60 pp, en Sudtirol – Sampdoria 'beide ploegen scoren — nee' @2,0976 met +9,62 pp. "
                "Eronder, en dus puur op rangorde: WSG Tirol Draw No Bet @1,80 (+7,59 pp), Real Salt "
                "Lake Under 3,5 @1,74 (+7,22 pp) en Portland Timbers Under 3,5 @2,00 (+7,72 pp). Van de "
                "822 doorgerekende selecties over 54 duels haalden er VIER alle negen poorten inclusief "
                "de drempel; er passen vijf regels in de zaterdaglijst, dus de drempel bindt vandaag "
                "niet als grens maar staat als label per regel. Lees de lijst als 'dit is het sterkste "
                "dat het model vandaag ziet' en niet als 'hier ligt waarde'."
            ),
            "WAT_ER_TEGEN_DE_DRIE_UNDERS_PLEIT_EN_DAT_IS_PINNACLE": (
                "DIT IS DE ZWAARSTE WAARSCHUWING VAN DEZE RUN EN ZE HOORT VOORAAN. DRIE VAN DE VIJF "
                "REGELS ZIJN EEN UNDER IN DE MLS, EN ALLE DRIE STAAN BOVEN HET PINNACLE-OORDEEL OP "
                "PRECIES DE KANT WAARVAN Sec. 6g MEET DAT ZE FOUT STAAT. Op Pinnacle's eigen lijn, per "
                "lijn de-vigd: COLUMBUS CREW – TORONTO FC +22,67 pp (Pinnacle lijn 3,25 op 1,97/1,90, "
                "marge 3,4%, de-vigd 50,9% voor de Under; het model zegt 73,6%) — dat is de GROOTSTE "
                "afstand van alle 51 gemeten paren van vandaag, en het is de bovenste regel van de "
                "lijst. REAL SALT LAKE – ST. LOUIS CITY +11,09 pp (lijn 3,25, Pinnacle 53,0% / model "
                "64,1%). PORTLAND TIMBERS – CHARLOTTE FC +8,21 pp (lijn 3,50, Pinnacle 49,9% / model "
                "58,1%). In doelpunten: het model verwacht bij Columbus 2,60 doelpunten waar Pinnacle's "
                "lijn op ongeveer 3,2 staat, en dat verschil van ruim een halve goal is exact de "
                "grootte die `margins.py goalbias` meet in de duels waar werkelijk een Under is "
                "gespeeld (+0,590 doelpunt per duel, z = +3,39 over 90 gevallen) — bovenop de vormfout "
                "die P(Under 2,5) over 1515 duels 2,6 pp te hoog zet. POORT 9 RAAKT GEEN VAN DE DRIE: "
                "Columbus haalt met +16,60 pp de verzwaarde lat van 10,0 ruim, en de twee andere komen "
                "niet eens aan de 8,0 — de poort bijt alleen in de band 8–10 pp. Op 1X2 is het beeld "
                "juist gunstig: over 51 duels staat het model gemiddeld 4,03 pp van het "
                "Pinnacle-oordeel af bij een gemiddelde Pinnacle-marge van 4,14%, en bij Columbus is "
                "die afstand op de uitkomstmarkt klein (1,4 / 3,4 / 2,1 pp). Het verschil zit dus niet "
                "in wie er wint maar in hoeveel er valt."
            ),
            "POORT5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
                "POORT 5 VANGT 606 VAN DE 822 SELECTIES WEG (73,7%) — 'tweede_methode', de twee "
                "methodes verslaan de markt niet dezelfde kant op. Daarna 92 op de edge (11,2%), 55 op "
                "poort 8 (6,7%), 33 op de koersband (4,0%), 14 op robuustheid (1,7%), 13 op poort 7 "
                "(1,6%) en 1 op poort 9. Acht selecties kwamen door alles heen. Die 73,7% ligt in "
                "dezelfde band als de afgelopen weken en voegt er geen nieuwe waarneming aan toe. "
                "TWAALF DUELS VALLEN VOLLEDIG OP DEZE POORT ('data conflicterend' als reden van het "
                "hele duel): AEK Athens – Panetolikos, Cordoba – Eibar, Avellino – Padova, Hertha BSC – "
                "Arminia Bielefeld, Magdeburg – Karlsruher SC, Blackpool – Mansfield Town, Cheltenham "
                "Town – Newport County, Barnet – Oldham Athletic, CF Montreal – Nashville SC, Sporting "
                "Kansas City – Austin FC, Palmeiras – RB Bragantino en Vitoria-vervangend geen. Op de "
                "RUWE schaal staat CF Montreal – Nashville SC als vierde van de dag (AH +1,5 @1,57, "
                "+9,39 pp ruw) en die rij gaat als `tweede_methode` het schaduwlogboek in."
            ),
            "POORT7": (
                "BINDT EN HOUDT DERTIEN SELECTIES TEGEN, OVER VIER DUELS, EN HIJ RAAKT GEEN VAN DE VIJF "
                "GEPUBLICEERDE REGELS. PHILADELPHIA UNION – NEW ENGLAND REVOLUTION: New England mist "
                "35% van de selectiewaarde tegen 13% bij Philadelphia (Mamadou Fofana tot half "
                "november, Alhassan Yusuf en Jack Harrison eind oktober) — drie selecties op de "
                "New England-kant eruit, en dit was het sterkste duel van de dag op die kant. FC DALLAS "
                "– SAN JOSE EARTHQUAKES: San Jose mist 33% tegen 10% (Benji Kikanovic half november, "
                "Niko Tsakiris en Jonathan Gonzalez begin november) — vijf selecties eruit, waaronder "
                "de AH +1,5 @1,51 die op de RUWE lijst als vierde van de dag staat (+11,35 pp). "
                "MAGDEBURG – KARLSRUHER SC vier selecties en MIRASSOL – SAO PAULO een (Mirassol mist "
                "26% tegen 7%: Andre Luis geschorst, Jose Aldo twijfelachtig, Negueba de rest van het "
                "seizoen). STADIONCONTROLE: 88 duels, EEN ALARM — PALMEIRAS – RB BRAGANTINO wordt "
                "gespeeld in Arena Crefisa Barueri (Barueri, Sao Paulo) en niet in Palmeiras' eigen "
                "Nubank Parque. Dat duel levert geen bet (het valt op poort 5), maar Sec. 1c eist dat "
                "een verplaatsing wordt genoemd ook als de poort opengaat, en thuisvoordeel is de "
                "aanname waar het model het zwaarst op leunt. OPSTELLINGEN: 83 van de 88 op "
                "'lastStarting11', 2 voorspeld (Hartberg – Wolfsberger AC en WSG Tirol – Grazer AK, de "
                "twee Oostenrijkse duels van 17:00) en 3 zonder opstellingsblok — dezelfde "
                "klokbevinding als elke ochtend, tien tot vierentwintig uur voor de aftrap. De context "
                "van ALLE 88 duels is opgehaald en vastgelegd, ook van de 33 die de cap heeft afgekapt, "
                "zoals Sec. 1c eist; de steekproef van ctxlog.py is dus volledig."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (Sec. 1e); sides.check() is met "
                "today=2026-10-24 aangeroepen zoals Sec. 1e eist, zodat het vervallen venster van 25 "
                "t/m 30 september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. HIJ "
                "HOUDT 55 SELECTIES TEGEN OVER 17 DUELS — het grootste aantal in weken, en dat komt "
                "doordat deze zaterdag veel duels met een duidelijke favoriet heeft. Vijf selecties "
                "elk bij Young Boys – St. Gallen, Houston Dynamo – Minnesota United en Portland Timbers "
                "– Charlotte FC; vier elk bij Asteras Tripolis – Levadiakos, Hamarkameratene – "
                "Rosenborg, AFC Wimbledon – Wycombe Wanderers, Notts County – Stockport County en Red "
                "Bull New York – Inter Miami. OP DE RUWE LIJST STAAN TWEE VAN DE VIJF BOVENSTE REGELS "
                "OP DEZE POORT: Asteras Tripolis – Levadiakos Double Chance @1,83 (+15,76 pp ruw, "
                "score 11,10) en Hamarkameratene – Rosenborg AH +1 @1,88 (+15,42 pp ruw, score 10,58). "
                "Dat is precies wat de poort kost en het staat daarom in het runrapport. GEEN VAN DE "
                "VIJF GEPUBLICEERDE REGELS WORDT ERDOOR GERAAKT: drie zijn een Under en een is een "
                "BTTS (geen kant, poort staat open), en WSG Tirol is de FAVORIETENkant. Dit is geen "
                "aanleiding om de vraag van 25 september opnieuw te stellen (Sec. 1e verbiedt dat "
                "zolang er niets wezenlijk verandert); de stand van beide reeksen staat in het "
                "runrapport onder 'Stand van het logboek' — `underdog` op −2,4% over 183 gevallen, "
                "`underdog_ruw` op −8,8% over 17. Die twee blijven twee populaties."
            ),
            "POORT9": (
                "BINDT EN HOUDT VANDAAG PRECIES EEN SELECTIE TEGEN, EN DAT IS DE EERSTE KEER IN DAGEN "
                "DAT HIJ WERKELIJK BIJT. `unders.BINDS_FROM` is 12 oktober en `unders.TIERS` is "
                "('FULL',), dus een Under op FULL moet 10,0 pp halen in plaats van 8,0. Het geval: SAN "
                "DIEGO FC – SEATTLE SOUNDERS FC, Under 3,5 @1,89 op +8,43 pp — midden in de band 8–10 "
                "pp die Sec. 6g op −47,7% over vijftien gevallen meet, de slechtste band van de hele "
                "reeks. De rij gaat als `doelpunten_onder` het schaduwlogboek in en brengt die reeks op "
                "13 kandidaten (10 afgewikkeld, −11,0%) — nog ver onder de ~30 die Sec. 6d eist, dus "
                "niet lezen. LET OP WAT DIT NIET DOET: de drie Unders die WEL op de lijst staan raakt "
                "hij niet. Columbus haalt de 10,0 ruim (+16,60 pp) en Real Salt Lake (+7,22) en "
                "Portland (+7,72) komen niet aan de 8,0, dus liggen onder de band waarin de poort "
                "werkt. Daar zit een scheefheid in het ontwerp die eerlijk benoemd hoort: de rem pakt "
                "de band 8–10 pp, terwijl Sec. 5b sinds 20 september regels publiceert die HELEMAAL "
                "ONDER de drempel liggen (0–8 pp), en daar meet Sec. 6g −34,1% over 26 gevallen. Dat is "
                "geen reden om de poort vandaag te verzetten — Sec. 1h en Sec. 6d verbieden dat "
                "uitdrukkelijk — maar het is de waarneming die bij deze vijf regels hoort."
            ),
            "PINNACLE": (
                "STAP 2 VAN STAGE 5 — het scherpste publieke expertoordeel, LOS van de beste prijs "
                "waarop gespeeld wordt en nooit in my_prob (Sec. 2). Pinnacle noteerde 51 van de 54 "
                "doorgerekende duels op 1X2 en 51 (duel, lijn)-paren op de totalen; de duels uit de "
                "vijf competities zonder sportkey (Czech, Croatian, Hungarian, Romanian, KKD) zijn niet "
                "te toetsen, maar die zijn vandaag vrijwel allemaal al door de cap afgekapt. OP 1X2 "
                "STAAT HET MODEL GEMIDDELD 4,03 pp VAN PINNACLE AF bij een gemiddelde Pinnacle-marge "
                "van 4,14% — ruimer dan de 1,71 pp van 23 oktober, en de uitschieters zijn Palmeiras – "
                "RB Bragantino (−14,46 pp op de thuiszege), CF Montreal – Nashville SC (+12,09 pp) en "
                "FC Dallas – San Jose (−10,67 pp). OP DE TOTALEN IS HET BEELD ONGUNSTIGER EN DAT IS HET "
                "PATROON VAN DE VIERDE WEEK OP RIJ: gemiddeld +1,39 pp boven Pinnacle op de Under-kant, "
                "met 30 van de 51 paren erboven. Zie het blok over de drie Unders hierboven voor wat "
                "dat bij de gepubliceerde regels doet. Let op de rekenwijze: deze vergelijking zet een "
                "zuiver Poisson-grid zonder Dixon-Coles tegen strikt 'minder dan de lijn', dus op een "
                "kwartlijn is het een benadering."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0743 (gepoold 1,0818 over 79 "
                "speeldagen) EN RUST OP ACHT COMPETITIES: Greek Super League, Segunda Division, Serie "
                "B, 2. Bundesliga, Swiss Super League, Austrian Bundesliga, English League One en "
                "English League Two. Dat is de breedste pool in weken — de afgelopen Run B-dagen "
                "draaiden op vier en zelfs op een. uplift_observations sloeg er NEGEN over, alle negen "
                "met reden, en dat staat hier omdat een stil weggelaten waarneming hetzelfde probleem "
                "is als een stille truncatie (Sec. 3 Stage 5): VIJF wegens 'geen xG in vorig of lopend "
                "seizoen' (Czech First League, Croatian HNL, Hungarian NB I, Romanian SuperLiga, Keuken "
                "Kampioen Divisie) en VIER wegens 'halverwege het seizoen' — Eliteserien (23 van 30), "
                "Allsvenskan (25 van 30), MLS (31 van 34) en Serie A BRA (32 van 38). DIE VIER KRIJGEN "
                "ROUTE 'lopend' van league_level en halen hun niveau rechtstreeks uit het lopende "
                "seizoen: Eliteserien thuis 1,832 / uit 1,375 / basis 1,674, Allsvenskan 1,603 / 1,314 "
                "/ 1,472, MLS 1,618 / 1,420 / 1,562 en Serie A BRA 1,524 / 1,138 / 1,337. DAT RAAKT "
                "DRIE VAN DE VIJF REGELS RECHTSTREEKS, want alle drie de Unders staan in de MLS en "
                "komen dus NIET uit de uplift-route maar uit het lopende seizoen zelf, ongeschaald. De "
                "twee andere regels (Sudtirol in Serie B, WSG Tirol in de Austrian Bundesliga) komen "
                "wel uit 'vorig+uplift' en worden door de factor 1,0743 rechtstreeks geraakt."
            ),
            "BEURSKOERS": (
                "EEN VAN DE VIJF GEPUBLICEERDE REGELS STAAT OP EEN BEURS en daar is met "
                "oddsapi.net_price gerekend zoals Sec. 1a eist: SUDTIROL – SAMPDORIA 'beide ploegen "
                "scoren — nee' staat bij MATCHBOOK op 2,12 bruto, na 2% commissie 2,0976 — en dat is de "
                "koers waarmee edge_pp en selection_score rekenen. Sec. 5 eist beide getallen naast "
                "elkaar omdat de gebruiker op de site 2,12 ziet; de edge van +9,62 pp is op 2,0976 "
                "gerekend en zou op de bruto koers hoger uitvallen. De vier andere regels staan bij "
                "gewone bookmakers zonder commissie. Over de hele run stond de beste prijs in een "
                "aanzienlijk deel van de gevallen bij een beurs, en elke koers is door net_price "
                "gehaald voordat er edge op is gemeten."
            ),
            "DE_KLOK_GAAT_VANNACHT_TERUG_EN_DAT_RAAKT_TWEE_GEPUBLICEERDE_REGELS": (
                "DIT IS DE TWEEDE BEVINDING VAN DEZE RUN EN HET IS EEN GEREPAREERDE FOUT, GEEN "
                "WAARSCHUWING. De EU zet de klok om op de laatste zondag van oktober om 01:00 UTC, en "
                "dat is 25 oktober 2026 — de nacht NA deze rundag, midden in het inzetvenster. ACHT van "
                "de 88 duels trappen daarna af: vijf MLS-duels om 01:30Z, twee om 02:30Z en Santos – "
                "Bahia om 01:00Z. De docstring van `runwindow.NL` noemt dit sinds 24 september als "
                "openstaand punt — `runwindow.kickoff_nl` rekent met zoneinfo en deed het dus goed, "
                "maar de RUNSCRIPTEN hadden een hardgecodeerde +02:00 en zetten die acht duels een uur "
                "TE LAAT. VANDAAG IS DE EERSTE DAG DAT DAT BINDT, en het raakt twee gepubliceerde "
                "regels: Real Salt Lake – St. Louis City trapt af om 02:30 NL (CET) en niet om 03:30, "
                "Portland Timbers – Charlotte FC om 03:30 NL en niet om 04:30. Sec. 5 is daar "
                "onomwonden over: 'een aftraptijd die er een uur naast zit maakt de hele bet "
                "onbruikbaar'. `rb_oct24_analyze.py` en `rb_oct24_publiceer.py` gebruiken nu "
                "ZoneInfo('Europe/Amsterdam') met de vaste +02:00 alleen als terugval, en de analyse is "
                "daarna opnieuw gedraaid (ronde 3) — met identieke uitkomsten op alles behalve de "
                "tijden. `scripts/report.py` deed het al goed voor de picks zelf (het rekent met "
                "zoneinfo op het kickoff-veld), dus de HTML-pagina stond nooit fout; wat fout stond is "
                "het `kickoff_nl`-veld in run-state waarmee de ranglijsten worden gerenderd."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "INZETVENSTER": (
                "Het venster is [08:00 NL 24 okt, 08:00 NL 25 okt) en runwindow.py levert "
                "ACHTENTACHTIG duels, alle 88 met RunMatch.playable = True — er is dus geen enkel duel "
                "dat al was afgetrapt voordat de gebruiker kon inzetten. De spreiding is groot: de "
                "eerste aftrap is 12:30 NL (Huddersfield – Wigan en Luton – Leicester in League One) en "
                "de laatste 03:30 NL in de nacht naar zondag (Portland Timbers en San Diego FC). ACHT "
                "DUELS ZITTEN IN DE NACHTBAND WAARVOOR DEZE MODULE BESTAAT en stonden op de "
                "UTC-daglijst van 25 oktober: vijf MLS-duels om 02:30 NL, twee om 03:30 NL en Santos – "
                "Bahia om 02:00 NL. Onder de regel van voor 24 september waren die acht aan de run van "
                "morgen toegewezen en morgenochtend allemaal al gespeeld geweest — en TWEE ERVAN ZIJN "
                "EEN GEPUBLICEERDE BET (Real Salt Lake – St. Louis City en Portland Timbers – Charlotte "
                "FC). Dat is de duurste les van deze runlijst (Sec. run-b.md, 24 september) en vandaag "
                "is het twee van de vijf regels waard. include_carry_over is niet gebruikt (die is "
                "eenmalig geweest op 24 september); RunMatch.source_day staat op 2026-10-24 voor 80 "
                "duels en op 2026-10-25 voor de acht nachtduels."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "17 VAN DE 17 COMPETITIES BEVESTIGD, 88 duels tegen 88. Fotmob levert de daglijst en "
                "BetExplorer de fixturepagina per competitie — twee losse bronnen — en op een dag "
                "waarop alle zeventien competities spelen is er geen competitie die stil kan wegvallen, "
                "wat de controle vandaag makkelijker maakt dan hij meestal is. Geen enkele afwijking, "
                "ook niet in de aantallen per competitie (MLS 14 tegen 14, English League One 12 tegen "
                "12, English League Two 11 tegen 11). De tijdzonerekening: BetExplorer labelt in "
                "UK-tijd, dus het venster [24.10. 08:00 NL, 25.10. 08:00 NL) is daar [24.10. 07:00, "
                "25.10. 07:00) — en LET OP dat die omrekening vannacht zelf verschuift, want ook het "
                "Verenigd Koninkrijk gaat van BST naar GMT; voor de grens van 07:00 maakt dat geen "
                "verschil omdat beide zones even veel opschuiven."
            ),
            "inkoop": (
                "78 CREDITS VAN EEN PLAFOND VAN 1179 (18.884 over bij 8 dagen tot de maandwissel, twee "
                "runs per dag). TWAALF van de zeventien spelende competities hebben een sportkey en "
                "kregen ALLE TWAALF de volledige bulk-aanroep van 3 credits (h2h + spreads + totals = "
                "36 credits), dus vijf van de zes markten; daarna 42 credits voor BTTS op de 42 duels "
                "met een kandidaat-edge (Sec. 1a stap 2, de vereniging van beide schalen). Die tweede "
                "ronde heeft wat opgeleverd: TWEE van de vijf gepubliceerde regels zijn een BTTS "
                "(Sudtirol – Sampdoria op de lijst, DC United – FC Cincinnati als lijstlengte-rij), en "
                "in ronde 1 zonder BTTS waren er twee bets boven de drempel in plaats van vier. VIJF "
                "spelende competities hebben GEEN sportkey — Czech First League, Croatian HNL, Hungarian "
                "NB I, Romanian SuperLiga en Keuken Kampioen Divisie — en draaien dus volledig op het "
                "gratis BetExplorer-marktgemiddelde als enige 1X2-bron, zonder enige andere markt. Dat "
                "raakt dertien duels, maar NEGEN ERVAN ZIJN AL DOOR DE CAP AFGEKAPT, dus in de analyse "
                "gaat het om vier duels (drie Romanian SuperLiga en Zalaegerszeg – Kisvarda) met samen "
                "twaalf selecties, alle twaalf een 1X2. Dat die vijf competities zonder prijzen ook "
                "precies de vijf zonder xG zijn is geen toeval maar hetzelfde onderliggende feit: het "
                "zijn de kleinste competities van de lijst. MARKTBALANS-CONTROLE GEHAALD EN ZEER RUIM: "
                "twaalf van de twaalf inkoopbare competities kregen zowel een uitkomstmarkt als een "
                "doelpuntenmarkt uit dezelfde bulk, dus er is geen enkele competitie met alleen het een "
                "of het ander. split_budget(1179, 12) gaf (12, 12) en het plafond bond nergens."
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
        # gevallen"). Vandaag bindt dat voor het eerst sinds deze runlijst een volle zaterdag heeft:
        # 88 duels tegen een cap van 55, en bij Czech First League (4 duels), Croatian HNL (2) en
        # Keuken Kampioen Divisie (1) is er geen enkel duel doorgerekend. Die als GEANALYSEERD
        # neerzetten is precies de stille truncatie die Stage 4 verbiedt: de dekkingstabel leest dan
        # als volledige dekking van zeventien competities.
        for comp, blok in st["competitions"].items():
            n_door = sum(1 for m in blok["matches"] if m.get("all_candidates"))
            entry = {"status": "GEANALYSEERD" if n_door else "AFGEKAPT", "matches": []}
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
        s3 = json.load(open("tmp-run/rb_oct24_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct24_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct24_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct24_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

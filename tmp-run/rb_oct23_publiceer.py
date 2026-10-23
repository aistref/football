"""Run B 23 okt 2026 onder §5b: run-state, picks en logboeken.

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

DAG = "2026-10-23"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-23T05:18:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct23_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.0006, b=0.0004 "
                "op 5400 afgerekende gevallen, fitted_through 2026-10-22. Dat is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist). "
                "DE CORRECTIE IS VANDAAG DE IDENTITEIT TOT IN DE TWEEDE DECIMAAL: over de hele speelbare "
                "band verschuift ze een kans met minder dan 0,05 procentpunt — het ruwe model zei "
                "gemiddeld 33,3% en het gebeurde 33,3%. Op de drie gepubliceerde regels telt ze +0,01 tot "
                "+0,02 pp bij, en bet_beide is bij alle drie FALSE omdat geen van drieën zijn lat haalt, "
                "op geen van beide schalen. Lees de identiteit zoals §1e punt 3 voorschrijft: de reeks is "
                "de ONGESELECTEERDE ijksteekproef uit calibration.jsonl en breder dan de staart waarop "
                "deze routine speelt. Dat ze niets meer corrigeert betekent niet dat er niets scheef "
                "staat — ledger.py zegt over 381 afgerekende bets dat het model 225,1 winnaars verwachtte "
                "en er 172 kwamen."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ACHT van de zeventien competities speelden, met samen NEGENTIEN duels in het "
                "inzetvenster: Keuken Kampioen Divisie (9 — een volle speelronde op vrijdagavond), "
                "Allsvenskan (2), Romanian SuperLiga (2), 2. Bundesliga (2), Segunda División (1), "
                "Serie B (1), Austrian Bundesliga (1) en Série A (BRA) (1, om 01:00 NL in de nacht naar "
                "24 oktober). NEGEN competities hadden GEEN WEDSTRIJD: Czech First League, Greek Super "
                "League, Eliteserien, Croatian HNL, Hungarian NB I, Swiss Super League, English League "
                "One, English League Two en MLS. scripts/idcheck.py gaf voor alle 33 fotmob_id's uit "
                "coverage.json een bruikbare stand (afsluitcode 0), dus geen enkele competitie is stil "
                "uit de lijst verdwenen — ook niet die negen die vandaag niet spelen, en dat is precies "
                "waarom die controle bestaat. De tweede bron bevestigde de daglijst voor 17 van de 17 "
                "competities (BetExplorer tegen Fotmob, 19 duels tegen 19)."
            ),
            "DE_LIJST_IS_EEN_RANGORDE_EN_GEEN_VONDST": (
                "DRIE REGELS, EN GEEN ENKELE HAALT ZIJN EIGEN LAT. Alle drie staan op de lijst op grond "
                "van RANGORDE (§5b) en niet omdat er een voordeel is gevonden: Darmstadt – St. Pauli "
                "Under 2,75 @1,97 met +9,77 pp tegen een LIGHT-lat van 16,0; Granada – Real Valladolid "
                "Over 2,25 @1,86 met +4,54 pp tegen een FULL-lat van 8,0; TOP Oss – Jong Ajax thuiszege "
                "@2,03 met +6,72 pp tegen een LIGHT-lat van 16,0. Van de 127 doorgerekende selecties over "
                "19 duels haalde er NUL alle negen poorten inclusief de drempel. Lees de lijst dus als "
                "'dit is het sterkste dat het model vandaag ziet' en niet als 'hier ligt waarde'."
            ),
            "DE_LIJST_IS_DRIE_LANG_OMDAT_MAX_LIGHT_BINDT_EN_NIET_OMDAT_ER_DRIE_KANDIDATEN_WAREN": (
                "DIT IS DE BEVINDING VAN DEZE RUN EN ZE HOORT VOORAAN. MAX_SHORTLIST is 5 op vrijdag en "
                "er staan er DRIE op de lijst. De reden is niet dat de kandidaten op waren — er bleven er "
                "zes over — maar MAX_LIGHT_IN_SHORTLIST = 2 (§0). De rangorde is: 1 Darmstadt (LIGHT), "
                "2 Granada (FULL), 3 TOP Oss (LIGHT), en daarmee is het LIGHT-quotum vol. Alles wat "
                "daarna komt is ÓÓK LIGHT — FC Volendam 1 @1,60 (+5,02 pp), Västerås SK Under 2,5 @2,28 "
                "(+5,29 pp), Vitesse 1 @2,20 (+3,49 pp), Bochum Over 3,5 @2,078 (+3,35 pp), FC Den Bosch "
                "1 @1,70 (+3,20 pp), Botoșani X @3,59 (+1,64 pp) — dus de lijst stopt op drie. DAT IS "
                "GEEN FOUT MAAR DE REGEL DIE WERKT: deze runlijst is per ontwerp zwak bedeeld met xG "
                "(vijf van de zeventien competities hebben er geen) en zonder dat plafond zou de "
                "vrijdaglijst van vijf vandaag uit vier of vijf LIGHT-regels bestaan. HET KOST WEL "
                "IETS, en dat hoort er net zo eerlijk bij: deze zes zijn GEEN `lijstlengte`-rijen, want "
                "§5b reserveert die naam voor selecties die alle poorten ÉN hun drempel halen, en geen "
                "van deze zes haalt zijn lat van 16,0. Ze gaan dus als gewone `edge`-rijen het "
                "schaduwlogboek in en zijn daarna niet meer te onderscheiden van de rest."
            ),
            "WAT_ER_TEGEN_DE_TWEE_DOELPUNTENREGELS_PLEIT_EN_DAT_IS_PINNACLE": (
                "DE ZWAARSTE WAARSCHUWING VAN VANDAAG KOMT VAN STAP 2 VAN STAGE 5 EN NIET VAN DE EIGEN "
                "POORTEN — en ze is scherper dan gebruikelijk, want BIJ BEIDE DOELPUNTENREGELS IS "
                "PINNACLE ZELF DE BESTE PRIJS. De bet wordt dus tegen de scherpste bookmaker van de markt "
                "gespeeld en niet tegen een zachte boek dat achterloopt; dat is een zwaardere claim dan "
                "normaal. DARMSTADT – ST. PAULI: Pinnacle noteert lijn 2,75 op 1,90/1,97 met een marge "
                "van 3,4% en zegt daarmee de-vigd 49,1% voor de Under; het model zegt 60,5%. Dat is "
                "+11,4 pp MEER aan de Under-kant dan Pinnacle, en precies de richting waarvan §6g meet "
                "dat ze structureel fout staat (de vormfout in het scoregrid zet P(Under) bij élk duel "
                "ongeveer 2 pp te hoog, en bovenop die fout meet §6g +0,616 doelpunt per duel in de "
                "duels waar werkelijk een Under is gespeeld, z = +3,49 over 88 gevallen). POORT 9 RAAKT "
                "DEZE REGEL NIET, want hij geldt alleen op FULL en Darmstadt – St. Pauli is LIGHT — dat "
                "is de keuze van de gebruiker van 12 oktober en geen omissie, maar het betekent wel dat "
                "de enige rem op de Under-kant hier niet staat. GRANADA – REAL VALLADOLID: Pinnacle "
                "noteert lijn 2,25 op 1,86/2,02 (marge 3,3%), de-vigd 52,1% voor de Over; het model zegt "
                "58,3%, dus +6,2 pp meer aan de OVER-kant. Die richting is de gunstige van de twee — §6g "
                "meet dat de Over-kant juist meebetaalt aan dezelfde vormfout (+10,6% over 62 gevallen "
                "tegen −16,5% over 76 Unders) — maar +6,2 pp tegen een boek met 3,3% marge blijft een "
                "grote claim. Op 1X2 is de afstand klein: 1,71 pp gemiddeld over de zes duels met een "
                "Pinnacle-prijs, bij een gemiddelde Pinnacle-marge van 4,34%."
            ),
            "DE_DERDE_REGEL_DRAAIT_OP_EEN_MARKTGEMIDDELDE_EN_DAT_IS_IETS_ANDERS": (
                "TOP OSS – JONG AJAX IS DE ENIGE REGEL ZONDER BOOKMAKERPRIJS. De Keuken Kampioen Divisie "
                "heeft geen sportkey bij The Odds API, dus de enige 1X2-bron is het BetExplorer-"
                "marktgemiddelde over 16 boeken (1 @2,03, X @3,69, 2 @3,08) en er is voor dit duel GEEN "
                "ENKELE andere markt te koop geweest: geen handicaps, geen Draw No Bet, geen Double "
                "Chance, geen totalen en geen BTTS. Van de 127 selecties van vandaag komen er 27 uit de "
                "negen KKD-duels, en dat zijn stuk voor stuk alleen 1X2. §1a zegt wat dat betekent: een "
                "marktgemiddelde ligt systematisch LAGER dan de beste prijs — op 5 september gemeten op "
                "+7,78% verschil, oftewel ongeveer +1,84 pp edge — dus de +6,72 pp van deze regel is "
                "conservatief en niet vergelijkbaar met een duel waar de beste prijs wél bekend is. De "
                "bookmaker is bovendien niet herleidbaar: de gebruiker moet zelf een boek zoeken dat "
                "2,03 of beter biedt. ÉN HET OMGEKEERDE HOORT ER OOK BIJ: op een duel met maar één markt "
                "kan `selection_score` niet kiezen, dus deze regel staat op de lijst omdat het de enige "
                "uitdrukking van deze mening is en niet omdat het de sterkste van zes is."
            ),
            "POORT5_VANGT_OPNIEUW_VERREWEG_HET_MEESTE_WEG": (
                "POORT 5 VANGT 104 VAN DE 127 SELECTIES WEG (81,9%) — 'tweede_methode', de twee methodes "
                "verslaan de markt niet dezelfde kant op. Daarna 16 op de edge, 4 op poort 7 (context) en "
                "3 op poort 8 (underdog); NUL op de koersband en NUL op robuustheid. Die 81,9% ligt in "
                "dezelfde band als de afgelopen weken en voegt er geen nieuwe waarneming aan toe. DRIE "
                "DUELS VALLEN VOLLEDIG OP DEZE POORT: Elfsborg – Malmö FF (FULL), Corvinul Hunedoara – "
                "Universitatea Cluj (LIGHT) en Altach – Austria Wien (FULL). Dat laatste is het duel van "
                "de dag met de hoogste ruwe score (5,19) en het staat NIET op de lijst: Under 2,5 @1,99 "
                "op +8,79 pp, waar de splitsmethode de markt de andere kant op verslaat. Het is bovendien "
                "het enige duel waarop poort 9 zou hebben gebonden (FULL-Under in de band 8–10 pp, de "
                "band die §6g op −47,7% meet) — twee onafhankelijke remmen die dezelfde kant op wijzen, "
                "maar poort 5 was er eerder bij en de rij gaat als `tweede_methode` het schaduwlogboek "
                "in en niet als `doelpunten_onder`."
            ),
            "POORT7": (
                "BINDT EN HOUDT VIER SELECTIES TEGEN, OVER TWEE DUELS, EN HIJ RAAKT ÉÉN VAN DE DRIE "
                "GEPUBLICEERDE WEDSTRIJDEN. BOCHUM – WOLFSBURG: Bochum mist 24% van de selectiewaarde "
                "tegen 3% bij Wolfsburg (Philipp Strompf, Enis Çokaj, Babis Drakas), dus de thuiszege "
                "@3,50 (+1,98 pp) gaat eruit. DARMSTADT – ST. PAULI: Darmstadt mist 14% tegen 2% bij St. "
                "Pauli (Carlo Sickinger tot half november, Fabian Nürnberger eind oktober, Luca "
                "Marseiler begin december), dus drie selecties op de DARMSTADT-kant vallen af — "
                "Asian Handicap +0,25 @1,98 (+6,43 pp), de thuiszege @3,36 (+5,99 pp) en AH +1 @1,32 "
                "(+3,30 pp). DAT IS RELEVANT VOOR DE BET DIE ER WÉL KWAM: de gepubliceerde Under 2,75 "
                "van datzelfde duel is een doelpuntenmarkt en heeft per definitie geen kant, dus poort 7 "
                "staat daar open (§1c). De uitvallerslijst van Darmstadt pleit niet tegen een Under — "
                "een verzwakte thuisploeg scoort eerder minder — maar het is wél dezelfde wedstrijd waar "
                "de poort de uitkomstmarkten van heeft geblokkeerd, en dat hoort in het verslag te "
                "staan. STADIONCONTROLE: negentien duels, nul alarmen, alle duels in het eigen stadion "
                "van de genoteerde thuisploeg. OPSTELLINGEN: alle negentien op 'lastStarting11', geen "
                "enkele bevestigd — dezelfde klokbevinding als elke ochtend, veertien tot twintig uur "
                "voor de aftrap. De context van ALLE negentien duels is opgehaald en vastgelegd; de cap "
                "(55 op vrijdag) kapte niets af, dus de steekproef van ctxlog.py is volledig."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                "today=2026-10-23 aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 "
                "september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. HIJ HOUDT "
                "DRIE SELECTIES TEGEN, ALLE DRIE OP HETZELFDE DUEL: Västerås SK – Halmstads BK, waar de "
                "markt Halmstads op 29,8% zet — onder de ondergrens. Het gaat om Asian Handicap "
                "Halmstads +1 @1,73 (+2,38 pp), AH +0,75 @1,9702 (+1,73 pp) en de uitzege @5,018 "
                "(+1,28 pp). Alle drie boeken ze op BEIDE schalen hetzelfde, want geen van drieën haalt "
                "een drempel: de rij gaat als `underdog` het logboek in met de herijkte kans. DE "
                "GEPUBLICEERDE REGEL VAN DAT DUEL BESTAAT NIET — Västerås SK – Halmstads BK staat niet "
                "op de lijst, de Under 2,5 @2,28 (+5,29 pp) viel af op MAX_LIGHT_IN_SHORTLIST. De "
                "thuiszege van TOP Oss is de FAVORIETENkant (45,3% om 29,8%), dus daar staat poort 8 "
                "open, en de twee doelpuntenregels hebben geen kant. Dit is geen aanleiding om de vraag "
                "van 25 september opnieuw te stellen (§1e verbiedt dat zolang er niets wezenlijk "
                "verandert); de stand van beide reeksen staat in het runrapport onder 'Stand van het "
                "logboek' — `underdog` op −2,3% over 181 gevallen, `underdog_ruw` op −8,8% over 17."
            ),
            "POORT9": (
                "BINDT MAAR HOUDT NUL SELECTIES TEGEN, EN DAT IS VANDAAG EEN BETEKENISVOLLE NUL. "
                "`unders.BINDS_FROM` is 12 oktober en `unders.TIERS` is ('FULL',), dus een Under op FULL "
                "moet 10,0 pp halen in plaats van 8,0. Er is vandaag PRECIES ÉÉN FULL-Under die boven de "
                "8,0 uitkomt — Altach – Austria Wien, Under 2,5 @1,99 op +8,79 pp — en die was door poort "
                "5 al tegengehouden, dus hij boekt als `tweede_methode` en niet als `doelpunten_onder`; "
                "de reeks blijft op 10 afgewikkelde gevallen staan (−11,0%). EN DE UNDER DIE WÉL "
                "GEPUBLICEERD IS, STAAT BUITEN DE POORT: Darmstadt – St. Pauli is LIGHT, en §1h houdt "
                "LIGHT er met opzet buiten omdat de meting hem daar niet steunt. Dit is exact het geval "
                "dat de gebruiker op 12 oktober is voorgelegd en waarop hij 'eerst kijken wat deze rem "
                "doet' antwoordde: de rem bestaat, de scheefstand bestaat op beide tiers, en vandaag "
                "staat de enige Under van de lijst aan de kant waar de rem niet komt. Dat is geen reden "
                "om de vraag opnieuw te stellen — §1h verbiedt dat expliciet zolang de reeks onder de "
                "~30 gevallen zit — maar het hoort wel feitelijk opgeschreven."
            ),
            "PINNACLE": (
                "STAP 2 VAN STAGE 5 — het scherpste publieke expertoordeel, LOS van de beste prijs waarop "
                "gespeeld wordt en nooit in my_prob (§2). Pinnacle noteerde ZES van de negentien duels "
                "(de zes uit competities met een sportkey die hij voert); de dertien andere — negen KKD, "
                "twee Romanian SuperLiga, Empoli – LR Vicenza en Cruzeiro – Remo — hebben geen "
                "Pinnacle-1X2 of geen eigen 1X2 en zijn dus niet te toetsen. Op 1X2 staat het model "
                "gemiddeld 1,71 pp van het Pinnacle-oordeel af, bij een gemiddelde Pinnacle-marge van "
                "4,34% — dichtbij, en dichterbij dan de afgelopen weken. Op de TOTALEN is het beeld "
                "anders en ongunstiger: over zes (duel, lijn)-paren staat het model gemiddeld +2,21 pp "
                "BOVEN Pinnacle op de Under-kant, met vier van de zes erboven, en de uitschieter is "
                "Altach – Austria Wien met +13,18 pp — het duel dat poort 5 heeft tegengehouden. Dat is "
                "de bekende richting van §6g, nu voor de vierde week op rij. Let op de rekenwijze: die "
                "+2,21 pp vergelijkt een zuiver Poisson-grid zonder Dixon-Coles op strikt 'minder dan de "
                "lijn', dus op een kwartlijn is het een benadering; de twee regels in het blok hierboven "
                "(+11,4 en +6,2 pp) zijn op de push-equivalente kans van totals_prob gerekend en zijn "
                "de getallen om op af te gaan."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0689 (gepoold 1,0851 over 34 speeldagen) "
                "EN RUST OP VIER COMPETITIES: Segunda División, Serie B, 2. Bundesliga en Austrian "
                "Bundesliga. uplift_observations sloeg er VIER over, alle vier met reden, en dat staat "
                "hier omdat een stil weggelaten waarneming hetzelfde probleem is als een stille "
                "truncatie (§3 Stage 5): Allsvenskan ('halverwege het seizoen, 24 van 30 speeldagen'), "
                "Série A BRA ('halverwege het seizoen, 31 van 38'), en Romanian SuperLiga en Keuken "
                "Kampioen Divisie allebei met 'geen xG in vorig of lopend seizoen'. DE EERSTE TWEE "
                "KRIJGEN ROUTE 'lopend' van league_level en halen hun niveau rechtstreeks uit het "
                "lopende seizoen — Allsvenskan thuis 1,615 / uit 1,318 / basis 1,473, Série A thuis "
                "1,521 / uit 1,142 / basis 1,325. De zes andere krijgen 'vorig+uplift'. EEN POOL VAN "
                "VIER IS SMAL MAAR HET IS GEEN POOL VAN ÉÉN, en dat is beter dan de afgelopen twee "
                "Run B-dagen. DE TWEE DOELPUNTENREGELS VAN VANDAAG KOMEN BEIDE UIT DE UPLIFT-ROUTE "
                "(2. Bundesliga 8 van 34 speeldagen, Segunda 10 van 42), dus de factor 1,0689 raakt ze "
                "rechtstreeks: zonder die correctie zou het doelpuntenniveau ongeveer 7% lager liggen en "
                "zouden beide regels de ANDERE kant op wijzen dan ze nu doen. De derde regel (TOP Oss) "
                "komt uit een competitie zonder xG en draait op doelpunten als sterktemaat."
            ),
            "BEURSKOERS": (
                "GEEN VAN DE DRIE GEPUBLICEERDE REGELS STAAT OP EEN BEURS, dus de dubbele notatie van §5 "
                "is vandaag niet nodig: Darmstadt Under 2,75 @1,97 en Granada Over 2,25 @1,86 staan "
                "allebei bij PINNACLE (een gewone bookmaker, geen commissie), en TOP Oss @2,03 is een "
                "marktgemiddelde zonder herleidbare bookmaker. Beurzen stonden er wél bij andere "
                "selecties van dezelfde duels — Betfair had de beste 1X2-thuisprijs bij Granada (2,30, "
                "na 2% commissie 2,274) en de gelijkspelprijs bij Darmstadt (3,70 → 3,646) — en daar is "
                "met oddsapi.net_price gerekend zoals §1a eist. DAT PINNACLE TWEE KEER DE BESTE PRIJS "
                "HEEFT IS ZELF EEN WAARNEMING en geen gunstig teken: de scherpste bookmaker van de markt "
                "is zelden de ruimste, en dat hij het hier is betekent dat de rest van de markt nóg "
                "verder van het model af staat dan het blok over Pinnacle hierboven laat zien."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "INZETVENSTER": (
                "Het venster is [08:00 NL 23 okt, 08:00 NL 24 okt) en runwindow.py levert NEGENTIEN "
                "duels, alle negentien met RunMatch.playable = True. Achttien trappen af tussen 17:00 en "
                "20:30 NL op de rundag zelf; ÉÉN zit in de nachtband waarvoor deze module bestaat: "
                "Cruzeiro – Remo (Série A BRA) trapt af om 01:00 NL in de nacht naar 24 oktober en stond "
                "op de UTC-daglijst van 23 oktober. Onder de regel van vóór 24 september was dat duel "
                "aan de run van morgen toegewezen en morgenochtend al gespeeld geweest. Vandaag kost het "
                "geen bet — Cruzeiro – Remo komt op tier NONE uit omdat Remo niet in de stand van 2025 "
                "staat en er voor het Braziliaanse divisiepaar GEEN gemeten factor bestaat (§run-b.md) — "
                "maar de module deed wat ze moet doen. RunMatch.source_day staat op 2026-10-23 voor alle "
                "negentien duels; er zat vandaag dus geen duel in de nachtband van de vórige rundag, en "
                "include_carry_over is niet gebruikt (die is eenmalig geweest op 24 september)."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "17 VAN DE 17 COMPETITIES BEVESTIGD, 19 duels tegen 19. Fotmob levert de daglijst en "
                "BetExplorer de fixturepagina per competitie — twee losse bronnen — en de controle "
                "draait óók op de negen competities die vandaag GEEN WEDSTRIJD hebben, want dat is "
                "precies waar een fout id of een verhuisde slug stil zou wegvallen (§run-b.md, de "
                "Serie B-les). Geen enkele afwijking. De tijdzonerekening: BetExplorer labelt in "
                "UK-tijd, dus het venster [23.10. 08:00 NL, 24.10. 08:00 NL) is daar "
                "[23.10. 07:00, 24.10. 07:00)."
            ),
            "inkoop": (
                "22 CREDITS VAN EEN PLAFOND VAN 1052 (18.967 over bij 9 dagen tot de maandwissel, twee "
                "runs per dag). ZES van de acht spelende competities hebben een sportkey en kregen alle "
                "zes de bulk-aanroep van 3 credits (h2h + spreads + totals = 18 credits), dus vijf van de "
                "zes markten; daarna 4 credits voor BTTS op de vier duels met een kandidaat-edge waar ook "
                "een spreads-respons bij zat (Elfsborg – Malmö, Granada – Real Valladolid, Darmstadt – "
                "St. Pauli, Altach – Austria Wien). TWEE spelende competities hebben GEEN sportkey — "
                "Romanian SuperLiga en Keuken Kampioen Divisie — en draaien dus volledig op het gratis "
                "BetExplorer-marktgemiddelde als enige 1X2-bron, zonder enige andere markt. Dat raakt "
                "ELF van de negentien duels, oftewel het grootste deel van de dag, en het is de reden "
                "dat 27 van de 127 selecties uit negen KKD-duels komen en allemaal 1X2 zijn. "
                "MARKTBALANS-CONTROLE GEHAALD en ruim: zes van de zes inkoopbare competities kregen "
                "zowel een uitkomstmarkt als een doelpuntenmarkt uit dezelfde bulk, dus er is geen "
                "enkele competitie met alléén het een of het ander. split_budget(1052, 6) gaf (6, 6) en "
                "het plafond bond nergens."
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

        # Dekkingstabel: óók de vijftien competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/rb_oct23_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct23_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct23_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct23_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

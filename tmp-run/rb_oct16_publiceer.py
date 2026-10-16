"""Run B 16 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct16_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. Tien van de zeventien competities speelden, met vijftien duels in
het inzetvenster en nul afgekapt (cap 55 op vrijdag). VIER gepubliceerde regels, waarvan ÉÉN zijn
eigen lat haalt.

Drie dingen die vandaag in de parameters horen:

* **Eén regel haalt de drempel, drie staan er op rangorde.** Rapid Wien - Hartberg Under 3,5 @1,90
  haalt +16,12 pp én de verzwaarde lat van poort 9 (10,0 pp). De andere drie staan onder hun lat en
  zijn er per §5b als rangorde en niet als vondst.
* **De BetExplorer-slug van Série A (BRA) is verhuisd**, en dat is dezelfde stille faalstand als
  het Serie B-id: HTTP 200 met nul rijen. Gerepareerd in `rb_oct16_bxfix.py`, zonder credits.
* **De stadioncontrole gaf één echt alarm en één vals**, en het valse is in `scripts/context.py`
  gerepareerd (`_norm_ground` liet "Stadium" tegen "Stadion" staan).

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-16"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-16T05:25:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct16_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.023, b=0.015 op 4608 "
                "afgerekende gevallen, fitted_through 2026-10-15. Die datum is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist). De "
                "correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,3% en het gebeurde "
                "33,3% (+0,0 pp) — en ze VERHOOGT een kans over vrijwel de hele speelbare band: +0,1 pp op "
                "40%, +0,4 pp op 50%, +0,6 pp op 60% en +0,7 pp op 70%, en ze verlaagt alleen onder ongeveer "
                "35%. OP DE GEPUBLICEERDE REGEL TELDE ZE DUS EDGE BIJ IN PLAATS VAN AF: Rapid Wien – "
                "Hartberg Under 3,5 gaat van +15,44 pp ruw naar +16,12 pp herijkt. DAT BINDT VANDAAG NIET: "
                "beide schalen liggen ruim boven de verzwaarde lat van poort 9 (10,0 pp), dus bet_beide "
                "staat op True en de regel haalt haar lat op de ruwe én de herijkte kans. Lees de identiteit "
                "zoals §1e punt 3 van 30 sep voorschrijft: de reeks is de ONGESELECTEERDE ijksteekproef en "
                "breder dan de staart waarop deze routine speelt, dus 'de fit is de identiteit' betekent "
                "niet dat het model recht staat op die staart — §6e meet daar nog +1,78 pp te veel kans op "
                "longshots en -3,53 pp te weinig op favorieten over 4866 uitkomsten."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TIEN van de zeventien competities speelden, met 15 duels in het inzetvenster: Keuken "
                "Kampioen Divisie (4), Romanian SuperLiga (2), 2. Bundesliga (2) en Allsvenskan, Croatian "
                "HNL, Hungarian NB I, Segunda División, Serie B, Austrian Bundesliga en Série A (BRA) elk 1. "
                "ZEVEN hadden GEEN WEDSTRIJD: Czech First League, Greek Super League, Eliteserien, Swiss "
                "Super League, English League One, English League Two en MLS (USA). Dat is een vrijdag in een "
                "gewone speelweek — de Engelse divisies spelen zaterdag, de MLS zaterdagnacht, Eliteserien en "
                "de Zwitserse competitie zondag — en dus geen storing en geen dekkingsgat. scripts/idcheck.py "
                "gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand (afsluitcode 0), dus geen "
                "enkele competitie is stil uit de lijst verdwenen — ook niet de zeven die vandaag niet "
                "spelen, en dat is precies waarom die controle bestaat (prompts/run-b.md: een fout id geeft "
                "geen foutmelding maar nul wedstrijden, en nul wedstrijden leest als GEEN WEDSTRIJD). VIER "
                "van de tien spelende competities draaien per prompts/run-b.md op doelpunten als sterktemaat "
                "en komen dus op LIGHT met een lat van 16,0 pp uit: Croatian HNL, Hungarian NB I, Romanian "
                "SuperLiga en Keuken Kampioen Divisie — Fotmob geeft daar geen xG, niet in 2025/2026 en niet "
                "in 2026/2027, en dat is per competitie nagetrokken en niet van de buurlanden overgenomen "
                "(prompts/run-b.md: Duitsland HEEFT xG in de 2. Bundesliga en Nederland niet in de KKD). "
                "Tiers over de 15 duels: 5 FULL, 7 LIGHT, 3 NONE. VIJF DUELS HEBBEN EEN PLOEG ZONDER STAND "
                "IN HET VORIGE SEIZOEN en gingen langs de omrekening van §4; TWEE daarvan lukten en DRIE "
                "niet. Gelukt: Hellas Verona (degradant uit Serie A, langs promotion.TIER1 met het gemeten "
                "paar I1/I2) en NAC Breda (degradant uit de Eredivisie, langs de gemeten NED-factor) — beide "
                "LIGHT, nooit FULL. Niet gelukt, en alle drie terecht op NONE: Rudeš (Croatian HNL heeft geen "
                "divisiepaar — §4, 'Kroatië kan niet'), Vasas Budapest (Hungarian NB I evenmin — §4, 'voor "
                "Hongarije is er geen factor') en Energie Cottbus, en die derde is een NIEUW geval: hij komt "
                "uit de 3. Liga en promotion.TIER2 kent voor '2. Bundesliga (GER)' geen divisie eronder. Er "
                "is dus geen gemeten factor voor dat divisiepaar en §4 verbiedt er een te verzinnen; NONE is "
                "de eerlijke uitkomst en het staat als openstaand punt in het runrapport."
            ),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 16 okt, 08:00 NL 17 okt) en runwindow.py levert 15 duels, alle 15 "
                "met RunMatch.playable = True. VEERTIEN trappen af op de rundag zelf tussen 17:00 en 20:30 "
                "NL; ÉÉN valt in de nachtband waar prompts/run-b.md over gaat: Mirassol – Internacional "
                "(Série A BRA) om 23:00 UTC, oftewel 01:00 NL op 17 OKTOBER. Dat duel stond op de daglijst "
                "van 2026-10-16 (source_day = DAY) en hoort bij deze run omdat het inzetvenster van deze run "
                "het nog kan bedienen — onder de oude UTC-dagregel was het óók aan vandaag toegewezen, dus "
                "vandaag kost die regel niets. Waar hij wél telt is de spiegel ervan: een Braziliaans of "
                "Amerikaans duel dat in UTC op de rundag valt maar in NL-tijd tussen 00:00 en 08:00, is al "
                "gespeeld voordat de gebruiker kan inzetten. Zulke duels zitten vandaag niet in de lijst. De "
                "run begon om 05:04 NL, ruim elf uur voor de vroegste aftrap. GEEN ENKEL duel kwam van de "
                "daglijst van 17 oktober."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "ALLE ZEVENTIEN COMPETITIES ZIJN DOOR EEN TWEEDE, ONAFHANKELIJKE BRON BEVESTIGD, en de twee "
                "bronnen zijn het over de hele runlijst eens: Fotmob 15 duels in het venster, BetExplorer 15. "
                "Dat geldt óók voor de zeven competities die vandaag GEEN WEDSTRIJD hebben — juist daar moet "
                "de tweede bron kijken, want 'nul wedstrijden' is de uitkomst die een kapot id en een lege "
                "speeldag niet van elkaar onderscheidt. Dit is de poort uit §1 die de scheduler expliciet "
                "noemt, en ze staat vandaag op 17 van 17. BetExplorer labelt in UK-tijd (NL −1 uur), dus het "
                "venster is daar [16.10. 07:00, 17.10. 07:00); dat is omgerekend en de omrekening staat in "
                "rb_oct16_bevestiging.py. EEN AANTEKENING DIE BIJ DEZE CONTROLE HOORT: ze slaagde vandaag "
                "alleen dóórdat de BetExplorer-slug van Série A (BRA) eerst is gerepareerd — zie "
                "BX_SLUG_CORRECTIE."
            ),
            "BX_SLUG_CORRECTIE": (
                "DE BETEXPLORER-PAGINA VAN SÉRIE A (BRA) IS VERHUISD EN DAT FAALT STIL. data/coverage.json "
                "schrijft sinds 20 sep 2026 'brazil/serie-a-betano' voor, met de uitdrukkelijke notitie dat "
                "de drie voor de hand liggende alternatieven ('brazil/serie-a', 'brazil/brasileirao-serie-a', "
                "'brazil/campeonato-brasileiro') toen alle drie HTTP 200 met NUL RIJEN gaven. Vandaag is het "
                "precies omgekeerd gemeten: serie-a-betano geeft 200 met 0 rijen en brazil/serie-a geeft 20 "
                "rijen, met Mirassol – Internacional erbij. DEZELFDE STILLE FAALSTAND ALS HET SERIE B-ID: "
                "geen foutmelding, alleen nul rijen, en nul rijen leest als 'geen marktgemiddelde voor dit "
                "duel'. WAT HET KOSTTE ALS HET NIET WAS OPGEVALLEN: het de-vigde marktoordeel over Mirassol – "
                "Internacional, en dat raakt twee dingen die NIET over de bet zelf gaan (§1a, 'gemiddelde om "
                "te meten, beste prijs om te spelen') — het kalibratieblok van §6e en poort 8. De bet zelf "
                "liep geen gevaar: Série A heeft een sportkey, dus de beste prijs kwam uit de bulk. "
                "Gerepareerd in rb_oct16_bxfix.py zonder één credit uit te geven, en de nieuwe slug is in "
                "coverage.json vastgelegd met de meting van vandaag ernaast."
            ),
            "POORT7": (
                "BINDT EN HOUDT NUL SELECTIES TEGEN. Van de 108 doorgerekende selecties sneuvelde er geen "
                "enkele op 'context': bij de duels mét een noemenswaardige uitvallerslijst staat de "
                "zwaarst getroffen ploeg niet op de kant waar de routine op zou willen spelen, of er is "
                "geen kant (Over/Under, BTTS — dan staat de poort per ontwerp open). WAT ER WEL IS "
                "OPGEHAALD en wat §1c eist vast te leggen: de context van ÉLK van de vijftien duels, ook "
                "de drie die op tier NONE uitkwamen. De zwaarste uitvallerslijsten van de dag staan bij "
                "Rapid Wien (zes uitvallers: Jakob Schöller, Jean Marcelin, Jonas Auer, Dominic Vincze, "
                "Martin Ndzie, Daniel Nunoo) tegen Hartberg (drie: Luca Pazourek, Fabian Wilfinger, Lukas "
                "Fridrikas) en bij Internacional (zes, onder wie Alan Patrick, Guillermo Maripán en "
                "Sergio Rochet) tegen Mirassol (twee). DE GEPUBLICEERDE REGEL IS EEN DOELPUNTENMARKT ZONDER "
                "KANT, dus poort 7 kón daar niets doen — en dat is geen formaliteit: beide ploegen van Rapid "
                "Wien – Hartberg missen spelers, wat op een totaal twee kanten op werkt en wat §1c "
                "uitdrukkelijk NIET in een getal vertaalt zolang er geen meting is. "
                "DE STADIONCONTROLE GAF VANDAAG TWEE ALARMEN, ÉÉN ECHT EN ÉÉN VALS, en dat tweede is "
                "gerepareerd: (1) ECHT — Rudeš – Rijeka wordt gespeeld in ŠRC Velika Gorica en niet op "
                "Igralište NK Rudeš; §1c eist dat zo'n verplaatsing in het runrapport staat ook als de poort "
                "opengaat, en het duel is hoe dan ook NONE. (2) VALS — MTK Budapest – Vasas Budapest stond "
                "als VERPLAATST omdat de wedstrijdpagina 'Hidegkuti Nandor Stadium' schrijft en de "
                "teampagina 'Hidegkuti Nándor Stadion'. Dat is hetzelfde stadion en dezelfde fout die Run B "
                "op 6 september al voor de accenten repareerde, nu één laag dieper: het generieke woord voor "
                "'stadion' verschilt per taal en Fotmob gebruikt op twee plekken twee vormen. "
                "scripts/context._norm_ground laat dat woord vanaf nu weg (stadium/stadion/stadio/stadionul, "
                "ook als prefix zoals in het Roemeens), en de echte verplaatsing van Rudeš blijft staan — dat "
                "is de toets die de reparatie moest halen. EEN AANTEKENING OVER DE OPSTELLINGEN, want die "
                "bepaalt hoeveel poort 7 vandaag kón doen: geen enkel duel had om 05:15 NL een bevestigde "
                "opstelling (alle vijftien op lineupType = lastStarting11). Dat is dezelfde klokbevinding als "
                "de afgelopen weken en geen competitie-eigenschap: Run B draait elf tot twintig uur voor de "
                "aftrap en de opstellingen komen een uur ervoor. Het contextlogboek blijft daarmee de enige "
                "weg naar een meting over het effect van blessures (§1c)."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met today=2026-10-16 "
                "aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. Hij hield 8 selecties tegen, "
                "verdeeld over VIJF wedstrijden (Leganés – Córdoba, Rapid Wien – Hartberg, FC Den Bosch – TOP "
                "Oss, FC Eindhoven – Vitesse, Helmond Sport – NAC Breda). EN HIJ KOST VANDAAG PLEK 1 VAN DE "
                "RUWE LIJST: Rapid Wien – Hartberg, Asian Handicap Hartberg +1.75 @1,94 (+18,19 pp ruw, "
                "selection_score 12,686) staat daar op 1 met `underdog` als bindende poort. DAT IS DEZELFDE "
                "WEDSTRIJD WAARUIT DE GEPUBLICEERDE REGEL KOMT, en dat is het vermelden waard: de routine "
                "ziet Rapid Wien – Hartberg als het scheefste duel van de dag en mag die mening alleen nog "
                "in de doelpuntenmarkt uitdrukken, omdat de handicap op de mindere ploeg door poort 8 dicht "
                "zit. WAT ER TEGENOVER STAAT: de `underdog`-schaduwreeks staat nu op 119 kandidaten, 111 "
                "afgewikkeld, -3,8% rendement (48,6% trefkans) — licht negatief, dus de poort bespaart geld, "
                "en de uitweg van 25 september ('positieve ROI over >= 30 afgewikkelde kandidaten') is "
                "daarmee niet de ja die hij op 5 oktober was. §1e verbiedt de vraag dagelijks opnieuw te "
                "stellen en er is niets wezenlijk veranderd. De gemeten kalibratiefout die de rem "
                "verantwoordt staat er nog: +1,78 pp te veel kans op longshots en -3,53 pp te weinig op "
                "favorieten over 4866 uitkomsten. `underdog_ruw` staat onveranderd op 17 gevallen met -8,8%; "
                "poort8_ruw is leeg omdat alle 8 al op de herijkte schaal sneuvelden en §1e verbiedt "
                "dezelfde selectie twee keer te boeken, en poort8_vervallen is leeg omdat het venster van "
                "zes dagen voorbij is. Die twee reeksen blijven twee populaties en worden nooit opgeteld."
            ),
            "POORT9_EN_DE_NIET_MONOTONIE_DIE_VANDAAG_PUBLICEERT": (
                "POORT 9 HOUDT VANDAAG NUL SELECTIES TEGEN, EN JUIST DAAROM IS HET GEVAL VAN 14 OKTOBER "
                "VANDAAG BETER TE ZIEN DAN TOEN. De poort (§1h, unders.BINDS_FROM = 2026-10-12) eist van een "
                "Under op FULL-data 10,0 pp in plaats van 8,0. De gepubliceerde regel haalt die lat ruim "
                "(+16,12 pp). MAAR ER STAAT EEN TWEEDE FULL-UNDER IN DE LIJST DIE HAAR NIET HAALT EN TOCH "
                "PUBLICEERT: Holstein Kiel – Hertha BSC, Under 3,25 @1,99, +4,89 pp, plek 4. unders.check "
                "laat die met opzet door — de docstring zegt waarom: élke Under onder de GEWONE drempel van "
                "8,0 pp gaat vrij, anders loopt de reeks `doelpunten_onder` vol met kandidaten die nooit een "
                "bet konden worden (de 'twee populaties'-fout van §1e). Die redenering berust erop dat `edge` "
                "dan de bindende poort is, en SINDS §5b (20 sep) IS `edge` GEEN POORT MEER MAAR EEN "
                "AFKAPPING. Vandaag is het resultaat dus letterlijk: een FULL-Under van +4,89 pp staat in de "
                "lijst, terwijl een FULL-Under van +8,66 pp (het geval van 14 oktober) wordt geblokkeerd. "
                "Precies de band die §6g als de slechtste van de hele reeks meet (8–10 pp, -47,7% over 15 "
                "gevallen) wordt weggehouden, terwijl de band eronder (0–8 pp, -34,1% over 26 gevallen) "
                "publiceert. DIT IS GEEN NIEUWE VRAAG EN WORDT NIET OPNIEUW VOORGELEGD: §1h en §6g verbieden "
                "een run deze poort op eigen initiatief te verzetten, en de vraag is op 14 oktober één keer "
                "aan de gebruiker voorgelegd en nog niet beantwoord — §1e en §6c schrijven voor hem dan niet "
                "dagelijks te herhalen. Hij staat hier als feit en in het dagrapport onder de regel zelf als "
                "voorbehoud. De reeks `doelpunten_onder` staat op 1 afgewikkeld geval (gewonnen, +65%); lees "
                "hem niet onder ~30 (§6d)."
            ),
            "EEN_UNDER_OP_DE_GEMETEN_SCHEVE_KANT": (
                "DE ENIGE REGEL DIE ZIJN EIGEN LAT HAALT IS EEN UNDER OP FULL-DATA, EN DAT IS EXACT DE "
                "MARKT-EN-KANT WAARVAN §6g OP UITKOMSTEN HEEFT GEMETEN DAT ZE SCHEEF STAAT. Twee metingen "
                "van vandaag, beide uit margins.py goalbias over 1228 doorgerekende duels: (1) de VORMFOUT — "
                "het gemiddelde aantal doelpunten klopt (voorspeld 3,046 / werkelijk 3,068, z = +0,45) maar "
                "de verdeling niet: -2,4 pp massa op 2 doelpunten en +2,4 pp op 4 doelpunten (boven twee "
                "standaardfouten), waardoor P(Under 3,5) structureel 2,4 pp te hoog staat bij ÉLK duel, vóór "
                "er iets gekozen is; en (2) het SELECTIE-EFFECT — in de 64 duels waarin de routine werkelijk "
                "een Under speelde vielen er +0,613 doelpunt per duel méér dan haar eigen lambda zei, z = "
                "+2,99, terwijl de Over-kant op z = -0,48 staat over 41 duels. Over het hele logboek: Under "
                "98 picks, -14,1% over 91 afgewikkeld, tegen Over 74 picks, +11,4% over 65. WAT DAT CONCREET "
                "VAN DE EDGE AFHAALT: van de +16,12 pp blijft na aftrek van de gemeten vormfout van 2,4 pp "
                "ongeveer +13,7 pp over — nog steeds boven de verzwaarde lat, maar het hoort erbij te staan. "
                "EN DE ONAFHANKELIJKE CONTROLE WIJST DEZELFDE KANT OP, SCHERPER DAN OP 14 OKTOBER: tegen "
                "Pinnacle — volgens §5 (Stage 5, stap 2) het scherpste publieke expertoordeel dat er is, "
                "vandaag met een marge van 3,4 tot 4,0% — staat het model op de gepubliceerde lijn 3,50 "
                "+14,99 pp boven de markt op de Under-kant (eigen 66,2% tegen Pinnacle 51,2%). DAT IS DE "
                "SIGNATUUR VAN DE GEMETEN SCHEEFSTAND EN GEEN BEVESTIGING VAN DE EDGE. Wat er vandaag anders "
                "is dan op 14 oktober, toen vier van de vier Unders boven Pinnacle stonden: over de vijf "
                "(duel, lijn)-paren met een Pinnacle-totaal staat het model gemiddeld -0,63 pp ONDER "
                "Pinnacle op de Under-kant, en bij drie van de vijf eronder (Leganés -14,45, Hellas Verona "
                "-10,51, Mirassol -3,43). De scheefstand is vandaag dus niet uniform; de gepubliceerde regel "
                "is juist de uitschieter, samen met Holstein Kiel (+10,23). Dat maakt het geval ERNSTIGER en "
                "niet milder: het is geen dagbrede verschuiving die je op de hele lijst kunt wegdenken, maar "
                "een verschil dat op precies dit duel het grootst is. DAT MOET IN HET DAGRAPPORT STAAN en het "
                "staat er (§6g, laatste alinea). WAT HET NIET IS: geen reden om de rangorde te negeren of de "
                "lijst leeg te laten — §5b schrijft de rangorde voor en §1 verbiedt zowel bets forceren als "
                "bets achterhouden buiten de poorten om."
            ),
            "BEVINDING_POORT5_NEGENTIENDE_DAG": (
                "POORT 5 VANGT OPNIEUW RUIM DRIEKWART WEG: 84 van de 108 selecties (77,8%) sneuvelden op "
                "'tweede_methode' — de twee methodes verslaan de markt niet dezelfde kant op. Daarna 10 op de "
                "edge, 8 op de underdog-poort en 4 op de koersband; NUL op context, NUL op robuustheid, NUL "
                "op data en NUL op poort 9. TWEE selecties haalden alle negen poorten, beide in Rapid Wien – "
                "Hartberg (Under 3,5 en Under 3,25), en §1a koos de hoogste selection_score. De reeks staat "
                "nu bijna drie weken rond twee derde tot vier vijfde, en §5 ('Net niet') zegt dat zoiets "
                "dagen achtereen een BEVINDING is over de splitsmethode en geen ruis. WAT HET SCHADUWLOGBOEK "
                "ERVAN ZEGT: 'tweede_methode' staat op 139 kandidaten, 132 afgewikkeld, -3,4% rendement "
                "(44,7% trefkans) — de poort bespaart dus geld, al is het bedrag klein. VANDAAG LEUNT DE "
                "GEPUBLICEERDE REGEL ZWAAR OP DE SPLITSMETHODE, en dat is een voorbehoud: Rapid Wien – "
                "Hartberg staat op xG +13,52 pp en splits +23,12 pp, bijna tien procentpunt verschil, en §1f "
                "heeft op 392 afgerekende gevallen gemeten dat de splitsmethode als kansbron vrijwel niets "
                "toevoegt (Brier .23674 voor alleen xG tegen .23625 voor de beste mix). De xG-arm alleen "
                "haalt de verzwaarde lat van poort 9 ook (13,52 > 10,0), dus de regel staat niet of alleen "
                "op de zwakke arm — maar de sprong van 13,5 naar 16,1 komt er wel vandaan. De zwakste stand "
                "van het (shrink, rho)-grid is 13,52 pp, dus poort 6 heeft ruimte. NIET VANDAAG EEN WEGING "
                "VERANDEREN (§6d, en §1f noemt de curve tussen 0,7 en 1,0 vlak)."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0627 (gepoold 1,0794 over 30 speeldagen, 4 "
                "competities), en ZES van de tien spelende competities zijn uit de pool weggelaten — dat "
                "weglaten is zélf de meting (§3 Stage 5) en hoort daarom integraal in het rapport. TWEE "
                "wegens een seizoen over de helft, waardoor league_level route 'lopend' kiest: Allsvenskan "
                "(23 van 30 speeldagen) en Série A (BRA) (30 van 38). VIER wegens het ontbreken van xG in "
                "beide seizoenen: Croatian HNL, Hungarian NB I, Romanian SuperLiga en Keuken Kampioen "
                "Divisie. WAT DE FACTOR VOOR DE OVERIGEN DOET: de acht competities op route 'vorig+uplift' "
                "krijgen het niveau van vorig seizoen × 1,0627; de twee op route 'lopend' rekenen "
                "rechtstreeks met het lopende seizoen, ongeschaald (Allsvenskan thuis 1,630 / uit 1,310 / "
                "basis 1,477 en Série A thuis 1,538 / uit 1,137 / basis 1,319). DE SEIZOENSNOTATIE VAN DIE "
                "TWEE EN VAN MLS EN ELITESERIEN IS '2025'/'2026' EN NIET '2025/2026', zoals prompts/run-b.md "
                "eist — anders valt Fotmob stil terug op het lopende seizoen en rekent de run zijn prior op "
                "de stand van vandaag. DE COMPETITIE VAN DE GEPUBLICEERDE REGEL draait op route "
                "'vorig+uplift': Austrian Bundesliga, niveau thuis 1,465 / uit 1,336 / basis 1,511, met 8 "
                "van de 22 speeldagen gespeeld en een lopend seizoen dat met gewicht 0,50 meeweegt in de "
                "teamsterktes (blend_seasons, k=8)."
            ),
            "BEURSKOERS": (
                "GEEN VAN DE VIER GEPUBLICEERDE REGELS STAAT OP EEN BEURS, dus de commissieregel van §5 bindt "
                "vandaag nergens op de bet zelf. De gepubliceerde koersen: Rapid Wien – Hartberg Under 3,5 "
                "@1,90 bij Tipico, Oțelul Galați 1X2 @1,63, Mirassol – Internacional Over 2,5 @1,9996 en "
                "Holstein Kiel – Hertha BSC Under 3,25 @1,99, alle vier van The Odds API op de beste prijs "
                "per uitkomst. WAAR DE BEURZEN WEL IN BEELD KWAMEN: in de 1X2-respons van Rapid Wien – "
                "Hartberg stond Betfair met de beste prijs aan beide kanten (1 @1,31 bruto / 1,3038 netto en "
                "2 @10,00 bruto / 9,82 netto) en Pinnacle op de X (@6,46); net_price is daar toegepast, maar "
                "geen van die selecties haalde de poorten. DE WINST VAN DE BESTE PRIJS boven het "
                "BetExplorer-marktgemiddelde was op dat duel +9,07% — ruim boven de +7,78% die §1a op 5 "
                "september mat, en het is gratis edge die niets aan het model verandert. DRIE VAN DE TIEN "
                "SPELENDE COMPETITIES HEBBEN GEEN SPORTKEY EN DRAAIEN OP HET GRATIS "
                "BETEXPLORER-MARKTGEMIDDELDE als enige 1X2-bron: Croatian HNL, Hungarian NB I en Keuken "
                "Kampioen Divisie, plus Romanian SuperLiga — daar is de bookmaker niet herleidbaar en valt "
                "de edge systematisch te laag uit (conservatief, dus geen risico op te veel bets, maar niet "
                "vergelijkbaar met een duel waar de beste prijs wél bekend is). ÉÉN VAN DE VIER "
                "GEPUBLICEERDE REGELS KOMT UIT DIE GROEP: Oțelul Galați – Csikszereda, 1X2 @1,63 op het "
                "marktgemiddelde."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": (
                "24 CREDITS VAN EEN PLAFOND VAN 645 (19.395 over bij api_check.py, 605 verbruikt deze maand, "
                "15 dagen tot de maandwissel, 2 runs per dag). Stap 0: ZES bulk-aanroepen à 3 credits (h2h + "
                "spreads + totals = 18) voor de zes spelende competities MET sportkey — Allsvenskan (8 "
                "events), Segunda División (11), Serie B (10), 2. Bundesliga (9), Austrian Bundesliga (12) en "
                "Série A BRA (20); split_budget(645, 6) -> (6, 6) dus niemand viel buiten de bulk en de losse "
                "totals-stap was niet nodig. Stap 2: BTTS voor 6 van de 10 duels met een kandidaat-edge (6 "
                "credits à 1). VIER duels met een kandidaat-edge kregen geen BTTS, alle vier met dezelfde "
                "reden in markets_checked: hun competitie heeft geen sportkey bij The Odds API (Oțelul "
                "Galați, FC Den Bosch, Helmond Sport, VVV-Venlo). Vijf duels kregen geen BTTS omdat er geen "
                "kandidaat-edge in dat duel zat (§1a stap 2) of omdat het tier NONE was. "
                "MARKTBALANS-CONTROLE: GEHAALD, EN RUIM — ZES van de zes inkoopbare competities kregen via de "
                "bulk álle zes de markten (1X2, AH, DNB, DC, OU, BTTS), dus er is geen enkele competitie met "
                "alléén een uitkomstmarkt of alléén een doelpuntenmarkt. §1a eist dat je meldt HOE RUIM die "
                "controle slaagt, en dat is hier zes op zes in plaats van de één-op-twaalf van 30 augustus. "
                "DAT MAAKT DE MARKTVERDELING VAN DE UITKOMST BETEKENISVOL: van de vier gepubliceerde regels "
                "komen DRIE uit de doelpuntenmarkt (Over/Under) en ÉÉN uit een uitkomstmarkt (1X2). Dat is "
                "geen inkoopartefact — alle zes markten dongen mee in zes van de tien competities — maar de "
                "uitkomst van selection_score, en zie "
                "EEN_UNDER_OP_DE_GEMETEN_SCHEVE_KANT voor waarom juist de doelpuntenkant vandaag een "
                "voorbehoud verdient. Twee aanroepen die NIET nodig waren: de losse totals-rotatie (alles zat "
                "in de bulk) en een tweede BetExplorer-ronde (de slugcorrectie van Série A koste 1 verzoek, 0 "
                "credits)."
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
        s3 = json.load(open("tmp-run/rb_oct16_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct16_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct16_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct16_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

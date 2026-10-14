"""Run B 14 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct12_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum
en de `parameters`-tekst verschillen. Twee van de zeventien competities speelden, met
zestien duels in het inzetvenster — een VOLLE MLS-speelronde van vijftien plus één Tsjechisch
duel — en nul afgekapt (cap 40). Drie gepubliceerde regels, alle drie een Under 3,5 op FULL.

Twee dingen die vandaag voor het eerst gebeuren en die in de parameters staan:

* **Poort 9 (§1h) neemt werkelijk iets weg.** CF Montréal – Atlanta United (Under 3,5 @1,65,
  +8,66 pp) wordt tegengehouden en is de EERSTE rij ooit in de reeks `doelpunten_onder`. Zijn
  selection_score (5,999) is hoger dan die van twee van de drie regels die wél zijn gepubliceerd,
  dus de poort kost vandaag plek 2 — en hij laat juist de twee Unders mét minder edge door, omdat
  `unders.check` élke Under onder de gewone drempel van 8,0 doorlaat op de aanname dat `edge` daar
  de bindende poort is. Sinds §5b is `edge` geen poort meer. Dat is een bevinding en geen reparatie
  die een run zelf mag doen (§1h, §6g); ze staat als `besluit` in het dagrapport.
* **`runwindow.py` vangt een hele speelronde.** Negen van de vijftien MLS-duels kwamen van de
  daglijst van 15 oktober en waren onder de oude UTC-dagregel aan de run van morgen toegewezen —
  die begint ná hun aftrap. Eén van de drie gepubliceerde regels staat in die groep.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-14"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-14T05:20:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct14_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.021, b=0.013 op 4455 "
                "afgerekende gevallen, fitted_through 2026-10-13. Die datum is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist). De "
                "correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,3% en het gebeurde "
                "33,3% (+0,0 pp) — en ze VERHOOGT een kans over vrijwel de hele speelbare band: +0,1 pp op "
                "40%, +0,3 pp op 50%, +0,5 pp op 60% en +0,6 pp op 70%, en ze verlaagt alleen onder ongeveer "
                "35%. OP DE DRIE GEPUBLICEERDE REGELS TELDE ZE DUS EDGE BIJ IN PLAATS VAN AF: 9,53 -> 10,09 "
                "(Toronto FC), 7,07 -> 7,69 (FC Dallas) en 7,10 -> 7,70 (Columbus Crew). EN BIJ DE KOP VAN DE "
                "LIJST BINDT DAT ECHT, op een manier die vandaag voor het eerst voorkomt: Toronto FC – "
                "Orlando City Under 3,5 haalt de VERZWAARDE lat van poort 9 (10,0 pp, §1h) alleen op de "
                "HERIJKTE schaal (+10,09) en niet op de ruwe (+9,53). bet_beide staat daarom op False en de "
                "regel staat óók als schaduwrij met failed_gate = doelpunten_onder — op de RUWE schaal, waar "
                "poort 9 hem tegenhoudt. Dat is precies het geval waarvoor §5a de vlag bet_beide heeft "
                "gebouwd in plaats van op de redenering 'herijkt haalt de drempel, dus ruw ook' te "
                "vertrouwen; die redenering is sinds 20 sep niet langer waar. Lees de identiteit zoals §1e "
                "punt 3 van 30 sep voorschrijft: de reeks is de ONGESELECTEERDE ijksteekproef en breder dan "
                "de staart waarop deze routine speelt, dus 'de fit is de identiteit' betekent niet dat het "
                "model recht staat op die staart — §6e meet daar nog +1,79 pp te veel kans op longshots en "
                "-3,50 pp te weinig op favorieten over 4722 uitkomsten."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de zeventien competities speelden, met 16 duels in het inzetvenster: MLS (USA) met "
                "een VOLLE speelronde van 15 duels en Czech First League (CZE) met één. VIJFTIEN hadden GEEN "
                "WEDSTRIJD: Greek Super League, Eliteserien, Allsvenskan, Croatian HNL, Hungarian NB I, "
                "Romanian SuperLiga, Segunda División, Serie B, 2. Bundesliga, Swiss Super League, Austrian "
                "Bundesliga, Keuken Kampioen Divisie, English League One, English League Two en Série A (BRA). "
                "Dat is een woensdag in een Europese bekerweek — de Champions League draait vandaag en de "
                "nationale competities van deze runlijst liggen stil — en dus geen storing en geen "
                "dekkingsgat. scripts/idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare "
                "stand (afsluitcode 0), dus geen enkele competitie is stil uit de lijst verdwenen — ook niet "
                "de vijftien die vandaag niet spelen, en dat is precies waarom die controle bestaat "
                "(prompts/run-b.md: een fout id geeft geen foutmelding maar nul wedstrijden, en nul "
                "wedstrijden leest als GEEN WEDSTRIJD). EEN van de twee spelende competities draait per "
                "prompts/run-b.md op doelpunten als sterktemaat en komt dus op LIGHT met een lat van 16,0 pp "
                "uit: Czech First League — Fotmob geeft daar geen xG, niet in 2025/2026 en niet in 2026/2027, "
                "en dat is per competitie nagetrokken en niet van de buurlanden overgenomen. Tiers over de 16 "
                "duels: 15 FULL (alle MLS), 1 LIGHT, 0 NONE. Geen enkele ploeg miste de stand van vorig "
                "seizoen, dus de omrekening van §4 is vandaag nergens aangeroepen — MLS kent geen promotie of "
                "degradatie (prompts/run-b.md) en San Diego FC speelde in 2025 al mee."
            ),
            "INZETVENSTER": (
                "VANDAAG IS HET DUURSTE PUNT VAN DEZE RUNLIJST VOOR HET EERST OP VOLLE SCHAAL ZICHTBAAR, EN "
                "runwindow.py VANGT HET. Het venster is [08:00 NL 14 okt, 08:00 NL 15 okt). ALLE VIJFTIEN "
                "MLS-duels trappen af in de band 01:30–04:30 NL op 15 oktober, dus in de nachtband waar "
                "prompts/run-b.md en §3 Stage 1 over gaan. ZES stonden op de daglijst van 2026-10-14 zelf "
                "(23:30 UTC) en NEGEN kwamen van de daglijst van 2026-10-15 (source_day = DAY + 1; 00:30, "
                "01:30 en 02:30 UTC). ONDER DE OUDE UTC-DAGREGEL WAREN DIE NEGEN AAN DE RUN VAN MORGEN "
                "TOEGEWEZEN, en die begint rond 05:05 NL — ná de laatste aftrap van 04:30 NL. Alle negen "
                "waren dan onspeelbaar bij die run aangekomen, en het runrapport had er normaal uitgezien met "
                "een nette nul erin. Dat is letterlijk de voorspelling van 24 september ('op een volle "
                "speelronde van tien tot veertien duels is het de hele ronde'), en EEN VAN DE DRIE "
                "GEPUBLICEERDE REGELS STAAT IN DIE GROEP: FC Dallas – Seattle Sounders FC, aftrap 02:30 NL, "
                "van de daglijst van 15 oktober. Het zestiende duel is het enige Europese: Bohemians 1905 – "
                "Mladá Boleslav om 18:00 NL vandaag. Alle 16 duels hebben RunMatch.playable = True; de run "
                "begon om 05:04 NL, ruim twaalf uur voor de vroegste aftrap die ertoe doet."
            ),
            "POORT7": (
                "BINDT EN HOUDT 14 SELECTIES TEGEN, verdeeld over DRIE wedstrijden, en dat is veel voor deze "
                "poort: Bohemians 1905 – Mladá Boleslav (Mladá Boleslav mist 38% van de selectiewaarde tegen "
                "5% bij de thuisploeg — Dominik Mareš, Adam Kadlec, Filip Lehký), Nashville SC – Sporting "
                "Kansas City (Kansas City mist 53% tegen 2% — Owen Wolff, Moisés Mosquera, Capita) en St. "
                "Louis City – Vancouver Whitecaps (Vancouver mist 19% tegen 4% — Tristan Blackmon geschorst, "
                "Thomas Müller en Jeevan Badwal geblesseerd). DE TWEEDE VAN DIE DRIE IS HET OPVALLENDST: 53% "
                "van de selectiewaarde van Sporting Kansas City ontbreekt, ruim vijf keer de drempel van 10 "
                "procentpunt verschil. En DE DERDE KOST VANDAAG DE KOP VAN DE RUWE LIJST: St. Louis City – "
                "Vancouver Whitecaps, Asian Handicap Vancouver +0.25 @1,8722 (+11,81 pp ruw, selection_score "
                "7,704) staat op plek 1 van de ruwe ranglijst met `context` als bindende poort. Dat is de "
                "poort die precies doet waarvoor hij in augustus is gebouwd: de routine zette 89% van haar "
                "kanten op de zwakkere ploeg, en juist daar hakt een uitvaller het hardst in. "
                "context.check_venue zette relocated bij GEEN ENKEL duel — nul van de zestien. EEN "
                "AANTEKENING OVER DE OPSTELLINGEN, want die bepaalt hoeveel poort 7 vandaag kón doen: geen "
                "enkel duel had om 05:10 NL een bevestigde opstelling. Dat is dezelfde klokbevinding als de "
                "afgelopen weken en geen competitie-eigenschap: Run B draait acht tot eenentwintig uur voor "
                "de aftrap en de opstellingen komen een uur ervoor. Het contextlogboek blijft daarmee de enige "
                "weg naar een meting over het effect van blessures (§1c), en de context is van ÉLK duel "
                "vastgelegd."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met today=2026-10-14 "
                "aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. Hij hield 16 selecties tegen, "
                "verdeeld over VIJF wedstrijden (DC United – Red Bull New York, FC Cincinnati – New England "
                "Revolution, Inter Miami CF – New York City FC, Toronto FC – Orlando City, Real Salt Lake – "
                "San Jose Earthquakes). EN HIJ KOST VANDAAG PLEK 2 VAN DE RUWE LIJST: Real Salt Lake – San "
                "Jose Earthquakes, Asian Handicap San Jose +0.75 @1,8330 (+10,56 pp ruw, selection_score "
                "6,877) staat daar op 2 met `underdog` als bindende poort. WAT ER TEGENOVER STAAT: de "
                "`underdog`-schaduwreeks staat nu op 97 afgewikkelde kandidaten met -2,2% rendement (48,5% "
                "trefkans) — licht negatief, dus de poort bespaart geld, en de uitweg van 25 september "
                "('positieve ROI over >= 30 afgewikkelde kandidaten') is daarmee niet meer de ja die hij op 5 "
                "oktober was. De reeks liep van +16,9% over 36 (5 okt) via -8,7% over 79 (11 okt) en +0,2% "
                "over 89 (12 okt) naar -2,2% over 97 vandaag; dat heen en weer over negen dagen is zelf het "
                "bewijs dat deze reeks nog te klein is om er een poort op te verzetten (§6d). §1e verbiedt "
                "bovendien de vraag dagelijks opnieuw te stellen, en er is niets wezenlijk veranderd. De "
                "gemeten kalibratiefout die de rem verantwoordt staat er nog: +1,79 pp te veel kans op "
                "longshots en -3,50 pp te weinig op favorieten over 4722 uitkomsten. `underdog_ruw` staat "
                "onveranderd op 17 gevallen met -8,8%; poort8_ruw is leeg omdat alle 16 al op de herijkte "
                "schaal sneuvelden en §1e verbiedt dezelfde selectie twee keer te boeken, en "
                "poort8_vervallen is leeg omdat het venster van zes dagen voorbij is. Die twee reeksen "
                "blijven twee populaties en worden nooit opgeteld."
            ),
            "POORT9_BINDT_VOOR_HET_EERST_ECHT": (
                "VANDAAG VALT DE EERSTE RIJ OOIT IN DE REEKS `doelpunten_onder`, EN DE POORT KOST DAARMEE "
                "PLEK 2 VAN DE GEPUBLICEERDE LIJST. Poort 9 (§1h, unders.BINDS_FROM = 2026-10-12) houdt CF "
                "Montréal – Atlanta United tegen: Over/Under Under 3,5 @1,65 (1xBet), herijkte edge +8,66 pp "
                "tegen de verzwaarde lat van 10,0 pp, selection_score 5,999. DIE SCORE IS HOGER DAN DIE VAN "
                "TWEE VAN DE DRIE REGELS DIE WEL ZIJN GEPUBLICEERD (FC Dallas 5,224 en Columbus Crew 5,081), "
                "dus hij zou op plek 2 van de dagranglijst hebben gestaan. Op 12 oktober hield de poort nul "
                "selecties tegen en op 11 oktober bond hij nog niet; dit is dus de eerste keer dat hij "
                "werkelijk iets wegneemt, en de reeks die §1h als de meting aanwijst begint hiermee op ÉÉN "
                "rij. Lees hem niet onder ~30 afgewikkelde gevallen (§6d). "
                "EN DAN DE BEVINDING DIE ERBIJ HOORT EN DIE EEN BESLUIT VAN DE GEBRUIKER VRAAGT: DE POORT "
                "WERKT VANDAAG NIET-MONOTOON. unders.check laat met opzet élke Under door die de GEWONE "
                "drempel van 8,0 pp niet haalt — de docstring zegt waarom: anders loopt de reeks "
                "`doelpunten_onder` vol met kandidaten die nooit een bet konden worden, de "
                "'twee populaties'-fout van §1e. Die redenering berust erop dat `edge` dan de bindende poort "
                "is. SINDS §5b (20 sep) IS `edge` GEEN POORT MEER MAAR EEN AFKAPPING, en dan houdt niets die "
                "Unders nog tegen. Het resultaat is vandaag letterlijk te zien: de FULL-Under met de MEESTE "
                "edge (CF Montréal, +8,66) is geblokkeerd en twee FULL-Unders met MINDER edge (Columbus Crew "
                "+7,70 en FC Dallas +7,69) zijn gepubliceerd. Precies de band die §6g als de slechtste van de "
                "hele reeks meet (8–10 pp, -47,7% over 15 gevallen) wordt weggehouden, terwijl de band eronder "
                "(0–8 pp, -34,1% over 26 gevallen) wél publiceert. DIT IS GEEN REDEN OM VANDAAG IETS AAN DE "
                "POORT TE DOEN: §1h en §6g verbieden een run uitdrukkelijk om deze poort op eigen initiatief "
                "te verzetten, en het gaat over risicobereidheid. Het staat als `besluit` in het dagrapport."
            ),
            "DRIE_UNDERS_OP_DE_GEMETEN_SCHEVE_KANT": (
                "ALLE DRIE DE GEPUBLICEERDE REGELS ZIJN EEN UNDER 3,5 OP FULL-DATA, EN DAT IS EXACT DE "
                "MARKT-EN-KANT WAARVAN §6g OP UITKOMSTEN HEEFT GEMETEN DAT ZE SCHEEF STAAT. Twee metingen van "
                "vandaag, allebei uit margins.py goalbias over 1186 doorgerekende duels: (1) de VORMFOUT — "
                "het gemiddelde aantal doelpunten klopt (voorspeld 3,048 / werkelijk 3,048, z = -0,01) maar "
                "de verdeling niet: -2,2 pp massa op 2 doelpunten en +2,6 pp op 4 doelpunten (boven twee "
                "standaardfouten), waardoor P(Under 3,5) structureel 2,0 pp te hoog staat bij ÉLK duel, vóór "
                "er iets gekozen is; en (2) het SELECTIE-EFFECT — in de 60 duels waarin de routine werkelijk "
                "een Under speelde vielen er +0,545 doelpunt per duel méér dan haar eigen lambda zei, z = "
                "+2,58, terwijl de Over-kant op z = -0,48 staat over 41 duels. Over het hele logboek: Under "
                "-16,5% tegen Over +10,6%. DE REPARATIE VAN DE VORMFOUT (keuze a van 11 oktober) STAAT NOG "
                "OPEN; poort 9 is een rem op het symptoom en die rem houdt vandaag juist de Under met de "
                "meeste edge tegen en niet de twee met de minste. EN DE ONAFHANKELIJKE CONTROLE WIJST "
                "DEZELFDE KANT OP: tegen Pinnacle — volgens §5 (Stage 5, stap 2) het scherpste publieke "
                "expertoordeel dat er is, met een marge van 3 tot 5% tegen 6 tot 10% bij de rest — staat het "
                "model op ALLE VIER deze duels aan de Under-kant boven de markt, op Pinnacle's eigen lijn "
                "gemeten en de-vigd: Toronto FC +10,8 pp (62,7% tegen 51,9% op 3,5), CF Montréal +9,5 pp "
                "(58,6% tegen 49,1% op 3,0), Columbus Crew +8,5 pp (60,8% tegen 52,3% op 3,25) en FC Dallas "
                "+8,1 pp (56,6% tegen 48,6% op 3,0). Vier van de vier dezelfde richting op dezelfde kant is "
                "geen bevestiging van de edge maar de signatuur van de gemeten scheefstand. DAT MOET IN HET "
                "DAGRAPPORT STAAN en het staat er (§6g, laatste alinea: noem bij een gepubliceerde Under dat "
                "deze kant meetbaar scheef staat). WAT HET NIET IS: geen reden om vandaag de rangorde te "
                "negeren of de lijst leeg te laten — §5b schrijft de rangorde voor en §1 verbiedt zowel bets "
                "forceren als bets achterhouden buiten de poorten om."
            ),
            "BEVINDING_POORT5_ZEVENTIENDE_DAG": (
                "POORT 5 VANGT OPNIEUW RUIM DRIEKWART WEG: 203 van de 280 selecties (72,5%) sneuvelden op "
                "'tweede_methode' — de twee methodes verslaan de markt niet dezelfde kant op. Daarna 28 op de "
                "edge, 16 op de underdog-poort, 14 op context, 12 op de koersband, 5 op robuustheid en 1 op "
                "poort 9; één selectie haalde alle negen poorten (Toronto FC – Orlando City, Under 3,5). De "
                "reeks staat nu op ruim tien dagen rond twee derde tot driekwart, en §5 ('Net niet') zegt dat "
                "zoiets dagen achtereen een BEVINDING is over de splitsmethode en geen ruis. WAT HET "
                "SCHADUWLOGBOEK ERVAN ZEGT: 'tweede_methode' staat op 131 afgewikkelde kandidaten met -4,0% "
                "rendement (44,3% trefkans) — de poort bespaart dus geld. VANDAAG MET EEN DRAAI DIE HET "
                "VERMELDEN WAARD IS: anders dan op 12 oktober, toen alle drie de regels op de splitsmethode "
                "leunden, rust vandaag maar ÉÉN van de drie daarop. Per regel de twee armen apart: Toronto FC "
                "– Orlando City xG +5,74 / splits +24,71; FC Dallas – Seattle xG +7,68 / splits +4,64; "
                "Columbus Crew – Charlotte xG +8,35 / splits +2,11. Bij de onderste twee doen de armen "
                "ongeveer hetzelfde en bij Columbus Crew is de xG-arm zelfs de sterkste van de twee — dat "
                "zijn de best onderbouwde regels van de dag, ook al staan ze lager in de rangorde. De kop van "
                "de lijst is juist de regel waar de armen het verst uiteen liggen (bijna 19 procentpunt), en "
                "§1f heeft op 392 afgerekende gevallen gemeten dat de splitsmethode als kansbron vrijwel "
                "niets toevoegt. NIET VANDAAG EEN WEGING VERANDEREN (§6d, en §1f noemt de curve tussen 0,7 "
                "en 1,0 vlak)."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE IS VANDAAG LEEG, EN DAT IS GEEN STORING MAAR HET "
                "ONTWERP VAN 24 SEPTEMBER DAT TOT HET UITERSTE IS DOORGEVOERD. uplift_observations liet "
                "BEIDE spelende competities uit de pool weg: Czech First League omdat er in geen van beide "
                "seizoenen xG is, en MLS omdat zijn seizoen over de helft is (29 van 34 speeldagen), waardoor "
                "league_level route 'lopend' kiest. De factor komt daarmee uit op 1,0000 over 0 speeldagen en "
                "0 competities. GEVOLG VOOR DE ENIGE COMPETITIE DIE DE POOL NOG ZOU GEBRUIKEN: Czech First "
                "League draait op route 'vorig+uplift' met factor 1,0000, dus feitelijk op het ongeschaalde "
                "niveau van vorig seizoen (thuis 1,379 / uit 1,217 / basis 1,347, op doelpunten omdat er geen "
                "xG is). Dat is de eerlijke uitkomst — er is vandaag geen enkele waarneming om een correctie "
                "op te baseren — maar schrijf het op in plaats van het als 'factor 1,0' weg te laten, want "
                "van buitenaf is 'geen correctie nodig' niet te onderscheiden van 'geen waarneming "
                "beschikbaar'. ALLE VIJFTIEN GEPUBLICEERDE EN DOORGEREKENDE MLS-DUELS DRAAIEN OP ROUTE "
                "'lopend': niveau thuis 1,852 / uit 1,405 / basis 1,542, rechtstreeks uit het lopende seizoen "
                "en ongeschaald. Dat is exact de route die §4/Stage 5 voor een halverwege lopend "
                "kalenderjaarseizoen voorschrijft, en de seizoensnotatie is '2025'/'2026' en niet "
                "'2025/2026' zoals prompts/run-b.md eist — anders valt Fotmob stil terug op het lopende "
                "seizoen en rekent de run zijn prior op de stand van vandaag."
            ),
            "BEURSKOERS": (
                "EEN van de drie gepubliceerde regels staat op een BEURS — Matchbook — en §5 eist dan beide "
                "getallen, want de gebruiker ziet op de site de koers vóór commissie: Columbus Crew – "
                "Charlotte FC Under 3,5 1,73 bruto / 1,7154 netto na 2% commissie. edge_pp en "
                "selection_score rekenen met de NETTO koers (oddsapi.net_price). DE ANDERE TWEE STAAN BIJ "
                "1XBET — Toronto FC – Orlando City Under 3,5 @1,90 en FC Dallas – Seattle Sounders Under 3,5 "
                "@1,66 — en dat is geen beurs en geen scherpe boekmaker. §5 (Stage 5, stap 2) noemt Pinnacle "
                "het scherpste publieke expertoordeel dat er is; een edge tegen een ruimere aanbieder is een "
                "zwakkere claim dan dezelfde edge tegen Pinnacle, en Pinnacle noteerde dezelfde kant vandaag "
                "8 tot 11 procentpunt lager (zie DRIE_UNDERS_OP_DE_GEMETEN_SCHEVE_KANT). Alle drie de regels "
                "komen van The Odds API op de beste prijs per uitkomst; geen van de drie leunt op het "
                "BetExplorer-marktgemiddelde."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": (
                "17 CREDITS VAN EEN PLAFOND VAN 540 (19.469 over bij api_check.py, 531 verbruikt deze maand, "
                "18 dagen tot de maandwissel, 2 runs per dag). Stap 0: ÉÉN bulk-aanroep à 3 credits (h2h + "
                "spreads + totals) voor de enige spelende competitie MET sportkey, MLS (soccer_usa_mls), die "
                "30 events teruggaf; split_budget(540, 1) -> (1, 1) dus niemand viel buiten de bulk en de "
                "losse totals-stap was niet nodig. Stap 2: BTTS voor 14 van de 16 duels met een kandidaat-edge "
                "(14 credits à 1). Twee duels kregen geen BTTS, allebei met een reden in markets_checked: "
                "Colorado Rapids – Minnesota United omdat er geen kandidaat-edge in dat duel zat (§1a stap 2) "
                "en Bohemians 1905 – Mladá Boleslav omdat Czech First League geen sportkey heeft. "
                "MARKTBALANS-CONTROLE: GEHAALD, maar met de kleinst mogelijke marge die er bestaat — één "
                "competitie met een doelpuntenmarkt op één inkoopbare competitie, want MLS kreeg via de bulk "
                "alle zes markten (1X2, AH, DNB, DC, OU, BTTS) en is de enige koper. §1a eist dat je meldt "
                "HOE RUIM die controle slaagt, en hier is het antwoord: hij slaagt omdat de bulk-aanroep per "
                "ontwerp zowel een uitkomst- als een doelpuntenmarkt levert, niet omdat het plafond ruim was. "
                "Czech First League heeft GEEN sportkey en draait op het gratis BetExplorer-marktgemiddelde "
                "over 3 boeken (1 @2,14, X @3,48, 2 @3,02) als enige 1X2-bron; daar is de bookmaker niet "
                "herleidbaar en valt de edge systematisch te laag uit — conservatief, dus geen risico op te "
                "veel bets, maar niet vergelijkbaar met een duel waar de beste prijs wél bekend is. ALLE DRIE "
                "DE GEPUBLICEERDE REGELS KOMEN UIT DE DOELPUNTENMARKT (Over/Under), en dat is bij één "
                "inkopende competitie met alle zes markten open geen inkoopartefact maar de uitkomst van "
                "selection_score — zie DRIE_UNDERS_OP_DE_GEMETEN_SCHEVE_KANT voor waarom dat juist vandaag "
                "een aantekening verdient."
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
        s3 = json.load(open("tmp-run/rb_oct14_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct14_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct14_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct14_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

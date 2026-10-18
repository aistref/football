"""Run B 16 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct18_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. Tien van de zeventien competities speelden, met vijftien duels in
het inzetvenster en nul afgekapt (cap 55 op vrijdag). VIER gepubliceerde regels, waarvan ÉÉN zijn
eigen lat haalt.

Drie dingen die vandaag in de parameters horen:

* **Eén regel haalt de drempel, drie staan er op rangorde.** Rapid Wien - Hartberg Under 3,5 @1,90
  haalt +16,12 pp én de verzwaarde lat van poort 9 (10,0 pp). De andere drie staan onder hun lat en
  zijn er per §5b als rangorde en niet als vondst.
* **De BetExplorer-slug van Série A (BRA) is verhuisd**, en dat is dezelfde stille faalstand als
  het Serie B-id: HTTP 200 met nul rijen. Gerepareerd in `rb_oct18_bxfix.py`, zonder credits.
* **De stadioncontrole gaf één echt alarm en één vals**, en het valse is in `scripts/context.py`
  gerepareerd (`_norm_ground` liet "Stadium" tegen "Stadion" staan).

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-18"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-18T05:05:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct18_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.017, b=0.011 op 4938 "
                "afgerekende gevallen, fitted_through 2026-10-17. Die datum is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist; hij "
                "wikkelde vanochtend 9 waarnemingen af). De correctie is praktisch de identiteit — het ruwe "
                "model zei gemiddeld 33,3% en het gebeurde 33,3% — en ze VERHOOGT een kans over vrijwel de "
                "hele speelbare band: +0,1 pp op 40%, +0,3 pp op 50%, +0,4 pp op 60%, +0,5 pp op 70%, en ze "
                "verlaagt alleen onder ongeveer 35%. OP ALLE VIJF DE GEPUBLICEERDE REGELS TELDE ZE DUS EDGE "
                "BIJ IN PLAATS VAN AF (Salzburg +14,12 ruw -> +14,65 herijkt; Juve Stabia +12,04 -> +12,54; "
                "Sturm Graz +9,67 -> +10,09; FC Cincinnati +9,60 -> +10,01; Tromsø +7,00 -> +7,47). EN "
                "VANDAAG BINDT DAT, bij twee van de vijf regels: zie "
                "BEVINDING_BET_BEIDE_EN_POORT_9_OP_TWEE_SCHALEN. Lees de identiteit zoals §1e punt 3 "
                "voorschrijft: de reeks is de ONGESELECTEERDE ijksteekproef en breder dan de staart waarop "
                "deze routine speelt, dus 'de fit is de identiteit' betekent niet dat het model recht staat "
                "op die staart — §6e meet daar nog +1,70 pp te veel kans op longshots en -3,41 pp te weinig "
                "op favorieten over 5283 uitkomsten."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "VEERTIEN van de zeventien competities speelden, met 45 duels in het inzetvenster. Greek "
                "Super League (5), Eliteserien (5), Allsvenskan (5), Segunda División (5), Série A BRA (4), "
                "Czech First League (3), Serie B (3), 2. Bundesliga (3), Austrian Bundesliga (3), Croatian "
                "HNL (2), Hungarian NB I (2), Romanian SuperLiga (2), Keuken Kampioen Divisie (2) en MLS (1). "
                "DRIE hadden GEEN WEDSTRIJD: Swiss Super League, English League One en English League Two — "
                "de twee Engelse divisies spelen zaterdag en dinsdag, de Zwitserse had gisteren haar ronde. "
                "scripts/idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand "
                "(afsluitcode 0), dus geen enkele competitie is stil uit de lijst verdwenen — ook niet die "
                "drie die vandaag niet spelen, en dat is precies waarom die controle bestaat "
                "(prompts/run-b.md: een fout id geeft geen foutmelding maar nul wedstrijden, en nul "
                "wedstrijden leest als GEEN WEDSTRIJD). VIJF van de spelende competities draaien per "
                "prompts/run-b.md op doelpunten als sterktemaat en komen dus op LIGHT met een lat van 16,0 "
                "pp uit: Czech First League, Croatian HNL, Hungarian NB I, Romanian SuperLiga en Keuken "
                "Kampioen Divisie — Fotmob geeft daar geen xG, niet in 2025/2026 en niet in 2026/2027, per "
                "competitie nagetrokken en niet van de buurlanden overgenomen. Tiers over de 45 duels: 21 "
                "FULL, 19 LIGHT, 5 NONE. ZESTIEN DUELS HEBBEN EEN PLOEG ZONDER STAND IN HET VORIGE SEIZOEN "
                "en gingen langs de omrekening van §4; ELF lukten (alle elf LIGHT, nooit FULL) en VIJF niet. "
                "Die vijf vallen in drie soorten, alle drie met NONE als eerlijke uitkomst: ÉÉN buiten het "
                "gemeten bereik van de omrekenfactor (conversion_in_range — Girona, relatieve aanval 1.160 "
                "na omrekening tegen een gemeten maximum; dat is de Coventry-val die die poort moet vangen), "
                "DRIE met een ploeg die ook in de divisie boven of onder haar niet in de stand staat "
                "(Kalamata staat niet in Super League 2, Arezzo niet in de Serie A, VfL Osnabrück niet in de "
                "Bundesliga — die komen van nóg een niveau lager) en ÉÉN waar het divisiepaar zelf niet "
                "gemeten is (Remo: Série B ligt onder Série A maar staat niet in promotion.TIER2, en §4 "
                "verbiedt een factor te verzinnen). TWEE OMREKENINGEN LIEPEN LANGS DE GEPOOLDE FACTOR, "
                "allebei OMLAAG: FC Volendam en Heracles uit de Eredivisie naar de Keuken Kampioen Divisie, "
                "x1.654 aanval / x0.647 verdediging. §4 noemt dat paar met naam als het laatste dat op "
                "POOLED_GAP draait — het is op 9 oktober wél gemeten (x1.772 / x0.621 over n=23) maar niet "
                "toegepast, want daarvoor is een eigen tabel voor de neerwaartse richting nodig en dat staat "
                "als besluit bij de gebruiker. Geen van beide duels is een gepubliceerde regel geworden, dus "
                "het kost vandaag niets; in de richting OMHOOG staat er geen enkel paar meer op de pool."
            ),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 18 okt, 08:00 NL 19 okt) en runwindow.py levert 45 duels, alle 45 "
                "met RunMatch.playable = True. VIERENVEERTIG stonden op de daglijst van 2026-10-18 en ÉÉN op "
                "die van 2026-10-19: Remo – RB Bragantino om 00:30 NL, precies de nachtband waar "
                "prompts/run-b.md over gaat en die de oude UTC-dagregel aan de verkeerde run gaf. Dat duel "
                "komt op tier NONE uit (geen gemeten divisiepaar onder Série A), dus het kost vandaag geen "
                "regel — maar het staat wél in de dekkingstabel in plaats van stil te verdwijnen. Omgekeerd "
                "kwam er geen enkel duel uit de band [00:00, 08:00) NL van vandaag zelf; dat venster is door "
                "de run van gisteren bediend. De run begon om 05:04 NL, ruim zeven uur voor de vroegste "
                "aftrap (12:15 NL, RKC Waalwijk – FC Volendam)."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "ALLE ZEVENTIEN COMPETITIES ZIJN DOOR EEN TWEEDE, ONAFHANKELIJKE BRON BEVESTIGD, en de twee "
                "bronnen zijn het over de hele runlijst exact eens: Fotmob 45 duels in het venster, "
                "BetExplorer 45, en per competitie gelijk (Greek Super League 5-5, Eliteserien 5-5, "
                "Allsvenskan 5-5, Segunda División 5-5, Série A 4-4, Czech First League 3-3, Serie B 3-3, 2. "
                "Bundesliga 3-3, Austrian Bundesliga 3-3, Croatian HNL 2-2, Hungarian NB I 2-2, Romanian "
                "SuperLiga 2-2, Keuken Kampioen Divisie 2-2, MLS 1-1). Dat geldt óók voor de DRIE "
                "competities die vandaag GEEN WEDSTRIJD hebben — Swiss Super League 0-0, English League One "
                "0-0 en English League Two 0-0 — en juist daar moet de tweede bron kijken, want 'nul "
                "wedstrijden' is de uitkomst die een kapot id en een lege speeldag niet van elkaar "
                "onderscheidt. Dit is de poort uit §1 die de scheduler expliciet noemt, en ze staat vandaag "
                "op 17 van 17. BetExplorer labelt in UK-tijd (NL −1 uur), dus het venster is daar [18.10. "
                "07:00, 19.10. 07:00); dat is omgerekend en de omrekening staat in rb_oct18_bevestiging.py."
            ),
            "ALLE_VIJF_DE_REGELS_STAAN_OP_DE_GEMETEN_SCHEVE_KANT": (
                "ALLE VIJF DE GEPUBLICEERDE REGELS ZIJN EEN UNDER OP FULL-DATA. Gisteren waren het vier van "
                "de vijf, vandaag vijf van de vijf, en dat is exact de markt-en-kant waarvan §6g op "
                "UITKOMSTEN heeft gemeten dat ze scheef staat. Dat hoort vooraan in het rapport en niet in "
                "een voetnoot. Twee metingen van vandaag, beide uit margins.py goalbias over 1335 "
                "doorgerekende duels: (1) de VORMFOUT — het gemiddelde aantal doelpunten klopt (voorspeld "
                "3,048 / werkelijk 3,044, z = -0,07) maar de verdeling niet: -2,0 pp massa op 2 doelpunten "
                "en +2,1 pp op 4 doelpunten (boven twee standaardfouten), waardoor P(Under 2,5) 1,7 pp en "
                "P(Under 3,5) 1,9 pp te hoog staat bij ÉLK duel, vóór er iets gekozen is; en (2) het "
                "SELECTIE-EFFECT — in de 74 duels waarin de routine werkelijk een Under speelde vielen er "
                "+0,501 doelpunt per duel méér dan haar eigen lambda zei (z = +2,61), terwijl de Over-kant "
                "op z = -0,79 staat over 45 duels. WAT DAT RUWWEG VAN DE EDGES AFHAALT (de vormfout alleen, "
                "zonder het selectie-effect): Salzburg +14,65 -> ongeveer +12,7 pp, Juve Stabia +12,54 -> "
                "+10,8, Sturm Graz +10,09 -> +8,2, FC Cincinnati +10,01 -> +8,1 en Tromsø +7,47 -> +5,6. "
                "Alleen de bovenste twee blijven dan boven de verzwaarde lat van poort 9. EN DE "
                "ONAFHANKELIJKE CONTROLE WIJST DEZELFDE KANT OP: tegen Pinnacle — volgens §5 (Stage 5, stap "
                "2) het scherpste publieke expertoordeel dat er is, vandaag met een marge van 2,8 tot 4,3% "
                "— staat het model op de Under-kant +20,63 pp boven de markt bij Salzburg (Pinnacle-lijn "
                "3,25: eigen 73,7% tegen 53,1%), +21,17 pp bij Juve Stabia (lijn 2,25), +9,59 pp bij FC "
                "Cincinnati (lijn 3,50, DEZELFDE lijn als de bet) en +4,09 pp bij Sturm Graz (lijn 2,75, "
                "ook dezelfde lijn). Alleen Tromsø staat met -0,55 pp onder Pinnacle, op lijn 2,75 tegen de "
                "lijn 3 van de bet. Over alle 27 (duel, lijn)-paren is het gemiddelde verschil +1,18 pp met "
                "16 van 27 boven Pinnacle — de scheefstand is dus NIET dagbreed, en juist de twee bovenste "
                "gepubliceerde Unders zijn de grootste uitschieters van de hele dag. DAT MAAKT HET GEVAL "
                "ERNSTIGER EN NIET MILDER. WAT HET NIET IS: geen reden om de rangorde te negeren of de lijst "
                "leeg te laten — §5b schrijft de rangorde voor en §1 verbiedt zowel bets forceren als bets "
                "achterhouden buiten de poorten om."
            ),
            "BEVINDING_BET_BEIDE_EN_POORT_9_OP_TWEE_SCHALEN": (
                "DE BEVINDING VAN DEZE RUN: TWEE VAN DE VIJF GEPUBLICEERDE REGELS HALEN POORT 9 OP DE "
                "HERIJKTE SCHAAL EN NIET OP DE RUWE, EN DE TWEE CODEPADEN DIE DAAROVER GAAN GEVEN EEN "
                "VERSCHILLEND ANTWOORD. Sturm Graz – Grazer AK Under 2,75 staat op +10,09 pp herijkt en "
                "+9,67 ruw; FC Cincinnati – Columbus Crew Under 3,5 op +10,01 en +9,60. De verzwaarde lat "
                "van poort 9 (§1h) is 10,0 pp voor een FULL-Under, dus beide halen hem herijkt met 0,09 "
                "respectievelijk 0,01 procentpunt marge en missen hem ruw. GEVOLG: de vlag `bet_beide` in "
                "het analysescript staat bij beide op False, dus dat script zet row['bet'] = False en geeft "
                "als reden 'alleen de ruwe schaal hield hem tegen'; `scripts/toplist.py` — het script dat "
                "§6b-5e als de publicerende route aanwijst en waaruit `report.py` de lijst rendert — toetst "
                "de poorten uitsluitend op de HERIJKTE kans en zet ze wél in de lijst. GEPUBLICEERD IS DE "
                "LIJST VAN toplist.py, en dat is naar de letter van de regels de juiste keuze: §1 zegt dat "
                "een bet alle poorten moet halen op de HERIJKTE my_prob, en §1e boekt de ruwe schaal bij "
                "poort 8 met opzet als METING (`underdog_ruw`) en niet als veto — twee populaties die nooit "
                "worden opgeteld. Poort 9 hoort dan dezelfde behandeling te krijgen. WAAROM `bet_beide` TOCH "
                "NIET ZOMAAR WEG KAN: §5a heeft die vlag in september gebouwd voor de EDGE-DREMPEL, toen die "
                "nog een poort was, met het argument dat 'hij haalt beide modellen' dezelfde eis is hardop "
                "gezegd. Sinds §5b (20 sep) is de edge een afkapping en geen poort meer, en daarmee is de "
                "vlag stil van betekenis veranderd: ze werkt nu als een extra, strengere eis op de zeven "
                "overgebleven poorten, en dat staat nergens in de regels. Vandaag is dat zichtbaar geworden "
                "omdat de fit sinds 20 september VERHOOGT in plaats van verlaagt. WAT DIT VANDAAG WEL EN "
                "NIET DOET: het verandert de lijst niet (toplist.py publiceert en heeft het laatste woord) "
                "maar het maakt row['bet'], row['reason'] en de near_miss-boekhouding in data/run-state/ "
                "tegenstrijdig met de gepubliceerde lijst. Dat laatste is afgedekt — publiceer.py hernoemt "
                "een near_miss naar near_miss_gepubliceerd zodra het duel een regel kreeg, dus er gaat geen "
                "schaduwrij naar data/shadow.jsonl die tegelijk een echte bet is — maar de tegenspraak zelf "
                "is er en hij is niet opgelost. EEN RUN VERZET DEZE POORT NIET OP EIGEN INITIATIEF (§1h, "
                "§6d): de vraag of `bet_beide` een veto of een meting hoort te zijn gaat over "
                "risicobereidheid en hoort bij de gebruiker. Ze staat één keer in het dagrapport onder 'Wat "
                "er nog moet gebeuren' met owner = besluit, en wordt daarna niet herhaald. ZOLANG ZE "
                "OPENSTAAT blijft de lijst van toplist.py de lijst, want dat is wat §1 en §6b-5e zeggen. DE "
                "REEKS DIE HET MOET METEN: `herijking_omgekeerd` staat op 3 afgewikkelde gevallen (0 "
                "winnaars, -100%) — veel te weinig om te lezen (§6d eist ~30), en de spiegel `herijking` op "
                "56 gevallen met -4,5%."
            ),
            "POORT7": (
                "BINDT EN HOUDT TWAALF SELECTIES TEGEN, verdeeld over VIJF wedstrijden die daarmee hun hele "
                "kant kwijt zijn: Baník Ostrava – Sparta Prague (Sparta had 3 dagen rust tegen 8 bij Baník), "
                "Sirius – Elfsborg (Sirius mist 19% van de selectiewaarde tegen 2% bij Elfsborg — Jesper "
                "Uneken en Otso Liimatta), Fluminense – Santos (Fluminense 4 dagen rust tegen 7) en twee "
                "andere. DAT IS DE DUURSTE POORT VAN VANDAAG IN RANGORDETERMEN: Fluminense – Santos staat op "
                "plek 3 van de RUWE lijst (1X2 Fluminense @2,4504, +13,86 pp, selection_score 7,577) en "
                "Sirius – Elfsborg op plek 4 (Asian Handicap Sirius -0,25 @1,9310, +9,99 pp, score 6,172), "
                "en geen van beide komt in de herijkte lijst. WAT ER WEL IS OPGEHAALD en wat §1c eist vast "
                "te leggen: de context van ÉLK van de 45 duels, ook de 5 op tier NONE — de cap kapte "
                "vandaag niets af. Dat is de steekproef van ctxlog.py, en die staat nu op 1252 afgewikkelde "
                "wedstrijden. DE STADIONCONTROLE GAF NUL ALARMEN: alle 45 duels spelen in het eigen stadion "
                "van de genoteerde thuisploeg, geen enkele relocated-vlag. GEEN ENKEL DUEL HAD OM 05:15 NL "
                "EEN BEVESTIGDE OPSTELLING (alle 45 op lineupType = lastStarting11). Dat is dezelfde "
                "klokbevinding als de afgelopen weken en geen competitie-eigenschap: Run B draait zeven tot "
                "twintig uur voor de aftrap en de opstellingen komen een uur ervoor."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met today=2026-10-18 "
                "aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. Hij hield 21 selecties tegen "
                "en kost vandaag plek 5 van de RUWE lijst (Kifisia FC +0.25 @1,85, +9,33 pp, score 5,914). "
                "WAT ER TEGENOVER STAAT: de `underdog`-schaduwreeks staat nu op 159 kandidaten, 142 "
                "afgewikkeld, -1,0% rendement (50,0% trefkans) — nog net negatief, dus de poort bespaart "
                "geld, maar de reeks is sinds 17 oktober van -6,4% naar -1,0% geschoven en kruipt richting "
                "nul. DAT IS GEEN AANLEIDING OM DE VRAAG OPNIEUW TE STELLEN: §1e verbiedt dat uitdrukkelijk "
                "zolang er niets wezenlijk verandert, het teken is niet gedraaid, en de gemeten "
                "kalibratiefout die de rem verantwoordt staat er nog (+1,70 pp te veel kans op longshots en "
                "-3,41 pp te weinig op favorieten over 5283 uitkomsten). Draait het teken wél, dan is dát "
                "het moment. `underdog_ruw` staat onveranderd op 17 gevallen met -8,8%; die twee reeksen "
                "blijven twee populaties en worden nooit opgeteld. poort8_vervallen is leeg omdat het "
                "venster van zes dagen voorbij is."
            ),
            "POORT9": (
                "POORT 9 (§1h, unders.BINDS_FROM = 2026-10-12) HOUDT VANDAAG VIJF SELECTIES TEGEN, alle vijf "
                "een Under op FULL-data in de band 8-10 pp — precies de band die §6g als de slechtste van de "
                "hele reeks meet (-47,7% over 15 gevallen). DE NIET-MONOTONIE STAAT ER WEER: Tromsø – KFUM "
                "Under 3 staat met +7,47 pp ONDER de gewone drempel van 8,0 en wordt door unders.check met "
                "opzet vrijgelaten en op rangorde gepubliceerd, terwijl een FULL-Under van bijvoorbeeld "
                "+9,5 pp wordt geblokkeerd. De redenering achter die vrijstelling (elke Under onder 8,0 pp "
                "wordt toch door de edge-poort gestopt, dus de reeks `doelpunten_onder` moet niet vollopen "
                "met kandidaten die nooit een bet konden worden) berust erop dat `edge` een poort is, en "
                "sinds §5b (20 sep) is het een afkapping. DIT IS GEEN NIEUWE VRAAG EN WORDT NIET OPNIEUW "
                "VOORGELEGD: de vraag is op 14 oktober één keer aan de gebruiker voorgelegd en nog niet "
                "beantwoord; §1h en §6g verbieden een run deze poort op eigen initiatief te verzetten. Hij "
                "staat hier als feit en in het dagrapport onder de regels zelf als voorbehoud. De reeks "
                "`doelpunten_onder` staat op 4 afgewikkelde gevallen (2 winnaars, -22,0%); lees hem niet "
                "onder ~30 (§6d), en reken op ongeveer één rij per paar dagen."
            ),
            "BEVINDING_POORT5_EENENTWINTIGSTE_DAG": (
                "POORT 5 VANGT OPNIEUW RUIM ZEVENTIG PROCENT WEG: 330 van de 464 selecties (71,1%) "
                "sneuvelden op 'tweede_methode' — de twee methodes verslaan de markt niet dezelfde kant op. "
                "Daarna 53 op de edge, 26 op de koersband, 21 op de underdog-poort, 12 op context, 5 op "
                "robuustheid en 5 op poort 9; TWAALF selecties haalden alle negen poorten op de herijkte "
                "schaal, verdeeld over VIER wedstrijden, en §1a koos daar de hoogste selection_score. De "
                "reeks staat nu bijna drie weken rond twee derde tot vier vijfde, en §5 ('Net niet') zegt "
                "dat zoiets dagen achtereen een BEVINDING is over de splitsmethode en geen ruis. WAT HET "
                "SCHADUWLOGBOEK ERVAN ZEGT: 'tweede_methode' staat op 168 kandidaten, 151 afgewikkeld, "
                "-9,9% rendement (41,7% trefkans) — de poort bespaart dus geld. DE VIJF REGELS LEUNEN OP "
                "ZEER VERSCHILLENDE ARMEN, en dat is het vermelden waard: Salzburg staat op xG +14,05 pp en "
                "splits +14,39 pp (de twee methodes zijn het eens), maar Sturm Graz komt bijna volledig van "
                "de SPLITSARM (xG +7,86 tegen splits +16,92) en Tromsø nog sterker (xG +2,45 tegen splits "
                "+25,21). Dat is de zwakke arm: §1f heeft op 392 afgerekende gevallen gemeten dat de "
                "splitsmethode als kansbron vrijwel niets toevoegt en alleen als veto zijn geld opbrengt. "
                "BIJ TROMSØ IS DE ZWAKSTE STAND VAN HET (shrink, rho)-GRID 0,15 pp — poort 6 staat daar dus "
                "op een haar open, en dat hoort bij de regel te staan in plaats van alleen in de tabel. "
                "Salzburg 12,65, Juve Stabia 7,10, Sturm Graz 6,30 en FC Cincinnati 9,50. NIET VANDAAG EEN "
                "WEGING VERANDEREN (§6d, en §1f noemt de curve tussen 0,7 en 1,0 vlak)."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0527 (gepoold 1,0630 over 41 speeldagen, 5 "
                "competities), en NEGEN van de veertien spelende competities zijn uit de pool weggelaten — "
                "dat weglaten is zélf de meting (§3 Stage 5) en hoort daarom integraal in het rapport. VIER "
                "wegens een seizoen over de helft, waardoor league_level route 'lopend' kiest: Eliteserien "
                "(23 van 30 speeldagen), Allsvenskan (24 van 30), MLS (31 van 34) en Série A BRA (31 van "
                "38). VIJF wegens het ontbreken van xG in beide seizoenen: Czech First League, Croatian HNL, "
                "Hungarian NB I, Romanian SuperLiga en Keuken Kampioen Divisie. WAT DE FACTOR VOOR DE "
                "OVERIGEN DOET: de tien competities op route 'vorig+uplift' krijgen het niveau van vorig "
                "seizoen x 1,0527; de vier op route 'lopend' rekenen rechtstreeks met het lopende seizoen, "
                "ongeschaald (Eliteserien thuis 1,827 / uit 1,369 / basis 1,660 en MLS thuis 1,837 / uit "
                "1,405 / basis 1,538). DE SEIZOENSNOTATIE VAN DIE VIER IS '2025'/'2026' EN NIET '2025/2026', "
                "zoals prompts/run-b.md eist — anders valt Fotmob stil terug op het lopende seizoen en "
                "rekent de run zijn prior op de stand van vandaag. DE COMPETITIES VAN DE GEPUBLICEERDE "
                "REGELS: Austrian Bundesliga (twee regels) en Serie B op route 'vorig+uplift' (niveau thuis "
                "1,451 en 1,565), MLS en Eliteserien op route 'lopend'."
            ),
            "BEURSKOERS": (
                "DRIE van de vijf gepubliceerde regels staan op een BEURS en §5 eist dan beide getallen, "
                "want de gebruiker ziet op de site de koers vóór commissie: Salzburg – Altach Under 3,5 "
                "@1,69 BRUTO / 1,6762 NETTO bij MATCHBOOK, Juve Stabia – Südtirol Under 2,5 @1,79 BRUTO / "
                "1,7742 NETTO bij MATCHBOOK, en FC Cincinnati – Columbus Crew Under 3,5 @2,04 BRUTO / "
                "2,0192 NETTO bij MATCHBOOK. edge_pp en selection_score rekenen met de NETTO koers "
                "(oddsapi.net_price). DE ANDERE TWEE STAAN NIET OP EEN BEURS: Sturm Graz – Grazer AK Under "
                "2,75 @1,98 bij PINNACLE en Tromsø – KFUM Under 3 @1,76 bij COOLBET. DIE EERSTE VERDIENT "
                "EEN AANTEKENING VAN TWEE KANTEN: Pinnacle is volgens §5 (Stage 5, stap 2) het scherpste "
                "publieke expertoordeel dat er is, dus een edge tegen Pinnacle is een STERKERE claim dan "
                "dezelfde edge tegen een ruimere aanbieder — maar op de doelpuntenkant van dat duel zegt "
                "Pinnacle zelf +4,09 pp minder Under dan het model, dus de claim is dat Pinnacle er op zijn "
                "eigen lijn naast zit. NEGEN van de veertien spelende competities hebben een sportkey; VIJF "
                "hebben er geen en draaien volledig op het gratis BetExplorer-marktgemiddelde als enige "
                "1X2-bron: Czech First League, Croatian HNL, Hungarian NB I, Romanian SuperLiga en Keuken "
                "Kampioen Divisie. Die vijf hebben dus ook geen handicap-, doelpunten- of BTTS-markt, en dat "
                "staat per duel met die reden in markets_checked."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": (
                "50 CREDITS VAN EEN PLAFOND VAN 684 (19.181 over bij api_check.py, 819 verbruikt deze maand, "
                "14 dagen tot de maandwissel, 2 runs per dag). Stap 0: NEGEN bulk-aanroepen à 3 credits (h2h "
                "+ spreads + totals = 27) voor de negen spelende competities MET sportkey — Greek Super "
                "League (12 events), Eliteserien (7), Allsvenskan (12), Segunda División (12), Serie B (11), "
                "2. Bundesliga (9), Austrian Bundesliga (9), MLS (20) en Série A BRA (15); split_budget(684, "
                "9) -> (9, 9) dus niemand viel buiten de bulk en de losse totals-stap was niet nodig. Stap "
                "2: BTTS voor 23 van de 26 duels met een kandidaat-edge (23 credits à 1). DRIE duels met een "
                "kandidaat-edge kregen geen BTTS, met die reden in markets_checked: Slovácko – FC Zbrojovka "
                "Brno, Baník Ostrava – Sparta Prague en UTA Arad – CFR Cluj spelen in een competitie zonder "
                "sportkey bij The Odds API. MARKTBALANS-CONTROLE: GEHAALD, EN RUIM — NEGEN van de negen "
                "inkoopbare competities kregen via de bulk álle zes de markten (1X2, AH, DNB, DC, OU, BTTS), "
                "dus er is geen enkele competitie met alléén een uitkomstmarkt of alléén een "
                "doelpuntenmarkt. §1a eist dat je meldt HOE RUIM die controle slaagt, en dat is hier negen "
                "op negen in plaats van de één-op-twaalf van 30 augustus. DAT MAAKT DE MARKTVERDELING VAN DE "
                "UITKOMST BETEKENISVOL: alle VIJF de gepubliceerde regels komen uit de DOELPUNTENMARKT "
                "(Over/Under) en nul uit een uitkomstmarkt. Dat is geen inkoopartefact — alle zes markten "
                "dongen mee in negen van de veertien competities, en de sterkste uitkomstmarkten van de dag "
                "(Fluminense 1X2, Sirius AH, Kifisia AH) sneuvelden op poort 7 en poort 8 en niet op het "
                "ontbreken van een prijs — maar het is de uitkomst van selection_score, en zie "
                "ALLE_VIJF_DE_REGELS_STAAN_OP_DE_GEMETEN_SCHEVE_KANT voor waarom juist die kant vandaag een "
                "voorbehoud verdient."
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
        s3 = json.load(open("tmp-run/rb_oct18_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct18_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct18_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct18_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

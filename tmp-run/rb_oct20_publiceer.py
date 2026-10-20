"""Run B 16 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct20_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. Tien van de zeventien competities speelden, met vijftien duels in
het inzetvenster en nul afgekapt (cap 55 op vrijdag). VIER gepubliceerde regels, waarvan ÉÉN zijn
eigen lat haalt.

Drie dingen die vandaag in de parameters horen:

* **Eén regel haalt de drempel, drie staan er op rangorde.** Rapid Wien - Hartberg Under 3,5 @1,90
  haalt +16,12 pp én de verzwaarde lat van poort 9 (10,0 pp). De andere drie staan onder hun lat en
  zijn er per §5b als rangorde en niet als vondst.
* **De BetExplorer-slug van Série A (BRA) is verhuisd**, en dat is dezelfde stille faalstand als
  het Serie B-id: HTTP 200 met nul rijen. Gerepareerd in `rb_oct20_bxfix.py`, zonder credits.
* **De stadioncontrole gaf één echt alarm en één vals**, en het valse is in `scripts/context.py`
  gerepareerd (`_norm_ground` liet "Stadium" tegen "Stadion" staan).

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-20"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-20T05:12:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct20_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.0202, b=0.0130 "
                "op 5220 afgerekende gevallen, fitted_through 2026-10-19. Dat is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist). "
                "De correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,3% en het "
                "gebeurde 33,3% — en ze VERHOOGT een kans over vrijwel de hele speelbare band. Op de drie "
                "gepubliceerde regels telde ze dus edge BIJ in plaats van af: Stevenage +8,00 ruw -> "
                "+8,39 herijkt, AFC Wimbledon +6,57 -> +7,10, Blackpool +7,00 -> +7,61. DAT IS VANDAAG "
                "NIET VRIJBLIJVEND, want het raakt poort 9: Stevenage Under 2,5 staat ruw op +8,58 en "
                "herijkt op +9,08, en poort 9 meet op de HERIJKTE edge — op beide schalen onder de lat "
                "van 10,0, dus het verandert de uitkomst hier niet. Lees de identiteit zoals §1e punt 3 "
                "voorschrijft: de reeks is de ONGESELECTEERDE ijksteekproef en breder dan de staart "
                "waarop deze routine speelt."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de zeventien competities speelden, met 23 duels in het inzetvenster: English "
                "League One (11) en English League Two (12). VIJFTIEN hadden GEEN WEDSTRIJD — Czech First "
                "League, Greek Super League, Eliteserien, Allsvenskan, Croatian HNL, Hungarian NB I, "
                "Romanian SuperLiga, Segunda División, Serie B, 2. Bundesliga, Swiss Super League, "
                "Austrian Bundesliga, Keuken Kampioen Divisie, MLS en Série A (BRA). Dat is een smalle "
                "lijst maar een VOLLE speelronde: twee complete midweekse rondes op één avond, allemaal "
                "om 20:45 of 21:00 NL. scripts/idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json "
                "een bruikbare stand (afsluitcode 0), dus geen enkele competitie is stil uit de lijst "
                "verdwenen — ook niet die vijftien die vandaag niet spelen, en dat is precies waarom die "
                "controle bestaat. BEIDE spelende competities hebben xG bij Fotmob, dus de lat is 8,0 pp "
                "tenzij er is omgerekend. TIERS over de 23 duels: 12 FULL, 5 LIGHT, 6 NONE. ELF DUELS "
                "HEBBEN EEN PLOEG ZONDER STAND IN 2025/2026 en gingen langs de omrekening van §4, in "
                "BEIDE richtingen: omhoog uit League Two (Milton Keynes Dons, Bromley, Notts County, "
                "Cambridge United) en omlaag uit de Championship (Leicester City, Sheffield Wednesday, "
                "Oxford United) respectievelijk uit League One (Exeter City, Northampton Town, Rotherham "
                "United, Port Vale). Vijf lukten en kwamen op LIGHT uit (nooit FULL, §4), zes werden "
                "NONE. GEEN ENKELE OMREKENING LIEP LANGS DE GEPOOLDE FACTOR: beide richtingen draaien "
                "hier op het gemeten football-data.co.uk-paar E1/E2 respectievelijk E2/E3."
            ),
            "VIER_NONES_MISSEN_HUN_BEREIK_OP_EEN_HAAR": (
                "VIER VAN DE ZES NONE-DUELS VALLEN OP conversion_in_range, EN ALLE VIER MISSEN ZE DE "
                "GEMETEN GRENS MET MINDER DAN 0,03 RELATIEVE STERKTE. Dat is geen toeval van één duel en "
                "hoort daarom in het rapport: Cambridge United verdediging 0,557 tegen een ondergrens van "
                "0,565 (0,008 eronder); Exeter City 1,008 tegen 1,033 (0,025); Port Vale 1,008 tegen "
                "1,033 (0,025); Leicester City aanval 0,968 tegen een bovengrens van 0,939 (0,029 "
                "erboven). WAT DAARUIT NIET VOLGT: het bereik oprekken. §4 noemt conversion_in_range "
                "uitdrukkelijk 'een poort, geen aantekening' en de Coventry-val is precies het geval "
                "waarin een ploeg net buiten alles ligt wat ooit is gemeten. WAT ER WEL UIT VOLGT: het "
                "gemeten bereik van de Engelse paren is smal (E2/E3 omhoog n=43, omlaag n=43, E1/E2 "
                "omlaag n=33) en ligt hier vier keer op een dag tegen de rand aan. Dat is een waarneming "
                "over de BREEDTE van de meting, niet over deze vier ploegen, en ze kostte vandaag 4 van "
                "de 23 duels."
            ),
            "GEEN_DIVISIE_ONDER_LEAGUE_TWO_EN_DAT_IS_MEETBAAR": (
                "TWEE DUELS KOMEN OP NONE UIT OM EEN ANDERE REDEN DAN HET BEREIK: Rochdale – Grimsby Town "
                "en York City – Accrington Stanley. Rochdale en York City zijn promovendus uit de "
                "National League, en promotion.TIER2 heeft GEEN INGANG voor 'League Two (ENG)' — de "
                "keten stopt bij League One -> League Two. De omrekening probeert daarom de enige tak die "
                "er wel is (degradant uit League One), vindt die ploegen daar niet, en meldt 'staat niet "
                "in de stand van League One (ENG) 2025/2026'. Die foutmelding beschrijft dus de verkeerde "
                "richting en niet het werkelijke gat. DIT IS EEN ROEMENIË-GEVAL EN GEEN KROATIË-GEVAL, en "
                "dat onderscheid is deze run nagetrokken: Fotmob HEEFT de National League (ccode ENG, id "
                "117) en dat id geeft per seizoen een EIGEN stand — 2018/2019 24 ploegen/46 speeldagen, "
                "2021/2022 23/44, 2024/2025 24/46, 2025/2026 24/46 — dus de stille faalstand van het "
                "Hongaarse id 9117 (één stand voor elk opgevraagd seizoen) doet zich hier NIET voor en "
                "het paar is met measure_gap te meten. NIET VANDAAG GEDAAN EN NIET MET TERUGWERKENDE "
                "KRACHT: §4 schrijft sinds 9 oktober voor dat een nieuwe factor VÓÓR de analyse wordt "
                "gemeten en niet erna, en het toevoegen van een divisiepaar is een besluit van de "
                "gebruiker. Het staat als zodanig in het dagrapport onder 'Wat er nog moet gebeuren'."
            ),
            "POORT9_BINDT_EN_LAAT_TEGELIJK_EEN_ZWAKKERE_UNDER_DOOR": (
                "DIT IS DE BELANGRIJKSTE BEVINDING VAN DEZE RUN EN ZE HOORT VOORAAN. Poort 9 (§1h) hield "
                "vandaag TWEE FULL-Unders tegen: Luton Town – Barnsley Under 3,5 @1,8428 met +8,99 pp en "
                "Stevenage – Plymouth Argyle Under 2,5 @1,96 met +9,08 pp — allebei in de band 8–10 pp "
                "waar de lat van 10,0 op mikt. TEGELIJK IS ER EEN FULL-UNDER GEPUBLICEERD DIE ZWAKKER "
                "STAAT: AFC Wimbledon – Mansfield Town Under 2,75 @1,83 met +7,10 pp. Dat is geen fout in "
                "de code maar een gat tussen twee regels die los van elkaar zijn ingevoerd. unders.check "
                "geeft bij een edge ONDER 8,0 pp bewust passed=True terug, met als motivering dat 'edge' "
                "daar de bindende poort is (zie de code: dat houdt de reeks doelpunten_onder schoon van "
                "kandidaten die nooit een bet konden worden). Maar §5b heeft op 20 september de "
                "edge-drempel uít de poorten gehaald en tot een rangorde-afkapping gemaakt — dus onder "
                "8,0 pp houdt 'edge' niets meer tegen, en wat poort 9 aan die poort overliet, houdt "
                "niemand meer tegen. HET GEVOLG IS VANDAAG LETTERLIJK TE ZIEN: de routine publiceert een "
                "FULL-Under op +7,10 pp en blokkeert er twee op +8,99 en +9,08 pp. De rem werkt daarmee "
                "op precies de omgekeerde volgorde van wat §6g meet. EN ER IS EEN TWEEDE ROUTE EROMHEEN: "
                "bij Stevenage – Plymouth blokkeerde poort 9 de Under 2,5, waarna dezelfde mening in een "
                "naburige markt alsnog is gepubliceerd (BTTS nee @2,22, +8,39 pp). §1h houdt BTTS met "
                "opzet buiten de poort omdat de reeks daar te klein is, maar §1a zegt net zo hard dat "
                "vier tot zeven markten 'één bevinding, zeven keer uitgedrukt' zijn — een rem op één "
                "uitdrukking van die bevinding is dan geen rem. WAT DEZE RUN DAARAAN DOET: niets. Een "
                "run verandert een poort of een drempel nooit op eigen initiatief (§1e, §6g), en dit "
                "gaat over risicobereidheid. Het staat als besluitpunt in het dagrapport, één keer, met "
                "de getallen van vandaag erbij."
            ),
            "DE_LIJST_IS_EEN_RANGORDE_EN_GEEN_VONDST": (
                "ÉÉN VAN DE DRIE REGELS HAALT ZIJN EIGEN LAT: Stevenage – Plymouth Argyle BTTS nee @2,22 "
                "met +8,39 pp tegen een lat van 8,0. De andere twee staan er op rangorde (§5b): AFC "
                "Wimbledon Under 2,75 +7,10 pp (lat 8,0) en Blackpool Over 2,5 +7,61 pp (lat 16,0 op "
                "LIGHT). Van de 233 doorgerekende selecties haalde er dus precies één zijn drempel. "
                "MAX_LIGHT_IN_SHORTLIST (2) bindt niet: er staat één LIGHT-regel in de lijst van drie."
            ),
            "POORT5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
                "POORT 5 VANGT 181 VAN DE 233 SELECTIES WEG (77,7%) — 'tweede_methode', de twee methodes "
                "verslaan de markt niet dezelfde kant op. Daarna 28 op de edge, 12 op poort 8, 8 op de "
                "koersband, 2 op poort 9 en 1 op robuustheid; 1 selectie haalde alle poorten. Dat 77,7% "
                "ligt in dezelfde band als de afgelopen weken (twee derde tot vier vijfde) en voegt er "
                "geen nieuwe waarneming van betekenis aan toe; de bevinding zelf — dat één poort "
                "structureel het leeuwendeel wegvangt — staat al weken en §5 ('Net niet') noemt dat een "
                "bevinding over de splitsmethode en geen ruis. WAT HET SCHADUWLOGBOEK ERVAN ZEGT: "
                "'tweede_methode' is de grootste reeks in het logboek en staat structureel negatief, dus "
                "de poort bespaart geld."
            ),
            "POORT7": (
                "BINDT MAAR HOUDT NUL SELECTIES TEGEN, en de reden daarvoor is zelf de bevinding: VAN DE "
                "46 PLOEGEN VAN VANDAAG HEEFT ER PRECIES ÉÉN EEN UITVALLERSLIJST BIJ FOTMOB. De "
                "blessurepoot van poort 7 kan dus op 45 van de 46 ploegen niets meten, en een meting die "
                "er niet is laat de poort open (§1c). Dat is geen storing maar de dekking van deze twee "
                "divisies ruim vijftien uur voor de aftrap. MARKTWAARDE is er wel voor 41 van de 46 "
                "ploegen. DE RUSTPOOT KAN OOK NIETS: het is een volledige midweekse ronde, alle 46 "
                "ploegen staan op ongeveer drie dagen rust (congested=true), en poort 7 eist een VERSCHIL "
                "van minstens twee dagen — dat verschil is er nergens. DE STADIONCONTROLE GAF NUL "
                "ALARMEN: alle 23 duels in het eigen stadion van de genoteerde thuisploeg. GEEN ENKEL "
                "DUEL HAD EEN BEVESTIGDE OPSTELLING; alle 23 staan op lastStarting11, dezelfde "
                "klokbevinding als de afgelopen weken. De context van ÉLK van de 23 duels is opgehaald en "
                "vastgelegd — de cap (40 op dinsdag) kapte niets af — en dat is de steekproef van "
                "ctxlog.py."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met today=2026-10-20 "
                "aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. HIJ IS VANDAAG DE "
                "OP-TWEE-NA-GROOTSTE POORT: 53 van de 233 selecties staan op een underdog-kant onder de "
                "ondergrens, en bij 12 daarvan is poort 8 de EERSTE dichte poort — dat zijn de rijen die "
                "als `underdog` het schaduwlogboek ingaan. Dat is fors meer dan de nul van gisteren, en "
                "het hoort bij deze runlijst: 23 duels in twee gelijkmatige divisies leveren veel "
                "selecties op de zwakkere kant van een krappe markt. GEEN VAN DE DRIE GEPUBLICEERDE "
                "REGELS HEEFT EEN KANT (twee doelpuntenmarkten en een BTTS), dus poort 8 staat daar per "
                "definitie open. Dit is geen aanleiding om de vraag van 25 september opnieuw te stellen "
                "(§1e verbiedt dat zolang er niets wezenlijk verandert); de stand van beide reeksen staat "
                "in het runrapport onder 'Stand van het logboek'."
            ),
            "POORT9": (
                "BINDT EN HOUDT TWEE SELECTIES TEGEN — zie de aparte paragraaf hierboven, want die twee "
                "staan allebei BOVEN de gepubliceerde Under. Luton Town – Barnsley Under 3,5 (+8,99 pp) "
                "en Stevenage – Plymouth Argyle Under 2,5 (+9,08 pp) gaan als failed_gate = "
                "'doelpunten_onder' het schaduwlogboek in; de reeks groeit daarmee van 0 naar 2 "
                "afgewikkelde-in-wording gevallen sinds 12 oktober. Lees hem niet onder ~30 gevallen "
                "(§6d) — dat is eerder een vraag voor december dan voor deze week, precies zoals §1h "
                "voorspelde."
            ),
            "PINNACLE": (
                "STAP 2 VAN STAGE 5 — het scherpste publieke expertoordeel, LOS van de beste prijs waarop "
                "gespeeld wordt en nooit in my_prob (§2). Pinnacle noteerde 17 van de 23 duels, met een "
                "gemiddelde marge van 5,04% op 1X2 en 3,6–5,1% op de totalen. Op 1X2 staat het model "
                "gemiddeld 3,19 pp van Pinnacle af — dicht, en dichter dan de meeste Run B-dagen. OP DE "
                "DRIE GEPUBLICEERDE REGELS LOPEN DE OORDELEN VER UITEEN EN DAT HOORT ER PER REGEL BIJ: "
                "(1) AFC Wimbledon Under 2,75 — op precies die lijn zegt Pinnacle 52,6% en het model "
                "53,0%, een verschil van +0,36 pp. Dat is de beste overeenstemming van de hele dag en "
                "het is opmerkelijk juist op de kant waarvan §6g zegt dat ze structureel te hoog staat. "
                "(2) Stevenage – Plymouth BTTS nee — Pinnacle noteert geen BTTS, maar op de verwante "
                "O/U-lijn 2,5 zegt Pinnacle 49,1% Under en het model 58,0%: +8,88 pp, de op een na "
                "grootste afwijking van de dag op de 'weinig doelpunten'-kant. Dat is het zwaarste "
                "voorbehoud bij de enige regel die zijn lat haalt. (3) Blackpool Over 2,5 — op lijn 3,00 "
                "zegt Pinnacle 52,8% Under en het model 33,3%, dus het model staat 19,58 pp MEER aan de "
                "Over-kant dan de scherpste bookmaker. Dat is veruit de grootste afwijking van de dag, "
                "en op de kant die volgens §6g juist van de vormfout PROFITEERT. Over alle 17 "
                "(duel, lijn)-paren staat het model gemiddeld +1,31 pp boven Pinnacle op de Under-kant, "
                "10 van de 17 erboven — de bekende richting van §6g, vandaag mild."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0635 (gepoold 1,0866 over 22 speeldagen) "
                "en rust op BEIDE spelende competities — uplift_observations sloeg er NUL over, dus er is "
                "vandaag geen stil weggelaten waarneming. Beide competities staan op 11 van 46 "
                "speeldagen (24%, onder SEASON_MATURE_SHARE), dus league_level kiest voor allebei route "
                "'vorig+uplift': English League One thuis 1,572 / uit 1,225 / basis 1,393 en English "
                "League Two thuis 1,460 / uit 1,281 / basis 1,342. LEES DE FACTOR MET DE GEBRUIKELIJKE "
                "TERUGHOUDENDHEID: een pool over twee competities is een smalle pool, en de twee "
                "waarnemingen lopen bovendien uiteen (ratio lopend/vorig 1,120 in League One tegen 1,053 "
                "in League Two). De gemeten ratio van League One ligt 5,4% boven de toegepaste factor en "
                "die van League Two 1,0% eronder; dat is de spreiding die het poolen glad strijkt. Het "
                "effect is reëel maar klein — 6,3% op het competitieniveau — en het raakt alle 23 duels."
            ),
            "BEURSKOERS": (
                "GEEN VAN DE DRIE GEPUBLICEERDE REGELS STAAT OP EEN BEURS, dus de dubbele notatie van §5 "
                "is vandaag niet nodig: Stevenage BTTS nee @2,22 bij PINNACLE, AFC Wimbledon Under 2,75 "
                "@1,83 bij PINNACLE en Blackpool Over 2,5 @1,65 bij UNIBET (SE) zijn alle drie gewone "
                "bookmakers, dus de genoteerde koers IS de koers die de gebruiker krijgt. DAT TWEE VAN "
                "DE DRIE BESTE PRIJZEN BIJ PINNACLE STAAN IS ZELF EEN WAARNEMING: Pinnacle is de "
                "scherpste bookmaker met de kleinste marge (§5 Stage 5, stap 2), dus dat hij hier de "
                "beste prijs heeft betekent dat de rest van de markt die kant nog minder waard vindt, "
                "niet dat er een uitschieter is gevonden. "
                "net_price is wel over de hele lijn toegepast (oddsapi.net_price), zoals §1a eist — hij "
                "doet hier alleen niets. BEIDE spelende competities hebben een sportkey en kregen via de "
                "bulk álle zes de markten, dus er is vandaag geen enkel duel dat op het gratis "
                "BetExplorer-marktgemiddelde als enige 1X2-bron draait. Dat is de ruimste dekking die "
                "deze runlijst kan hebben."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "INZETVENSTER": (
                "Het venster is [08:00 NL 20 okt, 08:00 NL 21 okt) en runwindow.py levert 23 duels, alle "
                "23 met RunMatch.playable = True. Alle 23 komen van de daglijst van 20 oktober; er zat "
                "vandaag geen enkel duel in de nachtband [00:00, 08:00) NL van 21 oktober, want MLS en "
                "Série A — de twee competities waar prompts/run-b.md die val voor beschrijft — spelen "
                "vandaag niet. 22 duels trappen af om 20:45 NL en één om 21:00 NL (Gillingham – Port "
                "Vale). De run begon om 05:04 NL, bijna zestien uur voor de aftrap."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "ZESTIEN VAN DE ZEVENTIEN COMPETITIES ZIJN DOOR BETEXPLORER BEVESTIGD, inclusief alle "
                "vijftien die vandaag GEEN WEDSTRIJD hebben (0-0) — en juist daar moet de tweede bron "
                "kijken, want 'nul wedstrijden' is de uitkomst die een kapot id en een lege speeldag niet "
                "van elkaar onderscheidt. English League One: 11-11, eens. DE ZEVENTIENDE WIJKT AF EN DAT "
                "IS UITGEZOCHT: English League Two staat bij Fotmob op 12 duels en bij BetExplorer op 13. "
                "Het verschil is één rij — 'Northampton - Colchester, Today 20:00 UK'. DIE WEDSTRIJD KAN "
                "NIET BESTAAN: Northampton speelt vanavond om 19:45 UK tegen Tranmere en Colchester om "
                "19:45 UK bij Chesterfield, allebei op dezelfde BetExplorer-pagina en allebei door Fotmob "
                "bevestigd; één ploeg kan niet twee keer op één avond spelen. Fotmob kent de combinatie "
                "Northampton – Colchester bovendien op GEEN van beide daglijsten (20 en 21 oktober) en in "
                "GEEN enkele competitie, beker inbegrepen. Dit is dus een artefact van de "
                "BetExplorer-fixturepagina (een rij zonder eigen datumlabel die als 'Today' leest) en "
                "GEEN gemiste wedstrijd. De conclusie van de poort is daarmee: 17 van 17 competities "
                "gedekt, 23 van 23 duels bevestigd, één spookrij verworpen met reden. BetExplorer labelt "
                "in UK-tijd (NL −1 uur), dus het venster is daar [20.10. 07:00, 21.10. 07:00); dat is "
                "omgerekend en de omrekening staat in rb_oct20_bevestiging.py."
            ),
            "inkoop": (
                "20 CREDITS VAN EEN PLAFOND VAN 866 (19.078 over bij api_check.py, 922 verbruikt deze "
                "maand, 11 dagen tot de maandwissel, 2 runs per dag). Stap 0: TWEE bulk-aanroepen à 3 "
                "credits (h2h + spreads + totals = 6) voor de twee spelende competities, allebei met "
                "sportkey — English League One (24 events) en English League Two (24); "
                "split_budget(866, 2) -> (2, 2), dus niemand viel buiten de bulk en de losse "
                "totals-stap was niet nodig. Stap 2: BTTS voor 14 van de 23 duels met een kandidaat-edge, "
                "1 credit per duel = 14. De negen duels zonder BTTS zijn de zes NONE-duels plus drie "
                "zonder kandidaat-edge; die staan met die reden in markets_checked en niet als gat. "
                "MARKTBALANS-CONTROLE: GEHAALD, en zo ruim als deze runlijst kan — BEIDE inkoopbare "
                "competities kregen via de bulk álle zes de markten (1X2, AH, DNB, DC, OU, BTTS), dus "
                "twee op twee, en er is geen enkele competitie met alléén een uitkomstmarkt of alléén "
                "een doelpuntenmarkt. Dat is een wezenlijk betere uitgangspositie dan gisteren, toen vijf "
                "van de acht duels alleen een 1X2 hadden."
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
        s3 = json.load(open("tmp-run/rb_oct20_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct20_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct20_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct20_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

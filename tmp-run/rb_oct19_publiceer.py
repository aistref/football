"""Run B 16 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct19_publiceer.py`; de rekenlogica is ongewijzigd, alleen de datum en de
`parameters`-tekst verschillen. Tien van de zeventien competities speelden, met vijftien duels in
het inzetvenster en nul afgekapt (cap 55 op vrijdag). VIER gepubliceerde regels, waarvan ÉÉN zijn
eigen lat haalt.

Drie dingen die vandaag in de parameters horen:

* **Eén regel haalt de drempel, drie staan er op rangorde.** Rapid Wien - Hartberg Under 3,5 @1,90
  haalt +16,12 pp én de verzwaarde lat van poort 9 (10,0 pp). De andere drie staan onder hun lat en
  zijn er per §5b als rangorde en niet als vondst.
* **De BetExplorer-slug van Série A (BRA) is verhuisd**, en dat is dezelfde stille faalstand als
  het Serie B-id: HTTP 200 met nul rijen. Gerepareerd in `rb_oct19_bxfix.py`, zonder credits.
* **De stadioncontrole gaf één echt alarm en één vals**, en het valse is in `scripts/context.py`
  gerepareerd (`_norm_ground` liet "Stadium" tegen "Stadion" staan).

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-19"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-19T05:09:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct19_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.020, b=0.013 op 5172 "
                "afgerekende gevallen, fitted_through 2026-10-18. Die datum is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist); "
                "hij vond vanochtend 0 nieuwe waarnemingen om af te wikkelen, want de duels van vandaag "
                "moeten nog gespeeld worden. De correctie is praktisch de identiteit — het ruwe model zei "
                "gemiddeld 33,3% en het gebeurde 33,3% — en ze VERHOOGT een kans over vrijwel de hele "
                "speelbare band: +0,1 pp op 40%, +0,3 pp op 50%, +0,5 pp op 60%, +0,6 pp op 70%, en ze "
                "verlaagt alleen onder ongeveer 35%. Op de enige gepubliceerde regel telde ze dus edge BIJ "
                "in plaats van af: Degerfors – Kalmar FF +13,42 ruw -> +14,02 herijkt. Dat bindt vandaag "
                "niet, want de regel staat zowel ruw als herijkt onder zijn eigen lat van 16,0 en wordt "
                "op rangorde gepubliceerd (§5b). Lees de identiteit zoals §1e punt 3 voorschrijft: de "
                "reeks is de ONGESELECTEERDE ijksteekproef en breder dan de staart waarop deze routine "
                "speelt, dus 'de fit is de identiteit' betekent niet dat het model recht staat op die "
                "staart."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "VIJF van de zeventien competities speelden, met 8 duels in het inzetvenster — de kleinste "
                "Run B-lijst van de maand, en dat hoort bij een maandag: Keuken Kampioen Divisie (3), "
                "Romanian SuperLiga (2), Allsvenskan (1), Segunda División (1) en Série A BRA (1). TWAALF "
                "hadden GEEN WEDSTRIJD: Czech First League, Greek Super League, Eliteserien, Croatian HNL, "
                "Hungarian NB I, Serie B, 2. Bundesliga, Swiss Super League, Austrian Bundesliga, English "
                "League One, English League Two en MLS. scripts/idcheck.py gaf voor alle 33 fotmob_id's uit "
                "coverage.json een bruikbare stand (afsluitcode 0), dus geen enkele competitie is stil uit "
                "de lijst verdwenen — ook niet die twaalf die vandaag niet spelen, en dat is precies waarom "
                "die controle bestaat (prompts/run-b.md: een fout id geeft geen foutmelding maar nul "
                "wedstrijden, en nul wedstrijden leest als GEEN WEDSTRIJD). TWEE van de vijf spelende "
                "competities draaien per prompts/run-b.md op doelpunten als sterktemaat en komen dus op "
                "LIGHT met een lat van 16,0 pp uit: Romanian SuperLiga en Keuken Kampioen Divisie — Fotmob "
                "geeft daar geen xG, niet in 2025/2026 en niet in 2026/2027, per competitie nagetrokken en "
                "niet van de buurlanden overgenomen. Tiers over de 8 duels: 1 FULL (Corinthians – Vitória), "
                "7 LIGHT, 0 NONE. VIER DUELS HEBBEN EEN PLOEG ZONDER STAND IN HET VORIGE SEIZOEN en gingen "
                "langs de omrekening van §4; alle vier lukten en kwamen daarmee op LIGHT uit (nooit FULL, "
                "§4): Kalmar FF (Superettan -> Allsvenskan, gemeten factor 0.551/1.723), FC Voluntari "
                "(Liga II -> Romanian SuperLiga, 0.541/1.811) en Celta Fortuna én Tenerife (Primera "
                "Federación -> LaLiga2, 0.716/1.581). DAT LAATSTE IS HET VERMELDEN WAARD: Celta Fortuna "
                "kwam op 5 oktober nog op NONE uit omdat zijn relatieve verdediging (1.042) boven het "
                "gemeten maximum van 0.925 lag — de Coventry-val van conversion_in_range. Met tien "
                "speeldagen van dit seizoen erbij in de blend valt hij nu wél binnen het bereik. GEEN "
                "ENKELE OMREKENING LIEP LANGS DE GEPOOLDE FACTOR; in de richting omhoog staat er geen "
                "paar meer op POOLED_GAP, en de neerwaartse tak (de enige die nog poolt) is vandaag niet "
                "gebruikt. De drie duels van de Keuken Kampioen Divisie zijn alle drie een beloftenelftal "
                "tegen een gewone club (Jong Ajax, Jong FC Utrecht, Jong PSV); die staan permanent in de "
                "Eerste Divisie en zijn dus geen promovendus — promotion.find_team accepteert een afkorting "
                "alleen als voorvoegsel, precies om 'Jong Ajax' niet aan 'Ajax' te koppelen (§4)."
            ),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 19 okt, 08:00 NL 20 okt) en runwindow.py levert 8 duels, alle 8 "
                "met RunMatch.playable = True. ZEVEN trappen af tussen 17:00 en 20:30 NL; ÉÉN valt in de "
                "nachtband waar prompts/run-b.md over gaat: Corinthians – Vitória (Série A BRA) om 01:00 "
                "NL, oftewel 20:00 lokaal op zondagavond. Onder de oude UTC-dagregel was dat duel aan de "
                "run van morgen gegeven en dan al gespeeld geweest; runwindow.py geeft hem aan vandaag. "
                "Omgekeerd kwam er geen enkel duel uit de band [00:00, 08:00) NL van vandaag zelf; dat "
                "venster is door de run van gisteren bediend. De run begon om 05:06 NL, ruim elf uur voor "
                "de vroegste aftrap (17:00 NL, Universitatea Cluj – FC Argeș Pitesti)."
            ),
            "BEVESTIGING_TWEEDE_BRON": (
                "ALLE ZEVENTIEN COMPETITIES ZIJN DOOR EEN TWEEDE, ONAFHANKELIJKE BRON BEVESTIGD, en de twee "
                "bronnen zijn het over de hele runlijst exact eens: Fotmob 8 duels in het venster, "
                "BetExplorer 8, en per competitie gelijk (Keuken Kampioen Divisie 3-3, Romanian SuperLiga "
                "2-2, Allsvenskan 1-1, Segunda División 1-1, Série A 1-1). Dat geldt óók voor de TWAALF "
                "competities die vandaag GEEN WEDSTRIJD hebben, alle twaalf 0-0 — en juist daar moet de "
                "tweede bron kijken, want 'nul wedstrijden' is de uitkomst die een kapot id en een lege "
                "speeldag niet van elkaar onderscheidt. Dit is de poort uit §1 die de scheduler expliciet "
                "noemt, en ze staat vandaag op 17 van 17. BetExplorer labelt in UK-tijd (NL −1 uur), dus "
                "het venster is daar [19.10. 07:00, 20.10. 07:00); dat is omgerekend en de omrekening "
                "staat in rb_oct19_bevestiging.py."
            ),
            "DE_ENIGE_REGEL_IS_EEN_UNDER_EN_DAT_IS_DE_GEMETEN_SCHEVE_KANT": (
                "DE ENIGE GEPUBLICEERDE REGEL IS EEN UNDER, en dat is exact de markt-en-kant waarvan §6g op "
                "UITKOMSTEN heeft gemeten dat ze scheef staat. Dat hoort vooraan en niet in een voetnoot. "
                "Hij staat wél op LIGHT-data, en poort 9 (§1h) raakt met opzet alleen FULL — die poort "
                "heeft vandaag dus niets te zeggen over deze regel, en dat is een besluit van de gebruiker "
                "van 12 oktober en geen omissie. WAT ER WEL TEGEN PLEIT, en het is het zwaarste voorbehoud "
                "van deze run: tegen PINNACLE — volgens §5 (Stage 5, stap 2) het scherpste publieke "
                "expertoordeel dat er is, vandaag met een marge van 4,1% op dit duel — staat het model op "
                "de Under-kant +17,13 pp boven de markt (Pinnacle-lijn 2,25: Pinnacle 47,5% tegen eigen "
                "64,7%). Dat is de grootste afwijking van de drie duels waarvoor Pinnacle een totaal "
                "noteerde (Corinthians +13,85 pp, Celta Fortuna +3,19 pp), en alle drie staan boven "
                "Pinnacle — gemiddeld +11,39 pp op de Under-kant. DE 1X2-KANT VAN HETZELFDE DUEL WIJST "
                "DE ANDERE KANT OP: daar zit het model op 1,37 pp van Pinnacle af (eigen 30,7/31,1/38,2 "
                "tegen Pinnacle 31,5/29,7/38,8), dus het meningsverschil gaat uitsluitend over het AANTAL "
                "doelpunten en niet over wie er wint. Dat is precies de vorm die §6g beschrijft: het "
                "scoregrid zet te weinig massa op 4 en 5 doelpunten, waardoor P(Under) bij élk duel te "
                "hoog staat. WAT HET NIET IS: geen reden om de rangorde te negeren of de lijst leeg te "
                "laten — §5b schrijft de rangorde voor en §1 verbiedt zowel bets forceren als bets "
                "achterhouden buiten de poorten om. Het is wél de reden dat de regel in het dagrapport "
                "met dat voorbehoud wordt gepubliceerd."
            ),
            "POORT5_VANGT_OPNIEUW_HET_MEESTE_WEG": (
                "POORT 5 VANGT 47 VAN DE 60 SELECTIES WEG (78,3%) — 'tweede_methode', de twee methodes "
                "verslaan de markt niet dezelfde kant op. Daarna 9 op de edge, 3 op de koersband en 1 op "
                "context; NUL op robuustheid, NUL op poort 8 en NUL op poort 9. Dat 78% is het hoogste "
                "aandeel van de afgelopen weken (het schommelt al bijna drie weken tussen twee derde en "
                "vier vijfde), maar lees het vandaag met de kleine n erbij: 60 selecties over 8 duels is "
                "een zevende van een normale Run B-dag, en vijf van de acht duels hadden ALLEEN een "
                "1X2-markt, waar poort 5 het strengst is. §5 ('Net niet') zegt dat zoiets dagen achtereen "
                "een BEVINDING is over de splitsmethode en geen ruis — die bevinding staat, en vandaag "
                "voegt ze er geen nieuwe waarneming van betekenis aan toe. WAT HET SCHADUWLOGBOEK ERVAN "
                "ZEGT: 'tweede_methode' is de grootste reeks in het logboek en staat structureel negatief, "
                "dus de poort bespaart geld. DE GEPUBLICEERDE REGEL LEUNT ZWAAR OP DE ZWAKKE ARM, EN DAT "
                "IS HET TWEEDE VOORBEHOUD VAN DEZE RUN: Degerfors – Kalmar FF Under 2,5 staat op xG "
                "+8,91 pp en op de splitsmethode +31,47 pp. De twee methodes wijzen dezelfde kant op — "
                "daarom staat poort 5 open — maar ze zijn het over de GROOTTE volstrekt oneens, en §1f "
                "heeft op 392 afgerekende gevallen gemeten dat de splitsmethode als KANSBRON vrijwel "
                "niets toevoegt en alleen als veto zijn geld opbrengt. Met de weging van 80/20 (§1f) "
                "komt de gepubliceerde +14,02 pp dus grotendeels van de arm waar de xG-methode op "
                "+8,91 blijft steken. EN POORT 6 STAAT HIER KRAP OPEN: de zwakste stand van het "
                "(shrink, rho)-grid is +2,67 pp — positief, dus de poort gaat open, maar het is de "
                "smalste marge die er vandaag te vinden was en dat hoort bij de regel te staan in "
                "plaats van alleen in de tabel."
            ),
            "POORT7": (
                "BINDT EN HOUDT ÉÉN SELECTIE TEGEN: Degerfors – Kalmar FF, 1X2 op Kalmar (+2,90 pp) — de "
                "uitploeg mist meer selectiewaarde dan de thuisploeg. Die selectie zou op haar eigen edge "
                "nooit een regel zijn geworden, dus de poort kost vandaag niets in rangordetermen. WAT ER "
                "WEL IS OPGEHAALD en wat §1c eist vast te leggen: de context van ÉLK van de 8 duels — de "
                "cap (40 op maandag) kapte vandaag niets af. Dat is de steekproef van ctxlog.py. DE "
                "STADIONCONTROLE GAF NUL ALARMEN: alle 8 duels spelen in het eigen stadion van de "
                "genoteerde thuisploeg, geen enkele relocated-vlag. GEEN ENKEL DUEL HAD OM 05:10 NL EEN "
                "BEVESTIGDE OPSTELLING. Dat is dezelfde klokbevinding als de afgelopen weken en geen "
                "competitie-eigenschap: Run B draait elf tot twintig uur voor de aftrap en de opstellingen "
                "komen een uur ervoor."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met today=2026-10-19 "
                "aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. HIJ HIELD VANDAAG NUL "
                "SELECTIES TEGEN, op beide schalen: geen enkele kandidaat die alle eerdere poorten haalde "
                "stond op een underdog-kant onder de ondergrens. De reeksen groeien vandaag dus niet. Dat "
                "is geen aanleiding om de vraag van 25 september opnieuw te stellen (§1e verbiedt dat "
                "uitdrukkelijk zolang er niets wezenlijk verandert); de stand van beide reeksen staat in "
                "het runrapport onder 'Stand van het logboek'. poort8_vervallen is leeg omdat het venster "
                "van zes dagen voorbij is."
            ),
            "POORT9": (
                "POORT 9 (§1h, unders.BINDS_FROM = 2026-10-12) HOUDT VANDAAG NUL SELECTIES TEGEN. Er was "
                "maar één FULL-duel (Corinthians – Vitória) en daar sneuvelden alle Under-selecties al op "
                "poort 5, dus de poort kwam niet aan de beurt. DE GEPUBLICEERDE UNDER VALT ER MET OPZET "
                "BUITEN: Degerfors – Kalmar FF staat op LIGHT, en unders.TIERS = ('FULL',) — dat is het "
                "besluit van de gebruiker van 12 oktober ('twee hoeft nog niet op de zwakke data; eerst "
                "kijken wat deze rem doet') en §1h noemt die vrijstelling met zoveel woorden geen omissie "
                "maar deze keuze. HET IS VANDAAG WEL ZICHTBAAR WAT DIE KEUZE INHOUDT: de enige regel van "
                "de dag is precies het geval dat de poort niet toetst. De reeks `doelpunten_onder` groeit "
                "vandaag niet; lees hem niet onder ~30 afgewikkelde gevallen (§6d)."
            ),
            "NIVEAU_EN_UPLIFT": (
                "DE GEPOOLDE VROEG-SEIZOENSCORRECTIE STAAT OP 1,0111 (gepoold 1,0200 over 10 speeldagen) EN "
                "RUST OP ÉÉN COMPETITIE: alleen Segunda División (ESP) telt mee in de pool. VIER van de "
                "vijf spelende competities zijn weggelaten — dat weglaten is zélf de meting (§3 Stage 5) en "
                "hoort daarom integraal in het rapport. TWEE wegens een seizoen over de helft, waardoor "
                "league_level route 'lopend' kiest: Allsvenskan (24 van 30 speeldagen) en Série A BRA (31 "
                "van 38). TWEE wegens het ontbreken van xG in beide seizoenen: Romanian SuperLiga en "
                "Keuken Kampioen Divisie. LEES DIE FACTOR DUS MET TERUGHOUDENDHEID: een gepoolde correctie "
                "die op één waarneming rust is geen pool, en ze raakt vandaag drie van de vijf competities "
                "(Romanian SuperLiga, Segunda División en Keuken Kampioen Divisie) op route 'vorig+uplift'. "
                "Het effect is klein — 1,1% op het competitieniveau — maar het is dunner onderbouwd dan de "
                "1,0527 over vijf competities van gisteren, en dat hoort erbij te staan. DE SEIZOENSNOTATIE "
                "van Allsvenskan en Série A is '2025'/'2026' en niet '2025/2026', zoals prompts/run-b.md "
                "eist — anders valt Fotmob stil terug op het lopende seizoen en rekent de run zijn prior op "
                "de stand van vandaag. DE COMPETITIE VAN DE GEPUBLICEERDE REGEL: Allsvenskan, route "
                "'lopend' (thuis 1,618 / uit 1,314 / basis 1,474), dus daar is de uplift NIET toegepast."
            ),
            "BEURSKOERS": (
                "DE ENIGE GEPUBLICEERDE REGEL STAAT OP EEN BEURS en §5 eist dan beide getallen, want de "
                "gebruiker ziet op de site de koers vóór commissie: Degerfors – Kalmar FF Under 2,5 @1,81 "
                "BRUTO bij MATCHBOOK, 1,7938 NETTO na 2% commissie. edge_pp en selection_score rekenen met "
                "de NETTO koers (oddsapi.net_price); zonder die correctie zou de geclaimde edge ongeveer "
                "een half procentpunt hoger uitvallen. DRIE van de vijf spelende competities hebben een "
                "sportkey (Allsvenskan, Segunda División, Série A BRA); TWEE hebben er geen en draaien "
                "volledig op het gratis BetExplorer-marktgemiddelde als enige 1X2-bron: Romanian SuperLiga "
                "en Keuken Kampioen Divisie. Die twee — vijf van de acht duels — hebben dus ook geen "
                "handicap-, doelpunten- of BTTS-markt, en dat staat per duel met die reden in "
                "markets_checked. DAT IS DE BELANGRIJKSTE BEPERKING VAN DEZE DAG: op vijf van de acht "
                "duels kon alleen de uitkomstmarkt meedingen, dus de marktverdeling van de uitkomst zegt "
                "vandaag minder dan op een dag waarop alle zes de markten overal meededen."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": (
                "11 CREDITS VAN EEN PLAFOND VAN 733 (19.102 over bij api_check.py, 898 verbruikt deze "
                "maand, 13 dagen tot de maandwissel, 2 runs per dag). Stap 0: DRIE bulk-aanroepen à 3 "
                "credits (h2h + spreads + totals = 9) voor de drie spelende competities MET sportkey — "
                "Allsvenskan (9 events), Segunda División (11) en Série A BRA (16); split_budget(733, 3) "
                "-> (3, 3) dus niemand viel buiten de bulk en de losse totals-stap was niet nodig. Stap 2: "
                "BTTS voor 2 van de 3 duels met een kandidaat-edge (2 credits à 1): Degerfors – Kalmar FF "
                "en Corinthians – Vitória. HET DERDE — Jong PSV – FC Dordrecht — kreeg geen BTTS, met die "
                "reden in markets_checked: de Keuken Kampioen Divisie heeft geen sportkey bij The Odds "
                "API. MARKTBALANS-CONTROLE: GEHAALD — alle DRIE de inkoopbare competities kregen via de "
                "bulk álle zes de markten (1X2, AH, DNB, DC, OU, BTTS), dus er is geen enkele competitie "
                "met alléén een uitkomstmarkt of alléén een doelpuntenmarkt. §1a eist dat je meldt HOE "
                "RUIM die controle slaagt, en dat is hier drie op drie — maar met de kanttekening "
                "hierboven dat twee van de vijf spelende competities helemaal niet inkoopbaar zijn, en dat "
                "die twee vijf van de acht duels leveren."
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
        s3 = json.load(open("tmp-run/rb_oct19_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct19_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct19_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct19_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

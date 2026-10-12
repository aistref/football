"""Run A 12 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct11_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. Eenentwintig van de 21 competities uit de runlijst zijn nagelopen, ZEVEN speelden en er
staan NEGEN duels in het inzetvenster. DRIE gepubliceerde regels onder §5b, waarvan één zijn
drempel op beide schalen haalt (Radomiak Radom), één alleen op de herijkte (GKS Katowice, zie
KATOWICE_HAALT_DE_LAT_ALLEEN_HERIJKT) en één op rangorde onder zijn lat (Atalanta – Venezia, een
LIGHT-Under — zie EEN_LIGHT_UNDER_OP_RANGORDE). Vandaag is de eerste dag dat POORT 9 bindt (§1h, `unders.BINDS_FROM` = 12 okt); hij heeft
niets tegengehouden en de reden daarvoor staat in POORT9_BINDT_VANDAAG_VOOR_HET_EERST.
`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-12"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-12T04:40:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("A", "tmp-run/ra_oct12_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=1.029179, b=0.018887 over 4356 afgerekende gevallen, fitted_through "
                          "2026-10-11, oftewel de vorige rundag zoals §6b-5c eist. Deze run heeft "
                          "calibration.py settle vóór de analyse gedraaid (237 waarnemingen "
                          "afgewikkeld, 4563 van 4587 compleet, 24 nog open). De fit VERHOOGT een "
                          "kans over vrijwel de hele speelbare band (+0,5 pp op 50%, +0,9 pp op "
                          "70%) en verlaagt alleen onder ~35%; het ruwe model zei gemiddeld "
                          "33,333% en het gebeurde 33,333%. Dat is precies de situatie waar §5a "
                          "voor waarschuwt — 'herijkt haalt de drempel, dus ruw ook' is niet "
                          "langer automatisch waar — en vandaag bindt dat: zie "
                          "KATOWICE_HAALT_DE_LAT_ALLEEN_HERIJKT."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ZEVEN van de eenentwintig competities uit de runlijst speelden, met NEGEN duels "
                "samen in het inzetvenster: Premier League 1 (Coventry City – Newcastle United), "
                "Serie A 2, La Liga 1, Primeira Liga 1, Super Lig 1, Danish Superliga 1, "
                "Ekstraklasa 2. Veertien competities hadden GEEN WEDSTRIJD: zes competities "
                "(Bundesliga, Ligue 1, Championship, Eredivisie, Belgian Pro League, Scottish "
                "Premiership — allemaal met hun eerstvolgende ronde op 14 of 16 oktober), de drie "
                "Europese toernooien (UCL 14 okt, UEL en UECL 15 okt) en de vijf bekers. Een "
                "maandag na een volle zondagse speelronde is de kleinste dag van de week voor "
                "deze runlijst; dat is geen storing (§3 Stage 2)."),
            "DE_CAP_BINDT_NIET": (
                "Negen duels op een maandagcap van 40, dus er is NIETS afgekapt (afgekapt = 0) en "
                "de hele runlijst is doorgerekend. Stille truncatie is verboden (§3 Stage 4) en "
                "het omgekeerde hoort er net zo expliciet te staan. De datarijkdom liep van 4,5 "
                "(Eyüpspor – Göztepe en Radomiak Radom – Motor Lublin, beide zonder "
                "opstellingsblok) tot 7,0 (AGF – Sønderjyske). Omdat niets afviel zijn "
                "`laagste_die_het_haalde` en `hoogste_die_afviel` leeg — er is geen grens om te "
                "noemen."),
            "DRIE_OMREKENINGEN": (
                "Drie van de negen duels hebben een ploeg die niet in de stand van 2025/2026 "
                "staat, en alle drie zijn via de §4-route 'Promovendi: eerst omrekenen, dan pas "
                "NONE' doorgerekend op data_tier LIGHT (een omgerekende ploeg is nooit FULL): "
                "COVENTRY CITY (Championship (ENG) 2025/2026, omgerekend met de gemeten factor "
                "x0.541/1.783 van het paar E0/E1 bij football-data.co.uk), VENEZIA (Serie B "
                "(ITA), x0.601/1.528 voor I1/I2) en WIECZYSTA KRAKÓW (I Liga (POL), x0.680/1.743 "
                "— een EIGEN meting uit promotion.MEASURED_TIER2_GAP van 31 aug 2026 en geen "
                "gepoolde factor). Alle drie vielen binnen conversion_in_range, dus geen enkele "
                "kwam op NONE uit: de Coventry-val heeft vandaag niets tegengehouden. TWEE van de drie "
                "leveren een gepubliceerde regel op, en dat is voor deze runlijst ongebruikelijk: "
                "bij GKS KATOWICE – WIECZYSTA KRAKÓW is de bet de thuisploeg (de NIET omgerekende "
                "kant) en bij ATALANTA – VENEZIA een Over/Under, dus geen van beide speelt de "
                "omgerekende ploeg zelf. Dat is geen geluk maar de LIGHT-lat van 16,0 pp: een "
                "omgerekende ploeg is nooit FULL, en op die lat komt een kant-selectie vrijwel "
                "nooit door. §4 eist dat de "
                "stand per selectie uit GapResult.direction wordt gelezen in plaats van uit een "
                "samenvattende zin, en die drie teksten staan integraal in `promovendi` per "
                "wedstrijd."),
            "POORT9_BINDT_VANDAAG_VOOR_HET_EERST": (
                "Poort 9 (§1h, besluit van de gebruiker van 11 okt 2026) heeft vandaag zijn "
                "eerste bindende dag: `unders.BINDS_FROM` = 2026-10-12. Een Over/Under op de "
                "UNDER-kant met data_tier FULL moet 10,0 pp halen in plaats van 8,0. Hij is voor "
                "elke selectie aangeroepen met today=2026-10-12, zoals §1h eist, zodat een "
                "herberekening van 11 oktober de poort van die dag krijgt en niet die van "
                "vandaag. HIJ HEEFT VANDAAG NIETS TEGENGEHOUDEN, en dat is een feit en geen "
                "vrijspraak: er staan 24 Under-selecties in de run, maar geen enkele FULL-Under "
                "komt in de band 8–10 pp waar de poort bindt — de twintig FULL-Unders staan "
                "allemaal NEGATIEF (−1,54 tot −8,01 pp) en de vier Unders boven de 8 pp "
                "(Atalanta – Venezia, +8,52 tot +11,24 pp) zijn LIGHT, waar de poort met opzet "
                "niet geldt en de lat 16,0 is. `poort9_geblokkeerd` is dus voor alle negen duels "
                "leeg en de reeks `doelpunten_onder` in shadow.jsonl begint vandaag op nul. "
                "scripts/shadow.py is deze run uitgebreid zodat die reeks straks wél gevuld "
                "wordt (zie SHADOW_KENT_POORT9_SINDS_VANDAAG)."),
            "SHADOW_KENT_POORT9_SINDS_VANDAAG": (
                "§1h eist dat elke door poort 9 tegengehouden kandidaat met failed_gate = "
                "'doelpunten_onder' in data/shadow.jsonl belandt en daar wordt afgerekend. Dat "
                "kon niet: shadow.py cmd_collect las alleen near_miss, poort8_geblokkeerd, "
                "poort8_ruw en zonder_herijking. Een near_miss alleen is te weinig — die wordt "
                "niet weggeschreven als de wedstrijd daarna alsnog een andere bet oplevert, en "
                "dan zou juist de kandidaat die deze poort kostte nooit worden afgerekend. "
                "Daarom twee wijzigingen deze run: het analysescript schrijft een eigen blok "
                "`poort9_geblokkeerd` (één rij per wedstrijd, de selectie met de hoogste "
                "selection_score, de rest als aantal in ook_geblokkeerd — zelfde constructie als "
                "poort 8), en shadow.py leest dat blok met suffix -p9- en slaat een near_miss "
                "over die dezelfde markt en koers beschrijft. Dat laatste is dezelfde "
                "dubbeltellingsfout die op 3 okt bij `underdog` vier keer op één dag optrad."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e, teruggezet per 1 okt "
                       "2026); sides.check() is met today=2026-10-12 aangeroepen zoals §1e eist. "
                       "Vandaag houdt hij ZES selecties tegen over TWEE wedstrijden, die elk één "
                       "rij in poort8_geblokkeerd krijgen. Eén van die twee is geen formaliteit: "
                       "bij ATALANTA – VENEZIA stond Venezia +1.5 @1.70 op +18,39 pp herijkt, "
                       "boven de LIGHT-lat van 16,0 — dat is dus een selectie die zonder poort 8 "
                       "een gepubliceerde bet was geweest, op een kant waar de markt Venezia "
                       "16,4% geeft tegen 62,3% voor Atalanta. Dat duel is daarna alsnog in "
                       "de lijst gekomen met een Over/Under (Under 3.5), dus de poort "
                       "heeft hier geen wedstrijd maar een KANT tegengehouden — precies "
                       "wat hij hoort te doen. De andere (Coventry City +0.25 "
                       "@2.00, +4,35 pp, markt 29,9%) haalde de lat sowieso niet. Die twee rijen "
                       "gaan als `underdog` het schaduwlogboek in; de reeks staat vóór vandaag op "
                       "40 afgewikkelde gevallen met +11,0% en blijft volgens §1e een reden om de "
                       "vraag te stellen en geen automatisme om de poort te schrappen — de "
                       "kalibratiefout die de rem afdekt is er nog (zie `calibration.py stats` in "
                       "het runrapport)."),
            "POORT7": ("Voor alle negen duels gedraaid en in `context` vastgelegd, ook waar hij "
                       "opengaat (§1c). Hij houdt ACHT selecties tegen en is bij DRIE duels de "
                       "bindende poort: LEVANTE – SEVILLA (Levante mist 39% van de "
                       "selectiewaarde tegen 19% bij Sevilla — Etta Eyong 'Doubtful', Hugo Sotelo "
                       "terug eind oktober; de thuiszege @2.87 stond op +12,27 pp en is daarmee "
                       "de grootste geclaimde edge die vandaag is tegengehouden), AGF – "
                       "SØNDERJYSKE (AGF mist 15% tegen 0%, drie uitvallers) en TORINO – UDINESE "
                       "(de uitkant). Bij de overige zes duels staat de poort aan beide kanten "
                       "open. Bij `side = None` — Over/Under en BTTS — staat hij altijd open; dat "
                       "is geen meting maar de regel van §1c, want er is geen kant om te "
                       "benadelen."),
            "POORT5_IS_OPNIEUW_DE_GROOTSTE_ZEEF": (
                "103 van de 141 doorgerekende selecties (73,0%) sneuvelen op poort 5 — de twee "
                "methodes verslaan de markt niet dezelfde kant op. Dat is de ZESDE dag op rij "
                "boven tweederde (Run A 11 okt: 417 van 550, 75,8%) en het is daarmee geen "
                "dageffect meer. Zie de bevinding in het runrapport: het aandeel is zo stabiel "
                "dat het eerder iets over de twee schatters zegt dan over de wedstrijden van een "
                "dag. De overige poorten: edge 16, context 8, underdog 6, odds 3, robuustheid 2, "
                "en DRIE selecties met alle poorten open."),
            "VROEG_SEIZOENSCORRECTIE_SCHIET_OPNIEUW_DOOR": (
                "factor x1.0665 (gepoold 1.0762 over 55 speeldagen in alle zeven spelende "
                "competities; `uplift_observations` sloeg er nul over, want alle zeven hebben xG "
                "in beide seizoenen en geen enkele is op of boven de helft van zijn speeldagen). "
                "De controlemeting die §3 Stage 5 eist wijst de verkeerde kant op, voor de tweede "
                "dag op rij en forser: P(Over 2.5) tegen de de-vigde marktkans staat op +3,83 pp "
                "ZONDER de correctie en op +8,02 pp MET (gemiddelde absolute fout 5,14 → 8,02 pp) "
                "over de zes duels met een 2.5-lijn aan beide kanten. Run A mat gisteren −2,06 → "
                "+3,03 pp. LET OP WAT DIT NIET MAG WORDEN: dit is een vergelijking met de MARKT "
                "en dus een diagnose, nooit een knop om de correctie op af te regelen (§2, §6e). "
                "Het hoort als openstaand punt in het runrapport en niet als wijziging in deze "
                "run."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 12 okt, 08:00 NL 13 okt). Alle negen duels komen van de "
                "daglijst van 2026-10-12 (source_day = DAY, geen enkele DAY+1) en alle negen "
                "staan op RunMatch.playable = True: de vroegste aftrap is Radomiak Radom – Motor "
                "Lublin om 18:00 NL en de run begon om 04:17 NL. De nachtband waarvoor "
                "runwindow.py op 24 september is gebouwd is vandaag leeg; deze runlijst heeft "
                "geen competitie in een Amerikaanse tijdzone. De aftraptijden zijn met twee "
                "bronnen bevestigd — Fotmob in UTC en BetExplorer in UK-tijd, dus NL −1 uur — en "
                "komen op hetzelfde NL-tijdstip uit."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1 eist bevestiging door een tweede methode, en dat geldt ook voor de vraag "
                "wélke wedstrijden er zijn. PER COMPETITIE EENS, niet alleen op het totaal: voor "
                "alle vijftien competities met een BetExplorer-slug geeft de fixturepagina exact "
                "hetzelfde aantal duels in het venster als de Fotmob-daglijst (9 tegen 9), "
                "inclusief de nullen bij de zes competities die vandaag niet spelen en bij de "
                "drie Europese toernooien. De zeven bulk-responsen van The Odds API dekken "
                "dezelfde zeven spelende competities. VALKUIL die deze run is tegengekomen en "
                "hier hoort te staan: BetExplorer labelt een duel van de pagina-datum als "
                "'Today HH:MM' en niet als '12.10. HH:MM'. Een filter dat alleen op de "
                "datumprefix kijkt vindt nul duels van vandaag en ziet eruit als een bron die het "
                "oneens is — de eerste meting van deze run gaf zo zeven valse afwijkingen."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "Geen van de vijf bekers op de Run A-runlijst heeft een fotmob_id in "
                "coverage.json, dus runwindow.matches_for_run kan ze niet filteren en 'niet in de "
                "daglijst' is voor hen geen uitspraak — dat is het gat dat Run A op 6 oktober "
                "trof. Alle vijf zijn daarom apart langs BetExplorer gegaan "
                "(tmp-run/ra_oct12_cups.py) en alle vijf hebben hun eerstvolgende ronde NA het "
                "inzetvenster: FA Cup 17 okt (32 teamparen, nog geen koersen), League Cup 27 okt "
                "(8 duels mét 24 koersen), KNVB Beker 27 okt (26 teamparen), DFB Pokal 27 okt (16 "
                "duels mét 48 koersen), Coppa Italia 1 dec (8 teamparen). Vijf keer GEEN "
                "WEDSTRIJD met een tweede bron eronder in plaats van met een stilte."),
            "ALLE_ZEVEN_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Anders dan gisteren draait vandaag GEEN enkel duel op het gratis "
                "BetExplorer-marktgemiddelde alleen: alle zeven spelende competities hebben een "
                "sportkey bij The Odds API en kregen de bulk-aanroep (h2h + spreads + totals, 3 "
                "credits elk). Vijf van de zes markten liggen dus bij elk duel op de BESTE PRIJS, "
                "en die lag vandaag gemiddeld 6,34% boven het marktgemiddelde van BetExplorer "
                "(4,90% tot 8,71% over de negen duels) — in edge is dat de orde van +1,8 pp per "
                "selectie, gratis (§1a). Elke koers is door oddsapi.net_price gehaald, dus "
                "beurzen staan er na 2% commissie in."),
            "MARKTBALANS": (
                "De controle van §1a is een controle op de INKOOP en hij slaagt ruim: alle zeven "
                "competities hebben zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een "
                "doelpuntenmarkt (Over/Under) — zeven op zeven, niet één op twaalf zoals op "
                "30 augustus. BTTS is er voor ZEVEN van de negen duels bij gekocht (2 credits "
                "per duel, §1a stap 2, op de vereniging van beide schalen van `kandidaat_edge`); "
                "de twee die hem niet kregen (Coventry City – Newcastle United, Famalicão – "
                "Alverca) staan in markets_checked met 'niet opgevraagd — geen kandidaat-edge in "
                "dit duel' en niet als gat. De 141 doorgerekende selecties verdelen zich over "
                "Over/Under 48, Asian Handicap 34, 1X2 27, BTTS 14, Draw No Bet 12 en Double "
                "Chance 6; de drie gepubliceerde regels zijn twee 1X2 en één Over/Under."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stap 2 van §3 Stage 5, in de enige vorm die bereikbaar is: de de-vigde 1X2 van "
                "PINNACLE apart gezet, LOS van de beste prijs waarop gespeeld wordt. Gevonden "
                "voor alle negen duels (84 events in de zeven responsen), gemiddelde marge 3,92% "
                "— scherper dan de 6 tot 10% van de rest van de markt. Het eigen xG-1X2 staat "
                "gemiddeld 5,56 procentpunt van dat oordeel af. Twee uitschieters, allebei bij "
                "een omgerekende promovendus: ATALANTA – VENEZIA (−18,66 pp op de thuiszege; "
                "Pinnacle 62,6%, eigen model 43,9%) en GKS KATOWICE – WIECZYSTA KRAKÓW (+14,84 "
                "pp; Pinnacle 46,0%, eigen model 60,9%). Bij de gepubliceerde bet staat het model "
                "+6,30 pp boven Pinnacle op de thuiszege van Radomiak — het model is daar dus "
                "optimistischer dan de scherpste bookmaker, en dat hoort er eerlijk bij. DIT "
                "GETAL ZIT NIET IN my_prob EN NIET IN prob_sources (§2, §4): het is andermans "
                "lezing en marktafgeleid, dus het hoort in de vergelijking en niet in de "
                "kansschatting."),
            "KATOWICE_HAALT_DE_LAT_ALLEEN_HERIJKT": (
                "De eerste gepubliceerde regel van vandaag is de scherpste illustratie van §5a "
                "die deze maand voorbijkwam. GKS KATOWICE – WIECZYSTA KRAKÓW, 1X2 thuiszege "
                "@2.12 (Coolbet), data_tier LIGHT: +16,12 pp HERIJKT en +15,34 pp RUW, tegen een "
                "LIGHT-lat van 16,0. Hij haalt die lat dus ALLEEN op de herijkte schaal; "
                "`bet_beide` staat op FALSE en dat staat ook in `notes` van de pick. §1 en §5a "
                "laten publicatie afhangen van alle poorten op de HERIJKTE my_prob en die staan "
                "alle zeven open, dus dit is geregeld gedrag — dezelfde situatie als de vijfde "
                "regel van Run A op 11 oktober. Maar het is wél het geval waarvoor de vlag op "
                "6 september is neergezet in plaats van de redenering 'de herijking verlaagt een "
                "kans toch altijd': sinds de fit op 20 september uit de ongeselecteerde "
                "ijksteekproef komt VERHOOGT hij juist, hier met 0,78 procentpunt, en dat is "
                "precies het verschil met de lat. DE SAMENVATTINGSREGEL VAN toplist.py ZEI DAT NIET — "
                "die schreef onvoorwaardelijk 'Gepubliceerd: 3 bet(s) — die haalden beide "
                "modellen', terwijl twee van de drie regels van vandaag dat niet doen. Die "
                "regel klopte vóór §5b en is sindsdien niet meegegroeid; hij is deze run "
                "gerepareerd en noemt nu hoeveel van de gepubliceerde regels ook de ruwe lat "
                "halen (vandaag 1 van de 3). Het statuslabel per regel ('haalt ook de lat van "
                "16.0 pp') blijft staan en is correct: dat meet op de schaal waarop die lijst "
                "staat, de herijkte. De tweede selectie van dezelfde wedstrijd, Asian "
                "Handicap GKS Katowice −1 @3.03, staat op +16,15 pp herijkt en +15,71 pp ruw en "
                "kreeg failed_gate 'herijking_omgekeerd' — eigen label, nooit opgeteld bij "
                "`herijking`, want dat is de spiegel ervan (§1e)."),
            "EEN_LIGHT_UNDER_OP_RANGORDE": (
                "De derde regel is ATALANTA – VENEZIA, Over/Under Under 3.5 @1.6958 "
                "(Matchbook-beurskoers 1.71 bruto, 1.6958 na 2% commissie), data_tier LIGHT, "
                "+11,24 pp herijkt tegen een LIGHT-lat van 16,0. Hij is dus GEPUBLICEERD OP "
                "RANGORDE en niet omdat hij een lat haalt (§5b: staan er minder selecties boven "
                "de drempel dan er regels in de lijst passen, dan bepaalt de rangorde de lijst en "
                "is de drempel een label). Dat hoort hardop gezegd, want het is op dezelfde dag "
                "dat poort 9 ingaat de énige Under in de lijst: poort 9 dekt LIGHT met opzet NIET "
                "(§1h punt 1 — tien afgewikkelde LIGHT-Unders, samen +60,6%, te weinig om iets te "
                "zeggen en het wijst de andere kant op), dus deze regel is door geen enkele poort "
                "tegengehouden en dat is regelconform. Maar §6g meet wél dat de Under-kant over "
                "het hele logboek op −16,5% staat (76 picks) tegen +10,6% voor de Over-kant, en "
                "de vormfout in het scoregrid die daaronder ligt is niet gerepareerd — die raakt "
                "LIGHT net zo goed als FULL. OF POORT 9 OOK OP LIGHT MOET GELDEN IS EEN BESLUIT "
                "VAN DE GEBRUIKER (risicobereidheid, niet data — dezelfde redenering als bij "
                "selection_score en bij poort 8) en het staat als zodanig in het dagrapport. Een "
                "run verandert deze poort nooit op eigen initiatief."),
            "VERPLAATSTE_WEDSTRIJDEN": (
                "context.check_venue is voor alle negen duels gedraaid en zet NUL keer relocated: "
                "elk duel staat in het eigen stadion van de genoteerde thuisploeg. §1c eist dat "
                "dit ook bij een open poort wordt vastgelegd en genoemd, want thuisvoordeel is de "
                "aanname waar het model het zwaarst op leunt."),
            "OPSTELLINGEN": (
                "Zes van de negen duels hebben een VOORSPELDE opstelling, één de laatste "
                "basiself (GKS Katowice – Wieczysta Kraków) en twee geen opstellingsblok "
                "(Eyüpspor – Göztepe, Radomiak Radom – Motor Lublin) — dat laatste is ook de "
                "reden dat die twee de laagste datarijkdom van de run hebben (4,5). Bij een "
                "ontbrekend blok laat poort 7 door: een meting die er niet is, is geen bewijs van "
                "een probleem (§1c). De gepubliceerde bet is één van die twee, dus bij Radomiak "
                "Radom – Motor Lublin is de context NIET meetbaar en staat dat ook zo in het "
                "dagrapport in plaats van als 'iedereen fit'."),
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
        s3 = json.load(open("tmp-run/ra_oct12_stage3.json"))
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
        for run, pad in (("A", "tmp-run/ra_oct12_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct12_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct12_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

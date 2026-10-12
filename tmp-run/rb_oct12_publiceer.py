"""Run B 12 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct11_publiceer.py`; alleen de datum en de `parameters`-tekst van
vandaag verschillen. Dertien duels in het inzetvenster over zes van de zeventien
competities, nul afgekapt (cap 40), en drie gepubliceerde regels — waarvan twee op
RANGORDE en één die haar lat alleen op de herijkte schaal haalt. Poort 9 (§1h) bindt
vandaag voor het eerst en heeft niets tegengehouden; waarom dat zo is staat in
BEVINDING_1. `mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-12"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-12T05:25:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct12_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.029, b=0.019 op 4356 "
                "afgerekende gevallen, fitted_through 2026-10-11. Die datum is de vorige rundag, dus "
                "calibration.py settle is niet blijven liggen (de controle die §6b-5c sinds 30 sep eist). De "
                "correctie is praktisch de identiteit — het ruwe model zei gemiddeld 33,3% en het gebeurde "
                "33,3% — maar ze wijst dezelfde kant op als gisteren: deze fit VERHOOGT een kans boven "
                "ongeveer 35%, met +0,2 pp op 40%, +0,5 pp op 50% en +0,9 pp op 70%. Op de drie gepubliceerde "
                "regels telde ze dus edge BIJ in plaats van af: 15,50 -> 16,43 (Real Oviedo), 13,15 -> 13,89 "
                "(Malmö FF) en 6,34 -> 6,99 (Burgos CF). EN VANDAAG BINDT DAT ECHT, bij de kop van de lijst: "
                "Real Oviedo – Eibar Under 2,5 haalt de LIGHT-lat van 16,0 pp alleen op de HERIJKTE schaal "
                "(16,43) en niet op de ruwe (15,50), dus bet_beide staat op False. Dat is precies het geval "
                "waarvoor §5a die vlag heeft gebouwd in plaats van op de redenering 'herijkt haalt de "
                "drempel, dus ruw ook' te vertrouwen — die redenering is sinds 20 sep niet langer waar. De "
                "regel is daarom gepubliceerd op RANGORDE met dat label erbij en niet als gevonden voordeel "
                "(§5b), en ze staat óók als near_miss met failed_gate = herijking_omgekeerd in het run-state. "
                "Lees de identiteit zoals §1e punt 3 van 30 sep voorschrijft: de reeks is de ONGESELECTEERDE "
                "ijksteekproef en breder dan de staart waarop deze routine speelt, dus 'de fit is de "
                "identiteit' betekent niet dat het model recht staat op die staart — §6e meet daar nog +1,80 "
                "pp te veel kans op longshots en -3,53 pp te weinig op favorieten over 4614 uitkomsten."
            ),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ZES van de zeventien competities speelden, met 13 duels in het inzetvenster. ELF hadden GEEN "
                "WEDSTRIJD: Czech First League, Croatian HNL, Hungarian NB I, Serie B, 2. Bundesliga, Swiss "
                "Super League, Austrian Bundesliga, Keuken Kampioen Divisie, English League One, English "
                "League Two en MLS. Dat is een maandag na een volle zondagronde en dus geen storing en geen "
                "dekkingsgat. scripts/idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare "
                "stand (afsluitcode 0), dus geen enkele competitie is stil uit de lijst verdwenen — ook niet "
                "de elf die vandaag niet spelen, en dat is precies waarom die controle bestaat "
                "(prompts/run-b.md: een fout id geeft geen foutmelding maar nul wedstrijden, en nul "
                "wedstrijden leest als GEEN WEDSTRIJD). EEN van de zes spelende competities draait per "
                "prompts/run-b.md op doelpunten als sterktemaat en komt dus op LIGHT met een lat van 16,0 pp "
                "uit: Romanian SuperLiga. De andere vier van dat rijtje (Czech First League, Croatian HNL, "
                "Hungarian NB I, Keuken Kampioen Divisie) speelden niet. Tiers over de 13 duels: 5 FULL, 4 "
                "LIGHT, 4 NONE."
            ),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 12 okt, 08:00 NL 13 okt). TWAALF van de dertien duels stonden op de "
                "daglijst van 2026-10-12 zelf; EEN kwam van de daglijst van 2026-10-13 (source_day = DAY + "
                "1): RB Bragantino – Cruzeiro, aftrap 00:00 UTC op 13 okt, oftewel 02:00 NL. Chapecoense – "
                "Athletico Paranaense zit in dezelfde band (22:30 UTC op 12 okt = 00:30 NL op 13 okt) maar "
                "stond nog op de daglijst van vandaag. Dat zijn exact de twee duels waar runwindow.py voor is "
                "gemaakt: onder de oude UTC-dagregel was Bragantino – Cruzeiro aan de run van MORGEN "
                "toegewezen en dan was hij om 05:25 NL al gespeeld. Alle dertien duels hebben "
                "RunMatch.playable = True; de vroegste aftrap is 14:00 NL (Real Valladolid – Albacete) en de "
                "run begon om 05:06 NL, ruim acht uur daarvoor."
            ),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met today=2026-10-12 "
                "aangeroepen zoals §1e eist, zodat het vervallen venster van 25 t/m 30 september uit "
                "sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen en niet geraden. Hij hield 12 selecties tegen, "
                "verdeeld over 4 wedstrijden (KFUM – Vålerenga, Malmö FF – Kalmar FF, Elfsborg – Halmstads "
                "BK, Real Oviedo – Eibar). EN HIJ KOST VANDAAG PLEK 2 VAN DE RUWE LIJST: KFUM – Vålerenga, "
                "Asian Handicap KFUM +0.25 @1,8526 (+7,97 pp ruw, selection_score 4,937) staat daar op 2 met "
                "underdog als bindende poort. Op de herijkte schaal zou die score tussen Malmö (4,215) en "
                "Burgos (3,984) zijn gevallen, dus de poort kost vandaag niet de kop van de lijst maar wel "
                "een plek erin. WAT ER TEGENOVER STAAT, en daarom blijft de poort staan: de "
                "`underdog`-schaduwreeks staat nu op 89 afgewikkelde kandidaten met +0,2% rendement (49,4% "
                "trefkans) — vlak, en daarmee is de uitweg van 25 september ('positieve ROI over >= 30 "
                "afgewikkelde kandidaten') niet meer de duidelijke ja die hij op 5 oktober was. De reeks liep "
                "van +16,9% over 36 (5 okt) via -8,7% over 79 (11 okt) naar +0,2% over 89 vandaag; dat heen "
                "en weer over tien dagen is zelf het bewijs dat deze reeks nog te klein is om er een poort op "
                "te verzetten (§6d). §1e verbiedt bovendien de vraag dagelijks opnieuw te stellen, en er is "
                "niets wezenlijk veranderd. De gemeten kalibratiefout die de rem verantwoordt staat er nog: "
                "+1,80 pp te veel kans op longshots en -3,53 pp te weinig op favorieten over 4614 uitkomsten. "
                "`underdog_ruw` staat onveranderd op 17 gevallen met -8,8%; poort8_ruw is leeg omdat alle 12 "
                "al op de herijkte schaal sneuvelden en §1e verbiedt dezelfde selectie twee keer te boeken, "
                "en poort8_vervallen is leeg omdat het venster van zes dagen voorbij is. Die twee reeksen "
                "blijven twee populaties en worden nooit opgeteld."
            ),
            "POORT9": (
                "BINDT VANDAAG VOOR HET EERST (unders.BINDS_FROM = 2026-10-12, §1h) EN HEEFT NIETS "
                "TEGENGEHOUDEN — nul selecties, nul wedstrijden. Dat is geen storing en het is ook geen "
                "toeval, en het is het vermelden waard omdat de lijst van vandaag juist door twee Unders "
                "wordt aangevoerd. De reden staat in §1h punt 1: de poort raakt ALLEEN de Under-kant op FULL. "
                "De zestien Under-selecties van vandaag vallen in twee groepen. Op FULL kwam de hoogste Under "
                "op +7,12 pp (RB Bragantino – Cruzeiro, Under 2.5 @2,1956) en daarmee onder de GEWONE drempel "
                "van 8,0 — dus `edge` is daar de bindende poort en unders.check geeft zelf passed = True "
                "terug, precies zoals de poortvolgorde in het analysescript beschrijft. En de twee Unders die "
                "wél zijn gepubliceerd — Real Oviedo – Eibar Under 2,5 (+16,43 pp) en Malmö FF – Kalmar FF "
                "Under 2,5 (+13,89 pp) — staan beide op LIGHT, waar §1h de lat uitdrukkelijk op 16,0 laat "
                "staan omdat de scheefstand daar niet is gemeten (tien afgewikkelde LIGHT-Unders, samen "
                "+60,6%, en die wijzen de andere kant op). Dit is dus letterlijk het geval dat §1h als "
                "voorbeeld noemt met Lillestrøm – Molde van 11 oktober: een LIGHT-Under die de poort NIET "
                "tegenhoudt. Wie deze poort over een paar weken herziet, heeft hier de eerste waarneming: op "
                "de dag dat hij ingaat bindt hij niet, terwijl tweederde van de gepubliceerde lijst een Under "
                "is. De reeks `doelpunten_onder` in data/shadow.jsonl staat daarmee nog op nul rijen; lees "
                "hem niet voor ~30 afgewikkelde gevallen (§6d)."
            ),
            "BEVINDING_1_DRIE_REGELS_OP_DE_SCHEEFSTE_ARM": (
                "ALLE DRIE DE GEPUBLICEERDE REGELS LEUNEN OP DE SPLITSMETHODE, EN DAT IS DE SCHEEFSTE VAN DE "
                "TWEE. Per regel de twee armen apart: Real Oviedo – Eibar Under 2,5 — xG +10,34 pp, splits "
                "+36,13 pp; Malmö FF – Kalmar FF Under 2,5 — xG +8,79 pp, splits +30,61 pp; Burgos CF – "
                "Granada 'beide ploegen scoren — nee' — xG +2,51 pp, splits +21,66 pp. De gewogen kans weegt "
                "de splits voor een vijfde (§1f, XG_WEIGHT 0.80), dus die enorme splitsedges tillen alle drie "
                "de regels een paar procentpunt op; bij Burgos is het verschil tussen publiceren en niet "
                "publiceren. WAAROM DAT TELT: §1f heeft op 392 afgerekende gevallen gemeten dat de "
                "splitsmethode als kansbron vrijwel niets toevoegt (Brier .23674 voor alleen xG tegen .23625 "
                "voor de mix) en dat haar rol het VETO van poort 5 is, niet het meerekenen. §6e wijst haar "
                "sinds 22 augustus aan als de scheefste arm, en calibration.py stats van vandaag laat zien "
                "dat dat nog zo is, zij het in de andere richting dan je zou denken: op longshots wijkt de "
                "xG-methode +2,18 pp af en de splitsmethode +1,43 pp, op favorieten -4,15 tegen -2,88 pp. WAT "
                "DIT NIET IS: geen reden om de weging vandaag te veranderen (§6d verbiedt dat op één dag, en "
                "§1f noemt de curve tussen 0,7 en 1,0 vlak). Wat het wél is: een aantekening bij drie regels "
                "die alle drie op rangorde of op een herijkte schaal staan, en die daarmee zwakker onderbouwd "
                "zijn dan hun edge-getal suggereert. Bij alle drie staat de xG-arm ver onder de splitsarm, en "
                "bij Burgos CF – Granada haalt de xG-arm met +2,51 pp niet eens een derde van de drempel."
            ),
            "BEVINDING_2_POORT_5_ZEVENDE_DAG_DRIEKWART": (
                "POORT 5 VANGT VOOR DE ZEVENDE DAG OP RIJ ONGEVEER DRIEKWART WEG: 79 van de 115 selecties "
                "(68,7%) sneuvelden op 'tweede_methode' — de twee methodes verslaan de markt niet dezelfde "
                "kant op. Daarna 18 op de edge, 12 op de underdog-poort, 3 op de koersband, 2 op robuustheid, "
                "0 op context en 0 op poort 9; één selectie haalde alle negen poorten (Real Oviedo – Eibar, "
                "Under 2,5). De reeks: 40 van 60 (7 okt), 29 van 37 (8 okt), 84 van 110 (9 okt), 553 van 754 "
                "(Run A 10 okt), 538 van 703 (Run B 10 okt), 341 van 447 (11 okt) en nu 79 van 115. Dat is "
                "zeven dagen rond twee derde tot driekwart over ruim 2200 selecties, en §5 ('Net niet') zegt "
                "dat zoiets dagen achtereen een BEVINDING is over de splitsmethode en geen ruis — zie "
                "BEVINDING_1, waar dezelfde methode vandaag de kop van de lijst draagt. Dat is de spanning "
                "die deze twee bevindingen samen beschrijven: dezelfde arm die driekwart van alles wegvangt, "
                "is de arm waarop de drie regels van vandaag rusten. WAT HET SCHADUWLOGBOEK ERVAN ZEGT: "
                "'tweede_methode' staat op 128 afgewikkelde kandidaten met -4,9% rendement (43,8% trefkans) — "
                "de poort bespaart dus geld, net als gisteren (-5,2% over 128). NIET VANDAAG EEN DREMPEL "
                "VERZETTEN (§6d: niet op één dag, en zeker niet op zeven)."
            ),
            "BEVINDING_3_VIER_KEER_NONE_DRIE_SOORTEN_LACUNE": (
                "VIER VAN DE DERTIEN DUELS KOMEN OP data_tier = NONE UIT, en het zijn drie verschillende "
                "soorten lacune — geen bronprobleem. (1) PAOK Thessaloniki – Kalamata: Kalamata is "
                "promovendus en staat niet in de stand van Super League 2 (GRE) 2025/2026, dus de omrekening "
                "heeft geen vertrekpunt. De Griekse factor is op 11 oktober wél gemeten en staat in "
                "promotion, maar een gemeten factor helpt niet als de BRONDIVISIE de ploeg niet kent. (2) "
                "Coritiba – Botafogo en Chapecoense – Athletico Paranaense: 'geen divisie boven of onder "
                "Série A (BRA) bekend'. Dat is bekend en vastgelegd — prompts/run-b.md zegt het met zoveel "
                "woorden: onder de Série A ligt de Série B, maar er is geen gemeten factor voor dat "
                "divisiepaar, dus een Braziliaanse promovendus komt op NONE uit. Drie van de vier "
                "Braziliaanse ploegen van vandaag zijn promovendus (Coritiba, Chapecoense, Athletico "
                "Paranaense), en daarmee kost deze ene lacune twee van de drie Braziliaanse duels. (3) "
                "Tenerife – Girona: hier LUKTE de omrekening aan beide kanten maar viel ze buiten het gemeten "
                "bereik — Girona's relatieve verdediging komt op 1,074 uit en het gemeten bereik voor SP1/SP2 "
                "omlaag begint bij 1,078 (n=33). Vier duizendsten, en §4 verbiedt extrapoleren, dus NONE is "
                "het juiste antwoord. DAT DERDE GEVAL IS HET INTERESSANTSTE EN HET IS GEEN ACTIEPUNT VOOR "
                "VANDAAG: een bereik dat op 33 waarnemingen rust en op vier duizendsten afsnijdt, is geen "
                "scherpe grens maar een kleine steekproef met een harde rand. Het goede antwoord is de meting "
                "vergroten, niet de rand oprekken — en §4 zegt sinds 9 oktober uitdrukkelijk zo'n meting "
                "liever VÓÓR de analyse van een dag te doen dan erna, omdat een al gepubliceerde run "
                "aanvullen een herberekening een andere uitkomst zou geven dan de run zelf gaf. De "
                "Braziliaanse lacune (2) is de duurste van de drie en staat al sinds 7 oktober open."
            ),
            "BEVINDING_4_CONTEXTLOGBOEK_VERLIEST_62_PROCENT_AAN_EEN_LEGE_NOEMER": (
                "HET CONTEXTLOGBOEK VERLIEST VANDAAG ACHT VAN DE DERTIEN DUELS AAN EEN ONTBREKENDE NOEMER, EN "
                "DOET DAT STIL. ctxlog.py collect nam 5 van de 13 wedstrijden op; de andere acht vielen eruit "
                "omdat Fotmob voor minstens één van de twee ploegen squad_value = 0,0 geeft en "
                "ctxlog.out_share een noemer nodig heeft (out / (basis + out), §1c). Het raakt: PAOK "
                "Thessaloniki – Kalamata (beide 0), Malmö FF – Kalmar FF (beide 0), Elfsborg – Halmstads BK "
                "(beide 0), FC Argeș Pitesti – CFR Cluj (beide 0), Universitatea Cluj – Rapid București "
                "(beide 0), Burgos CF – Granada (Granada 0), Real Oviedo – Eibar (Eibar 0) en Chapecoense – "
                "Athletico Paranaense (Chapecoense 0). DAT IS 62% VAN DE DAG, en het treft twee van de drie "
                "gepubliceerde regels. DIT IS BEKEND MAAR ONDERSCHAT. data/coverage.json legde het op 2 "
                "oktober vast voor de Keuken Kampioen Divisie ('NIEUW GEMETEN EN VAST TE HOUDEN: Fotmob geeft "
                "voor Helmond Sport geen selectiewaarde, waardoor dit duel stil buiten het contextlogboek "
                "valt — dat raakt deze competitie structureel'), en noemde het daar één competitie. Vandaag "
                "blijkt het veel breder: het raakt de Greek Super League, BEIDE Zweedse duels, BEIDE "
                "Roemeense duels en drie van de vijf Spaanse/Braziliaanse. Het is dus geen eigenschap van één "
                "competitie maar van de kleinere en niet-Europese ploegen in Fotmob breed. WAAROM DIT TELT: "
                "§1c heeft nagemeten dat er over het effect van blessures NIETS te zeggen is bij de huidige "
                "aantallen, en de hele oplossing was 'log élke wedstrijd met context in plaats van alleen de "
                "doorgerekende, dan zijn het er ruim honderd per dag en is de vraag over drie tot vier weken "
                "beantwoordbaar'. Een uitval van 62% maakt die rekensom ruim twee keer zo lang. Het logboek "
                "staat vandaag op 1039 afgewikkelde wedstrijden en meet nog steeds niets (model r = -0,035, t "
                "= -1,06, helling -10,1 pp per eenheid; markt r = -0,030, t = -0,91, -8,5 pp), en pas vanaf "
                "~18 pp per eenheid is iets aantoonbaar. WAT HET NIET IS: geen reden om out_share op een "
                "andere noemer te zetten. De verkeerde noemer (out / basis) is precies de fout die §1c op 5 "
                "september heeft gerepareerd en die Lommel – Club Brugge op 247% liet uitkomen. De uitweg is "
                "een tweede bron voor selectiewaarde, of het aantal uitvallers gebruiken in plaats van hun "
                "waarde — en dat laatste is een ANDERE grootheid, dus een eigen reeks en geen vervanging. Dat "
                "is werk voor een volgende run en het is geen besluit voor de gebruiker."
            ),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug), en vandaag slaagt ze "
                "ruim. VIJF van de zes spelende competities hebben een sportkey bij The Odds API en ALLE VIJF "
                "kregen de volledige bulk-aanroep met h2h, spreads en totals — dus vijf van de zes markten, "
                "op de beste prijs per aanbieder: Greek Super League, Eliteserien, Allsvenskan, Segunda "
                "División en Série A (BRA). split_budget(487, 5) gaf (5, 5), dus niemand viel buiten de bulk "
                "en de losse totals-stap was niet nodig. DE ENIGE zonder sportkey is Romanian SuperLiga; die "
                "draait op het gratis BetExplorer-marktgemiddelde, waar 1X2 de enige markt is en de andere "
                "vijf met de reden erbij in markets_checked staan — en waar de bookmaker niet herleidbaar is "
                "(§1a). Dat raakt 2 van de 13 duels. 115 selecties doorgerekend: Over/Under 32, Asian "
                "Handicap 28, 1X2 27, BTTS 14, Draw No Bet 10, Double Chance 4. Alle zes markten dingen dus "
                "werkelijk mee, en de controle SLAAGT met doelpuntenmarkten (OU 32, BTTS 14) én "
                "uitkomstmarkten (1X2 27, AH 28, DNB 10, DC 4). WAT ERUIT KOMT IS WEL EENZIJDIG: alle drie de "
                "regels zijn een doelpuntenmarkt (twee Under, één BTTS-nee), en dat is de tweede dag op rij — "
                "gisteren waren alle vijf het ook. §5b zegt: blijft de lijst dagen achtereen uit één hoek "
                "komen, dan is dat een signaal over het model en niet over de selectieregel. Twee dagen is "
                "nog geen reeks, maar het hoort geteld. Het is geen quotumovertreding (§1 verbiedt bets "
                "forceren om een verdeling te halen)."
            ),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie staat op factor 0,9957, gepoold 0,9933 over 15 speeldagen en TWEE "
                "competities, en dat is de eerste keer in weken dat de factor ONDER 1,0 staat: de correctie "
                "drukt het doelpuntenniveau vandaag licht in plaats van het op te tillen. Lees dat met de "
                "pool erbij — twee competities is een smalle basis. VIER van de zes spelende competities "
                "vallen uit de pool, en de reden is per competitie vastgelegd zoals Stage 5 eist (een stil "
                "weggelaten waarneming is hetzelfde probleem als een stille truncatie): EEN omdat er in geen "
                "van beide seizoenen xG is (Romanian SuperLiga) en DRIE omdat hun seizoen over de helft is, "
                "waardoor league_level route 'lopend' kiest — Eliteserien (22 van 30 speeldagen), Allsvenskan "
                "(23 van 30) en Série A BRA (30 van 38). Dat is exact de constructie van 24 september: die "
                "drie kalenderjaarcompetities zouden de gepoolde factor van de andere optillen en ze halen "
                "hun niveau nu rechtstreeks uit het lopende seizoen (Eliteserien thuis 1,834 / uit 1,349; "
                "Allsvenskan 1,621 / 1,324; Série A 1,534 / 1,125). EEN VAN DE DRIE GEPUBLICEERDE REGELS "
                "STAAT IN DIE GROEP (Malmö FF – Kalmar FF in de Allsvenskan), dus de route 'lopend' is ook "
                "vandaag geen voetnoot. De twee competities die wél in de pool zitten (Greek Super League, "
                "Segunda División) draaien samen met Romanian SuperLiga op route 'vorig+uplift'."
            ),
            "CONTEXT_EN_VERPLAATSING": (
                "context.check_venue zet relocated bij GEEN ENKEL duel — nul van de dertien. POORT 7 hield "
                "VANDAAG NIETS TEGEN: nul selecties, nul wedstrijden. Dat is de tweede poort die vandaag niet "
                "bindt (naast poort 9) en het heeft een begrijpelijke oorzaak: het interlandvenster is net "
                "voorbij, dus de rustkant van de poort kan niet binden — vrijwel elke ploeg komt met ruim "
                "rust de wedstrijd in — en op de blessurekant haalde geen enkel duel de 10 procentpunt "
                "verschil in ontbrekende selectiewaarde. EEN AANTEKENING OVER DE OPSTELLINGEN, want die "
                "bepaalt hoeveel poort 7 vandaag kón doen: van de dertien duels had er geen enkele een "
                "bevestigde opstelling om 05:10 NL. Eén stond op 'predicted', zeven op 'lastStarting11', twee "
                "op 'standard' en twee op 'unavailable'; bij één was het veld leeg. Dat is dezelfde "
                "klokbevinding als de afgelopen dagen en het is geen competitie-eigenschap: Run B draait acht "
                "tot eenentwintig uur voor de aftrap en de opstellingen komen een uur ervoor. Het "
                "contextlogboek blijft daarmee de enige weg naar een meting over het effect van blessures "
                "(§1c), en de context is van ÉLK duel vastgelegd — ook van de vier die op NONE uitkwamen."
            ),
            "BEURSKOERS": (
                "TWEE van de drie gepubliceerde regels staan op een BEURS — Matchbook — en §5 eist dan beide "
                "getallen, want de gebruiker ziet op de site de koers vóór commissie: Malmö FF – Kalmar FF "
                "Under 2,5 2,16 bruto / 2,1368 netto; Burgos CF – Granada 'beide ploegen scoren — nee' 2,02 "
                "bruto / 1,9996 netto. edge_pp en selection_score rekenen met de NETTO koers "
                "(oddsapi.net_price). Dat twee van de drie bij één beurs staan is geen toeval maar wat §1a op "
                "5 september al meet: in 61% van de gevallen staat de beste prijs bij een beurs. DE DERDE, en "
                "het is de kop van de lijst: Real Oviedo – Eibar Under 2,5 @1,75 staat bij 1XBET, geen beurs "
                "en geen scherpe boekmaker. §5 (Stage 5, stap 2) noemt Pinnacle het scherpste publieke "
                "expertoordeel dat er is; een edge tegen een ruimere aanbieder is een zwakkere claim dan "
                "dezelfde edge tegen Pinnacle. Bij Burgos CF – Granada duwt de commissie de koers bovendien "
                "nét onder 2,00 (1,9996), en dat is waarom §5 beide getallen eist. Alle drie de regels komen "
                "van The Odds API op de beste prijs per uitkomst; geen van de drie leunt op het "
                "BetExplorer-marktgemiddelde."
            ),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": (
                "22 credits van een plafond van 487 (19.525 over bij api_check.py, 475 verbruikt deze maand, "
                "20 dagen tot de maandwissel, 2 runs per dag). Stap 0: VIJF bulk-aanroepen à 3 credits (h2h + "
                "spreads + totals) voor alle vijf spelende competities MET sportkey, samen 15 credits; "
                "split_budget(487, 5) -> (5, 5) dus niemand viel buiten de bulk en de losse totals-stap was "
                "niet nodig. Stap 2: BTTS voor de 7 duels met een kandidaat-edge — de vereniging van beide "
                "schalen zoals §1a sinds 13 september voorschrijft — alle zeven ook werkelijk gekocht à 1 "
                "credit, samen 7 credits. EN DIE TWEEDE RONDE HEEFT DE LIJST VANDAAG WERKELIJK VERANDERD: de "
                "derde gepubliceerde regel — Burgos CF – Granada, 'beide ploegen scoren — nee' @1,9996 — "
                "bestaat alleen doordat BTTS in ronde twee is gekocht. In de eerste doorrekening (vóór die "
                "ronde) sneuvelde dat duel nog op robuustheid met een andere kandidaat; de BTTS-selectie "
                "haalt alle negen poorten op de robuustheidstoets (zwakste stand +0,61 pp) en scoort 3,984. "
                "Zonder die ronde had de lijst twee regels gehad in plaats van drie. De 6 duels zonder "
                "kandidaat-edge staan in markets_checked als 'niet opgevraagd — geen kandidaat-edge in dit "
                "duel', niet als gat; bij de twee Roemeense duels staat er bovendien 'geen sportkey'. Na deze "
                "run staat het maandverbruik op 497 van 20.000: het budget is op geen enkele manier de "
                "beperkende factor, en de tijdsgrens van §0 bond vandaag ook niet (13 duels op een cap van "
                "40, nul afgekapt)."
            ),
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
        s3 = json.load(open("tmp-run/rb_oct12_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct12_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct12_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct12_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

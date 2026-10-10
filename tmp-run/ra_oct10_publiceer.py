"""Run A 10 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct08_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. Twaalf duels in het inzetvenster over tien competities, en vier gepubliceerde regels die
alle vier ÓÓK hun eigen drempel halen; dat laatste is op deze routine ongewoon genoeg om het in de
tekst apart te benoemen. `mark_completed` gebeurt pas na het runrapport en de push (Stage -1,
§6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-10"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-10T04:40:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("A", "tmp-run/ra_oct10_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.996150, b=-0.002498 over 3819 afgerekende gevallen, fitted_through "
                          "2026-10-09, oftewel de vorige rundag zoals §6b-5c eist. Deze run heeft "
                          "calibration.py settle gedraaid vóór de analyse (84 waarnemingen "
                          "afgewikkeld, 4026 van 4050 compleet). De correctie is praktisch de "
                          "identiteit: het ruwe model zei gemiddeld 33,333% en het gebeurde "
                          "33,333%, en op de vijf gepubliceerde regels haalt ze tussen 0,08 en "
                          "0,12 procentpunt van de edge af. Dat getal staat hier omdat een niet "
                          "afgewikkeld logboek géén foutmelding geeft — het is van 18 t/m "
                          "29 september elf dagen stil blijven liggen."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "De grootste rundag tot nu toe: TWAALF van de eenentwintig competities uit de "
                "runlijst speelden, met 56 duels samen in het inzetvenster — tegen 12 op "
                "9 oktober. Negen competities hadden GEEN WEDSTRIJD: de Danish Superliga, de "
                "drie Europese toernooien (UCL, UEL, UECL) en de vijf bekers. De eerste vier "
                "staan niet in de Fotmob-daglijst; de vijf bekers hebben geen fotmob_id en zijn "
                "daarom apart langs BetExplorer gegaan — zie BEKERS_GAAN_LANGS_BETEXPLORER."),
            "DE_CAP_BINDT_VOOR_HET_EERST": (
                "56 duels op een zaterdagcap van 55, dus er valt er precies ÉÉN af, en dat is "
                "voor het eerst sinds MAX_DEEP_ANALYSES op 5 september naar 40/55 ging. Stille "
                "truncatie is verboden (§3 Stage 4), dus hier staat wie het was en waarom: "
                "GENK – KORTRIJK (Belgian Pro League, 20:45 NL), datarijkdom 4,5 en vijf "
                "beschikbare markten. De laagste wedstrijd die het nog haalde is Śląsk Wrocław – "
                "Lech Poznań, met exact dezelfde datarijkdom 4,5 en dezelfde vijf markten; het "
                "verschil zit dus niet in de informatie maar in de vierde sorteersleutel, de "
                "aftrap (17:30 NL tegen 20:45 NL). De hoogste datarijkdom in de run was 8,0 en "
                "de laagste 4,5. Met andere woorden: wat er afviel is willekeurig binnen de "
                "LIGHT-staart, precies zoals §0 zegt dat afkappen naar rato kost ('er gaat geen "
                "slechtere groep weg maar een willekeurige'). Beide ploegen in Genk – Kortrijk "
                "hadden hoe dan ook een LIGHT-tier gekregen: Kortrijk staat niet in de Belgische "
                "stand van 2025/2026 en moet worden omgerekend."),
            "ZEVENTIEN_OMREKENINGEN": (
                "Zeventien van de 56 duels hebben een ploeg die niet in de stand van 2025/2026 "
                "staat, tegen vier op 9 oktober — dus de §4-tak die gisteren is gerepareerd is "
                "vandaag de hoofdroute en geen randgeval. Zestien duels kwamen er door "
                "(data_tier LIGHT, want een omgerekende ploeg is nooit FULL) en één sneuvelde: "
                "ALANYASPOR – ERZURUMSPOR FK (Super Lig) komt op NONE uit omdat "
                "promotion.conversion_in_range de omrekening van Erzurumspor FK buiten het "
                "gemeten bereik legt. Dat is correct gedrag en precies de Coventry-val waarvoor "
                "die poort bestaat (§4). Omhoog (TIER2) liepen Ipswich Town, Frosinone, "
                "Paderborn, Elversberg, Le Mans, Cardiff City, Bolton Wanderers, Lincoln City, "
                "Marítimo, Académico Viseu, Kortrijk, Amed Sportif, Erzurumspor FK en Śląsk "
                "Wrocław; omlaag (TIER1, convert_relegated) Wolverhampton Wanderers en Burnley, "
                "die vorig seizoen Premier League speelden en nu in de Championship staan. "
                "LET OP DE RICHTING OMLAAG: §4 zegt zelf dat MEASURED_TIER2_GAP uitsluitend "
                "omhoog meet. Het Engelse paar heeft wel een fd_pair ('E0','E1') bij "
                "football-data.co.uk, dus die twee vallen níet op POOLED_GAP terug — maar een "
                "eigen neerwaartse meting is er niet, en dat hoort bij het lezen van "
                "Middlesbrough – Wolverhampton (+10,62 pp op een LIGHT-lat van 16,0) en "
                "Watford – Burnley. Geen van de zeventien is een gepubliceerde regel geworden."),
            "AMED_SPORTIF_EN_DE_ALIASTABEL": (
                "De aliasregel 'Super Lig (TUR)' -> 'Süper Lig (TUR)' in PROMO_COMP is op "
                "9 oktober vooruitlopend neergezet ('hij staat er voor de eerste Turkse "
                "promovendus die wél langs de omrekening moet') en bindt vandaag voor het eerst "
                "écht: Amed Sportif en Erzurumspor FK staan geen van beide in de Turkse stand "
                "van vorig seizoen. coverage.json schrijft de competitie zonder trema en "
                "promotion.TIER2 met trema; zonder die regel waren beide duels op 'geen divisie "
                "boven of onder Super Lig (TUR) bekend' gestrand in plaats van op een echte "
                "omrekening. Gençlerbirliği – Amed Sportif komt daarmee op LIGHT uit met "
                "+10,23 pp (lat 16,0) en Alanyaspor – Erzurumspor op NONE via "
                "conversion_in_range — twee verschillende uitkomsten, en bij beide is de "
                "omrekening werkelijk geprobeerd."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 10 okt, 08:00 NL 11 okt). Alle 56 duels komen van de "
                "daglijst van 2026-10-10 (source_day = DAY, geen enkele DAY+1) en alle 56 staan "
                "op RunMatch.playable = True: de vroegste aftrap is Gençlerbirliği – Amed "
                "Sportif om 12:30 NL en de run begon om 04:18 NL. De nachtband waarvoor "
                "runwindow.py op 24 september is gebouwd is vandaag leeg; deze runlijst heeft "
                "geen competitie in een Amerikaanse tijdzone. De aftraptijden zijn met twee "
                "bronnen bevestigd (Fotmob in UTC, BetExplorer in UK-tijd) en komen op hetzelfde "
                "NL-tijdstip uit — de controle die §5 'Aftraptijden' eist."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1 eist bevestiging door een tweede methode, en dat geldt ook voor de vraag "
                "wélke wedstrijden er zijn — de duurste fouten van deze maand zaten twee keer in "
                "die vraag en niet in de analyse (6 okt: FA Cup niet in de daglijst; 7 okt: de "
                "is_today-filter aan de prijskant). De 56 duels uit de Fotmob-daglijst zijn "
                "daarom nagelopen tegen de BetExplorer-fixturepagina's van dezelfde twaalf "
                "competities (7 tot 24 rijen per competitie, 3 tot 10 met vandaag als datum) en "
                "tegen de 11 bulk-responsen van The Odds API (6 tot 24 events per competitie). "
                "De drie bronnen zijn eens over de twaalf spelende competities en over de "
                "afwezigheid van de Danish Superliga en de drie Europese toernooien."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "Geen van de vijf bekers op de Run A-runlijst heeft een fotmob_id in "
                "coverage.json, dus runwindow.matches_for_run kan ze niet filteren en 'niet in "
                "de daglijst' is voor hen geen uitspraak. Dat is het gat dat Run A op 6 oktober "
                "trof. Alle vijf zijn daarom opnieuw langs BetExplorer gegaan "
                "(tmp-run/ra_oct10_cups.py) en alle vijf hebben hun eerstvolgende ronde NA het "
                "inzetvenster: FA Cup 17 okt (32 teamparen, nog geen koersen), League Cup "
                "27-29 okt (8 duels mét koersen), DFB Pokal 27-28 okt (16 mét koersen), KNVB "
                "Beker 27-28 okt (26 teamparen), Coppa Italia vanaf 1 dec (8 teamparen). Vijf "
                "keer GEEN WEDSTRIJD, met een tweede bron eronder in plaats van met een stilte. "
                "De drie afgekeurde slugs van 9 oktober staan nog vastgelegd met hun uitkomst, "
                "zodat ze niet opnieuw worden geraden."),
            "SCOTTISH_PREMIERSHIP_ZONDER_SPORTKEY": (
                "De Scottish Premiership is de enige spelende competitie ZONDER sportkey bij The "
                "Odds API, en vandaag heeft ze vier duels — dus voor het eerst deze maand draait "
                "een deel van de runlijst op het gratis BetExplorer-MARKTGEMIDDELDE alleen. "
                "Gevolg per duel, en het staat zo in markets_checked: drie selecties in plaats "
                "van dertien tot eenentwintig (alleen 1X2), en Asian Handicap, Draw No Bet, "
                "Double Chance, Over/Under en BTTS allemaal als 'niet opgevraagd — geen sportkey "
                "bij The Odds API voor deze competitie'. Dat is bekeken met een reden en geen "
                "gat (§1a), maar het betekent óók dat de edge daar systematisch te laag uitvalt: "
                "een marktgemiddelde over 5 boeken is geen beste prijs, en de beste prijs lag "
                "vandaag over de 50 duels met beide bronnen gemiddeld 7,14% hoger (3,84% tot "
                "22,1%). Vier duels zijn dus conservatief beoordeeld en niet vergelijkbaar met "
                "de 52 andere. Alle vier vielen af op de edge en geen van de vier zat in de "
                "buurt van de lijst."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e, teruggezet per "
                       "1 okt 2026); sides.check() is met today=2026-10-10 aangeroepen zoals §1e "
                       "eist, zodat een herberekening van het vervallen venster (25 t/m 30 sep) "
                       "niet stil de poort van vandaag krijgt. Hij heeft vandaag ZIJN DRUKSTE DAG "
                       "gehad: 41 selecties tegengehouden, verdeeld over ZESTIEN wedstrijden die "
                       "elk één rij in poort8_geblokkeerd krijgen — de selectie met de hoogste "
                       "selection_score, met de rest als aantal in ook_geblokkeerd (§1e: één rij "
                       "per wedstrijd, want dezelfde mening in een andere markt is één "
                       "bevinding). Dat is de grootste groei van deze reeks sinds ze bestaat, en "
                       "ze is nodig: de reeks stond op 36 afgewikkelde gevallen. poort8_ruw is "
                       "LEEG — geen enkele selectie sneuvelde alléén op de ruwe schaal, wat "
                       "logisch is bij een fit die praktisch de identiteit is. poort8_vervallen "
                       "is leeg omdat sides.has_lapsed(2026-10-10) onwaar is. Geen van de vijf "
                       "gepubliceerde regels staat op een underdog-kant onder de ondergrens: vier "
                       "hebben side = None (allemaal een Under) en de vijfde is een Draw No Bet "
                       "op Rayo Vallecano, waar de markt de ploegen niet scheidt (pick'em, 34,9% "
                       "om 36,8%). De stand van de twee reeksen wordt alleen GENOEMD en niet "
                       "opnieuw als besluit voorgelegd (§1e, 5 okt)."),
            "WAAROM_VIJF_REGELS": (
                "Vijf regels op vijf plekken (zaterdag, MAX_SHORTLIST = 5), en er is NIET "
                "aangevuld: de lijst is vol omdat er genoeg kandidaten de zeven overgebleven "
                "poorten haalden, niet omdat er naar vijf is toegewerkt. TWEE halen ÓÓK hun "
                "eigen drempel: Inter – Parma Under 3.5 @1,9604 met +8,74 pp en Cracovia – "
                "Zagłębie Lubin Under 2.5 @1,98 met +8,68 pp, beide FULL bij een lat van 8,0. De "
                "andere drie staan er op RANGORDE en blijven onder de lat: RAAL La Louvière – "
                "Club Brugge Under 3.5 @1,686 (+7,74 pp), Lille – Le Havre Under 3 @1,85 "
                "(+7,81 pp) en Rayo Vallecano – Athletic Club Draw No Bet op Rayo @2,06 "
                "(+6,63 pp). Omdat er maar twee boven hun lat staan bepaalt de rangorde de lijst "
                "en gaat de drempel mee als label (§5b stap 5). De §5b-afkapping op LIJSTLENGTE "
                "bindt daarmee niet en de reeks 'lijstlengte' groeit deze run niet. "
                "MAX_LIGHT_IN_SHORTLIST = 2 bindt ook niet: alle vijf regels zijn FULL, en dat is "
                "op een dag met zeventien omgerekende ploegen het noemen waard — geen van de "
                "omrekeningen heeft de lijst gehaald."),
            "WAT_DE_POORTEN_DEDEN": (
                "754 selecties over alle zes markten — vier keer zoveel als op 9 oktober — en de "
                "tweede methode (poort 5) vangt opnieuw het overgrote deel weg: 553 van de 754 "
                "sneuvelden op 'tweede_methode', oftewel 73%. Daarnaast 85 op de edge, 44 op de "
                "koersband, 41 op de underdog-regel, 15 op context, 13 op robuustheid, 1 op de "
                "herijking en 2 die alle poorten open hielden. DIT IS DE VIERDE DAG OP RIJ dat "
                "poort 5 tweederde of meer wegvangt (7 okt 40 van 60, 8 okt 29 van 37, 9 okt 130 "
                "van 174, vandaag 553 van 754), nu over twaalf competities en 56 duels in plaats "
                "van over tien en twaalf. Het is dus geen eigenschap van één competitie en geen "
                "ruis. Het patroon in de lambdas is hetzelfde als gisteren en het is bij de "
                "gepubliceerde regels direct te zien: de SPLITSMETHODE zet een ander "
                "doelpuntenniveau neer dan de xG-methode, niet een andere winnaar. Bij RAAL La "
                "Louvière – Club Brugge geeft xG 0,97 / 2,06 en de splits 0,72 / 1,59; bij Lille "
                "– Le Havre xG 1,83 / 0,98 tegen splits 1,50 / 0,63; bij Rayo – Athletic xG "
                "1,34 / 1,25 tegen splits 1,72 / 0,85. De edge op de splitsarm staat bij die "
                "drie op +20,54, +20,60 en +20,74 pp tegen +4,69, +4,74 en +3,20 pp op de "
                "xG-arm. Poort 5 eist dat beide methodes de markt dezelfde kant op verslaan, en "
                "op een totaal of een handicap is dat precies waar een niveauverschil tussen de "
                "twee methodes doorslaat. §6e wijst de splitsmethode sinds 22 augustus aan als de "
                "scheefste van de twee en §1f heeft haar gewicht daarom op 0,20 gezet; dit is de "
                "vierde dag met cijfers die dezelfde kant op wijzen. OPSCHRIJVEN EN VOLGEN, niet "
                "vandaag aan sleutelen (§6d: niet op één dag een drempel verzetten)."),
            "POORT7_HIELD_VIJFTIEN_SELECTIES_TEGEN": (
                "Voor het eerst sinds dagen houdt de contextpoort werkelijk iets tegen: 15 "
                "selecties over drie wedstrijden, alle drie op de blessurekant en niet op rust. "
                "AJAX – NEC NIJMEGEN is het duidelijkste geval: NEC mist 57% van zijn "
                "selectiewaarde tegen 15% bij Ajax (Clement Bischoff, Ahmetcan Kaplan, Gonzalo "
                "Crettaz), ruim boven het criterium van 10 procentpunt verschil. UNION BERLIN – "
                "ELVERSBERG: Union mist 20% tegen 4% (Josip Juranović, Marvin Friedrich, Andrej "
                "Ilić). BREST – ANGERS: Brest mist 21% tegen 0% (Noah Edjouma, Mamady Diambou, "
                "Brendan Chardonnet). In alle drie de gevallen stond de selectie op de kant van "
                "de ploeg die de spelers mist, en de poort doet dus precies wat §1c beschrijft: "
                "hij houdt alleen tegen, hij stelt my_prob niet bij en hij staat open bij side = "
                "None. Brest – Angers stond op de RUWE dagranglijst nog op plek 5 (Draw No Bet "
                "Brest @1,53, +8,34 pp); dat is de selectie die poort 7 heeft gekost, en dat "
                "hoort erbij te staan."),
            "POORT7_NIET_MEETBAAR_IN_VIJF_COMPETITIES": (
                "Fotmob geeft squad_value = 0 voor ALLE ploegen in vijf van de twaalf spelende "
                "competities: Championship (10 duels), Belgian Pro League (4), Super Lig (4), "
                "Scottish Premiership (4) en Ekstraklasa (3). Dat zijn 25 van de 56 duels; bij de "
                "andere 31 is de selectiewaarde voor beide ploegen bekend. context.check komt in "
                "die 25 correct uit op 'geen materieel nadeel gemeten' — de poort staat open "
                "omdat er niets te meten valt, wat §1c expliciet toestaat. De uitvallers zijn er "
                "wél bij naam bekend (Charlton mist er zes, Rangers vijf) en staan in het "
                "contextblok; wat ontbreekt is hun gewicht. Twee gevolgen die eerlijk benoemd "
                "moeten worden. (1) De blessurekant van poort 7 kan daar niet binden; de "
                "rustkant wel. (2) In de RANGSCHIKKING van Stage 4 kost het die 25 duels "
                "twee punten op de component 'afwezigen', omdat ranking._absence_points de "
                "aanwezigheid van het opstellingsblok aan squad_value > 0 afleest. Dat is "
                "verdedigbaar — de component meet of poort 7 kan werken, en daar kan hij dat "
                "niet — maar het is wél de reden dat alle 25 op datarijkdom 4,5 uitkomen en "
                "daarmee onderaan de sortering staan. Vandaag bepaalde dat welke wedstrijd de "
                "cap afkapte; zie DE_CAP_BINDT_VOOR_HET_EERST."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug). Alle zes "
                "markten hebben werkelijk meegedongen: de bulk-aanroep leverde voor elk van de "
                "elf competities MET sportkey 1X2 op de beste prijs, Asian Handicap, Draw No Bet "
                "en Over/Under, en de tweede ronde kocht BTTS voor de 35 duels met een "
                "kandidaat-edge. 754 selecties: Over/Under 232, Asian Handicap 214, 1X2 159, "
                "BTTS 70, Draw No Bet 48, Double Chance 31. De twee dunne markten zijn geen gat "
                "maar een ontbrekende lijn, en dat staat zo in markets_checked (Double Chance "
                "bestaat alleen waar de spreads-respons een +0,5-lijn had, Draw No Bet alleen "
                "waar er een 0,0-lijn was). De 21 duels zonder kandidaat-edge dragen bij BTTS "
                "'niet opgevraagd' MET de reden, niet 'opgevraagd' — §6b-5b eist dat onderscheid. "
                "DE UITKOMST IS WÉL EENZIJDIG, en dat hoort hier te staan in plaats van te worden "
                "weggelaten: vier van de vijf regels zijn een Under (Over/Under) en de vijfde is "
                "een Draw No Bet. Nul Over, nul 1X2, nul Asian Handicap, nul BTTS. Dat is geen "
                "inkoopeffect — Over/Under en Asian Handicap waren met 232 en 214 selecties de "
                "twee breedste markten van de dag en de handicaps hadden alle ruimte om te "
                "winnen. Het is de uitkomst van selection_score op een dag waarop poort 5 elke "
                "selectie wegvangt waar de twee methodes over het doelpuntenniveau botsen, en "
                "wat er dan overblijft zijn juist de duels waar beide methodes LAAG zitten. Geen "
                "quotum (§1 verbiedt bets forceren om een verdeling te halen); wel iets om te "
                "volgen, want vier Unders op vijf regels is precies het soort eenzijdigheid "
                "waar de gebruiker op 29 augustus over viel."),
            "UPLIFT": (
                "Factor 1,0972 (gepoold 1,1062 over 86 speeldagen, ALLE TWAALF spelende "
                "competities in de pool, NUL overgeslagen door uplift_observations). Alle twaalf "
                "draaien op route 'vorig+uplift': geen enkel lopend seizoen is over de helft van "
                "zijn speeldagen (5 tot 10 gespeeld van 30 tot 46), dus league_level kiest "
                "nergens de route 'lopend'. De correctie doet dus écht iets: 9,7% meer "
                "doelpunten op het niveau van vorig seizoen, meer dan de 7,4% van gisteren, en "
                "dat komt doordat er vandaag twaalf in plaats van tien competities in de pool "
                "zitten — waaronder de Premier League en de Serie A, die gisteren niet speelden. "
                "Gemeten tegen de markt als CONTROLE en niet als fit (§3 Stage 5 verbiedt "
                "afregelen op de markt): zie het runrapport."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("68 credits van een plafond van 449 (19.803 over bij api_check.py, 197 "
                       "verbruikt deze maand, 22 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: elf bulk-aanroepen à 3 credits (h2h + spreads + totals), één per "
                       "spelende competitie MET sportkey — split_budget(449, 11) -> (11, 11), dus "
                       "niemand viel buiten de bulk; 6 tot 24 events per competitie. Stap 2: BTTS "
                       "voor de 35 duels met een kandidaat-edge, 35 credits. De twaalfde spelende "
                       "competitie, de Scottish Premiership, heeft geen sportkey en draaide op "
                       "het gratis BetExplorer-marktgemiddelde — zie "
                       "SCOTTISH_PREMIERSHIP_ZONDER_SPORTKEY. Na deze run staat het maandverbruik "
                       "op 265 van 20.000. De marktbalans-controle slaagt ruim: elf van de twaalf "
                       "competities hebben zowel een doelpuntenmarkt als een uitkomstmarkt. Het "
                       "budget is op geen enkele manier de beperkende factor; MAX_DEEP_ANALYSES "
                       "is dat vandaag voor het eerst wél, met één afgekapt duel."),
            "BEURSKOERS": (
                "§5 eist bij een beurs beide getallen, en DRIE van de vijf regels staan op een "
                "beurs, alle drie bij Matchbook: Inter – Parma Under 3.5 1,98 bruto / 1,9604 na "
                "2% commissie, RAAL La Louvière – Club Brugge Under 3.5 1,70 bruto / 1,686 netto, "
                "en Cracovia – Zagłębie Lubin Under 2.5 2,00 bruto / 1,98 netto. edge_pp en "
                "selection_score rekenen met de NETTO koers (oddsapi.net_price); de gebruiker "
                "ziet de bruto koers op zijn scherm. De andere twee zijn geen beurs en dus "
                "commissievrij: Lille – Le Havre Under 3 @1,85 bij Coolbet en Rayo Vallecano – "
                "Athletic Club Draw No Bet @2,06 bij 1xBet. BetExplorer leverde het gratis "
                "marktgemiddelde voor het kalibratieblok van §6e en voor poort 8 — §1a: "
                "gemiddelde om te MÉTEN, beste prijs om te SPELEN. De beste prijs lag over de 50 "
                "duels met beide bronnen gemiddeld 7,14% boven het marktgemiddelde (3,84% tot "
                "22,1%), in lijn met de +5,63% tot +7,78% die §1a op 5 september mat."),
            "KALIBRATIE_SETTLE": (
                "§6b-5c eist calibration.py settle ELKE run, ook bij nul bets, en eist dat "
                "fitted_through in het runrapport staat. Deze run heeft settle gedraaid vóór de "
                "analyse (84 waarnemingen afgewikkeld) en fitted_through staat op 2026-10-09, de "
                "vorige rundag. Zie HERIJKING. Het kalibratieblok is vandaag voor 54 van de 56 "
                "duels gevuld; de twee die het niet kregen zijn het afgekapte Genk – Kortrijk en "
                "het NONE-duel Alanyaspor – Erzurumspor, en bij die twee is er geen "
                "modelkansverdeling om naast de markt te zetten."),
            "UNDERSTAT": (
                "Het tweede, onafhankelijke xG-model dekte vandaag ZEVENTIEN duels — het hoogste "
                "aantal tot nu toe — omdat alle vijf de Understat-competities speelden (Premier "
                "League 6, Serie A 3, La Liga 4, Bundesliga 6, Ligue 1 5, min de duels waarin een "
                "promovendus niet in de Understat-tabel van 2025 staat). p_xg_understat gaat mee "
                "in het kalibratieblok van §6e, zodat over enkele weken met cijfers te zeggen is "
                "of het ene xG-model beter voorspelt dan het andere. Het verandert my_prob niet "
                "(§4)."),
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
        s3 = json.load(open("tmp-run/ra_oct10_stage3.json"))
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
        for run, pad in (("A", "tmp-run/ra_oct10_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct10_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct10_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

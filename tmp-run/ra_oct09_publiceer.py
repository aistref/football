"""Run A 9 okt 2026 onder §5b: run-state, picks en logboeken.

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

DAG = "2026-10-09"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-09T04:40:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("A", "tmp-run/ra_oct09_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.991766, b=-0.005345 op 3726 afgerekende gevallen, fitted_through "
                          "2026-10-07 TEN TIJDE VAN DE ANALYSE. Dat is één dag vóór de vorige "
                          "rundag (8 okt), en dat is hier GEEN blijven liggen van "
                          "calibration.py settle: de waarnemingen van 8 oktober gaan over "
                          "wedstrijden die pas in de nacht erna zijn afgelopen, dus Run B kon ze "
                          "gisteren niet afwikkelen. Deze run heeft ze afgewikkeld en daarna "
                          "staat de fit op a=0.993655, b=-0.004119 over 3735 gevallen met "
                          "fitted_through 2026-10-08 — dus op de vorige rundag, zoals §6b-5c "
                          "eist. Dat getal staat hier omdat een niet-afgewikkeld logboek geen "
                          "foutmelding geeft; het is van 18 t/m 29 september elf dagen stil "
                          "blijven liggen. De correctie is praktisch de identiteit (het ruwe "
                          "model zei gemiddeld 33,333% en het gebeurde 33,333%) en haalde op de "
                          "vier gepubliceerde regels tussen 0,09 en 0,24 pp van de edge af."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "BEVINDING_1_BLEND_BIJ_OMGEREKENDE_PLOEGEN": (
                "DE BELANGRIJKSTE BEVINDING VAN DEZE RUN, en ze heeft de grootste bet van de dag "
                "gekost — terecht. §4 (\'Het lopende seizoen weegt mee\', 3 sep 2026) schrijft "
                "voor dat de teamsterkte ALTIJD via blend_seasons wordt opgebouwd, met gewicht "
                "n/(n+8) voor het lopende seizoen. De analysecode deed dat voor elke ploeg die in "
                "de stand van vorig seizoen staat, maar NIET voor een ploeg die uit "
                "promotion.convert of convert_relegated komt: die kreeg conv.stats ongeblend, en "
                "de duels die ze dit seizoen in déze divisie al heeft gespeeld bleven ongebruikt. "
                "Dat is precies de groep waarvoor §4 zelf zegt dat het hardst telt — \'bij een "
                "ploeg die in de zomer half is omgebouwd, en daar zitten de PROMOVENDI en de "
                "kleinere competities vol mee\'. Een promovendus is per definitie zo\'n ploeg, en "
                "zijn omgerekende sterkte komt uit een ANDERE divisie; de duels van dit seizoen "
                "zijn het enige directe bewijs op het niveau waarop hij nu speelt. "
                "WAT HET VANDAAG WAARD WAS (gemeten in tmp-run/ra_oct09_blendcheck.py, vóór de "
                "reparatie): vier van de twaalf duels hebben een omgerekende ploeg, en bij SK "
                "Beveren – Lommel zakt P(thuiszege) van 0,745 naar 0,576. Beveren kwam uit First "
                "Division B met een relatieve verdediging van 0,509 — vlak boven de ONDERGRENS "
                "van het gemeten bereik (0,462-1,109) en op een eigen meting van n=13 — maar "
                "staat dit seizoen op 1,06 xG en 2,01 xGA per duel over 7 duels, ruim ONDER het "
                "Belgische competitiegemiddelde van 1,57. Zonder blend leverde dat de grootste "
                "edge van de dag op: de thuiszege @1,8232 op +20,04 pp, ruim boven de LIGHT-lat "
                "van 16,0, en nummer 3 van de dagranglijst. MET de blend valt die edge terug "
                "naar +6,56 pp EN sneuvelt de selectie op poort 6 (zwakste stand van het "
                "(shrink, rho)-grid -2,09), dus ze wordt door twee poorten tegengehouden in "
                "plaats van door geen. De andere drie schuiven ook: Málaga – Espanyol Over 2.5 "
                "van +14,88 naar +8,48 pp, Wieczysta Kraków van +14,28 naar +9,16 pp op de "
                "poort-8-rij, en West Ham – QPR blijft onder zijn lat. "
                "WAAROM DIT IS GEREPAREERD EN NIET ALLEEN GEMELD: dit is geen keuze over "
                "risicobereidheid (zoals poort 8 of selection_score, die een run nooit op eigen "
                "initiatief verandert) maar een rekenstap die §4 met het woord \'altijd\' "
                "voorschrijft en die voor één groep werd overgeslagen. Een dagranglijst die wordt "
                "aangevoerd door een artefact van een overgeslagen rekenstap is erger dan een "
                "korte lijst (§1, §5: nul of minder bets is een geldige uitkomst, aanvullen is "
                "verboden). De SPLITS blijven ongeblend, net als bij een ploeg die wél in de "
                "stand staat — die methode heeft thuis/uit-doelpunten nodig en de code houdt die "
                "bewust op vorig seizoen — dus de reparatie raakt alleen de xG-arm, en tier "
                "blijft LIGHT. De drie FULL-regels van vandaag zijn er NIET door veranderd: geen "
                "van hun ploegen is omgerekend. "
                "WAT ER NOG MOET GEBEUREN: de reparatie staat nu in het runscript van vandaag "
                "(tmp-run/ra_oct09_analyze.py, _blend_omgerekend) en niet op een gedeelde plek. "
                "Elke run bouwt zijn side_stats opnieuw op uit het script van de vorige dag, dus "
                "zonder overzetten draait Run B en Run C morgen weer op de ongeblende versie — "
                "en die twee runlijsten zitten vol promovendi (Série B, de Engelse lagere "
                "divisies, de kalenderjaarcompetities). Dit hoort naar scripts/promotion.py of "
                "scripts/model.py, zodat er één implementatie is in plaats van drie die "
                "uiteenlopen — precies de redenering waarmee de aliastabel op 5 oktober naar "
                "scripts/teamnames.py is verhuisd."),
            "BEVINDING_2_NAAMKOPPELING_BEIDE_KANTEN_OP": (
                "Een stille faalstand gevonden en gerepareerd, in dezelfde familie als de "
                "is_today-filter van 7 oktober: ra_names.resolve las de aliastabel maar ÉÉN kant "
                "op. Het zocht de gevráágde naam op in ALIASES, niet de sleutel in de tabel. "
                "BetExplorer noteert de Championship-rij als \'West Ham - QPR\'; ALIASES heeft "
                "qpr -> queens park rangers, en dat helpt alleen als de vraag \'QPR\' is. Gevolg: "
                "de thuisploeg koppelde wel en de uitploeg niet, best_pair viel terug op 0,273 "
                "gelijkenis (vloer 0,62) en gaf None, en West Ham – QPR kreeg GEEN "
                "1X2-marktgemiddelde. Dat kostte geen bet — het duel haalde zijn LIGHT-lat "
                "nergens — maar wel twee dingen die de regels expliciet nodig hebben: het "
                "kalibratieblok van §6e bleef leeg (1 van de 12 waarnemingen van de dag) en "
                "poort 8 kwam uit op \'geen 1X2-prijzen, dus geen marktoordeel over wie de "
                "mindere is\' en stond dus OPEN zonder te zijn getoetst. Na de reparatie "
                "(resolve leest de tabelsleutels óók door ALIASES heen) hebben alle twaalf duels "
                "een marktgemiddelde en alle twaalf een kalibratieblok, staat het gemiddelde van "
                "West Ham – QPR op 17 boeken (1,47 / 4,57 / 5,83) en is poort 8 daar werkelijk "
                "getoetst (West Ham is de favorietenkant, 63,5% tegen 16,0%). Deze reparatie "
                "hoort om dezelfde reden als Bevinding 1 naar scripts/teamnames.py, waar de "
                "aliastabel zelf al staat."),
            "RUNLIJST": (
                "Tien van de eenentwintig competities uit de runlijst speelden, met twaalf duels "
                "samen. Zes hadden GEEN WEDSTRIJD op de Fotmob-daglijst (Premier League, Serie "
                "A, Scottish Premiership en de drie Europese toernooien) en de vijf BEKERS zijn "
                "apart gemeten — zie BEKERS_GAAN_LANGS_BETEXPLORER. scripts/idcheck.py gaf voor "
                "alle 33 fotmob_id\'s uit coverage.json een bruikbare stand (afsluitcode 0), "
                "inclusief alle zestien Run A-competities MÉT id. Het runrapport van 8 oktober "
                "noteerde als openstaand punt dat idcheck Run A niet dekte; dat is vandaag "
                "nagelopen en het klopt niet meer. Wat idcheck.py NIET dekt zijn de vijf bekers, "
                "en dat kán hij ook niet: die hebben geen fotmob_id."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "Geen van de vijf bekers op de Run A-runlijst heeft een fotmob_id in "
                "coverage.json, dus runwindow.matches_for_run kan ze niet filteren en de "
                "Fotmob-daglijst is voor hen geen bron. Dat is precies het gat dat Run A op "
                "6 oktober trof: de FA Cup-kwalificatie stond niet in de daglijst van die dag "
                "(59 competities, FA Cup er niet bij) en wél bij BetExplorer, met vijf duels in "
                "het venster. \'Niet in de daglijst\' mag dus nooit als GEEN WEDSTRIJD worden "
                "opgeschreven zonder tweede bron. Alle vijf zijn daarom langs BetExplorer "
                "nagelopen (tmp-run/ra_oct09_cups.py) en alle vijf hebben hun eerstvolgende "
                "ronde NA het inzetvenster: FA Cup 17 okt (32 teamparen, nog geen koersen), "
                "League Cup 27-29 okt (8 duels mét koersen), DFB Pokal 27-28 okt (16 mét "
                "koersen), KNVB Beker 27-28 okt (26 teamparen), Coppa Italia vanaf 1 dec (8 "
                "teamparen). Vijf keer GEEN WEDSTRIJD, nu met een tweede bron eronder in plaats "
                "van met een stilte. Drie afgekeurde slugs staan vastgelegd met hun uitkomst "
                "(fa-cup-qualification, netherlands/beker en toto-knvb-beker geven alle drie 0 "
                "teamparen op 564.497 bytes — de homepage-redirect die betexplorer.py als "
                "stille faalmodus documenteert), zodat een volgende run ze niet opnieuw raadt."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 9 okt, 08:00 NL 10 okt). Alle twaalf duels zijn gewone "
                "Europese avondwedstrijden tussen 18:00 en 21:15 NL, alle twaalf van de daglijst "
                "van 2026-10-09 (source_day = DAY, geen enkele DAY+1) en alle twaalf met "
                "RunMatch.playable = True — de run begon om 04:18 NL, ruim voor de vroegste "
                "aftrap van 18:00. De nachtband waarvoor runwindow.py op 24 september is "
                "gebouwd is vandaag leeg; deze runlijst heeft geen competitie in een "
                "Amerikaanse tijdzone. De aftraptijden zijn met twee bronnen bevestigd: Fotmob "
                "geeft ze in UTC en BetExplorer in UK-tijd, en de twee komen op elk duel uit op "
                "hetzelfde NL-tijdstip (Dortmund 19:30 UK = 20:30 NL, Galatasaray 18:00 UK = "
                "19:00 NL) — de controle die §5 \'Aftraptijden\' eist."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1 eist bevestiging door een tweede methode, en dat geldt ook voor de vraag "
                "wélke wedstrijden er zijn — de duurste fouten van deze week zaten twee keer in "
                "die vraag en niet in de analyse (6 okt: FA Cup niet in de daglijst; 7 okt: de "
                "is_today-filter aan de prijskant). De twaalf duels uit de Fotmob-daglijst zijn "
                "daarom onafhankelijk nagelopen tegen de BetExplorer-fixturepagina\'s van "
                "dezelfde tien competities. De twee bronnen zijn VOLLEDIG EENS: dezelfde twaalf "
                "duels, en nul in het venster bij Premier League, Serie A, Scottish "
                "Premiership, UCL, UEL en UECL."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e, teruggezet per "
                       "1 okt 2026); sides.check() is met today=2026-10-09 aangeroepen zoals "
                       "§1e eist, zodat een herberekening van het vervallen venster (25 t/m "
                       "30 sep, sides.LAPSED_FROM/LAPSED_UNTIL) niet stil de poort van vandaag "
                       "krijgt. Hij heeft vandaag voor het eerst sinds 24 september WEER "
                       "TEGENGEHOUDEN: twee wedstrijden, zes selecties. PSV – Heerenveen, "
                       "Heerenveen +2.5 @1,67 (+9,72 pp, markt geeft Heerenveen 10,5% tegen "
                       "76,4%) met 1 andere geblokkeerde selectie, en Wieczysta Kraków – Wisła "
                       "Płock, Wisła Płock +0,25 @1,95 (+9,16 pp, 30,2% tegen 43,3%) met 3 "
                       "andere — die staan als aantal in ook_geblokkeerd, want §1e eist één rij "
                       "per wedstrijd: dezelfde mening in een andere markt is één bevinding. "
                       "poort8_ruw is leeg (geen selectie sneuvelde alléén op de ruwe schaal). "
                       "poort8_vervallen is leeg EN DAT IS NIEUW: dat blok wordt sinds vandaag "
                       "alleen gevuld als sides.has_lapsed(DAY) waar is. Zonder die voorwaarde "
                       "vulde het zich voor negen wedstrijden met de mededeling dat poort 8 "
                       "\'zou hebben geblokkeerd als hij niet was vervallen\' — terwijl hij "
                       "bindt en ze ook écht heeft geblokkeerd. Dat stond dan dubbel in de "
                       "run-state, naast poort8_geblokkeerd dat het al zegt, onder een veldnaam "
                       "die het tegendeel beweert. Geen van de vier gepubliceerde regels staat "
                       "op een underdog-kant onder de ondergrens: drie hebben side = None (twee "
                       "Over en een Under) en Lens staat op de favorietenkant (39,9% om 34,3%). "
                       "De stand van de twee reeksen wordt alleen GENOEMD en niet opnieuw als "
                       "besluit voorgelegd (§1e, 5 okt: niet elke dag opnieuw vragen)."),
            "WAAROM_VIER_REGELS": (
                "Vier regels op vijf plekken (vrijdag, MAX_SHORTLIST = 5), en er is NIET "
                "aangevuld om de lijst vol te maken (§5 verbiedt dat expliciet). Drie halen ÓÓK "
                "hun eigen drempel: Nordsjælland – OB Over 3.25 +12,60 pp, Dortmund – Werder "
                "Under 3.5 +12,13 pp en Lens – Lyon de thuiszege +10,57 pp, alle drie FULL bij "
                "een lat van 8,0. De vierde, Málaga – Espanyol Over 2.5 @2,1564 met +8,48 pp, "
                "staat er op RANGORDE: hij haalt de zeven overige poorten maar blijft ruim onder "
                "de LIGHT-lat van 16,0, en omdat er maar drie boven hun lat staan bepaalt de "
                "rangorde de lijst en gaat de drempel mee als label (§5b stap 5). Er is dus een "
                "plek OPEN gebleven, en dat is de uitkomst en geen tekort. De §5b-afkapping op "
                "LIJSTLENGTE bindt niet en de reeks \'lijstlengte\' groeit deze run niet. "
                "MAX_LIGHT_IN_SHORTLIST = 2 bindt ook niet: er is één LIGHT-regel (Málaga). "
                "Zonder de reparatie van Bevinding 1 had hier een vijfde regel gestaan met de "
                "grootste edge van de dag erbij — die is weggevallen omdat hij een artefact was, "
                "niet omdat de dag slechter is geworden."),
            "WAT_DE_POORTEN_DEDEN": (
                "174 selecties over alle zes markten, en de tweede methode (poort 5) vangt "
                "opnieuw het overgrote deel weg: 130 van de 174 sneuvelden op "
                "\'tweede_methode\' — 75% — tegen 13 op de edge, 11 op de koersband, 6 op de "
                "underdog-regel, 5 op robuustheid, 0 op context en 9 die alles open hielden. "
                "DIT IS DE DERDE DAG OP RIJ dat deze poort tweederde of meer wegvangt (7 okt: "
                "40 van 60; 8 okt: 29 van 37; vandaag 130 van 174), en nu voor het eerst over "
                "tien competities in plaats van één of twee — dus het is geen eigenschap van de "
                "Braziliaanse Série A. §5 (\'Net niet\') zegt dat een poort die dagen achtereen "
                "alles wegvangt een bevinding is over die poort en geen ruis, en §6e wijst de "
                "splitsmethode al sinds 22 augustus aan als de scheefste van de twee. Vier van "
                "de twaalf duels vielen er volledig op af (PSV – Heerenveen, Moreirense – Gil "
                "Vicente, Galatasaray – Kasımpaşa en West Ham – QPR). Het patroon is bij alle "
                "vier hetzelfde en het is te zien in de lambdas: de splitsmethode zet een HOGER "
                "doelpuntenniveau neer dan de xG-methode, niet een andere richting. PSV – "
                "Heerenveen xG 2,574 / 1,063 tegen splits 3,472 / 1,686; Galatasaray – Kasımpaşa "
                "xG 2,193 / 0,738 tegen splits 3,551 / 0,775. De twee methodes zijn het dus eens "
                "over wie de betere ploeg is en oneens over hoeveel er valt — en poort 5 eist dat "
                "ze de markt dezelfde kant op verslaan, wat op een totaal of een handicap dan "
                "juist misgaat. Opschrijven en in de gaten houden, niet vandaag aan sleutelen. "
                "Dat de context-poort vandaag NUL selecties tegenhield komt doordat de ene "
                "selectie die hij vóór de reparatie van Bevinding 1 tegenhield (Málaga -1) nu al "
                "eerder afvalt; de poort zelf staat ongewijzigd dicht op dat duel — zie "
                "POORT7_BIJ_MALAGA."),
            "POORT7_BIJ_MALAGA": (
                "Bij Málaga – Espanyol mist Málaga 35% van zijn selectiewaarde tegen 5% bij "
                "Espanyol — Jens-Lys Cajuste (terug medio oktober), Diego Murillo (begin januari "
                "2027) en Aarón Ochoa (medio november) — ruim boven het criterium van 10 "
                "procentpunt verschil waarop poort 7 dichtgaat op de kant van Málaga. De "
                "gepubliceerde regel op dit duel is dan ook geen kant maar een totaal (Over 2.5, "
                "side = None), waar de poort per definitie openstaat omdat er geen kant is om te "
                "benadelen. Dat is geen omzeiling maar precies hoe §1c de poort beschrijft: hij "
                "is asymmetrisch en grof, hij houdt een KANT tegen en zegt niets over een "
                "totaal, want in welke richting context een totaal verschuift is zonder meting "
                "niet te zeggen. Het hoort hier genoemd te worden, want de gebruiker ziet een "
                "bet op een wedstrijd waarvan de thuisploeg een derde van zijn selectiewaarde "
                "mist — en bij een Over is dat eerder een argument vóór dan tegen, maar dat is "
                "een redenering en geen meting, dus my_prob is er niet mee aangepast."),
            "POORT7_NIET_MEETBAAR_IN_VIER_COMPETITIES": (
                "Fotmob geeft squad_value = 0 voor ALLE ploegen in vier van de tien spelende "
                "competities: Championship, Belgian Pro League, Super Lig en Ekstraklasa. "
                "ctxlog.out_share geeft dan correct None in plaats van 100%, en context.check "
                "komt uit op \'geen materieel nadeel gemeten\' — de poort staat open omdat er "
                "niets te meten valt, wat §1c expliciet toestaat (\'een meting die er niet is, is "
                "geen bewijs van een probleem\'). Gevolg voor de meting die §1c opbouwt: 5 van de "
                "12 duels van vandaag vallen buiten het contextlogboek (West Ham – QPR, SK "
                "Beveren – Lommel, Galatasaray – Kasımpaşa, Wieczysta Kraków – Wisła Płock, "
                "Raków – GKS Katowice), dus het logboek groeit met 7 in plaats van 12. Dat is "
                "hetzelfde gat als bij de Braziliaanse ploegen op 7 en 8 oktober, nu in kaart "
                "gebracht per competitie in plaats van per wedstrijd. De uitvallers zijn in die "
                "vier competities wél bij naam bekend en staan in het contextblok; wat ontbreekt "
                "is hun gewicht."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug). Alle "
                "zes markten hebben werkelijk meegedongen, en voor het eerst deze week over tien "
                "competities: de bulk-aanroep leverde voor alle tien 1X2 op de beste prijs, "
                "Asian Handicap, Draw No Bet en Over/Under, en de tweede ronde kocht BTTS voor "
                "de negen duels met een kandidaat-edge. 174 selecties: Over/Under 62, Asian "
                "Handicap 50, 1X2 34, BTTS 18, Draw No Bet 8, Double Chance 2. De twee dunne "
                "markten zijn GEEN gat maar een ontbrekende lijn, en dat staat zo in "
                "markets_checked: Double Chance bestaat alleen waar de spreads-respons een "
                "+0,5-lijn had (Lens – Lyon en Moreirense – Gil Vicente; de overige tien \'geen "
                "+0.5-lijn in de spreads-respons\'), en Draw No Bet alleen waar er een 0,0-lijn "
                "was (vier duels). BTTS staat bij de drie duels zonder kandidaat-edge als \'niet "
                "opgevraagd\' met de reden erbij, niet als opgevraagd — §6b-5b eist dat het "
                "verschil tussen \'opgevraagd en niet gevonden\' en \'niet opgevraagd\' in de "
                "administratie staat. progress.py verify is groen: alle 12 geanalyseerde "
                "wedstrijden hebben alle zes markten gehad. De uitkomst is verdeeld over twee "
                "marktsoorten: drie doelpuntenregels — twee Over (Nordsjælland Over 3.25, Málaga "
                "Over 2.5) en één Under (Dortmund Under 3.5) — en één uitkomstregel (Lens, "
                "thuiszege). Dat de doelpuntenregels niet allemaal dezelfde kant op staan is het "
                "noemen waard, want eenzijdigheid is precies waar de gebruiker op 29 augustus "
                "over viel. Een quotum is er niet (§1); dit is de uitkomst."),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie is vandaag GEVULD, en dat is het verschil met "
                "gisteren, toen de pool leeg was en de factor op 1,0000 terugviel. Factor "
                "1,0742 (gepoold 1,0828 over 69 speeldagen, alle TIEN de spelende competities in "
                "de pool, NUL overgeslagen). Alle tien draaien op route \'vorig+uplift\': geen "
                "enkel lopend seizoen is over de helft van zijn speeldagen (4 tot 9 gespeeld van "
                "30 tot 46), dus league_level kiest nergens de route \'lopend\'. Dat de pool deze "
                "keer vol is komt doordat alle tien xG hebben in beide seizoenen — precies de "
                "voorwaarde die uplift_observations stelt en die gisteren bij beide spelende "
                "competities faalde. De correctie doet dus écht iets: 7,4% meer doelpunten op "
                "het niveau van vorig seizoen, wat klopt met het patroon dat §3 Stage 5 "
                "beschrijft. Gemeten tegen de markt, als CONTROLE en niet als fit (§3 Stage 5 "
                "verbiedt afregelen op de markt): over de tien duels met een 2,5-lijn in de "
                "respons ligt het model gemiddeld +2,5 procentpunt boven de markt op P(Over "
                "2.5), mediaan +4,0 pp, met 8 van de 10 boven de markt. Dezelfde richting als de "
                "scheefstand die §6e op de doelpuntenmarkten meldt, maar de spreiding is groot "
                "en niet eenzijdig: van -10,9 pp (Dortmund – Werder) tot +12,8 pp (Nordsjælland "
                "– OB), met twee duels onder de markt. Het is dus geen vlakke scheefstand die je "
                "eraf kunt halen, en bij Dortmund is de gepubliceerde regel juist de UNDER — "
                "daar zegt het model mínder doelpunten dan de markt."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("39 credits van een plafond van 431 (19.857 over bij api_check.py, 143 "
                       "verbruikt deze maand, 23 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: tien bulk-aanroepen à 3 credits (h2h + spreads + totals), één "
                       "per spelende competitie — alle tien hebben een sportkey, dus "
                       "split_budget(431, 10) -> (10, 10) en niemand viel buiten de bulk; 6 tot "
                       "24 events per competitie. Stap 2: BTTS voor de negen duels met een "
                       "kandidaat-edge, 9 credits. De enige Run A-competitie ZONDER sportkey is "
                       "de Scottish Premiership, en die speelt vandaag niet — er is dus geen "
                       "duel dat op het gratis BetExplorer-marktgemiddelde alleen moest draaien. "
                       "Na deze run staat het maandverbruik op 182 van 20.000; het budget is op "
                       "geen enkele manier de beperkende factor, en MAX_DEEP_ANALYSES is dat "
                       "vandaag ook niet (12 duels op een cap van 55, nul afgekapt)."),
            "BEURSKOERS": (
                "§5 eist bij een beurs beide getallen, en ÉÉN van de vier regels staat op een "
                "beurs: Málaga – Espanyol, Over 2.5 bij Matchbook, 2,18 bruto en 2,1564 na 2% "
                "commissie. edge_pp en selection_score rekenen met de netto koers "
                "(oddsapi.net_price); de gebruiker ziet 2,18 op zijn scherm. De andere drie zijn "
                "géén beurs en dus commissievrij: Nordsjælland – OB Over 3.25 @1,93 bij "
                "Pinnacle, Dortmund – Werder Under 3.5 @1,89 bij 1xBet en Lens – Lyon de "
                "thuiszege @2,48 bij Unibet (SE). Bij Dortmund is dat laatste geen toeval maar "
                "het gevolg van de netto-vergelijking: Matchbook noteerde dezelfde 1,89 BRUTO, "
                "maar dat is 1,8722 na commissie en dus slechter dan de 1,89 van 1xBet. "
                "BetExplorer leverde het gratis marktgemiddelde (3 tot 17 boeken per duel) voor "
                "het kalibratieblok van §6e en voor poort 8 — §1a: gemiddelde om te MÉTEN, beste "
                "prijs om te SPELEN. De beste prijs lag over de twaalf duels 4,15% tot 13,98% "
                "boven het marktgemiddelde (gemiddeld 7,11%), in lijn met de +5,63% tot +7,78% "
                "die §1a op 5 september mat; de uitschieter is PSV – Heerenveen met 13,98%, een "
                "duel waarop niet is gepubliceerd."),
            "KALIBRATIE_SETTLE": (
                "§6b-5c eist calibration.py settle ELKE run, ook bij nul bets, en eist dat "
                "fitted_through in het runrapport staat — het ontbreken ervan heeft van 18 t/m "
                "29 september elf dagen stil schade gedaan zonder één foutmelding. Deze run "
                "heeft collect en settle in die volgorde gedraaid en fitted_through staat erna "
                "op 2026-10-08, de vorige rundag. Zie HERIJKING."),
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
        s3 = json.load(open("tmp-run/ra_oct09_stage3.json"))
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
        for run, pad in (("A", "tmp-run/ra_oct09_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct09_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct09_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

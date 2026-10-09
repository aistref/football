"""Run B 9 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `rb_oct08_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. Negentien duels in het inzetvenster over acht van de zeventien competities, nul afgekapt
(cap 55), en vier gepubliceerde regels die alle vier op RANGORDE staan: geen enkele selectie
haalde vandaag haar eigen drempel. `mark_completed` gebeurt pas na het runrapport en de push
(Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-09"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-09T05:10:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("B", "tmp-run/rb_oct09_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=0.993655, b=-0.004119 op 3735 afgerekende gevallen, fitted_through "
                          "2026-10-08. Die datum is de vórige rundag, dus calibration.py settle "
                          "is niet blijven liggen (§6b-5c). Deze run wikkelde er zelf 0 af, en "
                          "dat is hier geen overgeslagen stap maar de juiste uitkomst: Run A "
                          "heeft vanmorgen om 02:30 de waarnemingen van 8 oktober al afgewikkeld, "
                          "waarna 3942 van 4002 compleet zijn en de 60 openstaande de duels van "
                          "vandaag zijn. De correctie is praktisch de identiteit (het ruwe model "
                          "zei gemiddeld 33,333% en het gebeurde 33,333%) en haalde op de vier "
                          "gepubliceerde regels 0,11 tot 0,18 pp van de edge af: 6,99 -> 6,82 "
                          "(Avellino), 11,02 -> 10,84 (Heidenheim), 4,24 -> 4,11 (Braunschweig) "
                          "en 7,02 -> 6,91 (Volendam). Let op wat die identiteit wél en niet "
                          "zegt: de reeks is de ONGESELECTEERDE ijksteekproef, breder dan de "
                          "selecties waarop gespeeld wordt — zie §1e, punt 3 van 30 sep."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "ACHT van de zeventien competities speelden, met 19 duels in het inzetvenster — "
                "de breedste Run B-dag sinds de competities zijn hervat. Negen hadden GEEN "
                "WEDSTRIJD (Greek Super League, Hungarian NB I, Segunda División, Swiss Super "
                "League, Austrian Bundesliga, English League One, English League Two, MLS en "
                "Série A). scripts/idcheck.py gaf voor alle 33 fotmob_id\'s uit coverage.json een "
                "bruikbare stand (afsluitcode 0), dus geen enkele competitie is stil uit de lijst "
                "verdwenen — precies de controle waarvoor idcheck.py op 29 september is gebouwd. "
                "VANDAAG IS DE DAG DIE prompts/run-b.md VOORSPELDE: Serie B (ITA) speelt weer "
                "voor het eerst sinds 20 september, en het id 86 (en niet 56) is daarmee voor het "
                "eerst in een echte wedstrijd gebruikt — Avellino – Sampdoria, met xG voor beide "
                "ploegen en als enige FULL-duel dat ook een gepubliceerde regel opleverde. De "
                "tien duels van de Keuken Kampioen Divisie zijn meer dan de helft van de dag; "
                "die competitie heeft geen xG bij Fotmob en geen sportkey bij The Odds API, dus "
                "daar draait alles op doelpunten als sterktemaat en op het gratis "
                "BetExplorer-marktgemiddelde voor 1X2."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 9 okt, 08:00 NL 10 okt). Alle negentien duels stonden op "
                "de daglijst van 2026-10-09 zelf (source_day = DAY, geen enkele DAY+1) en trappen "
                "af tussen 17:00 en 20:30 NL; alle negentien hebben RunMatch.playable = True. Dat "
                "is de makkelijke variant van deze runlijst: de twee competities die het "
                "inzetvenster echt op de proef stellen — MLS en Série A, met aftrappen in de nacht "
                "ná de rundag — spelen vandaag niet. runwindow.py is gewoon gebruikt zoals Stage 1 "
                "voorschrijft, maar hij hoefde vandaag niets te verschuiven. De run begon om 05:04 "
                "NL, ruim twaalf uur voor de vroegste aftrap."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e); sides.check() is met "
                       "today=2026-10-09 aangeroepen zoals §1e eist, zodat het vervallen venster "
                       "van 25 t/m 30 september uit sides.LAPSED_FROM/LAPSED_UNTIL wordt gelezen "
                       "en niet geraden. Hij hield vandaag DRIE selecties tegen, alle drie in de "
                       "Keuken Kampioen Divisie en alle drie de uitploeg op 1X2: Jong FC Utrecht "
                       "bij De Graafschap (+8,84 pp, marktkans 28,6%), RKC Waalwijk bij Heracles "
                       "(+9,51 pp, 22,0%) en Jong PSV bij Roda JC Kerkrade (+4,63 pp, 25,2%). "
                       "Geen van de drie zou de lijst hebben aangevoerd en geen van de drie haalde "
                       "zijn LIGHT-lat van 16,0, dus de poort heeft vandaag geen bet gekost — maar "
                       "hij is wel de reden dat RKC niet bovenaan de RUWE lijst staat. "
                       "poort8_ruw is leeg: alle drie sneuvelden al op de herijkte schaal, dus er "
                       "is geen aparte ruwe rij (§1e, \'nooit dezelfde selectie twee keer\'). "
                       "poort8_vervallen is leeg omdat het venster voorbij is. "
                       "STAND VAN DE TWEE REEKSEN, en die is bewogen sinds 5 oktober: `underdog` "
                       "staat nu op 45 afgewikkelde gevallen met +4,6% rendement (51,1% trefkans) "
                       "tegen 36 gevallen met +16,9% op 5 oktober — nog steeds positief, maar "
                       "beduidend zwakker, en dat hoort er net zo eerlijk bij als de +16,9% toen. "
                       "`underdog_ruw` staat onveranderd op 17 gevallen met -8,8%. Die twee "
                       "blijven twee populaties en worden niet opgeteld. De vraag van 25 september "
                       "wordt hier NIET opnieuw voorgelegd: §1e zegt uitdrukkelijk hem niet elke "
                       "dag opnieuw te stellen en pas terug te komen als de reeks van teken "
                       "draait of de kalibratiefout verdwenen is. Geen van beide is gebeurd — de "
                       "reeks is positief gebleven en de fout staat op +1,96 pp te veel kans op "
                       "longshots en -3,77 pp te weinig op favorieten over 4002 uitkomsten."),
            "BEVINDING_1_DE_BLEND_BIJ_OMGEREKENDE_PLOEGEN_KENT_TWEE_EENHEDEN": (
                "DE BELANGRIJKSTE BEVINDING VAN DEZE RUN, en ze is het directe vervolg op "
                "bevinding 1 van Run A van vanmorgen. Run A repareerde dat §4 (\'Het lopende "
                "seizoen weegt mee\') niet werd toegepast op een ploeg uit promotion.convert of "
                "convert_relegated: die kreeg conv.stats ONGEBLEND. Die reparatie is hier "
                "overgenomen en bleek NOG NIET VOLLEDIG: ze test op `cr[\'xg\'] is not None` en "
                "valt bij een competitie ZONDER xG terug op dezelfde ongeblende sterkte. Voor "
                "Run A maakte dat niets uit — alle tien competities van die run hebben xG bij "
                "Fotmob — maar op deze runlijst hebben VIJF van de zeventien competities geen xG "
                "(Czech First League, Croatian HNL, Hungarian NB I, Romanian SuperLiga, Keuken "
                "Kampioen Divisie) en draaien die per prompts/run-b.md op doelpunten. Juist daar "
                "viel §4 dus nog steeds stil weg, en juist daar zitten de omgerekende ploegen: "
                "ACHT van de negentien duels van vandaag hebben een ploeg zonder stand in het "
                "vorige seizoen, tegen vijf van de twaalf bij Run A. "
                "DAT DE EENHEID KLOPT IS GEEN AANNAME. promotion.convert rekent de relatieve "
                "sterkte uit de lagere divisie terug naar top_league.avg_xg_per_match — het "
                "niveau van de DOELcompetitie — en bij een competitie zonder xG is dat niveau het "
                "doelpuntgemiddelde (model.league_level zet dat zo). conv.stats staat dus in "
                "dezelfde eenheid als de gf/ga van het lopende seizoen; er wordt geen xG bij "
                "doelpunten opgeteld. De tak voor een ploeg MET stand kent die tweedeling al, dus "
                "dit is de bestaande regel doortrekken en geen nieuwe keuze. "
                "WAT HET VANDAAG WAARD WAS, gemeten door de run twee keer volledig door te "
                "rekenen (de ongerepareerde uitkomst staat in het scratchpad, niet in de repo): "
                "drie duels veranderen, alle drie in de Keuken Kampioen Divisie, en alle drie "
                "omdat Volendam, Heracles en NAC Breda degradant zijn uit de Eredivisie. "
                "(1) Heracles – RKC Waalwijk: de omgerekende aanval van Heracles staat op 1,837 "
                "doelpunten per duel, maar Heracles maakt dit seizoen 3,111 per duel in de KKD. "
                "Met de blend (gewicht 0,529 over 9 duels) wordt dat 2,511, en de kans op een "
                "RKC-zege zakt van 40,5% naar 28,6%: de geclaimde edge valt van +21,46 pp terug "
                "naar +9,51 pp. Dat was de HOOGSTE edge van de hele dag en de nummer 1 van de "
                "ruwe dagranglijst; na de reparatie staat die selectie niet eens meer in de top "
                "vijf. Poort 8 hield hem hoe dan ook tegen, dus het heeft geen bet gekost — maar "
                "zonder deze stap had het runrapport de dag geopend met een edge van 21 "
                "procentpunt die een artefact is van een overgeslagen rekenstap, en §5 zegt met "
                "zoveel woorden dat zo\'n lijst erger is dan een korte lijst. "
                "(2) FC Volendam – Vitesse: de edge op een Volendam-zege valt van +9,83 naar "
                "+6,91 pp en de selection_score van 2,611 naar 1,734, waardoor deze regel in de "
                "dagranglijst van plek 3 naar plek 4 zakt — achter Braunschweig. Volendams "
                "verdediging is de oorzaak: omgerekend 1,129 tegen 1,889 werkelijk dit seizoen. "
                "(3) NAC Breda – MVV Maastricht: geen bet voor of na, maar de thuiszege zakt van "
                "71,9% naar 68,7% kans. "
                "EEN SAMENLOOP DIE OPVALT EN GEEN FOUT IS: alle drie de Nederlandse degradanten "
                "komen op een relatieve aanval van exact 0,648 uit. Dat is nagetrokken in de "
                "Eredivisie-stand van 2025/2026 en het is echt: Volendam, Heracles en NAC "
                "maakten alle drie 35 doelpunten in 34 duels. Hun verdediging verschilt wél "
                "sterk (55, 85 en 58 tegen), en dat is ook waar de drie uitkomsten uiteenlopen. "
                "WAT ER NIET IS GEREPAREERD: de splits blijven ongeblend, net als in de tak voor "
                "een ploeg met stand, en de tier blijft LIGHT. De omrekening haalt de "
                "systematische fout eruit, niet de onzekerheid (§4)."),
            "BEVINDING_2_DRIE_DUELS_OP_NONE_DOOR_EEN_ONTBREKEND_DIVISIEPAAR": (
                "Drie van de negentien duels komen op data_tier = NONE uit, en alle drie om "
                "dezelfde reden: promotion.TIER1/TIER2 kent voor Croatian HNL (CRO) en Romanian "
                "SuperLiga (ROU) GEEN divisiepaar, dus een promovendus uit die competities kan "
                "niet worden omgerekend. De foutmelding is letterlijk \'geen divisie boven of "
                "onder Croatian HNL (CRO) bekend\' respectievelijk \'... Romanian SuperLiga "
                "(ROU) ...\'. Het ging om HNK Gorica – Rudeš (Rudeš promovendus), Corvinul "
                "Hunedoara – FC Voluntari (BEIDE promovendus) en Sepsi OSK – Dinamo București "
                "(Sepsi promovendus). "
                "DIT IS GEEN NAAMVERSCHIL zoals bij Segunda División op 21 september of de twee "
                "Engelse divisies op 26 september — die stonden wél in de tabel onder een andere "
                "spelling en zijn met een PROMO_COMP-regel opgelost. Kroatië en Roemenië staan er "
                "helemaal niet in: §4 zegt dat TIER2 dertien divisieparen bevat die alle dertien "
                "op naam en land zijn GEVERIFIEERD, en dat na de meting van 31 augustus geen "
                "enkele competitie uit de runlijst nog op een gepoolde factor draait. Er een "
                "gepoolde factor bij verzinnen zou precies dat terugdraaien en is wat §2 en §4 "
                "verbieden. NONE is dus de eerlijke uitkomst en geen omissie om vandaag op te "
                "lossen. Wat het kost is wel het opschrijven waard: het is de hele Roemeense "
                "lijst (twee van twee duels) en het enige Kroatische duel, oftewel 3 van de 19 "
                "duels van de dag. Wie het ooit wil oplossen, lost het op zoals 31 augustus: "
                "eerst de factor voor dat divisiepaar METEN over meerdere seizoenen, dan de "
                "ingang toevoegen."),
            "WAT_DE_POORTEN_DEDEN": (
                "110 selecties over zes markten, en de tweede methode is voor de DERDE DAG OP RIJ "
                "de poort die vrijwel alles wegvangt: 84 van de 110 (76%) sneuvelden op "
                "\'tweede_methode\' — de twee methodes verslaan de markt niet dezelfde kant op — "
                "tegen 17 op de edge, 6 op de koersband en 3 op de underdog-poort. Poort 6 "
                "(robuustheid) en poort 7 (context) hielden vandaag niets tegen. Op 7 oktober was "
                "het 40 van 60 en op 8 oktober 29 van 37; vandaag 84 van 110. §5 (\'Net niet\') "
                "zegt dat zoiets dagen achtereen een BEVINDING is over de splitsmethode en geen "
                "ruis, en §6e wijst de splitsmethode al sinds 22 augustus aan als de scheefste "
                "van de twee. Nu met drie dagen en 207 selecties erachter is dat geen "
                "waarneming meer maar een reeks. Twee dingen die het relativeren voordat iemand "
                "eraan gaat sleutelen: (a) het schaduwlogboek zegt dat deze poort NIET duidelijk "
                "geld bespaart — 105 kandidaten, 99 afgewikkeld, -0,2% rendement, oftewel "
                "break-even; hij kost dus vooral bets en bespaart nauwelijks geld, en dat is al "
                "het tweede cijfer dat in die richting wijst; (b) vandaag is de oorzaak op twee "
                "duels letterlijk te zien in de lambdas: bij Eintracht Braunschweig – Holstein "
                "Kiel geeft de xG-methode 1,645 / 1,342 (thuis sterker) en de splitsmethode "
                "1,275 / 1,576 (uit sterker) — tegengesteld, en daar is de hoogst scorende "
                "selectie van het duel op afgeketst (1X2 thuis, +7,65 pp op xG tegen -6,13 pp op "
                "de splits). Bij Jong Ajax – VVV-Venlo hetzelfde beeld. Dit blijft een reeks om "
                "op te schrijven en te volgen, niet om vandaag een drempel op te verzetten "
                "(§6d: niet op één dag, en zeker niet op drie)."),
            "WAAROM_VIER_REGELS_EN_ALLE_VIER_OP_RANGORDE": (
                "Vier regels op vijf plekken (vrijdag, MAX_SHORTLIST = 5), en alle vier staan er "
                "op RANGORDE: geen enkele selectie van de dag haalde haar eigen drempel. Avellino "
                "– Sampdoria Under 2.5 op +6,82 pp tegen een FULL-lat van 8,0; FC Heidenheim – "
                "Kaiserslautern thuiszege op +10,84 pp tegen een LIGHT-lat van 16,0; Eintracht "
                "Braunschweig – Holstein Kiel Under 3 op +4,11 pp tegen 8,0; FC Volendam – "
                "Vitesse thuiszege op +6,91 pp tegen 16,0. §5b snijdt sinds 20 september aan het "
                "EIND van de dag: staan er minder selecties boven de drempel dan er regels in de "
                "lijst passen, dan bepaalt de rangorde de lijst en gaat de drempel mee als LABEL. "
                "Er is geen vijfde regel geworden omdat er maar vier publiceerbare selecties "
                "waren over de hele runlijst — vijftien van de negentien duels leverden niets op "
                "dat alle zeven overgebleven poorten haalde. Aanvullen is precies wat §5 "
                "verbiedt. MAX_LIGHT_IN_SHORTLIST bond op het randje en is NIET bindend geweest: "
                "er zijn exact twee LIGHT-regels (Heidenheim en Volendam) en twee is het "
                "maximum, maar er was geen derde LIGHT-kandidaat die erbuiten viel. De "
                "§5b-afkapping op LIJSTLENGTE bond dus niet en de reeks \'lijstlengte\' groeit "
                "deze run niet (die staat op 5 gevallen, waarvan 5 afgewikkeld, +14,9%)."),
            "MARKTBALANS": (
                "De controle gaat over de INKOOP en niet over de uitkomst (§1a, 29 aug), en "
                "vandaag is dat verschil groot. VIER van de acht spelende competities hebben een "
                "sportkey bij The Odds API — Eliteserien, Allsvenskan, Serie B en 2. Bundesliga — "
                "en die kregen alle vier de bulk-aanroep met h2h, spreads en totals, plus BTTS "
                "voor de drie duels met een kandidaat-edge waar een event-id bij hoorde. De "
                "ANDERE VIER hebben geen sportkey (Czech First League, Croatian HNL, Romanian "
                "SuperLiga, Keuken Kampioen Divisie) en draaien dus op het gratis "
                "BetExplorer-marktgemiddelde; daar is 1X2 de enige markt en staan de vijf andere "
                "in markets_checked met \'niet opgevraagd — geen sportkey bij The Odds API voor "
                "deze competitie\'. Dat is dertien van de negentien duels met één markt in plaats "
                "van zes, en dat moet hier staan omdat het van buitenaf niet te zien is. "
                "110 selecties: 1X2 48, Over/Under 28, Asian Handicap 17, Draw No Bet 8, BTTS 6, "
                "Double Chance 3. Double Chance is laag omdat de spreads-respons bij Serie B en "
                "Avellino geen +0,5-lijn had (\'geen +0.5-lijn in de spreads-respons\'), niet "
                "omdat de markt niet is bekeken. De marktbalans-controle SLAAGT: er zijn "
                "doelpuntenmarkten (Over/Under 28, BTTS 6) én uitkomstmarkten (1X2 48, AH 17, DNB "
                "8, DC 3) werkelijk doorgerekend, en de vier gepubliceerde regels komen uit twee "
                "markten (twee Over/Under, twee 1X2). Een quotum is er niet (§1)."),
            "UPLIFT": (
                "De vroeg-seizoenscorrectie staat op factor 1,0359, gepoold 1,0620 over 11 "
                "speeldagen en TWEE competities: Serie B (ITA, 5 speeldagen) en 2. Bundesliga "
                "(GER, 6). ZES van de acht spelende competities vallen uit de pool, en de reden "
                "is per competitie vastgelegd zoals Stage 5 eist (een stil weggelaten waarneming "
                "is hetzelfde probleem als een stille truncatie): vier omdat er in geen van beide "
                "seizoenen xG is (Czech First League, Croatian HNL, Romanian SuperLiga, Keuken "
                "Kampioen Divisie) en twee omdat hun seizoen over de helft is en league_level dus "
                "route \'lopend\' kiest — Eliteserien op 21 van 30 speeldagen en Allsvenskan op "
                "22 van 30. Dat is exact de constructie van 24 september: die twee "
                "kalenderjaarcompetities zouden de gepoolde factor van de andere optillen, en ze "
                "halen hun niveau nu rechtstreeks uit het lopende seizoen (Eliteserien thuis "
                "1,845 / uit 1,315; Allsvenskan 1,619 / 1,318). De zes overige competities draaien "
                "op route \'vorig+uplift\'. Let op het verschil met 8 oktober: toen was de pool "
                "LEEG en viel de factor terug op 1,0000; vandaag zitten er twee competities in en "
                "doet de correctie weer echt iets."),
            "CONTEXT_EN_VERPLAATSING": (
                "context.check_venue zet relocated = True bij ÉÉN duel: Jong AZ Alkmaar – FC Den "
                "Bosch wordt gespeeld in het AFAS Trainingscomplex in Wijdewormer, terwijl "
                "Fotmob als eigen stadion van de thuisploeg het AFAS Stadion noteert. §1c eist "
                "dat een verplaatsing wordt genoemd ook als de poort opengaat, dus hij staat "
                "hier — maar lees hem goed: dit is GEEN verplaatsing. Jong AZ is een beloftenploeg "
                "en speelt zijn thuiswedstrijden structureel op het trainingscomplex; Fotmob geeft "
                "bij zo\'n ploeg het stadion van de moederclub terug. De controle ziet dus een "
                "echt verschil, maar de oorzaak is de stamkaart van de ploeg en niet een verhuisde "
                "wedstrijd. Dat is het soort geval waarvoor de controle met opzet alleen MELDT en "
                "niet tegenhoudt (§1c). Houd in de gaten of het bij de vier beloftenploegen op "
                "deze runlijst (Jong Ajax, Jong AZ, Jong PSV, Jong FC Utrecht) elke keer terugkomt; "
                "is dat zo, dan is het een eigenschap van de bron en hoort het als zodanig in "
                "coverage.json. Poort 7 hield vandaag NIETS tegen: bij geen enkel duel miste de "
                "gespeelde kant 10 procentpunt meer selectiewaarde dan de tegenstander, en de "
                "rustkant bond nergens. Bij de tien KKD-duels is de blessurekant van poort 7 "
                "bovendien niet meetbaar — Fotmob geeft daar squad_value = 0 — dus staat de poort "
                "daar per definitie open; de uitvallers zijn wél bij naam bekend. Dat is een "
                "ontbrekende meting en geen bewijs dat het niet uitmaakt (§1c)."),
            "BEURSKOERS": (
                "Twee van de vier gepubliceerde regels staan op een beurs en §5 eist dan beide "
                "getallen. Regel 1, Avellino – Sampdoria Under 2.5 bij MATCHBOOK: 1,87 bruto en "
                "1,8526 na 2% commissie, en edge_pp en selection_score rekenen met die 1,8526 "
                "(oddsapi.net_price). Regel 2, FC Heidenheim – Kaiserslautern thuiszege bij "
                "BETFAIR: 1,93 bruto en 1,9114 netto. Regel 3, Eintracht Braunschweig – Holstein "
                "Kiel Under 3 bij Pinnacle @1,99: geen beurs, geen commissie. Regel 4, FC "
                "Volendam – Vitesse thuiszege @2,31: dat is het BetExplorer-MARKTGEMIDDELDE over "
                "3 boeken en geen prijs van één aanbieder — de bookmaker is niet herleidbaar en "
                "dat staat zo in de pick. Dat is de zwakste prijsonderbouwing van de vier en "
                "hoort als zodanig gelezen te worden: §1a zegt gemiddelde om te MÉTEN en beste "
                "prijs om te SPELEN, en bij een competitie zonder sportkey is het gemiddelde het "
                "enige dat er is. De gebruiker kan daar dus beter krijgen dan 2,31 of slechter; "
                "de target-notatie (\'target minimum odds\') is hier de eerlijke lezing. Waar de "
                "beste prijs wél te bepalen was, lag hij 4,57% tot 7,30% boven het "
                "marktgemiddelde — in lijn met de +5,63% tot +7,78% die §1a op 5 september mat."),
            "afgekapt": res["afkapping"]["afgekapt"], "afkapping": res["afkapping"],
            "inkoop": ("15 credits van een plafond van 430 (19.818 over bij api_check.py, 182 "
                       "verbruikt deze maand, 23 dagen tot de maandwissel, 2 runs per dag). "
                       "Stap 0: vier bulk-aanroepen à 3 credits (h2h + spreads + totals) voor de "
                       "vier spelende competities MET sportkey — Eliteserien, Allsvenskan, Serie B "
                       "en 2. Bundesliga, samen 12 credits; split_budget(430, 4) -> (4, 4) dus "
                       "niemand viel buiten de bulk. Stap 2: BTTS voor drie van de zeven duels met "
                       "een kandidaat-edge, 3 credits; de andere vier vielen af omdat hun "
                       "competitie geen sportkey heeft en er dus geen event-id is om op te vragen. "
                       "EEN OPMERKING OVER api_check.py: die lijst noemt soccer_norway_eliteserien "
                       "en soccer_sweden_allsvenskan niet onder \'Relevante sportkeys\', en toch "
                       "leverden beide gewoon acht events. Die lijst is een handmatige selectie in "
                       "het script en geen uitspraak over wat The Odds API aanbiedt — lees hem "
                       "niet als \'deze competitie heeft geen prijzen\'. Na deze run staat het "
                       "maandverbruik op 197 van 20.000, dus het budget is op geen enkele manier "
                       "de beperkende factor."),
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
        s3 = json.load(open("tmp-run/rb_oct09_stage3.json"))
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
        for run, pad in (("B", "tmp-run/rb_oct09_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/rb_oct09_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/rb_oct09_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

"""Run A 7 nov 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_nov07_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. DERTIEN van de eenentwintig competities uit de runlijst speelden, plus de FA Cup, met
86 duels in het inzetvenster — de volste dag van deze reeks.

VIJF GEPUBLICEERDE BETS EN ALLE VIJF OP OVER/UNDER. Dat is de bevinding van de run en ze is
NIET uit de portemonnee te verklaren: de marktbalans van §1a is op de inkoop gehaald met de
ruimste marge die er is (13 van de 13 inkoopbare competities kregen zowel een uitkomst- als een
doelpuntenmarkt), en alle zes de markten dongen mee met 668 doorgerekende selecties. Zie
ALLE_VIJF_DE_GEPUBLICEERDE_BETS_STAAN_OP_DE_DOELPUNTENMARKT_EN_DAT_IS_DE_ANALYSE_EN_NIET_DE_INKOOP.

DE CAP BINDT VOOR HET EERST SINDS WEKEN, EN HIJ KOSTTE ZES ANALYSES EN GEEN EENENDERTIG. 86 duels
op een zaterdagcap van 55, dus 31 afgekapt — maar 25 van die 31 zijn FA Cup-duels die op `NONE`
uitkwamen omdat er geen vergelijkbare historie is, en die kostten dus niets. Zie
DE_CAP_KOSTTE_ZES_ANALYSES_EN_NIET_EENENDERTIG_EN_DE_KNIP_LIEP_DWARS_DOOR_EEN_GELIJKSPEL.

DE FA CUP SPEELDE MET 33 DUELS EN LEVERDE EEN GEKWALIFICEERDE SELECTIE OP. Het id 132 dat Run A
op 6 november vond, staat onder `notes` in `coverage.json` en is vanochtend meteen de moeite waard
geweest. Zie DE_FA_CUP_LEVERDE_EEN_GEKWALIFICEERDE_SELECTIE_OP_EN_DAT_IS_DE_OPBRENGST_VAN_ID_132.

POORT 5 HOUDT VOOR DE DERDE DAG OP RIJ HET GROOTSTE DEEL VAN ALLES TEGEN: 498 van de 668
selecties (74,6%). Zie POORT_5_HOUDT_VOOR_DE_DERDE_DAG_OP_RIJ_DRIEKWART_VAN_ALLE_SELECTIES_TEGEN.

EEN VAN DE VIJF BETS STAAT OP DE UNDER-KANT, waar `margins.py goalbias` vanochtend over 127
gespeelde gevallen +0,626 doelpunt per duel te weinig meet (z = +4,25) — harder dan gisteren.
Zie EEN_VAN_DE_VIJF_BETS_STAAT_OP_DE_UNDER_KANT_WAAR_DE_SCHEEFSTAND_GEMETEN_IS.

UNDERSTAT VALT VOOR DE ZESDE DAG UIT en raakt vandaag 18 van de 52 doorgerekende duels. Zie
UNDERSTAT_VALT_VOOR_DE_ZESDE_DAG_UIT_EN_RAAKT_VANDAAG_ACHTTIEN_DUELS.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-11-07"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-11-07T03:05:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer + de BTTS-ronde), werkelijke klok (wintertijd)


def slug(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", t)).strip("-")


def state_uit(res, run):
    st = {"date": DAG, "run": run, "competitions": {}}
    for m in res["matches"]:
        st["competitions"].setdefault(m["competition"],
                                      {"status": "GEANALYSEERD", "matches": []})["matches"].append(m)
    return st


def bronnen_van(m, cand):
    """De onafhankelijke kansinputs van dit duel, met de bron per cijfer (§2)."""
    uit = []
    lam = (m.get("lambdas") or {}).get("xg") or []
    sw = m.get("seizoensweging") or {}
    if m.get("promovendi"):
        uit.append(
            "Fotmob team-xG, met de omgerekende ploeg via scripts/promotion.py (§4 Promovendi: "
            "relatieve sterkte uit de divisie eronder, omgerekend met een gemeten divisiefactor "
            "en getoetst aan conversion_in_range) en daarna geblend met het lopende seizoen "
            f"(§4, k=8)" + (f"; doelverwachting {lam[0]:.3f} thuis / {lam[1]:.3f} uit"
                            if len(lam) == 2 else ""))
    else:
        uit.append(
            "Fotmob team-xG van 2025/2026 geblend met het lopende seizoen (§4 blend_seasons, "
            f"k=8)" + (f"; doelverwachting {lam[0]:.3f} thuis / {lam[1]:.3f} uit"
                       if len(lam) == 2 else ""))
    sp = (m.get("lambdas") or {}).get("split") or []
    uit.append("Fotmob thuis/uit-doelpuntensplits van 2025/2026 (tweede methode, §1d "
               "multiplicatief en op het competitiegemiddelde genormaliseerd)"
               + (f"; doelverwachting {sp[0]:.3f} / {sp[1]:.3f}" if len(sp) == 2 else ""))
    if m.get("understat"):
        u = m["understat"]
        uit.append(f"Understat team-xG als tweede, ONAFHANKELIJK xG-model (§4): "
                   f"doelverwachting {u['lambdas'][0]:.3f} / {u['lambdas'][1]:.3f}, "
                   f"rollende xG over 8 duels {u['rolling_xg_8']}")
    uit.append("Fotmob wedstrijdcontext: voorspelde/laatste opstelling, uitvallers met "
               "marktwaarde, vorm over vijf duels, rustdagen en stadioncontrole")
    if sw:
        uit.append("seizoensweging per ploeg: " + json.dumps(sw, ensure_ascii=False))
    return uit


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
        onder = (r["market"] == "Over/Under" and r["selection"].startswith("Under"))
        tier_light = r["tier"] != "FULL"
        picks.append({
            "id": f"{DAG}-{slug(m['competition'])}-{slug(home)}-{slug(away)}-{slug(r['market'])}-{slug(r['selection'])}",
            "run": run, "run_date": DAG, "kickoff": m["kickoff_utc"],
            "competition": m["competition"], "home": home, "away": away,
            "market": r["market"], "selection": r["selection"], "odds": r["odds"],
            "odds_source": r["odds_source"], "odds_captured_at": CAPTURED,
            "implied_prob": round(1 / r["odds"], 4), "my_prob": r["prob"],
            "edge_pp": r["edge_pp"], "data_tier": r["tier"],
            "confidence": "Medium" if r["tier"] == "FULL" else "Low",
            "prob_sources": bronnen_van(m, cand), "shortlisted": True, "result": "pending",
            "notes": (f"Gepubliceerd op rangorde (§5b): plek {top['herijkt'].index(r)+1} van "
                      f"{len(top['herijkt'])} over {len(res['matches'])} doorgerekende wedstrijden. "
                      f"{r['status']}. selection_score {r['score']}. "
                      f"Ruwe kans {cand.get('my_raw')}, ruwe edge {cand.get('edge_raw')} pp; "
                      f"xG-methode {cand.get('edge_xg')} pp, splitsmethode {cand.get('edge_split')} pp, "
                      f"zwakste stand van het (shrink, rho)-grid {cand.get('edge_robust_min')} pp. "
                      f"shrink staat sinds 19 sep op 1.00 (§6e). "
                      + ("OMGEREKENDE PLOEG: een ploeg in dit duel komt uit de divisie eronder of "
                         "erboven en is via scripts/promotion.py omgerekend (§4), dus data_tier is "
                         "LIGHT en de lat 16,0 pp — nooit FULL, want de omrekening haalt de "
                         "systematische fout eruit en niet de onzekerheid. "
                         if m.get("promovendi") else "")
                      + (("ONDER-KANT, EN DIT IS DE KANT MET DE GEMETEN SCHEEFSTAND. §6g meet "
                          "dat de gespeelde Under-kant scheef staat, en dat is vanmorgen opnieuw "
                          "gemeten over 1996 doorgerekende duels: P(Under 2.5) voorspeld 42,5% "
                          "tegen werkelijk 40,5% (-2,1 pp), massa verschoven van 0-2 "
                          "doelpunten naar 4 en 5, en op de duels waar werkelijk een Under is "
                          "gespeeld +0,597 doelpunt per duel over 124 gevallen (z = +4,01) "
                          "terwijl de Over-kant op -0,268 staat (z = -1,19 over 66 gevallen). "
                          "HET MODEL ZELF STAAT GOED (+0,046 doelpunt per duel, z = +1,18); het "
                          "is de SELECTIE die scheef staat, en die twee regels mogen nooit als "
                          "een getal worden gelezen. "
                          "WAT ER AL IN ZIT: `model.LEVEL_SCALE` = 1.032 bindt sinds gisteren "
                          "(§0, §6g 'Het besluit van 2 november 2026') en schroeft de "
                          "lambdas van de xG-methode 3,2% op, wat P(Under) ongeveer twee "
                          "procentpunt VERLAAGT. De kans hierboven is dus AL gecorrigeerd - trek "
                          "er niet nog eens twee procentpunt af, want dan tel je dezelfde "
                          "correctie twee keer. De cijfers in deze alinea komen juist uit de "
                          "lambdas van VOOR die knop (alles t/m 2 november is ongecorrigeerd, "
                          "3 november is de eerste gecorrigeerde rundag) en beschrijven de "
                          "fout die de knop moet wegnemen, niet de stand erna. Of dat gelukt is, "
                          "is pas te zien zodra er genoeg duels van na 3 november liggen; §1h "
                          "zegt met zoveel woorden dat poort 9 tot die tijd onveranderd blijft "
                          "staan en dat een run hem niet op eigen initiatief verzet. "
                          + ("DIT DUEL STAAT OP LIGHT EN POORT 9 RAAKT HET DUS NIET: "
                             "`unders.TIERS` is (\"FULL\",) en dat is een besluit van de "
                             "gebruiker van 12 oktober 2026 ('twee hoeft nog niet op de zwakke "
                             "data; eerst kijken wat deze rem doet'), geen omissie. Deze Under "
                             "is daarmee alleen aan zijn eigen LIGHT-lat van 16,0 pp getoetst "
                             "en door geen enkele extra rem. "
                             if tier_light else
                             "Dit duel staat op FULL, dus poort 9 (§1h) kan hier bijten; of hij "
                             "dat werkelijk doet hangt af van de band waarin de edge valt - hij "
                             "bindt ALLEEN tussen 8,0 en 10,0 pp, en laat een Under daaronder met "
                             "opzet door omdat `edge` daar de bindende poort hoort te zijn. ")
                          + "De oorzaakkant - keuze (a) van 11 oktober - is op 28 oktober "
                            "gemeten en AFGEWEZEN (§6g: de voorgeschreven vormcorrectie "
                            "verergert het symptoom en de vormfout bleek grotendeels een "
                            "nalatenschap van shrink = 0.80, op 19 sep opgelost); de "
                            "niveaucorrectie van 2 november is wat daarvoor in de plaats is "
                            "gekomen. ")
                         if onder else "")
                      # `bet_beide = False` heeft DRIE oorzaken en ze zijn niet hetzelfde. Op
                      # 2 november stonden er twee: de lat op geen van beide schalen halen, en
                      # hem ruw wél en herijkt niet halen. De DERDE is op 3 november voor het
                      # eerst voorgekomen (Barcelona - Aston Villa, Under 4.5: herijkt +16,23 pp
                      # boven de LIGHT-lat van 16,0 en ruw +15,39 pp eronder) en kreeg de tekst
                      # van het geval "haalt hem nergens". Dat is onwaar, en het is dezelfde
                      # stille faalvorm als de twee eerdere: de tekst klaagt niet. De drie
                      # gevallen zijn uit `failed_gate` en `failed_gate_ruw` te lezen en niet
                      # uit `bet_beide` alleen — dat veld is één bit voor drie standen.
                      + ("" if cand.get("bet_beide") else
                         (f"bet_beide = FALSE, maar alleen op de HERIJKTE schaal: ruw haalt deze "
                          f"selectie haar lat met {cand.get('edge_raw')} pp wél en herijkt met "
                          f"{cand.get('edge_pp')} pp niet. Dat is de reeks `herijking` van §5a, "
                          f"en de rij is hier geen schaduwpick maar een gepubliceerde bet omdat "
                          f"de rangorde van §5b erover gaat. "
                          if cand.get("bet_ruw") else
                          (f"bet_beide = FALSE, maar alleen op de RUWE schaal: HERIJKT haalt deze "
                           f"selectie haar lat met {cand.get('edge_pp')} pp WEL (alle negen "
                           f"poorten open) en ruw met {cand.get('edge_raw')} pp niet. Dat is de "
                           f"spiegel van de reeks `herijking` - `herijking_omgekeerd` in §5a, "
                           f"mogelijk sinds de fit van 20 september een kans in deze band juist "
                           f"VERHOOGT. Publiceren gebeurt op de herijkte schaal (§1 en §5a: "
                           f"'vertrouw de vlag, niet de redenering'), dus dit is een "
                           f"gekwalificeerde bet en geen rangorderegel. "
                           if cand.get("failed_gate") is None else
                           "bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide "
                           "schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel "
                           "(§5b). ")))),
        })
    return st, top, picks, res


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("A", "tmp-run/ra_nov07_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "ALLE_VIJF_DE_GEPUBLICEERDE_BETS_STAAN_OP_DE_DOELPUNTENMARKT_EN_DAT_IS_DE_ANALYSE_EN_NIET_DE_INKOOP": (
                "DE LIJST VAN VANDAAG IS VIJF REGELS LANG EN STAAT VIJF KEER OP OVER/UNDER. Vier "
                "Overs (Malaga - Racing Santander, Nacional - Academico Viseu, Sporting CP - "
                "Moreirense, Mainz 05 - Bayern Munchen, Osasuna - Athletic Club viel op rang 6 "
                "buiten de lijst) en een Under (Roma - Sassuolo). Geen 1X2, geen handicap, geen "
                "Draw No Bet, geen Double Chance, geen BTTS. "
                "WAAROM DIT GEEN INKOOPARTEFACT IS, EN DAT IS HIER DE HELE VRAAG. §1a heeft de "
                "marktbalans-controle juist hiervoor gebouwd: op 29 augustus 2026 kwamen 12 van de "
                "14 bets uit een markt en dat was de portemonnee en niet de analyse, omdat "
                "Over/Under in negen van de elf competities de enige betaalde markt was. Vandaag "
                "is het omgekeerde waar. De bulk-aanroep (h2h + spreads + totals, 3 credits per "
                "competitie) is voor ALLE DERTIEN inkoopbare competities gelukt, 39 van 409 "
                "credits, dus elke competitie had zowel een uitkomstmarkt (1X2, AH, DNB, DC) als "
                "een doelpuntenmarkt. 13 van 13 - de ruimste marge waarmee die controle ooit is "
                "gehaald. Daarbovenop is BTTS in een tweede ronde gekocht voor 36 duels met een "
                "kandidaat-edge (§1a stap 2), 36 credits. Alle zes de markten dongen dus mee. "
                "WAT ER WERKELIJK IS DOORGEREKEND: 668 selecties over 52 duels, verdeeld als "
                "Over/Under 220, Asian Handicap 159, 1X2 144, BTTS 72, Draw No Bet 49 en Double "
                "Chance 24. De doelpuntenmarkt is dus de grootste van de zes, maar met een derde "
                "van het totaal en niet met vijf vijfde - de scheefstand zit in wat eruit komt en "
                "niet in wat erin ging. "
                "WAT DE LOGBOEKEN OVER DEZE KANT ZEGGEN, en het is de reden dat dit meer is dan "
                "een curiositeit. Over 468 afgewikkelde bets staat `Over/Under - Over` op +6,6% "
                "rendement over 90 gevallen (trefkans 56,7%) en is daarmee na Draw No Bet (+29,4% "
                "over 18) de beste markt van het logboek; `Over/Under - Under` staat op -15,7% "
                "over 159. Vier van de vijf regels van vandaag staan op de kant die historisch "
                "heeft opgeleverd en een op de kant die heeft gekost. Dat is geen voorspelling - "
                "§1g heeft op 552 gevallen gemeten dat er GEEN drempel bestaat die geld oplevert - "
                "maar het is wel de juiste manier om deze lijst te lezen. "
                "WAT HIER NIET UIT VOLGT: er wordt geen quotum ingevoerd en geen bet geforceerd om "
                "de verdeling recht te trekken. §1a zegt het met zoveel woorden: dit is een "
                "rapportageplicht en geen quotum, en als alle zes de markten meedingen en er komt "
                "toch een eenzijdige lijst uit, dan IS dat de uitkomst. Bets forceren om een "
                "verdeling te halen is precies wat §1 verbiedt. Wat er wel uit volgt is dat deze "
                "verdeling is opgeschreven in plaats van weggemoffeld, want zonder de tabel van "
                "§1a is van buitenaf niet te zien of een eenzijdige lijst uit de analyse of uit de "
                "inkoop komt."),

            "DE_CAP_KOSTTE_ZES_ANALYSES_EN_NIET_EENENDERTIG_EN_DE_KNIP_LIEP_DWARS_DOOR_EEN_GELIJKSPEL": (
                "`MAX_DEEP_ANALYSES` BINDT VANDAAG VOOR HET EERST SINDS WEKEN: 86 duels in het "
                "inzetvenster op een zaterdagcap van 55 (`ranking.max_deep_analyses`), dus 31 "
                "afgekapt. Stille truncatie is verboden (§3 Stage 4), dus hier staat precies wat "
                "het kostte. "
                "HET KOSTTE ZES ANALYSES EN GEEN EENENDERTIG, EN DAT VERSCHIL IS DE HELE "
                "BOODSCHAP. Van de 31 afgekapte duels komen er 25 op `tier = NONE` uit en zes op "
                "`LIGHT`. Die 25 zijn allemaal FA Cup-duels waarin minstens een ploeg niet in de "
                "stand van de Championship 2025/2026 staat en ook niet in een divisie eronder waar "
                "de tegenstander ook staat - non-league-clubs als Marine, Harborough Town, "
                "Alvechurch, Sholing en AFC Rushden & Diamonds. Daar is geen vergelijkbare "
                "historie en dus geen onafhankelijke kansinput (§2), en `NONE` betekent geen bet. "
                "Die duels waren met of zonder cap niet doorgerekend; de cap kostte daar niets. "
                "DE ZES DIE HET WEL KOSTTE, met naam: Blackburn Rovers - West Ham United, Queens "
                "Park Rangers - Lincoln City, Royal Antwerp - Lommel, Galatasaray - Amed Sportif, "
                "St. Johnstone - Dundee FC en Gornik Zabrze - Wieczysta Krakow. Alle zes `LIGHT`, "
                "alle zes met een promovendus of degradant die is omgerekend, en alle zes zouden "
                "de verzwaarde LIGHT-lat van 16,0 pp hebben moeten halen om in de lijst te komen. "
                "DE KNIP LIEP DWARS DOOR EEN GELIJKSPEL, EN DAT IS GEEN TOEVAL MAAR DE MEETUITKOMST "
                "VAN §4. De laagste wedstrijd die het nog haalde is Wrexham - Wolverhampton "
                "Wanderers met datarijkdom 5,5 en 5 markten; de hoogste die afviel is Blackburn "
                "Rovers - West Ham United met datarijkdom 5,5 en 5 markten. Exact dezelfde score "
                "en exact hetzelfde aantal markten - de rangorde is daar door de aftraptijd "
                "beslist. §4 heeft op 5 september 2026 gemeten dat deze score NIET scheidt (de "
                "betkans is vlak: 29,1% op plek 1-10 tegen 30,0% op plek 31-35) en dat afkappen "
                "dus naar rato kost in plaats van een slechtere groep weg te halen. Vandaag is dat "
                "letterlijk te zien aan de knip. Het bereik in de run liep van 3,5 tot 8,0. "
                "WAT HIER NIET UIT VOLGT: de cap gaat niet omhoog. Hij is een TIJDSgrens en geen "
                "creditgrens (§0) - de rapporten moeten om 06:30 klaar staan - en de 55 is op "
                "5 september bewust zo gezet. Dat de knip door een gelijkspel liep is een reden om "
                "het op te schrijven, niet om de grens te verzetten."),

            "DE_FA_CUP_LEVERDE_EEN_GEKWALIFICEERDE_SELECTIE_OP_EN_DAT_IS_DE_OPBRENGST_VAN_ID_132": (
                "DE FA CUP SPEELDE VANDAAG MET 33 DUELS, EN ZONDER HET WERK VAN GISTEREN WAREN ZE "
                "ALLE 33 GEMIST. `ra_nov07_stage3.py` filtert de Fotmob-daglijst op de "
                "`fotmob_id`s uit `coverage.json`, en de FA Cup heeft daar geen `fotmob_id` - een "
                "beker heeft geen stand en `idcheck.py` zou er elke run een vals alarm op geven. "
                "Run A heeft op 6 november vastgesteld dat het id 132 is en het onder `notes` "
                "gezet; vanochtend is dat meteen gebruikt. "
                "TWEE BRONNEN ZIJN HET EENS OVER HET AANTAL EN DAT IS DE EIS. De Fotmob-daglijst "
                "geeft onder `primaryId` 132 drieendertig duels in het inzetvenster; BetExplorer "
                "(`/england/fa-cup/fixtures/`, 38 teamparen) geeft er drieendertig in hetzelfde "
                "venster. Zelfde aantal, zelfde ploegen, zelfde aftraptijden - en de daglijst "
                "levert bovendien match_id, ploeg-id's en de aftrap in UTC, wat een "
                "BetExplorer-rij niet geeft en wat Stage 4 en 5 wel nodig hebben. 'Niet in de "
                "daglijst' mag nooit als `GEEN WEDSTRIJD` worden opgeschreven zonder tweede bron; "
                "dat is het gat dat Run A op 6 oktober 2026 vijf duels kostte. "
                "WAT HET OPLEVERDE, EERLIJK EN MET HET VOORBEHOUD EROP. Zes van de 33 duels komen "
                "op `FULL` uit via `promotion.shared_lower_division` (§4, 15 sep 2026): Barnet - "
                "Tranmere Rovers, Gillingham - Barrow, Huddersfield Town - Exeter City, Milton "
                "Keynes Dons - Swindon Town, Newport County - Walsall en Peterborough United - "
                "Reading. Bij die zes staan BEIDE ploegen in dezelfde divisie onder de Premier "
                "League, dus er valt niets te overbruggen en het duel is daarin gewoon "
                "doorgerekend - geen omrekening, en League One en League Two hebben xG. De andere "
                "27 blijven `NONE`, en terecht: daar staan de ploegen WEL op verschillende "
                "niveaus en is juist dat niveauverschil de vraag. Een gepoolde factor erop zetten "
                "zou het gat dichten en is precies wat §2 en §4 verbieden. "
                "EEN VAN DIE ZES WERD EEN GEKWALIFICEERDE SELECTIE: Newport County - Walsall, "
                "1X2 2 (Walsall wint) @2,61, `FULL`, +8,46 pp en dus boven de lat van 8,0, alle "
                "negen poorten open. HIJ IS NIET GEPUBLICEERD - met `selection_score` 4,004 staat "
                "hij op rang 7 van 8 en er passen vijf regels in de zaterdaglijst, dus hij valt "
                "op `lijstlengte` (§5b, 26 sep 2026). Dat is geen afgewezen kandidaat maar een "
                "selectie die de lijst niet haalde, en hij is als zodanig vastgelegd. "
                "HIJ LEUNT OP HET GRATIS MARKTGEMIDDELDE, want de FA Cup heeft geen actieve "
                "sportkey (`soccer_england_fa_cup` staat niet in de 50 actieve competities van "
                "`api_check.py`). De prijs komt dus van BetExplorer en niet van de beste "
                "aanbieder, de bookmaker is niet herleidbaar, en de edge valt daar systematisch te "
                "LAAG uit (§1a: conservatief, dus geen risico op te veel bets, maar niet "
                "vergelijkbaar met een duel waar de beste prijs wel bekend is). Met een beste "
                "prijs had deze selectie hoger in de rangorde kunnen staan; dat is niet te meten "
                "zonder hem te kopen en het is dus een voorbehoud en geen correctie. Twee van de "
                "33 FA Cup-duels kregen daardoor ook geen BTTS-ronde, en dat staat in "
                "`markets_checked` als 'niet opgevraagd - geen sportkey' en niet als 'opgevraagd "
                "maar geen boek noteerde deze markt' (§1a)."),

            "POORT_5_HOUDT_VOOR_DE_DERDE_DAG_OP_RIJ_DRIEKWART_VAN_ALLE_SELECTIES_TEGEN": (
                "POORT 5 - DE BEVESTIGING DOOR EEN TWEEDE METHODE - IS VOOR DE DERDE DAG OP RIJ DE "
                "POORT DIE DE DAG BEPAALT. Van de 668 doorgerekende selecties sneuvelen er 498 op "
                "poort 5 (74,6%). Daarna komt `edge` met 62 (9,3%), `context` met 34 (5,1%), "
                "`odds` met 29 (4,3%), `robuustheid` met 17 (2,5%), `underdog` met 14 (2,1%) en "
                "`doelpunten_onder` met 1 (0,1%); 13 selecties (1,9%) halen alle poorten. "
                "DE REEKS: 6 november 149 van 186 (80,1%), 5 november alle 17 selecties van het "
                "enige analyseerbare duel, vandaag 498 van 668 (74,6%). Vandaag is de steekproef "
                "ruim drie keer zo groot als gisteren en het aandeel is vrijwel gelijk. "
                "WAT POORT 5 TOETST: de xG-methode en de splitsmethode moeten de markt DEZELFDE "
                "KANT OP verslaan (§1, poort 5). Zakt een van de twee onder de marktkans, dan "
                "wijzen ze tegengesteld en gaat de selectie eruit met reden `data conflicterend`. "
                "Dat de poort op driekwart van alle selecties dichtstaat betekent dus niet dat de "
                "selecties zwak zijn maar dat de twee kansmethodes het structureel oneens zijn "
                "over de RICHTING - en dat is iets anders dan oneens over de grootte. "
                "EN DE REM EROP, WANT DIE IS HIER ONMISBAAR. DRIE DAGEN IS GEEN REEKS. §5 "
                "waarschuwt dat een poort structureel alles kan wegvangen en noemt dat een "
                "BEVINDING, maar §6d eist ~30 afgewikkelde gevallen voordat een reeks gelezen mag "
                "worden, en de reeks die deze vraag moet beantwoorden is de SCHADUWREEKS en niet "
                "het aandeel van vandaag. Die reeks staat er en ze zegt dat de poort zijn werk "
                "doet: `tweede_methode` staat op 265 kandidaten, 256 afgewikkeld, trefkans 46,5% "
                "en een rendement van -1,0% (-2,63u). Een poort met een negatief rendement op 256 "
                "gevallen bespaart geld, en dan is 'hij hield vandaag veel tegen' geen klacht maar "
                "een beschrijving. §1f zegt het nog scherper: als KANSBRON voegt de splitsmethode "
                "vrijwel niets toe (Brier .23674 tegen .23625), als VETO bespaart ze aantoonbaar "
                "geld - en dat veto is vandaag driekwart van de run. "
                "WAT HIER NIET UIT VOLGT: er wordt vandaag geen enkele poort, drempel of gewicht "
                "verzet. Dat zou precies de fout zijn die §6d en §1g beschrijven - een anekdote "
                "van drie dagen tot regel verheffen. Wat er WEL uit volgt is dat dit de derde dag "
                "op rij is met dit aandeel, en §5 noemt dat met zoveel woorden een bevinding en "
                "geen ruis. De vraag of de twee methodes systematisch uiteenlopen hoort gesteld op "
                "de schaduwreeks, en die staat nu op een rendement rond nul over 256 gevallen - "
                "dus hij bespaart geld zonder er veel te kosten, en dat is geen aanleiding om hem "
                "te verruimen."),

            "EEN_VAN_DE_VIJF_BETS_STAAT_OP_DE_UNDER_KANT_WAAR_DE_SCHEEFSTAND_GEMETEN_IS": (
                "ROMA - SASSUOLO, UNDER 3.5 @1,9506, STAAT OP DE KANT WAARVAN DEZE REPO ZELF HEEFT "
                "GEMETEN DAT ZE SCHEEF STAAT, EN DAT HOORT ERBIJ IN PLAATS VAN ERONDER. "
                "`margins.py goalbias` meet vanochtend over 127 gespeelde Unders +0,626 doelpunt "
                "per duel MEER dan de eigen lambda zei, met z = +4,25. Gisteren stond die reeks op "
                "126 gevallen, +0,614 en z = +4,16; de Hammarby - Elfsborg van gisteren (Under 3 "
                "@1,93, uitslag 4-1, dus vijf doelpunten tegen een verwachting van 2,90) is de "
                "128e steen op die hoop en heeft hem iets harder gemaakt in plaats van zachter. "
                "Op de Over-kant gebeurt dat niet: 67 gevallen, -0,267 doelpunt, z = -1,20. "
                "DE TWEE LAGEN ERONDER (§6g). Laag 1 is een vormfout in het scoregrid die "
                "`P(Under 2.5)` over alle 2060 doorgerekende duels 2,1 pp te hoog zet en "
                "`P(Under 3/3.5)` 1,6 pp - bij elk duel, voordat er iets is gekozen. Laag 2 is het "
                "selectie-effect erbovenop: de routine speelt Under juist daar waar haar lambda te "
                "laag staat. Over het logboek kost dat `Over/Under - Under` -15,7% over 159 "
                "afgewikkelde picks, tegen +6,6% over 90 voor de Over-kant. "
                "POORT 9 STAAT EN HEEFT VANDAAG EEN SELECTIE TEGENGEHOUDEN. `unders.check` eist "
                "sinds 12 oktober 10,0 pp in plaats van 8,0 voor een Under op `FULL`-data; vandaag "
                "sneuvelde er een selectie op (`doelpunten_onder`, 1 van de 668). Roma - Sassuolo "
                "haalt die verzwaarde lat met +11,22 pp wel. De schaduwreeks `doelpunten_onder` "
                "staat nu op 35 kandidaten, alle 35 afgewikkeld, trefkans 37,1% en een rendement "
                "van -30,4%. Dat is boven de ~30 gevallen die §6d eist en het is duidelijk "
                "negatief: de rem houdt verliezers tegen en doet zijn werk. "
                "WAT HIER NIET UIT VOLGT: poort 9 wordt niet verzet, niet verzwaard en niet naar "
                "`LIGHT` uitgebreid. §1h heeft die vraag op 12 oktober gesteld en de gebruiker "
                "heeft hem beantwoord met 'twee hoeft nog niet op de zwakke data; eerst kijken wat "
                "deze rem doet', en §1h en §6g verbieden een run uitdrukkelijk de poort op eigen "
                "initiatief te verzetten. De niveaucorrectie `LEVEL_SCALE` = 1.032 van 2 november "
                "is de eerste ingreep aan de OORZAAKkant; `gridfit.py measure` zegt vanochtend dat "
                "er 84 van de 1257 homogene duels lambdas van na 3 november dragen, en dat is te "
                "weinig om te lezen (§6d). De vraag hoort dus nog niet gesteld."),

            "UNDERSTAT_VALT_VOOR_DE_ZESDE_DAG_UIT_EN_RAAKT_VANDAAG_ACHTTIEN_DUELS": (
                "DIT IS DE ENIGE BRONSTORING VAN DE RUN. `scripts/understat.py` geeft voor alle "
                "vijf zijn competities exact dezelfde fout: `UnderstatError: geen JSON terug van "
                "https://understat.com/getLeagueData/<code>/2025 (26719 bytes)`. Vijf competities, "
                "vijf verzoeken, vijf keer EXACT 26.719 bytes - dat is geen storing die voorbijgaat "
                "maar een blokkadepagina of een permanent gewijzigde route. De reeks: 1 nov HTTP "
                "502 op de CONNECT van de netwerkgateway, 3 nov `Connection reset by peer`, 4 nov "
                "26.719 bytes zonder JSON, 5 nov idem, 6 nov idem, vandaag idem. Zesde dag. "
                "WAT HET VANDAAG CONCREET KOST, en het is meer dan gisteren omdat alle vijf de "
                "competities een volle speelronde hebben. Understat dekt PL, La Liga, Bundesliga, "
                "Serie A en Ligue 1 (§4), en vandaag vallen 18 van de 52 doorgerekende duels in "
                "die vijf. Bij die 18 is er geen TWEEDE, onafhankelijk xG-model naast Fotmob. §4 "
                "noemt dat precies zo: Fotmob-xG en Fotmob-splits zijn twee doorsnedes van DEZELFDE "
                "meting, Understat is een ander xG-model. Het kalibratieblok van §6e mist daardoor "
                "zijn `p_xg_understat`-arm bij deze 18, en dat is de arm die de vraag moet "
                "beantwoorden of het ene xG-model beter voorspelt dan het andere. Drie van de vijf "
                "gepubliceerde bets staan in die vijf competities (Malaga - Racing Santander, "
                "Mainz 05 - Bayern Munchen, Roma - Sassuolo). "
                "WAT HET NIET KOST, EN DAAROM STAAT HET NIET VOORAAN IN DE NOTIFICATIE. §2 blijft "
                "gedekt: Fotmob levert en is voor vrijwel elke competitie de xG-bron, dus er is "
                "voor elk duel een onafhankelijke kansinput en geen enkel duel wordt hierdoor "
                "`NONE`. §3 (27 sep 2026) schrijft voor dat de ontbrekende statistiekensleutel pas "
                "vooraan in de notificatie hoort zodra FOTMOB niet meer levert - dan is er geen "
                "kansbron meer en levert elke run gegarandeerd nul bets. Dat is vandaag niet het "
                "geval. "
                "WAT ER WEL UIT VOLGT: de redundantie waarvoor Understat op 31 augustus is "
                "toegevoegd, is zes dagen weg. Dat is geen actiepunt voor de gebruiker (het is een "
                "bron die zichzelf dichtzet, net als fbref, Forebet, FootyStats en PredictZ - §3: "
                "niet omheen werken) maar het hoort wel geteld te worden, want als Fotmob ook "
                "omvalt is er niets meer."),

            "DE_PINNACLE_VERGELIJKING_VAN_STAP_2": (
                "STAP 2 VAN STAGE 5 - 'wat anderen voorspellen' - is vandaag ingevuld met de enige "
                "vorm die bereikbaar is: de prijs van Pinnacle apart, de-vigd, naast de eigen kans "
                "(§3 Stage 5, 20 sep 2026). Over 45 duels met zowel een Pinnacle-1X2 als een eigen "
                "1X2 is de gemiddelde absolute afstand tot het Pinnacle-oordeel 4,17 pp, bij een "
                "gemiddelde Pinnacle-marge van 3,57%. Op de doelpuntenkant: 45 (duel, lijn)-paren, "
                "gemiddeld verschil op de Under-kant -1,81 pp, en in 22 van de 45 gevallen staat "
                "het model BOVEN Pinnacle. "
                "LEES DIE -1,81 pp SAMEN MET §6g EN HET WIJST DEZELFDE KANT OP ALS VANDAAGS LIJST. "
                "Het model zit op de Under-kant gemiddeld onder het scherpste publieke oordeel, "
                "oftewel het verwacht MEER doelpunten dan Pinnacle - en dat is precies waarom er "
                "vier Overs en een Under op de lijst staan in plaats van het omgekeerde. Dat is "
                "een vergelijking en geen bevestiging: Pinnacle is scherper dan dit model (§1g, "
                "Brier markt 0,2408 tegen eigen 0,2606 over 468 bets), dus een afstand tot zijn "
                "oordeel is eerder een eigen fout dan een gevonden voordeel. "
                "HARDE GRENS §2: dit getal staat NIET in `my_prob` en NIET in `prob_sources`. Het "
                "is marktafgeleid en het is andermans lezing; het hoort in de vergelijking en niet "
                "in de kansschatting. Het staat daarom in een eigen blok in `data/run-state/`."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. BINDT VANDAAG NIET, anders dan gisteren: er zijn TWEE wedstrijden met
        # een selectie die alle negen poorten haalt EN boven haar eigen LIGHT-lat van 16,0 pp
        # staat, er zijn drie plekken (MAX_SHORTLIST = 3, donderdag), en beide worden
        # gepubliceerd. `MAX_LIGHT_IN_SHORTLIST` = 2 is daarmee tot de rand VOL — beide regels
        # staan op LIGHT — maar hij houdt niets tegen, want er is geen derde gekwalificeerde
        # selectie. Deze lus levert vandaag dus NUL rijen, en dat hoort zo.
        # Hij blijft onveranderd staan omdat hij het verschil is tussen een gemeten reeks en een
        # stille weglating zodra de grens wél bindt. Hij legt zo'n gekwalificeerde selectie vast als
        # `gekwalificeerd_niet_gepubliceerd` plus een `near_miss` met
        # `failed_gate = "lijstlengte"` — bewust dezelfde naam, ook nu de oorzaak de LIGHT-grens
        # is, zodat de populatie niet in twee reeksen uiteenvalt (§5b, 26 sep 2026: "gebruik
        # precies die naam en verzin geen tweede"). De werkelijke oorzaak staat in `reden`.
        idx_match = {m["match"]: m for m in res["matches"]}
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
            if m["match"] in gepubliceerde_duels:
                m["binnen_wedstrijd_niet_gekozen"] = {
                    "selection": pick.get("selection"), "market": pick.get("market"),
                    "odds": pick.get("odds"), "edge_pp": pick.get("edge_pp"),
                    "score": pick.get("score"),
                    "reden": ("alle negen poorten open en boven de drempel, maar een andere "
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
                "reden": (f"alle negen poorten open en {pick.get('edge_pp'):+.2f} pp boven de "
                          f"drempel, maar rang {rang} en niet in de lijst van "
                          f"{len(top['herijkt'])} regels; laagste gepubliceerde selection_score "
                          f"{drempel_score}. "
                          + (f"DE OORZAAK IS `MAX_LIGHT_IN_SHORTLIST` = 2 (§0) EN NIET DE LENGTE "
                             f"VAN DE LIJST: er passen {max_shortlist(date.fromisoformat(DAG))} "
                             f"regels in en er staan er {len(top['herijkt'])}, maar alle "
                             f"gekwalificeerde selecties van vandaag staan op LIGHT en daar mogen "
                             f"er maar twee van in de lijst. `failed_gate` blijft `lijstlengte`, "
                             f"omdat §5b (26 sep 2026) verbiedt hiervoor een tweede naam te "
                             f"verzinnen - het is een vraag en twee namen zouden een populatie "
                             f"splitsen waarna geen van beide ooit de ~30 afgewikkelde gevallen "
                             f"van §6d haalt."
                             if len(top['herijkt']) < max_shortlist(date.fromisoformat(DAG))
                             else ""))}
            buiten += 1
        print(f"{buiten} gekwalificeerde selectie(s) buiten de lijst van §5b")

        # `MAX_LIGHT_IN_SHORTLIST` = 2 BINDT VANDAAG, en de weggevallen regel staat ONDER haar
        # eigen lat. Dat is NIET het geval van §5b van 26 september (dat gaat uitdrukkelijk over
        # selecties BOVEN de drempel, "geen afgewezen kandidaat: er is geen enkele poort die haar
        # heeft tegengehouden"), dus er komt hier GEEN `gekwalificeerd_niet_gepubliceerd` en GEEN
        # `near_miss` met `failed_gate = "lijstlengte"`. De selectie sneuvelt op `edge` en komt in
        # die schaduwreeks terecht; haar in `lijstlengte` zetten zou twee populaties optellen die
        # twee verschillende vragen beantwoorden ("te weinig voordeel" tegen "genoeg voordeel,
        # maar anderen hadden meer").
        #
        # Hij wordt wel VASTGELEGD, in een eigen veld, want anders is van buitenaf niet te zien
        # dat de lijst drie regels heeft omdat een grens bond en niet omdat er niets meer was.
        # Dat onderscheid is precies wat §5 en §6b-5b eisen: geen stille weglating.
        zonder_light = toplist.build({**st, "run": "C"},
                                     n=max_shortlist(date.fromisoformat(DAG)))["herijkt"]
        in_lijst = {(r["match"], r["market"], r["selection"]) for r in top["herijkt"]}
        geblokt = [r for r in zonder_light if (r["match"], r["market"], r["selection"]) not in in_lijst]
        for r in geblokt:
            m = idx_match[r["match"]]
            m["max_light_geblokkeerd"] = {
                "market": r["market"], "selection": r["selection"], "odds": r["odds"],
                "tier": r["tier"], "edge_pp": r["edge_pp"], "score": r["score"],
                "rang_zonder_de_grens": zonder_light.index(r) + 1,
                "failed_gate": r.get("failed_gate"),
                "reden": (
                    f"`MAX_LIGHT_IN_SHORTLIST` = 2 is vol (de lijst heeft "
                    f"{sum(1 for x in top['herijkt'] if x['tier'] != 'FULL')} LIGHT-regels van de "
                    f"{len(top['herijkt'])}) en deze selectie zou als nummer "
                    f"{zonder_light.index(r) + 1} in de rangorde staan. Er passen "
                    f"{max_shortlist(date.fromisoformat(DAG))} regels in de lijst, dus het is de "
                    f"LIGHT-grens die hem tegenhoudt en niet de lengte. "
                    f"GEEN `lijstlengte`-rij: deze selectie haalt haar eigen lat NIET "
                    f"({r['edge_pp']:+.2f} pp tegen 16,0) en sneuvelt op `{r.get('failed_gate')}`, "
                    f"terwijl §5b (26 sep 2026) `lijstlengte` reserveert voor selecties die alle "
                    f"poorten EN hun drempel halen. Twee namen voor een vraag zijn verboden, maar "
                    f"een naam voor twee vragen net zo goed."),
            }
            print(f"max_light_geblokkeerd: {r['match']} {r['market']} — {r['selection']} "
                  f"({r['edge_pp']:+.2f} pp, rang {zonder_light.index(r) + 1})")
        if not geblokt:
            print("MAX_LIGHT_IN_SHORTLIST houdt vandaag niets tegen")

        for comp, blok in st["competitions"].items():
            entry = {"status": "GEANALYSEERD", "matches": []}
            for m in blok["matches"]:
                e = dict(m)
                sleutel_bet = any((m["match"], mk, se) in gespeeld
                                  for mk, se in [(c["market"], c["selection"])
                                                 for c in m.get("all_candidates", [])])
                # §6d/§1a: is er op dit duel gepubliceerd, dan is een andere selectie van
                # dezelfde wedstrijd dezelfde mening en geen afgewezen kandidaat.
                nm = m.get("near_miss")
                if nm and any(mm == m["match"] for mm, _, _ in gespeeld):
                    e["near_miss_gepubliceerd"] = e.pop("near_miss")
                e["bet"] = sleutel_bet
                entry["matches"].append(e)
            mark(state, comp, entry)

        # Dekkingstabel: óók de competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/ra_nov07_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_nov07_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_nov07_cups.json"))["cups"]
        for comp, v in cups.items():
            if comp in state["competitions"]:
                continue
            bxv = v.get("betexplorer") or {}
            mark(state, comp, {"status": v["status"], "matches": [],
                               "bron": v.get("bron", "BetExplorer (§5)") + " + BetExplorer",
                               "eerstvolgende_ronde": bxv.get("eerste_ronde"),
                               "teamparen_op_de_fixturepagina": bxv.get("teamparen")})

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
        for run, pad in (("A", "tmp-run/ra_nov07_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_nov07_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_nov07_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

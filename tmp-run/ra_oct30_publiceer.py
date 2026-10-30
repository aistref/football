"""Run A 30 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct28_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. NEGEN van de eenentwintig competities uit de runlijst speelden, met TWAALF duels in het
inzetvenster: een vrijdagavond met de vooruitgeschoven duels van La Liga, de Bundesliga, de
Championship, de Primeira Liga, de Belgian Pro League, de Super Lig en de Danish Superliga, drie
Ligue 1-duels (het is daar een volledige vrijdagronde) en twee in de Ekstraklasa. Geen beker heeft
een ronde en geen Europees toernooi speelt.

VIER REGELS, WAARVAN ER EEN ZIJN LAT ONDUBBELZINNIG HAALT. De tweede staat op 0,00085 procentpunt
van de drempel en de twee rekenstappen zijn het over zijn label oneens — zie
HET_LABEL_VAN_LILLE_LENS_IS_EEN_AFRONDINGSGRENS_EN_GEEN_MENINGSVERSCHIL. De derde en vierde staan
op de Under-kant, onder de lat, en zijn door geen van beide latten getoetst; dat is de bevinding
van deze run en ze staat in TWEE_VAN_DE_VIER_REGELS_STAAN_OP_DE_UNDER_KANT_EN_DAT_IS_DE_SCHEVE_KANT.

DE RUN VAN 29 OKTOBER IS NIET GEDRAAID. Stage 0 had daardoor twee dagen open staan: zes picks en
38 schaduwrijen van 28 oktober, vanmorgen afgewikkeld.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-30"
NL = ZoneInfo("Europe/Amsterdam")   # wintertijd sinds 25 okt 2026 (+01:00)
CAPTURED = "2026-10-30T07:40:00+01:00"      # uitleestijd van de prijzen (bulk + BetExplorer), werkelijke klok (wintertijd)


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
                      + ("ONDER-KANT: §6g meet dat P(Under) bij élk duel ongeveer twee procentpunt "
                         "te hoog staat door een vormfout in score_grid (gemeten vandaag over "
                         "1752 doorgerekende duels: P(Under 2.5) voorspeld 42,5% tegen werkelijk "
                         "40,3%, en massa verschoven van 2 doelpunten naar 4 en 5), en dat de "
                         "gespeelde Under-kant daar bovenop een selectie-effect heeft van +0,609 "
                         "doelpunt per duel over 107 gevallen (z = +3,81), terwijl de Over-kant op "
                         "-0,296 staat (z = -1,25 over 60 gevallen). Dit duel staat op FULL, dus "
                         "poort 9 (§1h) kan hier bijten; of hij dat werkelijk doet hangt af van "
                         "de band waarin de edge valt — hij bindt ALLEEN tussen 8,0 en 10,0 pp, "
                         "en laat een Under daaronder met opzet door omdat `edge` daar de "
                         "bindende poort hoort te zijn. Dat is de rem die er is; de oorzaak — "
                         "keuze (a) van 11 oktober — is op 28 oktober gemeten en AFGEWEZEN (§6g: "
                         "de voorgeschreven correctie verergert het symptoom en de vormfout bleek "
                         "grotendeels een nalatenschap van shrink = 0.80, op 19 sep opgelost). "
                         "Trek dus ongeveer twee procentpunt van de genoemde kans af voordat je "
                         "haar leest. "
                         if onder else "")
                      # `bet_beide = False` heeft TWEE oorzaken en ze zijn niet hetzelfde: de lat
                      # op geen van beide schalen halen, of hem ruw wél en herijkt niet halen.
                      # Tot vandaag stond hier één tekst voor beide, en bij Lille – Lens (ruw
                      # +8,37 pp, herijkt +7,99915 pp) was die tekst onwaar.
                      + ("" if cand.get("bet_beide") else
                         (f"bet_beide = FALSE, maar alleen op de HERIJKTE schaal: ruw haalt deze "
                          f"selectie haar lat met {cand.get('edge_raw')} pp wél en herijkt met "
                          f"{cand.get('edge_pp')} pp niet. Dat is de reeks `herijking` van §5a, "
                          f"en de rij is hier geen schaduwpick maar een gepubliceerde bet omdat "
                          f"de rangorde van §5b erover gaat. "
                          if cand.get("bet_ruw") else
                          "bet_beide = FALSE: deze selectie haalt haar lat op GEEN van beide "
                          "schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel "
                          "(§5b). "))),
        })
    return st, top, picks, res


def wegschrijven():
    """Picks, run-state en het opruimen van schaduwrijen die nu echte bets zijn."""
    from scripts.progress import load_or_start, mark, save
    alle_picks = []
    for run, pad in (("A", "tmp-run/ra_oct30_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "VIER_REGELS_WAARVAN_EEN_ZIJN_LAT_HAALT_EN_DRIE_OP_RANGORDE_STAAN": (
                "De dagranglijst van §5b heeft VIER regels en `MAX_SHORTLIST` is 5 (vrijdag), dus "
                "de lijstlengte bindt NIET: er valt geen gekwalificeerde selectie buiten de lijst "
                "en `failed_gate = lijstlengte` krijgt vandaag geen enkele rij. Van de vier haalt "
                "er EEN de lat van 8,0 pp ondubbelzinnig: Nice - Rennes, Over 2.5 @1,67 (+8,74 pp, "
                "score 5,997). De tweede regel staat EXACT OP DE GRENS en dat hoort hier met het "
                "onafgeronde getal te staan in plaats van met het afgeronde: Lille - Lens, Over "
                "2.5 @1,94 komt op de herijkte schaal op +7,99915 pp uit en haalt de lat dus met "
                "0,00085 procentpunt NIET, terwijl hij op de ruwe schaal met +8,37 pp wel haalt. "
                "`ra_oct30_analyze.py` toetst op de onafgeronde waarde en geeft hem daarom "
                "`failed_gate = herijking`; `scripts/toplist.py` rangschikt op de afgeronde 8,00 "
                "en noemt hem in zijn `status` 'haalt ook de lat'. BEIDE ZIJN VERDEDIGBAAR EN ZE "
                "SPREKEN ELKAAR TEGEN — zie HET_LABEL_VAN_LILLE_LENS_IS_EEN_AFRONDINGSGRENS. Voor "
                "de publicatie maakt het niets uit: onder §5b bepaalt de rangorde de lijst en hij "
                "staat tweede van vier op een lijst die vijf plekken heeft. De derde en vierde "
                "regel staan ONDER de lat en zijn op rangorde gepubliceerd: Le Havre - Paris "
                "Saint-Germain, Under 2.5 @3,10 (+7,07 pp, score 2,781) en Zulte Waregem - Club "
                "Brugge, Under 3.25 @2,01 (+3,29 pp, score 1,745). Lees die lijst als 'dit is het "
                "beste van vandaag' en niet als 'dit is een gevonden voordeel': §1g heeft op 552 "
                "afgerekende gevallen gemeten dat er GEEN drempel op de herijkte edge bestaat die "
                "geld oplevert, en het logboek staat vandaag op -8,0% over 422 bets."),
            "HET_LABEL_VAN_LILLE_LENS_IS_EEN_AFRONDINGSGRENS_EN_GEEN_MENINGSVERSCHIL": (
                "Dit hoort opgeschreven omdat het anders over een maand als een fout wordt "
                "gelezen. De poortcontrole in `ra_oct30_analyze.py` vergelijkt `e_pp >= thresh` op "
                "de volledige float (7,99915 < 8,0, dus dicht) en `toplist.py` leest het veld "
                "`edge_pp` uit `all_candidates`, dat met `round(..., 2)` is weggeschreven (8,0, "
                "dus open). Het verschil is 0,00085 procentpunt en het raakt uitsluitend het "
                "LABEL in het dagrapport, niet welke regels er worden gepubliceerd. §0 zegt zelf "
                "dat de 8,0 'de eerste waarde waarbij het teken omslaat' is en geen optimum, dus "
                "een duizendste procentpunt is geen grootheid waarop iets hoort te hangen. "
                "GEEN WIJZIGING VANDAAG: een run verzet geen vergelijking in de rekencode op een "
                "randgeval van één dag (§6d). Het staat als openstaand punt in het runrapport, "
                "met de aantekening dat de nette oplossing is dat beide stappen dezelfde "
                "afgeronde waarde gebruiken en niet dat de drempel verschuift."),
            "TWEE_VAN_DE_VIER_REGELS_STAAN_OP_DE_UNDER_KANT_EN_DAT_IS_DE_SCHEVE_KANT": (
                "Le Havre - PSG (Under 2.5 @3,10) en Zulte Waregem - Club Brugge (Under 3.25 "
                "@2,01) staan beide op de kant waarvan §6g meet dat ze structureel te hoog wordt "
                "ingeschat, en BEIDE zijn op rangorde gepubliceerd zonder door een van de twee "
                "latten te zijn getoetst. Vandaag gemeten over 1752 doorgerekende duels: het "
                "GEMIDDELDE aantal doelpunten klopt (voorspeld 3,031 tegen werkelijk 3,072, "
                "z = +0,99) maar de VERDELING niet — massa verschoven van 2 doelpunten (-1,4 pp) "
                "naar 4 (+1,1) en 5 (+1,4), waardoor P(Under 2.5) 2,2 pp en P(Under 3.0) 1,8 pp "
                "te hoog staat bij ELK duel, vóór er iets is gekozen. Daar bovenop het "
                "selectie-effect: in de 107 duels waarin de routine werkelijk een Under speelde "
                "vielen er +0,609 doelpunt per duel méér dan haar eigen lambda zei, z = +3,81. "
                "Op de Over-kant gebeurt dat niet (-0,296 over 60, z = -1,25). TREK DUS ONGEVEER "
                "TWEE PROCENTPUNT VAN DE GENOEMDE KANS AF, en dan blijft er van de +3,29 pp van "
                "Zulte Waregem vrijwel niets over. De rem die er is, is poort 9, en die bindt hier "
                "met opzet niet (zie POORT_9). De oorzaak — keuze (a) van 11 oktober — is op "
                "28 oktober gemeten en AFGEWEZEN: de voorgeschreven vormcorrectie verergert het "
                "symptoom en de vormfout blijkt grotendeels een nalatenschap van `shrink = 0.80` "
                "die op 19 september al is opgelost. Zie §6g; lees het uitblijven van die trigger "
                "niet als openstaande taak."),
            "POORT_9_HIELD_DE_3_5_VAN_LE_HAVRE_TEGEN_EN_LIET_DE_2_5_VAN_DEZELFDE_WEDSTRIJD_DOOR": (
                "Dat ziet eruit als een tegenstrijdigheid en het is er geen. Poort 9 (§1h) hield "
                "vandaag EEN selectie tegen: Le Havre - PSG, Under 3.5 @1,92 met +9,01 pp tegen de "
                "verzwaarde lat van 10,0 pp. Die gaat als `failed_gate = doelpunten_onder` naar "
                "het schaduwlogboek. De GEPUBLICEERDE Under van diezelfde wedstrijd staat op de "
                "2.5-lijn met +7,07 pp en is door poort 9 HEENGEKOMEN, omdat `unders.check` met "
                "opzet alleen in de band 8,0-10,0 pp bindt: een Under die de gewone drempel van §0 "
                "al niet haalt wordt door `edge` tegengehouden en niet hierdoor, want anders loopt "
                "de reeks `doelpunten_onder` vol met kandidaten die nooit een bet konden worden en "
                "meet ze niets meer (de 'twee populaties'-fout van §1e). Sinds §5b de drempel van "
                "een poort in een afkapping heeft veranderd, betekent dat echter dat een Under "
                "ONDER de 8,0 wél gepubliceerd kan worden en door geen van beide latten wordt "
                "getoetst — en vandaag gebeurt dat TWEE keer in plaats van één. DAT IS GEEN "
                "OMISSIE VAN VANDAAG MAAR HET GEVOLG VAN TWEE REGELS DIE ELKAAR RAKEN, en het is "
                "dezelfde constructie die §1h punt 1 bij `LIGHT` expliciet heeft gekozen. Het is "
                "op 28 oktober als besluit aan de gebruiker voorgelegd en dat punt staat nog "
                "open; het wordt vandaag niet opnieuw als nieuwe vraag gesteld (§1h, 12 okt: stel "
                "hem niet elke dag opnieuw), maar de stand van de reeks staat in het runrapport: "
                "`doelpunten_onder` 24 afgewikkelde gevallen, -13,1%."),
            "POORT_8_HIELD_TWEE_WEDSTRIJDEN_TEGEN_EN_POORT_8_RUW_GEEN_ENKELE": (
                "Poort 8 bindt in de lichte vorm (ondergrens `sides.UNDERDOG_FLOOR` = 0,35, §1e) "
                "en is met `today=DAY` aangeroepen, zodat het venster van 25 t/m 30 september uit "
                "`sides.LAPSED_FROM`/`LAPSED_UNTIL` wordt gelezen in plaats van geraden. Hij hield "
                "vandaag ZES selecties tegen, verdeeld over twee wedstrijden: Le Havre - PSG (de "
                "sterkste is Le Havre +1.5 @2,09, +12,98 pp; de markt geeft Le Havre 10,7% tegen "
                "73,6% voor PSG) en Zulte Waregem - Club Brugge (Zulte-Waregem +1.25 @2,04, "
                "+6,65 pp; 14,0% tegen 66,7%). DIT IS DE DUURSTE POORT VAN DE DAG: de "
                "Le Havre-handicap voert de RUWE dagranglijst aan met score 8,184 — hoger dan "
                "elke gepubliceerde regel — en is dus de selectie die het model vandaag het "
                "sterkst vindt. Dat is precies het geval waarvoor de poort is gebouwd: §1e meet "
                "over 89 gevallen dat de routine op de underdog-kant 47,1 winnaars verwachtte, de "
                "markt 38,0, en het 33,0 werden (z = -3,14). De tweede schaal, `underdog_ruw`, "
                "krijgt vandaag GEEN ENKELE rij: er is geen selectie die op de ruwe kans alle "
                "eerdere poorten haalde en alleen op poort 8 sneuvelde. Dat is bij een herijking "
                "die vrijwel de identiteit is (a=0,985, b=-0,010) te verwachten. Tel die twee "
                "reeksen nooit bij elkaar op; het zijn twee populaties — `underdog` staat op 251 "
                "afgewikkelde gevallen en -2,8%, `underdog_ruw` op 17 en -8,8%."),
            "TWEEDE_METHODE_VANGT_123_VAN_DE_159_SELECTIES_EN_DAT_IS_EEN_WAARNEMING": (
                "Over de 12 wedstrijden zijn 159 selecties doorgerekend. De verdeling over de "
                "poorten: `tweede_methode` 123, `edge` 11, `odds` 8, `context` 6, `underdog` 6, "
                "`doelpunten_onder` 1, `robuustheid` 1, `herijking` 1, en 2 selecties haalden "
                "alles. DAT EERSTE GETAL IS GEEN DETAIL: poort 5 vangt 77% van alles wat er "
                "doorgerekend wordt, net als gisteren (78%), en §5 zegt met zoveel woorden dat "
                "als er een week lang alles op `tweede_methode` afvalt, de vraag is of de twee "
                "methodes systematisch uiteenlopen — en dat is een bevinding en geen ruis. Wat er "
                "tegenover staat: §1f heeft op 392 afgerekende gevallen gemeten dat de "
                "splitsmethode als KANSBRON vrijwel niets toevoegt (Brier .23625 bij gewicht 0,80 "
                "tegen .23674 voor alleen xG) en dat haar waarde juist in dit veto zit, dat "
                "aantoonbaar geld bespaart: `tweede_methode` staat op -8,4% over 219 afgewikkelde "
                "gevallen. Noem het getal dus, lees het over weken en niet vandaag, en verzet er "
                "niets op. Opvallend vandaag: bij Lille - Lens vielen alle selecties BEHALVE de "
                "gepubliceerde Over hierop af, en de splitsmethode staat daar op slechts +3,20 pp "
                "tegen +9,66 pp voor de xG-methode — de twee methodes wijzen dezelfde kant op maar "
                "liggen ver uiteen, en dat is precies waarom die regel op de grens staat."),
            "CONTEXT_HIELD_TWEE_WEDSTRIJDEN_TEGEN_EEN_OP_BLESSURES_EN_EEN_OP_RUST": (
                "Poort 7 (§1c) sloot bij twee duels. VILLARREAL - ESPANYOL op het "
                "beschikbaarheidsverschil: Villarreal mist 28% van de selectiewaarde tegen 6% bij "
                "Espanyol — Nathan Saliba (blessure, terug begin november), Pape Gueye (schorsing, "
                "terug eind oktober) en Ilias Akhomach (blessure, terug half november). GORNIK "
                "ZABRZE - LEGIA WARSZAWA op rust: Górnik had 3 dagen tegen 5 bij Legia, en dat is "
                "precies het criterium (ten hoogste 4 dagen rust én minstens 2 dagen minder dan de "
                "tegenstander). Die tweede is duur: de Górnik-thuiszege @2,16 staat vijfde op de "
                "RUWE dagranglijst. De poort houdt alleen tegen en stelt `my_prob` niet bij, want "
                "er is geen enkele meting die zegt hoeveel procentpunt een uitvaller of een "
                "rustdag waard is (§1c; de poging om er een bijstelling van te maken vond op 147 "
                "wedstrijden niets, en het contextlogboek staat vandaag op 1739 duels met "
                "r = -0,044 en t = -1,70 — nog steeds niets). De volledige context van alle 12 "
                "duels staat in het `context`-blok, ook van de duels waar de poort openging: dat "
                "is wat §1c eist en het is de steekproef van `ctxlog.py`. `context` staat in het "
                "schaduwlogboek op -26,6% over 98 gevallen; dat is de poort die het meeste geld "
                "bespaart."),
            "GEEN_VERPLAATSTE_WEDSTRIJD_VANDAAG": (
                "`context.check_venue` zette vandaag bij geen van de 12 duels `relocated`: elk "
                "duel staat in het eigen stadion van de genoteerde thuisploeg. §1c eist dat een "
                "verplaatsing wordt genoemd ook als de poort opengaat; vandaag is er niets te "
                "noemen, en dat is ook een uitkomst. Wat deze controle NIET vangt blijft hetzelfde: "
                "een fixture die van eigenaar is gewisseld, want dat is nieuws en geen data (de "
                "Rennes - PSG-les van 23 augustus). Twee stadions zijn het vermelden waard zonder "
                "dat ze een verplaatsing zijn: Casa Pia speelt vast in het Estádio Municipal de "
                "Rio Maior, ruim 70 km van Lissabon, omdat de eigen Pina Manique niet aan de "
                "competitie-eisen voldoet — dat is hun thuisveld en zo is het ook genoteerd; en "
                "Lille speelt in de Decathlon Arena in Villeneuve-d'Ascq, eveneens hun eigen grond."),
            "TWEE_PROMOVENDI_EN_BEIDE_OP_LIGHT": (
                "TIEN duels komen op FULL uit en TWEE op LIGHT, en die twee zijn promovendi die "
                "via `scripts/promotion.py` uit de divisie eronder zijn omgerekend (§4): "
                "ELVERSBERG, dat deze zomer naar de Bundesliga promoveerde en wordt omgerekend uit "
                "de 2. Bundesliga, en LYNGBY, promovendus in de Danish Superliga uit de NordicBet "
                "Liga. Een omgerekende ploeg is per regel NOOIT FULL — de omrekening haalt de "
                "systematische fout eruit en niet de onzekerheid — dus hun lat is 16,0 pp in plaats "
                "van 8,0, en geen van beide komt in de buurt. GEEN enkel duel komt vandaag op NONE "
                "uit, en geen enkele selectie valt op `promotion.conversion_in_range`: beide "
                "omrekeningen vallen binnen het gemeten invoerbereik. Lees de stand van de "
                "divisiefactor per selectie uit `GapResult.direction` en niet uit een "
                "samenvattende zin (§4, 9 okt 2026): voor Duitsland en Denemarken staat daar een "
                "eigen meting en geen `POOLED_GAP`."),
            "MARKTBALANS_NEGEN_VAN_DE_NEGEN_COMPETITIES_KREGEN_DE_VOLLEDIGE_BULK": (
                "De marktbalans-controle van §1a is gehaald op de INKOOP en niet op de uitkomst, "
                "en zo ruim als ze kan: van de negen competities die vandaag spelen hebben ALLE "
                "NEGEN een sportkey en kregen alle negen de volledige bulk (h2h + spreads + "
                "totals, 3 credits per competitie) — dus elke gekochte competitie heeft zowel een "
                "uitkomstmarkt (1X2, AH, DNB, DC) als een doelpuntenmarkt (O/U), en geen enkel "
                "duel draait op het gratis BetExplorer-marktgemiddelde voor de bet zelf. Plafond "
                "`suggest_cap(18579, 2)` = 4639 credits, `split_budget(4639, 9)` = 9 spreads / "
                "9 totals, werkelijk verbruikt 27 credits voor de bulk plus 5 voor BTTS = 32 van "
                "4639, en er staan nog 18547 credits van het maandplafond van 20000 open. BTTS is "
                "gekocht voor 5 van de 12 duels met een kandidaat-edge (§1a stap 2, de vereniging "
                "van beide schalen sinds 13 sep); de andere zeven staan in `markets_checked` als "
                "'niet opgevraagd — geen kandidaat-edge in dit duel' en niet als 'geen boek "
                "noteerde deze markt'. ALLE TWAALF DUELS HEBBEN EEN BESTE PRIJS met een "
                "herleidbare bookmaker; de winst ten opzichte van het marktgemiddelde ligt tussen "
                "+4,60% en +8,98% met een gemiddelde van +6,55%, wat volgens §1a ongeveer "
                "anderhalve procentpunt edge per selectie is. Wat eruit kwam: over 159 "
                "doorgerekende selecties 56 Over/Under, 45 Asian Handicap, 31 1X2, 11 Draw No Bet, "
                "10 BTTS en 6 Double Chance, en alle VIER de gepubliceerde regels zijn een "
                "Over/Under. DAT IS EENZIJDIG EN HET IS GEEN INKOOPARTEFACT: alle zes markten "
                "dongen in elk duel mee en de uitkomstmarkten vielen op poort 5 en poort 8 af. "
                "Het is de uitkomst, en bets forceren om een verdeling te halen is precies wat §1 "
                "verbiedt — maar het is wel het soort eentonigheid waar de gebruiker op "
                "19 september over viel, en het hoort daarom hier te staan."),
            "WAT_ANDEREN_VOORSPELLEN_PINNACLE_IS_HET_TEGEN_ALLE_VIER_DE_REGELS_ONEENS": (
                "Stage 5 stap 2, in de enige vorm die bereikbaar is (§3 Stage 5 heeft op 20 sep "
                "gemeten dat geschreven voorspellingen vrijwel niet te halen zijn: Forebet 403, "
                "Pinnacle-artikelen 404, Matchbook 530). Wat er wél is, is de PRIJS VAN PINNACLE "
                "APART: de scherpste bookmaker van de markt, en zijn de-vigde prijs is het beste "
                "publieke expertoordeel dat beschikbaar is. Over 12 duels: gemiddelde absolute "
                "afstand op 1X2 3,03 procentpunt, gemiddelde Pinnacle-marge 3,74% (tegen 6 à 10% "
                "bij de rest). Op de doelpuntenkant staat het eigen model gemiddeld -0,32 pp "
                "ONDER Pinnacle op de Under-kant, 7 van de 12 keer erboven. DE VIER "
                "GEPUBLICEERDE REGELS ZIJN PRECIES DE VIER DUELS WAAR DE AFSTAND TOT PINNACLE HET "
                "GROOTST IS, en alle vier de verkeerde kant op: bij Nice - Rennes zet Pinnacle "
                "P(Under 3.0) op 52,8% en het eigen model op 44,0% (8,8 pp meer Over); bij Lille - "
                "Lens P(Under 2.5) op 49,6% tegen 38,8% eigen (10,8 pp meer Over); bij Le Havre - "
                "PSG P(Under 3.5) op 52,2% tegen 58,6% eigen (6,4 pp meer Under); bij Zulte "
                "Waregem - Club Brugge P(Under 3.25) op 48,1% tegen 51,9% eigen (3,9 pp meer "
                "Under). LEES DAT ALS EEN WAARSCHUWING EN NIET ALS EEN BEVESTIGING: §1g meet dat "
                "de bookmaker scherper schat dan het model (Brier 0,2398 voor de markt tegen "
                "0,2603 eigen over 422 afgerekende bets), dus de grootste afstand tot Pinnacle is "
                "eerder de grootste modelfout dan de grootste vondst. Op het 1X2 is de grootste "
                "afstand Le Havre - PSG (11,7 pp: het model geeft PSG 62,0% waar Pinnacle 73,7% "
                "zegt) — dezelfde wedstrijd die de duurste poort-8-blokkade van de dag levert, en "
                "dat is geen toeval maar hetzelfde verschijnsel van twee kanten gezien. HARDE "
                "GRENS: niets hiervan gaat in `my_prob` of in `prob_sources` (§2); het staat in de "
                "lezing en in de vergelijking."),
            "DE_RUN_VAN_29_OKTOBER_IS_NIET_GEDRAAID_EN_STAGE_0_HAD_TWEE_DAGEN_OPEN_STAAN": (
                "Er is geen `runs/2026-10-29-run-*.md` en geen `data/run-state/2026-10-29-*.json`: "
                "de geplande taken van 29 oktober zijn niet afgegaan. Gevolg voor Stage 0: de ZES "
                "picks en 38 schaduwrijen van 28 oktober stonden twee dagen open in plaats van "
                "één, en zijn vanmorgen afgewikkeld. VIJF VAN DE ZES PICKS GEWONNEN (Bournemouth "
                "wint 3-0 van Aston Villa, St. Mirren - Hibernian 1-1 onder de 3, Santos - "
                "Palmeiras 0-0 onder de 2.5, Toronto - DC United 2-1 en New York City - Atlanta "
                "2-1 beide onder de 3.5); verloren is Hannover 96 -0,25 tegen Kaiserslautern, dat "
                "met 0-2 onderuit ging. De twee bekerduels in die reeks (EFL Cup, DFB Pokal) "
                "meldden beide `reason = Full-Time`, dus de eindstand IS de stand na 90 minuten en "
                "§6d is niet geschonden. De schaduwrijen gingen 21 gewonnen / 17 verloren. "
                "WAAROM DIT HIER STAAT: §7 noemt een uitgebleven notificatie zelf het signaal dat "
                "er iets stuk is, en een gemiste dag hoort daarom in het logboek en in de "
                "notificatie — niet stil te worden ingehaald. Wat er NIET is gebeurd: de "
                "wedstrijden van 29 oktober zijn niet achteraf geanalyseerd. Dat kan ook niet, "
                "want het inzetvenster van die dag is voorbij en een pick met terugwerkende kracht "
                "is geen pick (§5b, dezelfde redenering waarom poort 8 op 1 oktober inging en niet "
                "op 30 september)."),
            "HERIJKING": (
                "§1g, één fit per run uit data/calibration.jsonl: a=0,985, b=-0,010 op 6252 "
                "afgerekende gevallen t/m 2026-10-28 — het ruwe model zei gemiddeld 33,3% en het "
                "gebeurde 33,3%. `fitted_through` staat op 2026-10-28 en dat is de vórige RUNDAG "
                "(29 oktober is niet gedraaid), zoals §6b-5c eist; de 135 waarnemingen die nog "
                "open stonden zijn vanmorgen door `calibration.py settle` afgewikkeld voordat de "
                "fit is gelezen. De correctie VERLAAGT vandaag over vrijwel de hele speelbare "
                "band, maar nauwelijks: +0,1 pp op 30%, -0,2 pp op 50%, -0,5 pp op 70%. Gevolg "
                "voor §5a: bij Nice - Rennes staat `bet_beide = true` (+8,74 pp herijkt tegen "
                "+9,20 ruw), bij de andere drie staat hij op `false` — bij Lille - Lens omdat de "
                "herijking hem 0,00085 pp onder de lat duwt en bij de twee Unders omdat ze hun lat "
                "op geen van beide schalen halen. Vertrouw die vlag en niet de redenering: §5a "
                "waarschuwt daar uitdrukkelijk voor, omdat de fit elke run een ander getal is."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "De eenentwintig competities van `prompts/run-a.md`, ongewijzigd: dertien "
                "competities en acht toernooien. NEGEN hebben vandaag een duel in het venster (La "
                "Liga, Bundesliga, Ligue 1, Championship, Primeira Liga, Belgian Pro League, Super "
                "Lig, Danish Superliga, Ekstraklasa), TWAALF niet. De Premier League, Serie A, "
                "Eredivisie en Scottish Premiership spelen in het weekend; de drie Europese "
                "toernooien 3 t/m 5 november; de FA Cup 6 november, de League Cup 14 december en "
                "de Coppa Italia 1 december; de KNVB Beker en de DFB Pokal hebben geen ronde op de "
                "fixturepagina. Dat is GEEN WEDSTRIJD en geen storing (§3 Stage 2). De Fotmob-id's "
                "komen uit `data/coverage.json` en zijn deze run alle 33 groen bevonden door "
                "`scripts/idcheck.py`."),
            "GEEN_AFKAPPING_EN_GEEN_ONSPEELBAAR_DUEL": (
                "TWAALF duels in het inzetvenster tegen een cap van 55 (vrijdag), dus "
                "`MAX_DEEP_ANALYSES` bindt niet en er is niets afgekapt — stille truncatie is "
                "verboden (§3 Stage 4) en er valt vandaag niets te melden. De datarijkdom liep van "
                "5,0 (Zulte Waregem - Club Brugge en Górnik - Legia) tot 8,0 (Villarreal - "
                "Espanyol); omdat er niets afvalt zijn 'de laagste die het haalde' en 'de hoogste "
                "die afviel' allebei leeg. Alle twaalf duels komen van de daglijst van de rundag "
                "zelf (`source_day = 2026-10-30`), alle twaalf staan op `playable = True` — de "
                "vroegste aftrap is 18:00 NL — en er is geen carry-over-band. `runwindow` rekent "
                "met `zoneinfo`, dus het venster is in échte NL-tijd gemeten: nu de wintertijd in "
                "is, komt een aftrap van 20:00 UTC op 21:00 NL uit (CET) en niet op 22:00 (CEST). "
                "Dat is de reparatie van 25 oktober; `ra_oct30_analyze.py` en dit bestand gebruiken "
                "allebei ZoneInfo('Europe/Amsterdam') en `odds_captured_at` staat op +01:00."),
            "BRONSTATUS_EN_DE_BEVESTIGING_DOOR_EEN_TWEEDE_METHODE": (
                "`api_check.py` van deze run: The Odds API OK met 18579 credits over en 1421 "
                "verbruikt deze maand, 47 actieve voetbalcompetities, en 32 van de 34 sportkeys "
                "van de repo vandaag actief (Coppa Italia en DFB Pokal niet — die hebben geen "
                "ronde). `API_FOOTBALL_KEY` ontbreekt en dat is een BESLUIT van de gebruiker van "
                "27 september 2026 en geen gat: de kanskant komt van Fotmob (alle competities) en "
                "Understat (vijf, waarvan er vandaag drie spelen). Geen sleutel is afgewezen. "
                "DE DAG IS MET TWEE METHODES VASTGESTELD (§1): `ra_oct30_bevestiging.py` legt de "
                "Fotmob-daglijst naast de BetExplorer-fixturepagina's en ze zijn het over ALLE 16 "
                "competities eens — 12 duels tegen 12 — dus er is geen competitie waar de ene "
                "bron een wedstrijd ziet en de andere niet. Dat is precies de poort waar de "
                "duurste fouten van oktober zaten: in de vraag wélke wedstrijden er zijn, niet in "
                "de analyse. De vier bekers zonder ronde zijn bij BetExplorer nagetrokken en niet "
                "uit de daglijst geconcludeerd."),
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag NIET: er zijn VIER publiceerbare selecties en vijf
        # plekken beschikbaar (MAX_SHORTLIST = 5, vrijdag), dus er valt er geen enkele af en
        # deze lus legt vandaag niets vast. Hij blijft staan omdat hij op de eerste dag dat de
        # lijstlengte wél bindt het verschil is tussen een gemeten reeks en een stille
        # weglating. Deze lus legt zo'n
        # gekwalificeerde selectie vast als `gekwalificeerd_niet_gepubliceerd` plus een
        # `near_miss` met `failed_gate = "lijstlengte"` — bewust dezelfde naam, zodat de
        # populatie niet in twee reeksen uiteenvalt (§5b, 26 sep 2026).
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
                # dezelfde wedstrijd dezelfde mening en geen afgewezen kandidaat.
                nm = m.get("near_miss")
                if nm and any(mm == m["match"] for mm, _, _ in gespeeld):
                    e["near_miss_gepubliceerd"] = e.pop("near_miss")
                e["bet"] = sleutel_bet
                entry["matches"].append(e)
            mark(state, comp, entry)

        # Dekkingstabel: óók de competities zonder wedstrijd, zoals §5 eist.
        s3 = json.load(open("tmp-run/ra_oct30_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de bekers; vandaag heeft er geen enkele een ronde, dus ze komen alle vijf uit
        # `ra_oct30_cups.py` — de twee bronnen daarvan (Fotmob-daglijst en BetExplorer) zijn
        # het eens dat er niets is, en dat is iets anders dan "niet gevonden" (§5, 6 okt).
        cups = json.load(open("tmp-run/ra_oct30_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct30_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct30_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct30_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

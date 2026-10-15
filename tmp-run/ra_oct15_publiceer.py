"""Run A 15 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct14_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. TWEE van de eenentwintig competities uit de runlijst speelden, met ZESENDERTIG duels in
het inzetvenster: de Europa League (achttien) en de Conference League (achttien). Dat is de
grootste runlijst die Run A dit najaar heeft gehad, en ze bestaat voor 100% uit kruis-grensduels.

VIJF selecties haalden alle negen poorten én hun LIGHT-lat van 16,0 pp, en er zijn TWEE regels
gepubliceerd. De bindende grens is MAX_LIGHT_IN_SHORTLIST = 2 (§0) en die bijt vandaag harder dan
ooit: alle vijf staan op LIGHT, dus de derde plek van MAX_SHORTLIST = 3 blijft LEEG omdat er geen
enkele FULL-selectie bestaat om hem te vullen. Zie
DRIE_GEKWALIFICEERDE_SELECTIES_VALLEN_OP_DE_LIGHT_CAP.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-15"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-15T04:35:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
                f"Fotmob team-xG, via scripts/interleague.py omgerekend naar de Europese "
                f"referentieschaal (§4 Kruis-grens); doelverwachting {lam[0]:.3f} thuis / "
                f"{lam[1]:.3f} uit" if len(lam) == 2 else "Fotmob team-xG, kruis-grens omgerekend",
                "Fotmob thuis/uit-splits van de eigen competitie (tweede methode, §1d)",
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
                      f"shrink staat sinds 19 sep op 1.00 (§6e). "
                      f"KRUIS-GRENS: beide ploegen zijn door scripts/interleague.py naar de "
                      f"Europese referentieschaal omgerekend (§4), dus data_tier is LIGHT en de "
                      f"lat 16,0 pp — nooit FULL, want de omrekening haalt de systematische fout "
                      f"eruit en niet de onzekerheid. "
                      f"LET OP het Pinnacle-oordeel in het runrapport onder "
                      f"WAT_ANDEREN_VOORSPELLEN: het eigen model staat bij deze regel ver boven "
                      f"de scherpste bookmaker van de markt, en §1g heeft op uitkomsten gemeten "
                      f"dat het rendement het SLECHTST is bij de hoogste geclaimde edge."
                      + ("" if cand.get("bet_beide") else
                         " bet_beide = FALSE. §5a houdt die vlag bij voor het geval een selectie "
                         "de lat ALLEEN op de herijkte schaal haalt; lees hem samen met de twee "
                         "edges hierboven.")
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
    for run, pad in (("A", "tmp-run/ra_oct15_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": (
                "recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — a=1.023811, "
                "b=0.015420 over 4512 afgerekende gevallen, fitted_through 2026-10-14, oftewel "
                "de vorige rundag zoals §6b-5c eist. Deze run heeft calibration.py settle vóór "
                "de analyse gedraaid (57 waarnemingen afgewikkeld, 4719 van 4770 compleet, 51 "
                "nog open). De fit VERHOOGT een kans over vrijwel de hele speelbare band "
                "(+0,4 pp op 50%, +0,7 pp op 70%) en verlaagt alleen onder ~35%; het ruwe model "
                "zei gemiddeld 33,333% en het gebeurde 33,333%. Bij BEIDE gepubliceerde regels "
                "staat de herijkte edge daardoor BOVEN de ruwe (+25,09 tegen +24,32 pp bij "
                "Hoffenheim – Beşiktaş, +20,40 tegen +19,68 bij Dinamo Zagreb – Anderlecht) en "
                "staat `bet_beide` op TRUE: ze halen de LIGHT-lat van 16,0 pp herijkt én ruw."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de eenentwintig competities uit de runlijst speelden, met ZESENDERTIG "
                "duels samen in het inzetvenster: de UEFA EUROPA LEAGUE met achttien en de UEFA "
                "CONFERENCE LEAGUE met achttien. Dat is de grootste runlijst die Run A dit "
                "najaar heeft gehad — ruim twee keer de dertien van gisteren — en het is een "
                "volle Europese donderdag: twee complete speelronden op één avond, met aftrap "
                "om 18:45 en 21:00 NL. NEGENTIEN competities hadden GEEN WEDSTRIJD: de dertien "
                "binnenlandse competities (Premier League, Serie A, La Liga, Bundesliga, "
                "Ligue 1, Championship, Eredivisie, Primeira Liga, Belgian Pro League, Super "
                "Lig, Scottish Premiership, Danish Superliga, Ekstraklasa — allemaal met hun "
                "eerstvolgende ronde op 17 oktober of later, want het is een Europese "
                "midweek), de CHAMPIONS LEAGUE (die speelde gisteren en komt 20 oktober terug) "
                "en de VIJF BEKERS. Dat is geen storing (§3 Stage 2)."),
            "ALLE_ZESENDERTIG_DUELS_ZIJN_KRUIS_GRENS": (
                "DIT IS DE BEPALENDE EIGENSCHAP VAN DEZE RUNDAG en ze verklaart alles wat "
                "eronder staat. Beide spelende competities zijn Europese toernooien, dus ALLE "
                "zesendertig duels zetten ploegen uit verschillende LANDEN tegenover elkaar en "
                "gaan langs `scripts/interleague.py` (§4, 'Kruis-grens'): beide ploegen worden "
                "met de op Europese duels gemeten aanval- en verdedigingsfactor van hun eigen "
                "land naar de Europese referentieschaal omgerekend, waarna ze op dezelfde "
                "grootheid staan. Twee gevolgen die de hele dag bepalen: (1) er bestaat vandaag "
                "GEEN ENKELE FULL-wedstrijd — een omgerekende ploeg is nooit FULL, dus de lat "
                "is overal 16,0 pp in plaats van 8,0; (2) MAX_LIGHT_IN_SHORTLIST = 2 is "
                "daardoor de bindende grens en niet MAX_SHORTLIST = 3, want er is geen FULL-"
                "selectie om de derde plek te vullen. DRIEËNTWINTIG duels komen op LIGHT uit en "
                "DERTIEN op NONE."),
            "DERTIEN_DUELS_OP_NONE_EN_WAAROM_DAT_GEEN_TEKORT_IS": (
                "Dertien van de zesendertig duels komen op data_tier NONE uit en worden dus "
                "NIET geanalyseerd (§2: geen onafhankelijke kansinput, geen bet). In alle "
                "dertien gevallen is de oorzaak dezelfde en ligt ze bij de bron en niet bij de "
                "analyse: `interleague.convert_team` weigert te raden. Twee varianten. (a) GEEN "
                "GEMETEN COMPETITIEFACTOR — minder dan 40 Europese duels in de meting, dus geen "
                "factor: Slovenië (NK Celje), Albanië (Egnatia), Finland (KuPS), Letland en "
                "Kazachstan (Riga FC – Kairat Almaty, beide kanten), Armenië (Ararat Armenia), "
                "Bosnië (Borac Banja Luka), Gibraltar (Lincoln Red Imps), Litouwen (Kauno "
                "Žalgiris), Georgië (Iberia 1999) en Andorra (Inter Club d'Escaldes). (b) BUITEN "
                "HET GEMETEN BEREIK na omrekening — de Coventry-val, `in_range = False`: OFI "
                "Crete (GRE, verdediging 1,685 boven de bovengrens 1,446), CSKA Sofia (BUL, "
                "aanval 0,581 onder de ondergrens 0,585) en Mjällby (SWE, aanval én verdediging "
                "buiten het bereik). Eén apart geval: TORREENSE speelt in Liga Portugal 2 (id "
                "185) en niet in de hoogste Portugese divisie (id 61) waarop de factor is "
                "gemeten. STIL TERUGVALLEN OP FACTOR 1.0 IS PRECIES DE FOUT DIE `interleague` "
                "wegneemt, dus dit is de module die doet waarvoor hij bestaat. Elk van de "
                "dertien staat met zijn volledige omrekennotitie in `kruis_grens` en als GEEN "
                "BET in het rapport. Het kost vandaag wel echt iets: ruim een derde van de "
                "grootste runlijst van het najaar valt hiermee weg, en daar zitten duels bij "
                "waar een mens makkelijk een mening over heeft (Brighton – Kauno Žalgiris, "
                "Panathinaikos – Borac). Die mening hebben is niet hetzelfde als haar kunnen "
                "meten."),
            "DE_CAP_BINDT_NIET": (
                "Zesendertig duels op een donderdagcap van 40 (`ranking.max_deep_analyses`), "
                "dus er is NIETS afgekapt (afgekapt = 0) en de hele runlijst is doorgerekend. "
                "Dat is krap: vier duels marge op de grootste lijst van het najaar. Stille "
                "truncatie is verboden (§3 Stage 4) en het omgekeerde hoort er net zo expliciet "
                "te staan. De datarijkdom liep van 3,5 (zes duels, onder andere Atalanta – "
                "Pafos FC en Riga FC – Kairat Almaty) tot 6,5 (Gent – AGF). Omdat niets afviel "
                "zijn `laagste_die_het_haalde` en `hoogste_die_afviel` leeg — er is geen grens "
                "om te noemen. Was de cap wél gebonden, dan had hij op gemeten datarijkdom "
                "gesneden en niet op aftraptijd; §3 Stage 4 meet zelf dat die sortering de "
                "betkans niet scheidt, dus afkappen kost naar rato."),
            "TWEE_REGELS_EN_BEIDE_HALEN_HUN_LAT": (
                "De lijst van twee: (1) HOFFENHEIM – BEŞIKTAŞ, 1X2 op de thuiszege @2.02 "
                "(Coolbet, gewone bookmaker), LIGHT, +25,09 pp tegen een lat van 16,0 — de "
                "hoogste selection_score van de dag (9,357) en ruim boven zijn lat; (2) DINAMO "
                "ZAGREB – ANDERLECHT, 1X2 op de thuiszege @2.078 (Matchbook-beurskoers 2,10 "
                "bruto, 2,078 na 2% commissie), LIGHT, +20,40 pp tegen 16,0 (score 6,990), óók "
                "boven zijn lat. MAX_LIGHT_IN_SHORTLIST = 2 is exact gehaald en niet "
                "overschreden. Dat BEIDE regels hun lat halen is geen belofte: §1g heeft op 552 "
                "afgerekende gevallen gemeten dat er geen drempel op de herijkte edge bestaat "
                "die geld oplevert en dat het rendement het SLECHTST is bij de hoogste "
                "geclaimde edge. Een edge van +25 pp is dus geen sterker signaal dan een van "
                "+20 — lees de lijst als rangschikking van wat het model het sterkst vindt, "
                "niet als een gevonden voordeel. BEIDE REGELS ZIJN EEN THUISZEGE OP 1X2, en bij "
                "beide staat het eigen model ver boven Pinnacle; zie "
                "WAT_ANDEREN_VOORSPELLEN, want dat is vandaag de belangrijkste "
                "waarschuwing bij deze lijst."),
            "DRIE_GEKWALIFICEERDE_SELECTIES_VALLEN_OP_DE_LIGHT_CAP": (
                "VIJF selecties haalden alle negen poorten ÉN hun LIGHT-lat van 16,0 pp, en er "
                "zijn twee regels gepubliceerd. De drie die buiten de lijst vielen, op score: "
                "NEC NIJMEGEN – LEVSKI SOFIA (1X2 thuiszege @1,9408 Betfair-netto, +19,30 pp, "
                "score 6,837, rang 3), SALZBURG – MILAN (Asian Handicap AC Milan −0,25 @1,8624 "
                "Matchbook-netto, +18,47 pp, score 6,663, rang 4) en FC TWENTE – THUN (Under "
                "3.5 @2,0388 Matchbook-netto, +18,76 pp, score 6,360, rang 5). GEEN ENKELE "
                "POORT HIELD ZE TEGEN — het is MAX_LIGHT_IN_SHORTLIST = 2 (§0), en vandaag "
                "bijt die harder dan hij ooit heeft gedaan: normaal gaat de derde plek van "
                "MAX_SHORTLIST = 3 naar de hoogste FULL-regel, maar er BESTAAT vandaag geen "
                "FULL-selectie (zie ALLE_ZESENDERTIG_DUELS_ZIJN_KRUIS_GRENS), dus die derde "
                "plek BLIJFT LEEG. De lijst is daarmee twee regels lang terwijl er drie plekken "
                "zijn en vijf gekwalificeerde selecties liggen. Dat is niet §5 's 'lever er "
                "minder, vul niet aan' (dat gaat over te WEINIG gekwalificeerde bets) maar het "
                "omgekeerde geval: te veel, op één datatier. Alle drie zijn vastgelegd zoals "
                "§5b (26 sep 2026) eist: een `gekwalificeerd_niet_gepubliceerd`-blok op de "
                "wedstrijd in data/run-state/ MET de rang erin, en een near_miss met "
                "failed_gate = 'lijstlengte' zodat shadow.py collect ze afrekent. Die naam is "
                "met opzet niet nieuw — §5b zegt 'gebruik precies die naam en verzin geen "
                "tweede', omdat twee namen één populatie in twee reeksen splitsen die nooit de "
                "~30 afgewikkelde gevallen van §6d halen. EN LET OP WAT HET KOST: de drie "
                "weggelaten regels staan op +19,30, +18,47 en +18,76 pp, en er komt geen enkele "
                "regel in de plaats — de cap ruilt hier geen zwakke data voor sterke in, zoals "
                "op 14 oktober, maar laat een plek onbenut omdat er niets van het juiste soort "
                "ligt. Of dat de juiste afweging is, is een vraag over risicobereidheid en dus "
                "een vraag voor de gebruiker (§1a, §1e); deze run verandert de cap niet op eigen "
                "initiatief en legt hem ook niet als besluit voor, want dat is op geen enkele "
                "dag eerder gebeurd en één dag is geen reeks (§6d). Hij staat als feitelijke "
                "meting in het runrapport."),
            "POORT9": (
                "Vierde bindende dag (`unders.BINDS_FROM` = 2026-10-12, §1h) en voor elke "
                "selectie aangeroepen met today=2026-10-15 zoals §1h eist. HIJ HEEFT NIETS "
                "TEGENGEHOUDEN: `poort9_geblokkeerd` is voor alle zesendertig duels leeg en de "
                "reeks `doelpunten_onder` in shadow.jsonl staat nog op de ene rij van "
                "14 oktober. Dat is vandaag niet alleen correct maar ONVERMIJDELIJK: de poort "
                "geldt per besluit van de gebruiker op 12 oktober uitsluitend op FULL "
                "(`unders.TIERS = ('FULL',)`), en er is vandaag geen enkele FULL-wedstrijd. Van "
                "de 116 doorgerekende Over/Under-selecties staat er dus per definitie geen "
                "enkele in de band 8–10 pp op FULL waar de poort bindt. DIT IS GEEN REDEN OM DE "
                "POORT OP EIGEN INITIATIEF TE VERBREDEN (§1h punt 1, §1e: risicobereidheid "
                "hoort bij de gebruiker) en deze run heeft dat dus niet gedaan — de vraag is op "
                "12 oktober gesteld en beantwoord met 'eerst kijken wat deze rem doet', en §1h "
                "schrijft voor hem niet opnieuw te stellen. Het is wel het vermelden waard dat "
                "een dag als vandaag — honderd procent LIGHT — door de poort in het geheel niet "
                "geraakt wordt, en dat FC TWENTE – THUN (Under 3.5, +18,76 pp op LIGHT) "
                "daarmee de derde LIGHT-Under in vier dagen is die door geen enkele rem is "
                "getoetst. Vandaag kostte dat niets, want de LIGHT-cap hield hem toch al buiten "
                "de lijst."),
            "POORT8": (
                "BINDT, in de lichte vorm met ondergrens 0.35 (§1e, teruggezet per 1 okt 2026), "
                "en voor elke selectie aangeroepen met today=2026-10-15 zodat het venster van "
                "25 t/m 30 september uit `sides.LAPSED_FROM`/`LAPSED_UNTIL` wordt gelezen in "
                "plaats van geraden. Hij heeft vandaag ACHT duels een selectie gekost en dat is "
                "de meest actieve dag van de poort in weken: Lech Poznań – Bayer Leverkusen, "
                "Sparta Prague – Lillestrøm, Celta Vigo – Juventus, Gent – AGF, Hajduk Split – "
                "Ajax, FC København – Braga, FC Twente – Thun en Heart of Midlothian – "
                "Nordsjælland. Dat is geen toeval maar de eigenschap van deze runlijst: een "
                "Europees toernooi zet systematisch ongelijke ploegen tegenover elkaar, dus de "
                "handicap op de zwakkere kant is er vaker de sterkste selectie dan in een "
                "binnenlandse competitie. VIER van de acht stonden ruim boven hun lat: FC "
                "Twente – Thun (AH Thun +2 @1,9604, +26,80 pp — de hoogste geclaimde edge van "
                "de hele dag), Gent – AGF (AH AGF +1 @1,81, +20,92 pp), Hajduk Split – Ajax (AH "
                "Hajduk +1 @1,83, +20,42 pp) en Heart of Midlothian – Nordsjælland (AH Hearts "
                "+0,25 @1,8918, +17,85 pp). Alle vier gaan als `underdog` (herijkte schaal) én "
                "`underdog_ruw` (ruwe schaal) naar shadow.jsonl, op de twee schalen van §1e, en "
                "die twee reeksen mogen NOOIT bij elkaar worden opgeteld — het zijn twee "
                "populaties. Let op de RUWE ranglijst van §5a: die wordt aangevoerd door FC "
                "Twente – Thun en op plek drie door Gent – AGF, allebei selecties die poort 8 "
                "heeft tegengehouden. Zonder deze poort had de lijst van vandaag er dus wezenlijk "
                "anders uitgezien, en dat is precies wat de reeks moet meten."),
            "POORT7": (
                "context.check is voor alle zesendertig duels gedraaid (§1c: ophalen vóór de "
                "afkapping, ook bij tier = NONE) en heeft vandaag NUL selecties tegengehouden. "
                "Geen enkel duel kwam op een materieel beschikbaarheidsnadeel van ≥ 10 "
                "procentpunt uit op de gespeelde kant, en geen enkel duel haalde het "
                "rustcriterium (≤ 4 dagen rust én ≥ 2 dagen minder dan de tegenstander) — "
                "logisch op een Europese donderdag, waar vrijwel elke ploeg vier tot vijf dagen "
                "rust heeft gehad en de verschillen klein zijn (4,0 tot 5,3 dagen over de hele "
                "lijst). De volledige context van alle zesendertig duels staat in "
                "`data/run-state/` en gaat via `ctxlog.py collect` de steekproef in, ook die van "
                "de dertien NONE-duels; dat is wat §1c vraagt en het verdrievoudigt de "
                "steekproef waarmee de bijstellingsvraag ooit beantwoord kan worden. Twee "
                "uitvallerslijsten zijn het noemen waard bij de gepubliceerde regels: "
                "HOFFENHEIM mist Patrick Wimmer en Albian Hajdari (samen 39,7 miljoen van een "
                "selectiewaarde van 129,6 miljoen, oftewel 23,4%) en BEŞIKTAŞ mist Dušan "
                "Vlahović en Václav Cerny (28,6 van 127,5 miljoen, 18,3%) — het verschil is 5,1 "
                "procentpunt en blijft dus onder de drempel van 10, waardoor de poort opengaat. "
                "Bij DINAMO ZAGREB – ANDERLECHT ontbreekt aan de thuiskant NIEMAND (0,0%) en "
                "mist Anderlecht vier spelers voor 9,7 van 22,9 miljoen (29,7%); dat nadeel "
                "ligt op de TEGENSTANDER van de gespeelde kant, dus de poort gaat ook daar open "
                "— hij houdt alleen tegen en laat nooit iets extra's door, en stelt `my_prob` "
                "niet bij (§1c)."),
            "POORT5_IS_OPNIEUW_DE_GROOTSTE_ZEEF": (
                "Van de 331 doorgerekende selecties vielen er 202 af op `tweede_methode` (poort "
                "5): de twee methodes versloegen de markt niet dezelfde kant op. Dat is 61% en "
                "daarmee voor de zoveelste dag op rij de grootste zeef van de negen poorten — "
                "ter vergelijking: `edge` 64, `underdog` 26, `odds` 18, `robuustheid` 6, en 15 "
                "selecties hielden alle poorten open. §5 's 'Net niet'-regel noemt dit expliciet "
                "als iets om in de gaten te houden: valt er structureel alles af op "
                "`tweede_methode`, dan is de vraag of de twee methodes systematisch uiteenlopen, "
                "en dat is een bevinding en geen ruis. Vandaag is er een extra reden om het op "
                "te schrijven: bij ALLE vijf gekwalificeerde selecties staat de splitsmethode "
                "HOGER dan de xG-methode, en vaak flink (Dinamo Zagreb +29,19 tegen +17,30 pp; "
                "NEC +27,82 tegen +16,25; Hoffenheim +29,02 tegen +23,15; Salzburg +22,07 tegen "
                "+16,62; Twente +23,93 tegen +16,58). §1d en §6e wijzen de splitsmethode aan als "
                "de scheefste van de twee, en §1f geeft haar daarom maar een vijfde gewicht in "
                "`my_prob`. Dat alle vijf regels van vandaag door haar omhoog worden getrokken "
                "is dus geen bevestiging maar een waarschuwing, en ze wijst dezelfde kant op als "
                "het Pinnacle-verschil hieronder."),
            "VROEG_SEIZOENSCORRECTIE_OP_EEN_TOERNOOI_MET_EEN_SPEELDAG": (
                "De gepoolde vroeg-seizoenscorrectie komt vandaag uit ÉÉN competitie en ÉÉN "
                "speeldag: alleen de Europa League heeft xG in zowel 2025/2026 als 2026/2027, en "
                "dat lopende seizoen staat op één speeldag. Gemeten verhouding 1,1401 (1,5917 "
                "tegen 1,3960 xG per duel), teruggetrokken naar een factor van 1,0156 door de "
                "credibiliteitsweging van `early_season_uplift` — precies waarvoor die weging "
                "bestaat, want één speeldag is geen meting. De CONFERENCE LEAGUE is uit de pool "
                "OVERGESLAGEN omdat het lopende seizoen daar nog geen xG heeft (0 speeldagen in "
                "de respons), en dat staat expliciet in `vroeg_seizoen.overgeslagen`: een stil "
                "weggelaten waarneming is hetzelfde probleem als een stille truncatie (§3 Stage "
                "5). GEVOLG VOOR VANDAAG, en dit is het eerlijke voorbehoud: de correctie die op "
                "alle zesendertig duels wordt toegepast is gemeten op één speeldag van één van "
                "de twee spelende competities. Ze is klein (1,6%) en trekt dus nergens hard aan, "
                "maar ze is ook nauwelijks onderbouwd. Reken haar NOOIT af op de markt (§3 Stage "
                "5): ze komt volledig uit xG-waarnemingen, en haar bijstellen tot de afwijking "
                "tegenover de bookmakers nul is, maakt `my_prob` van de odds afgeleid en de edge "
                "betekenisloos (§2)."),
            "INZETVENSTER": (
                "`runwindow.matches_for_run` met het venster [15.10. 08:00 NL, 16.10. 08:00 NL) "
                "(§3 Stage 1). Alle zesendertig duels komen van de daglijst van 15 oktober "
                "(`source_day` = 2026-10-15, geen enkel duel van de lijst van 16 oktober) en "
                "alle zesendertig zijn SPEELBAAR: de vroegste aftrap is 18:45 NL en de laatste "
                "21:00 NL, dus de gebruiker kan tussen 07:00 en 08:00 op elk duel inzetten. Er "
                "is vandaag dus geen enkele `playable = False`-regel en geen enkel duel uit de "
                "band [00:00, 08:00) NL — een Europese donderdag speelt volledig in de avond. "
                "`include_carry_over` is NIET meegegeven; dat was eenmalig bij de overstap van "
                "24 september."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "De poort 'bevestiging door een tweede methode' (§1) is op de RUNLIJST zelf "
                "gedraaid en staat volledig groen: ZESTIEN van de zestien competities met een "
                "BetExplorer-slug geven hetzelfde aantal duels in het venster als de "
                "Fotmob-daglijst, en het totaal klopt op de wedstrijd — 36 tegen 36. Voor de "
                "twee spelende competities is dat 18 tegen 18 en 18 tegen 18; voor de veertien "
                "competities zonder wedstrijd 0 tegen 0, met hun eerstvolgende ronde op 17 "
                "oktober of later. Twee losse bronnen die het eens zijn, en dat is het punt: de "
                "twee duurste fouten van oktober zaten in de vraag wélke wedstrijden er zijn en "
                "niet in de analyse."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "De vijf bekers (FA Cup, League Cup, Coppa Italia, KNVB Beker, DFB Pokal) "
                "hebben geen `fotmob_id` in coverage.json, dus `runwindow.matches_for_run` kan "
                "ze niet filteren en de stilte van de daglijst is voor hen GEEN bron (§5). Ze "
                "zijn langs BetExplorer gegaan en alle vijf geven teamparen op de "
                "fixturepagina — dus een geldige slug, geen homepage-redirect — met nul duels in "
                "het venster: FA Cup 32 teamparen (eerstvolgende ronde 17.10. 12:30), League Cup "
                "8 (27.10. 20:45), Coppa Italia 8 (01.12. 21:00), KNVB Beker 26 (27.10. 18:45) "
                "en DFB Pokal 16 (27.10. 18:00). GEEN WEDSTRIJD dus, met een tweede bron "
                "eronder in plaats van een aanname — precies het gat dat Run A op 6 oktober geld "
                "kostte, toen de FA Cup-kwalificatie niet in de daglijst stond en wél bij "
                "BetExplorer. De FA Cup komt overmorgen terug."),
            "BEIDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Beide spelende competities hebben een sportkey bij The Odds API "
                "(soccer_uefa_europa_league en soccer_uefa_europa_conference_league), dus er "
                "valt GEEN competitie buiten de betaalde inkoop en er is geen enkele wedstrijd "
                "waar BetExplorer de enige 1X2-bron is. Het plafond was 571 credits "
                "(`suggest_cap(19452, 17)`, 19452 over en 548 verbruikt deze maand) en er is "
                "24 van uitgegeven: 6 aan de bulk (2 competities × 3 credits voor h2h + spreads "
                "+ totals) en 18 aan BTTS per duel. Beide competities kregen de volle bulk, dus "
                "`split_budget(571, 2)` → (2, 2) en de losse-totals-stap van §1a hoefde niet te "
                "draaien. 19428 credits over."),
            "MARKTBALANS": (
                "De controle van §1a is een controle op de INKOOP en hij slaagt ruim: BEIDE "
                "spelende competities hebben zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een "
                "doelpuntenmarkt (Over/Under) — twee op twee, de maximale marge die op twee "
                "competities te halen is. BTTS is er voor ACHTTIEN van de zesendertig duels bij "
                "gekocht (§1a stap 2, op de vereniging van beide schalen van `kandidaat_edge`); "
                "de andere achttien kregen hem niet, en voor dertien daarvan is de reden dat ze "
                "op tier = NONE staan, waar §6b-5b het doorrekenen van markten overslaat. De 331 "
                "doorgerekende selecties verdelen zich over Over/Under 116, Asian Handicap 83, "
                "1X2 66, BTTS 36, Draw No Bet 22 en Double Chance 8. DE TWEE GEPUBLICEERDE "
                "REGELS KOMEN BEIDE UIT 1X2, en dat is geen inkoopeffect — alle zes markten "
                "dongen bij elk van de drieëntwintig geanalyseerde duels mee, en Over/Under was "
                "met 116 selecties zelfs de ruimst bemeten markt. Het is `selection_score` die "
                "kiest. Dat is de uitkomst en geen quotumfout (§1a: bets forceren om een "
                "verdeling te halen is verboden). Wel het opmerken waard na twee dagen waarin de "
                "lijst uit Unders bestond: vandaag staat er geen enkele Under in, en de sterkste "
                "Under van de dag (FC Twente – Thun, +18,76 pp) viel op de LIGHT-cap."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stap 2 van §3 Stage 5, in de enige vorm die bereikbaar is: de de-vigde 1X2 van "
                "PINNACLE apart gezet, LOS van de beste prijs waarop gespeeld wordt. Gevonden "
                "voor alle TWEEËNTWINTIG duels met een eigen 1X2; de veertien duels zonder "
                "Pinnacle-regel zijn de dertien NONE-duels plus Lugano – FK Crvena Zvezda, waar "
                "het eigen 1X2 ontbreekt. Gemiddelde Pinnacle-marge 4,41% — scherper dan de 6 "
                "tot 10% van de rest van de markt. Het eigen xG-1X2 staat gemiddeld 8,54 "
                "procentpunt van dat oordeel af, en DAT IS AANZIENLIJK MEER DAN DE 5,43 pp VAN "
                "GISTEREN; op een lijst die volledig uit kruis-grensomrekeningen bestaat is dat "
                "te verwachten, maar het is ook precies het soort dag waarop het model zijn "
                "eigen fout voor marktfout kan aanzien. DIT IS DE BELANGRIJKSTE WAARSCHUWING BIJ "
                "DE LIJST VAN VANDAAG, want de twee grootste uitschieters ZIJN de twee "
                "gepubliceerde regels, en ze wijzen dezelfde kant op: HOFFENHEIM – BEŞIKTAŞ "
                "(+23,84 pp op de thuiszege; eigen model 72,7%, Pinnacle 48,8%) en DINAMO ZAGREB "
                "– ANDERLECHT (+18,50 pp; 65,4% tegen 46,9%). Bij Hoffenheim is er bovendien een "
                "tweede, onafhankelijk signaal dat dezelfde kant op wijst: de eigen VORM van de "
                "thuisploeg is LWLLL (één zege in vijf) tegen WWWLW voor Beşiktaş, en de "
                "kruis-grensomrekening rekent met de xG van vórig seizoen en ziet die vorm dus "
                "niet. Het model vindt de thuisploeg bij beide regels een kleine vijfentwintig "
                "procentpunt sterker dan de scherpste bookmaker van de markt. §1g heeft op "
                "uitslagen gemeten dat de bookmaker scherper schat dan dit model, ook na "
                "herijking en betere weging, en dat het rendement het slechtst is bij de hoogste "
                "geclaimde edge. LEES DE LIJST VAN VANDAAG DUS MET MEER DAN DE GEWONE "
                "TERUGHOUDENDHEID. DIT GETAL ZIT NIET IN my_prob EN NIET IN prob_sources (§2, "
                "§4): het is andermans lezing en marktafgeleid, dus het hoort in de vergelijking "
                "en niet in de kansschatting. De derde uitschieter de andere kant op is FC "
                "TWENTE – THUN (−23,68 pp: eigen model 54,4% voor de thuiszege, Pinnacle 78,1%) "
                "— daar vindt het model de thuisploeg veel zwakker, en de selectie die het duel "
                "opleverde is dan ook een Under en geen kant."),
            "GEEN_VERPLAATSTE_WEDSTRIJD": (
                "context.check_venue is voor alle zesendertig duels gedraaid en zet GEEN ENKELE "
                "keer `relocated`: alle zesendertig spelen in het eigen stadion van de "
                "genoteerde thuisploeg. Dat is vandaag het vermelden waard omdat Europese "
                "toernooien juist de plek zijn waar uitwijkstadions voorkomen — gisteren stond "
                "Shakhtar Donetsk nog op neutraal terrein. §1c eist dat een verplaatsing wordt "
                "genoemd ook als de poort opengaat; dat er geen is, hoort er net zo expliciet te "
                "staan. Let op wat deze controle niet vangt (§1c): dat een fixture van eigenaar "
                "is gewisseld is nieuws en geen data, en een geplande run heeft geen nieuwsbron."),
            "OPSTELLINGEN": (
                "TWEEËNTWINTIG van de zesendertig duels hebben de LAATSTE BASISELF "
                "(`lastStarting11`), VIER een VOORSPELDE opstelling en bij ACHT is het "
                "opstellingsblok er wel maar zonder elftal; bij TWEE ontbreekt het blok "
                "helemaal. Poort 7 kon dus bij vierendertig van de zesendertig duels werkelijk "
                "werken in plaats van door te laten bij gebrek aan meting (§1c), en bij beide "
                "gepubliceerde regels was de laatste basiself bekend. Dat er zo weinig "
                "VOORSPELDE opstellingen zijn is normaal bij een aftrap veertien tot zestien uur "
                "na de run: de officiële elftallen komen pas een uur voor de aftrap, en Fotmob "
                "geeft tot dan de laatste bekende."),
            "p_xg_shrink08": "Vastgelegd per doorgerekende wedstrijd, zoals §6e sinds 19 sep eist.",
        }
        state["vroeg_seizoen"] = res.get("vroeg_seizoen")
        state["niveau"] = res.get("niveau")
        state["selectie_5b"] = top

        # §5b-afkapping. Bindt vandaag via MAX_LIGHT_IN_SHORTLIST (drie selecties buiten de
        # lijst); de lus is de enige plek waar een gekwalificeerde selectie die niet in de lijst
        # past wordt vastgelegd (`failed_gate = "lijstlengte"`, bewust dezelfde naam).
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
            # 7 okt 2026 — GEEN LIJSTLENGTE als de wedstrijd zelf wél een regel kreeg: dan is dit
            # dezelfde mening in een andere markt (§1, 0-of-1-bet) en geen gekwalificeerde
            # selectie die op de lijst afviel.
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
                          f"{drempel_score}. BINDENDE GRENS: "
                          + ("MAX_LIGHT_IN_SHORTLIST = 2 — deze selectie staat op LIGHT en de "
                             "twee LIGHT-plekken waren door hoger scorende regels bezet. De "
                             "derde plek van MAX_SHORTLIST = 3 kon hem NIET opvangen, want die "
                             "is voorbehouden aan een FULL-selectie en op deze rundag bestaat "
                             "er geen enkele FULL-wedstrijd: alle zesendertig duels zijn "
                             "kruis-grens en dus per definitie LIGHT (§4). Die plek blijft "
                             "daarmee leeg. Geboekt onder failed_gate = 'lijstlengte' zoals "
                             "§5b (26 sep 2026) eist: 'gebruik precies die naam en verzin geen "
                             "tweede', want het is dezelfde vraag (wat kost de lijstlengte ons) "
                             "en twee namen splitsen één populatie in twee reeksen die nooit de "
                             "~30 afgewikkelde gevallen van §6d halen."
                             if pick.get("tier") != "FULL"
                             else f"MAX_SHORTLIST = {len(top['herijkt'])} op de rangorde"))}
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
        s3 = json.load(open("tmp-run/ra_oct15_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        cups = json.load(open("tmp-run/ra_oct15_cups.json"))["cups"]
        for comp, v in cups.items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": v["status"], "matches": [],
                               "bron": "BetExplorer (geen fotmob_id; §5)",
                               "eerstvolgende_ronde": v.get("eerste_ronde"),
                               "teamparen_op_de_fixturepagina": v.get("teamparen")})

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
        for run, pad in (("A", "tmp-run/ra_oct15_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct15_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct15_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

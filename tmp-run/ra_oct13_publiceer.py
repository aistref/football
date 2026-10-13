"""Run A 13 okt 2026 onder §5b: run-state, picks en logboeken.

Overgenomen van `ra_oct12_publiceer.py` — dezelfde mechaniek, met de `parameters`-tekst van
vandaag. Twee van de eenentwintig competities uit de runlijst speelden, met ZEVENTIEN duels in
het inzetvenster: de Championship (acht) en de Champions League (negen). DRIE gepubliceerde
regels onder §5b, en vandaag haalt **geen enkele** van de drie zijn lat — alle drie staan er op
rangorde (zie DRIE_REGELS_OP_RANGORDE). Twee van de drie zijn een Under, en dat is de bevinding
van de dag: zie TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS voor waarom poort 9 die niet kon zien en
waarom dat een besluit van de gebruiker is en niet van deze run.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json, re, sys, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import toplist
from scripts.ranking import max_shortlist

DAG = "2026-10-13"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-10-13T04:25:00+02:00"      # uitleestijd van de prijzen (bulk + BetExplorer)


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
    for run, pad in (("A", "tmp-run/ra_oct13_results.json"),):
        st, top, picks, res = bouw(run, pad)
        alle_picks += picks
        gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}

        state = load_or_start(run.lower(), date.fromisoformat(DAG))
        state["parameters"] = {
            "HERIJKING": ("recalibrate.apply, fit op uitslagen uit data/calibration.jsonl — "
                          "a=1.032216, b=0.020856 over 4410 afgerekende gevallen, fitted_through "
                          "2026-10-12, oftewel de vorige rundag zoals §6b-5c eist. Deze run heeft "
                          "calibration.py settle vóór de analyse gedraaid (54 waarnemingen "
                          "afgewikkeld, 4617 van 4641 compleet, 24 nog open). De fit VERHOOGT een "
                          "kans over vrijwel de hele speelbare band en verlaagt alleen onder "
                          "~35%; het ruwe model zei gemiddeld 33,333% en het gebeurde 33,333%. "
                          "Bij alle drie de gepubliceerde regels staat de herijkte edge daardoor "
                          "BOVEN de ruwe (+14,75 tegen +13,92 pp bij Inter – Club Brugge, +7,76 "
                          "tegen +7,00 bij Galatasaray – Barcelona, +3,84 tegen +3,17 bij Bristol "
                          "City – Blackburn Rovers), en `bet_beide` staat bij alle drie op FALSE — "
                          "maar dat is vandaag geen grensgeval, want geen van de drie haalt zijn "
                          "lat op welke schaal dan ook. Zie DRIE_REGELS_OP_RANGORDE."),
            "MAX_DEEP_ANALYSES": res["afkapping"]["cap"],
            "MAX_SHORTLIST": max_shortlist(date.fromisoformat(DAG)),
            "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
            "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
            "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8,
            "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping",
            "RUNLIJST": (
                "TWEE van de eenentwintig competities uit de runlijst speelden, met ZEVENTIEN "
                "duels samen in het inzetvenster: de CHAMPIONSHIP (ENG) met acht duels en de "
                "UEFA CHAMPIONS LEAGUE met negen. Negentien competities hadden GEEN WEDSTRIJD: "
                "elf competities (Premier League, Serie A, La Liga, Bundesliga, Ligue 1, "
                "Eredivisie, Primeira Liga, Belgian Pro League, Super Lig, Scottish Premiership, "
                "Danish Superliga, Ekstraklasa — allemaal met hun eerstvolgende ronde op 16 of "
                "later, want het interlandvenster is net afgelopen), de twee andere Europese "
                "toernooien (UEL en UECL op 15 okt) en de vijf bekers. Een dinsdag in een "
                "Europese speelweek is daarmee een smalle maar scherpe dag: weinig competities, "
                "en de helft van de duels op het hoogste niveau dat er is. Dat is geen storing "
                "(§3 Stage 2)."),
            "DE_CAP_BINDT_NIET": (
                "Zeventien duels op een dinsdagcap van 40 (`ranking.max_deep_analyses`), dus er "
                "is NIETS afgekapt (afgekapt = 0) en de hele runlijst is doorgerekend. Stille "
                "truncatie is verboden (§3 Stage 4) en het omgekeerde hoort er net zo expliciet "
                "te staan. De datarijkdom liep van 5,0 (Millwall – Swansea City, Stoke City – "
                "Middlesbrough, Burnley – Charlton Athletic en Wolverhampton Wanderers – Bolton "
                "Wanderers) tot 7,33 (Villarreal – Napoli). Omdat niets afviel zijn "
                "`laagste_die_het_haalde` en `hoogste_die_afviel` leeg — er is geen grens om te "
                "noemen."),
            "NEGEN_KRUIS_GRENSDUELS": (
                "De negen Champions League-duels zijn allemaal kruis-grens en gaan langs "
                "`scripts/interleague.py` (§4, 'Kruis-grens'): beide ploegen worden met de op "
                "2111 Europese duels gemeten aanval- en verdedigingsfactor van hun eigen land "
                "naar de Europese referentieschaal omgerekend, waarna ze op dezelfde grootheid "
                "staan. ZEVEN komen op data_tier LIGHT uit (een omgerekende ploeg is nooit FULL, "
                "dus lat 16,0 pp) en TWEE op NONE, en die twee zijn geen tekort maar `in_range` "
                "die precies doet waarvoor hij bestaat: ARSENAL – LILLE valt af op Arsenal "
                "(binnenlandse verdedigingsverhouding 0.517 over 38 duels, omgerekend x1.623/0.609 "
                "naar aanval 2.088 / verdediging 0.373 — die 0.373 ligt ONDER de ondergrens 0.388 "
                "van het gemeten bereik) en VIKING – BAYERN MÜNCHEN op Bayern (aanval 2.218 "
                "omgerekend naar 2.742, BOVEN de bovengrens 2.432). Dat is de Coventry-val: buiten "
                "het gemeten bereik is er geen meting, dus geen onafhankelijke kansinput op het "
                "niveau waarop gespeeld wordt. Stil terugvallen op factor 1.0 is precies de fout "
                "die deze module wegneemt. Beide duels staan daarom met hun volledige "
                "omrekennotitie in `kruis_grens` en als GEEN BET in het rapport."),
            "DRIE_OMREKENINGEN_IN_DE_CHAMPIONSHIP": (
                "Drie van de acht Championship-duels hebben een ploeg die niet in de stand van "
                "2025/2026 staat, en ze lopen langs BEIDE richtingen van §4, alle drie op "
                "data_tier LIGHT: OMLAAG (TIER1, degradant uit de Premier League) voor BURNLEY "
                "(relatieve aanval 0.727 / verdediging 1.435 over 38 duels, omgerekend met "
                "gap_for(E0,E1,down) x1.830/0.634 naar 1.331/0.910) en WOLVERHAMPTON WANDERERS "
                "(0.517/1.301 naar 0.946/0.825); OMHOOG (TIER2, promovendus uit League One) voor "
                "CARDIFF CITY (1.488/0.826 met gap_for(E1,E2,up) x0.673/1.638 naar 1.001/1.354) "
                "en BOLTON WANDERERS. Alle vier vallen binnen `conversion_in_range`, dus geen "
                "enkel duel kwam daarop op NONE uit. LET OP de waarschuwing van §4 bij de "
                "richting OMLAAG: die valt hier op het gemeten paar ('E0','E1') bij "
                "football-data.co.uk terug en niet op POOLED_GAP, maar er bestaat nog geen aparte "
                "neerwaartse meting — lees Burnley en Wolverhampton dus met meer "
                "terughoudendheid dan Cardiff en Bolton. Geen van de drie duels levert een "
                "gepubliceerde regel op. §4 eist dat de stand per selectie uit "
                "GapResult.direction wordt gelezen in plaats van uit een samenvattende zin, en "
                "die teksten staan integraal in `promovendi` per wedstrijd."),
            "DRIE_REGELS_OP_RANGORDE": (
                "ALLE DRIE de gepubliceerde regels staan er OP RANGORDE en niet omdat ze een lat "
                "halen (§5b: staan er minder selecties boven de drempel dan er regels in de lijst "
                "passen, dan bepaalt de rangorde de lijst en is de drempel een label). Geen "
                "enkele van de 229 doorgerekende selecties haalde vandaag zijn drempel met alle "
                "poorten open — `bets` uit de analyse is 0. De drie: INTER – CLUB BRUGGE, Over "
                "3.5 @2.15 (1xBet), LIGHT, +14,75 pp tegen een lat van 16,0 — de hoogste "
                "selection_score van de dag (4,518) en 1,25 procentpunt onder zijn lat; "
                "GALATASARAY – BARCELONA, Under 4.5 @1.78 (1xBet), LIGHT, +7,76 pp tegen 16,0 "
                "(score 2,481); BRISTOL CITY – BLACKBURN ROVERS, Under 2.5 @1.931 "
                "(Matchbook-beurskoers 1.95 bruto, 1.931 na 2% commissie), FULL, +3,84 pp tegen "
                "8,0 (score 2,136). MAX_LIGHT_IN_SHORTLIST = 2 is daarmee exact gehaald en niet "
                "overschreden. Dat de lijst drie regels heeft en nul daarvan een drempel haalt is "
                "geregeld gedrag sinds 20 september en hoort hardop gezegd: dit is een "
                "rangschikking van wat het model vandaag het sterkst vindt, geen gevonden "
                "voordeel."),
            "TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS": (
                "En dat is de bevinding van vandaag, want §6g meet de Under-kant over het hele "
                "logboek op −16,5% (76 picks) tegen +10,6% voor de Over-kant. POORT 9 (§1h) heeft "
                "vandaag NUL selecties tegengehouden en dat is correct maar niet vrijblijvend: "
                "`unders.check` bindt met opzet ALLEEN in de band tussen 8,0 en 10,0 pp op FULL "
                "(zie de commentaarregels bij `unders.py` regel 180 — eronder is `edge` de "
                "bindende poort en zou poort 9 de reeks `doelpunten_onder` vervuilen met "
                "kandidaten die nooit een bet konden worden). Onder §5b is `edge` echter GEEN "
                "veto meer maar een afkapping aan het eind, en dus kan een FULL-Under ónder de "
                "8,0 pp wél gepubliceerd worden zonder dat poort 9 hem ooit ziet. Dat gebeurt "
                "vandaag: BRISTOL CITY – BLACKBURN ROVERS, Under 2.5 op +3,84 pp FULL, zit in de "
                "band 0–8 pp die in de tabel van §1h op −34,1% staat over 26 gevallen — de "
                "tweede-slechtste band van de hele reeks. De Galatasaray-Under staat op LIGHT, "
                "waar poort 9 per besluit van 12 oktober met opzet niet geldt. "
                "DIT IS GEEN REDEN OM DE POORT OP EIGEN INITIATIEF TE VERBREDEN (§1h punt 3, "
                "§1e: risicobereidheid hoort bij de gebruiker) en deze run heeft dat dus niet "
                "gedaan. Het staat als BESLUIT in het dagrapport: moet poort 9 onder §5b ook "
                "binden op een Under die op rangorde wordt gepubliceerd, of blijft de rangorde "
                "voorgaan? De vormfout in `score_grid` die hieronder ligt — keuze (a) van "
                "11 oktober — staat nog open en blijft het echte werk."),
            "POORT9": (
                "Tweede bindende dag (`unders.BINDS_FROM` = 2026-10-12, §1h) en voor elke "
                "selectie aangeroepen met today=2026-10-13 zoals §1h eist. HIJ HEEFT NIETS "
                "TEGENGEHOUDEN: `poort9_geblokkeerd` is voor alle zeventien duels leeg en de "
                "reeks `doelpunten_onder` in shadow.jsonl staat nog op nul rijen. De reden is "
                "meetbaar en niet toevallig: van de 74 doorgerekende Over/Under-selecties staat "
                "geen enkele FULL-Under in de band 8–10 pp waar de poort bindt. Zie "
                "TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS voor wat dat wél betekent."),
            "POORT8": ("BINDT, in de lichte vorm met ondergrens 0.35 (§1e, teruggezet per 1 okt "
                       "2026); sides.check() is met today=2026-10-13 aangeroepen zoals §1e eist. "
                       "Vandaag houdt hij ELF selecties tegen over DRIE wedstrijden, die elk één "
                       "rij in poort8_geblokkeerd krijgen. ÉÉN van die drie is verre van een "
                       "formaliteit en het is de duurste poortbeslissing van de dag: bij "
                       "GALATASARAY – BARCELONA stond Galatasaray +1.5 @2.32 op +23,88 pp "
                       "herijkt (+22,94 ruw), RUIM boven de LIGHT-lat van 16,0 en met de hoogste "
                       "selection_score van de hele run (7,575 ruw) — dat is dus de énige "
                       "selectie van vandaag die zónder poort 8 een echte, lat-halende "
                       "gepubliceerde bet was geweest, op een kant waar Pinnacle Galatasaray "
                       "11,4% geeft tegen 75,3% voor Barcelona. Dat duel is daarna alsnog in de "
                       "lijst gekomen met een Over/Under (Under 4.5), dus de poort heeft hier "
                       "geen wedstrijd maar een KANT tegengehouden — precies wat hij hoort te "
                       "doen. De andere twee (Watford +0.75 @2.00 op +6,26 pp en Sabah FK of "
                       "gelijk @1.853 op +8,07 pp) haalden hun lat sowieso niet. Die drie rijen "
                       "gaan als `underdog` het schaduwlogboek in; de reeks staat vóór vandaag op "
                       "41 afgewikkelde gevallen en blijft volgens §1e een reden om de vraag te "
                       "stellen en geen automatisme om de poort te schrappen — de kalibratiefout "
                       "die de rem afdekt is er nog (zie `calibration.py stats` in het "
                       "runrapport)."),
            "POORT7": ("Voor alle zeventien duels gedraaid en in `context` vastgelegd, ook waar "
                       "hij opengaat (§1c). Hij houdt ELF selecties tegen en is bij DRIE duels de "
                       "bindende poort, alle drie in de Championship en alle drie op blessures: "
                       "BRISTOL CITY – BLACKBURN ROVERS (Blackburn mist 33% van de "
                       "selectiewaarde tegen 0% bij Bristol City — Yuri Ribeiro, Scott Wharton en "
                       "Mathias Jørgensen; de uitzege @3.90 stond op +3,72 pp), MILLWALL – "
                       "SWANSEA CITY (Millwall mist 55% tegen 22% — Lukas Bornhøft Jensen, Josh "
                       "Coburn en Casper de Norre; de thuiszege @2.54 stond op +5,08 pp en is "
                       "daarmee de grootste geclaimde edge die poort 7 vandaag tegenhield) en "
                       "BIRMINGHAM CITY – PRESTON NORTH END (Preston mist 39% tegen 5% — Callum "
                       "Lang, Harry Clarke en Caleb Wiley). Bij de overige veertien duels staat "
                       "de poort aan beide kanten open. Bij `side = None` — Over/Under en BTTS — "
                       "staat hij altijd open; dat is geen meting maar de regel van §1c, want er "
                       "is geen kant om te benadelen. LET OP: alle drie de gepubliceerde regels "
                       "zijn Over/Under en dus `side = None`, dus bij géén van de drie heeft "
                       "poort 7 iets kunnen zeggen. Bij Bristol City – Blackburn Rovers is dat "
                       "scherp: dezelfde wedstrijd waar de poort de KANT tegenhield levert wél "
                       "een gepubliceerde doelpuntenregel op, en die 33% ontbrekende "
                       "selectiewaarde bij Blackburn is voor een totaal net zo relevant — alleen "
                       "is niet gemeten in welke richting (§1c)."),
            "POORT5_IS_OPNIEUW_DE_GROOTSTE_ZEEF": (
                "160 van de 229 doorgerekende selecties (69,9%) sneuvelen op poort 5 — de twee "
                "methodes verslaan de markt niet dezelfde kant op. Dat is de ZEVENDE dag op rij "
                "boven tweederde (Run A 12 okt: 103 van 141, 73,0%; 11 okt: 417 van 550, 75,8%) "
                "en het is daarmee geen dageffect meer. Zie de bevinding in het runrapport: het "
                "aandeel is zo stabiel dat het eerder iets over de twee schatters zegt dan over "
                "de wedstrijden van een dag. De overige poorten: edge 35, context 11, underdog "
                "11, odds 8, robuustheid 4, en NUL selecties met alle poorten open."),
            "VROEG_SEIZOENSCORRECTIE_SCHIET_VOOR_DE_DERDE_DAG_DOOR": (
                "factor x1.0424 (gepoold 1.0763 over 10 speeldagen in de twee spelende "
                "competities; `uplift_observations` sloeg er NUL over — beide hebben xG in beide "
                "seizoenen en geen van beide is op of boven de helft van zijn speeldagen). De "
                "Championship staat op 9 van 46 speeldagen (20%), de Champions League op 1 van 8, "
                "dus beide nemen de route `vorig+uplift` van `league_level`. De controlemeting "
                "die §3 Stage 5 eist wijst opnieuw de verkeerde kant op, voor de DERDE dag op "
                "rij: P(Over 2.5) tegen de de-vigde marktkans staat op −0,63 pp ZONDER de "
                "correctie en op +2,11 pp MET (gemiddelde absolute fout 1,87 → 2,11 pp) over de "
                "vijf duels met een 2.5-lijn aan beide kanten. Run A mat op 12 okt +3,83 → +8,02 "
                "en op 11 okt −2,06 → +3,03. Het patroon is dus consistent: zonder correctie zit "
                "het model er dichter op. LET OP WAT DIT NIET MAG WORDEN: dit is een vergelijking "
                "met de MARKT en dus een diagnose, nooit een knop om de correctie op af te "
                "regelen (§2, §6e). Het hoort als openstaand punt in het runrapport en niet als "
                "wijziging in deze run — maar drie dagen op rij dezelfde richting is wél de "
                "aanleiding om het op uitkomsten te gaan meten in plaats van tegen de markt."),
            "INZETVENSTER": (
                "Het venster is [08:00 NL 13 okt, 08:00 NL 14 okt). Alle zeventien duels komen "
                "van de daglijst van 2026-10-13 (source_day = DAY, geen enkele DAY+1) en alle "
                "zeventien staan op RunMatch.playable = True: de vroegste aftrap is Lens – "
                "Sporting CP en Sabah FK – Slavia Prague om 18:45 NL en de run begon om 04:19 NL. "
                "De nachtband waarvoor runwindow.py op 24 september is gebouwd is vandaag leeg; "
                "deze runlijst heeft geen competitie in een Amerikaanse tijdzone. De aftraptijden "
                "zijn met twee bronnen bevestigd — Fotmob in UTC en BetExplorer in UK-tijd, dus "
                "NL −1 uur: 'Today 17:45' en 'Today 20:00' bij de Champions League komen uit op "
                "18:45 en 21:00 NL, precies wat Fotmob geeft."),
            "RUNLIJST_BEVESTIGD_DOOR_TWEEDE_BRON": (
                "§1 eist bevestiging door een tweede methode, en dat geldt ook voor de vraag "
                "wélke wedstrijden er zijn. PER COMPETITIE EENS, niet alleen op het totaal: voor "
                "alle ZESTIEN competities met een BetExplorer-slug geeft de fixturepagina exact "
                "hetzelfde aantal duels in het venster als de Fotmob-daglijst (17 tegen 17), "
                "inclusief de nullen bij de veertien competities die vandaag niet spelen. De twee "
                "bulk-responsen van The Odds API dekken dezelfde twee spelende competities. "
                "ÉÉN REPARATIE DEZE RUN, en ze hoort hier te staan omdat de controle er groen van "
                "stond: het script dat de META-tabel uitleest gebruikte `\\s+` na de dubbele punt "
                "en de regel \"Scottish Premiership (SCO)\":(\"SCO\", ... heeft daar geen ruimte. "
                "Die competitie werd daardoor door GEEN tweede bron bevestigd, terwijl het totaal "
                "('15 van 15') er compleet uitzag. Met `\\s*` zijn het er zestien van zestien. "
                "Dezelfde stille faalstand die §6b-5b beschrijft: een controle die groen staat "
                "omdat hij één rij niet meet."),
            "BEKERS_GAAN_LANGS_BETEXPLORER": (
                "Geen van de vijf bekers op de Run A-runlijst heeft een fotmob_id in "
                "coverage.json, dus runwindow.matches_for_run kan ze niet filteren en 'niet in de "
                "daglijst' is voor hen geen uitspraak — dat is het gat dat Run A op 6 oktober "
                "trof. Alle vijf zijn daarom apart langs BetExplorer gegaan "
                "(tmp-run/ra_oct13_cups.py) en alle vijf hebben hun eerstvolgende ronde NA het "
                "inzetvenster: FA Cup 17 okt (32 teamparen, nog geen koersen), League Cup 27 okt "
                "(8 duels mét 24 koersen), KNVB Beker 27 okt (26 teamparen), DFB Pokal 27 okt "
                "(16 duels mét 48 koersen), Coppa Italia 1 dec (8 teamparen). Vijf keer GEEN "
                "WEDSTRIJD met een tweede bron eronder in plaats van met een stilte."),
            "BEIDE_COMPETITIES_HEBBEN_EEN_SPORTKEY": (
                "Geen enkel duel draait vandaag op het gratis BetExplorer-marktgemiddelde alleen: "
                "beide spelende competities hebben een sportkey bij The Odds API en kregen de "
                "bulk-aanroep (h2h + spreads + totals, 3 credits elk). Vijf van de zes markten "
                "liggen dus bij elk duel op de BESTE PRIJS, en die lag vandaag gemiddeld 6,30% "
                "boven het marktgemiddelde van BetExplorer (3,03% tot 12,78% over de vijftien "
                "doorgerekende duels) — in edge is dat de orde van +1,8 pp per selectie, gratis "
                "(§1a). Elke koers is door oddsapi.net_price gehaald, dus beurzen staan er na 2% "
                "commissie in; bij de derde gepubliceerde regel is dat zichtbaar (Matchbook 1.95 "
                "bruto wordt 1.931 netto). Creditverbruik deze run: 6 voor de twee bulk-aanroepen "
                "plus 20 voor tien keer BTTS = 26 van een plafond van 512, en 19.477 van 20.000 "
                "over voor de rest van de maand."),
            "MARKTBALANS": (
                "De controle van §1a is een controle op de INKOOP en hij slaagt ruim: BEIDE "
                "spelende competities hebben zowel een uitkomstmarkt (1X2, AH, DNB, DC) als een "
                "doelpuntenmarkt (Over/Under) — twee op twee. BTTS is er voor TIEN van de "
                "zeventien duels bij gekocht (2 credits per duel, §1a stap 2, op de vereniging "
                "van beide schalen van `kandidaat_edge`); de zeven die hem niet kregen staan in "
                "markets_checked met 'niet opgevraagd — geen kandidaat-edge in dit duel' en niet "
                "als gat. De 229 doorgerekende selecties verdelen zich over Over/Under 74, Asian "
                "Handicap 67, 1X2 43, BTTS 20, Draw No Bet 14 en Double Chance 11. DE DRIE "
                "GEPUBLICEERDE REGELS ZIJN ALLE DRIE EEN OVER/UNDER, en dat is geen inkoopeffect "
                "— alle zes markten dongen bij elk duel mee. Het is `selection_score` die "
                "kiest, en de twee kantmarkten werden bij de hoogste edges door poort 7 en poort "
                "8 tegengehouden. Dat is de uitkomst en geen quotumfout (§1a: bets forceren om "
                "een verdeling te halen is verboden), maar het is wel de reden dat "
                "TWEE_VAN_DE_DRIE_REGELS_ZIJN_UNDERS hierboven staat."),
            "WAT_ANDEREN_VOORSPELLEN": (
                "Stap 2 van §3 Stage 5, in de enige vorm die bereikbaar is: de de-vigde 1X2 van "
                "PINNACLE apart gezet, LOS van de beste prijs waarop gespeeld wordt. Gevonden "
                "voor alle VIJFTIEN duels met een eigen 1X2 (30 events in de twee responsen); de "
                "twee duels zonder Pinnacle-regel zijn precies de twee NONE-duels, die geen eigen "
                "1X2 hebben. Gemiddelde Pinnacle-marge 3,93% — scherper dan de 6 tot 10% van de "
                "rest van de markt. Het eigen xG-1X2 staat gemiddeld 4,19 procentpunt van dat "
                "oordeel af, het laagste van de afgelopen dagen. Twee uitschieters, allebei in de "
                "Champions League en allebei dezelfde kant op: ATLÉTICO MADRID – MANCHESTER "
                "UNITED (−16,46 pp op de thuiszege; Pinnacle 50,1%, eigen model 33,7%) en "
                "GALATASARAY – BARCELONA (−17,06 pp op de uitzege; Pinnacle 75,3%, eigen model "
                "58,3%). Het model onderschat in beide gevallen de favoriet — dezelfde richting "
                "als de kalibratiefout van §1e. Bij de drie gepubliceerde regels zegt Pinnacle "
                "niets, want alle drie zijn een doelpuntenmarkt. DIT GETAL ZIT NIET IN my_prob EN "
                "NIET IN prob_sources (§2, §4): het is andermans lezing en marktafgeleid, dus het "
                "hoort in de vergelijking en niet in de kansschatting. ÉÉN REPARATIE: Lens – "
                "Sporting CP viel op de naamkoppeling weg omdat The Odds API 'RC Lens' en "
                "'Sporting Lisbon' noteert — `resolve` accepteert een afkorting alleen als "
                "voorvoegsel (§4, de Jong-Ajax-regel). Er is een derde terugval bijgezet die op "
                "bevatting óf een gemeenschappelijk voorvoegsel van vijf tekens koppelt en het "
                "resultaat alleen accepteert als er PRECIES ÉÉN kandidaat is; die eis van "
                "uniciteit is de rem tegen diezelfde val."),
            "EEN_VERPLAATSTE_WEDSTRIJD": (
                "context.check_venue is voor alle zeventien duels gedraaid en zet ÉÉN keer "
                "relocated: SABAH FK – SLAVIA PRAGUE wordt gespeeld in het Bakı Olimpiya "
                "Stadionu (Baku) en niet in Sabah's eigen Bank Respublika Arena. §1c eist dat een "
                "verplaatsing wordt genoemd ook als de poort opengaat, en dat is hier het geval: "
                "de poort houdt niets tegen, maar thuisvoordeel is de aanname waar het model het "
                "zwaarst op leunt en dit duel speelt op neutraal-achtig terrein in dezelfde stad. "
                "Het duel levert geen gepubliceerde regel op (de sterkste selectie, Sabah FK of "
                "gelijk @1.853 op +8,07 pp, is door poort 8 tegengehouden), dus de verplaatsing "
                "raakt vandaag geen bet. De overige zestien duels staan in het eigen stadion van "
                "de genoteerde thuisploeg."),
            "OPSTELLINGEN": (
                "Negen van de zeventien duels hebben een VOORSPELDE opstelling en acht de laatste "
                "basiself; GEEN ENKEL duel mist het opstellingsblok, en dat is voor deze runlijst "
                "ongebruikelijk gunstig — het is ook de reden dat de laagste datarijkdom van de "
                "run op 5,0 blijft in plaats van op 4,5 te zakken zoals op 12 oktober. Poort 7 "
                "kon dus bij elk duel werkelijk werken in plaats van door te laten bij gebrek aan "
                "meting (§1c)."),
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
        s3 = json.load(open("tmp-run/ra_oct13_stage3.json"))
        for comp, v in s3["fixtures"].items():
            if comp in state["competitions"]:
                continue
            mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": []})
        # En de VIJF BEKERS, die geen fotmob_id hebben en dus niet in s3["fixtures"] staan.
        # §5 eist een dekkingsregel voor ELKE competitie uit de runlijst; zonder deze lus telt de
        # tabel 16 van de 21 en leest een onvolledige dekking als een volledige. Hun status komt
        # uit de tweede bron (`ra_oct13_cups.json`), niet uit de stilte van de daglijst.
        cups = json.load(open("tmp-run/ra_oct13_cups.json"))["cups"]
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
        for run, pad in (("A", "tmp-run/ra_oct13_results.json"),):
            st, top, picks, res = bouw(run, pad)
            json.dump(top, open(f"tmp-run/ra_oct13_top_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            json.dump(picks, open(f"tmp-run/ra_oct13_picks_{run.lower()}.json", "w"),
                      ensure_ascii=False, indent=1)
            print(f"Run {run}: {len(res['matches'])} wedstrijden, {len(top['herijkt'])} regels")
            for p in picks:
                print(f"   {p['selection'][:30]:30s} @{p['odds']:6.4f}  edge {p['edge_pp']:+5.2f}  "
                      f"{p['competition']}")

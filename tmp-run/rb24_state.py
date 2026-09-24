"""Run B 24 sep 2026 — data/run-state/2026-09-24-run-b.json schrijven."""
import json
from datetime import date

DAY = "2026-09-24"
an = json.load(open("tmp-run/rb24_analysis.json"))
bex = json.load(open("tmp-run/rb24_bex.json"))
s3 = json.load(open("tmp-run/rb24_stage3.json"))

RUNLIST = ["Czech First League (CZE)","Greek Super League (GRE)","Eliteserien (NOR)",
 "Allsvenskan (SWE)","Croatian HNL (CRO)","Hungarian NB I (HUN)","Romanian SuperLiga (ROU)",
 "Segunda División (ESP)","Serie B (ITA)","2. Bundesliga (GER)","Swiss Super League (SUI)",
 "Austrian Bundesliga (AUT)","Keuken Kampioen Divisie (NED)","English League One (ENG)",
 "English League Two (ENG)","MLS (USA)","Série A (BRA)"]
IDS = {"Czech First League (CZE)":122,"Greek Super League (GRE)":135,"Eliteserien (NOR)":59,
 "Allsvenskan (SWE)":67,"Croatian HNL (CRO)":252,"Hungarian NB I (HUN)":212,
 "Romanian SuperLiga (ROU)":189,"Segunda División (ESP)":140,"Serie B (ITA)":56,
 "2. Bundesliga (GER)":146,"Swiss Super League (SUI)":69,"Austrian Bundesliga (AUT)":38,
 "Keuken Kampioen Divisie (NED)":111,"English League One (ENG)":108,"English League Two (ENG)":109,
 "MLS (USA)":130,"Série A (BRA)":268}

comps = {}
for name in RUNLIST:
    b = bex.get(name, {})
    if name == "MLS (USA)":
        continue
    reden = (f"geen wedstrijd op de Fotmob-daglijst van 24 sep 2026 (id {IDS[name]}: geen treffer, "
             f"find_league op naam+ccode leeg; ook de daglijst van 25 sep nagekeken); bevestigd met "
             f"de BetExplorer-fixturepagina")
    letop = None
    if b.get("rows") == 0:
        letop = ("de fixturepagina gaf 0 rijen na de ingebouwde herhaalpoging — dat is de bekende "
                 "wisselende respons van BetExplorer (coverage.json, notitie van 23 sep), geen "
                 "bewijs van 'geen wedstrijden'. Fotmob is hier de beslissende bron en die is ook "
                 "leeg; de competitie ligt tot 10 okt stil")
    comps[name] = {
        "status": "GEEN WEDSTRIJD", "matches": [], "reden": reden,
        "bevestiging_betexplorer": {
            "teamparen_op_de_pagina": b.get("rows"),
            "rijen_vandaag": len(b.get("today") or []),
            "eerstvolgende_label_UK_tijd": b.get("next") or None,
            "let_op": letop,
        }}
    if name == "Segunda División (ESP)":
        comps[name]["reden"] += "; eerstvolgende duel Girona – Albacete op 25 sep 20:30 NL"
    if name == "Keuken Kampioen Divisie (NED)":
        comps[name]["reden"] += "; eerstvolgende duel FC Dordrecht – Almere City op 25 sep 21:00 NL"

c = an["candidates"]
mls = {
 "status": "GEANALYSEERD",
 "primaryId": 130,
 "seizoensnotatie": {"vorig": "2025", "lopend": "2026",
   "waarom": "MLS loopt op kalenderjaar (prompts/run-b.md); '2025/2026' zou Fotmob stil laten "
             "terugvallen op het lopende seizoen"},
 "niveau": an["league"],
 "reden": "één duel op de Fotmob-daglijst van 24 sep (id 130), bevestigd op de BetExplorer-"
          "fixturepagina met label 'Today 02:30' (UK-tijd)",
 "bevestiging_betexplorer": {
   "teamparen_op_de_pagina": bex["MLS (USA)"]["rows"],
   "rijen_vandaag": 1,
   "eerstvolgende_label_UK_tijd": bex["MLS (USA)"]["next"],
   "let_op": None},
 "matches": [{
   "competition": "MLS (USA)",
   "match": "Seattle Sounders FC – Real Salt Lake",
   "match_id": 5071094,
   "home": "Seattle Sounders FC", "away": "Real Salt Lake",
   "kickoff_utc": "2026-09-24T01:40:00.000Z",
   "kickoff_nl": "03:40",
   "tier": "FULL",
   "tier_reden": "Fotmob geeft xG voor MLS in beide seizoenen (2025: 30 ploegen, avg 1.492; "
                 "2026: 30 ploegen, 27 speeldagen, avg 1.537)",
   "richness": an["richness"],
   "richness_parts": an["richness_parts"],
   "richness_notes": an["richness_notes"],
   "markets": 1,
   "bet": False,
   "geen_bet_reden": ("aftrap 03:40 NL — het duel stond bij het draaien van de run (05:15 CEST) op "
                      "89' met 2-0 en `finished` false. Er was dus niets meer te spelen: de "
                      "rapporten staan om 06:30 klaar en de gebruiker zet tussen 07:00 en 08:00 in "
                      "(§0). Onafhankelijk daarvan haalde geen enkele selectie een positieve edge."),
   "afkapping": None,
   "all_candidates": c,
   "markets_checked": {
     "1X2": (f"BetExplorer-marktgemiddelde over {4} boeken, pre-match slotkoers: 1 @1.76, X @3.90, "
             "2 @4.13 (marge 6.67%). The Odds API gaf voor dit duel LIVE prijzen omdat het al "
             "onderweg was — Seattle 1.01, Real Salt Lake 1000.0, gelijkspel 61.0 — en die zijn "
             "geen marktoordeel vooraf; niet gebruikt."),
     "AH": ("spreads opgehaald in de bulk-respons (soccer_usa_mls, 3 credits voor h2h+spreads+"
            "totals), maar de lijnen waren live: Seattle 0.0 @1.77 en -2.0 @1.70, Real Salt Lake "
            "+2.5 @1.15. Een pre-match handicapprijs was niet meer te krijgen."),
     "DNB": ("geen aparte draw_no_bet opgevraagd: die markt zit niet in de bulk-endpoint en kost "
             "een eigen credit per wedstrijd, en voor een duel op 89' is er geen pre-match prijs "
             "meer om te kopen."),
     "DC": ("idem double_chance — per-wedstrijd-endpoint, geen pre-match prijs meer beschikbaar."),
     "OU": ("totals opgehaald in dezelfde bulk-respons, maar live: Over 2.5 @3.40, Under 2.5 @2.07 "
            "bij een tussenstand van 2-0. Niet bruikbaar als pre-match markt."),
     "BTTS": ("niet opgevraagd — §1a stap 2 koopt BTTS alleen voor duels met een kandidaat-edge, en "
              "er was er geen; bovendien geen pre-match prijs meer."),
     "context": "Fotmob blessures/schorsingen + vorm + rustdagen + stadioncontrole",
   },
   "context": an["context"],
   "turnover": an["turnover"],
   "stadion": an["stadion"],
   "venue": an["venue"],
   "poort8_vervallen": {x["selection"]: x["poort8_vervallen"] for x in c},
   "calibration": {
     "market": round(an["devig"][0], 4),
     "p_xg": round(an["probs_xg"]["1"], 4),
     "p_xg_noshrink": round(an["probs_xg"]["1"], 4),
     "p_split": round(an["probs_split"]["1"], 4),
     "p_mean": round(0.8 * an["probs_xg"]["1"] + 0.2 * an["probs_split"]["1"], 5),
     "outcome": "thuis",
     "method": "multiplicatief",
     "let_op": ("de-vigd BetExplorer-gemiddelde over 4 boeken als marktkans; de stand van 2026 "
                "telt dit duel nog niet mee (25 resp. 26 van 27 speeldagen), dus de modelinput is "
                "zuiver pre-match"),
   },
   "near_miss": None,
 }],
}
comps["MLS (USA)"] = mls

state = {
 "run": "B", "date": DAY, "resumed_count": 0,
 "competitions": {k: comps[k] for k in RUNLIST},
 "completed": False,
 "parameters": {"MAX_DEEP_ANALYSES": 40, "MAX_SHORTLIST": 3, "EDGE_THRESHOLD_FULL": 8.0,
   "EDGE_THRESHOLD_LIGHT": 16.0, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8, "SHRINK": 1.00,
   "UNDERDOG_FLOOR": 0.35, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
   "herijking": an["fit"]},
 "credits": {"the_odds_api": {"gebruikt_deze_run": 3, "over": 18754,
   "waarvoor": "één bulk-verzoek h2h+spreads+totals op soccer_usa_mls (eu), om vast te stellen of "
               "een al begonnen wedstrijd nog pre-match prijzen krijgt — dat doet hij niet"}},
 "bevestiging": {
   "fixtures_bron_1": "Fotmob daglijst 24 sep (29 competities, 48 wedstrijden) én 25 sep "
                      "(61 competities, 103 wedstrijden), per primaryId getoetst",
   "fixtures_bron_2": "17 BetExplorer-fixturepagina's, los opgehaald",
   "uitkomst": "beide bronnen geven exact één duel uit de runlijst op 24 sep: MLS, Seattle "
               "Sounders FC – Real Salt Lake",
 },
 "afkapping": {"MAX_DEEP_ANALYSES": 40, "kandidaten": 1, "afgekapt": 0,
   "laagste_die_het_haalde": an["richness"], "hoogste_die_afviel": None},
 "dagrapport": None,
}
json.dump(state, open(f"data/run-state/{DAY}-run-b.json", "w"), ensure_ascii=False, indent=1)
print("geschreven:", f"data/run-state/{DAY}-run-b.json")
print("statussen:", {k: v["status"] for k, v in state["competitions"].items()})

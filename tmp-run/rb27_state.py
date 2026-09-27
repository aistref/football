"""Run B 27 sep 2026 — data/run-state/2026-09-27-run-b.json schrijven.

Alle zeventien competities uit `prompts/run-b.md` krijgen een regel (§5 eist dat), niet alleen
de drie die vandaag speelden: `report.py` rendert de dekkingstabel hieruit en meldt "alle N
competities uit de opdracht".
"""
import json
from datetime import date

DAY = "2026-09-27"
res = json.load(open("tmp-run/rb27_results.json"))
s3 = json.load(open("tmp-run/rb27_stage3.json"))
top = json.load(open("tmp-run/rb27_top_b.json"))
nxt = json.load(open("tmp-run/rb27_next.json"))
odds = json.load(open("tmp-run/rb27_odds.json"))

RUNLIST = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
 "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)", "Romanian SuperLiga (ROU)",
 "Segunda División (ESP)", "Serie B (ITA)", "2. Bundesliga (GER)", "Swiss Super League (SUI)",
 "Austrian Bundesliga (AUT)", "Keuken Kampioen Divisie (NED)", "English League One (ENG)",
 "English League Two (ENG)", "MLS (USA)", "Série A (BRA)"]
IDS = {"Czech First League (CZE)": 122, "Greek Super League (GRE)": 135, "Eliteserien (NOR)": 59,
 "Allsvenskan (SWE)": 67, "Croatian HNL (CRO)": 252, "Hungarian NB I (HUN)": 212,
 "Romanian SuperLiga (ROU)": 189, "Segunda División (ESP)": 140, "Serie B (ITA)": 56,
 "2. Bundesliga (GER)": 146, "Swiss Super League (SUI)": 69, "Austrian Bundesliga (AUT)": 38,
 "Keuken Kampioen Divisie (NED)": 111, "English League One (ENG)": 108,
 "English League Two (ENG)": 109, "MLS (USA)": 130, "Série A (BRA)": 268}

comps = {}
per_comp = {}
for m in res["matches"]:
    per_comp.setdefault(m["competition"], []).append(m)

for name in RUNLIST:
    if name in per_comp:
        comps[name] = {
            "status": "GEANALYSEERD",
            "primaryId": IDS[name],
            "seizoensnotatie": {"vorig": s3["fixtures"][name]["s_prev"],
                                "lopend": s3["fixtures"][name]["s_cur"]},
            "xg_dekking": s3["stats"].get(name),
            "matches": per_comp[name],
        }
        continue
    v = nxt.get(name)
    reden = (f"geen wedstrijd in het inzetvenster [08:00 NL 27 sep, 08:00 NL 28 sep) — "
             f"Fotmob-daglijsten van 27 sep (85 competities, 288 duels) en 28 sep (33 competities, "
             f"60 duels) op primaryId {IDS[name]} nagekeken, beide leeg")
    if v:
        reden += (f"; eerstvolgende duel {v['datum']} — {v['eerste']} {v['aftrap_nl']} NL "
                  f"({v['aantal']} duels die dag)")
    else:
        reden += "; geen duel binnen de achttien vooruit gescande daglijsten"
    comps[name] = {"status": "GEEN WEDSTRIJD", "matches": [], "reden": reden,
                   "eerstvolgende": v}

state = {
 "run": "B", "date": DAY, "resumed_count": 0,
 "competitions": {k: comps[k] for k in RUNLIST},
 "completed": False,
 "parameters": {
   "MAX_DEEP_ANALYSES": 55, "MAX_SHORTLIST": 5,
   "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0,
   "MAX_LIGHT_IN_SHORTLIST": 2, "MIN_ODDS": 1.30, "MAX_ODDS": 6.00,
   "SHRINK": 1.00, "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8, "UNDERDOG_FLOOR": 0.35,
   "SELECTIE": "§5b — rangorde over de hele runlijst, drempel als afkapping en anders als label",
   "POORT8": ("VERVALLEN sinds 25 sep 2026 (sides.LAPSES_ON). sides.check() laat elke kant door "
              "en zet alleen nog would_block; dat staat per selectie onder poort8_vervallen."),
   "HERIJKING": res.get("fit") or ("recalibrate.apply — a=1.0299, b=+0.0194 op 2346 afgerekende "
                                   "gevallen t/m 18 sep 2026"),
 },
 "vroeg_seizoen": res["vroeg_seizoen"],
 "niveau": res["niveau"],
 "afkapping": res["afkapping"],
 "selectie_5b": {
   "MAX_SHORTLIST": 5,
   "boven_de_drempel": sum(1 for r in top["herijkt"] if "haalt ook de lat" in r["status"]),
   "gepubliceerd": len(top["herijkt"]),
   "toelichting": ("Eén selectie haalt haar drempel (Eibar – Las Palmas, +18.53 pp bij 8.0). Dat "
                   "is minder dan MAX_SHORTLIST, dus de rangorde bepaalt de lijst en de drempel "
                   "gaat per regel mee als label (§5b stap 5). Er passen vijf regels en er zijn "
                   "vier kandidaten die alle poorten halen: De Graafschap – FC Den Bosch viel op "
                   "poort 5 (tweede_methode) en Columbus Crew – Inter Miami CF ook, en Burgos CF – "
                   "Eldense kwam op tier NONE uit. MAX_LIGHT_IN_SHORTLIST was daarmee niet "
                   "bindend: er staan precies twee LIGHT-regels in, en er was geen derde."),
   "gekwalificeerd_niet_gepubliceerd": [],
   "lijstlengte_reeks": ("geen rij vandaag — er stond maar één selectie boven haar drempel, dus "
                         "geen enkele gekwalificeerde selectie is op lijstlengte afgevallen"),
   "herijkt": top["herijkt"], "ruw": top["ruw"],
 },
 "bevestiging": {
   "fixtures_bron_1": ("Fotmob daglijsten 27 sep (85 competities, 288 duels) en 28 sep (33 "
                       "competities, 60 duels), per primaryId getoetst via runwindow.matches_for_run"),
   "fixtures_bron_2": ("BetExplorer-fixturepagina's van de drie actieve competities: Segunda "
                       f"División {len(odds['fixtures'].get('Segunda División (ESP)') or [])} "
                       f"teamparen ({sum(1 for r in (odds['fixtures'].get('Segunda División (ESP)') or []) if r['is_today'])} vandaag), "
                       f"Keuken Kampioen Divisie {len(odds['fixtures'].get('Keuken Kampioen Divisie (NED)') or [])} "
                       f"({sum(1 for r in (odds['fixtures'].get('Keuken Kampioen Divisie (NED)') or []) if r['is_today'])} vandaag), "
                       f"MLS {len(odds['fixtures'].get('MLS (USA)') or [])} "
                       f"({sum(1 for r in (odds['fixtures'].get('MLS (USA)') or []) if r['is_today'])} vandaag)"),
   "fixtures_bron_3": ("achttien daglijsten vooruit gescand (rb27_next.py) — de veertien stille "
                       "competities hervatten tussen 2 en 10 oktober, wat de interlandbreak "
                       "bevestigt in plaats van een storing"),
   "uitkomst": ("zeven duels in het inzetvenster, over drie competities: Segunda División 5, "
                "Keuken Kampioen Divisie 1, MLS 1"),
   "inzetvenster": ("negen van de tien MLS-duels op de Fotmob-daglijst van 27 sep trappen af "
                    "tussen 02:30 en 04:30 NL en hoorden dus bij de run van 26 sep (die twee "
                    "ervan ook echt heeft gespeeld — zie Stage 0). Het tiende, Columbus Crew – "
                    "Inter Miami CF om 01:00 NL op 28 sep, valt in dit venster. Dat is precies "
                    "waar runwindow.py voor is gebouwd."),
 },
 "credits": {"the_odds_api": {
   "gebruikt_deze_run": 11, "over": 18655,
   "waarvoor": ("2 bulk-aanroepen h2h+spreads+totals (Segunda División, MLS) van 3 credits, plus "
                "5 BTTS-event-aanroepen van 2 credits voor de duels met een kandidaat-edge. De "
                "Keuken Kampioen Divisie heeft geen sportkey en draait op het gratis "
                "BetExplorer-marktgemiddelde.")}},
 "stage_min2": {
   "takken_nagelopen": 31,
   "bevinding": ("main is een gesquashte lijn van 70 commits, dus rev-list telt op de oudere "
                 "takken tientallen 'eigen' commits die er inhoudelijk al in zitten. Op inhoud "
                 "vergeleken: picks (311 ids), calibration (3327 logische rijen) en coverage zijn "
                 "volledig verenigd. In shadow.jsonl ontbraken vijf rijen van Run A 19 sep uit "
                 "tak claude/zealous-edison-elu4ga; die zijn verenigd en in Stage 0 afgewikkeld."),
   "op_main": True,
 },
 "dagrapport": None,
}
json.dump(state, open(f"data/run-state/{DAY}-run-b.json", "w"), ensure_ascii=False, indent=1)
print("geschreven:", f"data/run-state/{DAY}-run-b.json")
print("statussen:", {k: v["status"] for k, v in state["competitions"].items()})

"""Stage 6 — vastleggen Run B 31 aug 2026: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-08-31"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-08-31T05:20:00+02:00"

res = json.load(open("tmp-run/rb_results.json"))
odds = json.load(open("tmp-run/rb_odds_all.json"))
stats = json.load(open("tmp-run/rb_stage3.json"))["stats"]
matches, vs = res["matches"], res["vroeg_seizoen"]

RUNLIJST = ["Czech First League (CZE)", "Greek Super League (GRE)", "Eliteserien (NOR)",
            "Allsvenskan (SWE)", "Croatian HNL (CRO)", "Hungarian NB I (HUN)",
            "Romanian SuperLiga (ROU)", "Segunda Division (ESP)", "Serie B (ITA)",
            "2. Bundesliga (GER)", "Swiss Super League (SUI)", "Austrian Bundesliga (AUT)",
            "Keuken Kampioen Divisie (NED)", "English League One (ENG)", "English League Two (ENG)",
            "Kategoria Superiore (ALB)", "Kosovo Superleague (KOS)"]

def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("ł", "l").replace("ß", "ss").replace("Ø", "o")
    return re.sub(r"[^a-z0-9]", "", s.lower())

def confidence(m):
    p = m["pick"]; rb = p["edge_robust_min"] or 0
    if m["tier"] == "FULL" and p["edge_pp"] >= 8 and rb >= 5: return "High"
    if p["edge_pp"] >= 5 and rb >= 3: return "Medium"
    return "Low"

def risk(m):
    p = m["pick"]
    if abs(p["edge_pp"]) >= 10 or p["odds"] >= 4.0: return "high"
    if p["edge_pp"] >= 5 or m["tier"] == "LIGHT": return "med"
    return "low"

bets = sorted([m for m in matches if m.get("bet")], key=lambda m: -m["pick"]["score"])
MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
short, n_light = set(), 0
for m in bets:
    if len(short) >= MAX_SHORT: break
    if m["tier"] == "LIGHT" and n_light >= MAX_LIGHT: continue
    short.add(m["match_id"]); n_light += m["tier"] == "LIGHT"

picks = []
for m in bets:
    p, c = m["pick"], m["competition"]
    b = stats[c]["prev"]
    seizoen = stats[c]["base_season"]
    lopend = c in {"Allsvenskan (SWE)"}
    ctx = m.get("context") or {}
    ho, aw = ctx.get("home", {}), ctx.get("away", {})
    if b["has_xg"]:
        basis = (f"Fotmob {c} {seizoen} xG — competitiegemiddelde {b['avg_xg']:.3f} xG per ploeg per "
                 f"duel over {b['n_teams']} ploegen ({'lopend seizoen' if lopend else 'vorig seizoen'})")
    else:
        basis = (f"Fotmob {c} {seizoen} doelpunten — geen xG bij Fotmob voor deze competitie, dus "
                 f"doelpunten voor/tegen als sterktemaat over {b['n_teams']} ploegen (LIGHT)")
    prob_sources = [
        basis,
        f"Fotmob {c} thuis/uit-splits — thuis {b['hg']:.3f} en uit {b['ag']:.3f} doelpunten per duel "
        f"(tweede methode, multiplicatief op het competitiegemiddelde)",
        f"Fotmob wedstrijdcontext ({ctx.get('lineup_type') or 'geen opstelling'}): "
        f"thuis {ho.get('out_count', 0)} afwezig · vorm {ho.get('form') or 'onbekend'}; "
        f"uit {aw.get('out_count', 0)} afwezig · vorm {aw.get('form') or 'onbekend'} — poort 7: {p['context_reason']}",
    ]
    if lopend:
        prob_sources.append("Geen vroeg-seizoenscorrectie: de teamsterkte komt hier uit het LOPENDE "
                            f"seizoen ({b['played']} speelronden), niet uit vorig seizoen")
    else:
        prob_sources.append(
            f"Vroeg-seizoenscorrectie x{vs['factor']:.4f} over {len(vs['competities'])} competities "
            f"({vs['speeldagen']} speeldagen, ruwe verhouding {vs['gepoold']:.4f}) — uitsluitend uit "
            f"xG-waarnemingen, geen enkele marktprijs (§2)")
    if stats[c]["prev"]["mp"] and stats[c]["prev"]["mp"] != stats[c]["prev"]["played"]:
        prob_sources.append(
            f"Let op splitsrondes in {c}: xG over {b['mp']} duels, tabel over {b['played']} — de twee "
            f"methodes zijn juist daarom naast elkaar gelegd (poort 5)")
    ru = m.get("runner_up")
    notes = (f"xG-methode {p['edge_xg']:+.2f} pp, splitsmethode {p['edge_split']:+.2f} pp, gemiddelde "
             f"{p['edge_pp']:+.2f} pp. Zwakste stand van het (shrink, rho)-grid {p['edge_robust_min']:+.2f} pp. "
             f"selection_score {p['score']} uit {m['candidates_evaluated']} doorgerekende selecties. "
             + (f"Tweede werd {ru['selection']} met score {ru['score']}." if ru else
                "Geen tweede selectie haalde alle zeven poorten."))
    if p["market"] == "Double Chance":
        notes += " Gekocht als de +0.5-handicaplijn uit de spreads-respons (§1a)."
    picks.append({
        "id": f"{DAY}-{slug(c)}-{slug(m['home'])}-{slug(m['away'])}-{slug(p['market'])}-{slug(p['selection'])[:26]}",
        "run": "B", "run_date": DAY,
        "kickoff": datetime.fromisoformat(m["kickoff_utc"].replace("Z", "+00:00")).astimezone(NL).isoformat(),
        "competition": c, "home": m["home"], "away": m["away"],
        "market": p["market"], "selection": p["selection"],
        "odds": p["odds"], "odds_source": p["odds_source"], "odds_captured_at": CAPTURED,
        "implied_prob": p["implied"], "my_prob": p["my_prob"], "edge_pp": p["edge_pp"],
        "data_tier": m["tier"], "confidence": confidence(m),
        "prob_sources": prob_sources,
        "shortlisted": m["match_id"] in short,
        "result": "pending", "notes": notes, "settled_at": None,
    })
    m["_pick_id"] = picks[-1]["id"]; m["_risk"] = risk(m)
    m["_confidence"] = picks[-1]["confidence"]; m["_shortlisted"] = m["match_id"] in short

bestaand = {json.loads(l)["id"] for l in open("data/picks.jsonl") if l.strip()}
nieuw = [p for p in picks if p["id"] not in bestaand]
with open("data/picks.jsonl", "a") as f:
    for p in nieuw:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")
print(f"picks toegevoegd: {len(nieuw)} (van {len(picks)}; {len(picks)-len(nieuw)} stonden er al)")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
n_none = sum(1 for m in matches if m["tier"] == "NONE")
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 3.0, "EDGE_THRESHOLD_LIGHT": 6.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00, "SETTLE_AFTER_HOURS": 12,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": (
        f"13 wedstrijden op de runlijst vandaag, in 7 van de 17 competities — maandag eind augustus, "
        f"de overige 10 hadden niets op de kalender. {13 - n_none} haalden de datadekkingspoort en zijn "
        f"doorgerekend, {n_none} kwamen op NONE uit (promovendus zonder historie in deze divisie en "
        f"zonder gemeten omrekenpaar). De cap van {res['afkapping']['cap']} is niet aangeraakt, dus er "
        f"is niets afgekapt."),
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = vs
state["credits"] = {
    "plafond": 9944,
    "gebruikt": 11,
    "split_budget": [3, 3],
    "bron": ("suggest_cap(19908, 1) = 9944 — 19.908 credits over bij aanvang (20K-plan), 1 dag tot de "
             "maandwissel, 2 runs per dag. Slechts 3 van de 7 competities met wedstrijden hebben een "
             "sportkey bij The Odds API, dus het plafond was nergens bindend."),
    "markten_gekocht": {"spreads": odds["bought"]["spreads"], "totals": odds["bought"]["totals"],
                        "btts": [m["match"] for m in matches
                                 if str(m["match_id"]) in odds["bought"]["btts"]]},
    "guard_report": ("6 van 9944 credits gebruikt in 6 aanroep(en) voor spreads+totals, plus 5 credits "
                     "voor vijf losse btts-events; 19.897 credits over"),
    "marktbalans_controle": ("geslaagd: 3 competities met een doelpuntenmarkt (OU) en 3 met een "
                            "uitkomstmarkt (AH/DNB/DC) bovenop het gratis 1X2 in alle 7 — de drie "
                            "inkoopbare competities kregen allebei de soorten, dus 3 op 3 in plaats "
                            "van de krappe 1-op-12 van 30 aug"),
}
by_comp = {}
for m in matches:
    by_comp.setdefault(m["competition"], []).append(m)
for comp, ms in by_comp.items():
    entry = {"status": "GEANALYSEERD", "matches": []}
    for m in ms:
        e = {"match": m["match"], "match_id": m["match_id"], "tier": m["tier"],
             "bet": bool(m.get("bet")), "kickoff_nl": m["kickoff_nl"], "kickoff_utc": m["kickoff_utc"],
             "markets_checked": m["markets_checked"], "lambdas": m.get("lambdas"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "market_counts": m.get("market_counts"),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "verplaatst", "promotie_poging"):
            if m.get(k): e[k] = m[k]
        if m.get("reason"): e["reden"] = m["reason"]
        if m.get("near_miss"): e["near_miss"] = m["near_miss"]
        if m.get("calibration"): e["calibration"] = m["calibration"]
        if m.get("bet"):
            e["pick_id"] = m["_pick_id"]; e["pick"] = m["pick"]
            e["risico"] = m["_risk"]; e["shortlisted"] = m["_shortlisted"]
        entry["matches"].append(e)
    mark(state, comp, entry)
for comp in RUNLIJST:
    if comp not in by_comp:
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": [],
                           "reden": "niets op de kalender vandaag (Fotmob-daglijst van 31 aug 2026)"})
save(state)
print("run-state weggeschreven")
json.dump({"short": sorted(short), "bets": [m["match"] for m in bets],
           "pick_ids": {m["match"]: m["_pick_id"] for m in bets},
           "risk": {m["match"]: m["_risk"] for m in bets}},
          open("tmp-run/rb_short.json", "w"), ensure_ascii=False, indent=1)

"""Stage 6 — vastleggen: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-08-31"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-08-31T04:20:00+02:00"

res = json.load(open("tmp-run/ra_results_v2.json"))
odds = json.load(open("tmp-run/ra_odds.json"))
s3 = json.load(open("tmp-run/ra_stage3.json"))
stats, fx = s3["stats"], s3["fixtures"]
matches, vs = res["matches"], res["vroeg_seizoen"]

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
    ctx = m.get("context") or {}
    ho, aw = ctx.get("home", {}), ctx.get("away", {})
    prob_sources = [
        f"Fotmob {c} vorig seizoen xG — competitiegemiddelde {b['avg_xg']:.3f} xG per ploeg per duel "
        f"over {b['teams']} ploegen",
        f"Fotmob {c} thuis/uit-splits — thuis {b['home_gpm']:.3f} en uit {b['away_gpm']:.3f} doelpunten "
        f"per duel (tweede methode, multiplicatief op het competitiegemiddelde)",
        f"Fotmob wedstrijdcontext ({ctx.get('lineup_type') or 'geen opstelling'}): "
        f"thuis {ho.get('out_count', 0)} afwezig · vorm {ho.get('form') or 'onbekend'}; "
        f"uit {aw.get('out_count', 0)} afwezig · vorm {aw.get('form') or 'onbekend'} — poort 7: {p['context_reason']}",
        f"Vroeg-seizoenscorrectie x{vs['factor']:.4f} over {len(vs['competities'])} competities "
        f"({vs['speeldagen']} speeldagen, ruwe verhouding {vs['gepoold']:.4f}) — uitsluitend uit "
        f"xG-waarnemingen, geen enkele marktprijs (§2)",
    ]
    if m.get("understat"):
        u = m["understat"]; r = u["rolling_xg_8"]
        rl = " · ".join(f"{k} {v[0]}/{v[1]} xG over {v[2]} duels" for k, v in r.items() if v)
        prob_sources.append(f"Understat {c} — tweede, onafhankelijk xG-model (§4): rollende xG {rl}")
    if m.get("promovendi"):
        for k, note in m["promovendi"].items():
            prob_sources.append(f"Promovendi-omrekening ({k}) — {note}")
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
        "run": "A", "run_date": DAY,
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

# De picks staan er al (eerste versie van 04:20); de twee die de nieuwe drempel niet halen zijn
# apart op `void` gezet. Hier alleen controleren dat wat we nu berekenen overeenkomt.
have = {json.loads(l)["id"] for l in open("data/picks.jsonl") if l.strip()}
missing = [p["id"] for p in picks if p["id"] not in have]
assert not missing, missing
print("picks gecontroleerd:", len(picks), "— alle 6 stonden al in picks.jsonl")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00, "SETTLE_AFTER_HOURS": 12,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": (
        "10 wedstrijden op de runlijst vandaag, in 6 van de 21 competities — maandag eind augustus, de "
        "overige 15 hadden niets op de kalender. Alle 10 haalden de datadekkingspoort en zijn "
        f"doorgerekend; de cap van {res['afkapping']['cap']} is niet aangeraakt, dus er is niets afgekapt. "
        "HERZIEN 31 aug ~04:50: EDGE_THRESHOLD_FULL van 3.0 naar 8.0 en LIGHT van 6.0 naar 16.0, op "
        "verzoek van de gebruiker en gemeten op 179 afgewikkelde picks (zie §0). Daardoor 6 bets in "
        "plaats van 8; Atalanta - Bologna (+7.33) en Besiktas - Corum FK (+7.37) zijn vóór de aftrap "
        "op void gezet."),
    "drempelverhoging": {
        "van": {"FULL": 3.0, "LIGHT": 6.0}, "naar": {"FULL": 8.0, "LIGHT": 16.0},
        "vervallen_picks": ["2026-08-31-serieaita-atalanta-bologna-doublechance-doublechancebolognaofgelij",
                            "2026-08-31-superligtur-besiktas-corumfk-btts-beideploegenscorenja"],
        "near_miss_ondergrens": {"FULL": 3.0, "LIGHT": 6.0},
        "waarom_ondergrens": ("de oude drempel blijft de ondergrens voor near_miss, anders valt precies "
                              "de groep die door deze verhoging wegvalt buiten shadow.jsonl en is niet "
                              "te meten of de verhoging klopte")},
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = vs
state["credits"] = {
    "plafond": odds["cap"], "gebruikt": odds["guard"]["spent"] if isinstance(odds["guard"], dict) else None,
    "split_budget": odds["split"],
    "bron": ("suggest_cap(19930, 1) — 19.930 credits over bij aanvang (20K-plan), 1 dag tot de "
             "maandwissel, 2 runs per dag"),
    "markten_gekocht": {"spreads": odds["bought"]["spreads"], "totals": odds["bought"]["totals"],
                        "btts": odds["bought"]["btts"]},
    "guard_report": odds["guard"],
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
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "understat", "verplaatst"):
            if m.get(k): e[k] = m[k]
        if m.get("reason"): e["reden"] = m["reason"]
        if m.get("near_miss"): e["near_miss"] = m["near_miss"]
        if m.get("calibration"): e["calibration"] = m["calibration"]
        if m.get("bet"):
            e["pick_id"] = m["_pick_id"]; e["pick"] = m["pick"]
            e["risico"] = m["_risk"]; e["shortlisted"] = m["_shortlisted"]
        entry["matches"].append(e)
    mark(state, comp, entry)
for comp, v in fx.items():
    if not v["matches"]:
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": [],
                           "reden": "niets op de kalender vandaag (Fotmob-daglijst)"})
save(state)
print("run-state weggeschreven")
json.dump({"short": sorted(short), "bets": [m["match"] for m in bets]},
          open("tmp-run/ra_short.json", "w"), ensure_ascii=False)

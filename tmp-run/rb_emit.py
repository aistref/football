"""Stage 6 — vastleggen: picks.jsonl, run-state, source-health."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts import fotmob
from scripts.ranking import max_shortlist

DAY = "2026-08-30"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-08-30T05:35:00+02:00"

res = json.load(open("tmp-run/rb_results.json"))
odds = json.load(open("tmp-run/rb_odds.json"))
stats = json.load(open("tmp-run/rb_stats.json"))
fx = json.load(open("tmp-run/rb_fixtures.json"))
matches = res["matches"]
vs = res["vroeg_seizoen"]

def slug(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace("ø", "o").replace("ł", "l").replace("ß", "ss").replace("Ø", "o")
    return re.sub(r"[^a-z0-9]", "", s.lower())

def confidence(m):
    p = m["pick"]
    rb = p["edge_robust_min"] or 0
    if m["tier"] == "FULL" and p["edge_pp"] >= 8 and rb >= 5:
        return "High"
    if p["edge_pp"] >= 5 and rb >= 3:
        return "Medium"
    return "Low"

def risk(m):
    p = m["pick"]
    if abs(p["edge_pp"]) >= 10 or p["odds"] >= 4.0:
        return "high"
    if p["edge_pp"] >= 5 or m["tier"] == "LIGHT":
        return "med"
    return "low"

bets = [m for m in matches if m.get("bet")]
bets.sort(key=lambda m: -m["pick"]["score"])
MAX_SHORT, MAX_LIGHT = max_shortlist(date.fromisoformat(DAY)), 2
short, n_light = set(), 0
for m in bets:
    if len(short) >= MAX_SHORT:
        break
    if m["tier"] == "LIGHT" and n_light >= MAX_LIGHT:
        continue
    short.add(m["match_id"])
    n_light += m["tier"] == "LIGHT"

comp_meta = {}
for m in matches:
    c = m["competition"]
    comp_meta.setdefault(c, {"n": 0})
    comp_meta[c]["n"] += 1

picks = []
for m in bets:
    p, c = m["pick"], m["competition"]
    s = stats[c]
    base = "cur" if c in ("Eliteserien (NOR)", "Allsvenskan (SWE)") else "prev"
    b = s[base]
    ctx = m.get("context") or {}
    ho, aw = ctx.get("home", {}), ctx.get("away", {})
    if m["tier"] == "FULL":
        src1 = (f"Fotmob {c} {'lopend seizoen' if base=='cur' else 'vorig seizoen'} xG — competitiegemiddelde "
                f"{b['avg_xg']:.3f} xG per ploeg per duel over {b['teams']} ploegen")
    else:
        src1 = (f"Fotmob {c} {'lopend seizoen' if base=='cur' else 'vorig seizoen'} doelpunten — geen xG bij "
                f"Fotmob voor deze competitie; teamsterkte op gescoorde/tegen doelpunten over {b['teams']} ploegen")
    prob_sources = [
        src1,
        f"Fotmob {c} thuis/uit-splits — thuis {b['hgpm']:.3f} en uit {b['agpm']:.3f} doelpunten per duel "
        f"(tweede methode, multiplicatief op het competitiegemiddelde)",
        f"Fotmob wedstrijdcontext ({ctx.get('lineup_type') or 'geen opstelling'}): "
        f"thuis {ho.get('out_count',0)} afwezig · vorm {ho.get('form') or 'onbekend'}; "
        f"uit {aw.get('out_count',0)} afwezig · vorm {aw.get('form') or 'onbekend'} — poort 7: {p['context_reason']}",
    ]
    if base != "cur":
        prob_sources.append(
            f"Vroeg-seizoenscorrectie x{vs['factor']:.4f} over {len(vs['competities'])} competities "
            f"({vs['speeldagen']} speeldagen, ruwe verhouding {vs['gepoold']:.4f}) — uitsluitend uit "
            f"xG-waarnemingen, geen enkele marktprijs (§2)")
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
    m["_pick_id"] = picks[-1]["id"]
    m["_risk"] = risk(m)
    m["_confidence"] = picks[-1]["confidence"]
    m["_shortlisted"] = m["match_id"] in short

with open("data/picks.jsonl", "a") as f:
    for p in picks:
        f.write(json.dumps(p, ensure_ascii=False) + "\n")
print("picks toegevoegd:", len(picks))

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 3.0, "EDGE_THRESHOLD_LIGHT": 6.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00, "SETTLE_AFTER_HOURS": 12,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": (
        "45 wedstrijden op de runlijst vandaag in 15 van de 17 competities. 7 vielen af op data_tier "
        "NONE (ten minste één ploeg zonder historie in deze divisie); 38 bleven over en daarvan zijn er "
        f"{res['afkapping']['cap']} doorgerekend — de cap. Afgekapt: {res['afkapping']['afgekapt']} duels, "
        "alle drie LIGHT en onderaan de datarijkdomsortering."),
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = vs
state["credits"] = {
    "plafond": odds["guard"]["cap"], "gebruikt": odds["guard"]["spent"],
    "over_na_de_run": odds["guard"]["remaining"],
    "bron": "suggest_cap(56, 2) — 56 over bij aanvang van deze run, 2 dagen tot de maandwissel, 2 runs per dag",
    "markten_gekocht": {"spreads": odds["bought"]["spreads"], "totals": odds["bought"]["totals"],
                        "btts": odds["bought"]["btts"]},
    "rotatie_totals": odds["totals_rotation"],
    "guard_report": odds["guard"]["report"],
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
        if m.get("afgekapt"):
            e["afgekapt"] = True
            e["markets_checked"] = {k: "AFGEKAPT — buiten MAX_DEEP_ANALYSES, niet doorgerekend"
                                    for k in ("1X2", "DC", "DNB", "AH", "OU", "BTTS")}
        if m.get("reason"):
            e["reden"] = m["reason"]
        if m.get("near_miss"):
            e["near_miss"] = m["near_miss"]
        if m.get("calibration"):
            e["calibration"] = m["calibration"]
        if m.get("bet"):
            e["pick_id"] = m["_pick_id"]
            e["pick"] = m["pick"]
            e["risico"] = m["_risk"]
            e["shortlisted"] = m["_shortlisted"]
        entry["matches"].append(e)
    mark(state, comp, entry)
for comp, v in fx.items():
    if not v["matches"]:
        mark(state, comp, {"status": "GEEN WEDSTRIJD", "matches": [],
                           "reden": "niets op de kalender vandaag (Fotmob-daglijst)"})
save(state)
print("run-state weggeschreven")
json.dump({"short": sorted(short), "bets": [m["match"] for m in bets]}, open("tmp-run/rb_short.json", "w"), ensure_ascii=False)

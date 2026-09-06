"""Stage 6 — vastleggen: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-06"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-06T04:25:00+02:00"

TOELICHTING = (
    "39 wedstrijden op de runlijst vandaag, in 13 van de 21 competities; de acht toernooien "
    "(UCL/UEL/UECL, FA Cup, League Cup, Coppa Italia, KNVB Beker, DFB Pokal) hadden niets op "
    "de kalender. De cap van 55 (zondag) is niet geraakt: nul duels afgekapt, alle 39 zijn "
    "doorgerekend voor zover ze dekking hadden. 38 van de 39 kwamen door de datadekkingspoort "
    "(24 FULL, 14 LIGHT); alleen Sonderjyske - AC Horsens viel op NONE omdat de omrekening van "
    "AC Horsens buiten het gemeten bereik van conversion_in_range ligt. Samen 595 selecties "
    "doorgerekend over alle zes de markten, en nul bets. "
    "Dit is de eerste run onder de vier regelwijzigingen van 5 september: 1X2 op de beste prijs, "
    "de 80/20-weging, de herijking op uitslagen en de lichte poort 8. De herijking is hier de "
    "beslissende: ze staat op 602 afgerekende gevallen (a=0.909, b=-0.445) en haalt rond de 11 "
    "procentpunt van elke kansschatting af, precies zoals _shared-rules.md 1g voorspelt. Vier "
    "kandidaten hielden daarna nog een positieve edge over, maar geen enkele haalde de 8.0 pp "
    "voor FULL of de 16.0 pp voor LIGHT. Poort 8 hield vandaag niets tegen - onder de herijkte "
    "kansen komt er nauwelijks nog een underdog-selectie tot aan die poort."
)

OMREKENINGEN = {
    "aanleiding": (
        "Vijftien ploegen stonden vorig seizoen niet in de stand van de competitie van vandaag: "
        "promovendi (Frosinone, Venezia, Monza, Malaga, Troyes, Cambuur, ADO Den Haag, "
        "Academico Viseu, Kortrijk, SK Beveren, Corum FK, Amed Sportif, St. Johnstone, "
        "AC Horsens, Slask Wroclaw) en een degradant (Wolves). Veertien daarvan zijn omgerekend "
        "en kwamen daarmee op LIGHT - een omgerekende ploeg is nooit FULL, want RESIDUAL_SPREAD "
        "houdt na correctie nog onzekerheid over. AC Horsens viel buiten het gemeten bereik van "
        "conversion_in_range en kwam daarmee op NONE: geen bet, conform 4."),
    "naamkoppeling": (
        "Twee ploegen liepen bij de eerste doorloop vast op de naamkoppeling, en ze zijn van "
        "verschillende soort. (1) 'Man United' is dezelfde val als 'Man City' gisteren: na _DROP "
        "valt {united} weg en houdt de daglijstnaam {man} over tegen {manchester} in de "
        "standtabel. Everton - Man United ging daardoor ten onrechte de promovendi-omrekening in "
        "en kwam uit op NONE, terwijl Manchester United gewoon in de Premier League-stand van "
        "2025/2026 staat - achtste geval van deze soort. (2) 'FC Kobenhavn' is nieuw en raakt "
        "niet de tier maar de PRIJZEN: Fotmob schrijft de Deense naam, The Odds API en "
        "BetExplorer de Engelse 'FC Copenhagen', en {kobenhavn} deelt geen token met "
        "{copenhagen}. OB - FC Kobenhavn stond op FULL en kreeg toch nul selecties doorgerekend "
        "omdat find_event de wedstrijd bij geen enkele bron terugvond. Beide aliassen toegevoegd "
        "in tmp-run/ra_names.py; daarna zijn beide duels alsnog volledig doorgerekend (14 "
        "selecties elk) en is de BTTS-markt voor OB - FC Kobenhavn nagekocht (2 credits)."),
    "toegepast_op": ["Frosinone", "Venezia", "Monza", "Malaga", "Troyes", "Wolves", "Cambuur",
                     "ADO Den Haag", "Academico Viseu", "Kortrijk", "SK Beveren", "Corum FK",
                     "Amed Sportif", "St. Johnstone", "Slask Wroclaw"],
    "geweigerd": ["AC Horsens (up, buiten het gemeten bereik van conversion_in_range)"],
}

CREDITBRON = (
    "suggest_cap(19749, 25) = 394 - 19.749 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 251 gebruikt deze maand), 25 dagen tot de maandwissel, 2 runs per dag. Het "
    "plafond is ruim genoeg voor 3 credits per competitie, dus de bulk-aanroep is voor alle 13 "
    "competities met een sportkey gedaan met h2h EN spreads EN totals (1a, regel van 5 sep): "
    "dat levert vijf van de zes markten in een keer en zet 1X2 op de beste prijs in plaats van "
    "op het BetExplorer-marktgemiddelde. Gemeten over 37 duels leverde dat +5.02% betere koers "
    "op dan het marktgemiddelde. BTTS is voor alle 39 duels gekocht (2 credits per wedstrijd), "
    "want de cap van 55 kapte vandaag niets af. Totaal 79 van 394 credits."
)

res = json.load(open("tmp-run/ra6_results.json"))
odds = json.load(open("tmp-run/ra6_odds.json"))
s3 = json.load(open("tmp-run/ra6_stage3.json"))
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
                "Geen tweede selectie haalde alle zeven poorten; sterkste afgewezen alternatief: "
                + (f"{rr['selection']} @ {rr['odds']} ({rr['edge_pp']:+.2f} pp, viel af op "
                   f"{rr['failed_gate']})." if (rr := m.get("runner_up_rejected")) else "geen.")))
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

have = {json.loads(l)["id"] for l in open("data/picks.jsonl") if l.strip()}
nieuw = [p for p in picks if p["id"] not in have]
with open("data/picks.jsonl", "a") as fh:
    for p in nieuw:
        fh.write(json.dumps(p, ensure_ascii=False) + "\n")
print(f"picks toegevoegd: {len(nieuw)} van {len(picks)} ({len(picks) - len(nieuw)} stonden er al)")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("a", date.fromisoformat(DAY))
state["parameters"] = {
    "MAX_DEEP_ANALYSES": res["afkapping"]["cap"], "MAX_SHORTLIST": MAX_SHORT,
    "EDGE_THRESHOLD_FULL": 8.0, "EDGE_THRESHOLD_LIGHT": 16.0, "MAX_LIGHT_IN_SHORTLIST": MAX_LIGHT,
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00, "POORT_8_UNDERDOG": "licht sinds 5 sep 2026 — sides.UNDERDOG_FLOOR = 0.35",
    "XG_WEIGHT": 0.80, "CREDIBILITY_K": 8, "HERIJKING": "recalibrate.apply, fit op uitslagen", "SETTLE_FALLBACK_HOURS": 2.0,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": TOELICHTING,
    "omrekeningen": OMREKENINGEN,
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = vs
state["credits"] = {
    "plafond": odds["cap"], "gebruikt": odds["guard"]["spent"] if isinstance(odds["guard"], dict) else None,
    "split_budget": odds["split"],
    "bron": CREDITBRON,
    "markten_gekocht": {"bulk_h2h_spreads_totals": odds["bought"]["spreads"],
                        "h2h": odds["bought"]["h2h"], "totals": odds["bought"]["totals"],
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
             "per_market": m.get("per_market"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "understat", "verplaatst", "poort8_geblokkeerd", "afgekapt",
                  "seizoensweging", "odds_1x2", "odds_1x2_best", "beste_prijs_winst_pct"):
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
          open("tmp-run/ra6_short.json", "w"), ensure_ascii=False)

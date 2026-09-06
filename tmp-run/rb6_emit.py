"""Run B, 6 sep 2026 — Stage 6: vastleggen in picks.jsonl en data/run-state/."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-06"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-06T05:20:00+02:00"

TOELICHTING = '39 wedstrijden op de runlijst vandaag, in 13 van de 17 competities. Vier hadden niets op de kalender: van de Austrian Bundesliga stond alleen de Cup op de daglijst (8 duels, staat niet op de runlijst), English League One en League Two speelden geen van beide, en van Kosovo staat er nog steeds geen enkele competitie in de Fotmob-daglijst - ongewijzigd sinds 13 aug 2026. De cap van 55 (zondag) is niet geraakt: nul duels afgekapt, alle 39 zijn beoordeeld. 32 van de 39 kwamen door de datadekkingspoort (16 FULL, 16 LIGHT), samen 378 selecties over alle zes de markten, en nul bets. De zeven op NONE vallen in twee groepen, en geen van beide is een storing. Vier duels hebben een ploeg die vorig seizoen in de divisie eronder speelde in een land waarvoor promotion.py geen divisiepaar kent (Kalamata in Griekenland, Rudes in Kroatie, Kispest Honved in Hongarije, Corvinul Hunedoara in Roemenie). Drie duels hebben een ploeg die uit de DERDE divisie is gepromoveerd - LR Vicenza en Arezzo uit de Serie C, VfL Osnabruck uit de 3. Liga - en promotion.TIER2 kent voor Serie B en 2. Bundesliga geen divisie eronder. Vijf ploegen zijn wel omgerekend en kwamen daarmee op LIGHT. Dat er nul bets uitkomen ligt aan de herijking van 1g, net als bij Run A vanochtend. Ze staat op 602 afgerekende gevallen (a=0.909, b=-0.445) en haalt rond de tien procentpunt van elke kansschatting af. De hoogste edge van de hele run na herijking is +5.84 pp, en die selectie valt bovendien buiten de koersband; de beste kandidaat binnen de band staat op +5.79 pp bij een LIGHT-drempel van 16.0. Ter vergelijking: dezelfde selectie zonder herijking stond op +16.19 pp op de xG-methode. Poort 8 hield vandaag niets tegen, en er is geen enkele near miss - dat laatste is zelf een waarneming, zie het runrapport.'

OMREKENINGEN = {'aanleiding': 'Elf ploegen stonden vorig seizoen niet in de stand van de competitie van vandaag. Vijf zijn omgerekend en kwamen daarmee op LIGHT - een omgerekende ploeg is nooit FULL, want RESIDUAL_SPREAD houdt na correctie nog onzekerheid over: Orgryte (Superettan -> Allsvenskan, gepoolde factor), Real Oviedo (La Liga -> LaLiga2, gemeten SP1/SP2), Pisa en Cremonese (Serie A -> Serie B, gemeten I1/I2) en FC Heidenheim (Bundesliga -> 2. Bundesliga, gemeten D1/D2). Zes gingen naar NONE, in twee soorten, en geen van beide is een meetfout: (1) Kalamata, Rudes, Kispest Honved en Corvinul Hunedoara spelen in een competitie waarvoor promotion.py geen divisie boven of onder kent - er is dus geen gemeten gat om mee om te rekenen; (2) LR Vicenza, Arezzo en VfL Osnabruck komen uit de DERDE divisie (Serie C respectievelijk 3. Liga), en TIER2 kent voor Serie B en 2. Bundesliga geen divisie eronder. Beide keren is NONE de eerlijke uitkomst conform 4: buiten het gemeten bereik geen bet.', 'naamkoppeling': "Twee reparaties, allebei aan tmp-run/ra_names.py en allebei nodig voor de PRIJZEN en niet voor de tier. (1) Alias 'NK Lokomotiva' -> 'Lok. Zagreb': Fotmob schrijft de ploeg voluit (zo staat hij ook in de HNL-stand, daar viel niets te koppelen), BetExplorer kort af. Na _DROP blijft {nk, lokomotiva} tegen {lok, zagreb} over - geen gedeeld token - en de naamgelijkenis over het hele paar komt op 0.48, onder de vloer van 0.62. Slaven - NK Lokomotiva kreeg daardoor nul selecties doorgerekend terwijl de Croatian HNL wel een 1X2-rij bij BetExplorer had; na de alias zijn het er drie. (2) norm() slaat nu dubbele spaties plat. Een punt wordt daar een spatie, dus 'Lok. Zagreb' kwam op 'lok  zagreb' uit en was niet gelijk aan de vorm waarin een alias geschreven staat - norm was niet idempotent.", 'toegepast_op': ['Örgryte', 'Real Oviedo', 'Pisa', 'Cremonese', 'FC Heidenheim'], 'geweigerd': ['Kalamata (geen divisiepaar bekend voor de Greek Super League)', 'Rudeš (geen divisiepaar bekend voor de Croatian HNL)', 'Kispest Honvéd (geen divisiepaar bekend voor de Hungarian NB I)', 'Corvinul Hunedoara (geen divisiepaar bekend voor de Romanian SuperLiga)', 'LR Vicenza (uit de Serie C; TIER2 kent geen divisie onder de Serie B)', 'Arezzo (uit de Serie C; TIER2 kent geen divisie onder de Serie B)', 'VfL Osnabrück (uit de 3. Liga; TIER2 kent geen divisie onder de 2. Bundesliga)']}

CREDITBRON = 'suggest_cap(19671, 25) = 393 - 19.671 credits over volgens api_check.py van deze run (20K-plan, 329 gebruikt deze maand), 25 dagen tot de maandwissel, 2 runs per dag. Zeven van de dertien competities met wedstrijden hebben een sportkey bij The Odds API; voor Tsjechie, Kroatie, Hongarije, Roemenie, de Eerste Divisie en Albanie bestaat er geen, en daar is BetExplorer de enige 1X2-bron (marktgemiddelde, bookmaker niet herleidbaar). split_budget(393, 7) geeft 7 spreads / 7 totals, en het plafond is ruim genoeg voor 3 credits per competitie, dus alle zeven kregen de bulk-aanroep met h2h EN spreads EN totals (1a, regel van 5 sep): vijf van de zes markten in een keer, met 1X2 op de beste prijs. Gemeten over 21 duels leverde dat gemiddeld +7.20% betere koers op dan het BetExplorer-marktgemiddelde (mediaan +6.67%, uitschieter +16.24%). BTTS is voor 25 duels gekocht a 1 credit. Totaal 46 van 393 credits in 32 aanroepen.'

res = json.load(open("tmp-run/rb6_results.json"))
odds = json.load(open("tmp-run/rb6_odds.json"))
s3 = json.load(open("tmp-run/rb6_stage3.json"))
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

have = {json.loads(l)["id"] for l in open("data/picks.jsonl") if l.strip()}
nieuw = [p for p in picks if p["id"] not in have]
with open("data/picks.jsonl", "a") as fh:
    for p in nieuw:
        fh.write(json.dumps(p, ensure_ascii=False) + "\n")
print(f"picks toegevoegd: {len(nieuw)} van {len(picks)} ({len(picks) - len(nieuw)} stonden er al)")

# ---------- run-state -------------------------------------------------------------------------
from scripts.progress import load_or_start, mark, save
state = load_or_start("b", date.fromisoformat(DAY))
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
                  "seizoensweging", "odds_1x2", "odds_1x2_best", "beste_prijs_winst_pct",
                  "zonder_herijking"):
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
          open("tmp-run/rb6_short.json", "w"), ensure_ascii=False)

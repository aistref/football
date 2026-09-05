"""Stage 6 — vastleggen: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-05"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-05T04:25:00+02:00"

res = json.load(open("tmp-run/ra5_results.json"))
odds = json.load(open("tmp-run/ra5_odds.json"))
s3 = json.load(open("tmp-run/ra5_stage3.json"))
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
    "MIN_ODDS": 1.30, "MAX_ODDS": 6.00, "POORT_8_UNDERDOG": "aan sinds 4 sep 2026", "SETTLE_FALLBACK_HOURS": 2.0,
    "afgekapt": res["afkapping"]["afgekapt"],
    "toelichting": (
        "55 wedstrijden op de runlijst vandaag, in 13 van de 21 competities — de eerste volle "
        "zaterdag na de interlandbreak, en de drukste rundag tot nu toe. Premier League 7, "
        "Serie A 3, La Liga 3, Bundesliga 6, Ligue 1 3, Championship 11, Eredivisie 4, "
        "Primeira Liga 4, Belgian Pro League 4, Super Lig 2, Scottish Premiership 4, "
        "Danish Superliga 1, Ekstraklasa 3; de acht toernooien (UCL/UEL/UECL, FA Cup, League "
        "Cup, Coppa Italia, KNVB Beker, DFB Pokal) hadden niets op de kalender. "
        f"De cap van {res['afkapping']['cap']} (zaterdag) is voor het eerst deze maand echt "
        f"geraakt: {res['afkapping']['afgekapt']} duels zijn afgekapt, waarvan er twee "
        "(Hull - Aston Villa en Erzurumspor - Konyaspor) sowieso op NONE zouden zijn uitgekomen, "
        "dus achttien echte analyses. Van de 35 doorgerekende duels haalden er zes een bet; "
        "vijf uit Over/Under en een uit BTTS. Poort 8 hield twee selecties tegen "
        "(Royal Antwerp +0.25 en Motherwell +1.25) die zonder die poort gepubliceerd zouden zijn."),
    "omrekeningen": {
        "aanleiding": (
            "Zeventien ploegen stonden vorig seizoen niet in de stand van de competitie van "
            "vandaag: veertien promovendi (Coventry, Hull, Racing Santander, Deportivo A Coruna, "
            "Elversberg, Paderborn, Schalke 04, Le Mans, Lincoln, Bolton, Cardiff, Willem II, "
            "Maritimo, Erzurumspor, Wisla Krakow) en twee degradanten (Burnley, West Ham). "
            "Vijftien daarvan vielen buiten MAX_DEEP_ANALYSES en zijn dus niet omgerekend; van "
            "de twee die wel aan de beurt kwamen, kwamen Hull en Erzurumspor buiten het gemeten "
            "bereik van conversion_in_range uit en daarmee op NONE - geen bet, conform §4."),
        "naamkoppeling": (
            "Drie ploegen gingen bij de eerste doorloop ten onrechte de omrekening in, alle drie "
            "dezelfde val als eerder: de Fotmob-daglijst kort de naam zo af dat er geen enkel "
            "token overblijft dat de standtabel ook heeft. 'Man City' houdt {man} over tegen "
            "{manchester}, 'Nottm Forest' {nottm, forest} tegen {nottingham, forest} en "
            "'M'gladbach' {m, gladbach} tegen {borussia, monchengladbach}. Alle drie stonden "
            "gewoon in de stand van 2025/2026. Aliassen toegevoegd in tmp-run/ra_names.py. "
            "Vijfde tot en met zevende geval na sheff utd/wolves/west ham (1 sep), "
            "qpr/west brom (2 sep), hearts (3 sep) en psg (4 sep)."),
        "brondefect": (
            "Losstaand van de naamkoppeling, en zwaarder: de xG-lijsten van Fotmob schrijven "
            "clubnamen zonder accenten en de stand mét, waardoor scripts/fotmob.py een club in "
            "twee halve tabelrijen zette - de ene met xg/xga/mp en zonder stand, de andere met "
            "de stand en zonder xG. De run koppelt op de daglijstnaam en die heeft accenten, "
            "dus hij pakte structureel de helft zonder xG. Zes ploegen in drie competities van "
            "deze runlijst: Atletico Madrid, Deportivo Alaves, Famalicao, Vitoria de Guimaraes, "
            "Standard Liege en RAAL La Louviere. Drie duels van vandaag klapten daarop eruit met "
            "een KeyError. Opgelost in scripts/fotmob.py met _merge_accent_duplicates(); "
            "La Liga ging van 22 naar 20 tabelsleutels, Liga Portugal van 20 naar 18 en de "
            "Belgische competitie van 18 naar 16, en geen enkele ploeg staat nog zonder xG."),
        "toegepast_op": [],
        "geweigerd": ["Hull City (up, buiten het gemeten bereik van conversion_in_range)",
                      "Erzurumspor FK (up, buiten het gemeten bereik van conversion_in_range)"],
    },
    "afkapping": res["afkapping"],
}
state["vroeg_seizoen"] = vs
state["credits"] = {
    "plafond": odds["cap"], "gebruikt": odds["guard"]["spent"] if isinstance(odds["guard"], dict) else None,
    "split_budget": odds["split"],
    "bron": ("suggest_cap(19844, 26) — 19.844 credits over volgens api_check.py van vanochtend "
             "(20K-plan, 156 gebruikt deze maand), 26 dagen tot de maandwissel, 2 runs per dag. "
             "BTTS is bewust alleen gekocht voor de 35 duels binnen MAX_DEEP_ANALYSES: die markt "
             "kost 2 credits per wedstrijd, en voor alle 55 zou een vijfde daarvan naar duels "
             "gaan die de cap toch afkapt."),
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
             "per_market": m.get("per_market"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "understat", "verplaatst", "poort8_geblokkeerd", "afgekapt"):
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
          open("tmp-run/ra5_short.json", "w"), ensure_ascii=False)

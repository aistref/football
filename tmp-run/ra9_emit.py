"""Stage 6 — vastleggen: picks.jsonl, run-state."""
import json, sys, re, unicodedata
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0, "tmp-run")
from scripts.ranking import max_shortlist

DAY = "2026-09-09"
NL = timezone(timedelta(hours=2))
CAPTURED = "2026-09-09T04:18:00+02:00"

TOELICHTING = (
    "14 wedstrijden op de runlijst vandaag, in 6 van de 21 competities: de Champions League (6), "
    "de Championship (3), de Scottish Premiership (2), de Eredivisie (1), de Primeira Liga (1) en "
    "de League Cup (1). De andere vijftien hadden niets op de kalender - dat is GEEN WEDSTRIJD, "
    "geen storing. De cap van 40 (woensdag) is bij lange na niet geraakt: nul duels afgekapt. "
    "Twaalf kwamen door de datadekkingspoort (6 FULL, 6 LIGHT) en zijn over alle zes de markten "
    "doorgerekend: samen 182 selecties, nul bets. "
    "Het verschil met gisteren zit in de Champions League. Tot en met 8 sep gingen kruis-grensduels "
    "blind naar NONE omdat het model het krachtsverschil tussen twee nationale competities niet "
    "kende; scripts/interleague.py rekent beide ploegen sinds die avond om naar de Europese schaal "
    "met een op 2111 Europese duels gemeten factor per competitie. Dit is de eerste run waarin die "
    "regel echt werk doet: vier van de zes UCL-duels zijn doorgerekend op LIGHT (nooit FULL - de "
    "omrekening haalt de systematische fout eruit, niet de onzekerheid). De twee andere blijven "
    "NONE, en allebei om een reden die de module zelf noemt: Slovan Bratislava speelt in Slowakije "
    "en daar is onder de 40 Europese duels geen factor gemeten, en Arsenal komt na omrekening uit "
    "op een verdediging van 0.373 tegen een gemeten ondergrens van 0.388 - dat is de Coventry-val "
    "waar in_range voor bestaat. "
    "Anders dan gisteren gaf de herijking van par. 1g vandaag WEL de doorslag, en precies bij een "
    "van die omgerekende duels. Bij VfB Stuttgart - Viking haalden drie Over/Under-selecties alle "
    "acht de poorten op de ruwe schaal (de sterkste: Under 4 @ 1.87, ruw +20.33 pp, en Under 3.5 "
    "@ 2.38, ruw +23.02 pp) en geen enkele op de herijkte (+9.33 respectievelijk +11.38 pp tegen "
    "een LIGHT-drempel van 16.0). Er gaat dus een schaduwregel met failed_gate herijking naar het "
    "logboek; over enkele weken staat daar een ROI onder. Dat dit juist het duel is waar het model "
    "het verst van de markt af staat, is exact het patroon waar par. 1g voor waarschuwt: de "
    "grootste geclaimde edge is de grootste modelfout. "
    "Bij de FULL-duels was het niet spannend: de hoogste herijkte edge binnen de koersband is "
    "-0.30 pp (Chelsea - Leeds, 1X2 Leeds @ 5.312) tegen een drempel van 8.0. Op de ruwe schaal is "
    "het hoogste FULL-cijfer +11.02 pp (Moreirense +2 @ 2.02), maar die selectie sneuvelde daar op "
    "poort 8: de markt zet Moreirense onder de UNDERDOG_FLOOR van 0.35. De fit staat op 613 "
    "afgerekende gevallen (a=0.934, b=-0.444, trefkans 41.4% tegen een geclaimd gemiddelde van "
    "51.8%)."
)

OMREKENINGEN = {
    "aanleiding": (
        "Twee soorten omrekening deze run. (1) Kruis-grens, nieuw sinds 8 sep: de zes "
        "Champions League-duels zijn stuk voor stuk door interleague.convert_team gehaald, dat de "
        "binnenlandse aanval- en verdedigingsverhouding van vorig seizoen omrekent naar de "
        "Europese schaal en de twee ploegen daarna in interleague.reference_league() tegen elkaar "
        "zet. Vier duels lukten (Barcelona - Feyenoord, VfB Stuttgart - Viking, Liverpool - "
        "Atletico Madrid, Sporting CP - Galatasaray), twee niet. (2) Binnen een land: "
        "St. Johnstone stond niet in de Scottish Premiership van 2025/2026 en is omgerekend uit "
        "de Championship (SCO) met de gemeten SC0/SC1-factor. In beide gevallen geldt dat een "
        "omgerekende ploeg nooit FULL is: die duels staan op LIGHT, waar 16.0 pp edge nodig is "
        "in plaats van 8.0."),
    "naamkoppeling": (
        "Geen enkele ploeg liep vast op de naamkoppeling: ra_names.py koppelde alle veertien duels "
        "bij Fotmob en alle twaalf doorgerekende ook bij The Odds API en BetExplorer. De twee "
        "duels zonder BetExplorer-marktgemiddelde (PSG - Slovan Bratislava en Napoli - Arsenal) "
        "eindigen op NONE en hebben daarom sowieso geen kalibratieblok."),
    "toegepast_op": ["Barcelona", "Feyenoord", "VfB Stuttgart", "Viking FK", "Liverpool",
                     "Atletico Madrid", "Sporting CP", "Galatasaray", "St. Johnstone"],
    "geweigerd": [
        "Slovan Bratislava (PSG - Slovan Bratislava): SVK heeft minder dan interleague.MIN_MATCHES "
        "= 40 Europese duels in de meting, dus geen gemeten competitiefactor -> NONE, geen bet",
        "Arsenal (Napoli - Arsenal): omgerekende verdediging 0.373 buiten het waargenomen bereik "
        "0.388-1.446 van interleague.in_range -> NONE, geen bet",
    ],
}

CREDITBRON = (
    "suggest_cap(19550, 22) = 443 - 19.550 credits over volgens api_check.py van vanochtend "
    "(20K-plan, 450 gebruikt deze maand), 22 dagen tot de maandwissel, 2 runs per dag. Het "
    "plafond is ruim genoeg voor 3 credits per competitie, dus de bulk-aanroep (h2h + spreads + "
    "totals, par. 1a) is voor alle 6 competities met een sportkey gedaan: dat levert vijf van de "
    "zes markten in een keer en zet 1X2 op de beste prijs in plaats van op het BetExplorer-"
    "marktgemiddelde. Gemeten over de twaalf doorgerekende duels leverde dat gemiddeld +10.03% "
    "betere koers op dan het marktgemiddelde (mediaan +7.25%). BTTS is voor alle 12 duels met "
    "dekking gekocht. De marktbalans-controle van par. 1a slaagt ruim: alle zes competities "
    "hebben zowel een uitkomstmarkt als een doelpuntenmarkt, dus 6 op 6 in plaats van 1 op 12. "
    "Totaal 30 van 443 credits."
)

res = json.load(open("tmp-run/ra9_results.json"))
odds = json.load(open("tmp-run/ra9_odds.json"))
s3 = json.load(open("tmp-run/ra9_stage3.json"))
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
    # Een competitie waarin GEEN enkel duel de datadekkingspoort haalde, is niet geanalyseerd
    # maar buiten datadekking gevallen (§5). Dat geldt vandaag voor de Champions League: zes
    # duels, alle zes kruis-grens, nul doorgerekend.
    doorgerekend = [m for m in ms if m["tier"] != "NONE"]
    entry = {"status": "GEANALYSEERD" if doorgerekend else "BUITEN DATADEKKING", "matches": []}
    if not doorgerekend:
        entry["reden"] = (f"{len(ms)} wedstrijd(en) vandaag, geen enkele met een bruikbare "
                          f"onafhankelijke kansinput op het niveau waarop gespeeld wordt — "
                          f"zie 'reden' per duel")
    for m in ms:
        e = {"match": m["match"], "match_id": m["match_id"], "tier": m["tier"],
             "bet": bool(m.get("bet")), "kickoff_nl": m["kickoff_nl"], "kickoff_utc": m["kickoff_utc"],
             "markets_checked": m["markets_checked"], "lambdas": m.get("lambdas"),
             "per_market": m.get("per_market"),
             "datarijkdom": {"score": m["richness"], "deelscores": m.get("richness_parts")},
             "context": m.get("context"), "candidates_evaluated": m.get("candidates_evaluated", 0),
             "all_candidates": m.get("all_candidates", [])}
        for k in ("promovendi", "kruis_grens", "understat", "verplaatst", "poort8_geblokkeerd",
                  "afgekapt", "seizoensweging", "odds_1x2", "odds_1x2_best",
                  "beste_prijs_winst_pct", "zonder_herijking"):
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
          open("tmp-run/ra9_short.json", "w"), ensure_ascii=False)

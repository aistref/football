"""Bouwt runs/2026-10-21-run-b.md: de vaste tabellen uit de data, de prozastukken hieronder."""
import json

st = json.load(open("data/run-state/2026-10-21-run-b.json"))
res = json.load(open("tmp-run/rb_oct21_results.json"))
top = json.load(open("tmp-run/rb_oct21_top_b.json"))
bev = json.load(open("tmp-run/rb_oct21_bevestiging.json"))
P = st["parameters"]

TOEL = {
 "English League One (ENG)": "1 duel (Reading – Leyton Orient), 21:00 NL. xG bij Fotmob en beide ploegen in de stand van 2025/2026, dus `FULL` zonder omrekening. Nul regels: de twee methodes wijzen hier lijnrecht tegengesteld.",
 "MLS (USA)": "1 duel (FC Cincinnati – DC United), 01:00 NL in de nacht naar 22 oktober — de nachtband waarvoor `runwindow.py` bestaat. xG bij Fotmob, `FULL`. Hier komt de enige regel van de run uit.",
}

# ---------- dekkingstabel ----------
dek = ["| Competitie | Status | Toelichting |", "|---|---|---|"]
actief = []
for comp, blok in st["competitions"].items():
    status = blok.get("status", "GEEN WEDSTRIJD")
    if status == "GEANALYSEERD":
        actief.append(comp)
        n = len(blok.get("matches") or [])
        dek.append(f"| {comp} | `GEANALYSEERD` | {TOEL.get(comp, '')} ({n} duels) |")
for comp, blok in st["competitions"].items():
    if blok.get("status") != "GEANALYSEERD":
        dek.append(f"| {comp} | `GEEN WEDSTRIJD` | niets op de kalender in het inzetvenster |")

# ---------- bevestiging ----------
bevr = ["| Competitie | Fotmob | BetExplorer | Eens |", "|---|---|---|---|"]
for naam in sorted(bev):
    v = bev[naam]
    bevr.append(f"| {naam} | {v.get('fotmob')} | {v.get('betexplorer')} | "
                f"{'ja' if v.get('eens') else '**nee**'} |")

# ---------- topselectie ----------
LAT = {"FULL": 8.0, "LIGHT": 16.0}
tops = ["| # | Bet | Prob | Edge | Score | Risico | Waarom deze |", "|---|---|---|---|---|---|---|"]
RISK = {0: "High"}
WAAROM = {
 0: ("De enige van 29 doorgerekende selecties die alle negen poorten haalt, en hij haalt zowel "
     "de lat van 8,0 als de verzwaarde lat van 10,0 die poort 9 op een FULL-Under legt. "
     "`bet_beide` = TRUE (ruw +12,59 pp). Risicoklasse **High** en niet Medium, en dat is een "
     "eigen oordeel bovenop de score: de frequentietelling en Pinnacle spreken deze bet beide "
     "tegen (zie de twee paragrafen hieronder). De eerstvolgende selectie — Under 3,75 op "
     "hetzelfde duel, score 7,513 — is dezelfde mening in een naburige markt en geen tweede "
     "bevinding; de beste selectie van het ándere duel staat op +2,14 pp."),
}
for i, r in enumerate(top["herijkt"]):
    lat = LAT[r["tier"]]
    gehaald = "**gehaald**" if r["edge_pp"] >= lat else "**niet gehaald**"
    tops.append(
        f"| {i+1} | {r['match']} · **{r['market']} — {r['selection']}** @{r['odds']} "
        f"({r['odds_source'].replace('The Odds API ', '').strip('()')}) · {r['kickoff_nl']} NL · "
        f"`{r['tier']}` | {r['prob']*100:.1f}% | **{r['edge_pp']:+.2f} pp** (lat {lat:.1f} — "
        f"{gehaald}) | {r['score']} | {RISK[i]} | {WAAROM[i]} |")

ruw = ["| # | Wedstrijd | Selectie | Kans | Edge (ruw) | Score | Viel af op |", "|---|---|---|---|---|---|---|"]
for i, r in enumerate(top["ruw"]):
    ruw.append(f"| {i+1} | {r['match']} | {r['selection']} @{r['odds']:.2f} | {r['prob']*100:.1f}% | "
               f"{r['edge_pp']:+.2f} pp | {r['score']} | {r.get('failed_gate') or '—'} |")

# ---------- net niet ----------
nn = ["| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |",
      "|---|---|---|---|---|---|"]
rows = []
for comp, blok in st["competitions"].items():
    for m in blok.get("matches") or []:
        x = m.get("near_miss") or m.get("near_miss_gepubliceerd")
        if x:
            rows.append((m["match"], x, bool(m.get("near_miss_gepubliceerd"))))
for match, x, pub in sorted(rows, key=lambda r: -(r[1].get("edge_xg") or -99)):
    mk = x["market"].replace("Over/Under — ", "").replace("BTTS — ", "BTTS ").replace(
         "Double Chance — Double Chance — ", "DC — ").replace("1X2 — ", "").replace(
         "Asian Handicap — ", "AH ")
    nn.append(f"| {match} | {mk} @{x['odds']:.4g} | {x['edge_xg']:+.2f} pp | "
              f"**{x['edge_split']:+.2f} pp** | {x['edge_robust_min']:+.2f} pp | "
              f"{x['failed_gate']}{' (gepubliceerd op rangorde)' if pub else ''} |")

# ---------- niveau ----------
niv = ["| Competitie | Route | Thuis | Uit | Basis | Reden |", "|---|---|---|---|---|---|"]
for comp, v in res["niveau"].items():
    niv.append(f"| {comp} | `{v['source']}` | {v['home_goals_per_match']:.3f} | "
               f"{v['away_goals_per_match']:.3f} | {v['avg_xg_per_match']:.3f} | {v['reason']} |")

open("tmp-run/rb_oct21_tabellen.md", "w").write("\n".join([
    "<!--DEK-->", *dek, "<!--BEV-->", *bevr, "<!--TOP-->", *tops, "<!--RUW-->", *ruw,
    "<!--NN-->", *nn, "<!--NIV-->", *niv]))
print("tabellen geschreven")
for k in ("RUNLIJST", "inkoop"):
    print("\n", k, "->", len(P[k]), "tekens")

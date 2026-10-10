"""Run A, 10 okt 2026 — Stage 3 vervolg: tier per wedstrijd, met degradantenomrekening.

Zelfde regels als `rb_oct08_cand.py`. Alle tien de actieve competities hebben xG in zowel
2025/2026 als 2026/2027 (`idcheck.py` groen op alle 33 id's), dus `FULL` is voor elk duel
haalbaar zolang beide ploegen in de stand van vorig seizoen staan. Wie daar niet staat is
promovendus of degradant en gaat langs §4 ("Promovendi: eerst omrekenen, dan pas NONE") — in
deze runlijst te verwachten bij de Ekstraklasa (Wieczysta Kraków is nieuw) en bij de
Championship, waar West Ham vorig seizoen Premier League speelde.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob
from ra_names import resolve

s3 = json.load(open("tmp-run/ra_oct10_stage3.json"))
fx, st = s3["fixtures"], s3["stats"]

cands = []
for name, v in fx.items():
    if not v["matches"]:
        continue
    season = v["s_prev"]
    full = (st.get(name, {}).get("prev") or {}).get("has_xg")
    teams = fotmob.fetch_league_stats(v["primaryId"], season)["teams"]
    for m in v["matches"]:
        rh, ra = resolve(m["home"], teams), resolve(m["away"], teams)
        missing = [t for t, r in ((m["home"], rh), (m["away"], ra)) if not r]
        cands.append({"competition": name, "season": season, "season_cur": v["s_cur"],
                      "primaryId": v["primaryId"], "crossborder": False,
                      "betexplorer": v["betexplorer"], "sportkey": v["sportkey"],
                      "understat": v.get("understat"),
                      "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
                      "table_home": rh, "table_away": ra, "missing": missing, **m})

json.dump(cands, open("tmp-run/ra_oct10_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    print(f"  {c['tier']:6s} {c['competition']:30s} {c['home']} - {c['away']}{flag}")

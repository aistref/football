"""Run B, 18 okt 2026 — Stage 3 vervolg: tier per wedstrijd, met promovendi-omrekening.

Zelfde regels als `rb_oct18_cand.py`; alleen de datum en de bestandsnamen verschillen. Van de tien
competities die vandaag spelen hebben er vier géén xG bij Fotmob (Croatian HNL, Hungarian NB I,
Romanian SuperLiga, Keuken Kampioen Divisie) en die komen dus hoe dan ook op `LIGHT` uit, met de
lat van 16,0 pp. Een ploeg die niet in de stand van het vorige seizoen staat krijgt hier `PROMO?`
en gaat in het analysescript langs `promotion.convert` / `convert_relegated` (§4) — met de
naamsleutels uit `PROMO_COMP` daar, want de runlijstnamen van `prompts/run-b.md` wijken voor
Segunda División en de twee Engelse divisies af van de namen in `promotion.TIER1/TIER2`.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob
from ra_names import resolve

s3 = json.load(open("tmp-run/rb_oct19_stage3.json"))
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
                      "understat": None,
                      "tier": "FULL" if full and not missing else ("LIGHT" if not missing else "PROMO?"),
                      "table_home": rh, "table_away": ra, "missing": missing, **m})

json.dump(cands, open("tmp-run/rb_oct19_cands.json", "w"), ensure_ascii=False, indent=1)
print("totaal", len(cands))
for c in cands:
    flag = "" if not c["missing"] else f"  <-- niet in stand {c['season']}: {c['missing']}"
    print(f"  {c['tier']:6s} {c['competition']:30s} {c['home']} - {c['away']}{flag}")

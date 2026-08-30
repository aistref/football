"""Stage 3 vervolg + Stage 4-voorbereiding: tier per wedstrijd, referentieseizoen, kandidaten."""
import json, sys
sys.path.insert(0, "tmp-run")
from scripts import fotmob
from rb_names import resolve

fx = json.load(open("tmp-run/rb_fixtures.json"))
st = json.load(open("tmp-run/rb_stats.json"))

CURRENT_BASE = {"Eliteserien (NOR)", "Allsvenskan (SWE)"}   # kalenderjaar, lopend seizoen ruim gespeeld

cands = []
for name, v in fx.items():
    if not v["matches"]:
        continue
    s = st[name]
    base = "cur" if name in CURRENT_BASE else "prev"
    season = v["s_cur"] if base == "cur" else v["s_prev"]
    full = s[base].get("has_xg")
    teams = fotmob.fetch_league_stats(v["primaryId"], season)["teams"]
    for m in v["matches"]:
        rh, ra = resolve(m["home"], teams), resolve(m["away"], teams)
        tier = "NONE" if not (rh and ra) else ("FULL" if full else "LIGHT")
        cands.append({"competition": name, "season": season, "base": base,
                      "primaryId": v["primaryId"], "slug": v["slug"], "sportkey": v["sportkey"],
                      "tier": tier, "table_home": rh, "table_away": ra, **m,
                      "missing": [t for t, r in ((m["home"], rh), (m["away"], ra)) if not r]})
json.dump(cands, open("tmp-run/rb_cands.json", "w"), ensure_ascii=False, indent=1)
print("FULL", sum(c["tier"]=="FULL" for c in cands), "LIGHT", sum(c["tier"]=="LIGHT" for c in cands),
      "NONE", sum(c["tier"]=="NONE" for c in cands), "totaal", len(cands))
for c in cands:
    if c["tier"] == "NONE":
        print("  NONE:", c["competition"], "|", c["home"], "-", c["away"], "| mist", c["missing"])

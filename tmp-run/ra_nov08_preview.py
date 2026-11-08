"""Run A, 8 nov 2026 — §6b-5i: het voorbeschouwingsblok per GEPUBLICEERDE bet.

Draait NA toplist.py, want pas dan is bekend wélke duels een bet zijn geworden. Kost geen
credits: Fotmob rekent niet af per verzoek, en de daglijsten van het venster rond de rundag
worden gedeeld over alle bets.

HARDE GRENS §2/§4: niets uit dit blok gaat in `my_prob` of in `prob_sources`. `insights` is
andermans redactie en de h2h is historie; een voorbeschouwing beschrijft en rekent niet.
"""
import json
from datetime import date
from scripts import preview

DAG = "2026-11-08"
STATE = f"data/run-state/{DAG}-run-a.json"
DAY = date.fromisoformat(DAG)

picks = json.load(open("tmp-run/ra_nov08_picks_a.json"))
# De ploeg-id's staan niet in de wedstrijdrecords van `data/run-state/` (het runscript kopieert
# ze niet mee) maar wel in de Stage 3-uitvoer. Ze zijn nodig omdat `week_around` zonder id op
# NAAM koppelt en dan clubs met dezelfde naam uit andere competities meeneemt — vanochtend
# gemeten op Nacional (Funchal), dat vier duels van twee andere Nacionals binnenhaalde.
IDS = {c["match_id"]: (c.get("home_id"), c.get("away_id"))
       for c in json.load(open("tmp-run/ra_nov08_ctx.json"))}
gepubliceerd = {p["home"] + " – " + p["away"] for p in picks}

st = json.load(open(STATE))
fixtures, gezet, fouten = {}, 0, {}
for comp, blok in st["competitions"].items():
    for m in blok.get("matches") or []:
        if m.get("match") not in gepubliceerd:
            continue
        try:
            # home_id/away_id meegeven: zonder id koppelt `week_around` op NAAM en haalt
            # clubs met dezelfde naam uit andere competities binnen. Vanochtend gemeten op
            # Nacional (Funchal), dat twee Uruguayaanse en twee Paraguayaanse duels in zijn
            # weekoverzicht kreeg. Zie de docstring van `preview.week_around`.
            m["voorbeschouwing"] = preview.match_block(
                m["match_id"], DAY, m["home"], m["away"], fixtures=fixtures,
                home_id=IDS.get(m["match_id"], (None, None))[0],
                away_id=IDS.get(m["match_id"], (None, None))[1])
            gezet += 1
            print(f"OK  {m['match']}")
        except Exception as e:
            fouten[m["match"]] = f"{type(e).__name__}: {e}"
            print(f"FOUT {m['match']}: {type(e).__name__}: {e}")

json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nvoorbeschouwing op {gezet} van de {len(gepubliceerd)} gepubliceerde duels, "
      f"{len(fouten)} fout(en)")

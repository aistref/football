"""Run A, 26 okt 2026 — §6b-5i: het voorbeschouwingsblok per GEPUBLICEERDE bet.

Draait NA toplist.py, want pas dan is bekend wélke duels een bet zijn geworden. Kost geen
credits: Fotmob rekent niet af per verzoek, en de daglijsten van het venster rond de rundag
worden gedeeld over alle bets.

HARDE GRENS §2/§4: niets uit dit blok gaat in `my_prob` of in `prob_sources`. `insights` is
andermans redactie en de h2h is historie; een voorbeschouwing beschrijft en rekent niet.
"""
import json
from datetime import date
from scripts import preview

DAG = "2026-10-27"
STATE = f"data/run-state/{DAG}-run-a.json"
DAY = date.fromisoformat(DAG)

picks = json.load(open("tmp-run/ra_oct27_picks_a.json"))
gepubliceerd = {p["home"] + " – " + p["away"] for p in picks}

st = json.load(open(STATE))
fixtures, gezet, fouten = {}, 0, {}
for comp, blok in st["competitions"].items():
    for m in blok.get("matches") or []:
        if m.get("match") not in gepubliceerd:
            continue
        try:
            m["voorbeschouwing"] = preview.match_block(
                m["match_id"], DAY, m["home"], m["away"], fixtures=fixtures)
            gezet += 1
            print(f"OK  {m['match']}")
        except Exception as e:
            fouten[m["match"]] = f"{type(e).__name__}: {e}"
            print(f"FOUT {m['match']}: {type(e).__name__}: {e}")

json.dump(st, open(STATE, "w"), ensure_ascii=False, indent=1)
print(f"\nvoorbeschouwing op {gezet} van de {len(gepubliceerd)} gepubliceerde duels, "
      f"{len(fouten)} fout(en)")

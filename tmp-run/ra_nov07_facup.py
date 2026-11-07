"""Run A, 7 nov 2026 — de FA Cup staat WEL in de Fotmob-daglijst, onder id 132.

`ra_nov06_cups.py` probeerde alleen de drie id's die de vorige run had opgeschreven (League Cup
133, DFB Pokal 209, KNVB Beker 235) en zette de FA Cup daarom op de BetExplorer-route. Die vond
twee duels in het venster; de daglijst-audit van `ra_nov06_stage3.py` laat zien dat ze er ook in
de daglijst staan, onder `primaryId` 132. Beide bronnen zijn het dus eens over het AANTAL (2) en
over de ploegen, en de daglijst levert bovendien match_id, ploeg-id's en de aftrap in UTC.

Het id gaat onder `notes` in coverage.json en niet onder `fotmob_id` — een beker heeft geen stand
en `idcheck.py` zou er elke run een vals alarm op geven (zelfde redenering als bij 133/209/235).
"""
import json
from datetime import date
from scripts import fotmob
from scripts.runwindow import days_needed, matches_for_run

DAY = date(2026, 11, 7)
FA_CUP_ID = 132

fixtures = {d: fotmob.fetch_fixtures(d) for d in days_needed(DAY)}
per_comp = matches_for_run(DAY, fixtures, {"FA Cup (ENG)": FA_CUP_ID})
ms = per_comp.get("FA Cup (ENG)") or []

rows = [{"match_id": m.match_id, "home": m.home, "away": m.away,
         "home_id": m.home_id, "away_id": m.away_id,
         "kickoff_utc": m.kickoff_utc, "kickoff_nl": str(m.kickoff_nl),
         "source_day": m.source_day.isoformat(), "playable": m.playable} for m in ms]
for r in rows:
    print(f"FA Cup  {r['home']} - {r['away']}  {r['kickoff_nl']} NL  "
          f"match_id={r['match_id']} home_id={r['home_id']} away_id={r['away_id']} "
          f"speelbaar={r['playable']}")

json.dump({"day": DAY.isoformat(), "fotmob_id": FA_CUP_ID, "matches": rows},
          open("tmp-run/ra_nov07_facup.json", "w"), ensure_ascii=False, indent=1)
print("totaal:", len(rows))

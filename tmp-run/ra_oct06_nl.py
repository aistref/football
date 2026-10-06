"""Hebben de tien FA Cup-clubs een divisie bij Fotmob met bruikbare cijfers?

Stage 3, eerlijk uitgezocht in plaats van aangenomen: de vijf duels liggen op tier 6-8 en de
TIER2-keten van promotion.py reikt tot League Two. Maar Fotmob kent de non-league-divisies wel
(ze staan in de daglijst van vandaag), dus de vraag is of de clubs daar in een stand staan.
"""
import json
from scripts import fotmob

CLUBS = ["Atherton", "Trafford", "Halesowen", "Stafford", "Scarborough",
         "Macclesfield", "Spalding", "Bury Town", "Wingate", "Bedford"]
# kandidaat-divisies, gevonden in de Fotmob-daglijst van vandaag + de voor de hand liggende
LEAGUES = {
    "National League": 117, "National League North": 8944, "National League South": 8944,
    "Northern Premier Division": 8947, "Southern Premier Division Central": 8947,
    "Isthmian Premier Division": 8947,
}

found = {}
for lid in sorted(set(LEAGUES.values())):
    for season in ("2025/2026", "2026/2027"):
        try:
            st = fotmob.fetch_league_stats(lid, season)
        except Exception as e:
            print(f"id={lid} {season}: FOUT {type(e).__name__}: {e}")
            continue
        teams = st.get("teams") or st.get("table") or {}
        names = sorted(teams.keys()) if isinstance(teams, dict) else []
        print(f"id={lid} {season}: {len(names)} ploegen, xG={st.get('has_xg')}, "
              f"avg_xg={st.get('avg_xg_per_match')}, avg_goals={st.get('avg_goals_per_match')}")
        for c in CLUBS:
            for n in names:
                if c.lower() in n.lower():
                    found.setdefault(c, []).append({"league_id": lid, "season": season, "team": n})
print()
for c in CLUBS:
    print(f"  {c:20s} {json.dumps(found.get(c, []), ensure_ascii=False)}")
json.dump(found, open("tmp-run/ra_oct06_nl.json", "w"), ensure_ascii=False, indent=1)

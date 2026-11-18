"""Tweede bron (BetExplorer) voor de vijf bekers en vier competities van de Run A-runlijst.
"Niet in de Fotmob-daglijst" mag niet als GEEN WEDSTRIJD worden opgeschreven zonder tweede bron
(het gat van 6 okt 2026, dat Run A vijf duels kostte).
"""
import json
from dataclasses import asdict
from scripts import betexplorer as bx

SLUGS = {
 "FA Cup (ENG)":        "https://www.betexplorer.com/football/england/fa-cup/",
 "League Cup (ENG)":    "https://www.betexplorer.com/football/england/efl-cup/",
 "Coppa Italia (ITA)":  "https://www.betexplorer.com/football/italy/coppa-italia/",
 "KNVB Beker (NED)":    "https://www.betexplorer.com/football/netherlands/knvb-beker/",
 "DFB Pokal (GER)":     "https://www.betexplorer.com/football/germany/dfb-pokal/",
 "Premier League (ENG)":"https://www.betexplorer.com/football/england/premier-league/",
 "Serie A (ITA)":       "https://www.betexplorer.com/football/italy/serie-a/",
 "Eredivisie (NED)":    "https://www.betexplorer.com/football/netherlands/eredivisie/",
 "UEFA Champions League":"https://www.betexplorer.com/football/europe/champions-league/",
}
res = {}
for naam, url in SLUGS.items():
    try:
        rows = bx.fetch_league_fixtures(url)
        # 18 nov = vandaag, 19 nov = het tweede deel van het venster
        venster = [r for r in rows if r.is_today or (r.when or "").startswith(("18.11.", "19.11."))]
        res[naam] = {"status": "ok", "n": len(rows), "in_venster": len(venster),
                     "venster": [asdict(r) for r in venster],
                     "eerste": [f"{r.home} - {r.away} @ {r.when}" for r in rows[:3]]}
    except Exception as e:
        res[naam] = {"status": f"{type(e).__name__}: {e}"[:160], "n": 0, "in_venster": None,
                     "venster": [], "eerste": []}
    r = res[naam]
    print(f'{naam:24s} {r["status"][:34]:34s} rijen={r["n"]:3d} in venster 18/19 nov={r["in_venster"]}')
    for e in r["eerste"]:
        print("       eerstvolgend:", e)
    for v in r["venster"]:
        print("       IN VENSTER:", v)
json.dump(res, open("tmp-run/ra_nov18_bx.json", "w"), ensure_ascii=False, indent=1)

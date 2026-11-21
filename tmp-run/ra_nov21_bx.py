"""Tweede bron (BetExplorer) voor de competities die vandaag volgens Fotmob LEEG zijn.
"Niet in de Fotmob-daglijst" mag niet als GEEN WEDSTRIJD worden opgeschreven zonder tweede bron
(het gat van 6 okt 2026, dat Run A vijf duels kostte). Venster: 21/22 nov.
"""
import json
from dataclasses import asdict
from scripts import betexplorer as bx

SLUGS = {
 "Premier League (ENG)":   "https://www.betexplorer.com/football/england/premier-league/",
 "Serie A (ITA)":          "https://www.betexplorer.com/football/italy/serie-a/",
 "Championship (ENG)":     "https://www.betexplorer.com/football/england/championship/",
 "Eredivisie (NED)":       "https://www.betexplorer.com/football/netherlands/eredivisie/",
 "Primeira Liga (POR)":    "https://www.betexplorer.com/football/portugal/liga-portugal/",
 "Super Lig (TUR)":        "https://www.betexplorer.com/football/turkey/super-lig/",
 "Scottish Premiership (SCO)": "https://www.betexplorer.com/football/scotland/premiership/",
 "UEFA Champions League":  "https://www.betexplorer.com/football/europe/champions-league/",
 "UEFA Europa League":     "https://www.betexplorer.com/football/europe/europa-league/",
 "UEFA Conference League": "https://www.betexplorer.com/football/europe/conference-league/",
 # en de zes die buiten de runlijst vallen: alleen om vast te leggen DAT er gespeeld wordt
 "FA Cup (ENG)":           "https://www.betexplorer.com/football/england/fa-cup/",
 "League Cup (ENG)":       "https://www.betexplorer.com/football/england/efl-cup/",
 "Coppa Italia (ITA)":     "https://www.betexplorer.com/football/italy/coppa-italia/",
 "KNVB Beker (NED)":       "https://www.betexplorer.com/football/netherlands/knvb-beker/",
 "DFB Pokal (GER)":        "https://www.betexplorer.com/football/germany/dfb-pokal/",
 "Copa del Rey (ESP)":     "https://www.betexplorer.com/football/spain/copa-del-rey/",
 # de competities met duels: controle dat de tweede bron hetzelfde zegt
 "La Liga (ESP)":          "https://www.betexplorer.com/football/spain/laliga/",
 "Bundesliga (GER)":       "https://www.betexplorer.com/football/germany/bundesliga/",
 "Ligue 1 (FRA)":          "https://www.betexplorer.com/football/france/ligue-1/",
 "Belgian Pro League (BEL)":"https://www.betexplorer.com/football/belgium/jupiler-pro-league/",
 "Danish Superliga (DEN)": "https://www.betexplorer.com/football/denmark/superliga/",
 "Ekstraklasa (POL)":      "https://www.betexplorer.com/football/poland/ekstraklasa/",
}
res = {}
for naam, url in SLUGS.items():
    try:
        rows = bx.fetch_league_fixtures(url)
        venster = [r for r in rows if r.is_today or (r.when or "").startswith(("21.11.", "22.11."))]
        res[naam] = {"status": "ok", "n": len(rows), "in_venster": len(venster),
                     "venster": [asdict(r) for r in venster],
                     "eerste": [f"{r.home} - {r.away} @ {r.when}" for r in rows[:3]]}
    except Exception as e:
        res[naam] = {"status": f"{type(e).__name__}: {e}"[:160], "n": 0, "in_venster": None,
                     "venster": [], "eerste": []}
    r = res[naam]
    print(f'{naam:26s} {r["status"][:30]:30s} rijen={r["n"]:3d} in venster 21/22 nov={r["in_venster"]}')
    for e in r["eerste"][:2]:
        print("       eerstvolgend:", e)
    for v in r["venster"]:
        print("       IN VENSTER:", v.get("home"), "-", v.get("away"), "@", v.get("when"))
json.dump(res, open("tmp-run/ra_nov21_bx.json", "w"), ensure_ascii=False, indent=1)

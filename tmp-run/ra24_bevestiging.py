"""Run A, 24 sep 2026 — tweede bron bij een lege dag (§3 Stage 1: 'probeer meerdere bronnen').

Fotmob geeft nul wedstrijden in de hele runlijst. Dat is een uitkomst die je niet op één bron
hoort te baseren, dus hier leest BetExplorer dezelfde competities na.
"""
import json
from datetime import date
from scripts import betexplorer

DAY = date(2026, 9, 24)
URLS = json.load(open("tmp-run/ra24_stage3.json"))
CHECK = {
 "Premier League (ENG)":   "https://www.betexplorer.com/football/england/premier-league/",
 "Serie A (ITA)":          "https://www.betexplorer.com/football/italy/serie-a/",
 "La Liga (ESP)":          "https://www.betexplorer.com/football/spain/laliga/",
 "Bundesliga (GER)":       "https://www.betexplorer.com/football/germany/bundesliga/",
 "Ligue 1 (FRA)":          "https://www.betexplorer.com/football/france/ligue-1/",
 "Championship (ENG)":     "https://www.betexplorer.com/football/england/championship/",
 "Eredivisie (NED)":       "https://www.betexplorer.com/football/netherlands/eredivisie/",
 "Primeira Liga (POR)":    "https://www.betexplorer.com/football/portugal/liga-portugal/",
 "Belgian Pro League (BEL)":"https://www.betexplorer.com/football/belgium/jupiler-pro-league/",
 "Süper Lig (TUR)":        "https://www.betexplorer.com/football/turkey/super-lig/",
 "Scottish Premiership (SCO)":"https://www.betexplorer.com/football/scotland/premiership/",
 "Danish Superliga (DEN)": "https://www.betexplorer.com/football/denmark/superliga/",
 "Ekstraklasa (POL)":      "https://www.betexplorer.com/football/poland/ekstraklasa/",
 "UEFA Champions League":  "https://www.betexplorer.com/football/europe/champions-league/",
 "UEFA Europa League":     "https://www.betexplorer.com/football/europe/europa-league/",
 "UEFA Conference League": "https://www.betexplorer.com/football/europe/conference-league/",
 "League Cup (ENG)":       "https://www.betexplorer.com/football/england/efl-cup/",
 "Coppa Italia (ITA)":     "https://www.betexplorer.com/football/italy/coppa-italia/",
}
stamp = DAY.strftime("%d.%m.")
out = {}
for name, url in CHECK.items():
    try:
        fx = betexplorer.fetch_league_fixtures(url)
    except Exception as e:
        out[name] = {"error": f"{type(e).__name__}: {e}"}
        print(f"{name:28s} FOUT {type(e).__name__}: {e}")
        continue
    times = sorted({f.when for f in fx if f.when})
    today = [f for f in fx if f.is_today or f.when.startswith(stamp)]
    out[name] = {"n": len(fx), "vandaag": len(today), "eerste": times[:2]}
    print(f"{name:28s} {len(fx):3d} fixtures, vandaag {len(today)}, eerstvolgende {times[:2]}")

json.dump(out, open("tmp-run/ra24_bevestiging.json", "w"), ensure_ascii=False, indent=1)
print("\nvandaag volgens BetExplorer:", sum(v.get("vandaag", 0) for v in out.values()))

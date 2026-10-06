"""Tegenstrijdigheid uitzoeken: BetExplorer zet Halesowen in de FA Cup, Fotmob in de Southern League."""
import json
from datetime import date
from scripts import betexplorer, fotmob

# 1. alle rijen van de BetExplorer FA Cup-pagina, ruw
fx = betexplorer.fetch_league_fixtures("https://www.betexplorer.com/football/england/fa-cup/")
print("FA Cup BetExplorer rijen:", len(fx))
for f in fx:
    print("  ", f.when, "|", f.home, "-", f.away, "|", getattr(f, "odds", None),
          "| is_today:", f.is_today)

# 2. Fotmob: welke Engelse competities spelen er vandaag, en staan onze clubs erin?
d = date(2026, 10, 6)
day = fotmob.fetch_fixtures(d)
print("\nEngelse competities in de Fotmob-daglijst van", d)
for lg in day.get("leagues", []) or []:
    if lg.get("ccode") == "ENG":
        print(f"   id={lg.get('primaryId') or lg.get('id'):>6}  {lg.get('name')}  "
              f"({len(lg.get('matches') or [])} duels)")
        for m in lg.get("matches", []) or []:
            print("        ", (m.get("status") or {}).get("utcTime"),
                  (m.get("home") or {}).get("name"), "-", (m.get("away") or {}).get("name"))

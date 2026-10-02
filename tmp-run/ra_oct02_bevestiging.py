"""Run A, 2 okt 2026 — tweede bron voor de lege runlijst (§3 Stage 1: probeer meerdere bronnen).

Haalt per competitie uit de runlijst de BetExplorer-fixturepagina op, los van Fotmob, en kijkt of
er vandaag iets staat en wanneer de eerstvolgende speelronde is. Achttien van de 21 competities
hebben hier een URL; de drie bekers zonder URL (FA Cup, KNVB Beker, DFB Pokal) gaan via
`ra30_gap.py`.

VALKUIL, deze run tegengekomen en daarom hier opgeschreven: `fetch_league_fixtures` geeft
`MatchOdds`-**dataclasses** terug en geen dicts. `f.get("date")` gooit `AttributeError`, en er is
geen `date`-veld — het veld met de aftrap heet `when` en bevat `"10.10. 15:00"`, dus dag en maand
zonder jaar. Vergelijken met vandaag gaat daarom op een `"%d.%m."`-prefix, niet op een ISO-datum.
"""
import json
from scripts import betexplorer

URLS = {
 "Premier League (ENG)": "https://www.betexplorer.com/football/england/premier-league/",
 "Serie A (ITA)": "https://www.betexplorer.com/football/italy/serie-a/",
 "La Liga (ESP)": "https://www.betexplorer.com/football/spain/laliga/",
 "Bundesliga (GER)": "https://www.betexplorer.com/football/germany/bundesliga/",
 "Ligue 1 (FRA)": "https://www.betexplorer.com/football/france/ligue-1/",
 "Championship (ENG)": "https://www.betexplorer.com/football/england/championship/",
 "Eredivisie (NED)": "https://www.betexplorer.com/football/netherlands/eredivisie/",
 "Primeira Liga (POR)": "https://www.betexplorer.com/football/portugal/liga-portugal/",
 "Belgian Pro League (BEL)": "https://www.betexplorer.com/football/belgium/jupiler-pro-league/",
 "Super Lig (TUR)": "https://www.betexplorer.com/football/turkey/super-lig/",
 "Scottish Premiership (SCO)": "https://www.betexplorer.com/football/scotland/premiership/",
 "Danish Superliga (DEN)": "https://www.betexplorer.com/football/denmark/superliga/",
 "Ekstraklasa (POL)": "https://www.betexplorer.com/football/poland/ekstraklasa/",
 "UEFA Champions League": "https://www.betexplorer.com/football/europe/champions-league/",
 "UEFA Europa League": "https://www.betexplorer.com/football/europe/europa-league/",
 "UEFA Conference League": "https://www.betexplorer.com/football/europe/conference-league/",
 "League Cup (ENG)": "https://www.betexplorer.com/football/england/efl-cup/",
 "Coppa Italia (ITA)": "https://www.betexplorer.com/football/italy/coppa-italia/",
}

out = {}
for naam, url in URLS.items():
    try:
        fx = betexplorer.fetch_league_fixtures(url)
        whens = sorted({f.when for f in fx if f.when})
        vandaag = [f for f in fx if f.is_today]
        out[naam] = {"n": len(fx), "eerste": whens[:3], "is_today": len(vandaag)}
        print(f"{naam:28s} {len(fx):3d} fixtures  eerste={whens[:2]}  is_today={len(vandaag)}")
    except Exception as e:
        out[naam] = {"error": f"{type(e).__name__}: {e}"}
        print(f"{naam:28s} FAIL {type(e).__name__}: {e}")

json.dump(out, open("tmp-run/ra_oct02_bevestiging.json", "w"), ensure_ascii=False, indent=1)

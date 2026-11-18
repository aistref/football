"""Wanneer heeft Run A weer werk? Eerstvolgende fixture per competitie van de runlijst (BetExplorer)."""
import json
from scripts import betexplorer as bx

SLUGS = {
 "Premier League (ENG)":      "england/premier-league/",
 "Serie A (ITA)":             "italy/serie-a/",
 "La Liga (ESP)":             "spain/laliga/",
 "Bundesliga (GER)":          "germany/bundesliga/",
 "Ligue 1 (FRA)":             "france/ligue-1/",
 "Championship (ENG)":        "england/championship/",
 "Eredivisie (NED)":          "netherlands/eredivisie/",
 "Primeira Liga (POR)":       "portugal/liga-portugal/",
 "Belgian Pro League (BEL)":  "belgium/jupiler-pro-league/",
 "Super Lig (TUR)":           "turkey/super-lig/",
 "Scottish Premiership (SCO)":"scotland/premiership/",
 "Danish Superliga (DEN)":    "denmark/superliga/",
 "Ekstraklasa (POL)":         "poland/ekstraklasa/",
}
out = {}
for naam, slug in SLUGS.items():
    try:
        rows = bx.fetch_league_fixtures("https://www.betexplorer.com/football/" + slug)
        nxt = sorted({r.when for r in rows if r.when})[:1]
        op1920 = [f"{r.home} - {r.away} @ {r.when}" for r in rows if (r.when or "").startswith(("19.11.", "20.11."))]
        out[naam] = {"n": len(rows), "eerste_datum": nxt[0] if nxt else None, "op_19_of_20_nov": op1920}
    except Exception as e:
        out[naam] = {"n": 0, "eerste_datum": f"FOUT {type(e).__name__}", "op_19_of_20_nov": []}
    print(f'{naam:28s} rijen={out[naam]["n"]:3d}  eerst={out[naam]["eerste_datum"]}  19/20 nov={len(out[naam]["op_19_of_20_nov"])}')
    for m in out[naam]["op_19_of_20_nov"]:
        print("      ", m)
json.dump(out, open("tmp-run/ra_nov18_next.json", "w"), ensure_ascii=False, indent=1)

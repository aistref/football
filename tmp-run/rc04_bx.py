import json
from scripts import betexplorer as bx

SLUGS = {
    "Friendly": bx.KNOWN_LEAGUE_URLS["Vriendschappelijke interlands"],
    "CONCACAF-NL": bx.KNOWN_LEAGUE_URLS["CONCACAF Nations League"],
    "Gulf-Cup": bx.KNOWN_LEAGUE_URLS["Arabian Gulf Cup"],
    "AFCON-kwal": bx.KNOWN_LEAGUE_URLS["CAF Afrika Cup-kwalificatie"],
}

out = {}
for key, url in SLUGS.items():
    try:
        rows = bx.fetch_league_fixtures(url)
        out[key] = [[r.home, r.away, list(r.odds), r.when, r.bookmakers, r.is_today] for r in rows]
        print(key, "->", len(rows), "rows")
    except Exception as e:
        out[key] = f"ERROR: {e}"
        print(key, "ERROR", e)

# FIFA ASEAN Cup: geen bekende slug. Probeer een paar varianten (vandaag "Premier Division",
# eerdere runs zagen "Challenge Division" zonder dekking).
ASEAN_TRIES = [
    "https://www.betexplorer.com/football/asia/fifa-asean-cup/",
    "https://www.betexplorer.com/football/asia/asean-cup/",
    "https://www.betexplorer.com/football/asia/asean-championship/",
    "https://www.betexplorer.com/football/world/fifa-asean-cup/",
]
out["ASEAN"] = None
for url in ASEAN_TRIES:
    try:
        rows = bx.fetch_league_fixtures(url)
        print("ASEAN try", url, "->", len(rows), "rows")
        if rows:
            out["ASEAN"] = [[r.home, r.away, list(r.odds), r.when, r.bookmakers, r.is_today] for r in rows]
            out["ASEAN_url"] = url
            break
    except Exception as e:
        print("ASEAN try", url, "ERROR", e)

json.dump(out, open("tmp-run/rc04_bx.json", "w"), indent=1, ensure_ascii=False)
print("done")

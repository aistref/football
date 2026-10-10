"""Run A, 10 okt 2026 — de vijf bekers van de runlijst, langs BetExplorer.

Waarom apart: geen van de vijf heeft een `fotmob_id` in `data/coverage.json`, dus
`runwindow.matches_for_run` kan ze niet filteren en de Fotmob-daglijst is voor hen geen bron.
Dat is precies het gat dat Run A op 6 oktober 2026 trof: de FA Cup-kwalificatie stond niet in
de daglijst (59 competities, FA Cup er niet bij) en wél bij BetExplorer, met vijf duels in het
venster. "Niet in de daglijst" mag dus nooit als `GEEN WEDSTRIJD` worden opgeschreven zonder
tweede bron.

Let op de drie faalmodi van BetExplorer die `scripts/betexplorer.py` documenteert, want twee
ervan zien er hier uit als "geen wedstrijden":
  nul teamparen                -> verkeerde slug (de pagina redirect stil naar de homepage)
  teamparen zonder koers       -> goede slug, nog geen boek met prijzen voor deze ronde
  teamparen mét koers          -> goede slug, prijzen beschikbaar
Een pagina van 564497 bytes mét 0 teamparen is de homepage; dat is de redirect-faalmodus.
"""
import json, re, urllib.request
from datetime import date
from scripts import betexplorer as bx

DAY = date(2026, 10, 10)
# Alleen slugs die teamparen opleveren. De afgekeurde varianten staan erbij met hun uitkomst,
# zodat een volgende run ze niet opnieuw hoeft te raden.
SLUGS = {
 "FA Cup (ENG)":      ("https://www.betexplorer.com/football/england/fa-cup/",
                       {"england/fa-cup-qualification": "0 teamparen, 564497 bytes = homepage-redirect",
                        "england/fa-cup-2026-2027": "identiek aan england/fa-cup"}),
 "League Cup (ENG)":  ("https://www.betexplorer.com/football/england/efl-cup/", {}),
 "Coppa Italia (ITA)":("https://www.betexplorer.com/football/italy/coppa-italia/", {}),
 "KNVB Beker (NED)":  ("https://www.betexplorer.com/football/netherlands/knvb-beker/",
                       {"netherlands/beker": "0 teamparen, 564497 bytes = homepage-redirect",
                        "netherlands/toto-knvb-beker": "0 teamparen, 564497 bytes = homepage-redirect"}),
 "DFB Pokal (GER)":   ("https://www.betexplorer.com/football/germany/dfb-pokal/", {}),
}

out = {}
for name, (url, afgekeurd) in SLUGS.items():
    fu = url.rstrip("/") + "/fixtures/"
    raw = urllib.request.urlopen(urllib.request.Request(fu, headers=bx.HEADERS), timeout=30).read()
    text = raw.decode(errors="replace")
    pairs, carried, rijen = 0, "", []
    for row in bx._FIX_ROW_RE.findall(text):
        w = bx._WHEN_RE.search(row)
        if w and w.group(1).strip() and w.group(1).strip() != "&nbsp;":
            carried = w.group(1).strip()
        tm = bx._TEAMS_RE.search(row)
        if tm:
            pairs += 1
            rijen.append({"home": tm.group(1), "away": tm.group(2), "when": carried})
    koersen = len(bx._ODDS_RE.findall(text))
    # Het venster is [10.10. 08:00 NL, 11.10. 08:00 NL). BetExplorer labelt in UK-tijd en toont
    # "Today" voor de eigen pagina-datum; een duel van vandaag of morgenvroeg staat dus als
    # "Today ..", "09.10. .." of "10.10. ..".
    in_venster = [r for r in rijen if r["when"].startswith(("Today", "10.10.", "11.10."))]
    eerste = next((r["when"] for r in rijen if r["when"]), None)
    out[name] = {"slug": fu, "bytes": len(raw), "teamparen": pairs, "koersen": koersen,
                 "in_venster": in_venster, "eerste_ronde": eerste,
                 "afgekeurde_slugs": afgekeurd,
                 "status": "GEEN WEDSTRIJD" if not in_venster else "?"}
    print(f"{name:20s} {pairs:3d} teamparen, {koersen:3d} koersen, {len(in_venster)} in venster, "
          f"eerstvolgende ronde: {eerste}")

json.dump({"day": DAY.isoformat(), "cups": out},
          open("tmp-run/ra_oct10_cups.json", "w"), ensure_ascii=False, indent=1)

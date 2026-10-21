"""Run A, 21 okt 2026 — bronprobe voor source-health.json.

10 duels in het inzetvenster over TWEE competities: een Champions League-avond (9 duels,
speelronde 4) plus één La Liga-duel. Alle drie de bronkanten werkelijk in gebruik. Fotmob voor de
daglijsten, de 33 standen, de context van alle 10 duels, de binnenlandse standen voor de
kruis-grensomrekening van §4, de voorbeschouwingsblokken van de twee bets en de marktvormtelling
van 9 duels. The Odds API voor de bulk (twee competities) en BTTS (7 duels). BetExplorer voor het
gratis 1X2-marktgemiddelde, als tweede bron op de vraag wélke wedstrijden er zijn, én als enige
bron voor de vijf bekers. Understat als tweede xG-model bij het ene La Liga-duel. De statusregels
komen dus uit echte aanroepen en niet uit een probe.

Als gisteren: GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.
"""

import json, datetime
from scripts import betexplorer

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
H = json.load(open("data/source-health.json"))
S = H["sources"]


def note(key, status, detail):
    prev = S.get(key, {})
    hist = prev.get("detail_history") or []
    if prev.get("detail") and prev.get("last_checked"):
        hist = (hist + [{"date": prev["last_checked"], "detail": prev["detail"]}])[-6:]
    S[key] = {**prev, "status": status, "last_checked": now[:10], "detail": detail,
              "detail_history": hist}
    print(f"{key:18} {status:8} {detail[:110]}")


note("fotmob", "ok",
     "21 okt (run A): daglijsten 21 en 22 okt opgehaald (47 competities / 142 wedstrijden resp. "
     "25 competities / 79 wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json "
     "een bruikbare stand. Standen van beide spelende competities geleverd (La Liga 20 ploegen, "
     "Champions League 36), beide met xG in zowel 2025/2026 als het lopende seizoen. Context "
     "opgehaald voor alle 10 duels, zonder een fout, en 10 van 10 staan in het contextlogboek. "
     "GEEN enkel duel komt deze run op relocated = True en er was GEEN promovendus of degradant "
     "om te converteren: Levante en Athletic Club staan beide in de La Liga-stand van 2025/2026. "
     "Daarnaast de binnenlandse standen voor de kruis-grensomrekening van de negen Champions "
     "League-duels (scripts/interleague.py). Ook het voorbeschouwingsblok van de twee "
     "gepubliceerde duels (preview.match_block: h2h, insights, weer, weekoverzicht) en de "
     "marktvormtelling van 9 duels (marketform.match_block) komen hiervandaan - nul fouten. "
     "GEEN GAT deze run.")

note("the_odds_api", "ok",
     "21 okt (run A): api_check.py OK, 48 actieve voetbalcompetities, quota 19058 over / 942 "
     "gebruikt deze maand. 13 credits uitgegeven: 2 bulk-aanroepen (h2h+spreads+totals, 3 "
     "credits per competitie) en 7 BTTS-aanroepen a 1 credit - opnieuw een goedkope dag, want "
     "negen van de tien duels zitten in EEN competitie en spreads/totals/h2h rekenen per "
     "competitie af (§0). Beide spelende competities hebben een sportkey, dus er is deze run "
     "geen enkel duel waar BetExplorer de enige 1X2-bron is.")

note("oddsapi", "ok",
     "21 okt (run A): fetch_bulk gaf voor beide sportkeys events met h2h, spreads en totals (21 "
     "events voor La Liga, 9 voor de Champions League); fetch_event_markets gaf btts voor 7 van "
     "de 7 duels met een kandidaat-edge. store['errors'] is LEEG - nul fouten over de hele run. "
     "net_price is bij de gepubliceerde Real Madrid-regel werkelijk gebruikt: de beste prijs "
     "stond op de beurs Matchbook (1.78 bruto, 1.7644 na 2% commissie, §0).")

note("betexplorer", "ok",
     "21 okt (run A): La Liga (ESP): 21 fixtures met 1X2-gemiddelde (1 in het inzetvenster); "
     "UEFA Champions League: 11 fixtures (9 in het venster). Tweede bron op de vraag wélke "
     "wedstrijden er zijn: 16 van 16 competities eens met de Fotmob-daglijst, 10 duels tegen 10 "
     "(ra_oct21_bevestiging.py). En de enige bron voor de vijf bekers zonder fotmob_id: alle "
     "vijf nul teamparen in het inzetvenster, met als eerstvolgende ronde FA Cup 7 nov, League "
     "Cup 27 okt, KNVB Beker 27 okt, DFB Pokal 27 okt en Coppa Italia 1 dec. Geen "
     "Cloudflare-challenge, geen 403.")

note("understat", "ok",
     "21 okt (run A): fetch_league voor La Liga (La_liga) geleverd en als tweede xG-model "
     "gebruikt bij het enige duel van de vijf Understat-competities dat vandaag speelt (Levante "
     "- Athletic Club: lambdas 1.409/1.326, rolling-xG over 8 duels voor beide ploegen). De "
     "negen Champions League-duels vallen buiten Understat - dat dekt vijf binnenlandse "
     "competities en geen Europees toernooi (§4).")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Beide leverden deze run zonder fout, "
     "dus §2 is gedekt en er is niets te doen. Wordt pas een echt probleem zodra Fotmob omvalt.")

H["last_run"] = {"run": "A", "date": "2026-10-21",
                 "note": "10 duels in het inzetvenster (9 Champions League + 1 La Liga), 2 bets, "
                         "nul bronstoringen, 13 van 794 credits."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

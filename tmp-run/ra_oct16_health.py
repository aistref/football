"""Run A, 16 okt 2026 — bronprobe voor source-health.json.

Tien duels in het inzetvenster over negen competities: de vrijdagavond-openingsronde van het
Europese weekend. Alle drie de bronkanten zijn deze run werkelijk gebruikt — Fotmob voor de
daglijsten, de 33 standen, de context en de divisies eronder/erboven voor negen omrekeningen,
The Odds API voor de bulk (negen competities) en BTTS (vijf duels), BetExplorer voor het gratis
1X2-marktgemiddelde van alle negen competities én als tweede bron op de vraag wélke wedstrijden
er zijn. De statusregels komen dus uit echte aanroepen en niet uit een probe.

Understat staat vandaag voor het eerst sinds dagen op `ok` in plaats van `n/a`, en dat is geen
toeval maar een reparatie: zie de alias "fc cologne" in scripts/teamnames.py.
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
     "16 okt (run A): daglijsten 16 en 17 okt opgehaald (102 resp. 198 competities, 178 resp. 791 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand "
     "(afsluitcode 0). Standen van alle negen spelende competities geleverd, alle negen met xG in "
     "zowel 2025/2026 als het lopende seizoen. Context opgehaald voor alle 10 duels, ook voor het "
     "duel op tier NONE. Daarnaast negen standen van divisies eronder/erboven voor de "
     "omrekeningen van §4: Serie B (86), LaLiga2 (140), Ligue 2 (110), 1. Lig (165), I Liga (197), "
     "1. Division (85) en Premier League (47, richting omlaag).")

note("the_odds_api", "ok",
     "16 okt (run A): api_check.py OK, 48 actieve voetbalcompetities, quota 19427 over / 573 "
     "gebruikt deze maand. 32 credits uitgegeven: 9 bulk-aanroepen (h2h+spreads+totals, 3 credits "
     "per competitie) en 5 BTTS-aanroepen à 1 credit. Alle negen spelende competities hebben een "
     "sportkey, dus geen enkele viel buiten de betaalde inkoop.")

note("oddsapi", "ok",
     "16 okt (run A): fetch_bulk gaf voor alle negen sportkeys events met h2h, spreads en totals "
     "(20, 21, 18, 18, 13, 18, 9, 6 en 9 events); fetch_event_markets gaf btts voor vijf duels. "
     "Nul fouten in store['errors']. Pinnacle in de respons voor 122 events (gebruikt voor Stage 5 "
     "stap 2), Betfair en Matchbook ook; net_price toegepast op de Matchbook-koers van de "
     "gepubliceerde regel Eintracht Frankfurt – 1. FC Köln (2.04 bruto / 2.0192 netto).")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

probes = {
    "Serie A (ITA)": "https://www.betexplorer.com/football/italy/serie-a/",
    "Ekstraklasa (POL)": "https://www.betexplorer.com/football/poland/ekstraklasa/",
    "FA Cup (ENG)": "https://www.betexplorer.com/football/england/fa-cup/",
}
ok, det = True, []
for naam, url in probes.items():
    try:
        rows = betexplorer.fetch_league_fixtures(url)
        det.append(f"{naam}: {len(rows)} fixtures met 1X2-gemiddelde")
    except Exception as e:
        ok = False
        det.append(f"{naam}: FAIL {type(e).__name__}: {e}")
note("betexplorer", "ok" if ok else "partial_failure",
     "16 okt (run A): " + "; ".join(det) + ". Deze run in drie rollen gebruikt: (1) het gratis "
     "1X2-marktgemiddelde voor alle negen competities, voor het kalibratieblok van §6e en poort 8 "
     "(11 tot 17 boeken per duel); (2) als TWEEDE BRON op de vraag wélke wedstrijden er zijn — "
     "zestien van de zestien competities met een fotmob_id eens, tien duels tegen tien; (3) als "
     "ENIGE bron voor de vijf bekers zonder fotmob_id, die alle vijf teamparen op de "
     "fixturepagina geven en alle vijf buiten het inzetvenster vallen. Geen enkele slug viel in "
     "de homepage-redirect-faalmodus.")

note("understat", "ok",
     "16 okt (run A): fetch_league voor Bundesliga, Serie A, La Liga en Ligue 1 (seizoen 2025) "
     "gaf alle vier een volledige stand (18 resp. 20, 20 en 18 ploegen). Werkelijk BRUIKBAAR voor "
     "één van de vier duels: Eintracht Frankfurt – 1. FC Köln. Bij de andere drie is een ploeg "
     "promovendus en staat terecht niet in de stand van 2025/2026 (Frosinone, Deportivo A Coruña, "
     "Le Mans). Köln kwam er pas na een NAAMREPARATIE bij: Understat noemt die club in het Engels "
     "'FC Cologne' en scripts/teamnames.ALIASES kende alleen de korte Duitse vorm, waardoor "
     "understat_pair None gaf ZONDER foutmelding en p_xg_understat uit het kalibratieblok van dat "
     "duel wegviel. Alias vandaag bijgeschreven; de rangorde van de dag is er niet door veranderd.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "A", "date": "2026-10-16",
                 "matches_in_window": 10, "bets": 3,
                 "note": "Tien duels in het inzetvenster [08:00 NL 16 okt, 08:00 NL 17 okt) over "
                         "negen competities: de vrijdagavond-openingsronde van Serie A, La Liga, "
                         "Bundesliga, Ligue 1, Championship, Eredivisie, Süper Lig en Danish "
                         "Superliga met elk één duel, en de Ekstraklasa met twee. Twaalf van de "
                         "eenentwintig competities hadden geen wedstrijd, inclusief alle vijf de "
                         "bekers en alle drie de Europese toernooien. Drie gepubliceerde regels, "
                         "alle drie uit de doelpuntenmarkt, geen ervan boven zijn eigen lat."}
H["last_run_bevinding"] = (
    "Drie dingen. (1) ACHT VAN DE TIEN DUELS HEBBEN EEN OMGEREKENDE PLOEG, de hoogste verhouding "
    "van welke rundag dan ook: zeven promovendi omhoog langs TIER2 en twee degradanten omlaag "
    "langs TIER1 (Burnley en Wolverhampton Wanderers, beide met het gemeten fd_pair E0/E1). Geen "
    "enkele omrekening draaide op POOLED_GAP. Gevolg: maar twee FULL-duels, en dus een dag waarop "
    "de LIGHT-lat van 16,0 pp bijna alles bepaalt. (2) WIECZYSTA KRAKOW PASSEERT "
    "conversion_in_range OP DE GRENS: relatieve verdediging 0.929 tegen een gemeten bovengrens van "
    "exact 0.929, en dat is de hoogst-rangschikkende bet van de dag. AC Horsens viel aan dezelfde "
    "poort juist af (aanval 0.860 tegen een ondergrens van 0.989) en is het enige NONE-duel. Die "
    "twee naast elkaar zijn de scherpste illustratie van die poort tot nu toe. (3) DE "
    "NIET-MONOTONIE VAN POORT 9 IS NU OOK OP FULL ZICHTBAAR: Eintracht Frankfurt – 1. FC Köln "
    "(Under 3,5 op FULL, +3,10 pp) is gepubliceerd zonder dat poort 9 hem heeft getoetst, omdat "
    "unders.check elke Under ONDER de gewone drempel van 8,0 doorlaat op de aanname dat `edge` "
    "daar de bindende poort is — en sinds §5b (20 sep) is `edge` geen poort meer maar een "
    "afkapping. Een FULL-Under met 8,5 pp zou wél zijn geblokkeerd. Dezelfde bevinding als die van "
    "Run B op 14 oktober, nu met een gepubliceerde regel eronder in plaats van een geblokkeerde. "
    "Deze run heeft de poort niet aangeraakt: §1h en §6g verbieden dat op eigen initiatief.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

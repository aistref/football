"""Run B, 16 okt 2026 — bronprobe voor source-health.json en twee correcties in coverage.json.

Vijftien duels over tien competities. Beide bronkanten zijn deze run werkelijk gebruikt — Fotmob
voor de standen, de context en de daglijsten, The Odds API voor de zes bulk-aanroepen en zes
BTTS-aanroepen, BetExplorer voor het gratis 1X2-marktgemiddelde en voor de bevestiging door een
tweede bron — dus de statusregels komen hier uit echte aanroepen en niet uit een probe.

Twee dingen gaan ook in `coverage.json`, want het zijn metingen over de bron en niet over de run:

1. **De BetExplorer-slug van Série A (BRA)** is verhuisd van `brazil/serie-a-betano` naar
   `brazil/serie-a`. De oude slug geeft HTTP 200 met nul rijen — de stille faalmodus die
   coverage.json op 20 september nog juist voor de nieuwe slug noteerde.
2. **Energie Cottbus** laat zien dat er voor het divisiepaar 2. Bundesliga <-> 3. Liga geen
   gemeten factor is. Dat is geen fout maar een grens, en hij hoort opgeschreven te staan zodat
   een volgende run niet opnieuw gaat zoeken.
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
    print(f"{key:18} {status:8} {detail[:110]}...")


note("fotmob", "ok",
     "16 okt (run B): daglijsten 16 en 17 okt opgehaald (102 resp. 198 competities, 178 resp. 791 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand "
     "(afsluitcode 0). Standen van alle tien spelende competities geleverd — zes met xG "
     "(Allsvenskan 67, Segunda División 140, Serie B 86, 2. Bundesliga 146, Austrian Bundesliga 38, "
     "Série A BRA 268) en vier zonder (Croatian HNL 252, Hungarian NB I 212, Romanian SuperLiga 189, "
     "Keuken Kampioen Divisie 111) — en context opgehaald voor alle 15 duels in het inzetvenster. "
     "Stadioncontrole: één ECHTE verplaatsing (Rudeš – Rijeka in ŠRC Velika Gorica) en één VALS "
     "alarm (MTK Budapest, 'Stadium' tegen 'Stadion'), dat laatste gerepareerd in "
     "scripts/context._norm_ground.")

note("the_odds_api", "ok",
     "16 okt (run B): api_check.py OK, 48 actieve voetbalcompetities, quota 19395 over / 605 "
     "gebruikt deze maand. 24 credits uitgegeven: 6 bulk-aanroepen (h2h+spreads+totals, 3 credits "
     "elk, voor soccer_sweden_allsvenskan, soccer_spain_segunda_division, soccer_italy_serie_b, "
     "soccer_germany_bundesliga2, soccer_austria_bundesliga en soccer_brazil_campeonato) en 6 "
     "BTTS-aanroepen à 1 credit. Let op dat de lijst 'relevante sportkeys' van api_check.py "
     "krapper is dan de werkelijkheid: soccer_sweden_allsvenskan, soccer_austria_bundesliga en "
     "soccer_brazil_campeonato staan er niet in en leverden alle drie gewoon events.")
note("oddsapi", "ok",
     "16 okt (run B): fetch_bulk gaf voor zes competities h2h, spreads en totals (8 tot 20 events "
     "per competitie); fetch_event_markets gaf btts voor 6 duels. Pinnacle, Betfair en Matchbook "
     "zaten in de respons — bij Rapid Wien – Hartberg had Betfair de beste 1X2-prijs aan beide "
     "kanten en Pinnacle de beste X. net_price is toegepast; geen van de vier gepubliceerde regels "
     "staat op een beurs, dus de commissieregel bond nergens op de bet zelf. Beste prijs tegen het "
     "BetExplorer-gemiddelde: +9,07% op dat duel.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

probes = {
    "Série A (BRA) — NIEUWE slug": "https://www.betexplorer.com/football/brazil/serie-a/",
    "Série A (BRA) — OUDE slug": "https://www.betexplorer.com/football/brazil/serie-a-betano/",
    "Keuken Kampioen Divisie (NED)": "https://www.betexplorer.com/football/netherlands/eerste-divisie/",
    "Croatian HNL (CRO)": "https://www.betexplorer.com/football/croatia/hnl/",
}
det = []
for naam, url in probes.items():
    try:
        rows = betexplorer.fetch_league_fixtures(url)
        det.append(f"{naam}: {len(rows)} fixtures met 1X2-gemiddelde")
    except Exception as e:
        det.append(f"{naam}: FAIL {type(e).__name__}: {e}")
note("betexplorer", "ok",
     "16 okt (run B): " + "; ".join(det) + ". ALLE ZEVENTIEN competities van de runlijst zijn langs "
     "BetExplorer bevestigd als tweede bron naast de Fotmob-daglijst (§1): 15 duels tegen 15, eens "
     "op alle zeventien. VIER competities hebben geen sportkey bij The Odds API en draaien hierop "
     "als ENIGE 1X2-bron: Croatian HNL, Hungarian NB I, Romanian SuperLiga en Keuken Kampioen "
     "Divisie — marktgemiddelde, bookmaker niet herleidbaar, edge systematisch te laag. Eén van de "
     "vier gepubliceerde regels komt uit die groep (Oțelul Galați, 1X2 @1,63). BELANGRIJK: de slug "
     "van Série A (BRA) is verhuisd — brazil/serie-a-betano geeft HTTP 200 met 0 rijen en "
     "brazil/serie-a geeft 20 rijen. Dat is de stille faalmodus; coverage.json is bijgewerkt.")

note("understat", "n/a",
     "16 okt (run B): geen aanroep. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue 1 — "
     "geen daarvan staat op de runlijst van Run B.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "B", "date": "2026-10-16",
                 "matches_in_window": 15, "bets": 4,
                 "note": "Vijftien duels in het inzetvenster [08:00 NL 16 okt, 08:00 NL 17 okt) over "
                         "tien van de zeventien competities; zeven hadden geen wedstrijd (vrijdag in "
                         "een gewone speelweek). Vier gepubliceerde regels op rangorde (§5b), waarvan "
                         "ÉÉN zijn eigen lat haalt: Rapid Wien – Hartberg Under 3,5 @1,90 (+16,12 pp, "
                         "FULL, ook boven de verzwaarde lat van 10,0 pp van poort 9)."}
H["last_run_bevinding"] = (
    "Twee stille faalstanden op één ochtend, beide gevonden en beide gerepareerd, en dat is de "
    "bevinding van de dag. (1) DE BETEXPLORER-SLUG VAN SÉRIE A (BRA) IS VERHUISD: coverage.json "
    "schrijft sinds 20 sep 'brazil/serie-a-betano' voor met de notitie dat 'brazil/serie-a' toen "
    "HTTP 200 met nul rijen gaf; vandaag is het precies omgekeerd. Nul rijen geeft geen "
    "foutmelding en leest als 'geen marktgemiddelde voor dit duel', dus Mirassol – Internacional "
    "was zijn de-vigde marktoordeel kwijtgeraakt — het kalibratieblok van §6e en poort 8, niet de "
    "bet zelf (Série A heeft een sportkey). Dezelfde faalvorm als het Serie B-id van 29 september. "
    "(2) DE STADIONCONTROLE GAF EEN VALS ALARM dat precies de reparatie van 6 september herhaalt, "
    "één laag dieper: na het weghalen van de accenten bleef 'Hidegkuti Nandor Stadium' (Fotmobs "
    "wedstrijdpagina) ongelijk aan 'Hidegkuti Nándor Stadion' (teampagina), want het generieke "
    "woord voor stadion verschilt per taal. _norm_ground laat dat woord vanaf nu weg, ook als "
    "prefix (Roemeens 'Stadionul X'), en de ECHTE verplaatsing van dezelfde dag blijft staan: "
    "Rudeš – Rijeka wordt gespeeld in ŠRC Velika Gorica. Dat is de toets die de reparatie moest "
    "halen. EN DE DERDE BEVINDING IS GEEN REPARATIE MAAR EEN GRENS: Energie Cottbus komt uit de "
    "3. Liga en promotion.TIER2 kent voor '2. Bundesliga (GER)' geen divisie eronder, dus er is "
    "geen gemeten factor en het duel komt terecht op NONE. §4 verbiedt er een te verzinnen.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

# ---- coverage.json: twee metingen erbij, als VERENIGING en niet als vervanging (Stage -2) ----
C = json.load(open("data/coverage.json"))
bra = C["competitions"]["Série A (BRA)"]
bra["betexplorer"] = "brazil/serie-a"
bra["notes"] = bra["notes"] + (
    " Run B 16 okt 2026 — BETEXPLORER-SLUG VERHUISD: brazil/serie-a-betano geeft nu HTTP 200 met 0 "
    "rijen en brazil/serie-a geeft 20 rijen (met het duel van vandaag erbij). Dat is omgekeerd aan "
    "wat hierboven op 20 sep is gemeten; de slug is dus verplaatst en de oude blijft als stille "
    "faalmodus bestaan. Gebruik brazil/serie-a en controleer het aantal rijen in plaats van op de "
    "HTTP-status te vertrouwen. fotmob_id 268 opnieuw bevestigd (20 ploegen, xG in beide "
    "kalenderjaren: 2025 38 speeldagen avg_xg 1.267, 2026 30 speeldagen avg_xg 1.332); "
    "league_level koos route `lopend` (30 van 38 speeldagen).")
gb2 = C["competitions"]["2. Bundesliga (GER)"]
gb2["notes"] = gb2.get("notes", "") + (
    " Run B 16 okt 2026 — GEEN DIVISIE ERONDER IN promotion.TIER2. Energie Cottbus is promovendus "
    "uit de 3. Liga en staat dus niet in de 2. Bundesliga-stand van 2025/2026; de omrekening van §4 "
    "probeert dan TIER1 (Bundesliga, als degradant) en vindt hem daar evenmin, waarna het duel op "
    "NONE komt. Dat is correct: er is geen gemeten factor voor het paar 2. Bundesliga <-> 3. Liga "
    "(football-data.co.uk heeft geen D3 en promotion.MEASURED_TIER2_GAP dekt GER niet op dit "
    "niveau), en §4 verbiedt er een te verzinnen. Verwacht dit elk seizoen bij de drie Duitse "
    "promovendi; NONE is de eerlijke uitkomst en geen storing.")
json.dump(C, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt (Série A slug + 2. Bundesliga divisiepaar).")

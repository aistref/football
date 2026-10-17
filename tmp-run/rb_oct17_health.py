"""Run B, 17 okt 2026 — bronprobe voor source-health.json en één meting in coverage.json.

74 duels over zestien competities. Beide bronkanten zijn deze run werkelijk gebruikt — Fotmob
voor de standen, de context en de daglijsten, The Odds API voor elf bulk-aanroepen en 41
BTTS-aanroepen, BetExplorer voor het gratis 1X2-marktgemiddelde en voor de bevestiging door een
tweede bron — dus de statusregels komen hier uit echte aanroepen en niet uit een probe.

Eén ding gaat ook in `coverage.json`, want het is een meting over de BRON en niet over de run:
de MLS-ploeg 'LA Galaxy' heet bij BetExplorer 'Los Angeles Galaxy', en die koppeling ontbrak.
Dat kostte vandaag het marktgemiddelde van één duel en daarmee de toetsing van poort 8 op een
selectie die anders gepubliceerd zou zijn. De alias zelf staat in `scripts/teamnames.py`.
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
     "17 okt (run B): daglijsten 17 en 18 okt opgehaald; idcheck.py gaf voor alle 33 fotmob_id's "
     "uit coverage.json een bruikbare stand (afsluitcode 0). Standen van alle zestien spelende "
     "competities geleverd — elf met xG (Greek Super League 135, Eliteserien 59, Allsvenskan 67, "
     "Segunda División 140, Serie B 86, 2. Bundesliga 146, Austrian Bundesliga 38, English League "
     "One 108, English League Two 109, MLS 130, Série A BRA 268) en vijf zonder (Czech First "
     "League 122, Croatian HNL 252, Hungarian NB I 212, Romanian SuperLiga 189, Keuken Kampioen "
     "Divisie 111) — en context opgehaald voor alle 74 duels in het inzetvenster, ook de 13 op "
     "tier NONE en de 19 die de cap afkapte. Stadioncontrole: NUL alarmen op 74 duels, dus de "
     "_norm_ground-reparatie van 16 okt geeft geen valse alarmen meer. Geen enkel duel had om "
     "05:30 NL een bevestigde opstelling (alle 74 op lastStarting11).")

note("the_odds_api", "ok",
     "17 okt (run B): api_check.py OK, 50 actieve voetbalcompetities, quota 19311 over / 689 "
     "gebruikt deze maand. 74 credits uitgegeven: 11 bulk-aanroepen (h2h+spreads+totals, 3 credits "
     "elk) en 41 BTTS-aanroepen à 1 credit. Marktbalans: alle elf inkoopbare competities kregen via "
     "de bulk alle zes markten, dus elf op elf — geen competitie met alleen een uitkomst- of alleen "
     "een doelpuntenmarkt. Let op dat de lijst 'relevante sportkeys' van api_check.py krapper is "
     "dan de werkelijkheid: soccer_norway_eliteserien, soccer_sweden_allsvenskan, "
     "soccer_greece_super_league, soccer_austria_bundesliga, soccer_england_league1, "
     "soccer_england_league2, soccer_usa_mls en soccer_brazil_campeonato staan er niet in en "
     "leverden alle acht gewoon events.")

note("oddsapi", "ok",
     "17 okt (run B): fetch_bulk gaf voor elf competities h2h, spreads en totals (8 tot 24 events "
     "per competitie); fetch_event_markets gaf btts voor 41 duels. Pinnacle, Betfair en Matchbook "
     "zaten in de respons. net_price is toegepast en bond op TWEE van de vijf gepubliceerde regels: "
     "Bradford City – Stevenage Under 2,5 bij Matchbook (1,67 bruto / 1,6566 netto) en Levadiakos – "
     "NFC Volos 1X2 bij Betfair (2,26 bruto / 2,2348 netto). De andere drie staan bij 1xBet (twee) "
     "en Pinnacle (één).")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

probes = {
    "MLS (USA)": "https://www.betexplorer.com/football/usa/mls/",
    "Série A (BRA)": "https://www.betexplorer.com/football/brazil/serie-a/",
    "English League Two (ENG)": "https://www.betexplorer.com/football/england/league-two/",
    "Romanian SuperLiga (ROU)": "https://www.betexplorer.com/football/romania/superliga/",
}
det = []
for naam, url in probes.items():
    try:
        rows = betexplorer.fetch_league_fixtures(url)
        det.append(f"{naam}: {len(rows)} fixtures met 1X2-gemiddelde")
    except Exception as e:
        det.append(f"{naam}: FAIL {type(e).__name__}: {e}")
note("betexplorer", "ok",
     "17 okt (run B): " + "; ".join(det) + ". ALLE ZEVENTIEN competities van de runlijst zijn langs "
     "BetExplorer bevestigd als tweede bron naast de Fotmob-daglijst (§1): 74 duels tegen 74, eens "
     "op alle zeventien, inclusief de Swiss Super League op 0 tegen 0. VIJF competities hebben geen "
     "sportkey bij The Odds API en draaien hierop als ENIGE 1X2-bron: Czech First League, Croatian "
     "HNL, Hungarian NB I, Romanian SuperLiga en Keuken Kampioen Divisie. BELANGRIJK — "
     "NAAMKOPPELING: de MLS-ploeg heet bij Fotmob 'LA Galaxy' en hier 'Los Angeles Galaxy', en die "
     "koppeling ontbrak. Gevolg: LA Galaxy – San Diego FC was het enige van de 74 duels zonder "
     "marktgemiddelde, dus zonder kalibratieblok (§6e) EN met poort 8 op 'geen marktoordeel' — open "
     "zonder te zijn getoetst, op een duel dat in de eerste doorrekening een gepubliceerde regel "
     "opleverde (de-vigde marktkans 0,322, onder de ondergrens 0,35). Alias toegevoegd aan "
     "scripts/teamnames.py; daarnaast zoekt de soepele terugval in find_1x2 nu in alle rijen van de "
     "competitie in plaats van alleen in de dagpool, want 'is_today' is hier de PAGINA-datum: MLS "
     "had 2 van de 16 rijen zo gelabeld. Dezelfde stille faalvorm als het Serie B-id en de "
     "verhuisde Série A-slug.")

note("understat", "n/a",
     "17 okt (run B): geen aanroep. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue 1 — "
     "geen daarvan staat op de runlijst van Run B.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "B", "date": "2026-10-17",
                 "matches_in_window": 74, "bets": 5,
                 "note": "74 duels in het inzetvenster [08:00 NL 17 okt, 08:00 NL 18 okt) over "
                         "zestien van de zeventien competities; alleen Swiss Super League had geen "
                         "wedstrijd. De cap bond voor het eerst sinds 11 okt: 55 doorgerekend, 19 "
                         "afgekapt. Vijf gepubliceerde regels op rangorde (§5b), waarvan TWEE hun "
                         "eigen lat halen: Bradford City – Stevenage Under 2,5 @1,6566 (+15,12 pp, "
                         "FULL, ook boven de verzwaarde lat van 10,0 pp van poort 9) en Levadiakos – "
                         "NFC Volos 1X2 @2,2348 (+17,98 pp, FULL). VIER van de vijf regels zijn een "
                         "Under op FULL — de kant waarvan §6g de scheefstand meet."}
H["last_run_bevinding"] = (
    "EEN NAAMKOPPELING LIET EEN BET DOOR DIE POORT 8 HOORT TE BLOKKEREN, en dat is de bevinding van "
    "de dag. Fotmob schrijft 'LA Galaxy', BetExplorer 'Los Angeles Galaxy'; na _DROP blijft "
    "{la, galaxy} tegen {los, angeles, galaxy} over en dat is geen deelverzameling, dus resolve "
    "koppelde niet. De soepele terugval kon het duel niet eens zien omdat die alleen in de dagpool "
    "van BetExplorer zocht en MLS 2 van de 16 rijen met een vandaag-label had — precies de "
    "scheefstand waarvoor de is_today-filter op 7 oktober al uit de EXACTE lus is gehaald, maar die "
    "in de terugval bleef staan. Gevolg: één duel van de 74 zonder marktgemiddelde, dus zonder "
    "kalibratieblok, en poort 8 op 'geen marktoordeel over wie de mindere is' — open zonder te zijn "
    "getoetst. In de eerste doorrekening stond 1X2 San Diego FC @3,25 (+10,11 pp) daardoor als "
    "vijfde regel op de lijst; met de prijzen erbij is de de-vigde marktkans van San Diego 0,322 en "
    "sluit poort 8 onder 0,35. Twee reparaties: de alias in scripts/teamnames.py (zodat ook "
    "settling.py en het kalibratielogboek koppelen) en de ruimere terugval in find_1x2. Daarna is "
    "de hele analyse opnieuw gedraaid. DIT IS IN ZES WEKEN DE VIERDE KEER dat deze faalvorm "
    "toeslaat (Serie B-id 29 sep, Série A-slug 16 okt, calibration.py settle 30 sep, nu dit), en "
    "alle vier keer was het symptoom hetzelfde: geen foutmelding, alleen een leeg veld. Wat er "
    "structureel uit volgt en als openstaand punt in het runrapport staat: een poort die 'open' "
    "rapporteert omdat zijn INVOER ontbreekt, hoort in data/run-state/ niet hetzelfde te heten als "
    "een poort die open is omdat hij is getoetst.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

# ---- coverage.json: één meting erbij, als VERENIGING en niet als vervanging (Stage -2) ----
C = json.load(open("data/coverage.json"))
mls = C["competitions"]["MLS (USA)"]
mls["notes"] = mls.get("notes", "") + (
    " Run B 17 okt 2026 — NAAMKOPPELING BETEXPLORER: 'LA Galaxy' (Fotmob) heet daar 'Los Angeles "
    "Galaxy', en zonder alias koppelt resolve niet ({la, galaxy} is geen deelverzameling van "
    "{los, angeles, galaxy}). Dat kostte het marktgemiddelde van LA Galaxy – San Diego FC en "
    "daarmee de TOETSING van poort 8 op een selectie die anders was gepubliceerd. Alias staat nu in "
    "scripts/teamnames.py, naast 'red bull new york' <-> 'new york red bulls' uit dezelfde "
    "competitie. LET OP de tweede helft van dit geval: BetExplorer labelt 'is_today' naar zijn "
    "eigen pagina-datum, dus van de zestien MLS-rijen stonden er maar twee op vandaag terwijl er "
    "veertien in het inzetvenster vielen. Filter hier nooit op is_today, ook niet in een soepele "
    "naamterugval.")
json.dump(C, open("data/coverage.json", "w"), ensure_ascii=False, indent=1)
print("coverage.json bijgewerkt (MLS-naamkoppeling + is_today-waarschuwing).")

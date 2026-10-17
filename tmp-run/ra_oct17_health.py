"""Run A, 17 okt 2026 — bronprobe voor source-health.json.

47 duels in het inzetvenster over tien competities: de volle Europese zaterdag en de grootste
rundag van deze maand. Alle drie de bronkanten zijn deze run werkelijk gebruikt — Fotmob voor de
daglijsten, de 33 standen, de context van alle 47 duels en de divisies eronder/erboven voor
zeventien omrekeningen, The Odds API voor de bulk (negen competities) en BTTS (33 duels),
BetExplorer voor het gratis 1X2-marktgemiddelde van alle tien competities, als tweede bron op de
vraag wélke wedstrijden er zijn, én als enige bron voor de vijf bekers. De statusregels komen dus
uit echte aanroepen en niet uit een probe.

BetExplorer staat op `ok` en niet op `partial_failure`, maar met een voorbehoud dat er hoort te
staan: de Ekstraklasa gaf bij de eerste bevestigingsronde een `TimeoutError` en kwam pas bij een
tweede aanroep met een ruimere timeout binnen. Dat is een ONTBREKENDE meting en geen afwijking,
en het is het soort storing dat als "15 van 16 eens" in een rapport verdwijnt.
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
     "17 okt (run A): daglijsten 17 en 18 okt opgehaald (200 resp. 174 competities, 806 resp. 580 "
     "wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. "
     "Standen van alle tien spelende competities geleverd, alle tien met xG in zowel 2025/2026 als "
     "het lopende seizoen. Context opgehaald voor alle 47 duels, ook voor de twee op tier NONE. "
     "Daarnaast de standen van zeven divisies eronder/erboven voor de zeventien omrekeningen van "
     "§4: Championship (48, beide richtingen), Serie B (86), 2. Bundesliga (146), Ligue 2 (110), "
     "League One (108), Eerste Divisie (111), 1. Lig (165), Championship SCO (123), I Liga (197) en "
     "Premier League (47, richting omlaag). Ook de drie Engelse divisies van de TIER2-keten zijn "
     "opgevraagd voor de 32 FA Cup-ties (Championship, League One, League Two) — geen van de "
     "64 ploegen staat erin, wat de NONE-uitkomst van die ronde een gemeten uitkomst maakt.")

note("the_odds_api", "ok",
     "17 okt (run A): api_check.py OK, 50 actieve voetbalcompetities, quota 19371 over / 629 "
     "gebruikt deze maand. 60 credits uitgegeven: 9 bulk-aanroepen (h2h+spreads+totals, 3 credits "
     "per competitie) en 33 BTTS-aanroepen à 1 credit. Negen van de tien spelende competities "
     "hebben een sportkey; de Scottish Premiership heeft er geen en viel dus buiten de betaalde "
     "inkoop (daar is BetExplorer de enige 1X2-bron).")

note("oddsapi", "ok",
     "17 okt (run A): fetch_bulk gaf voor alle negen sportkeys events met h2h, spreads en totals "
     "(20, 19, 20, 17, 17, 13, 17, 9 en 9 events); fetch_event_markets gaf btts voor 33 duels. Nul "
     "fouten in store['errors']. Pinnacle in de respons voor 40 van de 47 duels (gebruikt voor "
     "Stage 5 stap 2, gemiddelde marge 3,79%), Betfair en Matchbook ook; net_price toegepast op de "
     "Matchbook-koers van de gepubliceerde regel Motor Lublin – Śląsk Wrocław (1.61 bruto / 1.5978 "
     "netto). De winst van de beste prijs boven het BetExplorer-marktgemiddelde liep van +5,59% "
     "(Ekstraklasa) tot +10,52% (Eredivisie).")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md §3) — "
     "geen gat en geen actiepunt. Kanskant komt van Fotmob en Understat.")

probes = {
    "Premier League (ENG)": "https://www.betexplorer.com/football/england/premier-league/",
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
     "17 okt (run A): " + "; ".join(det) + ". Deze run in drie rollen gebruikt: (1) het gratis "
     "1X2-marktgemiddelde voor alle tien competities, voor het kalibratieblok van §6e en poort 8, "
     "en voor de Scottish Premiership als ENIGE 1X2-bron; (2) als TWEEDE BRON op de vraag wélke "
     "wedstrijden er zijn — zestien van de zestien competities met een fotmob_id eens, 47 duels "
     "tegen 47; (3) als ENIGE bron voor de vijf bekers zonder fotmob_id. WEL EEN HAPERING: de "
     "Ekstraklasa gaf bij de eerste bevestigingsronde een TimeoutError en kwam pas bij een tweede "
     "aanroep met een timeout van 120 seconden binnen (216 fixtures). Dat is een ontbrekende "
     "meting en geen afwijking, maar het is wel de enige bronstoring van deze run. Geen enkele "
     "slug viel in de homepage-redirect-faalmodus.")

note("understat", "ok",
     "17 okt (run A): fetch_league voor alle VIJF de Understat-competities (Premier League, Serie "
     "A, La Liga, Bundesliga, Ligue 1, seizoen 2025) gaf een volledige stand — voor het eerst "
     "sinds dagen spelen ze alle vijf op dezelfde dag. Werkelijk BRUIKBAAR voor 13 van de 21 duels "
     "in die vijf competities; bij de andere acht is een ploeg promovendus en staat terecht niet in "
     "de stand van 2025/2026 (Hull City, Ipswich Town, Venezia, Elversberg, Schalke 04, Paderborn, "
     "Troyes). Geen enkele stille naamfout deze run: de alias-reparatie van 16 oktober ('fc "
     "cologne') hield, en er is geen duel waar understat_pair None gaf zonder reden.")

H["sources"] = S
H["updated"] = now
H["last_run"] = {"run": "A", "date": "2026-10-17",
                 "matches_in_window": 47, "bets": 5,
                 "note": "47 duels in het inzetvenster [08:00 NL 17 okt, 08:00 NL 18 okt) over "
                         "tien competities: Championship 11, Bundesliga 6, Premier League 5, "
                         "Scottish Premiership 5, La Liga 4, Super Lig 4, en Serie A, Ligue 1, "
                         "Eredivisie en Ekstraklasa elk 3. De volle Europese zaterdag en de "
                         "grootste rundag van deze maand. Daarnaast 32 FA Cup-ties in het venster "
                         "die alle 32 op tier NONE uitkomen. Vijf gepubliceerde regels — de volle "
                         "MAX_SHORTLIST van een zaterdag — alle vijf uit de doelpuntenmarkt, "
                         "waarvan twee boven hun eigen lat."}
H["last_run_bevinding"] = (
    "Drie dingen. (1) DE FA CUP LEVERT 32 TIES IN HET VENSTER EN ALLE 32 ZIJN NONE, en dat is "
    "gemeten en niet aangenomen: promotion.shared_lower_division vindt voor geen enkele tie een "
    "gedeelde lagere divisie, want deze vierde kwalificatieronde speelt zich af in de National "
    "League en daaronder en de Engelse TIER2-keten houdt op bij League Two. Dat is exact wat "
    "prompts/run-a.md voor een lage-divisie bekerronde voorspelt. Het is ook de reden dat de cap "
    "niet bindt: met die 32 erbij waren het 79 kandidaten geweest op een zaterdagcap van 55, en "
    "dan had de datadekkingspoort niet gesneden maar de klok. (2) DE HOOGST-RANGSCHIKKENDE REGEL "
    "HAALT POORT 9 HERIJKT EN NIET RUW: Strasbourg – Paris Saint-Germain, Under 3,5 op FULL, "
    "+10,02 pp herijkt tegen de verzwaarde lat van 10,0 en +9,44 pp ruw. Dat is de spiegel van "
    "`herijking` en precies het geval waarvoor §5a `bet_beide` als controle heeft neergezet in "
    "plaats van als aanname; §1 en §5a laten de poorten op de herijkte kans binden, dus de regel "
    "is gepubliceerd met bet_beide = FALSE in `notes`. De reeks herijking_omgekeerd staat op 3 "
    "afgewikkelde gevallen (0 winnaars) waar §6d er ~30 eist. (3) DE NIET-MONOTONIE VAN POORT 9 "
    "STAAT ER VOOR DE TWEEDE DAG OP RIJ, nu met twee gepubliceerde regels eronder: Union Berlin – "
    "Borussia Dortmund (Under 3,5 op FULL, +7,64 pp) en Roma – Genoa (Under 3,5 op FULL, "
    "+5,76 pp) zijn beide gepubliceerd zonder dat poort 9 ze heeft getoetst, omdat unders.check "
    "elke Under ONDER de gewone drempel van 8,0 doorlaat op de aanname dat `edge` daar de "
    "bindende poort is — en sinds §5b (20 sep) is `edge` geen poort meer maar een afkapping. Een "
    "FULL-Under met 8,5 pp zou wél zijn geblokkeerd. Deze run heeft de poort niet aangeraakt: §1h "
    "en §6g verbieden dat op eigen initiatief.")
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

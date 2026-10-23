"""Run A, 23 okt 2026 — bronprobe voor source-health.json.

13 duels in het inzetvenster over TWAALF competities: een vrijdagavond met in vrijwel elke
competitie één openingsduel (de Ekstraklasa twee). Het spiegelbeeld van gisteren, toen 36 duels
in twee Europese toernooien zaten. Alle vier de bronkanten werkelijk in gebruik. Fotmob voor de
daglijsten, de 33 standen van `idcheck.py`, de context van alle 13 duels, de
voorbeschouwingsblokken van de vier bets en de marktvormtelling van alle 13 duels. The Odds API
voor de bulk (twaalf competities) en BTTS (10 duels). BetExplorer voor het gratis
1X2-marktgemiddelde, als tweede bron op de vraag wélke wedstrijden er zijn, én als enige bron
voor de vijf bekers. Understat deed deze run WEL mee, voor twee van de dertien duels.

GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.
"""

import json, datetime

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
     "23 okt (run A): daglijsten 23 en 24 okt opgehaald (112 competities / 220 wedstrijden resp. "
     "199 competities / 808 wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit "
     "coverage.json een bruikbare stand. Standen van alle twaalf spelende competities geleverd, "
     "alle twaalf met xG in zowel 2025/2026 als het lopende seizoen, plus de standen van de "
     "divisies eronder/erboven voor de zes omgerekende ploegen (promotion.py). Context opgehaald "
     "voor alle 13 duels, zonder een fout; 12 van 13 staan in het contextlogboek - bij Kortrijk - "
     "KV Mechelen geeft Fotmob GEEN opstelling (lineupType 'unavailable') en geen bruikbare "
     "selectiewaarde (squad_value 0 voor beide ploegen), dus het aandeel ontbrekende spelers is "
     "daar niet te berekenen en ctxlog.py slaat die rij over. Poort 7 staat daar per §1c dus "
     "OPEN; het duel levert geen regel op. TWEEDE OPMERKING OVER DE CONTEXT, en die is nieuw: "
     "venue.name is voor GEEN ENKEL van de 13 duels geleverd, dus context.check_venue heeft "
     "niets kunnen vergelijken en 'relocated = False' betekent hier 'geen verplaatsing gemeten' "
     "in plaats van 'gemeten dat er geen verplaatsing is'. Gisteren, op een Europese avond, gaf "
     "dezelfde controle bij vijf van de 36 duels wel een stadionnaam en een verplaatsing; het is "
     "dus geen storing maar wel een leegte die eerlijk genoemd hoort te worden. Daarnaast het "
     "voorbeschouwingsblok van de vier gepubliceerde duels (preview.match_block) en de "
     "marktvormtelling van alle 13 duels (marketform.match_block) - nul fouten. GEEN GAT deze "
     "run.")

note("the_odds_api", "ok",
     "23 okt (run A): api_check.py OK, 47 actieve voetbalcompetities, quota 19013 over / 987 "
     "gebruikt deze maand. 46 credits uitgegeven: 12 bulk-aanroepen (h2h+spreads+totals, 3 "
     "credits per competitie = 36) en 10 BTTS-aanroepen a 1 credit. Alle twaalf spelende "
     "competities hebben een sportkey, dus er is deze run geen enkel duel waar BetExplorer de "
     "enige 1X2-bron is en de edge systematisch te laag uitvalt. De beste prijs lag gemiddeld "
     "5,79% boven het BetExplorer-marktgemiddelde (van +3,42% bij Kortrijk - KV Mechelen tot "
     "+7,69% bij Go Ahead Eagles - Telstar).")

note("oddsapi", "ok",
     "23 okt (run A): fetch_bulk gaf voor alle twaalf sportkeys events met h2h, spreads en "
     "totals (6 tot 21 events per competitie); fetch_event_markets gaf btts voor alle 10 duels "
     "met een kandidaat-edge, zonder uitval. store['errors'] is LEEG over de hele run. "
     "net_price is gebruikt waar nodig, maar GEEN van de vier gepubliceerde regels staat op een "
     "beurs: Randers komt van Pinnacle, Brest van 1xBet en beide Over 2.5-regels van 1xBet. "
     "Binnen de 191 doorgerekende selecties zitten wel beurskoersen en die zijn alle netto "
     "gerekend.")

note("betexplorer", "ok",
     "23 okt (run A): alle twaalf spelende competities leverden hun 1X2-marktgemiddelde (6 tot "
     "20 fixtures per competitie, in elk geval het duel van vandaag). Tweede bron op de vraag "
     "welke wedstrijden er zijn: 16 van 16 competities eens met de Fotmob-daglijst, 13 duels "
     "tegen 13, nul afwijkingen (ra_oct23_bevestiging.py). En de enige bron voor de vijf bekers "
     "zonder fotmob_id: alle vijf leveren teamparen op de fixturepagina (40, 8, 8, 26 en 16), "
     "dus geen van de drie faalmodi is opgetreden, en alle vijf nul teamparen IN het "
     "inzetvenster - eerstvolgende ronde League Cup 27 okt, KNVB Beker 27 okt, DFB Pokal 27 okt, "
     "FA Cup 6 nov en Coppa Italia 1 dec. Die uitkomst is bovendien kruiselings bevestigd op de "
     "Fotmob-daglijst, waarin geen van de vijf voorkomt. Geen Cloudflare-challenge, geen 403.")

note("understat", "ok",
     "23 okt (run A): WEL aangeroepen en geleverd, voor twee van de dertien duels. Van de vijf "
     "competities die Understat dekt speelden de Bundesliga en de Ligue 1 vandaag, dus VfB "
     "Stuttgart - Borussia Monchengladbach en Brest - Nice hebben een tweede, onafhankelijk "
     "xG-model naast Fotmob (§4), inclusief rollende xG over acht duels. Bij Brest - Nice is dat "
     "direct van belang: dat duel levert een gepubliceerde regel op, en het is de enige van de "
     "vier bets met kansinput uit twee verschillende xG-modellen in plaats van twee doorsnedes "
     "van een. De overige elf duels (waaronder de Premier League- en La Liga-duels, want die "
     "spelen met een promovendus die Understat niet in zijn tabel heeft) krijgen hun kansinput "
     "uitsluitend van Fotmob.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Fotmob leverde deze run zonder fout en "
     "Understat deed voor twee duels mee, dus §2 is gedekt en er is niets te doen. Wordt pas een "
     "echt probleem zodra Fotmob omvalt.")

H["last_run"] = {"run": "A", "date": "2026-10-23",
                 "note": "13 duels in het inzetvenster over twaalf competities, geen enkel "
                         "kruis-grensduel en geen enkele NONE - alle 13 doorgerekend (7 FULL, "
                         "6 LIGHT met een omgerekende ploeg). 4 bets van de 4 publiceerbare "
                         "selecties, waarvan 2 hun lat halen en 2 op rangorde (§5b). Nul "
                         "bronstoringen, 46 van 1055 credits."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

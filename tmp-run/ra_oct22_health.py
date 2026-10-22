"""Run A, 22 okt 2026 — bronprobe voor source-health.json.

36 duels in het inzetvenster over TWEE competities: een volle Europa League- en Conference
League-avond, 18 duels elk. Alle drie de bronkanten werkelijk in gebruik. Fotmob voor de
daglijsten, de 33 standen van `idcheck.py`, de context van alle 36 duels, de binnenlandse
standen voor de kruis-grensomrekening van §4 (alle 72 ploegen), de voorbeschouwingsblokken van
de twee bets en de marktvormtelling van 23 duels. The Odds API voor de bulk (twee competities)
en BTTS (19 duels). BetExplorer voor het gratis 1X2-marktgemiddelde, als tweede bron op de vraag
wélke wedstrijden er zijn, én als enige bron voor de vijf bekers. Understat deed deze run NIET
mee: geen van de vijf competities die hij dekt speelt vandaag.

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
     "22 okt (run A): daglijsten 22 en 23 okt opgehaald (26 competities / 80 wedstrijden resp. "
     "109 competities / 212 wedstrijden); idcheck.py gaf voor alle 33 fotmob_id's uit "
     "coverage.json een bruikbare stand. Standen van beide spelende competities geleverd "
     "(Europa League en Conference League, elk 36 ploegen), beide met xG in zowel 2025/2026 als "
     "het lopende seizoen. Context opgehaald voor alle 36 duels, zonder een fout; 35 van 36 "
     "staan in het contextlogboek - bij Inter Club d'Escaldes - Universitatea Craiova geeft "
     "Fotmob geen bruikbare selectiewaarde, dus het aandeel ontbrekende spelers is daar niet te "
     "berekenen en ctxlog.py slaat die rij over. VIJF duels komen op relocated = True, het "
     "hoogste aantal tot nu toe en het normale patroon voor een Europese avond (Ararat Armenia, "
     "Union St.Gilloise in Dusseldorf, Inter Club d'Escaldes, Pafos FC en AGF). Daarnaast de "
     "binnenlandse standen voor de kruis-grensomrekening van alle 36 duels "
     "(scripts/interleague.py), het voorbeschouwingsblok van de twee gepubliceerde duels "
     "(preview.match_block) en de marktvormtelling van 23 duels (marketform.match_block) - nul "
     "fouten. GEEN GAT deze run.")

note("the_odds_api", "ok",
     "22 okt (run A): api_check.py OK, 49 actieve voetbalcompetities, quota 19038 over / 962 "
     "gebruikt deze maand. 25 credits uitgegeven: 2 bulk-aanroepen (h2h+spreads+totals, 3 "
     "credits per competitie) en 19 BTTS-aanroepen a 1 credit. Een dag met 36 duels kost dus "
     "nog altijd weinig, want spreads/totals/h2h rekenen per COMPETITIE af (§0) en er zijn er "
     "maar twee; de BTTS-inkoop is het enige dat per duel telt. Beide spelende competities "
     "hebben een sportkey, dus er is deze run geen enkel duel waar BetExplorer de enige "
     "1X2-bron is.")

note("oddsapi", "ok",
     "22 okt (run A): fetch_bulk gaf voor beide sportkeys 18 events met h2h, spreads en totals; "
     "fetch_event_markets gaf btts voor 19 van de 20 duels met een kandidaat-edge. Het "
     "twintigste, FK Crvena Zvezda - FC Kobenhavn, stond NIET in de spreads-respons en kon dus "
     "niet op event-id worden opgevraagd - dat is geen storing maar een ontbrekend event bij de "
     "aanbieder, en het duel is wel op de overige markten doorgerekend. store['errors'] is "
     "LEEG. net_price is werkelijk gebruikt: de gepubliceerde Braga-regel staat op de beurs "
     "Matchbook (2.24 bruto, 2.2152 na 2% commissie, §0), en bij de drie selecties die op "
     "lijstlengte afvielen staan er twee eveneens op een beurs.")

note("betexplorer", "ok",
     "22 okt (run A): UEFA Europa League 18 fixtures met 1X2-gemiddelde (18 in het "
     "inzetvenster), UEFA Conference League 18 (18 in het venster). Tweede bron op de vraag "
     "welke wedstrijden er zijn: 16 van 16 competities eens met de Fotmob-daglijst, 36 duels "
     "tegen 36 (ra_oct22_bevestiging.py). En de enige bron voor de vijf bekers zonder "
     "fotmob_id: alle vijf nul teamparen in het inzetvenster, met als eerstvolgende ronde "
     "League Cup 27 okt, KNVB Beker 27 okt, DFB Pokal 27 okt, FA Cup 7 nov en Coppa Italia "
     "1 dec. Geen Cloudflare-challenge, geen 403.")

note("understat", "untested",
     "22 okt (run A): NIET aangeroepen. Understat dekt vijf binnenlandse competities (Premier "
     "League, La Liga, Bundesliga, Serie A, Ligue 1) en geen van die vijf speelt vandaag - de "
     "hele runlijst bestaat uit twee Europese toernooien. Dat is geen storing: er was niets op "
     "te halen. Gevolg voor §2 wel noemen: de kansinput komt vandaag voor alle 23 doorgerekende "
     "duels van EEN bron (Fotmob) in twee doorsnedes, dus minder redundantie dan op een "
     "binnenlandse speeldag. Laatste geslaagde aanroep: 21 okt 2026 (La Liga).")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Fotmob leverde deze run zonder fout, "
     "dus §2 is gedekt en er is niets te doen. Wordt pas een echt probleem zodra Fotmob omvalt.")

H["last_run"] = {"run": "A", "date": "2026-10-22",
                 "note": "36 duels in het inzetvenster (18 Europa League + 18 Conference "
                         "League), alle 36 kruis-grens, 23 doorgerekend, 2 bets van de 5 "
                         "gekwalificeerde selecties (MAX_LIGHT_IN_SHORTLIST bindt), nul "
                         "bronstoringen, 25 van 950 credits."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

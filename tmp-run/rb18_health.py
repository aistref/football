"""Run B, 18 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-18"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 18 sep 2026 — vrijdagavond, en de drukste Run B-dag sinds weken: 9 van de 17 "
    "competities uit de runlijst hadden wedstrijden, samen 18 duels, waaronder een volledige "
    "KKD-ronde van 8. Leeg: Czech First League, Greek Super League, Allsvenskan, Serie B, Swiss "
    "Super League, English League One, English League Two en de Kosovo Superleague (die laatste "
    "komt nog altijd niet op de Fotmob-daglijst voor, ongewijzigd sinds 13 aug 2026). Cap 55 "
    "(vr-zo) tegen 18 duels, 0 afgekapt. 15 van de 18 door de datadekkingspoort: 4 FULL en 11 "
    "LIGHT; 3 op NONE (Rudeš – Slaven, Puskás – Kispest Honvéd, UTA Arad – Sepsi OSK) omdat "
    "promotion.TIER2 geen divisiepaar kent voor Kroatië, Hongarije en Roemenië — geen datagat "
    "maar een ontbrekende meting, zie het runrapport. 98 selecties over alle zes de markten, "
    "0 bets: hoogste herijkte edge +17.86 pp (Almere City, tegengehouden door poort 8), hoogste "
    "die geen poort raakte +7.54 pp (AH WSG Tirol +1.5, drempel 8.0). Vier schaduwrijen: 1 "
    "underdog, 1 underdog_ruw en 2 zonder_herijking. 4 van de 9 spelende competities hebben een "
    "sportkey en kregen de volle bulk; 15 van 733 credits, waarvan 3 aan BTTS voor drie van de "
    "vier duels met een kandidaat-edge.")}

TOEVOEGING = {
 "fotmob": (" Run B 18 sep 2026: daglijst gaf 9 Run B-competities met wedstrijden (Eliteserien 1, "
   "Croatian HNL 1, Hungarian NB I 1, Romanian SuperLiga 2, Segunda División 1, 2. Bundesliga 2, "
   "Austrian Bundesliga 1, Keuken Kampioen Divisie 8, Kategoria Superiore 1). xG-dekking "
   "ongewijzigd ten opzichte van de eerdere metingen: Eliteserien (id 59), Segunda División "
   "(140), 2. Bundesliga (146) en Austrian Bundesliga (38) hebben xG in vorig én lopend seizoen; "
   "Croatian HNL (252), Hungarian NB I (212), Romanian SuperLiga (189), Keuken Kampioen Divisie "
   "(111) en Kategoria Superiore (260) hebben het in geen van beide — daar komen zowel het "
   "competitieniveau als de teamsterktes uit doelpunten. Context opgehaald voor 12 van de 18 "
   "duels zonder fout; de zes zonder contextblok zijn de duels waarvoor Fotmob geen "
   "opstellings-/vormblok gaf. check_venue meldde nergens een verplaatsing."),
 "betexplorer": (" Run B 18 sep 2026: negen slugs opgehaald, acht raak — Eliteserien 8 rijen, "
   "Croatian HNL 5, Hungarian NB I 6, Romanian SuperLiga 10, Segunda División 11, 2. Bundesliga "
   "18, Austrian Bundesliga 12, Keuken Kampioen Divisie 10 (alle acht duels van vandaag erin, "
   "marktgemiddelde over 19 boeken). LET OP: albania/abissnet-superiore gaf 0 rijen terug — geen "
   "HTTP-fout, gewoon een lege tabel — waardoor Vllaznia – Teuta Durrës deze run helemaal zonder "
   "prijzen bleef. De slug is nog steeds die uit KNOWN_LEAGUE_URLS; of de pagina verhuisd is of "
   "of de competitie er tijdelijk niet op staat, is met één waarneming niet te zeggen."),
 "the_odds_api": (" Run B 18 sep 2026: 19.081 credits over, 919 gebruikt deze maand "
   "(api_check.py, 44 actieve voetbalcompetities). Plafond suggest_cap(19081, 13) = 733, "
   "split_budget(733, 4) = 4 spreads / 4 totals. Alle vier de competities met een sportkey "
   "kregen de bulk-aanroep (h2h+spreads+totals, 3 credits): soccer_norway_eliteserien 8 events, "
   "soccer_spain_segunda_division 11, soccer_germany_bundesliga2 9, soccer_austria_bundesliga "
   "11. Daarna 3 credits aan BTTS voor Albacete – Córdoba, Greuther Fürth – Magdeburg en Rapid "
   "Wien – WSG Tirol. Totaal 15 van 733, 19.066 over. Dekking binnen de spreads-respons is "
   "wisselend: Eliteserien had wél een ±0.5-lijn (Double Chance) maar géén 0.0-lijn (Draw No "
   "Bet), Segunda División en 2. Bundesliga precies andersom, en Austrian Bundesliga geen van "
   "beide — bekeken met een reden, geen gat. De beste 1X2-prijs lag gemiddeld +5,50% boven het "
   "BetExplorer-marktgemiddelde (9,30% / 5,41% / 5,12% / 3,88% / 3,81%), in lijn met de +7,78% "
   "van de meting op 5 sep; bij Rapid Wien – WSG Tirol stonden alle drie de uitkomsten bij een "
   "beurs en zijn ze door net_price gehaald."),
 "api_football": (" 18 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolg deze run: geen enkel duel is hierdoor op NONE uitgekomen; de drie "
   "NONE-duels zijn een ontbrekend divisiepaar in promotion.TIER2 en geen ontbrekende sleutel."),
 "understat": (" 18 sep 2026 (Run B): niet aangeroepen — Understat dekt alleen de vijf grote "
   "competities en geen daarvan staat op de runlijst van Run B."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"
S["understat"]["status"] = S["understat"].get("status", "ok")   # niet aangeroepen deze run

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")

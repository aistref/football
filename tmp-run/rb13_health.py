"""Run B, 13 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-13"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 13 sep 2026 — 13 van de 17 competities hadden wedstrijden, samen 39 duels. Cap 55 "
    "(zondag), 0 afgekapt: MAX_DEEP_ANALYSES heeft deze run geen enkele analyse gekost. 29 duels "
    "door de datadekkingspoort (14 FULL, 15 LIGHT), 325 selecties, 0 bets. Tien duels op NONE, in "
    "twee even grote groepen: vijf uit landen zonder gemeten divisiepaar (Griekenland, Kroatië, "
    "Roemenië, Oostenrijk, Albanië) en vijf ploegen die uit een DERDE divisie komen en daarom niet "
    "in de stand van de divisie erboven staan (Eldense, Sabadell, Tenerife, Energie Cottbus, VfL "
    "Osnabrück). Acht van de dertien competities hadden een sportkey en kregen de volle "
    "bulk-aanroep; vijf (Tsjechië, Kroatië, Roemenië, Keuken Kampioen Divisie, Albanië) hebben er "
    "geen en kwamen niet verder dan het BetExplorer-marktgemiddelde. 29 van 534 credits. Vier "
    "selecties in twee wedstrijden haalden alle acht poorten op de RUWE kans en sneuvelden alleen "
    "op de herijking.")}

TOEVOEGING = {
 "fotmob": (" Run B 13 sep 2026: daglijst gaf 13 Run B-competities met wedstrijden (39 duels). "
   "xG-dekking ongewijzigd ten opzichte van 12 sep: WEL xG bij Greek Super League (135), "
   "Eliteserien (59), Allsvenskan (67), Segunda División (140), Serie B (86), 2. Bundesliga (146), "
   "Swiss Super League (69) en Austrian Bundesliga (38); GEEN xG bij Czech First League (122), "
   "Croatian HNL (252), Romanian SuperLiga (189), Keuken Kampioen Divisie (111) en Kategoria "
   "Superiore (260) — die vijf rekenen op doelpunten voor/tegen en blijven LIGHT. English League "
   "One en League Two speelden vandaag niet en zijn dus niet opnieuw nagetrokken. Context "
   "opgehaald voor alle 39 duels zonder één fout; opstellingstype 27x lastStarting11, 5x "
   "predicted, 4x unavailable en 3x leeg. check_venue meldde één VERPLAATSING: Kalamata – NFC "
   "Volos werd niet in Dimotiko Stadio Kalamatas gespeeld maar in Dimotiko Stadio Peristeriou in "
   "Athene — dat duel viel hoe dan ook op NONE, maar de melding hoort genoteerd (§1c). Het "
   "`totalStarterMarketValue = 0`-gat van 12 sep is er nog: 9 van de 39 duels, waardoor "
   "ctxlog 30 van 39 kon vastleggen."),
 "betexplorer": (" Run B 13 sep 2026: dertien slugs opgehaald, alle dertien raak, inclusief "
   "Albanië (abissnet-superiore, 2 rijen). Voor de vijf competities zonder sportkey (Tsjechië, "
   "Kroatië, Roemenië, Keuken Kampioen Divisie, Albanië) was dit opnieuw de ENIGE 1X2-bron; daar "
   "is de bookmaker niet herleidbaar en valt de edge systematisch te laag uit."),
 "the_odds_api": (" Run B 13 sep 2026: 19.261 credits over, 739 gebruikt deze maand "
   "(api_check.py, 48 actieve voetbalcompetities). Plafond suggest_cap(19261, 18) = 534; "
   "uitgegeven 29 in 13 aanroepen (8 bulk-aanroepen h2h+spreads+totals à 3 credits, plus 5 "
   "BTTS-aanroepen à 1 credit in de tweede ronde van §1a stap 2). soccer_greece_super_league, "
   "soccer_norway_eliteserien, soccer_sweden_allsvenskan, soccer_spain_segunda_division, "
   "soccer_italy_serie_b, soccer_germany_bundesliga2, soccer_switzerland_superleague en "
   "soccer_austria_bundesliga leverden alle acht events; Tsjechië, Kroatië, Roemenië, de Keuken "
   "Kampioen Divisie en Albanië komen niet voor in de /v4/sports-lijst. Beste prijs lag over de "
   "21 duels waar hij bekend is gemiddeld +7.74% boven het BetExplorer-marktgemiddelde (mediaan "
   "+6.03%, hoogste +16.19%) — in lijn met de +7.78% / +6.07% van de meting op 5 sep."),
 "api_football": (" 13 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: de vijf competities zonder Fotmob-xG (Tsjechië, Kroatië, "
   "Roemenië, Keuken Kampioen Divisie, Albanië) hadden met een werkende statistiekenbron mogelijk "
   "FULL kunnen zijn in plaats van LIGHT; dat raakt acht van de 29 doorgerekende duels."),
 "understat": (" Run B 13 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
   "Bundesliga, Serie A en Ligue 1, en geen daarvan staat op de Run B-runlijst. Normale uitkomst "
   "voor Run B, geen storing."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"
S["understat"]["last_checked"] = "2026-09-12"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")

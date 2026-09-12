"""Run B, 12 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-12"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 12 sep 2026 — de grootste Run B-dag tot nu toe: 15 van de 17 competities hadden "
    "wedstrijden, samen 59 duels. Cap 55 (zaterdag), 4 afgekapt (waarvan 1 hoe dan ook op NONE "
    "zou zijn uitgekomen). 45 duels door de datadekkingspoort (28 FULL, 17 LIGHT), 641 selecties, "
    "0 bets. Elf duels op NONE: vier buiten conversion_in_range, zeven zonder gemeten divisiepaar "
    "(Griekenland en Roemenië kennen er geen; Ascoli, LR Vicenza, Rochdale en York City komen uit "
    "een derde divisie). Tien van de vijftien competities hadden een sportkey en kregen de volle "
    "bulk-aanroep; vijf (Tsjechië, Kroatië, Roemenië, Keuken Kampioen Divisie, Albanië) hebben er "
    "geen en kwamen niet verder dan het BetExplorer-marktgemiddelde. 76 van 509 credits. "
    "Negentien selecties in acht wedstrijden haalden alle acht poorten op de RUWE kans en "
    "sneuvelden alleen op de herijking — de grootste zo'n groep tot nu toe.")}

TOEVOEGING = {
 "fotmob": (" Run B 12 sep 2026: daglijst gaf 15 Run B-competities met wedstrijden (59 duels), "
   "de ruimste Run B-kalender tot nu toe. xG-dekking opnieuw per competitie nagetrokken: WEL xG "
   "bij Greek Super League (135), Eliteserien (59), Allsvenskan (67), Segunda División (140), "
   "Serie B (86), 2. Bundesliga (146), Swiss Super League (69), Austrian Bundesliga (38), English "
   "League One (108) en English League Two (109), in beide seizoenen; GEEN xG bij Czech First "
   "League (122), Croatian HNL (252), Romanian SuperLiga (189), Keuken Kampioen Divisie (111) en "
   "Kategoria Superiore (260) — die vijf rekenen op doelpunten voor/tegen en blijven LIGHT. "
   "Standen van het lopende seizoen gevuld voor alle vijftien (3 tot 21 speeldagen). Context "
   "opgehaald voor alle 59 duels zonder één fout; opstellingstype 53x lastStarting11, 2x "
   "predicted, 2x unavailable en 2x leeg. Geen enkele verplaatsing gemeld door check_venue. "
   "NIEUW GEMETEN EN VAN BELANG VOOR HET CONTEXTLOGBOEK: Fotmob geeft voor een deel van de "
   "kleinere clubs `totalStarterMarketValue` = 0. Dat raakte 13 van de 59 duels (o.a. zes in "
   "League Two, beide Oostenrijkse duels en beide Albanese), en omdat ctxlog.out_share dan geen "
   "aandeel kan uitrekenen vielen die 13 buiten het contextlogboek: 46 van 59 vastgelegd. Poort 7 "
   "zelf staat daar gewoon open (ontbrekende data laat de poort open, §1c) — het is een gat in de "
   "METING, niet in de analyse."),
 "betexplorer": (" Run B 12 sep 2026: vijftien slugs opgehaald, alle vijftien raak — voor het "
   "eerst inclusief Albanië (abissnet-superiore, 4 rijen), dat op 11 sep nog als 'geen slug' in "
   "de tabel stond. Die aanname was dus fout en is hierbij gecorrigeerd. Voor de vijf competities "
   "zonder sportkey (Tsjechië, Kroatië, Roemenië, Keuken Kampioen Divisie, Albanië) was dit de "
   "ENIGE 1X2-bron; daar is de bookmaker niet herleidbaar en valt de edge systematisch te laag "
   "uit."),
 "the_odds_api": (" Run B 12 sep 2026: 19.386 credits over, 614 gebruikt deze maand "
   "(api_check.py, 48 actieve voetbalcompetities). Plafond suggest_cap(19386, 19) = 509; "
   "uitgegeven 76 in 56 aanroepen (10 bulk-aanroepen h2h+spreads+totals à 3 credits, plus 46 "
   "BTTS-aanroepen à 1 credit). soccer_greece_super_league, soccer_norway_eliteserien, "
   "soccer_sweden_allsvenskan, soccer_spain_segunda_division, soccer_italy_serie_b, "
   "soccer_germany_bundesliga2, soccer_switzerland_superleague, soccer_austria_bundesliga, "
   "soccer_england_league1 en soccer_england_league2 leverden alle tien events; Tsjechië, "
   "Kroatië, Roemenië, de Keuken Kampioen Divisie en Albanië komen niet voor in de "
   "/v4/sports-lijst. Beste prijs lag over de 39 duels waar hij bekend is gemiddeld +7.05% boven "
   "het BetExplorer-marktgemiddelde (mediaan +5.71%). Let op de uitschieter: Olympiacos – OFI "
   "Crete op +38.64%, en dat is een staarteffect en geen structurele winst — Betfair noteerde de "
   "uitzege op 17.5 tegen een marktgemiddelde van 10.67, een longshot waar de spreiding tussen "
   "boeken het grootst is. De mediaan is hier het eerlijke getal."),
 "api_football": (" 12 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: de vijf competities zonder Fotmob-xG (Tsjechië, Kroatië, "
   "Roemenië, Keuken Kampioen Divisie, Albanië) hadden met een werkende statistiekenbron mogelijk "
   "FULL kunnen zijn in plaats van LIGHT; dat raakt zes van de 45 doorgerekende duels."),
 "understat": (" Run B 12 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
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
# Understat is deze run niet geprobeerd; status blijft staan op wat er laatst gemeten is.
S["understat"]["last_checked"] = "2026-09-12"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")

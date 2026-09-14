"""Run B, 14 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-14"

d["last_run"] = {"run": "B", "date": DAY, "note": (
    "Run B 14 sep 2026 — maandag, en dat is te zien: 6 van de 17 competities hadden wedstrijden, "
    "samen 9 duels. Cap 40 (ma-do), 0 afgekapt. 8 duels door de datadekkingspoort (3 FULL, "
    "5 LIGHT), 61 selecties, 0 bets. Eén duel op NONE: Celta Fortuna - Eibar, omdat Celta Fortuna "
    "uit de Primera Federacion komt en promotion voor LaLiga2 geen divisie eronder kent. Drie van "
    "de zes competities hadden een sportkey (Eliteserien, Allsvenskan, Segunda Division) en kregen "
    "de volle bulk-aanroep; drie (Croatian HNL, Romanian SuperLiga, Keuken Kampioen Divisie) "
    "hebben er geen en kwamen niet verder dan het BetExplorer-marktgemiddelde. 10 van 564 credits. "
    "Geen enkele selectie haalde alle acht poorten op de ruwe kans, dus ook geen schaduwrij op "
    "de herijking.")}

TOEVOEGING = {
 "fotmob": (" Run B 14 sep 2026: daglijst gaf 6 Run B-competities met wedstrijden (9 duels). "
   "WEL xG bij Eliteserien (59), Allsvenskan (67) en Segunda Division (140); GEEN xG bij Croatian "
   "HNL (252), Romanian SuperLiga (189) en Keuken Kampioen Divisie (111) — die drie rekenen op "
   "doelpunten voor/tegen en blijven LIGHT, ongewijzigd sinds 12 sep. De overige elf competities "
   "speelden vandaag niet en zijn dus niet opnieuw nagetrokken. Context opgehaald voor alle negen "
   "duels zonder één fout; opstellingstype 7x lastStarting11, 1x predicted, 1x unavailable. "
   "check_venue meldde geen enkele verplaatsing. Het `totalStarterMarketValue = 0`-gat is er nog "
   "en raakt vandaag vijf van de achttien ploegzijden (Kroatie, Roemenie en de Keuken Kampioen "
   "Divisie), waardoor ctxlog 5 van de 9 duels kon vastleggen."),
 "betexplorer": (" Run B 14 sep 2026: zes slugs opgehaald, alle zes raak. Voor de drie "
   "competities zonder sportkey (Croatian HNL, Romanian SuperLiga, Keuken Kampioen Divisie) was "
   "dit opnieuw de ENIGE 1X2-bron; daar is de bookmaker niet herleidbaar en valt de edge "
   "systematisch te laag uit."),
 "the_odds_api": (" Run B 14 sep 2026: 19.207 credits over, 793 gebruikt deze maand "
   "(api_check.py, 48 actieve voetbalcompetities). Plafond suggest_cap(19207, 17) = 564; "
   "uitgegeven 10 in 4 aanroepen (3 bulk-aanroepen h2h+spreads+totals à 3 credits, plus 1 "
   "BTTS-aanroep à 1 credit in de tweede ronde van §1a stap 2). soccer_norway_eliteserien, "
   "soccer_sweden_allsvenskan en soccer_spain_segunda_division leverden alle drie events; "
   "Croatian HNL, Romanian SuperLiga en de Keuken Kampioen Divisie komen niet voor in de "
   "/v4/sports-lijst. De spreads-respons bevatte deze run bij geen enkele competitie een "
   "0.0-lijn, dus Draw No Bet was nergens af te leiden; Double Chance (de ±0.5-lijn) lag er "
   "alleen bij de Allsvenskan. Beste prijs lag over de drie duels waar hij bekend is gemiddeld "
   "+17.4% boven het BetExplorer-marktgemiddelde (20.75%, 19.56% en 11.99%) — fors ruimer dan de "
   "+7.78% van de meting op 5 sep, wat past bij twee kleine Scandinavische competities waar de "
   "boeken verder uiteenlopen dan in de Premier League."),
 "api_football": (" 14 sep 2026 (Run B): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: de drie competities zonder Fotmob-xG (Croatian HNL, Romanian "
   "SuperLiga, Keuken Kampioen Divisie) hadden met een werkende statistiekenbron mogelijk FULL "
   "kunnen zijn in plaats van LIGHT; dat raakt vijf van de acht doorgerekende duels."),
 "understat": (" Run B 14 sep 2026: niet aangeroepen. Understat dekt alleen PL, La Liga, "
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

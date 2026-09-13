"""Run A, 13 sep 2026 — Stage 3 vervolg: data/source-health.json bijwerken (§3, §6b-3)."""
import json

P = "data/source-health.json"
d = json.load(open(P))
S = d["sources"]
DAY = "2026-09-13"

d["last_run"] = {"run": "A", "date": DAY, "note": (
    "Run A 13 sep 2026 — 12 van de 21 competities hadden wedstrijden, samen 36 duels. Cap 55 "
    "(zondag), 0 afgekapt. Voor het eerst kwamen ALLE wedstrijden door de datadekkingspoort: 24 "
    "FULL, 12 LIGHT, nul op NONE, doordat alle twaalf binnenlandse omrekeningen (elf promovendi, "
    "een degradant) binnen het gemeten bereik vielen. 507 selecties over alle zes de markten, "
    "0 bets. Alle twaalf competities kregen de volle bulk-aanroep, dus marktbalans 12 op 12; BTTS "
    "in een tweede ronde voor de dertien duels met een kandidaat-edge. 49 van 535 credits. Hoogste "
    "herijkte edge +14.05 pp (Brest +1.5), tegengehouden door poort 8. Eén naamkoppelingsfout "
    "opgespoord en gerepareerd: de ligatuur æ werd door ra_names.norm weggegooid in plaats van "
    "uitgeschreven, waardoor Nordsjælland – AGF bij geen enkele prijsbron terug te vinden was.")}

TOEVOEGING = {
 "fotmob": (" Run A 13 sep 2026: daglijst gaf 12 Run A-competities met wedstrijden, 36 duels. "
   "Team-xG aanwezig voor alle twaalf basiscompetities, zowel voor 2025/2026 als voor het lopende "
   "seizoen (3 tot 8 speeldagen), dus blend_seasons en de vroeg-seizoenscorrectie konden overal "
   "draaien; de pooling stond op 66 speeldagen over twaalf competities, ruimer dan de 56 van "
   "gisteren. Voor de twaalf omrekeningen leverde Fotmob de stand van de divisie eronder "
   "(Championship, Serie B, LaLiga2, 2. Bundesliga, Ligue 2, First Division B, 1. Lig, "
   "1. Division, I Liga) en die erboven (Premier League) zonder uitval, en alle twaalf vielen "
   "binnen het gemeten bereik — nul afwijzingen, dus nul duels op NONE. Context opgehaald voor "
   "alle 36 duels, 35 daarvan bruikbaar voor ctxlog.py; het contextlogboek staat daarmee op 502, "
   "waarvan 462 afgewikkeld. Opstellingstype: 25 predicted, 11 lastStarting11 — geen enkele "
   "bevestigde opstelling om 04:1x, wat voor middag- en avondwedstrijden normaal is. Poort 7 stond "
   "op 27 van de 36 duels aan minstens één kant dicht, maar hield uiteindelijk maar 6 selecties "
   "tegen: de rest sneuvelde al eerder op de edge."),
 "betexplorer": (" Run A 13 sep 2026: fixtures-rijen voor alle twaalf competities met wedstrijden, "
   "samen 154 rijen waarvan 36 van vandaag. Dekking 36 van 36 — maar pas ná de reparatie van de "
   "æ-ligatuur in ra_names.norm: Nordsjaelland – Aarhus was eerst niet te koppelen aan "
   "Nordsjælland – AGF (nordsjlland tegen nordsjaelland, plus een initiaalwoord tegen een "
   "plaatsnaam), en dat duel kwam daardoor eerst zonder 1X2-marktgemiddelde en zonder "
   "kalibratieblok te staan. Het aantal boeken per rij loopt opnieuw sterk uiteen: 19 in de "
   "Premier League en Serie A, 18 in Denemarken, maar 4 in Ligue 1 en 3 in de Eredivisie. Dat "
   "raakt alleen het consensusgemiddelde van §6e en poort 8, niet de prijs waarop gespeeld wordt."),
 "the_odds_api": (" Run A 13 sep 2026: 19.310 credits over, 690 gebruikt deze maand "
   "(api_check.py), 48 actieve voetbalcompetities. Alle twaalf sportkeys werkten met de "
   "bulk-aanroep (h2h+spreads+totals), samen 154 events, 36 credits. BTTS is voor de eerste keer "
   "in een TWEEDE ronde gekocht, ná de analyse, voor de dertien duels met een kandidaat-edge: "
   "13 credits (opnieuw 1 in plaats van de 2 die §1a aanhoudt — voor de zevende run op rij). "
   "Samen 49 van 535. Beste prijs lag over de 36 duels gemiddeld +7.73% boven het "
   "BetExplorer-marktgemiddelde (mediaan +5.94%, bereik +3.70% tot +24.19%); in 49 van de 102 "
   "gevallen stond die beste prijs bij een beurs (Betfair, Matchbook) en is er met net_price "
   "gerekend. De uitschieter van +24.19% is Nordsjælland – AGF, waar de Deense boeken ver "
   "uiteenlopen over de uitzege."),
 "api_football": (" 13 sep 2026 (Run A): API_FOOTBALL_KEY nog steeds niet gezet in de omgeving "
   "van de geplande taak. Ontbrekend, niet afgewezen — api_check.py slaat de bron over zonder "
   "HTTP-verzoek. Gevolgen deze run: geen, Fotmob leverde de kansinput voor alle 36 duels."),
 "understat": (" Run A 13 sep 2026: aangeroepen voor de vijf gedekte competities die vandaag "
   "speelden (Premier League, Serie A, La Liga, Bundesliga, Ligue 1), alle vijf zonder fout, 18 "
   "tot 20 ploegen per competitie. Als tweede onafhankelijk xG-model meegenomen bij zes duels "
   "(Manchester United – Manchester City, Napoli – Bologna, Sassuolo – Juventus, Levante – "
   "Barcelona, Real Sociedad – Atlético Madrid en Brest – Paris Saint-Germain); bij de overige "
   "duels in die competities staat minstens één ploeg niet in de Understat-reeks van vorig "
   "seizoen, meestal een promovendus."),
}

for k, extra in TOEVOEGING.items():
    S[k]["detail"] = (S[k].get("detail") or "").rstrip() + extra
    S[k]["last_checked"] = DAY

S["fotmob"]["status"] = "ok"
S["betexplorer"]["status"] = "ok"
S["the_odds_api"]["status"] = "ok"
S["understat"]["status"] = "ok"
S["api_football"]["status"] = "key_missing"

d["updated"] = DAY
json.dump(d, open(P, "w"), ensure_ascii=False, indent=1)
print("source-health.json bijgewerkt")

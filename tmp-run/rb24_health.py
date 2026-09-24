import json
from pathlib import Path

P = Path("data/source-health.json")
d = json.loads(P.read_text())

NOTE = (
 "Run B 2026-09-24 — donderdag, interlandperiode. Eén wedstrijd uit de runlijst van zeventien, en "
 "die was al gespeeld toen de run draaide. Methode 1: de Fotmob-daglijst van 24 sep (29 competities, "
 "48 duels) plus die van 25 sep, per primaryId getoetst voor alle zeventien competities — één "
 "treffer: MLS (130), Seattle Sounders FC – Real Salt Lake, aftrap 01:40Z = 03:40 NL. Methode 2: "
 "zeventien BetExplorer-fixturepagina's, los opgehaald — dezelfde ene rij ('Today 02:30' UK-tijd, "
 "1X2 over 4 boeken: 1.76 / 3.90 / 4.13) en nul andere duels op vandaag. Croatian HNL en Hungarian "
 "NB I gaven ook na de ingebouwde herhaalpoging 0 rijen; dat is de wisselende respons die op 23 sep "
 "is vastgelegd en geen bewijs van 'geen wedstrijden' — Fotmob bevestigt daar de lege dag, en beide "
 "competities liggen tot 10 okt stil. De eerstvolgende duels van de runlijst zijn Girona – Albacete "
 "(Segunda, 25 sep 20:30 NL) en FC Dordrecht – Almere City (KKD, 25 sep 21:00 NL); de rest hervat "
 "9–10 okt en English League One/Two op 26 sep. "
 "NIEUWE MEETING, en de belangrijkste van deze run: The Odds API geeft voor een wedstrijd die al "
 "onderweg is **live** prijzen, geen pre-match prijzen en geen fout. Één bulk-aanroep op "
 "soccer_usa_mls (h2h+spreads+totals, eu, 3 credits) om 05:30 CEST, met het duel op 89' en 2-0: "
 "h2h Seattle 1.01 (Winamax), gelijkspel 61.0 (888sport), Real Salt Lake 1000.0 (Betfair); spreads "
 "Seattle 0.0 @1.77 en -2.0 @1.70 (Pinnacle/Coolbet); totals Over 2.5 @3.40, Under 2.5 @2.07. Het "
 "event stond gewoon in /events/ met commence_time 01:40Z. Wie die respons zonder tijdcontrole "
 "doorrekent, meet edge tegen een markt die de tussenstand al kent. BetExplorer hield voor "
 "hetzelfde duel juist wél de pre-match slotkoers vast in de fixturetabel, en dat is de prijs die "
 "in het kalibratielogboek is gebruikt. "
 "The Odds API staat na deze run op 18.754 van 20.000 over (1.246 gebruikt deze maand); "
 "API_FOOTBALL_KEY blijft niet gezet — api_check.py meldt 'niet beschikbaar', onveranderd. "
 "1 wedstrijd doorgerekend (FULL), 0 bets, cap 40 bond nergens, 3 credits uitgegeven."
)

d["last_run"].append({"run": "B", "date": "2026-09-24", "note": NOTE})
d["last_run"] = d["last_run"][-6:]
d["updated"] = "2026-09-24"

ADD = {
 "the_odds_api": (
   " Run B 24 sep 2026: 18.754 van 20.000 over (1.246 gebruikt deze maand); één bulk-aanroep "
   "h2h+spreads+totals op soccer_usa_mls (3 credits), geen fouten. GEMETEN EN VASTGELEGD: voor een "
   "wedstrijd die al is afgetrapt levert deze bron LIVE prijzen in dezelfde velden als pre-match "
   "prijzen — geen fout, geen vlag, en het event staat gewoon in /events/ met zijn oorspronkelijke "
   "commence_time. Bij Seattle Sounders – Real Salt Lake op 89' en 2-0 gaf h2h 1.01 / 61.0 / 1000.0 "
   "en totals Over 2.5 @3.40 bij een stand van 2-0. Toets dus altijd commence_time tegen de klok "
   "vóór je een respons als marktoordeel gebruikt; een koers van 1000.0 valt op, maar een "
   "handicaplijn van 1.70 in de 20e minuut niet."),
 "betexplorer": (
   " Run B 24 sep 2026: zeventien fixturepagina's, alle slugs raak. Croatian HNL en Hungarian NB I "
   "gaven opnieuw 0 rijen ná de herhaalpoging (de wisselende respons van 23 sep is dus niet "
   "verholpen door die herhaling alleen); de overige vijftien gaven 4 tot 33 rijen. Nuttig detail "
   "dat hier nog niet stond: de fixturetabel houdt de PRE-MATCH slotkoers vast van een duel dat al "
   "is afgetrapt (label 'Today 02:30', 1X2 over 4 boeken) terwijl The Odds API op datzelfde moment "
   "live prijzen geeft. Voor het kalibratielogboek is deze bron daarmee de betrouwbaardere van de "
   "twee zodra een run ná de aftrap draait."),
 "fotmob": (
   " Run B 24 sep 2026: daglijst 24 en 25 sep opgehaald, MLS-teamstatistieken voor 2025 en 2026 "
   "(beide met xG, 30 ploegen), wedstrijddetails en context voor één duel. Eén onvolkomenheid "
   "gemeten: `lineupType` is voor een lopende wedstrijd `\"standard\"`, en "
   "`ranking._lineup_points` kent alleen `\"lineup\"` (2 punten) en `\"predicted\"` (1) — een "
   "bevestigde opstelling krijgt daardoor 0 punten, net als géén opstelling. Raakt alleen de "
   "tie-break van de datarijkdom-score, niet een kansschatting."),
}
for k, extra in ADD.items():
    s = d["sources"][k]
    s["detail"] = (s.get("detail") or "") + extra
    s["last_checked"] = "2026-09-24"
    s["status"] = "ok"

d["sources"]["api_football"]["last_checked"] = "2026-09-24"
P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
print("bijgewerkt; last_run nu:", [(x["run"], x["date"]) for x in d["last_run"]])

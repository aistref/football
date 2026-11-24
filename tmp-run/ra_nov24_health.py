"""Run A, 24 nov 2026 — bronprobe voor source-health.json (§6b-3).

NEGENTIEN duels in het inzetvenster over DRIE competities, tegen een dinsdagcap van 40: niets
afgekapt. Champions League-speelronde 5 vult de dag; geen beker heeft een ronde.

GEEN ENKELE BRONSTORING AAN DE KANT VAN DEZE REPO. `store["errors"]` is over de hele run leeg
gebleven en de tweede-bronbevestiging van §1 is het over ALLE 22 competities eens: 19 tegen 19.
De enige bron die niet levert is Understat, en dat is zijn eigen onderhoudspagina — zesde
RUNDAG op rij voor Run A, en vandaag zonder gevolg omdat geen van zijn vijf competities speelt.
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
    print(f"{key:28} {status:12} {detail[:80]}")


note("fotmob", "ok",
     "24 nov (run A): daglijsten 24 en 25 nov opgehaald (47 competities/153 duels en 51/145), en "
     "voor de afwikkeling die van 22 en 23 nov. Standen van drie competities over twee seizoenen "
     "(2025/2026 en 2026/2027), alle drie met xG in beide. Wedstrijdcontext van ALLE NEGENTIEN "
     "duels opgehaald ZONDER EEN ENKELE FOUT, inclusief de twee die op tier NONE uitkwamen - dat "
     "is wat Stage 4 eist (context VOOR de afkapping, ook voor wat afvalt). Marktvormfrequenties "
     "via marketform.match_block op alle zeventien doorgerekende duels, 0 fouten. "
     "Voorbeschouwingsblokken via preview.match_block op de twee gepubliceerde duels, 0 fouten. "
     "ENIGE KANSBRON VAN DEZE RUN, want Understat ligt eruit: alle negentien duels halen hun "
     "kansinput hier, en dat is sinds 19 nov een enkel punt van falen in plaats van twee (Sec. 4). "
     "Kost geen credits.")

note("the_odds_api", "ok",
     "24 nov (run A): api_check.py meldt OK, 45 actieve voetbalcompetities, quota 19027 over en "
     "973 verbruikt deze maand, 33 van 34 sportkeys actief (alleen soccer_france_ligue_two niet, "
     "en Ligue 2 staat niet op de runlijst van Run A). Plafond suggest_cap(19027, 7) = 1357; alle "
     "DRIE de spelende competities kregen de VOLLEDIGE bulk-aanroep (h2h + spreads + totals, "
     "3 credits elk = 9). Tweede ronde BTTS voor de dertien duels met een kandidaat-edge: "
     "13 credits. TOTAAL 22 van 1357, 19005 over met zeven dagen tot de maandwissel. Nul fouten "
     "in store['errors']. Vier actieve sportkeys die de repo niet kent (soccer_brazil_serie_b, "
     "soccer_england_efl_trophy, soccer_germany_liga3, soccer_uefa_nations_league) - geen van "
     "vier staat op de runlijst van Run A.")

note("betexplorer", "ok",
     "24 nov (run A): fetch_league_fixtures voor alle 22 competities van de runlijst, inclusief "
     "de dertien zonder wedstrijd en de zes bekers. 22 VAN 22 EENS MET FOTMOB, 19 duels tegen 19, "
     "en ook per competitie gelijk: Champions League 9-9, Championship 8-8, Scottish Premiership "
     "2-2. Dat is de bevestiging door een tweede methode van Sec. 1, op de vraag WELKE "
     "wedstrijden er zijn. Levert daarnaast het gratis 1X2-marktgemiddelde voor het "
     "kalibratieblok van Sec. 6e en voor poort 8 (Sec. 1a: gemiddelde om te METEN, beste prijs om "
     "te SPELEN). Nul fouten. De Champions League-pagina gebruikt vandaag 'Today HH:MM' in CET en "
     "niet in UK-tijd, zoals ook op 4 nov is vastgesteld.")

note("understat", "http_503",
     "24 nov (run A): ZESDE RUNDAG OP RIJ ERUIT. getLeagueData geeft HTTP 200 met een "
     "onderhoudspagina (26.719 bytes, geen JSON) voor EPL, Serie_A en La_liga. Zelfde respons en "
     "zelfde bytegrootte als op 19 t/m 23 november, dus geen nieuwe storing maar een "
     "voortdurende - vermoedelijk een permanent gewijzigde route of een blokkadepagina. NIET "
     "OMZEILD (Sec. 3, 'Niet doen': geen headless browser, geen challenge-solver, geen proxy). "
     "VANDAAG ZONDER FEITELIJK GEVOLG, en dat hoort erbij te staan: geen van Understats vijf "
     "competities (Premier League, La Liga, Bundesliga, Serie A, Ligue 1) speelt vandaag, dus ook "
     "een werkende Understat had aan geen enkel duel van deze run iets toegevoegd. WEL: "
     "p_xg_understat blijft leeg in het kalibratieblok van Sec. 6e, dus de reeks die moet "
     "uitwijzen of het ene xG-model beter voorspelt dan het andere groeit voor de zesde rundag "
     "niet. GEEN gevolg voor my_prob, de tiers of de poorten. Dit is dus GEEN geval van de "
     "uitzondering in Sec. 3 punt 3 (die gaat over Fotmob) en hoort niet vooraan in de "
     "notificatie. Staat als openstaand punt in het dagrapport met owner = 'ik'.")

note("interleague_kruis_grens", "ok",
     "24 nov (run A): EERSTE VOLLE KRUIS-GRENSDAG VAN DEZE REEKS SINDS 4 NOVEMBER, en de module "
     "deed precies wat Sec. 4 (8 sep 2026) van hem vraagt. interleague.convert_team op het laatst "
     "AFGERONDE seizoen (2025/2026) voor alle 18 ploegen van de negen Champions League-duels. "
     "ZEVEN van de negen duels kwamen door de omrekening heen en staan daarmee op LIGHT - nooit "
     "FULL, dat is de regel en geen aantekening. TWEE OP NONE, en beide poorten die dat deden "
     "zijn met opzet hard: (1) Slovan Bratislava - Real Betis, want SVK heeft geen gemeten "
     "competitiefactor (minder dan 40 Europese duels in de meting, Sec. 4 punt 2); (2) Arsenal - "
     "Borussia Dortmund, want Arsenals omgerekende verdediging komt op 0,373 uit en dat valt "
     "ONDER de gemeten vloer van 0,388 (in_range, Sec. 4 punt 3 - dezelfde Coventry-val als bij "
     "promotion.conversion_in_range). Stil terugvallen op factor 1,0 is precies wat deze module "
     "wegneemt. WAT OPVALT EN IN HET RUNRAPPORT STAAT: alle drie de selecties die vandaag hun "
     "eigen lat haalden komen uit deze zeven duels, terwijl de lat daar op het DUBBELE staat "
     "(16,0 pp). Dat is het patroon waar Sec. 4 punt 4 voor waarschuwt.")

note("pinnacle_via_odds_api", "ok",
     "24 nov (run A): Pinnacle zat bij 17 duels in de 1X2-respons en bij 17 (duel, lijn)-paren in "
     "de doelpuntenrespons, met een gemiddelde marge van 3,80 procent tegen 6 tot 10 procent bij "
     "de rest. Gebruikt als TOETS naast de eigen kans (Sec. 3 Stage 5 stap 2), nooit in my_prob of "
     "prob_sources (Sec. 2). Gemiddelde absolute afstand tot het Pinnacle-1X2-oordeel 4,61 pp. OP "
     "DE DOELPUNTENKANT STAAT HET MODEL GEMIDDELD +4,19 pp BOVEN PINNACLE OP P(UNDER), 11 van 17 "
     "erboven, en dat verschil wordt vrijwel volledig door de zes doorgerekende Champions "
     "League-duels gedragen: Bodo/Glimt +12,52, Como +18,89, Feyenoord +12,90, Manchester City "
     "+18,01 en RB Leipzig +20,77 pp, tegen een band van -5,2 tot +2,7 pp over de tien "
     "binnenlandse duels. DE GROOTSTE AFWIJKING VAN DE DAG STAAT OP EEN GEPUBLICEERD DUEL: bij "
     "RB Leipzig - Lens geeft Pinnacle de thuiszege 69,5 procent en het model 44,6 - 24,9 pp "
     "verschil, de grootste die deze vergelijking in weken gaf. Bij Bodo/Glimt - LASK staat het "
     "16,6 pp de andere kant op (model 81,1 tegen Pinnacle 64,5).")

note("forebet", "http_403",
     "Niet opnieuw geprobeerd op 24 nov (run A): bekende Cloudflare-blokkade, status overgenomen "
     "conform Stage 3. Wordt bewust niet omzeild.")

note("pinnacle_articles", "http_404",
     "Niet opnieuw geprobeerd op 24 nov (run A): /betting-articles/soccer/ bestaat sinds 20 sep "
     "2026 niet meer. De PRIJS van Pinnacle komt via The Odds API binnen en vult stap 2 van "
     "Stage 5 wel; zie pinnacle_via_odds_api.")

note("matchbook_blog", "http_530",
     "Niet opnieuw geprobeerd op 24 nov (run A): server lag er op 20 sep uit, status overgenomen "
     "conform Stage 3. De KOERSEN van Matchbook komen wel binnen via The Odds API, inclusief de "
     "2 procent beurscommissie van oddsapi.net_price - vandaag is dat een van de twee "
     "GEPUBLICEERDE koersen: Bodo/Glimt - LASK staat op 3,15 bruto en 3,107 netto, en dat laatste "
     "getal staat in picks.jsonl.")

note("betfair_blog", "http_403",
     "Niet opnieuw geprobeerd op 24 nov (run A): Cloudflare, status overgenomen conform Stage 3. "
     "De KOERSEN van Betfair komen wel binnen via The Odds API, inclusief commissie.")

note("kwartlijn_halve_uitkomst", "ok",
     "24 nov (run A): DE BEVINDING VAN 20 NOVEMBER KWAM VANDAAG METEEN OPNIEUW VOORBIJ EN IS NU "
     "GOED GEBOEKT. De pick van 23 nov op Wieczysta Krakow - Motor Lublin stond op OVER 3,25 en "
     "het werd 2-1, oftewel exact drie doelpunten. Een kwartlijn valt uiteen in twee halve bets "
     "(3,0 en 3,5): de eerste helft is een PUSH, de tweede verliest, dus de netto uitkomst is "
     "-0,50u en niet -1,00u. Geboekt met ledger.py settle --units -0.5. Zonder die correctie zou "
     "het dagresultaat van Stage 0 -4,00u zijn in plaats van -3,50u. Dit is de tweede keer in "
     "vijf dagen dat deze situatie zich voordoet (18 nov Cruzeiro - Palmeiras, 20 nov Vitoria - "
     "RB Bragantino, vandaag Wieczysta). OPENSTAAND PUNT ONGEWIJZIGD: er is nog geen script dat "
     "de boeking van kwartlijnen nacontroleert, en of een afwikkeling achteraf mag worden "
     "bijgesteld is een vraag voor de gebruiker (zie het runrapport van 20 nov).")

H["last_run"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")

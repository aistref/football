"""Run A, 23 nov 2026 — bronprobe voor source-health.json (§6b-3).

ZES duels in het inzetvenster over ZES competities, tegen een maandagcap van 40: niets afgekapt.
Geen beker heeft een ronde en geen Europees toernooi speelt.

GEEN ENKELE BRONSTORING AAN DE KANT VAN DEZE REPO. `store["errors"]` is over de hele run leeg
gebleven en de tweede-bronbevestiging van §1 is het over ALLE 22 competities eens: 6 tegen 6.
De enige bron die niet levert is Understat, en dat is zijn eigen onderhoudspagina — vijfde
RUNDAG op rij voor Run A.
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
    print(f"{key:22} {status:12} {detail[:90]}")


note("fotmob", "ok",
     "23 nov (run A): daglijsten 23 en 24 nov opgehaald, en voor de afwikkeling die van 22 en "
     "23 nov. Standen van zes competities over twee seizoenen (2025/2026 en 2026/2027), alle zes "
     "met xG in beide seizoenen. Wedstrijdcontext van ALLE ZES duels opgehaald ZONDER EEN ENKELE "
     "FOUT, inclusief de twee duels zonder opstellingsblok (Basaksehir - Corum FK en Wieczysta "
     "Krakow - Motor Lublin, beide datarijkdom 4,5). Marktvormfrequenties via "
     "marketform.season_results op alle zes duels, 0 fouten. Voorbeschouwingsblokken via "
     "preview.match_block op de twee gepubliceerde duels, 0 fouten. Promovendi-omrekening via de "
     "divisie eronder voor Monza, Corum FK en Wieczysta Krakow - alle drie binnen het gemeten "
     "bereik, dus LIGHT en geen NONE. Kost geen credits. ENIGE KANSBRON VAN DEZE RUN, want "
     "Understat ligt eruit: alle zes duels halen hun kansinput hier, en dat is sinds 19 nov een "
     "enkel punt van falen in plaats van twee (Sec. 4).")

note("the_odds_api", "ok",
     "23 nov (run A): api_check.py meldt OK, 46 actieve voetbalcompetities, quota 19072 over en "
     "928 verbruikt deze maand, 33 van 34 sportkeys actief (alleen soccer_italy_coppa_italia "
     "niet, en die competitie staat vandaag buiten de runlijst). Plafond suggest_cap(19072, 8) = "
     "1190; split_budget(1190, 6) = (6, 6), dus ALLE ZES spelende competities kregen de VOLLEDIGE "
     "bulk-aanroep (h2h + spreads + totals, 3 credits elk = 18). Tweede ronde BTTS voor alle zes "
     "duels, die alle zes een kandidaat-edge toonden: 6 credits. TOTAAL 24 van 1190, 19048 over. "
     "Nul fouten in store['errors']. Pinnacle zat bij alle zes duels in de respons, zowel op 1X2 "
     "als op de totalen, met een marge van 2,7 tot 4,1 procent.")

note("betexplorer", "ok",
     "23 nov (run A): fetch_league_fixtures voor alle zes spelende competities, 7 tot 22 rijen "
     "per competitie en overal precies een duel vandaag. Levert het gratis 1X2-marktgemiddelde "
     "voor het kalibratieblok van Sec. 6e en voor poort 8 (Sec. 1a: gemiddelde om te METEN, beste "
     "prijs om te SPELEN). Daarnaast de tweede bron voor de fixturecontrole van Sec. 1 over ALLE "
     "22 competities van de runlijst, inclusief de tien zonder wedstrijd en de zes bekers: 22 van "
     "22 eens met Fotmob, 6 duels tegen 6. Nul fouten.")

note("understat", "http_503",
     "23 nov (run A): VIJFDE RUNDAG OP RIJ ERUIT. getLeagueData geeft HTTP 200 met een "
     "onderhoudspagina (26.719 bytes, geen JSON) voor alle drie de gedekte competities die "
     "vandaag spelen: EPL, Serie_A en La_liga. Zelfde respons en zelfde bytegrootte als op 19, 20, "
     "21 en 22 november, dus geen nieuwe storing maar een voortdurende - vermoedelijk een "
     "permanent gewijzigde route of een blokkadepagina. NIET OMZEILD (Sec. 3, 'Niet doen': geen "
     "headless browser, geen challenge-solver, geen proxy). GEVOLG: p_xg_understat blijft leeg in "
     "het kalibratieblok van Sec. 6e, dus de reeks die moet uitwijzen of het ene xG-model beter "
     "voorspelt dan het andere groeit voor de vijfde rundag niet. GEEN gevolg voor my_prob, de "
     "tiers of de poorten - Sec. 4 noemt Understat redundantie en een tweede xG-model, geen "
     "invoer in my_prob, en alle zes duels halen hun kansinput bij Fotmob. Dit is dus GEEN geval "
     "van de uitzondering in Sec. 3 punt 3 (die gaat over Fotmob) en hoort niet vooraan in de "
     "notificatie. WEL: het tweede been onder Sec. 4 staat nu vijf rundagen niet onder de routine, "
     "en vanaf vandaag staat dat als openstaand punt in het dagrapport met owner = 'ik'.")

note("pinnacle_via_odds_api", "ok",
     "23 nov (run A): Pinnacle zat bij alle zes duels in de h2h- en totals-respons van The Odds "
     "API. De-vigde 1X2 naast de eigen kans: gemiddelde absolute afstand 4,57 pp over zes duels, "
     "gemiddelde Pinnacle-marge 3,48 procent. Op de TOTALEN staat het model gemiddeld 2,87 pp "
     "ONDER Pinnacle op P(Under), dus het verwacht meer doelpunten dan de scherpste prijs; de "
     "twee gepubliceerde regels zijn twee van de drie grootste afwijkingen van de dag (Wieczysta "
     "-11,13 pp, Levante -7,89 pp, en daartussen Brentford -8,74 pp dat door poort 7 is "
     "tegengehouden). HARDE GRENS Sec. 2/Sec. 4: dit getal gaat niet in my_prob en niet in "
     "prob_sources; het hoort in de vergelijking.")

note("forebet", "http_403",
     "Niet opnieuw geprobeerd op 23 nov (run A): bekende Cloudflare-blokkade, status overgenomen "
     "conform Stage 3. Wordt bewust niet omzeild.")

note("pinnacle_articles", "http_404",
     "Niet opnieuw geprobeerd op 23 nov (run A): /betting-articles/soccer/ bestaat sinds 20 sep "
     "2026 niet meer. De PRIJS van Pinnacle komt via The Odds API binnen en vult stap 2 van "
     "Stage 5 wel; zie pinnacle_via_odds_api.")

note("matchbook_blog", "http_530",
     "Niet opnieuw geprobeerd op 23 nov (run A): server lag er op 20 sep uit, status overgenomen "
     "conform Stage 3. De KOERSEN van Matchbook komen wel binnen via The Odds API, inclusief de "
     "2 procent beurscommissie van oddsapi.net_price - vandaag bij vier van de zes duels de beste "
     "prijs op minstens een markt.")

note("betfair_blog", "http_403",
     "Niet opnieuw geprobeerd op 23 nov (run A): Cloudflare, status overgenomen conform Stage 3. "
     "De KOERSEN van Betfair komen wel binnen via The Odds API, inclusief commissie.")

H["last_run"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")

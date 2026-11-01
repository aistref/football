"""Run A, 1 nov 2026 — bronprobe voor source-health.json.

ZEVENENDERTIG duels in het inzetvenster over ELF competities, tegen een zondagcap van 55: niets
afgekapt. Geen beker heeft een ronde en geen Europees toernooi speelt. Alle vier de bronkanten
werkelijk in gebruik (Fotmob, The Odds API, BetExplorer, Understat).

GEEN ENKELE BRONSTORING. `store["errors"]` is over de hele run leeg gebleven, en de
tweede-bronbevestiging van §1 is het over ALLE ZESTIEN competities eens — 37 tegen 37 duels, de
eerste run in weken zonder enig verschil tussen Fotmob en BetExplorer.

DE BEVINDING VAN VANDAAG ZIT IN DE INKOOPVOLGORDE EN NIET IN EEN BRON: zonder de tweede
BTTS-ronde van §1a stap 2 hadden de twee enige selecties die hun lat halen niet bestaan. Zie
`the_odds_api`.
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
     "1 nov (run A): daglijsten 1 en 2 nov opgehaald en voor de afwikkeling die van 31 okt en "
     "1 nov. idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. "
     "Standen van alle benodigde competitiebases geleverd: de elf spelende competities plus de "
     "divisie eronder voor de NEGEN omgerekende ploegen (Serie B, LaLiga2, Eerste Divisie, Liga "
     "Portugal 2, First Division B, 1. Lig en 1. Division DEN). Context voor ALLE 37 duels zonder "
     "een enkele fout, en alle 36 met een kansbron in het contextlogboek (1910 duels nu) - ook de "
     "duels die geen bet werden, zoals §1c eist. Ook de bekertak liep hierlangs: de daglijst geeft "
     "voor League Cup (133), DFB Pokal (209) en KNVB Beker (235) nul duels in het venster. "
     "Fotmob is nog steeds de enige xG-bron voor zes van de elf spelende competities, en de "
     "uitzondering van §3 punt 3 (melden zodra Fotmob omvalt) is dus niet aan de orde.")

note("the_odds_api", "ok",
     "1 nov (run A): 20000 credits over en 0 verbruikt - de maandwissel heeft het quotum gereset, "
     "en november heeft 30 dagen, dus suggest_cap zet het dagplafond op 333. ALLE ELF spelende "
     "competities hebben een sportkey en kregen de volledige bulk (h2h + spreads + totals, 3 "
     "credits per competitie, 33 in totaal); geen enkel duel hoeft voor de bet zelf op het gratis "
     "BetExplorer-marktgemiddelde te draaien. Daarna de tweede ronde van §1a stap 2: BTTS voor 23 "
     "duels met een kandidaat-edge, 23 credits. Totaal 56 van 20000. "
     "DAT WAS VANDAAG BESLISSEND EN HET IS DE BEVINDING VAN DEZE RUN: voor de BTTS-ronde stonden "
     "de twee enige selecties die hun lat halen op Under 2.5 @1,91 (Juventus - Napoli, +11,69 pp) "
     "en Under 2.75 @2,01 (Kasimpasa - Besiktas, +10,72 pp); met BTTS erbij scoort op beide duels "
     "de BTTS-nee hoger op selection_score (+12,75 resp. +13,22 pp) en is dat de gepubliceerde "
     "selectie. Dezelfde mening, een andere markt, een hogere prijs. Een run die BTTS zou "
     "overslaan omdat het een credit per duel kost, publiceert dus iets anders dan de regels "
     "voorschrijven. "
     "api_check.py meldt twee bekende sportkeys als NIET ACTIEF vandaag (Coppa Italia, DFB Pokal) "
     "- dat klopt met BetExplorer, waar de eerstvolgende ronde 1 dec resp. onbekend is - en vier "
     "actieve sportkeys die de repo niet kent: soccer_brazil_serie_b, soccer_germany_liga3, "
     "soccer_sweden_superettan en soccer_uefa_nations_league. Geen van de vier staat op een "
     "runlijst van Run A; de eerste drie zijn Run B-gebied en de Nations League is Run C. "
     "Geen enkele fout op een aanroep, geen enkele lege respons.")

note("betexplorer", "ok",
     "1 nov (run A): fixturepagina's van alle zestien competities van de runlijst opgehaald plus "
     "de vijf bekerpagina's, zonder een enkele fout. Gebruikt in twee rollen. EEN: het gratis "
     "1X2-marktgemiddelde voor §6e en poort 8 - 139 rijen over elf competities, waarvan 36 "
     "vandaag. TWEE: de tweede bron van de bevestigingspoort van §1, en die is vandaag volledig "
     "eens met Fotmob: 16 van de 16 competities en 37 tegen 37 duels, voor het eerst in weken "
     "zonder enig verschil. Bij de bekers bevestigt BetExplorer vier van de vijf met een "
     "eerstvolgende ronde erbij (FA Cup 6 nov, League Cup 15 dec, Coppa Italia 1 dec, KNVB Beker "
     "1 dec). DE DFB POKAL-FIXTUREPAGINA IS VANDAAG LEEG (0 teamparen, 200 OK): daar is Fotmob de "
     "enige bron die iets zegt, en dat is genoteerd als 'niet bevestigd' en niet als bevestiging. "
     "Dat onderscheid is precies wat 6 oktober 2026 vijf FA Cup-duels kostte, met de rollen "
     "omgedraaid.")

note("understat", "ok",
     "1 nov (run A): de vijf gedekte competities (PL, Serie A, La Liga, Bundesliga, Ligue 1) "
     "spelen vandaag ALLE VIJF, en Understat leverde voor alle vijf een tweede, onafhankelijk "
     "xG-model zonder fout en zonder sleutel. Dat is de arm waarop het kalibratieblok het eigen "
     "xG-model naast een ander zet: over 6951 uitkomsten staat de Understat-arm op +3,11 pp op "
     "longshots en -6,02 pp op favorieten, tegen +0,90 en -1,76 voor de eigen xG-methode met "
     "shrink 1.00 - dus Understat staat scheever dan de eigen arm en dat is sinds 19 september "
     "onveranderd. Blijft genormaliseerd op het EIGEN competitiegemiddelde van Understat (§4: dat "
     "ligt structureel ~0,13 xG per ploeg per duel hoger dan Fotmob) en gaat mee in het "
     "kalibratieblok, niet in my_prob.")

note("api_football", "plan_limited",
     "1 nov (run A): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker van "
     "27 september 2026 en geen storing - hij wil hier geen geld aan uitgeven. Niet als gat en "
     "niet als actiepunt melden (§3). De kanskant komt van Fotmob (alle competities) en Understat "
     "(vijf, vandaag alle vijf spelend); zolang die twee leveren is §2 gedekt. Fotmob leverde "
     "vandaag voor alle 37 duels, dus de uitzondering van §3 punt 3 is niet aan de orde.")

note("settling", "ok",
     "1 nov (run A): gebruikt bij het afwikkelen van 10 picks en 74 schaduwrijen over de "
     "daglijsten van 31 okt en 1 nov - de grootste afwikkeling in weken, en zonder een enkele "
     "verkeerde koppeling: 84 van de 85 open rijen kregen een wedstrijd met een plausibele "
     "uitslag. DE ENE DIE OPEN BLEEF IS CORRECT OPEN: Colorado Rapids - Chicago Fire FC trapte om "
     "01:30 UTC vanochtend af en de bron meldt hem na 2,1 uur nog niet afgelopen, dus hij gaat "
     "naar de volgende run. ALLE 84 AFGEWIKKELDE RIJEN ZIJN COMPETITIEWEDSTRIJDEN - de negen MLS- "
     "duels van 31 oktober zijn de laatste reguliere speelronde en geen play-offduel, dat is "
     "nagetrokken en niet aangenomen - dus er is geen verlenging of strafschoppenreeks en de "
     "eindstand IS de stand na 90 minuten (§6d); er hoefde geen doelpuntminuut te worden "
     "opgezocht. OPENSTAAND, onveranderd: niet nagegaan of de oude, te soepele naamregel in het "
     "verleden al eens een verkeerde uitslag heeft weggeschreven - dat is een audit over 68 "
     "rundagen.")

note("shadow_logboek", "gerepareerd",
     "1 nov (run A): 74 schaduwrijen in een keer afgewikkeld (39 gewonnen, 31 verloren, 4 void) "
     "met tmp-run/ra_nov01_settle.py, dezelfde marktlogica als elke run sinds 21 oktober. Dat is "
     "het grootste aantal op een dag tot nu toe en het is een gevolg van de volle zaterdag ervoor, "
     "niet van een stapel die was blijven liggen: er stond geen rij van voor 31 oktober open. Het "
     "logboek staat nu op 1517 kandidaten, waarvan 1458 afgewikkeld. De reeks 'lijstlengte' kreeg "
     "vandaag GEEN rij - er zijn maar twee wedstrijden met een selectie die alle negen poorten "
     "haalt en er zijn vijf plekken, dus de lijstlengte bindt niet (§5b).")

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)

H["last_run"] = {"run": "A", "date": "2026-11-01", "note": (
    "ZEVENENDERTIG duels in het inzetvenster over ELF competities, tegen een zondagcap van 55 - "
    "niets afgekapt, alle 37 doorgerekend, 28 op FULL, 8 op LIGHT (omgerekende promovendi) en 1 "
    "op NONE (Viborg - AC Horsens, omrekening buiten het gemeten bereik). De Championship en de "
    "Ekstraklasa hebben geen ronde, de drie Europese toernooien spelen dinsdag tot donderdag en "
    "geen van de vijf bekers heeft een ronde; dat is bij TWEE bronnen nagetrokken. NUL "
    "bronstoringen. 56 van 20000 credits (33 bulk + 23 BTTS; het quotum is met de maandwissel "
    "gereset). VIJF REGELS GEPUBLICEERD, waarvan TWEE hun lat halen: Juventus - Napoli BTTS nee "
    "@2,1564 (+12,75 pp) en Kasimpasa - Besiktas BTTS nee @2,4896 (+13,22 pp), beide een "
    "beurskoers bij Matchbook. Drie staan op rangorde in de lijst (§5b): Lyon - Angers Under 3.5, "
    "Getafe - Sevilla BTTS nee en Liverpool - Arsenal DNB Arsenal. DE BEVINDING: zonder de tweede "
    "BTTS-ronde van §1a stap 2 hadden die twee eerste regels niet bestaan - ze stonden voor de "
    "BTTS-aankoop als Under 2.5 en Under 2.75 met een lagere score. DRIE MARKTEN IN DE LIJST na "
    "twee rundagen die voor honderd procent Over/Under waren. tweede_methode vangt 356 van de 479 "
    "doorgerekende selecties (74%), de derde dag op rij boven de 70%, en de vraag welke van de "
    "twee methodes er stelselmatig naast zit is openstaand punt van deze run. STAGE 0: 10 picks "
    "afgewikkeld (6 gewonnen, 4 verloren) en 74 schaduwrijen (39 gewonnen, 31 verloren, 4 void).")}
H["last_run_bevinding"] = (
    "De inkoopvolgorde van §1a bepaalt wat er gepubliceerd wordt. BTTS wordt per duel afgerekend "
    "(1 credit) en pas in een tweede ronde gekocht voor wedstrijden die al een kandidaat-edge "
    "tonen; vandaag veranderde die ronde op BEIDE duels die hun lat halen de gepubliceerde "
    "selectie, van een Under naar de BTTS-nee van hetzelfde duel, met een hogere score. De regel "
    "is niet nieuw en er is niets aan veranderd - wat nieuw is, is het bewijs dat ze bijt.")
H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

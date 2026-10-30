"""Run A, 30 okt 2026 — bronprobe voor source-health.json.

TWAALF duels in het inzetvenster over NEGEN competities, geen enkele beker en geen Europees
toernooi: een vrijdagavond met de vooruitgeschoven duels van zeven competities, een volle
Ligue 1-ronde van drie en twee in de Ekstraklasa. Alle vier de bronkanten werkelijk in gebruik.
Fotmob voor de daglijsten, de 33 standen van `idcheck.py`, de context van alle 12 duels, de
voorbeschouwingsblokken van de vier bets en de marktvormtelling van alle 12. The Odds API voor de
bulk (ALLE NEGEN competities) en BTTS (5 duels). BetExplorer voor het gratis
1X2-marktgemiddelde, als tweede bron op de vraag wélke wedstrijden er zijn en voor de vijf bekers
zonder ronde. Understat deed voor vier duels mee.

GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.

DE BEVINDING VAN VANDAAG ZIT NIET IN EEN BRON MAAR IN `scripts/shadow.py`, en ze staat daarom
onder de rekenmodules: een selectie die §5b op rangorde publiceert kon tot vandaag óók als
afgewezen kandidaat in het schaduwlogboek belanden.
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
    print(f"{key:18} {status:12} {detail[:100]}")


note("fotmob", "ok",
     "30 okt (run A): daglijsten 30 en 31 okt opgehaald (170 duels in 94 competities en 723 in "
     "184) en voor de afwikkeling die van 28, 29 en 30 okt (548 duels geindexeerd). idcheck.py "
     "gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare stand. Standen van alle elf "
     "benodigde competitiebases geleverd: de negen spelende competities plus de 2. Bundesliga en "
     "de NordicBet Liga voor de twee promovendi (Elversberg, Lyngby), alle met xG. Context voor "
     "alle 12 duels zonder fout en alle 12 in het contextlogboek (1753 duels nu). Het stadion is "
     "bij alle 12 duels gevuld, dus context.check_venue heeft werkelijk gemeten en niet stil "
     "leeggestaan zoals van 25 t/m 27 oktober: NUL verplaatsingen gevonden, en dat is nu een "
     "meting en geen lege uitkomst. lineupType: 7 'predicted' en 5 'lastStarting11', geen enkele "
     "'confirmed' - te verwachten om 07:30 NL bij aftrappen van 18:00 tot 21:15. "
     "Voorbeschouwingsblokken (preview.py) voor alle VIER de bets zonder fout, en "
     "marketform.match_block voor alle 12 doorgerekende duels zonder fout. De vijf bekers "
     "hebben geen ronde: EFL Cup (id 133), DFB Pokal (209) en KNVB Cup (235) staan vandaag met "
     "nul duels in de daglijst, en dat is met BetExplorer bevestigd in plaats van eruit "
     "geconcludeerd (§5, de FA Cup-les van 6 oktober).")

note("the_odds_api", "ok",
     "30 okt (run A): sleutel geldig, 47 actieve voetbalcompetities, quota 18.579 over en 1.421 "
     "verbruikt bij de start van de run. Geen afgewezen sleutel en geen quotaprobleem. ALLE NEGEN "
     "spelende competities hebben een sportkey en kregen de volledige bulk (h2h + spreads + "
     "totals, 3 credits per competitie); daarna BTTS voor 5 duels met een kandidaat-edge. "
     "Verbruik 27 + 5 = 32 credits van een plafond van 4639 (suggest_cap(18579, 2)), nog 18.547 "
     "over van het maandplafond van 20.000. Dat elke competitie de bulk kreeg is het gevolg van "
     "de reparatie van 28 oktober: `soccer_spl` en de drie Europese toernooien staan sinds die "
     "dag in `oddsapi.SPORT_KEYS` en api_check.py meldt per bekende sleutel of hij actief is. "
     "ALLE TWAALF DUELS HEBBEN NU EEN BESTE PRIJS met een herleidbare bookmaker (gisteren 20 van "
     "22, eergisteren 11 van 22); de winst op het marktgemiddelde ligt tussen +4,60% en +8,98%, "
     "gemiddeld +6,55%. Twee bekende sportkeys zijn vandaag niet actief: Coppa Italia en DFB "
     "Pokal, en dat klopt - die hebben geen ronde. VIER actieve sportkeys kent de repo niet: "
     "soccer_brazil_serie_b, soccer_germany_liga3, soccer_sweden_superettan en "
     "soccer_uefa_nations_league. Alle vier vallen buiten de Run A-runlijst en zijn dus werk voor "
     "Run B en Run C; ze staan hier zodat die runs ze niet opnieuw hoeven te zoeken.")

note("betexplorer", "ok",
     "30 okt (run A): negen competitie-fixturepagina's opgehaald met fetch_league_fixtures, geen "
     "enkele fout - La Liga 20 rijen, Bundesliga 18, Ligue 1 18, Championship 24, Primeira Liga "
     "9, Belgian Pro League 10, Super Lig 9, Danish Superliga 5, Ekstraklasa 9. Het "
     "marktgemiddelde komt van 10 tot 16 boeken per duel en wordt gebruikt waarvoor het bedoeld "
     "is (§1a): het kalibratieblok van §6e en poort 8, niet de bet zelf - die loopt vandaag bij "
     "alle twaalf duels op de beste prijs. Daarnaast de vijf bekerfixturepagina's als TWEEDE "
     "BRON op de vraag of er een ronde is: FA Cup eerstvolgend 6 november, League Cup 14 "
     "december, Coppa Italia 1 december, KNVB Beker en DFB Pokal geen teamparen op de pagina. "
     "`ra_oct30_bevestiging.py` legt de twee bronnen over alle 16 competities naast elkaar en ze "
     "zijn het 16 van de 16 keer eens (12 duels tegen 12).")

note("understat", "ok",
     "30 okt (run A): drie van de vijf gedekte competities spelen vandaag (La Liga, Bundesliga, "
     "Ligue 1) en Understat leverde voor VIER duels een tweede, onafhankelijk xG-model - "
     "Villarreal - Espanyol, Le Havre - PSG, Nice - Rennes en Lille - Lens. Bundesliga leverde "
     "niets voor Elversberg - Mainz, wat te verwachten is bij een promovendus die vorig seizoen "
     "niet in de Understat-tabel stond. Geen fout, geen sleutel nodig. Blijft genormaliseerd op "
     "het EIGEN competitiegemiddelde van Understat (§4: die ligt structureel ~0,13 xG per ploeg "
     "per duel hoger dan Fotmob) en gaat mee in het kalibratieblok, niet in my_prob.")

note("api_football", "plan_limited",
     "30 okt (run A): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker van "
     "27 september 2026 en geen storing - hij wil hier geen geld aan uitgeven. Niet als gat en "
     "niet als actiepunt melden (§3). De kanskant komt van Fotmob (alle competities) en Understat "
     "(vijf); zolang die twee leveren is §2 gedekt. Wordt wél vooraan in de notificatie gemeld "
     "zodra Fotmob niet meer levert, want dan is er geen onafhankelijke kansinput meer.")

note("settling", "ok",
     "30 okt (run A): gebruikt bij het afwikkelen van 6 picks en 38 schaduwrijen over de "
     "daglijsten van 28 t/m 30 oktober, zonder een enkele verkeerde koppeling - alle 44 rijen "
     "kregen een wedstrijd met een plausibele uitslag. TWEE van de 44 zijn knock-outduels (EFL "
     "Cup: Bournemouth - Aston Villa; DFB Pokal: Hannover 96 - Kaiserslautern) en bij beide meldt "
     "Fotmob `reason = Full-Time`, dus status.scoreStr IS daar de stand na 90 minuten en er "
     "hoefde geen doelpuntminuut te worden opgezocht (§6d). Dat is nagetrokken en niet "
     "aangenomen: 3-0 en 0-2 zijn beslissende uitslagen, maar 0-2 had ook na verlenging kunnen "
     "vallen. DE PICKS STONDEN TWEE DAGEN OPEN omdat de run van 29 oktober niet is gedraaid; dat "
     "is geen fout van deze module. OPENSTAAND, onveranderd: niet nagegaan of de oude, te soepele "
     "naamregel in het verleden al eens een verkeerde uitslag heeft weggeschreven - dat is een "
     "audit over 66 rundagen.")

note("shadow_logboek", "gerepareerd",
     "30 okt (run A): DE BEVINDING VAN DEZE RUN. `shadow.py collect` boekte een selectie die "
     "§5b op RANGORDE had gepubliceerd ook als afgewezen kandidaat. Zolang "
     "EDGE_THRESHOLD_FULL een poort was kon dat niet: een `zonder_herijking`-blok beschreef per "
     "definitie een selectie die de drempel niet haalde en dus niet gepubliceerd kon worden. "
     "Sinds §5b op 20 september de drempel in een AFKAPPING heeft veranderd kan dezelfde "
     "selectie wél in de lijst komen - en dan staat ze zowel in picks.jsonl als in "
     "shadow.jsonl met `failed_gate = herijking` erbij, terwijl geen enkele poort haar heeft "
     "tegengehouden. Vandaag gebeurde dat bij Lille - Lens, Over 2.5 @1,94. GEREPAREERD: "
     "collect slaat een kandidaat over waarvan markt EN koers gelijk zijn aan een gepubliceerde "
     "pick van dezelfde run en dag - dezelfde vergelijking die `_dubbel` al deed voor near_miss "
     "tegen poort 8 en 9. EN DE HISTORIE IS NAGELOPEN: twee oudere rijen van 19 september "
     "(Wrexham - Southampton, Over 2.5 @1,78, gewonnen; Hibernian - Aberdeen, 1 @1,8036, "
     "verloren) waren op dezelfde manier dubbel geboekt en zijn verwijderd. De `herijking`-reeks "
     "gaat daarmee van 59 naar 57 afgewikkelde gevallen en van -3,3% naar -3,1%; de conclusie "
     "eronder verandert niet, maar §6d zegt zelf dat bij deze aantallen een verkeerd geboekte "
     "regel zwaarder weegt dan alles wat de poort werkelijk doet. OPENSTAAND: er zijn acht "
     "oudere paren waar een schaduwrij dezelfde markt en koers heeft als een pick die op `void` "
     "staat (23 en 31 aug, 4 sep). Een void pick valt buiten de ROI, dus daar wordt niets dubbel "
     "geteld en is er vandaag niets aan gedaan - maar het is niet uitgezocht waarom die picks "
     "void zijn en dat hoort op een dag met meer tijd dan een run.")

H["last_run"] = {"run": "A", "date": "2026-10-30",
                 "note": "TWAALF duels in het inzetvenster over NEGEN competities, geen beker en "
                         "geen Europees toernooi - 12 onder de cap van 55, dus niets afgekapt. "
                         "Tien duels op FULL, twee op LIGHT (de promovendi Elversberg en Lyngby, "
                         "omgerekend uit de divisie eronder), NUL op NONE. VIER REGELS, alle vier "
                         "een Over/Under: Nice - Rennes Over 2.5 @1,67 (+8,74 pp, boven de lat), "
                         "Lille - Lens Over 2.5 @1,94 (+7,99915 pp - 0,00085 pp onder de lat, "
                         "ruw +8,37 erboven), Le Havre - PSG Under 2.5 @3,10 (+7,07 pp, op "
                         "rangorde eronder) en Zulte Waregem - Club Brugge Under 3.25 @2,01 "
                         "(+3,29 pp, op rangorde eronder). DE BEVINDING: shadow.py boekte een "
                         "selectie die §5b op rangorde publiceerde ook als afgewezen kandidaat - "
                         "gerepareerd, en twee oudere dubbele rijen van 19 september verwijderd. "
                         "TWEE VAN DE VIER REGELS STAAN OP DE UNDER-KANT en zijn door geen van "
                         "beide latten getoetst; §6g meet daar ongeveer twee procentpunt te veel "
                         "kans, en bij Zulte Waregem blijft van +3,29 pp dan niets over. Poort 8 "
                         "hield zes selecties over twee wedstrijden tegen - waaronder Le Havre "
                         "+1.5, de selectie die de RUWE dagranglijst aanvoert - en poort 8 ruw "
                         "geen enkele. Poort 9 hield de Under 3.5 van Le Havre tegen en liet de "
                         "2.5 van dezelfde wedstrijd door; dat is geen fout maar het gevolg van "
                         "twee regels die elkaar raken, en het staat sinds 28 oktober als vraag "
                         "bij de gebruiker. tweede_methode vangt 123 van de 159 doorgerekende "
                         "selecties. Pinnacle is het met alle vier de regels oneens. DE RUN VAN "
                         "29 OKTOBER IS NIET GEDRAAID: zes picks en 38 schaduwrijen van 28 "
                         "oktober stonden twee dagen open en zijn vanmorgen afgewikkeld, vijf "
                         "van de zes picks gewonnen. Nul bronstoringen, 32 van 4639 credits."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

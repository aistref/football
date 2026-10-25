"""Run A, 25 okt 2026 — bronprobe voor source-health.json.

46 duels in het inzetvenster over TWAALF competities: een volle zondag, negen onder de cap van 55.
Alle vier de bronkanten werkelijk in gebruik. Fotmob voor de daglijsten, de 33 standen van
`idcheck.py`, de context van alle 46 duels, de voorbeschouwingsblokken van de vijf bets en de
marktvormtelling van 44 duels. The Odds API voor de bulk (elf competities) en BTTS (30 duels).
BetExplorer voor het gratis 1X2-marktgemiddelde, als tweede bron op de vraag wélke wedstrijden er
zijn, als ENIGE 1X2-bron voor de Scottish Premiership (geen sportkey) én als enige bron voor de
vijf bekers. Understat deed voor zestien duels mee — alle vijf zijn competities speelden.

GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.

WEL EEN FOUT IN DE REPO ZELF, en die hoort hier omdat ze over het lezen van een bron gaat:
`settling.DayIndex.lookup` koppelde een MLS-wedstrijd aan een USL League One-wedstrijd op de
eerste zes letters van beide clubnamen. Zie de regel `settling` hieronder.
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
    print(f"{key:18} {status:8} {detail[:110]}")


note("fotmob", "ok",
     "25 okt (run A): daglijsten 25 en 26 okt opgehaald en voor de afwikkeling de daglijsten van "
     "24 en 25 okt (1260 duels geindexeerd); idcheck.py gaf voor alle 33 fotmob_id's uit "
     "coverage.json een bruikbare stand. Standen van alle twaalf spelende competities geleverd, "
     "alle twaalf met xG in zowel 2025/2026 als het lopende seizoen, plus de standen van de "
     "divisies eronder/erboven voor de tien omgerekende duels (promotion.py). Context opgehaald "
     "voor ALLE 46 duels met NUL fouten, en alle 43 doorgerekende duels met context zijn nieuw in "
     "het contextlogboek. lineupType: 35 'predicted', 9 'lastStarting11', 2 'unavailable'; geen "
     "enkel 'confirmed', wat om 03:30 NL bij aftrappen van 12:15 tot 21:30 te verwachten is. LET "
     "OP EEN STILLE LEEGTE: venue.name is bij ALLE 46 duels None, dus context.check_venue heeft "
     "niets kunnen vergelijken en 'niet verplaatst' betekent hier 'geen verplaatsing gemeten'. "
     "Voorbeschouwingsblokken (preview.py) voor alle vijf de bets zonder fout, en "
     "marketform.match_block voor alle 44 doorgerekende duels zonder fout.")

note("the_odds_api", "ok",
     "25 okt (run A): sleutel geldig, 47 actieve voetbalcompetities, quota 18.806 over en 1.194 "
     "verbruikt bij de start van de run. Elf van de twaalf spelende competities hebben een "
     "sportkey; de Scottish Premiership heeft er geen en draait daarom op het "
     "BetExplorer-marktgemiddelde. Geen afgewezen sleutel en geen quotaprobleem.")

note("oddsapi", "ok",
     "25 okt (run A): 11 bulk-aanroepen (h2h + spreads + totals, 3 credits per competitie) en 30 "
     "event-aanroepen voor BTTS (1 credit per duel), samen 63 van een plafond van 1341 - alle 41 "
     "geslaagd, nul fouten. Nog 18.743 over met zeven dagen tot de maandwissel. Marktbalans: alle "
     "elf gekochte competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt (11 van 11, "
     "waar de controle er een eist). Beste prijs tegen het marktgemiddelde: gemiddeld +6,66% over "
     "de 42 duels waar beide bekend zijn (van +2,41% tot +19,31%). Drie van de vijf gepubliceerde "
     "regels staan op een beurs (Matchbook) en zijn met net_price doorgerekend.")

note("betexplorer", "ok",
     "25 okt (run A): 12 competitiefixturepagina's voor het gratis 1X2-marktgemiddelde plus 5 "
     "bekerfixturepagina's; alle 17 leverden teamparen op, dus geen van de drie gedocumenteerde "
     "faalmodi (homepage-redirect, teamparen zonder koers, lege pagina) is opgetreden. Als tweede "
     "bron op de vraag welke wedstrijden er zijn: 46 duels bij Fotmob tegen 46 bij BetExplorer "
     "over zestien competities, NUL afwijkingen. Voor de Scottish Premiership de enige 1X2-bron "
     "(twee duels, marktgemiddelde, bookmaker niet herleidbaar). TIJDZONE: BetExplorer labelt in "
     "UK-tijd, en sinds vannacht is dat GMT tegen CET in Nederland - nog steeds precies een uur "
     "verschil, dus de vensterfilter hoefde niet te veranderen.")

note("understat", "ok",
     "25 okt (run A): alle VIJF Understat-competities speelden vandaag (PL, Serie A, La Liga, "
     "Bundesliga, Ligue 1) en voor 16 duels is een tweede, onafhankelijk xG-model geleverd, "
     "inclusief rollende xG over acht duels. Dat raakt VIER van de vijf gepubliceerde regels "
     "(Sunderland - Leeds United, Manchester United - AFC Bournemouth, Real Sociedad - Levante en "
     "Lecce - Juventus); NEC Nijmegen - FC Groningen leunt uitsluitend op Fotmob, in twee "
     "doorsnedes. MEETRESULTAAT DAT HOORT TE BLIJVEN STAAN: over 5.871 uitkomsten staat de "
     "Understat-arm SCHEEVER dan de Fotmob-arm (+3,24 pp op longshots en -6,35 pp op favorieten, "
     "tegen +0,82 / -1,58). Dat is een meting en geen reden om iets te veranderen - my_prob leunt "
     "niet op Understat (§4) - maar het is wel het antwoord op de vraag van 31 augustus, en het "
     "antwoord is dat het andere xG-model niet beter voorspelt.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Fotmob leverde deze run zonder fout en "
     "Understat deed voor dertien duels mee, dus §2 is gedekt en er is niets te doen. Wordt pas "
     "een echt probleem zodra Fotmob omvalt.")

note("settling", "gerepareerd",
     "25 okt (run A): `shadow.py open` meldde Portland Timbers - Charlotte FC (MLS, Run B van 24 "
     "okt) als afgelopen met 4-1 terwijl dat duel nog niet was begonnen; de 4-1 kwam van Portland "
     "Hearts of Pine - Charlotte Independence uit de USL League One. Oorzaak: de tweede stap van "
     "`settling.DayIndex.lookup` vergeleek alleen de eerste ZES letters van beide clubnamen "
     "('portla', 'charlo') en accepteerde de koppeling omdat er precies een zo'n wedstrijd op die "
     "daglijst stond - 'precies een kandidaat' is geen bescherming als die ene kandidaat een "
     "andere club is. Gerepareerd: de stap eist nu dat een genormaliseerde naam een echt "
     "VOORVOEGSEL van de andere is (`settling._prefix_pair`). Swansea -> Swansea City en Grazer AK "
     "-> Grazer AK 1902 blijven koppelen; Portland Timbers -> Portland Hearts of Pine niet meer. "
     "ER IS NIETS VERKEERD AFGEREKEND: het settle-script van Stage 0 koppelt zelf strenger en gaf "
     "'MIS', dus twee stappen waren het oneens en de fout kwam aan het licht voordat er iets was "
     "weggeschreven. OPENSTAAND: niet nagegaan of deze regel in het verleden al eens een "
     "verkeerde uitslag heeft weggeschreven - dat is een audit over 61 rundagen.")

H["last_run"] = {"run": "A", "date": "2026-10-25",
                 "note": "46 duels in het inzetvenster over twaalf competities - een volle "
                         "zondag, negen onder de cap van 55. Geen enkel kruis-grensduel; 36 FULL, "
                         "8 LIGHT met een omgerekende ploeg en TWEE NONE (Hull City en AC Horsens "
                         "buiten conversion_in_range), dus 44 van de 46 doorgerekend over 636 "
                         "selecties in alle zes de markten. EERSTE WINTERTIJDDAG: de "
                         "hardgecodeerde +02:00 in de runscripts is vervangen door "
                         "ZoneInfo('Europe/Amsterdam'), zoals Run A van 24 okt als actiepunt "
                         "noteerde. De LIJSTLENGTE bindt: zes duels hadden een publiceerbare "
                         "selectie en er passen vijf regels in. Alle 5 gepubliceerde regels halen "
                         "hun eigen lat - voor het eerst in weken - en de afvaller (Slask Wroclaw "
                         "- Wieczysta Krakow, Over 3.5 op LIGHT) haalde zijn lat ook. Nul "
                         "bronstoringen, 63 van 1341 credits. EEN FOUT GEVONDEN EN GEREPAREERD in "
                         "settling.DayIndex.lookup - zie de bronregel 'settling'."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

"""Run A, 24 okt 2026 — bronprobe voor source-health.json.

51 duels in het inzetvenster over TWAALF competities: een volle zaterdag en de grootste Run A-dag
in weken (Championship 11, Bundesliga 6, vier competities met elk 4). Alle vier de bronkanten
werkelijk in gebruik en zwaarder dan ooit belast. Fotmob voor de daglijsten, de 33 standen van
`idcheck.py`, de context van alle 51 duels, de voorbeschouwingsblokken van de vijf bets en de
marktvormtelling van 50 duels. The Odds API voor de bulk (elf competities) en BTTS (28 duels).
BetExplorer voor het gratis 1X2-marktgemiddelde, als tweede bron op de vraag wélke wedstrijden er
zijn, als ENIGE 1X2-bron voor de Scottish Premiership (geen sportkey) én als enige bron voor de
vijf bekers. Understat deed voor dertien duels mee — alle vijf zijn competities speelden.

GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.
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
     "24 okt (run A): daglijsten 24 en 25 okt opgehaald en voor de afwikkeling de daglijsten van "
     "23 en 24 okt (995 duels geindexeerd); idcheck.py gaf voor alle 33 fotmob_id's uit "
     "coverage.json een bruikbare stand. Standen van alle twaalf spelende competities geleverd, "
     "alle twaalf met xG in zowel 2025/2026 als het lopende seizoen, plus de standen van de "
     "divisies eronder/erboven voor de twintig omgerekende ploegen (promotion.py). Context "
     "opgehaald voor ALLE 51 duels met NUL fouten - de breedste contextprobe tot nu toe, en 47 "
     "ervan zijn nieuw in het contextlogboek. lineupType: 25 'predicted', 22 'lastStarting11', 4 "
     "'unavailable'; geen enkel 'confirmed', wat om 04:15 NL bij aftrappen van 12:15 tot 21:30 te "
     "verwachten is. LET OP EEN STILLE LEEGTE: venue.name is bij ALLE 51 duels None, dus "
     "context.check_venue heeft niets kunnen vergelijken en 'niet verplaatst' betekent hier 'geen "
     "verplaatsing gemeten'. Voorbeschouwingsblokken (preview.py) voor alle vijf de bets zonder "
     "fout, en marketform.match_block voor alle 50 doorgerekende duels zonder fout.")

note("the_odds_api", "ok",
     "24 okt (run A): sleutel geldig, 48 actieve voetbalcompetities, quota 18.945 over en 1.055 "
     "verbruikt bij de start van de run. Elf van de twaalf spelende competities hebben een "
     "sportkey; de Scottish Premiership heeft er geen en draait daarom op het "
     "BetExplorer-marktgemiddelde. Geen afgewezen sleutel en geen quotaprobleem.")

note("oddsapi", "ok",
     "24 okt (run A): 11 bulk-aanroepen (h2h + spreads + totals, 3 credits per competitie) en 28 "
     "event-aanroepen voor BTTS (1 credit per duel), samen 61 van een plafond van 1182 - alle 39 "
     "geslaagd, nul fouten. Nog 18.884 over met acht dagen tot de maandwissel. Marktbalans: alle "
     "elf gekochte competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt (11 van 11, "
     "waar de controle er een eist). Beste prijs tegen het marktgemiddelde: gemiddeld +5,66% over "
     "de 46 duels waar beide bekend zijn (van +3,38% tot +8,49%). Drie van de vijf gepubliceerde "
     "regels staan op een beurs (Matchbook) en zijn met net_price doorgerekend.")

note("betexplorer", "ok",
     "24 okt (run A): 12 competitiefixturepagina's voor het gratis 1X2-marktgemiddelde plus 5 "
     "bekerfixturepagina's; alle 17 leverden teamparen op, dus geen van de drie gedocumenteerde "
     "faalmodi (homepage-redirect, teamparen zonder koers, lege pagina) is opgetreden. Als tweede "
     "bron op de vraag welke wedstrijden er zijn: 51 duels bij Fotmob tegen 51 bij BetExplorer "
     "over zestien competities, NUL afwijkingen. Voor de Scottish Premiership de enige 1X2-bron "
     "(vier duels, marktgemiddelde, bookmaker niet herleidbaar).")

note("understat", "ok",
     "24 okt (run A): alle VIJF Understat-competities speelden vandaag (PL, Serie A, La Liga, "
     "Bundesliga, Ligue 1) en voor 13 duels is een tweede, onafhankelijk xG-model geleverd, "
     "inclusief rollende xG over acht duels. Dat raakt DRIE van de vijf gepubliceerde regels "
     "(Chelsea - Tottenham, Como - Sassuolo, Lazio - Parma); Alverca - Arouca en de twee "
     "LIGHT-regels leunen uitsluitend op Fotmob, in twee doorsnedes. MEETRESULTAAT DAT HOORT TE "
     "BLIJVEN STAAN: over 5.871 uitkomsten staat de Understat-arm SCHEEVER dan de Fotmob-arm "
     "(+3,24 pp op longshots en -6,35 pp op favorieten, tegen +0,82 / -1,58). Dat is een meting en "
     "geen reden om iets te veranderen - my_prob leunt niet op Understat (§4) - maar het is wel "
     "het antwoord op de vraag van 31 augustus, en het antwoord is dat het andere xG-model niet "
     "beter voorspelt.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Fotmob leverde deze run zonder fout en "
     "Understat deed voor dertien duels mee, dus §2 is gedekt en er is niets te doen. Wordt pas "
     "een echt probleem zodra Fotmob omvalt.")

H["last_run"] = {"run": "A", "date": "2026-10-24",
                 "note": "51 duels in het inzetvenster over twaalf competities - de grootste Run "
                         "A-lijst in weken, vier onder de zaterdagcap van 55. Geen enkel "
                         "kruis-grensduel; 33 FULL, 17 LIGHT met een omgerekende ploeg en EEN "
                         "NONE (Erzurumspor FK buiten conversion_in_range), dus 50 van de 51 "
                         "doorgerekend over 705 selecties in alle zes de markten. Voor het eerst "
                         "in weken bindt de LIJSTLENGTE: veertien duels hadden een publiceerbare "
                         "selectie en er passen vijf regels in. 3 van de 5 halen hun lat, 2 staan "
                         "op rangorde (§5b), en een gekwalificeerde selectie valt af op "
                         "lijstlengte (Chelsea - Tottenham, BTTS nee). Nul bronstoringen, 61 van "
                         "1182 credits. Looptijd 34,2 minuten."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

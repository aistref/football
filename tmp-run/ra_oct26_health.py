"""Run A, 26 okt 2026 — bronprobe voor source-health.json.

ZEVEN duels in het inzetvenster over VIJF competities: een maandag, 33 onder de cap van 40.
Alle vier de bronkanten werkelijk in gebruik. Fotmob voor de daglijsten, de 33 standen van
`idcheck.py`, de context van alle zeven duels, de voorbeschouwingsblokken van de drie bets en
de marktvormtelling van zeven duels. The Odds API voor de bulk (vijf competities) en BTTS (zes
duels). BetExplorer voor het gratis 1X2-marktgemiddelde, als tweede bron op de vraag wélke
wedstrijden er zijn, en als enige bron voor de vijf bekers. Understat deed voor twee duels mee.

GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.

WEL EEN FOUT IN DE REPO ZELF, en die hoort hier omdat ze over het lezen van een bron gaat: de
naamkoppeling tussen Fotmobs `OB` en BetExplorers `Odense` ontbrak. Zie de regel `teamnames`.
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
     "26 okt (run A): daglijsten 26 en 27 okt opgehaald en voor de afwikkeling de daglijsten van "
     "24, 25 en 26 okt (1260 duels geindexeerd); idcheck.py gaf voor alle 33 fotmob_id's uit "
     "coverage.json een bruikbare stand. Standen van alle vijf spelende competities geleverd, "
     "alle vijf met xG in zowel 2025/2026 als het lopende seizoen. Geen enkele promovendi- of "
     "kruis-grensomrekening nodig: geen van de veertien ploegen valt buiten de stand van vorig "
     "seizoen. Context opgehaald voor ALLE zeven duels met NUL fouten, en alle zeven zijn nieuw "
     "in het contextlogboek. lineupType: 4 'predicted' en 3 'lastStarting11' (de drie Turkse "
     "duels), geen enkel 'confirmed' - te verwachten om 04:00 NL bij aftrappen van 17:00 tot "
     "21:00. LET OP DEZELFDE STILLE LEEGTE ALS GISTEREN: venue.name is bij ALLE zeven duels None, "
     "dus context.check_venue heeft niets kunnen vergelijken en 'niet verplaatst' betekent hier "
     "'geen verplaatsing gemeten'. Voorbeschouwingsblokken (preview.py) voor alle drie de bets "
     "zonder fout, en marketform.match_block voor alle zeven duels zonder fout.")

note("the_odds_api", "ok",
     "26 okt (run A): sleutel geldig, 46 actieve voetbalcompetities, quota 18.695 over en 1.305 "
     "verbruikt bij de start van de run. Alle vijf spelende competities hebben een sportkey, dus "
     "geen enkele competitie viel vandaag terug op alleen het BetExplorer-marktgemiddelde. Geen "
     "afgewezen sleutel en geen quotaprobleem.")

note("oddsapi", "ok",
     "26 okt (run A): 5 bulk-aanroepen (h2h + spreads + totals, 3 credits per competitie) en 6 "
     "event-aanroepen voor BTTS (1 credit per duel), samen 21 van een plafond van 1556 - alle 11 "
     "geslaagd, nul fouten. Nog 18.674 over met zes dagen tot de maandwissel. Marktbalans: alle "
     "vijf gekochte competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt (5 van 5, "
     "waar de controle er een eist). Beste prijs tegen het marktgemiddelde: gemiddeld +7,47% over "
     "alle zeven duels (van +5,70% tot +9,27%). Een van de drie gepubliceerde regels staat op een "
     "beurs (Matchbook, 2,12 bruto / 2,0976 na 2% commissie) en is met net_price doorgerekend. DE "
     "HERDRAAI VAN VANMORGEN KOSTTE NUL CREDITS: de analyse is opnieuw gedraaid op de al "
     "ingekochte respons in tmp-run/ra_oct26_odds.json.")

note("betexplorer", "ok",
     "26 okt (run A): 5 competitiefixturepagina's voor het gratis 1X2-marktgemiddelde plus 5 "
     "bekerfixturepagina's; alle 10 leverden teamparen op (40, 8, 8, 26 en 16 bij de bekers), dus "
     "geen van de drie gedocumenteerde faalmodi (homepage-redirect, teamparen zonder koers, lege "
     "pagina) is opgetreden. Als tweede bron op de vraag welke wedstrijden er zijn: 7 duels bij "
     "Fotmob tegen 7 bij BetExplorer over zestien competities, NUL afwijkingen - inclusief de elf "
     "competities die vandaag GEEN WEDSTRIJD hebben. TIJDZONE: BetExplorer labelt in UK-tijd, en "
     "dat is sinds de wintertijd GMT tegen CET in Nederland - nog steeds precies een uur "
     "verschil, dus het venster [26.10. 08:00 NL, 27.10. 08:00 NL) is in UK-tijd "
     "[26.10. 07:00, 27.10. 07:00). WAT ER VANDAAG MIS GING ZAT NIET IN DE BRON MAAR IN DE "
     "NAAMKOPPELING ERNAARTOE - zie de regel `teamnames`.")

note("understat", "ok",
     "26 okt (run A): twee van de vijf Understat-competities speelden vandaag (La Liga en "
     "Ligue 1) en voor beide duels is een tweede, onafhankelijk xG-model geleverd, inclusief "
     "rollende xG over acht duels: Sevilla - Osasuna en PSG - Lyon. Dat raakt EEN van de drie "
     "gepubliceerde regels (PSG - Lyon Under 2.5); Santa Clara - Benfica en Besiktas - Basaksehir "
     "leunen uitsluitend op Fotmob, in twee doorsnedes. De Premier League, Serie A en Bundesliga "
     "speelden niet. MEETRESULTAAT DAT BLIJFT STAAN: in het kalibratielogboek van vandaag (6282 "
     "uitkomsten) staat de Understat-arm SCHEEVER dan de Fotmob-arm (+3,06 pp op longshots en "
     "-5,89 pp op favorieten, tegen +0,89 / -1,71 voor de xG-methode op shrink 1.0). Dat is een "
     "meting en geen reden om iets te veranderen - my_prob leunt niet op Understat (§4) - maar "
     "het blijft het antwoord op de vraag van 31 augustus: het andere xG-model voorspelt niet "
     "beter.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Fotmob leverde deze run zonder fout en "
     "Understat deed voor twee duels mee, dus §2 is gedekt en er is niets te doen. Wordt pas een "
     "echt probleem zodra Fotmob omvalt - en vandaag leunen vijf van de zeven duels alleen op "
     "Fotmob, dus die afhankelijkheid is op een maandag groter dan in het weekend.")

note("teamnames", "gerepareerd",
     "26 okt (run A): Fotmob schrijft de Deense club als `OB` (Odense Boldklub) en BetExplorer "
     "als `Odense`. Na `norm` blijft {ob} tegen {odense} over - geen gedeeld token - en de "
     "naamgelijkenis over het paar is 0,25, ruim onder de vloer van 0,62 van `best_pair`. The "
     "Odds API schrijft `OB Odense BK` en kwam wel door ({ob} is een deelverzameling van {ob, "
     "odense, bk}), dus FC Kobenhavn - OB kreeg gewoon spreads, totals en BTTS en ALLEEN het "
     "gratis BetExplorer-marktgemiddelde viel weg. PRECIES DAT GEMIDDELDE IS WAAR POORT 8 OP "
     "DRAAIT: het duel kwam uit op `underdog_reason = \"geen 1X2-prijzen - geen marktoordeel over "
     "wie de mindere is\"`, dus poort 8 stond OPEN ZONDER TE ZIJN GETOETST, en de selectie die "
     "daardoor doorliep - Asian Handicap OB Odense BK +1 @2,15, +5,71 pp - stond in de eerste "
     "doorrekening op plek 2 van de lijst en was gepubliceerd. Met de alias `ob -> odense` in "
     "scripts/teamnames.py zet de markt OB op 15,6% tegen 64,1% voor FC Kobenhavn, ver onder "
     "sides.UNDERDOG_FLOOR = 0,35, en houdt poort 8 alle vier de OB-selecties tegen. Het kostte "
     "ook het kalibratieblok van dit duel (3 van de 21 waarnemingen van vandaag). DE RUN IS "
     "VOLLEDIG HERDRAAID op dezelfde, al ingekochte prijzen: nul extra credits. DERDE KEER DEZE "
     "MAAND DAT DEZELFDE STILLE FAALSTAND TOESLAAT - `qpr` op 9 oktober (ook een initiaalwoord "
     "tegen een plaatsnaam, ook poort 8 open zonder toetsing) en de `is_today`-filter op 7 "
     "oktober (ook een ontbrekend marktgemiddelde, ook een gepubliceerde regel eronder). Alle "
     "drie faalden zonder foutmelding. OPENSTAAND: er is geen controle die ZEGT dat een "
     "doorgerekend duel geen marktgemiddelde heeft; `progress.py verify` kijkt naar de zes "
     "markten en niet naar deze bron. Dat is de structurele vorm van dit probleem en ze is "
     "vandaag niet opgelost.")

note("settling", "ok",
     "26 okt (run A): de reparatie van 25 oktober (`settling._prefix_pair`) is vanmorgen in "
     "gebruik geweest bij het afwikkelen van 11 picks en 70 schaduwrijen over de daglijsten van "
     "24, 25 en 26 oktober, zonder een enkele verkeerde koppeling: alle 81 rijen kregen een "
     "wedstrijd met een plausibele uitslag en het settle-script van Stage 0 was het op alle 81 "
     "met `settling` eens. Los Angeles FC - LA Galaxy stond nog niet op afgelopen en is correct "
     "blijven staan. OPENSTAAND, onveranderd sinds gisteren: niet nagegaan of de oude, te "
     "soepele regel in het verleden al eens een verkeerde uitslag heeft weggeschreven - dat is "
     "een audit over 62 rundagen.")

H["last_run"] = {"run": "A", "date": "2026-10-26",
                 "note": "ZEVEN duels in het inzetvenster over VIJF competities - een maandag, 33 "
                         "onder de cap van 40. Geen enkel kruis-grensduel en geen enkele "
                         "omrekening: alle zeven op FULL, alle zeven doorgerekend over 103 "
                         "selecties in alle zes de markten. DRIE REGELS, ALLE DRIE OP DE "
                         "UNDER-KANT - de kant die §6g op -16,5% meet tegen +10,6% voor de Over - "
                         "waarvan een boven zijn eigen lat (Santa Clara - Benfica, +11,92 pp) en "
                         "twee op rangorde eronder. EEN FOUT IN DE REPO GEVONDEN DIE EEN BET "
                         "TEGENHIELD in plaats van er een te kosten: de ontbrekende alias `ob -> "
                         "odense` maakte poort 8 blind op FC Kobenhavn - OB, en de selectie die "
                         "daardoor doorliep stond op plek 2 van de lijst. Run volledig herdraaid, "
                         "nul extra credits. Poort 9 bindt op PSG - Lyon Under 3.5 (+9,11 pp) "
                         "terwijl dezelfde wedstrijd Under 2.5 met +7,06 pp alsnog publiceert: de "
                         "niet-monotonie van 16/17 oktober, nu voor het eerst binnen een "
                         "wedstrijd. Nul bronstoringen, 21 van 1556 credits."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

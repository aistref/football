"""Run A, 27 okt 2026 — bronprobe voor source-health.json.

TWEEENTWINTIG duels in het inzetvenster over VIER competities, en NEGENTIEN ervan zitten in een
beker: het drukste Run A-programma van de maand, 22 onder de cap van 40. Alle vier de bronkanten
werkelijk in gebruik. Fotmob voor de daglijsten, de 33 standen van `idcheck.py`, de context van
alle 22 duels, de voorbeschouwingsblokken van de drie bets en de marktvormtelling van elf duels.
The Odds API voor de bulk (twee competities) en BTTS (vier duels). BetExplorer voor het gratis
1X2-marktgemiddelde en als tweede bron op de vraag wélke wedstrijden er zijn. Understat deed voor
de drie Serie A-duels mee.

GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.

TWEE DINGEN DIE HIER HOREN OMDAT ZE OVER HET LEZEN VAN EEN BRON GAAN: de drie bekers staan wél in
de Fotmob-daglijst (regel `fotmob`), en de naamkoppeling naar de standtabel koppelde FC Eindhoven
aan PSV Eindhoven (regel `teamnames`).
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
     "27 okt (run A): daglijsten 27 en 28 okt opgehaald en voor de afwikkeling die van 26 en 27 "
     "okt (325 duels geindexeerd); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een "
     "bruikbare stand. DE BELANGRIJKSTE WAARNEMING VAN VANDAAG ZIT HIER: DE DRIE BEKERS MET EEN "
     "RONDE STAAN WEL IN DE DAGLIJST, onder EFL Cup id 133 (2 duels), DFB Pokal id 209 (8) en "
     "KNVB Cup id 235 (9) - exact dezelfde aantallen als BetExplorer. Die drie id's staan NIET in "
     "coverage.json, dus runwindow.matches_for_run kan ze niet filteren en elke run van oktober "
     "heeft de bekers langs BetExplorer gedaan. Het verschil is niet academisch: via de daglijst "
     "komen de duels met match_id, dus met context, opstelling, uitvallers en poort 7, en via "
     "BetExplorer alleen met namen en een koers - dat is wat het op 6 oktober kostte, toen vier "
     "van de vijf FA Cup-duels daardoor niet door te rekenen waren. Standen van alle zeven "
     "competitiebases geleverd (Serie A, Premier League, League One, Bundesliga, 2. Bundesliga, "
     "Eredivisie, Eerste Divisie), alle met xG behalve de Eerste Divisie - vandaar twee "
     "LIGHT-duels. Context voor alle 22 duels zonder fout, 17 ervan in het contextlogboek. "
     "lineupType: geen enkel 'confirmed' - te verwachten om 03:30 NL bij aftrappen van 18:00 tot "
     "21:00. LET OP DEZELFDE STILLE LEEGTE ALS DE TWEE DAGEN HIERVOOR: venue.name is bij ALLE 22 "
     "duels None, dus context.check_venue heeft niets kunnen vergelijken en 'niet verplaatst' "
     "betekent hier 'geen verplaatsing gemeten'. Voorbeschouwingsblokken (preview.py) voor alle "
     "drie de bets zonder fout, en marketform.match_block voor alle elf doorgerekende duels "
     "zonder fout.")

note("the_odds_api", "ok",
     "27 okt (run A): sleutel geldig, 49 actieve voetbalcompetities, quota 18.661 over en 1.339 "
     "verbruikt bij de start van de run. Geen afgewezen sleutel en geen quotaprobleem. MAAR WEL "
     "EEN ECHTE BEPERKING VANDAAG, en die hoort als bronbevinding en niet als krap plafond: TWEE "
     "VAN DE VIER SPELENDE COMPETITIES HEBBEN GEEN SPORTKEY. De League Cup (ENG) en de KNVB Beker "
     "(NED) staan niet bij de 49 actieve competities - soccer_germany_dfb_pokal bestaat wel, de "
     "twee andere bekers niet - dus elf van de 22 duels hebben geen beste prijs, geen spreads, "
     "geen totals en geen BTTS, en vallen terug op het gratis BetExplorer-marktgemiddelde. De "
     "edge valt daar systematisch te laag uit (conservatief, geen risico op te veel bets) en de "
     "bookmaker is niet herleidbaar. Alle drie de gepubliceerde regels komen uit Serie A, waar de "
     "beste prijs er wel is.")

note("oddsapi", "ok",
     "27 okt (run A): 2 bulk-aanroepen (h2h + spreads + totals, 3 credits per competitie) en 4 "
     "event-aanroepen voor BTTS (1 credit per duel), samen 9 van een plafond van 1864 - alle 6 "
     "geslaagd, nul fouten. Nog 18.652 over met vijf dagen tot de maandwissel. Marktbalans: beide "
     "gekochte competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt (2 van 2, waar "
     "de controle er een eist); dat de twee bekers zonder sportkey alleen een gratis 1X2 kregen "
     "is een ontbrekende competitie bij de bron en geen plafondkwestie - zie the_odds_api. Een "
     "van de drie gepubliceerde regels staat op een beurs (Matchbook, 2,38 bruto / 2,3524 na 2% "
     "commissie) en is met net_price doorgerekend.")

note("betexplorer", "ok",
     "27 okt (run A): 4 competitiefixturepagina's voor het gratis 1X2-marktgemiddelde plus 5 "
     "bekerfixturepagina's; alle 9 leverden teamparen op (20, 8, 16, 20 bij de competities en 40, "
     "8, 8, 26, 16 bij de bekers), dus geen van de drie gedocumenteerde faalmodi "
     "(homepage-redirect, teamparen zonder koers, lege pagina) is opgetreden. Als tweede bron op "
     "de vraag welke wedstrijden er zijn: 3 duels bij Fotmob tegen 3 bij BetExplorer over zestien "
     "competities, NUL afwijkingen - inclusief de vijftien die vandaag GEEN WEDSTRIJD hebben. EN "
     "VOOR HET EERST IS DAT OOK VOOR DE BEKERS MET TWEE BRONNEN GELUKT: BetExplorer geeft 2, 8 en "
     "9 duels in het venster en de Fotmob-daglijst dezelfde 2, 8 en 9 - zie de regel `fotmob`. De "
     "twee bekers zonder ronde (FA Cup, Coppa Italia) staan alleen op BetExplorer, met als "
     "eerstvolgende ronde 6 november 20:45 en 1 december 21:00. TIJDZONE: BetExplorer labelt in "
     "UK-tijd, en dat is sinds de wintertijd GMT tegen CET in Nederland - nog steeds precies een "
     "uur verschil, dus het venster [27.10. 08:00 NL, 28.10. 08:00 NL) is in UK-tijd "
     "[27.10. 07:00, 28.10. 07:00). Voor elf van de 22 duels is BetExplorer vandaag de ENIGE "
     "1X2-bron, want de League Cup en de KNVB Beker hebben geen sportkey.")

note("understat", "ok",
     "27 okt (run A): een van de vijf Understat-competities speelde vandaag (Serie A) en voor "
     "alle drie de duels is een tweede, onafhankelijk xG-model geleverd, inclusief rollende xG "
     "over acht duels: Sassuolo - Lazio, Roma - Cagliari en Torino - Como. Dat raakt ALLE DRIE de "
     "gepubliceerde regels, want alle drie komen uit Serie A - een gunstiger stand dan gisteren, "
     "toen een van de drie bets een Understat-arm had. De negentien bekerduels leunen uitsluitend "
     "op Fotmob, in twee doorsnedes van dezelfde meting. De Premier League, La Liga, Bundesliga "
     "en Ligue 1 speelden niet.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Fotmob leverde deze run zonder fout en "
     "Understat deed voor alle drie de bets mee, dus §2 is gedekt en er is niets te doen. Wordt "
     "pas een echt probleem zodra Fotmob omvalt - en vandaag leunen negentien van de 22 duels "
     "alleen op Fotmob, want een beker heeft geen Understat-tabel. Op een bekerdag is die "
     "afhankelijkheid dus groter dan op een gewone competitiedag.")

note("teamnames", "gerepareerd",
     "27 okt (run A): `tmp-run/ra_names.resolve` koppelde op een DEELVERZAMELING van tokens - "
     "`tokens(a) <= tokens(b) or tokens(b) <= tokens(a)`. Dat zegt alleen dat alle woorden van de "
     "korte naam in de lange voorkomen en niet WAAR ze staan. `fc` staat in `_DROP`, dus FC "
     "Eindhoven houdt het ene token `eindhoven` over en dat is een deelverzameling van {psv, "
     "eindhoven}: DE EERSTE-DIVISIECLUB FC EINDHOVEN KOPPELDE AAN PSV EINDHOVEN IN DE "
     "EREDIVISIE-STAND. Precies een treffer, dus de veiligheidsregel 'alleen bij een kandidaat' "
     "ving het niet, en FC Eindhoven - FC Volendam kwam op FULL uit met de xG van de kampioen "
     "achter de thuisploeg. GEEN ENKELE VAN DE NEGEN POORTEN KAN DAT ZIEN - het is geen te ruime "
     "kans maar een verkeerde ploeg, en dat is erger dan de `ob`-alias van gisteren, die alleen "
     "een poort blind maakte. Dezelfde faalvorm als de Jong Ajax-koppeling waarop "
     "promotion.measure_gap op 31 augustus een factor 1.010 vond. GEREPAREERD VOOR DE ANALYSE en "
     "niet erna (§4), met de eis die §4 al aan promotion.find_team stelt: een afkorting laat de "
     "STAART weg, nooit de KOP. `teamnames.is_abbreviation` doet dat op woordniveau en staat in "
     "scripts/ en niet in tmp-run/, zodat er een implementatie is en geen twee die uiteenlopen - "
     "dezelfde les als de ob-alias. REGRESSIE over alle 44 teamnamen van vandaag: precies een "
     "verschil, en dat is FC Eindhoven zelf (nu None, dus langs de promovendi-omrekening, waar "
     "hij op conversion_in_range alsnog op NONE uitkomt). Zelftest in ra_oct27_namecheck.py, 12 "
     "gevallen. OPENSTAAND: `scripts/settling.py` heeft dezelfde deelverzamelingsregel. Daar is "
     "ze met opzet ruim ('ruim, niet streng') en beslist lookup op het PAAR thuis-en-uit plus de "
     "eis van precies een kandidaat, dus de rem is er anders - maar het is wel hetzelfde patroon "
     "en het is vandaag niet aangeraakt, omdat een poort verzetten die niet knelt geen werk is "
     "dat een run op eigen initiatief doet.")

note("settling", "ok",
     "27 okt (run A): gebruikt bij het afwikkelen van 4 picks en 10 schaduwrijen over de "
     "daglijsten van 26 en 27 oktober, zonder een enkele verkeerde koppeling - alle 14 rijen "
     "kregen een wedstrijd met een plausibele uitslag en het settle-script van Stage 0 was het op "
     "alle 14 met `settling` eens. Alle veertien zijn competitieduels, dus status.scoreStr IS de "
     "stand na 90 minuten en er hoefde geen doelpuntminuut te worden opgezocht (§6d). OPENSTAAND, "
     "onveranderd: niet nagegaan of de oude, te soepele regel in het verleden al eens een "
     "verkeerde uitslag heeft weggeschreven - dat is een audit over 63 rundagen, en de "
     "deelverzamelingsregel van vandaag (zie `teamnames`) maakt die vraag scherper dan hij "
     "gisteren was.")

H["last_run"] = {"run": "A", "date": "2026-10-27",
                 "note": "TWEEENTWINTIG duels in het inzetvenster over VIER competities, 19 ervan "
                         "in een beker - het drukste Run A-programma van de maand, 22 onder de cap "
                         "van 40. ELF duels op NONE, en dat is bij een bekerronde de verwachting: "
                         "amateurclubs en Regionalliga-ploegen staan in geen divisie waarvoor een "
                         "omrekenfactor bestaat. DRIE REGELS, ALLE DRIE SERIE A EN ALLE DRIE OP DE "
                         "WEINIG-DOELPUNTENKANT (Under 2.75, BTTS nee, Under 3), waarvan een boven "
                         "zijn eigen lat (Sassuolo - Lazio, +15,15 pp) en twee op rangorde "
                         "eronder. DRIE ONAFHANKELIJKE METINGEN WIJZEN VANDAAG DEZELFDE KANT OP "
                         "TEGEN DIE DRIE REGELS: de vormfout van §6g (P(Under 2.5) 2,1 pp te "
                         "hoog), Pinnacle (3 van 3 duels onder dit model op de Under-kant, "
                         "gemiddeld 9,93 pp) en de marktvormtelling van §4 (Sassuolo 75% boven 2,5 "
                         "dit seizoen, Torino en Como samen 75% en 62% BTTS). TWEE BEVINDINGEN: de "
                         "drie bekers staan WEL in de Fotmob-daglijst (ids 133/209/235, zelfde "
                         "aantallen als BetExplorer) en het gat zat in coverage.json; en "
                         "ra_names.resolve koppelde FC Eindhoven aan PSV EINDHOVEN - gerepareerd "
                         "voor de analyse, met de voorvoegselregel van teamnames.is_abbreviation. "
                         "Poort 8 en poort 9 binden vandaag nergens, omdat tweede_methode 62 van "
                         "de 83 selecties eerder afvangt. Nul bronstoringen, 9 van 1864 credits."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

"""Run A, 28 okt 2026 — bronprobe voor source-health.json.

DRIEENDERTIG duels in het inzetvenster over VIJF competities, en TWEEENTWINTIG ervan zitten in
een beker: het drukste Run A-programma van deze maand, 33 onder de cap van 40. Alle vier de
bronkanten werkelijk in gebruik. Fotmob voor de daglijsten, de 33 standen van `idcheck.py`, de
context van alle 33 duels, de voorbeschouwingsblokken van de drie bets en de marktvormtelling van
22 duels. The Odds API voor de bulk (VIER competities) en BTTS (14 duels). BetExplorer voor het
gratis 1X2-marktgemiddelde en als tweede bron op de vraag wélke wedstrijden er zijn. Understat
deed voor twee Serie A-duels mee.

GEEN ENKELE bronstoring. `store["errors"]` is over de hele run leeg gebleven.

DE BEVINDING VAN VANDAAG STAAT ONDER `the_odds_api` EN GAAT OVER DE INKOOP: twee sportkeys die
bestonden en niet werden gebruikt.
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
     "28 okt (run A): daglijsten 28 en 29 okt opgehaald (271 en 125 duels) en voor de afwikkeling "
     "die van 27 en 28 okt (491 duels geindexeerd); idcheck.py gaf voor alle 33 fotmob_id's uit "
     "coverage.json een bruikbare stand. De drie bekers met een ronde staan opnieuw in de "
     "daglijst, onder EFL Cup id 133 (5 duels), DFB Pokal id 209 (8) en KNVB Cup id 235 (9) - "
     "exact dezelfde aantallen als BetExplorer, dus de dag is met twee methodes vastgesteld. "
     "Standen van alle zeven competitiebases geleverd (Serie A, Scottish Premiership, Premier "
     "League, Bundesliga, 2. Bundesliga, Eredivisie, Eerste Divisie), alle met xG behalve de "
     "Eerste Divisie - vandaar de LIGHT-tier bij VVV-Venlo - Vitesse. Context voor alle 33 duels "
     "zonder fout, 26 ervan in het contextlogboek (de zeven amateurclubs van de KNVB Beker hebben "
     "geen selectiewaarde, dus `out_share` is daar None en ctxlog.py slaat ze terecht over). "
     "EN DE STILLE LEEGTE VAN 25 T/M 27 OKTOBER IS VANDAAG WEG: `venue.name` was die drie dagen "
     "bij ALLE duels None, waardoor context.check_venue niets kon vergelijken en 'niet verplaatst' "
     "in werkelijkheid 'niet gemeten' betekende. Vandaag is het stadion bij ALLE 33 duels gevuld "
     "en slaat de controle ook echt aan: TWEE verplaatsingen gevonden (SSV Jeddeloh - Hertha BSC "
     "in het Marschwegstadion Oldenburg in plaats van de HASKAMP-Arena, en JOS Watergraafsmeer - "
     "NAC Breda op Sportpark Goed Genoeg in plaats van Sportpark Drieburg). Beide duels komen op "
     "NONE uit, dus geen gepubliceerde bet wordt geraakt - maar de controle werkt weer, en dat is "
     "iets anders dan drie dagen stil open staan. lineupType: 5 'predicted', 22 "
     "'lastStarting11', 2 'unavailable' en 4 leeg; geen enkele 'confirmed', en dat is te "
     "verwachten om 03:30 NL bij aftrappen van 18:00 tot 21:00. Voorbeschouwingsblokken "
     "(preview.py) voor alle drie de bets zonder fout, en marketform.match_block voor alle 22 "
     "doorgerekende duels zonder fout.")

note("the_odds_api", "ok",
     "28 okt (run A): sleutel geldig, 51 actieve voetbalcompetities, quota 18.633 over en 1.367 "
     "verbruikt bij de start van de run. Geen afgewezen sleutel en geen quotaprobleem. DE "
     "BEVINDING VAN VANDAAG ZIT HIER EN HET WAS GEEN BRONPROBLEEM MAAR EEN ADMINISTRATIEF GAT: "
     "VAN DE VIJF SPELENDE COMPETITIES KREGEN ER GISTEREN TWEE GEEN BESTE PRIJS TERWIJL HUN "
     "SPORTKEY BESTAAT. De runscripts gaven voor de Scottish Premiership en de League Cup "
     "sportkey=None mee. soccer_england_efl_cup staat sinds 10 aug 2026 in oddsapi.SPORT_KEYS; "
     "voor de Scottish Premiership noteert coverage.json bij die competitie AL SINDS 9 SEPTEMBER "
     "dat soccer_spl werkte ('5 events op h2h+spreads+totals'), maar die bevinding is nooit in "
     "SPORT_KEYS geland. WAAROM NIEMAND HET ZAG: api_check.py filterde zijn lijst 'relevante "
     "sportkeys' op de SLEUTEL en zocht daar het woord 'scot' in - en soccer_spl bevat dat woord "
     "alleen in title ('Premiership - Scotland') en description ('Scottish Premiership'). De "
     "controle stond dus elke ochtend groen terwijl ze de verkeerde grootheid mat, dezelfde "
     "stille faalvorm als het Serie B-id en calibration.py settle. GEVOLG: de Scottish "
     "Premiership draaide van 9 sep t/m 27 okt uitsluitend op het gratis "
     "BetExplorer-marktgemiddelde, en dat gemiddelde gaat daar over maar DRIE boeken - vandaag "
     "ligt de beste prijs er 4,90% tot 11,95% boven. GEREPAREERD voor de analyse en niet erna "
     "(§4): soccer_spl staat nu in SPORT_KEYS, net als de drie Europese toernooien die er ook "
     "nog niet in stonden, en api_check.py noemt vanaf nu per bekende sleutel of hij vandaag "
     "actief is EN welke actieve sleutels de repo niet kent (gefilterd op sleutel, titel en "
     "beschrijving). Die tweede lijst wijst nog vijf gaten aan die BUITEN de Run A-runlijst "
     "vallen en dus voor Run B en C zijn: soccer_norway_eliteserien, soccer_sweden_superettan, "
     "soccer_germany_liga3, soccer_spain_copa_del_rey en soccer_uefa_nations_league. Alleen de "
     "KNVB Beker heeft werkelijk geen sportkey; dat raakt vandaag twee doorgerekende duels.")

note("oddsapi", "ok",
     "28 okt (run A): 4 bulk-aanroepen (h2h + spreads + totals, 3 credits per competitie) en 14 "
     "event-aanroepen voor BTTS (1 credit per duel), samen 26 van een plafond van 2326 - alle 18 "
     "geslaagd, nul fouten. Nog 18.607 over met vier dagen tot de maandwissel. Marktbalans: alle "
     "VIER de gekochte competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt (4 van "
     "4, waar de controle er een eist) - ruimer dan gisteren, toen het 2 van 2 was. Dat de KNVB "
     "Beker alleen een gratis 1X2 kreeg is een ontbrekende competitie bij de bron en geen "
     "plafondkwestie, zie the_odds_api. Alle drie de gepubliceerde regels staan op een beste "
     "prijs met een herleidbare bookmaker (1xBet, Pinnacle, Coolbet); geen enkele op een beurs, "
     "dus net_price raakte vandaag geen van de drie.")

note("betexplorer", "ok",
     "28 okt (run A): 5 competitiefixturepagina's voor het gratis 1X2-marktgemiddelde plus 5 "
     "bekerfixturepagina's; alle 10 leverden teamparen op (17, 15, 6, 8, 9 bij de competities en "
     "40, 6, 8, 17, 8 bij de bekers), dus geen van de drie gedocumenteerde faalmodi "
     "(homepage-redirect, teamparen zonder koers, lege pagina) is opgetreden. Als tweede bron op "
     "de vraag welke wedstrijden er zijn: 33 duels bij Fotmob tegen 33 bij BetExplorer over "
     "negentien competities, NUL afwijkingen - inclusief de dertien die vandaag GEEN WEDSTRIJD "
     "hebben, en inclusief de drie bekers met een ronde (5, 8 en 9 bij beide bronnen). De twee "
     "bekers zonder ronde (FA Cup, Coppa Italia) staan alleen op BetExplorer, met als "
     "eerstvolgende ronde 6 november 20:30 en 1 december 21:00. TIJDZONE: BetExplorer labelt in "
     "UK-tijd, en dat is sinds de wintertijd GMT tegen CET in Nederland - nog steeds precies een "
     "uur verschil, dus het venster [28.10. 08:00 NL, 29.10. 08:00 NL) is in UK-tijd "
     "[28.10. 07:00, 29.10. 07:00). LET OP DE BREEDTE VAN HET GEMIDDELDE: 16 boeken bij Serie A "
     "en 11 bij de DFB Pokal, maar maar DRIE bij de Scottish Premiership en de League Cup. Daar "
     "is het marktgemiddelde dus een dun getal, en dat maakt het des te belangrijker dat die "
     "twee competities vanaf vandaag ook een beste prijs hebben (zie the_odds_api). Voor twee "
     "KNVB Beker-duels blijft BetExplorer de ENIGE 1X2-bron.")

note("understat", "ok",
     "28 okt (run A): een van de vijf Understat-competities speelde vandaag (Serie A) en voor "
     "TWEE van de vijf duels is een tweede, onafhankelijk xG-model geleverd: Milan - Bologna en "
     "Genoa - Juventus. Bij de andere drie staat minstens een ploeg niet in de Understat-tabel "
     "van vorig seizoen (Venezia en Monza zijn promovendus; Parma en Udinese ontbreken op naam). "
     "GEEN van de drie gepubliceerde regels heeft dus een Understat-arm - een ongunstiger stand "
     "dan gisteren, toen alle drie de bets uit Serie A kwamen. De 22 bekerduels en de zes Schotse "
     "duels leunen uitsluitend op Fotmob, in twee doorsnedes van dezelfde meting. De Premier "
     "League, La Liga, Bundesliga en Ligue 1 speelden niet.")

note("api_football", "missing_key",
     "API_FOOTBALL_KEY niet gezet. Besluit van de gebruiker op 27 sep 2026 (_shared-rules.md "
     "§3) - geen gat en geen actiepunt: hij wil hier geen geld aan uitgeven. De kanskant komt "
     "van Fotmob (alle competities) en Understat (vijf). Fotmob leverde deze run zonder fout, dus "
     "§2 is gedekt en er is niets te doen. Wordt pas een echt probleem zodra Fotmob omvalt - en "
     "vandaag leunen 31 van de 33 duels alleen op Fotmob, want een beker heeft geen "
     "Understat-tabel en de Scottish Premiership ook niet. Op een bekerdag is die afhankelijkheid "
     "dus groter dan op een gewone competitiedag.")

note("teamnames", "ok",
     "28 okt (run A): de voorvoegselregel van 27 oktober (`teamnames.is_abbreviation`) is vandaag "
     "opnieuw nagelopen over 66 namen, en ZE BEET METEEN. Precies een verschil met de oude "
     "deelverzamelingsregel, en dat is EXCELSIOR MAASSLUIS uit de KNVB Beker: de oude regel "
     "koppelde die amateurclub aan EXCELSIOR in de Eredivisie-stand, de nieuwe weigert. Zonder "
     "die reparatie was Excelsior Maassluis - SC Heerenveen doorgerekend met de xG van Excelsior "
     "Rotterdam achter de thuisploeg, en geen van de negen poorten kan dat zien - het is geen te "
     "ruime kans maar een verkeerde ploeg. Nu komt het duel op NONE uit, wat het hoort te zijn. "
     "Dat een reparatie van gisteren vandaag meteen iets tegenhoudt, is precies de reden dat §4 "
     "zegt: meet een nieuwe factor liever voor de analyse van de dag dan erna. OPENSTAAND, "
     "onveranderd: `scripts/settling.py` heeft nog dezelfde deelverzamelingsregel. Daar is ze met "
     "opzet ruim en beslist lookup op het PAAR thuis-en-uit plus de eis van precies een "
     "kandidaat, dus de rem is er anders - maar het is hetzelfde patroon, en het is vandaag niet "
     "aangeraakt omdat een poort verzetten die niet knelt geen werk is dat een run op eigen "
     "initiatief doet.")

note("settling", "ok",
     "28 okt (run A): gebruikt bij het afwikkelen van 6 picks en 7 schaduwrijen over de "
     "daglijsten van 27 en 28 oktober, zonder een enkele verkeerde koppeling - alle 13 rijen "
     "kregen een wedstrijd met een plausibele uitslag en het settle-script van Stage 0 was het op "
     "alle 13 met `settling` eens. Alle dertien zijn competitieduels (Serie A, Serie B, League "
     "One, Bundesliga, Allsvenskan), dus status.scoreStr IS de stand na 90 minuten en er hoefde "
     "geen doelpuntminuut te worden opgezocht (§6d). OPENSTAAND, onveranderd: niet nagegaan of de "
     "oude, te soepele naamregel in het verleden al eens een verkeerde uitslag heeft "
     "weggeschreven - dat is een audit over 64 rundagen.")

H["last_run"] = {"run": "A", "date": "2026-10-28",
                 "note": "DRIEENDERTIG duels in het inzetvenster over VIJF competities, 22 ervan "
                         "in een beker - het drukste Run A-programma van deze maand, 33 onder de "
                         "cap van 40. ELF duels op NONE, en dat is bij een bekerronde de "
                         "verwachting: amateurclubs en een Regionalliga-ploeg staan in geen "
                         "divisie waarvoor een omrekenfactor bestaat, en vijf duels vallen op "
                         "conversion_in_range. DRIE REGELS, uit drie verschillende competities en "
                         "drie verschillende markten: Bournemouth wint tegen Aston Villa @2,32 "
                         "(+15,39 pp, boven de lat), Hannover 96 -0,25 tegen Kaiserslautern @2,06 "
                         "(+11,14 pp, boven de lat) en St. Mirren - Hibernian Under 3 @1,71 "
                         "(+6,43 pp, op rangorde eronder). DE BEVINDING: twee sportkeys die "
                         "bestonden en niet werden gebruikt (soccer_spl en "
                         "soccer_england_efl_cup), waardoor de Scottish Premiership sinds "
                         "9 september op een marktgemiddelde over drie boeken draaide. Elf van de "
                         "33 duels kregen vandaag voor het eerst een beste prijs; api_check.py "
                         "controleert vanaf nu per bekende sleutel of hij actief is. Poort 9 hield "
                         "twee selecties tegen (beide St. Mirren - Hibernian, Under 2.75 op "
                         "+8,81 pp onder de verzwaarde lat van 10,0) terwijl de 3.0-lijn van "
                         "datzelfde duel op +6,43 pp wel is gepubliceerd - dat is geen fout maar "
                         "het gevolg van twee regels die elkaar raken, en het staat als vraag bij "
                         "de gebruiker. Poort 8 hield negentien selecties over vijf wedstrijden "
                         "tegen, poort 8 ruw geen enkele. tweede_methode vangt 234 van de 299 "
                         "doorgerekende selecties. Nul bronstoringen, 26 van 2326 credits."}

json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

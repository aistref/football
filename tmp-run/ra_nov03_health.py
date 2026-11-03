"""Run A, 3 nov 2026 — bronprobe voor source-health.json.

ACHTTIEN duels in het inzetvenster over TWEE competities (Championship 9, Champions League 9),
tegen een dinsdagcap van 40: niets afgekapt. Geen beker heeft een ronde en de twee andere
Europese toernooien spelen pas donderdag.

EEN BRONSTORING, EN DIE IS NIET NIEUW MAAR WEL VERANDERD VAN SYMPTOOM: Understat is voor de
tweede dag op rij onbereikbaar. Gisteren een 502 op de CONNECT van de netwerkgateway, vandaag een
`Connection reset by peer`. Twee dagen, twee symptomen, dezelfde onbereikbaarheid. Het raakt
vandaag niets: geen van de vijf gedekte competities speelt. Zie `understat`.

DE BEVINDING VAN VANDAAG ZIT IN DE VASTLEGGING EN NIET IN EEN BRON: `bet_beide = False` heeft
drie standen en de tekst bij een pick had er twee, waardoor een gekwalificeerde bet zichzelf als
rangorderegel beschreef. Zie `notes_bet_beide` en `last_run_bevinding`.
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
     "3 nov (run A): daglijsten 3 en 4 nov opgehaald (52 competities / 163 duels en 41 / 115) en "
     "voor de afwikkeling die van 1, 2 en 3 nov. idcheck.py gaf voor alle 33 fotmob_id's uit "
     "coverage.json een bruikbare stand. Standen geleverd voor de twee spelende competitiebases "
     "(Championship id 48 en Champions League id 42, beide met xG) plus de divisies voor de DRIE "
     "omgerekende ploegen van vandaag (Premier League voor Burnley, League One voor Lincoln City "
     "en Bolton Wanderers). "
     "CONTEXT VOOR ALLE ACHTTIEN DUELS OPGEHAALD ZONDER EEN ENKELE FOUT, en alle achttien zijn in "
     "het contextlogboek beland (§1c eist dat ook voor afgekapte duels; er was vandaag niets "
     "afgekapt). De datarijkdom liep van 5,0 tot 8,0, en dat verschil loopt netjes langs de "
     "competitiegrens: de negen Champions League-duels staan op 7,0-8,0 en de negen "
     "Championship-duels op 5,0-5,5. De oorzaak is het opstellingsblok - om 03:00 NL staat er "
     "voor een Champions League-avondduel al een voorspelde opstelling en voor de Championship "
     "nog niet. Dat is een eigenschap van het tijdstip van de run en niet van de bron. "
     "DE BEKERTAK LIEP OOK HIERLANGS: de daglijst geeft voor League Cup (133), DFB Pokal (209) en "
     "KNVB Beker (235) nul duels in het venster, en BetExplorer bevestigt dat. "
     "FOTMOB IS VANDAAG DE ENIGE XG-BRON, want Understat ligt eruit en geen van zijn vijf "
     "competities speelt vandaag toch al. De uitzondering van §3 punt 3 (melden zodra Fotmob "
     "omvalt) is dus niet aan de orde, maar de marge is nul: valt Fotmob ook om, dan is er geen "
     "kansinput meer en levert elke run gegarandeerd nul bets.")

note("the_odds_api", "ok",
     "3 nov (run A): sleutel werkt. api_check.py: 50 actieve voetbalcompetities, 19841 credits "
     "over en 159 verbruikt deze maand, en 33 van de 34 sportkeys van de repo actief vandaag. "
     "DE ENIGE INACTIEVE IS COPPA ITALIA (soccer_italy_coppa_italia) en dat klopt met de tweede "
     "bron: BetExplorer zet de eerstvolgende ronde op 1 december. Vijf actieve sportkeys kent de "
     "repo niet (soccer_brazil_serie_b, soccer_germany_liga3, soccer_spain_copa_del_rey, "
     "soccer_sweden_superettan, soccer_uefa_nations_league); geen van vijf staat op de runlijst "
     "van Run A. De Copa del Rey is vandaag nieuw in dat rijtje en hoort op de runlijst van Run B "
     "thuis, niet hier. "
     "INKOOP: beide spelende competities hebben een sportkey en kregen de volledige bulk "
     "(h2h + spreads + totals, 3 credits per competitie, 6 in totaal), plus een tweede ronde "
     "BTTS van 11 credits voor de elf duels met een kandidaat-edge (§1a stap 2). 17 van een "
     "plafond van 353 (suggest_cap over 28 dagen tot de maandwissel, twee runs per dag), 19824 "
     "over. Geen enkel duel hoefde op het gratis BetExplorer-marktgemiddelde te leunen.")

note("betexplorer", "ok",
     "3 nov (run A): marktgemiddelde 1X2 voor beide spelende competities geleverd (Championship "
     "24 fixturerijen waarvan 9 vandaag, Champions League 18 waarvan 9 vandaag) en de "
     "fixturepagina's van alle zestien competities plus de vijf bekers. Dat laatste is de "
     "bevestiging door een tweede methode van §1, en ze is het over ALLE ZESTIEN competities met "
     "Fotmob eens: 18 duels tegen 18, zonder enig verschil. "
     "ALLE VIJF BEKERPAGINA'S GAVEN TEAMPAREN (FA Cup 40, League Cup 4, Coppa Italia 8, KNVB "
     "Beker 16, DFB Pokal 8), dus er is nergens een lege pagina die als bevestiging zou kunnen "
     "worden gelezen - anders dan op 1 november, toen de DFB Pokal-pagina leeg was. De "
     "eerstvolgende rondes: FA Cup 6 nov, Coppa Italia 1 dec, KNVB Beker 1 dec, DFB Pokal 1 dec, "
     "League Cup 15 dec.")

note("understat", "onbereikbaar",
     "3 nov (run A): NIET BEREIKBAAR, voor de TWEEDE DAG OP RIJ, en met een ANDER symptoom dan "
     "gisteren. Gisteren: 'URLError ... Tunnel connection failed: 502 Bad Gateway' op de CONNECT "
     "van de netwerkgateway. Vandaag: 'UnderstatError: URLError op "
     "https://understat.com/getLeagueData/EPL/2025/2026: <urlopen error [Errno 104] Connection "
     "reset by peer>'. Twee dagen, twee symptomen, dezelfde onbereikbaarheid - dat de melding "
     "verandert maakt het eerder een netwerk- of upstream-toestand dan een eenmalige hapering. "
     "WAT HET VANDAAG KOST: NIETS, en dat is toeval en geen herstel. Understat dekt vijf "
     "competities (PL, La Liga, Bundesliga, Serie A, Ligue 1) en GEEN VAN DIE VIJF SPEELT "
     "VANDAAG - de runlijst bestond uit de Championship en de Champions League. Er was dus ook "
     "zonder deze storing geen Understat-arm in het kalibratieblok van §6e geweest. Een volgende "
     "run met een van die vijf competities op de lijst ziet wel wat het kost. "
     "WAT HET NOOIT KOST: geen bet en geen kansschatting. Understat staat per ontwerp NAAST het "
     "eigen model in het kalibratieblok en gaat niet in `my_prob` of `prob_sources` (§2, §4). "
     "HET IS NIET HET SCRIPT EN NIET DE SITE-BEVEILIGING. Dit is iets anders dan de "
     "Cloudflare-challenge van fbref/Forebet/FootyStats/PredictZ: daar antwoordt de site, hier "
     "komt de verbinding niet tot de site. De regel van §3 ('niet omzeilen') geldt hier niet eens "
     "- er is niets om langs te gaan, en een run repareert een netwerkpolicy niet zelf. "
     "WAT ER GEBEURT ALS HET BLIJFT: dan is de redundantie waarvoor Understat sinds 31 aug 2026 "
     "bestaat weg en wordt het kalibratielogboek voor die vijf competities eenarmig. Dat is "
     "verlies aan CONTROLE, niet aan kansinput. Twee dagen is nog geen nieuwe toestand; drie of "
     "vier dagen op rij wel, en dan hoort het in de notificatie en niet alleen hier.")

note("api_football", "plan_limited",
     "3 nov (run A): API_FOOTBALL_KEY is niet gezet en dat is een BESLUIT van de gebruiker van "
     "27 september 2026 ('Dat wil ik niet'), geen storing en geen actiepunt (§3). api_check.py "
     "meldt hem feitelijk en dringt niet meer aan. De kanskant kwam vandaag volledig van Fotmob. "
     "Blijft in de prob_sources-lijsten van coverage.json staan met status plan_limited, zodat "
     "hij meedoet als er ooit toch een plan komt.")

note("pinnacle", "ok",
     "3 nov (run A): Pinnacle stond in de bulk-respons van beide competities, met 30 events in de "
     "responsen. 1X2-oordeel voor ZESTIEN van de achttien duels (de twee NONE-duels Atletico "
     "Madrid - Bayern Munchen en LASK - Slovan Bratislava niet, want daar is geen eigen 1X2 om "
     "naast te zetten) met een marge van 3,0 tot 3,9% - scherper dan de 6 tot 10% van de rest, "
     "zoals §3 Stage 5 stap 2 beschrijft. Gemiddelde absolute afstand van het eigen model tot "
     "Pinnacle's de-vigde 1X2: 5,25 pp over zestien duels. Totalenoordeel voor alle zestien "
     "(duel, lijn)-paren, push-gecorrigeerd. "
     "DE TWEE GROOTSTE AFWIJKINGEN VAN DE DAG ZITTEN OP DE TWEE GEPUBLICEERDE UNDERS, en dat is "
     "de scherpste waarschuwing die deze run heeft. Bodo/Glimt - Lille: eigen P(Under 3.25) "
     "70,3% tegen 51,2% bij Pinnacle, +19,11 pp. Barcelona - Aston Villa: eigen P(Under 4.0) "
     "62,7% tegen 45,4%, +17,35 pp. Over alle zestien paren staat de eigen P(Under) gemiddeld "
     "+3,02 pp boven Pinnacle en bij 9 van de 16 erboven, dus deze twee zijn uitschieters in een "
     "scheefstand en niet die scheefstand zelf. Op het 1X2 wijst het dezelfde kant op: bij "
     "Bodo/Glimt geeft Pinnacle de thuisploeg 53,4% en het model 39,7% (-13,70 pp), bij Barcelona "
     "76,4% tegen 58,2% (-18,16 pp). Noteer dat naast de bets en niet erin (§2): Pinnacle is "
     "andermans oordeel, geen kansinput.")

note("settling", "ok",
     "3 nov (run A): settling.DayIndex besliste over acht openstaande picks en achttien "
     "schaduwrijen op de status van de bron en niet op de klok. ALLES is afgewikkeld; er bleef "
     "geen enkele rij open. Picks 4 gewonnen / 4 verloren, schaduwrijen 9 gewonnen / 7 verloren / "
     "2 VOID. "
     "DIE TWEE VOIDS ZIJN DE VONDST VAN DEZE STAP EN GEEN UITSLAG. Tenerife - FC Andorra "
     "(LaLiga2, 2 nov) staat bij Fotmob op `finished = true` met `scoreStr` 2-2 en `reason.long` "
     "= **Abandoned**: het duel is GESTAAKT en heeft de 90 minuten niet gehaald. §0 en §6d "
     "rekenen af op de stand NA 90 MINUTEN, en een tussenstand van een gestaakt duel is die stand "
     "niet - precies wat de oude 12-uursmarge van voor 3 september moest voorkomen. `finished = "
     "true` zegt alleen dat je MAG afwikkelen, niet dat er een uitslag is. Zonder deze controle "
     "waren twee schaduwrijen van Run B (1 en 2 nov, beide failed_gate = context, 1X2 op Andorra "
     "@3,78 en @3,499) als VERLOREN geboekt - twee onware rijen in de `context`-reeks, die op 115 "
     "afgewikkelde gevallen staat. "
     "DE CONTROLE STAAT NU IN EEN RUNSCRIPT EN HOORT IN `scripts/settling.py`. "
     "`ra_nov03_settle.py` heeft een `abandoned()`-functie op `reason.long` (abandoned, "
     "postponed, cancelled, awarded, afgebroken, uitgesteld). Zolang die in tmp-run/ staat, doet "
     "de volgende run hem alleen als zij hem overneemt - dezelfde reden waarom de aliastabel op "
     "5 oktober van tmp-run/ra_names.py naar scripts/teamnames.py is verhuisd (§3 Stage -2). Alle "
     "26 andere rijen van vandaag stonden op reason 'Full-Time' en zijn normaal afgerekend; de "
     "controle is per rij gedraaid en niet alleen op de twee die opvielen.")

note("notes_bet_beide", "gerepareerd",
     "3 nov (run A): de `notes`-tekst bij een gepubliceerde pick kon ONWAAR zijn over de pick "
     "zelf. `bet_beide = False` heeft DRIE standen - (a) de lat op geen van beide schalen halen, "
     "(b) hem RUW wel en herijkt niet, (c) hem HERIJKT wel en ruw niet - en de tekst had er twee: "
     "(b) en 'al het andere'. Stand (c) kwam vandaag voor het eerst voor bij een GEPUBLICEERDE "
     "bet (Barcelona - Aston Villa, Under 4.5: herijkt +16,23 pp boven de LIGHT-lat van 16,0, ruw "
     "+15,39 pp eronder) en kreeg daardoor de tekst van (a): 'deze selectie haalt haar lat op "
     "GEEN van beide schalen en is op rangorde gepubliceerd, niet op een gevonden voordeel'. Dat "
     "is onwaar: hij haalt zijn lat op de schaal waarop gepubliceerd wordt (§1, §5a: 'vertrouw de "
     "vlag') en staat op zijn eigen voordeel in de lijst, niet op rangorde. "
     "STAND (c) BESTAAT SINDS 20 SEPTEMBER 2026, toen `recalibrate.observations()` naar de "
     "ongeselecteerde ijksteekproef van data/calibration.jsonl ging. Sindsdien VERHOOGT de fit "
     "een kans over vrijwel de hele speelbare band (vandaag a=1,026, b=+0,017: +0,8 pp op 70%) in "
     "plaats van hem te verlagen, en dan kan een selectie de herijkte lat halen en de ruwe net "
     "niet. §5a zegt dat met zoveel woorden en noemt `bet_beide` de vlag die dat moet opvangen - "
     "maar de vlag is EEN BIT VOOR DRIE STANDEN, en de tekst eromheen las hem als twee. De drie "
     "zijn alleen uit `failed_gate` EN `failed_gate_ruw` samen te lezen; de tekst doet dat nu. "
     "HET FAALDE STIL, en dat is waarom dit de bevinding van de run is. ledger.py validate groen "
     "(519 picks geldig), progress.py verify groen, de pick geldig volgens het schema, de pagina "
     "rendert. Dezelfde faalvorm als calibration.py settle (§6b-5c, elf dagen), het Serie B-id, "
     "promotion.match_tier en de toplist-dagranglijst van gisteren - en pijnlijk precies: de "
     "tekst van gisteren KREEG zijn tweede tak als reparatie voor Lille - Lens, en daarbij is de "
     "derde stand niet opgemerkt. "
     "WAT HET NIET IS: geen wijziging in welke bets er worden gepubliceerd. De rekenregels, de "
     "poorten en de rangorde zijn ongemoeid.")

note("marktvorm_lijn", "gerepareerd",
     "3 nov (run A): de frequentietelling van §4 ('Hoe vaak ging deze markt eerder op?') las de "
     "doelpuntenlijn uit een tabel met VIER ingangen (Over 3, Under 3, Under 3.5, Over 2.5) en "
     "gaf voor al het andere stil 2,5 terug. Barcelona - Aston Villa staat vandaag op UNDER 4.5, "
     "dus de telling zou onder een bet op 4,5 doelpunt de frequenties van 2,5 doelpunt hebben "
     "gezet - een getal dat niets met de bet te maken heeft, zonder foutmelding. De lijn wordt nu "
     "uit de selectie GELEZEN. "
     "HET VERSCHIL IS GROOT GENOEG OM DE LEZING TE DRAAIEN: op 2,5 doelpunt staat Barcelona dit "
     "seizoen op 3 van 3 (100%) en vorig seizoen op 10 van 12 (83%); op de werkelijke lijn van "
     "4,5 is dat 3 van 3 (100%) en 5 van 12 (42%). De brede reeks gaat van 'spreekt de bet hard "
     "tegen' naar 'staat dichter bij de bet dan bij de tegenspraak'. "
     "DEZELFDE FAALVORM ALS DE BEKERBASIS VAN 30 OKTOBER: een telling die een leeg of verkeerd "
     "blok geeft zonder te klagen, bij precies de markt waar §4 de frequenties het hardst eist.")

H["last_run_bevinding"] = (
    "De `notes`-tekst bij een gepubliceerde pick kon ONWAAR zijn over die pick. `bet_beide = "
    "False` heeft drie standen en de tekst had er twee; de derde - herijkt boven de lat, ruw "
    "eronder - kwam vandaag voor het eerst bij een gepubliceerde bet voor (Barcelona - Aston "
    "Villa, Under 4.5) en kreeg de tekst van 'haalt hem nergens'. Het faalde stil: validate "
    "groen, verify groen, schema geldig, pagina rendert, en het enige dat niet klopte was dat de "
    "pick zichzelf te laag aansloeg. Pijnlijk precies: de tweede tak van die tekst IS de "
    "reparatie van gisteren (Lille - Lens), en daarbij is de derde stand niet opgemerkt. De tekst "
    "heeft nu drie takken, op `failed_gate` en `failed_gate_ruw` samen. Daarnaast twee kleinere "
    "reparaties van dezelfde soort: `abandoned()` in de afwikkeling (een gestaakt duel is geen "
    "uitslag - twee schaduwrijen stonden op het punt als verloren te worden geboekt) en de "
    "doelpuntenlijn van de frequentietelling, die uit de selectie wordt gelezen in plaats van uit "
    "een tabel met vier ingangen.")
H["updated"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\nsource-health.json bijgewerkt.")

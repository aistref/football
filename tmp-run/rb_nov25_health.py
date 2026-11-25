"""Run B, 25 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Zes dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **De kleinste runlijstdag van de maand**: TWEE van de zeventien competities spelen, met vijf
   duels; de woensdagcap van 40 bindt niet.
2. **GEEN van de 58 selecties haalt zijn eigen lat.** Beide gepubliceerde regels komen volledig
   op rangorde (§5b) — regel 1 mist de FULL-lat met 0,44 pp, regel 2 de LIGHT-lat met 3,89 pp.
3. **Regel 2 is een LIGHT-Under en is dus door GEEN ENKELE rem op de doelpuntenkant getoetst** —
   `unders.TIERS = ("FULL",)` sinds het besluit van de gebruiker van 12 okt 2026. Hetzelfde geval
   als Atalanta – Venezia (12 okt) en Lillestrøm – Molde (11 okt).
4. **Poort 7 bijt voor het eerst sinds 17 november**: drie selecties tegengehouden, alle drie op
   de uitkant van Pisa – Modena; de poort ging op de uitkant van twee van de vijf duels dicht.
5. **Pinnacle is het met regel 2 het meest oneens van alle vier de doelpuntenparen** (+7,01 pp),
   terwijl de 1X2-afstand met gemiddeld 2,69 pp de kleinste van de maand is.
6. **Het shallow-clone-alarm van Stage -2 deed zich opnieuw voor**: 89 van 101 takken leken eigen
   commits te hebben, na `--unshallow` nul van 101.
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
    print(f"{key:34} {status:38} {detail[:70]}")


note("fotmob", "ok",
     "25 nov (run B): daglijsten 25 en 26 nov opgehaald (133 en 75 wedstrijden over 51 en 28 "
     "competities); idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare "
     "stand, AFSLUITCODE 0 - Serie B staat op het echte id 86 met 20 ploegen. Standen van BEIDE "
     "spelende competities geleverd, beide seizoenen, en beide HEBBEN xG. De vijf competities "
     "ZONDER xG (Czech First League 122, Croatian HNL 252, Hungarian NB I 212, Romanian "
     "SuperLiga 189, Keuken Kampioen Divisie 111) spelen vandaag ALLE VIJF niet, dus er is geen "
     "enkel duel dat op doelpunten-als-sterktemaat moet draaien. Context voor alle 5 duels in "
     "een keer opgehaald, NUL fouten; datarijkdom tussen 5,0 en 7,5. context.check_venue sloeg "
     "bij GEEN van de 5 duels aan - alle vijf in het eigen stadion van de thuisploeg. "
     "lineupType stond op alle vijf de duels op 'lastStarting11' en op geen enkel duel op "
     "'confirmed'; de run draait om 03:05 NL en dan is er nergens een opstelling bevestigd.")

note("the_odds_api", "ok",
     "25 nov (run B): api_check.py meldt 46 actieve voetbalcompetities en 18969 credits over, "
     "1031 verbruikt deze maand. 33 van de 34 sportkeys van de repo actief; NIET ACTIEF is "
     "alleen Ligue 2 (soccer_france_ligue_two). VIJF actieve sportkeys die de repo niet kent: "
     "soccer_brazil_serie_b, soccer_england_efl_trophy, soccer_germany_liga3, "
     "soccer_sweden_superettan en soccer_uefa_nations_league - geen van die vijf staat op een "
     "runlijst, dus het is een aantekening en geen gat. suggest_cap(18969, 6) gaf plafond 1579; "
     "BEIDE spelende competities zijn inkoopbaar en kregen de bulkroute (h2h+spreads+totals, 3 "
     "credits elk = 6), en vier duels met kandidaat-edge kregen in ronde twee BTTS (1 elk = 4). "
     "TOTAAL 10 van 1579, 18959 over en 1041 verbruikt deze maand. MARKTBALANS GEHAALD: 2 van de "
     "2 inkoopbare competities kregen zowel een uitkomstmarkt als een doelpuntenmarkt, en over "
     "de hele run 20 selecties op een doelpuntenmarkt (12 O/U + 8 BTTS) tegen 38 op een "
     "uitkomstmarkt (16 AH + 12 1X2 + 8 DNB + 2 DC). Er is vandaag GEEN competitie die op het "
     "gratis BetExplorer-marktgemiddelde moet draaien. Beste prijs tegen dat gemiddelde: +4,72% "
     "(Atletico-MG - Corinthians) tot +6,82% (Pisa - Modena) per duel.")

note("betexplorer", "ok",
     "25 nov (run B): fixturepagina's van alle 17 competities van de runlijst opgehaald, nul "
     "fouten en geen enkele lege lijst (de stille faalmodus van een verkeerde slug deed zich "
     "niet voor). De bevestigingscontrole van §1 (Fotmob-daglijst naast de "
     "BetExplorer-fixturepagina, per competitie) staat op 17 VAN DE 17 EENS, 5 duels tegen 5, "
     "inclusief de VIJFTIEN competities die vandaag GEEN WEDSTRIJD hebben (0 tegen 0, met voor "
     "elk de eerstvolgende ronde erbij: English League One pas 1 dec, Serie B zelf pas 4 dec). "
     "Dat is de controle die juist op de stille competities moet draaien, want een fout id geeft "
     "geen foutmelding maar nul wedstrijden (prompts/run-b.md). Let op: voor Serie A (BRA) geeft "
     "de fixturepagina 10 rijen met 0 als 'vandaag' gemarkeerd, omdat het duel om 20:00 "
     "Braziliaanse tijd op 25 nov begint en dat in de NL-notatie 00:00 op 26 nov is; de "
     "venstercontrole van dit script rekent met UK-tijd en vond het duel wel.")

note("teamnames", "ok",
     "25 nov (run B): geen nieuwe naamkoppeling nodig. 'Atletico Mineiro' bij The Odds API tegen "
     "'Atletico-MG' bij Fotmob koppelde zonder tussenkomst; de gepubliceerde selectienaam volgt "
     "de bookmaker ('DNB - Atletico Mineiro'), zoals §1a voorschrijft - noem de bet zoals hij "
     "bij de bookmaker heet.")

note("understat", "niet_bevraagd",
     "25 nov (run B): niet opgevraagd. Understat dekt PL, La Liga, Bundesliga, Serie A en Ligue "
     "1 - geen enkele competitie van de Run B-runlijst. Dat is geen storing maar de afbakening "
     "van §4.")

note("api_football", "niet_gezet",
     "25 nov (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker (27 sep "
     "2026) en geen storing, geen gat en geen actiepunt (§3). De onafhankelijke kansinput komt "
     "van Fotmob, dat vandaag alles leverde voor beide spelende competities; de uitzondering van "
     "§3 punt 3 - melden zodra Fotmob niet meer levert - is niet aan de orde.")

note("settling", "niets_afwikkelbaar_en_drie_picks_terecht_open",
     "25 nov (run B): ledger.py open en shadow.py open gaven NUL afwikkelbare regels. Drie picks "
     "staan open en alle drie terecht. Twee zijn van Run A van VANDAAG (Paris Saint-Germain - "
     "Roma Under 3.5 en Atletico Madrid - Viking Under 4, aftrap 21:00 NL) en moeten nog "
     "beginnen. De derde is de MLS-pick van Run B van GISTEREN - San Jose Earthquakes - Houston "
     "Dynamo FC Over 2.5 - en die LIEP bij het begin van deze run werkelijk nog: Fotmob zet "
     "finished niet op true en meldt 0,1 uur na de aftrap. §0 zegt dan letterlijk wachten; de "
     "terugval op de klok (SETTLE_FALLBACK_HOURS = 2,0) geldt UITSLUITEND wanneer er geen "
     "bronstatus te krijgen was, en die is er hier wel. Elf schaduwrijen van Run A van vandaag "
     "staan om dezelfde reden open. Er is daarmee GEEN afwikkelingsreflectie te schrijven (§3 "
     "Stage 0, 12 okt 2026) en dat is een lege dag en geen overgeslagen stap.")

note("poort_9_doelpunten_onder", "reeks_53_rem_werkt_maar_raakte_de_bet_van_vandaag_niet",
     "25 nov (run B): poort 9 hield vandaag NUL selecties tegen EN heeft de gepubliceerde Under "
     "NIET getoetst - het omgekeerde van gisteren. Regel 2 (Pisa - Modena Under 2.5) staat op "
     "data_tier = LIGHT en valt daarmee buiten het bereik van de rem: unders.TIERS = ('FULL',) "
     "sinds het besluit van de gebruiker van 12 okt 2026 ('Twee hoeft nog niet op de zwakke "
     "data; eerst kijken wat deze rem doet'). Dit is dus EXACT hetzelfde geval als Atalanta - "
     "Venezia (12 okt) en Lillestrom - Molde (11 okt): een LIGHT-Under die de rangorde van §5b "
     "haalt en door geen enkele rem op de doelpuntenkant is gegaan. Geen omissie maar die "
     "keuze. De twee FULL-Unders van vandaag (Padova - Sampdoria, Under 2.5 @1,76 op +5,31 pp en "
     "Under 2.25 @1,98 op +4,69 pp) vielen al eerder af, op poort 6, dus er was ook geen "
     "FULL-kandidaat in de band 8-10 pp waar de rem bindt. De reeks blijft op 53 kandidaten, 52 "
     "afgewikkeld, 34,6% trefkans, -18,65u = -35,9% rendement: de rem bespaart geld op de "
     "categorie waar hij werkt en heeft de ~30 van §6d ruim gehaald. EEN RUN VERZET POORT 9 NIET "
     "OP EIGEN INITIATIEF EN BREIDT HEM NIET UIT NAAR LIGHT (§1h punt 3).")

note("poort_7_context", "bijt_voor_het_eerst_sinds_17_nov",
     "25 nov (run B): poort 7 hield DRIE selecties tegen, de eerste sinds 17 november op deze "
     "runlijst. Hij ging dicht op de UITKANT van twee van de vijf duels: Sampdoria mist 51% van "
     "zijn selectiewaarde tegen 11% bij Padova (Esposito, Di Pardo, Verschaeren) en Modena 34% "
     "tegen 4% bij Pisa (Zampano, Tonoli, Caso). Bij Pisa - Modena kostte dat drie selecties die "
     "anders waren doorgerekend: AH Modena +0,25 @1,81 (+4,25 pp), 1X2 Modena wint @3,17 "
     "(+3,62 pp) en DNB Modena @2,14 (+3,11 pp). Bij Padova - Sampdoria waren er geen "
     "uitkant-kandidaten die zo ver kwamen. LET OP DE SPIEGEL: de gepubliceerde Under van Pisa - "
     "Modena heeft side = None en daar staat poort 7 per ontwerp ALTIJD open (§1c, 'er is geen "
     "kant om te benadelen, en in welke richting context een totaal verschuift is zonder meting "
     "niet te zeggen'). De reeks `context` staat op 157 kandidaten, 152 afgewikkeld, 34,2% "
     "trefkans, -35,37u = -23,3% - de duidelijkst besparende van alle negen poorten.")

note("pinnacle_vergelijking", "let_op",
     "25 nov (run B): Stage 5 stap 2. Op de doelpuntenkant vier toetsbare (duel, lijn)-paren, en "
     "DE GROOTSTE AFWIJKING VAN ALLE VIER IS REGEL 2: Pisa - Modena op lijn 2,50, eigen "
     "P(Under) 55,5% tegen 48,5% bij Pinnacle (+7,01 pp, Pinnacle-marge 3,2%). Over alle vier "
     "gemiddeld +3,39 pp op de Under-kant met 3 van 4 erboven; uitgesplitst +6,25 pp over de "
     "twee zuivere halve lijnen (2 van 2 erboven) en +0,53 pp over de twee met push. Op de 1X2 "
     "vier toetsbare duels met een gemiddelde absolute afstand van 2,69 pp bij een gemiddelde "
     "Pinnacle-marge van 3,57% - DE KLEINSTE GEMIDDELDE AFSTAND VAN DEZE MAAND. Bij regel 1 is "
     "het verschil met +4,14 pp het grootste van de vier maar in absolute zin klein: eigen model "
     "44,4% voor Atletico-MG tegen 40,2% bij Pinnacle. Mantova - Arezzo had geen eigen 1X2 om "
     "tegen te leggen (tier NONE). DEZE GETALLEN GAAN NIET IN my_prob (§2); ze horen in de "
     "vergelijking.")

note("goalbias_selectie", "onveranderd_scherp",
     "25 nov (run B): margins.py goalbias staat op 2478 doorgerekende duels. Het MODEL staat op "
     "+0,020 doelpunt per duel (z = +0,56): de lambdas kloppen. De SELECTIE niet - over de 150 "
     "duels waar werkelijk een Under is gespeeld vielen er 0,677 doelpunt per duel MEER dan "
     "verwacht (z = +4,99; 24 nov: +4,95 over 148, 23 nov: +4,95 over 148). De spiegel staat er "
     "ook: over de 83 gespeelde Overs vielen er 0,374 doelpunt per duel MINDER dan verwacht "
     "(z = -1,85). Regel 2 van vandaag staat op de Under-kant, dus op de kant waar de selectie "
     "tot nu toe de verkeerde kant op uitvalt - en vandaag ZONDER dat poort 9 ernaar heeft "
     "gekeken, want de regel staat op LIGHT. De VORM op deze lijn: P(Under 2.5) voorspeld 42,3% "
     "tegen werkelijk 40,9% over 2478 duels, 1,4 pp te hoog. Deze twee regels mogen NOOIT bij "
     "elkaar worden opgeteld en geen van beide is een reden om op een enkele dag een lat te "
     "verzetten (§6d).")

note("divisiekaart_promovendi", "een_structureel_gat_kostte_een_duel",
     "25 nov (run B): DRIE van de vijf duels hebben een ploeg zonder stand in het vorige seizoen "
     "en gingen langs de omrekening van §4; TWEE lukten en EEN kwam op data_tier = NONE. "
     "Cremonese en Pisa zijn degradanten uit de Serie A (TIER1-route) en zijn WEL om te rekenen "
     "- beide duels komen daardoor op LIGHT. Arezzo niet: ONDER 'Serie B (ITA)' KENT "
     "promotion.TIER2 GEEN DIVISIE, de Serie C ligt eronder maar is niet gemeten, dus Mantova - "
     "Arezzo is het enige duel van vandaag zonder kansbron. LET OP DE FOUTMELDING, die de "
     "oorzaak verkeerd laat lezen: hij zegt \"degradant: 'Arezzo' staat niet in de stand van "
     "Serie A (ITA) 2025/2026\" en noemt dus alleen de TIER1-tak, terwijl Arezzo juist van "
     "ONDEREN komt. Exact dezelfde misleidende melding als bij de Spaanse Primera Federacion "
     "(notitie van 4 okt 2026) en als bij Benevento, Ascoli en Vicenza op 24 nov. Dit is een "
     "STRUCTUREEL gat: de Serie B krijgt elk seizoen promovendi uit die divisie. Het tweede gat "
     "van gisteren (Serie A (BRA) in geen van beide kaarten) bond vandaag niet - Atletico-MG en "
     "Corinthians staan beide in de stand van 2025.")

note("stage_min_2_shallow_clone", "vals_alarm_opnieuw_voorgekomen_en_opgelost",
     "25 nov (run B): de container kreeg de repo opnieuw als ONDIEPE kloon - "
     "`git rev-parse --is-shallow-repository` gaf true, 58 commits lokaal, knip op 15 nov 2026. "
     "In die stand toonden 89 VAN DE 101 takken 'eigen' commits, tot 730 stuks, en gaf "
     "`git merge-base` niets terug: exact het valse alarm dat §3 Stage -2 beschrijft. Na "
     "`git fetch --unshallow origin` (797 commits) heeft GEEN ENKELE tak nog een commit die HEAD "
     "mist - 101 van 101 op nul. HEAD liep bij het begin van deze run gelijk met origin/main "
     "(4254f58, de afronding van Run A van vandaag). picks.jsonl bevatte geen openstaande pick "
     "van een run die op een andere tak nooit is afgewikkeld. Dit is de derde keer dat dit "
     "expliciet is vastgelegd (20 aug, 25 nov) en de reden dat de unshallow-stap VOOR de "
     "takkenvergelijking hoort en niet erna.")

# --- het gedateerde snapshotblok van deze run (zie _merge_note: branchaudit vergelijkt hierop) ---
prev_b = H.get("last_run_run_b")
if prev_b and prev_b.get("date") != "2026-11-25":
    hist = prev_b.pop("history", [])
    H["last_run_run_b"] = {"history": ([prev_b] + list(hist))[:8]}
else:
    H["last_run_run_b"] = {"history": (H.get("last_run_run_b") or {}).get("history", [])}

H["last_run_run_b"].update({
    "run": "B", "date": "2026-11-25",
    "matches_in_window": 5, "analysed": 4, "truncated": 0, "bets": 2,
    "qualified_not_published": 0,
    "credits": "10 van een plafond van 1579 (6 bulk voor 2 competities + 4 BTTS); 18959 over, "
               "1041 gebruikt deze maand na deze run",
    "note": "TWEE van de zeventien competities spelen, met vijf duels in het inzetvenster: Serie "
            "B (4) en Serie A (BRA) (1). Dat is de KLEINSTE runlijstdag van november. De "
            "woensdagcap van 40 bindt NIET, er is niets afgekapt. Beide spelende competities "
            "hebben xG bij Fotmob EN een sportkey bij The Odds API. Vier duels leverden "
            "kandidaten op; een kwam op data_tier = NONE (Mantova - Arezzo, geen gemeten divisie "
            "onder Serie B). 58 selecties doorgerekend over alle zes de markten; 35 (60%) "
            "sneuvelden op poort 5, 15 op de edge-afkapping, 3 op de koersband, 3 op poort 7 en "
            "2 op poort 6. Poort 8 en poort 9 hielden NUL tegen. GEEN ENKELE selectie haalde "
            "zijn eigen lat, dus beide gepubliceerde regels komen volledig op rangorde (§5b). De "
            "controle langs drie wegen op de vijftien stille competities: idcheck.py 33/33 met "
            "afsluitcode 0, BetExplorer 17 van 17 eens (5 tegen 5 duels), runwindow.py voor het "
            "venster.",
    "bevinding": "GEEN VAN DE TWEE REGELS HAALT ZIJN EIGEN LAT - anders dan gisteren, toen "
                 "Bradford City - Barnsley met +11,65 pp boven een verzwaarde lat van 10,0 "
                 "uitkwam. Regel 1 (Atletico-MG - Corinthians DNB Atletico Mineiro @1,75, FULL, "
                 "+7,56 pp bij een lat van 8,0) mist met 0,44 pp; regel 2 (Pisa - Modena Under "
                 "2.5 @2,0388, LIGHT, +12,11 pp bij een lat van 16,0) met 3,89 pp. HET PUNT DAT "
                 "VOORAAN HOORT: regel 2 is een LIGHT-Under en is daarmee door GEEN ENKELE rem "
                 "op de doelpuntenkant getoetst, want unders.TIERS = ('FULL',) sinds het besluit "
                 "van 12 okt 2026. Dat terwijl de Under-kant van de selectie op z = +4,99 staat "
                 "over 150 gespeelde Unders en Pinnacle het met deze specifieke lijn het meest "
                 "oneens is van alle vier de toetsbare doelpuntenparen (+7,01 pp). De "
                 "marktvormtelling spreekt hem ook tegen: Pisa bleef in een van zijn zes "
                 "thuisduels onder 2,5 (23 doelpunten in zes wedstrijden, 3,83 per duel) en "
                 "Modena in twee van zijn zes uitduels. Wat er voor pleit is de verdediging van "
                 "Modena (tien tegendoelpunten in twaalf duels, de beste van de Serie B) en de "
                 "onderlinge historie (2,2 doelpunten per duel over vijf ontmoetingen, drie "
                 "ervan op twee of minder). TWEEDE BEVINDING: poort 7 bijt voor het eerst sinds "
                 "17 november, met drie tegengehouden selecties op de uitkant van Pisa - Modena.",
    "sources_deze_run": {
        "fotmob": "ok - daglijsten 25 en 26 nov, standen van 2 competities in beide seizoenen, "
                  "context voor 5 van 5 duels zonder fout, idcheck 33/33 afsluitcode 0",
        "the_odds_api": "ok - 46 actieve competities, 18969 over bij de start, 10 credits "
                        "verbruikt (6 bulk + 4 BTTS), 18959 over",
        "betexplorer": "ok - 17 van 17 fixturepagina's, geen lege lijst, 5 tegen 5 duels eens",
        "understat": "niet bevraagd - dekt geen enkele competitie van deze runlijst (§4)",
        "api_football": "niet gezet - besluit van de gebruiker van 27 sep 2026, geen gat",
        "pinnacle": "ok - 17 events met 1X2 en totalen; 4 toetsbare duels en 4 (duel, lijn)-paren",
    },
})

H["last_run"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")

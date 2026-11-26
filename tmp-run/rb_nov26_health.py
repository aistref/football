"""Run B, 26 nov 2026 — `data/source-health.json` bijwerken (§6b-3).

Zes dingen die hier vastgelegd worden en die een volgende run anders opnieuw moet uitzoeken:

1. **TWEE van de zeventien competities spelen, met twee duels** — en van die twee is er maar ÉÉN
   door te rekenen. Dat is de kleinste runlijstdag sinds het begin van deze reeks.
2. **NUL regels, en de ondergrens van §5b is de bindende regel** — niet de drempel. De sterkste
   selectie met alle zeven overige poorten open staat op +0,83 pp; `toplist._publiceerbaar` eist
   3,0 pp op FULL.
3. **NUL schaduwrijen.** Geen kandidaat haalt de NEAR-drempel, dus `shadow.py collect` voegt niets
   toe en de "Net niet"-tabel staat leeg (uitgeschreven, §5 19 nov 2026).
4. **Poort 5 bindt op de sterkste kandidaat met twee duizendsten** — en op elf van de vijftien
   selecties van het duel.
5. **Het shallow-clone-alarm van Stage -2 deed zich opnieuw voor, en het heeft deze run bijna
   misleid**: vóór `--unshallow` leken 88 van de 101 takken GEEN gemeenschappelijke voorouder met
   `main` te hebben; erna delen alle 101 geschiedenis en hebben alle 101 nul eigen commits.
6. **`branchaudit.py` geeft 16 meldingen die alle zestien bij nader inzien géén verlies zijn** —
   zie `stage_min_2_branchaudit`. Dat is boekhouding die elke run opnieuw wordt gedaan.
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
     "26 nov (run B): daglijsten 26 en 27 nov opgehaald (78 wedstrijden over 30 competities, en "
     "155 over 91). idcheck.py gaf voor alle 33 fotmob_id's uit coverage.json een bruikbare "
     "stand, AFSLUITCODE 0 - Serie B staat op het echte id 86 met 20 ploegen. Standen van BEIDE "
     "spelende competities geleverd in beide seizoenen, en beide HEBBEN xG (League One 108: 24 "
     "ploegen in 2025/2026 met 46 speeldagen, 16 gespeeld in 2026/2027; Serie A BRA 268: 20 "
     "ploegen, 38 speeldagen vorig en 37 gespeeld). De vijf competities ZONDER xG (Czech First "
     "League 122, Croatian HNL 252, Hungarian NB I 212, Romanian SuperLiga 189, Keuken Kampioen "
     "Divisie 111) spelen vandaag geen van vijf. Context voor beide duels in een keer opgehaald, "
     "NUL fouten; datarijkdom 7,0 en 5,0. context.check_venue sloeg bij geen van beide aan - "
     "beide in het eigen stadion van de thuisploeg (Club Doncaster Sports Village, MorumBIS). "
     "lineupType stond op beide duels op 'lastStarting11' en op geen enkel duel op 'confirmed'; "
     "de run draait om 04:05 NL en dan is er nergens een opstelling bevestigd.")

note("the_odds_api", "ok",
     "26 nov (run B): api_check.py meldt 45 actieve voetbalcompetities en 18890 credits over, "
     "1110 verbruikt deze maand. 33 van de 34 sportkeys van de repo actief; NIET ACTIEF is "
     "alleen Ligue 2 (soccer_france_ligue_two). VIER actieve sportkeys die de repo niet kent: "
     "soccer_brazil_serie_b, soccer_germany_liga3, soccer_sweden_superettan en "
     "soccer_uefa_nations_league - geen van die vier staat op een runlijst, dus het is een "
     "aantekening en geen gat. suggest_cap(18890, 5) gaf plafond 1887; BEIDE spelende "
     "competities zijn inkoopbaar en kregen de bulkroute (h2h+spreads+totals, 3 credits elk = "
     "6). BTTS is NIET opgevraagd, want geen enkel duel toonde een kandidaat-edge en §1a stap 2 "
     "vraagt die tweede ronde pas dan. TOTAAL 6 van 1887, 18884 over en 1116 verbruikt deze "
     "maand. MARKTBALANS GEHAALD OP DE INKOOP: 2 van de 2 inkoopbare competities kregen zowel "
     "een uitkomstmarkt (h2h + spreads) als een doelpuntenmarkt (totals). Let op dat de prijzen "
     "voor Serie A (BRA) zijn gekocht voordat de tier bekend was; dat duel kwam daarna op NONE "
     "uit, dus die 3 credits leverden geen doorgerekende selectie op. Dat is de volgorde van "
     "§1a en geen fout om recht te zetten.")

note("betexplorer", "ok",
     "26 nov (run B): 17 van de 17 fixturepagina's van de runlijst geleverd, geen lege lijst en "
     "geen verhuisde slug. De tweede-bronbevestiging van §1 is VOLLEDIG EENS met Fotmob: 17 van "
     "17 competities hetzelfde aantal duels in het inzetvenster, en beide bronnen komen op 2 "
     "duels uit (English League One 1, Serie A BRA 1). Het 1X2-marktgemiddelde over 5 boeken is "
     "voor Doncaster - Huddersfield geleverd (4,32 / 4,02 / 1,68) en wordt gebruikt voor poort 8 "
     "en het kalibratielogboek, niet om op te spelen.")

note("teamnames", "ok",
     "26 nov (run B): beide duels koppelden zonder handwerk aan de stand van het vorige "
     "seizoen; Remo is de enige ploeg die niet in de stand staat en dat is terecht - hij is "
     "promovendus uit de Serie B (zie divisiekaart_promovendi).")

note("understat", "niet_bevraagd",
     "26 nov (run B): Understat dekt alleen Premier League, La Liga, Bundesliga, Serie A en "
     "Ligue 1 (§4) en dus geen enkele competitie van deze runlijst. Niet bevraagd is hier de "
     "juiste uitkomst en geen storing; voor Run B is Fotmob de enige xG-bron.")

note("api_football", "niet_gezet",
     "26 nov (run B): API_FOOTBALL_KEY ontbreekt. Dat is een BESLUIT van de gebruiker van 27 sep "
     "2026 ('Dat wil ik niet') en geen gat, geen actiepunt en niets voor de notificatie (§3). De "
     "kanskant komt van Fotmob; dat leverde vandaag voor beide spelende competities xG in beide "
     "seizoenen, dus §2 is gedekt. De uitzondering van §3 punt 3 is NIET aan de orde: zou Fotmob "
     "omvallen, dan wordt elk duel NONE en hoort de betaalde bron wel vooraan in de notificatie.")

note("settling", "niets_afwikkelbaar_en_twee_picks_terecht_open",
     "26 nov (run B): ledger.py open en shadow.py open geven beide 'niets klaar om af te "
     "wikkelen'. Run A van vanochtend (±03:00 NL) heeft de vier picks van 25 november al "
     "afgerekend: PSG - Roma Under 3.5 VERLOREN, Atletico Madrid - Viking Under 4 GEWONNEN "
     "(beide Run A), Atletico-MG - Corinthians DNB VOID en Pisa - Modena Under 2.5 GEWONNEN "
     "(beide Run B). De twee openstaande picks zijn de Europa League-regels van Run A van "
     "vandaag (Union St.Gilloise - Lech Poznan en Lyon - Lillestrom, beide Under 3.5); die "
     "trappen vanavond pas af en staan terecht op pending. GEEN pick van voor vandaag staat nog "
     "open, en er is dus ook geen openstaande pick van een run die op een andere tak nooit is "
     "afgewikkeld (§3 Stage -2).")

note("poort_5_tweede_methode", "bindt_op_elf_van_de_vijftien_selecties",
     "26 nov (run B): poort 5 (de twee methodes moeten de markt dezelfde kant op verslaan) is "
     "vandaag de bindende poort op ELF van de vijftien doorgerekende selecties, en ook op de "
     "sterkste van de dag: Doncaster Rovers +0,75 @1,98 (Pinnacle), herijkte edge +2,15 pp, "
     "waar de xG-methode op 50,49% staat tegen een marktkans van 50,51%. Twee honderdsten van "
     "een procentpunt de verkeerde kant op. De splitsmethode staat met 57,80% ruim boven de "
     "markt (+7,29 pp). Dat patroon loopt door het hele duel: op elke kant waar Doncaster de "
     "underdog is zegt de splitsmethode veel meer dan de xG-methode (1X2 thuis +7,24 tegen "
     "-0,14 pp; +1 handicap +4,59 tegen -2,05 pp). De oorzaak staat in de seizoensweging: "
     "Huddersfield staat dit seizoen op 2,073 xG per duel tegen 1,476 vorig seizoen (gewicht "
     "0,652 op het lopende seizoen), en dat tilt de xG-kant van Huddersfield op terwijl de "
     "doelpuntensplits van vorig seizoen dat niet doen. De reeks `tweede_methode` staat op "
     "-2,3% over 334 afgewikkelde kandidaten - de poort bespaart geld, maar met een smalle "
     "marge.")

note("poort_9_doelpunten_onder", "reeks_53_rem_werkt_en_bond_vandaag_niet",
     "26 nov (run B): poort 9 hield vandaag NUL selecties tegen, en dat is niet omdat de rem "
     "losser staat maar omdat geen enkele Under in de buurt van zijn gewone drempel kwam: de "
     "drie Under-lijnen van het duel staan op +0,45, -0,96 en -1,56 pp, dus `edge` is de "
     "bindende poort en niet poort 9 (de verzwaarde lat van 10,0 pp komt pas in beeld boven 8,0). "
     "De reeks zelf staat op 53 kandidaten, 52 afgewikkeld, 18 winnaars, -18,65u = -35,9%: de "
     "slechtste ROI van alle poorten, dus de rem doet aantoonbaar zijn werk. De scheefstand "
     "waarop hij is gebouwd is vandaag opnieuw gemeten en is onveranderd groot: z = +4,92 over "
     "153 gespeelde Unders (+0,661 doelpunt per duel meer dan de eigen lambda zei), tegen z = "
     "+0,46 over alle 2494 doorgerekende duels. Het model staat goed; het is de selectie die "
     "scheef staat.")

note("poort_7_context", "open_op_het_enige_doorgerekende_duel",
     "26 nov (run B): poort 7 stond op BEIDE kanten van Doncaster - Huddersfield open - geen "
     "uitvallers bij beide ploegen (0 van 0), exact gelijke rust (5,2 dagen elk), geen druk "
     "programma. Bij Sao Paulo - Remo zou de poort de THUISKANT hebben GEBLOKKEERD: Sao Paulo "
     "mist 43,0% van zijn selectiewaarde met zeven uitvallers (Wendell geschorst; Rafael Toloi, "
     "Sabino, Marcos Antonio, Domingos Duarte, Nicolas en Aurelio Buta geblesseerd, Sabino en "
     "Duarte voor de rest van het seizoen) tegen 24,6% bij Remo, en heeft 3,0 dagen rust tegen "
     "4,2. Dat verandert niets aan de uitkomst - NONE blijft NONE - maar het contextblok is wel "
     "vastgelegd, want de steekproef van ctxlog.py is de enige weg naar een meting over het "
     "effect van blessures (§1c). Het contextlogboek staat nu op 2605 wedstrijden, 2575 "
     "afgewikkeld; de helling van de modelfout tegen het beschikbaarheidsverschil is -10,8 pp "
     "per eenheid op t = -1,81, dus nog niet aantoonbaar (aantoonbaar vanaf ~11 pp).")

note("pinnacle_vergelijking", "ongewoon_dicht_bij_het_model",
     "26 nov (run B): Stage 5 stap 2. De gemiddelde absolute afstand tussen de eigen xG-kansen "
     "en Pinnacle's de-vigde 1X2 is 1,38 procentpunt op het ene toetsbare duel, bij een "
     "Pinnacle-marge van 4,48%. Dat is de kleinste afstand van de maand. Het model houdt "
     "Huddersfield 1,7 pp minder sterk dan Pinnacle en het gelijkspel 2,1 pp waarschijnlijker. "
     "Op de doelpuntenkant staat het model +2,91 pp BOVEN Pinnacle op de Under-kant van lijn 3,0 "
     "(eigen 53,8% tegen 50,9%) - dezelfde richting als de scheefstand van §6g, en de reden dat "
     "een Under hier niet zonder marge gepubliceerd hoort te worden. Dit getal gaat NIET in "
     "my_prob of prob_sources (§2).")

note("goalbias_selectie", "onveranderd_scherp",
     "26 nov (run B): margins.py goalbias over 2494 doorgerekende duels (25 aug t/m 25 nov). "
     "ALLE DUELS: verwacht 3,042 en werkelijk 3,058 doelpunten per duel, z = +0,46 - het model "
     "klopt. UNDER GESPEELD: 153 duels, verwacht 2,763 en werkelijk 3,425, +0,661 per duel, "
     "z = +4,92. OVER GESPEELD: 83 duels, -0,374 per duel, z = -1,85. Die twee regels mogen "
     "nooit als een getal worden gelezen: de bovenste meet het model, de onderste de selectie. "
     "De vorm van de verdeling schuift nog steeds massa van 2 naar 4-5 doelpunten (-1,1 pp op "
     "twee, +0,6 op vier, +1,0 op vijf), wat elke Under structureel iets te hoog zet, ook zonder "
     "selectie. P(Under 2.5) staat op voorspeld 42,3% tegen werkelijk 41,0%.")

note("margekalibratie", "gelijkspel_drie_procentpunt_te_hoog_sinds_de_shrink_overstap",
     "26 nov (run B): margins.py stats op 2494 duels geeft nergens een uitschieter boven twee "
     "standaardfouten. Op de meetset sinds de shrink-overstap (--since 2026-09-20) staat er WEL "
     "een: het gelijkspel is voorspeld 23,6% en werkelijk 20,6%, -3,0 pp, en dat is de enige "
     "regel met een markering. Dat is relevant voor vandaag, want de sterkste publiceerbare "
     "selectie van de dag WAS een gelijkspel (X @4,52, +0,83 pp) - het model houdt gelijke "
     "spelen structureel iets te waarschijnlijk, en dat de selectie alsnog onder de ondergrens "
     "bleef is dus geen verlies. Op duels met een duidelijke favoriet (n=476 sinds 20 sep) staat "
     "'favoriet wint met 2 of meer' op -4,3 pp zonder markering.")

note("divisiekaart_promovendi", "structureel_gat_bra_kostte_het_tweede_duel",
     "26 nov (run B): Remo staat niet in de Serie A-stand van 2025 en is promovendus uit de "
     "Serie B. `promotion.TIER2` kent voor Brazilie geen divisie en `MEASURED_TIER2_GAP` geen "
     "factor, dus er is niets om hem mee om te rekenen en Sao Paulo - Remo komt op data_tier = "
     "NONE. `prompts/run-b.md` schrijft dat met zoveel woorden voor ('er is geen gemeten factor "
     "voor dat divisiepaar, dus een Braziliaanse promovendus komt eveneens op NONE uit'), dus "
     "dit is de gemeten stand van zaken en geen omissie. Het kostte vandaag HET HALVE "
     "programma: een van de twee duels in het venster. Dat is dezelfde grens die op 25 november "
     "Mantova - Arezzo kostte (geen gemeten divisie onder Serie B) en op 23 oktober Osijek - "
     "Rudes (geen tweede divisie bij Fotmob voor Kroatie).")

note("stage_min_2_shallow_clone", "vals_alarm_opnieuw_voorgekomen_en_het_was_bijna_misleidend",
     "26 nov (run B): de container kreeg de repo opnieuw als ONDIEPE kloon (58 commits lokaal, "
     "`--is-shallow-repository` true). In die stand gaf `git merge-base HEAD <tak>` voor 88 van "
     "de 101 takken NIETS terug, wat eruitzag als 88 takken met een eigen rootcommit en samen "
     "duizenden eigen commits - precies het valse alarm dat §3 Stage -2 beschrijft, maar in de "
     "scherpste vorm die het tot nu toe heeft gehad (het lijkt niet op achterlopende takken maar "
     "op een TWEEDE REPO). Na `git fetch --unshallow origin` staat de geschiedenis op 801 "
     "commits, delen ALLE 101 takken geschiedenis met main en hebben ALLE 101 nul eigen "
     "commits. Er viel dus niets te mergen. LES VOOR DE VOLGENDE RUN: `--unshallow` hoort de "
     "EERSTE handeling van de takkenvergelijking te zijn en niet een controle achteraf; een "
     "uitkomst 'geen gemeenschappelijke voorouder' in een ondiepe kloon betekent niets.")

note("stage_min_2_branchaudit", "zestien_meldingen_en_alle_zestien_geen_verlies",
     "26 nov (run B): branchaudit.py vergelijkt per record op de INHOUD (de controle die §3 "
     "Stage -2 sinds 27 sep eist, omdat '0 eigen commits' alleen iets over de graaf zegt) en "
     "meldt 16 records die op een tak staan en niet op origin/main. Alle zestien zijn nagegaan "
     "en geen van zestien is een verloren meting. (1) picks.jsonl 603, context-log.jsonl 2603, "
     "calibration.jsonl 9256 en coverage.json 339 staan VOLLEDIG op main. (2) VIER shadowrijen "
     "ontbreken: canada---peru, croatia---england, estonia---luxembourg en "
     "switzerland---slovenia van 3 oktober, alle vier in de KALE vorm. Dat zijn exact de vier "
     "rijen die op 7 nov 2026 met opzet zijn verwijderd omdat ze dubbel stonden (een keer via "
     "near_miss en een keer via poort8_geblokkeerd); de versies met de `-p8-0`-suffix staan er "
     "nog en §3 Stage -2 zegt letterlijk: vul ze bij een merge NIET aan. (3) TWAALF leafpaden "
     "van source-health.json ontbreken, en alle twaalf staan in main onder "
     "`last_run_run_b.history[].blok` of `last_run_run_c.detail_history[]` - de ingedikte vorm "
     "die het health-script zelf gebruikt bij het doorrollen. Nagekeken: het blok van 19 nov in "
     "main bevat sources_deze_run met fotmob_daglijsten, fotmob_match_details, "
     "fotmob_league_stats en fotmob_context; het blok van 8 nov bevat `samenvatting` (met de "
     "aantekening dat het op 18 nov uit tak bold-curie-i16v98 is verenigd); en "
     "detail_history van 14 nov bevat betexplorer_saff en betexplorer_kings_cup. BEVINDING: "
     "branchaudit vergelijkt VLAKKE leafpaden en kijkt niet in `blok`, dus deze zestien "
     "meldingen komen elke run terug en elke run moet ze opnieuw uitzoeken. Dat is een stille "
     "kostenpost in de vorm van handwerk, geen risico voor de data.")

# --- het gedateerde snapshotblok van deze run (zie _merge_note: branchaudit vergelijkt hierop) ---
prev_b = H.get("last_run_run_b")
if prev_b and prev_b.get("date") != "2026-11-26":
    hist = prev_b.pop("history", [])
    H["last_run_run_b"] = {"history": ([prev_b] + list(hist))[:8]}
else:
    H["last_run_run_b"] = {"history": (H.get("last_run_run_b") or {}).get("history", [])}

H["last_run_run_b"].update({
    "run": "B", "date": "2026-11-26",
    "matches_in_window": 2, "analysed": 1, "truncated": 0, "bets": 0,
    "qualified_not_published": 0,
    "credits": "6 van een plafond van 1887 (2 bulkaanroepen, geen BTTS); 18884 over, 1116 "
               "gebruikt deze maand na deze run",
    "note": "TWEE van de zeventien competities spelen, met twee duels in het inzetvenster "
            "[08:00 NL 26 nov, 08:00 NL 27 nov): English League One (Doncaster Rovers - "
            "Huddersfield Town, 21:00 NL) en Serie A BRA (Sao Paulo - Remo, 00:00 NL). Dat is de "
            "kleinste runlijstdag van deze reeks, en er is maar EEN duel doorgerekend: Sao Paulo "
            "- Remo komt op data_tier = NONE omdat Remo promovendus uit de Serie B is en er voor "
            "dat Braziliaanse divisiepaar geen gemeten factor bestaat (run-b.md). De "
            "donderdagcap van 40 bindt NIET, er is niets afgekapt. Beide spelende competities "
            "hebben xG bij Fotmob EN een sportkey bij The Odds API. 15 selecties doorgerekend "
            "over alle zes de markten (1X2 3, AH 6, OU 6; DNB en DC hadden geen lijn in de "
            "spreads-respons, BTTS is niet opgevraagd omdat geen duel een kandidaat-edge toonde "
            "- §1a stap 2). Elf van de vijftien sneuvelden op poort 5, de rest op de "
            "edge-afkapping. progress.py verify groen: alle zes markten bij de ene geanalyseerde "
            "wedstrijd, 1 overgeslagen op tier NONE. De controle langs drie wegen op de vijftien "
            "stille competities: idcheck.py 33/33 met afsluitcode 0, BetExplorer 17 van 17 eens "
            "(2 tegen 2 duels), runwindow.py voor het venster. LET OP: op de daglijst van 27 "
            "november staan NEGENTIEN runlijstduels, die alle negentien na 08:00 NL aftrappen en "
            "dus bij de run van morgen horen.",
    "bevinding": "NUL REGELS, EN DE BINDENDE REGEL IS DE ONDERGRENS VAN §5b EN NIET DE DREMPEL. "
                 "Sinds 20 sep 2026 is EDGE_THRESHOLD_FULL een afkapping en geen poort: staan er "
                 "minder selecties boven de lat dan er regels in de lijst passen, dan bepaalt de "
                 "rangorde de lijst (45 van de 103 picks sinds 1 november staan onder hun eigen "
                 "lat, tot 3,41 pp bij FULL). Maar die rangorde heeft een ondergrens - "
                 "`toplist._publiceerbaar` eist de NEAR-drempel van 3,0 pp op FULL, omdat de "
                 "eerste herdraai onder §5b anders selecties met een NEGATIEVE edge publiceerde. "
                 "De sterkste selectie met alle zeven overige poorten open is het GELIJKSPEL in "
                 "Doncaster - Huddersfield (X @4,52 bij Pinnacle, kans 22,96%, +0,83 pp) en die "
                 "staat 2,17 pp onder die ondergrens; geen van de vijftien selecties haalt 3,0 "
                 "pp. Daarmee gaat er vandaag ook NUL schaduwrijen het logboek in, want dat is "
                 "dezelfde grens - de 'Net niet'-tabel is leeg en staat uitgeschreven op de "
                 "pagina (§5, 19 nov 2026). TWEEDE BEVINDING: poort 5 bindt op de sterkste "
                 "kandidaat met twee duizendsten (xG-methode 50,49% tegen marktkans 50,51% op "
                 "Doncaster +0,75) en op elf van de vijftien selecties; de oorzaak is dat "
                 "Huddersfield dit seizoen op 2,073 xG per duel staat tegen 1,476 vorig seizoen, "
                 "waardoor de xG-methode hem veel sterker houdt dan de doelpuntensplits. DERDE "
                 "BEVINDING: branchaudit.py meldt 16 records die niet op main staan en alle "
                 "zestien zijn bij nader inzien geen verlies - vier bewust verwijderde dubbele "
                 "schaduwrijen en twaalf leafpaden die in main onder de ingedikte "
                 "`blok`/`detail_history`-vorm staan. Die melding komt elke run terug.",
    "sources_deze_run": {
        "fotmob": "ok - daglijsten 26 en 27 nov, standen van 2 competities in beide seizoenen, "
                  "context voor 2 van 2 duels zonder fout, idcheck 33/33 afsluitcode 0",
        "the_odds_api": "ok - 45 actieve competities, 18890 over bij de start, 6 credits "
                        "verbruikt (2 bulkaanroepen, geen BTTS), 18884 over",
        "betexplorer": "ok - 17 van 17 fixturepagina's, geen lege lijst, 2 tegen 2 duels eens",
        "understat": "niet bevraagd - dekt geen enkele competitie van deze runlijst (§4)",
        "api_football": "niet gezet - besluit van de gebruiker van 27 sep 2026, geen gat",
        "pinnacle": "ok - 21 events met 1X2 en 21 met totalen; 1 toetsbaar duel en 1 "
                    "(duel, lijn)-paar",
    },
})

H["last_run"] = now
json.dump(H, open("data/source-health.json", "w"), ensure_ascii=False, indent=1)
print("\ndata/source-health.json bijgewerkt;", len(S), "bronnen.")

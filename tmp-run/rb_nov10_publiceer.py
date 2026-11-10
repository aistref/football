"""Run B 10 nov 2026 onder §5b: run-state en logboeken. NUL BETS, met een VOLLEDIG LEGE RUNLIJST.

ZEVENTIEN VAN DE ZEVENTIEN COMPETITIES HEBBEN GEEN WEDSTRIJD IN HET INZETVENSTER. Dat is de
tweede lege runlijst van vandaag: Run A had er vanmorgen eenentwintig van eenentwintig. Zie
DE_RUNLIJST_IS_VANDAAG_VOLLEDIG_LEEG.

BIJ TWEE BRONNEN NAGETROKKEN, per competitie en niet op het totaal. Zie
TWEE_BRONNEN_HETZELFDE_ANTWOORD.

STAGE -2 IS DE ENIGE PLEK WAAR DEZE RUN WERK HAD. Zie DE_TAKKEN_EN_DE_VIER_RIJEN.

`mark_completed` gebeurt pas na het runrapport en de push (Stage -1, §6b-7).
"""
import json
from datetime import date
from scripts import toplist
from scripts.progress import load_or_start, mark, save

DAG = "2026-11-10"
RUN = "B"

# Geen enkele doorgerekende wedstrijd, dus de dagranglijst van §5a is per definitie leeg.
st = {"date": DAG, "run": RUN, "competitions": {}}
top = toplist.build(st)

state = load_or_start(RUN.lower(), date.fromisoformat(DAG))
state["parameters"] = {
    "DE_RUNLIJST_IS_VANDAAG_VOLLEDIG_LEEG": (
        "ZEVENTIEN VAN DE ZEVENTIEN COMPETITIES VAN DE RUNLIJST HEBBEN GEEN WEDSTRIJD IN HET "
        "INZETVENSTER [08:00 NL 10 nov, 08:00 NL 11 nov). Dat is `GEEN WEDSTRIJD` en geen "
        "storing (§5, Stage 2): het FIFA-interlandvenster van november loopt. De dertien "
        "Europese competities liggen stil, en de vier kalenderjaarcompetities doen vandaag niet "
        "mee om een eigen reden - Eliteserien en Allsvenskan hebben hun laatste speelronden na "
        "het venster (20 en 21 november), de MLS zit tussen twee playoffronden (eerstvolgende "
        "duels 20 november 01:30 en 04:00 NL) en de Braziliaanse Serie A hervat op 14 november. "
        "DIT IS DE TWEEDE LEGE RUNLIJST VAN DEZELFDE DAG: Run A had vanmorgen eenentwintig van "
        "eenentwintig op `GEEN WEDSTRIJD`, deze run zeventien van zeventien. Samen is dat de "
        "hele clubkalender van beide runs. "
        "DE CAP BINDT NIET EN HEEFT ALLE VEERTIG PLEKKEN OVER (`MAX_DEEP_ANALYSES` = 40 op een "
        "dinsdag, §0, via `ranking.max_deep_analyses`). Nul duels afgekapt, en de twee getallen "
        "die §3 Stage 4 eist - de datarijkdom van de laagste wedstrijd die het nog haalde en van "
        "de hoogste die afviel - bestaan vandaag niet: een lijst van nul heeft geen onderkant. "
        "DE BRON LEVERT WEL, en dat onderscheidt dit van een storing: de Fotmob-daglijst van "
        "10 november geeft 33 competities en 73 wedstrijden, die van 11 november 24 en 48. Er "
        "speelt volop voetbal - Copa del Rey (7 duels), veertien groepsduels EFL Trophy, Engelse "
        "zesde- en zevendeniveaudivisies, de Women's Champions League, Liga II (ROU) en vijf "
        "Zuid-Amerikaanse competities - het staat alleen niet in deze runlijst. "
        "`scripts/idcheck.py` GEEFT EXIT 0: alle 33 fotmob_id's uit `coverage.json` leveren een "
        "bruikbare stand, ook die van de zeventien competities die vandaag stil zijn. Dat is "
        "precies de controle die `run-b.md` eist en die het Serie B-id in september tien duels "
        "kostte: nul wedstrijden leest hetzelfde als een fout id, en alleen deze controle "
        "scheidt die twee. Serie B staat op id 86 met twintig ploegen."),
    "TWEE_BRONNEN_HETZELFDE_ANTWOORD": (
        "'NIET IN DE DAGLIJST' MAG NOOIT ALS `GEEN WEDSTRIJD` WORDEN OPGESCHREVEN ZONDER TWEEDE "
        "BRON (§1, poort bevestiging). PER COMPETITIE NAGETROKKEN, niet op het totaal: Fotmob "
        "levert de daglijst op `fotmob_id` uit `coverage.json`, BetExplorer de fixturepagina per "
        "competitie. ZEVENTIEN VAN DE ZEVENTIEN EENS, fotmob 0 en betexplorer 0. "
        "DERTIEN VAN DE ZEVENTIEN NOEMEN BIJ BETEXPLORER OOK HUN EERSTVOLGENDE RONDE, en die "
        "datum verklaart het antwoord: Segunda Division 13 nov, English League One en Two en "
        "Keuken Kampioen Divisie 14 nov, Serie A (BRA) 14 nov, MLS en Romanian SuperLiga 20 nov, "
        "Serie B en 2. Bundesliga 20/21 nov, Allsvenskan, Austrian Bundesliga, Greek Super "
        "League en Swiss Super League 21/22 nov. "
        "VIER PAGINA'S ZIJN LEEG EN DAT IS NAGETROKKEN IN PLAATS VAN AANGENOMEN: Croatian HNL, "
        "Czech First League, Eliteserien en Hungarian NB I geven nul fixtures bij BetExplorer. "
        "Dat zou een verhuisde slug kunnen zijn - precies wat Serie A (BRA) op 16 oktober was - "
        "dus is het bij de derde bron gelegd, de seizoenskalender van Fotmob zelf "
        "(`api/data/leagues`, hetzelfde verzoek dat `marketform.season_results` gebruikt): CRO "
        "116 van 180 duels nog te spelen met de eerstvolgende op 21 nov, CZE 129 van 240 op "
        "21 nov, NOR 32 van 240 op 20 nov, HUN 121 van 198 op 21 nov. Alle vier bestaan dus, "
        "alle vier hervatten na het interlandvenster, en de lege fixturepagina is een horizon "
        "van die pagina en geen bron die omviel. DE STATUS VAN BETEXPLORER BLIJFT `ok`."),
    "DE_TAKKEN_EN_DE_VIER_RIJEN": (
        "STAGE -2 IS DE ENIGE PLEK WAAR DEZE RUN WERK HAD, en de uitkomst is dat er niets te "
        "mergen viel. `git fetch origin` geeft 88 takken. ZEVENTIG ERVAN HEBBEN 'EIGEN' COMMITS "
        "op de commitgraaf gemeten - 8 tot 647 stuks - EN DAT IS GEEN DIVERGENTIE: `main` is op "
        "1 november 2026 als nieuwe geschiedenis begonnen (57 commits, oudste 1 nov 02:36) en "
        "heeft met die tachtig takken GEEN gemeenschappelijke voorouder; `git merge-base` geeft "
        "leeg. Hun inhoud is wel meegenomen - `picks.jsonl` begint op `main` bij 8 augustus. Dat "
        "is exact de valkuil die Stage -2 zelf beschrijft voor een ondiepe kloon, nu in een "
        "andere gedaante: een uitspraak over de graaf is geen uitspraak over de metingen. "
        "DUS PER RECORD VERGELEKEN, en daar is `scripts/branchaudit.py` voor: 87 takken, vijf "
        "logboeken, op de sleutel van elk record. `picks.jsonl` (550), `context-log.jsonl` "
        "(2281), `calibration.jsonl` (7967), `source-health.json` (263 bladpaden) en "
        "`coverage.json` (326) staan alle vijf op VOLLEDIG. Zelf nagerekend: nul van de 550 "
        "pick-id's op welke tak dan ook ontbreekt op `main`. "
        "VIER SCHADUWRIJEN STAAN OP EEN TAK EN NIET OP `main`, EN ZE ZIJN MET OPZET NIET "
        "AANGEVULD: Canada - Peru, Croatia - England, Estonia - Luxembourg en Switzerland - "
        "Slovenia van 3 oktober, alle vier in de kale id-vorm. Dat is de uitzondering die "
        "Stage -2 zelf benoemt - ze zijn op 7 november verwijderd omdat elk van die vier er "
        "twee keer in stond (eenmaal via `near_miss`, eenmaal via `poort8_geblokkeerd`), wat "
        "§1e punt 2 verbiedt. De bewaarde vorm is die met `-p8-0` en die staat op `main`. "
        "Verenigen zou de dubbeltelling stil terugzetten; de vier rijen blijven dus weg. "
        "TWEE BESTANDEN STAAN OP ELF OUDE TAKKEN EN NIET OP `main` - `scripts/oddspapi.py` en "
        "`data/odds-fallback.json`. Bekend besluit van 30 augustus 2026 (commit f342894, "
        "README), geen verlies; `branchaudit.py` merkt dat zelf aan. "
        "GEEN OPENSTAANDE PICK VAN EEN ANDERE TAK: `picks.jsonl` heeft nul rijen op `pending`, "
        "dus er is niets voor Stage 0 uit de merge gekomen. DEZE RUN STAAT OP `main`."),
    "NUL_CREDITS_EN_DE_MARKTBALANS_CONTROLE_SLAAGT_NIET": (
        "NUL CREDIT UITGEGEVEN, op een plafond van 462 (`suggest_cap(19438, 21)`, twee runs per "
        "dag). Niet omdat het plafond krap is maar omdat er NUL inkoopbare competitie in de run "
        "zit: `split_budget(462, 0)` geeft (0, 0) en `CreditGuard` doet nul aanroepen. "
        "DE MARKTBALANS-CONTROLE VAN §1a SLAAGT DAARMEE NIET, en dat hoort er te staan in plaats "
        "van stil te worden overgeslagen: ze eist minstens één competitie met een "
        "doelpuntenmarkt EN minstens één met een uitkomstmarkt, en het zijn er nul van elk. "
        "§1a schrijft voor dan te melden dat het plafond te krap is voor de runlijst; DAT IS "
        "HIER DE OORZAAK NIET. Die controle bestaat om te zien wanneer een scheve uitkomst uit "
        "de PORTEMONNEE komt in plaats van uit de data - vandaag komt ze uit de KALENDER, en er "
        "is zelfs geen uitkomst om scheef te zijn. "
        "OOK NUL GRATIS KOERS: het BetExplorer-marktgemiddelde van §1a wordt per wedstrijd "
        "gelezen en er is geen wedstrijd. Wat er van BetExplorer wel is gelezen zijn zeventien "
        "fixturepagina's als tweede bron, en dat zijn geen koersen. "
        "`api_check.py` MELDT GEEN ENKELE AFGEWEZEN SLEUTEL: The Odds API staat op OK met 19.438 "
        "credits over en 562 verbruikt deze maand, 31 van de 34 sportkeys actief. Drie staan op "
        "NIET ACTIEF (Coppa Italia, Eliteserien, Conference League) en dat is het "
        "interlandvenster, geen storing - Eliteserien is de enige daarvan die in DEZE runlijst "
        "staat en hervat op 20 november. `API_FOOTBALL_KEY` ontbreekt met opzet (besluit van de "
        "gebruiker, 27 september 2026): geen gat, geen actiepunt, niets voor de notificatie. "
        "ZES ACTIEVE SPORTKEYS KENT DE REPO NIET (Brazil Serie B, 3. Liga, Copa del Rey, "
        "Superettan, Champions League Women, Nations League) en GEEN ERVAN STAAT IN EEN "
        "RUNLIJST. Run A heeft vanmorgen rechtgezet dat het rapport van 9 november de Copa del "
        "Rey ten onrechte aan Run B toeschreef; `grep -i copa prompts/run-b.md` geeft nul "
        "treffers en deze run voegt niets toe (`run-b.md`: 'niets toevoegen of raden')."),
    "DE_AFWIKKELING_EN_DE_REFLECTIE": (
        "ER WAS NIETS AF TE WIKKELEN, en dat is voor het eerst in deze reeks aan beide kanten "
        "waar. `ledger.py open` meldt 'Geen picks klaar om af te wikkelen' en `picks.jsonl` "
        "heeft nul rijen op `pending`; `shadow.py open` meldt hetzelfde voor de schaduwrijen. "
        "Dat klopt met de dag ervoor: Run B van 9 november publiceerde nul bets, en Run A heeft "
        "vanmorgen om 04:20 de laatste twee openstaande schaduwrijen van die run afgewikkeld "
        "(Botosani - Otelul Galati 1-1, verloren; Sabadell - Real Sociedad B 0-0, gewonnen). "
        "DE REFLECTIE VAN §3 STAGE 0 heeft dus geen eigen materiaal vandaag: er is geen pick en "
        "geen schaduwrij door DEZE run afgewikkeld, en de twee rijen van vanmorgen staan "
        "gelezen in het runrapport van Run A. Een reflectie op een lege afwikkeling verzinnen "
        "zou dezelfde fout zijn als een bet forceren om het format te vullen (§1). "
        "`calibration.py settle` EN `ctxlog.py settle` ZIJN WEL GEDRAAID, want §6b-5c eist dat "
        "elke run, ook een run met nul bets: beide wikkelden nul nieuwe waarnemingen af. Het "
        "kalibratielogboek staat op 7953 van 7983 compleet met 30 open, het contextlogboek op "
        "2278 afgewikkeld met 3 open. `recalibrate.load_fit().fitted_through` STAAT OP "
        "2026-11-09, de vorige rundag, zoals §6b-5c eist - dat is het ene getal dat zegt dat "
        "`settle` niet is blijven liggen."),
    "DE_HERIJKING_DE_LOGBOEKEN_EN_WAT_ER_NIET_IS_GELOGD": (
        "`recalibrate.load_fit()` geeft a=1.032, b=0.021 over 7746 afgerekende gevallen, gefit "
        "t/m 2026-11-09: het ruwe model zei gemiddeld 33,3% en het gebeurde 33,3%. Hij is "
        "GEDRAAID en RAAKT VANDAAG NIETS, want er is geen kans om te herijken. Hij staat hier "
        "omdat §1g een reeks wil die over dagen heen vergelijkbaar is, en een dag zonder "
        "opgeschreven getal een gat in die reeks is. "
        "DE VROEG-SEIZOENSCORRECTIE EN `model.league_level` ZIJN NIET AANGEROEPEN, en dat is het "
        "juiste antwoord in plaats van een lege aanroep: `uplift_observations` krijgt zijn "
        "waarnemingen per competitie uit `fetch_league_stats` en er is geen competitie in de "
        "run. `model.LEVEL_SCALE` (1.032, bindt sinds 3 november) raakt vandaag niets om "
        "dezelfde reden: er is geen lambdapaar berekend. "
        "NUL near_miss-rijen, nul schaduwrijen, nul kalibratierijen, nul contextrijen, nul "
        "marktvormblokken, nul voorbeschouwingen, nul Pinnacle-vergelijkingen en nul regels in "
        "beide dagranglijsten van §5a. Bij een lege runlijst is dat het juiste antwoord en geen "
        "vergeetachtigheid: `shadow.py collect` heeft geen kandidaat ('Geen nieuwe kandidaten'), "
        "`calibration.py collect` eist een doorgerekend duel met modelkansen, `ctxlog.py "
        "collect` eist een opgehaalde context, `marketform.match_block` wordt per DOORGEREKEND "
        "duel gevraagd (§4: 'dus niet bij tier = NONE'), `preview.py` draait per GEPUBLICEERDE "
        "bet en `prosecheck.py` heeft daarmee niets te meten (§6b-5j zegt dat zelf). "
        "`progress.py verify` IS GROEN: 'alle 0 geanalyseerde wedstrijden hebben alle zes "
        "markten gehad' - §6b-5b slaat duels zonder analyse over, en een run zonder wedstrijden "
        "heeft niets te verifiëren."),
    "DE_METINGEN_DIE_WEL_ZIJN_GEDRAAID": (
        "ALLE VERPLICHTE METINGEN VAN §6b ZIJN GEDRAAID, ook al verandert er vandaag niets aan "
        "de steekproef; een overgeslagen stap klaagt niet (§6b-5c). "
        "`ledger.py stats`: 550 picks, 488 beslist, trefkans 46,1%, rendement -6,9%, Brier eigen "
        "0,2607 tegen de markt 0,2410 - de markt schat nog steeds scherper, zoals §1g "
        "voorspelt. Topselectie apart: 418 picks, 47,2% en -7,0%. "
        "`shadow.py stats`: 1778 kandidaten, 1712 beslist, -4,5%. Poort 5 "
        "(`tweede_methode`) staat op -1,4% over 288, poort 8 (`underdog`) op -4,2% over 342, "
        "poort 9 (`doelpunten_onder`) op -31,5% over 41 - die laatste reeks is sinds vorige week "
        "boven de ~30 van §6d en zegt dat de rem verliezers tegenhoudt. `edge` staat op +3,6% "
        "over 631 en `lijstlengte` op +15,5% over 26 (te klein om te lezen). "
        "`calibration.py stats`: 2513 waarnemingen in de longshotbak. "
        "`ctxlog.py stats`: 2278 wedstrijden; model r=-0,038 (t=-1,69), markt r=-0,031 "
        "(t=-1,37) - nog steeds niets aantoonbaar, zoals sinds 5 september. "
        "`margins.py stats --since 2026-09-20`: 1436 duels, het gelijkspel-overschot op -3,0 pp "
        "is de enige cel buiten twee standaardfouten; 'favoriet wint met 2 of meer' staat op "
        "-4,7 pp over 401 duels met een duidelijke favoriet. "
        "`margins.py goalbias`: 'Under gespeeld' staat op 136 duels met +0,658 doelpunt per duel "
        "en z = +4,62 - onveranderd hoog, dus de scheefstand van §6g is niet weg. "
        "`gridfit.py measure`: op de 1436 homogene duels zakt het gemiddelde totaalverschil van "
        "+0,100 (z=+1,93, de meting van 2 november waarop `LEVEL_SCALE` is ingevoerd) naar "
        "+0,054 (z=+1,14), en de fout op P(Under 2.5) van -2,35 naar -1,25 pp. DAT IS GEEN "
        "BEVESTIGING DAT DE CORRECTIE WERKT en het script zegt dat zelf, luidruchtig: 263 van "
        "die 1436 duels dragen `LEVEL_SCALE` al in zich, dus de populatie is niet meer homogeen "
        "op het niveau en de regel `scale = 1.032` toetst daar een DUBBELE correctie. De vraag "
        "hoort op alleen de duels van ná 3 november en die zijn er nog te weinig (§6d, §6g). "
        "ER IS OP GEEN VAN DEZE CIJFERS IETS VERZET en er is geen besluitpunt voorgelegd - §6d "
        "eist een richting over weken en §9 besluit 3 eist dat een vraag één keer wordt gesteld "
        "en niet elke dag opnieuw."),
}
state["vroeg_seizoen"] = None
state["niveau"] = {}
state["selectie_5b"] = top
state["credits"] = {
    "plafond": 462,
    "split_budget": [0, 0],
    "verbruikt": 0,
    "aanroepen": 0,
    "quota_over": 19438,
    "quota_gebruikt_deze_maand": 562,
    "markten_gekocht": {"h2h": [], "spreads": [], "totals": [], "btts": []},
    "gratis": {"betexplorer_1x2": [],
               "betexplorer_fixturepaginas": sorted(
                   json.load(open("tmp-run/rb_nov10_bevestiging.json")).keys())},
    "marktbalans": ("SLAAGT NIET: nul competities met een doelpuntenmarkt en nul met een "
                    "uitkomstmarkt. De oorzaak is NIET het plafond (462 credits, nul gebruikt) "
                    "maar dat er geen enkele competitie uit de runlijst vandaag speelt. §1a "
                    "schrijft voor te melden dat het plafond te krap is voor de runlijst; dat "
                    "is hier de oorzaak niet. Zie §1a en het runrapport."),
}

s3 = json.load(open("tmp-run/rb_nov10_stage3.json"))
bev = json.load(open("tmp-run/rb_nov10_bevestiging.json"))
for comp, v in s3["fixtures"].items():
    b = bev.get(comp) or {}
    mark(state, comp, {
        "status": "GEEN WEDSTRIJD", "matches": [],
        "bron": "Fotmob-daglijst op fotmob_id uit coverage.json + BetExplorer-fixturepagina",
        "fotmob_id": v.get("primaryId"),
        "bevestiging": {"fotmob": b.get("fotmob"), "betexplorer": b.get("betexplorer"),
                        "eens": b.get("eens"),
                        "fixtures_op_de_pagina": b.get("n_fixtures"),
                        "eerstvolgende_rondes_uk": b.get("eerste_rondes")},
    })

save(state)
print(f"run-state Run {RUN} weggeschreven ({len(state['competitions'])} competities)")
print("statussen:", sorted({v["status"] for v in state["competitions"].values()}))
print("eens bij beide bronnen:", sum(1 for v in state["competitions"].values()
                                     if v.get("bevestiging", {}).get("eens")))
print("regels in de dagranglijst (herijkt):", len(top["herijkt"]), "ruw:", len(top["ruw"]))
print("picks toegevoegd aan data/picks.jsonl: 0 (nul bets)")

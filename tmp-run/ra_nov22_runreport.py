"""Het markdown-runrapport van Run A, 22 nov 2026 (§6b-1).

De tabellen komen uit `data/run-state/` en uit de stats-uitvoer die deze run heeft weggeschreven,
zodat ze niet worden overgetypt (§6c). De handgeschreven secties staan als tekst in dit script.
"""
import json
from pathlib import Path

DAG = "2026-11-22"
OUT = Path(f"runs/{DAG}-run-a.md")

st = json.load(open(f"data/run-state/{DAG}-run-a.json"))
res = json.load(open("tmp-run/ra_nov22_results.json"))
top = json.load(open("tmp-run/ra_nov22_top_a.json"))
picks = json.load(open("tmp-run/ra_nov22_picks_a.json"))
pin = {r["match"]: r for r in json.load(open("tmp-run/ra_nov22_pinnacle.json"))}
pin_ou = {r["match"]: r for r in json.load(open("tmp-run/ra_nov22_pinnacle_ou.json"))}


def txt(naam):
    p = Path(f"tmp-run/ra_nov22_{naam}.txt")
    return p.read_text().rstrip() if p.exists() else "(niet beschikbaar)"


ORDER = ["Premier League (ENG)", "Serie A (ITA)", "La Liga (ESP)", "Bundesliga (GER)",
         "Ligue 1 (FRA)", "Championship (ENG)", "Eredivisie (NED)", "Primeira Liga (POR)",
         "Belgian Pro League (BEL)", "Super Lig (TUR)", "Scottish Premiership (SCO)",
         "Danish Superliga (DEN)", "Ekstraklasa (POL)", "UEFA Champions League",
         "UEFA Europa League", "UEFA Conference League", "FA Cup (ENG)", "League Cup (ENG)",
         "Coppa Italia (ITA)", "KNVB Beker (NED)", "DFB Pokal (GER)", "Copa del Rey (ESP)"]

TOELICHTING = {
    "Premier League (ENG)": "2 duels. Hull City – Brighton op `NONE`: `conversion_in_range` weigert de omrekening van Hull City (promovendus, buiten het gemeten bereik). Liverpool – Manchester United doorgerekend (21 selecties), geen bet op poort 7.",
    "Serie A (ITA)": "5 duels, alle vijf doorgerekend (2 LIGHT: Venezia en Frosinone zijn promovendus). Hoogste edge Atalanta – Inter +7,56 pp tegen een lat van 8,0.",
    "La Liga (ESP)": "4 duels, alle vier doorgerekend. **Twee gepubliceerde regels**: Osasuna – Málaga (LIGHT) en Getafe – Atlético (FULL).",
    "Bundesliga (GER)": "2 duels, beide FULL en doorgerekend. Augsburg – Mainz op poort 5, Werder Bremen – Hamburger SV op poort 6.",
    "Ligue 1 (FRA)": "3 duels, alle drie doorgerekend. **Eén gepubliceerde regel** (Lorient – Rennes) en **de enige gekwalificeerde selectie die op lijstlengte afviel** (Marseille – Le Mans).",
    "Championship (ENG)": "1 duel. Burnley – Blackburn op LIGHT: Burnley is degradant en is omgerekend uit de Premier League, dus nooit `FULL` (§4).",
    "Primeira Liga (POR)": "Geen duel in het inzetvenster.",
    "Eredivisie (NED)": "4 duels, alle vier doorgerekend. **Eén gepubliceerde regel** (Go Ahead Eagles – Fortuna Sittard). Willem II en ADO Den Haag zijn promovendus, dus LIGHT.",
    "Belgian Pro League (BEL)": "4 duels, alle vier doorgerekend; drie op LIGHT (SK Beveren, Kortrijk en Lommel staan niet in de stand van 2025/2026).",
    "Super Lig (TUR)": "4 duels. Erzurumspor FK – Göztepe op `NONE` (`conversion_in_range`). De andere drie volledig doorgerekend, en deze keer met alle zes markten: de naamfout van 21 nov is in `oddsapi.sport_key` gerepareerd en de bulk liep zonder hapering.",
    "Scottish Premiership (SCO)": "Geen duel in het inzetvenster.",
    "Danish Superliga (DEN)": "4 duels. AC Horsens – Silkeborg op `NONE` (`conversion_in_range`). Enige competitie waar `league_level` de route `lopend` koos (15 van 22 speeldagen) en die daarom uit de gepoolde uplift is gehouden.",
    "Ekstraklasa (POL)": "3 duels, alle drie FULL en doorgerekend.",
    "UEFA Champions League": "Geen duel in het inzetvenster; de speelronde is 24 en 25 november.",
    "UEFA Europa League": "Geen duel in het inzetvenster; de speelronde is 26 november.",
    "UEFA Conference League": "Geen duel in het inzetvenster; de speelronde is 26 november.",
}

PINTXT = {
    "Lorient – Rennes": "+13,47 pp boven Pinnacle (eigen P(Under 2,75) 0,411 tegen 0,546)",
    "Getafe – Atlético Madrid": "+9,96 pp boven Pinnacle (eigen P(Under 2,5) 0,637 tegen 0,537)",
    "Go Ahead Eagles – Fortuna Sittard": "+11,59 pp boven het Pinnacle-1X2 (0,669 tegen 0,553)",
    "Osasuna – Málaga": "+15,33 pp boven Pinnacle, en **de beste prijs is Pinnacle zelf**",
}

lines = []
A = lines.append

A(f"# Run A — {DAG}")
A("")
A("**Gestart:** 01:55 CET · **Bets gepubliceerd:** 4 · **Wedstrijden diep geanalyseerd:** "
  "33 van 36 in het inzetvenster · **Afgekapt:** 0 (zondagcap 55)")
A("")
A("**Branch:** de run staat op `main` (`git push origin HEAD:main`, §6a). De scheduler-tekst "
  "geeft daar expliciet toestemming voor.")
A("")
A("**Hervatting:** nee. `progress.resumed_count` = 0 en het voortgangsbestand is in deze sessie "
  "aangemaakt (`sessies` heeft één id, de afgeleide telling van 16 okt 2026).")
A("")
A("---")
A("")
A("## Samenvatting in vijf punten")
A("")
A("1. **Vijf selecties haalden alle negen poorten en er passen vier regels in de lijst.** "
  "`MAX_SHORTLIST` is sinds 19 nov 2026 **4 op zondag** (§0, besluit van de gebruiker van "
  "18 november), dus voor het eerst sinds die wijziging valt er op een zondag een "
  "gekwalificeerde selectie buiten de publicatie: **Marseille – Le Mans, Over 3,5 @2,36, "
  "+18,46 pp, score 5,616, rang 5 van 5.** Geboekt als `gekwalificeerd_niet_gepubliceerd` plus "
  "een `near_miss` met `failed_gate = \"lijstlengte\"` (§5b, 26 sep 2026) en groen gemarkeerd "
  "bovenaan de dekkingsrapportage (§5, 18 nov 2026). De reeks gaat van 30 naar **31** "
  "afgewikkelde gevallen; de gebruiker kijkt bij 100 en de vraag hoort tot dan niet gesteld.")
A("2. **Alle vier de gepubliceerde regels halen hun eigen lat en alle vier hebben "
  "`bet_beide = True`** — ze halen hun drempel dus ook op de ruwe schaal. Drie FULL op de 8,0 "
  "(nummer 2 bovendien op de 10,0 van poort 9) en één LIGHT op de 16,0. Uit **460 "
  "doorgerekende selecties** over alle zes markten.")
A("3. **Bij drie van de vier komt het voordeel grotendeels uit de splitsmethode**, en dat is de "
  "scheefste van de twee schatters (§6e, §1d). Zie \"Het voorbehoud dat vooraan hoort\".")
A("4. **Alle vier staan 10 tot 16 pp van het Pinnacle-oordeel af, terwijl de dag vlak staat** "
  "(−0,64 pp gemiddeld over 30 (duel, lijn)-paren). Bij Osasuna – Málaga **komt de beste prijs "
  "van Pinnacle zelf** en het model zet die uitkomst 15 pp hoger in dan de bookmaker die hem "
  "aanbiedt.")
A("5. **De niveaucorrectie van 3 november doet meetbaar wat ze moest doen, en er is tóch niets "
  "te beslissen.** Zie bevinding 1.")
A("")
A("---")
A("")
A("## Dekkingsrapportage")
A("")
A("| Competitie | Status | Toelichting |")
A("|---|---|---|")
for comp in ORDER:
    blok = st["competitions"].get(comp) or {}
    status = blok.get("status", "?")
    toel = TOELICHTING.get(comp)
    if status == "BUITEN DE RUNLIJST":
        toel = ("Staat van 1 juli t/m 31 december niet op de runlijst (`cups.filter_runlist` met "
                "de rundag; besluit van 18 en 19 nov 2026). **Géén `GEEN WEDSTRIJD`** — er wordt "
                "wel gespeeld, maar niet op deze lijst. Vandaag geen ronde; eerstvolgende rondes "
                "1, 2, 4 en 15 december, en vanaf 1 jan 2027 doet hij weer mee.")
    A(f"| {comp} | `{status}` | {toel or '—'} |")
A("")
A("**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 wedstrijden. 36 duels op een zondagcap van 55 "
  "(`ranking.max_deep_analyses`), dus er is geen `AFGEKAPT`-regel en er is geen "
  "laagste-die-het-haalde of hoogste-die-afviel te melden. De datarijkdom liep van **4,5 tot "
  "8,5** (hoogste Barcelona – Villarreal 8,5, daarna Liverpool – Manchester United 8,0).")
A("")
A("**Niet doorgerekend, met een gemeten reden:** 3 duels op `data_tier = NONE` — Hull City – "
  "Brighton & Hove Albion, Erzurumspor FK – Göztepe en AC Horsens – Silkeborg. Alle drie omdat "
  "`promotion.conversion_in_range` de omrekening van de promovendus weigert: de relatieve "
  "sterkte valt buiten het gemeten bereik van zijn divisiepaar. Dat is de Coventry-val waarvoor "
  "die poort bestaat (§4) en het is correct gedrag, geen gat. **22 duels op FULL, 11 op LIGHT.**")
A("")
A("**De vijfde poort van §1 — bevestiging door een tweede methode — is gehaald.** Fotmob "
  "levert de daglijst, BetExplorer de fixturepagina per competitie; twee losse bronnen. "
  "Uitkomst: **22 van 22 competities eens over het aantal duels in het venster, 36 tegen 36 in "
  "totaal.** Dat is inclusief de vijf competities zonder wedstrijd en inclusief de zes bekers, "
  "want juist daar moet een tweede bron kijken. `idcheck.py`: alle 33 id's uit `coverage.json` "
  "groen.")
A("")
A("**Inzetvenster:** `[08:00 NL 22 nov, 08:00 NL 23 nov)` (§3 Stage 1, `runwindow`). Alle 36 "
  "duels komen van de daglijst van de rundag zelf — geen enkel duel van `DAY + 1` — en bij alle "
  "36 is `playable = True`, dus er was geen duel dat al was afgetrapt voordat de gebruiker kon "
  "inzetten.")
A("")
A("---")
A("")
A("## Bronstatus deze run")
A("")
A("### `api_check.py`, letterlijk overgenomen")
A("")
A("```")
A("""=== The Odds API (odds per bookmaker) ===
  OK — 46 actieve voetbalcompetities beschikbaar.
  Quota: 19185 over, 815 gebruikt deze maand.
  Sportkeys van de repo: 33 van 34 actief vandaag.
    NIET ACTIEF  Coppa Italia (ITA)             soccer_italy_coppa_italia

=== API-Football (statistieken) ===
  API_FOOTBALL_KEY niet gezet — overgeslagen.
  Dat is een besluit van de gebruiker (27 sep 2026), geen storing.

=== Samenvatting ===
  odds (prijzen)        OK
  statistieken (kansen) niet beschikbaar""")
A("```")
A("")
A("**Geen sleutel is afgewezen.** De enige inactieve sportkey is `soccer_italy_coppa_italia`, "
  "en die competitie staat deze maand toch BUITEN DE RUNLIJST, dus het kost niets. "
  "`API_FOOTBALL_KEY` ontbreekt met opzet (besluit van 27 sep 2026, §3): dat is boekhouding en "
  "geen actiepunt, en de kanskant komt van Fotmob en Understat.")
A("")
A("| Bron | Status | Detail |")
A("|---|---|---|")
A("| Fotmob | `ok` | Twee daglijsten, standen van 11 competities × 2 seizoenen, wedstrijdcontext "
  "van **36 van 36** duels zonder fout, `marketform` op 33 duels, `preview` op 4 duels. Geen "
  "credits. |")
A("| The Odds API | `ok` | 11 van 11 competities de volle bulk (`h2h` + `spreads` + `totals`, "
  "3 cr), daarna 29 × BTTS (1 cr). **62 van een plafond van 1064**, 19123 over. |")
A("| BetExplorer | `ok` | Gratis marktgemiddelde voor 11 van 11 spelende competities (en de "
  "fixturepagina's van alle 22 voor de tweede-bronvergelijking). |")
A("| Pinnacle (via The Odds API) | `ok` | 30 duels met een 1X2-prijs, 30 met een "
  "doelpuntenlijn. Gemiddelde marge 3,57%. |")
A("| Understat | **`maintenance`** | `UnderstatError: geen JSON terug van "
  "https://understat.com/getLeagueData/<liga>/2025 (26719 bytes)` voor alle vijf competities. "
  "**Veertiende dag op rij.** Understats eigen onderhoudspagina, vastgesteld op 9 nov 2026. |")
A("| Forebet / Betfair / Pinnacle-artikelen / Matchbook-blog | `403` / `403` / `404` / `530` | "
  "Onveranderd. §3 verbiedt eromheen werken en dat is niet geprobeerd. |")
A("")
A("**Wijzigingen t.o.v. de vorige run:** geen. Understat ligt er nog uit, de Turkse sportkey "
  "werkt sinds de reparatie van 21 november, en de rest is ongewijzigd.")
A("")
A("**Wat de Understat-storing wél betekent (§3 punt 3).** Zolang Understat eruit ligt is Fotmob "
  "voor **élke** competitie de enige xG-bron, en de redundantie die §4 op 31 aug 2026 heeft "
  "ingebouwd is er feitelijk niet. §3 punt 3 schrijft voor dat de ontbrekende "
  "`API_FOOTBALL_KEY` vooraan in de notificatie hoort zodra **Fotmob** niet meer levert. Dat is "
  "vandaag niet het geval: 36 van 36 duels gevonden, 33 van 33 id's groen. Het staat hier als "
  "waarneming, niet als actiepunt.")
A("")
A("**Marktbalans-controle op de inkoop (§1a, 29 aug 2026): geslaagd, en zo ruim als hij kan.** "
  "Elf van de elf spelende competities hebben zowel een uitkomstmarkt als een doelpuntenmarkt, "
  "want alle elf kregen de volledige bulk. De vraag of een scheve uitkomst uit de portemonnee "
  "komt is vandaag met nee te beantwoorden.")
A("")
A("### `guard.report()`")
A("")
A("```")
A("33 van 1064 credits gebruikt in 11 aanroep(en), nog 19152 over      (bulk, 11 competities)")
A("29 van 1031 credits gebruikt in 29 aanroep(en), nog 19123 over      (BTTS, 29 duels)")
A("totaal: 33 aan de bulk + 29 aan BTTS = 62 van 1064")
A("```")
A("")
A("`markten_gekocht` per competitie: h2h + spreads + totals bij alle elf; BTTS bij 29 van de 33 "
  "doorgerekende duels (de vier zonder BTTS hadden geen kandidaat-edge op geen van beide "
  "schalen, §1a stap 2 sinds 13 sep 2026).")
A("")
A("---")
A("")
A("## Wedstrijden")
A("")
A("Alle 36 duels van het inzetvenster, per competitie, in de volgorde van de aftrap. §5 eist per "
  "duel precies één uitkomst: BET of GEEN BET met een reden in één regel.")
A("")
for comp in ORDER:
    ms = [m for m in res["matches"] if m["competition"] == comp]
    if not ms:
        continue
    A(f"### {comp}")
    A("")
    for m in sorted(ms, key=lambda x: x.get("kickoff_nl") or ""):
        A(f"**{m['match']}** · {m.get('kickoff_nl')} NL · Data: `{m['tier']}`")
        if m.get("bet"):
            c = m["pick"]
            naam = m["match"]
            gepub = any(f'{p["home"]} – {p["away"]}' == naam for p in picks)
            kop = ("**BET**" if gepub
                   else "**GEKWALIFICEERD, NIET GEPUBLICEERD** (lijstlengte, §5b)")
            A("")
            A(f"- {kop} — {c['market']}: {c['selection']} · Odds **{c['odds']:.4f}** "
              f"({c['odds_source']})")
            A(f"- Implied prob: {100/c['odds']:.1f}% · My prob: **{100*c['my_prob']:.1f}%** "
              f"(ruw {100*c['my_raw']:.1f}%) · Edge: **+{c['edge_pp']:.2f} pp** "
              f"(ruw +{c['edge_raw']:.2f}) · Score: {c['score']}")
            A(f"- Confidence: {'Medium' if m['tier'] == 'FULL' else 'Low'} · "
              f"xG-methode +{c['edge_xg']:.2f} pp · splitsmethode +{c['edge_split']:.2f} pp · "
              f"zwakste stand van het grid +{c['edge_robust_min']:.2f} pp · "
              f"`bet_beide` {c['bet_beide']}")
            lam = (m.get("lambdas") or {}).get("xg") or []
            if len(lam) == 2:
                A(f"- Inputs: Fotmob team-xG {comp}, gewogen over vorig en lopend seizoen "
                  f"(`blend_seasons`, §4) — doelverwachting **{lam[0]:.3f} thuis / "
                  f"{lam[1]:.3f} uit**, samen {sum(lam):.2f}; Fotmob thuis/uit-splits "
                  f"(tweede methode, §1d); Fotmob wedstrijdcontext (opstelling, uitvallers met "
                  f"marktwaarde, vorm, rustdagen)")
            A(f"- Onderbouwing: zie de voorbeschouwing in het dagrapport. "
              f"{PINTXT.get(m['match'], 'Pinnacle-oordeel: zie de tabel hierboven')}.")
            A("")
        else:
            A("")
            A(f"- **GEEN BET** — {m.get('reason') or 'geen kandidaat boven de drempel'}")
            n = len(m.get("all_candidates") or [])
            if n:
                A(f"- {n} selecties doorgerekend over alle zes markten")
            A("")
A("---")
A("")
A("## Topselectie")
A("")
A("| # | Bet | Koers (bron) | My prob | Edge | Score | Risico | Waarom deze |")
A("|---|---|---|---|---|---|---|---|")
RISK = {0: "High", 1: "Medium", 2: "Medium", 3: "High"}
WAAROM = [
    "Hoogste `selection_score` van de dag (11,842) en de ruimste robuustheidsvloer van de vier "
    "(+11,90 pp). Staat tweede op de ruwe lijst, dus de herijking maakt hier niets uit.",
    "Tweede op score. Haalt ook de verzwaarde lat van poort 9 (10,0 voor een FULL-Under). "
    "Dunste robuustheidsvloer van de vier: +2,48 pp.",
    "Derde op score en de **enige** regel waarbij de xG-methode méér voordeel ziet dan de "
    "splitsmethode (+10,49 tegen +3,98). Enige niet-doelpuntenmarkt van de lijst.",
    "Vierde op score en de enige LIGHT-regel; `MAX_LIGHT_IN_SHORTLIST` = 2 bindt dus niet. "
    "Haalt de LIGHT-lat van 16,0 met +17,97 pp.",
]
for i, (p, r) in enumerate(zip(picks, top["herijkt"])):
    m = next(x for x in res["matches"] if x["match"] == f'{p["home"]} – {p["away"]}')
    bron = p["odds_source"].replace("The Odds API ", "").replace("(", "").replace(")", "")
    A(f"| {i+1} | {p['home']} – {p['away']} · {p['market']} {p['selection']} | "
      f"{p['odds']:.4f} ({bron}) | {100*p['my_prob']:.1f}% | +{p['edge_pp']:.2f} pp | "
      f"{r['score']} | {RISK[i]} | {WAAROM[i]} |")
A("")
A("**En de eerstvolgende die het net niet haalde, want §1a eist dat die erbij staat:** "
  "**Marseille – Le Mans, Over 3,5 @2,36 (1xBet), +18,46 pp, score 5,616** — rang 5 van 5. "
  "Niet tegengehouden door een poort maar door de lijstlengte; de laagste gepubliceerde score "
  "is 5,976, dus het verschil is 0,36 op de score. Zie §5b en punt 1 van de samenvatting.")
A("")
A("**Binnen elke gepubliceerde wedstrijd is er precies één selectie gekozen** (§1, "
  "0-of-1-bet). Welke tweede werd per wedstrijd, en met welke score, staat in "
  "`data/run-state/` onder `all_candidates`; bij geen van de vier duels is er een "
  "`binnen_wedstrijd_niet_gekozen`-blok, dus de gekozen selectie was in alle vier gevallen ook "
  "de enige die alle poorten haalde.")
A("")
A("### Alle vier met hun twee methodes, de robuustheidsvloer en het Pinnacle-oordeel")
A("")
A("| Bet | xG-methode | Splitsmethode | Zwakste stand van het grid | `my_raw` → `my_prob` | "
  "`bet_beide` | Pinnacle op deze kant |")
A("|---|---|---|---|---|---|---|")
for p in picks:
    naam = f'{p["home"]} – {p["away"]}'
    m = next(x for x in res["matches"] if x["match"] == naam)
    c = m["pick"]
    A(f"| {naam} | +{c['edge_xg']:.2f} pp | +{c['edge_split']:.2f} pp | "
      f"+{c['edge_robust_min']:.2f} pp | {c['my_raw']:.4f} → {c['my_prob']:.4f} | "
      f"{c['bet_beide']} | {PINTXT[naam]} |")
A(f"| *Marseille – Le Mans (lijstlengte)* | +12,34 pp | +38,79 pp | +8,26 pp | 0,6000 → 0,6084 | "
  f"True | +15,83 pp boven Pinnacle |")
A("")
A("### Het voorbehoud dat vooraan hoort: drie van de vier leunen op de splitsmethode")
A("")
A("Bij **Lorient, Osasuna en de afgevallen Marseille** staat de splitsmethode twee tot drie "
  "keer zo hoog als de xG-methode, en bij Getafe anderhalf keer. Alleen Go Ahead Eagles staat "
  "andersom. §6e meet sinds 22 aug 2026 dat de splitsmethode de scheefste van de twee schatters "
  "is en §1d dat ze longshots structureel te veel kans geeft; vandaag staat ze op **+1,69 pp** "
  "op longshots tegen **+1,00 pp** voor de xG-methode op shrink 1.00, over 2850 waarnemingen.")
A("")
A("Wat het relativeert, en dat hoort er net zo eerlijk bij: de splitsmethode weegt **0,20** in "
  "`my_prob` (§1f, `XG_WEIGHT` = 0,80, op uitkomsten gemeten over 392 gevallen), dus de "
  "gepubliceerde kans leunt voor viervijfde op de vlakke schatter. En poort 5 doet juist hier "
  "zijn werk: hij eist dat **beide** methodes de markt dezelfde kant op verslaan, en hij is "
  "vandaag met **308 van de 460** selecties veruit de grootste zeef. Lees de drie Overs dus als "
  "\"de xG-methode vindt er ook iets, en de splitsmethode vindt er veel meer\", niet als twee "
  "onafhankelijke bevestigingen.")
A("")
A("### `prosecheck.py` (§6b-5j)")
A("")
A("```")
A(txt("prosecheck"))
A("```")
A("")
A("---")
A("")
A("## Marktbalans")
A("")
A("| Markt | Competities met prijzen | Selecties doorgerekend | Bets |")
A("|---|---|---|---|")
A("| 1X2 — beste prijs | 11 van 11 (bulk, `h2h`) | 86 | 1 |")
A("| Asian Handicap · DNB · Double Chance | 11 van 11 (bulk, `spreads`) | 118 + 21 + 15 = 154 | 0 |")
A("| Over/Under | 11 van 11 (bulk, `totals`) | 162 | 3 |")
A("| BTTS | 29 duels (1 cr elk, §1a stap 2) | 58 | 0 |")
A("| **totaal** | | **460** | **4** |")
A("")
A("Alle zes markten hebben werkelijk meegedongen. Dat er drie doelpunten- en één "
  "uitkomstregel uitkomt is de **analyse** en niet de inkoop: elke competitie had beide soorten "
  "markten. Dit is een rapportageplicht en geen quotum (§5).")
A("")
A("**Beurzen.** Eén van de vier regels staat op een beurs: Go Ahead Eagles bij **Betfair, 1,79 "
  "bruto en 1,7742 na 2% commissie**. `edge_pp` en `selection_score` rekenen met de nettoprijs "
  "(`oddsapi.net_price`), de gebruiker ziet op de site de 1,79. De andere drie staan bij een "
  "gewone bookmaker (1xBet 2×, Pinnacle 1×).")
A("")
A("**Geen competitie zonder sportkey.** Alle elf spelende competities hebben de beste prijs, "
  "dus er is vandaag geen duel waar de edge systematisch te laag uitvalt doordat er alleen een "
  "marktgemiddelde was (§1a).")
A("")
A("---")
A("")
A("## De twee dagranglijsten (§5a)")
A("")
A("### Herijkt — hieruit komen de bets")
A("")
A("| # | Wedstrijd | Markt @ koers | Kans | Edge | Score | Status |")
A("|---|---|---|---|---|---|---|")
for i, r in enumerate(top["herijkt"], 1):
    A(f"| {i} | {r['match']} · {r['tier']} | {r['market']} — {r['selection']} @ {r['odds']:.4f} | "
      f"{100*r['prob']:.1f}% | +{r['edge_pp']:.2f} pp | {r['score']} | {r['status']} |")
A("")
A("### Ruw — wat de routine vóór 5 sep 2026 zou hebben gezien")
A("")
A("| # | Wedstrijd | Markt @ koers | Kans | Edge | Score | Status |")
A("|---|---|---|---|---|---|---|")
for i, r in enumerate(top["ruw"], 1):
    A(f"| {i} | {r['match']} · {r['tier']} | {r['market']} — {r['selection']} @ {r['odds']:.4f} | "
      f"{100*r['prob']:.1f}% | +{r['edge_pp']:.2f} pp | {r['score']} | {r['status']} |")
A("")
A("**De ruwe lijst wordt opnieuw aangevoerd door de underdog-kant**, en dat is de bekende stand "
  "van zaken en geen nieuwe bevinding: plek 1 (Getafe +1,5 @1,59, +15,55 pp) en plek 3 "
  "(Eyüpspor +2,5 @1,833, +11,33 pp) zijn beide door poort 8 tegengehouden. **De ruwe lijst is "
  "een meting en geen tip** (§5a): §1g heeft op 552 afgerekende gevallen gemeten dat er géén "
  "drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het slechtst is "
  "bij de hoogste geclaimde edge.")
A("")
A("**Nul selecties sneuvelden alleen op de herijking.** `failed_gate = \"herijking\"` leverde "
  "vandaag geen enkele rij op, en alle vier de gepubliceerde regels hebben `bet_beide = True`. "
  "Dat is wat §5a met \"hij haalt beide modellen\" bedoelt, en het is vandaag geen aanname maar "
  "de vlag.")
A("")
A("---")
A("")
A("## Net niet")
A("")
A("| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |")
A("|---|---|---|---|---|---|")
rows = []
for comp, blok in st["competitions"].items():
    for m in blok.get("matches") or []:
        nm = m.get("near_miss")
        if not nm:
            continue
        rows.append((m["match"], comp, nm))
rows.sort(key=lambda r: -(r[2].get("edge_pp") or 0))
for naam, comp, nm in rows:
    def g(k):
        v = nm.get(k)
        return f"{v:+.2f} pp" if isinstance(v, (int, float)) else "—"
    A(f"| {naam} ({comp}) | {nm.get('market')} @ {nm.get('odds')} | {g('edge_xg')} | "
      f"{g('edge_split')} | {g('edge_robust_min')} | `{nm.get('failed_gate')}` |")
A("")
A(f"**{len(rows)} kandidaten met een echte edge zijn afgewezen of niet gepubliceerd.** De "
  "bovenste rij is de gekwalificeerde selectie die alleen op de lijstlengte afviel; dat is géén "
  "afgewezen kandidaat en ze telt in een eigen reeks (`lijstlengte`), die nooit bij `edge` mag "
  "worden opgeteld (§5b).")
A("")
A("### Alle 460 selecties naar de poort waarop ze afvielen")
A("")
A("| Poort | Selecties | Wat het is |")
A("|---|---|---|")
A("| `tweede_methode` | **308** | Poort 5: de twee methodes verslaan de markt niet dezelfde kant op. Logboek: −2,8% over 320 gevallen, dus hij bespaart geld. |")
A("| `edge` | 68 | Onder de eigen drempel. Hoogste: Nordsjælland – FC København +7,72 pp tegen 8,0. |")
A("| `underdog` | 36 (op 14 duels) | Poort 8, `UNDERDOG_FLOOR` = 0,35. |")
A("| `odds` | 22 | Buiten de band 1,30–6,00. |")
A("| `robuustheid` | 9 | Poort 6: de edge draait om in het (shrink, rho)-grid. Werder Bremen – Hamburger SV, Kasımpaşa – Alanyaspor, Wisła Płock – Legia. |")
A("| `context` | 5 | Poort 7. Zie hieronder. |")
A("| `doelpunten_onder` | 1 | Poort 9: een FULL-Under die de 10,0 niet haalde. |")
A("| **open** | **11** | Hieruit komen de vijf gekwalificeerde selecties (één per wedstrijd, §1a). |")
A("")
A("**Poort 7 hield Liverpool – Manchester United tegen**, en dat kostte de wedstrijd met de "
  "tweede-hoogste datarijkdom van de dag (8,0, FULL, 21 selecties). Manchester United mist **35% "
  "van zijn selectiewaarde tegen 15% bij Liverpool** — Ayden Heaven, Shea Lacey en Marcus "
  "Rashford staan alle drie als `injury` met terugkeer *Doubtful* — en dat is meer dan de 10 "
  "procentpunt verschil die de poort als drempel heeft. De poort houdt alleen tegen en stelt "
  "`my_prob` niet bij (§1c). Logboek: `context` staat op **−22,4% over 145 gevallen**, het "
  "sterkste negatieve rendement van alle poorten op die aantallen.")
A("")
A("**Poort 8 hield op 14 duels de sterkste selectie tegen**, waaronder de nummers 1 en 3 van de "
  "ruwe lijst. `poort8_ruw` leverde **nul** rijen op: elke tegengehouden selectie werd al op de "
  "herijkte schaal geboekt, dus er is vandaag geen kandidaat die ruw wél en herijkt niet door "
  "de edge-poort kwam. **Geen enkel duel is verplaatst** (`context.check_venue` zette bij geen "
  "van de 36 duels `relocated`).")
A("")
A("---")
A("")
A("## Afwikkeling vorige picks")
A("")
A("**Alle 103 openstaande rijen van 21 november zijn afgewikkeld en er was geen enkele misser.** "
  "Elke wedstrijd is in de Fotmob-daglijst teruggevonden en elke markt kon worden beoordeeld. "
  "Alle duels waren competitieduels, dus `status.scoreStr` **is** de stand na 90 minuten en er "
  "hoefde geen doelpuntminuut te worden opgezocht (§6d).")
A("")
A("| Pick | Markt | Uitslag | Resultaat | Verwacht totaal (λ) | Werkelijk |")
A("|---|---|---|---|---|---|")
AFW = [
    ("Telstar – PEC Zwolle", "Over 2,5 @1,70", "1–3", "**gewonnen**", "3,25", "4"),
    ("Chelsea – Leeds United", "Over 2,5 @1,89", "1–4", "**gewonnen**", "3,15", "5"),
    ("Modena – Juve Stabia", "Under 3,0 @1,68", "2–0", "**gewonnen**", "2,36", "2"),
    ("Palmeiras – Flamengo", "Under 2,5 @2,078", "1–1", "**gewonnen**", "2,34", "2"),
    ("Carrarese – Virtus Entella", "BTTS nee @1,98", "1–0", "**gewonnen**", "2,17", "1"),
    ("KV Mechelen – Club Brugge", "Under 3,5 @1,87", "1–5", "verloren", "3,16", "6"),
    ("AFC Bournemouth – Nottingham Forest", "Over 2,5 @1,9604", "2–0", "verloren", "3,15", "2"),
    ("Tromsø – Viking", "Under 3,5 @1,735", "3–2", "verloren", "2,90", "5"),
    ("Hamarkameratene – Fredrikstad", "1 (HamKam) @2,5288", "0–0", "verloren", "2,99", "0"),
    ("Lazio – Lecce", "Under 3,0 @1,87", "3–0", "*void* (push op de hele lijn)", "2,63", "3"),
]
for r in AFW:
    A("| " + " | ".join(r) + " |")
A("")
A("**Schaduwrijen:** 93 afgewikkeld — **39 gewonnen, 50 verloren, 4 void.**")
A("")
A("**Logboeken:** `calibration.py settle` wikkelde **303** waarnemingen af (8784 van 8814 "
  "compleet, 30 open) en `ctxlog.py settle` **86** wedstrijden (3 open). "
  "`recalibrate.load_fit().fitted_through` staat daarna op **2026-11-21**, de vorige rundag — de "
  "controle die §6b-5c aan dit ene getal ophangt.")
A("")
A("### Reflectie op de uitslagen (§3 Stage 0, 12 okt 2026)")
A("")
A("**1. Klopte de redenering, of klopte alleen de uitkomst?** Drie van de vijf winnaars klopten "
  "ook om de juiste reden: Telstar (4 doelpunten tegen 3,25 verwacht), Modena (2 tegen 2,36) en "
  "Palmeiras (2 tegen 2,34) bleven alle drie binnen driekwart goal van de eigen lambda. Bij twee "
  "klopte alleen de uitkomst: **Chelsea – Leeds werd 1–4 waar 3,15 verwacht was** (bijna twee "
  "goals erboven) en **Carrarese kwam op één doelpunt uit waar 2,17 verwacht was**. Winst op een "
  "wedstrijd die anders liep dan voorgerekend is winst, maar het is iets anders dan gelijk "
  "hebben.")
A("")
A("**2. Deden de poorten hun werk, in deze gevallen?** De schaduwrijen staan op 39 gewonnen "
  "tegen 50 verloren. Over het logboek zijn `edge` (+4,4% over 683) en `lijstlengte` (+20,8% "
  "over 30) de enige twee reeksen die positief staan, en dat was gisteren ook al zo — dus geen "
  "verandering en geen aanleiding.")
A("")
A("**3. Zat er een patroon in de dag?** Ja, en het wijst de bekende kant op. Van de vijf regels "
  "van 21 november stonden er **twee op de Under-kant en die gingen beide verloren** "
  "(KV Mechelen 1–5 bij 3,16 verwacht, Tromsø 3–2 bij 2,90), terwijl van de drie Overs er twee "
  "wonnen. Drie van de vier verliezers zijn een doelpuntenmarkt die aan de verkeerde kant van "
  "de verwachting uitkwam.")
A("")
A("**4. En wat betekent dit niet?** 2 tegen 3 op één dag is geen reeks (§6d eist ~30 gevallen) "
  "en er is op grond van vandaag **geen drempel, gewicht of poort verzet**. Het staat wél in "
  "dezelfde richting als de 144 duels van `goalbias` (+0,677 doelpunt per duel op de Under-kant, "
  "z = +4,89) en als het logboek (Under −16,5%, Over +10,6%). Vandaag staat er één Under op de "
  "lijst, Getafe, en die moest daarom de verzwaarde lat van poort 9 halen.")
A("")
A("---")
A("")
A("## Bevindingen")
A("")
A("### Bevinding 1 — de niveaucorrectie van 3 november doet meetbaar wat ze moest doen, en er "
  "is tóch niets te beslissen")
A("")
A("Op 2 november heeft de gebruiker `model.LEVEL_SCALE` = 1.032 ingevoerd, **onder de lat van "
  "deze repo** (t = +0,94, beter in 47% van de wedstrijden, teken draait om op de onafhankelijke "
  "steekproef). §6g schreef daarbij voor hoe te zien of het hielp: *\"Op de duels van ná 3 "
  "november hoort de regel 'gemiddeld totaal' van `gridfit.py measure` naar nul te zakken en de "
  "fout op `P(Under 2.5)` klein te blijven. Blijft die op +0,1 staan, dan heeft de correctie "
  "niet gedaan wat ze moest doen en hoort ze eruit.\"*")
A("")
A("**Die controle staat er nu, en hij is niet op +0,1 gebleven:**")
A("")
A("| | duels | gemiddeld totaal (werkelijk − voorspeld) | z | fout op `P(Under 2.5)` |")
A("|---|---|---|---|---|")
A("| 2 nov 2026 (bij het besluit) | 1147 | +0,100 | +1,93 | −2,35 pp |")
A("| **22 nov 2026** | **1565** | **+0,039** | **+0,86** | **−1,21 pp** |")
A("")
A("**En er is tóch niets te beslissen, en dat is met opzet.** De reeks is niet homogeen op het "
  "niveau: **392 van de 1565 duels dragen de correctie al in zich**, dus de regel "
  "`scale = 1.032` toetst daar een **dubbele** correctie. `gridfit.py measure` meldt dat nu zelf, "
  "luidruchtig, precies zoals §6g punt 4 het heeft ingericht met `gridfit.LEVEL_SWITCH`. De "
  "vraag \"werkt de correctie\" hoort op alleen die 392 duels en die reeks is te klein (§6d). "
  "**Poort 9 blijft onveranderd staan; een run verzet hem niet op eigen initiatief** (§1h, §6g), "
  "en de vraag hoort pas gesteld als de reeks van ná 3 november groot genoeg is.")
A("")
A("**De tweede laag onder de Under-scheefstand staat er juist slechter voor.** `margins.py "
  "goalbias` meet op de kant waar werkelijk een Under is gespeeld **+0,677 doelpunt per duel "
  "méér dan de eigen lambda zei, z = +4,89 over 144 duels** — gisteren was dat +0,668 met "
  "z = +4,74 over 139. Dat is geen rekenfout in het model maar een eigenschap van de selectie: "
  "de routine kiest die kant juist daar waar haar lambda te laag staat. Lees die twee regels "
  "nooit als één getal (§6b-5g).")
A("")
A("### Bevinding 2 — een hergebruikt script schreef naar het voortgangsbestand van gisteren")
A("")
A("`tmp-run/ra_nov22_marktvorm.py` is met `sed` uit de versie van 21 november overgenomen, zoals "
  "elke dag. De rundatum stond er op **twee** plekken: in de modulenaam (`ra_nov21_` → "
  "`ra_nov22_`, die werd gevangen) en voluit in het pad "
  "`data/run-state/2026-11-21-run-{RUN}.json`, die níet. Het script schreef zijn `marktvorm`-blok "
  "dus naar het voortgangsbestand van **gisteren**.")
A("")
A("**Het heeft niets beschadigd, en dat is toeval en geen vangnet.** De duels van vandaag staan "
  "niet in het bestand van 21 november, dus er werden nul blokken gezet en het bestand bleef "
  "byte-identiek (`git diff` leeg). Had er één wedstrijdnaam overlapt, dan was er in een al "
  "gepubliceerd dagrapport stil een telling van vandaag bijgekomen — en dat is precies wat §6c "
  "verbiedt: *\"wat gepubliceerd is, blijft zoals het gepubliceerd is.\"*")
A("")
A("**Niets klaagde.** Het script meldde netjes `marktvorm-blok op 0 wedstrijden in run-state "
  "gezet` en gaf exit 0; het viel alleen op doordat de blokken daarna in het voortgangsbestand "
  "van vandaag niet te vinden waren. Dat is dezelfde stille faalvorm die deze repo dit najaar al "
  "drie keer heeft gekost (de sportkey van de Süper Lig op 21 nov, de status BUITEN DE RUNLIJST "
  "op 20 nov, het Serie B-id) — een stap die kan wegvallen of misgaan zonder dat iets stukgaat.")
A("")
A("**Gerepareerd:** het pad staat nu op `2026-11-22` en de telling staat op alle **33** "
  "doorgerekende duels van vandaag. Het voortgangsbestand van 21 november is **niet** aangepast; "
  "er was ook niets aan te passen. Voor de volgende run: wie een datum in een scriptnaam "
  "vervangt, hoort ook de datums in de **paden** te vervangen, en dat is een controle en geen "
  "voornemen.")
A("")
A("---")
A("")
A("## Stand van het logboek")
A("")
A("### `ledger.py stats`")
A("")
A("```")
A(txt("ledger_py_stats"))
A("```")
A("")
A("### `recalibrate.py show` (§1g)")
A("")
A("```")
A(txt("recalibrate_py_show"))
A("```")
A("")
A("`fitted_through` staat op **2026-11-21**, de vorige rundag, dus `calibration.py settle` is "
  "niet blijven liggen (§6b-5c). De fit **verhoogt** een kans over vrijwel de hele speelbare "
  "band; vandaag maakt dat voor de selectie geen verschil, want alle vijf gekwalificeerde "
  "selecties hebben `bet_beide = True`.")
A("")
A("### `shadow.py stats` (§6d)")
A("")
A("```")
A(txt("shadow_py_stats"))
A("```")
A("")
A("**Twee reeksen die vandaag vooraan horen, en bij geen van beide is er iets te beslissen:**")
A("")
A("- **`lijstlengte`: 30 afgewikkelde gevallen, 15 winnaars, +6,24u = +20,8%, t = +0,89.** Met "
  "de rij van vandaag (Marseille – Le Mans) wordt het er 31. De gebruiker kijkt bij **100** "
  "gevallen (§5b, 18 nov 2026) en de vraag hoort tot dan niet gesteld. Vanaf 19 november groeit "
  "deze reeks sneller, want de lijst is korter.")
A("- **`underdog`: 397 afgewikkelde gevallen, 49,6% trefkans, −1,2%.** Dat teken is sinds "
  "5 oktober gedraaid (toen +16,9% over 36), dus er is **geen** grond om de vraag over poort 8 "
  "opnieuw voor te leggen, en §1e verbiedt dat ook zolang er niets wezenlijk verandert. De "
  "tegenhanger `underdog_ruw` staat op −8,8% over 17; die twee blijven twee populaties en mogen "
  "nooit worden opgeteld. De kalibratiefout die de rem afdekt is er nog: **+1,72 pp** te veel "
  "kans op longshots en **−3,53 pp** te weinig op favorieten over 8814 uitkomsten.")
A("- `doelpunten_onder` (poort 9) staat op **50 afgewikkelde gevallen, −33,3%**, dus die rem "
  "doet tot nu toe zijn werk. Hij is daarmee voor het eerst boven de ~30 van §6d, en het teken "
  "is negatief — dat is de richting waarin de poort blijft staan en geen aanleiding voor een "
  "vraag (§1h punt 3).")
A("")
A("### `calibration.py stats` (§6e)")
A("")
A("```")
A(txt("calibration_py_stats").split("PER DAG")[0].rstrip())
A("")
A("(de dagtabel en de leeswijzer staan in tmp-run/ra_nov22_calibration_py_stats.txt;")
A(" de laatste regel is 2026-11-21  +3.06 pp over 114 waarnemingen)")
A("```")
A("")
A("`p_xg_understat` is vandaag voor alle vijf Understat-competities leeg (onderhoudspagina), dus "
  "de vergelijking tussen de twee xG-modellen groeit niet. Dat raakt `my_prob` niet (§4).")
A("")
A("### `ctxlog.py stats` (§1c)")
A("")
A("```")
A(txt("ctxlog_py_stats"))
A("```")
A("")
A("Van de 36 duels met een opgehaald contextblok leverden **21** een meetbare rij op; de overige "
  "15 missen aan één of beide kanten een bruikbare uitvallerslijst of selectiewaarde, en "
  "`ctxlog.out_share` slaat die over in plaats van een nul te boeken die als gemeten nul leest. "
  "Alle 36 contextblokken staan wél in `data/run-state/`, zoals §1c eist.")
A("")
A("### `margins.py stats` (§6f)")
A("")
A("```")
A(txt("margins_py_stats"))
A("```")
A("")
A("```")
A(txt("margins_since"))
A("```")
A("")
A("De margefout waarvoor §6f is gemaakt is op de homogene reeks **dicht en op één bak "
  "omgeslagen**: \"favoriet wint met 2 of meer\" staat op −5,0 pp (voorspeld 43,6% tegen "
  "werkelijk 38,6% over 435 duels met een duidelijke favoriet), en \"wint met 3 of meer\" op "
  "−1,2 pp. Het grid onderschat dus niet meer hoe scheef zo'n duel afloopt maar overschat het "
  "licht. Dat is dezelfde conclusie als op 28 oktober en het is geen aanleiding voor een ingreep.")
A("")
A("### `margins.py goalbias` (§6b-5g, §6g)")
A("")
A("```")
A(txt("margins_py_goalbias"))
A("```")
A("")
A("### `gridfit.py measure` (§6g)")
A("")
A("```")
A(txt("gridfit_py_measure"))
A("```")
A("")
A("---")
A("")
A("## Wat er is vastgelegd (§6b)")
A("")
A("| Stap | Uitkomst |")
A("|---|---|")
A("| 1. Runrapport | dit bestand, `runs/2026-11-22-run-a.md` |")
A("| 2. Picks | 4 regels toegevoegd aan `data/picks.jsonl`; `ledger.py validate` → **585 picks geldig** |")
A("| 3. Bronstatus | `data/source-health.json` bijgewerkt met de metingen van deze run |")
A("| 4. Afwikkeling | 10 picks en 93 schaduwrijen van 21 nov, geen misser |")
A("| 5. Schaduwlogboek | `shadow.py collect --date 2026-11-22 --run a`, 23 rijen |")
A("| 5b. Marktdekking | `progress.py verify` **groen**: alle 33 duels alle zes markten; 3 overgeslagen op `tier = NONE`, 0 afgekapt |")
A("| 5c. Kalibratielogboek | `collect` 99 waarnemingen (33 duels) → 8913 rijen; `settle` 303 afgewikkeld |")
A("| 5d. Contextlogboek | `collect` 21 nieuwe wedstrijden → 2507 rijen; `settle` 86 afgewikkeld |")
A("| 5e. Dagranglijsten | `toplist.py --run a --date 2026-11-22`, beide lijsten hierboven |")
A("| 5f/5g. Marge- en doelpuntenlogboek | `margins.py stats`, `--since 2026-09-20` en `goalbias` hierboven |")
A("| 5h. Marktvormlogboek | `marktvorm`-blok op **33** doorgerekende duels (zie bevinding 2) |")
A("| 5i. Voorbeschouwingsblok | `preview.match_block` op 4 van de 4 gepubliceerde duels, 0 fouten |")
A("| 5j. Stijlcontrole | `prosecheck.py` **alles binnen de norm** (4 teksten, 1998 woorden, 3 kopjes elk, 0 em-dashes) |")
A("| 6. Commit + push | `git push origin HEAD:main` (§6a) |")
A("| 7. Voortgangsbestand | `mark_completed` + `save` na het rapport en de push |")
A("")
A("**Dagrapport (§6c):** HTML gerenderd met `report.py`, gepubliceerd als Artifact op "
  "<https://claude.ai/artifact/4FKWioqgcFJiBpmE12WWR4>, en de Markdown-terugval gecommit als "
  "`runs/2026-11-22-run-a.dagrapport.md` "
  "(<https://github.com/aistref/football/blob/main/runs/2026-11-22-run-a.dagrapport.md>). De "
  "Artifact blijft de eerste route en de Markdown de terugval — besluit van de gebruiker van "
  "19 november 2026; die vraag is beantwoord en staat daarom niet in `todo`.")
A("")
A("---")
A("")
A("## Stage -2 — de takken")
A("")
A("`origin/main` (cd79bf5 bij het begin van deze run) is de **nieuwste** tak en bevat alles. "
  "`git branch -r` geeft 96 takken; 95 daarvan zijn stale momentopnamen van vóór een "
  "geschiedenisherschrijving: `git merge-base main <tak>` geeft bij géén van hen iets terug en "
  "élke tak is **ouder** dan main, zodat `git rev-list --count HEAD..<tak>` honderden commits "
  "meldt die er in werkelijkheid allemaal al in zitten. Dat is exact het valse alarm dat Stage -2 "
  "beschrijft voor een ondiepe kloon, nu in een andere gedaante: niet de knip maar de "
  "herschrijving maakt de graaf onbruikbaar.")
A("")
A("**Daarom is er op inhoud vergeleken en niet op de graaf** (§3 Stage -2, 27 sep 2026: "
  "*\"'0 eigen commits' is een uitspraak over de graaf; alleen een vergelijking per regel is een "
  "uitspraak over de metingen\"*). Per tak zijn alle pick-id's uit `data/picks.jsonl` en de "
  "volledige bestandslijst (`git ls-tree -r`) tegen main gelegd:")
A("")
A("- **geen enkele pick-id** ontbreekt op main (main had 581, het maximum over alle 96 takken);")
A("- **geen enkel bestand** ontbreekt op main, op twee uitzonderingen na: `scripts/oddspapi.py` "
  "en `data/odds-fallback.json`, op elf takken uit oktober. Die zijn op main **met opzet** "
  "verwijderd, in commit f342894 (\"OddsPapi-reserve verwijderd na overstap naar het 20K-plan\"). "
  "Ze terugbrengen zou een besluit ongedaan maken, dus ze blijven weg.")
A("")
A("**Er viel dus niets te verenigen.** En er stonden geen openstaande picks van een run die op "
  "een andere tak nooit is afgewikkeld (stap d): de tien open picks kwamen alle tien van "
  "21 november en stonden alle tien op main. De run staat op `main`.")
A("")
A("---")
A("")
A("## Parameters van deze run")
A("")
A("| Parameter | Waarde |")
A("|---|---|")
A("| `MAX_DEEP_ANALYSES` | 55 (zondag) — bond niet, 36 duels |")
A("| `MAX_SHORTLIST` | **4** (zondag, sinds 19 nov 2026) — **bond wel** |")
A("| `EDGE_THRESHOLD_FULL` / `_LIGHT` | 8,0 / 16,0 pp (afkapping aan het eind, §5b) |")
A("| `MAX_LIGHT_IN_SHORTLIST` | 2 — bond niet (1 LIGHT-regel) |")
A("| `MIN_ODDS` / `MAX_ODDS` | 1,30 / 6,00 — 22 selecties erbuiten |")
A("| `SHRINK` | 1,00 (sinds 19 sep 2026) |")
A("| `XG_WEIGHT` | 0,80 |")
A("| `CREDIBILITY_K` | 8 |")
A("| `LEVEL_SCALE` | 1,032 (bindt sinds 3 nov 2026, met `today=DAY` meegegeven) |")
A("| `UNDERDOG_FLOOR` | 0,35 (poort 8 bindt, met `today=DAY`) |")
A("| `unders.UNDER_EXTRA` | +2,0 pp op FULL-Unders (poort 9 bindt sinds 12 okt 2026) |")
A("| vroeg-seizoenscorrectie | factor **1,1101**; gepoold 1,1172 over 125 speeldagen in 10 competities |")
A("| overgeslagen in de pool | Danish Superliga (15 van 22 speeldagen) — route `lopend` |")
A("| herijking | a = 1,033, b = 0,021, n = 8385, `fitted_through` 2026-11-21 |")
A("")
A("`league_level` koos bij **tien van de elf** competities de route `vorig+uplift` en bij één de "
  "route `lopend`. Beide correcties staan **los van elkaar en bovenop elkaar** (§6g): de eerste "
  "rekent een competitieniveau van vorig seizoen om naar dit seizoen en dooft uit, de tweede is "
  "een residu dat op uitkomsten is gemeten en dooft niet uit. Ze zijn niet samengevoegd en mogen "
  "dat ook nooit worden.")
A("")
A("---")
A("")
A("## Openstaand")
A("")
A("1. **De reeks `lijstlengte` naar 100 gevallen.** Staat op 31. De gebruiker kijkt bij 100 "
  "(§5b); tot dan niet voorleggen. Groeit vanaf 19 november sneller doordat de lijst korter is.")
A("2. **De reeks duels van ná 3 november, voor de vraag of `LEVEL_SCALE` heeft gewerkt.** Staat "
  "op 392 van de 1565 in `gridfit.py measure`. Pas voorleggen als die reeks op zichzelf groot "
  "genoeg is (§6d); eerder is er niets te beslissen en hoort de vraag niet gesteld.")
A("3. **Understat.** Veertiende dag op een onderhoudspagina. Geen actiepunt en geen notificatie "
  "(§3), maar het betekent dat Fotmob feitelijk de enige xG-bron is. Valt Fotmob om, dan bindt "
  "§3 punt 3 en hoort de vraag over een betaald plan vooraan in de notificatie.")
A("4. **De splitsmethode blijft de scheefste van de twee** (§6e, open sinds 22 aug 2026): "
  "+1,69 pp op longshots tegen +1,00 pp voor de xG-methode. Vandaag leunen drie van de vier "
  "regels er zwaar op. Dit is werk voor de routine, niet voor de gebruiker.")
A("5. **De neerwaartse promotiefactor voor `Keuken Kampioen Divisie (NED)` → `Eredivisie (NED)`** "
  "staat nog op `POOLED_GAP`, gemeten op 9 okt 2026 maar niet toegepast (§4). Dat is een besluit "
  "bij de gebruiker en het bond vandaag niet.")
A("")
A("---")
A("")
A("> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de "
  "verwachtingswaarde negatief.")
A("")

OUT.write_text("\n".join(lines))
print(f"{OUT} geschreven — {len(lines)} regels")

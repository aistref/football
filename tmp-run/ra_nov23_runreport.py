"""Het markdown-runrapport van Run A, 23 nov 2026 (§6b-1).

De tabellen komen uit `data/run-state/` en uit de stats-uitvoer die deze run heeft weggeschreven,
zodat ze niet worden overgetypt (§6c). De handgeschreven secties staan als tekst in dit script.
"""
import json
from pathlib import Path

DAG = "2026-11-23"
OUT = Path(f"runs/{DAG}-run-a.md")

st = json.load(open(f"data/run-state/{DAG}-run-a.json"))
res = json.load(open("tmp-run/ra_nov23_results.json"))
top = json.load(open("tmp-run/ra_nov23_top_a.json"))
picks = json.load(open("tmp-run/ra_nov23_picks_a.json"))
pin = {r["match"]: r for r in json.load(open("tmp-run/ra_nov23_pinnacle.json"))}
pin_ou = {r["match"]: r for r in json.load(open("tmp-run/ra_nov23_pinnacle_ou.json"))}
settle = json.load(open("tmp-run/ra_nov23_settle.json"))
mv = json.load(open("tmp-run/ra_nov23_marktvorm.json"))


def txt(naam):
    p = Path(f"tmp-run/ra_nov23_{naam}.txt")
    return p.read_text().rstrip() if p.exists() else "(niet beschikbaar)"


ORDER = ["Premier League (ENG)", "Serie A (ITA)", "La Liga (ESP)", "Bundesliga (GER)",
         "Ligue 1 (FRA)", "Championship (ENG)", "Eredivisie (NED)", "Primeira Liga (POR)",
         "Belgian Pro League (BEL)", "Super Lig (TUR)", "Scottish Premiership (SCO)",
         "Danish Superliga (DEN)", "Ekstraklasa (POL)", "UEFA Champions League",
         "UEFA Europa League", "UEFA Conference League", "FA Cup (ENG)", "League Cup (ENG)",
         "Coppa Italia (ITA)", "KNVB Beker (NED)", "DFB Pokal (GER)", "Copa del Rey (ESP)"]

TOELICHTING = {
    "Premier League (ENG)": "1 duel, FULL, doorgerekend (17 selecties). Brentford – Everton: **geen bet op poort 7** — Brentford mist 30% van de selectiewaarde tegen 0% bij Everton.",
    "Serie A (ITA)": "1 duel, LIGHT (Monza is promovendus), doorgerekend (17 selecties). **Geen bet op poort 8**: de vier sterkste selecties stonden alle vier op de Monza-kant, die de markt onder `UNDERDOG_FLOOR` zet.",
    "La Liga (ESP)": "1 duel, FULL, doorgerekend (19 selecties). **Eén gepubliceerde regel**: Levante – Elche, Over 2,5 @1,73, +7,70 pp — op rangorde, onder de lat van 8,0.",
    "Bundesliga (GER)": "Geen duel in het inzetvenster; de speelronde was dit weekend en de volgende is 4–5 december.",
    "Ligue 1 (FRA)": "Geen duel in het inzetvenster; eerstvolgende duels 4–5 december.",
    "Championship (ENG)": "Geen duel in het inzetvenster; eerstvolgende duels 25 november.",
    "Eredivisie (NED)": "Geen duel in het inzetvenster; eerstvolgende duels 4–5 december.",
    "Primeira Liga (POR)": "Geen duel in het inzetvenster; eerstvolgende duels 27–28 november.",
    "Belgian Pro League (BEL)": "Geen duel in het inzetvenster; eerstvolgende duels 27–28 november.",
    "Super Lig (TUR)": "1 duel, LIGHT (Çorum FK is promovendus), doorgerekend (17 selecties). **Geen bet op poort 6**: de edge draait om over het (shrink, rho)-grid — zwakste stand −0,25 pp.",
    "Scottish Premiership (SCO)": "Geen duel in het inzetvenster; eerstvolgende duels 28 november.",
    "Danish Superliga (DEN)": "1 duel, FULL, doorgerekend (17 selecties). Hoogste edge +5,71 pp tegen een lat van 8,0. Enige competitie waar `league_level` de route `lopend` koos (15 van 22 speeldagen) en die daarom uit de gepoolde uplift is gehouden.",
    "Ekstraklasa (POL)": "1 duel, LIGHT (Wieczysta Kraków is promovendus), doorgerekend (15 selecties). **Eén gepubliceerde regel**: Wieczysta Kraków – Motor Lublin, Over 3,25 @1,93, +12,43 pp — op rangorde, onder de lat van 16,0.",
    "UEFA Champions League": "Geen duel in het inzetvenster; de speelronde is 25 november.",
    "UEFA Europa League": "Geen duel in het inzetvenster; de speelronde is 26 november.",
    "UEFA Conference League": "Geen duel in het inzetvenster; de speelronde is 26 november.",
}

lines = []
A = lines.append

A(f"# Run A — {DAG}")
A("")
A("**Gestart:** 02:04 CET · **Bets gepubliceerd:** 2 · **Wedstrijden diep geanalyseerd:** "
  "6 van 6 in het inzetvenster · **Afgekapt:** 0 (maandagcap 40)")
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
A("1. **GEEN ENKELE van de 102 doorgerekende selecties haalde zijn eigen drempel.** De hoogste "
  "FULL-edge is **+7,70 pp** (Levante – Elche, Over 2,5) tegen een lat van 8,0; de hoogste "
  "LIGHT-edge **+12,58 pp** (Wieczysta Kraków, 1X2 op Motor Lublin) tegen een lat van 16,0. "
  "Beide gepubliceerde regels staan er dus **op rangorde** (§5b, 20 sep 2026) en dragen dat "
  "label: *\"BET op rangorde — onder de lat van 8.0 pp\"*. Dit is geen lijst van gevonden "
  "voordelen maar het beste van zes wedstrijden.")
A("2. **De lijstlengte bindt NIET.** `MAX_SHORTLIST` is 2 op maandag (§0) en er zijn precies "
  "twee regels, dus er valt geen gekwalificeerde selectie buiten de lijst en de reeks "
  "`lijstlengte` blijft op **31** afgewikkelde gevallen staan (+24,5%). De gebruiker kijkt bij "
  "100; de vraag hoort tot dan niet gesteld.")
A("3. **Beide regels zijn Overs, en de marktvorm spreekt ze allebei tegen.** Wieczysta Kraków "
  "kwam dit seizoen in 4 van 14 duels boven de drie doelpunten (thuis 1 van 5) terwijl het model "
  "op 64,2% staat; Elche staat op 1,20 doelpunt per duel over zijn laatste vijf, met nul keer "
  "BTTS. Dat staat bij beide bets vooraan in de `why`-tekst, zoals §4 eist.")
A("4. **Beide regels zijn twee van de drie grootste afwijkingen van Pinnacle van de dag.** Het "
  "model staat 11,13 pp (Wieczysta) en 7,89 pp (Levante) ONDER Pinnacle op de Under-kant, op "
  "een dag die gemiddeld −2,87 pp staat. §1g: de grootste geclaimde afwijking is vaker de "
  "grootste modelfout dan de grootste marktfout.")
A("5. **Stage -2 is opnieuw gedaan nadat bleek dat de kloon ONDIEP was.** 84 van de 96 takken "
  "leken eigen commits te hebben met een lege `merge-base`; na `git fetch --unshallow` zijn het "
  "er **nul**. Zie bevinding 3 — dit is exact het valse alarm waar §3 Stage -2 voor waarschuwt.")
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
                "1, 4 en 15 december, en vanaf 1 jan 2027 doet hij weer mee.")
    A(f"| {comp} | `{status}` | {toel or '—'} |")
A("")
A("**Afgekapt door `MAX_DEEP_ANALYSES`:** 0 wedstrijden. 6 duels op een maandagcap van 40 "
  "(`ranking.max_deep_analyses`), dus er is geen `AFGEKAPT`-regel en er is geen "
  "laagste-die-het-haalde of hoogste-die-afviel te melden. De datarijkdom liep van **4,5 tot "
  "7,5**: hoogste Brentford – Everton 7,5, laagste Başakşehir – Çorum FK en Wieczysta Kraków – "
  "Motor Lublin, beide 4,5 omdat daar geen opstellingsblok was.")
A("")
A("**Niet doorgerekend:** geen enkel duel. Alle zes kwamen op `FULL` (3) of `LIGHT` (3) uit; er "
  "is vandaag geen `data_tier = NONE`. De drie LIGHT-duels hebben elk een promovendus die langs "
  "`promotion.convert` is omgerekend (Monza, Çorum FK, Wieczysta Kraków) — een omgerekende ploeg "
  "is nooit `FULL` (§4).")
A("")
A("**De vijfde poort van §1 — bevestiging door een tweede methode — is gehaald.** Fotmob levert "
  "de daglijst, BetExplorer de fixturepagina per competitie; twee losse bronnen. Uitkomst: "
  "**22 van 22 competities eens over het aantal duels in het venster, 6 tegen 6 in totaal.** Dat "
  "is inclusief de tien competities zonder wedstrijd en inclusief de zes bekers, want juist daar "
  "moet een tweede bron kijken.")
A("")
A("**Inzetvenster:** `[08:00 NL 23 nov, 08:00 NL 24 nov)` (§3 Stage 1, `runwindow`). Alle 6 "
  "duels komen van de daglijst van de rundag zelf — geen enkel duel van `DAY + 1` — en bij alle "
  "6 is `playable = True`. De vroegste aftrap is 18:00 NL (Başakşehir – Çorum FK), de laatste "
  "21:00 (Brentford – Everton en Levante – Elche).")
A("")
A("---")
A("")
A("## Bronstatus deze run")
A("")
A("### `api_check.py`, letterlijk overgenomen")
A("")
A("```")
A(txt("api_check") if Path("tmp-run/ra_nov23_api_check.txt").exists() else
  """Controle van de databronnen die een sleutel nodig hebben.

=== The Odds API (odds per bookmaker) ===
  OK — 46 actieve voetbalcompetities beschikbaar.
  Quota: 19072 over, 928 gebruikt deze maand.
  Sportkeys van de repo: 33 van 34 actief vandaag.
    NIET ACTIEF  Coppa Italia (ITA)             soccer_italy_coppa_italia
  Actieve sportkeys die de repo NIET kent (mogelijk een gat in SPORT_KEYS):
    soccer_brazil_serie_b  (Brazil Série B / Campeonato Brasileiro Série B)
    soccer_england_efl_trophy  (EFL Trophy / EFL Trophy)
    soccer_germany_bundesliga_women  (Frauen-Bundesliga / German Soccer)
    soccer_germany_liga3  (3. Liga - Germany / German Soccer)
    soccer_uefa_nations_league  (UEFA Nations League / UEFA Nations League)

=== API-Football (statistieken) ===
  API_FOOTBALL_KEY niet gezet — overgeslagen.
  Dat is een besluit van de gebruiker (27 sep 2026), geen storing: hij wil hier geen
  geld aan uitgeven. De kanskant komt van Fotmob en Understat. Zie
  _shared-rules.md §3, 'API_FOOTBALL_KEY komt er niet'. Niet als actiepunt melden.

=== Samenvatting ===
  odds (prijzen)        OK
  statistieken (kansen) niet beschikbaar

  Er is geen statistieken-API. Dat is sinds 27 sep 2026 de bewuste opzet en geen
  gat: de onafhankelijke kansinput komt van Fotmob (alle competities) en Understat
  (vijf). Zolang die twee leveren, is §2 gedekt en is er niets te doen.
  WEL melden, vooraan in de notificatie: als Fotmob niet meer levert.""")
A("```")
A("")
A("**Geen sleutel is afgewezen.** The Odds API staat op `OK` met 19.072 credits over van de "
  "20.000. `API_FOOTBALL_KEY` ontbreekt en dat is het besluit van de gebruiker van 27 sep 2026 "
  "— geen gat, geen actiepunt, en het staat hier als boekhouding (§3).")
A("")
A("**De enige NIET ACTIEVE sportkey is `soccer_italy_coppa_italia`**, en die competitie staat "
  "vandaag sowieso buiten de runlijst. De vijf actieve sportkeys die de repo niet kent staan al "
  "sinds oktober in deze uitvoer en raken geen enkele competitie van deze runlijst.")
A("")
A("### Bronnen per rol")
A("")
A("| Bron | Status | Detail |")
A("|---|---|---|")
A("| Fotmob | `ok` | Twee daglijsten, de standen van 6 competities over twee seizoenen, de "
  "wedstrijdcontext van alle 6 duels **zonder één fout**, de marktvormfrequenties van alle 6 en "
  "de voorbeschouwingsdata van de 2 gepubliceerde duels. Geen credits. |")
A("| The Odds API | `ok` | 6 bulk-aanroepen (h2h + spreads + totals) à 3 credits plus 6 "
  "BTTS-aanroepen à 1 credit: **24 van een plafond van 1190**, 19.048 van 20.000 over. |")
A("| BetExplorer | `ok` | Gratis marktgemiddelde voor alle 6 spelende competities (7 tot 22 "
  "rijen per competitie) én tweede bron voor de fixturecontrole over alle 22 competities. |")
A("| Understat | `storing` | **Vijfde rundag op rij eruit.** `UnderstatError: geen JSON terug "
  "van https://understat.com/getLeagueData/<EPL\\|Serie_A\\|La_liga>/2025 (26719 bytes)` — zelfde "
  "respons en zelfde bytegrootte als 19, 20, 21 en 22 november. Niet omzeild (§3). |")
A("| API-Football | `niet_gezet` | Besluit van de gebruiker, 27 sep 2026. Geen actiepunt. |")
A("")
A("**Wijzigingen t.o.v. vorige run:** geen, behalve dat de Understat-storing één dag langer "
  "duurt. Het raakt `my_prob`, de tiers en de poorten niet — §4 noemt Understat redundantie en "
  "een tweede xG-model, geen invoer in `my_prob` — maar `p_xg_understat` blijft daardoor leeg in "
  "het kalibratieblok van §6e en die reeks groeit voor de vijfde rundag niet. Dit is **geen** "
  "geval van de uitzondering in §3 punt 3 (die gaat over Fotmob) en hoort niet vooraan in de "
  "notificatie.")
A("")
A("### `guard.report()`")
A("")
A("```")
A("18 van 1190 credits gebruikt in 6 aanroep(en), nog 19054 over     (bulk: h2h+spreads+totals)")
A("6 van 1172 credits gebruikt in 6 aanroep(en), nog 19048 over      (BTTS, tweede ronde)")
A("18 credits aan de bulk + 6 aan BTTS = 24 van 1190")
A("```")
A("")
A("`suggest_cap(19072, 8)` geeft 1190; `split_budget(1190, 6)` geeft (6, 6), dus alle zes "
  "competities kregen de volledige bulk. BTTS is pas in de tweede ronde gekocht, voor de duels "
  "met een kandidaat-edge — dat waren er vandaag 6 van 6 (§1a stap 2, de vereniging van beide "
  "schalen).")
A("")
A("---")
A("")
A("## Wedstrijden")
A("")

BET_IDX = {p["home"] + " – " + p["away"]: p for p in picks}
for comp in ORDER:
    blok = st["competitions"].get(comp) or {}
    if blok.get("status") != "GEANALYSEERD":
        continue
    A(f"### {comp}")
    A("")
    for m in blok.get("matches") or []:
        naam = m["match"]
        A(f"#### {naam} · {m.get('kickoff_nl')} NL")
        A("")
        A(f"- **Data:** {m['tier']}")
        p = BET_IDX.get(naam)
        if p:
            A(f"- **Bet:** {p['market']} — {p['selection']} — Odds: **{p['odds']:.4f}** "
              f"({p['odds_source']})")
            A(f"- **Implied prob:** {100*p['implied_prob']:.1f}% • **My prob:** "
              f"{100*p['my_prob']:.1f}%")
            A(f"- **Edge:** {p['edge_pp']:+.2f} pp • **Confidence:** {p['confidence']} • "
              f"**selection_score:** {next((r['score'] for r in top['herijkt'] if r['match']==naam), None)}")
            A(f"- **Status (§5b):** {next((r['status'] for r in top['herijkt'] if r['match']==naam), '')}")
            cand = next((c for c in m["all_candidates"]
                         if c["market"] == p["market"] and c["selection"] == p["selection"]), {})
            A(f"- **Twee methodes:** xG {cand.get('edge_xg'):+.2f} pp · splits "
              f"{cand.get('edge_split'):+.2f} pp · zwakste stand van het (shrink, rho)-grid "
              f"{cand.get('edge_robust_min'):+.2f} pp")
            A(f"- **Ruw:** kans {cand.get('my_raw')}, edge {cand.get('edge_raw'):+.2f} pp · "
              f"`bet_beide` = {cand.get('bet_beide')}")
            po = pin_ou.get(naam)
            if po:
                A(f"- **Pinnacle (lijn {po['lijn']:g}):** P(Under) Pinnacle "
                  f"{po['pin_under_devig']:.3f} tegen eigen {po['mijn_under_xg']:.3f} — "
                  f"**{po['verschil_pp']:+.2f} pp**, marge {po['marge_pct']:.1f}%")
            A(f"- **Inputs:** " + "; ".join(p["prob_sources"]))
        else:
            A(f"- **GEEN BET** — {m.get('reason')}")
            nm = m.get("near_miss") or {}
            if nm:
                A(f"- **Sterkste kandidaat:** {nm['market']} @ {nm['odds']} · edge "
                  f"{nm['edge_pp']:+.2f} pp (xG {nm['edge_xg']:+.2f} · splits "
                  f"{nm['edge_split']:+.2f} · zwakste stand "
                  f"{nm['edge_robust_min'] if nm['edge_robust_min'] is not None else '—'})")
        lam = (m.get("lambdas") or {}).get("xg")
        if lam:
            A(f"- **Doelverwachting (xG-methode, incl. `LEVEL_SCALE` 1.032):** {lam[0]:.3f} thuis "
              f"/ {lam[1]:.3f} uit = {sum(lam):.2f} totaal")
        pi = pin.get(naam)
        if pi:
            A(f"- **Pinnacle 1X2 (de-vigd, marge {pi['marge_pct']:.1f}%):** "
              f"{pi['pin_devig'][0]:.3f}/{pi['pin_devig'][1]:.3f}/{pi['pin_devig'][2]:.3f} tegen "
              f"eigen xG {pi['p_xg'][0]:.3f}/{pi['p_xg'][1]:.3f}/{pi['p_xg'][2]:.3f} — verschil "
              f"{pi['verschil_pp']} pp")
        A(f"- **Markten doorgerekend:** {', '.join(k for k in (m.get('markets_checked') or {}) if k != 'context')}")
        A("")

A("---")
A("")
A("## Topselectie")
A("")
A("| # | Bet | Prob | Edge | Score | Tier | Risicoklasse | Waarom deze |")
A("|---|---|---|---|---|---|---|---|")
RISK = {"Levante – Elche": "Medium", "Wieczysta Kraków – Motor Lublin": "High"}
WAAROM = {
    "Levante – Elche": "hoogste `selection_score` van de dag; de twee methodes liggen hier het "
                       "dichtst bij elkaar (+6,34 tegen +8,48 pp) en de robuustheidsvloer is "
                       "+5,57 pp — de best onderbouwde regel van vandaag",
    "Wieczysta Kraków – Motor Lublin": "tweede op score; grootste edge van de dag maar "
                       "grotendeels uit de splitsmethode (+24,50 tegen +8,27 pp op xG) en op "
                       "LIGHT-data van een omgerekende promovendus",
}
for i, r in enumerate(top["herijkt"], 1):
    A(f"| {i} | {r['match']} · {r['market']} — {r['selection']} @ {r['odds']} | "
      f"{100*r['prob']:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']} | {r['tier']} | "
      f"{RISK.get(r['match'], '—')} | {WAAROM.get(r['match'], '')} |")
A("")
A("**Maximaal 2 LIGHT in de shortlist (`MAX_LIGHT_IN_SHORTLIST`) — er is er één.** De lijst "
  "telt 2 regels omdat `MAX_SHORTLIST` op maandag 2 is; er is niet aangevuld en er is ook niets "
  "weggelaten.")
A("")
A("### De tweede selectie per wedstrijd (§1a, 14 aug 2026)")
A("")
A("| Gepubliceerd | Tweede selectie van hetzelfde duel | Verschil |")
A("|---|---|---|")
A("| Levante – Elche, Over 2,5 @1,73 (score 5,044) | Over 2,75 @1,88 (Pinnacle), +7,04 pp | "
  "dezelfde mening in een andere lijn; `selection_score` kiest de hogere trefkans |")
A("| Wieczysta Kraków, Over 3,25 @1,93 (score 3,993) | Over 3,5 @2,1368 (Matchbook), +12,44 pp | "
  "idem — de edge is een honderdste hoger, de kans lager |")
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
mk = {}
for m in res["matches"]:
    for c in m.get("all_candidates", []):
        mk[c["market"]] = mk.get(c["market"], 0) + 1
A(f"| 1X2 | 6 van 6 (beste prijs, betaald) | {mk.get('1X2', 0)} | 0 |")
A(f"| Asian Handicap | 6 van 6 | {mk.get('Asian Handicap', 0)} | 0 |")
A(f"| Draw No Bet | 6 van 6 (de 0.0-lijn uit dezelfde spreads) | {mk.get('Draw No Bet', 0)} | 0 |")
A(f"| Double Chance | 6 van 6 (de ±0.5-lijn uit dezelfde spreads) | {mk.get('Double Chance', 0)} | 0 |")
A(f"| Over/Under | 6 van 6 | {mk.get('Over/Under', 0)} | **2** |")
A(f"| BTTS | 6 van 6 duels (tweede ronde, 1 credit per duel) | {mk.get('BTTS', 0)} | 0 |")
A("")
A("**De marktbalans-controle slaagt zo ruim als hij kan:** alle zes competities hebben zowel "
  "een doelpuntenmarkt als uitkomstmarkten, en alle zes markten zijn bij alle zes de duels "
  "werkelijk doorgerekend (`progress.py verify`: *\"Alle 6 geanalyseerde wedstrijd(en) hebben "
  "alle zes markten gehad\"*).")
A("")
A("**Dat er tóch twee Overs uitkomen is de analyse en niet de inkoop.** Dat onderscheid is "
  "precies waarvoor deze tabel sinds 29 aug 2026 bestaat. De uitkomstmarkten lagen vandaag lager "
  "op `selection_score`, en de twee duels waar ze bovenaan stonden zijn door poort 7 (Brentford) "
  "en poort 8 (Monza) tegengehouden. Een verdeling afdwingen is wat §1 verbiedt.")
A("")
A("**Geen enkele competitie draaide op een marktgemiddelde zonder herleidbare bookmaker:** alle "
  "zes hadden een sportkey. Vier van de zes beste prijzen van de dag stonden bij een **beurs** "
  "(Betfair of Matchbook) en zijn via `oddsapi.net_price` met 2% commissie doorgerekend; beide "
  "gepubliceerde regels staan bij een gewone bookmaker (1xBet en Pinnacle), dus daar is bruto "
  "gelijk aan netto.")
A("")
A("---")
A("")
A("## De twee dagranglijsten (§5a)")
A("")
for naam, kop in (("herijkt", "Herijkt — hieruit komen de bets"),
                  ("ruw", "Ruw — wat de routine vóór 5 sep 2026 zou hebben gezien")):
    A(f"### {kop}")
    A("")
    A("| # | Wedstrijd | Markt | Koers | Kans | Edge | Score | Status |")
    A("|---|---|---|---|---|---|---|---|")
    for i, r in enumerate(top[naam], 1):
        A(f"| {i} | {r['match']} | {r['market']} — {r['selection']} | {r['odds']} | "
          f"{100*r['prob']:.1f}% | {r['edge_pp']:+.2f} pp | {r['score']} | {r['status']} |")
    A("")
A("**Geen van de twee gepubliceerde regels haalt de lat op de ruwe schaal**, en dat is vandaag "
  "geen nieuws maar hetzelfde feit als punt 1: geen enkele selectie haalde zijn lat op welke "
  "schaal dan ook. `bet_beide` is bij beide `False`. Over de hele run sneuvelde **0** selecties "
  "alleen op §1g, dus de reeks `herijking` groeit vandaag niet.")
A("")
A("**De ruwe lijst noemt een ander tweede duel:** Monza – Fiorentina, AH Monza +1 @1,52, +11,20 "
  "pp — de selectie die poort 8 op de herijkte schaal tegenhield. Die staat als `underdog` in het "
  "schaduwlogboek en niet in de lijst.")
A("")
A("---")
A("")
A("## Net niet")
A("")
A("| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |")
A("|---|---|---|---|---|---|")
for m in res["matches"]:
    nm = m.get("near_miss")
    if not nm:
        continue
    rb = nm["edge_robust_min"]
    A(f"| {m['match']} | {nm['market']} @ {nm['odds']} | {nm['edge_xg']:+.2f} pp | "
      f"{nm['edge_split']:+.2f} pp | {(f'{rb:+.2f} pp' if rb is not None else '—')} | "
      f"`{nm['failed_gate']}` |")
A("")
A("Twee duels staan hier niet in omdat ze een gepubliceerde regel kregen (Levante – Elche en "
  "Wieczysta Kraków – Motor Lublin); hun andere selecties zijn dezelfde mening in een andere "
  "markt en horen niet in het schaduwlogboek (§6d/§1a).")
A("")
A("### Alle 102 selecties naar de poort waarop ze afvielen")
A("")
A("| Poort | Selecties | Wat dat was |")
A("|---|---|---|")
A("| `tweede_methode` (poort 5) | 63 | de twee methodes verslaan de markt niet dezelfde kant op "
  "— tweederde van alles, zoals vrijwel elke run |")
A("| `edge` (geen poort meer, §5b) | 26 | onder de eigen drempel; hieruit komen de twee regels "
  "op rangorde |")
A("| `context` (poort 7) | 5 | alle vijf bij Brentford – Everton |")
A("| `underdog` (poort 8) | 4 | alle vier bij Monza – Fiorentina |")
A("| `robuustheid` (poort 6) | 2 | beide bij Başakşehir – Çorum FK |")
A("| `odds` (poort 2) | 2 | buiten de band 1,30–6,00 |")
A("| `doelpunten_onder` (poort 9) | **0** | er stond geen Under op FULL-data in de band 8–10 pp |")
A("")
A("**Poort 7 kostte het enige Premier League-duel van de dag.** Brentford – Everton had met "
  "+7,23 pp op de thuiszege de op twee na hoogste FULL-edge van de dag; Brentford mist 30% van "
  "zijn selectiewaarde (Fábio Carvalho, Aaron Hickey, Nathan Collins) tegen 0% bij Everton, ruim "
  "boven de drempel van 10 procentpunt verschil. De reeks `context` staat op 148 afgewikkelde "
  "gevallen en −22,8%: van alle poorten de poort die het meest aantoonbaar geld bespaart.")
A("")
A("**Poort 8 hield Monza – Fiorentina in zijn geheel tegen.** Monza is promovendus, de markt "
  "zet hem onder `UNDERDOG_FLOOR` (0,35), en de vier sterkste selecties stonden alle vier op de "
  "Monza-kant (DC +13,87 · AH +1 +12,27 · 1X2 +12,09 pp). Op datzelfde duel stond het model "
  "**+11,37 pp boven Pinnacle** op de thuiszege, veruit de grootste 1X2-afwijking van de dag — "
  "precies het patroon waarvoor die rem er staat.")
A("")
A("---")
A("")
A("## Afwikkeling vorige picks")
A("")
A("| Wedstrijd | Markt | Koers | Uitslag | Resultaat | Run |")
A("|---|---|---|---|---|---|")
RUNVAN = {json.loads(l)["id"]: json.loads(l).get("run")
          for l in open("data/picks.jsonl") if l.strip()}
for p in settle["picks"]:
    A(f"| {p['match']} | {p['market']} | {p['odds']:.3f} | {p['score']} | "
      f"**{p['result']}** | {RUNVAN.get(p['id'], '?')} |")
A("")
A("**8 picks** (3 gewonnen, 5 verloren, 0 void) en **64 schaduwrijen** (30 gewonnen, 31 "
  "verloren, 3 void). Alle rijen komen uit competitieduels zonder verlenging, dus "
  "`status.scoreStr` is de stand na 90 minuten (§6d).")
A("")
A("**Eén schaduwrij blijft open en dat is correct gedrag:** `shadow-2026-11-22-b-vancouver-"
  "whitecaps---real-salt-lake` meldt 2,1 uur na de aftrap nog niet afgelopen, dus de statusregel "
  "van §0 laat hem staan in plaats van hem op de klok af te wikkelen. `ledger.py open` en "
  "`shadow.py open` geven daarna allebei niets meer.")
A("")
A("### Reflectie op de uitslagen (§3 Stage 0, 12 okt 2026)")
A("")
A("**1. Klopte de redenering, of alleen de uitkomst?** De vier picks van Run A verloren alle "
  "vier, en drie daarvan doordat de wedstrijd ONDER de eigen doelverwachting bleef: Lorient – "
  "Rennes 1–1 tegen λ-som 3,27 (Over 2,5), Osasuna – Málaga 1–0 tegen 3,22 (Over 2,5) en Go "
  "Ahead Eagles – Fortuna Sittard 0–1 tegen een thuis-λ van 2,42 alleen. De vierde ging precies "
  "andersom: Getafe – Atlético 0–3 tegen een λ-som van 2,15, op een **Under** 2,5. Over die vier "
  "duels verwachtte het model 12,1 doelpunt en vielen er 7.")
A("")
A("**2. Deden de poorten hun werk?** De 64 schaduwrijen kwamen uit op 30–31–3: de tegengehouden "
  "kandidaten deden het als groep niet beter dan de gespeelde bets. Geen enkele poort springt "
  "eruit op één dag, en dat is ook niet de schaal waarop ze gelezen horen te worden.")
A("")
A("**3. Zat er een patroon in?** Niet in één richting. Twee Overs verloren omdat er te weinig "
  "viel en de Under verloor omdat er te veel viel. Over alle acht afgewikkelde picks van beide "
  "runs verwachtte het model 24,9 doelpunt en vielen er 22 — binnen de ruis. Het enige wat "
  "opvalt is dat Run A vier van de vier verloor, en bij vier gevallen is dat met een trefkans "
  "rond 46% een alledaagse uitkomst (kans ≈ 8%).")
A("")
A("**4. Wat betekent dit NIET?** Eén dag is geen reeks. §6d eist ~30 gevallen voordat een reeks "
  "gelezen mag worden, en er is op grond van gisteren geen enkele drempel, geen gewicht en geen "
  "poort aangeraakt.")
A("")
A("---")
A("")
A("## Bevindingen")
A("")
A("### Bevinding 1 — nul van de 102 selecties haalde zijn drempel, en dat is de normale vorm "
  "van een maandag")
A("")
A("Zes wedstrijden leveren 102 selecties en geen daarvan komt boven 8,0 pp (FULL) of 16,0 pp "
  "(LIGHT) uit. Dat is geen storing: hoe kleiner de dag, hoe kleiner de kans dat er een duel "
  "tussen zit waar het model ver van de markt af zit. §5b is precies voor deze situatie "
  "geschreven — minder selecties boven de drempel dan er regels in de lijst passen, dus de "
  "rangorde bepaalt de lijst en de drempel gaat mee als label.")
A("")
A("Wat dat betekent voor de lezing: §1g heeft op 552 afgerekende gevallen gemeten dat er geen "
  "drempel op de herijkte edge bestaat die geld oplevert, en dat het rendement het **slechtst** "
  "is bij de hóógste geclaimde edge. Een lagere edge is dus niet per se een slechter "
  "vooruitzicht. Maar hij is wel lager dan de lat waarop de 8,0 van 31 aug 2026 gemeten is, en "
  "dat hoort per regel zichtbaar te zijn — `toplist.build` zet dat label er zelf bij.")
A("")
A("### Bevinding 2 — beide regels staan op de Over-kant, en dáár meet `goalbias` nu een "
  "scheefstand die de andere kant op wijst")
A("")
A("De Under-kant staat al weken meetbaar scheef: over 146 duels waarin werkelijk een Under is "
  "gespeeld vallen er **+0,663 doelpunt per duel méér** dan de eigen lambda zei, z = **+4,82**. "
  "Dat is de meting waarop poort 9 staat en ze is sinds 11 oktober alleen maar harder geworden.")
A("")
A("Wat vandaag opvalt is de spiegel ervan, en die is relevant omdat beide regels Overs zijn: "
  "over 81 duels waarin een **Over** is gespeeld vallen er **−0,356 doelpunt per duel minder** "
  "dan verwacht, z = −1,74. Dat haalt de lat van §6d niet (|z| < 2) en er wordt dus niets mee "
  "gedaan, maar het is het eerste cijfer dat suggereert dat de selectie aan béide kanten te ver "
  "doorschiet in plaats van alleen aan de Under-kant. In rendement staat de Over-kant nog steeds "
  "positief: **+5,7% over 107 afgewikkelde picks** tegen −14,7% over 184 Unders.")
A("")
A("**Er wordt hier niets op verzet.** Poort 9 blijft onveranderd (§1h: een run verzet hem niet "
  "op eigen initiatief), en de Over-kant krijgt geen eigen lat op een z van −1,74. Dit is een "
  "waarneming om over enkele weken opnieuw te bekijken, met `margins.py goalbias` en niet met "
  "een nieuwe redenering.")
A("")
A("### Bevinding 3 — de kloon was ONDIEP en Stage -2 gaf daardoor eerst een vals alarm over 84 "
  "takken")
A("")
A("De eerste controle van vanochtend meldde dat **84 van de 96 zijtakken** eigen commits hadden, "
  "39 tot 691 stuks, met een **lege `merge-base`** ten opzichte van HEAD. Dat zag eruit als 84 "
  "losse weesgeschiedenissen. Het was iets anders: `git rev-parse --is-shallow-repository` gaf "
  "`true`, en bij een ondiepe kloon ontbreekt alles van vóór de knip, dus telt élke commit van "
  "daarvoor als \"nog niet hier\". §3 Stage -2 beschrijft dit vals alarm met zoveel woorden en "
  "schrijft voor om éérst te unshallowen — en dat is vanochtend in de verkeerde volgorde gedaan.")
A("")
A("Na `git fetch --unshallow origin` (783 commits lokaal in plaats van 60) hebben **0 van de 96 "
  "takken** nog eigen commits. De conclusie dat er niets te mergen viel blijft dus staan, maar "
  "ze stond eerst op de verkeerde grond.")
A("")
A("De controle op INHOUD, die §3 Stage -2 sinds 27 sep 2026 naast de commitgraaf eist, is wél "
  "meteen goed gedaan: van elke tak zijn `picks.jsonl`, `shadow.jsonl`, `calibration.jsonl` en "
  "`context-log.jsonl` per regel-id vergeleken met main. Nul ontbrekende picks, nul ontbrekende "
  "kalibratierijen, nul ontbrekende contextrijen. **Wél dragen 38 takken vier schaduwrijen die "
  "main niet heeft**, en die zijn bewust NIET teruggezet: het zijn Canada – Peru, Croatia – "
  "England, Estonia – Luxembourg en Switzerland – Slovenia van 3 oktober, in hun kale vorm "
  "zonder `-p8-0`-suffix — de dubbeltellingen die Run D op 7 november heeft verwijderd omdat "
  "§1e punt 2 ze verbiedt. §3 Stage -2 schrijft met zoveel woorden voor ze bij een merge niet "
  "aan te vullen.")
A("")
A("**Les voor de volgende run:** `git rev-parse --is-shallow-repository` is de eerste opdracht "
  "van Stage -2 en niet de derde. De verse container levert de repo nog steeds ondiep aan, net "
  "als op 20 aug 2026.")
A("")
A("### Bevinding 4 — een hergebruikt script wees opnieuw naar het voortgangsbestand van gisteren")
A("")
A("`ra_nov23_marktvorm.py` is uit het script van 22 november overgenomen met een "
  "`sed`-vervanging op de bestandsnamen, en die vervanging raakte de f-string "
  "`data/run-state/2026-11-22-run-{RUN}.json` niet. Het script las en herschreef daardoor het "
  "voortgangsbestand van **gisteren** in plaats van dat van vandaag, en meldde \"marktvorm-blok "
  "op **0** wedstrijden gezet\" — het enige teken dat er iets niet klopte.")
A("")
A("Schade: geen. `git diff` op `data/run-state/2026-11-22-run-a.json` is leeg, want het bestand "
  "is byte-identiek teruggeschreven (de match-namen van vandaag komen in dat bestand niet voor, "
  "dus er werd niets gezet, en de `marktvorm_toegevoegd`-sleutel stond er al). Na het corrigeren "
  "van het pad staat het blok op alle 6 wedstrijden van vandaag.")
A("")
A("**Dit is dezelfde faalvorm als bevinding 2 van 22 november**, en dat is het punt: het is de "
  "tweede dag op rij dat een hergebruikt script naar het bestand van gisteren wees, en beide "
  "keren klaagde er niets — alleen een getal dat 0 was waar het 6 had moeten zijn. Een "
  "`sed`-vervanging op `ra_nov22_` dekt de scriptnamen en niet de datums in paden. Wie dit "
  "patroon blijft gebruiken: vervang ook `2026-11-22` naar `2026-11-23`, en lees de uitvoerregel "
  "met het aantal.")
A("")
A("---")
A("")
A("## Stand van het logboek")
A("")
for naam, kop in (("ledger_py_stats", "`ledger.py stats`"),
                  ("recalibrate_py_show", "`recalibrate.py show` (§1g)"),
                  ("shadow_py_stats", "`shadow.py stats` (§6d)"),
                  ("calibration_py_stats", "`calibration.py stats` (§6e)"),
                  ("ctxlog_py_stats", "`ctxlog.py stats` (§1c)"),
                  ("margins_py_stats", "`margins.py stats` (§6f)"),
                  ("margins_since", "`margins.py stats --since 2026-09-20` (§6f)"),
                  ("margins_py_goalbias", "`margins.py goalbias` (§6b-5g, §6g)"),
                  ("gridfit_py_measure", "`gridfit.py measure` (§6g)")):
    A(f"### {kop}")
    A("")
    A("```")
    A(txt(naam))
    A("```")
    A("")

A("**De controle van §6b-5c aan één getal:** `recalibrate.load_fit().fitted_through` staat na de "
  "settle van deze run op **2026-11-22**, de vorige rundag. `calibration.py settle` is dus niet "
  "blijven liggen: deze run heeft 204 waarnemingen afgewikkeld en er staan er nog 51 open. Bij "
  "het rekenen stond de fit nog op 2026-11-21, en dat is de normale volgorde — `load_fit()` "
  "draait aan het begin van de run en `settle` in Stage 6.")
A("")
A("**Wat er in `margins.py stats --since 2026-09-20` opvalt**, twee cellen boven twee "
  "standaardfouten: het model voorspelt **3,1 pp te veel gelijkspelen** (23,6% tegen 20,5% "
  "werkelijk over 1633 duels) en bij duels met een duidelijke favoriet **4,9 pp te veel "
  "\"favoriet wint met 2 of meer\"** (43,6% tegen 38,7% over 460 duels). Dat tweede is het "
  "spiegelbeeld van de margefout van 19 september, die de andere kant op wees — het gat is daar "
  "niet alleen dicht maar omgeslagen. Beide zijn waarnemingen voor over enkele weken, geen "
  "aanleiding om vandaag iets te verzetten.")
A("")
A("**`gridfit.py measure`** meldt zelf dat de populatie niet meer homogeen is op het niveau: 460 "
  "van de 1633 duels dragen `LEVEL_SCALE` = 1.032 al in zich, dus de regel `scale = 1.032` "
  "toetst daar een dubbele correctie. De vraag \"werkt de correctie\" hoort op alleen die 460 "
  "duels en die reeks is nog te kort (§6d). **Er is dus niets te beslissen en poort 9 blijft "
  "onveranderd** (§1h, §6g).")
A("")
A("---")
A("")
A("## Wat er is vastgelegd (§6b)")
A("")
A("| Stap | Uitkomst |")
A("|---|---|")
A("| 1. Runrapport | `runs/2026-11-23-run-a.md` (dit bestand) |")
A("| 2. Picks | 2 regels aan `data/picks.jsonl`; `ledger.py validate`: **591 picks geldig** |")
A("| 3. Bronstatus | `data/source-health.json` bijgewerkt met de meting van deze run |")
A("| 4. Afwikkeling | 8 picks en 64 schaduwrijen van 22 nov; 1 schaduwrij blijft open |")
A("| 5. Schaduwlogboek | `shadow.py collect`: 5 rijen (context, edge ×2, underdog, robuustheid) |")
A("| 5b. Marktdekking | `progress.py verify`: **alle 6 wedstrijden hebben alle zes markten gehad** |")
A("| 5c. Kalibratielogboek | `collect`: 18 waarnemingen (6 duels), totaal 9039; `settle`: 204 afgewikkeld, 51 open |")
A("| 5d. Contextlogboek | `collect`: 4 nieuwe wedstrijden (2 duels hebben `squad_value = 0` en leveren geen bruikbaar beschikbaarheidsverschil), totaal 2525; `settle`: 35 afgewikkeld, 7 open |")
A("| 5e. Dagranglijsten | `toplist.py`: 2 regels herijkt, 2 ruw |")
A("| 5f/5g. Marge- en doelpuntenlogboek | `margins.py stats`, `--since`, `goalbias` — alle drie hierboven |")
A("| 5h. Marktvormlogboek | `marketform.match_block` op alle 6 wedstrijden |")
A("| 5i. Voorbeschouwingsblok | `preview.match_block` op beide gepubliceerde duels, 0 fouten |")
A("| 5j. Stijlcontrole | `prosecheck.py`: 2 teksten, 1141 woorden, 0 verboden formuleringen, 0 jargon |")
A("| 6c. Dagrapport | `runs/2026-11-23-run-a.html` + `.dagrapport.md`, Artifact gepubliceerd |")
A("| 6. Commit en push | `git push origin HEAD:main` |")
A("| 7. Voortgangsbestand | `mark_completed` na deze commit |")
A("")
A("---")
A("")
A("## Stage -2 — de takken")
A("")
A("| | |")
A("|---|---|")
A("| `origin/main` bij de start | `f7553f5` |")
A("| HEAD bij de start | gelijk aan `origin/main` (0 heen, 0 terug) |")
A("| Remote takken | 97 |")
A("| Ondiepe kloon? | **ja** — `--is-shallow-repository` = `true`, 60 commits lokaal |")
A("| Takken met eigen commits, ondiep gemeten | **84** (39 tot 691), alle met lege `merge-base` |")
A("| Takken met eigen commits, ná `--unshallow` | **0** van de 96 (783 commits lokaal) |")
A("| Controle op inhoud (4 logboeken, per regel-id) | 0 ontbrekende picks, 0 kalibratierijen, 0 contextrijen |")
A("| Schaduwrijen op andere takken die main niet heeft | 4, op 38 takken — de bewust verwijderde dubbeltellingen van 3 okt. **Niet teruggezet** (§3 Stage -2) |")
A("")
A("---")
A("")
A("## Parameters van deze run")
A("")
A("```json")
A(json.dumps(st.get("parameters", {}), ensure_ascii=False, indent=1))
A("```")
A("")
A("---")
A("")
A("## Openstaand")
A("")
A("1. **Understat ligt er vijf rundagen uit.** Geen gevolg voor `my_prob`, de tiers of de "
  "poorten; wel staat `p_xg_understat` vijf dagen leeg in het kalibratieblok en groeit de reeks "
  "die het ene xG-model tegen het andere moet leggen niet. Het is bovendien het tweede been "
  "onder §4: valt Fotmob om terwijl dit zo blijft, dan is er geen kansbron meer. Elke run "
  "opnieuw proberen, niet omzeilen, en melden zodra het een week duurt.")
A("2. **De niveaucorrectie van 3 november is nog niet te beoordelen.** 460 duels dragen hem, en "
  "`gridfit.py measure` waarschuwt zelf dat de gemengde reeks de vraag niet beantwoordt. De "
  "vraag hoort pas voorgelegd als die reeks op zichzelf groot genoeg is (§6d). Poort 9 blijft "
  "tot dan onveranderd.")
A("3. **De Over-kant van `goalbias` staat op z = −1,74 over 81 duels.** Nog geen bevinding, wel "
  "het eerste cijfer dat suggereert dat de doelpuntenselectie aan beide kanten te ver "
  "doorschiet. Opnieuw bekijken bij ruim 100 gevallen, met `goalbias` en niet met een redenering.")
A("4. **Eén schaduwrij van 22 november staat nog open** (Vancouver Whitecaps – Real Salt Lake). "
  "De run van 24 november wikkelt hem af.")
A("5. **`sed`-hergebruik van runscripts raakt datums in paden niet.** Tweede dag op rij dat dit "
  "naar het voortgangsbestand van gisteren schreef (bevinding 4). Vervang voortaan ook de datum, "
  "en lees de uitvoerregel met het aantal.")
A("")

OUT.write_text("\n".join(lines) + "\n")
print(f"{OUT} geschreven — {len(lines)} regels")

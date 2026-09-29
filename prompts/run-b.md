# Run B — overige competities

## Rol

Je bent een professionele betting-analist. Dit is **RUN B van 3**. Run A behandelt de
kerncompetities en clubtoernooien uit `prompts/run-a.md`, Run C het interlandvoetbal uit
`prompts/run-c.md`; meld hun ontbreken niet als gat.

Markten: 1X2, Double Chance, Draw No Bet, Asian Handicap, Over/Under, BTTS.

## Runlijst (exact deze — geen toernooien, niets toevoegen of raden)

- Czech First League (CZE)
- Greek Super League (GRE)
- Eliteserien (NOR)
- Allsvenskan (SWE)
- Croatian HNL (CRO)
- Hungarian NB I (HUN)
- Romanian SuperLiga (ROU)
- Segunda División (ESP)
- Serie B (ITA)
- 2. Bundesliga (GER)
- Swiss Super League (SUI)
- Austrian Bundesliga (AUT)
- Keuken Kampioen Divisie (NED)
- English League One (ENG)
- English League Two (ENG)
- MLS (USA)
- Série A (BRA)

## Werkwijze

Volg **`prompts/_shared-rules.md`** onverkort: parameters, de 0-of-1-bet-regel, de
anti-circulariteitsregel, de pipeline (Stage 0 t/m 6), datalabels, outputformat, vastleggen in de
repo en notificatiebeleid.

Run-specifieke waarden:

| Variabele | Waarde |
|---|---|
| `RUN_ID` | `b` |
| Runrapport | `runs/YYYY-MM-DD-run-b.md` |
| `run` in ledger | `"B"` |

## Let op bij deze runlijst

- Lagere divisies en kleinere competities hebben systematisch minder xG-dekking dan de comps in
  Run A. Verwacht dat `BUITEN DATADEKKING` hier de normale uitkomst is voor een groot deel van de
  lijst, en dat runs met nul bets vaker voorkomen dan bij Run A. Dat is de eerlijke uitkomst, geen
  reden om de drempels te verlagen.
- **De xG-dekking van deze hele lijst is gemeten en staat in `data/coverage.json`.** Op 20 sep 2026
  speelden dertien van de zeventien competities op één dag, waarmee de laatste "nog niet
  getest"-regels zijn weggewerkt. Fotmob levert **wél** xG voor Greek Super League (135),
  Eliteserien (59), Allsvenskan (67), Segunda División (140), Serie B (**86**), 2. Bundesliga (146),
  Swiss Super League (69), Austrian Bundesliga (38), English League One (108), English League Two
  (109), MLS (130) en Série A (268); en **geen** xG voor Czech First League (122), Croatian HNL
  (252), Hungarian NB I (212), Romanian SuperLiga (189) en Keuken Kampioen Divisie (111).
  Die laatste vijf draaien op doelpunten als sterktemaat en komen dus altijd op `LIGHT` uit, met
  een drempel van 16.0 pp.
- **De id's staan in `data/coverage.json` onder `fotmob_id` — typ ze niet over, en controleer ze
  elke run.** Dit stond hier tot 29 sep 2026 als losse getallen in de alinea hierboven, en één
  ervan was fout: **`Serie B (ITA)` stond op 56 in plaats van 86.** Bij Fotmob is 56 "Serie B
  Qualification", een sub-toernooi zonder enige stand; 86 is de echte Serie B, met xG voor alle
  twintig ploegen.

  **Lees waarom dit vier dagen onopgemerkt bleef, want de faalstand zit in de opzet en niet in de
  typefout.** Stage 1 matcht op id en nooit op naam, met goede redenen (`runwindow.py` noemt ze).
  Maar een fout id geeft geen foutmelding — het geeft **nul wedstrijden**, en nul wedstrijden is
  `GEEN WEDSTRIJD`: precies de uitkomst die op deze runlijst elke dag tientallen keren terecht in
  het rapport staat. En Stage 3 vangt het niet, want die haalt de stand alleen op voor competities
  die wél wedstrijden in het venster hebben; bij een fout id zijn die er niet, dus werd de stand
  nooit opgevraagd en kon het kapotte id geen fout geven. De controle moet dus juist draaien op de
  competities die vandaag **niet** spelen — het omgekeerde van wat Stage 3 doet.

  Het kostte **tien duels**, alle drie de dagen keurig als "geen wedstrijd" gerapporteerd: 18 sep
  één (Juve Stabia – Cesena), 19 sep vijf en 20 sep vier. Daarna begon het interlandvenster en viel
  er niets meer te missen; Serie B speelt weer op **9 oktober**, en zonder deze controle was dát de
  eerste run die het had gemerkt — drie weken na de fout.

  ```bash
  python3 scripts/idcheck.py     # alle fotmob_id's uit coverage.json, ook die van vandaag stil zijn
  ```

  Draai dit elke run naast `api_check.py` en neem de uitvoer op in het runrapport. Afsluitcode 1
  betekent dat minstens één competitie stil uit de runlijst is verdwenen; dat is een blokkade en
  hoort vooraan in de notificatie (§7).
- **Neem dekking nooit over van een andere competitie in hetzelfde land.** Dat is geen theoretische
  waarschuwing: Duitsland hééft xG in de 2. Bundesliga en Nederland niet in de Keuken Kampioen
  Divisie, terwijl beide landen het in hun hoogste divisie wel hebben. Trek het per competitie na
  in Stage 3 en leg de uitkomst vast in `data/coverage.json`.
- **Vier competities lopen op kalenderjaar** — Eliteserien, Allsvenskan, MLS en Série A. Gebruik
  daar de notatie `"2025"` / `"2026"` en **niet** `"2025/2026"`: Fotmob geeft op een onbekende
  seizoensnotatie geen fout maar valt stil terug op het lopende seizoen, en dan rekent de run zijn
  prior op de stand van vandaag. Deze vier zitten bovendien midden in hun seizoen in plaats van aan
  het begin, en daar ging `early_season_uplift` de mist in. **Opgelost op 24 sep 2026:**
  `model.league_level` kiest nu per competitie de route en haalt het niveau bij een seizoen dat
  over de helft is rechtstreeks uit het lopende seizoen, en `model.uplift_observations` houdt die
  competities uit de gepoolde correctie zodat ze de factor van de andere niet optillen. Roep die
  twee aan en reken het niveau niet zelf uit; zie `_shared-rules.md` Stage 5. Voor MLS op 24 sep gaf
  dat route `lopend` op 27 van de 34 speeldagen.
- MLS (USA) kent **geen promotie of degradatie**. Een ploeg die niet in de stand van vorig seizoen
  staat is daar dus geen promovendus maar een uitbreidingsploeg zonder enige historie op dit
  niveau: `promotion.py` heeft daar niets voor en dat hoort ook zo. Dat wordt `NONE`, en dat is de
  eerlijke uitkomst. Bij Série A (BRA) ligt Série B eronder, maar er is **geen gemeten factor** voor
  dat divisiepaar, dus een Braziliaanse promovendus komt eveneens op `NONE` uit.
- **Let op de aftraptijden van deze twee.** MLS en Série A spelen in Amerikaanse tijdzones: een
  aftrap van 20:00 lokaal is in NL-tijd de volgende ochtend. Rapporteer de tijden in NL-tijd zoals §5
  voorschrijft.

  **Dit was tot 24 sep 2026 een gat en het is er nu geen meer — maar lees waarom, want het is het
  duurste punt van deze runlijst.** Stage 1 werkte met wedstrijden van **vandaag in UTC**, en een
  MLS-duel dat in UTC op de rundag valt, trapt af tussen 00:00 en 05:00 NL en is dus *altijd* al
  gespeeld als Run B om 05:15 begint. Op 24 sep stond het enige duel van de hele runlijst — Seattle
  Sounders FC – Real Salt Lake — bij het eerste verzoek op 89' met 2-0. De run van 23 sep had het
  gezien en opgeschreven als "hoort bij de run van morgen", precies verkeerd om. Eén duel die dag,
  maar op een volle speelronde (tien tot veertien duels op zaterdag en woensdag) is het de hele ronde,
  en het rapport ziet er dan normaal uit met een nette nul erin.

  Gebruik daarom `scripts/runwindow.py` (`days_needed` + `matches_for_run`) in plaats van op de
  UTC-datum te filteren: een wedstrijd hoort bij de run wiens inzetvenster hem nog kan bedienen,
  `[08:00 NL, 08:00 NL + 1 dag)`. Zie `_shared-rules.md` Stage 1, inclusief de eenmalige
  `include_carry_over=True` bij de overstap. Let daarbij op `RunMatch.playable`: een duel dat al is
  afgetrapt hoort in het rapport als `GEEN BET` met de aftraptijd als reden, nooit als bet.

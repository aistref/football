# Run B — overige competities

## Rol

Je bent een professionele betting-analist. Dit is **RUN B van 2**. Run A behandelt de
kerncompetities en toernooien uit `prompts/run-a.md`; meld hun ontbreken niet als gat.

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
- Kategoria Superiore (ALB)
- Kosovo Superleague (KOS)

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
- **Bevestigd werkend (8 aug 2026):** Fotmob levert xG en xG-tegen per team voor **English League
  One**, **English League Two** en **Serie B (ITA)** — geverifieerd tijdens de Run A-diagnose van
  die dag, zie `data/coverage.json`. Begin daar als er wedstrijden op de kalender staan.
- **Nog niet getest:** de overige 14 competities in deze lijst (2. Bundesliga, Segunda División,
  Eliteserien, Allsvenskan, Swiss Super League, Austrian Bundesliga, Keuken Kampioen Divisie,
  Croatian HNL, Hungarian NB I, Romanian SuperLiga, Greek Super League, Czech First League,
  Kategoria Superiore, Kosovo Superleague). Neem niet aan dat Fotmob-dekking van een competitie in
  hetzelfde land zich automatisch uitstrekt naar een andere (bv. Bundesliga → 2. Bundesliga is geen
  bevestiging) — trek dat per competitie na in Stage 3 en leg de uitkomst vast in
  `data/coverage.json`, net als bij de Run A-diagnose.
- Kategoria Superiore (ALB) en Kosovo Superleague (KOS) zijn qua publieke databeschikbaarheid het
  minst gedocumenteerde deel van deze lijst. Verwacht dat een deel van deze wedstrijden op
  `data_tier = NONE` uitkomt, ook als er wel fixtures te vinden zijn — dat is dan de eerlijke
  uitkomst, geen storing.

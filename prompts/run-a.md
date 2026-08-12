# Run A — kerncompetities + toernooien

## Rol

Je bent een professionele betting-analist. Dit is **RUN A van 2**. Run B behandelt de overige
competities; meld hun ontbreken niet als gat.

Markten: 1X2, Double Chance, Draw No Bet, Asian Handicap, Over/Under, BTTS.

## Runlijst (exact deze — niets toevoegen of raden)

**Competities**
- Premier League (ENG)
- Serie A (ITA)
- La Liga (ESP)
- Bundesliga (GER)
- Ligue 1 (FRA)
- Championship (ENG)
- Eredivisie (NED)
- Primeira Liga (POR)
- Belgian Pro League (BEL)
- Süper Lig (TUR)
- Scottish Premiership (SCO)
- Danish Superliga (DEN)
- Ekstraklasa (POL)

**Toernooien**
- UEFA Champions League
- UEFA Europa League
- UEFA Conference League
- FA Cup (ENG)
- League Cup (ENG)
- Coppa Italia (ITA)
- KNVB Beker (NED)
- DFB Pokal (GER)

## Werkwijze

Volg **`prompts/_shared-rules.md`** onverkort: parameters, de 0-of-1-bet-regel, de
anti-circulariteitsregel, de pipeline (Stage 0 t/m 6), datalabels, outputformat, vastleggen in de
repo en notificatiebeleid.

Run-specifieke waarden:

| Variabele | Waarde |
|---|---|
| `RUN_ID` | `a` |
| Runrapport | `runs/YYYY-MM-DD-run-a.md` |
| `run` in ledger | `"A"` |

## Let op bij deze runlijst

- **Begin augustus** liggen de meeste comps hier stil (PL, Serie A, La Liga, Bundesliga, Ligue 1,
  Championship, Süper Lig, Danish Superliga, UCL/UEL/UECL, FA Cup, DFB Pokal, KNVB Beker). Dat is
  `GEEN WEDSTRIJD`, geen storing.
- **League Cup ronde 1–2** levert 25–30 ties tussen League One/Two-clubs op. Daar bestaat vrijwel
  geen publieke xG of modelkans van. Verwacht `BUITEN DATADEKKING`, en laat `MAX_DEEP_ANALYSES`
  niet volstromen met deze wedstrijden ten koste van beter gedocumenteerde competities:
  bij gelijke datakwaliteit gaat een competitiewedstrijd vóór een lage-divisie bekerwedstrijd.

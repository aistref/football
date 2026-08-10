# Run [A|B] — [YYYY-MM-DD]

**Gestart:** [tijd] CEST · **Bets gepubliceerd:** [n] · **Wedstrijden diep geanalyseerd:** [n] van [n] gekwalificeerd

## Dekkingsrapportage

| Competitie | Status | Toelichting |
|---|---|---|
| … | GEANALYSEERD / GEEN WEDSTRIJD / BUITEN DATADEKKING / AFGEKAPT | … |

**Afgekapt door `MAX_DEEP_ANALYSES`:** [n] wedstrijden — [welke, kort]

## Bronstatus deze run

| Bron | Status | Detail |
|---|---|---|
| … | ok / http_403 / js_only / … | … |

Wijzigingen t.o.v. vorige run: [bron X hersteld / bron Y omgevallen / geen]

## Wedstrijden

### [Thuis] – [Uit] · [aftrap] · [competitie]
- **Data:** FULL | LIGHT | NONE
- **Bet:** [markt + selectie] — Odds: best [x.xx] ([bron]) / target ≥ [x.xx]
- **Implied prob:** xx.x% • **My prob:** xx.x%
- **Edge:** +x.x pp • **Confidence:** High | Medium | Low
- **Inputs:** [onafhankelijke inputs met bron per cijfer]
- **Onderbouwing:** [max 5 zinnen]

<!-- of, bij geen bet: -->
### [Thuis] – [Uit] · [aftrap] · [competitie]
- **Data:** NONE
- **GEEN BET** — [reden in één regel]

## Topselectie

| # | Bet | Probability | Edge | Risicoklasse | Waarom deze |
|---|---|---|---|---|---|
| 1 | … | …% | +… pp | Low/Medium/High | … |

### Net niet

Elke afgewezen kandidaat met een echte edge, met het cijfer per poort. Ook invullen bij nul bets —
zie `_shared-rules.md` §5. Dezelfde cijfers gaan als `near_miss` in `data/run-state/`, waar
`scripts/report.py` de tabel op de HTML-pagina uit opbouwt.

| Wedstrijd | Markt @ koers | xG-model | 2e methode | Zwakste stand | Valt af op |
|---|---|---|---|---|---|
| … | … | +x.x pp | +x.x pp | +x.x pp | edge / robuustheid / tweede methode / odds / data |

Waren er geen kandidaten die in de buurt kwamen, schrijf dat dan met zoveel woorden — dat is een
ander soort dag dan een dag waarop er drie op een haar afvielen.

## Afwikkeling vorige picks

[Uitkomsten die deze run zijn vastgelegd, of "geen openstaande picks"]

## Stand van het logboek

Uitvoer van `python3 scripts/ledger.py stats`:

```
[plakken]
```

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.

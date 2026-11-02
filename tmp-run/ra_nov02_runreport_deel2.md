## Vastgelegd deze run (§6b)

| Stap | Commando / bestand | Uitkomst |
|---|---|---|
| 1 | `runs/2026-11-02-run-a.md` | dit bestand |
| 2 | `data/picks.jsonl` | 3 regels toegevoegd; `ledger.py validate` → **513 picks geldig** |
| 3 | `data/source-health.json` | bijgewerkt: Fotmob, The Odds API, BetExplorer, Pinnacle en `settling` op `ok`, **Understat op `onbereikbaar`**, `api_football` op `plan_limited` (besluit), en `toplist_dagranglijst` op `gerepareerd` |
| 4 | afwikkeling Stage 0 | 8 picks en 53 schaduwrijen verwerkt |
| 5 | `shadow.py collect --date 2026-11-02 --run a` | **9 rijen**: 3 × `edge`, 3 × `underdog`, 2 × `tweede_methode`, 1 × `context`. Nul op `doelpunten_onder`, `herijking` en `lijstlengte` |
| 5b | `progress.py verify --run a --date 2026-11-02` | **groen** — alle 12 wedstrijden hebben alle zes markten gehad |
| 5c | `calibration.py collect` + **`settle`** | 36 waarnemingen toegevoegd (12 duels), 234 afgewikkeld; 7047 van 7119 compleet. `fitted_through` = **2026-11-01** |
| 5d | `ctxlog.py collect` + `settle` | 11 duels toegevoegd (logboek op 1964), 77 afgewikkeld |
| 5e | `toplist.py --run a --date 2026-11-02` | twee ranglijsten van 3 regels, hierboven opgenomen |
| 5f | `margins.py stats` (+ `--since 2026-09-20`) | hieronder |
| 5g | `margins.py goalbias` | hieronder |
| 5h | `marktvorm`-blok via `marketform.match_block` | op alle 12 wedstrijden |
| 5i | `voorbeschouwing`-blok via `preview.match_block` | op alle 3 gepubliceerde bets, 0 fouten |
| 6 | `git push origin HEAD:main` | gelukt, geen botsing |
| 7 | `progress.py` `mark_completed` + `save` | na de push |

## Dagrapport (§6c)

- **HTML-pagina:** https://claude.ai/artifact/WrTKptPwewDDigqPnJuMf8
- **Tweede route (14 okt):** [`runs/2026-11-02-run-a.dagrapport.md`](https://github.com/aistref/football/blob/main/runs/2026-11-02-run-a.dagrapport.md)

**De rendercontrole van §6c (15 okt) is preventief gedraaid** met Chromium uit `/opt/pw-browsers`, in licht én donker:

| meting | licht | donker |
|---|---|---|
| `scrollHeight` van `body` | 16.300 px | 16.300 px |
| zichtbare tekst | 40.010 tekens | 40.010 tekens |
| zichtbare blokken (`h1,h2,p,table,div.bet`) | 47 | 47 |
| tabellen / betblokken | 6 / 3 | 6 / 3 |
| achtergrond / tekstkleur | `rgb(235,238,242)` / `rgb(20,26,33)` | `rgb(12,17,23)` / `rgb(230,235,241)` |
| console- en pagefouten | **0** | **0** |

De pagina rendert dus volledig en foutloos. Blijkt ze onbereikbaar, dan is opnieuw publiceren zinloos en is de Markdown-route het antwoord (§6c, 15 okt); de notificatie bevat beide links.

De drie voorbeschouwingen van §6c staan op de pagina onder de bets en zijn elk 300 tot 600 woorden, zonder rekentaal. Bij Atalanta – Parma staat de reeks die de bet **tegenspreekt** vooraan, zoals §6c punt 4 eist: 4–4 en 2–2 in de laatste twee duels, 4,6 doelpunten per wedstrijd over de laatste vijf, negen wedstrijden zonder de nul te houden, en een onderlinge historie van gemiddeld vier doelpunten per duel.


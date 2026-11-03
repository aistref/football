## Vastgelegd deze run (§6b)

| Stap | Commando / bestand | Uitkomst |
|---|---|---|
| 1 | `runs/2026-11-03-run-a.md` | dit bestand |
| 2 | `data/picks.jsonl` | 3 regels toegevoegd; `ledger.py validate` → **519 picks geldig** |
| 3 | `data/source-health.json` | bijgewerkt: Fotmob, The Odds API, BetExplorer, Pinnacle en `settling` op `ok`, **Understat op `onbereikbaar`** (tweede dag), `api_football` op `plan_limited` (besluit), en **`notes_bet_beide`** en **`marktvorm_lijn`** op `gerepareerd` |
| 4 | afwikkeling Stage 0 | 8 picks (4–4) en 18 schaduwrijen (9–7–**2 void**) verwerkt; niets bleef open |
| 5 | `shadow.py collect --date 2026-11-03 --run a` | **10 rijen**: 3 × `underdog`, 2 × `robuustheid`, 2 × `tweede_methode`, 2 × `edge`, 1 × `context`. Nul op `doelpunten_onder`, `herijking`, `underdog_ruw` en `lijstlengte` |
| 5b | `progress.py verify --run a --date 2026-11-03` | **groen** — 16 van 16 geanalyseerde wedstrijden hebben alle zes markten gehad; 2 overgeslagen op `tier = NONE`, 0 afgekapt |
| 5c | `calibration.py collect` + **`settle`** | 48 waarnemingen toegevoegd (16 duels), 87 afgewikkeld; 7134 van 7161 compleet. `fitted_through` = **2026-11-02** |
| 5d | `ctxlog.py collect` + `settle` | 18 duels toegevoegd (logboek op 1992), 24 afgewikkeld |
| 5e | `toplist.py --run a --date 2026-11-03` | twee ranglijsten van 3 regels, hierboven opgenomen |
| 5f | `margins.py stats` (+ `--since 2026-09-20`) | hieronder |
| 5g | `margins.py goalbias` | hieronder |
| 5h | `marktvorm`-blok via `marketform.match_block` | op 16 van de 18 wedstrijden (de twee `NONE`-duels niet) |
| 5i | `voorbeschouwing`-blok via `preview.match_block` | op alle 3 gepubliceerde bets, 0 fouten |
| 6 | `git push origin HEAD:main` | gelukt, geen botsing |
| 7 | `progress.py` `mark_completed` + `save` | na de push |

## Dagrapport (§6c)

- **HTML-pagina:** https://claude.ai/artifact/T6ng7HyFX5QT72wNpzaovz
- **Tweede route (14 okt):** [`runs/2026-11-03-run-a.dagrapport.md`](https://github.com/aistref/football/blob/main/runs/2026-11-03-run-a.dagrapport.md)

**De rendercontrole van §6c (15 okt) is preventief gedraaid** met Chromium uit `/opt/pw-browsers`, in licht én donker:

| meting | licht | donker |
|---|---|---|
| `scrollHeight` van `body` | 16.964 px | 16.964 px |
| zichtbare tekst | 41.141 tekens | 41.141 tekens |
| zichtbare blokken (`h1,h2,p,table,div.bet`) | 47 | 47 |
| tabellen / betblokken | 6 / 3 | 6 / 3 |
| achtergrond / tekstkleur | `rgb(235,238,242)` / `rgb(20,26,33)` | `rgb(12,17,23)` / `rgb(230,235,241)` |
| console- en pagefouten | **0** | **0** |

De pagina rendert dus volledig en foutloos. Blijkt ze onbereikbaar, dan is opnieuw publiceren zinloos en is de Markdown-route het antwoord (§6c, 15 okt); de notificatie bevat beide links.

De drie voorbeschouwingen van §6c staan op de pagina onder de bets en zijn 543, 562 en 602 woorden — de bovengrens van §6c is 600, dus die eerste staat twee woorden over en dat is hier opgeschreven in plaats van weggelaten. Bij **beide** Unders staat de reeks die de bet **tegenspreekt** vooraan, zoals §6c punt 4 eist: bij Bodø/Glimt – Lille vier van de zes Europese duels van deze twee ploegen boven de lijn en acht van de twaalf vorig seizoen; bij Barcelona – Aston Villa drie van drie en gemiddeld 5,67 doelpunt per duel. Geen van de drie teksten gebruikt het woord procentpunt, drempel, lat, edge, scheefstand of rangorde.

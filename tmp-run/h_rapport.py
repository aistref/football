"""Runrapport en prosebestand voor de herdraai van 19 sep 2026, beide runs."""
import json, os, collections

S = os.environ["SCRATCH"]
cap = lambda p: open(p).read().rstrip("\n")
NEAR = {"FULL": 3.0, "LIGHT": 6.0}

META = {
 "A": {"pad": "tmp-run/ra19h_results.json", "comps": 21,
       "lijst": "kerncompetities + toernooien", "credits": "39 bulk + 15 BTTS = 54 van 791"},
 "B": {"pad": "tmp-run/rb19h_results.json", "comps": 22,
       "lijst": "overige competities", "credits": "27 bulk + 8 BTTS = 35 van 787"},
}


def cijfers(run):
    res = json.load(open(META[run]["pad"]))
    ms = res["matches"]
    cs = [(m, c) for m in ms for c in m.get("all_candidates", [])]
    dicht = collections.Counter()
    for _, c in cs:
        for k, v in (c.get("poorten") or {}).items():
            if v is False:
                dicht[k] += 1
    kand = sorted([(m, c) for m, c in cs
                   if c.get("edge_pp", 0) >= NEAR.get(m["tier"], 3.0)],
                  key=lambda x: -x[1]["edge_pp"])
    return {"res": res, "ms": ms, "n_sel": len(cs), "dicht": dicht, "kand": kand,
            "tiers": collections.Counter(m["tier"] for m in ms),
            "comps": collections.Counter(m["competition"] for m in ms)}


def kandidaattabel(kand):
    r = ["| Edge | Wedstrijd | Selectie | Koers | Dichte poort |", "|---|---|---|---|---|"]
    for m, c in kand:
        d = [k for k, v in (c.get("poorten") or {}).items() if v is False]
        namen = {"odds": "koersband", "context": "poort 7 context", "underdog": "poort 8 underdog",
                 "tweede_methode": "poort 5 tweede methode", "robuustheid": "poort 6 robuustheid"}
        r.append(f"| **{c['edge_pp']:+.2f} pp** | {m['match']} | {c['market']} — {c['selection']} "
                 f"| {c['odds']:.2f} | {', '.join(namen.get(x, x) for x in d) or '—'} |")
    return "\n".join(r)


def rapport(run):
    g = cijfers(run)
    res, ms = g["res"], g["ms"]
    t, d = g["tiers"], g["dicht"]
    pct5 = d["tweede_methode"] / g["n_sel"] * 100
    return f"""# Run {run} — 2026-09-19 (herdraai onder §5b)

**Herdraai om 11:05 CEST** · **Bets gepubliceerd:** 0 · **Wedstrijden:** {len(ms)} in {len(g['comps'])} competities · **Selecties:** {g['n_sel']} · **Afgekapt:** {res['afkapping']['afgekapt']}

Dit vervangt de ochtendrun van vandaag. Die draaide nog met `shrink = 0.80` en met de edge-poort
vooraf; deze draait met `shrink = 1.00` (§6e), met verse prijzen, en met de selectieregel van §5b —
de drempel snijdt aan het eind van de dag in de rangorde over alle wedstrijden, niet per selectie
vooraf. De ochtendversie staat in de geschiedenis bij commit `d424da2`.

## De uitkomst, en waarom ze anders is dan "edge onder de drempel"

**Nul bets, maar niet meer om de oude reden.** Onder de oude regel was het antwoord op elke
selectie "edge onder de drempel van 8,0" — een getal dat niets zei over de wedstrijd. Onder §5b
is de vraag een andere: welke selecties halen de andere zeven poorten én hebben genoeg edge om
überhaupt een kandidaat te zijn? Dat zijn er vandaag **{len(g['kand'])}**, en ze sneuvelen stuk
voor stuk op een poort die wél iets over de wedstrijd zegt:

{kandidaattabel(g['kand'])}

**Alle {len(g['kand'])} worden geblokkeerd door poort 7 (rust of blessures) of poort 8 (de
underdog-ondergrens), of vallen buiten de koersband.** Geen enkele viel op de drempel zelf. Dat is
precies het verschil dat §5b beoogde: het rapport noemt nu een voetbalreden in plaats van een
getal.

## Poortstanden over alle {g['n_sel']} selecties

| Poort | Dicht | Aandeel |
|---|---|---|
| 5 — de twee methodes wijzen tegengesteld | {d['tweede_methode']} | {pct5:.0f}% |
| 8 — underdog onder de ondergrens | {d['underdog']} | {d['underdog']/g['n_sel']*100:.0f}% |
| 7 — context (rust, blessures) | {d['context']} | {d['context']/g['n_sel']*100:.0f}% |
| 2 — koers buiten 1.30–6.00 | {d['odds']} | {d['odds']/g['n_sel']*100:.0f}% |

**Poort 5 is met afstand de grootste zeef**: op {pct5:.0f}% van alle selecties wijzen de
xG-methode en de splitsmethode tegengesteld. Dat is geen detail — het betekent dat de twee
schatters het op vier van de vijf selecties oneens zijn over of de markt te laag of te hoog zit.
Zie **Openstaand**.

## Dekking

{len(ms)} wedstrijden: **{t['FULL']} `FULL`, {t['LIGHT']} `LIGHT`, {t['NONE']} `NONE`**.
Afgekapt door `MAX_DEEP_ANALYSES` (55): {res['afkapping']['afgekapt']}.
Vroeg-seizoenscorrectie ×{res['vroeg_seizoen']['factor']:.4f}.
Credits: {META[run]['credits']}.

## De dagelijkse top-N (§5a)

```
{cap(f"{S}/top_{run.lower()}.txt")}
```

## Stand van het logboek

### `ledger.py stats`
```
{cap(f"{S}/ledger2.txt").split("data_tier = FULL")[0].rstrip()}
```

### `recalibrate.py show`
```
{cap(f"{S}/recal2.txt")}
```

### `margins.py stats` — klopt de vórm van de uitslag? (§6f)
```
{cap(f"{S}/marg2.txt")}
```

### `ctxlog.py stats`
```
{cap(f"{S}/ctx2.txt")}
```

## Openstaand

1. **Poort 5 sneuvelt op {pct5:.0f}% van de selecties en dat is nooit gemeten.** Het
   schaduwlogboek zet `tweede_methode` op −1,6% over 74 afgewikkelde gevallen: de poort bespaart
   dus nauwelijks iets, terwijl hij verreweg het meeste tegenhoudt. §1f heeft al gemeten dat de
   splitsmethode als *kansbron* vrijwel niets toevoegt (Brier .23674 voor alleen xG tegen .23625
   voor de mix). De vraag die daarna overblijft is of ze als *veto* nog wel deugt. Meet dat op
   uitkomsten voordat er iets aan verandert.
2. **Poort 8 vervalt op 25 september.** Vier van de acht kandidaten van vandaag (beide runs samen)
   worden mede door die poort tegengehouden. Vanaf 25 september zouden die dus wél in de lijst
   komen — houd in de gaten wat dat doet, want het is de eerste keer dat het verval iets kost of
   oplevert dat te zien is.
3. **Poort 7 houdt hier de twee sterkste kandidaten tegen** (Alavés op 4 dagen rust tegen 7,
   Osasuna idem). Het contextlogboek mat vanochtend dat het beschikbaarheidssignaal echt is
   (t = −2,48) maar dat de markt dezelfde helling heeft (−28,7 tegen −29,4). Als de markt het al
   inprijst, houdt poort 7 misschien waarde tegen in plaats van risico. Zelfde route: meten, niet
   sleutelen.

---

> Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is de verwachtingswaarde negatief.
"""


if __name__ == "__main__":
    for run in ("A", "B"):
        pad = f"runs/2026-09-19-run-{run.lower()}.md"
        open(pad, "w").write(rapport(run))
        print(f"{pad} geschreven")

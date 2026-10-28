"""Is de vormfout van §6g te repareren? — de vaste meting die die vraag beantwoordt.

Aanleiding: op **28 oktober 2026** gaf de gebruiker opdracht keuze **(a)** van 11 oktober uit te
voeren — de vormfout in `score_grid` repareren. §6g zet daar zelf één voorwaarde bij: *"het is een
ingreep in `score_grid` zelf en raakt élke markt, niet alleen Unders — reken dus eerst door wat
het met de andere vijf doet."* Dit script is die doorrekening, en het staat in `scripts/` en niet
in `tmp-run/` omdat het antwoord met de steekproef meebeweegt: nu is het "nee, dit is ruis", en
over een paar maanden kan dat anders zijn. Dan is dit één commando in plaats van een ochtend werk.

```bash
python3 scripts/gridfit.py measure          # de volledige meting (netwerk, ~2 min, 0 credits)
python3 scripts/gridfit.py measure --all     # ook de lambdas van vóór de shrink-overstap
python3 scripts/gridfit.py selftest          # 12 controles, geen netwerk
```

## DE UITKOMST OP 28 OKTOBER 2026: NIET REPAREREN

Op 914 duels met lambdas van ná de shrink-overstap is **geen enkele kandidaat ingevoerd**, en dat
is een meting en geen terughoudendheid. Drie bevindingen, in volgorde van belang:

**1. De voorgeschreven reparatie kan het symptoom niet repareren waarvoor ze is voorgeschreven.**
§6g beschrijft de fout als "massa verschoven van 2 naar 4 en 5, en uit de extreme staart weg", en
de letterlijke uitvoering daarvan is massa uit de staarten naar het midden halen (`narrow`, b < 0).
Wat dat met de Under-lijnen doet:

| variant | P(Under 2.5) | fout | P(Under 3.5) | fout |
|---|---|---|---|---|
| huidig grid | 43,07% | **−2,48** | 64,66% | **−0,99** |
| narrow b = −0,010 | 43,04% | −2,45 | 65,22% | −1,55 |
| narrow b = −0,020 | 42,96% | −2,37 | 65,71% | −2,04 |
| narrow b = −0,040 | 42,72% | −2,13 | 66,55% | **−2,87** |
| scale = 1,032 | 41,03% | **−0,44** | 62,59% | +1,08 |

Op `Under 2.5` beweegt de reparatie 0,03 tot 0,35 procentpunt van een fout van 2,48, en op
`Under 3.5` gaat ze de **verkeerde kant** op.

### Waarom knijpen het symptoom verergert in plaats van verhelpt

Dat is geen pech maar rekenkunde, en het is het leerzaamste stuk van deze meting. De
totaalverdeling is **rechtsscheef**: een harde grens op nul en een lange staart naar boven.
Knijpen rond het gemiddelde haalt daarom **meer van de lange rechterstaart weg dan van de korte
linkerkant**, en dus zakt het gemiddelde mee:

| | λ = 2,7 | λ = 3,0 | λ = 1,7 |
|---|---|---|---|
| b = −0,010 | −0,024 | −0,026 | −0,016 |
| b = −0,020 | −0,043 | −0,047 | −0,029 |
| b = −0,040 | −0,071 | −0,076 | −0,051 |

Een **lager** verwacht totaal betekent een **hogere** `P(Under)`. De voorgeschreven reparatie
duwt het verwachte aantal doelpunten dus naar beneden, terwijl §6g juist meet dat het model al te
weinig doelpunten verwacht (+0,098 per duel) en `P(Under)` al te hoog zet. Ze verergert het
symptoom waarvoor ze is voorgeschreven. Alleen een **niveau**knop beweegt de Under-lijnen de
goede kant op.

`gridfit.py selftest` controleert die eigenschap expliciet — en de eerste versie van die controle
beweerde het omgekeerde ("laat het gemiddelde ongeveer staan") en viel om. Dát de controle
omviel, is de reden dat dit mechanisme is uitgezocht in plaats van aangenomen.

**2. En op een eerlijke scoringsregel maakt ze het model slechter, steeds erger naarmate de
correctie groter wordt.** Gepaarde toets per wedstrijd op de log loss van het werkelijke totaal:

| variant | winst | t | beter in |
|---|---|---|---|
| narrow b = −0,005 | −0,00083 | −1,05 | 65,6% van de duels |
| narrow b = −0,010 | −0,00214 | −1,37 | 65,1% |
| narrow b = −0,015 | −0,00391 | −1,66 | 64,7% |

Let op die laatste kolom, want ze is het leerzaamste cijfer van deze hele meting: de correctie
**wint in tweederde van de wedstrijden** en verliest toch gemiddeld. Ze wint dus vaak en klein, en
verliest zelden en groot — precies het spiegelbeeld van wat §6e bij `shrink` beschrijft ("wint
váker, maar als 0.8 wint, wint hij grōter"). Wie op "beter in 65% van de gevallen" had gekozen,
had een verslechtering ingevoerd.

**3. Elke gefitte kandidaat draait van teken tussen twee splitsingen van dezelfde 914 duels.**

| kandidaat | gefit op tijd → toets | gefit om en om → toets |
|---|---|---|
| rho | −0,00201 | +0,00294 |
| scale | +0,00183 | −0,00193 |
| shift | +0,00199 | −0,00430 |
| narrow | −0,00026 | +0,00027 |

en de gefitte waarden zelf net zo: rho +0,10 tegen −0,01, scale 1,024 tegen 1,040, shift +0,026
tegen +0,058. Een parameter die op de ene helft wint en op de andere evenveel verliest, met een
waarde die een factor twee verschilt, meet de ruis van de steekproef.

### De beslissende waarneming: élke kandidaat draait van teken tussen de twee populaties

De 803 duels met lambdas van vóór de overstap zijn de enige gegevens die bij het kijken naar de
914 geen rol speelden. Daar gebeurt dit:

| variant | op de 914 (ná de overstap) | op de 803 (vóór de overstap) |
|---|---|---|
| `narrow b = −0,005` | −0,00083 (t = −1,05) | **+0,00113 (t = +1,71)** |
| `narrow b = −0,010` | −0,00214 (t = −1,37) | **+0,00175 (t = +1,33)** |
| `rho = −0,025` | +0,00111 (t = +1,89) | **−0,00042 (t = −0,62)** |
| `scale = 1,032` | +0,00146 (t = +0,79) | **−0,00201 (t = −1,09)** |

**Alle vier draaien om, en `narrow` het duidelijkst.** De vormcorrectie die §6g voorschrijft
*hélpt* op de oude lambdas en *schaadt* op de nieuwe — en dat is geen ruis maar precies wat je
mag verwachten. `shrink = 0.80` drukte de teamsterktes naar elkaar toe, wat de totaalverdeling te
breed maakte; `shrink = 1.00` heeft dat per 19 september rechtgetrokken en §6e schreef toen al op
dat die ene wijziging *"op zichzelf al ongeveer tweederde van het gat sluit"*.

**Daarmee is de vormfout van §6g grotendeels een nalatenschap van de oude `shrink`-instelling, en
is ze op 19 september al gerepareerd — door een andere ingreep dan deze.** Dat is dezelfde
conclusie die `margins.py stats --since 2026-09-20` op 28 oktober voor de MARGE-kant trok (het gat
van §6f is dicht en op één bak zelfs omgeslagen), nu voor de TOTAAL-kant. Twee onafhankelijke
controles die hetzelfde zeggen over dezelfde wijziging.

### Wat de diagnose van §6g wél is, en waar ze misattribueerd was

De tabel in §6g is gemeten over **1717 duels die twee verschillende `shrink`-instellingen door
elkaar bevatten** (803 van vóór 19 sep 2026 op 0.80, 914 erna op 1.00) — en `margins.py`
waarschuwt in zijn eigen kop dat die twee niet op één hoop horen. Op alleen de homogene 914:

| | gemengd (1717) | homogeen (914) |
|---|---|---|
| gemiddeld totaal, voorspeld − werkelijk | +0,044 (z = +1,05) | **+0,098 (z = +1,67)** |
| P(Under 2.5) | −2,24 pp (z = −1,89) | −2,48 pp (z = −1,53) |
| P(Under 3.5) | −1,70 pp (z = −1,46) | −0,99 pp (z = −0,62) |

**Daarmee valt de kern van §6g anders uit dan er staat.** Daar staat "het gemiddelde klopt wél" en
"de verdeling niet"; op de homogene populatie is het **gemiddelde juist het grootste signaal**
(het model verwacht ~0,1 doelpunt per duel te weinig) en haalt van de hele histogram maar één cel
de twee standaardfouten: `totaal = 0` staat te dik (z = −2,67). Dat is geen vormfout maar een
**niveau**fout, en een niveaufout hoort niet in `score_grid` gerepareerd te worden maar in de
lambdaketen — `league_level`, `blend_seasons`, de vroeg-seizoenscorrectie.

Dat verklaart ook punt 1 hierboven: `scale = 1.032` (dus 3% meer doelpunten) brengt de fout op
`Under 2.5` van −2,48 naar −0,44 pp. Het is de knop die past op wat er werkelijk gemeten is. Maar
hij haalt zijn eigen lat niet: t = +0,79 in-steekproef, en van teken wisselend tussen de twee
splitsingen. **Daarom is ook die niet ingevoerd.**

### En rho, de enige kandidaat met een hypothese vóóraf

De enige significante cel (`totaal = 0` te dik) is precies de cel die Dixon-Coles met rho regelt,
en met `rho = −0.05` blaast `tau(0,0)` die cel met ongeveer 11% op. "rho minder negatief" is dus
een hypothese die vóór het kijken vaststaat. Gemeten met **vaste** waarden, nergens gefit:

| deelsteekproef | n | rho = −0,025 | rho = 0,00 |
|---|---|---|---|
| homogeen, eerste helft | 457 | +0,00178 (t=+2,12) | +0,00324 (t=+1,93) |
| homogeen, tweede helft | 457 | +0,00044 (t=+0,53) | +0,00057 (t=+0,35) |
| homogeen, even duels | 457 | +0,00028 (t=+0,36) | +0,00029 (t=+0,19) |
| homogeen, oneven duels | 457 | +0,00195 (t=+2,17) | +0,00352 (t=+1,97) |
| **de 803 van vóór de overstap** | 803 | **−0,00042 (t=−0,62)** | **−0,00120 (t=−0,89)** |

Over de hele homogene populatie: t = +1,89 op het totaal en +1,86 op de exacte uitslag. **Drie
redenen om hem tóch niet in te voeren**, en de eerste is de belangrijkste:

1. **Die vijf regels zijn geen vijf steekproeven.** De vier homogene regels zijn twee
   partities van dezelfde 914 duels, dus ze bevatten elkaars gegevens. De enige werkelijk
   onafhankelijke steekproef is de onderste — en daar is het teken **negatief**.
2. **Hij repareert de cel niet waarvoor hij is bedoeld.** Zelfs met `rho = 0`, dus zonder enige
   Dixon-Coles-correctie, blijft 0-0 te dik voorspeld: 5,53% tegen 3,94% werkelijk. De
   scheefstand op die cel komt uit de Poisson-aanname zelf en niet uit rho.
3. **De lat van deze repo wordt niet gehaald.** `CREDIBILITY_K` is ingevoerd op t = +2,11
   in-steekproef en +1,71 uit-steekproef (§4), en rollende xG is afgewezen op t = +0,05 en
   +1,06 met de woorden "daarom niet ingevoerd". t = +1,89 op één steekproef met een negatief
   teken op de enige onafhankelijke controle hoort aan de verkeerde kant van die lat.

### Wat dit betekent voor poort 9

§1h schrijft: *"Zodra de vormfout is gerepareerd hoort deze poort opnieuw gemeten en vermoedelijk
verlaagd of geschrapt."* Die voorwaarde is **niet** ingetreden — er is niets gerepareerd, omdat er
op deze steekproef niets te repareren viel. **Poort 9 blijft dus staan, onveranderd**, en dat is
geen apart besluit maar het uitblijven van de trigger.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import margins, model

CACHE = ROOT / "data" / "cache" / "gridfit"

SHRINK_SWITCH = "2026-09-20"
"""Vanaf deze datum zijn de lambdas in `data/run-state/` met `DEFAULT_SHRINK` = 1.00 gerekend.

Dit is geen smaak maar de scheiding tussen twee modelinstellingen (§6e, 19 sep 2026). Een
correctie fitten op de ene en toetsen op de andere is geen uit-steekproefcontrole maar een
vergelijking van twee modellen — dat is bij de eerste poging op 28 okt 2026 gebeurd en het gaf een
gefitte parameter die vier keer zo groot was als op de homogene populatie.
"""

TMAX = 2 * model.MAX_GOALS


# --------------------------------------------------------------------- data
def totals_vector(lambda_home: float, lambda_away: float,
                  rho: float = model.DEFAULT_RHO, scale: float = 1.0) -> list[float]:
    """Kansverdeling over het TOTAAL aantal doelpunten, uit het scoregrid."""
    grid = model.score_grid(lambda_home * scale, lambda_away * scale, rho=rho)
    out = [0.0] * (TMAX + 1)
    for i, row in enumerate(grid):
        for j, p in enumerate(row):
            out[i + j] += p
    return out


def tilt(vector: list[float], mu: float, a: float, b: float) -> list[float]:
    """Exponentiële tilt op de anti-diagonalen: `w(t) = exp(a*(t-mu) + b*(t-mu)^2)`.

    Werkt op het TOTAAL en laat de verdeling van het doelsaldo GEGEVEN dat totaal exact zoals ze
    was — §6f meet dat de margekant klopt, §6g dat de totaalkant scheef staat, dus dit is de
    ingreep die precies de scheve grootheid raakt. `a` schuift het gemiddelde, `b < 0` knijpt de
    spreiding.
    """
    out = [0.0] * len(vector)
    z = 0.0
    for t, p in enumerate(vector):
        if p <= 0.0:
            continue
        d = t - mu
        v = p * math.exp(a * d + b * d * d)
        out[t] = v
        z += v
    if z <= 0.0:
        return list(vector)
    return [v / z for v in out]


def load(since: str | None = SHRINK_SWITCH, refresh: bool = False) -> list[dict]:
    """Lambdaparen uit `data/run-state/` met de werkelijke uitslag erbij, met dagcache."""
    CACHE.mkdir(parents=True, exist_ok=True)
    pad = CACHE / f"{date.today().isoformat()}-{since or 'alles'}.json"
    if pad.exists() and not refresh:
        return json.loads(pad.read_text())
    rows = margins.load_matches(since=since)
    with_result, _ = margins.attach_results(rows)
    keep = [{"date": r["date"], "match": r["match"], "lam": r["lam"],
             "hg": r["hg"], "ag": r["ag"]} for r in with_result]
    pad.write_text(json.dumps(keep, ensure_ascii=False))
    return keep


# ---------------------------------------------------------------- maatstaf
def log_losses(rows: list[dict], rho: float = model.DEFAULT_RHO, scale: float = 1.0,
               a: float = 0.0, b: float = 0.0) -> list[float]:
    """Log loss van het WERKELIJKE totaal, per wedstrijd — de maatstaf om op te kiezen.

    Per wedstrijd en niet geaggregeerd, want een gemiddelde histogram kan afwijken terwijl elke
    wedstrijd apart goed is gekalibreerd, en omgekeerd. Dezelfde discipline als §1f voor de
    80/20-weging: kiezen op een score per waarneming, niet op een plaatje.
    """
    out = []
    for r in rows:
        lh, la = r["lam"]
        v = totals_vector(lh, la, rho=rho, scale=scale)
        if a or b:
            v = tilt(v, (lh + la) * scale, a, b)
        t = r["hg"] + r["ag"]
        out.append(-math.log(max(v[t] if t <= TMAX else 1e-12, 1e-12)))
    return out


def paired_t(base: list[float], cand: list[float]) -> tuple[float, float, int]:
    """Gepaarde toets op het verschil in log loss. Positief = kandidaat beter.

    Dit is de juiste toets voor "is deze variant beter dan het huidige grid": elke wedstrijd
    levert één verschil, en de vraag is of het gemiddelde daarvan van nul te onderscheiden is.
    Geen fit en geen splitsing nodig, dus ook niets om op te overfitten.
    """
    d = [x - y for x, y in zip(base, cand)]
    n = len(d)
    if n < 2:
        return 0.0, 0.0, 0
    m = sum(d) / n
    var = sum((x - m) ** 2 for x in d) / (n - 1)
    se = math.sqrt(var / n)
    return m, (m / se if se > 0 else 0.0), sum(1 for x in d if x > 0)


def under_calibration(rows: list[dict], line: float, **kw) -> tuple[float, float, float]:
    """Voorspelde en werkelijke `P(Under line)`, plus de z van het verschil."""
    pred = act = 0.0
    for r in rows:
        lh, la = r["lam"]
        v = totals_vector(lh, la, rho=kw.get("rho", model.DEFAULT_RHO),
                          scale=kw.get("scale", 1.0))
        if kw.get("a") or kw.get("b"):
            v = tilt(v, (lh + la) * kw.get("scale", 1.0), kw.get("a", 0.0), kw.get("b", 0.0))
        pred += sum(v[k] for k in range(len(v)) if k < line)
        act += 1.0 if (r["hg"] + r["ag"]) < line else 0.0
    n = len(rows)
    pred, act = pred / n, act / n
    se = math.sqrt(max(act * (1 - act), 1e-12) / n)
    return 100 * pred, 100 * act, (act - pred) / se


# ----------------------------------------------------------------- meting
CANDIDATES = (
    ("huidig grid", {}),
    ("rho = -0.025", {"rho": -0.025}),
    ("rho =  0.000", {"rho": 0.0}),
    ("narrow b = -0.005", {"b": -0.005}),
    ("narrow b = -0.010", {"b": -0.010}),
    ("narrow b = -0.015", {"b": -0.015}),
    ("shift a = +0.032", {"a": 0.032}),
    ("scale = 1.032", {"scale": 1.032}),
)


def measure(rows: list[dict], label: str) -> None:
    n = len(rows)
    print(f"POPULATIE: {n} duels, {rows[0]['date']} t/m {rows[-1]['date']}  ({label})\n")

    pm = sum(sum(r["lam"]) for r in rows) / n
    am = sum(r["hg"] + r["ag"] for r in rows) / n
    sd = math.sqrt(sum((r["hg"] + r["ag"] - am) ** 2 for r in rows) / (n - 1))
    print("DE DIAGNOSE VAN §6g OP DEZE POPULATIE")
    print(f"  gemiddeld totaal : voorspeld {pm:.3f}  werkelijk {am:.3f}  "
          f"{am-pm:+.3f}  z = {(am-pm)/(sd/math.sqrt(n)):+.2f}")
    for line in (2.5, 3.5):
        p, a, z = under_calibration(rows, line)
        print(f"  P(Under {line})     : voorspeld {p:5.2f}%  werkelijk {a:5.2f}%  "
              f"{a-p:+.2f} pp  z = {z:+.2f}")

    base = log_losses(rows)
    print(f"\nGEPAARDE TOETS per wedstrijd (log loss van het werkelijke totaal)")
    print(f"  huidig grid: {sum(base)/n:.5f}\n")
    print(f"  {'variant':22s} {'winst':>10} {'t':>7} {'beter in':>10}   "
          f"{'P(U2.5) fout':>13} {'P(U3.5) fout':>13}")
    print("  " + "-" * 82)
    for lab, kw in CANDIDATES:
        if not kw:
            continue
        m, t, win = paired_t(base, log_losses(rows, **kw))
        _, _, z25 = under_calibration(rows, 2.5, **kw)
        p25, a25, _ = under_calibration(rows, 2.5, **kw)
        p35, a35, _ = under_calibration(rows, 3.5, **kw)
        print(f"  {lab:22s} {m:+10.5f} {t:+7.2f} {100*win/n:9.1f}%   "
              f"{a25-p25:+12.2f} {a35-p35:+12.2f}")

    print("""
  LEESWIJZER. 'winst' is hoeveel log loss de variant van het huidige grid afhaalt; positief is
  beter. Let vooral op de kolom 'beter in': een variant die in tweederde van de wedstrijden wint
  en toch gemiddeld verliest, wint vaak en klein en verliest zelden en groot. Dat is géén
  verbetering, en het is precies de val waar §6e bij `shrink` voor waarschuwt.

  De `narrow`-varianten zijn de letterlijke uitvoering van wat §6g voorschrijft (massa uit de
  staarten naar het midden). Kijk wat ze met de twee rechterkolommen doen: op Under 2.5 bijna
  niets en op Under 3.5 de verkeerde kant op. Het gemiddelde totaal ligt rond 3,0, dus knijpen
  schuift massa naar 3 — van twee kanten tegelijk — en laat P(totaal <= 2) staan. Alleen een
  NIVEAU-knop (`scale`, `shift`) beweegt de Under-lijnen echt, en die haalt zijn eigen lat niet.""")


def split_report(rows: list[dict], onafhankelijk: list[dict] | None = None) -> None:
    """Dezelfde duels, twee keer gesplitst — plus één werkelijk onafhankelijke steekproef.

    LET OP WAT DE TWEE PARTITIES WEL EN NIET ZIJN. "Op tijd" en "om en om" zijn twee manieren om
    dezelfde duels in tweeën te knippen, dus de vier helften bevatten elkaars gegevens: vier keer
    hetzelfde teken is NIET vier onafhankelijke bevestigingen. Dat is precies de fout die op
    28 okt 2026 bijna is gemaakt met `rho` — die staat op alle vier positief en lijkt daarmee
    robuust, tot je hem op een steekproef legt die er echt buiten staat.

    Daarom hoort `onafhankelijk` erbij: de duels met lambdas van vóór de shrink-overstap. Die zijn
    met een andere modelinstelling gerekend en dus geen zuivere toets van de parameter alleen —
    maar ze zijn wél de enige gegevens die bij het kijken naar de 914 geen enkele rol speelden.
    Een kandidaat die daar van teken wisselt, heeft zijn robuustheid niet aangetoond.
    """
    half = len(rows) // 2
    partities = {
        "op tijd (eerste helft / tweede helft)": (rows[:half], rows[half:]),
        "om en om (even / oneven)": (rows[0::2], rows[1::2]),
    }
    print("\nVASTE WAARDEN OP TWEE PARTITIES VAN DEZELFDE DUELS")
    print("  (geen fit, dus geen overfit; de vraag is alleen of het teken standhoudt)\n")
    print(f"  {'variant':22s}" + "".join(f"{naam[:22]:>26s}" for naam in partities))
    print("  " + "-" * 76)
    for lab, kw in CANDIDATES:
        if not kw:
            continue
        cel = f"  {lab:22s}"
        for naam, (h1, h2) in partities.items():
            vals = []
            for deel in (h1, h2):
                m, t, _ = paired_t(log_losses(deel), log_losses(deel, **kw))
                vals.append(f"{m:+.5f}")
            cel += f"{'/'.join(vals):>26s}"
        print(cel)
    print("\n  Twee getallen per partitie: de twee helften apart.")

    if onafhankelijk and len(onafhankelijk) >= 100:
        print(f"\n  DE ENIGE ONAFHANKELIJKE CONTROLE — {len(onafhankelijk)} duels met lambdas van")
        print(f"  vóór {SHRINK_SWITCH}, die bij het kijken naar de {len(rows)} geen rol speelden:")
        base = log_losses(onafhankelijk)
        for lab, kw in CANDIDATES:
            if not kw:
                continue
            m, t, _ = paired_t(base, log_losses(onafhankelijk, **kw))
            vlag = "" if m > 0 else "   <-- TEKEN DRAAIT OM"
            print(f"    {lab:22s} {m:+.5f}  t = {t:+5.2f}{vlag}")
        print("""
  Lees die laatste tabel naast de twee partities erboven. `rho` staat op alle VIER de helften
  positief en lijkt daarmee de robuuste kandidaat — maar die vier zijn twee knipbeurten van
  dezelfde duels, en op de enige steekproef die er echt buiten staat draait zijn teken om. Vier
  keer hetzelfde getal uit één zak is één waarneming, niet vier.""")


# --------------------------------------------------------------- selftest
def selftest() -> int:
    ok = fail = 0

    def check(naam, cond):
        nonlocal ok, fail
        if cond:
            ok += 1
        else:
            fail += 1
            print(f"  FOUT: {naam}")

    v = totals_vector(1.5, 1.2)
    check("totaalvector sommeert tot 1", abs(sum(v) - 1.0) < 1e-9)
    check("totaalvector heeft de juiste lengte", len(v) == TMAX + 1)
    mu = 2.7
    check("tilt(0, 0) verandert niets",
          max(abs(x - y) for x, y in zip(tilt(v, mu, 0.0, 0.0), v)) < 1e-12)
    t1 = tilt(v, mu, 0.0, 0.0)
    check("tilt blijft genormaliseerd", abs(sum(t1) - 1.0) < 1e-9)

    # b < 0 hoort de spreiding te verkleinen en het gemiddelde ongeveer te laten staan
    def gem(x):
        return sum(i * p for i, p in enumerate(x))

    def var(x):
        g = gem(x)
        return sum((i - g) ** 2 * p for i, p in enumerate(x))

    tn = tilt(v, gem(v), 0.0, -0.05)
    check("b < 0 verkleint de spreiding", var(tn) < var(v))
    # ZIE DE DOCSTRING, 'Waarom knijpen het symptoom verergert': de totaalverdeling is
    # rechtsscheef, dus knijpen rond het gemiddelde haalt meer van de lange rechterstaart dan van
    # de korte linkerkant en VERLAAGT het gemiddelde. Dit is de eerste versie van deze zelftest
    # die dat goed heeft: hij stond er eerst als "laat het gemiddelde ongeveer staan" en viel
    # terecht om. Dat de controle dat ving is de reden dat het mechanisme is uitgezocht.
    check("b < 0 VERLAAGT het gemiddelde (rechtsscheve verdeling)", gem(tn) < gem(v))
    tp = tilt(v, gem(v), 0.08, 0.0)
    check("a > 0 verhoogt het gemiddelde", gem(tp) > gem(v))

    # rho: minder negatief hoort 0-0 te verkleinen
    g_a = model.score_grid(1.5, 1.2, rho=-0.05)
    g_b = model.score_grid(1.5, 1.2, rho=0.0)
    check("rho minder negatief verkleint 0-0", g_b[0][0] < g_a[0][0])

    # gepaarde toets
    m, t, win = paired_t([1.0, 1.0, 1.0, 1.0], [0.5, 0.5, 0.5, 0.5])
    check("gepaarde toets: kandidaat beter geeft positieve winst", m > 0)
    check("gepaarde toets telt de winnaars", win == 4)
    m0, t0, _ = paired_t([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    check("gepaarde toets: gelijk geeft 0", abs(m0) < 1e-12 and abs(t0) < 1e-12)

    # scale verhoogt het verwachte totaal
    check("scale > 1 verhoogt het verwachte totaal",
          gem(totals_vector(1.5, 1.2, scale=1.1)) > gem(totals_vector(1.5, 1.2)))

    print(f"{ok} controle(s) ok, {fail} fout")
    return 1 if fail else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("measure", help="de volledige meting (netwerk, geen credits)")
    m.add_argument("--all", action="store_true",
                   help="ook de lambdas van vóór de shrink-overstap (NIET aanbevolen: "
                        "twee modelinstellingen door elkaar)")
    m.add_argument("--refresh", action="store_true", help="dagcache negeren")
    sub.add_parser("selftest", help="rekencontroles, geen netwerk")
    args = ap.parse_args(argv)

    if args.cmd == "selftest":
        return selftest()

    since = None if args.all else SHRINK_SWITCH
    rows = sorted(load(since=since, refresh=args.refresh),
                  key=lambda r: (r["date"], r["match"]))
    if len(rows) < 100:
        print(f"Te weinig duels ({len(rows)}) om iets te zeggen — §6d eist er veel meer.")
        return 0
    label = ("ALLE lambdas, twee shrink-instellingen door elkaar" if args.all
             else f"alleen lambdas van ná {SHRINK_SWITCH} (homogeen)")
    measure(rows, label)
    # De duels van vóór de overstap als onafhankelijke controle — ze spelen in de meting zelf
    # geen rol (andere modelinstelling), maar ze zijn de enige gegevens die buiten de 914 staan.
    vooraf = []
    if not args.all:
        vooraf = [r for r in sorted(load(since=None, refresh=args.refresh),
                                    key=lambda r: (r["date"], r["match"]))
                  if r["date"] < SHRINK_SWITCH]
    split_report(rows, vooraf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

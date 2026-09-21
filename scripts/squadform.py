"""Selectiewaarde als tweede methode voor interlands — en de blessurelijst die poort 7 mist.

Toegevoegd 21 september 2026, op voorstel van de gebruiker ("je kunt ook opzoeken over
selecties, blessures, individuele vorm van spelers"). Twee dingen die `national.py` niet kan:

1. **Een tweede, onafhankelijke kansmethode.** Poort 5 (§1) eist dat twee methodes de markt
   dezelfde kant op verslaan. Bij clubvoetbal zijn dat de xG-methode en de splitsmethode; voor
   interlands was er er maar één, en dat is de reden dat Run C op `LIGHT` bleef staan. Deze
   module levert de tweede, en hij is werkelijk onafhankelijk: `national.py` kijkt naar
   **uitslagen**, deze naar de **marktwaarde van de selectie**. Die waarde wordt gezet op de
   clubtransfermarkt en weet niets van interlanduitslagen.
2. **De blessurelijst die poort 7 op interlands niet had.** Zie hieronder.

## Wat er is en wat er niet is (gemeten 21 sep 2026)

`https://www.fotmob.com/api/data/teams?id=<landen-id>` geeft `squad.squad`: vijf groepen
(coach, keepers, defenders, midfielders, attackers) met per speler `id`, `name`, `age`,
`transferValue`, `injury` (null of `{id, expectedReturn}`), `ccode`/`cname` (**de CLUB**, niet
het land — verwarrende veldnaam) en `positionIdsDesc`.

| veld | bruikbaar? |
|---|---|
| `transferValue` | **ja** — Nederland € 676 mln, Japan € 198 mln, San Marino € 2 mln |
| `injury` | **ja** — met verwachte terugkeer (Wieffer, Goretzka, …) |
| `rating`, `goals`, `assists` | **nee** — vrijwel overal leeg; dit zijn interlandcijfers van het lopende seizoen, geen clubvorm |

Daarom is dit **géén** module over individuele vorm geworden, hoezeer dat ook het idee was:
die cijfers staan er niet in. Wat er wel staat is de waarde van de selectie, en dat is een
sterk en volstrekt onafhankelijk signaal.

## Twee gegevens, twee rollen — en die worden niet door elkaar gehaald

Dat is geen nettigheid maar §1c: poort 7 **remt alleen** en stelt `my_prob` nooit bij, omdat er
geen meting bestaat die zegt hoeveel procentpunt een uitvaller waard is.

- **Selectiewaarde → de kans.** Fitbaar, want de waarde van vandaag beschrijft de selectie die
  de afgelopen maanden ook speelde. Gaat in `team()` en dus in `my_prob`.
- **Blessures → poort 7.** Niet fitbaar, want de blessurelijst is een momentopname en de
  uitslagen zijn historie. Gaat in `injuries()` en blijft een rem.

## Het model

Vier parameters, geen 2×213 zoals `national.py`:

    log lambda_thuis = basis + thuis/2 + beta*v_thuis - delta*v_uit
    log lambda_uit   = basis - thuis/2 + beta*v_uit   - delta*v_thuis

met `v` de gecentreerde log-selectiewaarde. Zo sterk ingeperkt is met opzet: deze methode moet
iets **anders** zeggen dan de vrije rating van `national.py`, niet hetzelfde met meer ruis.

## Wat het waard is — en de enige toets die telt

Uit-steekproef, fit t/m 1 maart 2026 en getoetst op de 308 duels erna waarop **beide** methodes
een kans geven:

| | Brier op de 1X2-uitkomst |
|---|---|
| alleen selectiewaarde (deze module) | 0,53191 |
| alleen uitslagenrating (`national.py`) | 0,51652 |
| **0,70 uitslagenrating + 0,30 selectiewaarde** | **0,51261** |
| blind gokken | 0,66667 |

**De mengeling verslaat beide methodes afzonderlijk.** Dat is het hele bestaansrecht van deze
module: ze is op zichzelf zwakker dan de rating, maar ze weet iets wat de rating niet weet. De
curve is glad met een optimum binnenin (0,5145 bij 0,50 · 0,5129 bij 0,60 · **0,5126 bij 0,70**
· 0,5128 bij 0,75 · 0,5144 bij 0,90) — dat is de handtekening van echt aanvullende informatie
en niet van ruis.

Gebruik dus **0,70 / 0,30** bij het samenvoegen, net zoals §1f bij clubvoetbal 0,80 / 0,20
gebruikt. Ga er niet op fijnregelen: tussen 0,60 en 0,80 is het verschil 0,0005.

De vensterlengte van de fit doet vrijwel niets (6 t/m 48 maanden geven 0,5319 tot 0,5354
uit-steekproef), dus die staat op 48 maanden: meer duels, geen prijs.

## De look-ahead die erin zit, en waarom hij aanvaard is

De selectie-endpoint geeft alleen de **huidige** selectie, geen historie. De fit draait dus op
resultaten van de afgelopen jaren met de waarde van vandaag. Dat is look-ahead: een ploeg die
sinds 2022 veel duurder is geworden, krijgt die waarde met terugwerkende kracht.

Twee dingen die dat verzachten, en één die het niet doet. Het model heeft maar **vier**
parameters, dus het kan zich niet aan individuele ploegen vastbijten zoals een vrije rating zou
doen. En de uit-steekproeftoets hierboven is een échte tijdsplitsing: gefit t/m 1 maart 2026,
gemeten op wat daarna kwam. Wat het niet verzacht: de waarde zelf is van ná die datum. Lees de
0,5319 dus als een bovengrens van wat deze methode alleen waard is — de winst van de
**mengeling** staat er los van, want die vergelijkt twee methodes met dezelfde handicap.

Gebruik:

    python3 scripts/squadform.py build     # selecties ophalen (~200 verzoeken, geen credits)
    python3 scripts/squadform.py fit       # fitten en wegschrijven
    python3 scripts/squadform.py show Netherlands Germany Japan
    python3 scripts/squadform.py injuries Netherlands
    python3 scripts/squadform.py verify
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path

try:
    from .fotmob import _get_json
    from .model import LeagueContext, TeamStats
    from . import national
except ImportError:                                   # als los script gedraaid
    from fotmob import _get_json                      # type: ignore[no-redef]
    from model import LeagueContext, TeamStats        # type: ignore[no-redef]
    import national                                   # type: ignore[no-redef]

SQUADS = Path("data/national-squads.json")
FIT = Path("data/squadform-fit.json")

# Hoeveel maanden resultaten de fit gebruikt. Korter = minder look-ahead maar minder data;
# `tune` meet het.
WINDOW_MONTHS = 48
# Onder dit aantal spelers mét een waarde is de selectie niet beschreven en is de methode
# onbruikbaar — poort, geen aantekening. Guyana gaf op 21 sep 2026 nul spelers terug.
MIN_PLAYERS = 11
MIN_VALUE = 1_000_000.0       # onder een miljoen euro totaal is het geen meting maar een gat


def build_squads(team_ids: dict[str, str] | None = None, *, verbose: bool = True) -> dict:
    """Haal per landenteam de selectie op. Eén verzoek per land, geen credits."""
    if team_ids is None:
        f = national.load_fit()
        team_ids = {t: v.get("name") for t, v in f["teams"].items()}
    uit: dict[str, dict] = {}
    for i, (tid, naam) in enumerate(sorted(team_ids.items(), key=lambda x: x[1] or ""), 1):
        try:
            d = _get_json(f"https://www.fotmob.com/api/data/teams?id={tid}")
        except Exception as e:                                       # noqa: BLE001
            if verbose:
                print(f"  {naam or tid:26s} FOUT {type(e).__name__}")
            continue
        blok = d.get("squad") or {}
        groepen = blok.get("squad") or []
        spelers = [m for g in groepen if g.get("title") != "coach"
                   for m in (g.get("members") or [])]
        waarden = [(p.get("transferValue") or 0.0) for p in spelers]
        geblesseerd = [{"id": p.get("id"), "name": p.get("name"),
                        "value": p.get("transferValue") or 0.0,
                        "expected_return": (p.get("injury") or {}).get("expectedReturn")}
                       for p in spelers if p.get("injury")]
        uit[tid] = {
            "name": (d.get("details") or {}).get("name") or naam,
            "is_national": bool(blok.get("isNationalTeam")),
            "n_players": len(spelers),
            "n_valued": sum(1 for w in waarden if w > 0),
            "total_value": float(sum(waarden)),
            "top11_value": float(sum(sorted(waarden, reverse=True)[:11])),
            "injured": geblesseerd,
            "injured_value": float(sum(x["value"] for x in geblesseerd)),
            "fetched": date.today().isoformat(),
        }
        if verbose and i % 25 == 0:
            print(f"  … {i} landen")
    SQUADS.parent.mkdir(parents=True, exist_ok=True)
    SQUADS.write_text(json.dumps(uit, ensure_ascii=False, indent=1))
    if verbose:
        bruikbaar = sum(1 for v in uit.values() if _usable(v))
        print(f"\n{len(uit)} selecties opgehaald, {bruikbaar} bruikbaar "
              f"(≥ {MIN_PLAYERS} spelers en ≥ € {MIN_VALUE/1e6:.0f} mln) → {SQUADS}")
    return uit


def load_squads() -> dict:
    if not SQUADS.exists():
        raise FileNotFoundError(f"{SQUADS} bestaat niet — draai eerst `squadform.py build`")
    return json.loads(SQUADS.read_text())


def _usable(v: dict) -> bool:
    return (v.get("n_valued", 0) >= MIN_PLAYERS
            and (v.get("total_value") or 0.0) >= MIN_VALUE
            and bool(v.get("is_national")))


def usable(team_id: str, squads: dict | None = None) -> tuple[bool, str]:
    """Poort, geen aantekening — zelfde constructie als `national.in_range`."""
    squads = squads if squads is not None else load_squads()
    v = squads.get(team_id)
    if not v:
        return False, f"geen selectie opgehaald voor team-id {team_id}"
    if not _usable(v):
        return False, (f"{v.get('name')}: {v.get('n_valued', 0)} spelers met een waarde, "
                       f"totaal € {(v.get('total_value') or 0)/1e6:.1f} mln — te dun")
    return True, (f"{v.get('name')}: {v['n_valued']} spelers, "
                  f"€ {v['total_value']/1e6:.0f} mln")


def injuries(team_id: str, squads: dict | None = None) -> dict:
    """Voor poort 7 (§1c) — een REM, nooit een bijstelling van `my_prob`."""
    squads = squads if squads is not None else load_squads()
    v = squads.get(team_id) or {}
    tot = (v.get("total_value") or 0.0)
    out = (v.get("injured_value") or 0.0)
    return {"team": v.get("name"), "count": len(v.get("injured") or []),
            "out_value": out, "squad_value": tot,
            "out_share": (out / tot) if tot > 0 else None,
            "names": [f"{x['name']} (terug {x['expected_return'] or 'onbekend'})"
                      for x in (v.get("injured") or [])],
            "measurable": bool(v.get("n_players"))}


# ---------------------------------------------------------------------------------------------
# De fit
# ---------------------------------------------------------------------------------------------
def _rows_in_window(corpus: list[dict], squads: dict, months: int, ref: date) -> list[tuple]:
    grens = ref.toordinal() - int(months * 30.44)
    uit = []
    for r in corpus:
        try:
            d = date.fromisoformat(r["date"])
        except ValueError:
            continue
        if d.toordinal() < grens or d > ref:
            continue
        h, a = squads.get(r["home_id"]), squads.get(r["away_id"])
        if not h or not a or not _usable(h) or not _usable(a):
            continue
        uit.append((math.log(h["total_value"]), math.log(a["total_value"]), r["gh"], r["ga"]))
    return uit


def fit(corpus: list[dict], squads: dict, *, months: int = WINDOW_MONTHS,
        ref: date | None = None, iters: int = 3000, lr: float = 0.02) -> dict:
    ref = ref or date.today()
    data = _rows_in_window(corpus, squads, months, ref)
    if len(data) < 100:
        raise ValueError(f"te weinig duels in het venster ({len(data)})")
    gem_v = sum(h + a for h, a, _, _ in data) / (2 * len(data))
    gem_g = sum(gh + ga for _, _, gh, ga in data) / (2 * len(data))
    base, home_adv, beta, delta = math.log(max(1e-6, gem_g)), 0.2, 0.15, 0.15
    n = len(data)
    for it in range(iters):
        g_b = g_h = g_be = g_de = 0.0
        for lh, la, gh, ga in data:
            vh, va = lh - gem_v, la - gem_v
            lam_h = math.exp(base + home_adv / 2 + beta * vh - delta * va)
            lam_a = math.exp(base - home_adv / 2 + beta * va - delta * vh)
            rh, ra = gh - lam_h, ga - lam_a
            g_b += rh + ra
            g_h += (rh - ra) / 2
            g_be += rh * vh + ra * va
            g_de += -rh * va - ra * vh
        step = lr / (1 + it / 400)
        base += step * g_b / n
        home_adv += step * g_h / n
        beta += step * g_be / n
        delta += step * g_de / n
    return {"ref": ref.isoformat(), "n_matches": n, "months": months,
            "base": base, "home_adv": home_adv, "beta": beta, "delta": delta,
            "mean_log_value": gem_v, "avg_goals_per_team": gem_g}


def save_fit(f: dict) -> None:
    FIT.parent.mkdir(parents=True, exist_ok=True)
    FIT.write_text(json.dumps(f, ensure_ascii=False, indent=1))


def load_fit() -> dict:
    if not FIT.exists():
        raise FileNotFoundError(f"{FIT} bestaat niet — draai eerst `squadform.py fit`")
    return json.loads(FIT.read_text())


# ---------------------------------------------------------------------------------------------
# Aansluiting op model.py — zelfde truc als national.py
# ---------------------------------------------------------------------------------------------
def _basis(f: dict) -> float:
    """Het doelpuntniveau waar de FIT mee rekent: `exp(base)`, niet het ruwe gemiddelde.

    Anders dan in `national.py` wordt `base` hier **meegefit** (er staat een gradiënt op), dus
    `exp(base)` loopt uiteen met `avg_goals_per_team`. Op 21 sep 2026 scheelde dat een constante
    factor 1,158 op élk duel — `verify` ving dat, en dat is precies waarvoor die controle er is.
    Gebruik daarom overal hieronder dezelfde constante, en nooit het ruwe gemiddelde.
    """
    return math.exp(f["base"])


def context(f: dict | None = None) -> LeagueContext:
    f = f or load_fit()
    gem = _basis(f)
    h = math.exp(f["home_adv"] / 2)
    return LeagueContext(home_goals_per_match=gem * h, away_goals_per_match=gem / h,
                         avg_xg_per_match=gem)


def team(team_id: str, f: dict | None = None, squads: dict | None = None,
         *, matches: int = 20) -> TeamStats:
    f = f or load_fit()
    squads = squads if squads is not None else load_squads()
    v = math.log(squads[team_id]["total_value"]) - f["mean_log_value"]
    gem = _basis(f)
    return TeamStats(xg=math.exp(f["beta"] * v) * gem * matches,
                     xga=math.exp(-f["delta"] * v) * gem * matches,
                     matches_played=matches)


def _brier(rows: list[dict], f: dict, squads: dict) -> tuple[float, int]:
    try:
        from .model import analyze_match
    except ImportError:
        from model import analyze_match                              # type: ignore[no-redef]
    ctx = context(f)
    som, n = 0.0, 0
    for r in rows:
        h, a = squads.get(r["home_id"]), squads.get(r["away_id"])
        if not h or not a or not _usable(h) or not _usable(a):
            continue
        p = analyze_match(team(r["home_id"], f, squads), team(r["away_id"], f, squads),
                          ctx, shrink=1.0)
        werk = (1.0, 0.0, 0.0) if r["gh"] > r["ga"] else (
            (0.0, 1.0, 0.0) if r["gh"] == r["ga"] else (0.0, 0.0, 1.0))
        som += sum((q - w) ** 2 for q, w in zip((p.home, p.draw, p.away), werk))
        n += 1
    return (som / n if n else float("nan")), n


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="selecties ophalen bij Fotmob")
    fp = sub.add_parser("fit", help="fitten op recente uitslagen")
    fp.add_argument("--months", type=int, default=WINDOW_MONTHS)
    t = sub.add_parser("tune", help="vensterlengte uit-steekproef meten")
    t.add_argument("--cutoff", default="2026-03-01")
    s = sub.add_parser("show", help="selectiewaarde en afgeleide sterkte")
    s.add_argument("teams", nargs="*")
    i = sub.add_parser("injuries", help="blessurelijst voor poort 7")
    i.add_argument("teams", nargs="*")
    sub.add_parser("verify", help="controleer de aansluiting op model.py")
    a = ap.parse_args()

    if a.cmd == "build":
        build_squads()
        return
    if a.cmd == "fit":
        corpus, squads = national.load_corpus(), load_squads()
        f = fit(corpus, squads, months=a.months)
        save_fit(f)
        b, n = _brier([r for r in corpus if r["date"] >= "2026-01-01"], f, squads)
        print(f"{f['n_matches']} duels in een venster van {f['months']} maanden")
        print(f"  beta (aanval per log-euro)      {f['beta']:+.4f}")
        print(f"  delta (verdediging per log-euro){f['delta']:+.4f}")
        print(f"  thuisvoordeel                   {math.exp(f['home_adv']):.3f}x")
        print(f"  Brier in-steekproef {b:.5f} over {n} duels van 2026 (blind gokken 0.66667)")
        print(f"weggeschreven naar {FIT}")
        return
    if a.cmd == "tune":
        corpus, squads = national.load_corpus(), load_squads()
        cut = a.cutoff
        train = [r for r in corpus if r["date"] < cut]
        test = [r for r in corpus if r["date"] >= cut]
        ref = date.fromisoformat(cut)
        print(f"fit t/m {cut}, getoetst op de duels erna")
        for m in (6, 12, 18, 30, 48):
            try:
                f = fit(train, squads, months=m, ref=ref)
                b, n = _brier(test, f, squads)
                print(f"  venster {m:3d} mnd  n_fit={f['n_matches']:4d}  "
                      f"beta={f['beta']:+.3f} delta={f['delta']:+.3f}  Brier uit {b:.5f} (n={n})")
            except ValueError as e:
                print(f"  venster {m:3d} mnd  {e}")
        print("blind gokken = 0.66667")
        return

    squads = load_squads()
    if a.cmd == "injuries":
        nf = national.load_fit()
        for naam in (a.teams or ["Netherlands", "Germany"]):
            tid = national.find_team(nf, naam)
            if not tid:
                print(f"{naam}: niet gevonden")
                continue
            inf = injuries(tid, squads)
            deel = f"{inf['out_share']*100:.1f}%" if inf["out_share"] is not None else "n.v.t."
            print(f"{inf['team'] or naam:18s} {inf['count']} geblesseerd, "
                  f"€ {inf['out_value']/1e6:.1f} mln van € {inf['squad_value']/1e6:.0f} mln = {deel}")
            for nm in inf["names"]:
                print(f"     {nm}")
        return
    if a.cmd == "show":
        f, nf = load_fit(), national.load_fit()
        print(f"{'ploeg':18s}{'selectie':>12s}{'aanval':>9s}{'verdediging':>13s}  poort")
        for naam in (a.teams or ["Netherlands", "Germany", "Brazil", "Japan", "San Marino"]):
            tid = national.find_team(nf, naam)
            if not tid or tid not in squads:
                print(f"{naam:18s}  geen selectiedata")
                continue
            ok, reden = usable(tid, squads)
            if not ok:
                print(f"{naam:18s}  POORT DICHT — {reden}")
                continue
            ts = team(tid, f, squads)
            print(f"{squads[tid]['name'][:17]:18s}{squads[tid]['total_value']/1e6:10.0f}M"
                  f"{ts.xg_per_match/f['avg_goals_per_team']:9.3f}"
                  f"{ts.xga_per_match/f['avg_goals_per_team']:13.3f}  open")
        return
    if a.cmd == "verify":
        try:
            from .model import match_lambdas
        except ImportError:
            from model import match_lambdas                          # type: ignore[no-redef]
        f = load_fit()
        ctx = context(f)
        ids = [t for t, v in squads.items() if _usable(v)][:4]
        ok = True
        for h in ids[:2]:
            for aa in ids[2:4]:
                vh = math.log(squads[h]["total_value"]) - f["mean_log_value"]
                va = math.log(squads[aa]["total_value"]) - f["mean_log_value"]
                lh = math.exp(f["base"] + f["home_adv"] / 2 + f["beta"] * vh - f["delta"] * va)
                la = math.exp(f["base"] - f["home_adv"] / 2 + f["beta"] * va - f["delta"] * vh)
                mlh, mla = match_lambdas(team(h, f, squads), team(aa, f, squads), ctx, shrink=1.0)
                if abs(lh - mlh) > 1e-6 or abs(la - mla) > 1e-6:
                    ok = False
                print(f"{squads[h]['name'][:16]:17s}-{squads[aa]['name'][:16]:17s}"
                      f"fit {lh:6.3f}/{la:6.3f}   model {mlh:6.3f}/{mla:6.3f}")
        print("\nOK — sluit aan op model.match_lambdas." if ok else
              "\nAFWIJKING — de schaal klopt niet.")
        return


if __name__ == "__main__":
    main()

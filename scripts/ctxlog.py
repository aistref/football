#!/usr/bin/env python3
"""Contextlogboek — voorspellen ontbrekende spelers en rust iets dat het model niet weet?

Waarom dit bestaat (5 sep 2026, op verzoek van de gebruiker). Poort 7 houdt sinds 23 aug bets
tegen op grond van blessures, schorsingen en rust, maar stelt `my_prob` **niet** bij. §1c geeft
daar de reden bij: *"er is geen enkele meting die zegt hoeveel procentpunt een geblesseerde
middenvelder waard is, en zo'n getal verzinnen is precies wat §2 en §4 verbieden."*

Op 5 sep is geprobeerd die meting alsnog te doen, op 147 wedstrijden met zowel een contextblok als
een marktkans als een uitslag. **Uitkomst: niets.** De samenhang tussen het beschikbaarheids-
verschil en de fout van het model is r = −0.007 (t = −0.08); over het hele waargenomen bereik gaat
het om 1.5 procentpunt. Dat blijft zo in elke variant: zonder uitschieters, alleen wedstrijden
waarin iemand ontbreekt, en ook op doelpunten in plaats van op de uitslag.

**Dat is geen bewijs dat het effect er niet is — het is bewijs dat 147 wedstrijden te weinig zijn.**
Met deze steekproef was alleen een effect van ~54 procentpunt per eenheid aantoonbaar geweest, en
zo groot is het zeker niet. Wat er nodig is om een realistisch effect te kunnen zien:

| effect (pp per eenheid beschikbaarheidsverschil) | wedstrijden nodig |
|---|---|
| 30 | ~475 |
| 20 | ~1.070 |
| 15 | ~1.900 |
| 10 | ~4.270 |

Daarom dit logboek. Het verzamelt de context van **élke** wedstrijd waarvoor ze is opgehaald — ook
de duels die buiten `MAX_DEEP_ANALYSES` vielen, want daar is de context toch al gratis binnengehaald
(§3, Stage 4 eist dat vóór de afkapping). Dat is ongeveer 114 wedstrijden per dag over beide runs in
plaats van de tien per dag die de meting van 5 sep opleverde, en daarmee is de vraag over drie tot
vier weken beantwoordbaar in plaats van over zeven maanden.

    python3 scripts/ctxlog.py collect --run a --date 2026-09-05
    python3 scripts/ctxlog.py settle
    python3 scripts/ctxlog.py stats

**De meetlat is de uitslag, niet de markt.** De marktkans wordt wél vastgelegd, maar alleen als
controlevariabele en om te kunnen zien of de markt het effect zelf al inprijst — precies de rol die
§6e voor marktvergelijkingen toestaat. Er wordt niets van `my_prob` afgetrokken (§2).

Alleen de standaardbibliotheek.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics as S
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "context-log.jsonl"
STATE_DIR = ROOT / "data" / "run-state"

_SHARE_IN_TEXT = re.compile(r"\((\d+(?:[.,]\d+)?)\s*% van de selectiewaarde\)")


def out_share(block) -> float | None:
    """Aandeel van de selectiewaarde dat ontbreekt, uit een contextblok in run-state.

    LET OP DE NOEMER. `squad_value` is de waarde van de vermoedelijke **basiself**, en de
    uitvallers zitten daar niet in — het aandeel is dus `out / (basis + out)`, precies zoals
    `context.TeamContext.out_share` het rekent. Met `out / basis` kwam Lommel – Club Brugge op
    5 sep 2026 op 247% uit, wat onmogelijk is; die fout zat in de eerste versie van deze meting en
    mengde bovendien twee definities door elkaar, want de tekstvorm hieronder gebruikte wél de
    goede. Twee definities in één regressie is ruis die je zelf toevoegt.

    Twee vormen worden geaccepteerd: het dict-blok, en de leesbare zin die sommige runs schreven
    ("2 afwezig (13% van de selectiewaarde) · vorm LWWWL"). Die laatste bevat hetzelfde getal.
    """
    if isinstance(block, dict):
        squad = block.get("squad_value") or 0
        out = block.get("out_value") or 0
        return (out / (squad + out)) if squad > 0 else None
    hit = _SHARE_IN_TEXT.search(str(block or ""))
    return float(hit.group(1).replace(",", ".")) / 100 if hit else None


def rest_days(block) -> float | None:
    if isinstance(block, dict):
        return block.get("rest_days")
    hit = re.search(r"(\d+(?:[.,]\d+)?)\s*dagen rust", str(block or ""))
    return float(hit.group(1).replace(",", ".")) if hit else None


def _rows_from_state(state: dict, day: str, run: str) -> list[dict]:
    rows = []
    for comp, block in (state.get("competitions") or {}).items():
        if not isinstance(block, dict):
            continue
        for match in block.get("matches", []):
            if not isinstance(match, dict):
                continue
            ctx = match.get("context") or {}
            home_block = ctx.get("home") if isinstance(ctx, dict) else None
            if not home_block:
                continue
            sh, sa = out_share(home_block), out_share(ctx.get("away"))
            if sh is None or sa is None:
                continue
            cal = match.get("calibration") or {}
            rh, ra = rest_days(home_block), rest_days(ctx.get("away"))
            rows.append({
                "id": f"ctx-{day}-{run}-{_slug(match.get('match', ''))}",
                "date": day, "run": run.upper(), "competition": comp,
                "match": match.get("match"), "match_id": match.get("match_id"),
                "afgekapt": bool(match.get("afgekapt")),
                "lineup_type": ctx.get("lineup_type") if isinstance(ctx, dict) else None,
                "out_share_home": round(sh, 4), "out_share_away": round(sa, 4),
                "gap": round(sh - sa, 4),
                "rest_home": rh, "rest_away": ra,
                "rest_gap": (round(rh - ra, 2) if rh is not None and ra is not None else None),
                "p_market_home": (cal.get("market") or [None])[0],
                "p_model_home": (None if not cal.get("p_xg") or not cal.get("p_split")
                                 else round((cal["p_xg"][0] + cal["p_split"][0]) / 2, 4)),
                "result": "pending", "home_goals": None, "away_goals": None,
            })
    return rows


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60]


def load() -> list[dict]:
    if not LOG.exists():
        return []
    return [json.loads(line) for line in LOG.read_text().splitlines() if line.strip()]


def _cmd_collect(args: argparse.Namespace) -> int:
    path = STATE_DIR / f"{args.date}-run-{args.run.lower()}.json"
    if not path.exists():
        print(f"Geen voortgangsbestand: {path}")
        return 1
    rows = _rows_from_state(json.loads(path.read_text()), args.date, args.run)
    have = {r["id"] for r in load()}
    new = [r for r in rows if r["id"] not in have]
    with LOG.open("a") as fh:
        for row in new:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    afgekapt = sum(1 for r in new if r["afgekapt"])
    print(f"{len(new)} nieuwe wedstrijd(en) toegevoegd van de {len(rows)} met context "
          f"({afgekapt} daarvan waren afgekapt en zouden anders niet zijn vastgelegd); "
          f"logboek staat nu op {len(have) + len(new)}.")
    return 0


def _cmd_settle(_args: argparse.Namespace) -> int:
    from settling import DayIndex, norm            # zelfde module als ledger en shadow (§0)

    rows = load()
    open_rows = [r for r in rows if r["result"] == "pending"]
    if not open_rows:
        print("Niets af te wikkelen.")
        return 0
    index, done = DayIndex(), 0
    for row in open_rows:
        naam = row.get("match") or ""
        if "–" not in naam:
            continue
        home, away = (x.strip() for x in naam.split("–", 1))
        hit = index._day(date.fromisoformat(row["date"])).get((norm(home), norm(away)))
        if not hit or not hit.get("finished") or not hit.get("score"):
            continue
        try:
            gh, ga = (int(x) for x in str(hit["score"]).replace("-", " ").split())
        except ValueError:
            continue
        row["home_goals"], row["away_goals"] = gh, ga
        row["result"] = "home" if gh > ga else ("away" if ga > gh else "draw")
        done += 1
    LOG.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(f"{done} wedstrijd(en) afgewikkeld; nog {sum(1 for r in rows if r['result'] == 'pending')} open.")
    return 0


def _corr(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n < 5:
        return float("nan"), float("nan")
    mx, my = S.mean(xs), S.mean(ys)
    sx, sy = S.pstdev(xs), S.pstdev(ys)
    if not sx or not sy:
        return float("nan"), float("nan")
    r = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n * sx * sy)
    return r, r * math.sqrt((n - 2) / max(1e-9, 1 - r * r))


def _cmd_stats(_args: argparse.Namespace) -> int:
    rows = [r for r in load() if r["result"] in ("home", "draw", "away")]
    if len(rows) < 20:
        print(f"Nog te weinig afgewikkelde wedstrijden ({len(rows)}). Kom terug bij een paar honderd.")
        return 0
    won = [1.0 if r["result"] == "home" else 0.0 for r in rows]
    gap = [r["gap"] for r in rows]
    print(f"CONTEXTLOGBOEK — {len(rows)} afgewikkelde wedstrijden, "
          f"{sum(1 for r in load() if r['result'] == 'pending')} nog open")
    print(f"  thuiswinst werkelijk {S.mean(won) * 100:.1f}%")
    print(f"  beschikbaarheidsverschil: gemiddelde {S.mean(gap):+.3f}, spreiding {S.pstdev(gap):.3f}\n")

    for label, key in (("fout van het MODEL", "p_model_home"), ("fout van de MARKT", "p_market_home")):
        sub = [(r, w) for r, w in zip(rows, won) if r.get(key) is not None]
        if len(sub) < 20:
            print(f"  {label}: te weinig waarnemingen ({len(sub)})")
            continue
        xs = [r["gap"] for r, _ in sub]
        ys = [w - r[key] for r, w in sub]
        r_, t_ = _corr(xs, ys)
        mx, my = S.mean(xs), S.mean(ys)
        var = sum((x - mx) ** 2 for x in xs)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / var if var else float("nan")
        print(f"  {label} tegen het beschikbaarheidsverschil (n={len(sub)}):")
        print(f"     r = {r_:+.3f}   t = {t_:+.2f}   helling {b * 100:+.1f} pp per eenheid")

    sx, sy = S.pstdev(gap), 0.46
    detecteerbaar = (2 / math.sqrt(len(rows))) * sy / sx if sx else float("nan")
    print(f"\n  Met {len(rows)} wedstrijden is alleen een effect vanaf ~{detecteerbaar * 100:.0f} pp "
          f"per eenheid aantoonbaar (t=2).")
    print("  Lees dit als §6d: kijk naar de richting over weken, niet naar het getal van vandaag,")
    print("  en stel op grond hiervan pas iets bij als het teken consistent is én groot genoeg.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    collect = sub.add_parser("collect", help="context van één run in het logboek zetten")
    collect.add_argument("--run", required=True, choices=["a", "b", "A", "B"])
    collect.add_argument("--date", required=True, help="YYYY-MM-DD")
    collect.set_defaults(func=_cmd_collect)
    settle = sub.add_parser("settle", help="uitslagen ophalen voor wat nog openstaat")
    settle.set_defaults(func=_cmd_settle)
    stats = sub.add_parser("stats", help="voorspelt context iets dat het model niet weet?")
    stats.set_defaults(func=_cmd_stats)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

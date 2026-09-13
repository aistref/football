"""Stage 4 — context + datarijkdom vóór de afkapping (§3, Stage 4).

Ongewijzigd ten opzichte van 11 sep: de context wordt voor élke wedstrijd opgehaald, ook voor de
duels die op `tier = NONE` uitkomen en voor wat de cap zou afkappen. Dat is gratis (Fotmob) en het
is wat §1c vraagt — de steekproef van `ctxlog.py` is de enige weg naar een meting over het effect
van blessures.
"""
import json, sys
sys.path.insert(0, "tmp-run")
from dataclasses import asdict
from scripts import context, squad, ranking

cands = json.load(open("tmp-run/ra13_cands.json"))
stats = json.load(open("tmp-run/ra13_stage3.json"))["stats"]
out = []
for c in cands:
    ctx = err = None
    try:
        ctx = context.fetch_match_context(c["match_id"], c["kickoff_utc"])
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    th = ta = None
    if ctx is not None:
        try: th = squad.turnover(ctx.home.team_id, ctx.home.squad_value)
        except Exception: pass
        try: ta = squad.turnover(ctx.away.team_id, ctx.away.squad_value)
        except Exception: pass
    mh = ma = (stats.get(c["competition"], {}).get("cur") or {}).get("played") or 0
    r = ranking.data_richness(ctx, th, ta, mh, ma)
    row = {**c, "ctx_error": err, "richness": r.total, "richness_parts": r.parts,
           "richness_notes": r.notes}
    if ctx is not None:
        row["ctx"] = {
            "home": asdict(ctx.home), "away": asdict(ctx.away),
            "lineup_type": ctx.lineup_type, "venue": asdict(ctx.venue),
            "gate": {s: asdict(context.check(ctx, s)) for s in ("home", "away", None)},
        }
        row["turnover"] = {"home": (asdict(th) if th else None), "away": (asdict(ta) if ta else None)}
    else:
        row["ctx"] = None
    out.append(row)
    print(f"{c['home'][:18]:18s} - {c['away'][:18]:18s} {c['tier']:5s} rich={r.total:.1f}"
          + (f"  ctx-fout: {err}" if err else ""))
json.dump(out, open("tmp-run/ra13_ctx.json", "w"), ensure_ascii=False, indent=1, default=str)

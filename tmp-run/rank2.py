import json, pickle, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0,'tmp-run')
from scripts import fotmob, context as ctxmod, squad, ranking

rows = json.load(open('tmp-run/matches.json'))
LEAGUES = {r['comp']: r['league_id'] for r in rows}
cur = {c: fotmob.fetch_league_stats(l, '2026/2027') for c, l in LEAGUES.items()}

def played(comp, key, fallback):
    t = cur[comp]['teams'].get(key) or cur[comp]['teams'].get(fallback) or {}
    return int(t.get('played') or 0)

def one(r):
    try:
        ctx = ctxmod.fetch_match_context(r['match_id'], r['kickoff']); cerr = None
    except Exception as e:
        ctx, cerr = None, f'{type(e).__name__}: {e}'
    th = ta = None
    if ctx is not None:
        try: th = squad.turnover(ctx.home.team_id, ctx.home.squad_value)
        except Exception: th = None
        try: ta = squad.turnover(ctx.away.team_id, ctx.away.squad_value)
        except Exception: ta = None
    mh = played(r['comp'], r['home_key'], r['home'])
    ma = played(r['comp'], r['away_key'], r['away'])
    rich = ranking.data_richness(ctx, th, ta, mh, ma)
    return {**r, 'rich': rich.total, 'rich_parts': rich.parts, 'rich_notes': rich.notes,
            'ctx': ctx, 'cerr': cerr, 'turn_h': th, 'turn_a': ta,
            'played_h': mh, 'played_a': ma,
            'tier_pre': 'FULL' if (r['home_key'] and r['away_key']) else 'CONV'}

with ThreadPoolExecutor(max_workers=5) as pool:
    out = list(pool.map(one, rows))
for i, o in enumerate(out, 1):
    print(f"{i:2}/49 {o['comp'][:18]:20} {o['home'][:14]:15}-{o['away'][:14]:15} "
          f"rich {o['rich']:5.2f} {o['tier_pre']:5} {'' if o['ctx'] else 'GEEN CONTEXT'}", flush=True)
pickle.dump(out, open('tmp-run/ranked.pkl','wb'))
print('KLAAR', len(out))

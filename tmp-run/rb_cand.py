import json, sys
sys.path.insert(0,'tmp-run')
from scripts import fotmob
from rb_names import resolve
S3=json.load(open('tmp-run/rb_stage3.json'))['stats']
CTX=json.load(open('tmp-run/rb_ctx.json'))
FIX=json.load(open('tmp-run/rb_fixtures.json'))
cands=[]
tcache={}
for f in FIX:
    comp=f['comp']; meta=S3[comp]
    if comp not in tcache:
        tcache[comp]=fotmob.fetch_league_stats(meta['primaryId'], meta['base_season'])['teams']
    teams=tcache[comp]
    th=resolve(f['home'],teams); ta=resolve(f['away'],teams)
    missing=[n for n,r in ((f['home'],th),(f['away'],ta)) if r is None]
    tier = "NONE" if missing else meta['tier']
    rec=CTX[str(f['match_id'])]
    cands.append({"competition":comp,"home":f['home'],"away":f['away'],"match_id":f['match_id'],
        "kickoff_utc":f['utc'],"primaryId":meta['primaryId'],"season":meta['base_season'],
        "sportkey":meta['sportkey'],"tier":tier,"table_home":th,"table_away":ta,"missing":missing,
        "richness":(rec.get('richness') or {}).get('score'),
        "richness_parts":(rec.get('richness') or {}).get('deelscores'),
        "understat":None,
        "ctx":rec.get('context')})
    print(f"{comp[:28]:30} {f['home'][:20]:22}-{f['away'][:20]:22} tier={tier:5} rich={cands[-1]['richness']} missing={missing}")
json.dump(cands, open('tmp-run/rb_cands.json','w'), ensure_ascii=False, indent=1)

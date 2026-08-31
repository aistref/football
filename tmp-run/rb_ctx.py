import json, traceback
from scripts import context, squad, ranking, fotmob
FIX=json.load(open('tmp-run/rb_fixtures.json'))
CUR={"Greek Super League (GRE)":(135,"2026/2027"),"Allsvenskan (SWE)":(67,"2026"),
     "Croatian HNL (CRO)":(252,"2026/2027"),"Romanian SuperLiga (ROU)":(189,"2026/2027"),
     "Segunda Division (ESP)":(140,"2026/2027"),"Keuken Kampioen Divisie (NED)":(111,"2026/2027"),
     "Kategoria Superiore (ALB)":(260,"2026/2027")}
curcache={}
def played(comp, team):
    lid,s=CUR[comp]
    if comp not in curcache:
        try: curcache[comp]=fotmob.fetch_league_stats(lid,s)
        except Exception: curcache[comp]={"teams":{}}
    t=curcache[comp]['teams']
    import unicodedata
    def n(x): return unicodedata.normalize('NFKD',x).encode('ascii','ignore').decode().lower().strip()
    for k,v in t.items():
        if n(k)==n(team): return v.get('played',0) or 0
    return 0

out={}
for f in FIX:
    key=str(f['match_id'])
    rec={"fixture":f}
    try:
        ctx=context.fetch_match_context(f['match_id'], f['utc'])
        rec['ctx_ok']=True
    except Exception as e:
        ctx=None; rec['ctx_ok']=False; rec['ctx_err']=str(e)[:200]
    tos={}
    for side in ('home','away'):
        try:
            sv = 0.0
            if ctx is not None:
                tc = getattr(ctx, side, None)
                sv = getattr(tc,'squad_value',0.0) or 0.0
            tos[side]=squad.turnover(f[side+'_id'], sv)
        except Exception as e:
            tos[side]=None
    mh=played(f['comp'], f['home']); ma=played(f['comp'], f['away'])
    try:
        r=ranking.data_richness(ctx, tos['home'], tos['away'], mh, ma)
        rec['richness']={"score":round(r.total,3),
                         "deelscores":{k:round(v,3) for k,v in r.parts.items()},
                         "notes":r.notes}
    except Exception as e:
        rec['richness_err']=str(e)[:300]; rec['richness']=None
    if ctx is not None:
        def td(tc):
            return {"name":getattr(tc,'name',''),"team_id":getattr(tc,'team_id',None),
                    "out_count":getattr(tc,'out_count',None),"out_value":getattr(tc,'out_value',None),
                    "squad_value":getattr(tc,'squad_value',None),"out_names":getattr(tc,'out_names',[]),
                    "form":getattr(tc,'form',''),"form_points":getattr(tc,'form_points',None),
                    "form_matches":getattr(tc,'form_matches',None),"rest_days":getattr(tc,'rest_days',None),
                    "congested":getattr(tc,'congested',None),"note":getattr(tc,'note','')}
        rec['context']={"home":td(ctx.home),"away":td(ctx.away),
                        "lineup_type":getattr(ctx,'lineup_type',None)}
        v=getattr(ctx,'venue',None)
        if v is not None:
            rec['context']['venue']={k:getattr(v,k,None) for k in ('stadium','city','home_ground','away_ground','relocated','at_away_ground','note')}
        g={}
        for side in ('home','away',None):
            gg=context.check(ctx, side)
            g['null' if side is None else side]={"passed":gg.passed,"reason":gg.reason,"detail":getattr(gg,'detail',{})}
        rec['context']['gate']=g
    rec['played_current']={'home':mh,'away':ma}
    out[key]=rec
    rs = rec['richness']['score'] if rec.get('richness') else None
    print(f"{f['home'][:22]:24}-{f['away'][:22]:24} ctx={rec['ctx_ok']} rich={rs} lineup={rec.get('context',{}).get('lineup_type')}")
json.dump(out, open('tmp-run/rb_ctx.json','w'), ensure_ascii=False, indent=1, default=str)

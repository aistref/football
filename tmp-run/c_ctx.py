import json, sys
sys.path.insert(0,'.')
from scripts import context, squad, ranking, fotmob

M = json.load(open("tmp-run/c_matches.json"))
S = json.load(open("tmp-run/c_stage3.json"))
FULL = [c for c in M if S[c]["prev"].get("has_xg")]
cur_tables={}
for comp in FULL:
    st = fotmob.fetch_league_stats(M[comp]["league_id"], S[comp]["cur_season"])
    cur_tables[comp]={n:t.get("played",0) for n,t in st["teams"].items()}
def played(comp,name):
    tbl=cur_tables[comp]
    if name in tbl: return tbl[name]
    for k,v in tbl.items():
        if name.lower() in k.lower() or k.lower() in name.lower(): return v
    return 0
out={}
for comp in FULL:
    for m in M[comp]["matches"]:
        key=f"{m['home']} – {m['away']}"
        ph, pa = played(comp,m["home"]), played(comp,m["away"])
        rec={"comp":comp,"match_id":m["id"],"utc":m["utc"],"home":m["home"],"away":m["away"],
             "home_id":m["home_id"],"away_id":m["away_id"],"played_home":ph,"played_away":pa}
        try:
            ctx = context.fetch_match_context(m["id"], m["utc"])
            rec["ctx"]={"lineup_type":ctx.lineup_type,
                        "venue":{"stadium":ctx.venue.stadium,"city":ctx.venue.city,
                                 "home_ground":ctx.venue.home_ground,"relocated":ctx.venue.relocated,
                                 "at_away_ground":ctx.venue.at_away_ground,"note":ctx.venue.note},
                        "home":{k:v for k,v in ctx.home.__dict__.items()},
                        "away":{k:v for k,v in ctx.away.__dict__.items()},
                        "home_summary":ctx.home.summary(),"away_summary":ctx.away.summary()}
            th = squad.turnover(m["home_id"], ctx.home.squad_value)
            ta = squad.turnover(m["away_id"], ctx.away.squad_value)
            rich = ranking.data_richness(ctx, th, ta, ph, pa)
            rec["turnover"]={"home":th.summary(),"away":ta.summary(),"home_share":th.share,"away_share":ta.share}
            rec["richness"]={"score":rich.total,"parts":rich.parts,"summary":rich.summary(),"notes":rich.notes}
            rec["gate7"]={}
            for side in ("home","away","None"):
                g=context.check(ctx, None if side=="None" else side)
                rec["gate7"][side]={"passed":g.passed,"reason":getattr(g,'reason','')}
            print(f"OK  {comp[:20]:22s} {key[:32]:34s} rich={rich.total:5.1f} lineup={ctx.lineup_type or '-':10s} reloc={ctx.venue.relocated} g7h={rec['gate7']['home']['passed']} g7a={rec['gate7']['away']['passed']}", flush=True)
        except Exception as e:
            rec["ctx_error"]=f"{type(e).__name__}: {e}"
            rich = ranking.data_richness(None,None,None,ph,pa)
            rec["richness"]={"score":rich.total,"parts":rich.parts,"summary":rich.summary(),"notes":rich.notes}
            rec["gate7"]={s:{"passed":True,"reason":"context niet opgehaald — poort open"} for s in ("home","away","None")}
            print(f"ERR {comp[:20]:22s} {key[:32]:34s} {type(e).__name__}: {e} -> rich={rich.total:.1f}", flush=True)
        out[key]=rec
json.dump(out, open("tmp-run/c_ctx.json","w"), ensure_ascii=False, indent=1, default=str)
print("klaar:", len(out))

"""Stage 5-controle: hoe ver zit het model van de markt op P(Over 2.5), vóór en ná de
vroeg-seizoenscorrectie? Dit is CONTROLEREN, geen fitten (§5) — de factor zelf komt
uitsluitend uit xG-waarnemingen."""
import json, sys
sys.path.insert(0,'.'); sys.path.insert(0,'tmp-run')
from scripts import fotmob
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
    splits_from_fotmob, totals_prob, scale_level, blend_seasons)
from scripts.promotion import find_team
from scripts.oddsapi import best_by_line
from b_merge import merge_teams

M=json.load(open("tmp-run/b_matches.json")); L=json.load(open("tmp-run/b_leagues.json"))
API=json.load(open("tmp-run/b_oddsapi.json")); A=json.load(open("tmp-run/b_analysis.json"))
UP=L["_uplift"]["factor"]

def stats_merged(lid, season):
    st=dict(fotmob.fetch_league_stats(lid, season)); st["teams"],_=merge_teams(st["teams"]); return st

rows=[]
for comp,blk in M.items():
    if not L[comp]["uplift"]: continue
    evs=API["totals"].get(comp) or []
    if not evs: continue
    st=stats_merged(blk["league_id"], L[comp]["base_season"])
    lvl=st
    avg=lvl["avg_xg_per_match"] or (lvl["home_goals_per_match"]+lvl["away_goals_per_match"])/2
    base=LeagueContext(lvl["home_goals_per_match"], lvl["away_goals_per_match"], avg)
    cur=stats_merged(blk["league_id"], L[comp]["cur_season"])["teams"]
    has_xg = st["avg_xg_per_match"] is not None
    def ts_for(name):
        rn=find_team(st["teams"],name)
        if not rn: return None,None
        t=st["teams"][rn]
        s=TeamStats(t["xg"],t["xga"],t["mp"]) if (has_xg and t.get("xg") is not None) else TeamStats(float(t["gf"]),float(t["ga"]),t["played"])
        cn=find_team(cur,name)
        if cn:
            c=cur[cn]
            cs=TeamStats(c["xg"],c["xga"],c["mp"]) if (has_xg and c.get("xg") is not None) else (
                TeamStats(float(c["gf"]),float(c["ga"]),c["played"]) if c.get("played") else None)
            if cs: s=blend_seasons(s,cs)
        return s, splits_from_fotmob(t)
    for m in blk["matches"]:
        key=f"{m['home']} – {m['away']}"
        if A[key]["tier"]=="NONE": continue
        hs,hsp=ts_for(m["home"]); as_,asp=ts_for(m["away"])
        if not hs or not as_: continue
        ev=None
        for e in evs:
            if e.get("commence_time")==m["utc"].replace(".000Z","Z"): ev=e; break
        if not ev: continue
        bl=best_by_line(ev,"totals")
        o_over=bl.get(("Over",2.5)); o_under=bl.get(("Under",2.5))
        if not (o_over and o_under): continue
        inv=1/o_over[0]+1/o_under[0]
        mkt=(1/o_over[0])/inv
        for tag,lg in (("zonder",base),("met",scale_level(base,UP))):
            p1=analyze_match(hs,as_,lg); p2=analyze_match_from_splits(hsp,asp,league=lg)
            my=(totals_prob(p1.grid,2.5,"over",2.0)+totals_prob(p2.grid,2.5,"over",2.0))/2
            rows.append((key,tag,round((my-mkt)*100,2)))
for tag in ("zonder","met"):
    d=[r[2] for r in rows if r[1]==tag]
    if d: print(f"P(Over 2.5) t.o.v. de de-vigde markt, {tag} correctie: gemiddeld {sum(d)/len(d):+.2f} pp over {len(d)} duels; "
                f"gem. absolute fout {sum(abs(x) for x in d)/len(d):.2f} pp")
for k,tag,v in rows:
    if tag=="met": print(f"   {k:34s} {v:+7.2f} pp")

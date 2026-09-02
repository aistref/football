import json, sys, math
from datetime import date, datetime, timezone, timedelta
sys.path.insert(0,'.')
from scripts import fotmob, model, context, calibration, promotion
from scripts.model import (TeamStats, TeamSplits, LeagueContext, analyze_match,
    analyze_match_from_splits, splits_from_fotmob, robustness_check, edge_pp,
    asian_prob, dnb_prob, totals_prob, selection_score, scale_level, early_season_uplift)
from scripts.oddsapi import best_by_line

EDGE_FULL, EDGE_LIGHT = 8.0, 16.0
MIN_ODDS, MAX_ODDS = 1.30, 6.00

M=json.load(open("tmp-run/matches.json")); L=json.load(open("tmp-run/leagues.json"))
CTX=json.load(open("tmp-run/context.json")); OD1=json.load(open("tmp-run/odds1x2.json"))
API=json.load(open("tmp-run/odds_api.json"))
UP = L["_uplift"]["factor"]

# ---- league contexts + team stats
LG={}
for comp,blk in M.items():
    prev=fotmob.fetch_league_stats(blk["league_id"], L[comp]["prev_season"])
    base=LeagueContext(prev["home_goals_per_match"], prev["away_goals_per_match"],
                       prev["avg_xg_per_match"] if prev["has_xg"] else
                       (prev["home_goals_per_match"]+prev["away_goals_per_match"])/2)
    LG[comp]={"stats":prev,"league":scale_level(base, UP),"has_xg":prev["has_xg"]}

def find(teams, name):
    if name in teams: return name
    low=name.lower()
    cands=[n for n in teams if n.lower()==low]
    if cands: return cands[0]
    cands=[n for n in teams if low in n.lower() or n.lower() in low]
    if len(cands)==1: return cands[0]
    # token overlap
    toks=set(low.replace('.',' ').split())
    best=None;bs=0
    for n in teams:
        s=len(toks & set(n.lower().replace('.',' ').split()))
        if s>bs: bs=s;best=n
    return best if bs else None

# name maps for odds sources
def match_odds_row(comp, home, away, rows):
    if isinstance(rows, dict): return None
    for r in rows:
        if not r.get("is_today"): continue
        if find({r["home"]:1}, home) or find({home:1}, r["home"]):
            if find({r["away"]:1}, away) or find({away:1}, r["away"]):
                return r
    # fallback fuzzy
    def norm(s): return s.lower().replace("fc","").replace("afc","").replace("1905","").replace(".","").strip()
    for r in rows:
        if not r.get("is_today"): continue
        if norm(r["home"])[:5]==norm(home)[:5] and norm(r["away"])[:5]==norm(away)[:5]: return r
    return None

def api_event(comp, home, away, kind):
    evs = API[kind].get(comp) or []
    def norm(s): return "".join(ch for ch in s.lower() if ch.isalnum())
    for e in evs:
        h,a = norm(e["home_team"]), norm(e["away_team"])
        H,A = norm(home), norm(away)
        if (H in h or h in H or H[:6]==h[:6]) and (A in a or a in A or A[:6]==a[:6]):
            return e
    return None

print(f"uplift factor {UP:.4f}")
out={}
for comp,blk in M.items():
    st=LG[comp]["stats"]; teams=st["teams"]; league=LG[comp]["league"]; has_xg=LG[comp]["has_xg"]
    for m in blk["matches"]:
        key=f"{m['home']} – {m['away']}"
        rec={"comp":comp,"match":key,"kickoff_utc":m["utc"],"match_id":m["id"]}
        hn, an = find(teams,m["home"]), find(teams,m["away"])
        rec["resolved"]={"home":hn,"away":an}
        row = match_odds_row(comp, m["home"], m["away"], OD1.get(comp,[]))
        rec["odds_1x2"] = row["odds"] if row else None
        rec["books_1x2"] = row["books"] if row else 0
        rec["sp_event"] = bool(api_event(comp,m["home"],m["away"],"spreads"))
        rec["to_event"] = bool(api_event(comp,m["home"],m["away"],"totals"))
        rec["missing"] = [x for x,v in (("home",hn),("away",an)) if v is None]
        out[key]=rec
        print(f"{comp[:20]:22s} {key[:34]:36s} xg={has_xg} home={hn} away={an} 1x2={rec['odds_1x2']} sp={rec['sp_event']} to={rec['to_event']}")
json.dump(out, open("tmp-run/premap.json","w"), ensure_ascii=False, indent=1)

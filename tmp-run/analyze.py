import json, sys
from datetime import date
sys.path.insert(0,'.')
from scripts import fotmob, model, context, calibration, promotion
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
    splits_from_fotmob, robustness_check, edge_pp, asian_prob, dnb_prob, totals_prob,
    selection_score, scale_level, DEFAULT_RHO)
from scripts.promotion import find_team
from scripts.oddsapi import best_by_line

EDGE={"FULL":8.0,"LIGHT":16.0}; MIN_ODDS,MAX_ODDS=1.30,6.00
M=json.load(open("tmp-run/matches.json")); L=json.load(open("tmp-run/leagues.json"))
CTX=json.load(open("tmp-run/context.json")); OD1=json.load(open("tmp-run/odds1x2.json"))
API=json.load(open("tmp-run/odds_api.json")); UP=L["_uplift"]["factor"]
import os
BTTS=json.load(open("tmp-run/btts.json")) if os.path.exists("tmp-run/btts.json") else {}
ALIAS={"Wimbledon":"AFC Wimbledon","MK Dons":"Milton Keynes Dons"}
# De runlijst noemt de competitie "English League One (ENG)"; promotion.TIER2 kent hem als
# "League One (ENG)". Zonder deze vertaling valt elke promovendus daar op een ontbrekende
# aanroep in plaats van op een ontbrekende meting.
TIER2_KEY={"English League One (ENG)":"League One (ENG)"}

LG={}
for comp,blk in M.items():
    st=fotmob.fetch_league_stats(blk["league_id"], L[comp]["prev_season"])
    avg = st["avg_xg_per_match"] if st["has_xg"] else (st["home_goals_per_match"]+st["away_goals_per_match"])/2
    base=LeagueContext(st["home_goals_per_match"], st["away_goals_per_match"], avg)
    LG[comp]={"stats":st,"league":scale_level(base,UP),"base":base,"has_xg":st["has_xg"]}

def team_inputs(comp, name):
    """(TeamStats, TeamSplits, tier_hint, note)"""
    st=LG[comp]["stats"]; teams=st["teams"]; has_xg=LG[comp]["has_xg"]
    row_name = find_team(teams, ALIAS.get(name, name))
    if row_name:
        t=teams[row_name]
        if has_xg and "xg" in t:
            ts=TeamStats(t["xg"], t["xga"], t["mp"])
        else:
            ts=TeamStats(float(t["gf"]), float(t["ga"]), t["played"])
        return ts, splits_from_fotmob(t), ("FULL" if has_xg else "LIGHT"), \
               f"{row_name} uit {comp} {L[comp]['prev_season']}" + ("" if has_xg else " (doelpunten, geen xG bij Fotmob)")
    tier2_comp = TIER2_KEY.get(comp, comp)
    c=promotion.convert(tier2_comp, ALIAS.get(name,name), L[comp]["prev_season"], LG[comp]["league"])
    return c.stats, c.splits, c.tier, c.note

import unicodedata
def norm(s):
    s=unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii","ignore").decode()
    return "".join(ch for ch in s if ch.isalnum())
def _same(a, b):
    """Twee clubnamen van verschillende bronnen. Alleen containment of een gedeeld woord van >=4
    letters telt — geen losse prefixvergelijking, want die koppelde 'FC Vaduz' aan 'FC Zurich'."""
    A, B = norm(a), norm(b)
    if A == B or A in B or B in A: return True
    wa = {w for w in norm_words(a) if len(w) >= 4}
    wb = {w for w in norm_words(b) if len(w) >= 4}
    return bool(wa & wb)

def norm_words(s):
    import unicodedata, re
    s = unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii","ignore").decode()
    return [w for w in re.split(r"[^a-z0-9]+", s) if w and w not in ("fc","afc","sc","bsc","rb","1905")]

def api_event(comp, home, away, kind, kickoff=None):
    """Koppel op aftraptijd én naam. De aftraptijd is de betrouwbaarste sleutel; de namen
    verschillen per bron ('MK Dons' / 'Milton Keynes Dons', 'Salzburg' / 'RB Salzburg')."""
    evs = API[kind].get(comp) or []
    if kickoff:
        k = kickoff.replace(".000Z","Z")
        timed = [e for e in evs if e.get("commence_time") == k]
        for e in timed:
            if _same(e["home_team"], home) and _same(e["away_team"], away): return e
        if len(timed) == 1 and _same(timed[0]["home_team"], home): return timed[0]
    for e in evs:
        if _same(e["home_team"], home) and _same(e["away_team"], away): return e
    return None
#: BetExplorer schrijft sommige clubs anders dan de Fotmob-daglijst; alleen handmatig
#: gecontroleerde paren, want een losse deelstringmatch koppelde eerder 'FC Vaduz' aan 'FC Zurich'.
BEX_ALIAS = {"Austria Wien": "Austria Vienna", "Salzburg": "RB Salzburg",
             "Grasshopper": "Grasshoppers", "FC Vaduz": "Vaduz", "Rapid Wien": "SK Rapid",
             "WSG Tirol": "Tirol", "FC Zbrojovka Brno": "Brno", "Bohemians 1905": "Bohemians"}

def x2_row(comp, home, away):
    rows=OD1.get(comp) or []
    if isinstance(rows,dict): return None
    H = BEX_ALIAS.get(home, home); A = BEX_ALIAS.get(away, away)
    for r in rows:
        if not r.get("is_today"): continue
        if _same(r["home"], H) and _same(r["away"], A): return r
    return None

results={}
for comp,blk in M.items():
    league=LG[comp]["league"]
    for m in blk["matches"]:
        key=f"{m['home']} – {m['away']}"
        rec={"comp":comp,"match":key,"kickoff_utc":m["utc"],"match_id":m["id"],
             "markets_checked":{}, "candidates":[], "bet":False}
        try:
            hs,hsp,ht,hnote = team_inputs(comp,m["home"])
            as_,asp,at,anote = team_inputs(comp,m["away"])
        except Exception as e:
            rec["tier"]="NONE"; rec["reason"]=f"omrekening onmogelijk: {type(e).__name__}: {e}"
            results[key]=rec; print(f"NONE {key}: {rec['reason']}"); continue
        tier = "LIGHT" if "LIGHT" in (ht,at) else "FULL"
        rec["tier"]=tier; rec["inputs"]={"home":hnote,"away":anote}
        rec["team_stats"]={"home":{"xg":hs.xg,"xga":hs.xga,"mp":hs.matches_played},
                           "away":{"xg":as_.xg,"xga":as_.xga,"mp":as_.matches_played}}
        p_xg = analyze_match(hs, as_, league)
        p_xg_ns = analyze_match(hs, as_, league, shrink=1.0)
        p_sp = analyze_match_from_splits(hsp, asp, league=league)
        rec["lambdas"]={"xg":[round(p_xg.lambda_home,3),round(p_xg.lambda_away,3)],
                        "split":[round(p_sp.lambda_home,3),round(p_sp.lambda_away,3)]}
        g7 = CTX[key]["gate7"]; rich = CTX[key]["richness"]
        rec["richness"]=rich; rec["gate7"]=g7
        rec["datarijkdom"]=rich

        cands=[]
        def add(market, label, side, odds, src, pf_xg, pf_sp, line=None, select=None):
            if not odds: return
            my=(pf_xg+pf_sp)/2
            e=edge_pp(my,odds)
            rob = robustness_check(hs, as_, league, select, odds) if select else None
            gates={"edge": e>=EDGE[tier], "odds": MIN_ODDS<=odds<=MAX_ODDS,
                   "tier": tier!="NONE",
                   "tweede_methode": (pf_xg>1/odds and pf_sp>1/odds),
                   "robuustheid": (rob.min_edge > 0) if rob else False,
                   "context": g7[side if side else "None"]["passed"]}
            c={"market":market,"selection":label,"odds":round(odds,3),"odds_source":src,
               "line":line,"side":side,"my_prob":round(my,4),"implied":round(1/odds,4),
               "edge_pp":round(e,2),"edge_xg":round(edge_pp(pf_xg,odds),2),
               "edge_split":round(edge_pp(pf_sp,odds),2),
               "edge_robust_min":round(rob.min_edge,2) if rob else None,
               "edge_robust_max":round(rob.max_edge,2) if rob else None,"gates":gates}
            cands.append(c)

        # --- 1X2 (BetExplorer, free)
        row=x2_row(comp,m["home"],m["away"])
        if row:
            o1,ox,o2=row["odds"]
            src=f"BetExplorer marktgemiddelde over {row['books']} boeken (bookmaker niet herleidbaar)"
            add("1X2",f"1 ({m['home']} wint)","home",o1,src,p_xg.home,p_sp.home,select=lambda r: r.home)
            add("1X2","X (gelijkspel)",None,ox,src,p_xg.draw,p_sp.draw,select=lambda r: r.draw)
            add("1X2",f"2 ({m['away']} wint)","away",o2,src,p_xg.away,p_sp.away,select=lambda r: r.away)
            rec["markets_checked"]["1X2"]=f"BetExplorer, {row['books']} boeken"
            rec["odds_1x2"]=row["odds"]; rec["books_1x2"]=row["books"]
        else:
            rec["markets_checked"]["1X2"]="geen rij op de BetExplorer-fixturespagina"

        # --- spreads -> AH, DNB, DC
        ev=api_event(comp,m["home"],m["away"],"spreads",m["utc"])
        if ev:
            bl=best_by_line(ev,"spreads")
            n_ah=n_dnb=n_dc=0
            for (outcome,line),(odds,book) in bl.items():
                side = "home" if _same(outcome, ev["home_team"]) else "away"
                if line is None: continue
                if abs(line)<1e-9:
                    add("Draw No Bet",f"DNB — {outcome}",side,odds,f"The Odds API, {book}",
                        dnb_prob(p_xg.grid,side,odds), dnb_prob(p_sp.grid,side,odds), line,
                        select=(lambda sd, od: (lambda r: dnb_prob(r.grid, sd, od)))(side, odds)); n_dnb+=1
                elif abs(line-0.5)<1e-9:
                    lab = f"Double Chance — {outcome} of gelijk (AH +0.5 @ {odds})"
                    add("Double Chance",lab,side,odds,f"The Odds API, {book}",
                        asian_prob(p_xg.grid,line,side,odds), asian_prob(p_sp.grid,line,side,odds), line,
                        select=(lambda ln, sd, od: (lambda r: asian_prob(r.grid, ln, sd, od)))(line, side, odds)); n_dc+=1
                else:
                    add("Asian Handicap",f"{outcome} {line:+g}",side,odds,f"The Odds API, {book}",
                        asian_prob(p_xg.grid,line,side,odds), asian_prob(p_sp.grid,line,side,odds), line,
                        select=(lambda ln, sd, od: (lambda r: asian_prob(r.grid, ln, sd, od)))(line, side, odds)); n_ah+=1
            rec["markets_checked"]["AH"]=f"The Odds API spreads, {n_ah} lijnen"
            rec["markets_checked"]["DNB"]=f"0.0-lijn uit dezelfde spreads, {n_dnb} selecties" if n_dnb else "geen 0.0-lijn in de spreads-respons"
            rec["markets_checked"]["DC"]=f"±0.5-lijn uit dezelfde spreads, {n_dc} selecties" if n_dc else "geen ±0.5-lijn in de spreads-respons"
        else:
            why = "geen sportkey bij The Odds API voor deze competitie" if comp=="Czech First League (CZE)" else "geen spreads-event bij The Odds API"
            for k in ("AH","DNB","DC"): rec["markets_checked"][k]=why

        # --- totals
        ev=api_event(comp,m["home"],m["away"],"totals",m["utc"])
        if ev:
            bl=best_by_line(ev,"totals"); n=0
            for (outcome,line),(odds,book) in bl.items():
                if line is None: continue
                s = "over" if outcome.lower().startswith("over") else "under"
                add("Over/Under",f"{outcome} {line:g}",None,odds,f"The Odds API, {book}",
                    totals_prob(p_xg.grid,line,s,odds), totals_prob(p_sp.grid,line,s,odds), line,
                    select=(lambda ln, sd, od: (lambda r: totals_prob(r.grid, ln, sd, od)))(line, s, odds)); n+=1
            rec["markets_checked"]["OU"]=f"The Odds API totals, {n} lijnen"
        else:
            rec["markets_checked"]["OU"]="geen sportkey bij The Odds API voor deze competitie" if comp=="Czech First League (CZE)" else "geen totals-event bij The Odds API"

        # --- BTTS (per wedstrijd gekocht, 1 credit; zie runrapport)
        bev = BTTS.get(key)
        if bev and not (isinstance(bev, dict) and bev.get("error")):
            bl = best_by_line(bev, "btts"); n=0
            for (outcome, _), (odds, book) in bl.items():
                yes = outcome.lower().startswith("y")
                add("BTTS", "Beide ploegen scoren — " + ("ja" if yes else "nee"), None, odds,
                    f"The Odds API, {book}",
                    p_xg.btts if yes else 1-p_xg.btts, p_sp.btts if yes else 1-p_sp.btts,
                    select=(lambda y: (lambda r: r.btts if y else 1-r.btts))(yes)); n+=1
            rec["markets_checked"]["BTTS"]=f"The Odds API event-markt, {n} selecties (1 credit)"
        elif bev:
            rec["markets_checked"]["BTTS"]=f"opgevraagd maar mislukt: {bev.get('error')}"
        else:
            rec["markets_checked"]["BTTS"]="geen sportkey bij The Odds API voor deze competitie"

        rec["candidates"]=cands
        rec["p"]={"xg":[round(p_xg.home,4),round(p_xg.draw,4),round(p_xg.away,4)],
                  "xg_noshrink":[round(p_xg_ns.home,4),round(p_xg_ns.draw,4),round(p_xg_ns.away,4)],
                  "split":[round(p_sp.home,4),round(p_sp.draw,4),round(p_sp.away,4)]}
        if rec.get("odds_1x2"):
            dv=calibration.devig(rec["odds_1x2"])
            rec["calibration"]={"market":[round(x,4) for x in dv],"p_xg":rec["p"]["xg"],
                                "p_xg_noshrink":rec["p"]["xg_noshrink"],"p_split":rec["p"]["split"]}
        rec["_grids"]=True
        results[key]=rec
        best=max(cands,key=lambda c:c["edge_pp"]) if cands else None
        print(f"{tier:5s} {key[:34]:36s} n_cand={len(cands):3d} best_edge={best['edge_pp'] if best else '-':>6} {best['market'] if best else ''}")

json.dump(results, open("tmp-run/analysis.json","w"), ensure_ascii=False, indent=1)

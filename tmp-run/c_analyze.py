import json, sys, unicodedata, re
sys.path.insert(0,'.'); sys.path.insert(0,'tmp-run')
from scripts import fotmob, model, calibration, promotion
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
    splits_from_fotmob, robustness_check, edge_pp, asian_prob, dnb_prob, totals_prob,
    selection_score, scale_level, blend_seasons, blend_weight)
from scripts.promotion import find_team
from scripts.oddsapi import best_by_line
from b_merge import merge_teams

EDGE={"FULL":8.0,"LIGHT":16.0}; MIN_ODDS,MAX_ODDS=1.30,6.00
M=json.load(open("tmp-run/c_matches.json")); L=json.load(open("tmp-run/c_leagues.json"))
CTX=json.load(open("tmp-run/c_ctx.json")); OD1=json.load(open("tmp-run/c_bx.json"))
API=json.load(open("tmp-run/c_oddsapi.json")); RANK=json.load(open("tmp-run/c_rank.json"))
try: BTTS=json.load(open("tmp-run/c_btts.json"))
except FileNotFoundError: BTTS={}
UP=L["_uplift"]["factor"]
SELECTED=set(RANK["selected"])

def stats_merged(league_id, season):
    st=fotmob.fetch_league_stats(league_id, season)
    st=dict(st); st["teams"], st["_merged"] = merge_teams(st["teams"])
    return st

COMPS=[c for c in M if c in L]
LG={}
for comp in COMPS:
    blk=M[comp]; cfg=L[comp]
    st = stats_merged(blk["league_id"], cfg["base_season"])
    lvl = st if cfg["level_season"]==cfg["base_season"] else stats_merged(blk["league_id"], cfg["level_season"])
    avg = lvl["avg_xg_per_match"] if lvl["avg_xg_per_match"] else (lvl["home_goals_per_match"]+lvl["away_goals_per_match"])/2
    base=LeagueContext(lvl["home_goals_per_match"], lvl["away_goals_per_match"], avg)
    cur_teams={}
    if cfg["cur_season"]!=cfg["base_season"]:
        try: cur_teams = stats_merged(blk["league_id"], cfg["cur_season"])["teams"]
        except Exception as e: print(f"  {comp}: lopend seizoen niet op te halen ({type(e).__name__})")
    LG[comp]={"stats":st,"league":scale_level(base,UP) if cfg["uplift"] else base,"base":base,
              "has_xg":st["avg_xg_per_match"] is not None,"cur_teams":cur_teams,
              "merged":st.get("_merged") or []}
    print(f"{comp}: sterkte {cfg['base_season']} has_xg={LG[comp]['has_xg']} · niveau {cfg['level_season']} "
          f"({base.home_goals_per_match:.3f}/{base.away_goals_per_match:.3f}) uplift={cfg['uplift']} merged={len(LG[comp]['merged'])}", flush=True)

# Fixture-naam -> naam in de Fotmob-standentabel. `find_team` accepteert een afkorting alleen als
# **voorvoegsel** (bewust: zo koppelt "Ajax" niet aan "Jong Ajax"), en deze drie zijn dat niet.
# Gemeten 5 sep 2026: zonder deze drie regels kwamen Peterborough - Sheff Wed, Wycombe - MK Dons en
# Rosenborg - HamKam op NONE uit, terwijl alle drie de ploegen gewoon in de tabel van vorig seizoen
# staan. HamKam is niet eens een promovendus - hij heet in de stand voluit.
ALIAS={"Sheff Wed":"Sheffield Wednesday","MK Dons":"Milton Keynes Dons","HamKam":"Hamarkameratene"}
def team_inputs(comp, name):
    st=LG[comp]["stats"]; teams=st["teams"]; has_xg=LG[comp]["has_xg"]
    name = ALIAS.get(name, name)     # ook de omrekening hieronder zoekt op deze naam
    row_name = find_team(teams, name)
    if not row_name:
        errs=[]
        for fn, kind in ((promotion.convert, "promovendus"), (promotion.convert_relegated, "degradant")):
            try: c = fn(comp, name, L[comp]["base_season"], LG[comp]["league"])
            except Exception as e: errs.append(f"{kind}: {type(e).__name__}: {e}"); continue
            if c.tier=="NONE": raise KeyError(f"{name}: omrekening buiten het gemeten bereik — {c.note}")
            return c.stats, c.splits, c.tier, f"{name} omgerekend als {kind} — {c.note}", None
        raise KeyError(f"{name} niet in de tabel van {comp} {L[comp]['base_season']}; " + " | ".join(errs))
    t=teams[row_name]
    if has_xg and t.get("xg") is not None: ts=TeamStats(t["xg"], t["xga"], t["mp"])
    else: ts=TeamStats(float(t["gf"]), float(t["ga"]), t["played"])
    note=f"{row_name} uit {comp} {L[comp]['base_season']}" + ("" if has_xg else " (doelpunten, geen xG bij Fotmob)")
    weging=None
    cur_teams=LG[comp].get("cur_teams") or {}
    cur_name=find_team(cur_teams, name) if cur_teams else None
    if cur_name:
        cr=cur_teams[cur_name]
        if has_xg and cr.get("mp") and cr.get("xg") is not None: cur=TeamStats(cr["xg"], cr["xga"], cr["mp"])
        elif (not has_xg) and cr.get("played") and cr.get("gf") is not None: cur=TeamStats(float(cr["gf"]), float(cr["ga"]), cr["played"])
        else: cur=None
        if cur:
            merged=blend_seasons(ts, cur)
            weging={"duels_dit_seizoen":cur.matches_played,
                    "gewicht_dit_seizoen":round(blend_weight(cur.matches_played),3),
                    "eenheid":"xG" if has_xg else "doelpunten",
                    "per_duel_voor":{"vorig":round(ts.xg_per_match,3),"dit":round(cur.xg_per_match,3),"gewogen":round(merged.xg_per_match,3)},
                    "tegen_per_duel":{"vorig":round(ts.xga_per_match,3),"dit":round(cur.xga_per_match,3),"gewogen":round(merged.xga_per_match,3)}}
            note += f"; lopend seizoen {cur.matches_played} duels meegewogen voor {weging['gewicht_dit_seizoen']:.0%}"
            ts=merged
    return ts, splits_from_fotmob(t), ("FULL" if has_xg else "LIGHT"), note, weging

def norm(s):
    s=unicodedata.normalize("NFKD",(s or "").lower()).encode("ascii","ignore").decode()
    return "".join(ch for ch in s if ch.isalnum())
STOP=("fc","afc","sc","bsc","if","aif","ik","eto","cf","ud","sd","cd","ac","nk","hk","fk","cfc","utd","town","city","united")
def norm_words(s):
    s=unicodedata.normalize("NFKD",(s or "").lower()).encode("ascii","ignore").decode()
    return [w for w in re.split(r"[^a-z0-9]+",s) if w and w not in STOP]
def _same(a,b):
    A,B=norm(a),norm(b)
    if A==B or A in B or B in A: return True
    wa={w for w in norm_words(a) if len(w)>=4}; wb={w for w in norm_words(b) if len(w)>=4}
    return bool(wa & wb)

def api_event(comp, home, away, kind, kickoff=None):
    evs = API[kind].get(comp) or []
    if kickoff:
        k=kickoff.replace(".000Z","Z")
        timed=[e for e in evs if e.get("commence_time")==k]
        for e in timed:
            if _same(e["home_team"],home) and _same(e["away_team"],away): return e
        if len(timed)==1 and _same(timed[0]["home_team"],home): return timed[0]
    for e in evs:
        if _same(e["home_team"],home) and _same(e["away_team"],away): return e
    return None

BEX_ALIAS={"Sheff Wed":"Sheffield Wed","Oxford Utd":"Oxford Utd","MK Dons":"Milton Keynes Dons",
           "Real Sociedad B":"Sociedad B","Celta Fortuna":"Celta B","AD Ceuta FC":"Ceuta",
           "Sporting Gijón":"Sporting Gijon","Västerås SK":"Vasteras SK","Halmstads BK":"Halmstad",
           "Lillestrøm":"Lillestrom","Energie Cottbus":"Cottbus","Holstein Kiel":"Holstein Kiel",
           "1. FC Nürnberg":"Nurnberg","Aris Thessaloniki":"Aris","Grasshopper":"Grasshoppers",
           "FC Zürich":"Zurich","FC Vaduz":"Vaduz","Stockport County":"Stockport",
           "Notts County":"Notts County","York City":"York","Port Vale":"Port Vale"}
def x2_row(comp, home, away):
    rows=OD1.get(comp) or []
    if isinstance(rows,dict): return None
    H=BEX_ALIAS.get(home,home); A=BEX_ALIAS.get(away,away)
    for r in rows:
        if not r.get("is_today"): continue
        if _same(r["home"],H) and _same(r["away"],A): return r
    return None

results={}
for comp in COMPS:
    league=LG[comp]["league"]
    for m in M[comp]["matches"]:
        key=f"{m['home']} – {m['away']}"
        if key not in SELECTED: continue
        rec={"comp":comp,"match":key,"kickoff_utc":m["utc"],"match_id":m["id"],
             "markets_checked":{}, "candidates":[], "bet":False}
        try:
            hs,hsp,ht,hnote,hw = team_inputs(comp,m["home"])
            as_,asp,at,anote,aw = team_inputs(comp,m["away"])
        except Exception as e:
            rec["tier"]="NONE"; rec["reason"]=f"{type(e).__name__}: {e}"
            rec["richness"]=CTX[key]["richness"]; rec["datarijkdom"]=CTX[key]["richness"]
            results[key]=rec; print(f"NONE {key}: {rec['reason']}", flush=True); continue
        tier = "LIGHT" if "LIGHT" in (ht,at) else "FULL"
        rec["tier"]=tier; rec["inputs"]={"home":hnote,"away":anote}
        if hw or aw: rec["seizoensweging"]={k:v for k,v in ((m["home"],hw),(m["away"],aw)) if v}
        rec["team_stats"]={"home":{"xg":hs.xg,"xga":hs.xga,"mp":hs.matches_played},
                           "away":{"xg":as_.xg,"xga":as_.xga,"mp":as_.matches_played}}
        p_xg=analyze_match(hs,as_,league); p_xg_ns=analyze_match(hs,as_,league,shrink=1.0)
        p_sp=analyze_match_from_splits(hsp,asp,league=league)
        rec["lambdas"]={"xg":[round(p_xg.lambda_home,3),round(p_xg.lambda_away,3)],
                        "split":[round(p_sp.lambda_home,3),round(p_sp.lambda_away,3)]}
        g7=CTX[key]["gate7"]; rec["richness"]=CTX[key]["richness"]; rec["datarijkdom"]=CTX[key]["richness"]
        rec["gate7"]=g7
        cb=CTX[key].get("ctx") or {}
        rec["context"]={"lineup_type":cb.get("lineup_type"),"venue":cb.get("venue"),
                        "home":cb.get("home_summary"),"away":cb.get("away_summary")}
        cands=[]
        def add(market,label,side,odds,src,pf_xg,pf_sp,line=None,select=None):
            if not odds: return
            my=(pf_xg+pf_sp)/2; e=edge_pp(my,odds)
            rob=robustness_check(hs,as_,league,select,odds) if select else None
            gates={"edge":e>=EDGE[tier],"odds":MIN_ODDS<=odds<=MAX_ODDS,"tier":tier!="NONE",
                   "tweede_methode":(pf_xg>1/odds and pf_sp>1/odds),
                   "robuustheid":(rob.min_edge>0) if rob else False,
                   "context":g7[side if side else "None"]["passed"]}
            cands.append({"market":market,"selection":label,"odds":round(odds,3),"odds_source":src,
                "line":line,"side":side,"my_prob":round(my,4),"implied":round(1/odds,4),
                "edge_pp":round(e,2),"edge_xg":round(edge_pp(pf_xg,odds),2),
                "edge_split":round(edge_pp(pf_sp,odds),2),
                "edge_robust_min":round(rob.min_edge,2) if rob else None,
                "edge_robust_max":round(rob.max_edge,2) if rob else None,
                "score":round(selection_score(e,my,tier),3),"gates":gates})
        # ALIAS geldt ook voor de prijsbronnen: The Odds API schrijft "Sheffield Wednesday" waar de
        # Fotmob-daglijst "Sheff Wed" zegt, en _same() koppelt die twee niet (voorvoegsel noch woord).
        hn, an = ALIAS.get(m["home"], m["home"]), ALIAS.get(m["away"], m["away"])
        row=x2_row(comp,m["home"],m["away"]) or x2_row(comp,hn,an)
        if row:
            o1,ox,o2=row["odds"]; books=row.get("books")
            src=f"BetExplorer marktgemiddelde{'' if not books else f' over {books} boeken'} (bookmaker niet herleidbaar)"
            add("1X2",f"1 ({m['home']} wint)","home",o1,src,p_xg.home,p_sp.home,select=lambda r:r.home)
            add("1X2","X (gelijkspel)",None,ox,src,p_xg.draw,p_sp.draw,select=lambda r:r.draw)
            add("1X2",f"2 ({m['away']} wint)","away",o2,src,p_xg.away,p_sp.away,select=lambda r:r.away)
            rec["markets_checked"]["1X2"]="BetExplorer fixturespagina (marktgemiddelde)"
            rec["odds_1x2"]=row["odds"]
        else:
            rec["markets_checked"]["1X2"]="geen rij op de BetExplorer-fixturespagina"
        NOKEY="geen sportkey bij The Odds API voor deze competitie"
        ev=api_event(comp,m["home"],m["away"],"spreads",m["utc"]) or api_event(comp,hn,an,"spreads",m["utc"])
        if ev:
            bl=best_by_line(ev,"spreads"); n_ah=n_dnb=n_dc=0
            for (outcome,line),(odds,book) in bl.items():
                side="home" if _same(outcome,ev["home_team"]) else "away"
                if line is None: continue
                if abs(line)<1e-9:
                    add("Draw No Bet",f"DNB — {outcome}",side,odds,f"The Odds API, {book}",
                        dnb_prob(p_xg.grid,side,odds), dnb_prob(p_sp.grid,side,odds), line,
                        select=(lambda sd,od:(lambda r: dnb_prob(r.grid,sd,od)))(side,odds)); n_dnb+=1
                elif abs(line-0.5)<1e-9:
                    add("Double Chance",f"Double Chance — {outcome} of gelijk (AH +0.5 @ {odds})",side,odds,
                        f"The Odds API, {book}", asian_prob(p_xg.grid,line,side,odds),
                        asian_prob(p_sp.grid,line,side,odds), line,
                        select=(lambda ln,sd,od:(lambda r: asian_prob(r.grid,ln,sd,od)))(line,side,odds)); n_dc+=1
                else:
                    add("Asian Handicap",f"{outcome} {line:+g}",side,odds,f"The Odds API, {book}",
                        asian_prob(p_xg.grid,line,side,odds), asian_prob(p_sp.grid,line,side,odds), line,
                        select=(lambda ln,sd,od:(lambda r: asian_prob(r.grid,ln,sd,od)))(line,side,odds)); n_ah+=1
            rec["markets_checked"]["AH"]=f"The Odds API spreads, {n_ah} lijnen"
            rec["markets_checked"]["DNB"]=f"0.0-lijn uit dezelfde spreads, {n_dnb} selecties" if n_dnb else "geen 0.0-lijn in de spreads-respons"
            rec["markets_checked"]["DC"]=f"±0.5-lijn uit dezelfde spreads, {n_dc} selecties" if n_dc else "geen ±0.5-lijn in de spreads-respons"
        else:
            for k in ("AH","DNB","DC"): rec["markets_checked"][k]=NOKEY
        ev=api_event(comp,m["home"],m["away"],"totals",m["utc"]) or api_event(comp,hn,an,"totals",m["utc"])
        if ev:
            bl=best_by_line(ev,"totals"); n=0
            for (outcome,line),(odds,book) in bl.items():
                if line is None: continue
                s="over" if outcome.lower().startswith("over") else "under"
                add("Over/Under",f"{outcome} {line:g}",None,odds,f"The Odds API, {book}",
                    totals_prob(p_xg.grid,line,s,odds), totals_prob(p_sp.grid,line,s,odds), line,
                    select=(lambda ln,sd,od:(lambda r: totals_prob(r.grid,ln,sd,od)))(line,s,odds)); n+=1
            rec["markets_checked"]["OU"]=f"The Odds API totals, {n} lijnen"
        else:
            rec["markets_checked"]["OU"]=NOKEY
        bev=BTTS.get(key)
        if bev and not (isinstance(bev,dict) and bev.get("error")):
            bl=best_by_line(bev,"btts"); n=0
            for (outcome,_),(odds,book) in bl.items():
                yes=outcome.lower().startswith("y")
                add("BTTS","Beide ploegen scoren — "+("ja" if yes else "nee"),None,odds,
                    f"The Odds API, {book}", p_xg.btts if yes else 1-p_xg.btts,
                    p_sp.btts if yes else 1-p_sp.btts,
                    select=(lambda y:(lambda r: r.btts if y else 1-r.btts))(yes)); n+=1
            rec["markets_checked"]["BTTS"]=f"The Odds API event-markt, {n} selecties (2 credits)"
        else:
            rec["markets_checked"]["BTTS"]=BTTS.get("_reden","niet opgevraagd — geen kandidaat-edge in de goedkope markten (§1a stap 2)")
        rec["candidates"]=cands
        rec["p"]={"xg":[round(p_xg.home,4),round(p_xg.draw,4),round(p_xg.away,4)],
                  "xg_noshrink":[round(p_xg_ns.home,4),round(p_xg_ns.draw,4),round(p_xg_ns.away,4)],
                  "split":[round(p_sp.home,4),round(p_sp.draw,4),round(p_sp.away,4)],
                  "btts":{"xg":round(p_xg.btts,4),"split":round(p_sp.btts,4)}}
        if rec.get("odds_1x2"):
            dv=calibration.devig(rec["odds_1x2"])
            rec["calibration"]={"market":[round(x,4) for x in dv],"p_xg":rec["p"]["xg"],
                                "p_xg_noshrink":rec["p"]["xg_noshrink"],"p_split":rec["p"]["split"]}
        results[key]=rec
        best=max(cands,key=lambda c:c["edge_pp"]) if cands else None
        print(f"{tier:5s} {key[:32]:34s} n={len(cands):3d} best_edge={best['edge_pp'] if best else '-':>6} {best['market'] if best else ''}", flush=True)
json.dump(results, open("tmp-run/c_analysis.json","w"), ensure_ascii=False, indent=1)
print("wedstrijden doorgerekend:", len(results))

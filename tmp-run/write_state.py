import json, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'.')
A=json.load(open("tmp-run/analysis.json")); M=json.load(open("tmp-run/matches.json"))
CTX=json.load(open("tmp-run/context.json")); L=json.load(open("tmp-run/leagues.json"))
API=json.load(open("tmp-run/odds_api.json"))
NL=timezone(timedelta(hours=2))
RUNLIST=["Czech First League (CZE)","Greek Super League (GRE)","Eliteserien (NOR)","Allsvenskan (SWE)",
 "Croatian HNL (CRO)","Hungarian NB I (HUN)","Romanian SuperLiga (ROU)","Segunda División (ESP)",
 "Serie B (ITA)","2. Bundesliga (GER)","Swiss Super League (SUI)","Austrian Bundesliga (AUT)",
 "Keuken Kampioen Divisie (NED)","English League One (ENG)","English League Two (ENG)",
 "Kategoria Superiore (ALB)","Kosovo Superleague (KOS)"]
NOMATCH={
 "Greek Super League (GRE)":"alleen Cup Group Stage in de daglijst; dat is geen competitieduel",
 "Eliteserien (NOR)":"alleen Cup en NM Kvinner in de daglijst",
 "Allsvenskan (SWE)":"alleen Cup in de daglijst",
 "Croatian HNL (CRO)":"niets op de kalender",
 "Hungarian NB I (HUN)":"niets op de kalender",
 "Romanian SuperLiga (ROU)":"alleen drie Cup-groepsduels in de daglijst",
 "Segunda División (ESP)":"niets op de kalender",
 "Serie B (ITA)":"alleen Coppa Italia in de daglijst (Run A)",
 "2. Bundesliga (GER)":"alleen DFB Pokal en drie Regionalliga-groepen in de daglijst",
 "Keuken Kampioen Divisie (NED)":"niets op de kalender",
 "English League Two (ENG)":"niets op de kalender",
 "Kategoria Superiore (ALB)":"niets op de kalender",
 "Kosovo Superleague (KOS)":"geen enkele competitie met ccode KOS in de daglijst — ongewijzigd sinds 13 aug",
}
def nl(utc): return datetime.fromisoformat(utc.replace("Z","+00:00")).astimezone(NL).strftime("%H:%M")
def nl_iso(utc): return datetime.fromisoformat(utc.replace("Z","+00:00")).astimezone(NL).isoformat()

comps={}
for c in RUNLIST:
    if c in NOMATCH: comps[c]={"status":"GEEN WEDSTRIJD","toelichting":NOMATCH[c],"matches":[]}
for comp,blk in M.items():
    rows=[]
    for m in blk["matches"]:
        key=f"{m['home']} – {m['away']}"; r=A[key]; ctx=CTX[key]
        row={"match":key,"match_id":m["id"],"tier":r["tier"],"bet":bool(r.get("bet")),
             "kickoff_nl":nl(m["utc"]),"kickoff_utc":m["utc"],
             "markets_checked":r["markets_checked"],
             "datarijkdom":{"score":ctx["richness"]["score"],"deelscores":ctx["richness"]["parts"]},
             "context":ctx.get("ctx"),"turnover":ctx.get("turnover"),
             "inputs":r["inputs"],"lambdas":r["lambdas"],"team_stats":r["team_stats"],
             "gate7":{s:v["passed"] for s,v in r["gate7"].items()}}
        if r.get("calibration"): row["calibration"]=r["calibration"]
        if r.get("bet"):
            w=r["winner"]; s=r.get("second")
            row["pick"]={"market":w["market"],"selection":w["selection"],"odds":w["odds"],
                "odds_source":w["odds_source"],"my_prob":w["my_prob"],"implied":w["implied"],
                "edge_pp":w["edge_pp"],"edge_xg":w["edge_xg"],"edge_split":w["edge_split"],
                "edge_robust_min":w["edge_robust_min"],"score":w["score"]}
            row["second"]={"market":s["market"],"selection":s["selection"],"score":s["score"],
                           "gekwalificeerd":r.get("second_qualified",False)} if s else None
        elif r.get("near_miss"):
            nm=dict(r["near_miss"]); nm["edge_pp"]=nm.pop("edge_avg")
            row["near_miss"]=nm
            row["reden"]=f"geen selectie haalde alle zeven de poorten; sterkste kandidaat {nm['market']} @ {nm['odds']} viel af op {nm['failed_gate']} ({nm['edge_pp']:+.2f} pp gemiddeld)"
        else:
            row["reden"]="geen enkele kandidaat met een positieve edge"
        rows.append(row)
    comps[comp]={"status":"GEANALYSEERD","toelichting":f"{len(rows)} duels, alle {len(rows)} doorgerekend","matches":rows}

state={"run":"B","date":"2026-09-02","resumed_count":0,
 "competitions":{c:comps[c] for c in RUNLIST if c in comps},
 "completed":False,
 "parameters":{"MAX_DEEP_ANALYSES":30,"MAX_SHORTLIST":3,"EDGE_THRESHOLD_FULL":8.0,
   "EDGE_THRESHOLD_LIGHT":16.0,"MAX_LIGHT_IN_SHORTLIST":2,"MIN_ODDS":1.30,"MAX_ODDS":6.00,
   "SETTLE_AFTER_HOURS":12},
 "vroeg_seizoen":{"factor":L["_uplift"]["factor"],"gepoold":L["_uplift"]["pooled"],
   "speeldagen":L["_uplift"]["total_md"],"waarnemingen":L["_uplift"]["n_obs"],
   "competities":{k:{"vorig":v["prev"]["avg_xg_per_match"],"huidig":v["cur"]["avg_xg_per_match"],
                     "speeldagen":v["matchdays"]} for k,v in L.items() if not k.startswith("_")}},
 "credits":{"plafond":343,"split_budget":[3,3],"bron":"suggest_cap(19935, 29)",
   "markten_gekocht":{"spreads":3,"totals":3,"btts":10,"totaal":16},
   "guard_report":"16 van 343 credits gebruikt in 16 aanroep(en), nog 19919 over",
   "marktbalans_controle":"geslaagd — 3 van de 3 inkoopbare competities hebben een doelpuntenmarkt (totals) en 3 van de 3 een uitkomstmarkt (spreads); 1X2 gratis via BetExplorer in alle 4 de competities met wedstrijden"}}
json.dump(state, open("data/run-state/2026-09-02-run-b.json","w"), ensure_ascii=False, indent=1)
print("geschreven; competities:", len(state["competitions"]), " geanalyseerd:", sum(1 for c in state["competitions"].values() if c["status"]=="GEANALYSEERD"))
print("duels:", sum(len(c["matches"]) for c in state["competitions"].values()))
print("bets:", sum(1 for c in state["competitions"].values() for m in c["matches"] if m["bet"]))
print("near_miss:", sum(1 for c in state["competitions"].values() for m in c["matches"] if m.get("near_miss")))

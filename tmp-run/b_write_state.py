import json, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'.')
A=json.load(open("tmp-run/b_analysis.json")); M=json.load(open("tmp-run/b_matches.json"))
CTX=json.load(open("tmp-run/b_ctx.json")); L=json.load(open("tmp-run/b_leagues.json"))
NL=timezone(timedelta(hours=2))
RUNLIST=["Czech First League (CZE)","Greek Super League (GRE)","Eliteserien (NOR)","Allsvenskan (SWE)",
 "Croatian HNL (CRO)","Hungarian NB I (HUN)","Romanian SuperLiga (ROU)","Segunda División (ESP)",
 "Serie B (ITA)","2. Bundesliga (GER)","Swiss Super League (SUI)","Austrian Bundesliga (AUT)",
 "Keuken Kampioen Divisie (NED)","English League One (ENG)","English League Two (ENG)",
 "Kategoria Superiore (ALB)","Kosovo Superleague (KOS)"]
NOMATCH={
 "Czech First League (CZE)":"niets op de kalender — geen enkele CZE-competitie in de Fotmob-daglijst",
 "Greek Super League (GRE)":"alleen Cup Group Stage (Fotmob-id 145) in de daglijst; dat is geen competitieduel",
 "Eliteserien (NOR)":"niets op de kalender — geen enkele NOR-competitie in de daglijst",
 "Croatian HNL (CRO)":"niets op de kalender",
 "Romanian SuperLiga (ROU)":"alleen Cup Grp. A en Cup Grp. D in de daglijst",
 "Segunda División (ESP)":"niets op de kalender; van Spanje staat alleen LaLiga op de daglijst (Run A)",
 "Serie B (ITA)":"niets op de kalender; van Italië alleen Coppa Italia (Run A)",
 "2. Bundesliga (GER)":"niets op de kalender — geen enkele GER-competitie in de daglijst",
 "Austrian Bundesliga (AUT)":"niets op de kalender — geen enkele AUT-competitie in de daglijst",
 "Keuken Kampioen Divisie (NED)":"niets op de kalender — geen enkele NED-competitie in de daglijst",
 "English League One (ENG)":"niets op de kalender — geen enkele ENG-competitie in de daglijst",
 "English League Two (ENG)":"niets op de kalender — geen enkele ENG-competitie in de daglijst",
 "Kategoria Superiore (ALB)":"niets op de kalender",
 "Kosovo Superleague (KOS)":"geen enkele competitie met ccode KOS in de daglijst — ongewijzigd sinds 13 aug",
}
def nl(u): return datetime.fromisoformat(u.replace("Z","+00:00")).astimezone(NL).strftime("%H:%M")
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
             "datarijkdom":{"score":ctx["richness"]["score"],"deelscores":ctx["richness"]["parts"],
                            "samenvatting":ctx["richness"]["summary"],"notities":ctx["richness"]["notes"]},
             "context":ctx.get("ctx"),"turnover":ctx.get("turnover"),
             "inputs":r["inputs"],"lambdas":r["lambdas"],"team_stats":r["team_stats"],
             "gate7":{s:v["passed"] for s,v in r["gate7"].items()},
             "gate7_reden":{s:v.get("reason","") for s,v in r["gate7"].items()}}
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
            row["reden"]=(f"geen selectie haalde alle zeven de poorten; sterkste kandidaat {nm['market']} "
                          f"@ {nm['odds']} viel af op {nm['failed_gate']} ({nm['edge_pp']:+.2f} pp gemiddeld)")
        else:
            row["reden"]="geen enkele kandidaat met een positieve edge"
        rows.append(row)
    comps[comp]={"status":"GEANALYSEERD",
                 "toelichting":f"{len(rows)} duel(s), alle {len(rows)} doorgerekend","matches":rows}
state={"run":"B","date":"2026-09-03","resumed_count":0,
 "competitions":{c:comps[c] for c in RUNLIST if c in comps},
 "completed":False,
 "parameters":{"MAX_DEEP_ANALYSES":30,"MAX_SHORTLIST":3,"EDGE_THRESHOLD_FULL":8.0,
   "EDGE_THRESHOLD_LIGHT":16.0,"MAX_LIGHT_IN_SHORTLIST":2,"MIN_ODDS":1.30,"MAX_ODDS":6.00,
   "SETTLE_AFTER_HOURS":12,"afgekapt":0,
   "toelichting":("4 wedstrijden op de runlijst vandaag, in 3 van de 17 competities — donderdag van de "
     "interlandbreak, de overige 14 hadden niets op de kalender. Allsvenskan 1, Hungarian NB I 1, "
     "Swiss Super League 2. Alle vier haalden de datadekkingspoort en zijn doorgerekend. De cap van 30 "
     "is niet aangeraakt, dus er is niets afgekapt; laagste datarijkdom die het haalde 5.5 (Mjällby – "
     "Djurgården), hoogste die afviel: geen.")},
 "vroeg_seizoen":{"factor":L["_uplift"]["factor"],"gepoold":L["_uplift"]["pooled"],
   "speeldagen":L["_uplift"]["total_md"],"waarnemingen":L["_uplift"]["n_obs"],
   "competities":L["_uplift"]["competities"],
   "voorbehoud":("Slechts één bruikbare waarneming: Allsvenskan draait op het lopende seizoen als basis "
     "(geen correctie nodig) en de Hungarian NB I heeft geen xG bij Fotmob. Met 5,2 speeldagen tegen een "
     "prior van 8,0 wordt de ruwe verhouding 1.0662 teruggetrokken naar 1.0261. Run A mat vanochtend "
     "1.0823 op 28 speeldagen in 7 competities. Zie het runrapport onder Bevinding."),
   "gevoeligheid_bet":{"factor_eigen_run":{"f":1.026083,"edge_pp":12.43,"rob_min":3.75},
     "factor_ruw_gepoold":{"f":1.066210,"edge_pp":10.12,"rob_min":1.03},
     "factor_run_a":{"f":1.082280,"edge_pp":9.19,"rob_min":-0.05},
     "ongecorrigeerd":{"f":1.0,"edge_pp":13.92,"rob_min":5.52}}},
 "credits":{"plafond":354,"gebruikt":7,"split_budget":[2,2],
   "bron":"suggest_cap(19896, 28) — 19.896 credits over volgens api_check.py van deze run (20K-plan, 104 gebruikt deze maand), 28 dagen tot de maandwissel, 2 runs per dag",
   "markten_gekocht":{"spreads":["Allsvenskan (SWE)","Swiss Super League (SUI)"],
     "totals":["Allsvenskan (SWE)","Swiss Super League (SUI)"],
     "btts":["Mjällby – Djurgården","Basel – Sion","Lugano – Servette"],"totaal":7},
   "guard_report":"4 van 354 credits gebruikt in 4 aanroep(en) voor spreads+totals, plus 3 aanroepen à 1 credit voor BTTS; nog 19889 over",
   "marktbalans_controle":("geslaagd, en ruim: 2 van de 2 inkoopbare competities kregen zowel een "
     "doelpuntenmarkt (totals) als een uitkomstmarkt (spreads); 1X2 kwam gratis via BetExplorer in alle "
     "3 de competities met wedstrijden. De Hungarian NB I heeft geen sportkey bij The Odds API en had "
     "daardoor alleen 1X2 — dat is een bronngat, geen plafondgat.")}}
json.dump(state, open("data/run-state/2026-09-03-run-b.json","w"), ensure_ascii=False, indent=1)
print("competities:", len(state["competitions"]),
      "geanalyseerd:", sum(1 for c in state["competitions"].values() if c["status"]=="GEANALYSEERD"))
print("duels:", sum(len(c["matches"]) for c in state["competitions"].values()))
print("bets:", sum(1 for c in state["competitions"].values() for m in c["matches"] if m["bet"]))
print("near_miss:", sum(1 for c in state["competitions"].values() for m in c["matches"] if m.get("near_miss")))

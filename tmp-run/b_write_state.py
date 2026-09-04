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
 "Czech First League (CZE)":"niets op de kalender; van Tsjechië staat alleen de FNL (tweede divisie, Fotmob-id 253) op de daglijst",
 "Greek Super League (GRE)":"niets op de kalender — geen enkele GRE-competitie in de Fotmob-daglijst",
 "Allsvenskan (SWE)":"niets op de kalender; van Zweden staan alleen Superettan en de twee Ettan-reeksen op de daglijst",
 "Serie B (ITA)":"niets op de kalender; van Italië staat alleen de Serie A op de daglijst (Run A)",
 "Swiss Super League (SUI)":"niets op de kalender; van Zwitserland staat alleen de Challenge League (tweede divisie) op de daglijst",
 "Austrian Bundesliga (AUT)":"niets op de kalender; van Oostenrijk staat alleen de Cup op de daglijst",
 "English League One (ENG)":"niets op de kalender; van Engeland staan alleen Premier League, National League en de twee WSL-reeksen op de daglijst",
 "English League Two (ENG)":"niets op de kalender; van Engeland staan alleen Premier League, National League en de twee WSL-reeksen op de daglijst",
 "Kosovo Superleague (KOS)":"geen enkele competitie met ccode KOS in de daglijst — ongewijzigd sinds 13 aug 2026",
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
             "context":ctx.get("ctx"),"turnover":ctx.get("turnover")}
        if r["tier"]=="NONE":
            row["reden"]=r["reason"]
            row["markets_checked"]={}
            rows.append(row); continue
        row.update({"inputs":r["inputs"],"lambdas":r["lambdas"],"team_stats":r["team_stats"],
             "gate7":{s:v["passed"] for s,v in r["gate7"].items()},
             "gate7_reden":{s:v.get("reason","") for s,v in r["gate7"].items()}})
        if r.get("calibration"): row["calibration"]=r["calibration"]
        if r.get("seizoensweging"): row["seizoensweging"]=r["seizoensweging"]
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
    n_none=sum(1 for x in rows if x["tier"]=="NONE")
    toel=f"{len(rows)} duel(s), {len(rows)-n_none} doorgerekend"
    if n_none: toel += f", {n_none} op data_tier NONE (ploeg niet in de stand van vorig seizoen en geen gemeten omrekening beschikbaar)"
    comps[comp]={"status":"GEANALYSEERD","toelichting":toel,"matches":rows}
state={"run":"B","date":"2026-09-04","resumed_count":0,
 "competitions":{c:comps[c] for c in RUNLIST if c in comps},
 "completed":False,
 "parameters":{"MAX_DEEP_ANALYSES":35,"MAX_SHORTLIST":5,"EDGE_THRESHOLD_FULL":8.0,
   "EDGE_THRESHOLD_LIGHT":16.0,"MAX_LIGHT_IN_SHORTLIST":2,"MIN_ODDS":1.30,"MAX_ODDS":6.00,
   "SETTLE_FALLBACK_HOURS":2.0,"afgekapt":0,
   "toelichting":("Vrijdag, dus de weekendwaarden: cap 35 diepe analyses en shortlist 5. "
     "16 wedstrijden op de runlijst, in 8 van de 17 competities; de andere 9 hadden niets op de "
     "kalender. De cap van 35 is niet aangeraakt, dus er is niets afgekapt — laagste datarijkdom "
     "die het haalde 4.2 (Egnatia – Skënderbeu), hoogste die afviel: geen. Van de 16 duels zijn er "
     "10 doorgerekend; 6 vielen op data_tier NONE omdat één van beide ploegen niet in de stand van "
     "vorig seizoen staat en er voor die competitie geen gemeten divisieparen zijn (§4).")},
 "vroeg_seizoen":{"factor":L["_uplift"]["factor"],"gepoold":L["_uplift"]["pooled"],
   "speeldagen":L["_uplift"]["total_md"],"waarnemingen":L["_uplift"]["n_obs"],
   "competities":L["_uplift"]["competities"],
   "voorbehoud":("Twee bruikbare waarnemingen (2. Bundesliga en Segunda División, allebei 3 speeldagen) "
     "die tegengesteld wijzen: 1.528 -> 1.756 tegen 1.360 -> 1.229. Met 6,0 speeldagen tegen een prior "
     "van 8,0 wordt de ruwe verhouding 1.0263 teruggetrokken naar 1.0113. Eliteserien levert geen "
     "waarneming: dat is een kalenderjaarcompetitie waar het lopende seizoen 2026 (18 speeldagen, eigen "
     "xG) rechtstreeks het niveau geeft, dus daar is niets te corrigeren. De vijf competities zonder xG "
     "kunnen per definitie geen waarneming leveren. Run A mat vanochtend 1.0644 op 39 speeldagen in "
     "11 competities; zie het runrapport onder Bevinding.")},
 "credits":{"plafond":381,"gebruikt":11,"split_budget":[3,3],
   "bron":"suggest_cap(19855, 26) — 19.855 credits over volgens api_check.py van deze run (145 gebruikt deze maand), 26 dagen tot de maandwissel, 2 runs per dag",
   "markten_gekocht":{"spreads":["2. Bundesliga (GER)","Segunda División (ESP)","Eliteserien (NOR)"],
     "totals":["2. Bundesliga (GER)","Segunda División (ESP)","Eliteserien (NOR)"],
     "btts":["Arminia Bielefeld – St. Pauli","Hannover 96 – Karlsruher SC","Fredrikstad – Bodø/Glimt",
             "Sandefjord – Viking","Las Palmas – Leganés"],"totaal":11},
   "guard_report":"6 van 381 credits voor spreads+totals in 6 aanroepen, plus 5 aanroepen à 1 credit voor BTTS; nog 19.844 over",
   "marktbalans_controle":("geslaagd, en zo ruim als het plafond toelaat: alle 3 de inkoopbare competities "
     "kregen zowel een doelpuntenmarkt (totals) als een uitkomstmarkt (spreads), en BTTS is er voor "
     "5 wedstrijden bij gekocht. 1X2 kwam gratis via BetExplorer in 7 van de 8 competities met "
     "wedstrijden. De vijf competities zonder sportkey bij The Odds API (KKD, Croatian HNL, Kategoria "
     "Superiore, Hungarian NB I, Romanian SuperLiga) hadden daardoor alleen 1X2 — dat is een bronngat, "
     "geen plafondgat: het plafond van 381 is voor 11 credits aangesproken.")}}
json.dump(state, open("data/run-state/2026-09-04-run-b.json","w"), ensure_ascii=False, indent=1)
print("competities:", len(state["competitions"]),
      "geanalyseerd:", sum(1 for c in state["competitions"].values() if c["status"]=="GEANALYSEERD"))
print("duels:", sum(len(c["matches"]) for c in state["competitions"].values()))
print("bets:", sum(1 for c in state["competitions"].values() for m in c["matches"] if m["bet"]))
print("near_miss:", sum(1 for c in state["competitions"].values() for m in c["matches"] if m.get("near_miss")))
print("NONE:", sum(1 for c in state["competitions"].values() for m in c["matches"] if m["tier"]=="NONE"))

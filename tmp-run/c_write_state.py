import json, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'.')
A=json.load(open("tmp-run/c_analysis.json")); M=json.load(open("tmp-run/c_matches.json"))
CTX=json.load(open("tmp-run/c_ctx.json")); L=json.load(open("tmp-run/c_leagues.json"))
S=json.load(open("tmp-run/c_stage3.json")); R=json.load(open("tmp-run/c_rank.json"))
OA=json.load(open("tmp-run/c_oddsapi.json"))
NL=timezone(timedelta(hours=2)); SEL=set(R["selected"])
RUNLIST=["Czech First League (CZE)","Greek Super League (GRE)","Eliteserien (NOR)","Allsvenskan (SWE)",
 "Croatian HNL (CRO)","Hungarian NB I (HUN)","Romanian SuperLiga (ROU)","Segunda División (ESP)",
 "Serie B (ITA)","2. Bundesliga (GER)","Swiss Super League (SUI)","Austrian Bundesliga (AUT)",
 "Keuken Kampioen Divisie (NED)","English League One (ENG)","English League Two (ENG)",
 "Kategoria Superiore (ALB)","Kosovo Superleague (KOS)"]
NOMATCH={
 "Austrian Bundesliga (AUT)":"niets op de kalender; van Oostenrijk staat alleen de Cup (Fotmob-id 278, 8 duels) op de daglijst en die staat niet op de runlijst",
 "Kosovo Superleague (KOS)":"geen enkele competitie met ccode KOS in de Fotmob-daglijst — ongewijzigd sinds 13 aug 2026",
}
GEEN_XG="geen Fotmob-xG voor deze competitie (has_xg=false voor 2025/2026 én 2026/2027); stand met thuis/uit-splits is er wel, dus LIGHT — maar LIGHT staat in de Stage 4-sortering onder FULL en er waren al 45 FULL-kandidaten voor 35 plekken"
def nl(u): return datetime.fromisoformat(u.replace("Z","+00:00")).astimezone(NL).strftime("%H:%M")
comps={}
for c in RUNLIST:
    if c in NOMATCH: comps[c]={"status":"GEEN WEDSTRIJD","toelichting":NOMATCH[c],"matches":[]}
for comp,blk in M.items():
    rows=[]; n_an=n_cut=n_none=0
    for m in blk["matches"]:
        key=f"{m['home']} – {m['away']}"
        base={"match":key,"match_id":m["id"],"kickoff_nl":nl(m["utc"]),"kickoff_utc":m["utc"]}
        if key not in SEL:
            n_cut+=1
            ctx=CTX.get(key)
            base.update({"afgekapt":True,"tier":"FULL" if comp in L else "LIGHT","bet":False,
                "reden":"buiten MAX_DEEP_ANALYSES (35) gevallen in Stage 4",
                "markets_checked":{}})
            if ctx: base["datarijkdom"]={"score":ctx["richness"]["score"],"deelscores":ctx["richness"]["parts"],
                                         "samenvatting":ctx["richness"]["summary"]}
            else: base["datarijkdom"]={"score":None,"reden":"context niet opgehaald: deze competitie viel al op datakwaliteit af (LIGHT onder FULL), dus vóór de afkapping was er niets te rangschikken"}
            rows.append(base); continue
        r=A[key]; ctx=CTX[key]
        base.update({"tier":r["tier"],"bet":bool(r.get("bet")),"markets_checked":r["markets_checked"],
            "datarijkdom":{"score":ctx["richness"]["score"],"deelscores":ctx["richness"]["parts"],
                           "samenvatting":ctx["richness"]["summary"],"notities":ctx["richness"]["notes"]},
            "context":ctx.get("ctx"),"turnover":ctx.get("turnover")})
        if r["tier"]=="NONE":
            n_none+=1; base["reden"]=r["reason"]; base["markets_checked"]={}
            rows.append(base); continue
        n_an+=1
        base.update({"inputs":r["inputs"],"lambdas":r["lambdas"],"team_stats":r["team_stats"],
            "gate7":{s:v["passed"] for s,v in r["gate7"].items()},
            "gate7_reden":{s:v.get("reason","") for s,v in r["gate7"].items()}})
        if r.get("calibration"): base["calibration"]=r["calibration"]
        if r.get("seizoensweging"): base["seizoensweging"]=r["seizoensweging"]
        if r.get("winner"):
            w=r["winner"]; s=r.get("runner_up")
            base["pick"]={"market":w["market"],"selection":w["selection"],"odds":w["odds"],
                "odds_source":w["odds_source"],"my_prob":w["my_prob"],"implied":w["implied"],
                "edge_pp":w["edge_pp"],"edge_xg":w["edge_xg"],"edge_split":w["edge_split"],
                "edge_robust_min":w["edge_robust_min"],"score":w["score"],"side":w["side"]}
            base["second"]={"market":s["market"],"selection":s["selection"],"score":s["score"],
                            "gekwalificeerd":True} if s else None
        elif r.get("near_miss"):
            nm=r["near_miss"]; base["near_miss"]=nm
            base["reden"]=(f"geen selectie haalde alle acht de poorten; sterkste kandidaat {nm['market']} "
                           f"@ {nm['odds']} viel af op {nm['failed_gate']} ({nm['edge_pp']:+.2f} pp gemiddeld)")
        else:
            base["reden"]="geen enkele kandidaat met een positieve edge binnen de oddsband"
        rows.append(base)
    if n_an==0 and n_none==0:
        status="AFGEKAPT"
        toel=f"{len(rows)} duel(s), alle {n_cut} buiten de cap van 35 gevallen in Stage 4"
    elif n_an==0:
        # Wél binnen de cap gekomen en wél datadekking op competitieniveau, maar elk geselecteerd
        # duel viel op ploegniveau om (§4: geen gemeten omrekening voor die promovendus/degradant).
        status="GEANALYSEERD"
        toel=(f"{len(rows)} duel(s), {n_none} binnen de cap beoordeeld maar alle {n_none} op data_tier "
              f"NONE, {n_cut} afgekapt — nul doorgerekend")
    else:
        status="GEANALYSEERD"
        toel=f"{len(rows)} duel(s), {n_an} doorgerekend"
        if n_none: toel+=f", {n_none} op data_tier NONE"
        if n_cut: toel+=f", {n_cut} afgekapt"
    if comp not in L: toel += f" — {GEEN_XG}"
    comps[comp]={"status":status,"toelichting":toel,"matches":rows}
tot=sum(len(c["matches"]) for c in comps.values())
state={"run":"B","date":"2026-09-05","resumed_count":0,
 "competitions":{c:comps[c] for c in RUNLIST if c in comps},"completed":False,
 "parameters":{"MAX_DEEP_ANALYSES":35,"MAX_SHORTLIST":5,"EDGE_THRESHOLD_FULL":8.0,
   "EDGE_THRESHOLD_LIGHT":16.0,"MAX_LIGHT_IN_SHORTLIST":2,"MIN_ODDS":1.30,"MAX_ODDS":6.00,
   "SETTLE_FALLBACK_HOURS":2.0,"afgekapt":24,
   "afkapping":{"kandidaten":59,"cap":35,"afgekapt":24,
     "laagste_die_het_haalde":{"match":R["low_in"]["key"],"datarijkdom":R["low_in"]["rich"]},
     "hoogste_die_afviel":{"match":R["high_out"]["key"],"datarijkdom":R["high_out"]["rich"]},
     "toelichting":("De knip viel middenin een gelijkspel op datarijkdom: 5.0 haalde het nog "
       "(Sporting Gijón – Girona) en 5.0 viel af (Young Boys – Luzern). Binnen die gelijke score "
       "besliste eerst het aantal beschikbare markten (voor alle negen FULL-competities gelijk op 5) "
       "en daarna de aftrap, precies zoals sort_key voorschrijft. De 14 duels in de zes competities "
       "zonder Fotmob-xG vielen al op de eerste sorteersleutel af: LIGHT staat onder FULL, en er "
       "waren 45 FULL-kandidaten voor 35 plekken.")},
   "toelichting":("Zaterdag, dus de weekendwaarden: cap 35 diepe analyses en shortlist 5. "
     f"{tot} wedstrijden op de runlijst, in 15 van de 17 competities; Austrian Bundesliga en Kosovo "
     "Superleague hadden niets op de kalender. 35 duels zijn doorgerekend en 24 afgekapt; van de 35 "
     "kwamen er 8 op data_tier NONE uit, dus 27 zijn er werkelijk gemodelleerd.")},
 "vroeg_seizoen":{"factor":L["_uplift"]["factor"],"gepoold":L["_uplift"]["pooled"],
   "speeldagen":L["_uplift"]["total_md"],"waarnemingen":L["_uplift"]["n_obs"],
   "competities":L["_uplift"]["competities"],
   "voorbehoud":("Zeven bruikbare waarnemingen over 23,6 speeldagen — het breedste fundament dat "
     "een Run B tot nu toe had. Ze wijzen niet allemaal dezelfde kant op: 2. Bundesliga (1.528 -> "
     "1.733), English League One (1.302 -> 1.481) en League Two (1.302 -> 1.413) staan duidelijk "
     "boven vorig seizoen, Segunda División (1.360 -> 1.218) en Serie B (1.297 -> 1.288) eronder. "
     "De gepoolde ruwe verhouding is 1.0566; met 23,6 speeldagen tegen een prior van 8,0 wordt dat "
     "teruggetrokken naar 1.0423. Eliteserien en Allsvenskan leveren geen waarneming: dat zijn "
     "kalenderjaarcompetities waar het lopende seizoen 2026 (18+ speeldagen, eigen xG) rechtstreeks "
     "het niveau geeft, dus daar valt niets te corrigeren.")},
 "credits":{"plafond":OA["cap"],"gebruikt":27,"split_budget":[OA["n_spreads"],OA["n_totals"]],
   "bron":"suggest_cap(19783, 26) — 19.783 credits over volgens api_check.py van deze run (217 gebruikt deze maand), 26 dagen tot de maandwissel, 2 runs per dag",
   "markten_gekocht":{"spreads":sorted(OA["spreads"]),"totals":sorted(OA["totals"]),
     "btts":["Holstein Kiel – 1. FC Nürnberg","Degerfors – Halmstads BK","GAIS – Häcken",
             "Rosenborg – HamKam","Peterborough – Sheff Wed","Wigan – Stockport County",
             "Bradford – Mansfield","Tranmere – Oldham","AEK Athens – Aris Thessaloniki"],
     "btts_mislukt":["Brann – Lillestrøm — geen event-id in de spreads-respons"],"totaal":27},
   "guard_report":"18 van 380 credits voor spreads+totals in 18 aanroepen (9 competities x 2), plus 9 BTTS-aanroepen à 1 credit; nog 19.756 over",
   "marktbalans_controle":("geslaagd, en zo ruim als deze runlijst toelaat: alle negen competities met "
     "een sportkey kregen zowel een uitkomstmarkt (spreads: AH + DNB + DC) als een doelpuntenmarkt "
     "(totals) — 9 op 9, niet 1 op 12 zoals op 30 aug. Daar kwam gratis 1X2 van BetExplorer bij voor "
     "alle negen, en BTTS voor de negen wedstrijden die in de goedkope markten al een kandidaat-edge "
     "lieten zien. Alle zes de markten hebben dus meegedongen. Dat er alsnog vier van de vijf bets "
     "uit Over/Under komen, is deze keer dus geen inkoopartefact maar de analyse.")}}
json.dump(state, open("data/run-state/2026-09-05-run-b.json","w"), ensure_ascii=False, indent=1)
print("competities:", len(state["competitions"]))
for c,b in state["competitions"].items(): print(f'  {b["status"]:15s} {c}')
print("duels:", tot, "bets:", sum(1 for c in comps.values() for m in c["matches"] if m.get("bet")),
      "near_miss:", sum(1 for c in comps.values() for m in c["matches"] if m.get("near_miss")),
      "NONE:", sum(1 for c in comps.values() for m in c["matches"] if m.get("tier")=="NONE" and not m.get("afgekapt")))

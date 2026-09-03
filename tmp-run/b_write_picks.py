import json, sys, re, unicodedata
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'.')
A=json.load(open("tmp-run/b_analysis.json"))
NL=timezone(timedelta(hours=2))
CAPTURED = datetime.now(timezone.utc).astimezone(NL).replace(microsecond=0).isoformat()
def nl_iso(u): return datetime.fromisoformat(u.replace("Z","+00:00")).astimezone(NL).isoformat()
def slug(s):
    s=unicodedata.normalize("NFKD",s.lower()).encode("ascii","ignore").decode()
    return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-")

PROB={"Basel – Sion":[
 "Fotmob team-xG Swiss Super League 2025/2026 (Basel 69.0 xG / 56.1 xGA in 38 duels, Sion 59.9 / 48.1 in 38; competitiegemiddelde 1.604 xG per ploeg per duel)",
 "Fotmob thuis/uit-splits 2025/2026 (Basel thuis 25-15 in 16, Sion uit 26-23 in 16)",
 "Fotmob wedstrijdcontext: blessures/schorsingen, vorm, rustdagen en stadioncontrole (Basel 5 afwezigen / 20% van de selectiewaarde, Sion 1 / 11%)",
 "vroeg-seizoenscorrectie x1.0261 uit xG-waarnemingen van 1 competitie over 5,2 speeldagen"]}
CONF={"Basel – Sion":"Low"}
NOTES={"Basel – Sion":(
 "De edge komt vooral uit de splitsmethode (+20.30 pp) en veel minder uit het xG-model (+4.56 pp); "
 "§1d noemt de splitsmethode de scheefste van de twee. De zwakste stand van het (shrink, rho)-grid "
 "is +3.75 pp. Let op de kampioenssplitsing in Zwitserland: de xG-respons telt 38 duels per ploeg, "
 "de tabel 33, dus die twee dekken niet dezelfde wedstrijden. Extra voorbehoud: de "
 "vroeg-seizoenscorrectie van deze run rust op één competitie (5,2 speeldagen) en komt daardoor op "
 "x1.0261 uit; met de factor die Run A vanochtend op 28 speeldagen mat (x1.0823) zakt de edge naar "
 "+9.19 pp en de zwakste stand van het grid naar -0.05 pp — dan zou deze selectie op poort 6 "
 "afvallen en Under 3.25 @ 1.90 (score 8.67) overblijven. De Zwitserse competitie draait dit seizoen "
 "op 3.87 doelpunten per duel tegen 3.34 waar het model op rekent; dat is het hoofdrisico op een Under.")}

picks=[]
for k,r in A.items():
    if not r.get("bet"): continue
    w=r["winner"]; comp=r["comp"]; home,away=k.split(" – ")
    picks.append({
      "id": f"2026-09-03-{slug(comp)}-{slug(home)}-{slug(away)}-{slug(w['market'])}",
      "run":"B","run_date":"2026-09-03","kickoff":nl_iso(r["kickoff_utc"]),
      "competition":comp,"home":home,"away":away,
      "market":w["market"],"selection":w["selection"],"odds":w["odds"],
      "odds_source":w["odds_source"],"odds_captured_at":CAPTURED,
      "implied_prob":round(w["implied"],4),"my_prob":round(w["my_prob"],4),
      "edge_pp":round(w["edge_pp"],2),"data_tier":r["tier"],"confidence":CONF[k],
      "prob_sources":PROB[k],"shortlisted":True,"result":"pending",
      "settled_at":None,"settled_score":None,"settled_units":None,"notes":NOTES[k]})
with open("data/picks.jsonl","a") as f:
    for p in picks: f.write(json.dumps(p, ensure_ascii=False)+"\n")
for p in picks: print(p["id"],"|",p["market"],"|",p["selection"],"@",p["odds"])

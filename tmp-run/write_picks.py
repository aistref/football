import json, sys
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'.')
A=json.load(open("tmp-run/analysis.json"))
NL=timezone(timedelta(hours=2))
CAPTURED = datetime.now(timezone.utc).astimezone(NL).replace(microsecond=0).isoformat()
def nl_iso(u): return datetime.fromisoformat(u.replace("Z","+00:00")).astimezone(NL).isoformat()
def slug(s):
    import re, unicodedata
    s=unicodedata.normalize("NFKD",s.lower()).encode("ascii","ignore").decode()
    return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-")

PROB={
 "Thun – Lausanne":["Fotmob team-xG Swiss Super League 2025/2026 (Thun 69.7 xG / 62.4 xGA in 38, Lausanne 60.5 / 57.3 in 38; competitiegemiddelde 1.604 xG per ploeg per duel)",
   "Fotmob thuis/uit-splits 2025/2026 (Thun thuis 42-20 in 17, Lausanne uit 19-30 in 17)",
   "Fotmob wedstrijdcontext: blessures/schorsingen, vorm, rustdagen en stadioncontrole",
   "vroeg-seizoenscorrectie x1.0837 uit xG-waarnemingen van 3 competities over 15 speeldagen"],
 "Austria Wien – WSG Tirol":["Fotmob team-xG Austrian Bundesliga 2025/2026 (Austria Wien 41.1 / 43.0 in 32, WSG Tirol 37.2 / 43.6 in 32; competitiegemiddelde 1.385 xG per ploeg per duel)",
   "Fotmob thuis/uit-splits 2025/2026",
   "Fotmob wedstrijdcontext: blessures/schorsingen, vorm, rustdagen en stadioncontrole",
   "vroeg-seizoenscorrectie x1.0837"],
 "Reading – Mansfield":["Fotmob team-xG English League One 2025/2026 (Reading 52.9 / 57.3 in 46, Mansfield Town 59.9 / 57.2 in 46; competitiegemiddelde 1.302 xG per ploeg per duel)",
   "Fotmob thuis/uit-splits 2025/2026",
   "Fotmob wedstrijdcontext: blessures/schorsingen, vorm, rustdagen en stadioncontrole",
   "vroeg-seizoenscorrectie x1.0837"],
}
CONF={"Thun – Lausanne":"Low","Austria Wien – WSG Tirol":"Medium","Reading – Mansfield":"Medium"}
NOTES={
 "Thun – Lausanne":"Handicap -1: bij precies één goal verschil komt de inzet terug. De twee methodes staan hier het verst uit elkaar van de drie bets — xG-model +0.67 pp, doelpunten/splitsmethode +24.78 pp — en de zwakste stand van het (shrink, rho)-grid is +0.43 pp. Poort 5 en 6 zijn dus op het randje gehaald, niet ruim. Let ook op de kampioenssplitsing in Zwitserland: de xG-respons telt 38 duels per ploeg en de tabel 33, dus die twee dekken niet dezelfde wedstrijden (zie de docstring van fetch_league_stats). Thun maakte vorig seizoen 75 doelpunten uit 69.7 xG en overtrof zijn xG dus fors; dat verschil is precies wat de twee methodes uit elkaar drijft.",
 "Austria Wien – WSG Tirol":"Gepubliceerd als Double Chance; bij de bookmaker gekocht als Asian Handicap WSG Tirol +0.5 @ 1.97 (Pinnacle) — dezelfde uitbetaling, zie _shared-rules.md §1a. De ±0.5-lijn kwam gratis uit dezelfde spreads-respons als de handicaps.",
 "Reading – Mansfield":"Geen kant, dus poort 7 staat open; de contextpoort blokkeerde bij dit duel wel de uitploeg (Mansfield), wat de handicap Mansfield +0.25 (+7.53 pp) uitsloot.",
}
picks=[]
for k,r in A.items():
    if not r.get("bet"): continue
    w=r["winner"]; comp=r["comp"]
    home, away = k.split(" – ")
    picks.append({
      "id": f"2026-09-02-{slug(comp)}-{slug(home)}-{slug(away)}-{slug(w['market'])}",
      "run":"B","run_date":"2026-09-02","kickoff":nl_iso(r["kickoff_utc"]),
      "competition":comp,"home":home,"away":away,
      "market":w["market"],"selection":w["selection"],"odds":w["odds"],
      "odds_source":w["odds_source"],"odds_captured_at":CAPTURED,
      "implied_prob":round(w["implied"],4),"my_prob":round(w["my_prob"],4),
      "edge_pp":round(w["edge_pp"],2),"data_tier":r["tier"],"confidence":CONF[k],
      "prob_sources":PROB[k],"shortlisted":True,"result":"pending",
      "settled_at":None,"settled_score":None,"settled_units":None,
      "notes":NOTES[k]})
picks.sort(key=lambda p:-A[f"{p['home']} – {p['away']}"]["winner"]["score"])
with open("data/picks.jsonl","a") as f:
    for p in picks: f.write(json.dumps(p, ensure_ascii=False)+"\n")
for p in picks: print(p["id"], "|", p["market"], "|", p["selection"], "@", p["odds"])

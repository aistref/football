import json, sys, re, unicodedata
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'.')
A=json.load(open("tmp-run/b_analysis.json"))
NL=timezone(timedelta(hours=2))
CAPTURED = "2026-09-04T05:35:00+02:00"
def nl_iso(u): return datetime.fromisoformat(u.replace("Z","+00:00")).astimezone(NL).isoformat()
def slug(s):
    s=unicodedata.normalize("NFKD",s.lower()).encode("ascii","ignore").decode()
    return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-")

ELI = [
 "Fotmob team-xG Eliteserien (NOR) — competitieniveau uit het lopende seizoen 2026 zelf (18 speeldagen, 1.674 xG per ploeg per duel over 16 ploegen), dus zonder vroeg-seizoenscorrectie",
 "Fotmob thuis/uit-splits Eliteserien 2025 (tweede methode, multiplicatief op het competitiegemiddelde)",
 "Seizoensweging §4: teamsterkte 2025 geblend met 18 duels uit 2026, gewicht 53% voor het lopende seizoen (blend_seasons, k=16)",
]
PROB={
 "Fredrikstad – Bodø/Glimt": ELI + [
   "Fotmob team-xG: Fredrikstad 1.31 xG / 1.447 xGA per duel in 2025 en 1.233 / 2.000 in 2026 (gewogen 1.269 / 1.740); Bodø/Glimt 2.473 / 1.107 en 2.861 / 1.033 (gewogen 2.679 / 1.068)",
   "Fotmob wedstrijdcontext (predicted): thuis 2 afwezig · 11% van de selectiewaarde · vorm WWWWW · 5 dagen rust; uit 5 afwezig · 18% · vorm WWWWW · 5 dagen rust — poort 7 open aan beide kanten",
 ],
 "Sandefjord – Viking": ELI + [
   "Fotmob team-xG: Sandefjord 1.427 xG / 1.573 xGA per duel in 2025 en 1.261 / 1.850 in 2026 (gewogen 1.339 / 1.720); Viking 1.950 / 1.153 en 2.211 / 1.261 (gewogen 2.088 / 1.210)",
   "Fotmob wedstrijdcontext (predicted): thuis 4 afwezig · 28% van de selectiewaarde · vorm LLWWD · 5 dagen rust; uit 3 afwezig · 12% · vorm LDWWW · 2 dagen rust (druk programma) — poort 7 sluit beide kanten, maar staat open voor een doelpuntenmarkt zonder kant",
 ],
 "Las Palmas – Leganés": [
   "Fotmob team-xG Segunda División (ESP) 2025/2026 — competitiegemiddelde 1.360 xG per ploeg per duel over 22 ploegen",
   "Fotmob team-xG: Las Palmas 1.212 xG / 1.083 xGA per duel in 2025/2026 en 1.100 / 1.567 in 2026/2027 (gewogen 1.194 / 1.160); Leganés 1.333 / 1.388 en 0.833 / 1.733 (gewogen 1.254 / 1.443)",
   "Fotmob thuis/uit-splits Segunda División 2025/2026 (tweede methode, multiplicatief op het competitiegemiddelde)",
   "Seizoensweging §4: 3 duels uit het lopende seizoen meegewogen voor 16% (blend_seasons, k=16)",
   "Fotmob wedstrijdcontext (lastStarting11): thuis 4 afwezig · 29% van de selectiewaarde · vorm LDWWL; uit 2 afwezig · 7% · vorm LLDWW — poort 7 sluit de thuiskant, maar staat open voor een markt zonder kant",
   "Vroeg-seizoenscorrectie x1.0113 over 2 competities (6 speeldagen, ruwe verhouding 1.0263) — uitsluitend uit xG-waarnemingen, geen enkele marktprijs (§2)",
 ],
}
CONF={"Fredrikstad – Bodø/Glimt":"High","Sandefjord – Viking":"Medium","Las Palmas – Leganés":"Low"}
NOTES={
 "Fredrikstad – Bodø/Glimt":(
   "xG-methode +16.72 pp, splitsmethode +19.14 pp, gemiddelde +17.93 pp — de twee methodes liggen "
   "hier dicht bij elkaar, wat bij deze routine ongebruikelijk is. Zwakste stand van het "
   "(shrink, rho)-grid +9.90 pp, hoogste +20.01. selection_score 12.46 uit 13 doorgerekende "
   "selecties. Tweede werd Asian Handicap — Fredrikstad FK +1.5 @ 2.11 met score 11.30, die ook alle "
   "zeven poorten haalde. Bodø/Glimt is de sterkste ploeg van de competitie (2.68 xG voor, 1.07 tegen "
   "per duel na weging) en mist vijf spelers voor 18% van de selectiewaarde; Fredrikstad won zijn "
   "laatste vijf. De handicap van +1.75 wordt half verloren bij een nederlaag met precies twee "
   "doelpunten en volledig bij drie of meer."),
 "Sandefjord – Viking":(
   "xG-methode +11.74 pp, splitsmethode +6.38 pp, gemiddelde +9.06 pp. Zwakste stand van het "
   "(shrink, rho)-grid +11.01 pp — hoger dan de gemiddelde edge zelf, want het grid varieert alleen "
   "de xG-methode (§6e). selection_score 6.09 uit 21 doorgerekende selecties. Tweede werd "
   "Over/Under — Under 3.25 @ 1.87 met score 5.30, ook volledig gekwalificeerd. Poort 7 sluit hier "
   "beide kanten (Sandefjord mist vier spelers voor 28% van de selectiewaarde, Viking speelde twee "
   "dagen geleden), en dat is precies waarom er een doelpuntenmarkt overblijft en geen uitkomstmarkt: "
   "Sandefjord +0.75 @ 2.01 had met +15.63 pp de hoogste edge van de wedstrijd maar viel af op "
   "context. Het risico op deze Under is de Eliteserien zelf, die dit seizoen op 3.09 doelpunten per "
   "duel draait."),
 "Las Palmas – Leganés":(
   "xG-methode +3.24 pp, splitsmethode +18.23 pp, gemiddelde +10.73 pp — de edge komt vrijwel volledig "
   "uit de splitsmethode, en §1d noemt die de scheefste van de twee. Zwakste stand van het "
   "(shrink, rho)-grid +2.39 pp, hoogste +4.97: dun. selection_score 6.41 uit 17 doorgerekende "
   "selecties. Tweede werd Over/Under — Under 2.5 @ 1.81 met score 4.59, maar die haalde de "
   "drempel van 8.0 pp niet (+7.33) en was dus geen gekwalificeerde bet. Beide ploegen staan op drie "
   "gespeelde duels, dus het lopende seizoen weegt maar voor 16% mee en de kansschatting rust "
   "grotendeels op 2025/2026. Let op: die tabel kwam bij Fotmob binnen als 30 rijen voor een "
   "competitie van 22 ploegen — acht ploegen, waaronder Leganés, stonden in twee halve rijen "
   "(de ene met xG, de andere met de stand en de thuis/uit-splits). Zonder samenvoegen was deze "
   "wedstrijd op NONE uitgekomen; zie het runrapport onder Bevinding."),
}

picks=[]
for k,r in A.items():
    if not r.get("bet"): continue
    w=r["winner"]; comp=r["comp"]; home,away=k.split(" – ")
    picks.append({
      "id": f"2026-09-04-{slug(comp)}-{slug(home)}-{slug(away)}-{slug(w['market'])}-{slug(w['selection'])}"[:150],
      "run":"B","run_date":"2026-09-04","kickoff":nl_iso(r["kickoff_utc"]),
      "competition":comp,"home":home,"away":away,
      "market":w["market"],"selection":w["selection"],"odds":w["odds"],
      "odds_source":w["odds_source"],"odds_captured_at":CAPTURED,
      "implied_prob":round(w["implied"],4),"my_prob":round(w["my_prob"],4),
      "edge_pp":round(w["edge_pp"],2),"data_tier":r["tier"],"confidence":CONF[k],
      "prob_sources":PROB[k],"shortlisted":True,"result":"pending",
      "settled_at":None,"notes":NOTES[k]})
with open("data/picks.jsonl","a") as f:
    for p in picks: f.write(json.dumps(p, ensure_ascii=False)+"\n")
for p in picks: print(p["id"],"|",p["market"],"|",p["selection"],"@",p["odds"])

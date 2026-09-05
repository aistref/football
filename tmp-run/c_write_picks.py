# -*- coding: utf-8 -*-
import json, sys, re, unicodedata
from datetime import datetime, timezone, timedelta
sys.path.insert(0,'.')
A=json.load(open("tmp-run/c_analysis.json"))
NL=timezone(timedelta(hours=2))
CAPTURED="2026-09-05T05:15:00+02:00"
def nl_iso(u): return datetime.fromisoformat(u.replace("Z","+00:00")).astimezone(NL).isoformat()
def slug(s):
    s=unicodedata.normalize("NFKD",s.lower()).encode("ascii","ignore").decode()
    return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-")

UPLIFT=("Vroeg-seizoenscorrectie x1.0423 over 7 competities (23,6 speeldagen, ruwe verhouding 1.0566) "
        "— uitsluitend uit xG-waarnemingen, geen enkele marktprijs (§2)")
PROB={
 "Rosenborg – HamKam":[
  "Fotmob team-xG Eliteserien (NOR) — competitieniveau uit het lopende seizoen 2026 zelf (18,4 speeldagen, 1.676 xG per ploeg per duel over 16 ploegen), dus zonder vroeg-seizoenscorrectie",
  "Fotmob team-xG: Rosenborg 1.513 xG / 1.447 xGA per duel in 2025 en 1.644 / 1.672 in 2026 (gewogen 1.583 / 1.566); HamKam 1.280 / 1.740 en 1.439 / 1.683 (gewogen 1.364 / 1.710)",
  "Fotmob thuis/uit-splits Eliteserien 2025 (tweede methode, multiplicatief op het competitiegemiddelde)",
  "Seizoensweging §4: teamsterkte 2025 geblend met 18 duels uit 2026, gewicht 53% voor het lopende seizoen (blend_seasons, k=16)",
  "Fotmob wedstrijdcontext (predicted): thuis 4 afwezig · 11% van de selectiewaarde · vorm LWWWL · 6 dagen rust; uit 1 afwezig · 14% · vorm WDLWD · 6 dagen rust — poort 7 open aan beide kanten",
 ],
 "GAIS – Häcken":[
  "Fotmob team-xG Allsvenskan (SWE) — competitieniveau uit het lopende seizoen 2026 zelf (18,9 speeldagen, 1.502 xG per ploeg per duel over 16 ploegen), dus zonder vroeg-seizoenscorrectie",
  "Fotmob team-xG: GAIS 1.637 xG / 1.130 xGA per duel in 2025 en 1.684 / 1.321 in 2026 (gewogen 1.662 / 1.234); Häcken 1.753 / 1.497 en 1.874 / 1.232 (gewogen 1.819 / 1.353)",
  "Fotmob thuis/uit-splits Allsvenskan 2025 (tweede methode, multiplicatief op het competitiegemiddelde)",
  "Seizoensweging §4: teamsterkte 2025 geblend met 19 duels uit 2026, gewicht 54% voor het lopende seizoen (blend_seasons, k=16)",
  "Fotmob wedstrijdcontext (lastStarting11): thuis 6 afwezig · 37% van de selectiewaarde · vorm WLLWW · 5 dagen rust; uit 4 afwezig · 30% · vorm LWWWL · 7 dagen rust — poort 7 open aan beide kanten",
 ],
 "Holstein Kiel – 1. FC Nürnberg":[
  "Fotmob team-xG 2. Bundesliga (GER) 2025/2026 — competitiegemiddelde 1.528 xG per ploeg per duel over 18 ploegen",
  "Fotmob team-xG: Holstein Kiel 1.371 xG / 1.497 xGA per duel in 2025/2026 en 1.967 / 1.367 in 2026/2027 (gewogen 1.465 / 1.476); 1. FC Nürnberg 1.441 / 1.485 en 1.700 / 1.967 (gewogen 1.482 / 1.561)",
  "Fotmob thuis/uit-splits 2. Bundesliga 2025/2026 (tweede methode, multiplicatief op het competitiegemiddelde)",
  "Seizoensweging §4: 3 duels uit het lopende seizoen meegewogen voor 16% (blend_seasons, k=16)",
  "Fotmob wedstrijdcontext (lastStarting11): thuis 3 afwezig · 16% van de selectiewaarde · vorm LDDWL · 6 dagen rust; uit 2 afwezig · 23% · vorm DWWDW · 7 dagen rust — poort 7 open aan beide kanten",
  UPLIFT,
 ],
 "AEK Athens – Aris Thessaloniki":[
  "Fotmob team-xG Greek Super League (GRE) 2025/2026 — competitiegemiddelde 1.306 xG per ploeg per duel over 14 ploegen",
  "Fotmob team-xG: AEK Athens 1.863 xG / 0.916 xGA per duel in 2025/2026 en 1.250 / 0.800 in 2026/2027 (gewogen 1.794 / 0.903); Aris Thessaloniki 1.194 / 1.200 en 2.150 / 1.250 (gewogen 1.300 / 1.206)",
  "Fotmob thuis/uit-splits Greek Super League 2025/2026 (tweede methode, multiplicatief op het competitiegemiddelde)",
  "Seizoensweging §4: 2 duels uit het lopende seizoen meegewogen voor 11% (blend_seasons, k=16)",
  "Fotmob wedstrijdcontext (lastStarting11): thuis niemand afwezig gemeld · vorm DWWDW · 3 dagen rust (druk programma); uit niemand afwezig gemeld · vorm WLWWW · 6 dagen rust — poort 7 sluit de thuiskant op rust, maar staat open voor een markt zonder kant",
  UPLIFT,
 ],
 "Tranmere – Oldham":[
  "Fotmob team-xG English League Two (ENG) 2025/2026 — competitiegemiddelde 1.302 xG per ploeg per duel over 24 ploegen; sinds deze week ook has_xg=true voor het lopende 2026/2027 (1.413), wat in coverage.json nog als ontbrekend stond",
  "Fotmob team-xG: Tranmere Rovers 1.067 xG / 1.520 xGA per duel in 2025/2026 en 0.875 / 1.550 in 2026/2027 (gewogen 1.029 / 1.526); Oldham Athletic 1.480 / 1.272 en 1.475 / 0.950 (gewogen 1.479 / 1.207)",
  "Fotmob thuis/uit-splits English League Two 2025/2026 (tweede methode, multiplicatief op het competitiegemiddelde)",
  "Seizoensweging §4: 4 duels uit het lopende seizoen meegewogen voor 20% (blend_seasons, k=16)",
  "Fotmob wedstrijdcontext (lastStarting11): aan beide kanten niemand afwezig gemeld; thuis vorm DWDDD · 4 dagen rust, uit vorm LWLWD · 4 dagen rust — poort 7 open aan beide kanten",
  UPLIFT,
 ],
}
CONF={"Rosenborg – HamKam":"High","Holstein Kiel – 1. FC Nürnberg":"Medium",
      "Tranmere – Oldham":"Medium","GAIS – Häcken":"Low","AEK Athens – Aris Thessaloniki":"Low"}
NOTES={
 "Rosenborg – HamKam":(
  "xG-methode +12.34 pp, splitsmethode +22.29 pp, gemiddelde +17.32 pp — de enige bet van deze run "
  "waar béide methodes ruim boven de drempel van 8.0 uitkomen, en daarmee de enige die niet op de "
  "splitsmethode alleen leunt. Zwakste stand van het (shrink, rho)-grid +11.52 pp, hoogste +13.96: "
  "de edge overleeft het hele grid met marge. selection_score 12.95, de hoogste van de run, uit 17 "
  "doorgerekende selecties. Tweede werd Over/Under — Under 3.25 @ 1.88 met score 11.60, ook volledig "
  "gekwalificeerd. Rosenborg is thuis favoriet (1X2 1.32) maar incasseert dit seizoen meer dan vorig "
  "(1.672 tegen 1.447 xGA per duel) en HamKam scoort weinig (1.364 xG per duel na weging); het model "
  "komt op 2.77 verwachte doelpunten tegen een lijn van 3.5. Poort 8 hield hier twee handicaps op "
  "HamKam tegen (+1.5 @ 2.02 met +17.76 pp en +1.75 @ 1.72 met +14.38 pp) — precies de underdog-kant "
  "waar §1e over gaat. Risico: HamKam is bij Fotmob de opstelling nog 'predicted', niet bevestigd."),
 "GAIS – Häcken":(
  "xG-methode +0.56 pp, splitsmethode +21.74 pp, gemiddelde +11.15 pp — deze edge komt vrijwel "
  "volledig uit de splitsmethode, en §1d noemt die de scheefste van de twee. Zwakste stand van het "
  "(shrink, rho)-grid +0.46 pp, hoogste +0.85: dat is de nauwste marge van de vijf bets, en het grid "
  "varieert alleen de xG-methode (§6e), dus het zegt weinig over de methode die de edge draagt. "
  "selection_score 7.17 uit 19 doorgerekende selecties. Tweede werd Over/Under — Under 2.5 @ 2.44 met "
  "score 6.60, ook gekwalificeerd. Beide ploegen missen veel: GAIS 6 spelers voor 37% van de "
  "selectiewaarde, Häcken 4 voor 30% — poort 7 laat dat bij een doelpuntenmarkt zonder kant "
  "uitdrukkelijk open, want in welke richting uitvallers een totaal verschuiven is niet gemeten. "
  "Het lopende seizoen weegt hier voor 54% mee (19 duels). Lees deze bet als Low: hij staat of valt "
  "met de splitsmethode."),
 "Holstein Kiel – 1. FC Nürnberg":(
  "xG-methode +3.12 pp, splitsmethode +15.04 pp, gemiddelde +9.08 pp. Zwakste stand van het "
  "(shrink, rho)-grid +2.85 pp, hoogste +3.65 — positief over het hele grid, maar dun. "
  "selection_score 6.50 uit 17 doorgerekende selecties. Tweede werd Over/Under — Under 3 @ 1.95 met "
  "score 5.94, ook gekwalificeerd. Beide ploegen staan op drie gespeelde duels, dus het lopende "
  "seizoen weegt maar voor 16% mee en de kansschatting rust grotendeels op 2025/2026. De 2. Bundesliga "
  "draait dit seizoen op 1.733 xG per ploeg per duel tegen 1.528 vorig jaar; die stijging zit al in "
  "de vroeg-seizoenscorrectie van x1.0423 en werkt dus tegen deze Under in — de bet blijft er "
  "overheen. Koers 1.60 is de laagste van de vijf."),
 "AEK Athens – Aris Thessaloniki":(
  "xG-methode +1.72 pp, splitsmethode +18.15 pp, gemiddelde +9.93 pp — net als bij GAIS – Häcken komt "
  "de edge vrijwel volledig uit de splitsmethode. Zwakste stand van het (shrink, rho)-grid +1.72 pp, "
  "hoogste +1.74: het grid is hier vlak omdat het alleen de xG-methode varieert. selection_score 6.36 "
  "uit 13 doorgerekende selecties. Tweede werd Over/Under — Under 2.5 @ 2.08 met score 6.14, ook "
  "gekwalificeerd. AEK is zwaar favoriet (1X2 1.38) en gaf vorig seizoen weinig weg (0.903 xGA per duel "
  "na weging); Aris scoorde weinig (1.300 xG). Poort 7 sluit de thuiskant — AEK speelde drie dagen "
  "geleden — maar staat open voor deze doelpuntenmarkt zonder kant. Beide ploegen staan op twee "
  "gespeelde duels, dus het lopende seizoen weegt voor 11% mee. Low: dunne robuustheid én een "
  "kansschatting die op één van de twee methodes rust."),
 "Tranmere – Oldham":(
  "xG-methode +4.00 pp, splitsmethode +16.32 pp, gemiddelde +10.16 pp. Zwakste stand van het "
  "(shrink, rho)-grid +2.13 pp, hoogste +7.72. selection_score 6.11 uit 15 doorgerekende selecties. "
  "Tweede werd 1X2 — 2 (Oldham wint) @ 2.28 met score 5.43, ook gekwalificeerd; dat de handicap wint "
  "is precies wat §1a beoogt, want -0.25 geeft bij een gelijkspel de helft van de inzet terug waar de "
  "1X2 dan volledig verliest. De enige bet van de run met een kant, en hij staat op de "
  "favorietenkant: de markt zet Oldham op 2.28 tegen 2.99 voor Tranmere, dus poort 8 gaat open. "
  "Oldham is de betere ploeg op beide seizoenen (1.479 xG voor / 1.207 tegen tegen 1.029 / 1.526 voor "
  "Tranmere). Aan beide kanten meldt Fotmob niemand afwezig, maar allebei speelden vier dagen geleden. "
  "Let op de lijn: -0.25 verliest half bij een gelijkspel en volledig bij winst van Tranmere."),
}
picks=[]
for k,r in A.items():
    if not r.get("bet"): continue
    w=r["winner"]; comp=r["comp"]; home,away=k.split(" – ")
    picks.append({
      "id": f"2026-09-05-{slug(comp)}-{slug(home)}-{slug(away)}-{slug(w['market'])}-{slug(w['selection'])}"[:150],
      "run":"B","run_date":"2026-09-05","kickoff":nl_iso(r["kickoff_utc"]),
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

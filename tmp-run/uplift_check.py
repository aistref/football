import json, sys
sys.path.insert(0,'.')
from scripts import fotmob, calibration
from scripts.model import (TeamStats, LeagueContext, analyze_match, analyze_match_from_splits,
    splits_from_fotmob, totals_prob, scale_level)
from scripts.promotion import find_team
from scripts.oddsapi import best_by_line
import unicodedata
exec(open("tmp-run/analyze.py").read().split("results={}")[0].replace('print(f"uplift factor {UP:.4f}")',''))

devs_pre=[]; devs_post=[]
for comp,blk in M.items():
    st=LG[comp]["stats"]; base=LG[comp]["base"]; scaled=LG[comp]["league"]
    for m in blk["matches"]:
        ev=api_event(comp,m["home"],m["away"],"totals",m["utc"])
        if not ev: continue
        bl=best_by_line(ev,"totals")
        pair={}
        for (o,line),(odds,book) in bl.items():
            if abs((line or 0)-2.5)<1e-9: pair[o.lower()[:1]]=odds
        if "o" not in pair or "u" not in pair: continue
        mkt = (1/pair["o"])/((1/pair["o"])+(1/pair["u"]))
        try:
            hs,hsp,_,_ = team_inputs(comp,m["home"]); as_,asp,_,_ = team_inputs(comp,m["away"])
        except Exception: continue
        for lg, acc in ((base,devs_pre),(scaled,devs_post)):
            px=analyze_match(hs,as_,lg); ps=analyze_match_from_splits(hsp,asp,league=lg)
            my=(px.over_2_5+ps.over_2_5)/2
            acc.append((my-mkt)*100)
import statistics as S
print(f"P(Over 2.5) t.o.v. de de-vigde marktkans, {len(devs_pre)} wedstrijden")
print(f"  zonder vroeg-seizoenscorrectie : gemiddelde afwijking {S.mean(devs_pre):+.2f} pp, gem. absolute fout {S.mean(map(abs,devs_pre)):.2f} pp")
print(f"  met correctie x{UP:.4f}          : gemiddelde afwijking {S.mean(devs_post):+.2f} pp, gem. absolute fout {S.mean(map(abs,devs_post)):.2f} pp")

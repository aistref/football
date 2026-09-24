"""Kalibratieblok in het juiste formaat: lijsten van drie (thuis, gelijk, uit)."""
import json
from scripts import model
from scripts.model import TeamStats, LeagueContext, analyze_match, analyze_match_from_splits, \
    splits_from_fotmob, blend_seasons

s3 = json.load(open("tmp-run/rb24_stage3.json"))
an = json.load(open("tmp-run/rb24_analysis.json"))
prev, cur = s3["prev"], s3["cur"]
HOME, AWAY = "Seattle Sounders FC", "Real Salt Lake"

lg = LeagueContext(home_goals_per_match=cur["home_goals_per_match"],
                   away_goals_per_match=cur["away_goals_per_match"],
                   avg_xg_per_match=cur["avg_xg_per_match"])
ts = lambda d: TeamStats(xg=d["xg"], xga=d["xga"], matches_played=d["mp"])
blend = lambda n: blend_seasons(ts(prev["teams"][n]), ts(cur["teams"][n]), k=model.CREDIBILITY_K)
h, a = blend(HOME), blend(AWAY)

p10 = analyze_match(h, a, lg, shrink=1.00)
p08 = analyze_match(h, a, lg, shrink=0.80)
def splits(name):
    p, c = prev["teams"][name], cur["teams"][name]
    return splits_from_fotmob({"home": {k: p["home"][k] + c["home"][k] for k in ("played","gf","ga")},
                               "away": {k: p["away"][k] + c["away"][k] for k in ("played","gf","ga")}})
ps = analyze_match_from_splits(splits(HOME), splits(AWAY), league=lg)
trip = lambda p: [round(p.home, 4), round(p.draw, 4), round(p.away, 4)]

block = {"market": [round(x, 4) for x in an["devig"]],
         "p_xg": trip(p10), "p_xg_noshrink": trip(p10), "p_xg_shrink08": trip(p08),
         "p_split": trip(ps),
         "odds": [1.76, 3.90, 4.13], "boeken": 4, "bron": "BetExplorer, pre-match marktgemiddelde",
         "let_op": ("de-vigd BetExplorer-gemiddelde over 4 boeken als marktkans; de stand van 2026 "
                    "telt dit duel nog niet mee (25 resp. 26 van 27 speeldagen), dus de modelinput "
                    "is zuiver pre-match. Competitieniveau uit het lopende seizoen in plaats van "
                    "uit early_season_uplift — zie openstaand punt 3 van 20 sep.")}
print(json.dumps(block, ensure_ascii=False, indent=1))

path = "data/run-state/2026-09-24-run-b.json"
st = json.load(open(path))
m = st["competitions"]["MLS (USA)"]["matches"][0]
m["calibration"] = block
json.dump(st, open(path, "w"), ensure_ascii=False, indent=1)
print("bijgewerkt:", path)

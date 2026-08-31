import json
bx=json.load(open('tmp-run/rb_bx.json'))
raw=json.load(open('tmp-run/rb_odds.json'))
btts=json.load(open('tmp-run/rb_btts.json'))
out={"fixtures":{comp:[{"home":r["home"],"away":r["away"],"odds":r["odds"],
                        "is_today":r["is_today"],"when":r["when"],"books":r["bookmakers"]}
                       for r in rows] for comp,rows in bx.items()},
     "raw":{"spreads":raw["spreads"],"totals":raw["totals"],"btts":btts},
     "bought":{"spreads":list(raw["spreads"].keys()),"totals":list(raw["totals"].keys()),
               "btts":list(btts.keys())}}
json.dump(out, open('tmp-run/rb_odds_all.json','w'), ensure_ascii=False)
print("spreads:",out['bought']['spreads'])
print("totals :",out['bought']['totals'])
print("btts   :",len(out['bought']['btts']))

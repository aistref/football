import json, unicodedata
from scripts import fotmob
def norm(s):
    return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower().replace('.',' ').replace('-',' ').split()
def key(s): return ' '.join(norm(s))

COMPS={
 "Greek Super League (GRE)":   dict(pid=135, base="2025/2026", cur="2026/2027", sportkey="soccer_greece_super_league"),
 "Allsvenskan (SWE)":          dict(pid=67,  base="2026",      cur="2026",      sportkey="soccer_sweden_allsvenskan"),
 "Croatian HNL (CRO)":         dict(pid=252, base="2025/2026", cur="2026/2027", sportkey=None),
 "Romanian SuperLiga (ROU)":   dict(pid=189, base="2025/2026", cur="2026/2027", sportkey=None),
 "Segunda Division (ESP)":     dict(pid=140, base="2025/2026", cur="2026/2027", sportkey="soccer_spain_segunda_division"),
 "Keuken Kampioen Divisie (NED)":dict(pid=111,base="2025/2026",cur="2026/2027", sportkey=None),
 "Kategoria Superiore (ALB)":  dict(pid=260, base="2025/2026", cur="2026/2027", sportkey=None),
}
out={"stats":{},"understat":{}}
for comp,c in COMPS.items():
    prev=fotmob.fetch_league_stats(c['pid'], c['base'])
    cur =fotmob.fetch_league_stats(c['pid'], c['cur']) if c['cur']!=c['base'] else prev
    def summ(d):
        t=d['teams']
        return {"has_xg":d.get('has_xg'),"avg_xg":d.get('avg_xg_per_match'),
                "hg":d.get('home_goals_per_match'),"ag":d.get('away_goals_per_match'),
                "n_teams":len(t),"played":max([x.get('played',0) or 0 for x in t.values()],default=0),
                "mp":max([x.get('mp',0) or 0 for x in t.values()],default=0)}
    out['stats'][comp]={"prev":summ(prev),"cur":summ(cur),"base_season":c['base'],
                        "cur_season":c['cur'],"primaryId":c['pid'],"sportkey":c['sportkey'],
                        "tier":"FULL" if prev.get('has_xg') else "LIGHT"}
    print(f"{comp:32} tier={out['stats'][comp]['tier']:5} prev={summ(prev)}")
    print(f"{'':32} cur ={summ(cur)}")
json.dump(out, open('tmp-run/rb_stage3.json','w'), ensure_ascii=False, indent=1)

import sys, json
sys.path.insert(0,'.')
from scripts.fotmob import _get_json
d=_get_json("https://www.fotmob.com/api/allLeagues")
print("keys:", list(d.keys())[:10])
found=[]
def walk(o):
    if isinstance(o,dict):
        if "id" in o and "name" in o and isinstance(o.get("name"),str):
            found.append((o.get("ccode") or o.get("localizedCcode") or "?", o["id"], o["name"]))
        for v in o.values(): walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
walk(d)
for cc,i,n in found:
    if cc in ("SUI","CZE") or "challenge" in n.lower() or "zbrojovka" in n.lower():
        print(cc,i,n)

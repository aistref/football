import os, json, urllib.request, sys
sys.path.insert(0,'.')
from scripts.oddsapi import _api_key
key=_api_key()
u=f"https://api.the-odds-api.com/v4/sports/?apiKey={key}"
d=json.load(urllib.request.urlopen(u, timeout=30))
want=['sweden','switzer','hungar','allsven','swiss']
for s in d:
    if any(w in s['key'].lower() or w in s['title'].lower() for w in want):
        print(f"{s['key']:45} active={s['active']}  {s['title']}")

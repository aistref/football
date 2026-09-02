import sys, urllib.parse, json
sys.path.insert(0,'.')
from scripts.fotmob import _get_json
for q in ("Challenge League","Vaduz","Zbrojovka","Narodni Liga"):
    for url in (f"https://www.fotmob.com/api/searchapi/?term={urllib.parse.quote(q)}&lang=en",
                f"https://www.fotmob.com/api/search/suggest?term={urllib.parse.quote(q)}&lang=en"):
        try:
            d=_get_json(url)
            print("==",q,url.split('/api/')[1][:20])
            s=json.dumps(d)[:900]
            print(s)
            break
        except Exception as e:
            print("  err",q,type(e).__name__,str(e)[:50])

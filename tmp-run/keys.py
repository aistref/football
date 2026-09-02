import sys, json, urllib.request
sys.path.insert(0,'.')
from scripts import oddsapi
url=f"https://api.the-odds-api.com/v4/sports/?apiKey={oddsapi._api_key()}"
req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
data=json.load(urllib.request.urlopen(req, timeout=45))
soccer=[s for s in data if s.get("group")=="Soccer" and s.get("active")]
print("active soccer:", len(soccer))
for s in soccer:
    print(" ", s["key"], "|", s.get("title"))

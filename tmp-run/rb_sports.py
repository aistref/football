import os, json, urllib.request
key=os.environ.get('ODDS_API_KEY')
print("key set:", bool(key))
u=f"https://api.the-odds-api.com/v4/sports/?apiKey={key}"
d=json.load(urllib.request.urlopen(u, timeout=30))
want=['greece','sweden','croatia','romania','segunda','netherlands','albania','eerste','allsven','norway','denmark']
for s in d:
    k=s['key']
    if any(w in k.lower() for w in want) or 'soccer' in k and any(w in s['title'].lower() for w in want):
        print(f"{k:45} active={s['active']}  {s['title']}")
print("---totaal soccer---", sum(1 for s in d if s['key'].startswith('soccer')))

import unicodedata, re, difflib

TRANS = str.maketrans({'ł':'l','Ł':'l','ø':'o','Ø':'o','đ':'d','Đ':'d','ß':'ss','æ':'ae','å':'a','þ':'th'})

def norm(s):
    s = s.translate(TRANS)
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", ' ', s)
    stop = {'fc','sc','ac','cf','afc','sad','futebol','de','da','1','05','04','club','tsg','fsv',
            'city','united','town','rovers','athletic','wanderers','albion','county','spor',
            'north','end','hove','and','the','borussia','eintracht','vfb','vfl','sv','bsc',
            'b','cd','ud','sd','calcio','ss','as','us','ogc','rc','sm','stade','olympique'}
    toks = [t for t in s.split() if t and t not in stop]
    return ' '.join(toks) if toks else re.sub(r'\s+',' ',s).strip()

MANUAL = {
 'Nottm Forest':'Nottingham Forest', "M'gladbach":'Borussia Mönchengladbach', 'Köln':'1. FC Köln',
 'Mainz':'Mainz 05', 'Leverkusen':'Bayer Leverkusen', 'Frankfurt':'Eintracht Frankfurt',
 'Dortmund':'Borussia Dortmund', 'Stuttgart':'VfB Stuttgart', 'Bournemouth':'AFC Bournemouth',
 'Tottenham':'Tottenham Hotspur', 'Newcastle':'Newcastle United', 'West Ham':'West Ham United',
 'West Brom':'West Bromwich Albion', 'Sheff Utd':'Sheffield United', 'QPR':'Queens Park Rangers',
 'Preston':'Preston North End', 'Blackburn':'Blackburn Rovers', 'Charlton':'Charlton Athletic',
 'Derby':'Derby County', 'Norwich':'Norwich City', 'Stoke':'Stoke City', 'Swansea':'Swansea City',
 'Cardiff':'Cardiff City', 'Hull':'Hull City', 'Coventry':'Coventry City',
 'Wolves':'Wolverhampton Wanderers', 'Atlético Madrid':'Atletico Madrid',
 'Hearts':'Heart of Midlothian', 'Marítimo':'Maritimo', 'Académico Viseu':'Academico Viseu',
 'PSV':'PSV Eindhoven',
}
# losse tokens die als synoniem gelden bij het koppelen van oddsbronnen
SYN = [('mgladbach','monchengladbach'), ('gladbach','monchengladbach'), ('spurs','tottenham'),
       ('wolves','wolverhampton'), ('inter','internazionale'), ('psg','paris saint germain')]

def _canon(s):
    # korte fixture-namen eerst naar hun volledige vorm; anders koppelt 'QPR' nergens aan
    s = MANUAL.get(s, s)
    n = norm(s)
    for a, b in SYN:
        if a in n.split() or n == a:
            n = n.replace(a, b)
    return n

def sim(a, b):
    na, nb = _canon(a), _canon(b)
    if na == nb: return 1.0
    if na and nb and (na in nb or nb in na): return 0.95
    ta, tb = set(na.split()), set(nb.split())
    if ta & tb: return 0.8 + 0.1 * len(ta & tb) / max(len(ta), len(tb))
    return difflib.SequenceMatcher(None, na, nb).ratio()

def resolve(fixture_name, table_names):
    if fixture_name in table_names: return fixture_name
    m = MANUAL.get(fixture_name)
    if m and m in table_names: return m
    scored = sorted(((sim(fixture_name, t), t) for t in table_names), reverse=True)
    # 0.95 = alleen exacte gelijkheid of volledige insluiting na normalisatie. Lager
    # koppelde West Ham aan West Bromwich Albion, St. Johnstone aan St. Mirren en
    # Wisla Krakow aan Wisla Plock — alle drie op een gedeeld eerste woord.
    if scored and scored[0][0] >= 0.95 and (len(scored) == 1 or scored[0][0] > scored[1][0]):
        return scored[0][1]
    return None

def pair_match(home, away, pairs, threshold=1.60):
    """pairs: list of (home_name, away_name, payload). Geeft de best passende payload."""
    best, bs = None, 0.0
    for h, a, payload in pairs:
        s = sim(home, h) + sim(away, a)
        if s > bs: best, bs = payload, s
    return (best, bs) if bs >= threshold else (None, bs)

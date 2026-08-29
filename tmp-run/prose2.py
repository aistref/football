import json, pickle, sys
sys.path.insert(0,'tmp-run')
res = pickle.load(open('tmp-run/deep3.pkl','rb'))
picks = [json.loads(l) for l in open('data/picks.jsonl') if l.strip()]
picks = [p for p in picks if p['run_date']=='2026-08-29' and p['run']=='A' and p['result']=='pending']
risk = json.load(open('tmp-run/risk2.json'))
COMPN={'Super Lig (TUR)':'Süper Lig (TUR)'}
def find(p):
    return next(r for r in res if COMPN.get(r['row']['comp'],r['row']['comp'])==p['competition']
                and r['row']['home']==p['home'] and r['row']['away']==p['away'])

WHY = {
 'Over/Under': "U wint als er {n} vallen in deze wedstrijd. De bookmakers geven daar {imp} kans op, ik kom op {my}. Mijn model verwacht ongeveer {lh} doelpunt van de thuisploeg en {la} van de uitploeg.",
 'Double Chance': "U wint als {team} wint óf gelijkspeelt — alleen bij verlies bent u uw inzet kwijt. De bookmakers geven dat {imp} kans, ik kom op {my}.",
 'Draw No Bet': "U wint als {team} wint; bij gelijkspel krijgt u uw hele inzet terug. Alleen verlies kost u geld. De bookmakers geven {imp}, ik kom op {my}.",
 'Asian Handicap': "{team} begint deze weddenschap met een voorsprong of achterstand van {pt} doelpunt. De bookmakers geven dit {imp} kans, ik kom op {my}.",
}
RISKTXT = {
 'low': "Laag risico naar mijn maatstaven: mijn twee rekenmethodes zijn het eens (allebei ruim boven de bookmakers) en het voordeel blijft overeind als ik aan alle knoppen van mijn model draai.",
 'med': "Gemiddeld risico: de onderbouwing is in orde, maar mijn twee rekenmethodes lopen behoorlijk uiteen in hóevéél voordeel ze zien, of het voordeel slinkt flink zodra ik aan mijn model draai.",
 'high': "<b>Hoog risico.</b> Deze weddenschap haalt mijn drempel maar overleeft mijn eigen controles op het nippertje: één van mijn twee rekenmethodes ziet weinig voordeel, of het voordeel is bijna weg zodra ik aan de knoppen draai.",
}
def num(x): return f"{x*100:.0f} procent"
def pp(v):
    tekst = f"{abs(v):.1f}".replace('.', ',')
    return (tekst if v >= 0 else 'min ' + tekst)
bets = {}
for p in picks:
    r = find(p); t = r['passing'][0]
    lh, la = r['lam_xg']
    if p['market']=='Over/Under':
        line = p['selection'].split()[-1]; over = p['selection'].startswith('Over')
        n = f"meer dan {line.replace('.',',')} doelpunt" if over else f"minder dan {line.replace('.',',')} doelpunt"
        why = WHY['Over/Under'].format(n=n, imp=num(p['implied_prob']), my=num(p['my_prob']),
                                       lh=f"{lh:.1f}".replace('.',','), la=f"{la:.1f}".replace('.',','))
    elif p['market']=='Double Chance':
        team = p['home'] if t['side']=='home' else p['away']
        why = WHY['Double Chance'].format(team=team, imp=num(p['implied_prob']), my=num(p['my_prob']))
        why += " Deze weddenschap kocht ik als de +0,5-handicap: dat is precies dezelfde uitbetaling, maar hij zat gratis in een aanvraag die ik toch al deed."
    elif p['market']=='Draw No Bet':
        team = p['selection']
        why = WHY['Draw No Bet'].format(team=team, imp=num(p['implied_prob']), my=num(p['my_prob']))
    else:
        team = ' '.join(p['selection'].split()[:-1]); pt = p['selection'].split()[-1].replace('.',',')
        why = WHY['Asian Handicap'].format(team=team, pt=pt, imp=num(p['implied_prob']), my=num(p['my_prob']))
    book = p['odds_source'].split(' (')[0]
    bets[p['id']] = {'book': book, 'why': why,
                     'risk': RISKTXT[risk[p['id']]] + (
                        " Concreet: mijn kansenmethode ziet " + pp(t['edge_xg']) + " procentpunt voordeel, "
                        "mijn doelpuntenmethode " + pp(t['edge_split']) + ", en bij de ongunstigste "
                        "instelling van mijn model blijft er " + pp(t['robust']) + " over."),
                     'risk_level': risk[p['id']]}

P = {
 "_doc": ["De leesbare tekst bij runs/2026-08-29-run-a.html (herdraai).",
          "Structurele data haalt scripts/report.py zelf uit picks.jsonl en data/run-state/."],
 "started": "07:45",
 "truncated": 14,
 "sources": ("prijzen: handicaps, Draw No Bet en Double Chance om 07:52 · doelpuntenmarkten om 04:35 "
   "(La Liga opnieuw om 08:05) · uitslagmarkt van BetExplorer om 07:55 · cijfers van Fotmob en "
   "football-data.co.uk · 10 betaalde aanvragen verbruikt, 68 over deze maand"),
 "verdict": ("<b>Dit is een tweede, herziene versie van vanochtend.</b> U vond de eerste te eenzijdig — "
   "twaalf van de veertien weddenschappen gingen over het aantal doelpunten — en u had gelijk: dat kwam "
   "niet uit mijn analyse maar uit mijn inkoop. Bij het uitzoeken bleek er geld te liggen dat ik liet "
   "liggen: één aanvraag van één credit levert niet één markt maar <b>drie</b> (handicap, Draw No Bet "
   "én Double Chance), omdat die laatste twee letterlijk dezelfde weddenschap zijn als een handicap van "
   "0 en van een halve goal. Double Chance kocht ik tot vandaag apart in, voor twintig keer die prijs. "
   "Met die volgorde omgedraaid heeft elke wedstrijd nu vier markten in plaats van twee. "
   "Ook heb ik de afkapregel vervangen die vanochtend de hele Bundesliga uit de run gooide, en de "
   "limiet voor het weekend verhoogd van 30 naar 35 wedstrijden. Resultaat: <b>20 weddenschappen uit "
   "35 wedstrijden</b>, over vier verschillende markten, en de Bundesliga is terug. "
   "De vijf die ik zelf zou spelen staan hieronder; de sterkste is <b>Real Sociedad – Espanyol, meer "
   "dan 2,5 doelpunt</b> bij 1xBet. Eén waarschuwing die ik er zelf bij zet: twintig weddenschappen uit "
   "vijfendertig wedstrijden is véél, en een deel daarvan is rekenkunde — hoe meer markten ik bekijk, "
   "hoe groter de kans dat er ergens één doorheen komt. Dat houd ik de komende weken in de gaten."),
 "coverage_labels": {
  "League Cup (ENG)":"Engelse League Cup","UEFA Champions League":"Champions League",
  "UEFA Europa League":"Europa League","UEFA Conference League":"Conference League",
  "FA Cup (ENG)":"FA Cup","Coppa Italia (ITA)":"Coppa Italia","KNVB Beker (NED)":"KNVB Beker",
  "DFB Pokal (GER)":"DFB-Pokal","Championship (ENG)":"Engelse Championship",
  "Danish Superliga (DEN)":"Deense Superliga","Ekstraklasa (POL)":"Poolse Ekstraklasa",
  "Scottish Premiership (SCO)":"Schotse Premiership","Primeira Liga (POR)":"Portugese Primeira Liga",
  "Belgian Pro League (BEL)":"Belgische Pro League","Süper Lig (TUR)":"Turkse Süper Lig",
  "Premier League (ENG)":"Premier League","Serie A (ITA)":"Serie A","La Liga (ESP)":"La Liga",
  "Bundesliga (GER)":"Bundesliga","Ligue 1 (FRA)":"Ligue 1","Eredivisie (NED)":"Eredivisie"},
 "coverage_notes": {
  "Ligue 1 (FRA)":"vijf wedstrijden, alle vijf doorgerekend · vier bets · de enige competitie waar vandaag alles paste",
  "Bundesliga (GER)":"zes wedstrijden, vier doorgerekend · twee bets · vanochtend viel deze competitie er nog volledig uit",
  "La Liga (ESP)":"drie wedstrijden, alle drie doorgerekend · twee bets",
  "Championship (ENG)":"elf wedstrijden, zes doorgerekend · één bet · vijf overgeslagen wegens een club uit een andere divisie",
  "Ekstraklasa (POL)":"vier wedstrijden, drie doorgerekend · twee bets · Wisła Kraków – Wieczysta Kraków kan ik niet beoordelen",
  "Scottish Premiership (SCO)":"drie wedstrijden, twee doorgerekend · twee bets",
  "Serie A (ITA)":"vier wedstrijden, twee doorgerekend · twee bets",
  "Premier League (ENG)":"vier wedstrijden, drie doorgerekend · één bet",
  "Süper Lig (TUR)":"drie wedstrijden, alle drie doorgerekend · één bet",
  "Eredivisie (NED)":"drie wedstrijden, alle drie doorgerekend · geen bet",
  "Primeira Liga (POR)":"drie wedstrijden, één doorgerekend · geen bet · twee clubs uit de tweede divisie kan ik niet omrekenen",
  "Belgian Pro League (BEL)":"speelt dit weekend zondag en maandag",
  "Danish Superliga (DEN)":"vandaag niets op de kalender"},
 "bets": bets,
 "todo": [
  {"title":"Mijn model geeft underdogs structureel te veel kans — en ik weet nu waar het vandaan komt",
   "detail":("Ik houd sinds een week bij of mijn kansschattingen systematisch scheef staan. Vandaag is "
     "die meting voor het eerst groot genoeg om iets te betekenen: 169 waarnemingen, waar 150 de "
     "ondergrens is. De uitkomst is stabiel — ik geef uitkomsten die de bookmakers onder de 25 procent "
     "zetten ruim twee procentpunt méér kans dan zij, en favorieten vier procentpunt minder. "
     "Nieuw is dat ik nu kan aanwijzen wáár het zit: bijna twee van die twee-en-een-halve procentpunt "
     "komt van één instelling in mijn model die op 'begin van het seizoen' staat en nooit afloopt. "
     "Dat wil ik repareren, maar niet in dezelfde run als drie andere wijzigingen — dan weet ik "
     "achteraf niet meer welke verandering wat deed."),
   "when":"volgende run"},
  {"title":"Twintig weddenschappen uit vijfendertig wedstrijden is veel",
   "detail":("Vanochtend waren het er veertien uit dertig, nu twintig uit vijfendertig. Een deel van die "
     "stijging is echt: er dingen nu vier markten per wedstrijd mee in plaats van twee, dus er valt meer "
     "te vinden. Maar een deel is rekenkunde. Ik reken nu 423 mogelijke weddenschappen door in plaats van "
     "273, en bij meer pogingen komt er vaker één door mijn zeven controles heen zonder dat mijn "
     "inschatting beter is geworden. Ik hou per wedstrijd hooguit één weddenschap over, dus het loopt "
     "niet uit de hand, maar als het aantal bets structureel omhoog gaat terwijl het rendement niet "
     "meebeweegt, dan hoort er een strengere drempel te komen. Dat is over een week of twee te zien."),
   "when":"over een week of twee"},
  {"title":"De reservesleutel voor koersen is weg, en de belangrijkste sleutel ontbreekt nog steeds",
   "detail":("Ongewijzigd sinds vanochtend. De tweede leverancier van koersen is niet meer in de "
     "instellingen te vinden — gisteren werd de sleutel nog geweigerd, vandaag is hij verdwenen. Dat "
     "maakt vandaag niets uit (ik heb nog 68 aanvragen bij mijn hoofdleverancier), maar de noodvoorraad "
     "is er niet. En API-Football is de zeventiende dag op rij niet ingesteld; Fotmob vangt dat op, maar "
     "daarmee hangt alles aan één bron."),
   "when":"wanneer het uitkomt"}],
 "finding": [
  {"title":"Wat mij vandaag opviel: één aanvraag kocht drie markten, en dat had ik nooit gezien",
   "paragraphs":[
    "U vond de lijst van vanochtend te eenzijdig. Dat was hij ook — twaalf van de veertien weddenschappen gingen over het aantal doelpunten — en de oorzaak lag niet in mijn analyse maar in wat ik had ingekocht.",
    "Koersen kosten geld: ik heb een gratis abonnement met vijfhonderd aanvragen per maand. Mijn regel zei sinds een week: koop eerst de doelpuntenmarkt, want die kost één aanvraag per competitie en de handicapmarkt kost er twee. Met elf competities en dertien aanvragen ging het hele budget daarheen, en hielden negen competities alleen de gewone uitslagmarkt over. Mijn analyse kón dus niets anders kiezen dan doelpunten.",
    "Bij het uitzoeken bleek die rekensom fout. De handicapmarkt kost óók één aanvraag, en — dit is het punt — <b>een handicap van 0 is precies hetzelfde als Draw No Bet, en een handicap van een halve goal is precies hetzelfde als Double Chance.</b> Niet ongeveer: exact dezelfde uitbetaling, tot op zes decimalen nagerekend. Eén aanvraag van één credit levert dus drie markten, niet één.",
    "En dat legt een tweede fout bloot. Ik kocht Double Chance tot vandaag apart in, voor twee aanvragen <b>per wedstrijd</b> in plaats van één per competitie. Op 15 augustus concludeerde ik uit die kosten dat Double Chance 'dertig aanvragen per weddenschap' kostte en er als eerste af moest. Die conclusie ging niet over de markt maar over de manier waarop ik hem kocht.",
    "Dat is voor mij de echte les van vandaag, en hij is breder dan dit geval: een meting van wat een markt kost, meet de inkoopweg — niet de markt. Ik heb de volgorde omgedraaid, en het resultaat staat hierboven: waar vanochtend twee markten meededen, dingen er nu vier mee, en er komen weddenschappen uit vier verschillende soorten in plaats van twee.",
    "Eerlijk erbij: het aantal doelpuntenweddenschappen is nog altijd veertien van de twintig. Maar nu is dat mijn analyse die spreekt. Elke doorgerekende wedstrijd heeft drie tot vijf markten gehad, en de gewone uitslagmarkt — 105 mogelijkheden doorgerekend — leverde er nul op omdat er geen enkele door mijn controles kwam. Dat is iets anders dan hem niet gekeken hebben."]}],
}
P['settled'] = [
 {"label":"De veertien weddenschappen van vanochtend zijn vervallen, niet verloren",
  "score":("De eerste versie van vandaag publiceerde veertien weddenschappen. Die zijn allemaal op "
    "'vervallen' gezet vóórdat er ook maar één wedstrijd was begonnen, en vervangen door de twintig "
    "hierboven. Ze tellen dus niet mee in mijn rendement — dat zou oneerlijk zijn in beide richtingen. "
    "Elf van de twintig van nu staan op dezelfde wedstrijd als vanochtend; negen zijn nieuw, en in vier "
    "gevallen koos ik een andere markt op dezelfde wedstrijd omdat er nu meer te kiezen viel."),
  "result":"void"}]
json.dump(P, open('runs/2026-08-29-run-a.prose.json','w'), ensure_ascii=False, indent=1)
print('bets in prose:', len(P['bets']))

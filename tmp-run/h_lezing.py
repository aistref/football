"""Het dagrapport als voetbalverslag: wedstrijden eerst, mechaniek onderaan.

Vervangt de poortgerichte opzet. De gebruiker op 20 sep 2026: "Ik snak echt naar gewoon echte
verslagen, met inhoud, niet over poort dit poort dat." Terecht — het vorige rapport somde
poortstanden op en noemde geen enkele ploeg.
"""
import json, html

K = json.load(open("/tmp/claude-0/kandidaten.json"))

# Per kandidaat: wat de cijfers willen, wat het voetbal zegt, en het oordeel. Dit is het enige
# deel dat met de hand geschreven is; alle getallen komen uit de run.
LEZING = {
 "Kristiansund – Rosenborg": dict(
   speel=True, markt="Kristiansund wint", koers=5.61, edge=7.60,
   kop="De enige van vandaag waar het voetbal mijn cijfers steunt",
   waarom=("Rosenborg is in bloedvorm — <b>24 goals in vijf duels</b>, vier van de laatste vijf "
     "gewonnen — en staat daarom terecht als favoriet. Maar ze reizen af met <b>vier uitvallers</b>: "
     "Jonas Svensson, Iver Fossum, Johan Bakke en spits Dino Islamović. Dat is een spits, een "
     "controleur en een vleugel tegelijk."),
   tegen=("De onderlinge balans is 4–9–13 in het voordeel van Rosenborg over 26 duels, en "
     "Kristiansund won er maar vier van. Wie op de thuisploeg zet, gaat tegen dertig jaar "
     "geschiedenis in."),
   oordeel=("Kristiansund staat zelf op twaalf goals in vijf, speelt thuis en heeft evenveel rust. "
     "Met vier absenties aan de overkant vind ik 17,8% voor de thuisploeg te laag. <b>Dit is de "
     "bet die ik zou spelen.</b>")),
 "Athletic Club – Deportivo Alavés": dict(
   speel=False, markt="Alavés wint", koers=5.90, edge=5.36,
   kop="Mijn cijfers willen Alavés, de kalender spreekt ze tegen",
   waarom=("Athletic Club scoorde <b>zeven keer in vijf duels</b> en verloor er twee — geen ploeg "
     "in vorm. Alavés kwam tot acht goals in diezelfde periode."),
   tegen=("Alavés speelde <b>vier dagen geleden</b>, Athletic bijna zeven. In San Mamés is dat "
     "een reëel verschil, en de onderlinge stand is 11–8–6 voor Athletic. Fotmob noteert bovendien "
     "dat deze twee hun laatste vier ontmoetingen geen van alle gelijkspeelden — het wordt "
     "zelden een saaie 0–0, maar wel meestal Athletic."),
   oordeel=("Het rustverschil is precies waar mijn contextcontrole op aanslaat, en hier ben ik het "
     "met die controle eens. <b>Niet spelen.</b>")),
 "Osasuna – Rayo Vallecano": dict(
   speel=False, markt="Osasuna −1", koers=4.25, edge=3.80,
   kop="Mijn model wil dat een ploeg met twee doelpunten wint die al twee duels niet scoorde",
   waarom=("Op seizoens-xG is Osasuna de betere ploeg: 1,90 tegen 1,24 verwachte goals."),
   tegen=("Osasuna verloor de laatste drie en <b>scoorde niet in de laatste twee</b>. Ze missen "
     "Aimar Oroz én Moi Gómez — hun twee aanjagers — plus Herrando en Rosier achterin. En mijn "
     "model vraagt van deze ploeg een zege met twee doelpunten verschil."),
   oordeel=("Dit is geen waarde maar een blinde vlek: mijn cijfers komen uit het hele seizoen en "
     "weten niet dat de aanval stilstaat. <b>Niet spelen</b>, en het is een goed voorbeeld van "
     "waar ik nog mis zit.")),
 "Sevilla – Barcelona": dict(
   speel=False, markt="Sevilla wint", koers=11.00, edge=3.78,
   kop="Vijf keer winst in 44 duels, en mijn model ziet er waarde in",
   waarom=("De koers van 11,00 is hoog genoeg om mijn model te verleiden."),
   tegen=("Barcelona won de laatste vijf, scoorde <b>26 keer in vijf duels</b> en staat op 5–7–32 "
     "in het onderlinge klassement. Sevilla mist Lucas Stassin, hun man met de meeste schoten op "
     "doel per duel. Deze twee speelden hun laatste negen ontmoetingen nooit gelijk."),
   oordeel=("<b>Niet spelen.</b> Dit is mijn model dat het verschil tussen deze twee ploegen niet "
     "ziet — precies de fout die ik gisteren heb gemeten en maar half heb gerepareerd.")),
 "Ajax – Excelsior": dict(
   speel=False, markt="Excelsior wint", koers=12.50, edge=4.81,
   kop="Ajax scoorde twintig keer in vijf duels",
   waarom=("Ook hier is het de hoge koers die mijn model optilt."),
   tegen=("Ajax staat op <b>twintig goals in vijf duels</b>, hield de meeste nullen van de "
     "competitie, en Oscar Gloukh is koploper in gecreëerde grote kansen (6). Onderling: 14–5–2."),
   oordeel=("<b>Niet spelen.</b>")),
 "Bromley – Huddersfield Town": dict(
   speel=False, markt="Bromley wint", koers=6.10, edge=8.53,
   kop="De grootste 'edge' van de dag, op een ploeg die vijf duels niet won",
   waarom=("Met +8,5 procentpunt is dit het hoogste getal dat vandaag uit mijn model komt."),
   tegen=("Bromley <b>won in vijf pogingen niet</b> en hield in vijf duels geen enkele keer de nul. "
     "Huddersfield is ongeslagen in vijf met negen goals. Beide ploegen hadden een week rust, dus "
     "daar ligt het niet aan."),
   oordeel=("<b>Niet spelen.</b> Dat mijn grootste getal op mijn slechtste bet staat, is precies "
     "wat er al gemeten is: hoe groter het geclaimde voordeel, hoe slechter het rendement.")),
 "Salford City – Swindon Town": dict(
   speel=False, markt="Swindon wint", koers=6.10, edge=5.22,
   kop="Swindon verloor in zeven ontmoetingen geen enkele keer van Salford — andersom",
   waarom=("Mijn model geeft Swindon meer kans dan de 16% die de koers impliceert."),
   tegen=("Fotmob is er helder over: <b>Salford verloor in de laatste zeven onderlinge duels niet</b> "
     "van Swindon (vier keer winst, drie gelijk). Salford had een week rust, Swindon vier dagen. En "
     "mijn eigen doelverwachting zet Salford hoger (1,69 tegen 1,19)."),
   oordeel=("<b>Niet spelen</b> — mijn eigen cijfers spreken deze keuze zelfs tegen.")),
 "Young Boys – Servette": dict(
   speel=False, markt="Servette wint", koers=5.02, edge=3.19,
   kop="De topscorer van de competitie staat aan de andere kant",
   waarom=("Servette op 5,02 is de laatste kandidaat die boven mijn ondergrens uitkomt."),
   tegen=("Young Boys scoorde <b>zestien keer in vijf duels</b> en heeft met Samuel Essende de "
     "topscorer van de Super League (8). Servette kwam tot zes goals, speelde drie dagen geleden "
     "tegen bijna zeven voor Young Boys, en mist keeper Jérémy Frick plus drie anderen."),
   oordeel=("<b>Niet spelen.</b>")),
}

CSS = open("runs/2026-09-20-voorbeeld-lezing.html").read().split("<style>")[1].split("</style>")[0]


def kaart(naam, d, k):
    cls = "flag" if d["speel"] else ""
    tag = ('<span class="tag lezing">Speelbaar</span>' if d["speel"]
           else '<span class="tag rang">Niet spelen</span>')
    vorm = k["vorm"]; rust = k["rust"]
    h = k["h2h"] or {}
    meta = (f'{k["ko"]} · {k["comp"]}'
            + (f' · onderling {h.get("thuisploeg_won")}–{h.get("gelijk")}–{h.get("uitploeg_won")}'
               if h else ""))
    ins = "".join(f"<li>{html.escape(t)}</li>" for t in k["insights"][:4])
    afw = ""
    for kant, lbl in (("thuis", "thuis"), ("uit", "uit")):
        namen = k["afwezig"].get(kant) or []
        if namen:
            afw += f"<li><b>afwezig {lbl}:</b> {html.escape(', '.join(namen[:5]))}</li>"
    return f"""
  <section>
    <h2>{html.escape(naam)}</h2>
    <div class="{cls}" style="padding:{'18px 20px' if d['speel'] else '0'}">
      <p style="margin-bottom:6px"><span class="eyebrow">{meta}</span></p>
      <h3 style="margin-top:4px">{d['kop']}</h3>
      <p>{tag} &nbsp;<span class="mono">{html.escape(d['markt'])} @ {d['koers']:.2f}</span>
         &nbsp;<span class="mono" style="color:var(--muted)">mijn voordeel {d['edge']:+.2f} pp</span></p>
      <p><b>Wat mijn cijfers zien.</b> {d['waarom']}</p>
      <p><b>Wat daartegenin gaat.</b> {d['tegen']}</p>
      <p>{d['oordeel']}</p>
    </div>
    <div class="facts" style="margin-top:14px">
      <div class="fact"><span class="lbl">Vorm thuis</span><span class="fig">{vorm.get('home') or '—'}</span>
        <span class="note">{(rust.get('home') or 0):.1f} dagen rust</span></div>
      <div class="fact"><span class="lbl">Vorm uit</span><span class="fig">{vorm.get('away') or '—'}</span>
        <span class="note">{(rust.get('away') or 0):.1f} dagen rust</span></div>
      <div class="fact"><span class="lbl">Doelverwachting</span>
        <span class="fig">{k['lam'][0]:.2f} – {k['lam'][1]:.2f}</span>
        <span class="note">mijn model, per duel</span></div>
    </div>
    <ul class="notes" style="margin-top:12px">{ins}{afw}</ul>
  </section>"""


def bouw(run, titel, intro):
    kaarten = "".join(kaart(n, LEZING[n], K[n]) for n in K if K[n]["run"] == run)
    return f"""<title>{titel}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <header>
    <div class="eyebrow"><span>zaterdag 19 september 2026</span><span>opgesteld 11:05</span></div>
    <h1>{titel}</h1>
    <p class="sub">{intro}</p>
  </header>
{kaarten}
  <footer>
    <p class="rule-quote">Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is
      de verwachtingswaarde negatief.</p>
    <p>Vorm, rust, blessures, onderlinge historie en de waarnemingen per wedstrijd komen van Opta
      via Fotmob. Koersen van The Odds API over 25 aanbieders, beste prijs per selectie,
      beurskoersen na commissie. Doelverwachting uit mijn eigen model, herijkt op 687 afgerekende
      uitkomsten.</p>
  </footer>
</div>"""


if __name__ == "__main__":
    a = bouw("A", "Run A · 19 september",
             "Vier wedstrijden uit 57 waar mijn cijfers iets zagen. Bij drie ervan spreekt het "
             "voetbal ze tegen, en dat is het eerlijke verhaal van deze dag.")
    b = bouw("B", "Run B · 19 september",
             "Vier wedstrijden uit 57 waar mijn cijfers iets zagen. Eén daarvan houd ik over, en "
             "het is de enige van de dag waar de absenties mijn kant op wijzen.")
    open("runs/2026-09-19-run-a-lezing.html", "w").write(a)
    open("runs/2026-09-19-run-b-lezing.html", "w").write(b)
    print("twee lezingen geschreven")

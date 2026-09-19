"""Dagrapport als voetbalverslag, met de gepubliceerde bets erin. 19 sep 2026, herdraai 2."""
import json, html
from scripts import dossier

WAAROM = {
 "Korona Kielce – Raków Częstochowa": "Korona speelt thuis tegen een Raków dat vier van de laatste vijf verloor, en mijn doelverwachting komt op 2,26 om 1,49 — samen bijna vier goals. Wiktor Długosz creëerde er al zes grote kansen. De markt prijst dit als een doorsnee duel; mijn cijfers niet.",
 "Hibernian – Aberdeen": "Het grootste krachtsverschil van mijn dag: 2,28 tegen 1,05 verwachte goals. Aberdeen won één van zijn laatste vijf. Hibernian kreeg dit seizoen de meeste strafschoppen van de competitie mee — maar gaf er ook de meeste weg, dus dat snijdt beide kanten op.",
 "VfB Stuttgart – Borussia Dortmund": "Dortmund won de laatste vijf op rij. Draw No Bet in plaats van de kale zege: bij een gelijkspel krijg je je inzet terug, en dat is precies de uitkomst waar mijn model het minst betrouwbaar is. Stuttgart is thuis sterk met Demirović (2,4 schoten op doel per duel), dus de verzekering is het kwartje koers waard.",
 "Wrexham – Southampton": "Allebei ongeslagen noch overtuigend, maar samen goed voor 3,15 verwachte goals en geen van beide houdt achterin de deur dicht. Southampton kwam ongeslagen uit vier duels zonder er een te winnen — dat levert open wedstrijden op.",
 "Paris FC – Strasbourg": "Strasbourg is zeven duels ongeslagen en hield de meeste nullen van de Ligue 1 (3), en tóch komt mijn verwachting op 3,47 goals samen. Dat is de ene kant van deze bet die me ongemakkelijk maakt; de andere is dat Paris FC thuis op 2,09 staat.",
 "Blackpool – Plymouth Argyle": "Twee ploegen die allebei rond de twee goals per duel verwacht worden en allebei wisselvallig zijn. Peacock-Farrell staat tweede in reddingen per duel van de hele League One — dat betekent dat er veel op zijn doel af komt.",
 "Luzern – Grasshopper": "Luzern won de laatste vier onderlinge duels, en de doelverwachting komt op 2,62 om 1,81 — samen ruim vier goals. Over 3,5 is een hoge lat, maar bij een verwachting van 4,4 is 1,87 aan de ruime kant.",
 "Gillingham – Bristol Rovers": "Bristol Rovers is vijf duels ongeslagen met acht goals, Gillingham speelde er drie op rij gelijk. Fotmob merkt op dat deze twee hun laatste vier ontmoetingen geen van alle gelijk eindigden — er valt hier meestal wel iets.",
 "Colchester United – Cheltenham Town": "Colchester won de vorige drie onderlinge duels en heeft in Oscar Thorn de nummer twee van de competitie in gecreëerde grote kansen (4). Thuis op 2,02 verwachte goals tegen 1,18.",
 "Young Boys – Servette": "Gisteren wilde mijn model Servette wínnen bij Young Boys, en dat was onzin — YB scoorde zestien keer in vijf duels en heeft de topscorer van de competitie. Maar dat beide ploegen scoren is een andere vraag: Servette kwam in zijn laatste twee wel tot doelpunten, en YB geeft ook wat weg. Dit is dezelfde wedstrijd, andere markt, en nu de goede kant.",
}
CSS = open("runs/2026-09-20-voorbeeld-lezing.html").read().split("<style>")[1].split("</style>")[0]


def kaart(p, m, d):
    ctx = m.get("context") or {}
    lam = m["lambdas"]["xg"]
    ins = "".join(f"<li>{html.escape(i['tekst'])}</li>" for i in d.insights[:3])
    h2 = d.h2h_summary or {}
    onder = (f" · onderling {h2.get('thuisploeg_won')}–{h2.get('gelijk')}–{h2.get('uitploeg_won')}"
             if h2 else "")
    return f"""
  <section>
    <h2>{html.escape(p['home'])} – {html.escape(p['away'])}</h2>
    <p><span class="eyebrow">{m['kickoff_nl']} · {html.escape(p['competition'])}{onder}</span></p>
    <div class="flag" style="padding:18px 20px">
      <span class="lbl">Bet</span>
      <p style="font-size:18px;margin-bottom:8px"><b>{html.escape(p['market'])} —
        {html.escape(p['selection'])}</b> tegen <span class="mono">{p['odds']:.2f}</span></p>
      <p style="margin-bottom:0">Mijn kans <span class="mono">{p['my_prob']*100:.1f}%</span>,
        de prijs zegt <span class="mono">{p['implied_prob']*100:.1f}%</span> — een voordeel van
        <span class="mono">{p['edge_pp']:+.2f}</span> procentpunt.</p>
    </div>
    <p>{WAAROM.get(f"{p['home']} – {p['away']}", "")}</p>
    <div class="facts">
      <div class="fact"><span class="lbl">Vorm thuis</span>
        <span class="fig">{(ctx.get('home') or {}).get('form') or '—'}</span>
        <span class="note">{((ctx.get('home') or {}).get('rest_days') or 0):.1f} dagen rust</span></div>
      <div class="fact"><span class="lbl">Vorm uit</span>
        <span class="fig">{(ctx.get('away') or {}).get('form') or '—'}</span>
        <span class="note">{((ctx.get('away') or {}).get('rest_days') or 0):.1f} dagen rust</span></div>
      <div class="fact"><span class="lbl">Doelverwachting</span>
        <span class="fig">{lam[0]:.2f} – {lam[1]:.2f}</span>
        <span class="note">samen {lam[0]+lam[1]:.2f} per duel</span></div>
    </div>
    <ul class="notes" style="margin-top:12px">{ins}</ul>
  </section>"""


def bouw(run, titel, intro, picks):
    kaarten = ""
    for p in picks:
        st = json.load(open(f"data/run-state/2026-09-19-run-{run.lower()}.json"))
        m = None
        for comp, b in st["competitions"].items():
            for x in b.get("matches", []):
                if x["match"] == f"{p['home']} – {p['away']}":
                    m = x
        kaarten += kaart(p, m, dossier.build(m["match_id"]))
    return f"""<title>{titel}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <header>
    <div class="eyebrow"><span>zaterdag 19 september 2026</span><span>opgesteld 11:40</span>
      <span>{len(picks)} bets</span></div>
    <h1>{titel}</h1>
    <p class="sub">{intro}</p>
  </header>
{kaarten}
  <footer>
    <p class="rule-quote">Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is
      de verwachtingswaarde negatief.</p>
    <p>Vorm, rust, blessures, onderlinge historie en de waarnemingen per wedstrijd komen van Opta
      via Fotmob. Koersen van The Odds API over 25 aanbieders, beste prijs per selectie,
      beurskoersen na commissie.</p>
  </footer>
</div>"""


if __name__ == "__main__":
    picks = [json.loads(l) for l in open("data/picks.jsonl") if l.strip()]
    vandaag = [p for p in picks if p["run_date"] == "2026-09-19"]
    intro = ("Voor het eerst in twee weken komen er weer bets uit, en het zijn favorieten en "
             "doelpuntenmarkten in plaats van longshots. De reden staat onderaan: de correctie die "
             "ik op elke kansschatting toepaste, was gefit op de verkeerde steekproef.")
    for run in ("A", "B"):
        sel = [p for p in vandaag if p["run"] == run]
        open(f"runs/2026-09-19-run-{run.lower()}-lezing.html", "w").write(
            bouw(run, f"Run {run} · 19 september", intro, sel))
        print(f"Run {run}: {len(sel)} bets")

"""Dagrapport in de volgorde die de gebruiker op 20 sep 2026 vroeg.

Eerst context, dan wat anderen voorspellen, dan de marktodds, dan pas de vergelijking en de bet.
Met de vaste kopjes terug: bets vandaag, wat in beeld was, wat ik nog moet doen, bevinding,
dekkingsrapportage, eerlijke stand, de termen en de disclaimer.
"""
import json, html, collections
from scripts import dossier

CSS = open("runs/2026-09-20-voorbeeld-lezing.html").read().split("<style>")[1].split("</style>")[0]
PIN = json.load(open("/tmp/claude-0/pinnacle.json"))
NEAR = {"FULL": 3.0, "LIGHT": 6.0}

CONTEXT = {
 "Korona Kielce – Raków Częstochowa": "Een Pools duel tussen een middenmoter en een ploeg die het spoor bijster is: Raków verloor vier van de laatste vijf. Korona won er thuis twee van de laatste drie. Wiktor Długosz creëerde dit seizoen al zes grote kansen voor de thuisploeg — de meeste van de selectie.",
 "Hibernian – Aberdeen": "Schotse middenmoot, en allebei wisselvallig: Hibernian won er twee van vijf, Aberdeen één. Wat eruit springt is de strafschoppenstatistiek — Hibernian kreeg er dit seizoen de meeste van de competitie mee (2) én gaf er de meeste weg (2). Dat maakt de wedstrijd rommeliger dan de stand suggereert.",
 "VfB Stuttgart – Borussia Dortmund": "De grootste wedstrijd van de Bundesliga-zaterdag. Dortmund won de laatste vijf op rij en scoorde dertien keer in die reeks. Stuttgart is thuis lastig, met Mittelstädt als aanjager (vier grote kansen gecreëerd) en Demirović die 2,4 schoten op doel per duel produceert.",
 "Wrexham – Southampton": "Twee ploegen die niet verliezen maar ook niet winnen. Southampton kwam ongeslagen uit vier duels zonder er een te winnen; Wrexham speelde er twee op rij gelijk. Kieffer Moore is de aanspeelpunt bij de thuisploeg.",
 "Paris FC – Strasbourg": "Strasbourg is zeven duels ongeslagen en hield de meeste nullen van de Ligue 1 — op papier een gesloten wedstrijd. Paris FC daarentegen scoorde acht keer in vijf duels en speelt thuis.",
 "Blackpool – Plymouth Argyle": "League One-duel tussen twee ploegen die allebei niet weten of ze meedoen of niet. Plymouth won er twee van de laatste drie, Blackpool verloor er drie van vijf. Keeper Peacock-Farrell staat tweede in reddingen per duel van de hele competitie — er komt veel op zijn doel af.",
 "Luzern – Grasshopper": "Luzern won de vorige vier onderlinge ontmoetingen, en dat is in Zwitserland een reeks die telt. Beide ploegen wisselen winst en verlies af; Letica bij de bezoekers staat derde in reddingen per duel.",
 "Gillingham – Bristol Rovers": "Bristol Rovers is vijf duels ongeslagen met acht goals; Gillingham speelde er drie op rij gelijk. Fotmob merkt op dat deze twee hun laatste vier ontmoetingen geen van alle gelijk eindigden.",
 "Colchester United – Cheltenham Town": "Colchester won de vorige drie onderlinge duels. Oscar Thorn staat tweede in de hele League Two in gecreëerde grote kansen (4) en is de reden dat de thuisploeg op 2,02 verwachte goals komt.",
 "Young Boys – Servette": "Young Boys scoorde zestien keer in vijf duels en heeft in Samuel Essende de topscorer van de Super League (8). Servette kwam tot zes goals en speelde drie dagen geleden, tegen bijna zeven dagen rust voor de thuisploeg. Gisteren wilde mijn model hier Servette laten wínnen — dat was onzin.",
}
VERGELIJKING = {
 "Korona Kielce – Raków Częstochowa": "Mijn doelverwachting komt op 2,26 om 1,49 — samen 3,75. Dat is fors hoger dan de 2,5-lijn waar de markt op 54,6% zit. Het verschil zit vooral in Raków's verdediging, die in vijf duels weinig tegenhield.",
 "Hibernian – Aberdeen": "Pinnacle zet Hibernian op 54,0% na aftrek van de marge; ik kom op 67,7%. Dat is een groot verschil en het komt uit het krachtsverschil in verwachte goals (2,28 om 1,05). Neem dit als de meest onzekere van de vijf: als Pinnacle gelijk heeft, is er geen voordeel.",
 "VfB Stuttgart – Borussia Dortmund": "Pinnacle geeft Dortmund 36,1% en Stuttgart 38,7% — vrijwel gelijk. Ik zet Dortmund hoger, en daarom is Draw No Bet de veiligste uitdrukking: bij een gelijkspel krijg je de inzet terug, en dat is precies de uitkomst waar mijn model het minst betrouwbaar is.",
 "Wrexham – Southampton": "Samen 3,15 verwachte goals tegen een 2,5-lijn op 56,2%. Pinnacle ziet de wedstrijd als vrijwel gelijkwaardig (34,5% om 39,2%), wat bij open duels past.",
 "Paris FC – Strasbourg": "Hier ben ik het het minst met mezelf eens: Strasbourg hield de meeste nullen van de competitie en tóch komt mijn verwachting op 3,47 goals samen. Pinnacle zet Paris FC op 50,3%, wat past bij mijn 2,09 verwachte thuisgoals — maar de Over-lijn leunt op de aanname dat Strasbourg niet opnieuw de deur dichthoudt.",
 "Blackpool – Plymouth Argyle": "3,76 verwachte goals samen tegen een 2,75-lijn op 54,9%. Pinnacle noemt de wedstrijd vrijwel gelijk (36,7% om 38,6%), en gelijkwaardige duels in de League One leveren zelden 0–0 op.",
 "Luzern – Grasshopper": "4,43 verwachte goals samen — de hoogste van de dag. Over 3,5 op 1,87 impliceert 53,5%; ik kom op 66,0%. Pinnacle noteert deze wedstrijd niet op 1X2 in mijn uitlezing, dus hier ontbreekt de scherpe referentie.",
 "Gillingham – Bristol Rovers": "3,21 verwachte goals tegen een 2,5-lijn op 51,0%. Pinnacle zet Bristol Rovers duidelijk hoger (45,8% om 27,5%) — een uitploeg die favoriet is, produceert vaker een open wedstrijd dan een gesloten.",
 "Colchester United – Cheltenham Town": "Pinnacle zet Colchester op 48,1%, ik op 59,5%. Dat verschil van elf punten is de hele bet. De onderlinge reeks (drie zeges op rij) en Thorn's kansen creëren zijn wat mij hoger zet dan de markt.",
 "Young Boys – Servette": "Beide ploegen scoren staat op 1,47, oftewel 68,0%. Ik kom op 75,0%. Young Boys scoort vrijwel altijd; de vraag is of Servette tegenscoort, en dat deden ze in hun laatste twee wel.",
}
TERMEN = [
 ("Doelverwachting", "Hoeveel goals ik per ploeg verwacht, uit hun schotkwaliteit van dit en vorig seizoen. 2,26 om 1,49 betekent: samen bijna vier."),
 ("Mijn kans", "De kans die ik aan een uitkomst geef, nadat ik hem heb bijgesteld op wat er in 2346 eerdere wedstrijden werkelijk gebeurde."),
 ("De prijs zegt", "Wat de koers impliceert: 1 gedeeld door de koers. Inclusief de marge van het boek, dus altijd iets te hoog."),
 ("Voordeel", "Het verschil tussen die twee, in procentpunten. Positief betekent dat ik de uitkomst waarschijnlijker vind dan de prijs suggereert."),
 ("Pinnacle", "De scherpste bookmaker van de markt, met de laagste marge (3,4 tot 4,9% vandaag). Zijn prijs is het beste publieke expertoordeel dat er is — niet de prijs waar je op speelt, wel de prijs om je eigen mening aan te toetsen."),
 ("Draw No Bet", "Een weddenschap op een ploeg waarbij je je inzet terugkrijgt als het gelijkspel wordt. Kost koers, koopt zekerheid."),
 ("Over 2,5", "Er vallen drie of meer goals. Over 2,75 is een halve inzet op 2,5 en een halve op 3,0."),
]


def kaart(p, m, d):
    ctx = m.get("context") or {}
    lam = m["lambdas"]["xg"]
    naam = f"{p['home']} – {p['away']}"
    ins = "".join(f"<li>{html.escape(i['tekst'])}</li>" for i in d.insights[:4])
    afw = ""
    for kant, lbl in (("thuis", p["home"]), ("uit", p["away"])):
        namen = [x["naam"] for x in (d.unavailable.get(kant, {}).get("afwezig") or [])]
        if namen:
            afw += f"<li><b>{html.escape(lbl)} mist:</b> {html.escape(', '.join(namen[:5]))}</li>"
    h2 = d.h2h_summary or {}
    pin = PIN.get(p["id"])
    pinblok = ""
    if pin:
        pinblok = (f"<p>Pinnacle — de scherpste bookmaker, marge {pin['marge']}% — zet deze "
                   f"wedstrijd op <span class='mono'>{pin['devig'][0]*100:.1f}% / "
                   f"{pin['devig'][1]*100:.1f}% / {pin['devig'][2]*100:.1f}%</span> "
                   f"(thuis / gelijk / uit), na aftrek van zijn marge.</p>")
    else:
        pinblok = ("<p>Pinnacle noteerde deze wedstrijd niet in mijn uitlezing, dus de scherpe "
                   "referentie ontbreekt hier.</p>")
    return f"""
  <section>
    <h2>{html.escape(naam)}</h2>
    <p><span class="eyebrow">{m['kickoff_nl']} · {html.escape(p['competition'])}"""+(
      f" · onderling {h2.get('thuisploeg_won')}–{h2.get('gelijk')}–{h2.get('uitploeg_won')}" if h2 else "")+f"""</span></p>

    <h3>1 · De wedstrijd</h3>
    <p>{CONTEXT.get(naam, '')}</p>
    <div class="facts">
      <div class="fact"><span class="lbl">Vorm thuis</span>
        <span class="fig">{(ctx.get('home') or {}).get('form') or '—'}</span>
        <span class="note">{((ctx.get('home') or {}).get('rest_days') or 0):.1f} dagen rust</span></div>
      <div class="fact"><span class="lbl">Vorm uit</span>
        <span class="fig">{(ctx.get('away') or {}).get('form') or '—'}</span>
        <span class="note">{((ctx.get('away') or {}).get('rest_days') or 0):.1f} dagen rust</span></div>
      <div class="fact"><span class="lbl">Doelverwachting</span>
        <span class="fig">{lam[0]:.2f} – {lam[1]:.2f}</span>
        <span class="note">samen {lam[0]+lam[1]:.2f}</span></div>
    </div>
    <ul class="notes" style="margin-top:12px">{ins}{afw}</ul>

    <h3>2 · Wat de scherpste markt zegt</h3>
    {pinblok}

    <h3>3 · De prijzen</h3>
    <p>Beste prijs op mijn selectie: <span class="mono">{p['odds']:.2f}</span>
       ({html.escape(p['odds_source'][:70])}), oftewel een marktkans van
       <span class="mono">{p['implied_prob']*100:.1f}%</span>.</p>

    <h3>4 · De vergelijking</h3>
    <p>{VERGELIJKING.get(naam, '')}</p>
    <div class="flag" style="padding:18px 20px">
      <span class="lbl">Bet</span>
      <p style="font-size:18px;margin-bottom:8px"><b>{html.escape(p['market'])} —
        {html.escape(p['selection'])}</b> tegen <span class="mono">{p['odds']:.2f}</span></p>
      <p style="margin-bottom:0">Mijn kans <span class="mono">{p['my_prob']*100:.1f}%</span> tegen
        <span class="mono">{p['implied_prob']*100:.1f}%</span> uit de prijs —
        voordeel <span class="mono">{p['edge_pp']:+.2f}</span> procentpunt.</p>
    </div>
  </section>"""


def bouw(run, picks, st, res, ledger):
    comps = st["competitions"]
    rijen = []
    for comp, b in sorted(comps.items()):
        if b.get("status") != "GEANALYSEERD":
            rijen.append(f"<tr><td>{html.escape(comp)}</td><td>—</td><td>geen wedstrijd</td></tr>")
            continue
        t = collections.Counter(m["tier"] for m in b["matches"])
        n_bet = sum(1 for m in b["matches"] if m.get("bet"))
        rijen.append(f"<tr><td>{html.escape(comp)}</td><td class='num'>{len(b['matches'])}</td>"
                     f"<td>{', '.join(f'{v}× {k.lower()}' for k,v in sorted(t.items()))}"
                     + (f" · <b>{n_bet} bet</b>" if n_bet else "") + "</td></tr>")
    # wat in beeld was: kandidaten boven de ondergrens die het niet haalden
    gespeeld = {(p["home"] + " – " + p["away"], p["market"], p["selection"]) for p in picks}
    inbeeld = []
    for m in res["matches"]:
        for c in m.get("all_candidates", []):
            if c.get("edge_pp", 0) < NEAR.get(m["tier"], 3.0):
                continue
            if (m["match"], c["market"], c["selection"]) in gespeeld:
                continue
            dicht = [k for k, v in (c.get("poorten") or {}).items() if v is False]
            lbl = {"odds": "koers boven 6,00", "context": "rust of blessures",
                   "underdog": "te zwakke ploeg", "tweede_methode": "mijn twee methodes oneens",
                   "robuustheid": "houdt niet stand"}
            inbeeld.append((c["edge_pp"], m["match"], c["market"], c["selection"], c["odds"],
                            ", ".join(lbl.get(x, x) for x in dicht) or "buiten de top 5"))
    inbeeld.sort(reverse=True)
    inbeeld_html = "".join(
        f"<tr><td class='num'>{e:+.2f}</td><td>{html.escape(w)}</td>"
        f"<td>{html.escape(sel)}</td><td class='num'>{o:.2f}</td><td>{html.escape(r)}</td></tr>"
        for e, w, mk, sel, o, r in inbeeld[:8])
    kaarten = "".join(kaart(p, _match(st, p), dossier.build(_match(st, p)["match_id"]))
                      for p in picks)
    lijst = "".join(
        f"<tr><td>{m['kickoff_nl']}</td><td>{html.escape(p['home'])} – {html.escape(p['away'])}</td>"
        f"<td>{html.escape(p['selection'])}</td><td class='num'>{p['odds']:.2f}</td>"
        f"<td class='num pos'>{p['edge_pp']:+.2f}</td></tr>"
        for p, m in ((p, _match(st, p)) for p in picks))
    termen = "".join(f"<tr><td><b>{html.escape(t)}</b></td><td>{html.escape(u)}</td></tr>"
                     for t, u in TERMEN)
    return f"""<title>Run {run} · 19 september</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <header>
    <div class="eyebrow"><span>zaterdag 19 september 2026</span><span>opgesteld 12:20</span>
      <span>{len(picks)} bets uit {len(res['matches'])} wedstrijden</span></div>
    <h1>Run {run} · 19 september</h1>
    <p class="sub">Voor het eerst in twee weken weer bets, en het zijn favorieten en
      doelpuntenmarkten in plaats van longshots. Onder <b>Bevinding</b> staat waarom dat zo lang
      niet lukte.</p>
  </header>

  <section>
    <h2>Bets vandaag</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Aftrap</th><th>Wedstrijd</th><th>Selectie</th><th class="num">Koers</th>
        <th class="num">Voordeel</th></tr></thead>
      <tbody>{lijst}</tbody>
      <caption>Op volgorde van hoe sterk ik ze vind. Koersen van rond 11:40; controleer ze voor je inzet.</caption>
    </table></div>
  </section>
{kaarten}
  <section>
    <h2>Wat in beeld was maar het niet haalde</h2>
    <div class="tablewrap"><table>
      <thead><tr><th class="num">Voordeel</th><th>Wedstrijd</th><th>Selectie</th>
        <th class="num">Koers</th><th>Waarom niet</th></tr></thead>
      <tbody>{inbeeld_html or '<tr><td colspan="5">Niets boven de ondergrens.</td></tr>'}</tbody>
    </table></div>
  </section>

  <section>
    <h2>Dekkingsrapportage</h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Competitie</th><th class="num">Duels</th><th>Datakwaliteit</th></tr></thead>
      <tbody>{''.join(rijen)}</tbody>
      <caption>Afgekapt door de dagelijkse limiet van 55 wedstrijden: {res['afkapping']['afgekapt']}.</caption>
    </table></div>
  </section>

  <section>
    <h2>De eerlijke stand</h2>
    <pre style="overflow-x:auto;font-size:12.5px;font-family:'IBM Plex Mono',monospace;background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:14px">{html.escape(ledger)}</pre>
    <p>Dat is het rendement over alles wat ik ooit publiceerde. De bookmaker schat nog altijd
      scherper dan ik, en de tien bets van vandaag veranderen daar niets aan tot ze zijn afgerekend.</p>
  </section>

  <section>
    <h2>Bevinding</h2>
    <p><b>De correctie die ik op elke kansschatting toepaste, was op de verkeerde steekproef
      gefit.</b> Ik stelde mijn kansen bij op basis van de weddenschappen die eerder door mijn
      filters kwamen — maar dat zijn juist de gevallen waar ik het verst van de markt af zat, en
      daar is elk model te optimistisch. Die bijstelling liet ik vervolgens los op álle
      berekeningen.</p>
    <p>Gemeten op 2346 wedstrijduitkomsten die niet vooraf geselecteerd zijn: waar mijn ruwe
      berekening 70% of meer zei, gebeurde het <b>85,7%</b> van de tijd — en mijn
      &ldquo;gecorrigeerde&rdquo; schatting zei 64,1%. Ruim twintig procentpunt te laag, en aan de
      bovenkant het ergst. Daarom kon ik nooit op een favoriet spelen, en bestond elke lijst uit
      outsiders.</p>
    <p>De correctie is nu gefit op die ongeselecteerde steekproef en komt daarmee vrijwel op nul
      uit. Wat blijft: ik selecteer nog steeds op mijn eigen grootste fout, en daar is de lat van
      acht procentpunt voor — niet een aftrek op elke kans.</p>
  </section>

  <section>
    <h2>Wat ik nog moet doen</h2>
    <ul class="notes">
      <li><b>Mijn twee rekenmethodes spreken elkaar op vier van de vijf selecties tegen.</b>
        Verreweg de grootste zeef, en over 74 afgerekende gevallen bespaart hij vrijwel niets
        (−1,6%). Uitzoeken of die controle nog deugt.</li>
      <li><b>Geschreven voorspellingen van andere sites krijg ik niet binnen.</b> Pinnacle geeft
        404 op zijn artikelroute, Matchbook's blog ligt eruit, Betfair en Forebet zitten achter
        Cloudflare, en voetbalwedden's voorspellingenpagina bevat de wedstrijden van vandaag niet.
        Wat ik wél heb is Pinnacle's prijs zelf, en die gebruik ik hierboven als scherpe
        referentie.</li>
      <li><b>De rem op zwakke ploegen vervalt op 25 september.</b> Vandaag hield die niets tegen
        dat ik had willen spelen, maar dat verandert.</li>
      <li><b>Het scoregrid onderschat hoe scheef een duel met een duidelijke favoriet afloopt.</b>
        Gemeten over 155 zulke wedstrijden: de favoriet won 73,5% van de keren waar ik 65,5% zei.
        Half gerepareerd; de rest moet op nieuwe cijfers gemeten worden.</li>
    </ul>
  </section>

  <section>
    <h2>De termen</h2>
    <div class="tablewrap"><table><tbody>{termen}</tbody></table></div>
  </section>

  <footer>
    <p class="rule-quote">Beslissingsondersteuning, geen winnend systeem. Na de bookmakermarge is
      de verwachtingswaarde negatief.</p>
    <p>Wedstrijdfeiten, vorm, blessures en onderlinge historie: Opta via Fotmob. Koersen: The Odds
      API over 25 aanbieders, beste prijs per selectie, beurskoersen na commissie. Pinnacle apart
      vermeld als scherpste referentie.</p>
  </footer>
</div>"""


def _match(st, p):
    for comp, b in st["competitions"].items():
        for m in b.get("matches", []):
            if m["match"] == f"{p['home']} – {p['away']}":
                return m


if __name__ == "__main__":
    import subprocess
    ledger = subprocess.run(["python3", "scripts/ledger.py", "stats"],
                            capture_output=True, text=True).stdout.split("data_tier =")[0].strip()
    picks = [json.loads(l) for l in open("data/picks.jsonl") if l.strip()]
    vandaag = [p for p in picks if p["run_date"] == "2026-09-19"]
    for run, pad in (("A", "tmp-run/ra19h_results.json"), ("B", "tmp-run/rb19h_results.json")):
        st = json.load(open(f"data/run-state/2026-09-19-run-{run.lower()}.json"))
        res = json.load(open(pad))
        sel = [p for p in vandaag if p["run"] == run]
        open(f"runs/2026-09-19-run-{run.lower()}-lezing.html", "w").write(
            bouw(run, sel, st, res, ledger))
        print(f"Run {run}: {len(sel)} bets")

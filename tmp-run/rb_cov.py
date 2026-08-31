import json
c=json.load(open('data/coverage.json'))
C=c['competitions']
ADD={
 "Greek Super League (GRE)":
  " Run B 31 aug 2026: has_xg nu OOK true voor 2026/2027 (2 speeldagen, 14 ploegen) — het seizoen is "
  "begonnen. Basis blijft 2025/2026 (26 speeldagen). LET OP: xG loopt over mp=36, de tabel over "
  "played=26; de splitsrondes zitten wel in de xG en niet in de stand, dus de twee methodes zijn "
  "naast elkaar gelegd (poort 5). Levadiakos – Panathinaikos leverde de grootste edge van de run "
  "(+28.8 pp op AH +0.75) doordat Levadiakos vorig seizoen méér xG maakte (55.7) dan Panathinaikos "
  "(47.9) terwijl de markt Panathinaikos op 1.59 zette — een markt/model-gat van 35 pp op de 1X2. "
  "BetExplorer gaf hier maar 3 boeken.",
 "Allsvenskan (SWE)":
  " Run B 31 aug 2026: seizoen '2026' op 19 speelronden, has_xg=true — de enige competitie van deze "
  "run waar de teamsterkte uit het LOPENDE seizoen komt, dus geen vroeg-seizoenscorrectie. Alle drie "
  "de duels doorgerekend met alle zes markten; 2 bets (Over 2.5 en Under 2.5), 1 afgevallen op "
  "poort 5 (Sirius – Malmö FF: xG +14.1 pp tegen splits -5.8 pp op AH -1).",
 "Croatian HNL (CRO)":
  " Run B 31 aug 2026: has_xg=false opnieuw bevestigd voor 2025/2026 en 2026/2027. Beide duels "
  "doorgerekend op doelpunten (LIGHT); HNK Gorica – Rijeka leverde een LIGHT-bet op (Gorica @5.23, "
  "+11.0 pp). Geen sportkey bij The Odds API, dus alleen het gratis 1X2 van BetExplorer.",
 "Romanian SuperLiga (ROU)":
  " Run B 31 aug 2026: has_xg=false bevestigd. Eén duel (Rapid București – Universitatea Craiova), "
  "doorgerekend op doelpunten, alle drie de 1X2-uitkomsten onder de LIGHT-drempel. BetExplorer had "
  "hier met 19 boeken het diepste marktgemiddelde van de run. Naamkoppeling: 'Rapid București' "
  "(daglijst) tegen 'Rapid Bucuresti' (tabel) gaat goed via de diakrietennormalisatie.",
 "Segunda División (ESP)":
  " Run B 31 aug 2026: has_xg=true voor 2025/2026 (22 ploegen, 42 speeldagen) en nu ook voor "
  "2026/2027 (3 speeldagen); basis blijft vorig seizoen. Burgos CF – Real Sociedad B leverde een "
  "bet op (Under 2.5 @1.75). Celta Fortuna kwam op NONE: het B-elftal promoveerde uit de Primera "
  "Federación en promotion.TIER2 kent geen paar LaLiga2 -> Primera Federación, dus er is geen "
  "gemeten omrekenfactor. Dat is een echt bronngat, geen datagat — vergelijkbaar met de Eerste "
  "Divisie vóór 30 aug.",
 "Keuken Kampioen Divisie (NED)":
  " Run B 31 aug 2026: has_xg=false bevestigd. Beide duels waren beloftenelftallen onderling (Jong "
  "AZ – Jong Utrecht en Jong PSV – Jong Ajax); alle vier de ploegen staan gewoon in de KKD-stand van "
  "2025/26, dus LIGHT en geen promovendi-probleem. Jong AZ – Jong Utrecht leverde de tweede "
  "LIGHT-bet op (Jong Utrecht @4.59, +17.2 pp).",
 "Kategoria Superiore (ALB)":
  " Run B 31 aug 2026: has_xg=false bevestigd voor 2025/2026, 2026/2027 en '2026'. DOORBRAAK AAN DE "
  "ODDSKANT: de BetExplorer-slug albania/abissnet-superiore geeft nu WEL rijen (2 duels, 9 en 8 "
  "boeken) — dat gat stond sinds 13 aug open. Beide duels hadden dus voor het eerst een prijs. Vora "
  "– Egnatia is doorgerekend op doelpunten (LIGHT, alles onder de drempel); Skënderbeu – Dinamo City "
  "kwam op NONE omdat Skënderbeu niet in de stand van 2025/26 staat en promotion.TIER2 geen paar "
  "Kategoria Superiore -> Kategoria e Parë kent.",
 "Kosovo Superleague (KOS)":
  " Run B 31 aug 2026: opnieuw niet op de Fotmob-daglijst. Dekkingsgat blijft.",
}
for k,v in ADD.items():
    if k in C:
        C[k]['notes'] = C[k]['notes'].rstrip() + v
    else:
        print("ONBEKEND:",k)
c['updated']="2026-08-31"
json.dump(c, open('data/coverage.json','w'), ensure_ascii=False, indent=1)
print("coverage bijgewerkt:", len(ADD))

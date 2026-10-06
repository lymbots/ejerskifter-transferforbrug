# Ejerskifter og transferforbrug i fodbold, 1987-2026

Data og kode til analysen *Køber nye ejere sig til succes? Effekten af ejerskifter på transfermarkedet i engelsk fodbold* af Asger Krogh (oktober 2026): https://asgerkrogh.substack.com/p/kber-nye-ejere-sig-til-succes-effekten

## Data

- `data/ejerskifter.csv`: 69 skift af kontrol, hvor en ny ejer fik mere end halvdelen af aktierne, med dato, ejerandel, ejertype og kilde.
- `data/effekter.csv`: effekten af de 68 ejerskifter, der har data nok.
- `data/klub_saeson.csv`: køb, salg og netto for 4.288 klub-sæsoner.
- `data/pl_placeringer.csv`: slutplaceringer i Premier League 1992/93-2025/26.
- `data/raa/`: de filer, koden læser direkte (læg dem i en mappe `data/` ved siden af koden).

Køb, salg og placeringer er hentet fra Transfermarkt.com den 5. og 6. oktober 2026. Beløbene er Transfermarkts estimater i euro.

## Kode

1. `kode/hent_tm.js` køres i browserens konsol på transfermarkt.com.
2. `kode/analyse2.py` beregner målet og effekten af hvert ejerskifte.
3. `kode/robust2.py` gentager analysen med andre valg og placebotesten.
4. `kode/grafer2.py` tegner figur 1-7.
5. `kode/byg_datasaet.py` bygger datasættet.

Python 3 med pandas, numpy, matplotlib og openpyxl.

## Brug

Data og kode må gerne bruges med kildeangivelse: Asger Krogh (2026) på baggrund af Transfermarkt.

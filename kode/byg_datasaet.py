"""Bygger det offentlige datasæt (Excel og CSV) ud fra analysens filer. Kør efter analyse2.py."""
import pandas as pd, numpy as np
from openpyxl.utils import get_column_letter

sz = lambda s: f"{int(s)}/{str(int(s) + 1)[2:]}"
LIGA = {'GB1': 'Premier League / First Division', 'GB2': 'Championship / Second Division', 'GB3': 'League One',
        'FR1': 'Ligue 1', 'FR2': 'Ligue 2', 'IT1': 'Serie A', 'ES1': 'LaLiga'}
reg = lambda y: 'Før regler (til 2010)' if y <= 2010 else ('UEFA FFP (2011-12)' if y <= 2012 else 'FFP og PSR (fra 2013)')

o = pd.read_csv('data/overtagelser.csv'); r = pd.read_csv('data/v2_resultater.csv')
p = pd.read_csv('data/v2_panel.csv'); t = pd.read_csv('data/tm_pl_tabeller.csv')
navn = p.drop_duplicates('club_id').set_index('club_id').club

e = pd.DataFrame({'Klub': o.klub, 'Transfermarkt-id': o.club_id, 'Ny ejer': o.ejer, 'Dato for kontrol (år-måned)': o.dato,
                  'Ejerandel': o.andel, 'Ejertype': o.ejertype, 'Amerikansk ejer eller kapitalfond': np.where(o.usa_pe, 'Ja', 'Nej'),
                  'Første sæson med ny ejer': o.t0.map(sz), 'Regelperiode': o.t0.map(reg),
                  'Datering': o.sikkerhed.map({'høj': 'Sikker', 'middel': 'Usikker', 'lav': 'Usikker'}),
                  'Note': o.note.fillna('').str.replace('USA/kapitalfond', '').str.strip(), 'Kilde': o.kilde}).sort_values(['Klub', 'Første sæson med ny ejer'])
f = pd.DataFrame({'Rang': r.rang, 'Klub': r.klub, 'Første sæson med ny ejer': r.t0.map(sz), 'Ny ejer': r.ejer, 'Ejertype': r.ejertype,
                  'Regelperiode': r.t0.map(reg), 'Liga sæsonen før': r.liga_t_1.map(LIGA), 'Niveau før (gns. 3 sæsoner)': r.base.round(1),
                  'Ændring for klubben': r.delta.round(1), 'Ændring for kontrolklubber': r.kontrol_delta.round(1), 'Antal kontrolklubber': r.n_kontrol,
                  'Effekt (point)': r.effekt.round(1), 'Effekt i første sæson (point)': r.foerste_saeson.round(1),
                  'Sæsoner over ligasnit af de første fem': r.saesoner_over_snit, 'PL-placering før (gns. 3 sæsoner)': r.pl_plac_foer.round(1),
                  'PL-placering efter (gns. sæson 2-4)': r.pl_plac_efter.round(1), 'Placebo-andel': r.p_placebo.round(2)})
k = p.sort_values(['league', 'season', 'netto'], ascending=[True, True, False])
g = pd.DataFrame({'Sæson': k.season.map(sz), 'Liga': k.league.map(LIGA), 'Klub': k.club, 'Transfermarkt-id': k.club_id,
                  'Køb (mio. euro)': k.expenditure_m.round(2), 'Antal tilgange': k.arrivals, 'Salg (mio. euro)': k.income_m.round(2),
                  'Antal afgange': k.departures, 'Nettoforbrug (mio. euro)': k.netto.round(2),
                  'Ligaens gns. nettoforbrug (mio. euro)': k.liga_netto_snit.round(2),
                  'Gns. indkøb pr. klub i øverste række (mio. euro)': k.top_koeb_snit.round(2), 'Afvigelse fra ligasnit (point)': k.Y.round(1)})
pl = pd.DataFrame({'Sæson': t.season.map(sz), 'Klub': t.club_id.map(navn), 'Transfermarkt-id': t.club_id, 'Placering': t.placering,
                   'Point': t.point, 'Målforskel': t.maalforskel}).sort_values(['Sæson', 'Placering'])
laes = open('Datasaet/LAES_MIG.txt').read().strip().split('\n')
out = 'Datasaet/Ejerskifter_og_transferforbrug_1987-2026.xlsx'
with pd.ExcelWriter(out, engine='openpyxl') as w:
    pd.DataFrame({'Læs mig': laes}).to_excel(w, sheet_name='Læs mig', index=False)
    for name, df in [('Ejerskifter', e), ('Effekter', f), ('Klub_saeson', g), ('PL_placeringer', pl)]:
        df.to_excel(w, sheet_name=name, index=False)
    wb = w.book; wb.properties.creator = 'Asger Krogh'; wb.properties.lastModifiedBy = 'Asger Krogh'
    for ws in wb.worksheets:
        ws.freeze_panes = 'A2'
        for col in ws.columns:
            L = max(len(str(c.value)) if c.value is not None else 0 for c in col[:200])
            ws.column_dimensions[get_column_letter(col[0].column)].width = min(max(10, L + 2), 160 if ws.title == 'Læs mig' else 70)
for name, df in [('ejerskifter', e), ('effekter', f), ('klub_saeson', g), ('pl_placeringer', pl)]:
    df.to_csv(f'Datasaet/{name}.csv', index=False, encoding='utf-8-sig')
print('ok', len(e), len(f), len(g), len(pl))

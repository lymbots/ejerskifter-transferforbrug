import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import analyse2 as A
C = 'Manchester City 2008'
def S(name, r):
    r = r.dropna(subset=['effekt']).sort_values('effekt', ascending=False).reset_index(drop=True)
    i = r.index[r.label == C]; m, lo, hi = A.boot(r.effekt)
    eng = r[r.liga_t_1.str.startswith('GB')]
    ie = eng.reset_index(drop=True).index[eng.reset_index(drop=True).label == C]
    return dict(variant=name, N=len(r), gns=round(m), ki=f'{lo:.0f} til {hi:.0f}', city=round(r.effekt[i[0]]) if len(i) else None,
                rang=f'{i[0]+1}/{len(r)}' if len(i) else '', rang_england=f'{ie[0]+1}/{len(eng)}' if len(ie) else '',
                stat=round(r[r.ejertype=='Stat'].effekt.mean()), privat=round(r[r.ejertype!='Stat'].effekt.mean()))
base, _ = A.run(); out = [S('Hovedanalyse', base)]
out.append(S('Uden 2026/27', A.run(maxs=2025)[0]))
out.append(S('Kun høj sikkerhed', base[base.sikkerhed=='høj']))
out.append(S('Kun England', base[base.liga_t_1.str.startswith('GB')]))
out.append(S('Kun klubber i øverste række før', base[base.liga_t_1.isin(['GB1','FR1','IT1','ES1'])]))
liga = A.liga
same = [all(A.get(liga, r.club_id, r.t0+k) == r.liga_t_1 for k in [-3,-2,-1,0,1,2] if pd.notna(A.get(liga, r.club_id, r.t0+k))) for r in base.itertuples()]
out.append(S('Uden op-/nedrykning i vinduet', base[same]))
for pre, post, nm in [([-2,-1],[0,1],'Vindue 2+2'), ([-4,-3,-2,-1],[0,1,2,3],'Vindue 4+4')]:
    A.PRE, A.POST = pre, post; out.append(S(nm, A.run()[0]))
A.PRE, A.POST = [-3,-2,-1], [0,1,2]
ev2 = A.ev.copy()
for lab, t0 in [('Everton 2018', 2015), ('Bournemouth 2012', 2011), ('Sunderland 2022', 2020)]:
    ev2.loc[ev2.label==lab, 't0'] = t0
ev2['label'] = ev2.klub + ' ' + ev2.t0.astype(str)
out.append(S('De facto-datoer', A.run(events=ev2)[0]))
ev3 = A.ev.copy(); ev3['t0'] -= 3; ev3['label'] = ev3.label + ' (placebo)'
rp = A.run(maxs=2025, events=ev3)[0]; m, lo, hi = A.boot(rp.effekt)
cp = rp[rp.label.str.startswith(C)].effekt
out.append(dict(variant='Placebo: 3 sæsoner før', N=len(rp), gns=round(m), ki=f'{lo:.0f} til {hi:.0f}', city=round(cp.iloc[0]) if len(cp) else None))
t = pd.DataFrame(out); t.to_csv('data/v2_robusthed.csv', index=False); print(t.to_string(index=False))

# Alle ligaer i samme enhed: gns. indkøb pr. klub i de fem store ligaer (Bundesliga-totaler hentet separat)
d5 = A.d.copy()
l1 = pd.read_csv('data/tm_bundesliga_total_hentet_2026-10-05.csv').set_index('season').L1_expenditure_m
top = d5[d5.league.isin(['GB1', 'FR1', 'IT1', 'ES1'])]
big5 = (top.groupby('season').expenditure_m.sum() + l1) / (top.groupby('season').size() + 18)
d5['Y'] = (d5.netto - d5.liga_netto_snit) / d5.season.map(big5) * 100
A.Y = d5.pivot(index='club_id', columns='season', values='Y')
print(S('Alle ligaer i samme enhed (Big-5)', A.run()[0]))

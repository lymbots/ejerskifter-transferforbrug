"""Version 2 (6/10): mål = nettoforbrug over ligasnittet i pct. af en gennemsnitsklubs indkøb, egen liga."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
RANK = {'GB1': 1, 'GB2': 2, 'GB3': 3, 'FR1': 1, 'FR2': 2, 'IT1': 1, 'ES1': 1}

d = pd.read_csv('data/tm_klub_saeson.csv')
d[['expenditure_m', 'income_m']] = d[['expenditure_m', 'income_m']].fillna(0)
d['niveau'] = d.league.map(RANK)
d = d.sort_values('niveau').drop_duplicates(['club_id', 'season'])  # TM-fejl i gamle sæsoner: højeste række vinder
d['netto'] = d.expenditure_m - d.income_m
g = d.groupby(['league', 'season'])
d['liga_netto_snit'] = g.netto.transform('mean')
d['liga_koeb_snit'] = g.expenditure_m.transform('mean')
TOP = {'GB': 'GB1', 'FR': 'FR1', 'IT': 'IT1', 'ES': 'ES1'}
d['land'] = d.league.str[:2]
topk = d[d.league.isin(TOP.values())].groupby(['land', 'season']).expenditure_m.mean().rename('top_koeb_snit')
d = d.join(topk, on=['land', 'season'])
# Afvigelse fra egen ligas nettosnit, målt i pct. af en gennemsnitsklubs indkøb i landets øverste liga
d['Y'] = (d.netto - d.liga_netto_snit) / d.top_koeb_snit * 100
Y = d.pivot(index='club_id', columns='season', values='Y')
liga = d.pivot(index='club_id', columns='season', values='league')
tab = pd.read_csv('data/tm_pl_tabeller.csv').pivot(index='club_id', columns='season', values='placering')

ev = pd.read_csv('data/overtagelser.csv')
ev['regime'] = pd.cut(ev.t0, [0, 2010, 2012, 3000], labels=['Før regler (–2010)', 'UEFA FFP (2011–12)', 'FFP + PL-regler (2013–)'])
ev['label'] = ev.klub + ' ' + ev.t0.astype(str)
PRE, POST, K = [-3, -2, -1], [0, 1, 2], range(-4, 6)
MAXS = 2026


def get(M, c, s):
    try:
        return M.at[c, s]
    except KeyError:
        return np.nan


def delta(c, t0, maxs):
    pre = [x for x in (get(Y, c, t0 + k) for k in PRE) if pd.notna(x)]
    post = [x for x in (get(Y, c, t0 + k) for k in POST if t0 + k <= maxs) if pd.notna(x)]
    if len(pre) < 2 or len(post) < 2:
        return np.nan, np.nan
    return np.mean(post) - np.mean(pre), np.mean(pre)


def run(maxs=MAXS, events=None):
    events = ev if events is None else events
    rows, paths = [], []
    for e in events.itertuples():
        dt, base = delta(e.club_id, e.t0, maxs)
        if np.isnan(dt):
            continue
        lg = get(liga, e.club_id, e.t0 - 1)
        if pd.isna(lg):
            lg = get(liga, e.club_id, e.t0)
        blocked = set(ev[(ev.t0 >= e.t0 - 3) & (ev.t0 <= e.t0 + 2)].club_id)
        ctrl = [c for c in liga.index[liga.get(e.t0 - 1, pd.Series(dtype=object)) == lg] if c not in blocked]
        cd = {c: delta(c, e.t0, maxs) for c in ctrl}
        cd = {c: v for c, v in cd.items() if not np.isnan(v[0])}
        if not cd:
            continue
        cdel = np.array([v[0] for v in cd.values()])
        y0 = get(Y, e.club_id, e.t0)
        first = y0 - base - np.nanmean([get(Y, c, e.t0) - v[1] for c, v in cd.items()])
        over = [get(Y, e.club_id, e.t0 + k) for k in range(0, 5) if e.t0 + k <= maxs]
        over = [x for x in over if pd.notna(x)]
        pos_pre = [get(tab, e.club_id, e.t0 + k) for k in PRE]
        pos_post = [get(tab, e.club_id, e.t0 + k) for k in [1, 2, 3]]
        rows.append(dict(**{k: v for k, v in e._asdict().items() if k != 'Index'}, liga_t_1=lg, base=base, delta=dt,
                         kontrol_delta=cdel.mean(), n_kontrol=len(cdel), effekt=dt - cdel.mean(), foerste_saeson=first,
                         p_placebo=(np.sum(cdel >= dt) + 1) / (len(cdel) + 1),
                         saesoner_over_snit=f'{sum(x > 0 for x in over)}/{len(over)}',
                         pl_plac_foer=np.nanmean(pos_pre) if any(pd.notna(pos_pre)) else np.nan,
                         pl_plac_efter=np.nanmean(pos_post) if any(pd.notna(pos_post)) else np.nan))
        for k in K:
            s = e.t0 + k
            if s > maxs:
                continue
            yt = get(Y, e.club_id, s)
            yc = [get(Y, c, s) - v[1] for c, v in cd.items()]
            yc = [x for x in yc if pd.notna(x)]
            if pd.notna(yt) and yc:
                paths.append(dict(label=e.label, k=k, sti=(yt - base) - np.mean(yc), raa=yt))
    res = pd.DataFrame(rows).sort_values('effekt', ascending=False).reset_index(drop=True)
    res['rang'] = res.index + 1
    return res, pd.DataFrame(paths)


def boot(x, n=4000):
    x = np.asarray(x)
    m = rng.choice(x, (n, len(x))).mean(1)
    return x.mean(), np.percentile(m, 2.5), np.percentile(m, 97.5)


if __name__ == '__main__':
    import warnings; warnings.filterwarnings('ignore')
    res, paths = run()
    res.to_csv('data/v2_resultater.csv', index=False); paths.to_csv('data/v2_stier.csv', index=False); d.to_csv('data/v2_panel.csv', index=False)
    pd.set_option('display.width', 250)
    print(res[['rang', 'label', 'ejertype', 'regime', 'liga_t_1', 'base', 'effekt', 'foerste_saeson', 'saesoner_over_snit', 'pl_plac_foer', 'pl_plac_efter', 'p_placebo']].round(1).to_string())
    print('\nN', len(res), 'gns', np.round(boot(res.effekt), 1), 'median', round(res.effekt.median(), 1))
    for col in ['ejertype', 'regime']:
        for k, x in res.groupby(col, observed=True):
            print(f'  {k:25s} n={len(x):2d}', np.round(boot(x.effekt), 1))
    u = res[res.ejertype == 'Privat, udenlandsk']
    print('  USA/PE vs anden udl.:', np.round(boot(u[u.usa_pe].effekt), 1), np.round(boot(u[~u.usa_pe].effekt), 1))
    c = d[d.club_id == 281].set_index('season').sort_index()
    print(c.loc[1998:2016, ['league', 'netto', 'liga_netto_snit', 'liga_koeb_snit', 'Y']].round(1).to_string())
    for cid, t0, n in [(583, 2011, 'PSG'), (762, 2021, 'Newcastle'), (281, 2008, 'City'), (631, 2003, 'Chelsea'), (164, 1990, 'Blackburn'), (989, 2022, 'Bournemouth')]:
        x = d[d.club_id == cid].set_index('season').sort_index().loc[t0 - 3:t0 + 4]
        print(n, x[['league', 'netto', 'Y']].round(1).T.to_string())

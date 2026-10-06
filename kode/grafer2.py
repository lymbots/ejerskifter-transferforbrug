"""Grafer v2 (6/10). Kør efter analyse2.py. Nummereret i artiklens rækkefølge."""
import warnings; warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for f in ['fonts/Inter-400.ttf', 'fonts/Inter-600.ttf', 'fonts/Inter-800.ttf']:
    fm.fontManager.addfont(f)
BG, INK, MUTED, GRID, GREY = '#FAF9F6', '#16181D', '#6B6F76', '#E4E2DC', '#BDBAB3'
COL = {'City': '#1F4E79', 'PSG': '#C8553D', 'Newcastle': '#2E7D6B', 'Chelsea': '#D99A2B', 'Blackburn': '#7A5C99'}
TYPE = {'Stat': '#1F4E79', 'Privat, udenlandsk': '#D99A2B', 'Privat, indenlandsk': '#2E7D6B'}
ENHED = 'Pct. af en gennemsnitsklubs indkøb'
KILDE = 'Kilde: Egne beregninger på baggrund af Transfermarkt, dataudtræk 5.–6. oktober 2026.'
mpl.rcParams.update({'font.family': 'Inter', 'font.size': 10.5, 'text.color': INK, 'axes.labelcolor': MUTED,
                     'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.edgecolor': GRID, 'axes.facecolor': BG,
                     'figure.facecolor': BG, 'savefig.facecolor': BG, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.spines.left': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
                     'xtick.major.size': 0, 'ytick.major.size': 0, 'axes.axisbelow': True})
W = 7.28
res = pd.read_csv('data/v2_resultater.csv')
paths = pd.read_csv('data/v2_stier.csv')
panel = pd.read_csv('data/v2_panel.csv')
Y = panel.pivot(index='club_id', columns='season', values='Y')
NET = panel.pivot(index='club_id', columns='season', values='netto')
navn = panel.drop_duplicates('club_id').set_index('club_id').club


def header(fig, nr, titel, under):
    H = fig.get_figheight(); y = lambda i: 1 - i / H; nt = titel.count('\n') + 1
    fig.text(0.035, y(0.12), f'FIGUR {nr}', fontsize=8.5, color=MUTED, weight=600, va='top')
    fig.text(0.035, y(0.30), titel, fontsize=15, weight=800, va='top', linespacing=1.15)
    fig.text(0.035, y(0.36 + 0.27 * nt), under, fontsize=10, color=MUTED, va='top', linespacing=1.35)


def footer(fig, note=''):
    fig.text(0.035, 0.012, (note + '\n' if note else '') + KILDE, fontsize=7.8, color=MUTED, va='bottom', linespacing=1.4)


def save(fig, name):
    fig.savefig(f'grafer/{name}.png', dpi=200, metadata={'Software': None}); plt.close(fig)


KLAB = ['−4', '−3', '−2', '−1', 'Ny ejer', '+1', '+2', '+3', '+4', '+5']

# ---------- Figur 1: event study ----------
fig = plt.figure(figsize=(W, 5.6))
ax = fig.add_axes([0.10, 0.15, 0.71, 0.60])
rng = np.random.default_rng(1)
P = paths.set_index('label')
bs = pd.concat([P.loc[rng.choice(res.label.values, len(res))].groupby('k').sti.mean() for _ in range(2000)], axis=1)
ax.fill_between(bs.index, bs.quantile(.025, axis=1), bs.quantile(.975, axis=1), color=GREY, alpha=.45, lw=0)
m = paths.groupby('k').sti.mean(); ax.plot(m.index, m, color=MUTED, lw=2)
ax.text(5.15, m.iloc[-1] - 45, 'Gennemsnit,\nalle 68', color=MUTED, fontsize=8.5, va='center')
for lab, key, txt in [('Manchester City 2008', 'City', 'Man. City 2008'), ('Chelsea 2003', 'Chelsea', 'Chelsea 2003'),
                      ('Blackburn 1990', 'Blackburn', 'Blackburn 1991')]:
    p = paths[paths.label == lab]; city = key == 'City'
    ax.plot(p.k, p.sti, color=COL[key], lw=3 if city else 1.8, marker='o', ms=4 if city else 3)
    ax.text(p.k.iloc[-1] + 0.15, p.sti.iloc[-1], txt, color=COL[key], fontsize=8.8, va='center', weight=800 if city else 600)
ax.axvline(-0.5, color=INK, lw=.8, ls=(0, (3, 3))); ax.axhline(0, color=INK, lw=.8)
ax.set_xticks(range(-4, 6), KLAB); ax.set_xlim(-4.3, 5.1)
ax.set_xlabel('Sæson i forhold til ejerskiftet (Ny ejer = første sæson med ny ejer)')
ax.set_ylabel('Pct. af gns. klubs indkøb,\nud over kontrolklubberne')
header(fig, 1, 'Rigmandsovertagelserne gav et spring med det samme',
       'Nettotransferforbrug før og efter ejerskiftet, målt mod klubber i samme liga uden ejerskifte.\nGråt bånd: 95 %-interval for gennemsnittet af 68 overtagelser.')
footer(fig, 'Blackburn: Jack Walker overtog i januar 1991, sæson 1990/91.')
save(fig, 'figur1_spring')

# ---------- Figur 2: Citys forløb ----------
yrs = list(range(1998, 2017))
c = Y.loc[281, yrs]
era = ['#BDBAB3' if s < 2007 else ('#D99A2B' if s == 2007 else COL['City']) for s in yrs]
fig = plt.figure(figsize=(W, 5.0))
ax = fig.add_axes([0.11, 0.15, 0.85, 0.58])
ax.bar(yrs, c, color=era, width=0.72)
ax.axhline(0, color=INK, lw=.8)
for s in [2007, 2008, 2009, 2010]:
    ax.text(s, c[s] + 8, f'{NET.at[281, s]:.0f} mio.', ha='center', fontsize=7.6, color=INK)
ax.text(2002, 330, 'Før 2007: under eller\nomkring ligasnittet', fontsize=8.5, color=MUTED)
ax.text(2006.6, 140, 'Shinawatra\n2007', fontsize=8.5, color='#B07A16', ha='right', weight=600)
ax.text(2011.3, 330, 'Sheikh Mansour (ADUG)\nfra 1. september 2008', fontsize=8.5, color=COL['City'], weight=700)
ax.set_xticks(yrs[::2], [f"{y % 100:02d}/{(y + 1) % 100:02d}" for y in yrs[::2]], fontsize=8.5)
ax.set_ylabel('Pct. af gns. klubs indkøb,\nud over ligasnittet')
header(fig, 2, 'City var allerede begyndt at bruge penge, da Mansour kom',
       "Manchester Citys nettotransferforbrug pr. sæson i forhold til gennemsnittet i den liga, City spillede i.\nTal over søjlerne: nettoforbrug i mio. euro.")
footer(fig)
save(fig, 'figur2_city_forloeb')

# ---------- Figur 3: tre statsovertagelser ----------
cases = [(281, 2008, 'City', 'Manchester City', 'sep. 2008. Ingen bindende regler'),
         (583, 2011, 'PSG', 'Paris Saint-Germain', 'jun. 2011. UEFA FFP på vej'),
         (762, 2021, 'Newcastle', 'Newcastle United', 'okt. 2021. PSR + APT fra dec. 2021')]
fig = plt.figure(figsize=(W, 5.6))
ks = list(range(-3, 6))
for i, (cid, t0, key, nm, sub) in enumerate(cases):
    ax = fig.add_axes([0.07 + i * 0.31, 0.20, 0.27, 0.48])
    v = [Y.at[cid, t0 + k] if (t0 + k) in Y.columns and t0 + k <= 2026 else np.nan for k in ks]
    ax.bar(ks, v, color=[GREY if k < 0 else COL[key] for k in ks], width=0.72)
    ax.axhline(0, color=INK, lw=.8); ax.set_ylim(-250, 1500)
    ax.set_xticks([-3, 0, 3, 5], ['−3', 'Ny\nejer', '+3', '+5'], fontsize=8)
    if i: ax.set_yticklabels([])
    ax.set_title(nm, fontsize=10.5, weight=800, color=COL[key], loc='left', pad=18)
    ax.text(0, 1.03, sub, transform=ax.transAxes, fontsize=7.6, color=MUTED)
    e3 = sum(NET.at[cid, t0 + k] for k in range(3))
    ax.text(0.98, 0.93, f'Netto første 3 sæsoner:\n{e3:.0f} mio. euro', transform=ax.transAxes, ha='right', va='top', fontsize=7.8)
fig.text(0.035, 0.065, 'Lodret akse: pct. af en gennemsnitlig klubs indkøb, ud over ligasnittet', fontsize=8.5, color=MUTED)
header(fig, 3, 'Tre statsovertagelser: City og PSG blev ved, Newcastle bremsede',
       'Nettotransferforbrug pr. sæson i forhold til ligasnittet, fra tre sæsoner før til fem efter.\nPSG måles mod Ligue 1, der bruger langt færre penge end Premier League.')
footer(fig)
save(fig, 'figur3_statsovertagelser')

# ---------- Figur 4: effekt over tid ----------
fig = plt.figure(figsize=(W, 5.4))
ax = fig.add_axes([0.09, 0.14, 0.86, 0.60])
ax.axvspan(2010.5, 2012.5, color='#ECEAE4', lw=0); ax.axvspan(2012.5, 2026, color='#E4E1D9', lw=0)
for x, t in [(1991, 'Ingen regler'), (2010.6, 'UEFA FFP'), (2013, 'FFP + Premier Leagues egne regler (PSR)')]:
    ax.text(x, 0.97 if x != 2010.6 else 0.52, t, transform=ax.get_xaxis_transform(), fontsize=8, color=MUTED, va='top' if x != 2010.6 else 'bottom', rotation=0 if x != 2010.6 else 90)
for (a, b), x in zip([(1985, 2010.5), (2010.5, 2012.5), (2012.5, 2026)], [res[res.t0 <= 2010], res[(res.t0 > 2010) & (res.t0 <= 2012)], res[res.t0 > 2012]]):
    ax.plot([a + .3, b - .3], [x.effekt.mean()] * 2, color=INK, lw=1.6)
ax.scatter(res.t0, res.effekt, s=36, color=[TYPE[t] for t in res.ejertype], ec=BG, lw=.6, zorder=3)
lab = {'Manchester City 2008': 'Man. City', 'Paris Saint-Germain 2011': 'PSG', 'Chelsea 2003': 'Chelsea', 'Monaco 2011': 'Monaco',
       'Newcastle 2021': 'Newcastle', 'Blackburn 1990': 'Blackburn', 'Chelsea 2022': 'Chelsea 2022', 'Inter 2024': 'Inter'}
for r in res[res.label.isin(lab)].itertuples():
    ax.annotate(lab[r.label], (r.t0, r.effekt), xytext=(-62, -4) if 'City' in r.label else (6, 4), textcoords='offset points', fontsize=8.3, weight=700 if 'City' in r.label else 400)
ax.axhline(0, color=INK, lw=.8); ax.set_xlim(1989, 2025.5)
ax.set_ylabel('Effekt, ' + ENHED.lower()); ax.set_xlabel('Sæson for ejerskiftet')
for i, (t, cl) in enumerate(TYPE.items()):
    fig.text(0.09 + i * 0.2, 0.765, '— ' + t, color=cl, fontsize=8.5, weight=600)
header(fig, 4, 'Reglerne har klippet toppen af, men ikke flyttet gennemsnittet',
       'Effekten af hver overtagelse på nettotransferforbruget, efter hvornår den skete.\nSort streg: gennemsnittet i hver regelperiode.')
footer(fig)
save(fig, 'figur4_over_tid')

# ---------- Figur 5: ejertype ----------
fig = plt.figure(figsize=(W, 4.6))
ax = fig.add_axes([0.25, 0.17, 0.70, 0.55])
order = ['Stat', 'Privat, udenlandsk', 'Privat, indenlandsk']
rng = np.random.default_rng(3)
for i, g in enumerate(order):
    x = res[res.ejertype == g]; y = i + rng.uniform(-.2, .2, len(x))
    ax.scatter(x.effekt, y, s=34, color=TYPE[g], alpha=.9, ec=BG, lw=.6, zorder=3)
    b = [rng.choice(x.effekt, len(x)).mean() for _ in range(3000)]
    ax.plot(np.percentile(b, [2.5, 97.5]), [i - .34] * 2, color=INK, lw=1.4)
    ax.plot([x.effekt.mean()], [i - .34], marker='|', ms=11, mew=2.2, color=INK)
    for r, yy in zip(x.itertuples(), y):
        if r.label in lab:
            ax.annotate(lab[r.label], (r.effekt, yy), xytext=(6, -12 if 'City' in r.label else 5), textcoords='offset points',
                        fontsize=8.3, weight=700 if 'City' in r.label else 400)
ax.set_yticks(range(3), [f'{g}\n(n = {(res.ejertype == g).sum()})' for g in order], fontsize=9.5, color=INK)
ax.set_ylim(2.5, -.7); ax.axvline(0, color=INK, lw=.8); ax.grid(axis='y', visible=False)
ax.set_xlabel('Effekt, ' + ENHED.lower())
header(fig, 5, 'De tre statsejede overtagelser ligger i toppen',
       'Effekten af 68 overtagelser fordelt på ejertype. Hver prik er én overtagelse.')
footer(fig, 'Sort streg: gennemsnit med 95 %-interval (bootstrap).')
save(fig, 'figur5_ejertype')

# ---------- Figur 6: placering efter overtagelse ----------
t = pd.read_csv('data/tm_pl_tabeller.csv').pivot(index='club_id', columns='season', values='placering')
seas = list(range(1992, 2026))
cases6 = [(281, 2008, 'Manchester City', 'ADUG 2008', COL['City']), (631, 2003, 'Chelsea', 'Abramovitj 2003', COL['Chelsea']),
          (164, 1990, 'Blackburn Rovers', 'Walker 1991', COL['Blackburn']), (762, 2021, 'Newcastle United', 'PIF 2021', COL['Newcastle']),
          (1003, 2010, 'Leicester City', 'King Power 2010', '#8A6D3B'), (405, 2018, 'Aston Villa', 'NSWE 2018', '#8C2F39')]
fig = plt.figure(figsize=(W, 6.3))
for n, (cid, t0, nm, ejer, cl) in enumerate(cases6):
    r, c = divmod(n, 3)
    ax = fig.add_axes([0.07 + c * 0.315, 0.47 - r * 0.36, 0.27, 0.26])
    ax.axhspan(0.5, 4.5, color='#ECEAE4', lw=0)
    v = pd.Series([t.at[cid, s] if (cid in t.index and s in t.columns) else np.nan for s in seas], index=seas)
    ax.plot(v.index, v.values, color=cl, lw=2)
    ax.scatter(v.index, v.values, s=8, color=cl, zorder=3)
    out = v[v.isna()].index
    ax.scatter(out, [23] * len(out), s=6, color=GREY, marker='s')
    if t0 >= 1992:
        ax.axvline(t0, color=INK, lw=.9, ls=(0, (3, 2)))
    ax.set_ylim(24, 0); ax.set_yticks([1, 4, 10, 20, 23], ['1', '4', '10', '20', 'Ikke\ni PL'], fontsize=7.5)
    ax.set_xlim(1991.5, 2025.5); ax.set_xticks([1995, 2005, 2015, 2025], ['95', '05', '15', '25'], fontsize=7.5)
    ax.set_title(nm, fontsize=9.8, weight=800, color=cl, loc='left', pad=14)
    ax.text(0, 1.02, 'Ny ejer: ' + ejer, transform=ax.transAxes, fontsize=7.4, color=MUTED)
    ax.grid(axis='x', visible=False)
header(fig, 6, 'Kun City og Chelsea blev i toppen efter overtagelsen',
       'Slutplacering i Premier League pr. sæson, 1992/93 til 2025/26, for seks overtagne klubber.\nGråt bånd: top 4. Stiplet linje: første sæson med ny ejer.')
footer(fig, 'Blackburn blev overtaget i januar 1991 i den næstbedste række, før Premier League startede.')
save(fig, 'figur6_placering')
print('ok')

# ---------- Figur 7: top 4 og de seks store ----------
from matplotlib.patches import Rectangle as R7
t7 = pd.read_csv('data/tm_pl_tabeller.csv')
BIG6 = {985, 31, 11, 631, 281, 148}
kort = {164: 'Blackburn', 762: 'Newcastle', 399: 'Leeds', 1123: 'Norwich', 405: 'Villa', 703: 'Forest', 29: 'Everton', 1003: 'Leicester'}
fig = plt.figure(figsize=(W, 4.9))
ax = fig.add_axes([0.06, 0.18, 0.90, 0.48])
for s in range(1992, 2026):
    x = t7[(t7.season == s) & (t7.placering <= 4)].sort_values('placering')
    for j, (cid, pl_) in enumerate(zip(x.club_id, x.placering)):
        big = cid in BIG6
        ax.add_patch(R7((s - .42, j - .42), .84, .84, color=GREY if big else '#C8553D', lw=0))
        if not big and s >= 2003:
            ax.text(s, 3.62, kort.get(cid, navn.get(cid, '')), fontsize=7.2, rotation=90, ha='center', va='top', color='#8C2F1D')
ax.axvline(2002.5, color=INK, lw=.9, ls=(0, (3, 2)))
ax.text(1997.3, -0.9, '1992/93–2002/03:\n15 af 44 pladser til andre klubber', ha='center', fontsize=8.5)
ax.text(2014, -0.9, '2003/04–2025/26:\n5 af 92 pladser til andre klubber', ha='center', fontsize=8.5)
ax.set_xlim(1991.4, 2025.6); ax.set_ylim(5.5, -1.9)
ax.set_yticks(range(4), ['1', '2', '3', '4'], fontsize=8.5, color=INK); ax.grid(False)
ax.set_xticks(range(1992, 2026, 3), [f"{y % 100:02d}/{(y + 1) % 100:02d}" for y in range(1992, 2026, 3)], fontsize=8)
ax.set_ylabel('Placering')
fig.add_artist(R7((0.06, 0.725), 0.014, 0.022, transform=fig.transFigure, color=GREY, lw=0)); fig.text(0.08, 0.725, 'De seks klubber, der i dag udgør toppen: Man. United, Liverpool, Arsenal, Chelsea, Man. City, Tottenham', fontsize=8.3, color=MUTED)
fig.add_artist(R7((0.06, 0.692), 0.014, 0.022, transform=fig.transFigure, color='#C8553D', lw=0)); fig.text(0.08, 0.692, 'Andre klubber', fontsize=8.3, color=MUTED)
header(fig, 7, 'Siden 2003 har seks klubber haft 87 af 92 pladser i top 4',
       'Top 4 i Premier League pr. sæson, 1992/93 til 2025/26. Chelsea og City er blandt de seks, fordi de\nkøbte sig ind efter deres ejerskifter i 2003 og 2008.')
footer(fig)
save(fig, 'figur7_top4_lukket')

// Køres i konsollen på en transfermarkt.com-side. Henter "Transfer income and expenditures" pr. liga og sæson.
// Brugt 2026-10-05. Kør igen lige før udgivelse, da klausuler kan hæve gamle tal.
window.tm = [];
window.tmGet = async (lg, slug, s) => {
  const u = `/${slug}/einnahmenausgaben/wettbewerb/${lg}/plus/0?ids=a&sa=&saison_id=${s}&saison_id_bis=${s}&nat=&pos=&altersklasse=&w_s=&leihe=&intern=0`;
  const d = new DOMParser().parseFromString(await fetch(u).then(r => r.text()), 'text/html');
  const rows = [...d.querySelectorAll('table.items tbody tr')];
  rows.forEach(r => { const td = [...r.querySelectorAll('td')]; const a = r.querySelector('td.hauptlink a');
    if (td.length >= 8) tm.push([lg, s, a ? (a.getAttribute('href').match(/verein\/(\d+)/)||[])[1] : '', ...[2,3,4,5,6,7].map(i => td[i].innerText.trim())]); });
  return rows.length;
};
// Ligaer: GB1 premier-league, GB2 championship (1998–2026), FR1 ligue-1, IT1 serie-a, ES1 laliga, DK1 superliga (1998–2026),
// GB3 league-one (2004–2019), FR2 ligue-2 (2006–2014). 1 sek. pause mellem kald.

// Slutplaceringer i Premier League (brugt 2026-10-06), sæson 1992-2025:
window.tab = async (lg, slug, s) => {
  const d = new DOMParser().parseFromString(await fetch(`/${slug}/tabelle/wettbewerb/${lg}/saison_id/${s}`).then(r => r.text()), 'text/html');
  return [...d.querySelectorAll('table.items tbody tr')].map(r => { const td = [...r.querySelectorAll('td')]; const a = r.querySelector('td a[href*="/verein/"]');
    return [lg, s, a ? (a.getAttribute('href').match(/verein\/(\d+)/) || [])[1] : '', td[0].innerText.trim(), td[td.length - 1].innerText.trim(), td[td.length - 2].innerText.trim()]; });
};

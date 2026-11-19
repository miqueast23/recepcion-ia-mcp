// Renderiza los gráficos de overlays.html a PNG transparentes 1920x1080.
// Uso: node render.js <lista.json> <dirSalida>   (lista = [{nombre, hash}])
const path = require('path');
const { chromium } = require(path.join(process.env.APPDATA, 'npm/node_modules/playwright'));
const fs = require('fs');
const [lista, out] = process.argv.slice(2);
(async () => {
  const items = JSON.parse(fs.readFileSync(lista, 'utf8'));
  const b = await chromium.launch({ headless: true });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const url = 'file:///' + path.join(__dirname, 'overlays.html').replace(/\\/g, '/');
  for (const it of items) {
    await p.goto(url + '#' + it.hash);
    await p.reload();
    await p.screenshot({ path: path.join(out, it.nombre + '.png'), omitBackground: true });
  }
  await b.close();
  console.log('png', items.length);
})();

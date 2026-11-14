// Service worker van het UPKeepers-prototype.
// Doel: de app opent ook zonder internet, en op een trage verbinding binnen een paar seconden.
// Afweging (r. 1383 in Probeersels, "startscherm cachen"): online haalt hij altijd eerst de nieuwste versie,
// zodat een push op GitHub meteen zichtbaar is; duurt dat langer dan WACHT ms of is er geen netwerk,
// dan opent de laatst bewaarde versie.
const APP = 'upk-app-v1';
const LOS = 'upk-los-v1';
const WACHT = 2500;
const KERN = ['./', 'index.html', 'app.html', 'dcplayer.js', 'bundel.js', 'versie.json', 'klantreis.html', 'manifest.webmanifest'];
const BUITEN = ['fonts.googleapis.com', 'fonts.gstatic.com', 'images.unsplash.com'];
const MAX_LOS = 80;

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(APP).then((c) => c.addAll(KERN)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== APP && k !== LOS).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// Eigen bestanden: eerst het netwerk (met tijdslimiet), anders de bewaarde versie.
// De sleutel is het adres zonder ?-deel, want app.html laadt bundel.js?<tijd>.
async function eigen(req) {
  const url = new URL(req.url);
  const sleutel = url.origin + url.pathname;
  const cache = await caches.open(APP);
  const netwerk = fetch(req).then((res) => {
    if (res.ok) cache.put(sleutel, res.clone());
    return res;
  });
  netwerk.catch(() => {});
  const bewaard = new Promise((klaar) => setTimeout(async () => klaar(await cache.match(sleutel)), WACHT));
  try {
    const eerste = await Promise.race([netwerk, bewaard]);
    if (eerste) return eerste;
    return await netwerk;
  } catch (err) {
    const oud = await cache.match(sleutel);
    if (oud) return oud;
    if (req.mode === 'navigate') {
      const app = await cache.match(url.origin + url.pathname.replace(/[^/]*$/, '') + 'app.html');
      if (app) return app;
    }
    throw err;
  }
}

// Letters en foto's van buiten: de bewaarde versie meteen, op de achtergrond verversen.
async function buiten(req) {
  const cache = await caches.open(LOS);
  const oud = await cache.match(req);
  const nieuw = fetch(req).then(async (res) => {
    if (res.ok || res.type === 'opaque') {
      await cache.put(req, res.clone());
      const keys = await cache.keys();
      for (let i = 0; i < keys.length - MAX_LOS; i++) await cache.delete(keys[i]);
    }
    return res;
  }).catch(() => oud);
  return oud || nieuw;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === self.location.origin) e.respondWith(eigen(req));
  else if (BUITEN.includes(url.hostname)) e.respondWith(buiten(req));
});

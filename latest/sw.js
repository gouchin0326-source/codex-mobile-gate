const CACHE = "codex-gate-v108-20260904";
const ASSETS = [
  "./index.html",
  "./manifest.webmanifest",
  "./icon.svg",
  "./dashboard.html",
  "./app-launcher.html",
  "./free-info-lab/index.html",
  "./zero-token-army/index.html",
  "./weather-info/index.html",
  "./gate-health/index.html",
  "./codex-usage/index.html",
  "./ai-info/index.html",
  "./quick-notes-board/index.html",
  "./orbit-catcher/index.html",
  "./orbit-catcher-zombie-siege/index.html",
  "./orbit-catcher-zombie-siege/assets/actor-atlas-v11-level7.png",
  "./orbit-catcher-zombie-siege/assets/player-atlas-v15-vanguard.png",
  "./orbit-catcher-zombie-siege/assets/player-atlas-v15-medic.png",
  "./orbit-catcher-zombie-siege/assets/player-atlas-v15-scout.png",
  "./orbit-catcher-zombie-siege/assets/player-atlas-v15-engineer.png",
  "./codex-data-pocket/index.html",
  "./cat-affinity-lane/index.html",
  "./cat-affinity-lane/assets/cat-hero.png",
  "./csd-web-designer-sample/index.html",
  "./csd-designer-showcase/index.html",
  "./csd-designer-showcase/assets/csd-hero.png",
  "./data/codex-data-schema.json",
  "./data/seed-records.json",
  "./data/free-info.json",
  "./data/weather-info.json",
  "./data/gate-health.json",
  "./data/codex-usage-snapshot.json",
  "./data/ai-info.json",
  "./data/zero-token-capabilities.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});

























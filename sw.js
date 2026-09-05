const CACHE = "codex-gate-v113-20260905";
const ASSETS = [
  "./index.html",
  "./manifest.webmanifest",
  "./icon.svg",
  "./latest/dashboard.html",
  "./latest/app-launcher.html",
  "./latest/free-info-lab/index.html",
  "./latest/zero-token-army/index.html",
  "./latest/weather-info/index.html",
  "./latest/gate-health/index.html",
  "./latest/codex-usage/index.html",
  "./latest/ai-info/index.html",
  "./latest/index.html",
  "./latest/external-ai-lane-run-0805/index.html",
  "./latest/projects/external-ai-lane-run-0805/index.html",
  "./latest/quick-notes-board/index.html",
  "./latest/orbit-catcher/index.html",
  "./latest/orbit-catcher-zombie-siege/index.html",
  "./latest/codex-data-pocket/index.html",
  "./latest/cat-affinity-lane/index.html",
  "./latest/cat-affinity-lane/assets/cat-hero.png",
  "./latest/csd-web-designer-sample/index.html",
  "./latest/csd-designer-showcase/index.html",
  "./latest/csd-designer-showcase/assets/csd-hero.png",
  "./latest/data/codex-data-schema.json",
  "./latest/data/seed-records.json",
  "./latest/data/free-info.json",
  "./latest/data/weather-info.json",
  "./latest/data/gate-health.json",
  "./latest/data/codex-usage-snapshot.json",
  "./latest/data/ai-info.json",
  "./latest/data/zero-token-capabilities.json"
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

























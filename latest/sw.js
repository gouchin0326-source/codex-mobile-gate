const CACHE = "codex-gate-v15";
const ASSETS = [
  "./index.html",
  "./manifest.webmanifest",
  "./icon.svg",
  "./dashboard.html",
  "./app-launcher.html",
  "./external-ai-lane-run-0805/index.html",
  "./projects/external-ai-lane-run-0805/index.html",
  "./quick-notes-board/index.html",
  "./orbit-catcher/index.html",
  "./orbit-catcher-zombie-siege/index.html",
  "./codex-data-pocket/index.html",
  "./cat-affinity-lane/index.html",
  "./cat-affinity-lane/assets/cat-hero.png",
  "./csd-web-designer-sample/index.html",
  "./csd-designer-showcase/index.html",
  "./csd-designer-showcase/assets/csd-hero.png",
  "./data/codex-data-schema.json",
  "./data/seed-records.json",
  "./data/csd-lane-trials.json"
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

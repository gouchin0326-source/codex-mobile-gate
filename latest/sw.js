const CACHE = "codex-gate-v47";
const ASSETS = [
  "./index.html",
  "./manifest.webmanifest",
  "./icon.svg",
  "./dashboard.html",
  "./app-launcher.html",
  "./quick-notes-board/index.html",
  "./orbit-catcher/index.html",
  "./orbit-catcher-zombie-siege/index.html",
  "./orbit-catcher-zombie-siege/assets/actor-atlas-v6.png",
  "./codex-data-pocket/index.html",
  "./cat-affinity-lane/index.html",
  "./cat-affinity-lane/assets/cat-hero.png",
  "./csd-web-designer-sample/index.html",
  "./csd-designer-showcase/index.html",
  "./csd-designer-showcase/assets/csd-hero.png",
  "./data/codex-data-schema.json",
  "./data/seed-records.json"
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


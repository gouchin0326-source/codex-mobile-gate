const CACHE = "codex-gate-v7";
const ASSETS = [
  "./index.html",
  "./manifest.webmanifest",
  "./icon.svg",
  "./latest/index.html",
  "./latest/quick-notes-board/index.html",
  "./latest/orbit-catcher/index.html"
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


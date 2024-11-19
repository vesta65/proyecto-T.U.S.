const CACHE_NAME = 'v1_cache';
const urlsToCache = [
  '/',
  '/static/styles.css',
  '/static/scripts.js',
  '/static/icons/icon-192x192.jpg',
  '/static/icons/icon-512x512.jpg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});

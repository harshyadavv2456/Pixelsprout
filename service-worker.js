// Minimal service worker - required for "Add to Home Screen" installability
// on Android/Chrome. Does not cache anything or add offline support (out of
// scope for now) - just satisfies the PWA installability requirement.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {}); // pass-through, no caching

// Carolina's Diary Service Worker
const CACHE_NAME = 'carolinas-diary-v1';
const STATIC_CACHE = 'carolinas-diary-static-v1';
const DYNAMIC_CACHE = 'carolinas-diary-dynamic-v1';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico',
  '/logo192.png',
  '/logo512.png',
];

// Install event - cache static assets

self.addEventListener('install', (event) => {
  console.log('Service Worker: Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
//Loading..
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activating...');
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve cached content
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip external requests
  if (!request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        // Return cached version if available
        if (cachedResponse) {
          console.log('Service Worker: Serving from cache', request.url);
          return cachedResponse;
        }

        // Fetch from network and cache dynamic content
        return fetch(request)
          .then((response) => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response
            const responseToCache = response.clone();

            // Cache dynamic content
            caches.open(DYNAMIC_CACHE)
              .then((cache) => {
                console.log('Service Worker: Caching dynamic content', request.url);
                cache.put(request, responseToCache);
              });

            return response;
          })
          .catch((error) => {
            console.log('Service Worker: Fetch failed, serving offline page', error);

            // Return a custom offline page for navigation requests
            if (request.destination === 'document') {
              return caches.match('/');
            }

            // For other requests, return a simple response
            return new Response('Offline content not available', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
          });
      })
  );
});

// Background sync for saving journal entries when back online
self.addEventListener('sync', (event) => {
  console.log('Service Worker: Background sync triggered', event.tag);

  if (event.tag === 'journal-sync') {
    event.waitUntil(syncJournalEntries());
  }
});

// Sync journal entries from localStorage to server
async function syncJournalEntries() {
  try {
    console.log('Service Worker: Syncing journal entries...');

    // This would typically sync with your backend
    // For now, we'll just log that sync would happen
    const allClients = await self.clients.matchAll();
    allClients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        message: 'Journal entries synced successfully'
      });
    });
  } catch (error) {
    console.error('Service Worker: Sync failed', error);
  }
}

// Push notifications (for future features)
self.addEventListener('push', (event) => {
  console.log('Service Worker: Push message received');

  const options = {
    body: event.data ? event.data.text() : 'New notification from Carolina\'s Diary',
    icon: '/logo192.png',
    badge: '/logo192.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Open App',
        icon: '/logo192.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/logo192.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Carolina\'s Diary', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
  console.log('Service Worker: Notification click received');

  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      self.clients.openWindow('/')
    );
  }
});

console.log('Service Worker: Registered successfully');

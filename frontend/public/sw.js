/* eslint-disable no-console */
// Carolina's Diary Service Worker
const STATIC_CACHE = 'carolinas-diary-static-v1';
const DYNAMIC_CACHE = 'carolinas-diary-dynamic-v1';

// Simple logging function for service worker
function swLog(level, message, data = null) {
  const isDevelopment = true; // Can be set based on environment

  if (isDevelopment) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] SW ${level.toUpperCase()}: ${message}`;

    switch (level) {
      case 'info':
        console.info(logMessage, data || '');
        break;
      case 'warn':
        console.warn(logMessage, data || '');
        break;
      case 'error':
        console.error(logMessage, data || '');
        break;
      default:
        console.log(logMessage, data || '');
    }
  }

  // In production, you could send logs to main thread:
  // self.clients.matchAll().then(clients => {
  //   clients.forEach(client => {
  //     client.postMessage({ type: 'SW_LOG', level, message, data });
  //   });
  // });
}

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

self.addEventListener('install', event => {
  swLog('info', 'Installing...');
  event.waitUntil(
    caches
      .open(STATIC_CACHE)
      .then(cache => {
        swLog('info', 'Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        swLog('info', 'Installation complete');
        return self.skipWaiting();
      })
      .catch(error => {
        swLog('error', 'Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
//Loading..
self.addEventListener('activate', event => {
  swLog('info', 'Activating...');
  event.waitUntil(
    caches
      .keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              swLog('info', 'Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
            return Promise.resolve();
          })
        );
      })
      .then(() => {
        swLog('info', 'Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - serve cached content
self.addEventListener('fetch', event => {
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
    caches.match(request).then(cachedResponse => {
      // Return cached version if available
      if (cachedResponse) {
        swLog('info', 'Serving from cache', request.url);
        return cachedResponse;
      }

      // Fetch from network and cache dynamic content
      return fetch(request)
        .then(response => {
          // Check if valid response
          if (
            !response ||
            response.status !== 200 ||
            response.type !== 'basic'
          ) {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          // Cache dynamic content
          caches.open(DYNAMIC_CACHE).then(cache => {
            swLog('info', 'Caching dynamic content', request.url);
            cache.put(request, responseToCache);
          });

          return response;
        })
        .catch(error => {
          swLog('warn', 'Fetch failed, serving offline page', error);

          // Return a custom offline page for navigation requests
          if (request.destination === 'document') {
            return caches.match('/');
          }

          // For other requests, return a simple response
          return new Response('Offline content not available', {
            status: 503,
            statusText: 'Service Unavailable',
            headers: new Headers({
              'Content-Type': 'text/plain',
            }),
          });
        });
    })
  );
});

// Background sync for saving journal entries when back online
self.addEventListener('sync', event => {
  swLog('info', 'Background sync triggered', event.tag);

  if (event.tag === 'journal-sync') {
    event.waitUntil(syncJournalEntries());
  }
});

// Sync journal entries from localStorage to server
async function syncJournalEntries() {
  try {
    swLog('info', 'Syncing journal entries...');

    // This would typically sync with your backend
    // For now, we'll just log that sync would happen
    const allClients = await self.clients.matchAll();
    allClients.forEach(client => {
      client.postMessage({
        type: 'SYNC_COMPLETE',
        message: 'Journal entries synced successfully',
      });
    });
  } catch (error) {
    swLog('error', 'Sync failed', error);
  }
}

// Push notifications (for future features)
self.addEventListener('push', event => {
  swLog('info', 'Push message received');

  const options = {
    body: event.data
      ? event.data.text()
      : "New notification from Carolina's Diary",
    icon: '/logo192.png',
    badge: '/logo192.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1,
    },
    actions: [
      {
        action: 'explore',
        title: 'Open App',
        icon: '/logo192.png',
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/logo192.png',
      },
    ],
  };

  event.waitUntil(
    self.registration.showNotification("Carolina's Diary", options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  swLog('info', 'Notification click received');

  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(self.clients.openWindow('/'));
  }
});

swLog('info', 'Registered successfully');

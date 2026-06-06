/* ════════════════════════════════════════════
   Service Worker — מערכת ניהול עסק
   גרסה: 2.0
   ════════════════════════════════════════════ */

const CACHE_NAME = 'biz-app-v5';

// קבצים שנשמרים לשימוש אופליין
const LOCAL_ASSETS = [
  './',
  './מחשבון_רווח_עסקי.html',
  './index.html',
  './home.js',
  './calc.js',
  './calendar.js',
  './tasks.js',
  './manifest.json',
  './icon-192.svg',
  './icon-512.svg',
  './icon-maskable.svg',
];

// ── התקנה: שמור את כל הקבצים בקאש ────────────────
self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(LOCAL_ASSETS);
    }).then(function() {
      return self.skipWaiting(); // הפעל מיד ללא המתנה
    })
  );
});

// ── הפעלה: מחק קאש ישן ────────────────────────────
self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames
          .filter(function(name) { return name !== CACHE_NAME; })
          .map(function(name) { return caches.delete(name); })
      );
    }).then(function() {
      return self.clients.claim(); // השתלט על כל הטאבים
    })
  );
});

// ── Fetch: קאש ראשון לקבצים מקומיים, רשת ראשונה לחיצוניים ────
self.addEventListener('fetch', function(e) {
  var url = e.request.url;

  // גופני Google, Chart.js — רשת ראשונה עם fallback לקאש
  if (url.includes('fonts.googleapis.com') ||
      url.includes('fonts.gstatic.com') ||
      url.includes('cdnjs.cloudflare.com')) {
    e.respondWith(
      fetch(e.request)
        .then(function(resp) {
          var clone = resp.clone();
          caches.open(CACHE_NAME).then(function(c) { c.put(e.request, clone); });
          return resp;
        })
        .catch(function() { return caches.match(e.request); })
    );
    return;
  }

  // קבצים מקומיים — קאש ראשון
  e.respondWith(
    caches.match(e.request).then(function(cached) {
      if (cached) return cached;
      return fetch(e.request).then(function(resp) {
        if (resp && resp.status === 200) {
          var clone = resp.clone();
          caches.open(CACHE_NAME).then(function(c) { c.put(e.request, clone); });
        }
        return resp;
      });
    })
  );
});

// ── הודעה לעדכון הקאש ────────────────────────────────
self.addEventListener('message', function(e) {
  if (e.data === 'SKIP_WAITING') self.skipWaiting();
  // Schedule a notification from the main thread
  if (e.data && e.data.type === 'SCHEDULE_NOTIF') {
    var payload = e.data;
    var delay = Math.max(0, payload.triggerMs - Date.now());
    setTimeout(function(){
      self.registration.showNotification(payload.title, {
        body: payload.body || '',
        icon: './icon-192.svg',
        badge: './icon-192.svg',
        tag: payload.tag || 'biz-notif',
        data: { url: payload.url || './' },
        vibrate: [100, 50, 100],
        requireInteraction: false
      });
    }, delay);
  }
});

// ── לחיצה על נוטיפיקציה ──────────────────────────────
self.addEventListener('notificationclick', function(e) {
  e.notification.close();
  var url = (e.notification.data && e.notification.data.url) || './';
  e.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(cls) {
      for (var i = 0; i < cls.length; i++) {
        if (cls[i].url.includes(url) && 'focus' in cls[i]) return cls[i].focus();
      }
      if (clients.openWindow) return clients.openWindow(url);
    })
  );
});

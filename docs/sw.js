/* Part 2 應答練習 — Service Worker
   殼層（HTML/JSON/圖示）用 stale-while-revalidate：離線一定開得起來，有網路時背景更新。
   音檔用 cache-first：檔案內容不會變，抓過就永久沿用，省流量。
   音檔快取由設定頁的「下載全部音檔」預先填滿，這裡只負責讀。 */
var SHELL = 'p2-shell-v3';
var AUDIO = 'p2-audio-v1';
var SHELL_FILES = [
  './', './index.html', './items.json', './manifest.webmanifest',
  './icon-192.png', './icon-512.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(SHELL).then(function (c) {
      // 個別加入：任何一支失敗都不該讓整個安裝失敗
      return Promise.all(SHELL_FILES.map(function (u) {
        return c.add(u).catch(function () {});
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k !== SHELL && k !== AUDIO) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  if (url.pathname.indexOf('/audio/') !== -1) {
    e.respondWith(
      caches.open(AUDIO).then(function (c) {
        return c.match(req).then(function (hit) {
          if (hit) return hit;
          return fetch(req).then(function (res) {
            if (res && res.ok) c.put(req, res.clone());
            return res;
          });
        });
      })
    );
    return;
  }

  e.respondWith(
    caches.open(SHELL).then(function (c) {
      return c.match(req, { ignoreSearch: true }).then(function (hit) {
        var net = fetch(req).then(function (res) {
          if (res && res.ok) c.put(req, res.clone());
          return res;
        }).catch(function () { return hit; });
        return hit || net;
      });
    })
  );
});

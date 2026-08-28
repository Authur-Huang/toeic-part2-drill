/* Part 2 應答練習 — Service Worker
   殼層（HTML/JSON/圖示）用 stale-while-revalidate：離線一定開得起來，有網路時背景更新。
   音檔用 cache-first：檔案內容不會變，抓過就永久沿用，省流量。
   音檔快取由設定頁的「下載全部音檔」預先填滿，這裡只負責讀。 */
var SHELL = 'p2-shell-v5';
// 兩個音檔快取分開，對應設定頁的分包下載。
// ⚠ 這裡的名稱必須與 index.html 的 download() 寫入的名稱一致，
//    否則下載好的檔案 SW 讀不到，離線就會失效。
var AUDIO2 = 'p2-audio-v1';
var AUDIO34 = 'p34-audio-v1';
function audioCacheFor(pathname) {
  return /\/audio34\//.test(pathname) ? AUDIO34 : AUDIO2;
}
var SHELL_FILES = [
  './', './index.html', './items.json', './items34.json', './manifest.webmanifest',
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
        if (k !== SHELL && k !== AUDIO2 && k !== AUDIO34) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET') return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // 同時涵蓋 /audio/（Part 2）與 /audio34/（Part 3、4）
  if (/\/audio(34)?\//.test(url.pathname)) {
    e.respondWith(
      caches.open(audioCacheFor(url.pathname)).then(function (c) {
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

  // 題庫會持續增加題目，不能用「先給快取」——那會讓新題晚一次開啟才出現。
  // 改成先問網路、失敗才回快取：有網路一定是最新，沒網路照樣能練。
  var isData = /items(34)?\.json/.test(url.pathname);

  e.respondWith(
    caches.open(SHELL).then(function (c) {
      if (isData) {
        return fetch(req).then(function (res) {
          if (res && res.ok) c.put(req, res.clone());
          return res;
        }).catch(function () {
          return c.match(req, { ignoreSearch: true });
        });
      }
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

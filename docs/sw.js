/* Part 2 應答練習 — Service Worker
   殼層（HTML/JSON/圖示）用 stale-while-revalidate：離線一定開得起來，有網路時背景更新。
   音檔用 cache-first 且不重驗，抓過就沿用，省流量。
   🔴 代價：音檔內容一改，舊裝置會永遠播舊檔。所以**只要重生過音檔，
      就必須把 AUDIO2／AUDIO34 的版本號加一**，activate 才會清掉舊快取。
      漏了這一步是靜默錯誤：items.json 是 network-first 會更新成新時間軸，
      音檔卻還是舊的，「重聽某一句」會對不準而畫面看不出異常。
   音檔快取由設定頁的「下載全部音檔」預先填滿，這裡只負責讀。 */
var SHELL = 'p2-shell-v16';  // v16：2026-08-30 Part 5 兩百題逐選項解析全部完成
// 兩個音檔快取分開，對應設定頁的分包下載。
// ⚠ 這裡的名稱必須與 index.html 的 download() 寫入的名稱一致，
//    否則下載好的檔案 SW 讀不到，離線就會失效。
// v2：2026-08-29 全量重生音檔（加報題號），必須換名才會重抓。
var AUDIO1 = 'p1-audio-v1';
var AUDIO2 = 'p2-audio-v2';
var AUDIO34 = 'p34-audio-v2';
function audioCacheFor(pathname) {
  if (/\/audio34\//.test(pathname)) return AUDIO34;
  if (/\/audio1\//.test(pathname)) return AUDIO1;
  return AUDIO2;
}
var SHELL_FILES = [
  './', './index.html', './items.json', './items34.json', './itemsR.json',
  './items1.json',
  './manifest.webmanifest',
  './icon-192.png', './icon-512.png'
];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(SHELL).then(function (c) {
      // 個別加入：任何一支失敗都不該讓整個安裝失敗。
      // 🔴 一定要 {cache:'reload'}。c.add() 走的是**瀏覽器自己的 HTTP 快取**，
      //    於是「換了版本號、重新安裝」也可能把**舊檔**存進新版快取 ——
      //    版本明明升了，內容卻沒換，而且不會有任何錯誤訊息。
      //    2026-08-30 實測到：伺服器上的 index.html 已含新函式，
      //    SHELL 升到 v10 重裝後，頁面拿到的仍是舊的。
      return Promise.all(SHELL_FILES.map(function (u) {
        return fetch(u, { cache: 'reload' }).then(function (res) {
          if (res && res.ok) return c.put(u, res);
        }).catch(function () {});
      }));
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k !== SHELL && k !== AUDIO1 && k !== AUDIO2 && k !== AUDIO34)
          return caches.delete(k);
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
  if (/\/audio(34|1)?\//.test(url.pathname)) {
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
  var isData = /items(34|R|1)?\.json/.test(url.pathname);

  e.respondWith(
    caches.open(SHELL).then(function (c) {
      if (isData) {
        // 🔴 這裡一定要 no-store。SW 的 fetch 預設會先問**瀏覽器自己的 HTTP 快取**，
        //    題庫 JSON 沒有帶 Cache-Control，瀏覽器就用啟發式規則自行沿用舊的，
        //    於是「網路優先」實際上拿到的還是舊檔 —— 更新了解析卻怎麼重開都看不到。
        //    2026-08-30 實測到：itemsR.json 已更新，透過 SW 拿到的仍是舊版，
        //    同一支檔案用 {cache:'no-store'} 抓就是新的。
        return fetch(req.url, { cache: 'no-store' }).then(function (res) {
          if (res && res.ok) c.put(req, res.clone());
          return res;
        }).catch(function () {
          return c.match(req, { ignoreSearch: true });
        });
      }
      return c.match(req, { ignoreSearch: true }).then(function (hit) {
        // 背景更新也要跳過 HTTP 快取，否則「背景更新」更新的是同一份舊檔。
        // 用 no-cache 而非 no-store：強制重新驗證，但檔案沒變時仍可回 304，不浪費流量。
        var net = fetch(req.url, { cache: 'no-cache' }).then(function (res) {
          if (res && res.ok) c.put(req, res.clone());
          return res;
        }).catch(function () { return hit; });
        return hit || net;
      });
    })
  );
});

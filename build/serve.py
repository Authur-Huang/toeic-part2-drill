# -*- coding: utf-8 -*-
u"""本機預覽用的靜態伺服器，**支援 HTTP Range 請求**。

🔴 為什麼不能直接用 `python -m http.server`：
   它不支援 Range，任何請求都回 200 加整個檔案。瀏覽器遇到不支援 Range 的音訊來源，
   會把 media.seekable 標成 [0, 0] —— 也就是**不能跳到指定秒數**。
   於是「重聽某個選項」「重聽對話的某一句」「點選項唸出那一句」在本機**全部失效**，
   audio.currentTime 設下去會被讀回 0，而且不會有任何錯誤訊息。
   （2026-08-30 就是在這裡卡了一次，先誤以為是 playRange 寫錯。）

   GitHub Pages 支援 Range，所以線上是好的 —— 這純粹是本機測試環境的坑。

用法：python build/serve.py [port]
"""
import os, sys, re

try:
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
except ImportError:
    raise SystemExit(u"需要 Python 3.7 以上")

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
RANGE_RE = re.compile(r"bytes=(\d*)-(\d*)")


class RangeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        SimpleHTTPRequestHandler.__init__(self, *a, directory=ROOT, **kw)

    def end_headers(self):
        # 開發時不要讓瀏覽器自作主張沿用舊檔，否則改了程式看不到
        self.send_header("Cache-Control", "no-store")
        self.send_header("Accept-Ranges", "bytes")
        SimpleHTTPRequestHandler.end_headers(self)

    def send_head(self):
        rng = self.headers.get("Range")
        if not rng:
            return SimpleHTTPRequestHandler.send_head(self)

        m = RANGE_RE.match(rng.strip())
        path = self.translate_path(self.path)
        if not m or not os.path.isfile(path):
            return SimpleHTTPRequestHandler.send_head(self)

        size = os.path.getsize(path)
        start, end = m.group(1), m.group(2)
        if start == "":                       # bytes=-N：最後 N 個位元組
            length = int(end or 0)
            start = max(0, size - length)
            end = size - 1
        else:
            start = int(start)
            end = int(end) if end else size - 1
        end = min(end, size - 1)
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return None

        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        # copyfile 會讀到底，所以自己只送這一段
        remaining = end - start + 1
        while remaining > 0:
            chunk = f.read(min(65536, remaining))
            if not chunk:
                break
            self.wfile.write(chunk)
            remaining -= len(chunk)
        f.close()
        return None

    def log_message(self, fmt, *args):
        pass                                   # 安靜一點，只有錯誤才值得看


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    srv = ThreadingHTTPServer(("127.0.0.1", port), RangeHandler)
    print(u"預覽：http://localhost:%d/  （支援 Range，音檔可以 seek）" % port)
    srv.serve_forever()


if __name__ == "__main__":
    main()

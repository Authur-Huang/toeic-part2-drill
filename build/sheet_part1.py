# -*- coding: utf-8 -*-
"""把 items1/*.json 的 SVG 排成一張總覽 HTML，再用 headless Chrome 截圖。

存在的理由就是 2026-08-29 那次翻車：24 張圖全部把人畫在梯子旁邊而不是梯子上，
純看程式碼看不出來。**畫完一定要 render 出來看過。**

    python build/sheet_part1.py                 # 全部
    python build/sheet_part1.py p1-025 p1-048   # 只看這個區間

輸出 build/_sheet.html 與 build/_sheet.png（都不進版控）。
"""
import glob, io, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
COLS = 4

CSS = """
body{margin:0;padding:14px;background:#fff;color:#111;
     font:13px/1.45 "Microsoft JhengHei",sans-serif}
.grid{display:grid;grid-template-columns:repeat(%d,1fr);gap:10px}
.cell{border:1px solid #ccc;border-radius:6px;padding:6px}
.cell svg{width:100%%;height:auto;display:block}
.id{font-weight:700;font-size:12px}
.sc{font-size:12px;color:#444;margin-bottom:2px}
.an{font-size:12px;color:#046;margin-top:4px}
""" % COLS


def load(lo=None, hi=None):
    items = []
    for p in sorted(glob.glob(os.path.join(ROOT, "items1", "*.json"))):
        for it in json.load(io.open(p, encoding="utf-8")):
            if lo and it["id"] < lo:
                continue
            if hi and it["id"] > hi:
                continue
            items.append(it)
    return items


def main():
    lo = sys.argv[1] if len(sys.argv) > 1 else None
    hi = sys.argv[2] if len(sys.argv) > 2 else None
    items = load(lo, hi)
    if not items:
        raise SystemExit(u"沒有符合的題目")

    cells = []
    for it in items:
        # 正解在 batch 檔裡一律是 choices[0]（打散是音檔生成時才做的）
        cells.append(u'<div class="cell"><div class="id">{}</div>'
                     u'<div class="sc">{}</div>{}'
                     u'<div class="an">✓ {}</div></div>'.format(
                         it["id"], it["scene"], it["svg"], it["choices"][0]))

    html = (u'<!doctype html><meta charset="utf-8"><style>{}</style>'
            u'<div class="grid">{}</div>'.format(CSS, u"".join(cells)))
    hpath = os.path.join(ROOT, "build", "_sheet.html")
    ppath = os.path.join(ROOT, "build", "_sheet.png")
    io.open(hpath, "w", encoding="utf-8").write(html)

    rows = (len(items) + COLS - 1) // COLS
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--window-size=1280,{}".format(min(30000, 190 + rows * 250)),
                    "--screenshot=" + ppath, "file:///" + hpath.replace("\\", "/")],
                   check=True)
    print(u"{} 題 → {}".format(len(items), ppath))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""把 src/ 的 App 檔案與圖示放進 docs/（GitHub Pages 的發布目錄）。
   音檔與 items.json 由 gen_audio.py 產生，這支不會動它們。"""
import os, shutil, io, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "docs")

FILES = ["index.html", "sw.js", "manifest.webmanifest"]


def make_icon(size, path):
    from PIL import Image, ImageDraw, ImageFont
    bg, fg = (43, 74, 168), (255, 255, 255)
    img = Image.new("RGB", (size, size), bg)
    d = ImageDraw.Draw(img)
    # maskable 圖示會被裁成圓形，重要內容要留在中央 80% 內
    font = None
    for name in ("segoeuib.ttf", "arialbd.ttf", "seguibl.ttf"):
        p = os.path.join("C:/Windows/Fonts", name)
        if os.path.exists(p):
            font = ImageFont.truetype(p, int(size * 0.42))
            break
    if font is None:
        font = ImageFont.load_default()
    text = "P2"
    box = d.textbbox((0, 0), text, font=font)
    d.text(((size - box[2] + box[0]) / 2 - box[0],
            (size - box[3] + box[1]) / 2 - box[1] - size * 0.06), text, font=font, fill=fg)
    # 底下一條線，讓圖示不只是兩個字
    w = int(size * 0.30)
    y = int(size * 0.70)
    d.rounded_rectangle([(size - w) // 2, y, (size + w) // 2, y + max(2, size // 40)],
                        radius=size // 80, fill=(150, 180, 255))
    img.save(path, "PNG", optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in FILES:
        shutil.copy2(os.path.join(SRC, f), os.path.join(OUT, f))
        print(u"複製 {}".format(f))
    for s in (192, 512):
        make_icon(s, os.path.join(OUT, "icon-{}.png".format(s)))
        print(u"產生 icon-{}.png".format(s))
    # 不加這個檔，GitHub Pages 的 Jekyll 會忽略底線開頭的檔案
    io.open(os.path.join(OUT, ".nojekyll"), "w").close()

    items = os.path.join(OUT, "items.json")
    if os.path.exists(items):
        d = json.load(io.open(items, encoding="utf-8"))
        n = len(d["items"])
        missing = [x["id"] for x in d["items"]
                   if not os.path.exists(os.path.join(OUT, "audio", x["id"] + ".mp3"))]
        if missing:
            raise SystemExit(u"缺少音檔：{}".format(missing[:5]))

        # 正解若集中在同一個位置，使用者不用聽也能全對，整套題庫等於作廢。
        # 這件事曾經真的發生過（題庫一律把正解寫在 choices[0]，忘了打散），所以在這裡擋。
        dist = [0, 0, 0]
        for x in d["items"]:
            dist[x["answer"]] += 1
        worst = max(dist) / float(n) if n else 0
        if n >= 30 and worst > 0.5:
            raise SystemExit(
                u"正解分佈失衡：A/B/C = {}，最高佔 {:.0%}。".format(dist, worst)
                + u"請確認 gen_audio.py 的 shuffle_item 有生效。")

        ids = [x["id"] for x in d["items"]]
        if len(set(ids)) != n:
            raise SystemExit(u"題號重複")
        print(u"檢查通過：{} 題，音檔齊全，正解分佈 A/B/C = {}".format(n, dist))
    else:
        print(u"⚠ 還沒有 items.json，請先跑 build/gen_audio.py")


if __name__ == "__main__":
    main()

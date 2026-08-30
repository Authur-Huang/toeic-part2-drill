# -*- coding: utf-8 -*-
u"""把逐選項解析（why）與難度（level）併進 docs/ 的題庫檔。

🔴 這支存在的唯一理由：**不重生音檔也能更新解析。**
   gen_audio*.py 沒有「只更新文字」的模式，重跑一定重新合成 mp3，
   使用者的手機就得再抓一次二十幾 MB。解析與難度是純文字，不該付那個代價。

資料流：
   notes/*.json（人寫的標註，用**題庫原始順序**）
     → 對照 items*/batch*.json 的原始 choices
     → 依「選項文字」對到 docs/*.json 裡**已被打散**的位置
     → 只寫入 why / level 兩個欄位

⚠ 為什麼用「選項文字」對位而不是重算那個雜湊排列：
   四支 gen_*.py 各有自己的打散寫法，在這裡重寫一次等於多一份會走鐘的複本。
   用文字對位則完全不必知道它怎麼打散的，而且對不上時會**當場中止**。

⚠ 執行順序：gen_audio*.py／gen_reading.py **之後**才跑這支。
   那些腳本會重寫 docs/*.json，把 why／level 洗掉；重跑它們就要再跑一次 enrich。
"""
import os, io, json, glob, sys

# Windows 主控台預設是 cp950，印不出 ⚠／★ 這類符號會直接丟 UnicodeEncodeError，
# 讓一支已經成功寫檔的腳本看起來像失敗了。
try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
NOTES = os.path.join(ROOT, "notes")

LEVEL_NAME = {1: u"基礎", 2: u"標準", 3: u"進階"}

# (標註檔, 原始題庫目錄, docs 檔名)
SETS = [
    ("p1.json", "items1", "items1.json"),
    ("p2.json", "items", "items.json"),
    ("p34.json", "items34", "items34.json"),
    ("r.json", "itemsR", "itemsR.json"),
]


def die(msg):
    raise SystemExit(u"[enrich] 中止：" + msg)


def load_src(dirname):
    u"""讀原始題庫，攤平成 (id, qi) -> {choices, answer}。"""
    out = {}
    for path in sorted(glob.glob(os.path.join(ROOT, dirname, "*.json"))):
        for raw in json.load(io.open(path, encoding="utf-8")):
            qs = raw.get("questions")
            if qs is None:                       # Part 1／2／5 是單題
                qs = [{"choices": raw["choices"], "answer": raw["answer"]}]
            for qi, q in enumerate(qs):
                out[(raw["id"], qi)] = {"choices": list(q["choices"]),
                                        "answer": q["answer"]}
    return out


def docs_questions(doc):
    u"""攤平 docs 的題目，回傳 [((id, qi), question_dict)]。"""
    out = []
    for it in doc["items"]:
        qs = it.get("questions")
        if qs is None:
            out.append(((it["id"], 0), it))
        else:
            for qi, q in enumerate(qs):
                out.append(((it["id"], qi), q))
    return out


def apply_one(note_file, src_dir, doc_file):
    npath = os.path.join(NOTES, note_file)
    dpath = os.path.join(DOCS, doc_file)
    if not os.path.exists(npath):
        print(u"  略過 {}（還沒有標註檔）".format(note_file))
        return 0, 0
    if not os.path.exists(dpath):
        die(u"找不到 {}，請先跑對應的 gen_*.py".format(doc_file))

    ann = json.load(io.open(npath, encoding="utf-8"))
    src = load_src(src_dir)
    doc = json.load(io.open(dpath, encoding="utf-8"))

    n_why = n_lv = 0
    for key, q in docs_questions(doc):
        # 標註檔的鍵：單題用 "p2-001"，一篇多題用 "p3-001#1"
        rec = ann.get(u"{}#{}".format(key[0], key[1]))
        if rec is None and key[1] == 0:
            rec = ann.get(key[0])
        if not rec:
            continue
        if key not in src:
            die(u"標註了 {} 但原始題庫沒有這題".format(key))
        s = src[key]

        # 正解必須是同一個字串，否則就是對錯題了
        if s["choices"][s["answer"]] != q["choices"][q["answer"]]:
            die(u"{} 正解對不上：原始「{}」vs docs「{}」".format(
                key, s["choices"][s["answer"]], q["choices"][q["answer"]]))

        if "why" in rec:
            why = rec["why"]
            if len(why) != len(s["choices"]):
                die(u"{} 的 why 有 {} 條，但選項有 {} 個".format(
                    key, len(why), len(s["choices"])))
            if sorted(s["choices"]) != sorted(q["choices"]):
                die(u"{} 的選項文字與 docs 不一致，無法對位".format(key))
            pos = {}
            for i, t in enumerate(q["choices"]):
                pos[t] = i
            out = [None] * len(why)
            for i, t in enumerate(s["choices"]):
                out[pos[t]] = why[i]
            if any(x is None for x in out):
                die(u"{} 有重複的選項文字，對位不唯一".format(key))
            q["why"] = out
            n_why += 1

        if "level" in rec:
            lv = rec["level"]
            if lv not in LEVEL_NAME:
                die(u"{} 的 level={} 不是 1／2／3".format(key, lv))
            q["level"] = lv
            n_lv += 1

    with io.open(dpath, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print(u"  {:<12} 逐選項解析 {:>3} 題、難度 {:>3} 題".format(doc_file, n_why, n_lv))
    return n_why, n_lv


def main():
    if not os.path.isdir(NOTES):
        die(u"找不到 notes/ 目錄")
    print(u"併入逐選項解析與難度（不動音檔）…")
    tw = tl = 0
    for a, b, c in SETS:
        w, l = apply_one(a, b, c)
        tw += w
        tl += l
    print(u"\n合計：逐選項解析 {} 題、難度 {} 題".format(tw, tl))
    if tw or tl:
        print(u"⚠ docs/*.json 已更新。記得把 src/sw.js 的 SHELL 版本加一，"
              u"否則裝置上的舊快取不會換。音檔快取版本**不要動**。")


if __name__ == "__main__":
    main()

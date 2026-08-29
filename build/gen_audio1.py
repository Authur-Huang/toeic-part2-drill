# -*- coding: utf-8 -*-
"""Part 1（照片描述）的音檔生成。

結構跟 Part 2 很像，差別在：
  - 沒有題目句，開頭是旁白報題號與「看題本上的圖」
  - 四句敘述由**同一位**說話者唸完（正式考試就是這樣）
  - 選項不印在題本上，所以 App 端預設不顯示文字

⚠ 報題號那一段刻意不列入 marks —— marks 的四格對應四個選項，
   App 靠索引重聽，多塞一格會讓全部重聽點位移。（跟 Part 2 同一個坑）
"""
import asyncio, glob, hashlib, io, itertools, json, os, re, shutil, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_audio import (FFMPEG, dur, encode, silence, synth_all, VOICES,
                       ROOT, OUT_DIR, NARRATOR)

ITEMS_DIR = os.path.join(ROOT, "items1")
AUDIO_DIR = os.path.join(OUT_DIR, "audio1")

GAP_INTRO = 0.8          # 旁白唸完到第一句敘述
GAP_BETWEEN = 0.45       # 敘述之間

# 四句由同一個人唸，逐題輪替，讓四種口音都會出現
SOLO = ["us-f", "gb-m", "ca-f", "au-m", "us-m", "gb-f", "ca-m", "au-f"]

PERMS4 = list(itertools.permutations(range(4)))


def shuffle_item(it):
    """四個選項打散；正解原本一律在 choices[0]。依題號雜湊，重跑不變動。"""
    perm = PERMS4[int(hashlib.md5(it["id"].encode("utf-8")).hexdigest(), 16) % len(PERMS4)]
    out = dict(it)
    out["choices"] = [it["choices"][p] for p in perm]
    out["answer"] = perm.index(it["answer"])
    old2new = {}
    for new_pos, old_pos in enumerate(perm):
        old2new["ABCD"[old_pos]] = "ABCD"[new_pos]
    out["note"] = re.sub(u"\\(([ABCD])\\)",
                         lambda m: u"({})".format(old2new[m.group(1)]), it.get("note", ""))
    return out


def load_items():
    items, seen = [], set()
    for path in sorted(glob.glob(os.path.join(ITEMS_DIR, "*.json"))):
        for it in json.load(io.open(path, encoding="utf-8")):
            if it["id"] in seen:
                raise SystemExit(u"題號重複：{}".format(it["id"]))
            seen.add(it["id"])
            if len(it["choices"]) != 4:
                raise SystemExit(u"{}：選項不是四個".format(it["id"]))
            if not it.get("svg"):
                raise SystemExit(u"{}：Part 1 一定要有圖".format(it["id"]))
            items.append(shuffle_item(it))
    # 正式考試 Part 1 是第 1-6 題
    for i, it in enumerate(items):
        it["_num"] = 1 + (i % 6)
    return items


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    items = load_items()
    if only:
        items = [i for i in items if i["id"] >= only]
    print(u"題數：{}".format(len(items)))

    os.makedirs(AUDIO_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        jobs, plan = [], []
        for idx, it in enumerate(items):
            vkey = SOLO[idx % len(SOLO)]
            pintro = os.path.join(tmp, u"{}_i.mp3".format(it["id"]))
            jobs.append((u"Number {}. Look at the picture marked number {} in your test book."
                         .format(it["_num"], it["_num"]), NARRATOR, pintro))
            segs = []
            for n, text in enumerate(it["choices"]):
                p = os.path.join(tmp, u"{}_{}.mp3".format(it["id"], n))
                jobs.append((text, VOICES[vkey], p))
                segs.append(p)
            plan.append((it, vkey, pintro, segs))

        print(u"開始合成 {} 段語音…".format(len(jobs)))
        asyncio.run(synth_all(jobs))

        gi = os.path.join(tmp, "gap_i.mp3")
        gb = os.path.join(tmp, "gap_b.mp3")
        silence(GAP_INTRO, gi)
        silence(GAP_BETWEEN, gb)
        di, db = dur(gi), dur(gb)

        out_items, total_bytes = [], 0
        for it, vkey, pintro, segs in plan:
            ei = os.path.join(tmp, u"{}_i_e.mp3".format(it["id"]))
            encode(pintro, ei)
            enc = []
            for n, s in enumerate(segs):
                e = os.path.join(tmp, u"{}_{}_e.mp3".format(it["id"], n))
                encode(s, e)
                enc.append(e)

            seq, marks, acc = [ei], [], dur(ei)
            seq.append(gi); acc += di
            for n, e in enumerate(enc):
                if n:
                    seq.append(gb); acc += db
                d = dur(e)
                marks.append({"start": round(acc, 2), "len": round(d, 2)})
                acc += d
                seq.append(e)

            lst = os.path.join(tmp, u"{}_list.txt".format(it["id"]))
            with io.open(lst, "w", encoding="utf-8") as f:
                for p in seq:
                    f.write(u"file '{}'\n".format(p.replace("\\", "/")))
            merged = os.path.join(AUDIO_DIR, u"{}.mp3".format(it["id"]))
            subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat",
                            "-safe", "0", "-i", lst, "-c", "copy", merged], check=True)

            # concat 的接縫補白會累積，用實際總長等比例校正
            real = dur(merged)
            scale = real / acc if acc else 1.0
            for m in marks:
                m["start"] = round(m["start"] * scale, 2)
                m["len"] = round(m["len"] * scale, 2)

            total_bytes += os.path.getsize(merged)
            out_items.append({
                "id": it["id"], "part": 1, "scene": it["scene"], "svg": it["svg"],
                "choices": it["choices"], "answer": it["answer"], "note": it["note"],
                "voice": vkey, "num": it["_num"],
                "total": round(real, 2), "marks": marks,
            })
            print(u"  {} {:.1f}s {:.0f}KB".format(
                it["id"], real, os.path.getsize(merged) / 1024.0), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out_path = os.path.join(OUT_DIR, "items1.json")
    merged_map = {}
    if only and os.path.exists(out_path):
        for x in json.load(io.open(out_path, encoding="utf-8"))["items"]:
            merged_map[x["id"]] = x
    for x in out_items:
        merged_map[x["id"]] = x
    order = [i["id"] for i in load_items()]
    final = [merged_map[i] for i in order if i in merged_map]

    dist = [0, 0, 0, 0]
    for x in final:
        dist[x["answer"]] += 1
    worst = max(dist) / float(len(final)) if final else 0
    if len(final) >= 16 and worst > 0.45:
        raise SystemExit(u"正解分佈失衡：A/B/C/D = {}，最高佔 {:.0%}".format(dist, worst))

    with io.open(out_path, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "items": final}, f,
                  ensure_ascii=False, separators=(",", ":"))
    print(u"\n本次 {} 題，items1.json 共 {} 題，正解分佈 A/B/C/D = {}，新音檔 {:.1f} MB".format(
        len(out_items), len(final), dist, total_bytes / 1048576.0))


if __name__ == "__main__":
    main()

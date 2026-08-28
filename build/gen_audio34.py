# -*- coding: utf-8 -*-
"""Part 3（對話）與 Part 4（獨白）的音檔生成。

與 Part 2 的差別：
  - 一段對話／獨白後面接三題，題目由旁白唸出（選項不唸，正式考試選項是印的）
  - 逐句標記，讓 App 可以單句重聽
  - 四選一，正解一樣在建置時打散

共用的 TTS／編碼／串接邏輯直接沿用 gen_audio.py，不重寫。
"""
import asyncio, io, json, os, subprocess, sys, tempfile, shutil, glob, hashlib, re, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_audio import (FFMPEG, dur, encode, silence, synth_all, VOICES,
                       ROOT, OUT_DIR)

ITEMS_DIR = os.path.join(ROOT, "items34")
AUDIO_DIR = os.path.join(OUT_DIR, "audio34")

NARRATOR = "en-US-ChristopherNeural"      # 旁白固定一個聲音，跟對話者區隔開
GAP_INTRO = 0.6                            # 旁白開場之後
GAP_LINE = 0.25                            # 對話句之間，短一點才像真的在對話
GAP_BEFORE_Q = 0.9                         # 對話結束到第一題
GAP_Q = 0.6                                # 題目之間

# 每題兩位（或一位）說話者，口音與性別都錯開，貼近實際考試
PAIRS = [("us-f", "gb-m"), ("gb-f", "us-m"), ("ca-f", "au-m"), ("au-f", "ca-m"),
         ("us-m", "ca-f"), ("gb-m", "au-f"), ("ca-m", "us-f"), ("au-m", "gb-f")]
# 正式考試有三人對話。三個人必須是三個不同的聲音，
# 否則第三位會跟第一位共用同一個聲音，聽起來像同一個人自問自答。
TRIPLES = [("us-f", "gb-m", "ca-m"), ("gb-f", "us-m", "au-f"),
           ("ca-f", "au-m", "us-m"), ("au-f", "ca-m", "gb-f")]
SOLO = ["us-m", "gb-f", "ca-m", "au-f", "us-f", "gb-m", "ca-f", "au-m"]

PERMS4 = list(itertools.permutations(range(4)))


def shuffle_q(item_id, qi, q):
    """四個選項打散；正解原本一律在 choices[0]。依題號雜湊，重跑不變動。"""
    key = u"{}#{}".format(item_id, qi).encode("utf-8")
    perm = PERMS4[int(hashlib.md5(key).hexdigest(), 16) % len(PERMS4)]
    out = dict(q)
    out["choices"] = [q["choices"][p] for p in perm]
    out["answer"] = perm.index(q["answer"])
    old2new = {}
    for new_pos, old_pos in enumerate(perm):
        old2new["ABCD"[old_pos]] = "ABCD"[new_pos]
    out["note"] = re.sub(u"\\(([ABCD])\\)",
                         lambda m: u"({})".format(old2new[m.group(1)]), q["note"])
    return out


def load_items():
    items, seen = [], set()
    for path in sorted(glob.glob(os.path.join(ITEMS_DIR, "*.json"))):
        for it in json.load(io.open(path, encoding="utf-8")):
            if it["id"] in seen:
                raise SystemExit(u"題號重複：{}".format(it["id"]))
            seen.add(it["id"])
            assert it["part"] in (3, 4), it["id"]
            assert len(it["questions"]) == 3, it["id"]
            for q in it["questions"]:
                assert len(q["choices"]) == 4, it["id"]
                assert q["answer"] in (0, 1, 2, 3), it["id"]
            out = dict(it)
            out["questions"] = [shuffle_q(it["id"], i, q)
                                for i, q in enumerate(it["questions"])]
            items.append(out)
    return items


def intro_text(it):
    return (u"Listen to the following conversation."
            if it["part"] == 3 else u"Listen to the following talk.")


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    items = load_items()
    if only:
        items = [i for i in items if i["id"] >= only]
    print(u"段數：{}（共 {} 題）".format(len(items), len(items) * 3))

    os.makedirs(AUDIO_DIR, exist_ok=True)
    tmp = tempfile.mkdtemp()
    try:
        jobs, plan = [], []
        for idx, it in enumerate(items):
            if it["part"] == 3:
                ns = len(it.get("speakers") or ["W", "M"])
                vk = list(TRIPLES[idx % len(TRIPLES)] if ns >= 3
                          else PAIRS[idx % len(PAIRS)])
            else:
                vk = [SOLO[idx % len(SOLO)]]
            # 說話者編號不得超出配到的聲音數，否則會悄悄繞回第一個人
            top = max(ln["s"] for ln in it["lines"])
            if top >= len(vk):
                raise SystemExit(u"{}：有 {} 位說話者但只配到 {} 個聲音".format(
                    it["id"], top + 1, len(vk)))
            segs = []

            def add(text, voice, tag):
                p = os.path.join(tmp, u"{}_{}.mp3".format(it["id"], len(segs)))
                jobs.append((text, voice, p))
                segs.append((tag, p))

            add(intro_text(it), NARRATOR, "intro")
            for ln in it["lines"]:
                add(ln["t"], VOICES[vk[ln["s"] % len(vk)]], "line")
            for q in it["questions"]:
                add(q["q"], NARRATOR, "q")
            plan.append((it, vk, segs))

        print(u"開始合成 {} 段語音…".format(len(jobs)))
        asyncio.run(synth_all(jobs))

        gaps = {}
        for name, sec in (("intro", GAP_INTRO), ("line", GAP_LINE),
                          ("beforeq", GAP_BEFORE_Q), ("q", GAP_Q)):
            p = os.path.join(tmp, "gap_" + name + ".mp3")
            silence(sec, p)
            gaps[name] = (p, dur(p))

        out_items, total_bytes = [], 0
        for it, vk, segs in plan:
            enc = []
            for n, (tag, s) in enumerate(segs):
                e = os.path.join(tmp, u"{}_{}_e.mp3".format(it["id"], n))
                encode(s, e)
                enc.append((tag, e))

            seq, marks, acc = [], [], 0.0
            prev = None
            for tag, e in enc:
                if prev is not None:
                    if tag == "line" and prev == "intro":
                        g = gaps["intro"]
                    elif tag == "q" and prev != "q":
                        g = gaps["beforeq"]
                    elif tag == "q":
                        g = gaps["q"]
                    else:
                        g = gaps["line"]
                    seq.append(g[0]); acc += g[1]
                d = dur(e)
                marks.append({"tag": tag, "start": round(acc, 2), "len": round(d, 2)})
                acc += d
                seq.append(e)
                prev = tag

            lst = os.path.join(tmp, u"{}_list.txt".format(it["id"]))
            with io.open(lst, "w", encoding="utf-8") as f:
                for p in seq:
                    f.write(u"file '{}'\n".format(p.replace("\\", "/")))
            merged = os.path.join(AUDIO_DIR, u"{}.mp3".format(it["id"]))
            subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat",
                            "-safe", "0", "-i", lst, "-c", "copy", merged], check=True)

            # concat 的接縫補白會累積，用實際總長等比例校正（與 Part 2 同一個坑）
            real = dur(merged)
            scale = real / acc if acc else 1.0
            for m in marks:
                m["start"] = round(m["start"] * scale, 2)
                m["len"] = round(m["len"] * scale, 2)

            lm = [m for m in marks if m["tag"] == "line"]
            qm = [m for m in marks if m["tag"] == "q"]
            convo = {"start": lm[0]["start"],
                     "len": round(lm[-1]["start"] + lm[-1]["len"] - lm[0]["start"], 2)}

            total_bytes += os.path.getsize(merged)
            out_items.append({
                "id": it["id"], "part": it["part"], "scene": it["scene"],
                "lines": it["lines"], "voices": vk,
                "intro": marks[0], "lineMarks": lm, "convo": convo,
                "questions": [dict(q, mark=qm[i]) for i, q in enumerate(it["questions"])],
                "total": round(real, 2),
            })
            print(u"  {} {:.1f}s {:.0f}KB".format(
                it["id"], real, os.path.getsize(merged) / 1024.0), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    out_path = os.path.join(OUT_DIR, "items34.json")
    merged_map = {}
    if only and os.path.exists(out_path):
        for x in json.load(io.open(out_path, encoding="utf-8"))["items"]:
            merged_map[x["id"]] = x
    for x in out_items:
        merged_map[x["id"]] = x
    order = [i["id"] for i in load_items()]
    final = [merged_map[i] for i in order if i in merged_map]

    with io.open(out_path, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "items": final}, f,
                  ensure_ascii=False, separators=(",", ":"))
    print(u"\n本次 {} 段，items34.json 共 {} 段（{} 題），新音檔 {:.1f} MB".format(
        len(out_items), len(final), len(final) * 3, total_bytes / 1048576.0))


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""把題庫 JSON 合成成每題一支 mp3（題目＋三個選項，中間留白），
   並量出每一段的起始秒數，輸出成 App 用的 items.json。

   音檔全部由 Edge-TTS 合成，沒有任何第三方版權素材。
   口音刻意涵蓋多益實際使用的四種：美 / 英 / 加 / 澳。
"""
import asyncio, io, json, os, subprocess, sys, tempfile, shutil, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS_DIR = os.path.join(ROOT, "items")
OUT_DIR = os.path.join(ROOT, "docs")
AUDIO_DIR = os.path.join(OUT_DIR, "audio")

BIN = (u"C:/Users/USER/AppData/Local/Microsoft/WinGet/Packages/"
       u"yt-dlp.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/"
       u"ffmpeg-N-125365-g9a01c1cb6a-win64-gpl/bin/")
FFMPEG, FFPROBE = BIN + u"ffmpeg.exe", BIN + u"ffprobe.exe"

BITRATE, RATE = "48k", "32000"          # 單聲道語音；跟舊專案同一組參數，實測夠清楚
GAP_AFTER_PROMPT = 0.7                  # 題目唸完到第一個選項的空檔（秒）
GAP_BETWEEN = 0.45                      # 選項之間的空檔（秒）

# 多益實際使用的四種口音。每題兩位說話者：一位問、一位答三個選項。
VOICES = {
    "us-m": "en-US-AndrewNeural",   "us-f": "en-US-AvaNeural",
    "gb-m": "en-GB-RyanNeural",     "gb-f": "en-GB-SoniaNeural",
    "ca-m": "en-CA-LiamNeural",     "ca-f": "en-CA-ClaraNeural",
    "au-m": "en-AU-WilliamMultilingualNeural", "au-f": "en-AU-NatashaNeural",
}
# 問答配對：刻意讓問與答的口音、性別都不同，貼近實際考試
PAIRS = [
    ("us-f", "gb-m"), ("gb-f", "us-m"), ("ca-m", "au-f"), ("au-m", "us-f"),
    ("us-m", "ca-f"), ("gb-m", "au-f"), ("ca-f", "gb-m"), ("au-f", "us-m"),
    ("us-f", "ca-m"), ("gb-f", "au-m"), ("ca-m", "us-f"), ("au-m", "gb-f"),
]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def dur(path):
    r = run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path])
    return float(r.stdout.strip())


# Edge-TTS 每段前後會自己補上約 0.5 秒靜音，不修掉的話選項間隔會變成設定值的三倍多，
# 聽起來比真實考試鬆很多。兩次 areverse 是為了用同一個濾鏡處理尾端。
TRIM = ("silenceremove=start_periods=1:start_silence=0.05:"
        "start_threshold=-45dB:detection=peak,areverse,"
        "silenceremove=start_periods=1:start_silence=0.05:"
        "start_threshold=-45dB:detection=peak,areverse")


def encode(src, dst):
    """切掉頭尾靜音並統一編碼參數，之後才能用 concat -c copy 串接。"""
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src,
                    "-af", TRIM, "-ac", "1", "-ar", RATE, "-b:a", BITRATE, dst],
                   check=True)


def silence(seconds, dst):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "lavfi",
                    "-i", "anullsrc=r={}:cl=mono".format(RATE), "-t", str(seconds),
                    "-b:a", BITRATE, dst], check=True)


async def tts(text, voice, dst):
    import edge_tts
    for attempt in range(4):
        try:
            await edge_tts.Communicate(text, voice).save(dst)
            if os.path.getsize(dst) > 500:
                return
        except Exception as e:
            if attempt == 3:
                raise RuntimeError(u"TTS 失敗：{} / {}".format(voice, text)) from e
        await asyncio.sleep(1.5 * (attempt + 1))
    raise RuntimeError(u"TTS 產出過小：{} / {}".format(voice, text))


async def synth_all(jobs, workers=6):
    """jobs: [(text, voice, path)]。限流是必要的，一次打太多會被伺服器拒絕。"""
    sem = asyncio.Semaphore(workers)
    done = [0]

    async def one(text, voice, path):
        async with sem:
            await tts(text, voice, path)
            done[0] += 1
            if done[0] % 25 == 0:
                print(u"  合成 {}/{}".format(done[0], len(jobs)), flush=True)

    await asyncio.gather(*(one(*j) for j in jobs))


def load_items():
    items, seen = [], set()
    for path in sorted(glob.glob(os.path.join(ITEMS_DIR, "*.json"))):
        for it in json.load(io.open(path, encoding="utf-8")):
            if it["id"] in seen:
                raise SystemExit(u"題號重複：{}".format(it["id"]))
            seen.add(it["id"])
            assert len(it["choices"]) == 3, it["id"]
            assert it["answer"] in (0, 1, 2), it["id"]
            items.append(it)
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
        # 1) 先把所有語音一次合成完，減少來回等待
        jobs, plan = [], []
        for idx, it in enumerate(items):
            ask, ans = PAIRS[idx % len(PAIRS)]
            segs = []
            for n, (text, vkey) in enumerate(
                    [(it["prompt"], ask)] + [(c, ans) for c in it["choices"]]):
                p = os.path.join(tmp, u"{}_{}.mp3".format(it["id"], n))
                jobs.append((text, VOICES[vkey], p))
                segs.append(p)
            plan.append((it, ask, ans, segs))

        print(u"開始合成 {} 段語音…".format(len(jobs)))
        asyncio.run(synth_all(jobs))

        # 2) 統一編碼 → 插入空白 → 串成一支，並記錄每段起點
        gap_a = os.path.join(tmp, "gap_a.mp3")
        gap_b = os.path.join(tmp, "gap_b.mp3")
        silence(GAP_AFTER_PROMPT, gap_a)
        silence(GAP_BETWEEN, gap_b)
        ga, gb = dur(gap_a), dur(gap_b)

        out_items, total_bytes = [], 0
        for it, ask, ans, segs in plan:
            enc = []
            for n, s in enumerate(segs):
                e = os.path.join(tmp, u"{}_{}_e.mp3".format(it["id"], n))
                encode(s, e)
                enc.append(e)

            seq, marks, acc = [], [], 0.0
            for n, e in enumerate(enc):
                if n == 1:
                    seq.append(gap_a); acc += ga
                elif n > 1:
                    seq.append(gap_b); acc += gb
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

            # 每個接縫都會多出一點編碼器補白。用實際總長等比例校正，
            # 否則「重聽某個選項」會愈後面愈歪。（舊專案踩過這個坑）
            real = dur(merged)
            scale = real / acc if acc else 1.0
            for m in marks:
                m["start"] = round(m["start"] * scale, 2)
                m["len"] = round(m["len"] * scale, 2)

            total_bytes += os.path.getsize(merged)
            out_items.append({
                "id": it["id"], "type": it["type"], "prompt": it["prompt"],
                "choices": it["choices"], "answer": it["answer"], "note": it["note"],
                "askVoice": ask, "ansVoice": ans,
                "total": round(real, 2), "marks": marks,
            })
            print(u"  {} {:.1f}s {:.0f}KB".format(
                it["id"], real, os.path.getsize(merged) / 1024.0), flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    with io.open(os.path.join(OUT_DIR, "items.json"), "w", encoding="utf-8") as f:
        json.dump({"version": 1, "items": out_items}, f,
                  ensure_ascii=False, separators=(",", ":"))
    print(u"\n完成：{} 題，音檔共 {:.1f} MB".format(len(out_items), total_bytes / 1048576.0))


if __name__ == "__main__":
    main()

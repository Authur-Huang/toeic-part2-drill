# -*- coding: utf-8 -*-
"""閱讀題庫（Part 5／6／7）→ docs/itemsR.json。

跟聽力題庫最大的差別：**完全不用產音檔**，所以沒有 TTS、沒有 ffmpeg，
跑起來是瞬間的事。純文字也代表題庫可以放大而不影響 repo 體積。

題庫為了好寫，一律把正解放在 choices[0]，打散在這裡做（跟 Part 2／3／4 同一套
做法）。重排依題號雜湊，重跑建置不會改變順序，使用者的作答紀錄才不會對不上。
"""
import glob, hashlib, io, itertools, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ITEMS_DIR = os.path.join(ROOT, "itemsR")
OUT_DIR = os.path.join(ROOT, "docs")

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
                         lambda m: u"({})".format(old2new[m.group(1)]), q.get("note", ""))
    return out


def normalize(it):
    """Part 5 是單題，Part 6／7 是一篇文章配數題。統一成同一個形狀給 App 用。"""
    if "questions" in it:
        return dict(it)
    out = dict(it)
    q = {"q": it["q"], "choices": it["choices"],
         "answer": it["answer"], "note": it.get("note", "")}
    for k in ("q", "choices", "answer", "note"):
        out.pop(k, None)
    out["questions"] = [q]
    return out


def load_items():
    items, seen = [], set()
    for path in sorted(glob.glob(os.path.join(ITEMS_DIR, "*.json"))):
        for raw in json.load(io.open(path, encoding="utf-8")):
            it = normalize(raw)
            if it["id"] in seen:
                raise SystemExit(u"題號重複：{}".format(it["id"]))
            seen.add(it["id"])
            if it["part"] not in (5, 6, 7):
                raise SystemExit(u"{}：part 只能是 5／6／7".format(it["id"]))
            if it["part"] in (6, 7) and not it.get("passage"):
                raise SystemExit(u"{}：Part {} 一定要有 passage".format(it["id"], it["part"]))
            for q in it["questions"]:
                if len(q["choices"]) != 4:
                    raise SystemExit(u"{}：選項不是四個".format(it["id"]))
                if q["answer"] not in (0, 1, 2, 3):
                    raise SystemExit(u"{}：answer 超出範圍".format(it["id"]))
                if len(set(q["choices"])) != 4:
                    raise SystemExit(u"{}：有重複的選項".format(it["id"]))
            out = dict(it)
            out["questions"] = [shuffle_q(it["id"], i, q)
                                for i, q in enumerate(it["questions"])]
            items.append(out)
    return items


def main():
    items = load_items()
    nq = sum(len(x["questions"]) for x in items)

    # 正解若集中在同一個位置，不用讀也能全對，整套題庫等於作廢。
    dist = [0, 0, 0, 0]
    for x in items:
        for q in x["questions"]:
            dist[q["answer"]] += 1
    worst = max(dist) / float(nq) if nq else 0
    if nq >= 40 and worst > 0.4:
        raise SystemExit(u"正解分佈失衡：A/B/C/D = {}，最高佔 {:.0%}".format(dist, worst))

    by_part = {}
    for x in items:
        by_part[x["part"]] = by_part.get(x["part"], 0) + len(x["questions"])

    os.makedirs(OUT_DIR, exist_ok=True)
    with io.open(os.path.join(OUT_DIR, "itemsR.json"), "w", encoding="utf-8") as f:
        json.dump({"version": 1, "items": items}, f,
                  ensure_ascii=False, separators=(",", ":"))

    size = os.path.getsize(os.path.join(OUT_DIR, "itemsR.json"))
    print(u"閱讀題庫：{} 組 {} 題（{}），正解分佈 A/B/C/D = {}，{:.0f} KB".format(
        len(items), nq,
        u"／".join(u"Part {} {} 題".format(p, n) for p, n in sorted(by_part.items())),
        dist, size / 1024.0))


if __name__ == "__main__":
    main()

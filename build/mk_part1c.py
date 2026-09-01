# -*- coding: utf-8 -*-
"""產生 items1/batch03.json（Part 1 第三批，p1-049 ~ p1-072）。

2026-09-01 新增，同 `mk_part1b.py` 的兩條鐵律：
人與物互動時人的座標從物件幾何算出來；每批畫完一定要 render 出來看過
（`python build/sheet_part1.py p1-049 p1-072`）。
"""
import io, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mk_part1 import (GY, PH, THIN, ARM_DOWN, LEG_STAND, LEG_STRIDE, LEG_TOGETHER,
                      arm_to, both_to, box, chair_side, circ, figure, ground, ln,
                      poly, reach, shoulder_of, sit, stand, svg, wall)

ITEMS = []


def add(sid, scene, label, body, choices, note):
    ITEMS.append({"id": sid, "part": 1, "scene": scene, "svg": svg(body, label),
                  "choices": choices, "answer": 0, "note": note})


G = ground()


# ── 這一批新增的共用物件 ────────────────────────────────────────────
def scaffold(x, y, w=132.0, levels=2, h=52.0):
    """鷹架。回傳 (svg, 各層踏板中點)，人要站上去就用它。"""
    o, decks = [], []
    for i in range(levels + 1):
        yy = y - h * i
        o.append(ln(x, yy, x + w, yy, THIN))
        if i:
            decks.append((x + w * 0.5, yy))
    for px in (x, x + w * 0.5, x + w):
        o.append(ln(px, y, px, y - h * levels))
    for i in range(levels):
        o.append(ln(x, y - h * i, x + w * 0.5, y - h * (i + 1), THIN))
    return "".join(o), decks


def bricks(x, y, rows=3, cols=5, bw=24.0, bh=13.0):
    o = []
    for r in range(rows):
        off = (bw * 0.5) if r % 2 else 0.0
        n = cols - 1 if r % 2 else cols
        for c in range(n):
            o.append(box(x + off + c * bw, y - bh * (r + 1), bw - 2, bh - 2))
    return "".join(o)


def barrow(x, y):
    """獨輪車。回傳 (svg, 把手座標)。"""
    handle = (x - 26, y - 40)
    s = "".join([poly([(x, y - 34), (x + 6, y - 8), (x + 54, y - 8), (x + 62, y - 34)]),
                 ln(x, y - 34, x + 62, y - 34, THIN),
                 circ(x + 54, y - 2, 9), ln(x + 6, y - 8, handle[0], handle[1]),
                 ln(x + 20, y - 8, x + 14, y + 2, THIN)])
    return s, handle


def bookshelf(x, y, w=118.0, rows=3, rh=42.0):
    """書架＋直立的書。回傳 (svg, 最上層某本書的座標)。"""
    o = [ln(x, y, x, y - rh * rows), ln(x + w, y, x + w, y - rh * rows)]
    for i in range(rows + 1):
        o.append(ln(x, y - rh * i, x + w, y - rh * i, THIN))
    for i in range(rows):
        for j in range(9):
            bx = x + 8 + j * 12
            o.append(box(bx, y - rh * i - 32, 8, 32))
    return "".join(o), (x + 8 + 4 * 12 + 4, y - rh * rows + 16)


def open_book(x, y, w=68.0):
    """攤開的書。第一版只有一個三角形，render 出來像屋頂；
    改成左右兩頁＋書脊，再加兩條字行才看得出是書。"""
    h = x + w * 0.5
    # ⚠ 一度加了「字行」的細線，1.6px 間距在 320×200 的畫布上會糊成一塊黑。
    #   這個尺寸只畫得下左右兩頁與書脊，不要再加細節。
    return "".join([poly([(x, y), (h, y - 13), (h, y - 3), (x, y + 4)]),
                    poly([(x + w, y), (h, y - 13), (h, y - 3), (x + w, y + 4)]),
                    ln(h, y - 13, h, y - 3, THIN)])


def frame(x, y, w=64.0, h=48.0):
    return "".join([box(x, y, w, h), ln(x + 8, y + h - 12, x + w * 0.45, y + 14, THIN),
                    ln(x + w * 0.45, y + 14, x + w - 8, y + h - 12, THIN)])


def window(x, y, w=88.0, h=72.0, curtain=True):
    o = [box(x, y, w, h), ln(x + w * 0.5, y, x + w * 0.5, y + h, THIN),
         ln(x, y + h * 0.5, x + w, y + h * 0.5, THIN)]
    if curtain:
        o += [poly([(x - 14, y), (x - 8, y + h * 0.5), (x - 14, y + h)], THIN),
              poly([(x + w + 14, y), (x + w + 8, y + h * 0.5), (x + w + 14, y + h)], THIN)]
    return "".join(o)


def stairs(x, y, steps=5, sw=26.0, sh=18.0):
    """樓梯（往右上）。回傳 (svg, 各階踏面中點)。"""
    o, treads = [], []
    px, py = x, y
    for i in range(steps):
        o.append(ln(px, py, px, py - sh))
        o.append(ln(px, py - sh, px + sw, py - sh))
        treads.append((px + sw * 0.5, py - sh))
        px, py = px + sw, py - sh
    o.append(ln(x, y - sh - 34, px, py - 34, THIN))
    o.append(ln(x, y - sh, x, y - sh - 34, THIN))
    o.append(ln(px, py, px, py - 34, THIN))
    return "".join(o), treads


def stove(x, y=124.0, w=104.0):
    """流理台＋兩口鍋。回傳 (svg, 右邊那口鍋的鍋口中心)。"""
    pot = (x + 74, y - 12)
    s = "".join([box(x, y, w, 8), ln(x + 6, y + 8, x + 6, GY), ln(x + w - 6, y + 8, x + w - 6, GY),
                 poly([(x + 16, y - 22), (x + 18, y), (x + 46, y), (x + 48, y - 22)]),
                 ln(x + 14, y - 22, x + 50, y - 22, THIN),
                 poly([(x + 62, y - 22), (x + 64, y), (x + 86, y), (x + 88, y - 22)]),
                 ln(x + 60, y - 22, x + 90, y - 22, THIN)])
    return s, pot


def washer(x, y, w=72.0, h=84.0):
    """滾筒洗衣機。回傳 (svg, 門口中心)。"""
    door = (x + w * 0.5, y + h * 0.55)
    s = "".join([box(x, y, w, h), ln(x, y + 16, x + w, y + 16, THIN),
                 circ(door[0], door[1], 22), circ(door[0], door[1], 15, THIN),
                 circ(x + 12, y + 8, 3, THIN)])
    return s, door


def mailbox(x, y):
    """郵筒。回傳 (svg, 投信口)。"""
    slot = (x + 16, y - 62)
    s = "".join([box(x, y - 58, 32, 58), ln(x, y - 58, x + 32, y - 58, THIN),
                 poly([(x, y - 58), (x + 4, y - 70), (x + 28, y - 70), (x + 32, y - 58)]),
                 ln(x + 6, y - 66, x + 26, y - 66, THIN),
                 ln(x + 16, y, x + 16, y + 0.1, THIN)])
    return s, slot


def seat_row(x, y, n=4, sw=34.0):
    """一排連在一起的候位椅（側視）。

    第一版只畫椅面與一根豎線，render 出來整排像柵欄。改成沿用
    `chair_side` 的比例：椅面、椅背、兩隻腳都要有。
    """
    o = []
    for i in range(n):
        sx = x + i * sw
        o += [ln(sx, y - 26, sx + sw - 6, y - 26),
              ln(sx + sw - 6, y - 26, sx + sw - 6, y - 50),
              ln(sx + 3, y - 26, sx + 3, y),
              ln(sx + sw - 9, y - 26, sx + sw - 9, y)]
    return "".join(o)


def bulletin(x, y, w=110.0, h=66.0):
    """公佈欄＋釘上去的紙。回傳 (svg, 中間那張紙)。"""
    o = [box(x, y, w, h)]
    for i in range(3):
        for j in range(2):
            o.append(box(x + 10 + i * 34, y + 10 + j * 30, 24, 20))
    return "".join(o), (x + 10 + 34 + 12, y + 20)


# ══════════════════════════ p1-049 ~ p1-072 ══════════════════════════

# 49 ─ 建築外的鷹架（無人）
sc, decks = scaffold(96, GY)
add("p1-049", u"工地・搭好的鷹架", "Scaffolding set up beside a building, no workers",
    G + wall(80) + sc,
    ["Scaffolding has been set up beside a building.",
     "Workers are climbing the scaffolding.",
     "The scaffolding is being taken down.",
     "A building is being painted."],
    u"★ 架子搭好、沒有人 → have been V-ed。\n"
    u"★ (C)(D) 的 being V-ed 都要有人正在做；(B) 直接違反「畫面無人」。")

# 50 ─ 工人站在鷹架上（腳從踏板算）
sc2, decks2 = scaffold(96, GY)
dx, dy = decks2[0]
add("p1-050", u"工地・鷹架上的工人", "A worker standing on a scaffold platform",
    G + wall(80) + sc2 + figure(dx, dy, [arm_to(24, -18), ((-11, 14), (-14, 30))],
                                LEG_TOGETHER, 82),
    ["A worker is standing on a platform.",
     "The scaffolding has been left empty.",
     "He's carrying a ladder across the site.",
     "The workers are being lifted by a crane."],
    u"★ **跟 p1-049 成對**：同一組鷹架，差別只在上面有沒有人。\n"
    u"★ 人的位置是從踏板座標算出來的 —— 這種「站在某物上」的圖，"
    u"畫錯就會直接推翻正解。")

# 51 ─ 堆好的磚（無人）
add("p1-051", u"工地・堆好的磚塊", "Bricks stacked on the ground, nobody working",
    G + bricks(112, GY),
    ["Bricks have been stacked on the ground.",
     "A worker is laying bricks.",
     "The bricks are being unloaded from a truck.",
     "A wall is being built."],
    u"★ 疊好、沒人動 → have been stacked。\n"
    u"★ (D) a wall is being built 是很典型的陷阱：磚是蓋牆用的，"
    u"但**畫面沒有人在蓋**，材料在不等於工程進行中。")

# 52 ─ 推獨輪車的工人
bw, bhandle = barrow(178, GY)
add("p1-052", u"工地・推獨輪車", "A worker pushing a wheelbarrow",
    G + bw + both_to(126, GY, bhandle[0], bhandle[1], PH, 6, LEG_STRIDE),
    ["A man is pushing a wheelbarrow.",
     "The wheelbarrow has been left beside a wall.",
     "He's filling a barrow with sand.",
     "Tools are being handed to a coworker."],
    u"★ 雙手在把手上 → pushing。\n"
    u"★ (C) filling 是「裝東西進去」，畫面看不到有人在裝 —— "
    u"有人動作也要挑對動詞。")

# 53 ─ 書架上排好的書（無人）
bs, topbook = bookshelf(100, GY)
add("p1-053", u"圖書館・書架上的書", "Books arranged on shelves in an empty library",
    bs,
    ["Books have been arranged on shelves.",
     "A librarian is shelving books.",
     "Some books are being returned to a cart.",
     "The shelves have been emptied."],
    u"★ 書排好、沒有人 → have been arranged。\n"
    u"★ (D) emptied 與畫面矛盾（架上滿的）—— 完成被動的陷阱常常是狀態寫反。")

# 54 ─ 從書架上取書（手落在某一本書上）
bs2, book2 = bookshelf(120, GY)
add("p1-054", u"圖書館・取書", "A woman taking a book from a shelf",
    bs2 + G + reach(80, GY, book2[0], book2[1] + 26),
    ["A woman is reaching for a book.",
     "She's carrying an armful of books.",
     "The books have all been removed.",
     "A book is being read at a table."],
    u"★ **跟 p1-053 成對**。手伸向書 → reach for。\n"
    u"★ (B) an armful of books（一大疊抱在手上）畫面裡沒有，"
    u"**數量與姿勢對不上一樣是錯**。")

# 55 ─ 桌上攤開的書（無人）
add("p1-055", u"圖書館・桌上攤開的書", "An open book left on a table, no one seated",
    G + box(70, 120, 180, 8) + ln(86, 128, 86, GY) + ln(234, 128, 234, GY)
    + open_book(132, 118) + chair_side(96, GY, 1),
    ["A book has been left open on a table.",
     "Someone is turning the pages of a book.",
     "The table is being cleared.",
     "Students are studying at a desk."],
    u"★ 書攤著、椅子空著 → have been left open。\n"
    u"★ left（leave 的過去分詞）常搭配「東西擺著沒人管」，Part 1 高頻。")

# 56 ─ 飯店櫃檯辦入住（櫃檯兩側各一人）
add("p1-056", u"飯店・櫃檯接待", "A guest being helped at a hotel front desk",
    G + box(112, 122, 96, 8) + ln(120, 130, 120, GY) + ln(200, 130, 200, GY)
    + reach(88, GY, 130, 118) + reach(232, GY, 194, 118),
    ["A guest is being helped at a counter.",
     "The lobby has been left empty.",
     "They're carrying suitcases to a room.",
     "A key is being dropped into a box."],
    u"★ 有人服務另一人 → is being helped（被動進行式，主詞是被服務的人）。\n"
    u"★ (B) empty 與畫面矛盾；(C)(D) 是畫面上沒有的動作。")

# 57 ─ 大廳裡沒人的行李推車
# 🔴 車台、輪子、立柱一定要連在一起 —— 第一版三者各畫各的，render 出來斷成兩截。
add("p1-057", u"飯店・沒人的行李車", "A luggage cart left unattended in a lobby",
    G + box(96, 144, 116, 8)
    + ln(112, 152, 112, 164) + ln(196, 152, 196, 164)
    + circ(112, 170, 8) + circ(196, 170, 8)
    + ln(206, 144, 206, 72) + ln(182, 72, 216, 72)
    + box(112, 108, 40, 36) + box(156, 120, 34, 24),
    ["A cart has been left unattended.",
     "A porter is wheeling luggage away.",
     "Bags are being loaded onto a cart.",
     "The cart is being pushed into an elevator."],
    u"★ 車上有行李但沒有人 → unattended。\n"
    u"★ 這題三個錯的選項都需要一個「人」，**先數畫面裡有幾個人，"
    u"再看選項要求幾個人**，是 Part 1 最省力的解法。")

# 58 ─ 牆上掛好的畫（無人）
add("p1-058", u"室內・牆上的畫", "Framed artwork hanging on a wall, empty room",
    G + ln(6, 44, 314, 44, THIN) + frame(70, 62) + frame(180, 62),
    ["Some artwork has been hung on a wall.",
     "A painting is being taken down.",
     "A man is straightening a picture frame.",
     "The frames have been stacked on the floor."],
    u"★ 掛好、沒人 → have been hung。hang-hung-hung。\n"
    u"★ (D) 說「疊在地上」，但畫在牆上 —— 位置寫錯也是錯。")

# 59 ─ 掛畫（手扶在畫框邊）
add("p1-059", u"室內・正在掛畫", "A man hanging a picture on a wall",
    G + ln(6, 44, 314, 44, THIN) + frame(178, 66)
    + reach(126, GY, 176, 84),
    ["A picture is being hung on a wall.",
     "The picture has been hung crookedly.",
     "He's painting a wall.",
     "A frame is being wrapped in paper."],
    u"★ **跟 p1-058 成對**：同樣一幅畫，有人扶著就是 is being hung。\n"
    u"★ 這一組是全題庫最直接的 have been V-ed ↔ be being V-ed 對照，"
    u"聽不出差別就回頭聽這兩題。")

# 60 ─ 窗簾拉開的窗（無人）
add("p1-060", u"室內・拉開窗簾的窗戶", "A window with curtains pulled back, nobody in the room",
    G + window(116, 56),
    ["The curtains have been pulled back.",
     "A woman is closing the curtains.",
     "The window is being replaced.",
     "Blinds have been lowered over the window."],
    u"★ 窗簾往兩側收、窗面全露 → have been pulled back。\n"
    u"★ (D) blinds（百葉窗）lowered 與畫面矛盾 —— "
    u"Part 1 很愛換一個相近的名詞來測你有沒有真的在看圖。")

# 61 ─ 擦窗戶（手貼在窗面上）
add("p1-061", u"室內・擦窗戶", "A man cleaning a window with a cloth",
    G + window(150, 56, 88, 72, False) + reach(104, GY, 158, 100)
    + box(154, 96, 14, 10, THIN),
    ["A window is being cleaned.",
     "The window has been left open.",
     "He's installing a new window.",
     "Curtains are being hung."],
    u"★ 手貼在窗面上、拿著抹布 → is being cleaned。\n"
    u"★ (C) installing 需要工具與未完成的窗框，畫面沒有。")

# 62 ─ 空的樓梯（無人）
st, treads = stairs(88, GY)
add("p1-062", u"室內・空的樓梯", "An empty staircase with a handrail",
    G + st,
    ["A handrail runs alongside the steps.",
     "People are walking up the stairs.",
     "The stairway is being repaired.",
     "A man is holding onto a railing."],
    u"★ 無人畫面又一種正解寫法：**描述東西的相對位置**"
    u"（alongside 沿著）。\n"
    u"★ 三個錯的都要有人。")

# 63 ─ 上樓梯（腳踩在踏面上）
st2, treads2 = stairs(88, GY)
tx, ty = treads2[2]
add("p1-063", u"室內・上樓梯的人", "A woman walking up a staircase",
    G + st2 + figure(tx, ty, [arm_to(20, -14), ((-11, 14), (-14, 30))], LEG_STRIDE, 84),
    ["A woman is climbing a staircase.",
     "She's leaning against a railing.",
     "The stairs have been blocked off.",
     "She's carrying a box down the steps."],
    u"★ **跟 p1-062 成對**。人的腳踩在第三階上（座標從踏面算）。\n"
    u"★ (D) 方向相反（down）也是常見陷阱：**up／down 一定要聽清楚**。")

# 64 ─ 爐台上的鍋（無人）
sv, potc = stove(108)
add("p1-064", u"廚房・爐台上的鍋子", "Pots on a stove in an empty kitchen",
    G + sv,
    ["Some pots have been placed on a stove.",
     "A cook is stirring a pot.",
     "The pots are being washed in a sink.",
     "Food is being served onto plates."],
    u"★ 鍋子擺著、沒人 → have been placed。\n"
    u"★ 廚房場景的三個錯選項都預設「有廚師」，畫面沒有人就全刪。")

# 65 ─ 攪拌鍋子（手落在鍋口）
sv2, potc2 = stove(140)
add("p1-065", u"廚房・攪拌鍋子", "A cook stirring a pot on a stove",
    G + sv2 + reach(94, GY, potc2[0], potc2[1])
    + ln(potc2[0], potc2[1], potc2[0] + 10, potc2[1] - 16, THIN),
    ["A man is stirring a pot.",
     "The stove has been turned off.",
     "He's washing dishes at a sink.",
     "A meal is being served to customers."],
    u"★ **跟 p1-064 成對**。手伸到鍋口、握著長柄 → stirring。\n"
    u"★ (B) turned off 看不出來 —— **看不出來的就不能選**，"
    u"Part 1 只描述「畫面上看得見」的事。")

# 66 ─ 把衣物放進洗衣機（手伸到門口）
ws, door = washer(168, 92)
add("p1-066", u"洗衣間・放衣物進洗衣機", "Clothes being loaded into a washing machine",
    G + ws + reach(112, GY, door[0] - 20, door[1]),
    ["Clothing is being loaded into a machine.",
     "The machine door has been left open.",
     "She's folding laundry on a table.",
     "The laundry has been hung out to dry."],
    u"★ 有人正在放 → 被動進行式。load A into B。\n"
    u"★ (D) hung out to dry 是另一張圖的正解（p1-015 晾衣服），"
    u"**同一個主題不同動作，靠畫面分辨**。")

# 67 ─ 投信（手伸到投信口）
mb, slot = mailbox(206, GY)
add("p1-067", u"街道・投信", "A woman dropping a letter into a mailbox",
    G + mb + reach(150, GY, slot[0] - 14, slot[1] + 6) + box(184, slot[1] + 2, 14, 9, THIN),
    ["A letter is being dropped into a mailbox.",
     "The mailbox has been emptied.",
     "She's opening an envelope.",
     "Mail has been left on a doorstep."],
    u"★ 手伸向投信口、手上有信 → is being dropped into。\n"
    u"★ (B)(D) 都是 have been V-ed，但**畫面裡有人正在動作**，"
    u"這種時候完成被動幾乎不會是正解。")

# 68 ─ 排隊的人（三人一列）
add("p1-068", u"室內・排隊等候", "Three people standing in a line",
    G + stand(108, GY) + stand(156, GY) + stand(204, GY) + ln(6, 166, 314, 166, THIN),
    ["Some people are standing in a line.",
     "They're seated in a waiting area.",
     "The line has been cleared.",
     "They're boarding a bus."],
    u"★ 三個人站成一排 → standing in a line／waiting in line。\n"
    u"★ (B) seated 與站著矛盾（跟 p1-032 是同一種站坐陷阱）。")

# 69 ─ 空的候位排椅（無人，跟 p1-068 對）
add("p1-069", u"室內・空的候位椅", "Rows of empty seats in a waiting area",
    G + seat_row(74, GY, 5),
    ["The seats are unoccupied.",
     "People are waiting to be called.",
     "The chairs are being rearranged.",
     "Someone is sitting near a window."],
    u"★ unoccupied＝沒人坐，無人畫面的固定用字。\n"
    u"★ **跟 p1-068 成對**：一樣的等候區，有人 vs 沒人。")

# 70 ─ 抱著文件夾走路的人
add("p1-070", u"辦公室・抱著文件走路", "A man walking while carrying a folder",
    G + figure(160, GY, [arm_to(26, 6), arm_to(26, 16, -1)], LEG_STRIDE)
    + box(186, 128, 26, 20),
    ["A man is carrying a folder.",
     "He's setting a folder on a desk.",
     "Documents have been spread across a table.",
     "He's shaking hands with a colleague."],
    u"★ 東西在手上、人在走 → carrying。\n"
    u"★ (B) setting…on a desk 需要一張桌子，畫面沒有 —— "
    u"**選項提到畫面上沒有的東西就是錯**。")

# 71 ─ 公佈欄上釘著紙（無人）
bl, mid = bulletin(104, 60)
add("p1-071", u"走廊・公佈欄", "Notices posted on a bulletin board, nobody nearby",
    G + bl,
    ["Notices have been posted on a board.",
     "A woman is removing a flyer.",
     "Announcements are being made over a speaker.",
     "The board has been left blank."],
    u"★ 紙釘上去了、沒人 → have been posted。post 張貼。\n"
    u"★ (D) blank 與畫面矛盾。")

# 72 ─ 在公佈欄前看（手指著其中一張）
bl2, mid2 = bulletin(126, 60)
add("p1-072", u"走廊・看公佈欄的人", "A man looking at a bulletin board",
    G + bl2 + reach(90, GY, mid2[0] - 6, mid2[1] + 8),
    ["A man is pointing at a notice.",
     "He's taking down a bulletin board.",
     "The notices have all been removed.",
     "He's writing on a sheet of paper."],
    u"★ **跟 p1-071 成對**。手指向其中一張紙 → pointing at。\n"
    u"★ (C) removed 與畫面矛盾（紙還在）。")


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "items1", "batch03.json")
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(ITEMS, f, ensure_ascii=False, indent=1)
    sizes = [len(x["svg"]) for x in ITEMS]
    print(u"寫出 {} 題，SVG 平均 {:.0f} 位元組，合計 {:.1f} KB".format(
        len(ITEMS), sum(sizes) / float(len(sizes)), sum(sizes) / 1024.0))
    bad = [x["id"] for x in ITEMS if len(set(x["choices"])) != 4]
    print(u"選項檢查：" + (u"通過" if not bad else u"有問題 {}".format(bad)))

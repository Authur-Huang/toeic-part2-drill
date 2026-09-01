# -*- coding: utf-8 -*-
"""產生 items1/batch02.json（Part 1 第二批，p1-025 ~ p1-048）。

2026-09-01 新增。使用者把每日題數拉高 50% 之後，Part 1 只有 24 題會在第 1 週
就被轉三輪（一週約 71 題次），等於在背位置而不是在練文法反射 —— 故擴充到 96 題。

畫法沿用 `mk_part1.py` 的兩條鐵律，不要自己另發明一套：
  1. **人與物互動時，人的座標一律從物件幾何算出來**（reach／both_to 吃絕對座標）。
  2. **每批畫完都要 render 出來親眼看過**：`python build/sheet_part1.py p1-025 p1-048`。

定位同樣是**文法反射訓練，不是 Part 1 模擬**：
  做得到 is V-ing／is being V-ed／have been V-ed 的分辨、位置介系詞、畫面裡有沒有人。
  做不到 leaning／kneeling 這類細緻姿態與真實照片的曖昧地帶。
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
def copier(x, y, w=64.0, h=76.0):
    """影印機。回傳 (svg, 面板中心)，人要按就用面板中心。"""
    panel = (x + w - 12, y + 14)
    s = "".join([box(x, y, w, h), ln(x, y + 22, x + w, y + 22, THIN),
                 box(x - 16, y + 40, 18, 10), circ(panel[0], panel[1], 4, THIN)])
    return s, panel


def board(x, y, w=118.0, h=68.0):
    """白板／看板。回傳 (svg, 書寫點)。"""
    return box(x, y, w, h), (x + w - 26, y + h - 24)


def counter(x, y=132.0, w=180.0):
    return "".join([box(x, y, w, 8), ln(x + 8, y + 8, x + 8, GY),
                    ln(x + w - 8, y + 8, x + w - 8, GY)])


def cup(x, y, w=14.0, h=16.0):
    """馬克杯：杯身＋把手。y 是杯口。

    把手一度畫成一個完整的圓，render 出來像杯子旁邊浮著一顆球；
    改成三點勾狀線才看得出是把手。
    """
    return "".join([poly([(x, y), (x + 1.5, y + h), (x + w - 1.5, y + h), (x + w, y)]),
                    poly([(x + w, y + 3), (x + w + 6, y + h * 0.5), (x + w, y + h - 3)], THIN)])


def pitcher(x, y, w=22.0, h=26.0):
    """有壺嘴與把手的水壺。回傳 (svg, 壺嘴口座標)。"""
    spout = (x + w + 6, y + 5)
    s = "".join([poly([(x, y), (x + 2, y + h), (x + w - 2, y + h), (x + w, y)]),
                 ln(x, y, x + w, y, THIN),
                 poly([(x + w, y + 1), spout, (x + w, y + 11)], THIN),
                 poly([(x, y + 4), (x - 7, y + h * 0.5), (x, y + h - 6)], THIN)])
    return s, spout


def plate(x, y, r=11.0):
    return circ(x, y, r, THIN) + circ(x, y, r * 0.45, THIN)


def shopcart(x, y):
    """購物車（側視）。回傳 (svg, 把手座標)。"""
    handle = (x - 14, y - 26)
    s = "".join([poly([(x, y - 24), (x + 6, y), (x + 60, y), (x + 66, y - 24)]),
                 ln(x, y - 24, x + 66, y - 24, THIN),
                 circ(x + 12, y + 10, 7), circ(x + 54, y + 10, 7),
                 ln(x, y - 24, handle[0], handle[1])])
    return s, handle


def suitcase(x, y, w=30.0, h=42.0):
    """行李箱（立著）。y 是底部。"""
    return "".join([box(x, y - h, w, h), ln(x, y - h + 12, x + w, y - h + 12, THIN),
                    poly([(x + 8, y - h), (x + 8, y - h - 12), (x + w - 8, y - h - 12),
                          (x + w - 8, y - h)]),
                    circ(x + 5, y + 4, 4, THIN), circ(x + w - 5, y + 4, 4, THIN)])


def bench(x, y, w=90.0):
    return "".join([ln(x, y - 30, x + w, y - 30), ln(x, y - 44, x + w, y - 44, THIN),
                    ln(x + 6, y - 30, x + 6, y), ln(x + w - 6, y - 30, x + w - 6, y),
                    ln(x + 6, y - 44, x + 6, y - 30), ln(x + w - 6, y - 44, x + w - 6, y - 30)])


def tree(x, y):
    """樹。回傳 (svg, 樹冠左緣)——修剪的人要伸到那裡。

    第一版是「一個圓＋兩條斜線」，render 出來像放大鏡或時鐘指針，
    完全不像樹。改成三顆交疊的圓當樹冠，樹幹拉長。
    """
    s = "".join([ln(x, y, x, y - 46),
                 circ(x, y - 74, 26), circ(x - 23, y - 60, 17), circ(x + 23, y - 60, 17)])
    return s, (x - 34, y - 62)


def bin_(x, y, w=28.0, h=38.0):
    return "".join([poly([(x + 3, y - h), (x + 6, y), (x + w - 6, y), (x + w - 3, y - h)]),
                    ln(x, y - h, x + w, y - h, THIN)])


def train(x, y, w=210.0, h=54.0):
    """側面車廂。y 是車底。"""
    o = [box(x, y - h, w, h)]
    for i in range(4):
        o.append(box(x + 16 + i * 48, y - h + 12, 30, 20))
    o += [circ(x + 34, y + 8, 8), circ(x + w - 34, y + 8, 8)]
    return "".join(o)


def pump(x, y=92.0):
    """加油機。回傳 (svg, 油槍口)。"""
    return box(x, y, 34, 78), (x, y + 18)


# ══════════════════════════ p1-025 ~ p1-048 ══════════════════════════

# 25 ─ 影印機前操作的人（手按在面板上）
cp, panel = copier(178, 100)
add("p1-025", u"辦公室・使用影印機", "A man operating a copy machine",
    G + cp + reach(120, GY, panel[0] - 6, panel[1]),
    ["A man is operating a copy machine.",
     "The copier has been unplugged.",
     "Papers are scattered on the floor.",
     "He's repairing a printer."],
    u"★ 有人、手在機器上 → 進行式 is operating。\n"
    u"★ (D) repairing 與 operating 都是「有人在動它」，差別在**做什麼**——"
    u"畫面看不出在修，就不能選 repair。")

# 26 ─ 沒人的影印機，紙留在出紙匣（跟 p1-025 成對）
cp2, _ = copier(140, 100)
add("p1-026", u"辦公室・沒人的影印機", "A copy machine with documents left in the tray",
    G + cp2 + ln(124, 136, 142, 136, THIN) + ln(124, 130, 142, 130, THIN),
    ["Some documents have been left in a tray.",
     "A woman is making copies.",
     "The machine is being repaired.",
     "Papers are being fed into a printer."],
    u"★ **跟 p1-025 是刻意做的一對**：同一台影印機，差別只在有沒有人。\n"
    u"★ 無人 → 只能用 have been V-ed 描述結果狀態；(C)(D) 的 being V-ed 都需要動作者。")

# 27 ─ 在白板前寫字（筆尖落在板面）
bd, tip = board(150, 54)
add("p1-027", u"會議室・在白板前寫字", "A woman writing on a whiteboard",
    G + bd + ln(160, 78, 214, 78, THIN) + ln(160, 94, 196, 94, THIN)
    + reach(112, GY, tip[0], tip[1]),
    ["A woman is writing on a board.",
     "The board has been wiped clean.",
     "She's hanging a poster on the wall.",
     "Notes are being handed out."],
    u"★ 板上已有字、手還在板面 → is writing。\n"
    u"★ (B) wiped clean 說「已擦乾淨」，但板上有字 —— 完成被動的陷阱多半是**狀態寫反**。")

# 28 ─ 空白板（無人，跟 p1-027 成對）
bd2, _ = board(101, 54)
add("p1-028", u"會議室・擦乾淨的白板", "An empty whiteboard in a room with no people",
    G + bd2 + ln(112, 130, 208, 130, THIN),
    ["A board has been wiped clean.",
     "Someone is erasing a whiteboard.",
     "A presentation is being given.",
     "People are taking notes."],
    u"★ 板面全空、沒有人 → have been V-ed。\n"
    u"★ 這題四個選項的動詞都跟白板有關，**能刪的依據只有「畫面裡有沒有人」**。")

# 29 ─ 櫃檯上排好的杯子（無人）
b = [counter(70)]
for i in range(5):
    b.append(cup(84 + i * 32, 110))
add("p1-029", u"咖啡店・櫃檯上的杯子", "Cups lined up on a counter, nobody behind it",
    G + "".join(b),
    ["Some cups have been lined up on a counter.",
     "A server is pouring coffee.",
     "The cups are being washed.",
     "Customers are waiting in line."],
    u"★ 排好、沒人動 → have been lined up。line up 排成一列。\n"
    u"★ 只要畫面無人，server／customers 開頭的選項一律先刪。")

# 30 ─ 倒飲料的服務生（壺口對著杯子）
pit, spout = pitcher(122, 84)
b = [counter(96, 132, 150), cup(160, 116), cup(196, 116), pit,
     ln(spout[0], spout[1] + 2, 166, 114, THIN)]
add("p1-030", u"咖啡店・倒飲料", "A server pouring a drink into a cup",
    G + "".join(b) + reach(76, GY, 118, 92),
    ["A beverage is being poured.",
     "The cups have all been put away.",
     "She's wiping down a counter.",
     "A customer is paying for a drink."],
    u"★ **這題就是 is being V-ed 的標準情境**：有人正在對物做這件事，"
    u"焦點放在物（飲料）就用被動進行式。\n"
    u"★ 跟 p1-029 對照：同一個櫃檯，有人動作才輪得到 being V-ed。")

# 31 ─ 擺好餐具的桌子（無人）
b = [box(60, 122, 200, 8), ln(76, 130, 76, GY), ln(244, 130, 244, GY),
     plate(104, 118), plate(160, 118), plate(216, 118),
     ln(88, 112, 88, 124, THIN), ln(120, 112, 120, 124, THIN),
     ln(144, 112, 144, 124, THIN), ln(176, 112, 176, 124, THIN)]
add("p1-031", u"餐廳・擺好的餐桌", "A table set with plates, no diners",
    G + "".join(b),
    ["A table has been set for a meal.",
     "Diners are being served.",
     "A waiter is clearing the plates.",
     "The plates have been stacked in a pile."],
    u"★ set the table 是「擺餐具」的固定用法，考過很多次。\n"
    u"★ (D) stacked in a pile（疊成一疊）與畫面「分開擺好」矛盾。")

# 32 ─ 兩人隔桌對坐
b = [box(112, 118, 96, 8), ln(124, 126, 124, GY), ln(196, 126, 196, GY)]
s1, h1, _ = sit(96, GY, PH, -1)
s2, h2, _ = sit(224, GY, PH, 1)
add("p1-032", u"餐廳・隔桌對坐的兩人", "Two people seated across from each other at a table",
    G + "".join(b) + s1 + s2 + chair_side(56, GY, -1) + chair_side(238, GY, 1),
    ["They're seated across from each other.",
     "They're standing near a doorway.",
     "One of them is serving food.",
     "The chairs have been pushed under the table."],
    u"★ 兩人 → They're。across from each other 面對面。\n"
    u"★ 跟 p1-008（兩人站著握手）刻意對照：**站與坐是 Part 1 最常互換的一組陷阱**。")

# 33 ─ 推購物車的人
sc, handle = shopcart(178, 152)
add("p1-033", u"超市・推購物車", "A shopper pushing a cart down an aisle",
    G + sc + both_to(120, GY, handle[0], handle[1], PH, 6, LEG_STRIDE),
    ["A shopper is pushing a cart.",
     "The cart has been left in an aisle.",
     "She's lifting a basket onto a shelf.",
     "Groceries are being bagged."],
    u"★ 手在把手上 → 進行式。\n"
    u"★ (B) has been left（被留下）需要「沒人」，但人就在車後面。")

# 34 ─ 把商品放進袋子（手伸向袋口）
b = [counter(88, 132, 152), poly([(150, 132), (154, 96), (186, 96), (190, 132)]),
     box(196, 112, 20, 20), box(220, 112, 20, 20)]
add("p1-034", u"超市・裝袋", "Items being placed into a bag at a checkout counter",
    G + "".join(b) + reach(72, GY, 158, 100),
    ["Some items are being placed into a bag.",
     "The bag has been left empty on the floor.",
     "He's unloading a shopping cart.",
     "Shelves are being restocked."],
    u"★ 有人正在放 → 被動進行式，主詞是被處理的東西（items）。\n"
    u"★ 分辨 be being V-ed 與 have been V-ed，看的永遠是**畫面裡有沒有人正在做**。")

# 35 ─ 空掉的貨架（無人，跟 p1-007 成對）
b = [ln(56, 44, 56, GY), ln(264, 44, 264, GY)]
for i in range(4):
    yy = 60 + i * 40
    b.append(ln(56, yy, 264, yy, THIN))
b += [box(66, 34, 22, 26), box(100, 34, 22, 26)]
add("p1-035", u"商店・幾乎空掉的貨架", "Mostly empty shelves with a few items on top",
    "".join(b),
    ["Most of the shelves have been emptied.",
     "The shelves are fully stocked.",
     "A clerk is arranging merchandise.",
     "Shoppers are browsing the aisles."],
    u"★ **跟 p1-007 是刻意做的一對**：同一組貨架，滿的 vs 空的。\n"
    u"★ (B) fully stocked 與畫面矛盾；(C)(D) 需要人。")

# 36 ─ 收銀台掃描商品
b = [counter(96, 132, 148), box(196, 104, 34, 28), ln(200, 132, 200, 108, THIN),
     box(126, 112, 22, 20)]
add("p1-036", u"商店・結帳掃描", "A cashier scanning an item at a register",
    G + "".join(b) + reach(84, GY, 130, 108),
    ["An item is being scanned at a register.",
     "The register has been left unattended.",
     "She's counting money into a drawer.",
     "Customers are lining up to pay."],
    u"★ 有人正在掃 → 被動進行式。register 收銀機。\n"
    u"★ (B) unattended 無人看管、(D) customers 都與畫面不合。")

# 37 ─ 月台上等車的人（車還沒到）
b = [ln(6, 148, 314, 148, THIN), ln(40, 148, 40, GY, THIN), ln(280, 148, 280, GY, THIN)]
add("p1-037", u"車站・月台上等車的人", "Two people standing on a platform, no train",
    G + "".join(b) + stand(120, 148) + stand(196, 148),
    ["Some people are waiting on a platform.",
     "A train is pulling into the station.",
     "Passengers are boarding a train.",
     "The platform has been closed off."],
    u"★ 兩人站著、沒有車 → 只能講人在等。\n"
    u"★ (B)(C) 都預設「有一列車」，畫面裡沒有 —— **選項裡出現畫面上不存在的東西，直接刪**。")

# 38 ─ 停在月台邊的列車（無人，跟 p1-037 成對）
add("p1-038", u"車站・停靠的列車", "A train stopped alongside an empty platform",
    G + ln(6, 148, 314, 148, THIN) + train(56, 148),
    ["A train has stopped alongside a platform.",
     "Passengers are getting off the train.",
     "The train is being cleaned.",
     "A conductor is checking tickets."],
    u"★ **跟 p1-037 成對**：那題有人沒車，這題有車沒人。\n"
    u"★ 無人的交通工具，正解幾乎都是 has stopped／is parked 這類狀態描述。")

# 39 ─ 排成一列的行李（無人）
b = [suitcase(60 + i * 56, GY) for i in range(4)]
add("p1-039", u"機場・排成一列的行李", "Suitcases lined up in a row, nobody around",
    G + "".join(b),
    ["Luggage has been lined up in a row.",
     "A traveler is checking in her bags.",
     "Suitcases are being loaded onto a cart.",
     "The bags have been placed on a conveyor belt."],
    u"★ luggage 是不可數名詞，動詞用單數 has —— Part 1 偶爾靠這個分辨。\n"
    u"★ (D) 動詞形態沒錯，但畫面沒有輸送帶：**完成被動的陷阱常常錯在「地點」**。")

# 40 ─ 拉行李的人（手在拉桿上）
b = [suitcase(196, GY)]
add("p1-040", u"機場・拉著行李的旅客", "A traveler pulling a suitcase",
    G + "".join(b) + reach(140, GY, 204, 122),
    ["A man is pulling a suitcase.",
     "He's lifting a bag onto a rack.",
     "The luggage has been left unattended.",
     "Bags are being weighed at a counter."],
    u"★ 手在拉桿上、箱子在地上 → pulling。\n"
    u"★ (B) lifting 是「抬起來」，畫面裡箱子沒離地 —— 同樣是有人動作，"
    u"**動詞挑錯一樣是錯**，不是有人就選。")

# 41 ─ 加油（人握著油槍對車）
car = [poly([(46, 152), (46, 128), (72, 104), (134, 104), (156, 128), (180, 128), (180, 152)]),
       ln(46, 152, 180, 152, THIN), circ(74, 158, 15), circ(152, 158, 15),
       ln(72, 104, 78, 128), ln(134, 104, 130, 128), ln(46, 128, 180, 128, THIN)]
pm, nozzle = pump(246)
# 🔴 手一定要落在油槍上：油槍口是從加油機算出來的，人再伸過去。
#    第一版寫死 arm_to(-18, -38)，手舉到頭頂上方去了 —— 跟 08-29 梯子那次同一種錯。
NOZZLE = (198.0, 134.0)
add("p1-041", u"加油站・正在加油", "A man refueling a car at a pump",
    G + "".join(car) + pm + ln(nozzle[0], nozzle[1], NOZZLE[0], NOZZLE[1], THIN)
    + reach(224, GY, NOZZLE[0], NOZZLE[1]),
    ["A vehicle is being refueled.",
     "The car has been left with no one nearby.",
     "He's washing the windshield.",
     "The pump has been shut off."],
    u"★ **跟 p1-009 是刻意做的一對**：同一個加油站，那題沒人（is parked），"
    u"這題有人在加油（is being refueled）。\n"
    u"★ 同一張畫面該用主動還是被動，看你要把主詞放在人還是物，兩種都對；"
    u"但 have been V-ed 一定要**沒人在動它**。")

# 42 ─ 洗車（水管對著車身）
car2 = [poly([(96, 152), (96, 128), (122, 104), (184, 104), (206, 128), (230, 128), (230, 152)]),
        ln(96, 152, 230, 152, THIN), circ(124, 158, 15), circ(202, 158, 15),
        ln(122, 104, 128, 128), ln(184, 104, 180, 128), ln(96, 128, 230, 128, THIN)]
add("p1-042", u"戶外・洗車", "A person washing a car with a hose",
    G + "".join(car2) + reach(56, GY, 104, 118) + ln(104, 118, 128, 126, THIN),
    ["A car is being washed.",
     "The vehicle has been parked in a garage.",
     "He's changing a tire.",
     "The hood has been propped open."],
    u"★ 有人拿水管對著車 → is being washed。\n"
    u"★ (C) changing a tire、(D) hood propped open 都是「畫面上不存在的細節」。")

# 43 ─ 候車亭下的空長椅（無人）
add("p1-043", u"街道・候車亭的空長椅", "An empty bench under a shelter",
    G + ln(70, 74, 250, 74) + ln(76, 74, 76, GY, THIN) + ln(244, 74, 244, GY, THIN)
    + bench(118, GY, 96),
    ["A bench has been placed under a shelter.",
     "People are seated on a bench.",
     "The bench is being repainted.",
     "Someone is waiting for a bus."],
    u"★ 空長椅 → 位置描述（under a shelter）。\n"
    u"★ 位置介系詞是無人畫面的常見正解：under／beside／against／along。")

# 44 ─ 坐在長椅上看手機（跟 p1-043 成對）
sb, hipb, shb = sit(196, GY, PH, 1)
add("p1-044", u"街道・坐在長椅上", "A man sitting on a bench looking at a phone",
    G + bench(140, GY, 96) + sb
    + poly([shb, (shb[0] + 16, shb[1] + 18), (shb[0] + 26, shb[1] + 6)]),
    ["A man is sitting on a bench.",
     "The bench is unoccupied.",
     "He's getting up from his seat.",
     "A bench is being moved onto a sidewalk."],
    u"★ **跟 p1-043 成對**：同一張長椅，有沒有人坐。\n"
    u"★ (B) unoccupied（沒人坐）正是 p1-043 的正解 —— 這組就是要你聽出這個差別。")

# 45 ─ 修剪樹木（工具伸到樹冠）
tr, canopy = tree(220, GY)
add("p1-045", u"花園・修剪樹木", "A gardener trimming a tree with a tool",
    G + tr + reach(146, GY, canopy[0] - 14, canopy[1] + 6)
    + ln(canopy[0] - 14, canopy[1] + 6, canopy[0] + 2, canopy[1] - 2, THIN),
    ["A tree is being trimmed.",
     "The branches have been piled up.",
     "He's planting a tree.",
     "Leaves are being raked into a bag."],
    u"★ 工具碰到樹 → is being trimmed。trim 修剪。\n"
    u"★ (B) piled up 地上沒有樹枝堆；(C) planting 樹已經長好了，不是在種。")

# 46 ─ 草地上的灑水器（無人）
b = []
for i in range(3):
    px = 84 + i * 76
    b += [ln(px, GY, px, GY - 20), circ(px, GY - 24, 5, THIN),
          poly([(px, GY - 30), (px - 14, GY - 42), (px - 24, GY - 40)]),
          poly([(px, GY - 30), (px + 14, GY - 42), (px + 24, GY - 40)])]
# 沒有草，三支灑水器看起來像天線。沿地面加草叢，畫面才讀得出是草坪。
for i in range(11):
    gx = 26 + i * 26
    b += [poly([(gx - 5, GY), (gx - 2, GY - 9), (gx + 1, GY)], THIN),
          poly([(gx + 2, GY), (gx + 6, GY - 7), (gx + 9, GY)], THIN)]
add("p1-046", u"公園・草地上的灑水器", "Sprinklers set up on a lawn, no people",
    G + "".join(b),
    ["Sprinklers have been set up on a lawn.",
     "A worker is watering the grass.",
     "The lawn is being mowed.",
     "Hoses have been coiled beside a shed."],
    u"★ 器材架好、沒有人 → have been set up。\n"
    u"★ (D) 文法完全正確，但畫面沒有水管盤、也沒有小屋 —— **背景物件對不上就是錯**。")

# 47 ─ 掃落葉（耙子頭落在地上）
b = [circ(196 + i * 22, GY - 5, 5, THIN) for i in range(4)]
add("p1-047", u"戶外・掃落葉", "A man raking leaves on the ground",
    G + "".join(b) + reach(128, GY, 184, GY - 8)
    + ln(184, GY - 8, 172, GY - 2, THIN) + ln(184, GY - 8, 196, GY - 2, THIN),
    ["A man is raking leaves.",
     "The leaves have all been cleared away.",
     "He's sweeping a hallway.",
     "A bag is being filled with grass."],
    u"★ 地上還有葉子、耙子在動 → is raking。\n"
    u"★ (B) have all been cleared away 說「已經清光」，但葉子還在 —— 狀態寫反。")

# 48 ─ 路邊排好的垃圾桶（無人）
b = [bin_(64 + i * 52, GY) for i in range(4)]
add("p1-048", u"街道・路邊的垃圾桶", "Trash bins placed along a curb, nobody nearby",
    G + "".join(b) + ln(6, 166, 314, 166, THIN),
    ["Some bins have been placed along a curb.",
     "Trash is being collected.",
     "A worker is emptying a container.",
     "The bins have been knocked over."],
    u"★ along a curb 沿著路緣，又一個位置介系詞的正解。\n"
    u"★ (D) knocked over（被撞倒）與畫面「立得好好的」矛盾。")


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "items1", "batch02.json")
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(ITEMS, f, ensure_ascii=False, indent=1)
    sizes = [len(x["svg"]) for x in ITEMS]
    print(u"寫出 {} 題，SVG 平均 {:.0f} 位元組，合計 {:.1f} KB".format(
        len(ITEMS), sum(sizes) / float(len(sizes)), sum(sizes) / 1024.0))
    bad = [x["id"] for x in ITEMS if len(set(x["choices"])) != 4]
    print(u"選項檢查：" + (u"通過" if not bad else u"有問題 {}".format(bad)))

# -*- coding: utf-8 -*-
"""產生 items1/batch04.json（Part 1 第四批，p1-073 ~ p1-096）。

2026-09-01 新增，收尾到 96 題。鐵律同前：人與物互動時人的座標從物件幾何算出來，
每批畫完 render 出來看過（`python build/sheet_part1.py p1-073 p1-096`）。

⚠ 這個畫布是 320×200，**細節有下限**：間距小於 3px 的線在實際尺寸下會糊成一塊黑
（p1-055 的「字行」踩過），寧可少畫。
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
def car(x, y, s=1.0):
    """側面小客車。y 是車底線。"""
    w, h = 120 * s, 48 * s
    return "".join([poly([(x, y), (x, y - h * 0.5), (x + w * 0.22, y - h),
                          (x + w * 0.72, y - h), (x + w * 0.9, y - h * 0.5),
                          (x + w, y - h * 0.5), (x + w, y)]),
                    ln(x, y, x + w, y, THIN),
                    ln(x, y - h * 0.5, x + w, y - h * 0.5, THIN),
                    ln(x + w * 0.22, y - h, x + w * 0.27, y - h * 0.5),
                    ln(x + w * 0.72, y - h, x + w * 0.67, y - h * 0.5),
                    circ(x + w * 0.24, y + 6 * s, 13 * s),
                    circ(x + w * 0.78, y + 6 * s, 13 * s)])


def crosswalk(y=168.0, n=7):
    return "".join([box(30 + i * 38, y, 22, 8, THIN) for i in range(n)])


def traffic_light(x, y=GY):
    return "".join([ln(x, y, x, y - 96), box(x - 12, y - 132, 24, 40),
                    circ(x, y - 122, 5, THIN), circ(x, y - 112, 5, THIN),
                    circ(x, y - 102, 5, THIN)])


def truck(x, y, s=1.0):
    """側面貨車。回傳 (svg, 車斗後緣中點)。"""
    bw, bh = 118 * s, 62 * s
    tail = (x, y - bh * 0.5)
    o = [box(x, y - bh, bw, bh),
         poly([(x + bw, y - bh * 0.62), (x + bw + 22 * s, y - bh * 0.62),
               (x + bw + 34 * s, y - bh * 0.3), (x + bw + 34 * s, y)]),
         ln(x + bw, y, x + bw + 34 * s, y, THIN),
         circ(x + 26 * s, y + 8 * s, 12 * s), circ(x + bw + 14 * s, y + 8 * s, 12 * s)]
    return "".join(o), tail


def crate(x, y, w=34.0, h=28.0):
    return "".join([box(x, y - h, w, h), ln(x, y - h, x + w, y, THIN),
                    ln(x, y, x + w, y - h, THIN)])


def wall_lamp(x, y=64.0):
    """壁燈。回傳 (svg, 燈罩中心)。"""
    c = (x, y + 18)
    s = "".join([ln(x, y - 14, x, y + 6),
                 poly([(x - 16, y + 6), (x - 10, y + 22), (x + 10, y + 22), (x + 16, y + 6)])])
    return s, c


def workbench(x, y=126.0, w=140.0):
    return "".join([box(x, y, w, 8), ln(x + 8, y + 8, x + 8, GY),
                    ln(x + w - 8, y + 8, x + w - 8, GY)])


def microscope(x, y):
    """顯微鏡。回傳 (svg, 目鏡口)。"""
    eye = (x + 6, y - 62)
    s = "".join([box(x - 20, y - 8, 44, 8), ln(x, y, x, y - 8),
                 ln(x, y - 8, x, y - 46), poly([(x, y - 46), (x + 6, y - 56), (x + 6, y - 62)]),
                 ln(x - 14, y - 30, x + 12, y - 30, THIN), circ(x - 2, y - 22, 5, THIN)])
    return s, eye


def flask(x, y, w=22.0, h=26.0):
    return "".join([poly([(x + w * 0.35, y - h), (x + w * 0.35, y - h * 0.5),
                          (x, y), (x + w, y), (x + w * 0.65, y - h * 0.5),
                          (x + w * 0.65, y - h)]),
                    ln(x + w * 0.3, y - h, x + w * 0.7, y - h, THIN)])


def desk_row(x, y, n=3, dw=58.0):
    o = []
    for i in range(n):
        dx = x + i * dw
        o += [box(dx, y - 34, 42, 6), ln(dx + 4, y - 28, dx + 4, y),
              ln(dx + 36, y - 28, dx + 36, y),
              ln(dx + 8, y - 52, dx + 30, y - 52), ln(dx + 8, y - 52, dx + 8, y - 34),
              ln(dx + 10, y - 34, dx + 10, y), ln(dx + 26, y - 34, dx + 26, y)]
    return "".join(o)


def treadmill(x, y):
    """跑步機。回傳 (svg, 踏帶中點, 把手)。"""
    belt = (x + 46, y - 18)
    handle = (x + 96, y - 78)
    s = "".join([box(x, y - 22, 96, 10), ln(x + 8, y - 12, x + 8, y),
                 ln(x + 88, y - 12, x + 88, y),
                 ln(x + 90, y - 22, x + 96, y - 78), ln(x + 74, y - 78, x + 108, y - 78),
                 box(x + 84, y - 106, 26, 24)])
    return s, belt, handle


def weight_rack(x, y):
    o = [ln(x, y, x, y - 62), ln(x + 132, y, x + 132, y - 62),
         ln(x, y - 26, x + 132, y - 26, THIN), ln(x, y - 58, x + 132, y - 58, THIN)]
    for r in range(2):
        for i in range(4):
            cx = x + 20 + i * 32
            cy = y - 32 - r * 32
            o += [circ(cx - 9, cy, 8, THIN), circ(cx + 9, cy, 8, THIN),
                  ln(cx - 9, cy, cx + 9, cy, THIN)]
    return "".join(o)


def umbrella(x, y, r=34.0):
    """撐開的傘。回傳 (svg, 握把)。"""
    grip = (x, y + 46)
    s = "".join([poly([(x - r, y), (x - r * 0.55, y - r * 0.5), (x, y - r * 0.66),
                       (x + r * 0.55, y - r * 0.5), (x + r, y)]),
                 ln(x - r, y, x + r, y, THIN), ln(x, y - r * 0.66, x, y + 46)])
    return s, grip


def brolly_stand(x, y):
    """傘桶＋三把收起來的傘。

    第一版太小、傘柄又畫成箭頭，render 出來像插了三支箭。放大並改成 J 形彎鉤。
    """
    o = [poly([(x, y - 46), (x + 5, y), (x + 47, y), (x + 52, y - 46)]),
         ln(x, y - 46, x + 52, y - 46, THIN)]
    for i in range(3):
        px = x + 13 + i * 13
        o += [ln(px, y - 46, px - 4, y - 108),
              poly([(px - 4, y - 108), (px - 15, y - 113), (px - 18, y - 101)])]
    return "".join(o)


def camera(x, y, w=30.0, h=20.0):
    return "".join([box(x, y, w, h), circ(x + w * 0.5, y + h * 0.5, 6, THIN),
                    box(x + w - 10, y - 5, 8, 5, THIN)])


def elevator(x):
    """電梯門＋按鈕面板。回傳 (svg, 按鈕座標)。"""
    btn = (x - 14, 116.0)
    s = "".join([box(x, 56, 96, 124), ln(x + 48, 56, x + 48, 180),
                 box(x - 24, 104, 20, 26), circ(btn[0], 112, 4, THIN),
                 circ(btn[0], 122, 4, THIN)])
    return s, btn


def coat_rack(x, y):
    o = [ln(x, y, x + 140, y)]
    for i in range(3):
        cx = x + 26 + i * 44
        o += [ln(cx, y, cx, y + 6), circ(cx, y + 6, 3, THIN),
              poly([(cx - 16, y + 10), (cx - 20, y + 62), (cx + 20, y + 62),
                    (cx + 16, y + 10)])]
    return "".join(o)


# ══════════════════════════ p1-073 ~ p1-096 ══════════════════════════

# 73 ─ 停車場一排車（無人）
add("p1-073", u"停車場・停成一排的車", "Cars parked in a row in a lot, no drivers",
    G + car(20, 168, 0.62) + car(112, 168, 0.62) + car(204, 168, 0.62)
    + ln(96, 150, 96, GY, THIN) + ln(188, 150, 188, GY, THIN),
    ["Vehicles have been parked side by side.",
     "Cars are stopped at a traffic light.",
     "A parking lot is being repaved.",
     "Drivers are getting out of their cars."],
    u"★ side by side 並排，又一個位置說法。\n"
    u"★ (B) 沒有紅綠燈、(D) 沒有人 —— 選項提到畫面上沒有的東西就是錯。")

# 74 ─ 行人過斑馬線
add("p1-074", u"街道・過馬路的行人", "Two pedestrians crossing at a crosswalk",
    G + crosswalk() + traffic_light(286)
    + figure(112, 168, [arm_to(16, 10), arm_to(-14, 12, -1)], LEG_STRIDE)
    + figure(176, 168, [arm_to(14, 12), arm_to(-16, 10, -1)], LEG_STRIDE),
    ["Some people are crossing the street.",
     "Pedestrians are waiting at a corner.",
     "The crosswalk has been closed to traffic.",
     "They're boarding a bus at a stop."],
    u"★ 人在斑馬線上、腳是跨步的 → crossing。\n"
    u"★ (B) waiting 與 crossing 是 Part 1 最常互換的一組：**在等 vs 正在走**。")

# 75 ─ 空的路口（無人，跟 p1-074 對）
add("p1-075", u"街道・沒人的路口", "An empty crosswalk with a traffic light",
    G + crosswalk() + traffic_light(272),
    ["A traffic light has been installed at a corner.",
     "Pedestrians are crossing the road.",
     "A vehicle is being towed away.",
     "Cars are lined up at the intersection."],
    u"★ **跟 p1-074 成對**：一樣的路口，有人 vs 沒人。\n"
    u"★ 無人的街景，正解幾乎都是「某個東西被裝在某處」這種完成被動＋地點。")

# 76 ─ 騎腳踏車
# 🔴 這張不能用 figure()：它假設人站在地上，套上來腿會停在半空、跟車架糊成一團。
#    騎車的人要自己接關節——臀在坐墊、手在把手、腳踩在踏板 —— 三個接點都從車架算。
SEAT, BB, BAR = (146.0, 116.0), (152.0, 156.0), (186.0, 114.0)
bike = [circ(108, 156, 18), circ(200, 156, 18),
        ln(BB[0], BB[1], 108, 156, THIN), ln(SEAT[0], SEAT[1] + 2, 108, 156, THIN),
        ln(BB[0], BB[1], SEAT[0], SEAT[1] + 2), ln(BB[0], BB[1], 184, 120),
        ln(184, 120, 200, 156), ln(184, 120, BAR[0], BAR[1], THIN),
        ln(140, 114, 154, 114, THIN), circ(BB[0], BB[1], 4, THIN)]
hip, sho, hd = (146.0, 110.0), (161.0, 86.0), (169.0, 74.0)
rider = [circ(hd[0], hd[1], 9.5), ln(sho[0], sho[1], hip[0], hip[1]),
         poly([sho, (175, 100), BAR]),
         poly([hip, (158, 132), (149, 148)]), poly([hip, (152, 134), (158, 150)])]
add("p1-076", u"公園・騎腳踏車", "A cyclist riding a bicycle along a path",
    G + "".join(bike) + "".join(rider),
    ["A cyclist is riding along a path.",
     "The bicycles have been parked in a rack.",
     "He's repairing a flat tire.",
     "A bicycle is being lifted onto a car."],
    u"★ **跟 p1-005 成對**：那題是停好的腳踏車（have been parked），這題有人在騎。\n"
    u"★ (C)(D) 都是「有人動作」但動作對不上畫面。")

# 77 ─ 兩人合抬桌子（四隻手都在桌面）
tb = box(112, 116, 96, 8)
add("p1-077", u"辦公室・兩人合抬桌子", "Two people carrying a table together",
    G + tb + reach(84, GY, 116, 112) + reach(236, GY, 204, 112),
    ["They're carrying a table together.",
     "The table has been set up in a hallway.",
     "One of them is sitting on a table.",
     "The furniture is being covered with a cloth."],
    u"★ 兩人各扶一端、桌子離地 → carrying…together。\n"
    u"★ (B) has been set up 是「已經擺好」，桌子還在手上就不成立。")

# 78 ─ 把箱子搬上貨車
tk, tail = truck(120, 160, 0.9)
add("p1-078", u"倉庫・搬箱子上貨車", "A box being lifted onto a truck",
    # 箱子要在手上，不是在頭上：座標跟著 reach 的目標點走。
    G + tk + reach(84, GY, tail[0] - 8, tail[1] + 6) + crate(tail[0] - 20, tail[1] + 20, 30, 26),
    ["A box is being loaded onto a truck.",
     "The truck has been fully loaded.",
     "He's unloading crates onto a dock.",
     "The cartons have been sealed with tape."],
    u"★ **這題是 be being V-ed 的教科書用法**：有人正在把箱子搬上車。\n"
    u"★ (B) fully loaded 是「已經裝滿」的結果狀態 —— 動作還在進行就不能用。")

# 79 ─ 貨車旁堆好的木箱（無人，跟 p1-078 對）
tk2, _ = truck(96, 160, 0.9)
add("p1-079", u"倉庫・貨車旁的木箱", "Crates stacked beside a truck, nobody around",
    G + tk2 + crate(30, GY) + crate(30, GY - 28) + crate(66, GY),
    ["Some crates have been stacked beside a truck.",
     "Boxes are being loaded into a van.",
     "A driver is closing the tailgate.",
     "The crates have been placed inside the truck."],
    u"★ **跟 p1-078 成對**。木箱在車外的地上、沒有人 → have been stacked beside。\n"
    u"★ (D) 動詞形態一樣正確，錯在**位置**（inside vs beside）——"
    u"Part 1 的完成被動陷阱，一半以上錯在地點介系詞。")

# 80 ─ 換燈泡（手伸到燈罩）
wl, lamp = wall_lamp(214)
add("p1-080", u"室內・換燈泡", "A man reaching up to a light fixture",
    G + ln(6, 44, 314, 44, THIN) + wl + reach(150, GY, lamp[0] - 18, lamp[1]),
    ["A light fixture is being replaced.",
     "The lights have been switched off.",
     "He's standing on a ladder.",
     "A lamp has been placed on a table."],
    u"★ 手伸到燈具上 → is being replaced。\n"
    u"★ (C) 畫面沒有梯子 —— **人站在哪裡也要看**，不能因為「換燈泡通常要梯子」就選。")

# 81 ─ 鋸木板（鋸子落在木板上）
wb = workbench(96)
add("p1-081", u"工作間・鋸木板", "A man sawing a board on a workbench",
    G + wb + box(120, 118, 92, 8)
    + reach(80, GY, 150, 112) + ln(150, 112, 174, 106, THIN)
    + ln(150, 116, 174, 110, THIN),
    ["A man is sawing a board.",
     "The boards have been stacked on a bench.",
     "He's measuring a piece of wood.",
     "Sawdust is being swept off the floor."],
    u"★ 鋸子壓在木板上 → sawing。\n"
    u"★ (C) measuring 也要有人有工具，但捲尺跟鋸子畫面上不一樣 —— 看清楚工具。")

# 82 ─ 工作台上疊好的木板（無人，跟 p1-081 對）
wb2 = workbench(90)
add("p1-082", u"工作間・疊好的木板", "Boards stacked on a workbench, no one working",
    G + wb2 + box(108, 118, 104, 7) + box(108, 108, 104, 7) + box(108, 98, 104, 7),
    ["Some boards have been stacked on a bench.",
     "A carpenter is cutting lumber.",
     "The wood is being carried outside.",
     "Tools have been spread across the floor."],
    u"★ 疊好、沒人 → have been stacked on。\n"
    u"★ (D) 地上沒有工具 —— **位置＋有沒有那個東西**，兩個都要對。")

# 83 ─ 用顯微鏡（眼睛靠在目鏡上）
ms, eye = microscope(196, 140)
add("p1-083", u"實驗室・使用顯微鏡", "A researcher looking into a microscope",
    G + workbench(96, 140, 150) + ms + reach(120, 140, eye[0] - 22, eye[1] + 16),
    ["A woman is looking into a microscope.",
     "The equipment has been put away.",
     "She's writing in a notebook.",
     "Samples are being carried to a shelf."],
    u"★ 人靠在儀器前 → looking into。\n"
    u"★ (B) put away（收起來）與畫面矛盾。")

# 84 ─ 實驗桌上的器材（無人）
b = [workbench(84, 132, 156), flask(112, 132), flask(146, 132), flask(180, 132),
     box(212, 108, 22, 24)]
add("p1-084", u"實驗室・桌上的器材", "Lab equipment set out on a bench, no researchers",
    G + "".join(b),
    ["Equipment has been set out on a bench.",
     "A technician is adjusting an instrument.",
     "The bottles are being filled with liquid.",
     "The lab has been cleared of equipment."],
    u"★ 器材擺出來、沒有人 → have been set out。\n"
    u"★ (D) cleared of equipment（器材被清空）與畫面正好相反。")

# 85 ─ 排好的課桌椅（無人）
add("p1-085", u"教室・排好的課桌椅", "Desks arranged in rows in an empty classroom",
    G + desk_row(58, GY, 4, 62),
    ["Desks have been arranged in rows.",
     "Students are taking an exam.",
     "The desks are being moved into a corner.",
     "A teacher is handing out papers."],
    u"★ 排好、沒有人 → have been arranged in rows。in rows 成排。\n"
    u"★ 三個錯的都需要人。這種題型答對的關鍵只有一句：**先數人**。")

# 86 ─ 舉手（兩人坐，其中一人手舉高）
s1, hip1, sh1 = sit(120, GY, PH, 1)
s2, hip2, sh2 = sit(206, GY, PH, 1)
add("p1-086", u"教室・舉手發問", "One of two seated people raising a hand",
    G + desk_row(80, GY, 2, 86) + s1 + s2
    + poly([sh1, (sh1[0] + 12, sh1[1] - 16), (sh1[0] + 8, sh1[1] - 34)]),
    ["One of them is raising a hand.",
     "They're standing beside a desk.",
     "The classroom has been left empty.",
     "Papers are being collected from the desks."],
    u"★ 兩人坐著、其中一人手舉起 → One of them is V-ing。\n"
    u"★ **One of them／Both of them／Neither 是 Part 1 分辨兩人動作的固定句型**，"
    u"聽到就要立刻判斷「是一個人還是兩個人在做」。")

# 87 ─ 跑步機（腳在踏帶上、手在把手）
tm, belt, handle = treadmill(150, GY)
add("p1-087", u"健身房・跑步機", "A man exercising on a treadmill",
    G + tm + figure(belt[0] + 24, belt[1], [arm_to(handle[0] - belt[0] - 44, -8),
                                            ((-11, 14), (-14, 30))], LEG_STRIDE, 84),
    ["A man is exercising on a machine.",
     "The equipment has been left unused.",
     "He's lifting weights over his head.",
     "Towels have been folded on a bench."],
    u"★ 人在機器上、手扶把手 → exercising on。\n"
    u"★ (C) lifting weights 是另一種器材的動作，畫面沒有啞鈴。")

# 88 ─ 架上的啞鈴（無人，跟 p1-087 對）
add("p1-088", u"健身房・啞鈴架", "Dumbbells arranged on a rack, no one nearby",
    G + weight_rack(94, GY),
    ["Weights have been arranged on a rack.",
     "Someone is putting a dumbbell back.",
     "The rack is being assembled.",
     "The weights have been left on the floor."],
    u"★ 排好、沒人 → have been arranged on a rack。\n"
    u"★ (D) on the floor 位置寫錯 —— 又一個「動詞對、地點錯」的陷阱。")

# 89 ─ 撐傘走路（握把在手上）
um, grip = umbrella(178, 84)
add("p1-089", u"街道・撐傘", "A woman walking while holding an open umbrella",
    G + um + figure(178, GY, [arm_to(grip[0] - 178, grip[1] - 108 + 6),
                              ((-11, 14), (-14, 30))], LEG_STRIDE),
    ["A woman is holding an umbrella.",
     "The umbrella has been folded up.",
     "She's opening an umbrella.",
     "Umbrellas have been left in a stand."],
    u"★ 傘撐開、握把在手上 → holding。\n"
    u"★ (C) opening 是「正在打開」的瞬間動作，傘已經開了就不是 —— "
    u"**動作進行到哪一步也要看**。")

# 90 ─ 傘桶裡收起來的傘（無人，跟 p1-089 對）
add("p1-090", u"門口・傘桶裡的傘", "Folded umbrellas in a stand near a doorway",
    G + brolly_stand(126, GY) + wall(84),
    ["Some umbrellas have been placed in a stand.",
     "A man is shaking out an umbrella.",
     "The umbrellas are being handed out.",
     "An umbrella has been opened up."],
    u"★ **跟 p1-089 成對**：撐開的傘 vs 收起來插在傘桶裡。\n"
    u"★ (D) opened up 與畫面矛盾。")

# 91 ─ 拍照（相機舉到臉前）
add("p1-091", u"戶外・拍照", "A man taking a photograph with a camera",
    G + figure(150, GY, [arm_to(22, -22), arm_to(18, -14, -1)], LEG_STAND)
    + camera(168, 92),
    ["A man is taking a photograph.",
     "The camera has been set on a tripod.",
     "He's putting a camera into a bag.",
     "Photographs have been hung on a wall."],
    u"★ 相機舉在臉前、雙手扶著 → taking a photograph。\n"
    u"★ (B) 沒有腳架、(D) 牆上沒有照片。")

# 92 ─ 按電梯按鈕（手指落在面板上）
ev, btn = elevator(160)
add("p1-092", u"大樓・按電梯", "A woman pressing an elevator button",
    G + ev + reach(104, GY, btn[0] - 8, btn[1]),
    ["A woman is pressing a button.",
     "The elevator doors have been propped open.",
     "She's stepping into an elevator.",
     "A sign has been posted beside the doors."],
    u"★ 手指伸到面板 → pressing。\n"
    u"★ (C) stepping into 需要門開著、人已經跨進去，畫面裡門是關的。")

# 93 ─ 開著的門（無人）
add("p1-093", u"走廊・開著的門", "An open doorway with no one in it",
    G + box(112, 56, 96, 124) + poly([(112, 56), (74, 74), (74, 180)])
    + ln(74, 180, 112, 180, THIN) + circ(104, 124, 4, THIN),
    ["A door has been left open.",
     "Someone is walking through a doorway.",
     "The door is being locked.",
     "A doorway has been blocked with boxes."],
    u"★ 門板往外開著、門口沒有人 → have been left open。\n"
    u"★ 這題與 p1-092 相鄰：**同樣是門，有沒有人決定用哪一種時態**。")

# 94 ─ 衣架上的外套（無人）
add("p1-094", u"門廳・掛好的外套", "Coats hanging on a rack in an entryway",
    G + coat_rack(90, 56),
    ["Some coats have been hung on a rack.",
     "A man is putting on his jacket.",
     "The coats are being handed to a guest.",
     "Jackets have been folded over a chair."],
    u"★ 掛在架上、沒有人 → have been hung on。\n"
    u"★ (D) folded over a chair 位置與方式都不對（是掛著不是摺著）。")

# 95 ─ 碼頭上卸下的木箱（無人）
add("p1-095", u"碼頭・卸下的木箱", "Crates unloaded onto a dock beside the water",
    ln(6, 150, 314, 150, THIN) + ln(6, 168, 314, 168, THIN)
    + crate(56, 150) + crate(56, 122) + crate(98, 150) + crate(150, 150)
    + ln(196, 150, 214, 150) + ln(196, 150, 196, 132),
    ["Crates have been unloaded onto a dock.",
     "Workers are loading a ship.",
     "The cargo is being weighed.",
     "Boxes have been stacked on a boat."],
    u"★ 木箱在碼頭上、沒有人 → have been unloaded onto。\n"
    u"★ (D) on a boat 位置錯 —— 東西在岸上不在船上。")

# 96 ─ 擦桌子（抹布落在桌面）
add("p1-096", u"餐廳・擦桌子", "A table being wiped down with a cloth",
    G + box(126, 120, 116, 8) + ln(140, 128, 140, GY) + ln(228, 128, 228, GY)
    + reach(96, GY, 152, 116) + box(146, 112, 18, 8, THIN),
    ["A table is being wiped down.",
     "The table has been set with dishes.",
     "He's pulling out a chair.",
     "Dishes are being carried to the kitchen."],
    u"★ 抹布壓在桌面、有人在擦 → is being wiped down。\n"
    u"★ **跟 p1-031 成對**：一樣的餐桌，那題擺好餐具沒有人（have been set），"
    u"這題有人在動它（being V-ed）。整個 Part 1 的核心分辨就在這裡。")


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "items1", "batch04.json")
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(ITEMS, f, ensure_ascii=False, indent=1)
    sizes = [len(x["svg"]) for x in ITEMS]
    print(u"寫出 {} 題，SVG 平均 {:.0f} 位元組，合計 {:.1f} KB".format(
        len(ITEMS), sum(sizes) / float(len(sizes)), sum(sizes) / 1024.0))
    bad = [x["id"] for x in ITEMS if len(set(x["choices"])) != 4]
    print(u"選項檢查：" + (u"通過" if not bad else u"有問題 {}".format(bad)))

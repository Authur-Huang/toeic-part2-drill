# -*- coding: utf-8 -*-
"""產生 items1/batch01.json（Part 1 照片描述，24 題）與場景 SVG。

★ 這裡的圖是**自己畫的 SVG，不是照片**。做得到與做不到要講清楚：
  做得到：is being V-ed 與 have been V-ed 的分辨（Part 1 最大的考點）、
          位置介系詞、畫面裡到底有沒有人、物品在但動作不存在。
  做不到：leaning／kneeling 這類細緻姿態，以及真實照片才有的曖昧地帶。
  → 定位是**文法反射訓練**，不是 Part 1 模擬。

🔴 第一版失敗的教訓（2026-08-29）：用絕對座標盲畫，人與物的相對關係沒對上，
   「站在梯子上」畫成人站在梯子旁邊，等於推翻正解。這一版兩條鐵律：

   1. **凡是人與物互動的場景，人的座標一律從物件幾何算出來**，不再各畫各的。
   2. **每次改完都要用 headless Chrome 截圖自己看過**：
        chrome --headless=new --disable-gpu --hide-scrollbars \\
               --window-size=1000,760 --screenshot=out.png file:///.../sheet.html
      看不到成品就不要交出去。
"""
import io, json, os

W, H = 320, 200
ST = 'stroke="currentColor" fill="none" stroke-width="3" stroke-linecap="round"'
STJ = ST + ' stroke-linejoin="round"'
THIN = 'stroke="currentColor" fill="none" stroke-width="2.2" stroke-linecap="round"'
FAINT = 'stroke="currentColor" fill="none" stroke-width="2.5" opacity=".45"'


def ln(x1, y1, x2, y2, s=ST):
    return '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" %s/>' % (x1, y1, x2, y2, s)


def poly(pts, s=STJ):
    return '<polyline points="%s" %s/>' % (" ".join("%.1f,%.1f" % p for p in pts), s)


def circ(cx, cy, r, s=ST):
    return '<circle cx="%.1f" cy="%.1f" r="%.1f" %s/>' % (cx, cy, r, s)


def box(x, y, w, h, s=STJ):
    return '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="2" %s/>' % (x, y, w, h, s)


GY = 180.0


def ground(y=GY):
    return ln(6, y, W - 6, y, FAINT)


def wall(x, y0=18, y1=GY):
    return ln(x, y0, x, y1, FAINT)


# ── 人物 ────────────────────────────────────────────────────────────
PH = 92


def _joints(x, y, h, lean):
    hip = (x, y - h * 0.46)
    sh = (x + lean, y - h * 0.78)
    hd = (x + lean * 1.25, y - h * 0.90)
    return hip, sh, hd


def figure(x, y, arms, legs, h=PH, lean=0.0):
    hip, sh, hd = _joints(x, y, h, lean)
    out = [circ(hd[0], hd[1], h * 0.105), ln(sh[0], sh[1], hip[0], hip[1])]
    for elbow, hand in arms:
        out.append(poly([sh, (sh[0] + elbow[0], sh[1] + elbow[1]),
                         (sh[0] + hand[0], sh[1] + hand[1])]))
    for knee, foot in legs:
        out.append(poly([hip, (hip[0] + knee[0], hip[1] + knee[1]),
                         (hip[0] + foot[0], hip[1] + foot[1])]))
    return "".join(out)


LEG_STAND = [((-6, 22), (-9, 42)), ((7, 22), (10, 42))]
LEG_STRIDE = [((-14, 20), (-23, 42)), ((11, 22), (18, 42))]
LEG_TOGETHER = [((-3, 22), (-4, 42)), ((4, 22), (5, 42))]
ARM_DOWN = [((-11, 14), (-14, 30)), ((11, 14), (14, 30))]


def arm_to(dx, dy, side=1):
    return ((dx * 0.55 + side * 3, dy * 0.5 + 6), (dx, dy))


def shoulder_of(x, y, h=PH, lean=0.0):
    return _joints(x, y, h, lean)[1]


def stand(x, y, h=PH):
    return figure(x, y, ARM_DOWN, LEG_STAND, h)


def reach(x, y, tx, ty, h=PH):
    """一手伸向畫布上的絕對座標 (tx,ty)，另一手垂下"""
    sh = shoulder_of(x, y, h)
    return figure(x, y, [arm_to(tx - sh[0], ty - sh[1]), ((-11, 14), (-14, 30))],
                  LEG_STAND, h)


def both_to(x, y, tx, ty, h=PH, lean=0.0, legs=None):
    """雙手伸向絕對座標（推車、端托盤、掃地）"""
    sh = shoulder_of(x, y, h, lean)
    return figure(x, y, [arm_to(tx - sh[0], ty - sh[1] - 4, 1),
                         arm_to(tx - sh[0], ty - sh[1] + 4, -1)],
                  legs or LEG_STAND, h, lean)


def sit(x, y, h=PH, face=1):
    """側坐，x,y 是腳著地點。回傳 (svg, hip, shoulder)"""
    hip = (x - face * 32, y - h * 0.42)
    knee = (x - face * 5, y - h * 0.42)
    sh = (hip[0] - face * 2, hip[1] - h * 0.32)
    hd = (sh[0], sh[1] - h * 0.13)
    s = "".join([circ(hd[0], hd[1], h * 0.105), ln(sh[0], sh[1], hip[0], hip[1]),
                 poly([hip, knee, (x, y)])])
    return s, hip, sh


def chair_side(x, y, face=1):
    """側面椅子：椅面 26 寬、椅背在 face 的反方向"""
    bx = x if face > 0 else x + 26
    return "".join([ln(x, y - 22, x + 26, y - 22), ln(bx, y - 22, bx, y - 48),
                    ln(x + 3, y - 22, x + 3, y), ln(x + 23, y - 22, x + 23, y)])


def svg(body, label):
    return ('<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" '
            'role="img" aria-label="%s">%s</svg>' % (W, H, label, body))


# ── 共用物件 ────────────────────────────────────────────────────────
def ladder(bx=120.0, by=GY, tx=210.0, ty=44.0, n=8):
    """回傳 (svg, rungs)。rungs 是每根橫木的中點，人要站上去就用它。"""
    dx, dy = tx - bx, ty - by
    o = [ln(bx - 11, by, tx - 11, ty), ln(bx + 11, by, tx + 11, ty)]
    rungs = []
    for i in range(1, n):
        t = i / float(n)
        rx, ry = bx + dx * t, by + dy * t
        rungs.append((rx, ry))
        o.append(ln(rx - 11, ry, rx + 11, ry, THIN))
    return "".join(o), rungs


def desk(x=150.0, y=118.0, w=150.0):
    return "".join([box(x, y, w, 7), ln(x + 8, y + 7, x + 8, GY),
                    ln(x + w - 8, y + 7, x + w - 8, GY)])


def bicycle(x, y, s=1.0):
    r = 17 * s
    return "".join([circ(x, y, r), circ(x + 46 * s, y, r),
                    ln(x, y, x + 46 * s, y, THIN),
                    poly([(x, y), (x + 22 * s, y - 26 * s), (x + 46 * s, y)], THIN),
                    ln(x + 22 * s, y - 26 * s, x + 30 * s, y - 34 * s, THIN)])


ITEMS = []


def add(sid, scene, label, body, choices, note):
    ITEMS.append({"id": sid, "part": 1, "scene": scene, "svg": svg(body, label),
                  "choices": choices, "answer": 0, "note": note})


# ══════════════════════════ 24 個場景 ══════════════════════════
G = ground()

# 1 ─ 箱子堆在牆邊（無人）
b = [wall(70)]
for i in range(3):
    b.append(box(76, GY - 38 * (i + 1), 52, 36))
for i in range(2):
    b.append(box(132, GY - 38 * (i + 1), 52, 36))
add("p1-001", "倉庫・堆好的箱子", "Boxes stacked against a wall, no people",
    G + "".join(b),
    ["Some boxes have been stacked against a wall.",
     "A man is carrying a box.",
     "The boxes are being loaded onto a truck.",
     "Cartons are scattered across the floor."],
    "★ 畫面裡沒有人，所以任何 A man is... 一律錯，being loaded 也錯（沒人在裝）。\n"
    "★ 東西已經放好、沒人在動它 → have been V-ed。這是 Part 1 最常考的一組對比。")

# 2 ─ 人站在梯子上（腳的位置由橫木算出來）
lad, rungs = ladder()
fx, fy = rungs[2]
add("p1-002", "工地・站在梯子上的人", "A man standing on a ladder",
    G + wall(236) + lad
    + figure(fx, fy, [arm_to(26, -30), ((-10, 12), (-13, 26))], LEG_TOGETHER, 84),
    ["A man is standing on a ladder.",
     "A ladder is leaning against a wall with no one on it.",
     "He's folding up a ladder.",
     "Workers are climbing down from a roof."],
    "★ 有人在梯子上 → 用進行式。\n"
    "★ 跟 p1-023 剛好成對：那一題是空梯子靠牆，正解就變成狀態描述。")

# 3 ─ 會議室排好的椅子（側視，全部站在地上）
b = [box(96, 112, 128, 8), ln(112, 120, 112, GY), ln(208, 120, 208, GY)]
for i in range(2):
    b.append(chair_side(28 + i * 34, GY, 1))
for i in range(2):
    b.append(chair_side(232 + i * 34, GY, -1))
add("p1-003", "會議室・排好的椅子", "Chairs arranged around a table, empty room",
    G + "".join(b),
    ["Chairs have been arranged around a table.",
     "People are seated at a conference table.",
     "The chairs are being stacked in a corner.",
     "A meeting is in progress."],
    "★ 空無一人的會議室：有人物的選項全錯。\n"
    "★ being stacked 需要有人在疊，畫面沒有人 → 錯。")

# 4 ─ 坐著用電腦（手伸到桌面）
dsvg = desk()
fs, hip, sh = sit(150, GY, 96, 1)
b = [dsvg, box(196, 70, 62, 44), ln(227, 114, 227, 118), ln(214, 118, 240, 118), fs,
     poly([sh, (sh[0] + 22, sh[1] + 16), (168, 114)]),
     ln(hip[0] - 15, hip[1] + 6, hip[0] + 17, hip[1] + 6),
     ln(hip[0] - 15, hip[1] + 6, hip[0] - 15, hip[1] - 34),
     ln(hip[0] + 2, hip[1] + 6, hip[0] + 2, GY)]
add("p1-004", "辦公室・使用電腦", "A woman working at a computer",
    G + "".join(b),
    ["A woman is working at a computer.",
     "She's unplugging a monitor.",
     "The desk has been cleared off.",
     "She's standing beside a filing cabinet."],
    "★ 有人、在動作 → 進行式。\n"
    "★ (C) the desk has been cleared off 是「桌子被清空」，但桌上有電腦 —— "
    "Part 1 很愛用文法正確但與畫面不符的完成被動當陷阱。")

# 5 ─ 停放的腳踏車（無人）
b = [bicycle(40 + i * 92, GY - 18) for i in range(3)]
add("p1-005", "街道・停放的腳踏車", "Bicycles parked in a row, nobody nearby",
    G + "".join(b),
    ["Bicycles have been parked in a row.",
     "Cyclists are riding along a path.",
     "A bicycle is being repaired.",
     "Someone is locking up a bicycle."],
    "★ 沒有人 → 所有含 cyclists／someone 的選項直接刪。\n"
    "★ is being repaired 同樣需要有人在修。")

# 6 ─ 推推車的人（雙手在把手上）
cart_x, cart_y = 196.0, 120.0
b = [box(cart_x, cart_y, 74, 46), circ(cart_x + 16, GY - 7, 7), circ(cart_x + 58, GY - 7, 7),
     ln(cart_x, cart_y, cart_x - 22, cart_y - 14)]
add("p1-006", "倉庫・推推車的人", "A man pushing a cart",
    G + "".join(b) + both_to(140, GY, cart_x - 22, cart_y - 14, PH, 8, LEG_STRIDE),
    ["A man is pushing a cart.",
     "A cart has been left unattended.",
     "He's loading boxes onto a shelf.",
     "The cart is being repaired."],
    "★ 有人正在推 → 進行式。\n"
    "★ (B) unattended（無人看管）與畫面矛盾 —— 人就在把手上。")

# 7 ─ 貨架上的商品（無人）
b = [ln(56, 44, 56, GY), ln(264, 44, 264, GY)]
for i in range(4):
    yy = 60 + i * 40
    b.append(ln(56, yy, 264, yy, THIN))
    for j in range(6):
        b.append(box(66 + j * 34, yy - 26, 22, 26))
add("p1-007", "商店・貨架上的商品", "Products displayed on shelves, no shoppers",
    "".join(b),
    ["Merchandise is displayed on shelves.",
     "A customer is reaching for an item.",
     "The shelves are being restocked.",
     "Products are being scanned at a register."],
    "★ 空店：沒有 customer、沒有人在補貨。\n"
    "★ is displayed 是狀態描述，不需要動作者，這種寫法在無人畫面裡最常當正解。")

# 8 ─ 兩人握手（手在中間相接）
mx, my = 160.0, 128.0
la, ra = shoulder_of(112, GY), shoulder_of(208, GY)
b = [figure(112, GY, [arm_to(mx - la[0], my - la[1]), ((-11, 14), (-14, 30))], LEG_STAND),
     figure(208, GY, [arm_to(mx - ra[0], my - ra[1], -1), ((11, 14), (14, 30))], LEG_STAND),
     circ(mx, my, 5, THIN)]
add("p1-008", "辦公室・兩人握手", "Two people shaking hands",
    G + "".join(b),
    ["They're shaking hands.",
     "They're carrying luggage.",
     "One of them is pointing at a screen.",
     "They're seated across from each other."],
    "★ 兩個人 → 主詞用 They're。\n"
    "★ (D) seated 與畫面矛盾，兩人都站著 —— Part 1 常拿 standing/seated 互換當陷阱。")

# 9 ─ 加油站停著的車（無人）
b = [poly([(50, 152), (50, 126), (76, 100), (140, 100), (162, 126), (186, 126), (186, 152)]),
     ln(50, 152, 186, 152, THIN), circ(78, 158, 15), circ(158, 158, 15),
     ln(76, 100, 82, 126), ln(140, 100, 136, 126), ln(50, 126, 186, 126, THIN),
     box(238, 92, 36, 80), ln(238, 108, 206, 124), circ(256, 104, 6, THIN)]
add("p1-009", "加油站・停著的車", "A car parked next to a fuel pump, no driver",
    G + "".join(b),
    ["A vehicle is parked beside a pump.",
     "A man is filling up his tank.",
     "The car is being washed.",
     "Cars are lined up at a traffic light."],
    "★ 沒有人 → filling up 與 being washed 都要有人。\n"
    "★ is parked 是狀態，最適合無人的靜態畫面。")

# 10 ─ 澆花的人（水壺在手上、對著花）
b = []
for i in range(3):
    px = 214 + i * 32
    b.append(ln(px, GY, px, GY - 34))
    b.append(circ(px, GY - 42, 9))
# 水壺：壺身 + 上提把 + 斜向下的壺嘴，再加水流，才看得出「正在澆」
can = (178.0, 112.0)
b.append(box(can[0] - 16, can[1] - 6, 30, 26))
b.append(poly([(can[0] - 10, can[1] - 6), (can[0] - 2, can[1] - 18), (can[0] + 8, can[1] - 6)], THIN))
b.append(poly([(can[0] + 14, can[1] - 2), (can[0] + 32, can[1] + 6), (can[0] + 38, can[1] + 16)]))
for k in range(3):
    b.append(ln(can[0] + 40 + k * 5, can[1] + 22 + k * 9,
                can[0] + 43 + k * 5, can[1] + 30 + k * 9, THIN))
add("p1-010", "花園・澆花的人", "A woman watering plants",
    G + "".join(b) + reach(132, GY, can[0] - 18, can[1] + 4),
    ["A woman is watering some plants.",
     "She's trimming a hedge.",
     "The plants have been moved indoors.",
     "Flowers are being arranged in a vase."],
    "★ 有人正在做 → 進行式。\n"
    "★ (C) moved indoors 與畫面矛盾（植物在戶外地上）。")

# 11 ─ 撐開的陽傘（無人）
b = []
for i in range(2):
    cx = 96 + i * 118
    b.append(ln(cx, GY, cx, 62))
    b.append(poly([(cx - 52, 78), (cx - 26, 52), (cx, 44), (cx + 26, 52), (cx + 52, 78)]))
    b.append(ln(cx - 52, 78, cx + 52, 78, THIN))
    b.append('<ellipse cx="%.1f" cy="150" rx="34" ry="9" %s/>' % (cx, ST))
add("p1-011", "露台・撐開的陽傘", "Open patio umbrellas over tables, no people",
    G + "".join(b),
    ["Umbrellas have been opened above the tables.",
     "A server is clearing a table.",
     "The umbrellas are being folded up.",
     "Diners are seated outdoors."],
    "★ 傘已經撐開、沒人在動它 → have been opened。\n"
    "★ being folded up 需要有人在收。")

# 12 ─ 漆牆的人（滾筒貼著牆）
wx = 236.0
roll = (wx - 16, 96.0)
b = [wall(wx), box(wx + 4, 52, 76, 108, THIN),
     box(roll[0] - 7, roll[1] - 12, 14, 22), ln(roll[0], roll[1] + 10, roll[0] - 4, roll[1] + 20)]
add("p1-012", "室內・漆牆的人", "A man painting a wall with a roller",
    G + "".join(b) + reach(168, GY, roll[0] - 6, roll[1] + 16),
    ["A man is painting a wall.",
     "He's hanging a picture.",
     "The wall is being torn down.",
     "Paint cans have been stacked in a corner."],
    "★ 有人正在漆 → 進行式。\n"
    "★ 注意 (C)：the wall is being torn down 文法對、也用了 being V-ed，但動作跟畫面不符。"
    "**being V-ed 不是萬用正解，要真的在做那件事。**")

# 13 ─ 路上的三角錐（無人）
b = [ln(6, 116, W - 6, 116, 'stroke="currentColor" fill="none" stroke-width="2.2" '
                            'stroke-dasharray="14 12" opacity=".4"')]
for i in range(4):
    cx = 58 + i * 62
    b.append(poly([(cx - 16, GY - 6), (cx, GY - 52), (cx + 16, GY - 6)]))
    b.append(ln(cx - 22, GY - 6, cx + 22, GY - 6))
    b.append(ln(cx - 8, GY - 24, cx + 8, GY - 24, THIN))
add("p1-013", "道路・擺放的三角錐", "Traffic cones placed on a road, no workers",
    G + "".join(b),
    ["Cones have been placed along the road.",
     "Workers are repaving the street.",
     "The cones are being removed.",
     "A vehicle is driving between the cones."],
    "★ 沒有人、沒有車 → 只剩狀態描述可選。\n"
    "★ 這一題和 p1-001 是同一個考點的不同外觀，練到反射為止。")

# 14 ─ 看文件的人（紙拿在雙手之間）
paper = (196.0, 116.0)
b = [box(paper[0] - 20, paper[1] - 14, 40, 28), ln(paper[0] - 12, paper[1] - 6, paper[0] + 12, paper[1] - 6, THIN),
     ln(paper[0] - 12, paper[1] + 2, paper[0] + 12, paper[1] + 2, THIN)]
add("p1-014", "辦公室・看文件的人", "A man examining a document",
    G + "".join(b) + both_to(148, GY, paper[0] - 22, paper[1]),
    ["A man is looking at a document.",
     "He's signing a contract with a pen.",
     "Papers have been thrown away.",
     "He's speaking on the telephone."],
    "★ 動作要選畫面撐得住的那個。手上拿著紙在看 → looking at。\n"
    "★ (B) 多了一支筆、(D) 多了一支電話 —— 畫面沒有的東西不能選。")

# 15 ─ 晾著的衣物（無人）
b = [ln(44, 74, 276, 82), ln(44, 74, 44, GY), ln(276, 82, 276, GY)]
for i in range(4):
    x = 70 + i * 50
    y = 76 + i * 2
    b.append(box(x, y, 32, 44))
    b.append(ln(x + 6, y, x + 6, y - 6, THIN))
    b.append(ln(x + 26, y, x + 26, y - 6, THIN))
add("p1-015", "戶外・晾著的衣物", "Laundry hanging on a line outdoors",
    G + "".join(b),
    ["Clothing has been hung out to dry.",
     "A woman is folding towels.",
     "The laundry is being taken down.",
     "Clothes are piled in a basket."],
    "★ 東西已經掛好、沒人在動 → has been hung。\n"
    "★ (D) piled in a basket 與畫面矛盾。")

# 16 ─ 站牌下等車的人（長椅是空的）
b = [ln(84, 62, 250, 62), ln(90, 62, 90, GY), ln(244, 62, 244, GY),
     ln(102, 138, 164, 138), ln(108, 138, 108, GY), ln(158, 138, 158, GY),
     ln(102, 138, 102, 116)]
add("p1-016", "站牌・等車的人", "A woman standing under a bus shelter, bench empty",
    G + "".join(b) + stand(206, GY),
    ["A woman is standing under a shelter.",
     "She's boarding a bus.",
     "Passengers are getting off a train.",
     "The bench is occupied."],
    "★ 人站著、長椅是空的 → (D) occupied 錯。\n"
    "★ (B)(C) 都出現了畫面上沒有的交通工具。")

# 17 ─ 工作台上排好的工具（無人）
b = [box(44, 116, 232, 9), ln(58, 125, 58, GY), ln(262, 125, 262, GY),
     ln(76, 116, 76, 92), ln(68, 92, 84, 92),
     poly([(112, 116), (112, 100), (130, 84)]),
     box(154, 98, 34, 18), circ(224, 104, 11), circ(224, 104, 4, THIN)]
add("p1-017", "工作台・排好的工具", "Tools laid out on a workbench, nobody present",
    G + "".join(b),
    ["Tools have been laid out on a workbench.",
     "A mechanic is repairing an engine.",
     "The tools are being put away.",
     "Equipment is stored in a cabinet."],
    "★ 無人 → 排除所有動作者。\n"
    "★ (D) stored in a cabinet 與畫面矛盾（工具在台面上，不在櫃子裡）。")

# 18 ─ 掃地的人（掃把柄在雙手上、刷頭在地）
grip = (168.0, 128.0)
b = [ln(grip[0], grip[1], 212, GY - 4),
     ln(204, GY - 8, 226, GY, 'stroke="currentColor" fill="none" stroke-width="7" stroke-linecap="round"')]
add("p1-018", "室內・掃地的人", "A man sweeping the floor",
    G + "".join(b) + both_to(132, GY, grip[0] - 4, grip[1], PH, 6, LEG_STRIDE),
    ["A man is sweeping the floor.",
     "He's mopping up a spill.",
     "The floor has been carpeted.",
     "He's leaning against a broom."],
    "★ (D) leaning against 是「靠著不動」，跟正在掃是不同動作 —— "
    "Part 1 最愛用同一個道具配錯誤動作。")

# 19 ─ 繫在碼頭的船（無人）
b = [ln(6, 152, W - 6, 152, FAINT), box(24, 116, 88, 14),
     ln(40, 130, 40, 152), ln(96, 130, 96, 152),
     poly([(146, 118), (266, 118), (248, 156), (164, 156), (146, 118)]),
     ln(200, 118, 200, 66), ln(200, 70, 232, 112), ln(200, 112, 232, 112, THIN),
     poly([(112, 124), (130, 130), (148, 126)], THIN)]
add("p1-019", "碼頭・繫好的船", "A boat tied up at a dock, no one aboard",
    "".join(b),
    ["A boat is tied up at a dock.",
     "Passengers are boarding a ferry.",
     "The boat is being launched into the water.",
     "Sails are being raised."],
    "★ 無人 → boarding、being launched、being raised 全部要有人。\n"
    "★ is tied up 是狀態，符合停泊不動的畫面。")

# 20 ─ 兩人看螢幕（都面向螢幕，一人伸手指）
scr = (146.0, 74.0, 76.0, 50.0)
b = [box(*scr), ln(184, 124, 184, 136), ln(166, 136, 202, 136), box(132, 136, 104, 8)]
ra = shoulder_of(258, GY)
b.append(figure(258, GY, [arm_to(scr[0] + scr[2] - 6 - ra[0], scr[1] + 34 - ra[1], -1),
                          ((11, 14), (14, 30))], LEG_STAND))
b.append(stand(96, GY))
add("p1-020", "辦公室・兩人看螢幕", "Two people looking at a monitor together",
    G + "".join(b),
    ["They're looking at a monitor.",
     "They're moving a desk.",
     "One of them is turning off a light.",
     "The screen has been unplugged."],
    "★ 兩人共同面向螢幕 → They're looking at。\n"
    "★ 有人伸手指著螢幕，但沒有在搬桌子或關燈 —— 畫面裡沒有的動作不能選。")

# 21 ─ 報架上的報紙（無人）
b = [ln(76, 52, 76, GY), ln(244, 52, 244, GY)]
for i in range(3):
    yy = 72 + i * 40
    b.append(ln(76, yy, 244, yy, THIN))
    for j in range(3):
        x = 88 + j * 54
        b.append(box(x, yy - 28, 40, 28))
        b.append(ln(x + 20, yy - 28, x + 20, yy, THIN))
add("p1-021", "書報架・擺放的報紙", "Newspapers placed on a rack, no customers",
    G + "".join(b),
    ["Newspapers have been placed on a rack.",
     "A man is buying a newspaper.",
     "The rack is being refilled.",
     "Magazines are scattered on the ground."],
    "★ 無人 → 排除 (B)(C)。\n"
    "★ (D) scattered on the ground 與畫面矛盾（東西整齊放在架上）。")

# 22 ─ 端托盤的服務生（托盤在手上）
tray = (188.0, 122.0)
b = [ln(tray[0] - 26, tray[1], tray[0] + 26, tray[1]),
     circ(tray[0] - 12, tray[1] - 8, 7), circ(tray[0] + 10, tray[1] - 8, 7),
     box(238, 132, 74, 8), ln(248, 140, 248, GY), ln(302, 140, 302, GY)]
add("p1-022", "餐廳・端托盤的服務生", "A server carrying a tray",
    G + "".join(b) + both_to(132, GY, tray[0] - 28, tray[1] + 2),
    ["A server is carrying a tray.",
     "She's setting a table.",
     "The tray has been placed on a table.",
     "Customers are being seated."],
    "★ 托盤在手上 → carrying；(C) placed on a table 與畫面矛盾。\n"
    "★ (D) 畫面沒有顧客。")

# 23 ─ 空梯子靠牆（p1-002 的對照組）
lad2, _ = ladder()
add("p1-023", "牆邊・靠著的空梯子", "An empty ladder leaning against a wall",
    G + wall(236) + lad2,
    ["A ladder is leaning against a wall.",
     "A man is climbing a ladder.",
     "The ladder is being carried away.",
     "A ladder has been laid on the ground."],
    "★ **跟 p1-002 是刻意做的一對。** 同樣的梯子，差別只在有沒有人：\n"
    "  有人在上面 → A man is standing on a ladder.\n"
    "  沒人 → A ladder is leaning against a wall.\n"
    "★ (D) laid on the ground 與畫面矛盾（梯子是靠著的，不是躺著的）。")

# 24 ─ 拉開抽屜（有一格是拉出來的，手伸過去）
cab = (196.0, 84.0, 78.0, 96.0)
b = [box(cab[0], cab[1], cab[2], cab[3]),
     ln(cab[0], cab[1] + 32, cab[0] + cab[2], cab[1] + 32, THIN),
     ln(cab[0], cab[1] + 64, cab[0] + cab[2], cab[1] + 64, THIN),
     box(cab[0] - 32, cab[1] + 36, 34, 26),
     ln(cab[0] - 32, cab[1] + 36, cab[0], cab[1] + 32, THIN),
     ln(cab[0] - 32, cab[1] + 62, cab[0], cab[1] + 64, THIN)]
add("p1-024", "辦公室・拉開抽屜", "A woman opening a filing cabinet drawer",
    G + "".join(b) + reach(120, GY, cab[0] - 30, cab[1] + 40),
    ["A woman is opening a drawer.",
     "She's locking a cabinet.",
     "The drawers have all been closed.",
     "Files are being shredded."],
    "★ 有一格抽屜是拉開的、人手伸過去 → is opening。\n"
    "★ (C) have all been closed 與畫面矛盾 —— 完成被動的陷阱通常就是「狀態寫反」。")


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "items1", "batch01.json")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with io.open(OUT, "w", encoding="utf-8") as f:
        json.dump(ITEMS, f, ensure_ascii=False, indent=1)
    sizes = [len(x["svg"]) for x in ITEMS]
    print(u"寫出 {} 題，SVG 平均 {:.0f} 位元組，合計 {:.1f} KB".format(
        len(ITEMS), sum(sizes) / float(len(sizes)), sum(sizes) / 1024.0))
    bad = [x["id"] for x in ITEMS if len(set(x["choices"])) != 4]
    print(u"選項檢查：" + (u"通過" if not bad else u"有問題 {}".format(bad)))

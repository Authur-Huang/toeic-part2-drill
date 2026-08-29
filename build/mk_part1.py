# -*- coding: utf-8 -*-
"""產生 items1/batch01.json（Part 1 照片描述，24 題）。

★ 這裡的圖是**自己畫的 SVG，不是照片**。做得到與做不到要講清楚：

  做得到：is being V-ed 與 have been V-ed 的分辨（Part 1 最大的考點）、
          位置介系詞、畫面裡到底有沒有人、物品在但動作不存在。
  做不到：leaning／kneeling 這類細緻姿態，以及真實照片才有的曖昧地帶。
          所以這批題的定位是**文法反射訓練**，不是 Part 1 模擬。
          真正的 Part 1 手感留給官方 Vol.8 那 12 題。

人形統一用同一組原件畫，風格才一致；每個人物約 56 單位高，腳踩在 y。
"""
import io, json, os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "items1", "batch01.json")

S = 'stroke="currentColor" fill="none" stroke-width="2.4" stroke-linecap="round"'
SJ = 'stroke="currentColor" fill="none" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"'
FILL = 'fill="currentColor" stroke="none"'


def head(x, y):
    return '<circle cx="{}" cy="{}" r="7" {}/>'.format(x, y - 48, S)


def _p(x, y, arms, legs):
    return (head(x, y)
            + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 41, x, y - 20, S)
            + arms + legs)


def legs_stand(x, y):
    return ('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 20, x - 8, y, S)
            + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 20, x + 8, y, S))


def legs_stride(x, y):
    return ('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 20, x - 12, y, S)
            + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 20, x + 11, y, S))


def stand(x, y):
    """雙手自然下垂"""
    a = ('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 37, x - 10, y - 24, S)
         + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 37, x + 10, y - 24, S))
    return _p(x, y, a, legs_stand(x, y))


def reach(x, y, dx=14, dy=-16):
    """一手往上／往前伸（漆牆、拿架上東西）"""
    a = ('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 37, x + dx, y - 37 + dy, S)
         + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 37, x - 8, y - 24, S))
    return _p(x, y, a, legs_stand(x, y))


def push(x, y):
    """雙手往前平舉（推車）"""
    a = ('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 37, x + 16, y - 33, S)
         + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 36, x + 16, y - 30, S))
    return _p(x, y, a, legs_stride(x, y))


def carry(x, y):
    """雙手前伸端東西"""
    a = ('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 37, x + 13, y - 34, S)
         + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 36, x + 13, y - 31, S))
    return _p(x, y, a, legs_stand(x, y))


def sit(x, y):
    """側坐：臀部在 y-20，腿往前"""
    return (head(x, y - 8)
            + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 49, x, y - 28, S)
            + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 45, x + 15, y - 38, S)
            + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 28, x + 14, y - 28, S)
            + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x + 14, y - 28, x + 14, y, S))


def sweep(x, y):
    """雙手斜握（掃地）"""
    a = ('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 37, x + 12, y - 28, S)
         + '<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(x, y - 30, x + 16, y - 20, S))
    return _p(x, y, a, legs_stride(x, y))


def ground(y=178):
    return '<line x1="10" y1="{}" x2="310" y2="{}" stroke="currentColor" stroke-width="2" opacity=".45"/>'.format(y, y)


def rect(x, y, w, h, extra=""):
    return '<rect x="{}" y="{}" width="{}" height="{}" rx="2" {} {}/>'.format(x, y, w, h, SJ, extra)


def wrap(body, label):
    return ('<svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" '
            'role="img" aria-label="{}">{}</svg>'.format(label, body))


# ─────────────────────────── 24 個場景 ───────────────────────────
# 每題：正解一律寫在 choices[0]，建置時依題號雜湊打散。
G = ground()
SC = []


def add(sid, scene, label, body, choices, note):
    SC.append({"id": sid, "part": 1, "scene": scene,
               "svg": wrap(G + body, label),
               "choices": choices, "answer": 0, "note": note})


add("p1-001", "倉庫・堆好的箱子", "Boxes stacked against a wall, no people",
    '<line x1="40" y1="60" x2="40" y2="178" stroke="currentColor" stroke-width="2.4" opacity=".55"/>'
    + rect(46, 146, 40, 32) + rect(46, 114, 40, 32) + rect(46, 82, 40, 32)
    + rect(90, 146, 40, 32) + rect(90, 114, 40, 32),
    ["Some boxes have been stacked against a wall.",
     "A man is carrying a box.",
     "The boxes are being loaded onto a truck.",
     "Cartons are scattered across the floor."],
    "★ 畫面裡沒有人，所以任何 A man is... 一律錯，being loaded 也錯（沒人在裝）。\n"
    "★ 東西已經放好、沒人在動它 → have been V-ed。這是 Part 1 最常考的一組對比。"),

add("p1-002", "工地・站在梯子上的人", "A man standing on a ladder",
    '<line x1="200" y1="40" x2="200" y2="178" stroke="currentColor" stroke-width="2.4" opacity=".55"/>'
    + '<line x1="150" y1="178" x2="176" y2="60" ' + S + '/>'
    + '<line x1="172" y1="178" x2="196" y2="60" ' + S + '/>'
    + ''.join('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(
        156 + i * 3, 158 - i * 24, 178 + i * 3, 158 - i * 24, S) for i in range(5))
    + reach(120, 120, 16, -14),
    ["A man is standing on a ladder.",
     "A ladder is leaning against a wall with no one on it.",
     "He's folding up a ladder.",
     "Workers are climbing down from a roof."],
    "★ 有人在梯子上 → 用進行式。\n"
    "★ 跟 p1-023 剛好成對：那一題是空梯子靠牆，正解就變成 has been leaned／is leaning。"),

add("p1-003", "會議室・排好的椅子", "Chairs arranged around a table, empty room",
    rect(110, 96, 100, 20)
    + ''.join(rect(96 + i * 44, 122, 22, 26) for i in range(4))
    + ''.join(rect(96 + i * 44, 62, 22, 26) for i in range(4)),
    ["Chairs have been arranged around a table.",
     "People are seated at a conference table.",
     "The chairs are being stacked in a corner.",
     "A meeting is in progress."],
    "★ 空無一人的會議室：有人物的選項全錯。\n"
    "★ being stacked 需要有人在疊，畫面沒有人 → 錯。"),

add("p1-004", "辦公室・使用電腦", "A woman working at a computer",
    rect(150, 120, 120, 8) + '<line x1="160" y1="128" x2="160" y2="178" ' + S + '/>'
    + '<line x1="260" y1="128" x2="260" y2="178" ' + S + '/>'
    + rect(200, 88, 46, 32) + '<line x1="223" y1="120" x2="223" y2="128" ' + S + '/>'
    + sit(130, 178),
    ["A woman is working at a computer.",
     "She's unplugging a monitor.",
     "The desk has been cleared off.",
     "She's standing beside a filing cabinet."],
    "★ 有人、在動作 → 進行式。\n"
    "★ (C) the desk has been cleared off 是「桌子被清空」，但畫面上桌上有東西 —— "
    "Part 1 很愛用文法正確但與畫面不符的完成被動來當陷阱。"),

add("p1-005", "街道・停放的腳踏車", "Bicycles parked in a rack, nobody nearby",
    ''.join('<circle cx="{}" cy="150" r="18" {}/><circle cx="{}" cy="150" r="18" {}/>'
            '<line x1="{}" y1="150" x2="{}" y2="150" {}/>'
            '<line x1="{}" y1="150" x2="{}" y2="118" {}/>'.format(
                70 + i * 80, S, 116 + i * 80, S, 70 + i * 80, 116 + i * 80, S,
                93 + i * 80, 100 + i * 80, S) for i in range(3)),
    ["Bicycles have been parked in a row.",
     "Cyclists are riding along a path.",
     "A bicycle is being repaired.",
     "Someone is locking up a bicycle."],
    "★ 沒有人 → 所有含 cyclists／someone 的選項直接刪。\n"
    "★ is being repaired 同樣需要有人在修。"),

add("p1-006", "倉庫・推推車的人", "A man pushing a cart",
    rect(196, 128, 66, 40)
    + '<circle cx="210" cy="176" r="6" ' + S + '/><circle cx="250" cy="176" r="6" ' + S + '/>'
    + '<line x1="196" y1="128" x2="186" y2="112" ' + S + '/>'
    + push(160, 178),
    ["A man is pushing a cart.",
     "A cart has been left unattended.",
     "He's loading boxes onto a shelf.",
     "The cart is being repaired."],
    "★ 有人正在推 → 進行式。\n"
    "★ (B) unattended（無人看管）與畫面矛盾 —— 人就在旁邊。"),

add("p1-007", "商店・貨架上的商品", "Products displayed on shelves, no shoppers",
    ''.join('<line x1="60" y1="{}" x2="260" y2="{}" {}/>'.format(60 + i * 38, 60 + i * 38, S)
            for i in range(4))
    + ''.join('<rect x="{}" y="{}" width="16" height="22" {}/>'.format(
        70 + j * 26, 38 + i * 38, SJ) for i in range(3) for j in range(7)),
    ["Merchandise is displayed on shelves.",
     "A customer is reaching for an item.",
     "The shelves are being restocked.",
     "Products are being scanned at a register."],
    "★ 空店：沒有 customer、沒有人在補貨。\n"
    "★ is displayed 是狀態描述，不需要動作者，這種寫法在無人畫面裡最常當正解。"),

add("p1-008", "辦公室・兩人握手", "Two people shaking hands",
    stand(118, 178) + stand(202, 178)
    + '<line x1="128" y1="154" x2="192" y2="154" ' + S + '/>',
    ["They're shaking hands.",
     "They're carrying luggage.",
     "One of them is pointing at a screen.",
     "They're seated across from each other."],
    "★ 兩個人 → 主詞用 They're。\n"
    "★ (D) seated 與畫面矛盾，兩人都站著 —— Part 1 常拿 standing/seated 互換當陷阱。"),

add("p1-009", "加油站・停著的車", "A car parked next to a fuel pump, no driver",
    rect(60, 122, 130, 34)
    + '<path d="M86 122 L104 100 L150 100 L166 122" ' + SJ + '/>'
    + '<circle cx="92" cy="160" r="12" ' + S + '/><circle cx="158" cy="160" r="12" ' + S + '/>'
    + rect(224, 96, 34, 74) + '<line x1="224" y1="112" x2="200" y2="126" ' + S + '/>',
    ["A vehicle is parked beside a pump.",
     "A man is filling up his tank.",
     "The car is being washed.",
     "Cars are lined up at a traffic light."],
    "★ 沒有人 → filling up 與 being washed 都要有人。\n"
    "★ is parked 是狀態，最適合無人的靜態畫面。"),

add("p1-010", "花園・澆花的人", "A woman watering plants",
    ''.join('<line x1="{}" y1="178" x2="{}" y2="146" {}/>'
            '<circle cx="{}" cy="140" r="8" {}/>'.format(200 + i * 34, 200 + i * 34, S,
                                                         200 + i * 34, S) for i in range(3))
    + reach(140, 178, 22, -8)
    + '<path d="M162 149 L182 145 L178 156 Z" ' + SJ + '/>',
    ["A woman is watering some plants.",
     "She's trimming a hedge.",
     "The plants have been moved indoors.",
     "Flowers are being arranged in a vase."],
    "★ 有人正在做 → 進行式。\n"
    "★ (C) moved indoors 與畫面矛盾（植物在戶外地上）。"),

add("p1-011", "露台・撐開的陽傘", "Open patio umbrellas over tables, no people",
    ''.join('<line x1="{}" y1="178" x2="{}" y2="70" {}/>'
            '<path d="M{} 82 Q{} 46 {} 82 Z" {}/>'.format(
                90 + i * 90, 90 + i * 90, S, 48 + i * 90, 90 + i * 90, 132 + i * 90, SJ)
            for i in range(2))
    + '<ellipse cx="90" cy="152" rx="30" ry="8" ' + S + '/>'
    + '<ellipse cx="180" cy="152" rx="30" ry="8" ' + S + '/>',
    ["Umbrellas have been opened above the tables.",
     "A server is clearing a table.",
     "The umbrellas are being folded up.",
     "Diners are seated outdoors."],
    "★ 傘已經撐開、沒人在動它 → have been opened。\n"
    "★ being folded up 需要有人在收。"),

add("p1-012", "室內・漆牆的人", "A man painting a wall with a roller",
    '<line x1="230" y1="30" x2="230" y2="178" stroke="currentColor" stroke-width="2.4" opacity=".55"/>'
    + rect(232, 60, 76, 90, 'opacity=".28"')
    + reach(180, 178, 26, -34)
    + '<line x1="206" y1="107" x2="224" y2="98" ' + S + '/>'
    + rect(222, 88, 12, 16),
    ["A man is painting a wall.",
     "He's hanging a picture.",
     "The wall is being torn down.",
     "Paint cans have been stacked in a corner."],
    "★ 有人正在漆 → 進行式。\n"
    "★ 注意 (C)：the wall is being torn down 文法對、也用了 being V-ed，但動作跟畫面不符。"
    "**being V-ed 不是萬用正解，要真的在做那件事。**"),

add("p1-013", "道路・擺放的三角錐", "Traffic cones placed on a road, no workers",
    ''.join('<path d="M{} 168 L{} 128 L{} 168 Z" {}/>'
            '<line x1="{}" y1="168" x2="{}" y2="168" {}/>'.format(
                70 + i * 60, 84 + i * 60, 98 + i * 60, SJ,
                64 + i * 60, 104 + i * 60, S) for i in range(4))
    + '<line x1="10" y1="112" x2="310" y2="112" stroke="currentColor" stroke-width="2" '
      'stroke-dasharray="12 10" opacity=".4"/>',
    ["Cones have been placed along the road.",
     "Workers are repaving the street.",
     "The cones are being removed.",
     "A vehicle is driving between the cones."],
    "★ 沒有人、沒有車 → 只剩狀態描述可選。\n"
    "★ 這一題和 p1-001 是同一個考點的不同外觀，練到反射為止。"),

add("p1-014", "辦公室・看文件的人", "A man examining a document at a table",
    rect(150, 126, 130, 8) + '<line x1="160" y1="134" x2="160" y2="178" ' + S + '/>'
    + '<line x1="270" y1="134" x2="270" y2="178" ' + S + '/>'
    + rect(196, 108, 34, 18)
    + carry(150, 178),
    ["A man is looking at a document.",
     "He's signing a contract with a pen.",
     "Papers have been thrown away.",
     "He's speaking on the telephone."],
    "★ 動作要選畫面撐得住的那個。手上拿著紙在看 → looking at。\n"
    "★ (B) 多了一支筆、(D) 多了一支電話 —— 畫面沒有的東西不能選。"),

add("p1-015", "戶外・晾著的衣物", "Laundry hanging on a line outdoors",
    '<line x1="50" y1="78" x2="270" y2="86" ' + S + '/>'
    + '<line x1="50" y1="78" x2="50" y2="178" ' + S + '/>'
    + '<line x1="270" y1="86" x2="270" y2="178" ' + S + '/>'
    + ''.join(rect(74 + i * 46, 82 + i * 2, 28, 40) for i in range(4)),
    ["Clothing has been hung out to dry.",
     "A woman is folding towels.",
     "The laundry is being taken down.",
     "Clothes are piled in a basket."],
    "★ 東西已經掛好、沒人在動 → has been hung。\n"
    "★ (D) piled in a basket 與畫面矛盾。"),

add("p1-016", "站牌・等車的人", "A woman waiting under a bus shelter",
    '<line x1="90" y1="70" x2="240" y2="70" ' + S + '/>'
    + '<line x1="96" y1="70" x2="96" y2="178" ' + S + '/>'
    + '<line x1="234" y1="70" x2="234" y2="178" ' + S + '/>'
    + rect(104, 130, 60, 12) + '<line x1="112" y1="142" x2="112" y2="178" ' + S + '/>'
    + '<line x1="156" y1="142" x2="156" y2="178" ' + S + '/>'
    + stand(200, 178),
    ["A woman is standing under a shelter.",
     "She's boarding a bus.",
     "Passengers are getting off a train.",
     "The bench is occupied."],
    "★ 人站著、長椅是空的 → (D) occupied 錯。\n"
    "★ (B)(C) 都出現了畫面上沒有的交通工具。"),

add("p1-017", "工作台・排好的工具", "Tools laid out on a workbench, nobody present",
    rect(50, 116, 220, 10) + '<line x1="62" y1="126" x2="62" y2="178" ' + S + '/>'
    + '<line x1="258" y1="126" x2="258" y2="178" ' + S + '/>'
    + '<line x1="76" y1="116" x2="76" y2="94" ' + S + '/><line x1="70" y1="94" x2="82" y2="94" ' + S + '/>'
    + '<line x1="110" y1="116" x2="126" y2="100" ' + S + '/>'
    + rect(150, 100, 30, 16) + '<circle cx="216" cy="108" r="9" ' + S + '/>',
    ["Tools have been laid out on a workbench.",
     "A mechanic is repairing an engine.",
     "The tools are being put away.",
     "Equipment is stored in a cabinet."],
    "★ 無人 → 排除所有動作者。\n"
    "★ (D) stored in a cabinet 與畫面矛盾（工具在台面上，不在櫃子裡）。"),

add("p1-018", "室內・掃地的人", "A man sweeping the floor",
    sweep(140, 178)
    + '<line x1="156" y1="158" x2="196" y2="176" ' + S + '/>'
    + '<line x1="186" y1="172" x2="206" y2="180" stroke="currentColor" stroke-width="5" '
      'stroke-linecap="round"/>',
    ["A man is sweeping the floor.",
     "He's mopping up a spill.",
     "The floor has been carpeted.",
     "He's leaning against a broom."],
    "★ (D) leaning against 是「靠著不動」，跟正在掃是不同動作 —— "
    "Part 1 最愛用同一個道具配錯誤動作。"),

add("p1-019", "碼頭・繫好的船", "A boat tied up at a dock, no one aboard",
    '<line x1="10" y1="150" x2="310" y2="150" stroke="currentColor" stroke-width="2" opacity=".4"/>'
    + rect(30, 118, 90, 14)
    + '<line x1="44" y1="132" x2="44" y2="150" ' + S + '/>'
    + '<line x1="104" y1="132" x2="104" y2="150" ' + S + '/>'
    + '<path d="M150 122 L262 122 L246 156 L166 156 Z" ' + SJ + '/>'
    + '<line x1="196" y1="122" x2="196" y2="76" ' + S + '/>'
    + '<line x1="120" y1="126" x2="152" y2="132" ' + S + '/>',
    ["A boat is tied up at a dock.",
     "Passengers are boarding a ferry.",
     "The boat is being launched into the water.",
     "Sails are being raised."],
    "★ 無人 → boarding、being launched、being raised 全部要有人。\n"
    "★ is tied up 是狀態，符合停泊不動的畫面。"),

add("p1-020", "辦公室・兩人看螢幕", "Two people looking at a monitor together",
    rect(150, 84, 74, 46) + '<line x1="187" y1="130" x2="187" y2="142" ' + S + '/>'
    + '<line x1="170" y1="142" x2="204" y2="142" ' + S + '/>'
    + rect(140, 142, 130, 8)
    + stand(96, 178) + reach(266, 178, -22, -34),
    ["They're looking at a monitor.",
     "They're moving a desk.",
     "One of them is turning off a light.",
     "The screen has been unplugged."],
    "★ 兩人共同面向螢幕 → They're looking at。\n"
    "★ 有人伸手指著螢幕，但沒有在搬桌子或關燈 —— 畫面裡沒有的動作不能選。"),

add("p1-021", "書報架・擺放的報紙", "Newspapers placed on a rack, no customers",
    '<line x1="80" y1="60" x2="80" y2="178" ' + S + '/>'
    + '<line x1="240" y1="60" x2="240" y2="178" ' + S + '/>'
    + ''.join('<line x1="80" y1="{}" x2="240" y2="{}" {}/>'.format(76 + i * 34, 76 + i * 34, S)
              for i in range(3))
    + ''.join('<rect x="{}" y="{}" width="34" height="24" {}/>'.format(
        94 + j * 50, 52 + i * 34, SJ) for i in range(3) for j in range(3)),
    ["Newspapers have been placed on a rack.",
     "A man is buying a newspaper.",
     "The rack is being refilled.",
     "Magazines are scattered on the ground."],
    "★ 無人 → 排除 (B)(C)。\n"
    "★ (D) scattered on the ground 與畫面矛盾（東西整齊放在架上）。"),

add("p1-022", "餐廳・端托盤的服務生", "A server carrying a tray",
    carry(120, 178)
    + rect(130, 138, 50, 8)
    + '<circle cx="144" cy="132" r="6" ' + S + '/><circle cx="166" cy="132" r="6" ' + S + '/>'
    + rect(210, 130, 70, 8) + '<line x1="220" y1="138" x2="220" y2="178" ' + S + '/>'
    + '<line x1="270" y1="138" x2="270" y2="178" ' + S + '/>',
    ["A server is carrying a tray.",
     "She's setting a table.",
     "The tray has been placed on a table.",
     "Customers are being seated."],
    "★ 托盤在手上 → carrying；(C) placed on a table 與畫面矛盾。\n"
    "★ (D) 畫面沒有顧客。"),

add("p1-023", "牆邊・靠著的空梯子", "An empty ladder leaning against a wall",
    '<line x1="230" y1="30" x2="230" y2="178" stroke="currentColor" stroke-width="2.4" opacity=".55"/>'
    + '<line x1="150" y1="178" x2="212" y2="54" ' + S + '/>'
    + '<line x1="172" y1="178" x2="232" y2="58" ' + S + '/>'
    + ''.join('<line x1="{}" y1="{}" x2="{}" y2="{}" {}/>'.format(
        158 + i * 12, 162 - i * 24, 180 + i * 12, 166 - i * 24, S) for i in range(5)),
    ["A ladder is leaning against a wall.",
     "A man is climbing a ladder.",
     "The ladder is being carried away.",
     "A ladder has been laid on the ground."],
    "★ **跟 p1-002 是刻意做的一對。** 同樣的梯子，差別只在有沒有人：\n"
    "  有人在上面 → A man is standing on a ladder.\n"
    "  沒人 → A ladder is leaning against a wall.\n"
    "★ (D) laid on the ground 與畫面矛盾（梯子是靠著的，不是躺著的）。"),

add("p1-024", "辦公室・拉開抽屜", "A woman opening a filing cabinet drawer",
    rect(180, 84, 76, 94)
    + '<line x1="180" y1="114" x2="256" y2="114" ' + S + '/>'
    + '<line x1="180" y1="146" x2="256" y2="146" ' + S + '/>'
    + rect(160, 118, 30, 24)
    + reach(120, 178, 30, -38),
    ["A woman is opening a drawer.",
     "She's locking a cabinet.",
     "The drawers have all been closed.",
     "Files are being shredded."],
    "★ 有一格抽屜是拉開的、人手伸過去 → is opening。\n"
    "★ (C) have all been closed 與畫面矛盾 —— 完成被動的陷阱通常就是「狀態寫反」。")


os.makedirs(os.path.dirname(OUT), exist_ok=True)
with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(SC, f, ensure_ascii=False, indent=1)

sizes = [len(x["svg"]) for x in SC]
print(u"寫出 {} 題，SVG 平均 {:.0f} 位元組（最大 {}），合計 {:.1f} KB".format(
    len(SC), sum(sizes) / float(len(sizes)), max(sizes), sum(sizes) / 1024.0))
bad = [x["id"] for x in SC if len(set(x["choices"])) != 4 or len(x["choices"]) != 4]
print(u"選項檢查：" + (u"通過" if not bad else u"有問題 {}".format(bad)))

# -*- coding: utf-8 -*-
u"""把 p1-025 ~ p1-096 的逐選項解析與難度併進 notes/p1.json（2026-09-01）。

why 依**題庫原始順序**（items1/batch*.json 的 choices，正解一律在 [0]），
enrich.py 會依選項文字對到 App 打散後的位置。level：1 基礎／2 標準／3 進階。

跑完要接著跑 enrich.py，解析才會進到 docs/items1.json。
"""
import io, json, os, sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

N = {
"p1-025": (2, [
 u"✓ 正解。有人、手按在面板上 → 進行式。operate 操作（機器）。",
 u"✗ unplug 拔掉插頭，是「已經被拔掉」的狀態，但畫面看不到插頭 —— 看不見的事不能選。",
 u"✗ scatter 散落一地。地上沒有紙。",
 u"✗ repair 修理。同樣是有人在動機器，但畫面看不出在修 —— ★ 有人動作也要挑對動詞。"]),
"p1-026": (1, [
 u"✓ 正解。紙留在出紙匣、現場沒有人 → have been left in（結果狀態）。tray 紙匣。",
 u"✗ 畫面裡沒有人。make copies 影印。",
 u"✗ be being V-ed 一定要有人正在做這個動作。",
 u"✗ feed A into B 把 A 送進 B，同樣需要動作者。"]),
"p1-027": (2, [
 u"✓ 正解。手還在板面上、板上已經有字 → is writing。",
 u"✗ wipe clean 擦乾淨，與「板上有字」矛盾。★ 完成被動的陷阱多半是狀態寫反。",
 u"✗ hang 掛。畫面沒有海報。",
 u"✗ hand out 發放。畫面沒有講義，也沒有第二個人。"]),
"p1-028": (1, [
 u"✓ 正解。板面全空、沒有人 → have been wiped clean。",
 u"✗ erase 擦掉，需要有人正在擦。",
 u"✗ give a presentation 做簡報，需要人。",
 u"✗ take notes 抄筆記，需要人。★ 這題四個選項都跟白板有關，能刪的依據只有「畫面裡有沒有人」。"]),
"p1-029": (1, [
 u"✓ 正解。排好、沒人動 → have been lined up on。line up 排成一列。",
 u"✗ pour 倒。畫面無人。",
 u"✗ 被動進行式要有人正在洗。",
 u"✗ wait in line 排隊。畫面沒有客人。⚠ line up（把東西排好）與 wait in line（人排隊）長得像，考的是不同畫面。"]),
"p1-030": (2, [
 u"✓ 正解。有人拿著壺正在倒 → 被動進行式，主詞放在被處理的東西上。beverage 飲料。",
 u"✗ put away 收起來，但杯子就在檯面上。",
 u"✗ wipe down 擦拭。手上拿的是壺不是抹布。",
 u"✗ pay for 付錢。畫面只有一個人。"]),
"p1-031": (2, [
 u"✓ 正解。set the table 擺餐具，是 Part 1 的固定用法。",
 u"✗ serve 上菜。被動進行式要有人，畫面沒有。diner 用餐的人。",
 u"✗ clear 收走。需要服務生。",
 u"✗ stack in a pile 疊成一疊，與「分開擺好」矛盾。"]),
"p1-032": (2, [
 u"✓ 正解。兩人坐著面對面 → be seated across from each other。",
 u"✗ 站著、門口，兩處都不符。★ 站與坐是 Part 1 最常互換的一組陷阱。",
 u"✗ serve food 上菜。兩人都坐著，沒有人在服務。",
 u"✗ push under 推到桌子底下，但椅子上有人坐著。"]),
"p1-033": (1, [
 u"✓ 正解。雙手在把手上 → pushing。",
 u"✗ leave 留下，需要「沒有人」。人就在車後面。aisle 走道。",
 u"✗ lift onto 抬上去。畫面沒有籃子也沒有貨架。",
 u"✗ bag（動詞）裝袋，需要有人在裝。grocery 食品雜貨。"]),
"p1-034": (2, [
 u"✓ 正解。有人正在放 → 被動進行式。place A into B。",
 u"✗ 袋子在檯面上不在地上，位置錯；而且袋子不是空的。",
 u"✗ unload 卸下。畫面沒有購物車。",
 u"✗ restock 補貨。畫面沒有貨架。"]),
"p1-035": (2, [
 u"✓ 正解。架子大半空著 → have been emptied。",
 u"✗ fully stocked 補得滿滿的，與畫面正好相反。",
 u"✗ clerk 店員。畫面無人。",
 u"✗ browse 逛、瀏覽。需要客人。"]),
"p1-036": (2, [
 u"✓ 正解。有人正在掃描 → 被動進行式。register 收銀機。",
 u"✗ unattended 無人看管，但人就在櫃檯後面。",
 u"✗ count money 數錢。手上是商品不是錢。",
 u"✗ 畫面只有一個人，沒有排隊的客人。"]),
"p1-037": (1, [
 u"✓ 正解。人站在月台上、沒有車 → waiting on a platform。",
 u"✗ pull into 進站。畫面沒有車。",
 u"✗ board 上車，同樣需要車。★ 選項提到畫面上不存在的東西，直接刪。",
 u"✗ close off 封閉。月台是通的。"]),
"p1-038": (1, [
 u"✓ 正解。車停著、沒有人 → has stopped alongside。alongside 沿著…旁邊。",
 u"✗ get off 下車。畫面無人。",
 u"✗ 被動進行式要有人在清。",
 u"✗ conductor 列車長。畫面無人。"]),
"p1-039": (3, [
 u"✓ 正解。排成一列、沒有人 → has been lined up in a row。⚠ luggage 是不可數名詞，動詞用 has。",
 u"✗ check in 辦託運。畫面無人。",
 u"✗ 被動進行式要有人在搬。",
 u"✗ 動詞形態完全正確，錯在**地點**：畫面沒有輸送帶。★ 完成被動的陷阱，一半以上錯在地點介系詞。"]),
"p1-040": (2, [
 u"✓ 正解。手在拉桿上、箱子還在地上滾 → pulling。",
 u"✗ lift onto 抬上去，但箱子沒有離地。★ 有人動作也要挑對動詞，不是有人就選。",
 u"✗ unattended 無人看管，需要沒有人。",
 u"✗ weigh 秤重。畫面沒有磅秤櫃檯。"]),
"p1-041": (2, [
 u"✓ 正解。有人握著油槍對著車 → 被動進行式。refuel 加油。",
 u"✗ 與畫面矛盾，人就在旁邊。",
 u"✗ windshield 擋風玻璃。手上是油槍不是抹布。",
 u"✗ shut off 關掉，畫面看不出來。★ 看不出來的不能選。"]),
"p1-042": (2, [
 u"✓ 正解。有人拿水管對著車 → is being washed。",
 u"✗ garage 車庫，畫面在戶外。",
 u"✗ change a tire 換輪胎。人站在車頭邊拿著水管。",
 u"✗ hood 引擎蓋、prop open 撐開著。畫面裡引擎蓋是關的。"]),
"p1-043": (1, [
 u"✓ 正解。空長椅 → 完成被動＋位置（under 在…下面）。shelter 遮蔽處、候車亭。",
 u"✗ 長椅上沒有人坐。",
 u"✗ repaint 重漆，需要有人。",
 u"✗ 畫面無人。"]),
"p1-044": (2, [
 u"✓ 正解。人坐在長椅上 → is sitting on。",
 u"✗ unoccupied 沒人坐 —— 那是 p1-043 的正解，這兩題就是要你聽出這個差別。",
 u"✗ get up 起身，人還坐著。",
 u"✗ 被動進行式要有人在搬。sidewalk 人行道。"]),
"p1-045": (2, [
 u"✓ 正解。工具碰到樹冠 → is being trimmed。trim 修剪。",
 u"✗ pile up 堆起來。地上沒有樹枝堆。",
 u"✗ plant 種。樹已經長好了，不是在種。",
 u"✗ rake 用耙子耙。那是 p1-047 的動作。"]),
"p1-046": (3, [
 u"✓ 正解。器材架好、沒有人 → have been set up on。lawn 草坪。",
 u"✗ 畫面無人。water（動詞）澆水。",
 u"✗ mow 割草，需要有人推割草機。",
 u"✗ 文法完全正確，但畫面沒有水管盤也沒有工具間。coil 盤繞、shed 工具間。★ 背景物件對不上就是錯。"]),
"p1-047": (2, [
 u"✓ 正解。耙子落在地上的葉子中間 → raking。",
 u"✗ clear away 清光，但葉子還在地上。狀態寫反。",
 u"✗ hallway 走廊，畫面在戶外。sweep 掃。",
 u"✗ 畫面沒有袋子，也不是草。"]),
"p1-048": (1, [
 u"✓ 正解。along a curb 沿著路緣。curb 路緣、人行道邊石。",
 u"✗ 被動進行式要有人在收。trash 垃圾。",
 u"✗ empty（動詞）倒空，需要有人。container 容器。",
 u"✗ knock over 撞倒。桶子立得好好的。"]),
"p1-049": (1, [
 u"✓ 正解。架子搭好、沒有人 → have been set up beside。scaffolding 鷹架（不可數）。",
 u"✗ 畫面無人。climb 攀爬。",
 u"✗ take down 拆掉，被動進行式要有人。",
 u"✗ 同樣需要有人在漆。"]),
"p1-050": (2, [
 u"✓ 正解。人站在踏板上 → standing on。platform 平台、踏板。",
 u"✗ left empty 空著沒人，但人就在上面。",
 u"✗ 畫面沒有梯子。site 工地。",
 u"✗ crane 吊車，畫面沒有；而且只有一個人。"]),
"p1-051": (2, [
 u"✓ 正解。疊好、沒人動 → have been stacked on。",
 u"✗ lay bricks 砌磚，需要人。",
 u"✗ 畫面沒有卡車，也沒有人。unload from 從…卸下。",
 u"✗ 磚是蓋牆用的，但畫面沒有人在蓋 —— ★ 材料在，不等於工程正在進行。"]),
"p1-052": (1, [
 u"✓ 正解。雙手在把手上 → pushing。wheelbarrow 獨輪手推車。",
 u"✗ 需要「沒有人」。",
 u"✗ fill 裝滿，看不出在裝東西。sand 沙。",
 u"✗ hand A to B 把 A 遞給 B。畫面只有一個人。coworker 同事。"]),
"p1-053": (1, [
 u"✓ 正解。書排好、沒有人 → have been arranged on。",
 u"✗ shelve（動詞）上架，需要人。librarian 圖書館員。",
 u"✗ 被動進行式要有人在放。",
 u"✗ emptied 與畫面矛盾，架上是滿的。"]),
"p1-054": (2, [
 u"✓ 正解。手伸向架上的書 → reach for 伸手去拿。",
 u"✗ an armful of 一大抱，但手上沒有書。★ 數量與姿勢對不上一樣是錯。",
 u"✗ 書都還在架上。remove 移走。",
 u"✗ 畫面沒有桌子。"]),
"p1-055": (1, [
 u"✓ 正解。書攤著、椅子空著 → have been left open。★ left 常搭配「東西擺著沒人管」，Part 1 高頻。",
 u"✗ turn the pages 翻頁，需要人。",
 u"✗ clear 收拾，被動進行式要有人。",
 u"✗ 畫面無人。"]),
"p1-056": (2, [
 u"✓ 正解。一個人在服務另一個人 → 被動進行式，主詞是被服務的那位。guest 客人。",
 u"✗ 有兩個人，不是 empty。lobby 大廳。",
 u"✗ 手上沒有行李。",
 u"✗ 畫面沒有鑰匙與箱子。"]),
"p1-057": (1, [
 u"✓ 正解。車上有行李但沒有人 → unattended 無人看管。",
 u"✗ porter 行李員、wheel away 推走。畫面無人。",
 u"✗ 被動進行式要有人在搬。",
 u"✗ 同樣需要人，畫面也沒有電梯。★ 先數畫面裡有幾個人，再看選項要求幾個人，是 Part 1 最省力的解法。"]),
"p1-058": (1, [
 u"✓ 正解。掛好、沒有人 → have been hung on。hang-hung-hung。artwork 畫作（不可數）。",
 u"✗ take down 取下，被動進行式要有人。",
 u"✗ straighten 扶正，需要人。",
 u"✗ 畫在牆上不在地上，位置錯。"]),
"p1-059": (3, [
 u"✓ 正解。有人扶著畫框 → is being hung on。★ 跟 p1-058 是全題庫最直接的一組 have been V-ed ↔ be being V-ed 對照。",
 u"✗ crookedly 歪歪地。「已經掛好」與「手還扶著」矛盾。",
 u"✗ paint a wall 漆牆。手上是畫框。",
 u"✗ wrap in paper 用紙包起來，畫面沒有。"]),
"p1-060": (2, [
 u"✓ 正解。窗簾往兩側收、窗面全露 → pull back 拉開。",
 u"✗ 畫面無人。close 關上。",
 u"✗ replace 更換，需要有人在裝。",
 u"✗ blinds 百葉窗、lower 放下。★ 換一個相近的名詞來測你有沒有真的在看圖，是 Part 1 的常用手法。"]),
"p1-061": (2, [
 u"✓ 正解。手貼在窗面、拿著抹布 → is being cleaned。",
 u"✗ left open 開著，但窗戶是關的。",
 u"✗ install 安裝，畫面是一扇完好的窗。",
 u"✗ 這張圖沒有窗簾。"]),
"p1-062": (3, [
 u"✓ 正解。無人畫面的另一種正解寫法：**描述東西的相對位置**。handrail 扶手、run alongside 沿著…延伸。",
 u"✗ 畫面無人。",
 u"✗ 被動進行式要有人在修。stairway 樓梯。",
 u"✗ hold onto 抓住，需要人。railing 欄杆。"]),
"p1-063": (2, [
 u"✓ 正解。腳踩在階梯上、跨步 → climbing a staircase。",
 u"✗ lean against 靠著。人是在走，不是靠著。",
 u"✗ block off 封起來，樓梯是通的。",
 u"✗ 方向相反（down），手上也沒有箱子。★ up／down 一定要聽清楚。"]),
"p1-064": (1, [
 u"✓ 正解。鍋子擺著、沒有人 → have been placed on。",
 u"✗ stir 攪拌，需要人。",
 u"✗ 畫面沒有水槽，也沒有人。sink 水槽。",
 u"✗ serve onto 盛到…上，需要人與盤子。"]),
"p1-065": (2, [
 u"✓ 正解。手伸到鍋口、握著長柄 → stirring。",
 u"✗ turned off 關火，畫面看不出來。★ 看不出來的就不能選，Part 1 只描述看得見的事。",
 u"✗ 畫面沒有水槽。do the dishes／wash dishes 洗碗。",
 u"✗ 畫面只有一個人，沒有客人。"]),
"p1-066": (2, [
 u"✓ 正解。有人正在把衣物放進去 → 被動進行式。load A into B。",
 u"✗ 這句只講門開著，但畫面的重點是有人正在放東西進去。",
 u"✗ fold 摺，畫面沒有桌子。laundry 待洗／洗好的衣物。",
 u"✗ hang out to dry 晾乾，那是 p1-015 的正解。★ 同一個主題不同動作，靠畫面分辨。"]),
"p1-067": (2, [
 u"✓ 正解。手伸向投信口、手上有信 → is being dropped into。",
 u"✗ empty（動詞）清空，畫面看不出來。",
 u"✗ open an envelope 拆信，動作相反（是投進去，不是拆開）。",
 u"✗ doorstep 門階，畫面是郵筒不是門口。"]),
"p1-068": (1, [
 u"✓ 正解。三個人站成一排 → standing in a line。",
 u"✗ 站著不是坐著（跟 p1-032 同一種站坐陷阱）。",
 u"✗ clear 清空，隊伍還在。",
 u"✗ 畫面沒有公車。board 上車。"]),
"p1-069": (1, [
 u"✓ 正解。unoccupied 沒人坐，是無人畫面的固定用字。",
 u"✗ 畫面無人。be called 被叫號。",
 u"✗ rearrange 重新排列，被動進行式要有人。",
 u"✗ 沒有人，也沒有窗戶。"]),
"p1-070": (1, [
 u"✓ 正解。東西在手上、人在走 → carrying。folder 文件夾。",
 u"✗ set on 放到…上。畫面沒有桌子。",
 u"✗ spread across 攤開在，同樣沒有桌子。★ 選項提到畫面上沒有的東西就是錯。",
 u"✗ 畫面只有一個人。colleague 同事。"]),
"p1-071": (1, [
 u"✓ 正解。紙釘上去了、沒有人 → have been posted on。post 張貼、notice 公告。",
 u"✗ remove 取下、flyer 傳單。畫面無人。",
 u"✗ 廣播是聽的不是看的，Part 1 不會這樣考。",
 u"✗ blank 空白，與畫面矛盾。"]),
"p1-072": (2, [
 u"✓ 正解。手指向其中一張紙 → point at。",
 u"✗ take down 拆下，那是把整個板子拆掉，動作太大。",
 u"✗ 紙都還在板上。",
 u"✗ 手上沒有筆。sheet of paper 一張紙。"]),
"p1-073": (1, [
 u"✓ 正解。side by side 並排，又一個位置說法。",
 u"✗ 畫面沒有紅綠燈。",
 u"✗ repave 重鋪路面，需要有人與機具。",
 u"✗ get out of 下車。畫面無人。"]),
"p1-074": (2, [
 u"✓ 正解。人在斑馬線上、腳是跨步的 → crossing。",
 u"✗ waiting 是在等 —— ★ 跟 crossing 是 Part 1 最常互換的一組：在等 vs 正在走。",
 u"✗ close to traffic 封閉，路是通的。crosswalk 斑馬線。",
 u"✗ 畫面沒有公車。"]),
"p1-075": (2, [
 u"✓ 正解。無人街景的典型正解：完成被動＋地點。install 安裝。",
 u"✗ 畫面無人。",
 u"✗ tow away 拖吊，畫面沒有車。",
 u"✗ intersection 路口，但畫面沒有車。"]),
"p1-076": (1, [
 u"✓ 正解。人在車上、腳在踏板 → riding along。cyclist 騎士。",
 u"✗ 那是 p1-005 的正解（停好的腳踏車）。rack 停車架。",
 u"✗ flat tire 爆胎。人在騎，不是在修。",
 u"✗ lift onto 抬上去，畫面沒有汽車。"]),
"p1-077": (2, [
 u"✓ 正解。兩人各扶一端、桌子離地 → carrying…together。",
 u"✗ set up 擺好，但桌子還在手上。hallway 走廊。",
 u"✗ 兩人都站著。",
 u"✗ cover with 覆蓋，畫面沒有布。furniture 家具（不可數）。"]),
"p1-078": (2, [
 u"✓ 正解。有人正在把箱子推上車 → 被動進行式。load A onto B。",
 u"✗ fully loaded 已經裝滿，是結果狀態；動作還在進行就不能用。",
 u"✗ 方向相反（unload 卸下），畫面也不是碼頭。crate 木箱、dock 碼頭。",
 u"✗ seal with tape 用膠帶封起來，畫面看不出來。carton 紙箱。"]),
"p1-079": (3, [
 u"✓ 正解。木箱在車外的地上、沒有人 → have been stacked beside。",
 u"✗ 被動進行式要有人在搬。van 廂型車。",
 u"✗ tailgate 後車門。畫面無人。",
 u"✗ 動詞形態一樣正確，錯在**位置**（inside vs beside）。★ Part 1 的完成被動陷阱，一半以上錯在地點介系詞。"]),
"p1-080": (3, [
 u"✓ 正解。手伸到燈具上 → is being replaced。fixture 固定裝置（此處指燈具）。",
 u"✗ switch off 關掉，畫面看不出來。",
 u"✗ 畫面沒有梯子 —— 不能因為「換燈泡通常要梯子」就選。★ 人站在哪裡也要看。",
 u"✗ 燈在牆上不在桌上，位置錯。"]),
"p1-081": (2, [
 u"✓ 正解。鋸子壓在木板上 → sawing。board 木板。",
 u"✗ 那是 p1-082 的正解（疊好的木板）。",
 u"✗ measure 量。手上的工具不一樣。★ 看清楚手上拿的是什麼。",
 u"✗ sawdust 木屑、sweep off 掃掉，畫面沒有。"]),
"p1-082": (1, [
 u"✓ 正解。疊好、沒有人 → have been stacked on。",
 u"✗ carpenter 木匠、lumber 木材。畫面無人。",
 u"✗ 被動進行式要有人在搬。",
 u"✗ 地上沒有工具。★ 位置＋有沒有那個東西，兩個都要對。"]),
"p1-083": (1, [
 u"✓ 正解。人靠在儀器前 → look into 湊近看（顯微鏡、望遠鏡固定用法）。",
 u"✗ put away 收起來，但儀器就擺在檯面上。",
 u"✗ 手上沒有筆記本。",
 u"✗ sample 檢體。畫面沒有人在搬。"]),
"p1-084": (2, [
 u"✓ 正解。器材擺出來、沒有人 → set out 陳列擺放。",
 u"✗ technician 技術員、adjust 調整。畫面無人。",
 u"✗ fill with 裝入，被動進行式要有人。",
 u"✗ cleared of 被清空，與畫面正好相反。"]),
"p1-085": (1, [
 u"✓ 正解。排好、沒有人 → have been arranged in rows。in rows 成排。",
 u"✗ take an exam 考試，需要學生。",
 u"✗ 被動進行式要有人在搬。",
 u"✗ hand out 發放，需要老師。★ 這種題型答對的關鍵只有一句：先數人。"]),
"p1-086": (3, [
 u"✓ 正解。兩人坐著、其中一人手舉起 → One of them is V-ing。",
 u"✗ 兩人都坐著，不是站著。",
 u"✗ left empty 空著，但教室裡有人。",
 u"✗ collect 收（考卷），需要有人在收。"
 u"★ One of them／Both of them／Neither 是 Part 1 分辨兩人動作的固定句型，聽到就要立刻判斷「是一個人還是兩個人在做」。"]),
"p1-087": (1, [
 u"✓ 正解。人在機器上、手扶把手 → exercising on。",
 u"✗ unused 沒在用，但人就在上面。",
 u"✗ lift weights 舉重，畫面沒有啞鈴。",
 u"✗ towel 毛巾、fold 摺。畫面沒有。"]),
"p1-088": (2, [
 u"✓ 正解。排好、沒有人 → have been arranged on a rack。rack 置物架。",
 u"✗ put back 放回去，需要人。dumbbell 啞鈴。",
 u"✗ assemble 組裝，被動進行式要有人。",
 u"✗ on the floor 位置錯，啞鈴在架上。★ 又一個「動詞對、地點錯」。"]),
"p1-089": (3, [
 u"✓ 正解。傘撐開、握把在手上 → holding。",
 u"✗ fold up 收起來，但傘是開的。",
 u"✗ opening 是「正在打開」的那一瞬間，傘已經開好了。★ 動作進行到哪一步也要看。",
 u"✗ 那是 p1-090 的正解（收在傘桶裡）。"]),
"p1-090": (1, [
 u"✓ 正解。收起來插在傘桶裡、沒有人 → have been placed in。stand 架、桶。",
 u"✗ shake out 抖乾。畫面無人。",
 u"✗ hand out 發放，需要人。",
 u"✗ 傘是收著的，不是撐開的。"]),
"p1-091": (1, [
 u"✓ 正解。相機舉在臉前、雙手扶著 → take a photograph。",
 u"✗ tripod 腳架，畫面沒有。",
 u"✗ 相機在臉前，不是在收進包包。",
 u"✗ 牆上沒有照片。"]),
"p1-092": (2, [
 u"✓ 正解。手指伸到面板上 → pressing a button。",
 u"✗ prop open 撐開著，但門是關的。",
 u"✗ step into 跨進去，人還在門外。",
 u"✗ 門邊只有按鈕面板，沒有標示牌。sign 標示。"]),
"p1-093": (1, [
 u"✓ 正解。門板往外開著、門口沒有人 → have been left open。",
 u"✗ walk through 走過去。畫面無人。doorway 門口。",
 u"✗ lock 上鎖，被動進行式要有人。",
 u"✗ block with 用…擋住，門口沒有箱子。"]),
"p1-094": (1, [
 u"✓ 正解。掛在架上、沒有人 → have been hung on。",
 u"✗ put on 穿上。畫面無人。",
 u"✗ hand to 遞給，需要人。",
 u"✗ fold over 摺放在…上，位置與方式都不對（是掛著不是摺著）。"]),
"p1-095": (2, [
 u"✓ 正解。木箱在碼頭上、沒有人 → have been unloaded onto。dock 碼頭。",
 u"✗ 畫面無人。load 裝載。",
 u"✗ cargo 貨物、weigh 秤重，需要有人與磅秤。",
 u"✗ on a boat 位置錯 —— 東西在岸上不在船上。"]),
"p1-096": (3, [
 u"✓ 正解。抹布壓在桌面、有人在擦 → is being wiped down。",
 u"✗ 那是 p1-031 的正解（擺好餐具）；這張桌上是空的。★ 這兩題成對：同一張餐桌，有人動它 vs 沒人。",
 u"✗ pull out 拉開，畫面沒有椅子。",
 u"✗ 手上沒有餐盤。"]),
}


def main():
    path = os.path.join(ROOT, "notes", "p1.json")
    data = json.load(io.open(path, encoding="utf-8"))
    for sid, (level, why) in N.items():
        if len(why) != 4:
            raise SystemExit(u"{}：why 不是四條".format(sid))
        data[sid] = {"level": level, "why": why}
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    n = len([k for k in data if k.startswith("p1-")])
    dist = {1: 0, 2: 0, 3: 0}
    for k, v in data.items():
        if k.startswith("p1-"):
            dist[v["level"]] += 1
    print(u"notes/p1.json 共 {} 題（本次新增／更新 {}），難度 基礎 {}／標準 {}／進階 {}".format(
        n, len(N), dist[1], dist[2], dist[3]))


if __name__ == "__main__":
    main()

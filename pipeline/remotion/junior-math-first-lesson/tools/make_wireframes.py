from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "research" / "wireframes"
OUT.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
BG = (244, 244, 242)
INK = (28, 28, 28)
MUTED = (110, 110, 106)
LINE = (210, 210, 206)
PANEL = (255, 255, 255)
SHADE = (232, 232, 228)

def f(size, bold=False):
    return ImageFont.truetype(FONT, size, index=0)

def text(d, xy, s, size=32, fill=INK, bold=False, anchor="la"):
    d.text(xy, s, font=f(size, bold), fill=fill, anchor=anchor)

def panel(d, box, fill=PANEL, outline=INK, width=3, dash=False):
    d.rectangle(box, fill=fill, outline=outline, width=width)
    if dash:
        # simple corner marks for wireframe
        x1, y1, x2, y2 = box
        for (x, y) in ((x1,y1),(x2,y1),(x1,y2),(x2,y2)):
            d.line([(x-10,y),(x+10,y)], fill=outline, width=2)
            d.line([(x,y-10),(x,y+10)], fill=outline, width=2)

def safe(d):
    d.rectangle([96, 48, 1824, 926], outline=(200,200,196), width=2)
    text(d, (104, 54), "SAFE 96 / 48 / 154", 14, (160,160,156))

def caption(d, s):
    d.rectangle([96, 966, 1824, 1030], fill=SHADE, outline=(190,190,186), width=2)
    text(d, (112, 982), "字幕 · " + s, 24, (70,70,68))

def focus(d, xy, label="FOCAL"):
    x, y = xy
    d.ellipse([x-7,y-7,x+7,y+7], fill=INK)
    text(d, (x+14,y-9), label, 14, MUTED)

def base(title, sub, sid):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for x in range(96, 1825, 124):
        d.line([(x,48),(x,1080)], fill=(238,238,234), width=1)
    safe(d)
    text(d, (96, 18), "WIREFRAME · " + sid, 16, MUTED)
    text(d, (96, 96), title, 54, INK)
    if sub:
        text(d, (96, 166), sub, 26, MUTED)
    return im, d

# S1
im, d = base("S1 开场", "-3℃ 怎么读？0℃ 是没有温度吗？", "S1")
panel(d, (120, 250, 620, 840), width=4)
text(d, (150, 280), "温度计", 24, MUTED)
d.rectangle([240, 330, 300, 760], outline=INK, width=3)
for y, lab in ((360,"3℃"), (500,"0℃"), (700,"-3℃")):
    d.line([(300, y), (360, y)], fill=INK, width=2)
    text(d, (380, y-18), lab, 30, INK)
text(d, (340, 600), "-3℃", 58, INK)
panel(d, (700, 250, 1824, 730), width=4)
text(d, (740, 290), "问题卡", 24, MUTED)
text(d, (740, 350), "天气预报：最低 -3℃", 38)
text(d, (740, 420), "读作：零下三摄氏度 / 负三摄氏度", 34)
text(d, (740, 500), "0℃ 是不是「没有温度」？", 42)
d.rectangle([740, 600, 1780, 610], fill=LINE)
text(d, (740, 640), "先给问题，不先给定义", 24, MUTED)
text(d, (360, 770), "FOCAL: -3℃", 16, MUTED)
caption(d, "天气预报最低 -3℃。这个 -3，读作零下三摄氏度")
im.save(OUT / "s1.png")

# S2
im, d = base("S2 规定", "同一组量，两种规定，符号相反", "S2")
panel(d, (96, 250, 900, 760), width=5)
panel(d, (1020, 250, 1824, 760), width=3)
text(d, (126, 280), "A · 规定收入为正", 30)
text(d, (1050, 280), "B · 规定支出为正", 30)
for (y, a, b, c) in ((380,"收入 200","+200","-200"), (520,"支出 150","-150","+150")):
    text(d, (126, y), a, 30)
    text(d, (620, y), b, 48)
    text(d, (1540, y), c, 48)
    d.line([(126,y+70),(870,y+70)], fill=LINE, width=2)
    d.line([(1050,y+70),(1794,y+70)], fill=LINE, width=2)
text(d, (126, 660), "两种都行，但同一题只能选一种", 24, MUTED)
text(d, (1050, 660), "符号是规定，不是好坏", 24, MUTED)
d.rectangle([900, 430, 1020, 450], fill=INK)
text(d, (920, 460), "VS", 28)
focus(d, (500, 500), "FOCAL 当前规定")
caption(d, "规定收入为正，记 +200、-150；规定支出为正，记 -200、+150")
im.save(OUT / "s2.png")

# S3
im, d = base("S3 0", "0 个 / 0℃ / 0 米：三种 0，两种用法", "S3")
text(d, (860, 210), "0", 120, INK)
text(d, (980, 250), "是分界", 28, INK)
for i, (x, t, sub) in enumerate([
    (96, "0 个苹果", "记数：没有"),
    (650, "0℃", "温度：确定刻度"),
    (1204, "0 米海拔", "基准：海平面"),
]):
    panel(d, (x, 380, x+500, 780), width=4 if i==1 else 3)
    text(d, (x+24, 410), t, 32)
    text(d, (x+24, 470), sub, 24, MUTED)
    d.rectangle([x+24, 540, x+476, 720], fill=SHADE, outline=LINE, width=2)
text(d, (650, 810), "0 既不是正数，也不是负数", 28)
focus(d, (900, 230), "FOCAL 0 分界")
caption(d, "0 个苹果是没有；0℃ 是确定温度；0 米是海平面")
im.save(OUT / "s3.png")

# S4
im, d = base("S4 数轴", "原点、正方向、单位长度；右边总比左边大", "S4")
d.line([(120, 620), (1800, 620)], fill=INK, width=4)
d.line([(1800, 620), (1760, 600)], fill=INK, width=4)
d.line([(1800, 620), (1760, 640)], fill=INK, width=4)
for i in range(-10, 11):
    x = 960 + i*60
    d.line([(x, 610), (x, 630)], fill=INK, width=2)
for x, lab in ((780,"-3"),(900,"-1"),(960,"0"),(1140,"+3")):
    d.ellipse([x-11,609,x+11,631], fill=INK)
    text(d, (x-18, 650), lab, 28, INK)
text(d, (930, 690), "原点", 22, MUTED)
text(d, (1640, 560), "正方向 →", 22, MUTED)
d.line([(960, 740), (1020, 740)], fill=INK, width=3)
text(d, (900, 754), "单位长度：1 格 = 1", 20, MUTED)
panel(d, (1320, 250, 1824, 440), width=3)
text(d, (1344, 280), "预测卡", 24, MUTED)
text(d, (1344, 330), "-3 和 -1，谁大？", 34)
text(d, (1344, 390), "停 2 秒，再看数轴", 22, MUTED)
d.line([(780, 580), (900, 580)], fill=INK, width=3)
text(d, (790, 540), "-3 < -1", 30)
focus(d, (840, 590), "FOCAL 位置")
caption(d, "先画原点、正方向箭头、单位长度，再放点")
im.save(OUT / "s4.png")

# contact sheet
imgs = [Image.open(OUT / ("s%d.png" % i)).resize((960, 540)) for i in range(1,5)]
sheet = Image.new("RGB", (1920, 1080), (255,255,255))
for i, img in enumerate(imgs):
    sheet.paste(img, ((i%2)*960, (i//2)*540))
sheet.save(OUT / "wireframes-contact.png")
print("saved", [p.name for p in OUT.glob("*.png")])
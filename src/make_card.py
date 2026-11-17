"""縦長（2:3）の意味カードを作る。使い方: python3 make_card.py <作品画像> <出力PNG>"""
import sys
from PIL import Image, ImageDraw, ImageFont
import numpy as np

W, H = 1000, 1500
BG = (246, 241, 231)      # 生成り
INK = (60, 24, 28)        # 濃い臙脂寄りの墨
ACCENT = (158, 27, 50)    # 臙脂
GOLD = (196, 160, 70)
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SERIF_R = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

card = {
    "label": "縁起物の意味",
    "title": "だるまの片目",
    "body": [
        "願いごとを決めたら片目を入れ、",
        "叶ったらもう片方を入れる。",
        "だるまは、そんな願掛けの縁起物とされています。",
        "転んでも起き上がる姿から、",
        "「七転び八起き」の象徴とも言われます。",
    ],
    "name": "モダンだるま｜Modern Daruma",
    "footer": "紋処すず MONDOKORO SUZU",
    "cta": "グッズはSUZURIで販売中",
}


def font(path, size):
    return ImageFont.truetype(path, size, index=0)  # index 0 = JP


def cutout(path):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(int)
    # ほぼ白の部分を透明にして、作品だけを切り抜く
    white = (a.min(axis=2) > 238)
    alpha = np.where(white, 0, 255).astype(np.uint8)
    rgba = np.dstack([a.astype(np.uint8), alpha])
    out = Image.fromarray(rgba, "RGBA")
    return out.crop(out.getbbox())


def center(draw, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)


def main(src, dst):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # 枠
    d.rectangle([28, 28, W - 29, H - 29], outline=GOLD, width=3)
    d.rectangle([40, 40, W - 41, H - 41], outline=GOLD, width=1)

    center(d, 92, card["label"], font(SANS, 30), ACCENT)
    center(d, 140, card["title"], font(SERIF, 84), INK)

    art = cutout(src)
    box = 580
    art.thumbnail((box, box), Image.LANCZOS)
    img.paste(art, ((W - art.width) // 2, 280 + (box - art.height) // 2), art)

    y = 900
    fb = font(SERIF_R, 34)
    for line in card["body"]:
        center(d, y, line, fb, INK)
        y += 54

    d.line([(W / 2 - 120, y + 30), (W / 2 + 120, y + 30)], fill=GOLD, width=2)
    center(d, y + 52, card["name"], font(SANS, 30), ACCENT)
    center(d, H - 180, card["cta"], font(SANS, 30), INK)
    center(d, H - 122, card["footer"], font(SERIF, 30), INK)

    img.save(dst, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

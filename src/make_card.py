"""縦長（2:3）の意味カードを作る。

使い方:
  python3 src/make_card.py <key> <作品画像> [出力PNG]
  key は src/cards.json のキー（例: daruma）。出力の既定は cards/<key>_card.png
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1000, 1500
BG = (246, 241, 231)      # 生成り
INK = (60, 24, 28)        # 墨（臙脂寄り）
ACCENT = (158, 27, 50)    # 臙脂
GOLD = (196, 160, 70)
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SERIF_R = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
SANS = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FOOTER = "紋処すず MONDOKORO SUZU"
CTA = "グッズはSUZURIで販売中"


def font(path, size):
    return ImageFont.truetype(path, size, index=0)  # index 0 = JP


def cutout(path):
    src = Image.open(path).convert("RGBA")
    rgba = np.asarray(src)
    a = rgba[..., :3].astype(int)
    white = a.min(axis=2) > 238          # ほぼ白の背景を透明にする
    alpha = np.where(white, 0, rgba[..., 3]).astype(np.uint8)  # 元が透過PNGならその透明度も使う
    out = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")
    return out.crop(out.getbbox())


def center(draw, y, text, f, fill):
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)


def make(card, src, dst):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([28, 28, W - 29, H - 29], outline=GOLD, width=3)
    d.rectangle([40, 40, W - 41, H - 41], outline=GOLD, width=1)

    center(d, 92, card.get("label", "縁起物の意味"), font(SANS, 30), ACCENT)
    center(d, 140, card["title"], font(SERIF, 84), INK)

    art = cutout(src)
    box = 580
    art.thumbnail((box, box), Image.LANCZOS)
    img.paste(art, ((W - art.width) // 2, 280 + (box - art.height) // 2), art)

    y, fb = 900, font(SERIF_R, 34)
    for line in card["body"]:
        assert d.textlength(line, font=fb) < W - 140, f"長すぎる行: {line}"
        center(d, y, line, fb, INK)
        y += 54
    d.line([(W / 2 - 120, y + 30), (W / 2 + 120, y + 30)], fill=GOLD, width=2)
    center(d, y + 52, card["name"], font(SANS, 30), ACCENT)
    center(d, H - 180, CTA, font(SANS, 30), INK)
    center(d, H - 122, FOOTER, font(SERIF, 30), INK)
    img.save(dst, optimize=True)


if __name__ == "__main__":
    key, src = sys.argv[1], sys.argv[2]
    cards = json.loads((ROOT / "src" / "cards.json").read_text(encoding="utf-8"))
    dst = sys.argv[3] if len(sys.argv) > 3 else ROOT / "cards" / f"{key}_card.png"
    make(cards[key], src, dst)
    print(dst)

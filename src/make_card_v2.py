"""紋処すず 意味カード v2（和のしるし / SYMBOLS OF JAPAN）。

使い方:
  ART_DIR=<原本PNGのフォルダ> python3 src/make_card_v2.py <key> [--platform pinterest|threads|all]
                                     [--lang ja|en|all] [--out <出力フォルダ>]
出力: <out>/<key>_<platform>_<lang>.png（既定の出力先は previews/。cards/ の既存画像は上書きしない）

原則:
- 作品の絵は変えない。拡大縮小と、外側の透明余白のトリミングだけを行う
- 透過PNGは元の透明度をそのまま使う。透明度のない画像は外周につながった白だけを背景として抜く
- 文字の位置・幅は textbbox で実測し、はみ出し・重なりがあれば止める
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "src" / "cards_v2.json"

CREAM = "#F4F0E7"
INK = "#243C43"
GOLD = "#B9975A"
DARK = "#252B2A"
MUTED = "#526464"

FONT_DIR = "/usr/share/fonts/opentype/noto"
SERIF_B = f"{FONT_DIR}/NotoSerifCJK-Bold.ttc"     # Noto Serif JP Bold（SIL OFL 1.1）
SERIF_R = f"{FONT_DIR}/NotoSerifCJK-Regular.ttc"
SANS_R = f"{FONT_DIR}/NotoSansCJK-Regular.ttc"    # Noto Sans JP Regular（SIL OFL 1.1）

TAG = {"ja": "和のしるし", "en": "SYMBOLS OF JAPAN"}
BRAND = "紋処すず  |  MONDOKORO SUZU"
CTA = {"ja": "SUZURIにて販売中", "en": "Available on SUZURI"}
SIDE_MARGIN = 80

LAYOUT = {
    "pinterest": dict(size=(1000, 1500), tag_y=77, tag_px={"ja": 30, "en": 25}, tag_rule_y=132,
                      title_y=172, title_px={"ja": 94, "en": 68}, art_cy=660, art_max=700,
                      keyword_y=1064, keyword_px={"ja": 55, "en": 47},
                      body_y=1155, body_step=57, body_px={"ja": 34, "en": 31},
                      rule_y=1367, brand_y=1391, brand_px=25, cta_y=1444, cta_px=23,
                      show_body=True, show_cta=True),
    "threads": dict(size=(1080, 1350), tag_y=77, tag_px={"ja": 30, "en": 25}, tag_rule_y=132,
                    title_y=172, title_px={"ja": 94, "en": 68}, art_cy=610, art_max=665,
                    keyword_y=990, keyword_px={"ja": 55, "en": 47},
                    rule_y=1147, brand_y=1190, brand_px=29,
                    show_body=False, show_cta=False),
}


class LayoutError(Exception):
    pass


def font(path, size):
    return ImageFont.truetype(path, size, index=0)  # index 0 = 日本語字形


def load_cards():
    return json.loads(DATA.read_text(encoding="utf-8"))


# ---------- 作品 ----------

def load_art(path):
    """原本を読み、外側の透明余白だけを落とす。絵柄・色・比率は変えない。"""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA") or "transparency" in im.info:
        art = im.convert("RGBA")
    else:
        rgb = im.convert("RGB")
        a = np.asarray(rgb).astype(int)
        mask = Image.fromarray(np.where(a.min(axis=2) > 238, 255, 0).astype(np.uint8), "L").copy()
        w, h = mask.size
        for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
            if mask.getpixel(seed) == 255:
                ImageDraw.floodfill(mask, seed, 128)       # 外周につながった白だけ
        alpha = np.where(np.asarray(mask) == 128, 0, 255).astype(np.uint8)
        art = Image.fromarray(np.dstack([a.astype(np.uint8), alpha]), "RGBA")
    bbox = art.getchannel("A").getbbox()
    return art.crop(bbox)


def scale_art(art, box, art_scale):
    s = min(box / art.width, box / art.height) * art_scale
    s = min(s, box / max(art.width, art.height))         # 枠（box×box）を超えない
    return art.resize((round(art.width * s), round(art.height * s)), Image.Resampling.LANCZOS)


# ---------- 文字 ----------

def text_w(d, text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0]


def wrap(d, text, f, max_w):
    """幅に収まるよう折り返す。英語は単語単位、日本語は文字単位（行頭禁則つき）。"""
    if text_w(d, text, f) <= max_w:
        return [text]
    no_head = "、。，．・：；？！ー）」』】〉》"
    lines, cur = [], ""
    tokens = text.split(" ") if text.isascii() else list(text)
    sep = " " if text.isascii() else ""
    for t in tokens:
        cand = (cur + sep + t) if cur else t
        if text_w(d, cand, f) <= max_w or (not text.isascii() and t in no_head):
            cur = cand
        else:
            lines.append(cur)
            cur = t
    if cur:
        lines.append(cur)
    return lines


def fit_font(d, text, path, size, max_w, min_size):
    while size > min_size and text_w(d, text, font(path, size)) > max_w:
        size -= 2
    f = font(path, size)
    if text_w(d, text, f) > max_w:
        raise LayoutError(f"収まらない: {text}")
    return f


def draw_center(d, text, y, f, fill, W, boxes, label):
    b = d.textbbox((0, 0), text, font=f)
    x = (W - (b[2] - b[0])) / 2
    d.text((x, y - b[1]), text, font=f, fill=fill)
    box = (x, y, x + (b[2] - b[0]), y + (b[3] - b[1]))
    boxes.append((label, box))
    return box


# ---------- 組み立て ----------

def render(card, platform, lang, art):
    L = LAYOUT[platform]
    W, H = L["size"]
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    boxes = []
    max_w = W - 2 * SIDE_MARGIN

    # 上の角線（全面は囲わない）
    pad = 44
    for x0, sx in ((pad, 1), (W - pad, -1)):
        d.line([(x0, 55), (x0, 135)], fill=GOLD, width=3)
        d.line([(x0, 55), (x0 + sx * 90, 55)], fill=GOLD, width=3)

    draw_center(d, TAG[lang], L["tag_y"], font(SANS_R, L["tag_px"][lang]), INK, W, boxes, "tag")
    d.line([(W // 2 - 48, L["tag_rule_y"]), (W // 2 + 48, L["tag_rule_y"])], fill=GOLD, width=3)

    title = card[f"title_{lang}"]
    ft = fit_font(d, title, SERIF_B, L["title_px"][lang], max_w, 48)
    draw_center(d, title, L["title_y"], ft, INK, W, boxes, "title")

    # 作品の背面に細い六角形を1つ
    cx, cy, diam = W // 2, L["art_cy"], L["art_max"]
    r = diam * 0.46
    pts = [(cx + r * math.cos(math.pi / 6 + i * math.pi / 3),
            cy + r * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    d.line(pts + [pts[0]], fill=GOLD, width=4, joint="curve")

    a = scale_art(art, int(diam * 0.9), card.get("art_scale", 1.0))
    ax, ay = round(cx - a.width / 2), round(cy - a.height / 2)
    img.paste(a, (ax, ay), a)
    d = ImageDraw.Draw(img)
    boxes.append(("art", (ax, ay, ax + a.width, ay + a.height)))

    rule2 = L["keyword_y"] - 30
    d.line([(cx - 50, rule2), (cx + 50, rule2)], fill=GOLD, width=3)
    kw = card[f"keyword_{lang}"]
    fk = fit_font(d, kw, SERIF_B, L["keyword_px"][lang], max_w, 36)
    draw_center(d, kw, L["keyword_y"], fk, INK, W, boxes, "keyword")

    if L["show_body"]:
        fb = font(SANS_R, L["body_px"][lang])
        lines = []
        for line in card[f"body_{lang}"]:
            lines += wrap(d, line, fb, max_w)
        if len(lines) > 3:
            raise LayoutError(f"本文が3行を超える（{len(lines)}行）")
        for i, t in enumerate(lines):
            draw_center(d, t, L["body_y"] + i * L["body_step"], fb, DARK, W, boxes, f"body{i}")

    d.line([(cx - 56, L["rule_y"]), (cx + 56, L["rule_y"])], fill=GOLD, width=2)
    draw_center(d, BRAND, L["brand_y"], font(SERIF_R, L["brand_px"]), INK, W, boxes, "brand")
    if L["show_cta"]:
        draw_center(d, CTA[lang], L["cta_y"], font(SANS_R, L["cta_px"]), MUTED, W, boxes, "cta")

    check(boxes, W, H)
    return img, boxes, (ax, ay, a)


def check(boxes, W, H):
    """はみ出しと重なりを検査する。"""
    for label, (x0, y0, x1, y1) in boxes:
        if x0 < SIDE_MARGIN - 1 or x1 > W - SIDE_MARGIN + 1 or y0 < 40 or y1 > H - 30:
            raise LayoutError(f"{label} が余白をはみ出している: {(x0, y0, x1, y1)}")
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            (la, a), (lb, b) = boxes[i], boxes[j]
            if a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]:
                raise LayoutError(f"{la} と {lb} が重なっている")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("key")
    ap.add_argument("--platform", default="all", choices=["pinterest", "threads", "all"])
    ap.add_argument("--lang", default="all", choices=["ja", "en", "all"])
    ap.add_argument("--out", default=str(ROOT / "previews"))
    args = ap.parse_args()

    card = load_cards()[args.key]
    art_dir = Path(os.environ.get("ART_DIR", ROOT.parent / "art"))
    art = load_art(art_dir / card["art_path"])
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    plats = ["pinterest", "threads"] if args.platform == "all" else [args.platform]
    langs = ["ja", "en"] if args.lang == "all" else [args.lang]
    for p in plats:
        for lg in langs:
            img, _, _ = render(card, p, lg, art)
            dst = out / f"{args.key}_{p}_{lg}.png"
            img.save(dst, optimize=True)
            print(dst)


if __name__ == "__main__":
    sys.exit(main())

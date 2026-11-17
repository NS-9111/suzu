"""意味カード v2 の検査。ART_DIR に原本PNG（kitsune.png）がある前提。

  ART_DIR=<原本フォルダ> python3 -m pytest tests/test_card_v2.py -q
"""
import os
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import make_card_v2 as m  # noqa: E402

ART_DIR = Path(os.environ.get("ART_DIR", ROOT.parent / "art"))
CARDS = {k: v for k, v in m.load_cards().items() if not k.startswith("_")}
CARD = CARDS["kitsune"]
SIZES = {"pinterest": (1000, 1500), "threads": (1080, 1350)}


@pytest.fixture(scope="module")
def art():
    p = ART_DIR / CARD["art_path"]
    if not p.exists():
        pytest.skip(f"原本PNGがない: {p}")
    return m.load_art(p)


@pytest.mark.parametrize("platform", ["pinterest", "threads"])
@pytest.mark.parametrize("lang", ["ja", "en"])
def test_size_and_layout(art, platform, lang):
    img, boxes, _ = m.render(CARD, platform, lang, art)   # はみ出し・重なりがあれば LayoutError
    assert img.size == SIZES[platform]
    labels = [b[0] for b in boxes]
    assert labels.count("title") == 1 and labels.count("keyword") == 1
    assert ("cta" in labels) == (platform == "pinterest")
    assert any(l.startswith("body") for l in labels) == (platform == "pinterest")


@pytest.mark.parametrize("platform", ["pinterest", "threads"])
def test_art_unchanged(art, platform):
    """作品は縮小以外の加工をしていない：不透明部分の画素が、縮小した原本と一致する。"""
    img, _, (ax, ay, scaled) = m.render(CARD, platform, "ja", art)
    region = np.asarray(img.crop((ax, ay, ax + scaled.width, ay + scaled.height))).astype(int)
    s = np.asarray(scaled).astype(int)
    opaque = s[..., 3] == 255
    assert opaque.sum() > 1000
    assert np.abs(region[opaque] - s[..., :3][opaque]).max() == 0
    ratio_src = art.width / art.height
    ratio_out = scaled.width / scaled.height
    assert abs(ratio_src - ratio_out) < 0.01


def test_transparency_kept(art):
    """透過PNGの前景の透明度を残している（白を一律に抜いていない）。"""
    src = Image.open(ART_DIR / CARD["art_path"]).convert("RGBA")
    a_src = np.asarray(src.crop(src.getchannel("A").getbbox()))[..., 3]
    assert np.array_equal(a_src, np.asarray(art)[..., 3])


def test_long_text_is_rejected(art):
    bad = dict(CARD, keyword_ja="あ" * 40)
    with pytest.raises(m.LayoutError):
        m.render(bad, "pinterest", "ja", art)


@pytest.mark.parametrize("key", sorted(CARDS))
@pytest.mark.parametrize("platform", ["pinterest", "threads"])
@pytest.mark.parametrize("lang", ["ja", "en"])
def test_all_cards_render(key, platform, lang):
    p = ART_DIR / CARDS[key]["art_path"]
    if not p.exists():
        pytest.skip(f"原本PNGがない: {p}")
    img, _, (ax, ay, scaled) = m.render(CARDS[key], platform, lang, m.load_art(p))
    assert img.size == SIZES[platform]
    region = np.asarray(img.crop((ax, ay, ax + scaled.width, ay + scaled.height))).astype(int)
    s = np.asarray(scaled).astype(int)
    opaque = s[..., 3] == 255
    assert np.abs(region[opaque] - s[..., :3][opaque]).max() == 0

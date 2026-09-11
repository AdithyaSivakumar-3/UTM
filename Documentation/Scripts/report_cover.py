# -*- coding: utf-8 -*-
"""The report's cover picture — composed from the project's own imagery, nothing stock.

  left   the rig (UTM rig_12-08-26.jpg)
  right  top: the two-marker principle (ppd_dic_explain.png)
         bottom: the twelve fractured final frames (frac_map.png)

Writes documentation/figures/report_cover.png (16:9, 300 dpi-class).
"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.abspath(os.path.join(HERE, "..", "figures"))

INK = (37, 52, 57)
TAN = (178, 158, 132)
CREAM = (245, 243, 239)

W, H = 2400, 1350
PAD, GAP = 40, 28


def fit(im, w, h):
    """Cover-fit (crop to fill) so panels have no letterboxing."""
    im = im.convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def contain(im, w, h, bg=(255, 255, 255)):
    """Contain-fit on a white card (for figures that must not be cropped)."""
    im = im.convert("RGB")
    s = min(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    card = Image.new("RGB", (w, h), bg)
    card.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return card


def main():
    canvas = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(canvas)

    left_w = 900
    right_x = PAD + left_w + GAP
    right_w = W - right_x - PAD
    inner_h = H - 2 * PAD

    rig = fit(Image.open(os.path.join(FIGS, "UTM rig_12-08-26.jpg")), left_w, inner_h)
    canvas.paste(rig, (PAD, PAD))

    top_h = int(inner_h * 0.42)
    bot_h = inner_h - top_h - GAP
    dic = contain(Image.open(os.path.join(FIGS, "ppd_dic_explain.png")), right_w, top_h)
    frac = contain(Image.open(os.path.join(FIGS, "frac_map.png")), right_w, bot_h)
    canvas.paste(dic, (right_x, PAD))
    canvas.paste(frac, (right_x, PAD + top_h + GAP))

    # tan hairlines between the panels, and an ink bar at the foot — the deck's palette
    d.rectangle([PAD + left_w, PAD, PAD + left_w + GAP, H - PAD], fill=CREAM)
    d.rectangle([PAD + left_w + GAP // 2 - 2, PAD, PAD + left_w + GAP // 2 + 2, H - PAD],
                fill=TAN)
    d.rectangle([right_x, PAD + top_h + GAP // 2 - 2, W - PAD, PAD + top_h + GAP // 2 + 2],
                fill=TAN)
    d.rectangle([0, H - 14, W, H], fill=INK)
    d.rectangle([0, H - 14, 420, H], fill=TAN)

    out = os.path.join(FIGS, "report_cover.png")
    canvas.save(out, dpi=(300, 300))
    print("  report_cover.png", canvas.size)


if __name__ == "__main__":
    main()

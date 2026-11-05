"""Contact sheet: one row per building (front / back / cutaway) + the role palette legend."""
import json
import os

from PIL import Image, ImageDraw, ImageFont

from .render import LOOK

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _font(n):
    try:
        return ImageFont.truetype(FONT, n)
    except OSError:
        return ImageFont.load_default()


def sheet(out_dir, doc, path):
    man = json.load(open(os.path.join(out_dir, "manifest.json")))
    spec = doc["spec"]
    rows = []
    for e in man:
        ims = [Image.open(os.path.join(out_dir, p)) for p in e["previews"]]
        rows.append((e, ims))
    pad = 24
    W = max(sum(i.width for i in ims) + pad * (len(ims) + 1) for _, ims in rows)
    leg_h = 40 + 26 * ((len(spec["palette"]) + 2) // 3)
    H = 70 + sum(max(i.height for i in ims) + 60 for _, ims in rows) + leg_h
    img = Image.new("RGB", (W, H), "#17191e")
    d = ImageDraw.Draw(img)
    d.text((pad, 18), f"{doc['display_name']} culture ({doc['content_id']}), tier {spec.get('tier')}: preview renders",
           font=_font(26), fill="#eeeeee")
    y = 70
    names = {b["id"]: b for b in spec["buildings"]}
    for e, ims in rows:
        b = names[e["id"]]
        sx, sy, sz = e["size"]
        d.text((pad, y), f"{b['display_name']}  ({e['id']}, {sx}x{sy}x{sz}, {b['role_in_village']})",
               font=_font(18), fill="#e8d27a")
        x = pad
        for lab, im in zip(("front (north = door side)", "back", "cutaway (roof off)"), ims):
            img.paste(im, (x, y + 28))
            d.text((x + 6, y + 32), lab, font=_font(13), fill="#9aa0aa")
            x += im.width + pad
        y += max(i.height for i in ims) + 60
    d.text((pad, y), "Palette roles (main block of each role; colours approximate vanilla)", font=_font(16), fill="#cccccc")
    y += 30
    col_w = (W - 2 * pad) // 3
    for n, (role, blocks) in enumerate(spec["palette"].items()):
        cx, cy = pad + (n % 3) * col_w, y + (n // 3) * 26
        main = next(iter(blocks))
        c = LOOK.get(main, ("", "#ff00ff"))[1]
        d.rectangle([cx, cy, cx + 18, cy + 18], fill=c, outline="#000000")
        extra = f" +{len(blocks) - 1} mix" if len(blocks) > 1 else ""
        d.text((cx + 26, cy + 1), f"{role}: {main.split(':')[1]}{extra}", font=_font(14), fill="#cfcfcf")
    img.save(path)
    return img

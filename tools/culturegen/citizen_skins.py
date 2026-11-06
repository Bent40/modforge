"""Race citizen skins for MineColonies: composite a race's layered mob textures into 64x64 player-layout skins,
then write a full MineColonies texture style (every file name the `default` style has) plus a preview sheet.

usage: python -m tools.culturegen.citizen_skins SKINS.yaml DEFAULT_STYLE_DIR OUT_STYLE_DIR [--preview out.png]

SKINS.yaml:
  style: goblin
  skins:                                    # one entry per (gender, tone, outfit)
    - { gender: male, tone: a, outfit: 0, layers: [ {path: .../skin1.png, tint: "#ffffff"}, {path: ..., tint: "#5a7a2a"} ] }
  tone_by_suffix: { _a: a, _b: b, _d: d, _w: w }   # MineColonies suffix -> tone key (optional; default identity)

Facts (minecolonies-1.1.1368, read 2026-11-06): a citizen texture is 128x64; the LEFT 64x64 half is the modern
player-skin layout (MaleCitizenModel/FemaleCitizenModel extend HumanoidModel), the right half holds hats/beards/job
props. Path: textures/entity/citizen/<style>/<model><male|female><textureId><suffix>.png; a missing file falls back
to the default style (a human skin), so every name must exist. Tensura goblin textures are 64x64 player layout.
"""
import os
import re
import sys

import yaml
from PIL import Image, ImageDraw

NAME = re.compile(r"^(?P<model>.*?)(?P<gender>male|female)(?P<id>\d+)(?P<suffix>_[a-z])?\.png$")


def _tint(img, hexcol):
    if not hexcol or hexcol.lower() in ("#ffffff", "ffffff"):
        return img
    r, g, b = (int(hexcol.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
    px = img.load()
    out = img.copy()
    po = out.load()
    for y in range(img.height):
        for x in range(img.width):
            pr, pg, pb, pa = px[x, y]
            po[x, y] = (pr * r // 255, pg * g // 255, pb * b // 255, pa)
    return out


def composite(layers):
    base = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    for L in layers:
        im = Image.open(L["path"]).convert("RGBA")
        if im.size != (64, 64):
            im = im.resize((64, 64), Image.NEAREST)
        base = Image.alpha_composite(base, _tint(im, L.get("tint")))
    return base


def front_view(skin, s=6):
    """Flat front view of a 64x64 player-layout skin (head, body, arms, legs + overlays)."""
    v = Image.new("RGBA", (16, 32), (0, 0, 0, 0))
    parts = [((8, 8, 16, 16), (4, 0)), ((40, 8, 48, 16), (4, 0)),          # head, hat
             ((20, 20, 28, 32), (4, 8)), ((20, 36, 28, 48), (4, 8)),       # body, jacket
             ((44, 20, 48, 32), (0, 8)), ((44, 36, 48, 48), (0, 8)),       # right arm (+sleeve)
             ((36, 52, 40, 64), (12, 8)), ((52, 52, 56, 64), (12, 8)),     # left arm (+sleeve)
             ((4, 20, 8, 32), (4, 20)), ((4, 36, 8, 48), (4, 20)),         # right leg (+pants)
             ((20, 52, 24, 64), (8, 20)), ((4, 52, 8, 64), (8, 20))]       # left leg (+pants)
    for box, at in parts:
        v.alpha_composite(skin.crop(box), at)
    return v.resize((16 * s, 32 * s), Image.NEAREST)


def main(argv):
    cfg = yaml.safe_load(open(argv[0]))
    default_dir, out_dir = argv[1], argv[2]
    os.makedirs(out_dir, exist_ok=True)
    tone_by_suffix = cfg.get("tone_by_suffix", {})
    skins = {}
    for s in cfg["skins"]:
        skins.setdefault((s["gender"], s["tone"]), []).append(composite(s["layers"]))
    written, missing = 0, set()
    for f in sorted(os.listdir(default_dir)):
        m = NAME.match(f)
        if not m:
            continue
        suffix = m["suffix"] or "_a"
        tone = tone_by_suffix.get(suffix, suffix.lstrip("_"))
        pool = skins.get((m["gender"], tone)) or skins.get((m["gender"], cfg.get("fallback_tone", "a")))
        if not pool:
            missing.add((m["gender"], tone))
            continue
        skin = pool[int(m["id"]) % len(pool)]
        canvas = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
        canvas.paste(skin, (0, 0))
        canvas.save(os.path.join(out_dir, f))
        written += 1
    print(written, "textures written to", out_dir, "; no skin for:", sorted(missing))
    if "--preview" in argv:
        views = [(f"{s['gender']} {s['tone']} #{s.get('outfit', 0)}", front_view(composite(s["layers"]))) for s in cfg["skins"]]
        W = 20 + sum(v.width + 20 for _, v in views)
        sheet = Image.new("RGBA", (W, views[0][1].height + 50), "#20232a")
        d = ImageDraw.Draw(sheet)
        x = 20
        for label, v in views:
            sheet.alpha_composite(v, (x, 34))
            d.text((x, 10), label, fill="#dddddd")
            x += v.width + 20
        sheet.save(argv[argv.index("--preview") + 1])
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

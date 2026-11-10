"""Build the hand-designed dwarf huts, levels 1-5, into a loose Structurize pack plus previews.

    python3 -m tools.culturegen.build_dwarf [out_pack_dir] [preview_dir]

Every level of a hut shares one footprint (union box, padded with structurize substitution corners), so
MineColonies can upgrade in place; the hut block sits at the same spot in every level.
"""
import os
import sys

from . import blueprint as bp
from .colony import _share_footprint
from .hand_dwarf import dwarf_hall, dwarf_house, dwarf_smithy

HALL = {"width": 15, "length": 25, "wall_height": 8, "tower": True, "wheel": True, "chimneys": 2}
HUTS = [
    # id, builder, params, hut block, (x, z) of the hut block (y = 1), pack sub-folder
    ("townhall", dwarf_hall, HALL, "minecolonies:blockhuttownhall", (HALL["width"] // 2 + 2, 2), "fundamentals"),
    ("residence", dwarf_house, {}, "minecolonies:blockhutcitizen", (2, 1), "fundamentals"),
    ("blacksmith", dwarf_smithy, {}, "minecolonies:blockhutblacksmith", (8, 1), "craftsmanship/metallurgy"),
]


def build(out, pdir=None, huts=None, prefix="dwarf"):
    report = []
    for hid, fn, par, hut, (hx, hz), sub in (huts or HUTS):
        levels = []
        for lv in range(1, 6):
            g = fn(dict(par, level=lv))
            c = g.get(hx, 1, hz)
            assert c is None or c[0] == "minecraft:air", f"{hid}{lv}: hut spot taken by {c}"
            levels.append((lv, g, []))
        os.makedirs(os.path.join(out, sub), exist_ok=True)
        for lv, g, hp, _ in _share_footprint(levels, (hx, hz)):
            g.set(*hp, hut, facing="north")
            name = f"{hid}{lv}.blueprint"
            root = bp.from_grid(g, name, hut, hp, required_mods=("minecolonies", "create"), architects=["culturegen"])
            bp.write(os.path.join(out, sub, name), root)
            beds = sum(1 for v in g.cells.values() if v[0].endswith("_bed") and v[1].get("part") == "head")
            (sx, sy, sz) = (root["size_x"], root["size_y"], root["size_z"])
            report.append(f"{sub}/{name}: {sx}x{sy}x{sz} hut@{hp} beds {beds} blocks {len(g.cells)}")
            if pdir:
                from .render import render
                os.makedirs(pdir, exist_ok=True)
                render(g, os.path.join(pdir, f"{prefix}_{hid}{lv}_front.png"), scale=4)
    return report


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "drafts/dwarf-culture/pack/dwarf_preview"
    pdir = sys.argv[2] if len(sys.argv) > 2 else "drafts/dwarf-culture/previews/levels"
    print("\n".join(build(out, pdir)))

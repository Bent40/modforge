"""MineColonies huts from culture forms: one generated building per hut level, written as Structurize .blueprint.

usage: python -m tools.culturegen.colony cultures/goblin.yaml OUT_DIR [--no-render]

Writes OUT_DIR/blueprints/<hut><level>.blueprint (drop into the style pack's fundamentals/), previews of every
level, and a sheet. Rules (see drafts/goblin-culture/HUTS.md):
  * every level of a hut has the SAME footprint (upgrades build in place): each level is generated, centred on a
    fixed anchor, and padded to the union box with structurize substitution corners;
  * the hut block sits at the same spot in every level (primary_offset);
  * each level carries its working blocks: beds (residence level n = n beds), racks, chests, stash, furnaces.
Culture-specific shapes come from the spec's `colony:` block; forms only name roles.
"""
import os
import sys
import zlib

import yaml

from . import blueprint as bp
from .forms import FORMS
from .grid import Palette, Grid
from .nbt import Byte, Short

SUB = "structurize:blocksubstitution"
DIRS = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}
OPP = {"north": "south", "south": "north", "west": "east", "east": "west"}


def _inv():
    return [{"empty": Byte(1)} for _ in range(27)]


def _te(kind):
    if kind == "rack":
        return {"id": "minecolonies:rack", "relNeighbor": {"x": 0, "y": 0, "z": 0}, "inWarehouse": Byte(0),
                "main": Byte(0), "inventory": _inv(), "version": Byte(0), "tagSIze": 0, "Item": "",
                "pos": {"x": 0, "y": 0, "z": 0}}
    if kind == "stash":
        return {"id": "minecolonies:stash", "mirror": Byte(0), "inWarehouse": Byte(0), "colony": 0, "main": Byte(0),
                "inventory": _inv(), "type": "minecolonies:stash", "version": 0, "tagSIze": 0, "Item": "",
                "style": "", "pos": {"x": 0, "y": 0, "z": 0},
                "blueprintDataProvider": {"corner1": {"x": 0, "y": 0, "z": 0}, "corner2": {"x": 0, "y": 0, "z": 0},
                                          "schematicName": "", "posTagMap": []}}
    if kind == "bed":
        return {"id": "minecraft:bed"}
    if kind in ("chest", "barrel"):
        return {"id": f"minecraft:{kind}", "Items": []}
    if kind == "furnace":
        return {"id": "minecraft:furnace", "Items": [], "BurnTime": Short(0), "CookTime": Short(0),
                "CookTimeTotal": Short(200)}
    return None


def _strip(g):
    """Drop world-gen bits a colony hut must not carry: jigsaws, hide carpets (beds replace them), mobs."""
    for pos, (b, _) in list(g.cells.items()):
        if b == "minecraft:jigsaw":
            del g.cells[pos]
            g.block_entities.pop(pos, None)
        elif b.endswith("_carpet"):
            g.cells[pos] = ("minecraft:air", {})
    g.entities = []


def _shift(g, dx, dz):
    out = Grid()
    out.cells = {(x + dx, y, z + dz): v for (x, y, z), v in g.cells.items()}
    out.block_entities = {(x + dx, y, z + dz): v for (x, y, z), v in g.block_entities.items()}
    return out


def _merge(g, other, dx, dy, dz):
    for (x, y, z), v in other.cells.items():
        g.cells[(x + dx, y + dy, z + dz)] = v
    for (x, y, z), v in other.block_entities.items():
        g.block_entities[(x + dx, y + dy, z + dz)] = v


def _free_floor(g, keep_clear):
    """Interior floor cells: air at y=1 with air above and a full block below, not reserved."""
    out = []
    for (x, y, z), (b, _) in g.cells.items():
        if y != 1 or b != "minecraft:air" or (x, z) in keep_clear:
            continue
        up = g.get(x, 2, z)
        if up is not None and up[0] != "minecraft:air":
            continue
        if not g.solid(x, 0, z):
            continue
        out.append((x, z))
    return out


def _wall_dir(g, x, z):
    """Direction of an adjacent wall (full block at y=1), or None."""
    for d, (dx, dz) in DIRS.items():
        if g.solid(x + dx, 1, z + dz):
            return d
    return None


def furnish(g, needs, keep_clear, seed):
    """Place working blocks on free interior floor, against walls first. needs = list of (kind, block, props).
    Beds take two cells, head against the wall. Returns what could not be placed."""
    free = set(_free_floor(g, keep_clear))
    order = sorted(free, key=lambda p: (0 if _wall_dir(g, *p) else 1, zlib.crc32(f"{seed}{p}".encode())))
    missed = []
    for kind, block, props in needs:
        placed = False
        for (x, z) in order:
            if (x, z) not in free:
                continue
            wd = _wall_dir(g, x, z)
            if kind == "bed":
                if not wd:
                    continue
                fx, fz = x - DIRS[wd][0], z - DIRS[wd][1]  # foot one step away from the wall
                if (fx, fz) not in free:
                    continue
                # keep a walkway: the cell beyond the foot must stay free
                bx, bz = fx - DIRS[wd][0], fz - DIRS[wd][1]
                g.set(x, 1, z, block, part="head", facing=wd, occupied="false")
                g.set(fx, 1, fz, block, part="foot", facing=wd, occupied="false")
                g.block_entities[(x, 1, z)] = _te("bed")
                g.block_entities[(fx, 1, fz)] = _te("bed")
                free -= {(x, z), (fx, fz)}
                free.discard((bx, bz))  # walkway
                placed = True
                break
            face = OPP[wd] if wd else "north"
            p = dict(props)
            if "facing" in p:
                p["facing"] = face
            g.set(x, 1, z, block, **p)
            te = _te(kind)
            if te:
                g.block_entities[(x, 1, z)] = te
            free.discard((x, z))
            placed = True
            break
        if not placed:
            missed.append(kind)
    return missed


def _needs(spec_level, pal):
    bed = spec_level.get("bed_block", "minecraft:brown_bed")
    out = [("bed", bed, {})] * spec_level.get("beds", 0)
    out += [("stash", "minecolonies:blockstash", {"facing": "north"})] * spec_level.get("stash", 0)
    out += [("rack", "minecolonies:blockminecoloniesrack", {"variant": "blockrackemptysingle", "facing": "north"})] \
        * spec_level.get("racks", 0)
    out += [("chest", "minecraft:chest", {"facing": "north", "type": "single", "waterlogged": "false"})] \
        * spec_level.get("chests", 0)
    out += [("furnace", "minecraft:furnace", {"facing": "north", "lit": "false"})] * spec_level.get("furnaces", 0)
    out += [("workbench", pal.main("workbench"), {})] * spec_level.get("workbenches", 0)
    return out


def build_hut(hut, culture):
    """Generate every level of one hut. Returns [(level, grid, hut_pos, missed)] on a shared footprint."""
    levels = []
    for lv, L in enumerate(hut["levels"], start=1):
        pal = Palette(culture["palette"], seed=zlib.crc32(f"{hut['id']}{lv}".encode()))
        g, _ = FORMS[L["form"]](L["params"], pal, culture)
        _strip(g)
        anchor = _anchor(g, L["form"], L["params"])
        for extra in L.get("annex", []):  # e.g. a watchtower beside the hall
            eg, _ = FORMS[extra["form"]](extra["params"], pal, culture)
            _strip(eg)
            ax, az = extra["at"]  # relative to this level's anchor
            _merge(g, eg, anchor[0] + ax, 0, anchor[1] + az)
        g = _shift(g, -anchor[0], -anchor[1])  # anchor -> (0, 0)
        hx, hz = hut["hut_block_at"]          # relative to the anchor, same for every level
        keep = {(hx, hz), (hx, hz - 1), (hx, hz + 1), (hx - 1, hz), (hx + 1, hz)} | _door_lane(g)
        missed = furnish(g, _needs(L, pal), keep, f"{hut['id']}{lv}")
        g.connect_fences()
        levels.append((lv, g, missed))
    # union box over all levels, so every level shares one footprint
    xs, ys, zs = [], [], []
    for _, g, _ in levels:
        (a, b, c), (d, e, f) = g.bounds()
        xs += [a, d]; ys += [b, e]; zs += [c, f]
    lo, hi = (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))
    out = []
    for lv, g, missed in levels:
        for corner in (lo, hi):
            if corner not in g.cells:
                g.set(*corner, SUB)
        g.normalise()
        hx, hz = hut["hut_block_at"]
        out.append((lv, g, (hx - lo[0], 1 - lo[1], hz - lo[2]), missed))
    return out


def _anchor(g, form, p):
    """The point all levels line up on: the hearth / centre of the main building, in grid coords."""
    if form == "round_hut":
        c = int((p["diameter"] - 1) / 2) + 1
        return (c, c)
    if form == "long_hall":
        x0, z0 = 1, 1
        return (x0 + (p["width"] - 1) // 2, z0 + (p["length"] - 1) // 2)
    if form == "lean_to":
        return (p["width"] // 2, p["depth"] - 1)
    (a, _, c), (d, _, f) = g.bounds()
    return ((a + d) // 2, (c + f) // 2)


def _door_lane(g):
    """Cells in front of and behind doors (y=1) stay clear so nobody is walled in."""
    lane = set()
    for (x, y, z), (b, p) in g.cells.items():
        if b.endswith("_door") and p.get("half") == "lower":
            lane |= {(x, z - 1), (x, z + 1), (x, z + 2)}
    return lane


def main(argv):
    spec_path, out = argv[0], argv[1]
    render_on = "--no-render" not in argv
    doc = yaml.safe_load(open(spec_path))
    culture = doc["spec"]
    culture["_ns"], culture["_race"] = doc["modid"], doc["content_id"]
    bdir = os.path.join(out, "blueprints")
    pdir = os.path.join(out, "previews")
    os.makedirs(bdir, exist_ok=True)
    os.makedirs(pdir, exist_ok=True)
    report = []
    for hut in culture["colony"]["huts"]:
        for lv, g, hut_pos, missed in build_hut(hut, culture):
            name = f"{hut['id']}{lv}.blueprint"
            g.set(*hut_pos, hut["hut_block"], facing="north")  # so previews show where the hut block sits
            if render_on:
                from .render import render
                render(g, os.path.join(pdir, f"{hut['id']}{lv}_front.png"), scale=4)
                render(g, os.path.join(pdir, f"{hut['id']}{lv}_cutaway.png"), scale=4, cut_y=hut.get("cut_y", 3))
            root = bp.from_grid(g, name, hut["hut_block"], hut_pos, hut_facing="north",
                                architects=["culturegen"])
            bp.write(os.path.join(bdir, name), root)
            back = bp.read(os.path.join(bdir, name))
            counts = {}
            names = [p["Name"] for p in back["palette"]]
            for i in bp.unpack_blocks(back["blocks"], back["size_x"] * back["size_y"] * back["size_z"]):
                counts[names[i]] = counts.get(names[i], 0) + 1
            beds = sum(v for k, v in counts.items() if k.endswith("_bed")) // 2
            racks = counts.get("minecolonies:blockminecoloniesrack", 0)
            line = (f"{name}: size {back['size_x']}x{back['size_y']}x{back['size_z']} hut@{hut_pos} beds {beds} "
                    f"racks {racks} stash {counts.get('minecolonies:blockstash', 0)} "
                    f"chests {counts.get('minecraft:chest', 0)} furnaces {counts.get('minecraft:furnace', 0)}"
                    + (f"  MISSED {missed}" if missed else ""))
            print(line)
            report.append(line)
    open(os.path.join(out, "colony_report.txt"), "w").write("\n".join(report) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])

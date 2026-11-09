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
from .nbt import Byte, Short, IntArray

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


TE_DEFAULTS = {   # blocks whose tile entity Fortress stores; give ours an empty one too
    "minecraft:barrel": lambda: {"id": "minecraft:barrel", "Items": []},
    "minecraft:smoker": lambda: {"id": "minecraft:smoker", "Items": [], "BurnTime": Short(0), "CookTime": Short(0),
                                 "CookTimeTotal": Short(100)},
    "minecraft:campfire": lambda: {"id": "minecraft:campfire", "Items": [], "CookingTimes": IntArray([0, 0, 0, 0]),
                                   "CookingTotalTimes": IntArray([0, 0, 0, 0])},
    "minecraft:skeleton_skull": lambda: {"id": "minecraft:skull"},
    "minecraft:crafting_table": None,
}


def _fill_tes(g):
    for pos, (b, _) in g.cells.items():
        f = TE_DEFAULTS.get(b)
        if f and pos not in g.block_entities:
            g.block_entities[pos] = f()


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
    out.tags = [(x + dx, y, z + dz, n) for (x, y, z, n) in getattr(g, "tags", [])]
    out.cells = {(x + dx, y, z + dz): v for (x, y, z), v in g.cells.items()}
    out.block_entities = {(x + dx, y, z + dz): v for (x, y, z), v in g.block_entities.items()}
    return out


def _merge(g, other, dx, dy, dz):
    if getattr(other, "tags", None):
        g.tags = getattr(g, "tags", []) + [(x + dx, y + dy, z + dz, n) for (x, y, z, n) in other.tags]
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
    budget = int(len(free) * 0.5)            # leave half the floor to walk on
    stack = []                               # rack tops: (x, z) where a second rack can sit at y=2
    missed = []
    for kind, block, props in needs:
        placed = False
        is_rack = block == "minecolonies:blockminecoloniesrack"
        if is_rack and stack:
            x, z = stack.pop()
            p = dict(props)
            te_tpl = p.pop("_te", None)
            g.set(x, 2, z, block, **p)
            g.block_entities[(x, 2, z)] = dict(te_tpl) if te_tpl else _te("rack")
            continue
        if budget <= 0:
            missed.append(kind)
            continue
        for (x, z) in order:
            if (x, z) not in free:
                continue
            wd = _wall_dir(g, x, z)
            if kind == "bed":
                block = props.get("_block", block)
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
                budget -= 2
                placed = True
                break
            face = OPP[wd] if wd else "north"
            p = dict(props)
            te_tpl = p.pop("_te", None)
            if "facing" in p:
                p["facing"] = face
            g.set(x, 1, z, block, **p)
            te = dict(te_tpl) if te_tpl else _te("rack" if is_rack else kind)
            if te:
                g.block_entities[(x, 1, z)] = te
            free.discard((x, z))
            budget -= 1
            if is_rack and wd and g.get(x, 2, z) and g.get(x, 2, z)[0] == "minecraft:air" and g.solid(
                    x + DIRS[wd][0], 2, z + DIRS[wd][1]):
                stack.append((x, z))
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
        _fill_tes(g)
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


# ---------- auto huts: working blocks copied from a source pack's hut, shell sized to fit ----------
SKIP_TE = {"minecolonies:colonybuilding", "minecraft:sign", "minecraft:hanging_sign", "minecraft:banner",
           "domum_ornamentum:materially_retexturable", "minecolonies:colony_flag", "minecraft:jukebox",
           "minecraft:dispenser", "minecraft:dropper", "minecraft:hopper", "minecraft:bell", "minecraft:beacon",
           "minecraft:ender_chest", "minecraft:skull", "minecraft:campfire"}
SKIP_MC = ("minecolonies:blockhut", "minecolonies:colony_wall_banner", "minecolonies:colony_banner",
           "minecolonies:blockconstructiontape", "minecolonies:decorationcontroller", "minecolonies:blockwaypoint",
           "minecolonies:gate_")
FACING_ONLY = {"facing"}
SIGNATURE = {"minecraft:anvil": 2, "minecraft:chipped_anvil": 1, "minecraft:grindstone": 2, "minecraft:stonecutter": 2,
             "minecraft:smithing_table": 2, "minecraft:loom": 2, "minecraft:cartography_table": 1,
             "minecraft:fletching_table": 2, "minecraft:cauldron": 2, "minecraft:water_cauldron": 2,
             "minecraft:composter": 2, "minecraft:bookshelf": 8, "minecraft:crafting_table": 2}


def source_tags(path):
    root = bp.read(path)
    out = {}
    for t in root["tile_entities"]:
        if t["id"] == "minecolonies:colonybuilding":
            for e in t.get("blueprintDataProvider", {}).get("posTagMap", []):
                for n in e["tagNameList"]:
                    out[n["tagName"]] = out.get(n["tagName"], 0) + 1
    return out


def source_needs(path):
    """(hut_block, needs) from a source blueprint: every working block, with its tile entity as a template."""
    root = bp.read(path)
    sx, sy, sz = root["size_x"], root["size_y"], root["size_z"]
    pal = root["palette"]
    tes = {(t["x"], t["y"], t["z"]): t for t in root["tile_entities"]}
    hut_block, needs = None, []
    sig = {}
    for i, pi in enumerate(bp.unpack_blocks(root["blocks"], sx * sy * sz)):
        e = pal[pi]
        n, props = e["Name"], dict(e.get("Properties", {}))
        if n.startswith("minecolonies:blockhut"):
            hut_block = n
            continue
        x, z, y = i % sx, (i // sx) % sz, i // (sx * sz)
        te = tes.get((x, y, z))
        if n.endswith("_bed"):
            if props.get("part") == "head":
                needs.append(("bed", n, {"_block": n}))
            continue
        if n.endswith("_door") or n.endswith("_chest") and props.get("type") == "left":
            continue
        if n in SIGNATURE and te is None:
            if sig.get(n, 0) < SIGNATURE[n]:
                sig[n] = sig.get(n, 0) + 1
                needs.append(("block", n, {k: str(v) for k, v in props.items()}))
            continue
        is_mc = n.startswith("minecolonies:") and not n.startswith(SKIP_MC)
        has_te = te is not None and te["id"] not in SKIP_TE
        if not (is_mc or has_te):
            continue
        keep = {k: str(v) for k, v in props.items() if k not in ("part",)}
        if n.endswith("chest"):
            keep["type"] = "single"
        if has_te:
            t = {k: v for k, v in te.items() if k not in ("x", "y", "z", "pos")}
            keep["_te"] = t
        needs.append(("block", n, keep))
    # bulky first so they get wall spots
    order = {"bed": 0}
    needs.sort(key=lambda t: (order.get(t[0], 1), t[1]))
    return hut_block, needs


def _annex_cells(g, hut_cells):
    return {(x, z) for (x, _, z) in g.cells} - hut_cells


SHELL_SIZES = {
    "round_hut": [{"diameter": d, "wall_height": 3 if d < 13 else 4} for d in (7, 9, 11, 13, 15, 17, 19)],
    "long_hall": [{"width": w, "length": L, "wall_height": 4, "post_spacing": 4}
                  for w in (9, 11) for L in range(11, 48, 4)],
}


def build_auto_hut(hut, culture, pack_dir):
    """Levels from the source pack's <path>1..5; each level gets the smallest shell (never smaller than the
    previous level's) that holds every working block."""
    import glob
    levels = []
    floor = 0
    srcs = sorted(glob.glob(os.path.join(pack_dir, hut["source"] + "[0-9].blueprint")))
    hut_block = None
    for src in srcs:
        lv = int(os.path.basename(src)[len(os.path.basename(hut["source"])):].split(".")[0])
        hb, needs = source_needs(src)
        hut_block = hut_block or hb
        sizes = SHELL_SIZES[hut["shell"]]
        done = None
        for si in range(floor, len(sizes)):
            pal = Palette(culture["palette"], seed=zlib.crc32(f"{hut['id']}{lv}".encode()))
            g, _ = FORMS[hut["shell"]](sizes[si], pal, culture)
            _strip(g)
            anchor = _anchor(g, hut["shell"], sizes[si])
            g = _shift(g, -anchor[0], -anchor[1])
            hx, hz = 1, 0
            keep = {(hx, hz), (hx, hz - 1), (hx, hz + 1), (hx - 1, hz), (hx + 1, hz)} | _door_lane(g)
            outside = set(hut.get("outside", []))
            inside_needs = [n for n in needs if n[1] not in outside]
            out_needs = [n for n in needs if n[1] in outside]
            ann = hut.get("annex")
            if ann:
                (_, _, _), (ex, _, _) = g.bounds()
                aparams = dict(ann.get("params", {}))
                for k in ann.get("tag_params", []):          # e.g. plots: bamboo/sugar/cactus from the source
                    aparams[k] = source_tags(src).get(k, 0)
                ag, _ = FORMS[ann["form"]](aparams, pal, culture)
                _strip(ag)
                (a0, _, c0), (a1, _, c1) = ag.bounds()
                dz = -(c0 + c1) // 2 + ann.get("dz", 0)
                dx = ex + 1 - a0 + ann.get("gap", 0)
                # inside the main building's cells nothing changes; the annex keeps its own cells
                hut_cells = set((x, z) for (x, _, z) in g.cells)
                _merge(g, ag, dx, 0, dz)
                ann_cells = {(x + dx, z + dz) for (x, _, z) in ag.cells} - hut_cells
                if out_needs:
                    out_missed = furnish(g, out_needs, keep | hut_cells, f"{hut['id']}{lv}o")
                    if out_missed:
                        inside_needs += out_needs[-len(out_missed):]
            else:
                inside_needs += out_needs
            missed = furnish(g, inside_needs, keep | ({c for c in _annex_cells(g, hut_cells)} if ann else set()),
                             f"{hut['id']}{lv}")
            if not missed or si == len(sizes) - 1:
                done = (lv, g, missed, si)
                break
        lv, g, missed, floor = done
        g.connect_fences()
        _fill_tes(g)
        levels.append((lv, g, missed))
    return _share_footprint(levels, (1, 0)), hut_block


def build_barracks(hut, culture, pack_dir):
    """Barracks = a longhall with k bunk alcoves, each a child barracks-tower hut (MineColonies upgrades the
    child from its own <tower>N.blueprint, which the source pack keeps). k per level comes from the source."""
    tower_src = bp.read(os.path.join(pack_dir, hut["tower_source"] + "1.blueprint"))
    tsx, tsy, tsz = tower_src["size_x"], tower_src["size_y"], tower_src["size_z"]
    tflat = bp.unpack_blocks(tower_src["blocks"], tsx * tsy * tsz)
    ttes = {(t["x"], t["y"], t["z"]): t for t in tower_src["tile_entities"]}
    levels = []
    for lv in range(1, 6):
        src = os.path.join(pack_dir, f"{hut['source']}{lv}.blueprint")
        root = bp.read(src)
        child_tpl = [t for t in root["tile_entities"] if t["id"] == "minecolonies:colonybuilding"
                     and "tower" in str(t.get("type", ""))]
        k = len(child_tpl)
        hb, needs = source_needs(src)
        needs = [n for n in needs if n[0] != "bed" and n[1] != "minecolonies:blockhutbarrackstower"]
        racks = [n for n in needs if n[1] == "minecolonies:blockminecoloniesrack"]
        needs = [n for n in needs if n[1] != "minecolonies:blockminecoloniesrack"] + racks[k:]
        pal = Palette(culture["palette"], seed=zlib.crc32(f"{hut['id']}{lv}".encode()))
        params = {"width": 9, "length": 19, "wall_height": 4, "post_spacing": 4}
        g, _ = FORMS["long_hall"](params, pal, culture)
        _strip(g)
        x0, z0 = 1, 1
        zs = z0 + 2
        for i in range(k):
            ox, oz = x0 + 1, zs + 4 * i
            for ty in range(1, tsy):
                for tz in range(tsz):
                    for tx in range(tsx):
                        e = tower_src["palette"][tflat[(ty * tsz + tz) * tsx + tx]]
                        n = e["Name"]
                        if n.startswith("structurize:"):
                            continue
                        props = {kk: str(v) for kk, v in e.get("Properties", {}).items()}
                        g.cells[(ox + tx, ty, oz + tz)] = (n, props)
                        te = ttes.get((tx, ty, tz))
                        if te is not None:
                            t = {kk: v for kk, v in te.items() if kk not in ("x", "y", "z", "pos")}
                            if n.startswith("minecolonies:blockhut"):
                                t = {kk: v for kk, v in child_tpl[i].items() if kk not in ("x", "y", "z", "pos")}
                            g.block_entities[(ox + tx, ty, oz + tz)] = t
            for tx in range(tsx):                     # corridor row in front of each alcove stays clear
                g.air(ox + tx, 1, oz - 1)
        anchor = _anchor(g, "long_hall", params)
        g = _shift(g, -anchor[0], -anchor[1])
        corridor = {(x, z) for (x, y, z), c in g.cells.items() if y == 1 and c[0] == "minecraft:air"
                    and x <= 0 and (z - (zs - anchor[1])) % 4 == 3}
        keep = {(1, 0), (1, -1), (1, 1), (0, 0), (2, 0)} | _door_lane(g) | corridor
        missed = furnish(g, needs, keep, f"{hut['id']}{lv}")
        g.connect_fences()
        _fill_tes(g)
        levels.append((lv, g, missed))
    return _share_footprint(levels, (1, 0)), "minecolonies:blockhutbarracks"


def _share_footprint(levels, hut_at):
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
        g.tags = [(x - lo[0], y - lo[1], z - lo[2], n) for (x, y, z, n) in getattr(g, "tags", [])]
        g.normalise()
        hx, hz = hut_at
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
    src_pack = argv[argv.index("--source-pack") + 1] if "--source-pack" in argv else None
    only = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
    jobs = [(hut, build_hut(hut, culture)) for hut in culture["colony"].get("huts", [])
            if not only or hut["id"] in only]
    if src_pack:
        for hut in culture["colony"].get("auto_huts", []):
            if only and hut["id"] not in only:
                continue
            lvls, hb = (build_barracks if hut.get("shell") == "barracks" else build_auto_hut)(hut, culture, src_pack)
            jobs.append((dict(hut, hut_block=hb), lvls))
    for hut, built in jobs:
        sub = os.path.dirname(hut.get("source", ""))
        os.makedirs(os.path.join(bdir, sub), exist_ok=True)
        for lv, g, hut_pos, missed in built:
            name = f"{hut['id']}{lv}.blueprint"
            rel = os.path.join(sub, name)
            g.set(*hut_pos, hut["hut_block"], facing="north")  # so previews show where the hut block sits
            if render_on:
                from .render import render
                render(g, os.path.join(pdir, f"{hut['id']}{lv}_front.png"), scale=4)
                render(g, os.path.join(pdir, f"{hut['id']}{lv}_cutaway.png"), scale=4, cut_y=hut.get("cut_y", 3))
            root = bp.from_grid(g, name, hut["hut_block"], hut_pos, hut_facing="north",
                                architects=["culturegen"], tags=getattr(g, "tags", []))
            bp.write(os.path.join(bdir, rel), root)
            back = bp.read(os.path.join(bdir, rel))
            counts = {}
            names = [p["Name"] for p in back["palette"]]
            for i in bp.unpack_blocks(back["blocks"], back["size_x"] * back["size_y"] * back["size_z"]):
                counts[names[i]] = counts.get(names[i], 0) + 1
            beds = sum(v for k, v in counts.items() if k.endswith("_bed")) // 2
            racks = counts.get("minecolonies:blockminecoloniesrack", 0)
            line = (f"{rel}: size {back['size_x']}x{back['size_y']}x{back['size_z']} hut@{hut_pos} beds {beds} "
                    f"racks {racks} stash {counts.get('minecolonies:blockstash', 0)} "
                    f"chests {counts.get('minecraft:chest', 0)} furnaces {counts.get('minecraft:furnace', 0)}"
                    + (f"  MISSED {missed}" if missed else ""))
            print(line)
            report.append(line)
    open(os.path.join(out, "colony_report.txt"), "w").write("\n".join(report) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:])

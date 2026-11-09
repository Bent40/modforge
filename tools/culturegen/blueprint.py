"""Structurize .blueprint read/write (MineColonies style packs).

Format read from structurize-1.0.832 BlueprintUtil with javap on 2026-11-06 (spike_tools/goblin_shots/blueprint_format.md):
gzip NBT, empty root name. version:byte 1, size_x/y/z:short, palette:list{Name,Properties}, blocks:int[] with two
16-bit palette indices per int (first in the HIGH half; odd count -> last in the high half), flat index
(y*size_z + z)*size_x + x; tile_entities:list (x,y,z shorts, relative), entities:list, required_mods:list<string>,
name:string, architects:list<string>, mcversion:int, optional_data.structurize.primary_offset {x,y,z} = hut block.
"""
from . import nbt
from .nbt import Byte, IntArray, Short

MC_VERSION = 3955


def unpack_blocks(data, count):
    flat = []
    for v in data:
        v &= 0xFFFFFFFF
        flat.append(v >> 16)
        flat.append(v & 0xFFFF)
    return flat[:count]


def pack_blocks(flat):
    out = []
    for k in range(0, len(flat), 2):
        hi = flat[k]
        lo = flat[k + 1] if k + 1 < len(flat) else 0
        v = (hi << 16) | lo
        out.append(v - (1 << 32) if v >= 1 << 31 else v)
    return IntArray(out)


def read(path):
    root = nbt.read(path)
    sx, sy, sz = root["size_x"], root["size_y"], root["size_z"]
    root["_flat"] = unpack_blocks(root["blocks"], sx * sy * sz)
    return root


def write(path, root):
    out = {k: v for k, v in root.items() if not k.startswith("_")}
    if "_flat" in root:
        out["blocks"] = pack_blocks(root["_flat"])
    nbt.write(path, out)


def idx(root, x, y, z):
    return (y * root["size_z"] + z) * root["size_x"] + x


def from_grid(grid, name, hut_block, hut_pos, hut_facing="north", required_mods=("minecolonies",), architects=(),
              tags=()):
    """Turn a culturegen Grid into a blueprint with the hut block at hut_pos (grid coords, after normalise)."""
    grid.normalise()
    grid.set(*hut_pos, hut_block, facing=hut_facing)
    (_, _, _), (Mx, My, Mz) = grid.bounds()
    sx, sy, sz = Mx + 1, My + 1, Mz + 1
    palette, index = [{"Name": "structurize:blocksubstitution"}], {("structurize:blocksubstitution", ()): 0}
    flat = [0] * (sx * sy * sz)  # untouched cells keep the terrain, like structure_void in .nbt
    for (x, y, z), (b, props) in grid.cells.items():
        key = (b, tuple(sorted(props.items())))
        if key not in index:
            index[key] = len(palette)
            e = {"Name": b}
            if props:
                e["Properties"] = dict(sorted(props.items()))
            palette.append(e)
        flat[(y * sz + z) * sx + x] = index[key]
    hx, hy, hz = hut_pos
    stem = name[:-len(".blueprint")] if name.endswith(".blueprint") else name
    tes = []
    for (x, y, z), be in grid.block_entities.items():
        if be.get("id") == "minecraft:jigsaw":
            continue
        t = dict(be)
        t.update({"x": Short(x), "y": Short(y), "z": Short(z)})
        tes.append(t)
    tes.append({
        "id": "minecolonies:colonybuilding", "x": Short(hx), "y": Short(hy), "z": Short(hz),
        "mirror": Byte(0), "inWarehouse": Byte(0), "version": 0, "type": "minecraft:", "pack": "", "path": name,
        "blueprintDataProvider": {
            "corner1": {"x": -hx, "y": -hy, "z": -hz},
            "corner2": {"x": sx - 1 - hx, "y": sy - 1 - hy, "z": sz - 1 - hz},
            "path": name, "schematicName": stem, "pack": "", "posTagMap": _tag_map(tags, hut_pos)},
    })
    return {
        "version": Byte(1), "size_x": Short(sx), "size_y": Short(sy), "size_z": Short(sz),
        "palette": palette, "_flat": flat, "tile_entities": tes, "entities": [],
        "required_mods": list(required_mods), "name": name, "architects": list(architects) or ["culturegen"],
        "mcversion": MC_VERSION,
        "optional_data": {"structurize": {"primary_offset": {"x": hx, "y": hy, "z": hz}}},
    }


def _tag_map(tags, hut_pos):
    """[(x, y, z, name)] in grid coords -> MineColonies posTagMap, positions relative to the hut block."""
    by = {}
    for x, y, z, n in tags:
        by.setdefault((x - hut_pos[0], y - hut_pos[1], z - hut_pos[2]), []).append(n)
    return [{"tagPos": {"x": x, "y": y, "z": z}, "tagNameList": [{"tagName": n} for n in ns]}
            for (x, y, z), ns in sorted(by.items())]


def to_grid(root):
    """Blueprint -> culturegen Grid (for preview renders). Substitution placeholders are dropped."""
    from .grid import Grid
    g = Grid()
    sx, sy, sz = root["size_x"], root["size_y"], root["size_z"]
    pal = root["palette"]
    for i, p in enumerate(root["_flat"]):
        e = pal[p]
        if e["Name"].startswith("structurize:") or e["Name"] == "minecraft:air":
            continue
        x = i % sx
        z = (i // sx) % sz
        y = i // (sx * sz)
        g.cells[(x, y, z)] = (e["Name"], {k: str(v) for k, v in e.get("Properties", {}).items()})
    return g

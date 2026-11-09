"""Isometric preview renderer for a Grid. Sanity/approval render only; the .nbt is the data.

Each block is split into N^3 sub-voxels so slabs, stairs, fences, doors, torches and carpets keep their shape.
Faces are painted from small procedural textures that APPROXIMATE vanilla colours (no game jar in the cloud),
so read these as layout + palette previews, not final in-game looks.
"""
import random
import zlib

import numpy as np
from PIL import Image, ImageDraw

N = 8
FLAME = "x:flame"
GRASS = "minecraft:grass_block"
DIRT = "minecraft:dirt"

# base colours (approximate vanilla averages) and texture style per face
LOOK = {
    "minecraft:cobblestone": ("cobble", "#7e7e7e", "#5c5c5c", "#9c9c9c"),
    "minecraft:mossy_cobblestone": ("moss", "#7a7a7a", "#586f36", "#6d8a3e"),
    "minecraft:packed_mud": ("noise", "#8e6b53", "#7d5c46", "#a07c62"),
    "minecraft:mud_bricks": ("bricks", "#8a6a50", "#6c5040", "#9a7a5e"),
    "minecraft:coarse_dirt": ("noise", "#77553a", "#5f4430", "#8a6648"),
    "minecraft:rooted_dirt": ("noise", "#8f6a4e", "#6f5038", "#a8846a"),
    "minecraft:dirt": ("noise", "#86603f", "#6c4c32", "#977050"),
    "minecraft:stripped_spruce_log": ("log", "#75593a", "#634a30", "#8a6c48"),
    "minecraft:stripped_spruce_wood": ("bark", "#75593a", "#634a30", "#8a6c48"),
    "minecraft:spruce_log": ("log_bark", "#3d2a17", "#2c1d10", "#6b5232"),
    "minecraft:spruce_planks": ("planks", "#73552f", "#5b4226", "#86643a"),
    "minecraft:hay_block": ("hay", "#b39a1c", "#8d6f10", "#7a2e18"),
    "minecraft:spruce_slab": ("planks", "#73552f", "#5b4226", "#86643a"),
    "minecraft:spruce_stairs": ("planks", "#73552f", "#5b4226", "#86643a"),
    "minecraft:spruce_fence": ("planks", "#6b4f2c", "#56401f", "#7e5f36"),
    "minecraft:spruce_door": ("planks", "#5e4429", "#47331e", "#735634"),
    "minecraft:spruce_trapdoor": ("planks", "#664a2b", "#4e3920", "#795a35"),
    "minecraft:ladder": ("planks", "#7d5c33", "#5f4425", "#937040"),
    "minecraft:wall_torch": ("flat", "#6b4a28", "#6b4a28", "#6b4a28"),
    "minecraft:campfire": ("bark", "#4c3620", "#3a2816", "#6b5232"),
    "minecraft:brown_carpet": ("noise", "#72472a", "#633d22", "#7d5232"),
    "minecraft:light_gray_carpet": ("noise", "#8e8e86", "#7f7f78", "#a0a098"),
    "minecraft:barrel": ("planks", "#6a4e2e", "#4f3a22", "#86653c"),
    "minecraft:brown_wall_banner": ("banner", "#72472a", "#633d22", "#e8e6dc"),
    "minecraft:skeleton_skull": ("skull", "#c9c8b6", "#a8a796", "#2c2c2c"),
    "minecraft:crafting_table": ("planks", "#8a6a3e", "#5b4226", "#a07c4a"),
    "minecraft:smoker": ("cobble", "#5a5450", "#3e3a36", "#7a6e66"),
    "minecraft:dirt_path": ("noise", "#94753f", "#7e6234", "#a8884e"),
    "minecraft:brown_bed": ("noise", "#6e3f22", "#5a3219", "#d8d2c0"),
    "minecraft:chest": ("planks", "#9a6e2e", "#6e4c1e", "#b4843c"),
    "minecraft:furnace": ("cobble", "#6e6e6e", "#4a4a4a", "#8a8a8a"),
    "minecolonies:blockminecoloniesrack": ("planks", "#5e4429", "#3a2a18", "#8a6a40"),
    "minecolonies:blockstash": ("planks", "#a07a3a", "#6e5226", "#c49a4e"),
    "minecolonies:blockhutcitizen": ("flat", "#d4a017", "#b8860b", "#f0c040"),
    "minecolonies:blockhuttownhall": ("flat", "#d4a017", "#b8860b", "#f0c040"),
    "minecolonies:blockhutbuilder": ("flat", "#d4a017", "#b8860b", "#f0c040"),
    "minecraft:water": ("noise", "#3f63c8", "#3557b4", "#5478d8"),
    "minecraft:sand": ("noise", "#dbcf9c", "#c8ba84", "#e6dcae"),
    "minecraft:spruce_fence_gate": ("planks", "#6b4f2c", "#56401f", "#7e5f36"),
    "minecolonies:blockhutplantation": ("flat", "#d4a017", "#b8860b", "#f0c040"),
    "minecolonies:blockhutfisherman": ("flat", "#d4a017", "#b8860b", "#f0c040"),
    "minecolonies:blockhutbarracks": ("flat", "#d4a017", "#b8860b", "#f0c040"),
    "minecolonies:blockhutbarrackstower": ("flat", "#d4a017", "#b8860b", "#f0c040"),
    GRASS: ("grass", "#6a9a3c", "#5a8632", "#86603f"),
    FLAME: ("flat", "#ffcf4a", "#ffcf4a", "#ffcf4a"),
}


def _hex(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], dtype=float)


def _texture(name, face):
    """face: 'top' | 'side'. Returns N x N x 3 (row = v downward... we index [u][v])."""
    style, a, b, c = LOOK.get(name, ("noise", "#8a8a8a", "#777777", "#9a9a9a"))
    A, B, C = _hex(a), _hex(b), _hex(c)
    rng = random.Random(zlib.crc32(f"{name}/{face}".encode()))
    t = np.zeros((N, N, 3))
    for u in range(N):
        for v in range(N):  # v = 0 is the TOP row of a side face
            r = rng.random()
            col = A
            if style == "noise":
                col = B if r < 0.25 else C if r > 0.85 else A
            elif style == "cobble":
                col = B if (u * 3 + v * 5) % 7 in (0, 3) else C if r > 0.8 else A
            elif style == "moss":
                col = (B if r < 0.35 else C) if (u + v * 2) % 5 < 2 else (_hex("#5c5c5c") if r < 0.3 else A)
            elif style == "bricks":
                mortar = v % 4 == 3 or (u + (4 if (v // 4) % 2 else 0)) % 8 == 0
                col = B if mortar else (C if r > 0.8 else A)
            elif style == "planks":
                col = B if v % 4 == 3 else (C if r > 0.85 else A)
                if face == "top":
                    col = B if u % 4 == 3 else (C if r > 0.85 else A)
            elif style in ("log", "log_bark", "bark"):
                if face == "top" and style != "bark":
                    d = max(abs(u - 3.5), abs(v - 3.5))
                    col = C if int(d) % 2 == 0 else (B if style == "log" else A * 0.5 + C * 0.5)
                    if d > 3:
                        col = A
                else:
                    col = B if (u + (rng.random() < 0.3)) % 3 == 0 else A
            elif style == "hay":
                if face == "top":
                    col = B if r < 0.3 else A
                else:
                    col = C if v in (2, 5) and u % 2 == 0 else (B if u % 2 else A)
            elif style == "grass":
                col = (B if r < 0.3 else A) if face == "top" else (A if v == 0 or (v == 1 and r < 0.5) else C)
            elif style == "banner":
                skull = {(3, 2), (4, 2), (2, 3), (3, 3), (4, 3), (5, 3), (3, 4), (4, 4), (3, 5), (4, 5)}
                col = C if (u, v) in skull and face == "side" else (B if r < 0.2 else A)
            elif style == "skull":
                col = C if face == "side" and v in (3,) and u in (2, 5) else (B if r < 0.2 else A)
            t[u, v] = col
    return t


def _shape(name, props):
    """Return list of (box, look_name) with box in sub-voxel units (may exceed 0..N)."""
    f = props.get("facing", "north")
    opp = {"north": "south", "south": "north", "east": "west", "west": "east"}.get(f, f)
    full = ((0, 0, 0), (N, N, N))
    h = N // 2

    def plate(side, th, y0=0, y1=N, inset=0):
        x0, z0, x1, z1 = inset, inset, N - inset, N - inset
        if side == "north":
            z0, z1 = 0, th
        elif side == "south":
            z0, z1 = N - th, N
        elif side == "west":
            x0, x1 = 0, th
        elif side == "east":
            x0, x1 = N - th, N
        return ((x0, y0, z0), (x1, y1, z1))

    if name.endswith("_slab"):
        t = props.get("type", "bottom")
        return [(full, name)] if t == "double" else [(((0, 0, 0), (N, h, N)) if t == "bottom" else ((0, h, 0), (N, N, N)), name)]
    if name.endswith("_stairs"):
        (x0, _, z0), (x1, _, z1) = plate(f, h)
        return [(((0, 0, 0), (N, h, N)), name), (((x0, h, z0), (x1, N, z1)), name)]
    if name.endswith("_fence"):
        out = [(((3, 0, 3), (5, N, 5)), name)]
        arms = {"north": ((3, 0), (5, 3)), "south": ((3, 5), (5, N)), "west": ((0, 3), (3, 5)), "east": ((5, 3), (N, 5))}
        for d, ((ax0, az0), (ax1, az1)) in arms.items():
            if props.get(d) == "true":
                out += [(((ax0, 5, az0), (ax1, 7, az1)), name), (((ax0, 2, az0), (ax1, 3, az1)), name)]
        return out
    if name.endswith("_door"):
        return [(plate(opp, 2), name)]
    if name.endswith("_trapdoor"):
        if props.get("open") == "true":
            return [(plate(opp, 2), name)]
        return [(((0, 0, 0), (N, 2, N)) if props.get("half") == "bottom" else ((0, N - 2, 0), (N, N, N)), name)]
    if name == "minecraft:ladder":
        return [(plate(opp, 1), name)]
    if name.endswith("wall_torch"):
        (x0, _, z0), (x1, _, z1) = plate(opp, 2, inset=3)
        return [(((x0, 2, z0), (x1, 6, z1)), name), (((x0, 6, z0), (x1, 7, z1)), FLAME)]
    if name.endswith("_bed"):
        return [(((0, 0, 0), (N, 5, N)), name)]
    if name.startswith("structurize:"):
        return []
    if name.endswith("_carpet"):
        return [(((0, 0, 0), (N, 1, N)), name)]
    if name == "minecraft:campfire":
        return [(((0, 0, 1), (N, 2, 3)), name), (((0, 0, 5), (N, 2, 7)), name), (((1, 2, 0), (3, 3, N)), name),
                (((5, 2, 0), (7, 3, N)), name), (((2, 2, 2), (6, 6, 6)), FLAME)]
    if name.endswith("_skull"):
        return [(((2, 0, 2), (6, 4, 6)), name)]
    if name.endswith("_wall_banner"):
        (x0, _, z0), (x1, _, z1) = plate(opp, 1, inset=1)
        return [(((x0, -6, z0), (x1, N - 1, z1)), name)]
    if name == "minecraft:air":
        return []
    return [(full, name)]


def _transform(cells, view):
    """view 'front' (camera north-west, sees north + west faces) or 'back' (rotated 180)."""
    if view == "front":
        return dict(cells)
    xs = [p[0] for p in cells]
    zs = [p[2] for p in cells]
    mx, mz = max(xs) + min(xs), max(zs) + min(zs)
    flip = {"north": "south", "south": "north", "east": "west", "west": "east"}
    out = {}
    for (x, y, z), (b, p) in cells.items():
        q = dict(p)
        if "facing" in q:
            q["facing"] = flip.get(q["facing"], q["facing"])
        for d in ("north", "south", "east", "west"):
            if d in p:
                q[flip[d]] = p[d]
        out[(mx - x, y, mz - z)] = (b, q)
    return out


def render(grid, path, view="front", cut_y=None, scale=3, ground=True):
    cells = {k: v for k, v in grid.cells.items() if cut_y is None or k[1] < cut_y}
    for k, (b, p) in list(cells.items()):  # jigsaws render as what they become
        if b == "minecraft:jigsaw":
            cells[k] = (grid.block_entities[k]["final_state"], {})
    cells = _transform(cells, view)
    if ground:
        xs = [p[0] for p in cells]
        zs = [p[2] for p in cells]
        for x in range(min(xs) - 2, max(xs) + 3):
            for z in range(min(zs) - 2, max(zs) + 3):
                cells.setdefault((x, -1, z), (DIRT, {}))
                cells.setdefault((x, 0, z), (GRASS, {}))
    mins = np.min(np.array(list(cells)), axis=0)
    maxs = np.max(np.array(list(cells)), axis=0)
    off = mins.copy()
    off[1] -= 1  # banners hang below their cell
    dims = (maxs - mins + np.array([1, 2, 1])) * N
    occ = np.zeros(tuple(dims), dtype=np.int16)
    names = [None]
    nidx = {}
    for (x, y, z), (b, p) in cells.items():
        for ((x0, y0, z0), (x1, y1, z1)), look in _shape(b, p):
            if look not in nidx:
                nidx[look] = len(names)
                names.append(look)
            bx, by, bz = (x - off[0]) * N, (y - off[1]) * N, (z - off[2]) * N
            occ[bx + x0:bx + x1, max(0, by + y0):by + y1, bz + z0:bz + z1] = nidx[look]
    tex = {i: (_texture(n, "top"), _texture(n, "side")) for i, n in enumerate(names) if n}

    filled = occ > 0
    pad = np.pad(filled, 1)
    top = filled & ~pad[1:-1, 2:, 1:-1]
    west = filled & ~pad[:-2, 1:-1, 1:-1]
    north = filled & ~pad[1:-1, 1:-1, :-2]
    vis = top | west | north
    gx, gy, gz = np.nonzero(vis)
    order = np.argsort(-gx - gz + gy, kind="stable")
    s = scale
    X, Y, Z = dims
    W = (X + Z) * s + 4 * s
    H = int((X + Z) * s / 2 + Y * s) + 4 * s
    img = Image.new("RGB", (W, H), "#20232a")
    d = ImageDraw.Draw(img)
    ox, oy = Z * s + 2 * s, int((X + Z) * s / 2 + Y * s) + 2 * s

    def P(x, y, z):
        return (ox + (x - z) * s, oy - (x + z) * s / 2 - y * s)

    for i in order:
        x, y, z = int(gx[i]), int(gy[i]), int(gz[i])
        b = int(occ[x, y, z])
        tt, ts = tex[b]
        if top[x, y, z]:
            c = tt[x % N, z % N]
            d.polygon([P(x, y + 1, z), P(x + 1, y + 1, z), P(x + 1, y + 1, z + 1), P(x, y + 1, z + 1)], fill=tuple(int(v) for v in c))
        if north[x, y, z]:
            c = ts[x % N, (N - 1) - (y % N)] * 0.8
            d.polygon([P(x, y, z), P(x + 1, y, z), P(x + 1, y + 1, z), P(x, y + 1, z)], fill=tuple(int(v) for v in c))
        if west[x, y, z]:
            c = ts[z % N, (N - 1) - (y % N)] * 0.64
            d.polygon([P(x, y, z), P(x, y, z + 1), P(x, y + 1, z + 1), P(x, y + 1, z)], fill=tuple(int(v) for v in c))
    from PIL import ImageChops
    bbox = ImageChops.difference(img, Image.new("RGB", img.size, "#20232a")).getbbox()
    img = img.crop((max(0, bbox[0] - 12), max(0, bbox[1] - 12), min(W, bbox[2] + 12), min(H, bbox[3] + 12)))
    img.save(path)
    return img

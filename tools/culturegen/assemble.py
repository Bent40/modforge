"""Flat-ground jigsaw assembly SIMULATION, for a whole-village preview render.

Mirrors the vanilla rules that matter for layout (name/target matching, opposite facings, weighted pool picks,
random rotation, no overlapping pieces, depth limit). It is not the game's generator: real terrain, heightmaps
and priorities will shift things. Use it to judge spacing and mix, not exact placement.
"""
import random

from .grid import Grid

DIRS = {"north": (0, -1), "east": (1, 0), "south": (0, 1), "west": (-1, 0)}
CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east"}


def _rot_dir(d, r):
    for _ in range(r):
        d = CW.get(d, d)
    return d


def _rot_xz(x, z, r):
    for _ in range(r):
        x, z = -z, x
    return x, z


def _rot_props(b, p, r):
    q = dict(p)
    if "facing" in q:
        q["facing"] = _rot_dir(q["facing"], r)
    if "orientation" in q:
        f, u = q["orientation"].split("_")
        q["orientation"] = f"{_rot_dir(f, r)}_{u}"
    if any(k in p for k in DIRS):
        for k in DIRS:
            if k in p:
                q[_rot_dir(k, r)] = p[k]
    if "axis" in q and r % 2 and q["axis"] in ("x", "z"):
        q["axis"] = "z" if q["axis"] == "x" else "x"
    if "rotation" in q:
        q["rotation"] = str((int(q["rotation"]) + 4 * r) % 16)
    return q


def _place(piece, r, off):
    cells, bes = {}, {}
    for (x, y, z), (b, p) in piece.cells.items():
        rx, rz = _rot_xz(x, z, r)
        cells[(rx + off[0], y + off[1], rz + off[2])] = (b, _rot_props(b, p, r))
    for (x, y, z), be in piece.block_entities.items():
        rx, rz = _rot_xz(x, z, r)
        bes[(rx + off[0], y + off[1], rz + off[2])] = be
    return cells, bes


def _box(cells):
    xs, ys, zs = zip(*cells)
    return min(xs), min(zs), max(xs), max(zs)


def _hit(a, b):
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def assemble(pieces, pools, start_pool, size, seed=1):
    """pieces: id -> Grid; pools: full pool id -> {piece id: weight}."""
    rng = random.Random(seed)
    world = Grid()
    boxes = []
    start = rng.choices(list(pools[start_pool]), weights=list(pools[start_pool].values()))[0]
    cells, bes = _place(pieces[start], 0, (0, 0, 0))
    queue = []

    def commit(cells, bes, depth, used=None):
        boxes.append(_box([k for k, v in cells.items() if v[0] != "minecraft:jigsaw" or True]))
        for k, v in cells.items():
            if v[0] == "minecraft:jigsaw":
                be = bes[k]
                if k != used:
                    queue.append((depth, k, v[1]["orientation"].split("_")[0], be))
                world.cells[k] = (be["final_state"], {})
            else:
                world.cells[k] = v
        for k, be in bes.items():
            if be.get("id") != "minecraft:jigsaw":
                world.block_entities[k] = be

    commit(cells, bes, 0)
    placed = [start]
    while queue:
        depth, pos, facing, j = queue.pop(0)
        if j["pool"] == "minecraft:empty" or depth >= size or j["pool"] not in pools:
            continue
        pool = pools[j["pool"]]
        options = list(pool)
        weights = [pool[o] for o in options]
        tried = set()
        while len(tried) < len(options):
            cid = rng.choices(options, weights=weights)[0]
            if cid in tried:
                continue
            tried.add(cid)
            child = pieces[cid]
            ok = False
            for (cx, cy, cz), be in child.block_entities.items():
                if be.get("id") != "minecraft:jigsaw" or be["name"] != j["target"]:
                    continue
                cf = child.cells[(cx, cy, cz)][1]["orientation"].split("_")[0]
                for r in rng.sample(range(4), 4):
                    if _rot_dir(cf, r) != OPP[facing]:
                        continue
                    rx, rz = _rot_xz(cx, cz, r)
                    dx, dz = DIRS[facing]
                    target = (pos[0] + dx, pos[1], pos[2] + dz)
                    off = (target[0] - rx, target[1] - cy, target[2] - rz)
                    cells, bes = _place(child, r, off)
                    box = _box(list(cells))
                    if any(_hit(box, b) for b in boxes):
                        continue
                    commit(cells, bes, depth + 1, used=target)
                    placed.append(cid)
                    ok = True
                    break
                if ok:
                    break
            if ok:
                break
    return world, placed

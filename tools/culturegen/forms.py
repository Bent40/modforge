"""Building forms. Each form takes (params, palette) and returns a Grid. Forms only name ROLES, never block ids.

Facing conventions used here (vanilla blockstates): door, open trapdoor, ladder, wall torch and wall banner all
sit on the side OPPOSITE their `facing` (they face away from what they hang on). Stairs: `facing` = high side.
Front of every building is z = 0 (north).
"""
import math

from .grid import Grid


def _role(g, pal, x, y, z, role, **props):
    g.set(x, y, z, pal.pick(role), **props)


def _log(g, pal, x, y, z, role="frame", axis="y"):
    g.set(x, y, z, pal.pick(role), axis=axis)


def _air_columns(g, cols, y0, y_stop_after):
    """Fill air up each column from y0 until the first set cell above y_stop_after."""
    for (x, z) in cols:
        y = y0
        while y < 64:
            c = g.get(x, y, z)
            if c is not None and y > y_stop_after:
                break
            if c is None:
                g.air(x, y, z)
            y += 1


def _totem(g, pal, x, z, ground_y=0, rot=8):
    """Bone totem motif: footing, two fence posts, a beast skull facing north (rotation 8)."""
    _role(g, pal, x, ground_y, z, "foundation")
    g.set(x, ground_y + 1, z, pal.main("trim"))
    g.set(x, ground_y + 2, z, pal.main("trim"))
    g.set(x, ground_y + 3, z, pal.main("trophy"), rotation=rot, powered="false")


def _torch(g, pal, x, y, z, facing):
    g.set(x, y, z, pal.main("light"), facing=facing)


def _shutter(g, pal, x, y, z, facing):
    g.set(x, y, z, pal.main("shutter"), facing=facing, half="bottom", open="true", powered="false",
          waterlogged="false")


def _door(g, pal, x, y, z, facing="south"):
    for half, dy in (("lower", 0), ("upper", 1)):
        g.set(x, y + dy, z, pal.main("door"), facing=facing, half=half, hinge="left", open="false",
              powered="false")


def _banner(g, pal, x, y, z, facing, pattern):
    g.set(x, y, z, pal.main("banner"), facing=facing)
    g.block_entities[(x, y, z)] = {"id": "minecraft:banner", "patterns": [dict(p) for p in pattern]}


def _ns(culture, name):
    return f"{culture['_ns']}:{name}"


def _pool(culture, pool):
    return f"{culture['_ns']}:{culture['_race']}/{pool}"


def _jigsaw(g, x, y, z, facing, name, target="minecraft:empty", pool="minecraft:empty",
            final="minecraft:air", joint="aligned"):
    """Jigsaw connector. A child connects where its `name` equals the parent's `target`; facings end opposite."""
    g.set(x, y, z, "minecraft:jigsaw", orientation=f"{facing}_up")
    g.block_entities[(x, y, z)] = {"id": "minecraft:jigsaw", "name": name, "target": target, "pool": pool,
                                   "final_state": final, "joint": joint,
                                   "selection_priority": 0, "placement_priority": 0}


def _entrance(g, culture, x, z, kind="building_entrance", final="minecraft:dirt_path"):
    _jigsaw(g, x, 0, z, "north", _ns(culture, kind), final=final)


def round_hut(p, pal, culture):
    D, H = p["diameter"], p["wall_height"]
    o = 1  # overhang margin
    c = (D - 1) / 2
    r_wall = D / 2 - 0.3

    def dist(i, j):
        return math.hypot(i - c, j - c)

    disc = {(i, j) for i in range(D) for j in range(D) if dist(i, j) <= r_wall}
    ring = {(i, j) for (i, j) in disc if any((i + a, j + b) not in disc for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    g = Grid()
    W = lambda i: i + o  # local -> grid
    posts = {(i, j) for (i, j) in ring if abs(i - c) == abs(j - c)}
    door = (int(c), 0)
    windows = {(0, int(c)): "east", (D - 1, int(c)): "west"}

    for (i, j) in disc:
        x, z = W(i), W(j)
        if (i, j) in ring:
            _role(g, pal, x, 0, z, "foundation")
            for y in range(1, H + 1):
                if (i, j) in posts:
                    _log(g, pal, x, y, z)
                elif (i, j) == door and y <= 2:
                    continue
                elif (i, j) in windows and y == 2:
                    _shutter(g, pal, x, y, z, windows[(i, j)])
                else:
                    _role(g, pal, x, y, z, "wall")
        else:
            _role(g, pal, x, 0, z, "floor")
    _door(g, pal, W(door[0]), 1, W(door[1]), facing="south")

    # top plate: a spruce log ring on the wall
    for (i, j) in ring:
        _log(g, pal, W(i), H + 1, W(j), role="beam", axis="x")
    # thatch cone: each step is the ring between its radius and the next one up, so it is closed from above
    r_out = r_wall + o
    span = [(i, j) for i in range(-o, D + o) for j in range(-o, D + o)]
    for (i, j) in span:
        if r_wall < dist(i, j) <= r_out:
            g.set(W(i), H + 1, W(j), pal.main("eave"), type="bottom", waterlogged="false")
    k = 1
    while r_wall - (k - 1) > 0:
        R = r_wall - (k - 1)
        for (i, j) in span:
            if R - 1 < dist(i, j) <= R:
                g.set(W(i), H + 1 + k, W(j), pal.main("thatch"), axis="y")
        k += 1
    _air_columns(g, [(W(i), W(j)) for (i, j) in disc - ring], 1, H)

    # interior: hearth centre, hides at the back, one barrel
    cx = W(int(c))
    g.set(cx, 1, cx, pal.main("hearth"), facing="south", lit="true", signal_fire="false", waterlogged="false")
    for i in range(int(c) - 1, int(c) + 2):
        g.set(W(i), 1, W(D - 2), pal.pick("bedding"))
    g.set(W(1), 1, W(int(c)), pal.main("storage"), facing="up", open="false")
    # outside: torch right of door, totem left of door
    _torch(g, pal, W(door[0] + 1), 2, W(door[1]) - 1, "north")
    _totem(g, pal, W(door[0] - 2), W(0) - 1)
    _entrance(g, culture, W(door[0]), W(0) - 1)
    return g, {"cut_y": 3}


def long_hall(p, pal, culture):
    Wd, L, H, sp = p["width"], p["length"], p["wall_height"], p["post_spacing"]
    o = 1
    g = Grid()
    x0, x1, z0, z1 = o, o + Wd - 1, o, o + L - 1
    xm = (x0 + x1) // 2
    long_posts = set(range(z0, z1 + 1, sp)) | {z1}
    win_z = [z + sp // 2 for z in range(z0, z1, sp) if z + sp // 2 < z1]
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            if not edge:
                _role(g, pal, x, 0, z, "floor")
                continue
            _role(g, pal, x, 0, z, "foundation")
            is_post = (x in (x0, x1) and z in long_posts) or (z in (z0, z1) and x in (x0, x1, xm - 1, xm + 1)) \
                or (z == z1 and x == xm)
            for y in range(1, H + 1):
                if is_post:
                    _log(g, pal, x, y, z)
                elif z == z0 and x == xm and y <= 2:
                    continue
                elif x in (x0, x1) and z in win_z and y == 2:
                    _shutter(g, pal, x, y, z, "east" if x == x0 else "west")
                else:
                    _role(g, pal, x, y, z, "wall")
            # top plate
            axis = "z" if x in (x0, x1) else "x"
            _log(g, pal, x, H + 1, z, role="beam", axis=axis)
    _door(g, pal, xm, 1, z0)
    # stepped thatch gable along z, overhang front/back and sides
    yb = H + 1
    for k in range((Wd + 2) // 2 + 1):
        xa, xb = x0 - o + k, x1 + o - k
        if xa > xb:
            break
        for z in range(z0 - o, z1 + o + 1):
            for x in {xa, xb}:
                if k == 0:
                    g.set(x, yb, z, pal.main("eave"), type="bottom", waterlogged="false")
                elif g.get(x, yb + k, z) is None:
                    g.set(x, yb + k, z, pal.main("thatch"), axis="z")
        # gable infill under this roof step
        for z in (z0, z1):
            for x in range(xa + 1, xb):
                if yb + k > yb and g.get(x, yb + k, z) is None:
                    _role(g, pal, x, yb + k, z, "gable")
    interior = [(x, z) for x in range(x0 + 1, x1) for z in range(z0 + 1, z1)]
    _air_columns(g, interior, 1, H + 1)
    # interior dressing
    zc = (z0 + z1) // 2
    g.set(xm, 1, zc, pal.main("hearth"), facing="south", lit="true", signal_fire="false", waterlogged="false")
    g.set(xm, 1, z1 - 1, pal.main("seat"), facing="south", half="bottom", shape="straight", waterlogged="false")
    for z in (z0 + 2, z0 + 3, z1 - 3, z1 - 4):
        g.set(x0 + 1, 1, z, pal.pick("bedding"))
        g.set(x1 - 1, 1, z, pal.pick("bedding"))
    for x in (x0 + 1, x1 - 1):
        g.set(x, 1, z1 - 1, pal.main("storage"), facing="up", open="false")
    post_z = sorted(long_posts)[1]
    _torch(g, pal, x0 + 1, 3, post_z, "east")
    _torch(g, pal, x1 - 1, 3, sorted(long_posts)[-2], "west")
    # outside: torches on the door posts, twin totems, tribe banner on the front gable
    _torch(g, pal, xm - 1, 3, z0 - 1, "north")
    _torch(g, pal, xm + 1, 3, z0 - 1, "north")
    _totem(g, pal, xm - 3, z0 - 1)
    _totem(g, pal, xm + 3, z0 - 1)
    _banner(g, pal, xm, yb + 2, z0 - 1, "north", culture["banner_pattern"])
    _entrance(g, culture, xm, z0 - 1, kind="hall_entrance")
    return g, {"cut_y": 3}


def stilt_tower(p, pal, culture):
    Wd, Dh, Rh = p["width"], p["deck_height"], p["roof_height"]
    g = Grid()
    m = Wd - 1
    mid = m // 2
    top = Dh + 3  # posts run up to here; roof starts above
    for (x, z) in ((0, 0), (m, 0), (0, m), (m, m)):
        _role(g, pal, x, 0, z, "foundation")
        for y in range(1, top + 1):
            _log(g, pal, x, y, z)
    _role(g, pal, mid, 0, mid, "foundation")
    for y in range(1, Dh):
        _log(g, pal, mid, y, mid)
    for x in range(Wd):
        for z in range(Wd):
            if g.get(x, Dh, z) is None and not (x == mid and z == mid - 1):
                g.set(x, Dh, z, pal.main("deck"))
    for y in range(1, Dh + 1):
        g.set(mid, y, mid - 1, pal.main("climb"), facing="north", waterlogged="false")
    for x in range(Wd):
        for z in range(Wd):
            if (x in (0, m) or z in (0, m)) and g.get(x, Dh + 1, z) is None:
                g.set(x, Dh + 1, z, pal.main("trim"))
    # stepped hip roof
    yr = top + 1
    for k in range(Rh):
        if k == 0:
            for x in range(-1, m + 2):
                for z in range(-1, m + 2):
                    if x in (-1, m + 1) or z in (-1, m + 1):
                        g.set(x, yr, z, pal.main("eave"), type="bottom", waterlogged="false")
                    elif x in (0, m) or z in (0, m):
                        g.set(x, yr, z, pal.main("thatch"), axis="y")
        else:
            a, b = k, m - k
            if a > b:
                break
            for x in range(a, b + 1):
                for z in range(a, b + 1):
                    if x in (a, b) or z in (a, b):
                        g.set(x, yr + k, z, pal.main("thatch"), axis="y")
    if Rh >= 1:
        g.set(mid, yr + Rh - 1, mid, pal.main("thatch"), axis="y")
    # air under the deck and on the deck
    under = [(x, z) for x in range(Wd) for z in range(Wd)]
    for (x, z) in under:
        for y in range(1, Dh):
            g.air(x, y, z)
    _air_columns(g, [(x, z) for x in range(1, m) for z in range(1, m)], Dh + 1, top)
    # dressing: skull on the front rail, torches on posts, banner under the deck front
    g.set(1, Dh + 2, 0, pal.main("trophy"), rotation=8, powered="false")
    _torch(g, pal, 0, Dh + 2, 1, "south")
    _torch(g, pal, m, Dh + 2, m - 1, "north")
    _banner(g, pal, mid, Dh - 1, -1, "north", culture["banner_pattern"])
    g.set(mid, Dh - 1, 0, pal.main("deck"))  # banner backing board
    _entrance(g, culture, mid, -1)
    return g, {"cut_y": Dh + 2}


def lean_to(p, pal, culture):
    """Open-fronted work shed: low front posts, mud back wall, mono-pitch thatch falling to the front."""
    Wd, D = p["width"], p["depth"]
    m, b = Wd - 1, D - 1
    g = Grid()
    for x in range(Wd):
        for z in range(D):
            _role(g, pal, x, 0, z, "foundation" if z == b or x in (0, m) else "floor")
    for x in (0, m):
        for y in (1, 2):
            _log(g, pal, x, y, 0)
        for y in (1, 2, 3):
            _log(g, pal, x, y, b)
        for z in range(1, b):
            _role(g, pal, x, 1, z, "wall")
    for x in range(1, m):
        for y in (1, 2, 3):
            _role(g, pal, x, y, b, "wall")
    split = (D + 1) // 2  # front half low, back half one higher
    for x in range(-1, Wd + 1):
        g.set(x, 3, -1, pal.main("eave"), type="bottom", waterlogged="false")
        for z in range(0, split):
            g.set(x, 3, z, pal.main("thatch"), axis="x")
        for z in range(split, D):
            g.set(x, 4, z, pal.main("thatch"), axis="x")
        g.set(x, 4, D, pal.main("eave"), type="bottom", waterlogged="false")
    for x in range(1, m):
        for z in range(0, b):
            for y in (1, 2):
                g.air(x, y, z)
        for z in range(split, b):
            g.air(x, 3, z)
    g.set(1, 1, b - 1, pal.main("workbench"))
    g.set(2, 1, b - 1, pal.main("smoker"), facing="north", lit="false")
    g.set(m - 1, 1, b - 1, pal.main("storage"), facing="up", open="false")
    _totem(g, pal, Wd + 1, -1)
    _entrance(g, culture, Wd // 2, -1)
    return g, {"cut_y": 3}


def plaza(p, pal, culture):
    """Village start piece: trampled ground, sunken fire pit, stump stools, four bone totems, four exits."""
    S = p["size"]
    m, c = S - 1, S // 2
    g = Grid()
    for x in range(S):
        for z in range(S):
            d = max(abs(x - c), abs(z - c))
            if (x, z) in ((0, 0), (0, m), (m, 0), (m, m)):
                continue
            _role(g, pal, x, 0, z, "path" if d <= 1 or x == c or z == c else "floor")
            for y in (1, 2, 3):
                g.air(x, y, z)
    for dx, dz in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)):
        _role(g, pal, c + dx, 0, c + dz, "foundation")
    g.set(c, 0, c, pal.main("hearth"), facing="south", lit="true", signal_fire="false", waterlogged="false")
    for dx, dz in ((-3, -2), (3, -2), (-3, 2), (3, 2), (-2, 3), (2, 3)):
        _log(g, pal, c + dx, 1, c + dz)
    for x, z in ((1, 1), (m - 1, 1), (1, m - 1), (m - 1, m - 1)):
        for y in (1, 2, 3):
            g.cells.pop((x, y, z), None)
        _totem(g, pal, x, z)
    streets, chief = _pool(culture, "streets"), _pool(culture, "chief")
    exit_ = _ns(culture, "street_exit")
    _jigsaw(g, c, 0, 0, "north", exit_, _ns(culture, "street"), streets, final=pal.main("path"))
    _jigsaw(g, 0, 0, c, "west", exit_, _ns(culture, "street"), streets, final=pal.main("path"))
    _jigsaw(g, m, 0, c, "east", exit_, _ns(culture, "street"), streets, final=pal.main("path"))
    _jigsaw(g, c, 0, m, "south", exit_, _ns(culture, "hall_entrance"), chief, final=pal.main("path"))
    return g, {"cut_y": None}


def street(p, pal, culture):
    """Terrain-matching path. kind straight: exits ahead + houses both sides; bend_left/right: turns 90 degrees."""
    kind, L = p.get("kind", "straight"), p.get("length", 9)
    g = Grid()
    streets, houses = _pool(culture, "streets"), _pool(culture, "houses")
    if kind == "straight":
        cells = [(x, z) for x in range(3) for z in range(L)]
    else:
        cells = [(x, z) for x in range(3) for z in range(3)]
    for x, z in cells:
        _role(g, pal, x, 0, z, "path")
    path = pal.main("path")
    _jigsaw(g, 1, 0, 0, "north", _ns(culture, "street"), final=path)
    if kind == "straight":
        _jigsaw(g, 1, 0, L - 1, "south", _ns(culture, "street_exit"), _ns(culture, "street"), streets, final=path)
        _jigsaw(g, 0, 0, L // 2, "west", _ns(culture, "street_side"), _ns(culture, "building_entrance"), houses, final=path)
        _jigsaw(g, 2, 0, L // 2, "east", _ns(culture, "street_side"), _ns(culture, "building_entrance"), houses, final=path)
    else:
        out, side = ("east", "west") if kind == "bend_left" else ("west", "east")
        ox, sx = (2, 0) if out == "east" else (0, 2)
        _jigsaw(g, ox, 0, 1, out, _ns(culture, "street_exit"), _ns(culture, "street"), streets, final=path)
        _jigsaw(g, 1, 0, 2, "south", _ns(culture, "street_side"), _ns(culture, "building_entrance"), houses, final=path)
    return g, {"cut_y": None}


FORMS = {"round_hut": round_hut, "long_hall": long_hall, "stilt_tower": stilt_tower, "lean_to": lean_to,
         "plaza": plaza, "street": street}

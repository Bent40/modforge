"""Role markers added around a generated hut so each job reads differently from the street.

Every feature works on a hut grid in anchor coordinates, given the main shell's box (x0, z0, x1, z1 of the walls,
roof overhang excluded) and wall height H. Front = -Z (z0 side). Features only add blocks OUTSIDE the walls or
above the roof, so furnishing and the hut block are untouched, and every level of a hut gets the same feature.
Blocks come from palette roles, so a culture's look still holds.
"""


def _wall_box(g, pal):
    """(x0, z0, x1, z1) of the foundation ring at y=0 (shell walls), ignoring roof overhang and paths."""
    found = set(pal.roles["wall"]) | set(pal.roles["frame"])
    pts = [(x, z) for (x, y, z), c in g.cells.items() if y == 2 and c[0] in found]
    xs, zs = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(zs), max(xs), max(zs)


def _door_x(g, z0):
    xs = [x for (x, y, z), c in g.cells.items() if y == 1 and c[0].endswith("_door") and z == z0]
    return xs[0] if xs else None


def _roof_top(g, x, z):
    ys = [y for (xx, y, zz), c in g.cells.items() if xx == x and zz == z and c[0] != "minecraft:air"]
    return max(ys) if ys else 0


def chimney(g, pal, box, H, culture):
    """Stone chimney up the back wall, smoking campfire on top (smith, cook, baker, kitchen...)."""
    x0, z0, x1, z1 = box
    x, z = x1 - 2, z1 + 1
    top = max(_roof_top(g, x, z1), _roof_top(g, x, z1 - 1)) + 2
    for y in range(0, top + 1):
        g.set(x, y, z, pal.main("foundation"))
    g.set(x, top + 1, z, pal.main("hearth"), facing="south", lit="true", signal_fire="false", waterlogged="false")


def porch(g, pal, box, H, culture):
    """Covered porch on posts in front of the door (residence, tavern, town hall)."""
    x0, z0, x1, z1 = box
    dx = _door_x(g, z0)
    if dx is None:
        return
    for x in range(dx - 2, dx + 3):
        for z in range(z0 - 3, z0):
            g.set(x, 0, z, pal.main("deck"))
            g.set(x, H, z, pal.main("eave"), type="bottom", waterlogged="false")
    for x in (dx - 2, dx + 2):
        for y in range(1, H):
            g.set(x, y, z0 - 3, pal.main("frame"), axis="y")
    g.set(dx - 2, H - 1, z0 - 4, pal.main("light"), facing="north")


def palisade(g, pal, box, H, culture):
    """Pointed log fence around the building with a gate gap and two corner watch platforms (barracks, military)."""
    x0, z0, x1, z1 = box
    dx = _door_x(g, z0)
    rx0, rz0, rx1, rz1 = x0 - 3, z0 - 3, x1 + 3, z1 + 3
    for x in range(rx0, rx1 + 1):
        for z in range(rz0, rz1 + 1):
            if x not in (rx0, rx1) and z not in (rz0, rz1):
                continue
            if z == rz0 and dx is not None and abs(x - dx) <= 1:
                continue                                   # gate gap in front of the door
            g.set(x, 0, z, pal.main("foundation"))
            post = (x - rx0) % 3 == 0 and (z - rz0) % 3 == 0
            for y in (1, 2):
                g.set(x, y, z, pal.main("frame"), axis="y")
            if post:
                g.set(x, 3, z, pal.main("trim"))
    for cx in (rx0, rx1 - 2):                             # front corner platforms
        for x in range(cx, cx + 3):
            for z in range(rz0, rz0 + 3):
                g.set(x, 4, z, pal.main("deck"))
        for x in (cx, cx + 2):
            for z in (rz0, rz0 + 2):
                for y in range(1, 6):
                    g.set(x, y, z, pal.main("frame"), axis="y")
        for x in range(cx, cx + 3):
            g.set(x, 5, rz0, pal.main("trim"))
    if dx is not None:
        _banner_at(g, pal, dx - 2, 4, rz0 - 1, "north", culture)
        _banner_at(g, pal, dx + 2, 4, rz0 - 1, "north", culture)


def _banner_at(g, pal, x, y, z, facing, culture):
    g.set(x, y, z, pal.main("banner"), facing=facing)
    g.block_entities[(x, y, z)] = {"id": "minecraft:banner", "patterns": [dict(p) for p in culture["banner_pattern"]]}


def banners(g, pal, box, H, culture):
    """Tribe banners down both long walls (town hall, tavern, library...)."""
    x0, z0, x1, z1 = box
    for z in range(z0 + 2, z1 - 1, 4):
        for x, f in ((x0 - 1, "west"), (x1 + 1, "east")):
            if g.get(x, H - 1, z) is None or g.get(x, H - 1, z)[0] == "minecraft:air":
                _banner_at(g, pal, x, H - 1, z, f, culture)


def drying_rack(g, pal, box, H, culture):
    """Hay drying rack along the west wall (farmer, plantation, herders)."""
    x0, z0, x1, z1 = box
    x = x0 - 3
    for z in range(z0 + 1, z1, 1):
        g.set(x, 0, z, pal.main("foundation"))
        end = z in (z0 + 1, z1 - 1)
        g.set(x, 1, z, pal.main("frame") if end else pal.main("trim"), **({"axis": "y"} if end else {}))
        g.set(x, 2, z, "minecraft:hay_block", axis="y")
    for z in (z0 + 1, z1 - 1):
        g.set(x, 2, z, pal.main("frame"), axis="y")
        g.set(x, 3, z, pal.main("eave"), type="bottom", waterlogged="false")


def log_pile(g, pal, box, H, culture):
    """Stacked logs against the west wall (lumberjack, sawmill)."""
    x0, z0, x1, z1 = box
    for z in range(z0 + 1, z1):
        for y in (1, 2):
            g.set(x0 - 1, y, z, pal.main("beam"), axis="z")
        if (z - z0) % 2:
            g.set(x0 - 2, 1, z, pal.main("beam"), axis="z")


def bell_spire(g, pal, box, H, culture):
    """A tall open spire with a bell on the roof ridge: makes the town hall the tallest building."""
    x0, z0, x1, z1 = box
    xm, zm = (x0 + x1) // 2, z0 + 2
    base = _roof_top(g, xm, zm) + 1
    for x in (xm - 1, xm + 1):
        for z in (zm - 1, zm + 1):
            for y in range(base - 2, base + 5):
                g.set(x, y, z, pal.main("frame"), axis="y")
    for x in range(xm - 2, xm + 3):
        for z in range(zm - 2, zm + 3):
            g.set(x, base + 5, z, pal.main("thatch"))
    for x in range(xm - 1, xm + 2):
        for z in range(zm - 1, zm + 2):
            g.set(x, base + 6, z, pal.main("thatch"))
    g.set(xm, base + 7, zm, pal.main("thatch"))
    g.set(xm, base + 4, zm, "minecraft:bell", attachment="ceiling", facing="north", powered="false")
    _banner_at(g, pal, xm, base + 3, zm - 2, "north", culture)


FEATURES = {"chimney": chimney, "porch": porch, "palisade": palisade, "banners": banners,
            "drying_rack": drying_rack, "log_pile": log_pile, "bell_spire": bell_spire}


def apply(g, pal, names, box, H, culture):
    for n in names:
        FEATURES[n](g, pal, box, H, culture)

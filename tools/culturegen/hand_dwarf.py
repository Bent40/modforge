"""Hand-designed dwarf buildings (Create theme). Not a generic form: each building is laid out block by block.

Dwarves of the mountain halls: a dark deepslate plinth, polished andesite walls framed by andesite-casing
pillars, a brass band under the eaves, tall framed-glass windows, a steep deepslate-tile roof with a copper
ridge, brick chimneys, and their machines on show (cog trains, a water wheel, a gear clock on the tower).
Front = -Z (z = 0 side). Coordinates: x 0..W-1, z 0..L-1, ground floor y = 1.
"""
from .grid import Grid

P = {
    "plinth": "minecraft:deepslate_bricks",
    "plinth_alt": "minecraft:cracked_deepslate_bricks",
    "plinth_stairs": "minecraft:deepslate_brick_stairs",
    "floor": "minecraft:polished_deepslate",
    "floor_inlay": "create:brass_casing",
    "wall": "minecraft:polished_andesite",
    "wall_alt": "minecraft:andesite",
    "pillar": "create:andesite_casing",
    "band": "create:brass_casing",
    "window": "create:framed_glass",
    "roof": "minecraft:deepslate_tile_stairs",
    "roof_slab": "minecraft:deepslate_tile_slab",
    "ridge": "minecraft:waxed_cut_copper",
    "ridge_slab": "minecraft:waxed_cut_copper_slab",
    "chimney": "minecraft:bricks",
    "door": "minecraft:dark_oak_door",
    "lantern": "minecraft:lantern",
    "cog": "create:cogwheel",
    "big_cog": "create:large_cogwheel",
    "shaft": "create:shaft",
    "wheel": "create:water_wheel",
}


def _stair(g, x, y, z, facing, half="bottom", block=None):
    g.set(x, y, z, block or P["roof"], facing=facing, half=half, shape="straight", waterlogged="false")


def _door(g, x, z, facing="north", hinge="left"):
    g.set(x, 1, z, P["door"], facing=facing, half="lower", hinge=hinge, open="false", powered="false")
    g.set(x, 2, z, P["door"], facing=facing, half="upper", hinge=hinge, open="false", powered="false")


def _wall_block(x, y, z):
    return P["wall_alt"] if (x * 7 + y * 3 + z * 5) % 9 == 0 else P["wall"]


def _gable_roof(g, x0, x1, z0, z1, ybase, overhang=1):
    """Steep stair roof along z: slopes rise one block per block in x; copper ridge; gable ends filled."""
    k = 0
    while True:
        xa, xb = x0 - overhang + k, x1 + overhang - k
        y = ybase + k
        if xa > xb:
            break
        for z in range(z0 - overhang, z1 + overhang + 1):
            if xa == xb:
                g.set(xa, y, z, P["ridge"])
            elif xa + 1 == xb:
                g.set(xa, y, z, P["ridge_slab"], type="bottom", waterlogged="false")
                g.set(xb, y, z, P["ridge_slab"], type="bottom", waterlogged="false")
            else:
                _stair(g, xa, y, z, "east")
                _stair(g, xb, y, z, "west")
                if k == 0:  # eave underside trim
                    _stair(g, xa, y - 1, z, "west", half="top")
                    _stair(g, xb, y - 1, z, "east", half="top")
        for z in (z0, z1):  # gable infill
            for x in range(xa + 1, xb):
                if g.get(x, y, z) is None:
                    g.set(x, y, z, _wall_block(x, y, z))
        if xa + 1 >= xb:
            break
        k += 1
    return ybase + k


def dwarf_hall(p, culture=None):
    """The dwarf town hall. p: width (odd), length, wall_height, tower (bool), wheel (bool), chimneys (0-2)."""
    W, L, H = p["width"], p["length"], p["wall_height"]
    g = Grid()
    xc = W // 2
    pillars_z = set(range(0, L, 4)) | {L - 1}
    # plinth skirt: stairs stepping down outside the footprint
    for x in range(-1, W + 1):
        for z in range(-1, L + 1):
            if x in (-1, W) or z in (-1, L):
                if x in (-1, W) and z in (-1, L):
                    g.set(x, 0, z, P["plinth"])
                    continue
                f = "east" if x == -1 else "west" if x == W else "south" if z == -1 else "north"
                _stair(g, x, 0, z, f, block=P["plinth_stairs"])
    for x in range(W):
        for z in range(L):
            edge = x in (0, W - 1) or z in (0, L - 1)
            if not edge:
                inlay = (x == xc or z == L // 2) and x not in (1, W - 2)
                g.set(x, 0, z, P["floor_inlay"] if inlay else P["floor"])
                for y in range(1, H + 2):
                    g.air(x, y, z)
                continue
            g.set(x, 0, z, P["plinth"])
            pillar = (x in (0, W - 1) and z in pillars_z) or (z in (0, L - 1) and x in (0, W - 1, xc - 2, xc + 2))
            for y in range(1, H + 1):
                if pillar:
                    g.set(x, y, z, P["pillar"])
                elif y <= 2:
                    g.set(x, y, z, P["plinth_alt"] if (x + z + y) % 7 == 0 else P["plinth"])
                elif x in (0, W - 1) and 3 <= y <= H - 2 and (z % 4) == 2:
                    g.set(x, y, z, P["window"])
                elif z in (0, L - 1) and 3 <= y <= H - 2 and x in (xc - 4, xc + 4) and W >= 13:
                    g.set(x, y, z, P["window"])
                else:
                    g.set(x, y, z, _wall_block(x, y, z))
            g.set(x, H + 1, z, P["band"])
    # stepped buttresses at every long-wall pillar: depth along the sides
    for z in sorted(pillars_z)[1:-1]:
        for x, out, f in ((-1, -2, "east"), (W, W + 1, "west")):
            for y in range(0, 4):
                g.set(x, y, z, P["plinth"])
            _stair(g, x, 4, z, f, block=P["plinth_stairs"])
            g.set(out, 0, z, P["plinth"])
            _stair(g, out, 1, z, f, block=P["plinth_stairs"])
    top = _gable_roof(g, 0, W - 1, 0, L - 1, H + 2)
    # round gable windows
    for z in (0, L - 1):
        g.set(xc, H + 4, z, P["window"])
    # main door, steps, lanterns
    _door(g, xc, 0, hinge="left")
    _door(g, xc - 1, 0, hinge="right") if W >= 9 else None
    for x in (xc - 1, xc):
        _stair(g, x, 0, -1, "south", block=P["plinth_stairs"])
    for x in (xc - 2, xc + 1):
        g.set(x, 3, -1, P["lantern"], hanging="false", waterlogged="false")
    # cog train above the door: shaft, big gear, small gears
    gy = H - 1
    g.set(xc, gy, -1, P["big_cog"], axis="z")
    for dx in (-2, 2):
        g.set(xc + dx, gy + 1, -1, P["cog"], axis="z")
    if p.get("tower"):
        _tower(g, xc, top, H)
    if p.get("wheel"):
        _water_wheel(g, -1, L // 2 + 2, H)
    for i in range(p.get("chimneys", 0)):
        _chimney(g, W - 3 if i == 0 else 2, L, top)
    return g


def _tower(g, xc, roof_top, H):
    """Clock tower on the front: 5x5, rises well above the ridge, gear clock face, copper spire."""
    z0, z1 = -4, 0
    x0, x1 = xc - 2, xc + 2
    th = roof_top + 5
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            edge = x in (x0, x1) or z in (z0, z1)
            g.set(x, 0, z, P["plinth"])
            for y in range(1, th + 1):
                if not edge:
                    g.air(x, y, z)
                    continue
                corner = x in (x0, x1) and z in (z0, z1)
                if corner:
                    g.set(x, y, z, P["pillar"])
                elif y in (H + 1, th):
                    g.set(x, y, z, P["band"])
                elif y <= 2:
                    g.set(x, y, z, P["plinth"])
                elif (x == xc or z == (z0 + z1) // 2) and y % 4 == 1 and y > 3:
                    g.set(x, y, z, P["window"])
                else:
                    g.set(x, y, z, _wall_block(x, y, z))
    # open arch into the hall behind the tower, door on the tower front
    for y in (1, 2):
        g.air(xc, y, z1)
        g.air(xc - 1, y, z1)
    _door(g, xc, z0, hinge="left")
    _door(g, xc - 1, z0, hinge="right")
    for x in (xc - 1, xc):
        _stair(g, x, 0, z0 - 1, "south", block=P["plinth_stairs"])
    for x in (xc - 2, xc + 1):
        g.set(x, 3, z0 - 1, P["lantern"], hanging="false", waterlogged="false")
    # gear clock face high on the front
    g.set(xc, th - 3, z0 - 1, P["big_cog"], axis="z")
    g.set(xc, th - 3, z0, P["shaft"], axis="z")
    # stepped copper spire
    for k in range(3):
        for x in range(x0 - 1 + k, x1 + 2 - k):
            for z in range(z0 - 1 + k, z1 + 2 - k):
                on_edge = x in (x0 - 1 + k, x1 + 1 - k) or z in (z0 - 1 + k, z1 + 1 - k)
                if on_edge:
                    f = ("south" if z == z0 - 1 + k else "north" if z == z1 + 1 - k
                         else "east" if x == x0 - 1 + k else "west")
                    _stair(g, x, th + 1 + k, z, f)
                else:
                    g.set(x, th + 1 + k, z, P["roof_slab"], type="bottom", waterlogged="false")
    g.set(xc, th + 4, (z0 + z1) // 2, P["ridge"])
    g.set(xc, th + 5, (z0 + z1) // 2, "minecraft:lightning_rod", facing="up", powered="false", waterlogged="false")


def _water_wheel(g, x, zc, H):
    """Water wheel on the west wall driving a shaft into the hall, with a little race of water below."""
    g.set(x - 1, 2, zc, P["wheel"], axis="x")
    g.set(x, 2, zc, P["shaft"], axis="x")
    for z in range(zc - 2, zc + 3):
        g.set(x - 1, 0, z, "minecraft:water", level="0")
        g.set(x - 2, 0, z, P["plinth"])
        g.set(x - 3, 0, z, P["plinth"])


def _chimney(g, x, L, roof_top):
    z = L
    for y in range(0, roof_top + 3):
        g.set(x, y, z, P["chimney"])
        g.set(x + 1, y, z, P["chimney"])
    g.set(x, roof_top + 3, z, "minecraft:campfire", facing="south", lit="true", signal_fire="false", waterlogged="false")
    g.set(x + 1, roof_top + 3, z, "minecraft:campfire", facing="south", lit="true", signal_fire="false", waterlogged="false")

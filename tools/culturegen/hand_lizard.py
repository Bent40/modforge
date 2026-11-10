"""Hand-designed lizardman buildings (martial arts theme: Mortal Cultivation).

Marsh clan of the Great Marsh, warrior culture: raised mud-brick platforms above the wet ground, red mangrove
posts, packed-mud walls with bamboo screen windows, two-tier hip roofs of dark prismarine tiles with upturned eave
tips, lanterns hung at the corners, water channels with lily pads, and the dojo at the heart of the village.
Front = -Z (z = 0 side). Coordinates: x 0..W-1, z 0..L-1, floor y = 0, ground floor walking level y = 1.
"""
from .grid import Grid

P = {
    "plinth": "minecraft:mud_bricks",
    "plinth_stairs": "minecraft:mud_brick_stairs",
    "plinth_wall": "minecraft:mud_brick_wall",
    "floor": "minecraft:bamboo_mosaic",
    "mat": "minecraft:green_carpet",
    "post": "minecraft:mangrove_log",
    "beam": "minecraft:stripped_mangrove_log",
    "wall": "minecraft:packed_mud",
    "screen": "minecraft:bamboo_trapdoor",
    "planks": "minecraft:mangrove_planks",
    "roof": "minecraft:dark_prismarine_stairs",
    "roof_slab": "minecraft:dark_prismarine_slab",
    "roof_block": "minecraft:dark_prismarine",
    "ridge": "minecraft:waxed_oxidized_cut_copper",
    "door": "minecraft:mangrove_door",
    "lantern": "minecraft:lantern",
    "fence": "minecraft:mangrove_fence",
    "banner": "minecraft:green_wall_banner",
}

FENCE = dict(north="false", south="false", east="false", west="false", waterlogged="false")


def _stair(g, x, y, z, facing, half="bottom", block=None, shape="straight"):
    g.set(x, y, z, block or P["roof"], facing=facing, half=half, shape=shape, waterlogged="false")


def _door(g, x, z, facing="north", hinge="left", y=1):
    g.set(x, y, z, P["door"], facing=facing, half="lower", hinge=hinge, open="false", powered="false")
    g.set(x, y + 1, z, P["door"], facing=facing, half="upper", hinge=hinge, open="false", powered="false")


def hip_roof(g, x0, x1, z0, z1, ybase, overhang=2, lanterns=True):
    """Hip roof with upturned corners: a thin slab eave ring, corner tips raised one block, then stair rings
    stepping inward and up to a copper ridge. Returns the top y."""
    xa, xb, za, zb = x0 - overhang, x1 + overhang, z0 - overhang, z1 + overhang
    for x in range(xa, xb + 1):                  # eave ring: slabs, so the edge reads thin
        for z in (za, zb):
            g.set(x, ybase, z, P["roof_slab"], type="bottom", waterlogged="false")
    for z in range(za, zb + 1):
        for x in (xa, xb):
            g.set(x, ybase, z, P["roof_slab"], type="bottom", waterlogged="false")
    for x, z, f in ((xa, za, "north"), (xb, za, "north"), (xa, zb, "south"), (xb, zb, "south")):
        _stair(g, x, ybase + 1, z, f, half="bottom")   # the upturned tips
        if lanterns:
            g.set(x, ybase - 1, z, P["lantern"], hanging="true", waterlogged="false")
    k, y = 1, ybase
    while True:
        xa, xb, za, zb = x0 - overhang + k, x1 + overhang - k, z0 - overhang + k, z1 + overhang - k
        if xa > xb or za > zb:
            break
        y = ybase + k
        if xa == xb or za == zb:                 # ridge line
            for x in range(xa, xb + 1):
                for z in range(za, zb + 1):
                    g.set(x, y, z, P["ridge"])
            break
        for x in range(xa, xb + 1):
            for z in range(za, zb + 1):
                edge = x in (xa, xb) or z in (za, zb)
                if not edge:
                    continue
                if x == xa and z == za:
                    _stair(g, x, y, z, "south", shape="outer_left")
                elif x == xb and z == za:
                    _stair(g, x, y, z, "south", shape="outer_right")
                elif x == xa and z == zb:
                    _stair(g, x, y, z, "north", shape="outer_right")
                elif x == xb and z == zb:
                    _stair(g, x, y, z, "north", shape="outer_left")
                elif z == za:
                    _stair(g, x, y, z, "south")
                elif z == zb:
                    _stair(g, x, y, z, "north")
                elif x == xa:
                    _stair(g, x, y, z, "east")
                else:
                    _stair(g, x, y, z, "west")
        k += 1
    return y


def _platform(g, W, L, step_x=None):
    """Raised mud-brick platform one block above the marsh, stair skirt round it, steps up at the front."""
    for x in range(-1, W + 1):
        for z in range(-1, L + 1):
            if x in (-1, W) or z in (-1, L):
                if x in (-1, W) and z in (-1, L):
                    g.set(x, 0, z, P["plinth"])
                    continue
                f = "east" if x == -1 else "west" if x == W else "south" if z == -1 else "north"
                _stair(g, x, 0, z, f, block=P["plinth_stairs"])
            else:
                g.set(x, 0, z, P["plinth"])


def _channel(g, x, z0, z1):
    """A water channel with lily pads along one side: the marsh runs right up to the buildings."""
    for z in range(z0, z1 + 1):
        g.set(x, -1, z, P["plinth"])
        g.set(x, 0, z, "minecraft:water", level="0")
        g.set(x - 1, 0, z, P["plinth"]) if g.get(x - 1, 0, z) is None else None
        g.set(x + 1, 0, z, P["plinth"]) if g.get(x + 1, 0, z) is None else None
        if z % 3 == 1:
            g.set(x, 1, z, "minecraft:lily_pad")


def _stone_lantern(g, x, z):
    g.set(x, 0, z, P["plinth"])
    g.set(x, 1, z, P["plinth_wall"], up="true", north="none", south="none", east="none", west="none",
          waterlogged="false")
    g.set(x, 2, z, P["plinth"])
    g.set(x, 3, z, P["lantern"], hanging="false", waterlogged="false")
    g.set(x, 4, z, P["roof_slab"], type="bottom", waterlogged="false")


def _dummy(g, x, z):
    """Training dummy: a post with a hay torso and fence arms."""
    g.set(x, 1, z, P["fence"], **FENCE)
    g.set(x, 2, z, "minecraft:hay_block", axis="y")
    g.set(x, 3, z, "minecraft:carved_pumpkin", facing="north")


def lizard_dojo(p=None, culture=None):
    """The dojo (MineColonies combat academy): the signature building of the lizardman clan.

    13 x 11 hall on a raised platform; mangrove posts every 3 with packed-mud walls and bamboo screens; a deep
    front veranda; two-tier hip roof (a raised clerestory over the training floor); inside, a green mat ring with
    training dummies, weapon racks along the walls and a shrine dais with banners at the back. A stone-lantern
    approach and water channels either side.
    """
    p = p or {}
    W, L, H = p.get("width", 13), p.get("length", 11), 4
    lv = p.get("level", 5)
    g = Grid()
    xc = W // 2
    _platform(g, W, L)
    posts_x = set(range(0, W, 3)) | {W - 1}
    posts_z = set(range(2, L, 3)) | {L - 1}
    zw = 2                                       # the front wall stands back: z 0..1 is the veranda
    for x in range(W):
        for z in range(L):
            inside = 0 < x < W - 1 and zw < z < L - 1
            if z < zw:                           # veranda: plank deck, posts on the front edge
                g.set(x, 0, z, P["planks"])
                if z == 0 and x in posts_x:
                    for y in range(1, H + 1):
                        g.set(x, y, z, P["post"], axis="y")
                elif z == 0 and 0 < x < W - 1 and x not in (xc - 1, xc, xc + 1):
                    g.set(x, 1, z, P["fence"], **dict(FENCE, east="true", west="true"))
                continue
            if inside:
                g.set(x, 0, z, P["floor"])
                for y in range(1, H + 5):
                    g.air(x, y, z)
                continue
            post = (x in (0, W - 1) and z in posts_z | {zw}) or (z in (zw, L - 1) and x in posts_x)
            for y in range(1, H + 1):
                if post:
                    g.set(x, y, z, P["post"], axis="y")
                elif y == 1:
                    g.set(x, y, z, P["plinth"])
                elif y in (2, 3) and (x in (0, W - 1) or z == L - 1):
                    g.set(x, y, z, P["screen"], facing="north" if x in (0, W - 1) else "south", half="top",
                          open="true" if y == 2 else "false", powered="false", waterlogged="false")
                else:
                    g.set(x, y, z, P["wall"])
    # tie beams on top of the walls and veranda posts
    for x in range(W):
        for z in (0, zw, L - 1):
            g.set(x, H + 1, z, P["beam"], axis="x")
    for z in range(0, L):
        for x in (0, W - 1):
            g.set(x, H + 1, z, P["beam"], axis="z")
    # front: wide sliding-door opening (3 doors) on the front wall
    _door(g, xc - 1, zw, hinge="right")
    _door(g, xc, zw)
    g.set(xc + 1, 1, zw, P["wall"]); g.set(xc + 1, 2, zw, P["wall"])
    # lower roof over everything, then the raised clerestory and upper roof
    top_lo = hip_roof(g, 0, W - 1, 0, L - 1, H + 2, overhang=2)
    if lv >= 3:
        cx0, cx1, cz0, cz1 = 3, W - 4, zw + 2, L - 3
        for x in range(cx0, cx1 + 1):            # clear the lower roof inside the clerestory
            for z in range(cz0, cz1 + 1):
                for y in range(H + 3, top_lo + 1):
                    g.cells[(x, y, z)] = ("minecraft:air", {})
        cy = H + 3
        for x in range(cx0, cx1 + 1):
            for z in range(cz0, cz1 + 1):
                if x in (cx0, cx1) or z in (cz0, cz1):
                    corner = x in (cx0, cx1) and z in (cz0, cz1)
                    for y in range(cy, cy + 3):
                        g.set(x, y, z, P["post"] if corner else (P["screen"] if y == cy + 1 else P["wall"]),
                              **({"axis": "y"} if corner else {"facing": "north" if z == cz0 else "south",
                                                                "half": "top", "open": "false", "powered": "false",
                                                                "waterlogged": "false"} if y == cy + 1 else {}))
                else:
                    for y in range(cy, cy + 3):
                        g.air(x, y, z)
        hip_roof(g, cx0, cx1, cz0, cz1, cy + 3, overhang=2)
    # inside: mat ring, dummies, weapon racks, shrine dais at the back
    for x in range(2, W - 2):
        for z in range(zw + 2, L - 3):
            if x in (2, W - 3) or z in (zw + 2, L - 4):
                g.set(x, 1, z, P["mat"])
    if lv >= 2:
        for x in (4, W - 5):
            _dummy(g, x, zw + 4)
    if lv >= 4:
        for z in range(zw + 2, L - 2, 2):        # weapon racks: fence posts with trapdoor shelves
            for x, f in ((1, "east"), (W - 2, "west")):
                g.set(x, 1, z, "minecraft:barrel", facing="up", open="false")
                g.set(x, 2, z, "minecraft:bamboo_fence", **FENCE)
    for x in range(xc - 2, xc + 3):              # shrine dais
        g.set(x, 1, L - 2, P["plinth_stairs"], facing="south", half="top", shape="straight", waterlogged="false") \
            if x in (xc - 2, xc + 2) else g.set(x, 1, L - 2, P["plinth"])
    g.set(xc, 2, L - 2, "minecraft:decorated_pot", facing="north", cracked="false", waterlogged="false")
    for x in (xc - 1, xc + 1):
        g.set(x, 2, L - 2, P["lantern"], hanging="false", waterlogged="false")
    for x in (xc - 2, xc + 2):
        g.set(x, 3, L - 2, P["banner"], facing="north")
        g.block_entities[(x, 3, L - 2)] = {"id": "minecraft:banner", "patterns": [
            {"pattern": "minecraft:triangles_bottom", "color": "black"}, {"pattern": "minecraft:circle", "color": "yellow"}]}
    for z in (zw + 3, L - 4):
        g.set(xc, H + 2, z, "minecraft:chain", axis="y", waterlogged="false") if lv < 3 else None
        g.set(xc, H, z, P["lantern"], hanging="true", waterlogged="false") if lv < 3 else None
    if lv >= 3:
        for z in (zw + 3, L - 4):
            for y in range(H + 1, H + 6):
                g.set(xc, y, z, "minecraft:chain", axis="y", waterlogged="false")
            g.set(xc, H, z, P["lantern"], hanging="true", waterlogged="false")
    # approach: stone lanterns flanking the steps, water channels either side
    for x in (xc - 1, xc, xc + 1):
        _stair(g, x, 0, -1, "south", block=P["plinth_stairs"])
        g.set(x, 0, -2, "minecraft:packed_mud")
        g.set(x, 0, -3, "minecraft:packed_mud")
    if lv >= 2:
        _stone_lantern(g, xc - 3, -3)
        _stone_lantern(g, xc + 3, -3)
    if lv >= 5:
        _channel(g, -3, 0, L - 1)
        _channel(g, W + 2, 0, L - 1)
    return g

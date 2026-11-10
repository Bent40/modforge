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
    """The dwarf town hall. p: width (odd), length, wall_height, tower (bool), wheel (bool), chimneys (0-2),
    level (1-5, default 5): 1 bare hall with feast tables; 2 forge corner, cog train over the door, one chimney;
    3 water wheel and line shafts, second chimney; 4 tower; 5 clock face, lightning rod, brass floor inlay."""
    W, L, H = p["width"], p["length"], p["wall_height"]
    lv = p.get("level", 5)
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
                inlay = lv >= 5 and (x == xc or z == L // 2) and x not in (1, W - 2)
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
    if lv >= 2:
        g.set(xc, gy, -1, P["big_cog"], axis="z")
        for dx in (-2, 2):
            g.set(xc + dx, gy + 1, -1, P["cog"], axis="z")
    if p.get("tower") and lv >= 4:
        _tower(g, xc, top, H, clock=lv >= 5)
    if p.get("wheel") and lv >= 3:
        _water_wheel(g, -1, L // 2 + 2, H)
        _line_shafts(g, W, L, H, L // 2 + 2)
    _hall_furnish(g, W, L, H, lv)
    for i in range(min(p.get("chimneys", 0), max(0, lv - 1))):
        _chimney(g, W - 3 if i == 0 else 2, L, top)
    return g


def _tower(g, xc, roof_top, H, clock=True):
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
    if clock:  # gear clock face high on the front
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
    if clock:
        g.set(xc, th + 5, (z0 + z1) // 2, "minecraft:lightning_rod", facing="up", powered="false", waterlogged="false")


def _water_wheel(g, x, zc, H):
    """Large Create water wheel (5x5) in a stone mill race on the west wall; its shaft runs through the wall
    into a gearbox that feeds the hall's line shafts."""
    wx = x - 2                                   # wheel plane, two blocks out from the skirt
    for z in range(zc - 3, zc + 4):              # mill race: two deep, walled, under the wheel
        for xx in (wx - 1, wx + 1):
            for y in (-2, -1, 0):
                g.set(xx, y, z, P["plinth"])
        g.set(wx, -2, z, P["plinth"])
        g.set(wx, -1, z, "minecraft:water", level="0")
        g.set(wx, 0, z, "minecraft:water", level="0")
    g.set(wx, 2, zc, "create:large_water_wheel", axis="x", extension="false", waterlogged="false")
    # Create wheels only turn on FLOWING water against the blades: a stone cistern on a chute behind the wheel
    # drops a waterfall down the rim (z = zc+2, y 1..4) into the race, so the wheel spins as soon as it is pasted.
    zf = zc + 2
    for y in range(1, 6):                        # chute cheeks either side of the falling column
        for xx in (wx - 1, wx + 1):
            g.set(xx, y, zf, P["plinth"])
        g.set(wx, y, zf + 1, P["plinth"])        # chute back wall
    for y in range(1, 5):
        g.air(wx, y, zf)                         # the fall itself (the source above fills it)
    g.set(wx, 5, zf, "minecraft:water", level="0")
    g.set(wx, 5, zf - 1, P["plinth"])            # cistern front lip, above the wheel's top rim
    g.set(wx, 6, zf, P["plinth"])                # cistern lid
    for xx in range(wx + 1, 1):                  # through the skirt and the wall
        g.set(xx, 2, zc, P["shaft"], axis="x")
    g.set(1, 2, zc, "create:gearbox", axis="z")


def _line_shafts(g, W, L, H, zc):
    """Inside: from the gearbox a vertical shaft climbs to a line shaft running the length of the hall under the
    roof, cogwheels on it every four blocks, and hanging lanterns down the nave."""
    for y in range(3, H):
        g.set(1, y, zc, P["shaft"], axis="y")
    g.set(1, H, zc, P["cog"], axis="y")
    for z in range(1, L - 1):
        if z == zc:
            continue
        g.set(1, H, z, P["cog"] if z % 4 == 2 else P["shaft"], axis="z")


def _hall_furnish(g, W, L, H, lv):
    """Hanging lanterns down the nave and feast tables at every level; the forge corner from level 2."""
    xc = W // 2
    for z in range(3, L - 2, 4):
        g.set(xc, H, z, "minecraft:chain", axis="y", waterlogged="false")
        g.set(xc, H - 1, z, P["lantern"], hanging="true", waterlogged="false")
    # feast tables with benches either side of the nave
    for tx in (xc - 3, xc + 3):
        for z in range(5, L - 5):
            g.set(tx, 1, z, "minecraft:dark_oak_slab", type="top", waterlogged="false")
            for bx, f in ((tx - 1, "west"), (tx + 1, "east")):
                if 1 < bx < W - 2 and z % 3 != 0:
                    g.set(bx, 1, z, "minecraft:dark_oak_stairs", facing=f, half="bottom", shape="straight",
                          waterlogged="false")
    if lv < 2:
        return
    # forge corner at the back: the hall is also the clan's first workshop
    g.set(W - 2, 1, L - 2, "minecraft:blast_furnace", facing="west", lit="false")
    g.set(W - 2, 1, L - 3, "minecraft:anvil", facing="north")
    g.set(W - 3, 1, L - 2, "minecraft:smithing_table")


def _chimney(g, x, L, roof_top):
    z = L
    for y in range(0, roof_top + 3):
        g.set(x, y, z, P["chimney"])
        g.set(x + 1, y, z, P["chimney"])
    g.set(x, roof_top + 3, z, "minecraft:campfire", facing="south", lit="true", signal_fire="false", waterlogged="false")
    g.set(x + 1, roof_top + 3, z, "minecraft:campfire", facing="south", lit="true", signal_fire="false", waterlogged="false")


def _bed(g, x, y, z, facing="north", colour="gray"):
    """Bed whose foot is at (x, y, z); the head is one block toward `facing`."""
    dx, dz = {"north": (0, -1), "south": (0, 1), "east": (1, 0), "west": (-1, 0)}[facing]
    b = f"minecraft:{colour}_bed"
    g.set(x, y, z, b, facing=facing, part="foot", occupied="false")
    g.set(x + dx, y, z + dz, b, facing=facing, part="head", occupied="false")


def dwarf_house(p, culture=None):
    """Dwarf residence: a dug-in deepslate ground storey, a jettied andesite upper storey on casing posts with
    corbels, steep tile roof with a copper ridge, a brick chimney, and a small copper water tank on a stand.
    p: width (odd, >= 9), length (>= 11), level (1-5, default 5) = beds. Level 1 is the ground storey alone under
    its roof with one bed; 2 adds the jettied upper storey and stair; 3 the chimney; 4 the water tank; 5 the cog sign
    and porch lanterns, with a fifth bed back downstairs."""
    W, L = p.get("width", 9), p.get("length", 11)
    lv = p.get("level", 5)
    g = Grid()
    xc = W // 2
    LO, UP0, UP1 = 4, 6, 9                       # lower walls y1..4, upper floor y5, upper walls y6..9
    zf = -1                                      # the jettied upper front sticks out one block
    # ground storey: heavy deepslate, small windows
    for x in range(W):
        for z in range(L):
            edge = x in (0, W - 1) or z in (0, L - 1)
            g.set(x, 0, z, P["plinth"] if edge else P["floor"])
            if not edge:
                for y in range(1, UP1 + 1):
                    g.air(x, y, z)
                continue
            corner = x in (0, W - 1) and z in (0, L - 1)
            for y in range(1, LO + 1):
                if corner:
                    g.set(x, y, z, P["pillar"])
                elif x in (0, W - 1) and y in (2, 3) and z in (3, L - 4):
                    g.set(x, y, z, P["window"])
                else:
                    g.set(x, y, z, P["plinth_alt"] if (x * 3 + y + z) % 6 == 0 else P["plinth"])
    # plinth skirt
    for x in range(-1, W + 1):
        for z in range(-1, L + 1):
            if (x in (-1, W) or z in (-1, L)) and not (x in (-1, W) and z in (-1, L)):
                f = "east" if x == -1 else "west" if x == W else "south" if z == -1 else "north"
                if not (z == -1 and x in (xc, xc - 1, xc + 1)):
                    _stair(g, x, 0, z, f, block=P["plinth_stairs"])
    if lv == 1:
        for x in range(W):
            for z in range(L):
                if x in (0, W - 1) or z in (0, L - 1):
                    g.set(x, LO + 1, z, P["band"])
        top = _gable_roof(g, 0, W - 1, 0, L - 1, LO + 2)
        g.set(xc, LO + 3, 0, P["window"])
        g.set(xc, LO + 3, L - 1, P["window"])
        _door(g, xc, 0)
        _stair(g, xc, 0, -1, "south", block=P["plinth_stairs"])
        g.set(xc - 2, 3, -1, P["lantern"], hanging="false", waterlogged="false")
        _house_kitchen(g, W, L, xc)
        _bed(g, 2, 1, 2, facing="west")
        g.set(1, LO, L // 2, P["lantern"], hanging="true", waterlogged="false")
        return g
    # upper floor (dark oak boards) incl. the jetty, corbels under the jetty
    for x in range(W):
        for z in range(zf, L):
            g.set(x, LO + 1, z, "minecraft:dark_oak_planks" if 0 < x < W - 1 and 0 < z < L - 1 else P["band"])
    for x in range(W):
        _stair(g, x, LO, zf, "south", half="top", block=P["plinth_stairs"])
    # upper storey walls on the jettied box (z = zf .. L-1)
    for x in range(W):
        for z in range(zf, L):
            edge = x in (0, W - 1) or z in (zf, L - 1)
            if not edge:
                continue
            post = (x in (0, W - 1) and z in (zf, L - 1, (zf + L - 1) // 2)) or (z in (zf, L - 1) and x == xc)
            for y in range(UP0, UP1 + 1):
                if post:
                    g.set(x, y, z, P["pillar"])
                elif y in (7, 8) and ((z == zf and x in (2, W - 3)) or (x in (0, W - 1) and z in (2, L - 3))):
                    g.set(x, y, z, P["window"])
                else:
                    g.set(x, y, z, _wall_block(x, y, z))
    for x in range(1, W - 1):
        g.air(x, UP0, 0)                         # the old front wall line is now inside the jetty
    top = _gable_roof(g, 0, W - 1, zf, L - 1, UP1 + 1)
    g.set(xc, UP1 + 2, zf, P["window"])          # gable window
    g.set(xc, UP1 + 2, L - 1, P["window"])
    # door, steps, lantern, a cog sign on the jetty
    _door(g, xc, 0)
    _stair(g, xc, 0, -1, "south", block=P["plinth_stairs"])
    g.set(xc - 2, 3, -1, P["lantern"], hanging="false", waterlogged="false")
    if lv >= 5:
        g.set(xc, LO + 1, zf - 1, P["cog"], axis="z")
        g.set(xc + 2, 3, -1, P["lantern"], hanging="false", waterlogged="false")
        _bed(g, 2, 1, 2, facing="west")
    _house_kitchen(g, W, L, xc)
    sx = W - 2
    for k in range(4):                           # straight stair: y1..4 rising to the upper floor at y5
        g.set(sx, 1 + k, 2 + k, "minecraft:dark_oak_stairs", facing="south", half="bottom", shape="straight",
              waterlogged="false")
    for z in range(2, 6):
        g.cells[(sx, LO + 1, z)] = ("minecraft:air", {})   # stairwell opening
    for z in (3, 4):
        g.set(sx - 1, LO + 2, z, "minecraft:dark_oak_fence", north="false", south="false", east="false",
              west="false", waterlogged="false")
    g.set(1, LO, L // 2, P["lantern"], hanging="true", waterlogged="false")
    # upstairs: beds against the west wall, chests at their feet, a lantern
    for i in range(min(lv, 4)):
        bz = L - 2 - i * 2
        _bed(g, 2, UP0, bz, facing="west")
        g.set(3, UP0, bz, "minecraft:chest", facing="east", type="single", waterlogged="false")
    g.set(xc, UP1, L // 2, P["lantern"], hanging="true", waterlogged="false")
    if lv >= 3:  # chimney on the back wall
        for y in range(0, top + 2):
            g.set(xc, y, L, P["chimney"])
            g.set(xc + 1, y, L, P["chimney"])
        g.set(xc, top + 2, L, "minecraft:campfire", facing="south", lit="true", signal_fire="false",
              waterlogged="false")
    if lv >= 4:  # copper water tank on a casing stand by the west wall, piped into the kitchen
        tx, tz = -2, L - 3
        for y in range(0, 3):
            g.set(tx, y, tz, P["pillar"])
        g.set(tx, 3, tz, "create:fluid_tank", bottom="true", top="false", shape="window")
        g.set(tx, 4, tz, "create:fluid_tank", bottom="false", top="true", shape="window")
        g.set(-1, 3, tz, "create:fluid_pipe", east="true", west="true", north="false", south="false", up="false",
              down="false", waterlogged="false")
    return g


def _house_kitchen(g, W, L, xc):
    """Ground floor of the dwarf house: kitchen along the back wall, a table with two stools in the middle."""
    g.set(1, 1, L - 2, "minecraft:smoker", facing="north", lit="false")
    g.set(2, 1, L - 2, "minecraft:barrel", facing="up", open="false")
    g.set(3, 1, L - 2, "minecraft:crafting_table")
    g.set(1, 1, L - 3, "minecraft:barrel", facing="up", open="false")
    g.set(xc - 1, 1, L // 2, "minecraft:dark_oak_slab", type="top", waterlogged="false")
    g.set(xc - 1, 1, L // 2 - 1, "minecraft:dark_oak_stairs", facing="south", half="bottom", shape="straight",
          waterlogged="false")
    g.set(xc - 1, 1, L // 2 + 1, "minecraft:dark_oak_stairs", facing="north", half="bottom", shape="straight",
          waterlogged="false")


def dwarf_smithy(p, culture=None):
    """Dwarf blacksmith: a forge hall with a wide open front under a stone lintel, a 3x3 brick forge stack
    through the roof with the fire visible inside, a Create press over a depot turned by a hand crank, anvil,
    grindstone, quench cauldron, and an ore-and-coal lean-to along the west side. p: width (odd), length, level (1-5):
    1 forge hall, stack, one blast furnace, anvil; 2 second furnace, grindstone, quench; 3 ore lean-to; 4 Create press
    with hand crank; 5 cog sign over the door and the brass floor inlay."""
    W, L, H = p.get("width", 11), p.get("length", 9), 6
    lv = p.get("level", 5)
    g = Grid()
    xc = W // 2
    for x in range(W):
        for z in range(L):
            edge = x in (0, W - 1) or z in (0, L - 1)
            if not edge:
                g.set(x, 0, z, P["floor_inlay"] if lv >= 5 and (x, z) == (xc, L // 2) else P["floor"])
                for y in range(1, H + 2):
                    g.air(x, y, z)
                continue
            g.set(x, 0, z, P["plinth"])
            pillar = (x in (0, W - 1) and z in (0, L - 1, L // 2)) or (z in (0, L - 1) and x in (xc - 3, xc + 3))
            for y in range(1, H + 1):
                if pillar:
                    g.set(x, y, z, P["pillar"])
                elif y <= 2:
                    g.set(x, y, z, P["plinth"])
                elif x in (0, W - 1) and y in (3, 4) and z in (2, L - 3):
                    g.set(x, y, z, P["window"])
                else:
                    g.set(x, y, z, _wall_block(x, y, z))
            g.set(x, H + 1, z, P["band"])
    for x in range(-1, W + 1):
        for z in range(-1, L + 1):
            if (x in (-1, W) or z in (-1, L)) and not (x in (-1, W) and z in (-1, L)):
                f = "east" if x == -1 else "west" if x == W else "south" if z == -1 else "north"
                if not (z == -1 and xc - 2 <= x <= xc + 2):
                    _stair(g, x, 0, z, f, block=P["plinth_stairs"])
    # wide open front: 5 wide, 4 high, stone lintel with upside-down stair shoulders, big cog sign above
    for x in range(xc - 2, xc + 3):
        for y in range(1, 5):
            g.cells[(x, y, 0)] = ("minecraft:air", {})
        g.set(x, 5, 0, P["plinth"])
        g.set(x, 0, -1, P["plinth"])
    _stair(g, xc - 2, 4, 0, "east", half="top", block=P["plinth_stairs"])
    _stair(g, xc + 2, 4, 0, "west", half="top", block=P["plinth_stairs"])
    if lv >= 5:
        g.set(xc, 6, -1, P["big_cog"], axis="z")
    top = _gable_roof(g, 0, W - 1, 0, L - 1, H + 2)
    g.set(xc, H + 4, L - 1, P["window"])
    # forge stack: 3x3 bricks on the back wall, hollow flue, fire seen through an opening
    fx = 2
    for x in range(fx - 1, fx + 2):
        for z in range(L - 1, L + 2):
            for y in range(0, top + 3):
                if (x, z) == (fx, L) and 1 <= y <= top + 2:
                    g.cells[(x, y, z)] = ("minecraft:air", {})
                    continue
                g.set(x, y, z, P["chimney"])
    g.set(fx, 1, L, "minecraft:campfire", facing="north", lit="true", signal_fire="false", waterlogged="false")
    for y in (1, 2):
        g.cells[(fx, y, L - 1)] = ("minecraft:air", {})
    g.set(fx, 3, L - 1, P["plinth_stairs"], facing="north", half="top", shape="straight", waterlogged="false")
    for z in (L - 1,):                           # iron bars guard the fire mouth
        g.set(fx, 1, z - 1, "minecraft:iron_bars", north="false", south="false", east="true", west="true",
              waterlogged="false")
    for x in range(fx - 1, fx + 2):
        g.set(x, top + 3, L - 1, P["plinth_stairs"], facing="south", half="bottom", shape="straight", waterlogged="false")
    g.set(fx - 1, 1, L - 2, "minecraft:blast_furnace", facing="east", lit="false")
    if lv >= 2:
        g.set(fx + 1, 1, L - 2, "minecraft:blast_furnace", facing="west", lit="false")
    # work floor
    g.set(xc, 1, L // 2 + 1, "minecraft:anvil", facing="east")
    g.set(xc + 1, 1, L - 2, "minecraft:smithing_table")
    if lv >= 2:
        g.set(xc - 1, 1, L // 2 + 1, "minecraft:water_cauldron", level="3")
        g.set(1, 1, 2, "minecraft:grindstone", face="floor", facing="east")
    g.set(1, 1, 1, "minecraft:barrel", facing="up", open="false")
    if lv >= 4:
        # Create press over a depot on the east side, turned by a hand crank through the wall
        px, pz = W - 3, L // 2
        g.set(px, 1, pz, "create:depot")
        g.set(px, 3, pz, "create:mechanical_press", facing="west")
        g.set(px + 1, 3, pz, "create:shaft", axis="x")
        g.set(W, 3, pz, "create:hand_crank", facing="east", powered="false", waterlogged="false")
        g.cells[(W - 1, 3, pz)] = ("create:shaft", {"axis": "x"})
    for z in (2, L - 3):
        g.set(xc, H, z, "minecraft:chain", axis="y", waterlogged="false")
        g.set(xc, H - 1, z, P["lantern"], hanging="true", waterlogged="false")
    if lv < 3:
        return g
    # lean-to on the west: casing posts, tile slab roof, coal and ore stock
    for z in range(1, L - 1):
        for x in (-3, -2):
            g.set(x, 0, z, P["plinth"])
        g.set(-3, 4, z, P["roof_slab"], type="bottom", waterlogged="false")
        g.set(-2, 4, z, P["roof_slab"], type="top", waterlogged="false")
        g.set(-1, 4, z, P["roof"], facing="east", half="bottom", shape="straight", waterlogged="false") \
            if g.get(-1, 4, z) is None else None
    for z in (1, L - 2):
        for y in range(1, 4):
            g.set(-3, y, z, P["pillar"])
    stock = ["minecraft:coal_block", "minecraft:raw_iron_block", "minecraft:barrel", "minecraft:coal_block",
             "minecraft:raw_copper_block"]
    for i, z in enumerate(range(2, L - 2)):
        b = stock[i % len(stock)]
        g.set(-2, 1, z, b, **({"facing": "up", "open": "false"} if b.endswith("barrel") else {}))
        if i % 2 == 0:
            g.set(-2, 2, z, "minecraft:coal_block")
    return g

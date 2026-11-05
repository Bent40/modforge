"""Block grid + palette roles + structure .nbt export.

Coordinates: x right (+X), y up, z toward the back (+Z). The front of every building is z = 0 (north, -Z).
A cell holds (block_id, props) or AIR. Cells never written stay structure_void (terrain is kept there).
"""
import random

from . import nbt

AIR = ("minecraft:air", {})
DATA_VERSION = 3955  # Minecraft 1.21.1


class Palette:
    def __init__(self, roles, seed):
        self.roles = roles
        self.rng = random.Random(seed)

    def main(self, role):
        return next(iter(self.roles[role]))

    def pick(self, role):
        opts = self.roles[role]
        return self.rng.choices(list(opts), weights=list(opts.values()))[0]


class Grid:
    def __init__(self):
        self.cells = {}
        self.block_entities = {}

    def set(self, x, y, z, block, **props):
        self.cells[(x, y, z)] = (block, {k: str(v).lower() for k, v in props.items()})

    def air(self, x, y, z):
        if (x, y, z) not in self.cells:
            self.cells[(x, y, z)] = AIR

    def get(self, x, y, z):
        return self.cells.get((x, y, z))

    def solid(self, x, y, z):
        c = self.cells.get((x, y, z))
        return c is not None and c[0] != "minecraft:air" and is_full(c[0])

    def bounds(self):
        xs, ys, zs = zip(*self.cells)
        return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))

    def connect_fences(self):
        dirs = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0)}
        for (x, y, z), (b, p) in list(self.cells.items()):
            if b.endswith("_fence"):
                for d, (dx, dy, dz) in dirs.items():
                    n = self.cells.get((x + dx, y, z + dz))
                    p[d] = "true" if n and (n[0].endswith("_fence") or (is_full(n[0]) and n[0] != "minecraft:air")) else "false"
                p.setdefault("waterlogged", "false")

    def normalise(self):
        """Shift so the min corner is (0,0,0)."""
        (mx, my, mz), _ = self.bounds()
        self.cells = {(x - mx, y - my, z - mz): v for (x, y, z), v in self.cells.items()}
        self.block_entities = {(x - mx, y - my, z - mz): v for (x, y, z), v in self.block_entities.items()}

    def to_nbt(self, path):
        self.normalise()
        (_, _, _), (Mx, My, Mz) = self.bounds()
        palette, index, blocks = [], {}, []
        for pos in sorted(self.cells, key=lambda p: (p[1], p[2], p[0])):
            b, props = self.cells[pos]
            key = (b, tuple(sorted(props.items())))
            if key not in index:
                index[key] = len(palette)
                entry = {"Name": b}
                if props:
                    entry["Properties"] = dict(sorted(props.items()))
                palette.append(entry)
            blk = {"pos": [pos[0], pos[1], pos[2]], "state": index[key]}
            if pos in self.block_entities:
                blk["nbt"] = self.block_entities[pos]
            blocks.append(blk)
        root = {
            "DataVersion": DATA_VERSION,
            "size": [Mx + 1, My + 1, Mz + 1],
            "palette": palette,
            "blocks": blocks,
            "entities": [],
        }
        nbt.write(path, root)
        return root


PARTIAL_SUFFIXES = ("_slab", "_stairs", "_fence", "_door", "_trapdoor", "_torch", "_carpet", "_banner",
                    "_skull", "campfire", "ladder", "air")


def is_full(block):
    return not block.endswith(PARTIAL_SUFFIXES)

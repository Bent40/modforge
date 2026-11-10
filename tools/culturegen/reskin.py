"""Reskin a whole MineColonies style pack into a culture's materials (palette remap; shapes and huts untouched).

usage: python -m tools.culturegen.reskin cultures/goblin.yaml SRC_PACK_DIR OUT_PACK_DIR [--render N]

Every .blueprint under SRC is copied with its palette remapped by the culture's `reskin` rules, so a colony gets
every hut at every level in the race's materials at once. Hand-designed buildings can then replace files one by one.
Blocks the rules don't cover (modded blocks, Domum Ornamentum, ...) are kept and counted in reskin_report.json.
"""
import json
import os
import re
import shutil
import sys

import yaml

from . import blueprint as bp

WOODS = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "bamboo", "crimson", "warped")
SHAPES = ("_stairs", "_slab", "_wall", "_fence_gate", "_fence", "_door", "_trapdoor", "_button", "_pressure_plate",
          "_wall_hanging_sign", "_hanging_sign", "_wall_sign", "_sign")
COLORS = ("white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan",
          "purple", "blue", "brown", "green", "red", "black")
# shapes that exist per target family (vanilla 1.21.1)
FAMILY_SHAPES = {
    "mud_brick": {"_stairs", "_slab", "_wall"},
    "cobblestone": {"_stairs", "_slab", "_wall"},
    "mossy_cobblestone": {"_stairs", "_slab", "_wall"},
    "stone_brick": {"_stairs", "_slab", "_wall"},
    "deepslate_brick": {"_stairs", "_slab", "_wall"},
    "deepslate_tile": {"_stairs", "_slab", "_wall"},
    "cobbled_deepslate": {"_stairs", "_slab", "_wall"},
    "polished_andesite": {"_stairs", "_slab"},
}


def _full(prefix):
    return prefix + "s" if prefix.endswith(("brick", "tile")) else prefix


# targets that carry no blockstate properties (drop the source's, e.g. glazed terracotta `facing`)
NO_PROPS = {"minecraft:" + n for n in ("mud_bricks", "packed_mud", "cobblestone", "mossy_cobblestone", "spruce_planks",
                                        "coarse_dirt", "dirt", "air", "stone_bricks", "shroomlight", "hay_block",
                                        "deepslate_bricks", "deepslate_tiles", "cobbled_deepslate", "polished_andesite",
                                        "dark_oak_planks", "gray_terracotta")}


class Rules:
    def __init__(self, spec):
        r = spec["reskin"]
        self.wood = r["wood"]                       # target species, e.g. spruce
        self.stone = r.get("stone", {})             # source prefix -> target family prefix
        self.exact = r.get("exact", {})             # source id -> target id ("" = leave, "minecraft:air" = remove)
        self.dye = r.get("dye", {})                 # wool/carpet/banner/bed colour -> target colour
        self.patterns = [(re.compile(k), v) for k, v in r.get("patterns", {}).items()]
        self.texture_exact = r.get("texture_exact", {})      # Domum textureData value -> value
        self.texture_by_block = r.get("texture_by_block", {})  # Domum block id -> forced texture for every slot

    def map_texture(self, block, value):
        if block in self.texture_by_block:
            return self.texture_by_block[block]
        if value in self.texture_exact:
            return self.texture_exact[value]
        new = self.map(value)
        if new == "minecraft:air":  # a texture can't be air: use whatever replaces plain glass
            return self.texture_exact.get("minecraft:glass", value)
        return new

    def map(self, name):
        if not name.startswith("minecraft:"):
            return name
        n = name[len("minecraft:"):]
        if name in self.exact:
            return self.exact[name] or name
        for rx, tgt in self.patterns:
            if rx.fullmatch(n):
                return tgt
        # wood species swap
        for w in sorted(WOODS, key=len, reverse=True):
            for form in (f"stripped_{w}_", f"{w}_"):
                if n.startswith(form):
                    rest = n[len(form):]
                    if rest in ("log", "wood", "planks", "leaves") or ("_" + rest) in SHAPES or rest in (s[1:] for s in SHAPES):
                        if w in ("crimson", "warped", "bamboo") and rest in ("log", "wood"):
                            return name
                        return "minecraft:" + form.replace(w, self.wood, 1) + rest
        # stone families
        shape = next((s for s in SHAPES if n.endswith(s)), "")
        base = n[: -len(shape)] if shape else n
        prefix = base[:-1] if shape == "" and base.endswith(("bricks", "tiles")) else base
        if prefix in self.stone:
            tgt = self.stone[prefix]
            if not shape:
                return "minecraft:" + _full(tgt)
            if shape in FAMILY_SHAPES.get(tgt, set()):
                return "minecraft:" + tgt + shape
            return name
        # dyed blocks
        for c in sorted(COLORS, key=len, reverse=True):
            if n.startswith(c + "_"):
                kind = n[len(c) + 1:]
                if kind in ("wool", "carpet", "banner", "wall_banner", "bed") and c in self.dye:
                    return f"minecraft:{self.dye[c]}_{kind}"
        return name


def _texture_maps(obj):
    """Every Domum `textureData` map inside a tile entity, wherever it is nested."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "textureData" and isinstance(v, dict):
                yield v
            else:
                yield from _texture_maps(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _texture_maps(v)


def reskin_pack(spec, src, out, render_n=0):
    rules = Rules(spec)
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(src, out, ignore=shutil.ignore_patterns("*.blueprint"))
    report = {"files": 0, "changed_states": 0, "kept": {}, "mapped": {}, "textures": {}, "textures_kept": {}}
    rendered = []
    for dp, _, files in os.walk(src):
        for f in sorted(files):
            if not f.endswith(".blueprint"):
                continue
            s = os.path.join(dp, f)
            o = os.path.join(out, os.path.relpath(s, src))
            os.makedirs(os.path.dirname(o), exist_ok=True)
            root = bp.read(s)
            names = [e["Name"] for e in root["palette"]]
            for te in root.get("tile_entities", []):
                for td in _texture_maps(te):
                    blk = names[root["_flat"][bp.idx(root, te["x"], te["y"], te["z"])]] if "x" in te else ""
                    for k, v in list(td.items()):
                        nv = rules.map_texture(blk, v)
                        if nv != v:
                            td[k] = nv
                            report["textures"][f"{v} -> {nv}"] = report["textures"].get(f"{v} -> {nv}", 0) + 1
                        else:
                            report["textures_kept"][v] = report["textures_kept"].get(v, 0) + 1
            for e in root["palette"]:
                old = e["Name"]
                new = rules.map(old)
                if new != old:
                    report["mapped"][f"{old} -> {new}"] = report["mapped"].get(f"{old} -> {new}", 0) + 1
                    report["changed_states"] += 1
                    e["Name"] = new
                    if new in NO_PROPS:
                        e.pop("Properties", None)
                elif not old.startswith(("minecolonies:", "structurize:")) and old != "minecraft:air":
                    report["kept"][old] = report["kept"].get(old, 0) + 1
            bp.write(o, root)
            report["files"] += 1
            if render_n and len(rendered) < render_n and re.fullmatch(r"(townhall|residence|builder)1\.blueprint", f):
                from .render import render
                rp = os.path.join(out, "_preview_" + f.replace(".blueprint", ".png"))
                render(bp.to_grid(root), rp, scale=2)
                rendered.append(rp)
    pj = os.path.join(out, "pack.json")
    if os.path.exists(pj):
        meta = json.load(open(pj))
    else:
        meta = {}
    r = spec["reskin"]
    meta.update({"name": r["pack_name"], "desc": r.get("pack_desc", ""), "authors": r.get("authors", ["culturegen"])})
    json.dump(meta, open(pj, "w"), indent=2)
    for k in ("kept", "textures", "textures_kept"):
        report[k] = dict(sorted(report[k].items(), key=lambda kv: -kv[1]))
    json.dump(report, open(os.path.join(out, "_reskin_report.json"), "w"), indent=1)
    return report, rendered


def main(argv):
    doc = yaml.safe_load(open(argv[0]))
    n = int(argv[argv.index("--render") + 1]) if "--render" in argv else 0
    report, rendered = reskin_pack(doc["spec"], argv[1], argv[2], n)
    print(report["files"], "blueprints;", report["changed_states"], "palette entries remapped;",
          len(report["kept"]), "block ids kept as they were;", sum(report["textures"].values()),
          "Domum texture slots remapped,", sum(report["textures_kept"].values()), "kept")
    for k, v in list(report["textures_kept"].items())[:15]:
        print("  texture kept", v, k)
    for k, v in list(report["kept"].items())[:25]:
        print("  kept", v, k)
    for p in rendered:
        print("preview", p)


if __name__ == "__main__":
    main(sys.argv[1:])

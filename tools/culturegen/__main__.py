"""culturegen: culture spec (YAML) -> vanilla structure .nbt pieces + jigsaw world-gen data + preview renders.

usage: python -m tools.culturegen cultures/goblin.yaml OUT_DIR [--no-render]

OUT_DIR/data/<modid>/... is a ready datapack tree (structure/, worldgen/, tags/) to copy into a mod's
staging/data or a world's datapacks folder.
"""
import json
import os
import sys
import zlib

import yaml

from . import nbt
from .forms import FORMS
from .grid import Palette
from .worldgen import check_jigsaws, write_worldgen


def main(argv):
    spec_path, out = argv[0], argv[1]
    render_on = "--no-render" not in argv
    doc = yaml.safe_load(open(spec_path))
    culture = doc["spec"]
    cid, ns = doc["content_id"], doc["modid"]
    culture["_ns"], culture["_race"] = ns, cid
    sdir = os.path.join(out, "data", ns, "structure", cid)
    os.makedirs(sdir, exist_ok=True)
    os.makedirs(os.path.join(out, "previews"), exist_ok=True)
    manifest, roots = [], {}
    for b in culture["buildings"]:
        pal = Palette(culture["palette"], seed=zlib.crc32(b["id"].encode()))
        grid, meta = FORMS[b["form"]](b["params"], pal, culture)
        grid.connect_fences()
        inh = culture.get("inhabitants", {})
        if b["id"] in inh.get("per_piece", {}):
            import random
            grid.add_inhabitants(inh["entity"], inh["per_piece"][b["id"]], random.Random(zlib.crc32(b["id"].encode())))
        p = os.path.join(sdir, b["id"] + ".nbt")
        root = grid.to_nbt(p)
        roots[b["id"]] = root
        back = nbt.read(p)
        assert back["size"] == root["size"] and len(back["blocks"]) == len(root["blocks"])
        counts = {}
        for blk in root["blocks"]:
            name = root["palette"][blk["state"]]["Name"]
            counts[name] = counts.get(name, 0) + 1
        entry = {"id": b["id"], "nbt": os.path.relpath(p, out), "size": root["size"],
                 "states": len(root["palette"]), "blocks": counts}
        if render_on:
            from .render import render
            views = [("front", None), ("back", None)] + ([("cutaway", meta["cut_y"])] if meta["cut_y"] else [])
            for view, cut in views:
                rp = os.path.join(out, "previews", f"{b['id']}_{view}.png")
                render(grid, rp, scale=4, view="back" if view == "back" else "front", cut_y=cut)
            entry["previews"] = [f"previews/{b['id']}_{v}.png" for v, _ in views]
        manifest.append(entry)
        print(b["id"], root["size"], sum(counts.values()), "blocks")
    problems = check_jigsaws(roots, culture, ns, cid)
    for pr in problems:
        print("JIGSAW:", pr)
    if "village" in culture:
        for f in write_worldgen(out, culture, ns, cid):
            print("wrote", os.path.relpath(f, out))
    if "village" in culture and render_on:
        from .assemble import assemble
        from .render import render
        pools = {f"{ns}:{cid}/{k}": v for k, v in culture["village"]["pools"].items()}
        pieces = {}
        for b in culture["buildings"]:
            pal = Palette(culture["palette"], seed=zlib.crc32(b["id"].encode()))
            g, _ = FORMS[b["form"]](b["params"], pal, culture)
            g.connect_fences()
            g.normalise()
            pieces[b["id"]] = g
        for seed in (1, 2):
            world, placed = assemble(pieces, pools, f"{ns}:{cid}/center", culture["village"]["size"], seed=seed)
            world.connect_fences()
            render(world, os.path.join(out, f"{cid}_village_seed{seed}.png"), scale=2)
            print("village seed", seed, ":", len(placed), "pieces", {p: placed.count(p) for p in set(placed)})
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    if render_on:
        from .sheet import sheet
        sheet(out, doc, os.path.join(out, f"{cid}_culture_sheet.png"))
    if problems:
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])

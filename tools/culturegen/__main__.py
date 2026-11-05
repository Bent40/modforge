"""culturegen: culture spec (YAML) -> vanilla structure .nbt files + preview renders.

usage: python -m tools.culturegen cultures/goblin.yaml OUT_DIR [--no-render]
"""
import json
import os
import sys
import zlib

import yaml

from . import nbt
from .forms import FORMS
from .grid import Palette


def main(argv):
    spec_path, out = argv[0], argv[1]
    render_on = "--no-render" not in argv
    doc = yaml.safe_load(open(spec_path))
    culture = doc["spec"]
    cid = doc["content_id"]
    os.makedirs(os.path.join(out, "structures", cid), exist_ok=True)
    os.makedirs(os.path.join(out, "previews"), exist_ok=True)
    manifest = []
    for b in culture["buildings"]:
        pal = Palette(culture["palette"], seed=zlib.crc32(b["id"].encode()))
        grid, meta = FORMS[b["form"]](b["params"], pal, culture)
        grid.connect_fences()
        p = os.path.join(out, "structures", cid, b["id"] + ".nbt")
        root = grid.to_nbt(p)
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
            for view, cut in (("front", None), ("back", None), ("cutaway", meta["cut_y"])):
                rp = os.path.join(out, "previews", f"{b['id']}_{view}.png")
                render(grid, rp, scale=4, view="back" if view == "back" else "front", cut_y=cut)
            entry["previews"] = [f"previews/{b['id']}_{v}.png" for v in ("front", "back", "cutaway")]
        manifest.append(entry)
        print(b["id"], root["size"], sum(counts.values()), "blocks")
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1)
    if render_on:
        from .sheet import sheet
        sheet(out, doc, os.path.join(out, f"{cid}_culture_sheet.png"))


if __name__ == "__main__":
    main(sys.argv[1:])

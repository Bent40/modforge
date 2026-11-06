"""Jigsaw world-gen data (Minecraft 1.21.1 format) + a static connector check."""
import json
import os


def _jigsaws(root):
    for blk in root["blocks"]:
        st = root["palette"][blk["state"]]
        if st["Name"] == "minecraft:jigsaw":
            yield blk["pos"], st["Properties"]["orientation"], blk["nbt"]


def check_jigsaws(roots, culture, ns, race):
    """Every connector that opens a pool must find, in that pool, a piece with a connector of the target name."""
    v = culture.get("village")
    if not v:
        return []
    pools = {f"{ns}:{race}/{k}": list(ids) for k, ids in v["pools"].items()}
    names = {bid: {j[2]["name"] for j in _jigsaws(r)} for bid, r in roots.items()}
    out = []
    for bid, r in roots.items():
        for pos, ori, j in _jigsaws(r):
            if j["pool"] == "minecraft:empty":
                continue
            if j["pool"] not in pools:
                out.append(f"{bid} {pos}: pool {j['pool']} not defined")
                continue
            if not any(j["target"] in names.get(c, ()) for c in pools[j["pool"]]):
                out.append(f"{bid} {pos}: no piece in {j['pool']} has a connector named {j['target']}")
            if not ori.endswith("_up"):
                out.append(f"{bid} {pos}: unexpected orientation {ori}")
    for pool, ids in pools.items():
        for i in ids:
            if i not in roots:
                out.append(f"pool {pool} lists unknown piece {i}")
    return out


def _dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
        f.write("\n")
    return path


def write_worldgen(out, culture, ns, race):
    v = culture["village"]
    d = os.path.join(out, "data", ns)
    files = []
    tm = set(v.get("terrain_matching", []))
    for pool, ids in v["pools"].items():
        files.append(_dump(os.path.join(d, "worldgen", "template_pool", race, pool + ".json"), {
            "fallback": "minecraft:empty",
            "elements": [{"weight": w, "element": {
                "element_type": "minecraft:single_pool_element",
                "location": f"{ns}:{race}/{bid}",
                "projection": "terrain_matching" if bid in tm else "rigid",
                "processors": "minecraft:empty"}} for bid, w in ids.items()],
        }))
    sid = v["structure"]
    tag = f"{ns}:has_structure/{sid}"
    files.append(_dump(os.path.join(d, "tags", "worldgen", "biome", "has_structure", sid + ".json"),
                       {"replace": False, "values": v["biomes"]}))
    files.append(_dump(os.path.join(d, "worldgen", "structure", sid + ".json"), {
        "type": "minecraft:jigsaw",
        "biomes": "#" + tag,
        "step": "surface_structures",
        "spawn_overrides": v.get("spawn_overrides", {}),
        "terrain_adaptation": v.get("terrain_adaptation", "beard_thin"),
        "start_pool": f"{ns}:{race}/center",
        "size": v["size"],
        "start_height": {"absolute": 0},
        "project_start_to_heightmap": "WORLD_SURFACE_WG",
        "max_distance_from_center": v["max_distance_from_center"],
        "use_expansion_hack": False,
    }))
    files.append(_dump(os.path.join(d, "worldgen", "structure_set", sid + ".json"), {
        "structures": [{"structure": f"{ns}:{sid}", "weight": 1}],
        "placement": {"type": "minecraft:random_spread", "spacing": v["spacing"],
                      "separation": v["separation"], "salt": v["salt"],
                      **({"exclusion_zone": v["exclusion_zone"]} if "exclusion_zone" in v else {})},
    }))
    return files

# culturegen

Culture spec (YAML) -> vanilla structure `.nbt` + preview renders. Python 3 + PyYAML + Pillow + numpy;
NBT writing is built in (no nbtlib).

    python -m tools.culturegen cultures/goblin.yaml drafts/goblin-culture

Output: `data/<modid>/` datapack tree (pieces under `structure/<race>/`, jigsaw pools, structure,
structure set, biome tag), a flat-ground village simulation render `<race>_village_seed*.png`,, `previews/*_{front,back,cutaway}.png`, `<race>_culture_sheet.png`,
`manifest.json` (size + block counts per building). Every .nbt is read back after writing as a check.
Preview colours approximate vanilla (no game jar in the cloud); they show layout and palette, not the final look.

## MineColonies style pack (reskin)

    python -m tools.culturegen.reskin cultures/goblin.yaml <fortress pack dir> <out>/goblin --render 3

Copies every `.blueprint` of a source pack with its palette remapped by the culture's `reskin:` rules
(wood species, stone families, dyes, glass, exact ids, regexes). Hut blocks, shapes and Structurize placeholders
are untouched, so every hut keeps all its levels. `_reskin_report.json` lists what was mapped and what was
kept (modded blocks such as Domum Ornamentum). `blueprint.py` reads and writes the format, and can also turn a
culturegen building into a blueprint (`from_grid`) for hand-designed replacements.

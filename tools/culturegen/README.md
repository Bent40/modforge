# culturegen

Culture spec (YAML) -> vanilla structure `.nbt` + preview renders. Python 3 + PyYAML + Pillow + numpy;
NBT writing is built in (no nbtlib).

    python -m tools.culturegen cultures/goblin.yaml drafts/goblin-culture

Output: `data/<modid>/` datapack tree (pieces under `structure/<race>/`, jigsaw pools, structure,
structure set, biome tag), a flat-ground village simulation render `<race>_village_seed*.png`,, `previews/*_{front,back,cutaway}.png`, `<race>_culture_sheet.png`,
`manifest.json` (size + block counts per building). Every .nbt is read back after writing as a check.
Preview colours approximate vanilla (no game jar in the cloud); they show layout and palette, not the final look.

# culturegen

Culture spec (YAML) -> vanilla structure `.nbt` + preview renders. Python 3 + PyYAML + Pillow + numpy;
NBT writing is built in (no nbtlib).

    python -m tools.culturegen cultures/goblin.yaml drafts/goblin-culture

Output: `structures/<race>/*.nbt`, `previews/*_{front,back,cutaway}.png`, `<race>_culture_sheet.png`,
`manifest.json` (size + block counts per building). Every .nbt is read back after writing as a check.
Preview colours approximate vanilla (no game jar in the cloud); they show layout and palette, not the final look.

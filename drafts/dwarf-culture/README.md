# Dwarf culture (Create theme): hand-designed

Ben 2026-11-09: each evolved race gets a real mod theme (dwarves = Create) and builds should show real effort,
"how you would build the things yourself". So dwarf buildings are laid out by hand in
`tools/culturegen/hand_dwarf.py`, not by the generic forms.

First piece: the town hall (`dwarf_hall`): deepslate plinth with a stepped skirt and buttresses, polished andesite
walls between andesite-casing pillars, brass band, tall framed-glass windows, steep deepslate-tile roof with a
copper ridge, twin brick chimneys, a gear clock tower with a copper finial, a cog train over the door, and a water
wheel on the west wall.

- `previews/`: iso renders. `pack/dwarf_preview/`: loose Structurize pack (fundamentals/townhall1) for paste tests.
- Residence (`dwarf_house`): dug-in deepslate ground storey (kitchen, table, straight stair), jettied andesite
  upper storey on casing posts with corbels (beds, chests), brick chimney, copper water tank on a stand.
- Smithy (`dwarf_smithy`): forge hall with a 5-wide open front under a stone lintel, 3x3 brick forge stack with the
  fire seen behind iron bars, blast furnaces, anvil, grindstone, quench cauldron, a Create press over a depot turned
  by a hand crank through the wall, and a coal/ore lean-to.
- Town hall water wheel: cistern and chute drop a waterfall down the rim (Create wheels need flowing water).
- Pack now holds townhall1, residence1, blacksmith1. Untested in game: fluid_tank, fluid_pipe, depot,
  mechanical_press, hand_crank, and whether the wheel spins.
- Levels 1-5 for all three: `python3 -m tools.culturegen.build_dwarf` writes the pack (shared footprint per hut) and
  previews/levels/; sheets `previews/dwarf_{townhall,residence,blacksmith}_levels.png`.
- Next: the generator for the long tail in the dwarf style.

# Goblin colony huts: what each level must contain

Status: research for the "real goblin huts" proposal (card to Ben 2026-11-08). Counts below are from the current
Goblin pack (= Fortress layouts, reskinned), read with tools/culturegen/blueprint.py. A generated goblin hut must
keep the same footprint across levels (upgrades build in place) and carry at least these working blocks.

`*` = MineColonies/Structurize block. `blocksolidsubstitution` = "keep terrain/solid" filler, `blocksubstitution` = air-keep.

| hut | lvl | size x,y,z | hut block | beds | racks | other working blocks |
|---|---|---|---|---|---|---|
| townhall | 1 | 32,47,32 | blockhuttownhall | 2 | 1 | 4 chest, 3 barrel, 7 furnace, crafting table |
| townhall | 2 | 32,47,32 | " | 2 | 1 | 4 chest, 3 barrel, 12 furnace |
| townhall | 3 | 32,47,32 | " | 6 | 6 | stash, 5 chest, 8 barrel, 2 crafting |
| townhall | 4 | 32,47,32 | " | 12 | 19 | stash, 14 chest, smoker, campfire, composter |
| townhall | 5 | 32,47,32 | " | 22 | 27 | stash, 21 chest, brewing stand, enchanting table |
| residence | 1 | 16,16,16 | blockhutcitizen | 2 | 1 | |
| residence | 2 | 16,16,16 | " | 4 | 1 | crafting table |
| residence | 3 | 16,16,16 | " | 6 | 1 | 2 crafting |
| residence | 4 | 16,16,16 | " | 8 | 4 | |
| residence | 5 | 16,16,16 | " | 10 | 4 | |
| builder | 1 | 16,16,8 | blockhutbuilder | 0 | 0 | crafting table |
| builder | 2 | 16,16,8 | " | 0 | 2 | furnace |
| builder | 3 | 16,16,8 | " | 0 | 4 | 2 furnace |
| builder | 4 | 16,16,8 | " | 0 | 6 | |
| builder | 5 | 16,16,8 | " | 0 | 8 | |

Open checks before generating (read MineColonies source/jar on the PC): which counts MineColonies actually
enforces (residence beds = citizens housed; racks = storage) vs. Fortress decoration; whether the footprint may
change between levels; hut block facing + primary_offset rules.

Plan if approved: culturegen forms -> `round_hut` residence (grows a ring per level), `long_hall` town hall
(grows in length, adds stilts/tower at 4-5), `lean_to` builder yard (racks under the roof, fenced yard). Totem,
skull banner, hay thatch, mud walls, no glass, as in cultures/goblin.yaml. Previews to Ben first.

# Goblin colony huts: what each level must contain

Status: research for the "real goblin huts" proposal (card to Ben 2026-11-08). Counts below are from the current
Goblin pack (= Fortress layouts, reskinned), read with tools/culturegen/blueprint.py. A generated goblin hut must
keep the same footprint across levels (upgrades build in place) and carry at least these working blocks.

`*` = MineColonies/Structurize block. `blocksolidsubstitution` = "keep terrain/solid" filler, `blocksubstitution` = air-keep.

| hut | lvl | size x,y,z | hut block | beds (2 blocks each) | racks | other working blocks |
|---|---|---|---|---|---|---|
| townhall | 1 | 32,47,32 | blockhuttownhall | 1 | 1 | 4 chest, 3 barrel, 7 furnace, crafting table |
| townhall | 2 | 32,47,32 | " | 1 | 1 | 4 chest, 3 barrel, 12 furnace |
| townhall | 3 | 32,47,32 | " | 3 | 6 | stash, 5 chest, 8 barrel, 2 crafting |
| townhall | 4 | 32,47,32 | " | 6 | 19 | stash, 14 chest, smoker, campfire, composter |
| townhall | 5 | 32,47,32 | " | 11 | 27 | stash, 21 chest, brewing stand, enchanting table |
| residence | 1 | 16,16,16 | blockhutcitizen | 1 | 1 | |
| residence | 2 | 16,16,16 | " | 2 | 1 | crafting table |
| residence | 3 | 16,16,16 | " | 3 | 1 | 2 crafting |
| residence | 4 | 16,16,16 | " | 4 | 4 | |
| residence | 5 | 16,16,16 | " | 5 | 4 | |
| builder | 1 | 16,16,8 | blockhutbuilder | 0 | 0 | crafting table |
| builder | 2 | 16,16,8 | " | 0 | 2 | furnace |
| builder | 3 | 16,16,8 | " | 0 | 4 | 2 furnace |
| builder | 4 | 16,16,8 | " | 0 | 6 | |
| builder | 5 | 16,16,8 | " | 0 | 8 | |

Open checks before generating (read MineColonies source/jar on the PC): which counts MineColonies actually
enforces (residence level n = n beds = n citizens, matches the counts; racks = storage) vs. Fortress decoration; whether the footprint may
change between levels; hut block facing + primary_offset rules.

Plan if approved: culturegen forms -> `round_hut` residence (grows a ring per level), `long_hall` town hall
(grows in length, adds stilts/tower at 4-5), `lean_to` builder yard (racks under the roof, fenced yard). Totem,
skull banner, hay thatch, mud walls, no glass, as in cultures/goblin.yaml. Previews to Ben first.

## Rollout to every building (Ben approved the theme 2026-11-08)

Pack inventory (scripted, 313 hut blueprints, ~50 hut types):
- **A. Generic workshops (~35 types)**: crafters, luxury, metallurgy, masonry, husbandry pens, education, mystic,
  storage, hospital, tavern, barracks. Per level, copy the SOURCE level's working blocks (every block with a
  tile entity + every `minecolonies:` block: racks, beds, furnaces, smokers, brewing stands, lecterns, beehives,
  composter barrels, scarecrows, enchanting tables, graves, stash) into a goblin shell sized to fit.
- **B. Position tags** to recreate: sit (residence/townhall/tavern/cook/library/university), work (blacksmith, cook,
  university), groundlevel, fishing (fisherman), cobble+ladder (miner), portal+vault (netherworker),
  bamboo/cactus/sugar (plantation), gatehouse archer/knight/gate/stand_in/out.
- **C. Keep the reskin**: decorations, infrastructure (roads, rails, mineshafts, adapters), walls, crop fields
  (blockhutfield / plantationfield): terrain-shaped or not huts.
Order: A first (biggest win), then B one by one, previews per category for Ben.

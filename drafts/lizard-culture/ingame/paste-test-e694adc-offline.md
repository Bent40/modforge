# Lizardman Preview and Dwarf town hall checks at modforge e694adc (offline only)

Date: 2026-11-10. This was a **text-only, offline** check. No game was booted and nothing was pasted.

- **GPU:** the coordinator ruled out booking the GPU or running the test client: noesis is training until 18:28, and Aldo books right after.
- **Headless pasting:** `/structurize paste` needs a real logged-in player, and the test harness has no paste-as-fake-player test. Adding one would mean changing the harness jar, which this job ruled out.
- **Lock and GPU:** I took no testlock and no GPU booking for this.

So the questions that need a running world (does the line shaft actually turn, does water stay in its channels) are answered from the blueprint data and Create's connection rules, and still need one in-game paste to confirm.

## 1. Block states (all 15 lizard blueprints)

All 15 blueprints were checked against the vanilla 1.21.1 jar's blockstate files (townhall, residence and combatacademy, levels 1-5).

- **Property keys:** none unknown in any blueprint.
- **Property values:** all valid:
  - mangrove log, planks, fence, door and stairs
  - bamboo_mosaic, bamboo_trapdoor, bamboo_fence
  - dark_prismarine_stairs and slab, including `outer_left` and `outer_right`
  - waxed_oxidized_cut_copper
  - mud_brick stairs and wall
  - green_bed, decorated_pot, note_block, lily_pad, carved_pumpkin, chain
- **Fence and wall false alarms:** the checker flagged fences with `false` sides and walls with `none` sides. These are valid; vanilla's multipart blockstate files simply never list those values.
- **Stored without block-entity data:** beds, barrels, smoker and decorated pot. This is normal for Structurize, which creates them when it places the blocks.

## 2. Dwarf town hall line shaft

| Levels | Junction at rel (-8, 7, 12) | Below it | Line rel (-8, 7, -1..21) |
|---|---|---|---|
| townhall1, townhall2 | No line shaft yet (air) | - | - |
| townhall3, townhall4, townhall5 | `create:gearbox[axis=x]` | `create:shaft[axis=y]` | Unbroken: every block is shaft or cogwheel with `axis=z` |

An x-axis gearbox connects its up, down, north and south faces. So, unverified until pasted, the vertical shaft from the wheel's gearbox should now drive the whole line. In the previous run the line cogwheels read 0 RPM and the vertical stack read 4 RPM. With this fix the line should read 4 RPM, or the same magnitude reversed.

## 3. Lizardman buildings (levels 5 and 1)

| Check | townhall5 | residence5 | combatacademy5 |
|---|---|---|---|
| Hut block | `blockhuttownhall` at y5, mangrove planks under it | `blockhutcitizen` at y4, mangrove planks under it | `blockhutcombatacademy` at y2, bamboo mosaic under it |
| Raised floor layer | y4: 285 mangrove planks | y3: 107 mangrove planks | y1: bamboo mosaic and mud brick |
| Stilts (mangrove log columns from y1 up to the floor) | 35, all on mud-brick footings | 16; **2 end on "keep terrain" cells with no footing** | none (a ground-level hall) |
| Ramp / steps | stairs at y1-3, rising to the doors (rel -3 and -1, y0, z-2) | stairs at y1-2 | mud-brick steps at y1 |
| Roof corners | dark prismarine stairs: 16 outer_left and 16 outer_right | 10 and 10 | 13 and 13 |
| Water | 228 blocks, 14 lily pads all on water | 67 blocks, fully walled | 22 blocks, 8 lily pads all on water |
| **Water touching unwalled cells** | **4: rel (-12,-4,-4), (8,-4,-4), (-12,-4,16), (8,-4,16)** | none | **4: rel (-11,-1,-3), (7,-1,-3), (-11,-1,7), (7,-1,7)** |

Level 1 versions have the same structure. townhall1 has 186 water blocks and no unwalled ones, and combatacademy1 has no water.

### Things to look at

1. **Corner water (townhall5, combatacademy5):** in each building, the four corner water blocks of the channels or pond sit next to a `blocksubstitution` ("keep existing terrain") cell instead of a wall.
   - If the ground beside them is solid at that height, nothing happens.
   - On open or lower ground, the water will spill out of the corner.
   - Level 1 of both buildings has no such cells, so this looks like a corner missed when the level-5 pond or channel was added. A mud-brick block at each of those 8 outside neighbours would close them.
2. **Residence stilts:** two of the residence's stilt columns have no mud-brick footing under them, unlike the other 14. They will stand on whatever terrain is there, which is cosmetic.
3. **Ground level, unverified:** each blueprint's bottom layer (y0) is a mud-brick foundation, and the hut blocks are raised 5, 4 and 2 blocks above it.
   - Whether the stilts stand on the ground or sink into it depends on where the build tool puts y0 relative to the clicked ground, and that has not been checked in-game.
   - The dwarf town hall (hut at y3) did land with its floor at grass level when pasted with the hut one block above the grass. But the stilt buildings rely more heavily on this.

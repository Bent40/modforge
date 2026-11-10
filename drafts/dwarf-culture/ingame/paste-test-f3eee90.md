# Dwarf Preview paste test: town hall 1, residence 1, smithy 1 (modforge f3eee90)

Date: 2026-11-10. TestServer (NeoForge 21.1.264, isekai_kingdoms 1.5.11) with a scripted TestClient. World goblin155_test.
The pack was loaded as a loose pack from `TestServer\blueprints\dwarf_preview` and removed afterwards.

## Offline block-state check

The three blueprints were checked against the real Create and vanilla blockstate files.

- **Property keys:** none unknown.
- **New parts:** every value is valid:
  - `create:fluid_tank` (bottom true/false, top, shape=window)
  - `create:fluid_pipe` (east/west)
  - `create:depot`
  - `create:mechanical_press[facing=west]`
  - `create:hand_crank[facing=east]`
  - `minecraft:grindstone[face=floor,facing=east]`
  - `water_cauldron[level=3]`
  - `iron_bars`
  - `gray_bed` head and foot
- **Stored without block-entity data:** barrels, blast furnaces, smoker, beds, chests and campfires. This is normal for Structurize, which creates block entities when it places the blocks.

## Paste

| Building | Where | Result |
|---|---|---|
| townhall1 | Fresh flat area outside the colony. Floor measured at y71 and everything above cleared. | Paste successfully triggered |
| residence1 | Cleared spot inside colony 9 (grass y62) | Paste successfully triggered. The hut claimed its land. |
| blacksmith1 | Cleared spot inside colony 9 | Paste successfully triggered. The hut claimed its land. |

No Structurize or Create errors, and no server freeze.

## In-game checks

All of these were read over RCON after the paste. Positions are relative to each hut block.

### Town hall

- The hut block, `large_water_wheel` and `water_wheel_structure` filler, gearbox, and line-shaft cogwheels are all present.
- **Waterfall:** water at all four chute heights beside the wheel rim (rel -12, 1..4, 14), so the chute flows.
- **Speeds**, read once and again about 10 s later:

| Part | Position | Speed |
|---|---|---|
| Large water wheel | -12,1,12 | **4.0 RPM** both times. The wheel spins at Create's normal large-wheel speed. |
| Gearbox | -8,1,12 | 4.0 |
| Cogwheel where the vertical shaft meets the line shaft | -8,7,12 | 4.0 |
| Line-shaft cogwheels | -8,7,0 and -8,7,20 | **0.0** |

- **Bug:** the line shaft is not driven. The junction cogwheel at -8,7,12 has `axis=y`, so it turns with the vertical shaft below it. The line-shaft shafts and cogwheels run `axis=z`, and a y-axis cogwheel doesn't connect axially to z-axis shafts.
  - **Fix:** put a `create:gearbox[axis=x]` at -8,7,12. A gearbox with axis x connects its up, down, north and south faces, which joins the vertical shaft below to the z-axis line on both sides. A z-axis cogwheel meshed with a y-axis one would also work.

### Residence

- **Hut:** the hut block (`blockhutcitizen`) is in place.
- **Beds:** two beds upstairs, each with a chest; the screenshot shows them correctly formed. My RCON check had head and foot swapped, so it reported false negatives. The blueprint has the heads on the west, which is correct for `facing=west`.
- **Stairwell:** the opening in the upper floor (rel 5, 4, 1..4) is air, and the stair below it is in place.
- **Fluid tank:** formed correctly as one 2-high tank. The bottom block is the controller (`Height: 2, Size: 1, Window: 1`), and the top block points to it. The pipe is next to it.

### Smithy

- **Hut:** the hut block (`blockhutblacksmith`) is in place.
- **Press:** `create:depot` at 0,0,3, air at 0,1,3, and `mechanical_press[facing=west]` at 0,2,3. That is the correct press-over-depot spacing.
- **Crank line:** shafts (`axis=x`) at 1..2,2,3 and `hand_crank[facing=east]` at 3,2,3, so the crank is attached through the shafts to the press. Speed is 0 because nobody is cranking.
- **Other blocks:** the grindstone, anvil and iron bars are in place.

## Shots

- `dwarf_townhall3_front`, `_wheel`, `_inside`
- `dwarf_house1_front`, `_back`, `_inside`, `_upstairs`
- `dwarf_smithy1_front`, `_press`, `_inside`

## Process note

The GPU was booked exclusively by another project (noesis) during this run. My run script didn't stop when its reservation was refused, so the test client ran anyway. The script also released noesis's reservation at the end by mistake. The script is fixed, and Ben has been told so the noesis booking can be restored.

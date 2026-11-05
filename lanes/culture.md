# lane / culture

Race cultures for world-gen buildings (villages, ruins, outposts, later MineColonies styles).
One culture spec per race and tier; buildings are generated from it, never hand-placed.

## Deliverables

1. `cultures/<race>.yaml` — the SpecBlock (envelope + `spec` below). The data.
2. Generated `structures/<race>/<building>.nbt` (vanilla structure format, DataVersion 3955 = 1.21.1).
3. Preview sheet (front / back / cutaway per building) for approval. The sheet is NOT the handoff.

## spec body

```
spec:
  lore:      sourced paragraph (say which source, and when it is recall)
  tier:      wild | named | kingdom          # later tiers reuse roles with upgraded blocks
  front:     north                           # every building's door faces -Z (z = 0)
  palette:   { role: { block_id: weight, ... } }   # first entry = main block; weights = weathering mix
  banner_pattern: [ { pattern, color } ]
  rules:     { glass, roof, overhang, frame, motif, light_level }
  buildings: [ { id, display_name, form, role_in_village, params } ]
```

Roles used by the current forms: foundation, wall, frame, beam, floor, deck, gable, thatch, eave, trim,
door, shutter, climb, light, hearth, bedding, storage, seat, banner, trophy. Forms name roles, never
block ids, so a new race is mostly a palette edit; a new silhouette is a new form in
`tools/culturegen/forms.py` (round_hut, long_hall, stilt_tower so far).

## Rules

- Cells a building does not write stay structure_void (terrain kept); interiors are written as air.
- Fence connections are baked by the generator; hanging blocks (door, open trapdoor, ladder, wall torch,
  wall banner) sit on the side opposite their `facing`.
- Only vanilla or pack blocks that exist in 1.21.1. Modded blocks need their real id checked in the jar.

## verify (menu)

- Loads in a structure block (Load, `<modid>:<race>/<id>`) with no missing-block warnings.
- Door faces north, nothing floats, fences connect, torches attached, no terrain left inside.

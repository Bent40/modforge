# core / reject-checklist

A deliverable that trips any of these is **not usable** — fix before handoff. `[ ]` = confirm it is
NOT happening. Shared rejects apply to every lane; then the per-lane lists.

## Shared (all lanes)
```
[ ] visual deliverable with no paired SpecBlock
[ ] color named in prose / raw hex instead of a palette role
[ ] non-literal identifier (Title Case, spaces, caps, leading digit) used as a code name
[ ] texture delivered as PNG / b64 / procedural painter instead of palette-index grids
[ ] design computes UV / texOffs itself (the build must own atlas packing)
[ ] emoji anywhere
[ ] a cost / discount / regen not bound to magicule
[ ] no `verify` block, or no in-game acceptance check
[ ] geometry / numbers left "provisional, refine later" instead of solved + self-checked
```

## item
```
[ ] sprite uses a color off the declared palette
[ ] tooltip shows native mana/damage instead of the real magicule / boosted numbers
[ ] economy_binding raises capacity, or stacks uncapped
[ ] attribute item with no slot declared
[ ] recipe implied in prose instead of a datagen ref or explicit "none"
```

## spell
```
[ ] damage with no damage_type
[ ] vfx color as hex / prose instead of a palette role
[ ] cost given only in native mana, no magicule equivalent
[ ] a hosted spell with no mastery_lane and no explicit "none"
[ ] grief (block break / fire) on by default with no stated reason
[ ] entity spawned but no lifetime / hitbox
```

## entity
```
[ ] missing axes block, or a forward part not at the most-negative Z
[ ] animated bone with no pivot, or pivot not at its rotation centre
[ ] root-translating walk/run anim (legs animate in place; entity motion carries it)
[ ] texture not per-face grids / design computed texOffs itself
[ ] a ranged / breath ability at or below melee priority
[ ] no rest_pose declared
[ ] feet not at y=0 / cuboids interpenetrate beyond declared joints
```

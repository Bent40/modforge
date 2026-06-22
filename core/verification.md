# core / verification

Rejects (`core/reject-checklist.md`) catch what's wrong; `verify` states what **done** looks like, so
a build is testable, not vibes. Every spec ends in a `verify:` list — at least one check **observable
in-game**.

## Two principles
1. **Data is the source of truth; a render is a sanity check.** The spec's numbers and grids are what
   the build uses. A paired reference render is viewed only to confirm the bake matched — never as the
   data.
2. **Numbers are solved, not provisional.** We build straight from the spec (no Blockbench refine
   pass), so "starting value — refine later" ships as-is. Geometry must be solved precisely and carry
   **self-checks** the build verifies. This is the rule that stops heads overlapping bodies.

## Geometry self-checks (entity / 3D item)
```
- feet / base at y = 0 (sits on the ground)
- forward part at the most-negative Z (head leads travel)
- a connecting part seats on its neighbour — no deep interpenetration beyond declared joints
- the eyes / detail face is the front face
```

## Per-lane verify menus

### item
```
- appears in <creative_tab> with the rendered sprite (emissive cells glow)
- tooltip reads the real magicule cost / effect, not native numbers
- regen_flat adds <n> magicule/sec while held/worn, and stops at the stack cap
- cast_discount lowers <system> cost by <pct>, capped with other discounts
```

### spell
```
- casting costs <magicule> and fails / penalises when broke (per host bridge)
- mastery_lane rises with use; damage scales floor ×5 → cap
- bosses tagged immune take base (unboosted) damage and grant no mastery
- tooltip shows the real magicule cost + boosted damage
- vfx plays the keyframed sequence; emissive glows; no block grief
```

### entity
```
- on spawn, head leads travel (faces -Z); feet sit on the ground
- <ability> fires at range and is what you normally see; melee only at point-blank
- sit / idle / walk play from the rest pose with no slide, lurch, or root teleport
- emissive cells (eyes / markings) glow and land on the intended face
- spawn / tame / loot behave per spec
```

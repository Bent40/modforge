# core / spec-envelope

The shared handoff payload and every convention all three lanes obey. Read this before any lane doc.

## The envelope

```
type:          item | spell | entity
content_id:    <snake_case>            # literal registry id == the code name
modid:         <snake_case>            # target jar (isekai_beasts | mahoumagicule | ...)
display_name:  "Title Case"
build_target:  vanilla_codemodel | geckolib | datagen_only | event_handler | none
host:          none | irons_spells | ars_nouveau | psi | mahoutsukai | tensura
spec:          { lane-specific — see lanes/*.md }
verify:        [ acceptance checks; at least one in-game ]
```

`build_target` tells Claude Code HOW to build, decoupled from WHAT the design is:
- `vanilla_codemodel` — hand-written `EntityModel`/`item model json`. Most reliable for the
  in-env, no-Gradle hand-compile pipeline. **Default for `entity` and `item`.**
- `geckolib` — `.bbmodel` + `.animation.json` + GeoEntity. Use when Blockbench round-tripping is
  wanted. GeckoLib 4.8.4 is present in the pack.
- `datagen_only` — pure data (recipes, loot, tags, simple items). No Java behaviour.
- `event_handler` — no asset; a NeoForge/mixin handler (most `spell` integration, economy hooks).
- `none` — config/datapack only.

## AXES — the axiom that prevents the 180° spin

**Author in Minecraft's frame. Do not rely on Claude Code to rotate the model.**

```
forward: -Z      # the way the entity faces / travels; head/muzzle point here
up:      +Y
right:   +X
unit:    1 model px = 1/16 block
texel:   16 texture px = 1 model unit
```

Hard rule (reject if violated): a forward-facing part (head, muzzle, item tip) must have a
**more-negative Z** than its rear. Verified by self-check, not by eyeballing a render.
Authoring in-frame means no runtime rotation, which means **none** of the look-at / tilt / sit
sign-flips that cost four rebuilds on the Cinderkit ever happen.

## GEOMETRY — default is rotated cuboids

Primitives are **cuboids**. Each cuboid carries a **rest rotation** about its pivot
(`rot:[x,y,z]` degrees) — and by default it should be used. Rotated cuboids are the standard: they
give a non-blocky, low-poly silhouette (angled snouts, splayed ears, tapered limbs, faceted gems)
while every primitive stays a box you can grid-texture (`core/texture-grid.md`) and skeletally
animate. An axis-aligned box is just the `rot:[0,0,0]` case — fine for genuinely blocky parts.

- `vanilla_codemodel` — each independently-rotated box is its own `PartDefinition` with a rotation in
  its `PartPose`; animation adds deltas onto that rest rotation (the `restBodyXRot` pattern).
- `geckolib` — a bone/cube rotation.
- Free-form triangle meshes are NOT cuboids and leave this workflow — `build_target: custom_mesh`
  escape hatch only (no grid texture, no skeletal animation). See `core/texture-grid.md` §7.

## NAMING

snake_case, ASCII, leading letter, no caps/spaces. The label IS the code name. `"Title Case"` for
display strings only. One identifier, used identically on the diagram, in the spec, and in code.

## PALETTE — roles, never hex-in-prose

Defined once per content, referenced everywhere (texture grids, VFX colors, glow). See
`core/palette.md`. A color named in prose ("dark purple") instead of a role bound to a hex is a
reject. Each role: `{ id, hex, emissive: bool, note }`.

## TEXTURE — per-surface palette-index grids, build owns the UV

The source of truth for pixels is a **matrix of palette indices**, per surface, NOT a PNG, NOT a
b64 blob, NOT a procedural painter (procedural is what misplaced the Cinderkit eyes). The design
does **not** compute UV / `texOffs` — Claude Code packs the atlas so pixels and UVs cannot desync.
Emissive is flagged per cell. Grid orientation pinned: row 0 = top, col 0 = left, viewed from
outside. Full schema + shorthand in `core/texture-grid.md`. Items use a flat sprite grid; entities
use per-cube-per-face grids; spells use VFX color roles + any flat textures.

## BUILD CONVENTIONS (this pack)

- NeoForge **1.21.1**, Java 21. Registry id `modid:content_id`. Lang key per content + tooltip.
- Hand-compile pipeline (no Gradle): `javac -proc:none --release 21`, package with `jar`, run via
  PowerShell with `C:/` paths. Old jars are **renamed `.jar.disabled`, never deleted**. Version bump
  per change (`1.1.0 → 1.1.1`).
- Economy: this pack runs ONE currency — Tensura **magicule**. Anything with a cost or a
  cost-discount binds through the magicule bridges (`mahoumagicule` / `tensura_iron_spells`), never
  a parallel resource. Damage/mastery scale through the per-system **mastery lanes**.
- Missing-mod safety: a content that targets an optional host must degrade, not crash, if the host
  jar is absent (guard handlers on `ModList.isLoaded`).

## VERIFICATION — positive criteria, not just rejects

Every spec ends in a `verify:` list of acceptance checks, at least one **observable in-game**.
Rejects (`core/reject-checklist.md`) catch what's wrong; `verify` states what "done" looks like, so
a build is testable, not vibes. See `core/verification.md` for the per-lane check menus.

## SHARED REJECTS (apply to all lanes)

```
[ ] visual deliverable with no SpecBlock
[ ] color named in prose instead of a palette role
[ ] non-literal / Title-Case / spaced identifier used as a code name
[ ] texture delivered as PNG/b64/procedural instead of palette-index grids
[ ] design computes UV/texOffs itself (build must own atlas packing)
[ ] missing `axes` block, or forward part not at most-negative Z   (entity/3d-item)
[ ] emoji anywhere
[ ] a cost/discount/regen not bound to magicule
[ ] no `verify` block / no in-game acceptance check
```

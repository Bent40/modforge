# Modforge

A design language and handoff system for designing **mod content** that hands off cleanly to code.
Target stack: NeoForge 1.21.1. Build targets: vanilla code-model / GeckoLib / datagen / event-handler.
Default geometry: **rotated cuboids** — low-poly silhouettes that keep the grid-texture + skeletal-animation workflow.

Modforge is the evolution of **Mobforge**: the same visual system, the same standing-rules
philosophy, generalized from "mobs only" to **three content lanes**:

| lane     | makes                                   | worked example       |
|----------|-----------------------------------------|----------------------|
| `item`   | items, tools, trinkets, blocks-as-items | `cooling_ember_core` |
| `spell`  | spells, abilities, projectile/beam VFX  | `skyfall_lance`      |
| `entity` | mobs + NPCs (the old Mobforge)          | `cinderkit`          |

Mobs are no longer the whole system — they are the `entity` lane.

## The one rule everything still serves

**The image is NOT the handoff — the paired spec block is.** Claude Code reads text, not pictures.
Every visual deliverable ships alongside a structured, machine-readable **SpecBlock** (see
`core/spec-envelope.md`). A design with no spec block is not usable downstream.

## Architecture: one spine, three lanes

```
modforge/
  core/
    spec-envelope.md   ← the shared SpecBlock + every shared convention (READ FIRST)
    palette.md         ← palette-as-schema (roles, hex, emissive)            [shared]
    texture-grid.md    ← per-surface palette-index matrices, build owns UV   [shared]
    reject-checklist.md← shared rejects + per-lane rejects                   [shared]
    verification.md    ← positive acceptance criteria + in-game checks       [shared]
  lanes/
    item.md            ← item lane: deliverables + spec schema + example
    spell.md           ← spell lane: cast + effect + VFX + entity + integration
    entity.md          ← entity lane: model + rig + motion + behaviour + npc
  examples/
    cinderkit/  skyfall_lance/  cooling_ember_core/      ← full worked sheets
  SKILL.md             ← makes this folder a downloadable Claude Skill
```

Every lane inherits the spine. The spine never repeats itself per lane.

## The shared SpecBlock envelope (the join)

```
type:          item | spell | entity
content_id:    <snake_case>            # the literal registry id AND the code name
modid:         <snake_case>            # which jar it lands in
display_name:  "Title Case"
build_target:  vanilla_codemodel | geckolib | datagen_only | event_handler | none
host:          none | irons_spells | ars_nouveau | psi | mahoutsukai | tensura
spec:          { ...lane-specific body... }
verify:        [ acceptance checks, including in-game ]
```

One parser, one envelope, three `spec` bodies. Full field reference in `core/spec-envelope.md`.

## Lanes compose — they are not silos

- a mob's attack **is** a spell: `entity.spec.abilities[] → spell content_id`
  (the Cinderkit flamethrower is a `spell`-lane ability the entity references)
- a spell can spawn an **entity**: `spell.spec.entity → entity mini-spec`
  (Skyfall Lance spawns a `skyfall_beam` projectile entity)
- an item can grant an **ability** or bind to the economy:
  `item.spec.economy_binding`, `item.spec.use_action → spell content_id`

Design one thing, reference it everywhere. Variants reuse, never redraw.

## What changed from Mobforge (the fixes from the first real build)

The Cinderkit shipped, but four classes of bug cost most of the iterations. Each is now a
**spine-level rule**, not a thing the designer remembers:

1. **Orientation is an axiom.** Author in Minecraft's frame (forward = −Z). No 180° spin, no
   sign-flip cascade. Hard reject if the head isn't at the most-negative Z. (`core/spec-envelope.md`)
2. **Pivots are first-class and sit at the rotation center.** The sit-lurch was a pivot at world
   origin. Every animated bone declares its pivot. (`lanes/entity.md`)
3. **Behaviour is a deliverable.** The "attacked like a normal wolf" bug was a goal-priority
   conflict — invisible to a visual-only system. The `entity` lane now specs AI goals + priorities.
4. **Texture is per-surface pixel grids, build owns the UV.** The misplaced eyes were procedural
   noise + a UV/texOffs desync. Now: palette-index matrices per face, build packs the atlas.
   (`core/texture-grid.md`)

## Naming is sacred (unchanged, now lane-wide)

snake_case, ASCII, starts with a letter, no caps, no spaces. The label on the diagram IS the code
name: `cinderkit`, `skyfall_lance`, `cooling_ember_core`, `leg_front_left_upper`, `locator_muzzle`.
Display names are `"Title Case"` quoted strings. Headings/eyebrows UPPERCASE. Prose sentence case.
No emoji, ever. Structural glyphs only (`→  └─ ├─  [ ]  ▸▾`).

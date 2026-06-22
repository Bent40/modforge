# lane / entity

Mobs and NPCs. The entity lane adds the orientation axiom, first-class pivots, a **behaviour**
deliverable, and an NPC block on top of the shared spine. `build_target: vanilla_codemodel`
(default, proven) or `geckolib`.

## Deliverables (bundle)

1. `concept` / `ortho` / `darkview` — render slots (darkview = black, only emissive lit).
2. `palette` — roles (`core/palette.md`).
3. `model` — cuboids with sizes, offsets, **pivots**, parents. Obeys the `axes` axiom.
4. `texture` — per-cube **per-face** palette-index grids + emissive layer (`core/texture-grid.md`).
5. `rig` — archetype bone tree + locators.
6. `motion` — explicit rest pose + per-bone keyframes; loop/once/hold flags; particle/sound keys.
7. `behaviour` — attributes, AI goals + priorities, targeting, spawn, taming, ability hooks.
8. `npc` — (humanoid only) dialogue / trades / llm-chat binding.
9. `spec` — the SpecBlock.

## ARCHETYPES (pick one; it sets the rig + gait defaults)

`quadruped` · `biped` · `serpentine` · `avian` · `blob` · `humanoid_npc`

A new entity selects an archetype and customises it — it does not re-derive a bone tree.

## spec body

```
spec:
  archetype:  quadruped | biped | serpentine | avian | blob | humanoid_npc
  axes:       { forward: -Z, up: +Y, right: +X }      # MANDATORY. Author in-frame. No spin.
  model:
    cuboids:  [ { bone, size:[w,h,d], offset:[x,y,z], pivot:[x,y,z], rot:[x,y,z]deg, parent, texoff_hint } ]
                 # rot = rest rotation about the pivot. DEFAULT geometry is rotated cuboids — use it.
                 # rot:[0,0,0] is the axis-aligned (blocky) special case.
    self_checks: [ "feet at y=0", "head Z < tail Z", "no interpenetration beyond declared joints" ]
  texture:    <per-cube per-face grids ref>            # build owns UV
  rig:        { bones:<archetype tree>, locators:[ {id, on_bone, pos} ] }   # locator_muzzle, etc.
  motion:
    rest_pose:[ { bone, rot:[deg], pos } ]             # the neutral all anims blend from
    anims:    [ { name, type: loop|once|hold, keyframes:[ {bone, t, rot:[deg], pos} ],
                  particle_keys:[...], sound_keys:[...] } ]
  behaviour:
    attributes: { max_health, movement_speed, attack_damage, follow_range, ...other }
    ai_goals:   [ { priority:<int>, goal, params } ]   # LOWER number = HIGHER priority
    ai_rule:    "a ranged/breath ability MUST outrank melee, or they fight over MOVE/LOOK and
                 the ability never fires (the 'attacked like a normal wolf' bug). Gate the ranged
                 goal to yield only at point-blank so the bite still happens up close."
    targeting:  [ { goal, params } ]
    spawn:      { category, biomes:[...], weight, placement } | none
    tameable:   { item, mechanic } | none
    abilities:  [ <spell content_id> ]                 # a mob attack IS a spell-lane spec
  npc:          { interaction: trades | dialogue_tree | llm_chat, profession, ... } | none
```

## Notes for the builder (the hard-won ones)

- **`axes` is non-negotiable.** Authoring forward = −Z means no 180° spin, which means no inverted
  look-at, no flipped tilt/sit signs. Every flip we fought on the Cinderkit traces to a model that
  was authored +Z-forward.
- **Pivot = the rotation centre.** A bone that swings about a joint pivots at the joint; a bone that
  rotates in place (a body recline) pivots at its **own centre**. The sit-lurch was a body pivot
  left at world origin while the cube sat 16px away.
- **Rotated cuboids are the default — lean on `rot`.** A rest rotation per box is what escapes the
  blocky look (splayed ears, angled snout, tapered legs) with zero texture cost (the grids don't
  change). Each independently-rotated box is its own `PartDefinition`/bone; animation adds deltas
  onto its rest `rot` (the `restBodyXRot`/`restTailXRot` pattern). Real triangle meshes are a hero
  one-off only (`build_target: custom_mesh`) and leave the grid/animation workflow.
- **`ai_goals` priorities are load-bearing.** Goals sharing MOVE/LOOK run one-at-a-time by priority.
  Put the signature ability above the melee bite, distance-gated, so the ability is what you see.
- `abilities[]` reference `spell`-lane specs (`host: none` for native abilities). The Cinderkit
  flamethrower is `cinderkit_flamethrower` in the spell lane, referenced here.
- `humanoid_npc` + `npc.interaction: llm_chat` is the hook for the kingdom/NPC-dialogue backlog.

## Lane rejects

```
[ ] missing axes block, or a forward part not at the most-negative Z
[ ] animated bone with no pivot, or pivot not at its rotation centre
[ ] root-translating walk/run anim (legs must animate in place; the entity's motion carries it)
[ ] texture not per-face grids / design computed texOffs itself
[ ] a ranged/breath ability at or below melee priority
[ ] no rest_pose declared
[ ] feet not at y=0 / cuboids interpenetrate beyond declared joints
```

## verify menu

```
verify:
  - on spawn, head leads travel (faces -Z); feet sit on the ground
  - <ability> fires at range and is what you normally see; melee bites only at point-blank
  - sit/idle/walk play from the rest pose with no slide, lurch, or root teleport
  - emissive cells (eyes/markings) glow; eyes are on the front face
  - spawn/tame/loot behave per spec
```

## WORKED EXAMPLE — `cinderkit` (abbreviated; full sheet in examples/)

```
type: entity   content_id: cinderkit   modid: isekai_beasts   build_target: vanilla_codemodel
display_name: "Cinderkit"   host: none
spec:
  archetype: quadruped
  axes: { forward: -Z, up: +Y, right: +X }
  model:
    cuboids:
      - { bone: head,     size:[8,7,6], offset:[0,13.25,<−Z, seats on neck>], pivot:[neck joint], rot:[0,0,0],   parent: body }
      - { bone: ear_left, size:[2,5,1], offset:[<−X side of head>],           pivot:[ear base],   rot:[0,0,-11], parent: head }   # splayed — rotated cuboid
      - { bone: ear_right,size:[2,5,1], offset:[<+X side of head>],           pivot:[ear base],   rot:[0,0,11],  parent: head }
      # ...legs (slight rot for a tapered stance), tail (rot droop)...
    self_checks: [ "feet at y=0", "head Z < tail Z (head leads)", "head rear seats on body front, no deep overlap" ]
  texture: cinderkit_faces      # charcoal/ash base, ember-crack + eye cells emissive (front face)
  rig: { bones: quadruped(head, body, leg_front_left ... tail), locators: [ {id: locator_muzzle, on_bone: head, pos:[snout tip]} ] }
  motion:
    rest_pose: [ ...neutral... ]
    anims: [ {name: idle, type: loop}, {name: walk, type: loop}, {name: sit, type: hold},
             {name: breathe, type: once, particle_keys:[flame@locator_muzzle]} ]
  behaviour:
    attributes: { max_health: 12, movement_speed: 0.3, attack_damage: 3, follow_range: 24 }
    ai_goals: [ {priority:1, goal: float}, {priority:2, goal: sit_when_ordered},
                {priority:3, goal: breath_attack, params:{ ability: cinderkit_flamethrower, range:7, min:1.5, cd:30-55 }},
                {priority:4, goal: melee_bite} ]
    ai_rule: "breath (3) outranks bite (4); breath yields <1.5 blocks so bite covers point-blank"
    targeting: [ {goal: owner_hurt_by}, {goal: hurt_by, params:{ alert_others: true }} ]
    spawn: { category: creature, biomes: [basalt_deltas, crimson_forest], weight: 12, placement: on_ground }
    tameable: { item: magma_cream, mechanic: wolf_style_1_in_3 }
    abilities: [ cinderkit_flamethrower ]   # spell-lane, host: none, cast_type: breath_cone
  npc: none
verify:
  - head leads travel; sit reclines in place (no forward slide)
  - flamethrower cone fires at 1.5–7 blocks, ignites + damages, spares owner/pets; bite at point-blank
  - ember eyes glow on the front of the head
```

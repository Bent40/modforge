# drafts / homing_projectile + seeker_bolt (2026-11-06)

A shared guided-projectile **carrier** (spell lane, `entity` block) and its first user. Every homing spell,
mob homing ability and Formula Arms guided round references `homing_projectile` instead of re-specifying
guidance. Numbers harvested from Superb Warfare's missiles (ideas only; SBW is LGPL-3.0). Build lives in
`magicule_standard` 2.8.0 (`homing/HomingProjectile.java`); design notes in isekai-chronicles
`docs/homing-and-lock-warning.md`.

## Carrier — `homing_projectile` (abstract; not spawnable on its own)

```
type: spell   content_id: homing_projectile   modid: magicule_standard   build_target: event_handler
display_name: "Homing Projectile (base)"   host: none
spec:
  cast_type: projectile
  entity:
    entity_id: homing_projectile            # abstract base class; concrete ids below
    lifetime:  400                          # hard cap, ticks
    hitbox:    per subclass
    renderer:  per subclass
  guidance:                                  # NEW block for this carrier; every value is a tunable override
    target_ref:        uuid                  # re-read every tick
    speed:             0.9                   # blocks/tick, no gravity
    turn_rate_deg:     6                     # per tick
    loss_angle_deg:    80                    # off-boresight -> lock lost for good
    fizzle_ticks:      100                   # after lock lost (or target gone)
    top_attack:        { aim_raise: "0.2 x (horiz_dist - 30)", start_dist: 30, bonus: 1.25, when: descending }
    decoys:
      match:   [ "tag magicule_standard:homing_decoys", "persistent flag isekai_decoy" ]
      range:   32
      cone_deg: 60                           # full width (30 half-angle)
      chance:  0.25                          # one roll per decoy per projectile; stops after a steal
    impact_event: neoforge ProjectileImpactEvent   # barriers that cancel it still block
    lock_hook:  HomingProjectile.LOCK_LISTENERS    # fires on locking a player -> lock-warning toast
  effect:
    damage:   { type: magic (indirectMagic, owner = caster), base: per subclass }
    no_grief: true
  integration:
    magicule_cost: via the castable spell, not the carrier
    mastery_lane:  per spell
    immune_tag:    tensura:immune_to_spell_boost
    tooltip_truth: true
verify:
  - /homing selftest -> turn_and_hit, lock_loss_fizzle, top_attack, decoy_steal all PASS
  - a bolt fired behind you (> 80 deg off) flies straight and fizzles ~5 s later
  - an illusion clone in the cone pulls about 1 in 4 bolts
```

## First user — `seeker_bolt`

```
type: spell   content_id: seeker_bolt   modid: magicule_standard   build_target: vanilla_codemodel
display_name: "Seeker Bolt"   host: none   # castable skill + magicule cost = next slice
spec:
  extends: homing_projectile               # all guidance defaults
  cast_type: projectile
  target:    entity                        # /homing fire <target> [top] until the skill exists
  effect:
    damage: { type: magic, base: 6, top_attack: 7.5 }
    no_grief: true
  vfx:
    palette:  [ mag_hi, mag_1 ]            # ui-style-guide magicule ramp, emissive (particles are fullbright)
    particles:
      - { type: minecraft:end_rod, where: "trail, 0.5 x velocity behind", rate: "1/tick", color_role: mag_hi }
      - { type: minecraft:enchant, where: centre, rate: "1/2 ticks", color_role: mag_1 }
      - { type: minecraft:end_rod, where: impact, rate: "12 burst", color_role: mag_hi }
      - { type: minecraft:smoke,   where: fizzle, rate: "6 burst", color_role: none }
    geometry: []                           # no model: NoopRenderer, the trail IS the bolt
    sounds:   [ { t: impact, sound_event: minecraft:block.amethyst_block.break } ]
  entity:
    entity_id: seeker_bolt   model: none (particles)   lifetime: 400   hitbox: 0.3125x0.3125   renderer: noop
  integration:
    magicule_cost: TBD with the castable skill (proposal: 250 magicule per bolt)
    mastery_lane:  TBD (proposal: a new "arcane" lane in magicule_standard)
    immune_tag:    tensura:immune_to_spell_boost
    tooltip_truth: true
verify:
  - hits a target 45 deg off-line for 6.0; from above for 7.5
  - no block damage, no fire
```

## Adapting the pack's existing homing (Ben 2026-11-08: "make sure it is something we can adapt those into")

Verified with javap on the real jars (isekai-chronicles `docs/research/foreign-homing-javap.md`, commit 2df5e10).
Other mods' homing spells keep their **own steering** (their feel, their numbers). The carrier's shared rules
join them through a small **adapter** per projectile class, so the rules below apply to every homing thing in the
pack, ours or not:

```
adapter:                                   # magicule_standard homing/adapters/, one entry per foreign class
  get_target: <how to read the lock>       # public getter, or a mixin accessor
  set_target: <how to move the lock>       # needed for decoys stealing it
  joins:      [ decoys, lock_warning ]     # turn cap / loss angle / fizzle stay native unless the class lets us override steering
  impact:     neoforge | manascore         # which impact event barriers/flares must listen to
```

| mod | class (spells/skills) | lock read/write | adapter kind |
|---|---|---|---|
| Iron's Spells | `AbstractMagicProjectile` (Echoing Strikes, Flaming Barrage, …) | public `getHomingTarget` / `setHomingTarget(LivingEntity)` | plain adapter, no mixin |
| Tensura | `TensuraFlyingProjectile` + children (aura_bullet, magma_shot), `ThrownItemProjectile` (Thrower), `TempestScaleEntity`, `ChaosEaterProjectile` | public get/set `homingTarget` | plain adapter; impact = **manascore** `PROJECTILE_HIT`, NOT NeoForge's event |
| Ars Nouveau / Ars Elemental | `EntityHomingProjectileSpell` (homing_projectile glyph), `EntityCarianPhalanx` | private field, no accessor | mixin accessor |
| trnightmare | Asriel orb, Friendliness Pellet, Spellcraft projectile | re-aims at owner's look / builder only | mixin; lowest priority |

Rule: an adapted projectile's lock on a player shows the same lock-warning toast, and illusions/flares can steal it
(one 25% roll per decoy, same cone). Its damage, cost and mastery stay with its host mod (Iron's/Ars costs already
flow through magicule via the bridges).

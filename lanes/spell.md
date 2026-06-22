# lane / spell

Spells, mob abilities, and their projectile/beam/zone VFX. A spell = cast + effect + VFX +
(optional) entity + magic-system integration. Host is one of the pack's magic mods, or `none` for a
native mob ability (the Cinderkit flamethrower is `host: none`).

## Deliverables (bundle)

1. `concept` — VFX render slot (the cast, lit; optional).
2. `cast` — host, school, cast type, cost, timing.
3. `effect` — damage/status/AoE.
4. `vfx` — the "texture" of a spell: particles + emissive geometry + keyframed timing. See below.
5. `entity` — if it spawns a projectile/beam/zone (a mini `entity`-lane spec).
6. `integration` — magicule cost + mastery + immune-tag + tooltip-truth.
7. `spec` — the SpecBlock assembling all of the above.

## spec body

```
spec:
  host:       irons_spells | ars_nouveau | psi | mahoutsukai | none   # none = native mob ability
  school:     <host school/element>            # irons: evocation/fire/blood/...; ars: element
  cast_type:  instant | channel | projectile | self_buff | zone | breath_cone
  levels:     { max:<int>, scaling:"<note>" }
  cost:
    base_mana:<host native units>              # the number the host shows
    magicule: <base_mana × host_rate>          # the REAL cost (irons ×50, ars ×25, psi/mahou ×5)
  cast_time:  <ticks>                           # chant/charge
  cooldown:   <seconds>
  target:     block_raytrace<=Nm | entity | self | aoe<r> | cone<r,deg>
  effect:
    damage:   { type:<damage_type>, base:<f>, per_level:<f>, tick_interval:<t>, duration:<t> } | none
    aoe:      <radius blocks | none>
    knockback:<amount | none>
    status:   [ { effect, amplifier, seconds } ]
    no_grief: true                              # PROJECT DEFAULT: no block break / fire spread
  vfx:
    palette:  [ color roles ]                   # from core/palette.md (emissive flagged)
    particles:[ { type, where:<locator/path>, rate, color_role } ]
    geometry: [ { shape: beam|billboard|ring|orb, size, texture, scroll:<uv/s>, emissive, layer } ]
    keyframes:[ { t, what } ]                    # charge -> fire -> impact -> fade
    sounds:   [ { t, sound_event } ]
  entity:                                        # omit for instant/self spells
    entity_id:<snake_case>
    model:    <entity mini-spec | billboard>
    lifetime: <ticks>
    hitbox:   <w×h | none>
    renderer: custom | billboard
  integration:
    magicule_cost: via <irons:tensura_iron_bridge | mahoumagicule>   # WHO charges it
    mastery_lane:  <e.g. irons:evocation | ars:fire | mahou:gandr | psi:psionics | none>
    damage_scaling:"floor ×5 → cap ×<N> by mastery"                  # per the granular mastery system
    immune_tag:    tensura:immune_to_spell_boost                     # bosses skip boost + gain
    tooltip_truth: true                                              # show magicule + boosted dmg
```

## Notes for the builder

- `host: irons_spells` → register an `AbstractSpell` (+ school config); cost/charge already flow
  through `tensura_iron_spells` at ×50; our `mahoumagicule` neuters the flat damage so the
  **mastery lane** owns scaling. Build is `vanilla_codemodel` for the entity/renderer +
  `event_handler` for mastery.
- `host: none` (native mob ability) → no spell registry; the effect runs in the entity's server
  tick (cone damage + `sendParticles` + ignite), exactly like the Cinderkit. `cast_type: breath_cone`
  is the Cinderkit shape.
- `vfx` is to a spell what `texture` is to a model: the precise, machine-readable description of what
  the player sees. Colors are roles, geometry is declared (not drawn), timing is keyframed.
- `damage_scaling` never hardcodes a multiplier — it names the mastery lane and the floor/cap; the
  build reads live mastery. `tooltip_truth` forces the displayed cost/damage to the real magicule
  numbers (the pending truth-fix), never the host's native values.

## Lane rejects

```
[ ] damage with no damage_type
[ ] vfx color as hex/prose instead of a palette role
[ ] cost given only in native mana, no magicule equivalent
[ ] a hosted spell with no mastery_lane and no explicit "none"
[ ] grief (block break/fire) on by default without an explicit reason
[ ] entity spawned but no lifetime/hitbox
```

## verify menu

```
verify:
  - casting costs <magicule> and fails/penalises when broke (per host bridge)
  - mastery_lane rises with use; damage scales floor ×5 → cap
  - bosses tagged immune take base (unboosted) damage and grant no mastery
  - tooltip shows the real magicule cost + boosted damage, not native
  - vfx plays the keyframed sequence; emissive geometry glows; no block grief
```

## WORKED EXAMPLE — `skyfall_lance` (Iron's addon, from the design handoff)

```
type: spell   content_id: skyfall_lance   modid: mahoumagicule   build_target: vanilla_codemodel
display_name: "Skyfall Lance"   host: irons_spells
spec:
  host: irons_spells   school: evocation   cast_type: channel   levels: { max: 10, scaling: "+1.5 dmg/level" }
  cost:    { base_mana: 450, magicule: 22500 }     # 450 × irons_rate 50
  cast_time: 60        # 3.0s charge
  cooldown:  25
  target:    block_raytrace<=32m
  effect:
    damage: { type: magic, base: 3, per_level: 1.5, tick_interval: 5, duration: 20 }  # L1 90 .. L10 360
    aoe: 2.5   knockback: 0.3   status: [ {effect: glowing, amplifier: 0, seconds: 3}, {effect: slowness, amplifier: 1, seconds: 2} ]
    no_grief: true
  vfx:
    palette: [ core_white, sky_pale, sky_blue, deep_blue ]   # all emissive
    geometry:
      - { shape: beam,      size: "r1.25 → impactY+48", texture: beam,      scroll: -1.6, emissive: true, layer: entity_translucent_emissive }
      - { shape: beam,      size: "r1.9 shell",         texture: beam_glow, scroll:  1.6, emissive: true, layer: entity_translucent_emissive }
      - { shape: orb,       size: "r0.6 charge",        texture: orb,       emissive: true }
      - { shape: ring,      size: "0.3 → 2.7 / 0.7s",   texture: ring,      emissive: true }
    keyframes: [ {t:0,"charge orb + 2 rings grow"}, {t:60,"beam fires 100t"}, {t:60,"impact decal r3 + shockwave"} ]
    sounds:    [ {t:0, beacon_activate}, {t:60, lightning_impact} ]
  entity:
    entity_id: skyfall_beam   model: billboard   lifetime: 100   hitbox: none   renderer: custom
  integration:
    magicule_cost: via irons:tensura_iron_bridge   mastery_lane: irons:evocation
    damage_scaling: "floor ×5 → cap ×30 by evocation mastery"
    immune_tag: tensura:immune_to_spell_boost      tooltip_truth: true
verify:
  - channel costs ~22500 magicule; broke-overdraft triggers the Iron's burn
  - evocation mastery rises; damage scales floor ×5 → cap ×30
  - beam VFX scrolls/emits; impact ring plays once; no terrain damage
```

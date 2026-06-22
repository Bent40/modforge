# lane / item

Items, tools, trinkets, food, block-items. Most are `datagen_only` or a thin `vanilla_codemodel`.

## Deliverables (bundle)

1. `concept` — render slot (optional; items are small).
2. `sprite` — the texture, as a **palette-index grid** (16×16 default; layered for emissive).
   THE source of truth. See `core/texture-grid.md`. Build owns the model json.
3. `spec` — the SpecBlock below.

## spec body

```
spec:
  item_type:   material | tool | weapon | armor | food | consumable | trinket | block_item
  model:       generated | handheld | custom_cube   # build writes the json; generated = flat sprite
  sprite:      <sprite grid ref>                     # 16x16 palette-index matrix (+ emissive layer)
  properties:
    max_stack: 64 | 16 | 1
    rarity:    common | uncommon | rare | epic
    durability:<int | none>
    fireproof: bool
  food:        { nutrition:<int>, saturation:<float>, always_edible:bool } | none
  attributes:  [ { attribute, amount, operation: add|mult_base|mult_total, slot } ]
  use_action:  none | right_click:<spell content_id> | activated:<spell content_id>
  tooltip:     [ "sentence case lines; show REAL magicule numbers, never native mana" ]
  economy_binding:                                   # the magicule item-adaptation hooks
    regen_flat:    <magicule_per_sec | none>         # the flat-regen LADDER; STACK-CAPPED
    cast_discount: { system: irons|ars|psi|mahou, pct:<int> } | none   # mod-specific, STACK-CAPPED
    capacity:      none                              # PROJECT RULE: no item raises the magicule pool
  recipe:      <datagen recipe ref | hint | none>
  creative_tab:<vanilla tab id | custom>
```

## Notes for the builder

- `generated` items need only the sprite + a one-line model json — usually `datagen_only`.
- A `trinket`/`armor` with `attributes` or `economy_binding` is `vanilla_codemodel` (a real Item
  subclass or an event handler reading the equipped stack each tick).
- `economy_binding` is the canonical home for the **item-adaptation backlog**: flat magicule/sec
  regen ladder, mod-specific cast discounts. Both STACK-CAPPED; capacity is never granted.
- `use_action`/`activated` that point at a `spell content_id` make the item a spell delivery — the
  spell lane owns the effect; the item just triggers it.

## Lane rejects

```
[ ] sprite uses a color off the declared palette
[ ] tooltip shows native mana/damage instead of the real magicule/boosted numbers
[ ] economy_binding raises capacity, or stacks uncapped
[ ] attribute item with no slot declared
[ ] recipe implied in prose instead of a datagen ref or explicit "none"
```

## verify menu

```
verify:
  - item appears in <creative_tab> with the rendered sprite (emissive cells glow)
  - tooltip reads the real magicule cost/effect
  - regen_flat adds <n> magicule/sec while held/worn, and stops at the stack cap
  - cast_discount lowers <system> cost by <pct>, capped with other discounts
```

## WORKED EXAMPLE — `cooling_ember_core`

```
type: item   content_id: cooling_ember_core   modid: isekai_beasts
display_name: "Cooling Ember Core"   build_target: vanilla_codemodel   host: tensura
spec:
  item_type: trinket
  model: generated
  sprite: cooling_ember_core_16   # charcoal sphere, ember-crack emissive cells (palette: charcoal/ember)
  properties: { max_stack: 1, rarity: rare, durability: none, fireproof: true }
  food: none
  attributes: []
  use_action: none
  tooltip:
    - "A cinderkit's heart, never fully cooled."
    - "Worn: +40 magicule/sec regeneration."
  economy_binding:
    regen_flat: 40           # one rung of the flat ladder; stack-capped across all regen trinkets
    cast_discount: none
    capacity: none
  recipe: none               # boss/rare drop, datagen loot
  creative_tab: tensura_items
verify:
  - worn in a curio/trinket slot, magicule regen rises by 40/sec
  - two cores do NOT stack past the regen cap
  - ember cells glow in inventory (emissive layer)
```

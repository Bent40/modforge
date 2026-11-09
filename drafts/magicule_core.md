# DRAFT — `magicule_core` (item lane, Chromeware implant)

*Draft 2026-11-09, not approved, nothing built. The design, numbers and open questions live in
isekai-chronicles `docs/cyborg-integration-design.md`. This is the first spec for an item that is an **implant
in another mod** (Create: Chromeware 1.2.1). The item lane has no `host: chromeware` and no implant block, so
this draft adds an `implant:` block and flags the gap below.*

```
type:          item
content_id:    magicule_core
modid:         isekai_cyborg            # new module; soft-depends chromeware + tensura
display_name:  "Magicule Core"
build_target:  vanilla_codemodel        # real Item subclass + player attachment + event handlers
host:          tensura                  # magicule effects; the implant side is Chromeware (see implant:)
spec:
  item_type:   trinket                  # closest lane type; it is installed, never worn
  model:       generated
  sprite:      magicule_core_16         # grid below
  properties:  { max_stack: 1, rarity: epic, durability: none, fireproof: true }
  food:        none
  attributes:  []
  use_action:  none                     # fallback install path only: right-click while seated in chromeware:surgery_chair
  implant:                              # NEW block (lane gap)
    host_mod:        chromeware
    section:         circulatory_system # replaces the heart
    humanity_cost:   8                  # % permanent; tune vs Chromeware's Second Heart (unverified value)
    capacity_cost:   "match Second Heart"   # unverified
    install:         "Chromeware surgery (Surgery Chair + Mechanical Arm) or the Ripperdoc role; fallback: own install if Chromeware implants are Java-only"
    registration:    "UNVERIFIED: datapack JSON vs Java registry; javap chromeware-1.2.1 first"
  tooltip:
    - "A heart of crystallised magicule in a brass cage."
    - "Installed: refunds 50% of the chrome magicule penalty."
    - "Banks up to +25% magicule above your max. Overflow bleeds 2%/s."
    - "Over max for 60 s: Magicule Burn."
  economy_binding:
    regen_flat:    none
    cast_discount: none
    capacity:      none                 # no permanent pool increase
    chrome_penalty_refund_pct: 50       # cyborg.core_offset_pct
    overcharge:                         # FLAG: first thing that lets magicule sit above max (Ben's 06-30 design)
      max_over_pct:   25                # cyborg.core_overcharge_pct (Cyborg race: 50); 0 disables
      bleed_pct_per_s: 2                # of the overflow
      overload_after_s: 60              # then Magicule Burn 10 s
  recipe: "create:sequenced_assembly — tensura magic ore crystal -> deploy brass sheet -> deploy precision mechanism -> fill 1000 mB magic fluid (or 4 magic ore if no fluid); 1 loop"
  creative_tab: isekai_cyborg
palette:
  - { id: 0, role: transparent,   hex: "#00000000", emissive: false }
  - { id: 1, role: brass_shade,   hex: "#7a5426",   emissive: false, note: "casing shadow" }
  - { id: 2, role: brass,         hex: "#b8862f",   emissive: false }
  - { id: 3, role: brass_light,   hex: "#e3c062",   emissive: false, note: "top highlight" }
  - { id: 4, role: crystal_dark,  hex: "#2e5a8c",   emissive: false }
  - { id: 5, role: crystal,       hex: "#4fa3d9",   emissive: true }
  - { id: 6, role: crystal_glow,  hex: "#bff2ff",   emissive: true,  note: "the one detail: glowing core" }
  - { id: 7, role: outline,       hex: "#2b1d14",   emissive: false }
sprite magicule_core_16:   # row 0 = top, col 0 = left
  - "0000000000000000"
  - "0000077777700000"
  - "0007722332277000"
  - "0072233333322700"
  - "0072217777122700"
  - "0722174554712270"
  - "0721745665471270"
  - "0721746666471270"
  - "0721746666471270"
  - "0721745665471270"
  - "0722174554712270"
  - "0072217777122700"
  - "0072233333322700"
  - "0007722112277000"
  - "0000077777700000"
  - "0000000000000000"
verify:
  - item shows in the isekai_cyborg tab; crystal cells glow in a dark room (emissive 5, 6)
  - "/chrome install @s circulatory_system 1 isekai_cyborg:magicule_core" (or the fallback install) succeeds; /humanity drops by 8
  - with 6 other implants, max magicule penalty halves after installing the Core (read via Tensura status)
  - regen past max stops at +25%; overflow decays ~2%/s; held over max 60 s -> Magicule Burn applied
  - with chromeware absent the jar loads and the Core is a plain item (no crash)
```

## Lane gaps this draft raises

1. **Implant host.** Items that live inside another mod's body-slot system need an `implant:` block
   (host mod, section, humanity/capacity cost, install path). Propose adding it to `lanes/item.md` once
   Chromeware's registration is verified.
2. **Above-max magicule.** `economy_binding.capacity: none` stays true, but `overcharge` is a new kind of
   binding. If Ben keeps it, the item lane needs a rule for it (temporary, bleeding, risk-capped).

## Sibling: `octo_spine_port` (built in isekai_cyborg 0.2.0, 2026-11-09)

Same envelope as the Core: `type: item`, `modid: isekai_cyborg`, `build_target: vanilla_codemodel`,
implant section `skeleton`, 43 capacity (0 for the Cyborg race), installed seated in `chromeware:surgery_chair`.
Gates the Octo Arms (tentaworks) Tentacle Rig via a mixin on `RigServer.process`. Recipe: Create sequenced
assembly, brass sheet -> precision mechanism -> 2 andesite alloy -> 1 magic ore shard. Palette = the Core's.

```
sprite octo_spine_port_16:   # row 0 = top
  - "0000000000000000"
  - "0000007777000000"
  - "0000072332700000"
  - "0000721111270000"
  - "0000077777700000"
  - "0000007227000000"
  - "0007777777777000"
  - "0072233663322700"
  - "0072211441122700"
  - "0007777777777000"
  - "0000007227000000"
  - "0000077777700000"
  - "0000721111270000"
  - "0000072332700000"
  - "0000007777000000"
  - "0000000000000000"
verify:
  - without the port, double-jump with a Tentacle Rig: no arms, action bar "Needs a spine port (Ripperdoc)"
  - with the port installed: arms deploy; backtank air drains as normal
```

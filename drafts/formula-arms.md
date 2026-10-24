# DRAFT — Formula Arms (`formula_arms`): Youjo Senki aerial-mage firearms on Psi

Status: **design draft, not built.** Requested by Ben 2026-10-24 ("magic in Youjo Senki as a class or a way of
tinkering… a flashy addon to Psi… psi rifles and shotguns and special pellets… a compat mod that carries not
just spells but skills"). This sheet is the recommendation plus the SpecBlocks a build session needs. Sprite
grids are deliberately left as `pending` until Ben approves the direction (then a mockup pass draws them).

---

## 1. The pitch in one paragraph

A Psi addon that turns **guns into casting vessels**, the way the Empire's aerial mages fight in *The Saga of
Tanya the Evil*. You program a formula in Psi's own Spell Programmer, socket it into a **formula rifle** or
**formula shotgun**, load a **round type** (ball, airburst, piercing, buckshot, formula buckshot, slug), and the
formula fires *with the bullet* and executes where the bullet lands. Your **computation orb** is your CAD: the
mass-produced **Type 97** is a solid upgrade; the experimental four-core **Type 95 Elinium** has absurd output,
eats magicule, only works after you **pray**, and slowly contaminates your mind. The orb also gives you the
aerial mage's signature: **flight**, paid for in magicule per second. Every cost is magicule (through the
existing Psi bridge), so this is Psi made louder, not a parallel magic system.

---

## 2. Source research (where each idea comes from)

Strength key: **[S]** primary/strong (Wikipedia citing the novels/anime), **[F]** fan wiki or fan analysis
(usually right, not authoritative), **[R]** my recall of the anime, not re-verified this session.

| Idea used here | What the source says | Source |
|---|---|---|
| Magic is military hardware | In Tanya's world (an alternate 1920s Imperial Germany) "magic has been incorporated into the military"; Tanya joins the Mage Corps | [S] [Wikipedia: The Saga of Tanya the Evil](https://en.wikipedia.org/wiki/The_Saga_of_Tanya_the_Evil) |
| Mages fly and shoot magic through guns | Tanya is "a mage with magical powers that enable her to fly and fire explosive bullets from guns" | [S] same |
| Formula-loaded bullets as standard practice | Ordinary mages "cast explosion spell on the bullets all the time" | [F] r/YoujoSenki discussion (search result, informal) |
| Optical formulas (sniping, decoys, heat beams) | Optical formulas are shot out by the caster; cover sniping, decoys, explosions; "straight heat beams" | [F] fan formula ranking (fandomwire) + r/respectthreads |
| Computation orb = the casting device | Type 95 is the first multi-core orb: **four cores** vs one, output multiplied, **mana consumption quadrupled** | [F] [Youjo Senki wiki: Computation Orb](https://youjo-senki.fandom.com/wiki/Operation_Orb) (via search; page fetch was blocked) |
| Type 97 is the mass-produced follow-up | Type 97 "Mobile Assault": **2 cores**, by Schugel, product version of the Type 95; same principle, "more stable and far inferior output"; lets soldiers run two formulas at once | [F] Youjo Senki wiki (Operation Orb, rev. 7455) |
| Only Tanya can use the Type 95, because of Being X | Tanya is "the only one capable of using an experimental Type-95 operation orb", attributed to Being X's interference | [S] Wikipedia |
| Being X and the prayer | A self-styled god reincarnated her to make her believe; Being X stabilised the orb mid-test as its cores were about to explode and told her praying each time would keep it safe | [S] Wikipedia (Being X); [F] Crow's World of Anime, episode 3 recap |
| Prayer gates the big spells | Tanya says a short prayer before powerful spells; the orb won't produce the needed power without it | [F] TV Tropes, Characters |
| The cost of prayer: mental contamination | Each use erodes her atheist persona, blackouts; gold eyes, boosted capacity and accuracy, a high-tier explosive formula while praying; a **rosary** keeps the corruption from becoming permanent | [F] TV Tropes + Youjo Senki wiki (Tanya page) |
| The 203rd: fast elite aerial battalion | "Elite mages whose main purpose is to overwhelm enemy forces" while mobile | [S] Wikipedia |
| Altitude as a power ladder | Standard mages hit a ceiling around 6,000 ft; the Type 95 test flight goes far above it | [R] anime episodes 1-2, not re-verified |
| Mana signatures give mages away | Enemy forces track mages by their mana signal | [R] anime, not re-verified |

Unit note: one fan page and Wikipedia disagree on 203rd vs 205th in places; it doesn't affect the design.

**What the lore gives the design:** guns are the casting vessel and the formula rides the bullet; the orb is the
engine; flight is the class identity; the Type 95 is a cursed relic whose power is paid for with faith. That last
part lines up neatly with the pack's own Divine System (gods want worship; Being X wants Tanya's faith).

---

## 3. What the real jars allow (verified with javap, 2026-10-24)

All checked against the jars in `Tensura\mods`: `Psi-neoforge-1.21.1-110.jar`, `magicule_standard-2.5.3.jar`,
`manascore-neoforge-4.0.0.2.jar` (skill sub-jar), `ars_nouveau-1.21.1-5.13.1.jar`,
`irons_spellbooks-1.21.1-3.16.3.jar`. (The pack's docs still say Psi 108; the installed jar is 110.)

### Psi 110
- **CAD components are data-driven.** `CADComponentLookup.holder()` looks up a datapack registry
  (`psi:cad_component`) **keyed by the item's registry id**. Psi's own are JSON, e.g.
  `data/psi/psi/cad_component/cad_assembly_ebony_psimetal.json` =
  `{"type":"assembly","model":"psi:item/cad_ebony_psimetal","stats":{"efficiency":90,"potency":350}}`.
  So a computation orb assembly is **our item + one JSON** at `data/formula_arms/psi/cad_component/<item>.json`.
  Built-in assembly stats: iron 70/100, gold 75/175, psimetal 85/250, ebony 90/350, ivory 95/320, creative −1/−1.
  Cores give complexity/projection, sockets give bandwidth/sockets, batteries give overflow.
- **Casting entry point is public:** `ItemCAD.cast(Level, Player, PlayerData, ItemStack bullet, ItemStack cad,
  int cooldown, int particles, float sound, Consumer<SpellContext>)` (static). It checks `overflowed`/available
  psi, compiles the bullet's spell, posts `PreSpellCastEvent` (cost/cooldown are settable) on `PsiEvents`, calls
  `PlayerData.deductPsi(cost, cd, sync)`, then the bullet's `ISpellAcceptor.castSpell(context)`.
- **Bullets carry their delivery.** `ISpellAcceptor` has `castSpell`, `getCostModifier`, `castableFromSocket`.
  Verified cost modifiers: basic 1.0, projectile **1.02**, grenade **1.05**, charge **1.151**, mine **1.151**,
  circle **15.0**. Real cost also scales by the CAD's Efficiency stat (`ItemCAD.getRealCost`; −1 = free).
- **Psi's projectile is subclassable.** `EntitySpellProjectile extends ThrowableProjectile` is public, with a
  protected `(EntityType, Level, LivingEntity)` constructor, public `context`, `setInfo(player, cad, bullet)`,
  `cast()`, overridable `onHit` and `getDefaultGravity()`. A formula round is a subclass with rifle ballistics.
- **Sockets:** `ISocketable` (bullet in socket, selected slot, radial-menu slots/icons, `isItemValid`,
  `canLoopcast`). Psimetal tools use it; a gun can too, so Psi's own radial menu switches formulas.
- **New tricks** register into `PsiAPI.SPELL_PIECE_REGISTRY` with `SpellPieceType.ofClass(...)`; trick base
  class is `vazkii.psi.api.spell.piece.PieceTrick`. Unlock progression is data (`psi/spell_piece_group/*.json`).
- **Psi 110 moved its cast events to its own bus** (`PsiEvents.register`), already handled in magicule_standard
  2.5.3's `PsiMasteryHandler`.

### The magicule bridge (and a bug found while checking)
- Design intent (source): `PsiPlayerDataMixin` cancels Psi's `deductPsi(IIZZ)` and charges **5 magicule per psi**
  (`psiRate`), paying down to a safe floor and burning the shortfall as armor-piercing `psi:psi_overload`
  damage plus Psi's native overflow lockout.
- **Bug: that mixin does not apply on Psi 110.** It targets
  `vazkii.psi.common.core.handler.PlayerDataHandler$PlayerData`; Psi 110 moved the class to
  `vazkii.psi.common.core.handler.PlayerData` (same `deductPsi(IIZZ)V`, `overflowed`, `regenCooldown`,
  `loopcasting`; `playerWR` is no longer final). All three `latest.log`s (Tensura, TestServer, Tensura Testing)
  show `@Mixin target …PlayerDataHandler$PlayerData was not found … PsiPlayerDataMixin` as a WARN. Today Psi
  casts drain Psi's own battery and cost **no magicule**. Formula Arms depends on this being fixed first
  (reported to the project for a magicule_standard 2.5.4 fix).
- Psi mastery (`psi.psionics`) scales damage only inside the synchronous cast window
  (PreSpellCast → SpellCast). A round that executes its formula ticks later is **outside** that window, exactly
  like Psi's own projectile bullets. The build must open the mastery window around the round's `cast()`.

### Other carriers (for Ben's "skills too" idea)
- **Tensura skills** (manascore `ManasSkill` / `ManasSkillInstance`): `onPressed(LivingEntity, keyNumber, mode)`,
  `onHeld`, `onRelease`, `canInteractSkill`, cooldown get/set. `onProjectileHit` exists but fires when the skill
  holder is **hit** by a projectile (defensive), not when they shoot one. Skills pay their own magicule and run
  from the **caster's** eyes, so a gun can trigger a skill the shooter owns at the moment of firing, but it can't
  generically make the skill go off where the bullet lands.
- **Ars Nouveau**: `SpellResolver.onResolveEffect(Level, HitResult)` resolves a glyph chain **at a hit result**,
  and `SpellContext(Level, Spell, LivingEntity, IWrappedCaster[, ItemStack])` is public. That's a true
  impact-point carrier. Our bridge charges Ars through `LivingCaster.enoughMana/expendMana`; a direct resolve
  skips that, so the carrier must charge magicule itself (Ars rate ×25).
- **Iron's Spellbooks**: `AbstractSpell.onCast(Level, int level, LivingEntity, CastSource, MagicData)`, and
  `CastSource` already has a **`SWORD`** value (Iron's imbued weapons), so "spell on a weapon" is native to Iron's.
  Casting runs from the caster, not the impact. Our bridge charges Iron's in `canBeCastedBy`; a direct
  `onCast` skips it, so the carrier charges magicule itself (×50).
- **Mahou Tsukai**: the bridge only hooks `PlayerManaManager.drainMana` and `EffectUtil.genericAttack`; I found
  no clean "cast this effect at a point" API. Parked.

---

## 4. The recommendation

**Build a Psi-only P1, but give it one small internal seam, `FormulaPayload`, so other carriers plug in later
without a rewrite.** Don't build the multi-system carrier up front: only Psi (and Ars) can run *at the impact
point*, every other carrier needs per-system cost charging, and the Psi bridge itself is currently broken. One
payload implementation in P1 costs almost nothing extra and keeps the door open.

```
// design seam only — not code to ship as-is
interface FormulaPayload {
  ResourceLocation id();                              // formula_arms:psi_spell, :ars_glyphs, :irons_spell, :tensura_skill
  boolean onFire(ServerPlayer shooter, ItemStack gun, FormulaRound round); // false = misfire, nothing spent
  void    onImpact(FormulaRound round, HitResult hit);                     // impact-point payloads
  double  magiculePerCast(ServerPlayer shooter);      // tooltip_truth: what one cast REALLY costs
}
```

| Phase | Carrier | Where it goes off | Who charges magicule | Verdict |
|---|---|---|---|---|
| **P1** | Psi spell (socketed spell bullet) | Impact point (round = focal point) | Psi path → magicule bridge (×5) | **Build first** |
| P2 | Ars glyph chain (from a spell parchment) | Impact point (`onResolveEffect`) | Carrier, ×25, Ars mastery lane | Good fit, prototype first |
| P2 | Iron's spell (from a scroll, `CastSource.SWORD`) | Shooter, at the moment of firing | Carrier, ×50, Iron's mastery lane | Works; it's a "spell-assisted shot" |
| P3 | Tensura skill the shooter owns | Shooter, at the moment of firing | The skill itself (native) | Curated allowlist only, verified per skill |
| — | Mahou Tsukai | — | — | Parked, no clean API |

Lore check: the Empire's mages imbue *formulas* into rounds; skills aren't formulas. That's why Tensura skills
come last and only as an allowlist. Ben's skill-carrying idea is fun, but it's a stretch on the source.

---

## 5. How the pieces map

| Youjo Senki | Psi concept | Formula Arms item |
|---|---|---|
| Computation orb | CAD **assembly** (sets efficiency/potency, the CAD model) | `type_97_orb`, `type_95_elinium_orb` |
| Orb cores | CAD core (complexity) | reuse Psi's cores; Type 95's 4 cores are flavour in its stats |
| A formula | A programmed Psi spell in a spell bullet | Psi's own spell bullet (basic type), programmed as usual |
| Rifle/shotgun as casting vessel | `ISocketable` item + a custom `ISpellAcceptor` for delivery | `formula_rifle`, `formula_shotgun` |
| Imbued round | Custom projectile subclassing `EntitySpellProjectile` | `formula_round` entity |
| Round types | Delivery modifier, like Psi's bullet types | `ball_round`, `airburst_round`, `piercing_round`, `buckshot_shell`, `formula_buckshot_shell`, `slug_shell` |
| Flight | Orb-granted flight, magicule per second | flight formula (event handler) |
| Prayer + Being X | A pray action that unlocks the Type 95 for a window | `pray` use-action + `mental_contamination` effect |
| Rosary | Trinket that slows contamination | `field_rosary` |

### How a shot works (P1)
1. The gun holds formulas in its sockets (rifle 4, shotgun 2). Only **basic** spell bullets fit; projectile,
   circle, mine etc. are refused (`isItemValid`), because the round *is* the delivery.
2. On fire, the gun builds a transient acceptor for the loaded round type, copies the selected formula into it,
   and calls `ItemCAD.cast(...)` with the player's CAD (the orb). Psi compiles it, checks CAD limits, and charges
   once **at the moment of firing** (so misses still cost, like real ammunition), applying the round type's cost
   modifier. The bridge turns that into magicule.
3. The acceptor's `castSpell` spawns `formula_round` (subclass of `EntitySpellProjectile`) with the gun's
   ballistics and the round's behaviour.
4. On impact, the round becomes the focal point and runs the compiled spell, inside a mastery window.
5. No orb (no CAD) in the inventory = the gun only fires physical rounds, no formula.

---

## 6. SpecBlocks

### 6.1 `formula_rifle`

```
type: item   content_id: formula_rifle   modid: formula_arms
display_name: "Formula Rifle"   build_target: vanilla_codemodel   host: psi
spec:
  item_type: weapon
  model: custom_cube            # long-gun silhouette, rotated cuboids; muzzle at most-negative Z in hand frame
  sprite: pending               # palette-index grid after Ben approves direction
  palette:
    - { token: w, id: walnut_stock,   hex: "#5a3a22", layer: base }
    - { token: g, id: gunmetal,       hex: "#3b3f46", layer: base }
    - { token: s, id: steel_edge,     hex: "#8a9099", layer: base }
    - { token: b, id: brass_fitting,  hex: "#b08d3c", layer: base }
    - { token: F, id: formula_glow,   hex: "#7fd8ff", layer: emissive, note: "socket rune; recolours to CAD spell colour" }
  properties: { max_stack: 1, rarity: rare, durability: 900, fireproof: false }
  attributes: [ { attribute: attack_damage, amount: 3, operation: add, slot: mainhand } ]  # bayonet butt-stroke
  sockets: 4                    # ISocketable; Psi radial menu picks the active formula
  accepts_rounds: [ ball_round, airburst_round, piercing_round ]
  ballistics: { velocity: 5.0, gravity: 0.005, inaccuracy_deg: 0.25, lifetime_ticks: 60 }   # ~300 blocks
  fire_cooldown_ticks: 16
  physical_damage: 6            # the bullet itself, with or without a formula
  use_action: right_click:formula_round
  tooltip:
    - "Fires formula-imbued rounds. Load spell bullets into its sockets."
    - "Each shot costs the formula's magicule (shown per socket)."
  economy_binding: { regen_flat: none, cast_discount: none, capacity: none }
  recipe: hint  "iron + gunpowder + psimetal + a CAD socket"   # datagen ref at build
  creative_tab: formula_arms
verify:
  - with a CAD and a programmed bullet socketed, right-click fires a round; the formula runs where it lands
  - magicule drops by (spell cost / efficiency x round modifier x 5) per shot; nothing drains Psi's own bar
  - broke: the burnout (psi_overload damage + lockout) fires, same as a normal Psi overcast
  - no CAD in inventory: the round still does 6 physical damage, no formula, no magicule spent
  - projectile and circle bullets cannot be socketed
```

### 6.2 `formula_shotgun`

```
type: item   content_id: formula_shotgun   modid: formula_arms
display_name: "Formula Shotgun"   build_target: vanilla_codemodel   host: psi
spec:
  item_type: weapon
  model: custom_cube
  sprite: pending
  palette: (shares formula_rifle roles)
  properties: { max_stack: 1, rarity: rare, durability: 600, fireproof: false }
  sockets: 2
  accepts_rounds: [ buckshot_shell, formula_buckshot_shell, slug_shell ]
  ballistics: { velocity: 2.5, gravity: 0.03, inaccuracy_deg: 7.5, lifetime_ticks: 12 }      # ~30 blocks
  pellets: 6                    # buckshot loads only; slug = 1
  fire_cooldown_ticks: 24
  physical_damage: { per_pellet: 3, slug: 10, slug_knockback: 1.5 }
  use_action: right_click:formula_round
  tooltip:
    - "Close-range formula delivery. Shell type decides how the formula spreads."
  economy_binding: { regen_flat: none, cast_discount: none, capacity: none }
  recipe: hint  "iron + gunpowder + psimetal + a CAD socket"
  creative_tab: formula_arms
verify:
  - buckshot: 6 pellets, physical damage each, the formula runs ONCE on the first pellet that hits
  - formula buckshot: every pellet that hits runs the formula; magicule is charged per pellet cast
  - slug: one heavy round with knockback; the formula runs at impact
```

### 6.3 Round types (the "special pellets")

Consumable, stack 64, cheap to craft (iron nugget + gunpowder + a pinch of magic crystal). They carry **no
magicule**; the formula's magicule is the only cost. (`consume_rounds` is a config toggle; off = infinite.)

| content_id | Gun | Behaviour | Formula runs | Cost modifier (vs Psi's spell cost) |
|---|---|---|---|---|
| `ball_round` | rifle | Plain imbued bullet | Once, at impact | **1.02** (same as Psi's projectile bullet) |
| `airburst_round` | rifle | Bursts after a fuse distance (default 24 blocks; sneak + scroll sets 8 to 64) or on impact, whichever first. The artillery-mage round | Once, at the burst point | **1.05** (same as Psi's grenade) |
| `piercing_round` | rifle | Passes through up to 3 entities | At each entity hit | **1.02 per cast**, extra casts charged as they happen |
| `buckshot_shell` | shotgun | 6 pellets, physical | Once, first pellet hit | **1.05** |
| `formula_buckshot_shell` | shotgun | 6 pellets | At every pellet that hits | **1.0 per pellet cast**; up to 6 casts. The "really crazy" round |
| `slug_shell` | shotgun | 1 heavy round, knockback | Once, at impact | **1.02** |

Extra casts (piercing, formula buckshot) charge through `PlayerData.deductPsi` as each one happens, so the bridge
bills them like any Psi spend and the burnout rule still applies mid-volley.

### 6.4 `formula_round` (entity)

```
type: entity   content_id: formula_round   modid: formula_arms
display_name: "Formula Round"   build_target: vanilla_codemodel   host: psi
spec:
  base_class: vazkii.psi.common.entity.EntitySpellProjectile   # protected (EntityType, Level, LivingEntity) ctor
  axes: { forward: -Z, up: +Y, right: +X }
  model: billboard              # tracer streak, no cuboid model
  hitbox: 0.15 x 0.15
  lifetime: per gun ballistics (lifetime_ticks)
  behaviour: none (projectile, no AI)
  render:
    tracer: { shape: billboard, length_px: 6, colour: cad_spell_colour, emissive: true }
    trail_particles: { type: psi spark, rate: 1/tick, colour: cad_spell_colour }
  on_hit: set focal point to self -> open psi mastery window -> context.cspell.safeExecute -> close window
verify:
  - a formula round that hits a mob runs e.g. "Explode" at the mob, not at the shooter
  - psi.psionics mastery rises and its damage scaling applies to the round's formula
  - the round despawns after its lifetime; no block grief unless the formula itself breaks blocks
```

### 6.5 Computation orbs (CAD assemblies)

Both are items with a `psi:cad_component` JSON; the CAD's model becomes the orb (a pendant-style gem on a chain,
held in the off hand). Numbers chosen against Psi's own ladder (ebony 90/350 is the best normal assembly).

```
type: item   content_id: type_97_orb   modid: formula_arms
display_name: "Elinium Type 97 Computation Orb"   build_target: datagen_only   host: psi
spec:
  item_type: material            # a CAD assembly
  cad_component: { type: assembly, model: "formula_arms:item/cad_type_97", stats: { efficiency: 88, potency: 300 } }
  grants_flight: { tier: 1 }     # see 6.6
  tooltip: [ "Two-core mass-production orb. Stable, dependable, unremarkable." ]
  recipe: hint "psimetal assembly + 2 magic crystals + a computation core; questbook Mage Corps chapter"
verify:
  - assembles into a CAD in Psi's CAD assembler; CAD tooltip shows efficiency 88, potency 300
```

```
type: item   content_id: type_95_elinium_orb   modid: formula_arms
display_name: "Elinium Type 95 Computation Orb"   build_target: vanilla_codemodel   host: psi
spec:
  item_type: material            # a CAD assembly with behaviour
  cad_component: { type: assembly, model: "formula_arms:item/cad_type_95", stats: { efficiency: 50, potency: 800 } }
  # efficiency 50 = every formula costs 2x (lore says 4x; 2x keeps it usable, tunable to 25 for 4x)
  # potency 800 = more than twice ebony: spells no other CAD can compile
  prayer_gate:
    applies_when: "spell potency > 350 (beyond any normal CAD)"   # small spells work without praying
    pray_action: "sneak + use the orb CAD, 3 s channel"
    prayed_window_s: 60
    unprayed_result: "cast refused with a red message (PreSpellCastEvent cancel), no cost"
  mental_contamination:          # mob effect, stacks 0..100
    gain_per_overclocked_cast: 4
    decay_per_minute: 2
    thresholds:
      - { at: 25, effect: "gold eyes: +10% projectile accuracy, Haste I while prayed" }
      - { at: 60, effect: "involuntary prayer lines in chat when casting (flavour)" }
      - { at: 90, effect: "Nausea pulses; the orb casts at efficiency 40 until it decays below 60" }
  grants_flight: { tier: 2 }
  tooltip:
    - "Four-core experimental orb. Unstable without divine assistance."
    - "Pray before overclocked formulas. Faith has a price."
  recipe: none                   # unique relic: boss drop / questbook reward, one per player
verify:
  - a potency-500 spell compiles on this CAD and on no other assembly
  - without praying, that spell is refused at no cost; after praying it fires for 60 s
  - each overclocked cast adds 4 contamination; thresholds apply in order and decay over time
```

```
type: item   content_id: field_rosary   modid: formula_arms
display_name: "Field Rosary"   build_target: vanilla_codemodel   host: psi
spec:
  item_type: trinket            # curio slot
  effect: "halves mental_contamination gain; contamination cannot pass 89 while worn"
  economy_binding: { regen_flat: none, cast_discount: none, capacity: none }
verify:
  - worn rosary: overclocked casts add 2 contamination, and it stops at 89
```

### 6.6 Flight formula (the class identity)

```
type: spell   content_id: flight_formula   modid: formula_arms
display_name: "Flight Formula"   build_target: event_handler   host: none
spec:
  host: none   cast_type: self_buff
  trigger: "double-jump while an orb CAD is in your inventory; double-jump again or land to stop"
  mechanism: "NeoForge creative-flight attribute while active (verify the attribute id in the 21.1 jar before building)"
  cost: { magicule_per_second: { tier_1: 25, tier_2: 60 } }      # charged through the same floored spend as Psi
  speed: { tier_1: 0.08, tier_2: 0.13 }                          # vanilla creative is 0.05
  ceiling_y: { tier_1: 200, tier_2: 320 }                        # altitude ladder from the source
  broke: "flight ends, slow-falling 5 s (no burnout death from flying)"
  mana_signature: "optional: Glowing for 3 s after any formula shot over 2000 magicule (config, default off)"
  integration: { magicule_cost: via formula_arms floored spend, mastery_lane: psi:psionics, tooltip_truth: true }
verify:
  - with a Type 97 CAD, double-jump starts flight; magicule drops 25/s; it stops at Y 200
  - running out of magicule ends flight with slow-falling, not damage
  - races that already fly natively are unaffected (no double drain)
```

---

## 7. How it fits the pack

- **Pillar 1, one currency:** every formula, extra pellet cast and second of flight is magicule. Rounds are
  cheap materials, not a second currency. **Blocked until the Psi bridge fix lands.**
- **Pillar 2, curated whole:** it's Psi with a new delivery layer and a new CAD tier. Players still program in
  Psi's Spell Programmer, use Psi's radial menu, and grow Psi mastery. P2 lets Ars and Iron's spells ride the
  same guns.
- **Pillar 3, custom content:** two guns, six round types, two orbs, a rosary, flight, the prayer mechanic.
- **Pillar 4, faithful power fantasy:** guns as casting vessels, orbs as engines, flight and altitude, the Type 95
  as a cursed relic paid for in faith.
- **Race and skill system:** the aerial mage is a **gear-based class open to every race** (a slime with a rifle is
  very on-brand for this pack). Progression gates are Psi mastery (`psi.psionics`) and a questbook chapter, "Mage
  Corps", that hands out the Type 97 recipe. No new race.
- **Divine System hook (Phase 5):** once the Divine Crest exists, praying on the Type 95 goes **to a god whose
  domain you're in**: that god gains Divinity from each prayer (Being X gets the faith it wanted), and a blessed
  player gets a shorter prayer channel. Until then, prayer is the standalone 3 s channel above.
- **Magicule Forge:** not the home for orbs. Orbs are CAD parts and belong in Psi's assembler. A later Forge tier
  could "overclock" a Type 97 into a one-off Type 95 replica at a gamble, but that's optional.

### Roadmap slot
Phase 6 expansion window ("Formula Arms"), with two things that should happen sooner:
1. **Now:** the Psi bridge fix (magicule_standard 2.5.4). It's a bug, not a feature, and pillar 1 is broken for
   Psi until it lands.
2. **P1 can be pulled forward as a palate cleanser** between tentpoles: it doesn't need the kingdom side-car or
   any custom screen (Psi's programmer and radial menu are the UI).
3. The Type 95's prayer-to-a-god link waits for **Phase 5** (Divine Crest).

### Build phases
- **P1:** formula rifle + shotgun, 6 round types, `formula_round`, Type 97 orb, flight formula, the
  `FormulaPayload` seam with the Psi payload. Itest: a scripted fake player fires each round type at a dummy and
  asserts magicule spent, formula ran at the impact point, mastery rose.
- **P2:** Type 95 Elinium + prayer + contamination + rosary; Ars and Iron's payloads.
- **P3:** Tensura skill payload (allowlist); Divine Crest prayer link (after roadmap Phase 5).

---

## 8. Tunable numbers (all config)

| Knob | Default | Notes |
|---|---|---|
| `psiRate` (existing bridge) | 5 magicule/psi | shared with all Psi |
| Round cost modifiers | ball/slug 1.02, airburst/buckshot 1.05, piercing & formula buckshot 1.0 per cast | Psi's own bullets as anchors |
| Rifle | 4 sockets, velocity 5.0, cooldown 16 t, 6 physical | |
| Shotgun | 2 sockets, 6 pellets, 7.5 deg spread, cooldown 24 t, 3/pellet, slug 10 | |
| Airburst fuse | 24 blocks (8 to 64) | |
| Type 97 | efficiency 88, potency 300 | between psimetal and ebony |
| Type 95 | efficiency 50, potency 800 | efficiency 25 = the lore's 4x cost |
| Prayer | potency > 350 needs it; 3 s channel; 60 s window | |
| Contamination | +4 per overclocked cast, -2/min, thresholds 25/60/90 | rosary halves gain, caps at 89 |
| Flight | 25 / 60 magicule/s; speed 0.08 / 0.13; ceiling Y 200 / 320 | |
| `consume_rounds` | true | false = infinite rounds |
| Mana signature | off | Glowing after big shots |

## 9. Decisions for Ben

1. **Psi-only first with a payload seam (recommended), or the full carrier up front?** Recommended: Psi first.
2. **Consumable rounds (recommended) or infinite rounds?** Rounds make "special pellets" a real choice.
3. **Type 95 cost: 2x (recommended, playable) or the lore's 4x?**
4. **Flight from the orb (recommended), or leave flight to races and Psi's own motion tricks?**
5. **Slot it as Phase 6 with P1 pullable forward (recommended), or earlier?**

## 10. Open checks before building

- Fix and re-verify the Psi bridge on Psi 110 (an itest that asserts a Psi cast lowers magicule).
- Confirm the NeoForge creative-flight attribute id in the 21.1.248 jar.
- Confirm Psi's CAD assembler accepts a third-party assembly with only the JSON + an `ICADComponent` item
  (the lookup is by item id; the assembler's slot check wasn't read).
- Read `EntitySpellProjectile.onHit/cast` bytecode before subclassing (only signatures were checked).
- Prototype Ars `onResolveEffect` with a carrier-built `SpellContext` before promising P2.

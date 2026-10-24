# DRAFT — `presence_detection` (spell lane, Tensura skill + screen)

*Draft 2026-10-24 (v2 after Ben's feedback: renamed from sense_index, unlock confirmed, concealment by type, things
in general). Awaiting mockup approval; nothing built. Full design, javap evidence and tunables: isekai-chronicles
`docs/presence-detection-design.md`; mockups `docs/ui/presence-detection/`.*

This is the first spec for a **Tensura-hosted skill** (`host: tensura`) and the first to carry a screen. The
spell lane has no `host: tensura` row and there is no `gui` lane yet, so this draft uses the spell lane's shape,
records the screen in a `gui:` block shaped like the `lanes/gui.md` proposal in the isekai-chronicles UI style
guide, and flags both gaps below.

```
type:          spell
content_id:    presence_detection
modid:         mahoumagicule            # registry namespace of magicule_standard's skills (save-compat)
display_name:  "Presence Detection"
build_target:  event_handler            # skill class + payloads + client screen/mixin; no model
host:          tensura
spec:
  host:       tensura                   # extends io.github.manasmods.tensura.ability.skill.Skill, Skill.SkillType.EXTRA
  school:     sense                     # Tensura sense family (Magic Sense, Heat Source, Soundwave, Universal Perception)
  cast_type:  self_buff                 # press = open list; tracking = sustained
  levels:     { max: 500, scaling: "mastery: radius +0..+20 blocks, costs -0..-50%" }
  acquire:    "auto-learn when tensura:magic_sense is mastered (poll every 100 ticks)"   # Ben confirmed
  cost:
    base_mana: none                     # Tensura-native: costs are magicule directly
    magicule:
      open:   100                       # = Search Enemy cast
      open_upkeep:  "25 per 5 s"        # = Magic Sense upkeep
      track_upkeep: "25 per 5 s"
      things_scan:  50                  # once per open, block scan
  cast_time:  0
  cooldown:   0
  target:     aoe<presence_sense_radius + mastery bonus>     # 30 base, 50 with Universal Perception
  channels:                              # level 0-4, highest source wins; own mastery adds up to +1 to channels you have
    magic:  { from: "tensura:presence_sense (Magic Sense mastered 1, Observer/All-seeing +1, Universal Perception 3, Heavenly Eye 4)", finds: "all living; magic blocks, spawners" }
    intent: { from: "Danger Sense 1 (2 mastered), Search Enemy active 2, Observer hostile mode 3", finds: "hostile toward you; +2 while targeting you" }
    heat:   { from: "Sense Heat Source 2 (3 mastered), Universal Perception 3", finds: "warm-blooded, heat blocks; not #cold_blooded/#no_blood; off in ultraWarm" }
    sound:  { from: "Sense Soundwave 2 (3 mastered), Universal Perception 3", finds: "not silent, not canBlockSoundDetect; sneaking -1" }
  concealment:                           # by type: what each blocks
    magic:     { source: "tensura:presence_concealment value = level (real: mask 0.5, most skills 1-3, Shadow Motion 5, Snatch/Ban 11)", blocks: magic, leak: "0.5 x level vs intent/heat; sound fully blocked at >= 2 (Tensura canBlockSoundDetect)" }
    cold_body: { source: "#tensura:cold_blooded, #tensura:no_blood (incl. undead, slimes, arthropods), cold-blooded race", blocks: heat }
    silence:   { source: "silent, canBlockSoundDetect", blocks: sound }
    invisible: { counts_as: "+1 magic concealment" }
  reveal:                                # per channel
    power:  "level + 2 x log10(yourMaxEP / theirMaxEP)"
    found:  "power > concealment on that channel (strict, like Tensura S > C; unconcealed: no EP check)"
    margin: "best(power - needed) + 0.5 per extra channel"
    read:   "margin >= 1 full entry; 0..1 'Faint presence' (vague category, distance to 5 m, chip only)"
  things:                                # Beings / Things filter
    radius: "16 (+8 mastery), grouped same-type within 4 blocks"
    spawners: { by: magic, cat: trap }
    traps:     { by: "magic >= 2 or Observer", source: "Tensura trap blocks, #trap_entity", cat: trap }
    treasures: { by: "magic >= 2 or Observer", source: "Tensura treasure blocks, chests, #c:ores, #treasure_entity", cat: treasure }
    heat_blocks: { by: heat, source: "Tensura heat-source blocks", cat: heat_source }
    track: "box outline through walls (own client render pass) + HUD chip"
  readout:
    ep: "exact if viewer analysis_level > 0 and within analysis_distance, else band weaker|similar|stronger|far above you"
    unknown: "target maxEP >= 10 x viewer maxEP -> 'Unknown presence', no name"
  importance:                            # score = weight + 100*clamp(log10(theirEP/yourEP),-2,2) + 150 if named; ties -> nearer
    boss: 1000   unknown: 900   hunting_you: 800   player: 500   hostile: 400
    faint: 350   trap: 350   treasure: 250   neutral: 100   heat_block: 20   passive: 0   own_subordinate: -100
  effect:
    damage:   none
    aoe:      none
    knockback: none
    status:   []
    no_grief: true
  vfx:
    palette:  [ gold, bad_dk, warn_dk, ok_dk, mag_2, unknown_dk ]   # glow outline per category (ui-style-guide roles)
    particles: []
    geometry:
      - { shape: outline, size: "entity silhouette", texture: none, emissive: true, layer: vanilla_outline }  # @ModifyReturnValue getGlowColor, priority 1500 (after mysticism / tr_unique_monsters / trnightmare); bypasses concealment's early -1 for revealed targets
    keyframes: [ {t:0,"list opens"}, {t:"double-click","tracked entity glows; HUD chip shows name, distance, arrow"} ]
    sounds:   [ {t:0, ui.button.click} ]
  integration:
    magicule_cost: via mahoumagicule     # EnergyHelper.isOutOfEnergy on open + skill onTick upkeep
    mastery_lane:  none                  # own skill mastery (Tensura passive cadence), not a damage lane
    damage_scaling: none
    immune_tag:    tensura:immune_to_spell_boost   # also counts as "boss" for importance
    tooltip_truth: true
  gui:                                   # proposed lanes/gui.md shape
    voice:   vanilla_frame               # HUD chip uses the System voice
    size:    { w: 248, h: 210, min_gui: [320, 240] }
    regions:
      - { id: title,  rect: [8, 6, _, 8],      widget: label,  role: text_dark, text: "Presence Detection" }
      - { id: count,  rect: [right-8, 6, _, 8], widget: label, role: text_muted, text: "<n> found - <r> m" }
      - { id: search, rect: [7, 18, 96, 20],   widget: edit_box, sprite: widget/text_field, icon: icon/search }
      - { id: show,   rect: [105, 18, 52, 20], widget: cycle_button, values: [All, Beings, Things] }
      - { id: sort,   rect: [159, 18, 82, 20], widget: cycle_button, values: [Importance, Distance] }
      - { id: list,   rect: [7, 40, 234, 141], widget: well + rows, row: { h: 21, pitch: 23, visible: 6 } }
      - { id: hint,   rect: [8, 189, _, 8],    widget: label, role: text_muted, text: "Double-click to track" }
      - { id: track,  rect: [157, 183, 84, 20], widget: button, text: "Track | Stop tracking" }
    row: [ portrait_viewport 18x18 (live entity render / block item), name (fit 112) + veil marker if concealed,
           dot|crown + category word, 4 channel pips (magic diamond mag_3, intent ! bad, heat flame warn, sound waves ok),
           distance + 8-way arrow (relative to facing), EP or band ]
    hud_chip: { voice: system, anchor: "centre, bottom edge = action bar line - 10", h: 13,
                content: [ eye glyph (gold), name (sys_text), distance (white), arrow (sys_edge) ] }
    data:    [ { field: snapshot, source: "server scan", sync: s2c_payload, refresh_ticks: 20, max_rows: 64 },
               { field: tracked_pos, source: server, sync: s2c_payload, every: 20 } ]
    actions: [ { id: track, calls: "c2s TrackPayload(entityId)" }, { id: stop, calls: "c2s TrackPayload(-1)" } ]
    states:  [ default, hover_tooltip, concealed_revealed, faint, things, tracking, search, sorted_distance, empty, scale2, scale4, min_320x240 ]
    open:    { keybind: "skill slot key", stop: "sneak + skill key" }
  icon: |                                # 16x16 skill glyph grid (upscale x8 to the 128x128 skill icon)
    roles: . clear, o mag_lo (outline), 1 mag_4, 2 mag_2, 3 mag_1, h mag_hi
    ................
    ......oooo......
    ....oo2222oo....
    ...o23333332o...
    ..o2331111332o..
    .o2331oooo1332o.
    o23310hh1o01332o   <- draft; finalise as a proper palette grid with the build
    .o2331oooo1332o.
    ..o2331111332o..
    ...o23333332o...
    ....oo2222oo....
    ......oooo......
verify:
  - mastering tensura:magic_sense learns mahoumagicule:presence_detection exactly once
  - pressing it costs 100 magicule and opens the list; 25 per 5 s while open; out of magicule closes it
  - unconcealed zombie at 20 blocks listed; presence_concealment 2 at equal EP: missed by Magic 1, found by Heat 2; at 10x your EP found by Magic 1
  - cold silent concealed mob found only via Magic with enough EP; heat channel absent in the Nether
  - diamond ore listed at Magic 2 not Magic 1; three adjacent ores = one row; tracking a block draws its outline
  - a mob targeting the player ranks above a stronger idle hostile; own subordinates sort last
  - double-click tracks: glow outline + HUD chip with live distance; 25 per 5 s; "Lost the trail" after 10 s out of range
  - in-game screenshot matches docs/ui/presence-detection mockups at GUI scale 3 and fits 320x240
  - javap: common classes have no net/minecraft/client refs; one active magicule_standard jar
```

## Gaps this draft exposes in Modforge

1. **`host: tensura` has no spell-lane row.** Proposed: Tensura-native skills cost magicule directly
   (`base_mana: none`), charge through `EnergyHelper.isOutOfEnergy`, and use skill mastery instead of a damage lane.
2. **No `gui` lane yet.** The `gui:` block above follows the proposal in the UI style guide (isekai-chronicles PR #2).
   If Ben approves that lane, this block moves into a `type: gui` companion spec with the same `content_id`.

## Ben's open calls

- Approve the mockup (or one-line tweaks).
- Ben confirmed (2026-10-24): unlock on Magic Sense mastered; name Presence Detection; concealment by type with the
  EP gap deciding reveals; detect things in general.
- Still open: ep_weight 2 (10x EP = +2 levels), ores/chests needing Magic level 2.

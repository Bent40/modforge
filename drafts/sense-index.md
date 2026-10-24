# DRAFT — `sense_index` (spell lane, Tensura skill + screen)

*Draft 2026-10-24, awaiting Ben's mockup approval; nothing built. Full design, javap evidence and tunables:
isekai-chronicles `docs/sense-index-design.md`; mockups `docs/ui/sense-index/`.*

This is the first spec for a **Tensura-hosted skill** (`host: tensura`) and the first to carry a screen. The
spell lane has no `host: tensura` row and there is no `gui` lane yet, so this draft uses the spell lane's shape,
records the screen in a `gui:` block shaped like the `lanes/gui.md` proposal in the isekai-chronicles UI style
guide, and flags both gaps below.

```
type:          spell
content_id:    sense_index
modid:         mahoumagicule            # registry namespace of magicule_standard's skills (save-compat)
display_name:  "Sense Index"
build_target:  event_handler            # skill class + payloads + client screen/mixin; no model
host:          tensura
spec:
  host:       tensura                   # extends io.github.manasmods.tensura.ability.skill.Skill, Skill.SkillType.EXTRA
  school:     sense                     # Tensura sense family (Magic Sense, Heat Source, Soundwave, Universal Perception)
  cast_type:  self_buff                 # press = open list; tracking = sustained
  levels:     { max: 500, scaling: "mastery: radius +0..+20 blocks, costs -0..-50%" }
  acquire:    "auto-learn when tensura:magic_sense is mastered (poll every 100 ticks); config: or universal_perception"
  cost:
    base_mana: none                     # Tensura-native: costs are magicule directly
    magicule:
      open:   100                       # = Search Enemy cast
      open_upkeep:  "25 per 5 s"        # = Magic Sense upkeep
      track_upkeep: "25 per 5 s"
  cast_time:  0
  cooldown:   0
  target:     aoe<presence_sense_radius + mastery bonus>     # 30 base, 50 with Universal Perception
  perceive:                              # list membership = Tensura's getGlowColor rules, re-run server-side
    - presence: "within tensura:presence_sense_radius and tensura:presence_sense > 0.5"
    - heat:     "within tensura:heat_sense_radius, warm-blooded or #hot_source/#cold_source, not ultraWarm dims"
    - sound:    "tensura:sound_sense marker present, entity not silent and not canBlockSoundDetect"
    - exclude:  "self, #no_highlight, invisible-to-viewer, tensura:presence_concealment > 0 (pierce_concealment=false)"
  readout:
    ep: "exact if viewer analysis_level > 0 and within analysis_distance, else band weaker|similar|stronger|far above you"
    unknown: "target maxEP >= 10 x viewer maxEP -> 'Unknown presence', no name"
  importance:                            # score = weight + 100*clamp(log10(theirEP/yourEP),-2,2) + 150 if named; ties -> nearer
    boss: 1000   unknown: 900   hunting_you: 800   player: 500   hostile: 400
    trap_treasure: 300   neutral: 100   passive: 0   own_subordinate: -100
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
      - { shape: outline, size: "entity silhouette", texture: none, emissive: true, layer: vanilla_outline }  # via SkillClientUtils.getGlowColor mixin
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
      - { id: title,  rect: [8, 6, _, 8],      widget: label,  role: text_dark, text: "Sense Index" }
      - { id: count,  rect: [right-8, 6, _, 8], widget: label, role: text_muted, text: "<n> sensed - <r> m" }
      - { id: search, rect: [7, 18, 126, 20],  widget: edit_box, sprite: widget/text_field, icon: icon/search }
      - { id: sort,   rect: [135, 18, 106, 20], widget: cycle_button, values: [Importance, Distance] }
      - { id: list,   rect: [7, 40, 234, 141], widget: well + rows, row: { h: 21, pitch: 23, visible: 6 } }
      - { id: hint,   rect: [8, 189, _, 8],    widget: label, role: text_muted, text: "Double-click to track" }
      - { id: track,  rect: [157, 183, 84, 20], widget: button, text: "Track | Stop tracking" }
    row: [ portrait_viewport 18x18 (live entity render), name (fit 118), dot|crown + category word,
           distance + 8-way arrow (relative to facing), EP or band ]
    hud_chip: { voice: system, anchor: "centre, bottom edge = action bar line - 10", h: 13,
                content: [ eye glyph (gold), name (sys_text), distance (white), arrow (sys_edge) ] }
    data:    [ { field: snapshot, source: "server scan", sync: s2c_payload, refresh_ticks: 20, max_rows: 64 },
               { field: tracked_pos, source: server, sync: s2c_payload, every: 20 } ]
    actions: [ { id: track, calls: "c2s TrackPayload(entityId)" }, { id: stop, calls: "c2s TrackPayload(-1)" } ]
    states:  [ default, hover_tooltip, tracking, search, sorted_distance, empty, scale2, scale4, min_320x240 ]
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
  - mastering tensura:magic_sense learns mahoumagicule:sense_index exactly once
  - pressing it costs 100 magicule and opens the list; 25 per 5 s while open; out of magicule closes it
  - list matches Tensura's glow rules: a zombie at 20 blocks listed, a concealed mob not, heat targets absent in the Nether
  - a mob targeting the player ranks above a stronger idle hostile; own subordinates sort last
  - double-click tracks: glow outline + HUD chip with live distance; 25 per 5 s; "Lost the trail" after 10 s out of range
  - in-game screenshot matches docs/ui/sense-index mockups at GUI scale 3 and fits 320x240
  - javap: common classes have no net/minecraft/client refs; one active magicule_standard jar
```

## Gaps this draft exposes in Modforge

1. **`host: tensura` has no spell-lane row.** Proposed: Tensura-native skills cost magicule directly
   (`base_mana: none`), charge through `EnergyHelper.isOutOfEnergy`, and use skill mastery instead of a damage lane.
2. **No `gui` lane yet.** The `gui:` block above follows the proposal in the UI style guide (isekai-chronicles PR #2).
   If Ben approves that lane, this block moves into a `type: gui` companion spec with the same `content_id`.

## Ben's open calls

- Approve the mockup (or one-line tweaks).
- Unlock on Magic Sense mastered (recommended) or only with Universal Perception.
- The name "Sense Index".
- Whether concealed entities ever appear (default: never, as Tensura intends).

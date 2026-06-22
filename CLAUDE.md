# CLAUDE.md — Modforge (agent quick-start)

Modforge is a design + handoff system for Minecraft **mod content** (items / spells / mobs+NPCs) on
NeoForge 1.21.1. It is consumed two ways: **Claude Design** generates designs that conform to it, and
**Claude Code** builds the result. Full orientation is in `README.md`; this is the quick-start plus
the rules you must enforce when generating or building.

## The one rule
The image is NOT the handoff — the paired **SpecBlock** is. Claude Code reads text, not pictures.
Every deliverable ships `{ type, content_id, modid, display_name, build_target, host, spec, verify }`.
A design with no spec block is unusable downstream.

## Structure
- `core/spec-envelope.md` — the shared SpecBlock + every shared convention. **READ FIRST.**
- `core/texture-grid.md` — per-surface palette-index texture grids (the build owns the UV).
- `lanes/item.md` · `lanes/spell.md` · `lanes/entity.md` — the three lane schemas + worked examples.
- *(pending)* React components + `examples/` — see the README "left as stubs" section.

## Non-negotiables when generating or building
- Identifiers are literal `snake_case` — the label IS the code name.
- Colors are palette **roles** (token + hex + emissive), never a hex or "dark orange" in prose.
- Textures are **per-surface palette-index grids** (base + sparse emissive); the BUILD computes
  UV / `texOffs` — the design never does.
- Entities: author in the Minecraft frame (**forward = −Z**, no runtime spin); **rotated cuboids**
  by default (each cuboid carries a rest `rot`); pivots at the rotation centre; a **behaviour** spec
  with AI-goal priorities (a ranged/breath ability must outrank melee, or it never fires).
- `build_target` decouples what-from-how: `vanilla_codemodel` (default, reliable) · `geckolib` ·
  `datagen_only` · `event_handler` · `custom_mesh` (mesh escape hatch — leaves the grid workflow).

## Lanes compose
A mob's ability IS a spell-lane spec; a spell can spawn an entity; an item can trigger a spell.
Design one thing, reference it everywhere. Variants reuse, never redraw.

## Where it's used
Primary build target is the `isekai-chronicles` modpack (NeoForge 1.21.1, hand-compiled, no Gradle).
New content flows: Modforge SpecBlock → Claude Code build → deploy into the pack. MIT-licensed, public.

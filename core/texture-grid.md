# core / texture-grid

The source of truth for pixels. Shared by all three lanes. The rule: textures are handed off as
**matrices of palette indices**, never a PNG, never a b64 blob, never a procedural painter
(procedural is what misplaced the Cinderkit eyes). The design does **not** compute UV / `texOffs` —
Claude Code packs the atlas, so pixels and UVs cannot desync.

## Why grids, not images

Claude Code reads text, not pictures, and cannot read pixels out of a PNG/b64 without round-tripping
through code — and cannot reason about *which face* a patch lands on at all. A palette-index grid is
read exactly, edited by hand (move one cell), diffed, and baked deterministically. A paired rendered
PNG may ship **only** as a human/at-a-glance sanity check — never as the data.

## 1. Palette (define once, per content)

Single-char tokens. `.` is reserved for transparent. Convention: lowercase = base layer, UPPERCASE =
emissive layer (readability only; the layer is fixed by which grid the token appears in).

```
palette:
  token  hex        role            layer
  .      —          transparent     —
  c      #2b2b30    charcoal        base
  a      #9a958c    ash             base
  n      #141417    nose            base
  E      #ff7a1a    ember_glow      emissive
  e      #ffd24a    ember_hot_glow  emissive
```

A color named in prose ("dark orange") instead of a token+hex role is a reject.

## 2. Two layers per surface

Minecraft renders an entity/item as a **diffuse** texture (lit by world light) plus an optional
**emissive** texture (additive glow, `RenderType.eyes`). So every surface carries up to two grids:

```
base:      full grid; every cell is a base role or '.'  (the diffuse atlas)
emissive:  SPARSE grid; only glowing cells, '.' elsewhere (the additive atlas), overlaid on base
```

A glowing eye = a base cell (e.g. `n`) **and** an emissive cell (`E`) at the same row/col. Omit the
`emissive` grid for a surface that doesn't glow. This mirrors the Cinderkit's two-PNG setup
(`cinderkit.png` + `cinderkit_emissive.png`) exactly.

## 3. Grid orientation (pinned — same axis rule as the model)

Each grid is **row 0 = top, col 0 = left, painted flat as seen face-on from OUTSIDE** the surface,
+Y(down) toward the bottom rows. The front (north / −Z) face is the one that matters most — get its
up/left right and the build maps the rest. Ambiguous orientation is the face-level version of the
180° spin; it is pinned, not guessed.

## 4. Surfaces by lane

- **item** — one flat sprite: `base` 16×16 (cols×rows), optional `emissive` 16×16. Model is
  `generated`; the sprite IS the geometry. (32×32 allowed for hi-detail items.)
- **entity** — per cube, up to 6 face grids, keyed by direction (`north`=−Z=FRONT, `south`=+Z=back,
  `east`=+X, `west`=−X, `up`=−Y, `down`=+Y). Each face grid is sized to that face:
  front/back = `w×h`, sides = `d×h`, top/bottom = `w×d`. The build packs them into the box-net (§6).
- **spell** — mostly VFX color *roles* (no pixels); but flat VFX textures (beam, orb, ring) are
  sprites in this same format, usually emissive-heavy.

## 5. Shorthand (keep it concise)

```
north: { base: <grid>, emissive: <grid> }   # detailed face: full grids
up:    solid c                                # uniform face: one role
east:  mirror west                            # symmetric face: reuse its mirror
south: —                                       # omitted = fully transparent / default
```
A 12-cube mob is ~72 faces but most are `solid` — only the ~8 detailed faces need grids.

## 6. The cube box-net — BUILD reference, not the designer's job

For a box `(w,h,d)` at `texOffs (u,v)` the build lays the six faces into one net of footprint
`(2d+2w) × (d+h)`; each provided face grid drops into its sub-rect:

```
            cols u+d .. u+d+w      u+d+w .. u+d+2w
   rows v   +----------------+----------------+
            |      up (w×d)  |    down (w×d)   |
  rows v+d  +--------+-------+--------+--------+
            | east   | NORTH | west   | south  |
            | (d×h)  | (w×h) | (d×h)  | (w×h)  |
            +--------+-------+--------+--------+
```
The designer supplies six oriented grids; the build computes `texOffs` and packs this net (and
verifies exact sub-rect offsets against the running `ModelPart` UV). The designer NEVER writes
`texOffs`. This is the single rule that kills the UV/grid desync that put detail on the wrong face.

## 7. Geometry support (the low-poly answer)

| geometry              | grid format works? | notes                                                    |
|-----------------------|--------------------|----------------------------------------------------------|
| **rotated cuboid**    | **yes (per-face)** | **THE DEFAULT — low-poly look, keeps grids/UV/animation** |
| axis-aligned cuboid   | yes (per-face)     | the `rot:[0,0,0]` case; for genuinely blocky parts       |
| flat sprite (items)   | yes (one grid)     | `generated` item model                                   |
| free-form mesh (OBJ)  | **no**             | needs hand-UV-unwrap; `build_target: custom_mesh`, custom renderer, no skeletal anim — escape hatch only |

A box's UV unwrap is in texture space, so a cuboid's **rest rotation does not change its grids** —
rotate freely without touching the texture. That's why rotated cuboids are the default: full
low-poly freedom at zero texture cost. Reach for a true mesh only for VFX or a hero one-off, and
accept it leaves this workflow.

## 8. Rejects

```
[ ] texture as PNG / b64 / procedural painter instead of palette-index grids
[ ] grid dimensions don't match the face/sprite pixel size
[ ] token used that isn't in the palette
[ ] emissive cell with no base cell under it
[ ] design computed texOffs / UV itself
[ ] face orientation not pinned (row0/col0 ambiguous)
[ ] color named in prose instead of a token+hex role
```

## 9. Verify

```
verify:
  - every grid token resolves to a palette role; dims match the surface
  - baked diffuse + emissive atlases match the grids cell-for-cell
  - emissive cells (eyes/markings/cracks) glow in-game and land on the intended face
  - a paired reference render, if shipped, matches the baked atlas (sanity only)
```

## 10. Worked grids

**Cinderkit head — `north` (FRONT) face, 8w × 7h**
```
base:                          emissive:        (sparse — eyes only)
. c c c c c c .                . . . . . . . .
. c n c c n c .                . . . . . . . .
. c n c c n c .                . . E . . E . .     ← ember glow over the dark eye cells
. c c c c c c .                . . . . . . . .
. c c n n c c .                . . . . . . . .
. c c n n c c .                . . . . . . . .
. c c c c c c .                . . . . . . . .
```
`up/east/west/down`: `solid c`.  `south` (back of head): `solid c`.

**Item — `cooling_ember_core` 16×16 (excerpt, charcoal sphere w/ ember cracks)**
```
base: rows of c/a forming a sphere, '.' in the corners
emissive: a few 'E'/'e' cells tracing the cracks (transparent elsewhere)
```

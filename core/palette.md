# core / palette

The color contract, shared by all lanes. A palette is **N named roles**, defined once per content and
referenced everywhere (texture grids, VFX, glow). Never a hex or a color word in prose — that's a
reject.

## A role

```
{ token: <1 char>, id: <snake_case>, hex: "#rrggbb", layer: base | emissive, note: "<optional>" }
```

- `token` — the single character used in texture grids (`core/texture-grid.md`). Convention:
  lowercase = base layer, UPPERCASE = emissive (readability only; the `layer` field is authoritative).
  `.` is reserved for transparent.
- `id` — the human / code name for the role.
- `layer` — `base` (diffuse atlas, lit by world light) or `emissive` (additive glow atlas).

## The vocabulary is per-content, not a fixed list

Role ids describe THIS content's materials. A beast might use `fur_base / underfur / claw`; a golem
`stone_base / crack_glow`; a slime `gel_core / nucleus`; a spell `core_white / sky_pale / sky_blue`.
There is no canonical role set — only the schema. Pick 4–8 roles that name the materials; more than
~8 usually means two materials that should be one.

## Rules
- A color given in prose ("dark orange") or raw hex instead of a `token`+`id`+`hex` role → **reject**.
- Emissive is a role property, not a separate texture the designer paints — the build routes emissive
  roles to the glow atlas (see `core/texture-grid.md`).

## Examples

```
# cinderkit (entity)
.  transparent
c  charcoal        #2b2b30  base
a  ash             #9a958c  base
n  nose            #141417  base
E  ember_glow      #ff7a1a  emissive
e  ember_hot_glow  #ffd24a  emissive

# skyfall_lance (spell VFX — all emissive)
W  core_white  #ffffff  emissive
P  sky_pale    #cdf3ff  emissive
B  sky_blue    #57b6ff  emissive
D  deep_blue   #1f6fe0  emissive
```

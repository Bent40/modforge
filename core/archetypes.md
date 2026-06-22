# core / archetypes

A new entity picks an **archetype** and customises it — it does not re-derive a skeleton. Each
archetype is a standard bone tree + locators + gait defaults; override sizes / pivots / `rot` per
content. Bones are `snake_case`. The root group (`everything`) carries breathe-bob / global offset;
pivots sit at the joint; rotated cuboids by default; the head group carries look-at.

Common shape: `root → everything → { body, <limbs>, head|head_group, tail? }`.

## quadruped  (cinderkit, wolves, beasts)
```
everything
├─ body
├─ head            look-at; children: snout, ear_left, ear_right
├─ leg_front_left  leg_front_right  leg_back_left  leg_back_right
└─ tail            tail_base → tail_mid → tail_tip
locators: locator_muzzle (head, snout tip)
gait: diagonal pairs FL+BR / FR+BL, cos cadence ~0.66; tail idle sway
```

## biped  (humanoids, golems)
```
everything
├─ body            children: head
├─ arm_left  arm_right
└─ leg_left  leg_right
locators: locator_hand_left, locator_hand_right
gait: arm/leg counter-swing (left arm with right leg)
```

## serpentine  (snakes, dragons, worms)
```
everything
└─ spine_00 → spine_01 → … → spine_n     head on spine_00; chain of segments
locators: locator_mouth (spine_00)
gait: travelling sine along the chain (phase offset per segment)
```

## avian  (birds, flyers)
```
everything
├─ body            children: head, tail_feathers
├─ wing_left  wing_right
└─ leg_left  leg_right
locators: locator_beak
gait: wing flap (sin); legs tuck in flight
```

## blob  (slimes, amorphous)
```
everything
└─ core            squash/stretch; optional nucleus child
locators: locator_center
gait: squash on land, stretch on jump (scaleY); no limbs
```

## humanoid_npc  (villagers, tribe leaders)
The `biped` tree plus an `npc` block (dialogue / trades / llm_chat) and an optional `held_item` bone
under an arm. See `lanes/entity.md` → `spec.npc`.

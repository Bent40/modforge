# Lizardman culture (martial arts theme: Mortal Cultivation)

Ben 2026-11-09: lizardmen = martial arts, trading with them advances Mortal Cultivation. Hand-designed hero
buildings in `tools/culturegen/hand_lizard.py`; `python3 -m tools.culturegen.build_lizard` builds levels 1-5.

Look: raised mud-brick platforms above the marsh, red mangrove posts and beams, packed-mud walls with bamboo screen
windows, two-tier hip roofs of dark prismarine with upturned corner tips and copper ridges, lanterns hung from the
eave corners, stone lanterns on the approach, water channels with lily pads.

- Dojo (`lizard_dojo`, MineColonies combat academy): veranda on posts, mat ring with training dummies, weapon
  racks, shrine dais with banners. Levels: 1 hall; 2 dummies and stone lanterns; 3 raised clerestory and second
  roof; 4 weapon racks; 5 water channels. Sheet `previews/lizard_dojo_levels.png`.
- Town hall (`lizard_hall`): great hall on mangrove stilts over a pond, ramp, railed gallery, two-tier roof, chief's
  seat and banners, war drum (note block) on the gallery. Levels: 1 hall; 2 gallery, banners; 3 upper roof tier;
  4 drum, stone lanterns; 5 water channels.
- Residence (`lizard_house`): stilt house over a fish pond with a porch and fish rack; level n = n beds (3+ adds a
  stilted side room).
- `pack/lizard_preview/`: loose test pack (townhall, residence, combatacademy 1-5). Not pasted in game yet.
- Next: the long tail via `cultures/lizardman.yaml` (reskin + colony.py) in these materials.

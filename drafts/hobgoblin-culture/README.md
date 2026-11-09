# Hobgoblin culture (goblin race tier 2)

Spec: `cultures/hobgoblin.yaml`. One palette drives everything; a look change reruns:

    python -m tools.culturegen.reskin cultures/hobgoblin.yaml <pristine Goblin pack> OUT/hobpack
    python -m tools.culturegen.colony cultures/hobgoblin.yaml OUT/hob --source-pack OUT/hobpack
    # overlay OUT/hob/blueprints onto OUT/hobpack (residence/townhall/builder go under fundamentals/)

Pristine Goblin pack = isekai-chronicles 28fd014 `isekai_kingdoms_build/staging/blueprints/isekai_kingdoms/goblin`
(the staging copy now holds generated goblin huts; don't reskin from it).

- `pack/hobgoblin/`: full MineColonies style pack "Hobgoblin", 461 blueprints: 45 generated hut types (223) +
  everything else (roads, fields, walls, towers, gatehouse, miner, decorations) reskinned from the Goblin pack.
- `colony/`: level sheets (residence, town hall, builder), category sheets in `all/`, `colony_report.txt`.
- Hobgoblin vs goblin: stone-brick footings, white plaster walls, dark oak posts and plank roofs, blue beds and
  banners; round huts become square timber houses (`shell_map: { round_hut: house }`).
- Not in any jar yet: waits for Ben's OK on the look.

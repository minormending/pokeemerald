---
name: add-evolution
description: Add or replace an evolution for a species. Use when the user wants a Pokémon to evolve into another via level, stone, friendship, trade, or beauty. Runs tools/agent_tools/add_evolution.py.
---

# add-evolution

```bash
# Level-up evolution
python3 tools/agent_tools/add_evolution.py --from FLARION --to CHARIZARD --method LEVEL --param 36

# Stone evolution
python3 tools/agent_tools/add_evolution.py --from LEAFLING --to ROSELIA --method ITEM --param ITEM_LEAF_STONE

# Friendship
python3 tools/agent_tools/add_evolution.py --from EEVEE --to UMBREON --method FRIENDSHIP_NIGHT --param 0
```

Methods: `LEVEL`, `FRIENDSHIP`, `FRIENDSHIP_DAY`, `FRIENDSHIP_NIGHT`,
`TRADE`, `TRADE_ITEM`, `ITEM`, `LEVEL_ATK_GT_DEF`, `LEVEL_ATK_EQ_DEF`,
`LEVEL_ATK_LT_DEF`, `LEVEL_SILCOON`, `LEVEL_CASCOON`, `LEVEL_NINJASK`,
`LEVEL_SHEDINJA`, `BEAUTY`. Prepend `EVO_` is done by the tool.

The tool aborts if either species is not defined, so add creatures first
with `/add-pokemon`.

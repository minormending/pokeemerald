---
name: edit-species
description: Modify an existing species' base stats, types, abilities, growth rate, or body color in-place. Use when the user wants to rebalance or re-type an existing Pokémon. Runs tools/agent_tools/edit_species.py.
---

# edit-species

```bash
python3 tools/agent_tools/edit_species.py --species TREECKO \
    --base-attack 80 --base-speed 100

python3 tools/agent_tools/edit_species.py --species PIKACHU \
    --type1 ELECTRIC --type2 NORMAL --ability1 LIGHTNING_ROD
```

Any field you omit is left unchanged. Supported fields: `--base-hp`,
`--base-attack`, `--base-defense`, `--base-speed`, `--base-sp-attack`,
`--base-sp-defense`, `--catch-rate`, `--exp-yield`, `--egg-cycles`,
`--type1`, `--type2`, `--ability1`, `--ability2`, `--growth-rate`,
`--body-color`.

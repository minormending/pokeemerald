---
name: add-pokemon
description: Add a new Pokémon species to the pokeemerald decomp. Use when the user asks to add a new creature, Pokémon, fakemon, or species. Runs tools/agent_tools/add_species.py which handles all ~15 related files (constants, base stats, pokedex, learnset, graphics lookups).
---

# add-pokemon

Insert a new species into pokeemerald. The tool clones an existing species'
graphics so you don't need new art.

## When to use

- User says "add a Pokémon named X" / "add a fakemon" / "add a new creature".
- User wants stats, typing, and a pokedex entry added in one go.

## How

Run the CLI tool. Required: `--name`, `--types`, `--stats`, `--ability`,
`--clone-from`. Optional but recommended: `--category`, `--height`,
`--weight`, `--dex-text`, `--learnset`.

```bash
python3 tools/agent_tools/add_species.py \
    --name FLARION --types FIRE,DRAGON \
    --stats 80,120,70,95,110,75 \
    --ability BLAZE --ability2 PRESSURE \
    --clone-from CHARIZARD \
    --category "EMBER" --height 12 --weight 500 \
    --dex-text "A fierce dragon said to breathe sapphire fire that can melt steel." \
    --learnset "1:TACKLE,5:EMBER,15:DRAGON_RAGE,30:FLAMETHROWER"
```

## Important

- Species names are UPPER_SNAKE_CASE. Max 10 display chars.
- Stats order: `hp,atk,def,spe,spa,spd`.
- Types must be valid `TYPE_*` without the prefix (e.g. `FIRE`, `DRAGON`).
- Ability must be a valid `ABILITY_*` from `include/constants/abilities.h`.
- After adding, run `python3 tools/agent_tools/build.py` to verify.

## For bulk additions

Prefer one `add_species.py` call per species in sequence — each run bumps
`SPECIES_EGG` and `NATIONAL_DEX_COUNT`, which the next call needs up-to-date.

You can also pass `--json path/to/spec.json` with the same keys.

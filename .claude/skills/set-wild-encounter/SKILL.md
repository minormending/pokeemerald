---
name: set-wild-encounter
description: Replace a wild-encounter slot on a given route/map so a species can be caught in the wild. Use when the user wants to spawn a Pokémon in a specific route. Runs tools/agent_tools/set_wild_encounter.py which edits src/data/wild_encounters.json.
---

# set-wild-encounter

```bash
python3 tools/agent_tools/set_wild_encounter.py \
  --map MAP_ROUTE101 --field land_mons --slot 0 \
  --species FLARION --level 5 --max-level 8
```

- `--field` ∈ `land_mons | water_mons | rock_smash_mons | fishing_mons`.
- `--slot` is the 0-indexed position inside that field's `mons` list.
- `--max-level` defaults to `--level`.

The JSON is preprocessed into `wild_encounters.h` during the build, so rerun
`/build-pokeemerald` after editing.

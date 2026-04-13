---
name: swap-trainer-species
description: Replace a species in a specific trainer's party with another species. Use when the user wants to give a gym leader or rival a different Pokémon. Runs tools/agent_tools/swap_trainer_species.py.
---

# swap-trainer-species

```bash
python3 tools/agent_tools/swap_trainer_species.py \
    --trainer Roxanne1 --from NOSEPASS --to FLARION
```

- `--trainer` is the identifier part of `sParty_<Name>` in
  `src/data/trainer_parties.h` (e.g. `Roxanne1`, `Brawly1`, `May1`).
- `--from` must already exist in that trainer's party.

Every matching `.species = SPECIES_<from>` inside that party is rewritten.

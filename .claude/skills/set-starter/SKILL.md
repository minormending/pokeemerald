---
name: set-starter
description: Change one of the three starter Pokémon (grass/fire/water slot). Use when the user wants to swap Treecko/Torchic/Mudkip with another species. Runs tools/agent_tools/set_starter.py.
---

# set-starter

```bash
python3 tools/agent_tools/set_starter.py --slot grass --species FLARION
```

Slots: `grass` | `fire` | `water`.

The species must already be defined (use `/add-pokemon` first). The tool
verifies `SPECIES_<NAME>` exists and edits `src/starter_choose.c` in place.
After editing, rebuild with `/build-pokeemerald`.

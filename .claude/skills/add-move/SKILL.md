---
name: add-move
description: Add a new battle move to pokeemerald. Use when the user asks to add/create a new move or attack. Runs tools/agent_tools/add_move.py which updates constants, battle_moves.h, contest_moves.h, and move_names.h.
---

# add-move

Append a new move to the game.

## Usage

```bash
python3 tools/agent_tools/add_move.py \
    --name SAPPHIRE_FLAME --display "SAPPHIRE FLAME" \
    --type FIRE --power 95 --accuracy 100 --pp 10 \
    --effect BURN_HIT --secondary 30
```

Required: `--name`, `--display`. Everything else has defaults.

## Notes

- `--effect` must be a valid `EFFECT_*` from `include/constants/battle_move_effects.h`.
- Move name identifier is UPPER_SNAKE_CASE; display is free text (max ~12 chars on-screen).
- Battle animation falls through to a default; wire up a custom one in
  `src/data/battle_anim_scripts.s` if you want unique visuals.

---
name: tweak-config
description: Toggle every compile-time optional mod and global gameplay constant — exp multiplier, catch rate bonus, perfect IVs, never miss, crit rate, no random encounters, unlimited TMs, starting money, instant text, run anywhere, skip intro, shiny odds. Use when the user asks about balance/QoL toggles. Runs tools/agent_tools/tweak_config.py.
---

# tweak-config

## Integer knobs

```bash
python3 tools/agent_tools/tweak_config.py --shiny-odds 512        # ~1/128
python3 tools/agent_tools/tweak_config.py --exp-multiplier 3      # 3× XP
python3 tools/agent_tools/tweak_config.py --catch-rate-bonus 3    # 3× catch odds
python3 tools/agent_tools/tweak_config.py --crit-rate-bonus 3     # always crit
python3 tools/agent_tools/tweak_config.py --starting-money 30000
```

## Boolean mods (accept `on` / `off`)

```bash
python3 tools/agent_tools/tweak_config.py --perfect-ivs on
python3 tools/agent_tools/tweak_config.py --never-miss on
python3 tools/agent_tools/tweak_config.py --no-random-encounters on
python3 tools/agent_tools/tweak_config.py --unlimited-tms on
python3 tools/agent_tools/tweak_config.py --instant-text on
python3 tools/agent_tools/tweak_config.py --run-anywhere on
python3 tools/agent_tools/tweak_config.py --skip-intro on
python3 tools/agent_tools/tweak_config.py --catch-exp on
python3 tools/agent_tools/tweak_config.py --exp-all on
python3 tools/agent_tools/tweak_config.py --poison-doesnt-faint on
python3 tools/agent_tools/tweak_config.py --physical-special-split on
python3 tools/agent_tools/tweak_config.py --quick-test on
```

### Testing battle-side mods quickly

`--quick-test on` is a ready-made testing harness: on New Game, the
player is dropped on Route 102 with Alakazam, Machamp, and Gardevoir at
Lv 50 — movesets tuned to show the Physical/Special split (Shadow Ball,
Ice Punch, Psychic as control). Combine with `--skip-intro on` and
`--instant-text on` for the fastest path from `make` → first battle.

Flags can be combined in one command. Rebuild after with
`/build-pokeemerald`. All of these are compile-time `#define`s in
`include/config.h` (SHINY_ODDS lives in `include/constants/pokemon.h`) and
gate single-line edits at well-known hook points in the engine.

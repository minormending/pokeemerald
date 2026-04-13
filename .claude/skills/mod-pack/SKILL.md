---
name: mod-pack
description: Apply a JSON bundle of multiple pokeemerald edits (species, moves, evolutions, starters, wild encounters, rebalance, config) in one shot. Use when the user hands you a mod-pack file or asks for bulk changes. Runs tools/agent_tools/mod_pack.py.
---

# mod-pack

```bash
python3 tools/agent_tools/mod_pack.py mods/megamix.json
python3 tools/agent_tools/mod_pack.py mods/megamix.json --verify
```

Schema (all keys optional):
```json
{
  "species": [ { "name": "FLARION", "types": ["FIRE","DRAGON"],
                 "stats": [80,120,70,95,110,75], "ability": "BLAZE",
                 "clone_from": "CHARIZARD", "dex_text": "...",
                 "learnset": [[1,"SCRATCH"],[7,"EMBER"]] } ],
  "moves":   [ { "name": "RUNE_BEAM", "display": "RUNE BEAM",
                 "type": "PSYCHIC", "power": 85 } ],
  "evolutions": [ { "from": "FLARION", "to": "CHARIZARD",
                    "method": "LEVEL", "param": 36 } ],
  "starters":[ { "slot": "grass", "species": "FLARION" } ],
  "wilds":   [ { "map": "MAP_ROUTE101", "field": "land_mons",
                 "slot": 0, "species": "LEAFLING", "level": 3, "max_level": 5 } ],
  "edits":   [ { "species": "TREECKO", "base_attack": 80 } ],
  "config":  { "shiny_odds": 4096 }
}
```

Each section delegates to its underlying tool. Order is fixed: species →
moves → evolutions → starters → wilds → edits → config. Pass `--verify` to
run `build.py --verify` at the end.

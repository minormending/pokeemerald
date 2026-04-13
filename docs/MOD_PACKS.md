# Mod packs

A mod pack is a JSON file that bundles many operations — adding
species, moves, evolutions, toggles, wild-encounter placements — into
one recipe. You apply them all with a single command.

## When to use

- You want to share your mod as a single file someone else can drop in.
- You're making more than ~3 changes at once.
- You want the changes under version control as a recipe rather than as
  a diff.

## Schema

All keys are optional. Operations run in the order listed.

```json
{
  "species": [
    {
      "name": "CINDERPUP",
      "types": ["FIRE"],
      "stats": [45, 60, 40, 65, 55, 40],
      "ability": "BLAZE",
      "clone_from": "GROWLITHE",
      "category": "CINDER",
      "height": 5,
      "weight": 70,
      "dex_text": "A spirited pup whose fur smolders with playful embers.",
      "body_color": "RED",
      "growth_rate": "MEDIUM_SLOW",
      "gender_ratio": "PERCENT_FEMALE(12.5)",
      "learnset": [[1, "TACKLE"], [8, "EMBER"], [30, "FLAMETHROWER"]]
    }
  ],
  "moves": [
    {
      "name": "SAPPHIRE_FLAME",
      "display": "SAPPHIRE FLAME",
      "type": "FIRE",
      "power": 95,
      "accuracy": 100,
      "pp": 10,
      "split": "SPECIAL"
    }
  ],
  "evolutions": [
    { "from": "CINDERPUP", "to": "ARCANINE",
      "method": "ITEM", "param": "ITEM_FIRE_STONE" }
  ],
  "starters": [
    { "slot": "fire", "species": "CINDERPUP" }
  ],
  "wilds": [
    { "map": "MAP_ROUTE103", "field": "land_mons", "slot": 0,
      "species": "CINDERPUP", "level": 4, "max_level": 6 }
  ],
  "edits": [
    { "species": "MUDKIP", "base_attack": 80 }
  ],
  "config": {
    "perfect_ivs": true,
    "exp_multiplier": 3,
    "shiny_odds": 512
  }
}
```

## Applying a pack

```bash
# Apply the pack only (doesn't build)
python3 tools/agent_tools/mod_pack.py path/to/mypack.json

# Apply + build + boot-test
python3 tools/agent_tools/mod_pack.py path/to/mypack.json --verify
```

The tool runs each section's underlying script in sequence. If one
step fails, earlier successful steps stay applied (they're not all-or-
nothing); run under `git` if you want durable rollback.

## Order of operations

Sections execute in this fixed order:

1. `species` — add new Pokémon.
2. `moves` — add new moves.
3. `evolutions` — wire evolutions (new species need to exist first).
4. `starters` — replace starter slots.
5. `wilds` — place species into wild encounters.
6. `edits` — edit existing species stats.
7. `config` — flip compile-time flags.

The order matters because later sections can reference names
introduced by earlier sections.

## Ready-made packs in this repo

- [`mods/demo.json`](../mods/demo.json) — small example: adds
  `CINDERPUP` (Growlithe clone), wires Fire-Stone evolution to Arcanine,
  spawns on Route 103, buffs Mudkip, doubles shiny odds.
- [`mods/qol.json`](../mods/qol.json) — maximum quality-of-life: every
  QoL mod turned on plus 3× XP, 3× catch rate, and ~1/128 shiny odds.

```bash
python3 tools/agent_tools/mod_pack.py mods/qol.json --verify
```

---

## Related docs

- [AGENTS.md](../AGENTS.md) — main user guide.
- [MODS.md](MODS.md) — full optional-mods reference.
- [tools/agent_tools/README.md](../tools/agent_tools/README.md) — developer/script reference.

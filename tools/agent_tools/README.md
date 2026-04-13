# agent_tools — scripts for modifying pokeemerald

These are Python 3 scripts that edit the pokeemerald source code for you.
Their job: turn "add a new Pokémon" into one command instead of 15
hand-edits.

This file is the developer-facing reference. If you've never used the
tooling before, start with the other docs first:

- [**AGENTS.md**](../../AGENTS.md) — main hub: install, first build,
  "what you can do", step-by-step tutorial.
- [docs/MODS.md](../../docs/MODS.md) — optional compile-time mods
  (perfect IVs, never-miss, physical/special split, etc.).
- [docs/MOD_PACKS.md](../../docs/MOD_PACKS.md) — JSON bundles of
  operations.
- [docs/QUICK_TEST.md](../../docs/QUICK_TEST.md) — fast iteration
  harness for battle-side mods.
- [docs/TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md) — common
  failures and fixes.
- [CLAUDE.md](../../CLAUDE.md) — rules for AI agents.

---

## Who should use these

- **Modders** who want to add Pokémon, tweak stats, or enable cheats
  without touching C code.
- **AI agents** (Claude Code, Cursor) editing the repo on behalf of users
  — the tools enforce invariants no human would reliably remember.
- **Engineers** who know C and could do these edits by hand but would
  rather have a script snapshot the file set and roll back on error.

All three audiences benefit from the fact that every script is
**atomic**: if it fails halfway, the files it touched are restored.

---

## What you need installed

On Ubuntu/Debian:

```bash
sudo apt install -y gcc-arm-none-eabi binutils-arm-none-eabi \
                    libnewlib-arm-none-eabi \
                    gcc g++ pkg-config libpng-dev zlib1g-dev \
                    python3 \
                    mgba-sdl xvfb      # optional, for verify_rom.py
```

On macOS:

```bash
brew install --cask gcc-arm-embedded
brew install pkg-config libpng zlib python3
# For mgba: download mGBA from https://mgba.io
```

On Windows: use WSL2 and the Ubuntu instructions.

`python3 --version` must be 3.8 or newer. No `pip install` is needed; the
scripts use only the standard library.

---

## All scripts at a glance

| Script | Purpose |
|---|---|
| `add_species.py`         | Insert a new Pokémon species, cloning graphics from an existing one. |
| `add_move.py`            | Append a new move (battle table, contest table, name, effect). |
| `add_evolution.py`       | Add or replace an evolution entry for a species. |
| `edit_species.py`        | Modify base stats / types / abilities of an existing species. |
| `swap_trainer_species.py`| Replace a species inside a specific trainer's party. |
| `set_starter.py`         | Swap one of the three starter slots (grass / fire / water). |
| `set_wild_encounter.py`  | Place a species into a route/map wild-encounter slot. |
| `tweak_config.py`        | Toggle optional mods and adjust global constants. |
| `mod_pack.py`            | Apply a JSON bundle that chains the other scripts. |
| `verify_rom.py`          | Boot the built ROM under mGBA headlessly and watch for crashes. |
| `list_species.py`        | Print every `SPECIES_*` define with its numeric ID. |
| `move_splits.py`         | Data dict mapping every move to Gen-4+ Physical/Special/Status. Import-only. |
| `populate_move_splits.py`| One-shot rewriter that injects `.split = SPLIT_X,` into every entry of `src/data/battle_moves.h`. Idempotent. |
| `build.py`               | Detect toolchain and run `make`. |
| `pe_paths.py`            | Shared path constants. Imported by other scripts, not a standalone tool. |
| `pe_edit.py`             | Shared editing helpers. Imported, not run. |

Every runnable script prints a detailed help message:

```bash
python3 tools/agent_tools/<name>.py --help
```

---

## Script-by-script reference

### `add_species.py`

Adds a new Pokémon species to the game. Touches ~15 source files in one
atomic operation:

```
include/constants/species.h                  # new SPECIES_* define
include/constants/pokedex.h                  # NATIONAL_DEX entry + COUNT bump
src/data/text/species_names.h                # in-game name
src/data/pokemon/species_info.h              # base stats, types, ability, etc.
src/data/pokemon/pokedex_entries.h           # dex entry (height, weight, text)
src/data/pokemon/pokedex_text.h              # dex flavor text
src/data/pokemon/pokedex_orders.h            # three sort orders
src/data/pokemon/level_up_learnset_pointers.h
src/data/pokemon/level_up_learnsets.h        # the learnset array
src/data/pokemon_graphics/front_pic_table.h
src/data/pokemon_graphics/still_front_pic_table.h
src/data/pokemon_graphics/back_pic_table.h
src/data/pokemon_graphics/palette_table.h
src/data/pokemon_graphics/shiny_palette_table.h
src/data/pokemon_graphics/front_pic_anims.h
src/data/pokemon_graphics/front_pic_coordinates.h
src/data/pokemon_graphics/back_pic_coordinates.h
src/data/pokemon_graphics/footprint_table.h
src/data/pokemon_graphics/enemy_mon_elevation.h
src/data/pokemon_graphics/unknown_table.h
```

Example:

```bash
python3 tools/agent_tools/add_species.py \
    --name FLARION --types FIRE,DRAGON \
    --stats 80,120,70,95,110,75 \
    --ability BLAZE --ability2 PRESSURE \
    --clone-from CHARIZARD \
    --category "EMBER" --height 12 --weight 500 \
    --dex-text "A fierce dragon said to breathe sapphire fire." \
    --body-color RED --catch-rate 45 --exp-yield 200 \
    --growth-rate MEDIUM_SLOW \
    --gender-ratio "PERCENT_FEMALE(12.5)" \
    --learnset "1:SCRATCH,7:EMBER,30:FLAMETHROWER"
```

Required flags: `--name`, `--types`, `--stats`, `--ability`,
`--clone-from`.

Key rules:

- **`--name`**: `ALL_CAPS_AND_UNDERSCORES`, ≤10 characters for the
  in-game display.
- **`--types`**: comma-separated, 1 or 2 values. Valid types are in
  `include/constants/pokemon.h` (without the `TYPE_` prefix). Gen 3
  only — no `FAIRY`.
- **`--stats`**: six integers in order — HP, Attack, Defense, Speed,
  Special Attack, Special Defense.
- **`--ability`, `--ability2`**: from `include/constants/abilities.h`,
  no prefix.
- **`--clone-from`**: an existing `SPECIES_*` (no prefix) whose sprite
  and palette the new species will reuse. Required because no art
  generation is performed.
- **`--learnset`**: comma-separated `level:MOVE` pairs; move names come
  from `include/constants/moves.h` without the `MOVE_` prefix. If you
  don't pass one, the species learns only Tackle at level 1.

You can also use `--json spec.json` to pass everything from a file; the
keys match the CLI flags but with underscores.

**Where the new species ends up**: right before `SPECIES_EGG`. The
`SPECIES_EGG` and `SPECIES_UNOWN_*` constants (which are defined
relative to `NUM_SPECIES`) shift automatically. National Dex order
appends after the current last entry, and `NATIONAL_DEX_COUNT` is
updated to the new last species.

### `add_move.py`

Appends a new battle move:

```bash
python3 tools/agent_tools/add_move.py \
    --name SAPPHIRE_FLAME --display "SAPPHIRE FLAME" \
    --type FIRE --power 95 --accuracy 100 --pp 10 \
    --effect BURN_HIT --secondary 30
```

Touches `include/constants/moves.h` (the `MOVE_*` define and bump
`MOVES_COUNT`), `src/data/text/move_names.h`, `src/data/battle_moves.h`,
and `src/data/contest_moves.h`.

Required: `--name`, `--display`.

- `--effect` — an `EFFECT_*` from `include/constants/battle_move_effects.h`
  (defaults to `HIT`).
- `--target` — defaults to `SELECTED`; other values include `USER`,
  `FOES_AND_ALLY`, `BOTH`.
- `--priority`, `--secondary` (chance of secondary effect, 0-100).
- `--flags` — space of flags like `FLAG_MAKES_CONTACT |
  FLAG_PROTECT_AFFECTED`. Defaults to a sensible combination.

Move animation falls through to a default; if you want a unique
animation you'll need to edit `src/data/battle_anim_scripts.s` by hand.

### `add_evolution.py`

```bash
# Level-up evolution
python3 tools/agent_tools/add_evolution.py \
    --from FLARION --to CHARIZARD --method LEVEL --param 36

# Stone evolution
python3 tools/agent_tools/add_evolution.py \
    --from LEAFLING --to ROSELIA --method ITEM --param ITEM_LEAF_STONE

# Friendship evolution (night)
python3 tools/agent_tools/add_evolution.py \
    --from EEVEE --to UMBREON --method FRIENDSHIP_NIGHT --param 0
```

Methods (drop the `EVO_` prefix when passing): `LEVEL`, `FRIENDSHIP`,
`FRIENDSHIP_DAY`, `FRIENDSHIP_NIGHT`, `TRADE`, `TRADE_ITEM`, `ITEM`,
`LEVEL_ATK_GT_DEF`, `LEVEL_ATK_EQ_DEF`, `LEVEL_ATK_LT_DEF`,
`LEVEL_SILCOON`, `LEVEL_CASCOON`, `LEVEL_NINJASK`, `LEVEL_SHEDINJA`,
`BEAUTY`.

If the species already has an evolution entry, it is replaced. The tool
refuses to run if either species isn't defined.

### `edit_species.py`

In-place edits to an existing species:

```bash
python3 tools/agent_tools/edit_species.py --species TREECKO \
    --base-attack 80 --base-speed 100

python3 tools/agent_tools/edit_species.py --species PIKACHU \
    --type1 ELECTRIC --type2 NORMAL --ability1 LIGHTNING_ROD
```

Supported flags: `--base-hp`, `--base-attack`, `--base-defense`,
`--base-speed`, `--base-sp-attack`, `--base-sp-defense`, `--catch-rate`,
`--exp-yield`, `--egg-cycles`, `--type1`, `--type2`, `--ability1`,
`--ability2`, `--growth-rate`, `--body-color`. Unspecified fields are
left unchanged.

### `swap_trainer_species.py`

```bash
# Give Roxanne's first team a FLARION in place of her NOSEPASS
python3 tools/agent_tools/swap_trainer_species.py \
    --trainer Roxanne1 --from NOSEPASS --to FLARION
```

`--trainer` is the suffix of `sParty_<Name>` in
`src/data/trainer_parties.h`. Common ones: `Roxanne1`, `Brawly1`,
`Wattson1`, `Flannery1`, `Norman1`, `Winona1`, `TateAndLiza1`,
`Juan1`, `Wally1`…`Wally5`, `May1`…`May3`, `Brendan1`…`Brendan3`.

The tool rewrites every occurrence of `SPECIES_<from>` in that party to
`SPECIES_<to>`. If the species wasn't present, the tool errors out
rather than do nothing silently.

### `set_starter.py`

```bash
python3 tools/agent_tools/set_starter.py --slot grass --species FLARION
python3 tools/agent_tools/set_starter.py --slot fire --species TERRAPYON
python3 tools/agent_tools/set_starter.py --slot water --species AZURUNE
```

Slots are literally `grass`, `fire`, `water` and map to Treecko,
Torchic, Mudkip in vanilla. The species must already be defined.

### `set_wild_encounter.py`

```bash
python3 tools/agent_tools/set_wild_encounter.py \
    --map MAP_ROUTE101 --field land_mons --slot 0 \
    --species FLARION --level 5 --max-level 8
```

- `--map` — a `MAP_*` constant. Use `grep -rn "MAP_" data/maps/map_groups.json`
  or `include/constants/layouts.h` to find valid names.
- `--field` — `land_mons` (walking), `water_mons` (surfing),
  `rock_smash_mons`, `fishing_mons`.
- `--slot` — 0-indexed position. The slot ordering inside each field
  determines rarity (slot 0 is most common).
- `--max-level` defaults to `--level` if omitted (fixed level).

### `tweak_config.py`

Toggles every optional mod and numeric knob. See
[Optional mods](#optional-mods) below.

### `mod_pack.py`

```bash
python3 tools/agent_tools/mod_pack.py mods/qol.json
python3 tools/agent_tools/mod_pack.py mods/qol.json --verify
```

Applies operations in fixed order: species → moves → evolutions →
starters → wilds → edits → config. See the `mods/` directory for
examples and the full schema.

### `verify_rom.py`

```bash
python3 tools/agent_tools/verify_rom.py                  # default 8s
python3 tools/agent_tools/verify_rom.py --seconds 20
python3 tools/agent_tools/verify_rom.py --rom other.gba
```

Runs three checks:

1. `gbafix -p` header validation.
2. `mgba -l 255 ... --timeout 8` headless boot; scans the log for
   `fatal`, `crash`, `abort`, `undefined instruction`, `illegal`.
3. Presence of gameplay-stage writes (audio FIFO, DMA to palette), to
   tell a black-screen freeze from a working boot.

Exit code non-zero on failure, so it can gate a CI pipeline or a loop.

### `list_species.py`

```bash
python3 tools/agent_tools/list_species.py
```

Dumps every `#define SPECIES_*` with its numeric ID. Useful to confirm a
new addition took effect or to spot duplicates.

### `build.py`

```bash
python3 tools/agent_tools/build.py
python3 tools/agent_tools/build.py --clean
python3 tools/agent_tools/build.py --verify
python3 tools/agent_tools/build.py --classic      # agbcc, matches rom.sha1
python3 tools/agent_tools/build.py -j 8           # explicit parallelism
```

Auto-detects `arm-none-eabi-gcc` (either on PATH or under
`$DEVKITARM`). Prints install hints if the toolchain is missing rather
than failing obscurely.

---

## Optional mods

Compile-time switches. Flip with `tweak_config.py`, rebuild, done.

Full reference (flags, defaults, effects, hook files):
[**docs/MODS.md**](../../docs/MODS.md).

Full reference for the mod-pack JSON bundle format:
[**docs/MOD_PACKS.md**](../../docs/MOD_PACKS.md).

Fast iteration harness for battle-side mods:
[**docs/QUICK_TEST.md**](../../docs/QUICK_TEST.md).

## Design notes

### Atomicity

`add_species.py` snapshots every file it will touch before making any
changes. If any step raises an exception, the snapshot is restored.
Other scripts touch one or two files each; anchor-miss failures happen
before any `write()` call.

The snapshot is in-memory only (not on disk), so if the Python process
is killed between the snapshot and the restore, you'll be left with
half-applied changes. Use `git` for durable safety.

### File encoding

Many pokeemerald data files contain non-ASCII bytes for the in-game
character map (ligatures, special symbols). If you process them with
UTF-8 string tools you will corrupt them. All editing goes through
`pe_edit.read()` / `pe_edit.write()`, which round-trip in `latin-1`.

### Species-ID insertion invariant

New species IDs are inserted **before `SPECIES_EGG`**. Because the Unown
form block (`SPECIES_UNOWN_B` … `SPECIES_UNOWN_QMARK`) is defined
relative to `NUM_SPECIES` (= `SPECIES_EGG`), those constants shift
automatically. Designated initializers (`[SPECIES_X] = {...}`) keep
working without renumbering.

### Graphics reuse

New species get `--clone-from X`'s sprite / palette / animation pointer
table entries. The game is happy because the lookup tables resolve; the
sprite that appears in-game is X's sprite. Unique art is a separate,
manual process (draw 64×64 sprite, convert with `gbagfx`, replace the
relevant `INCBIN("graphics/pokemon/<clone>/front.4bpp.lz")` line with
your new path).

### National Dex count

`NATIONAL_DEX_COUNT` in `include/constants/pokedex.h` is a `#define` that
equals the last national-dex species. Each `add_species.py` run bumps it
to the newly added species, so chained additions work without collision.

### Extending the tooling

Every script is plain Python 3, standard library only. If an anchor
breaks because upstream source drifted, fix the anchor in the relevant
`update_*` function and the next agent will pick up the fix instead of
running a stale version.

Single-hook gates (like the `PERFECT_IVS` / `EXP_MULTIPLIER` family) are
the cheapest feature to add: locate the one line that does the thing,
wrap it in `#if FLAG …`, define the flag in `include/config.h`, add a
row to `tweak_config.py`'s `INT_KNOBS` / `BOOL_MODS` table. Done.

---

## Troubleshooting

Full problem → fix list: [**docs/TROUBLESHOOTING.md**](../../docs/TROUBLESHOOTING.md).

# pokeemerald — AI Agent & Modding Guide

Welcome! This is the main entry point for modding this Pokémon Emerald
source, whether you're doing it by hand, with an AI assistant like
Claude Code, or both.

This file covers what you need to get started. Deeper material lives in
[`docs/`](docs/) — each topic has its own focused page you can link
people to.

---

## Jump-to

| You want to… | Read |
|---|---|
| Install prerequisites + first build | [§ Quick start](#quick-start) below |
| See the full list of things the tooling can do | [§ What you can do](#what-you-can-do) below |
| Walk through adding a Pokémon end-to-end | [§ Tutorial](#tutorial-add-a-pokémon-end-to-end) below |
| Enable cheats / rebalance knobs / QoL mods | [**docs/MODS.md**](docs/MODS.md) |
| Bundle many mods into one file | [**docs/MOD_PACKS.md**](docs/MOD_PACKS.md) |
| Test battle changes in 10 seconds, no replay | [**docs/QUICK_TEST.md**](docs/QUICK_TEST.md) |
| Script-by-script tool reference | [**tools/agent_tools/README.md**](tools/agent_tools/README.md) |
| Build / verify the ROM | [§ Build + verify](#build--verify) below |
| Fix something that's breaking | [**docs/TROUBLESHOOTING.md**](docs/TROUBLESHOOTING.md) |
| AI-agent-specific rules | [**CLAUDE.md**](CLAUDE.md) |

---

## What this is

`pokeemerald` is a full C reconstruction of Pokémon Emerald. Compiling
the code produces a `.gba` ROM file that runs in any GBA emulator
(mGBA, Visual Boy Advance, My Boy!, Delta) or on real hardware via a
flashcart.

This fork adds a Python tooling layer on top of that source code.
Instead of hand-editing the 15+ data files that a single "add a new
Pokémon" touches, you run one command. Same for moves, starters, wild
encounters, cheat flags, and more.

Examples:

```bash
# Add a Fire/Dragon Pokémon named FLARION
python3 tools/agent_tools/add_species.py \
    --name FLARION --types FIRE,DRAGON --stats 80,120,70,95,110,75 \
    --ability BLAZE --clone-from CHARIZARD \
    --dex-text "A fierce dragon said to breathe sapphire fire."

# Every Pokémon gets perfect IVs (31 in every stat)
python3 tools/agent_tools/tweak_config.py --perfect-ivs on

# Triple XP, 30k starting money, instant text
python3 tools/agent_tools/tweak_config.py \
    --exp-multiplier 3 --starting-money 30000 --instant-text on
```

After any change you run one build command and you get a playable ROM.

---

## Quick start

### 1. Install the build toolchain (one-time)

**Ubuntu / Debian / WSL:**

```bash
sudo apt update
sudo apt install -y gcc-arm-none-eabi binutils-arm-none-eabi \
                    libnewlib-arm-none-eabi \
                    gcc g++ pkg-config libpng-dev zlib1g-dev make python3

# Optional but recommended (for automated ROM boot-testing)
sudo apt install -y mgba-sdl xvfb
```

**macOS (Homebrew):**

```bash
brew install --cask gcc-arm-embedded
brew install pkg-config libpng zlib python3
# mGBA: download from https://mgba.io
```

**Windows:** use WSL2 and follow the Ubuntu instructions.

### 2. Build the ROM (sanity check)

From the project root:

```bash
python3 tools/agent_tools/build.py
```

On success you'll see memory-usage stats and a file called
`pokeemerald_modern.gba` appears in the project folder. That's your
ROM — open it in mGBA.

### 3. Make your first change

```bash
python3 tools/agent_tools/tweak_config.py --perfect-ivs on
python3 tools/agent_tools/build.py
```

Reload the ROM in your emulator. Start a new save. Every wild /
trainer / gift Pokémon now has 31 IVs in every stat.

### 4. (Optional) Self-test that the ROM still runs

```bash
python3 tools/agent_tools/build.py --verify
```

Expected output:

```
[ok] header valid (pokeemerald_modern.gba)
[ok] mgba ran 8s without fatal errors  (reached gameplay writes)
```

---

## What you can do

The tooling covers four broad categories. Every capability has a
script in `tools/agent_tools/` and a matching Claude Code slash command.

| I want to… | Command | Slash command |
|---|---|---|
| Add a brand-new Pokémon                | `add_species.py`          | `/add-pokemon` |
| Change an existing Pokémon's stats / types / abilities | `edit_species.py`         | `/edit-species` |
| Add a new move                          | `add_move.py`             | `/add-move` |
| Make a Pokémon evolve into another      | `add_evolution.py`        | `/add-evolution` |
| Change the starter Pokémon              | `set_starter.py`          | `/set-starter` |
| Put a Pokémon into a route's wild grass | `set_wild_encounter.py`   | `/set-wild-encounter` |
| Change a trainer's team                 | `swap_trainer_species.py` | `/swap-trainer-species` |
| Turn on cheats / quality-of-life mods   | `tweak_config.py`         | `/tweak-config` |
| Apply lots of changes from one file     | `mod_pack.py`             | `/mod-pack` |
| Build the ROM                           | `build.py`                | `/build-pokeemerald` |
| Test the ROM boots without crashing     | `verify_rom.py`           | `/verify-rom` |
| List all Pokémon currently defined      | `list_species.py`         | — |

Every script supports `--help`:

```bash
python3 tools/agent_tools/add_species.py --help
```

Per-script reference: [**tools/agent_tools/README.md**](tools/agent_tools/README.md).

---

## Tutorial: add a Pokémon end-to-end

Let's add a Grass-type fakemon called **LEAFLING**, make it evolve into
a stronger form, and make it catchable on Route 101.

### 1. Add the species

```bash
python3 tools/agent_tools/add_species.py \
    --name LEAFLING \
    --types GRASS \
    --stats 55,40,50,70,65,80 \
    --ability CHLOROPHYLL \
    --ability2 CUTE_CHARM \
    --clone-from ROSELIA \
    --category "LEAFLET" \
    --height 4 --weight 35 \
    --dex-text "A tiny forest sprite that dances in the breeze." \
    --learnset "1:ABSORB,1:GROWL,10:MEGA_DRAIN,28:GIGA_DRAIN"
```

What those flags mean:

- `--name LEAFLING` — code name. ALL_CAPS_AND_UNDERSCORES, ≤10 chars.
- `--types GRASS` — 1 or 2 comma-separated types (Gen 3 only; no Fairy).
- `--stats 55,40,50,70,65,80` — HP, Attack, Defense, Speed, Sp. Attack, Sp. Defense.
- `--ability`, `--ability2` — pick from
  [`include/constants/abilities.h`](include/constants/abilities.h).
- `--clone-from ROSELIA` — new species reuses Roselia's sprite, palette,
  and animations. No art needed.
- `--learnset` — comma-separated `level:MOVE` pairs.

Expected output:

```
Added SPECIES_LEAFLING = 418
  cloned graphics from SPECIES_ROSELIA
  NATIONAL_DEX_LEAFLING appended; NATIONAL_DEX_COUNT updated
```

### 2. Make it evolve

```bash
python3 tools/agent_tools/add_evolution.py \
    --from LEAFLING --to ROSELIA --method LEVEL --param 22
```

### 3. Put it in the wild

```bash
python3 tools/agent_tools/set_wild_encounter.py \
    --map MAP_ROUTE101 --field land_mons --slot 0 \
    --species LEAFLING --level 3 --max-level 5
```

### 4. Build and play

```bash
python3 tools/agent_tools/build.py --verify
```

Load `pokeemerald_modern.gba` in your emulator, start a new game, and
walk in the Route 101 grass until a LEAFLING shows up.

---

## Build + verify

```bash
python3 tools/agent_tools/build.py            # normal build
python3 tools/agent_tools/build.py --clean    # wipe build/ first
python3 tools/agent_tools/build.py --verify   # build + boot test
python3 tools/agent_tools/build.py --classic  # match original ROM checksum (needs agbcc)
```

**Outputs:**

- Modern: `pokeemerald_modern.gba`
- Classic: `pokeemerald.gba`

Load the `.gba` in mGBA (recommended), Visual Boy Advance, My Boy!
(Android), Delta (iOS), or flash to a GBA cart.

**Verifying the ROM runs** after changes:

```bash
python3 tools/agent_tools/verify_rom.py
```

Checks that the header is valid, the ROM boots under mGBA for 8
seconds without crashing, and reaches the gameplay stage. Exits
non-zero on failure so you can loop on it in CI.

---

## Gotchas

- **Generation 3 only.** No Fairy type, no Gen 4+ moves like
  `MOVE_METAL_BURST` / `MOVE_FLASH_CANNON`, no Gen 4+ abilities.
- **Name length.** Species and move names display at most 10
  characters in-game.
- **No new art.** Added species reuse the `--clone-from` source's
  sprite. Unique art is a separate, manual process.
- **Save compatibility.** Adding species shifts the Pokédex count;
  pre-existing saves may misinterpret species IDs. Add all species
  before generating the save you care about.
- **Some features the tooling doesn't automate:** egg moves, TM/HM
  compatibility, tutor moves, friendship evolutions with scripted
  event flags. See the files under `src/data/pokemon/` for hand edits.

Full troubleshooting list: [**docs/TROUBLESHOOTING.md**](docs/TROUBLESHOOTING.md).

---

## For AI agents

Read [**CLAUDE.md**](CLAUDE.md) for the agent-specific rules:
always use the tooling rather than hand-editing, verify after
changes, don't reorder existing IDs, data files use non-ASCII bytes
and need latin-1-aware editing.

Every user-facing operation has a slash command under `.claude/skills/`;
run `/help` in Claude Code to see them.

---

## Where to get help

- **This tooling / modding here** — raise an issue on the repo, or
  ask your AI assistant ("add a Fire/Water Pokémon called X to this
  repo" should Just Work).
- **The upstream decomp** —
  [pret/pokeemerald](https://github.com/pret/pokeemerald).
- **General ROM hacking** —
  [Poké Community](https://www.pokecommunity.com/).

Happy modding.

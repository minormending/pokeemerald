# pokeemerald — AI Agent & Modding Guide

Welcome! This document explains how to make changes to this Pokémon Emerald
source code using the bundled tooling, even if you have never touched a
compiler, a C file, or a terminal before.

It's written for two audiences at once:

- **People who want to mod the game** (add Pokémon, change starters, turn
  on cheats like perfect IVs, etc.) without learning C.
- **AI coding agents** (Claude Code, etc.) working in this repo on behalf
  of the user.

If you're a person: read the **Quick start** and the **What you can do**
sections first. The rest is reference material you only need when something
breaks or you want to go deeper.

---

## Table of contents

1. [What this is](#what-this-is)
2. [Quick start](#quick-start)
3. [What you can do](#what-you-can-do)
4. [Step-by-step: add a Pokémon end-to-end](#step-by-step-add-a-pokémon-end-to-end)
5. [All the tools](#all-the-tools)
6. [Optional mods (cheats & quality-of-life)](#optional-mods)
7. [Mod packs: apply many changes at once](#mod-packs)
8. [Fast testing: the `QUICK_TEST` harness](#fast-testing-the-quick_test-harness)
9. [Building the ROM](#building-the-rom)
10. [Testing the ROM](#testing-the-rom-verifying-it-runs)
11. [Troubleshooting](#troubleshooting)
12. [Gotchas and limitations](#gotchas-and-limitations)
13. [For AI agents](#for-ai-agents)

---

## What this is

`pokeemerald` is a full reconstruction of the Game Boy Advance game Pokémon
Emerald, in C source code. Compiling the code produces a `.gba` ROM file
that runs in any GBA emulator (mGBA, Visual Boy Advance, etc.) or on real
hardware via a flashcart.

This project adds a layer of Python scripts ("agent_tools") on top of that
source code. Those scripts make common mods — adding a new Pokémon, tweaking
stats, changing starters, turning on cheats — **one command each**, instead
of hand-editing 15 files.

Examples of things that used to take an afternoon and now take one line:

```bash
# Add a new dragon-type Pokémon called FLARION
python3 tools/agent_tools/add_species.py \
    --name FLARION --types FIRE,DRAGON --stats 80,120,70,95,110,75 \
    --ability BLAZE --clone-from CHARIZARD \
    --dex-text "A fierce dragon said to breathe sapphire fire."

# Every Pokémon gets perfect IVs (31 in every stat)
python3 tools/agent_tools/tweak_config.py --perfect-ivs on

# Start with 30,000 money and instant text
python3 tools/agent_tools/tweak_config.py --starting-money 30000 --instant-text on
```

After any changes you run **one build command** and you get a playable ROM.

---

## Quick start

### 1. Install the build toolchain (one-time setup)

On Ubuntu / Debian / WSL:

```bash
sudo apt update
sudo apt install -y gcc-arm-none-eabi binutils-arm-none-eabi \
                    libnewlib-arm-none-eabi \
                    gcc g++ pkg-config libpng-dev zlib1g-dev make python3
```

Also recommended, for testing the ROM without a physical emulator:

```bash
sudo apt install -y mgba-sdl xvfb
```

On macOS (Homebrew):

```bash
brew install --cask gcc-arm-embedded
brew install pkg-config libpng zlib python3
```

On Windows: use WSL2 (Windows Subsystem for Linux) and follow the
Ubuntu/Debian instructions inside it. The native Windows path is possible
but harder.

### 2. Build the ROM (first time, sanity check)

From the `pokeemerald` directory:

```bash
python3 tools/agent_tools/build.py
```

You should see lots of compiler output ending in something like:

```
Memory region         Used Size  Region Size  %age Used
           EWRAM:      249708 B       256 KB     95.26%
           IWRAM:       30416 B        32 KB     92.82%
             ROM:    13312140 B        32 MB     39.67%
```

A file called **`pokeemerald_modern.gba`** now exists in the project
folder. That's your ROM. Open it in mGBA to play.

### 3. Make your first change

Easy one: turn on perfect IVs (every Pokémon you catch/receive has max
stats) and rebuild.

```bash
python3 tools/agent_tools/tweak_config.py --perfect-ivs on
python3 tools/agent_tools/build.py
```

Reload the ROM in your emulator. Start a new save (old saves won't see
the change for Pokémon you already own). Your starter now has 31 IVs in
every stat.

### 4. (Optional) Confirm the ROM boots automatically

If you installed `mgba-sdl` and `xvfb` above, you can have the tooling
self-test the ROM:

```bash
python3 tools/agent_tools/build.py --verify
```

Output on success:

```
[ok] header valid (pokeemerald_modern.gba)
[ok] mgba ran 8s without fatal errors  (reached gameplay writes)
```

---

## What you can do

The tooling covers four broad categories. Each capability has a script in
`tools/agent_tools/` and a Claude Code slash command under `.claude/skills/`
for people using Claude Code.

| I want to… | Command | Slash command |
|---|---|---|
| Add a brand-new Pokémon                | `add_species.py`          | `/add-pokemon` |
| Change an existing Pokémon's stats / types / ability | `edit_species.py`         | `/edit-species` |
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

---

## Step-by-step: add a Pokémon end-to-end

Let's add a made-up Pokémon called **LEAFLING**, a tiny Grass-type that
evolves into a stronger form, and make it catchable on Route 101.

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

What those arguments mean:

- `--name LEAFLING` — the code name. Must be ALL_CAPS_AND_UNDERSCORES.
- `--types GRASS` — one or two types separated by commas (`FIRE,FLYING`
  for dual-type). Valid types are the 17 Gen-3 types (no Fairy).
- `--stats 55,40,50,70,65,80` — six numbers: **HP, Attack, Defense,
  Speed, Special Attack, Special Defense**.
- `--ability`, `--ability2` — pick from `include/constants/abilities.h`
  (drop the `ABILITY_` prefix).
- `--clone-from ROSELIA` — **important**: the new Pokémon reuses
  Roselia's sprite, palette, and animations. You don't need to draw any
  art.
- `--category`, `--height`, `--weight`, `--dex-text` — Pokédex info.
  Height is in decimetres (4 = 0.4 m), weight in hectograms (35 = 3.5 kg).
- `--learnset` — comma-separated `level:MOVE` pairs. Use move names from
  `include/constants/moves.h` without the `MOVE_` prefix.

Expected output:

```
Added SPECIES_LEAFLING = 418
  cloned graphics from SPECIES_ROSELIA
  NATIONAL_DEX_LEAFLING appended; NATIONAL_DEX_COUNT updated
```

### 2. Add its evolution

Make it evolve into Roselia at level 22:

```bash
python3 tools/agent_tools/add_evolution.py \
    --from LEAFLING --to ROSELIA --method LEVEL --param 22
```

### 3. Make it catchable in the wild

Put it in the first grass slot on Route 101 at levels 3–5:

```bash
python3 tools/agent_tools/set_wild_encounter.py \
    --map MAP_ROUTE101 --field land_mons --slot 0 \
    --species LEAFLING --level 3 --max-level 5
```

- `--field` is one of: `land_mons` (walking in grass), `water_mons`
  (surfing), `rock_smash_mons`, `fishing_mons`.
- `--slot` is the position in the encounter table (0 = most common).

### 4. Build and play

```bash
python3 tools/agent_tools/build.py --verify
```

Load `pokeemerald_modern.gba` in your emulator. Start a new game. Walk
through the grass on Route 101 until you bump into a LEAFLING.

---

## All the tools

Every script is in `tools/agent_tools/`. Every script prints `--help`.

### Content creation

- **`add_species.py`** — adds a new Pokémon. Reuses an existing Pokémon's
  graphics via `--clone-from`, so no art is needed. One run touches 15+
  related data files (stats, Pokédex, learnset, graphics lookups); if any
  step fails, the tool rolls back all files it touched.
- **`add_move.py`** — adds a new attack. Appears in battle and contest
  move tables, gets a name, and is selectable by Pokémon that are taught
  it.
- **`add_evolution.py`** — adds or replaces an evolution entry. Supports
  `LEVEL`, `ITEM` (stone), `FRIENDSHIP`, `FRIENDSHIP_DAY`,
  `FRIENDSHIP_NIGHT`, `TRADE`, `TRADE_ITEM`, `BEAUTY`, and level-stat
  comparisons like `LEVEL_ATK_GT_DEF` (Hitmonlee/Hitmonchan style).

### Content editing

- **`edit_species.py`** — change an existing Pokémon's base stats,
  types, abilities, growth rate, or body color in place.
- **`swap_trainer_species.py`** — inside a given trainer's team, replace
  every `SPECIES_X` with `SPECIES_Y`. Good for changing gym leader teams.

### Placement

- **`set_starter.py`** — swap one of the three starter slots
  (`grass`, `fire`, `water`) with any other species.
- **`set_wild_encounter.py`** — place a species into a specific wild
  encounter slot on a specific map.

### Global toggles

- **`tweak_config.py`** — turn on/off compile-time mods (perfect IVs,
  never miss, instant text, …) and set numeric balance knobs (shiny
  odds, experience multiplier, starting money). See the
  [Optional mods](#optional-mods) section for the full list.

### Meta

- **`mod_pack.py`** — apply a JSON file that bundles many changes at
  once. See [Mod packs](#mod-packs).
- **`list_species.py`** — print every `SPECIES_*` constant and its ID.
- **`build.py`** — compile the ROM.
- **`verify_rom.py`** — boot the ROM under an emulator and check it
  doesn't crash in the first few seconds.
- **`pe_paths.py`**, **`pe_edit.py`** — shared helpers used by the other
  scripts. Not useful on their own.

---

## Optional mods

These are compile-time toggles. You change a setting, rebuild, and the
change is baked into the ROM. They ship **off by default**; you opt in
explicitly.

All of them are single-line `#define` values in `include/config.h` (the
one exception is `SHINY_ODDS`, which lives in
`include/constants/pokemon.h` because that's where the game's random-roll
code reads it from). `tweak_config.py` flips them for you so you don't
have to edit C headers by hand.

### Integer knobs (numeric dials)

| Knob | What it does | Vanilla value | Example |
|---|---|---|---|
| `--shiny-odds N`       | Chance a wild/caught Pokémon is shiny. Probability = N / 65536. | 8 (about 1/8192) | `--shiny-odds 512` ≈ 1/128 |
| `--exp-multiplier N`   | Multiplies the XP each victory gives. | 1 | `--exp-multiplier 3` triples XP |
| `--catch-rate-bonus N` | Multiplies the capture odds on every throw. | 1 | `--catch-rate-bonus 3` ≈ "Ultra Ball on everything" |
| `--crit-rate-bonus N`  | Bumps the crit chance by N stages. 3 = always crit. | 0 | `--crit-rate-bonus 3` |
| `--starting-money N`   | Pokédollars you start a new save with. | 3000 | `--starting-money 30000` |

### Booleans (on/off switches)

Pass `on` or `off`. You can also say `true`/`false` or `1`/`0`.

| Switch | What it does |
|---|---|
| `--perfect-ivs on`          | Every Pokémon — wild, trainer's, gift, starter, hatched — gets 31 IVs in all 6 stats. |
| `--never-miss on`           | Your moves never miss (the accuracy roll is skipped when you're the attacker). |
| `--no-random-encounters on` | Disables all random wild battles. Useful for route-making playtests. |
| `--unlimited-tms on`        | TMs are not consumed when a Pokémon learns them. (HMs are already reusable in vanilla.) |
| `--instant-text on`         | All in-game text appears immediately, ignoring the "Text Speed" option. |
| `--run-anywhere on`         | You can run indoors and in other maps that normally block running. Tall grass and similar still block it. |
| `--skip-intro on`           | Skips the Latios/Latias intro cinematic. You go straight from the copyright screen to the title screen. |
| `--catch-exp on`            | Catching a Pokémon awards XP to every alive party member, just like defeating it would. (Modern Gen 6+ behavior.) |
| `--exp-all on`              | Every alive party member gains XP from every KO, divided evenly — like the modern "Exp. Share is always on" item. |
| `--poison-doesnt-faint on`  | Field-poison ticks (walking with a poisoned Pokémon) stop at 1 HP instead of fainting. You still take the damage tick but won't white out from poison. |
| `--physical-special-split on` | Each move's Physical / Special category is read from a per-move field instead of its type. Matches Gen 4+ behavior — e.g. Shadow Ball becomes Special on any Pokémon, Ice Punch becomes Physical. Big balance change; affects every battle. |
| `--quick-test on`           | On new game, skip the truck sequence and drop the player on Route 102 with a pre-built Lv 50 test party (Alakazam / Machamp / Gardevoir) chosen to highlight the Physical/Special split. Use purely for testing; not a playable save. |

### Combining knobs

You can pass any mix in one command:

```bash
python3 tools/agent_tools/tweak_config.py \
    --perfect-ivs on \
    --exp-multiplier 3 \
    --starting-money 30000 \
    --instant-text on \
    --run-anywhere on \
    --shiny-odds 512
```

Expected output:

```
SHINY_ODDS: 8 -> 512  (probability 0.007812)
EXP_MULTIPLIER: 1 -> 3
STARTING_MONEY: 3000 -> 30000
PERFECT_IVS: 0 -> 1  (ENABLED)
INSTANT_TEXT: 0 -> 1  (ENABLED)
RUN_ANYWHERE: 0 -> 1  (ENABLED)
```

Then rebuild:

```bash
python3 tools/agent_tools/build.py
```

### Turning a mod off

Any boolean switch accepts `off`:

```bash
python3 tools/agent_tools/tweak_config.py --perfect-ivs off
```

For integer knobs, set them back to the vanilla value (see the table):

```bash
python3 tools/agent_tools/tweak_config.py --shiny-odds 8 --exp-multiplier 1
```

### Technical note (what's actually changing)

Each mod is one `#if FLAG …` block at a single place in the engine. For
curious readers:

| Mod | File | Where |
|---|---|---|
| `PERFECT_IVS`          | `src/pokemon.c`                  | `CreateBoxMon` — the single function every Pokémon creation goes through. |
| `EXP_MULTIPLIER`       | `src/battle_script_commands.c`   | Where `calculatedExp = … / 7` is computed. |
| `CATCH_RATE_BONUS`     | `src/battle_script_commands.c`   | Right after status (sleep/poison) capture bonuses. |
| `NEVER_MISS`           | `src/battle_script_commands.c`   | `Cmd_accuracycheck`. |
| `CRIT_RATE_BONUS`      | `src/battle_script_commands.c`   | `Cmd_critcalc`. |
| `NO_RANDOM_ENCOUNTERS` | `src/wild_encounter.c`           | `StandardWildEncounter`. |
| `UNLIMITED_TMS`        | `src/party_menu.c`               | `Task_LearnedMove`. |
| `STARTING_MONEY`       | `src/new_game.c`                 | `NewGameBirchSpeech_SetDefaultPlayerName`. |
| `INSTANT_TEXT`         | `src/menu.c`                     | `GetPlayerTextSpeedDelay`. |
| `RUN_ANYWHERE`         | `src/bike.c`                     | `IsRunningDisallowed`. |
| `SKIP_INTRO`           | `src/intro.c`                    | `SetUpCopyrightScreen`. |
| `CATCH_EXP`            | `src/battle_script_commands.c`   | Helper `AwardCatchExp()` called on successful ball throw. |
| `EXP_ALL`              | `src/battle_script_commands.c`   | `Cmd_getexp` — rebuilds `sentIn` to include every alive party mon. |
| `POISON_DOESNT_FAINT`  | `src/field_poison.c`             | `DoPoisonFieldEffect` clamps HP at 1. |
| `PHYSICAL_SPECIAL_SPLIT`| `src/pokemon.c`, `src/battle_script_commands.c` | `CalculateBaseDamage` and Counter/Mirror Coat routing read `gBattleMoves[move].split`. |
| `QUICK_TEST`           | `src/new_game.c`                 | `NewGameInitData` routes to `QuickTest_WarpToRoute102` + `QuickTest_SetupParty` instead of the truck. |
| `SHINY_ODDS`           | `include/constants/pokemon.h`    | `#define` read by the shiny random roll. |

---

## Mod packs

A mod pack is a JSON file that bundles any number of the above operations.
You apply them all with one command.

### When to use a mod pack

- You want to share your mod as a single file someone else can drop in.
- You're making more than ~3 changes at once.
- You want the changes under version control as a recipe rather than as a
  source-code diff.

### File format

All keys are optional:

```json
{
  "species": [
    {
      "name": "CINDERPUP",
      "types": ["FIRE"],
      "stats": [45, 60, 40, 65, 55, 40],
      "ability": "BLAZE",
      "clone_from": "GROWLITHE",
      "dex_text": "A spirited pup whose fur smolders with playful embers.",
      "learnset": [[1, "TACKLE"], [8, "EMBER"], [30, "FLAMETHROWER"]]
    }
  ],
  "moves": [
    { "name": "SAPPHIRE_FLAME", "display": "SAPPHIRE FLAME",
      "type": "FIRE", "power": 95, "accuracy": 100, "pp": 10 }
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

The sections run in the order listed above (species → moves → evolutions
→ starters → wilds → edits → config). Run the pack with:

```bash
python3 tools/agent_tools/mod_pack.py path/to/mypack.json
python3 tools/agent_tools/mod_pack.py path/to/mypack.json --verify
```

`--verify` also builds the ROM and boot-tests it afterwards.

### Ready-made packs in this repo

- **`mods/demo.json`** — small demo: adds one new Pokémon (`CINDERPUP`),
  wires it to evolve into Arcanine, spawns it on Route 103, buffs Mudkip,
  doubles shiny odds.
- **`mods/qol.json`** — quality-of-life pack: perfect IVs, 3× XP, 3×
  catch rate, never miss, unlimited TMs, instant text, run anywhere,
  skip intro, 30000 starting money, ~1/128 shiny odds.

Apply either with:

```bash
python3 tools/agent_tools/mod_pack.py mods/qol.json --verify
```

---

## Fast testing: the `QUICK_TEST` harness

Save states (`.state` / `.sst` / `.sgm`) are emulator snapshots of RAM
tied to exact ROM bytes — they don't travel between builds, so we can't
ship one. Save files (`.sav`) are technically portable but generating a
valid one from scratch would mean re-implementing Emerald's save-block
format, encryption, and checksums.

Instead, the repo ships a "baked-in save state" as a compile-time mod:
`QUICK_TEST`. When enabled, pressing **New Game** drops you on Route
102 with a ready-made test party, skipping the ~15-minute intro entirely.
Total time from `make` → first wild battle: about 10 seconds.

### How to use it

```bash
# Enable the harness (plus instant text + skip intro for speed)
python3 tools/agent_tools/tweak_config.py \
    --quick-test on --skip-intro on --instant-text on \
    --physical-special-split on

python3 tools/agent_tools/build.py
```

Load `pokeemerald_modern.gba` in an emulator, press **New Game**, pick a
name (dialogue auto-fast with `INSTANT_TEXT`), confirm. You wake up on
Route 102 with:

| Slot | Species | Lv | Moves | Why it's here |
|---|---|---|---|---|
| 1 | **Alakazam**  | 50 | Psychic, **Shadow Ball**, Calm Mind, Recover | Huge SpAtk, trash Atk. In vanilla Gen 3, Shadow Ball (Ghost → Physical by type) was useless on Alakazam. With the split on, Shadow Ball is Special and hits like a truck. |
| 2 | **Machamp**   | 50 | Cross Chop, **Ice Punch**, Rock Slide, Bulk Up | Huge Atk. Ice Punch was Special (useless) in vanilla. With the split on it's Physical and slams. |
| 3 | **Gardevoir** | 50 | Psychic, Thunderbolt, Calm Mind, Moonlight   | Control — Psychic is Special in both vanilla and modded, so her output should match across flag states. |

Walk one step into the grass. Fight a Poochyena/Zigzagoon:

1. Use Alakazam's Shadow Ball. Note the damage.
2. Rebuild with `--physical-special-split off` and do the same thing.
3. Compare. Split-on should be several times higher.

Gardevoir's Psychic is the control — damage should be identical across
both configs.

### Behaviour

- Bypasses: the truck wake-up, Birch's intro battle, Mum's running-shoes
  delivery, the bedroom save-clock cutscene, and the Pokédex gift.
- Sets: `FLAG_SYS_POKEMON_GET`, `FLAG_SYS_B_DASH`, `FLAG_SYS_POKEDEX_GET`
  so the START menu exposes the Pokémon and Pokédex options and B-dash
  running works.
- Does **not** set: badge flags, gym-door flags, any story progression.
  Don't expect Norman's gym door to open or Wally to talk to you.

### When to turn it off

```bash
python3 tools/agent_tools/tweak_config.py --quick-test off
python3 tools/agent_tools/build.py
```

Start a fresh save. The old "QUICK_TEST" save is pinned to Route 102 with
no story state, so continuing it on the non-QUICK_TEST build will look
broken.

### Customising the test party

Edit `QuickTest_SetupParty()` in `src/new_game.c` — it's a small static
array of `{ species, level, item, moves[4] }` entries. Add or swap
mons, change the warp destination in `QuickTest_WarpToRoute102()`.
Rebuild.

## Building the ROM

```bash
python3 tools/agent_tools/build.py            # normal build
python3 tools/agent_tools/build.py --clean    # wipe build/ first
python3 tools/agent_tools/build.py --verify   # build + boot test
python3 tools/agent_tools/build.py --classic  # "matches original" build (needs agbcc)
```

### Build modes

- **Modern (default)** uses today's ARM compiler
  (`arm-none-eabi-gcc`). The ROM it produces is playable but its exact
  bytes won't match the original retail Emerald ROM's checksum. Use this
  for modding.
- **Classic** uses `agbcc`, the old compiler, and produces a ROM that is
  byte-identical to retail. This only matters if you're trying to
  reproduce the original ROM for research — it requires
  cloning `pret/agbcc` into `tools/agbcc/` and running its build script.
  Normal modders will never use this.

### Outputs

- Modern: `pokeemerald_modern.gba`
- Classic: `pokeemerald.gba`

Load the `.gba` file in mGBA (recommended), Visual Boy Advance, My Boy!
(Android), Delta (iOS), or flash to a GBA cartridge via EverDrive / EZ
Flash.

---

## Testing the ROM (verifying it runs)

Even if a build succeeds, there's no guarantee the ROM actually runs —
maybe a data table is subtly inconsistent. The verification tool catches
that by booting the ROM under mGBA headlessly and watching for crash
messages.

```bash
python3 tools/agent_tools/verify_rom.py
```

Expected output on success:

```
[ok] header valid (pokeemerald_modern.gba)
[ok] mgba ran 8s without fatal errors  (reached gameplay writes)
```

What it checks:

1. The ROM's header format is valid (`gbafix -p`).
2. After 8 seconds of emulated runtime, the log contains none of:
   `fatal`, `crash`, `abort`, `undefined instruction`, `illegal`.
3. The emulator reached the stage where the game is writing to the
   sound and palette hardware — i.e. it got past early init, it isn't
   stuck on a black screen.

Options:

```bash
python3 tools/agent_tools/verify_rom.py --seconds 20        # longer run
python3 tools/agent_tools/verify_rom.py --rom mybuild.gba   # different ROM
```

Exit code is non-zero on any failure, so CI pipelines can gate on it.

---

## Troubleshooting

### "`make: cc: No such file or directory`"

You're missing the host compiler. Install it:

```bash
sudo apt install -y gcc g++ pkg-config libpng-dev zlib1g-dev
```

### "`error: no arm-none-eabi-gcc found`"

You're missing the ARM cross-compiler. Install:

```bash
sudo apt install -y gcc-arm-none-eabi binutils-arm-none-eabi libnewlib-arm-none-eabi
```

On macOS: `brew install --cask gcc-arm-embedded`.

### "`Anchor not found`" / "`expected one `};`, found …`"

A tool tried to edit a source file and couldn't find the place it was
looking for. Usually this means:

- You already applied the same change once (so it's been moved).
- Someone hand-edited the file between tool runs.

Roll back the file (`git checkout -- path/to/file.c`) and re-run.

### The build succeeds but the ROM crashes on boot

- Run `python3 tools/agent_tools/verify_rom.py` to get a diagnosis.
- If it says `fatal` / `crash` / `undefined instruction`, check your
  latest species addition for a typo in a `TYPE_`/`ABILITY_`/`MOVE_`
  name.
- If a build error names a specific `SPECIES_X` or `MOVE_X`, that entry
  is missing from one of the many lookup tables. `grep -rn SPECIES_X
  src/data/` to find which tables do and don't have it.

### "`warning: missing terminating " character`"

This is the tool output format breaking on an unexpected character in
your Pokédex text (for example, a straight quote `"` inside
`--dex-text`). Use simple ASCII text without quotes in the description.

### mgba hangs forever under xvfb

Known quirk: `mgba` sometimes ignores the soft kill signal when started
via `xvfb-run`. If the verify step looks stuck:

```bash
pkill -9 -f "mgba"
```

and re-run. This does not affect normal use of mGBA when you open the ROM
yourself.

### I added a new Pokémon but can't find it in the game

- You need to put it into something the game spawns: a wild encounter
  (`set_wild_encounter.py`), a starter slot (`set_starter.py`), a
  trainer's team (`swap_trainer_species.py`), or a give-Pokémon script.
- Just defining the species makes it *exist* in the ROM, but nothing in
  the game world references it by default.

### I changed the starter but my save still has the old starter

Saves are generated at new-game time. Existing save files have already
picked a starter and keep the one they picked. Start a **new** save to
see starter changes.

### My old save stopped working after I ran the tools

The species ID list shifts when you `add_species`, so saved Pokémon can
get reinterpreted as the wrong species. This is a known limitation. For
save compatibility across mods, make all your additions before
generating the save you care about.

---

## Gotchas and limitations

### Pokémon naming

Species names are **ALL_CAPS_AND_UNDERSCORES**, maximum 10 characters in
the in-game display (`FLARION` is fine, `SUPERDRAGONOIDE` is too long).
Underscores separate parts of a multi-word name (`MR_MIME`).

### Generation 3 only

This is Emerald. It knows nothing about:

- Gen 4+ types (no `TYPE_FAIRY`).
- Gen 4+ moves (no `MOVE_METAL_BURST`, `MOVE_FLASH_CANNON`, etc.).
- Gen 4+ abilities.

If a build fails with "`TYPE_FAIRY undeclared`", swap it out for a Gen-3
type. See `include/constants/pokemon.h` for the full list.

### No new art generation

New species reuse `--clone-from` Pokémon's sprites, palette, and
animations. Creating unique sprites is a separate, manual process (draw
a 64×64 sprite, convert to GBA format, replace the `INCBIN` reference).
Most agent modding workflows don't bother.

### Legacy things that aren't auto-wired

The tooling does not automatically update:

- Trainer-facing Pokédex flavor text differences.
- Egg moves, TM/HM compatibility, or tutor move compatibility for new
  species (they learn only their level-up moveset).
- Friendship/trust evolutions that need scripted event flags.

You can still edit those by hand in the corresponding data file; see
`src/data/pokemon/` for `egg_moves.h`, `tmhm_learnsets.h`,
`tutor_learnsets.h`.

---

## For AI agents

Read `CLAUDE.md` in this directory for agent-specific rules, including:

- Always use the `tools/agent_tools/` scripts rather than hand-editing
  data tables — the tool invariants keep 15+ lookup tables in sync.
- Use `verify_rom.py` after changes; a ROM that builds isn't
  necessarily a ROM that runs.
- Don't reorder existing `SPECIES_*` / `MOVE_*` IDs; saves and trainer
  data reference them by numeric ID, not name.
- Data files use non-ASCII bytes for in-game character mapping; use
  `pe_edit.py`'s `latin-1` helpers when writing new editing scripts.

All user-facing operations have matching slash commands in
`.claude/skills/`, discoverable via `/help`.

---

## Where to get help

- The [pret/pokeemerald](https://github.com/pret/pokeemerald) community
  for questions about the decompilation itself.
- [Poké Community / Rom Hacking](https://www.pokecommunity.com/) forums
  for general modding questions.
- Your friendly AI assistant — the tooling is designed to be usable by
  Claude Code, Cursor, and other agents. Ask them to "add a new Fire/Water
  Pokémon called X" and they should pick the right scripts.

Happy modding.

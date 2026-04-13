# pokeemerald — AI agent guide

This file briefs AI coding agents (Claude Code, Cursor, etc.) working in
the pokeemerald decompilation. Read it before you touch any data file.

For users — the people *asking* the agent to do things — the main README
is **`AGENTS.md`** in this directory. When a user wants a walkthrough,
point them there.

---

## What this repo is

A C decompilation of Pokémon Emerald (GBA, 2004). Compiling it produces
a byte-identical or near-identical `.gba` ROM file playable in any GBA
emulator.

There is **no** high-level framework on top of the C. Game data is
*hard-coded* into data tables spread across 40+ header files. "Add a
Pokémon" means inserting a matching entry into each of those tables in
the right position with the right syntax. Miss one and the build
breaks; get the position wrong and the game silently corrupts.

---

## The golden rule

**Use the `tools/agent_tools/` scripts for any structural edit.** They
exist because a correct "add Pokémon" hand-edit is ~15 files; a
correct "add move" is ~4 files; a correct "add optional mod" is 1
define + 1 gate and then lookup tables of knobs in two different
headers. The scripts encode the invariants; hand-editing loses them.

Exception: if a user explicitly wants to see a raw diff for learning
purposes, follow their lead. Otherwise, reach for the tool.

---

## Tooling cheat sheet

| Task | Command | Slash command |
|---|---|---|
| Add a new Pokémon species   | `tools/agent_tools/add_species.py`          | `/add-pokemon` |
| Edit an existing species    | `tools/agent_tools/edit_species.py`          | `/edit-species` |
| Add a new move              | `tools/agent_tools/add_move.py`              | `/add-move` |
| Add / replace an evolution  | `tools/agent_tools/add_evolution.py`         | `/add-evolution` |
| Swap starters               | `tools/agent_tools/set_starter.py`           | `/set-starter` |
| Place a wild encounter      | `tools/agent_tools/set_wild_encounter.py`    | `/set-wild-encounter` |
| Swap trainer team species   | `tools/agent_tools/swap_trainer_species.py`  | `/swap-trainer-species` |
| Toggle mods / constants     | `tools/agent_tools/tweak_config.py`          | `/tweak-config` |
| Apply a bundled JSON mod    | `tools/agent_tools/mod_pack.py mods/demo.json` | `/mod-pack` |
| List all defined species    | `tools/agent_tools/list_species.py`          | — |
| Build the ROM               | `tools/agent_tools/build.py [--classic] [--verify]` | `/build-pokeemerald` |
| Boot-test the ROM           | `tools/agent_tools/verify_rom.py`            | `/verify-rom` |

After any non-trivial change, **run `/build-pokeemerald` or
`python3 tools/agent_tools/build.py --verify` before reporting
success**. The build is the only reliable check that every data table
stayed consistent. The verify step is the only reliable check that the
ROM actually boots.

---

## How species IDs are laid out

```
SPECIES_NONE           = 0
SPECIES_BULBASAUR      = 1
…
SPECIES_CHIMECHO       = 411
SPECIES_EGG            = 412        ← new species are inserted BEFORE this
SPECIES_UNOWN_B        = NUM_SPECIES + 1   (relative; shifts automatically)
…
SPECIES_UNOWN_QMARK    = NUM_SPECIES + 27
```

`NUM_SPECIES` is `SPECIES_EGG`. The Unown form block is defined
relative to `NUM_SPECIES`, so inserting before `SPECIES_EGG` is
structurally safe — the Unown IDs slide upward with the new species,
and designated initializers (`[SPECIES_X] = {...}`) in every lookup
table keep working without any renumbering.

`NATIONAL_DEX_COUNT` (in `include/constants/pokedex.h`) tracks the last
real species (vanilla: `NATIONAL_DEX_DEOXYS`). `add_species.py`
appends after the current last and bumps the count, so chained adds
compose.

Never reorder existing `SPECIES_*` / `MOVE_*` IDs. Saves and trainer
party data reference them by numeric ID, not name; a reordering
silently corrupts everything.

---

## File map (know where data lives)

Core constants:

- `include/constants/species.h` — `SPECIES_*` IDs.
- `include/constants/pokedex.h` — `NATIONAL_DEX_*`, `HOENN_DEX_*` enums.
- `include/constants/moves.h` — `MOVE_*` IDs.
- `include/constants/abilities.h` — `ABILITY_*` IDs.
- `include/constants/pokemon.h` — types, stats, `SHINY_ODDS`, etc.
- `include/constants/battle_split.h` — `SPLIT_PHYSICAL` / `SPLIT_SPECIAL` / `SPLIT_STATUS` constants.
- `include/config.h` — compile-time mod toggles (see below).

Pokémon data:

- `src/data/pokemon/species_info.h` — base stats, types, abilities.
- `src/data/pokemon/pokedex_entries.h` — height/weight/dex-text pointer.
- `src/data/pokemon/pokedex_text.h` — the `_("...")` dex description.
- `src/data/pokemon/pokedex_orders.h` — three sort orders.
- `src/data/pokemon/level_up_learnset_pointers.h` — species → learnset.
- `src/data/pokemon/level_up_learnsets.h` — the `LEVEL_UP_MOVE(...)` arrays.
- `src/data/pokemon/evolution.h` — evolution triggers.
- `src/data/pokemon/egg_moves.h`, `tmhm_learnsets.h`, `tutor_learnsets.h`.
- `src/data/text/species_names.h` — in-game display names.

Graphics lookups (all keyed by species):

- `src/data/pokemon_graphics/*.h` — 11 separate tables.

Moves:

- `src/data/battle_moves.h`, `src/data/contest_moves.h`.
- `src/data/text/move_names.h`.

Most of the `*.h` files contain non-ASCII bytes for the in-game
character map. When you write tools, edit in `latin-1` or use
`pe_edit.py`'s helpers — UTF-8 tools will corrupt them.

---

## Optional mods

Every mod is a single `#define` in `include/config.h` (the one
exception, `SHINY_ODDS`, lives in `include/constants/pokemon.h`). Each
is gated by `#if FLAG …` at exactly one hook in the engine. Disabling
restores vanilla behavior byte-for-byte.

Integer knobs:

| `#define` | Hook | CLI |
|---|---|---|
| `SHINY_ODDS`       | shiny random roll                                     | `tweak_config.py --shiny-odds N`       |
| `EXP_MULTIPLIER`   | `battle_script_commands.c` — `calculatedExp` line     | `tweak_config.py --exp-multiplier N`   |
| `CATCH_RATE_BONUS` | `battle_script_commands.c` — post-status `odds`       | `tweak_config.py --catch-rate-bonus N` |
| `CRIT_RATE_BONUS`  | `battle_script_commands.c::Cmd_critcalc`              | `tweak_config.py --crit-rate-bonus N`  |
| `STARTING_MONEY`   | `new_game.c` — replaces the hard-coded `3000`         | `tweak_config.py --starting-money N`   |

Booleans (pass `on` / `off`):

| `#define` | Hook | CLI |
|---|---|---|
| `PERFECT_IVS`          | `pokemon.c::CreateBoxMon`                        | `--perfect-ivs on` |
| `NEVER_MISS`           | `battle_script_commands.c::Cmd_accuracycheck`    | `--never-miss on` |
| `NO_RANDOM_ENCOUNTERS` | `wild_encounter.c::StandardWildEncounter`        | `--no-random-encounters on` |
| `UNLIMITED_TMS`        | `party_menu.c::Task_LearnedMove`                 | `--unlimited-tms on` |
| `INSTANT_TEXT`         | `menu.c::GetPlayerTextSpeedDelay`                | `--instant-text on` |
| `RUN_ANYWHERE`         | `bike.c::IsRunningDisallowed`                    | `--run-anywhere on` |
| `SKIP_INTRO`           | `intro.c::SetUpCopyrightScreen`                  | `--skip-intro on` |
| `CATCH_EXP`            | `battle_script_commands.c::AwardCatchExp`         | `--catch-exp on` |
| `EXP_ALL`              | `battle_script_commands.c::Cmd_getexp`            | `--exp-all on` |
| `POISON_DOESNT_FAINT`  | `field_poison.c::DoPoisonFieldEffect`             | `--poison-doesnt-faint on` |
| `PHYSICAL_SPECIAL_SPLIT`| `pokemon.c::CalculateBaseDamage` + `battle_script_commands.c` Counter/Mirror-Coat routing | `--physical-special-split on` |
| `QUICK_TEST`           | `new_game.c::NewGameInitData` (replaces `WarpToTruck` with Route-102 warp + Lv50 party) | `--quick-test on` |

All are reachable from `mod_pack.py` via the `"config"` block using
snake_case keys. Ready-made packs:

- `mods/demo.json` — small example (adds CINDERPUP, evo, wild spawn).
- `mods/qol.json` — full quality-of-life preset (every QoL mod on).

**`CreateBoxMon` as a chokepoint**: that one function creates every
wild spawn, trainer party mon, gift mon, hatched egg, and starter. A
single `#if` there covers the entire game. When adding new "universal"
mods in the future, look for similar chokepoint functions.

**Rule of thumb for adding new mods**: if the mod targets exactly one
logical moment in gameplay (capture roll, crit roll, text render),
prefer one `#if` at that hook rather than spreading gates across call
sites. Add the define to `include/config.h`, add a row to
`tweak_config.py`'s `INT_KNOBS` or `BOOL_MODS` table, and the
`mod_pack.py` `config` block picks it up automatically.

---

## Fast in-game testing: `QUICK_TEST`

When a user asks to test a battle-side mod (split, never-miss, crit,
exp, etc.) and doesn't want to replay the intro, enable `QUICK_TEST`.
It replaces `WarpToTruck()` in `src/new_game.c` with a Route-102 warp
and a `QuickTest_SetupParty()` helper that gives the player:

- Alakazam Lv 50 — Psychic, Shadow Ball, Calm Mind, Recover
- Machamp Lv 50 — Cross Chop, Ice Punch, Rock Slide, Bulk Up
- Gardevoir Lv 50 — Psychic, Thunderbolt, Calm Mind, Moonlight

Alakazam + Shadow Ball and Machamp + Ice Punch are the two cleanest
tests of `PHYSICAL_SPECIAL_SPLIT`. Gardevoir's Psychic is the control.

Recommended bundle for any battle-mod demo:

```
tweak_config.py --quick-test on --skip-intro on --instant-text on
```

The harness sets `FLAG_SYS_POKEMON_GET`, `FLAG_SYS_B_DASH`, and
`FLAG_SYS_POKEDEX_GET` so menus and running work. It does **not** set
badge / story flags, so Norman's gym door etc. stay closed. This is a
testing harness, not a playable save.

Customise the test party by editing `QuickTest_SetupParty` (the mons
list is a plain C array). For different map starts, edit
`QuickTest_WarpToRoute102`.

When the user is done testing, flip the flag off and start a fresh
save — continuing the QUICK_TEST save on a non-QUICK_TEST build works
but the world state is obviously inconsistent.

## Building

```bash
python3 tools/agent_tools/build.py            # modern gcc, playable ROM
python3 tools/agent_tools/build.py --classic  # agbcc, matches rom.sha1
python3 tools/agent_tools/build.py --verify   # build then boot-test
```

Prereqs on a fresh machine (Ubuntu/Debian):

```bash
sudo apt install -y gcc-arm-none-eabi binutils-arm-none-eabi \
                    libnewlib-arm-none-eabi \
                    gcc g++ pkg-config libpng-dev zlib1g-dev \
                    mgba-sdl xvfb
```

The `build.py` wrapper prints install hints when the ARM toolchain is
missing rather than failing obscurely.

Outputs: `pokeemerald_modern.gba` (modern) or `pokeemerald.gba` (classic).

---

## Verifying a change

After any tool that mutates data:

```bash
python3 tools/agent_tools/build.py --verify
```

Success looks like:

```
[ok] header valid (pokeemerald_modern.gba)
[ok] mgba ran 8s without fatal errors  (reached gameplay writes)
```

What the three checks mean:

1. `gbafix -p` validates the ROM header.
2. mgba runs for 8 seconds headlessly; if it emitted any of `fatal`,
   `crash`, `abort`, `undefined instruction`, `illegal`, we abort.
3. The log must reach gameplay-stage writes (sound FIFO, palette DMA),
   proving init completed — not a black-screen freeze.

If the build succeeds but verify fails: some data-table inconsistency
compiled but blows up at runtime. Grep for the `SPECIES_*` / `MOVE_*`
name that was last touched and confirm every lookup table has an entry
for it.

---

## Anchors and atomicity

Tools locate edit points by **text anchors** — a short unique string
in a source file. If the anchor is missing or ambiguous, the tool
aborts with `ValueError` before writing any bytes. `add_species.py` is
extra careful: it snapshots every file it will touch and restores them
on *any* exception, so a partial failure doesn't leave half-written
data.

If a tool refuses to run because an anchor drifted upstream: fix the
anchor in the tool rather than reverting to hand-edits. The next agent
benefits.

---

## What the tooling deliberately does NOT do

- **Draw new sprite art.** New species reuse a `--clone-from` source's
  graphics. Replace the `INCBIN` references by hand when you want
  unique art.
- **Wire up new species into scripted encounters** (gym-leader teams,
  story battles, give-Pokémon events). Adding a species makes it
  *exist*; putting it into the game world is a separate call
  (`set_wild_encounter.py`, `swap_trainer_species.py`, etc.).
- **Create evolutions or egg moves automatically.** Use
  `add_evolution.py`; egg moves live in `src/data/pokemon/egg_moves.h`
  and currently need a hand-edit.
- **Preserve save compatibility across structural changes.** Adding
  species shifts `SPECIES_EGG` and the dex count, which invalidates
  species IDs in pre-existing saves. For players, do all additions
  before they start their playthrough.

---

## Agent habits

- **Default to terse updates.** State what you did ("added SPECIES_X,
  cloned from Y, appended to dex #N"), not how you deliberated.
- **Always verify after structural edits.** Don't report success
  without at least a successful build; ideally a `--verify` run too.
- **Preserve invariants.** Don't introduce new species-ID reshuffles,
  don't remove the `#if GATE …` pattern around optional mods, don't
  hand-edit data tables when a tool exists.
- **Write memory notes for non-obvious choices.** If you discover a
  new hook you'd like to turn into a mod, drop a note in
  `~/.claude/projects/-<path>-pokeemerald/memory/` so future sessions
  can pick it up.
- **When the user says "add X", ask yourself**: do they also want it
  in the wild? as a starter? evolving into something? Catchable
  without a stone? Offer these follow-ups rather than stopping at the
  minimal completion, but don't silently do extra work without
  confirming.

---

## Where to get help yourself

- `AGENTS.md` — the user-facing README. More examples and troubleshooting.
- `tools/agent_tools/README.md` — the script-by-script developer reference.
- `mods/*.json` — worked mod-pack examples.
- Upstream: https://github.com/pret/pokeemerald — the decomp community.

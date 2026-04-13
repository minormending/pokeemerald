# Optional mods

Every mod is a single compile-time `#define` in
[`include/config.h`](../include/config.h) (the one exception,
`SHINY_ODDS`, lives in [`include/constants/pokemon.h`](../include/constants/pokemon.h)
because that's where the game reads it). Each is gated by an `#if FLAG`
at exactly one hook in the engine, so disabling restores vanilla
behaviour byte-for-byte.

You flip mods with
[`tools/agent_tools/tweak_config.py`](../tools/agent_tools/tweak_config.py),
the [`/tweak-config`](../.claude/skills/tweak-config/SKILL.md) slash
command, or a [mod pack](MOD_PACKS.md).

---

## Integer knobs (numeric dials)

| Knob | What it does | Vanilla | Example |
|---|---|---|---|
| `--shiny-odds N`       | Shiny probability numerator over 65536. | 8 (~1/8192) | `--shiny-odds 512` ≈ 1/128 |
| `--exp-multiplier N`   | Multiplies XP gained from each victory. | 1 | `--exp-multiplier 3` triples XP |
| `--catch-rate-bonus N` | Multiplies capture odds on every throw. | 1 | `--catch-rate-bonus 3` ≈ "Ultra Ball on everything" |
| `--crit-rate-bonus N`  | Adds stages to the crit chance index. 3 ≈ always crit. | 0 | `--crit-rate-bonus 3` |
| `--starting-money N`   | Pokédollars on a new save. | 3000 | `--starting-money 30000` |

## Boolean switches

Pass `on` / `off` (also accepts `true/false`, `1/0`).

| Switch | What it does |
|---|---|
| `--perfect-ivs on`           | Every Pokémon — wild, trainer, gift, starter, hatched — gets 31 IVs in all six stats. |
| `--never-miss on`            | Your moves never miss. The accuracy roll is skipped when you're the attacker. |
| `--no-random-encounters on`  | Disables all random wild battles. Useful for route-making playtests. |
| `--unlimited-tms on`         | TMs are not consumed when a Pokémon learns them. (HMs are already reusable.) |
| `--instant-text on`          | All in-game text appears immediately, overriding the "Text Speed" option. |
| `--run-anywhere on`          | You can run indoors and in other maps that normally block running. Tall grass still blocks. |
| `--skip-intro on`            | Skips the Latios/Latias intro cinematic. Goes copyright → title screen directly. |
| `--catch-exp on`             | Catching a Pokémon awards XP to every alive party member. (Gen 6+ behavior.) |
| `--exp-all on`               | Every alive party member gains XP from every KO, divided evenly. |
| `--poison-doesnt-faint on`   | Field-poison ticks stop at 1 HP instead of fainting. No more white-outs from walking. |
| `--physical-special-split on` | Per-move Physical/Special category instead of type-based. Gen 4+ style — Shadow Ball becomes Special, Ice Punch becomes Physical, etc. |
| `--quick-test on`            | Skip intro and drop the player on Route 102 with a Lv 50 test party on new game. See [QUICK_TEST.md](QUICK_TEST.md). |

## Combining

Any mix in one command:

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

## Turning a mod off

Booleans accept `off`:

```bash
python3 tools/agent_tools/tweak_config.py --perfect-ivs off
```

Integers: set them back to the vanilla value (see the table):

```bash
python3 tools/agent_tools/tweak_config.py --shiny-odds 8 --exp-multiplier 1
```

---

## Hook reference (for developers)

Each mod is one `#if FLAG …` block at a single location.

| Mod | File | Function / block |
|---|---|---|
| `PERFECT_IVS`          | `src/pokemon.c`                  | `CreateBoxMon` — the single function every Pokémon creation goes through. |
| `EXP_MULTIPLIER`       | `src/battle_script_commands.c`   | Where `calculatedExp = … / 7` is computed. |
| `CATCH_RATE_BONUS`     | `src/battle_script_commands.c`   | Right after status (sleep/poison) capture bonuses. |
| `NEVER_MISS`           | `src/battle_script_commands.c`   | `Cmd_accuracycheck`. |
| `CRIT_RATE_BONUS`      | `src/battle_script_commands.c`   | `Cmd_critcalc`. |
| `NO_RANDOM_ENCOUNTERS` | `src/wild_encounter.c`           | `StandardWildEncounter` early return. |
| `UNLIMITED_TMS`        | `src/party_menu.c`               | `Task_LearnedMove`. |
| `STARTING_MONEY`       | `src/new_game.c`                 | Hard-coded 3000 in `NewGameInitData`. |
| `INSTANT_TEXT`         | `src/menu.c`                     | `GetPlayerTextSpeedDelay`. |
| `RUN_ANYWHERE`         | `src/bike.c`                     | `IsRunningDisallowed`. |
| `SKIP_INTRO`           | `src/intro.c`                    | `SetUpCopyrightScreen`. |
| `CATCH_EXP`            | `src/battle_script_commands.c`   | Static helper `AwardCatchExp()` called on successful ball throw. |
| `EXP_ALL`              | `src/battle_script_commands.c`   | `Cmd_getexp` — rebuilds `sentIn` to include every alive party mon. |
| `POISON_DOESNT_FAINT`  | `src/field_poison.c`             | `DoPoisonFieldEffect` HP clamp. |
| `PHYSICAL_SPECIAL_SPLIT`| `src/pokemon.c`, `src/battle_script_commands.c` | `CalculateBaseDamage` + Counter/Mirror-Coat tracking read `gBattleMoves[move].split`. |
| `QUICK_TEST`           | `src/new_game.c`                 | `NewGameInitData` routes through `QuickTest_WarpToRoute102` + `QuickTest_SetupParty`. |
| `SHINY_ODDS`           | `include/constants/pokemon.h`    | `#define` consumed by the shiny random roll. |

---

## Related docs

- [AGENTS.md](../AGENTS.md) — main user guide.
- [MOD_PACKS.md](MOD_PACKS.md) — applying many mods at once from a JSON file.
- [QUICK_TEST.md](QUICK_TEST.md) — fast iteration harness.
- [tools/agent_tools/README.md](../tools/agent_tools/README.md) — developer/script reference.

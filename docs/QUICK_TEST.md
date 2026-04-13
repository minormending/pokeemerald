# Fast testing: the `QUICK_TEST` harness

## The problem

You've changed a battle-side mod (say, the Physical/Special split) and
you want to see it in action. Normally that means:

1. Play the 10-minute Birch intro.
2. Name your character.
3. Walk to the lab, pick a starter.
4. Walk back, fight May or Brendan.
5. Leave Littleroot, walk to Route 102.
6. Grind a few levels to reach something interesting.

Every rebuild. Repeatedly.

Save states (`.state` / `.sst` / `.sgm`) could bypass that — but
they're emulator-specific snapshots of RAM, pinned to the exact ROM
bytes they were captured against. Any rebuild invalidates them. Save
files (`.sav`) would be portable but generating a valid one from
scratch means re-implementing Emerald's save-block format, encryption,
and checksums.

## The fix

`QUICK_TEST` is a compile-time testing harness that bakes a "starting
save state" straight into the new-game path. When enabled, pressing
**New Game** replaces the truck sequence with a warp to Route 102 and
hands you a pre-built Lv 50 party. Total time from `make` to first
wild battle: about 10 seconds.

## Usage

```bash
# Recommended bundle for battle-mod testing
python3 tools/agent_tools/tweak_config.py \
    --quick-test on \
    --skip-intro on \
    --instant-text on \
    --physical-special-split on

python3 tools/agent_tools/build.py
```

Load `pokeemerald_modern.gba` in mGBA / Visual Boy Advance / any GBA
emulator. Press **New Game**. Fast-forward through the Birch dialogue
(it's 0-delay text thanks to `INSTANT_TEXT`). Name your character.

You wake up on **Route 102** with this team:

| Slot | Species | Lv | Moves | Why it's here |
|---|---|---|---|---|
| 1 | **Alakazam**  | 50 | Psychic, **Shadow Ball**, Calm Mind, Recover | Huge SpAtk, trash Atk. In vanilla Gen 3, Shadow Ball (Ghost → Physical by type) was useless on Alakazam. With `PHYSICAL_SPECIAL_SPLIT` on, Shadow Ball is Special and hits like a truck. |
| 2 | **Machamp**   | 50 | Cross Chop, **Ice Punch**, Rock Slide, Bulk Up | Huge Atk. Ice Punch was Special (useless) in vanilla. With the split on it's Physical and slams. |
| 3 | **Gardevoir** | 50 | Psychic, Thunderbolt, Calm Mind, Moonlight  | Control — Psychic is Special in both vanilla and modded. Her output should match across flag states. |

Walk one step into the grass. Fight a Poochyena or Zigzagoon:

1. Use Alakazam's Shadow Ball. Note the damage.
2. Rebuild with `--physical-special-split off` and do the same thing.
3. Compare. Split-on should be several times higher.

Repeat with Machamp's Ice Punch. Gardevoir's Psychic is the control —
her damage should be identical across both configs.

## What the harness sets and doesn't set

### Sets

- `FLAG_SYS_POKEMON_GET` — so the START menu shows POKEMON.
- `FLAG_SYS_B_DASH` — so holding B makes you run.
- `FLAG_SYS_POKEDEX_GET` — so the summary screen shows full data.

### Does not set

- Badge flags (no gym doors open).
- Story progression flags (Wally doesn't exist yet, Norman won't
  talk to you, the S.S. Tidal is locked, etc.).
- Hidden Machines (no Surf, no Fly).
- Pokémart / Poké Center flags past their defaults.

This is intentional — it's a **testing harness**, not a playable save.
Trying to play through the story from a QUICK_TEST save will be
broken.

## Turning it off

```bash
python3 tools/agent_tools/tweak_config.py --quick-test off
python3 tools/agent_tools/build.py
```

Start a **fresh** save. Continuing the QUICK_TEST save on a non-harness
build technically works, but world state is obviously inconsistent
(you're on Route 102 with no story flags set).

## Customising the test party

Open [`src/new_game.c`](../src/new_game.c) and find `QuickTest_SetupParty`.
The mons list is a plain C array:

```c
struct {
    u16 species;
    u8  level;
    u16 item;
    u16 moves[4];
} mons[] = {
    { SPECIES_ALAKAZAM, 50, ITEM_NONE,
      { MOVE_PSYCHIC, MOVE_SHADOW_BALL, MOVE_CALM_MIND, MOVE_RECOVER } },
    ...
};
```

Add entries up to 6 party slots. Use any `SPECIES_*` from
[`include/constants/species.h`](../include/constants/species.h) and
any `MOVE_*` from
[`include/constants/moves.h`](../include/constants/moves.h).

For a different starting map, edit `QuickTest_WarpToRoute102()` — the
`MAP_ROUTE102` / `5, 5` args are the destination and spawn tile.

Rebuild and your new party appears on the next New Game.

## Why not ship a .sav file?

Because the save format:

- Is 128 KB split across save blocks with rolling integrity checksums.
- Uses per-save encryption (a random key XORs every block).
- Stores species / move / flag IDs that shift when you add content to
  the ROM.

A pre-built `.sav` would work for exactly one build and break on the
next content change. The QUICK_TEST path regenerates the "save state"
deterministically on every New Game, so it's always in sync with the
ROM it was built into.

---

## Related docs

- [AGENTS.md](../AGENTS.md) — main user guide.
- [MODS.md](MODS.md) — full optional-mods reference.
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — if something doesn't work.

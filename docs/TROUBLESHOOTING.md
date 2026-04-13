# Troubleshooting

Common problems when building and modding pokeemerald with this
tooling.

## Build errors

### `make: cc: No such file or directory`

You're missing the host compiler. Install:

```bash
sudo apt install -y gcc g++ pkg-config libpng-dev zlib1g-dev
```

### `error: no arm-none-eabi-gcc found`

Missing the ARM cross-compiler. Install:

```bash
# Ubuntu/Debian/WSL
sudo apt install -y gcc-arm-none-eabi binutils-arm-none-eabi libnewlib-arm-none-eabi

# macOS
brew install --cask gcc-arm-embedded
```

Windows: use WSL2 and follow the Ubuntu instructions.

### `error: 'TYPE_FAIRY' undeclared`

Generation 3 doesn't have the Fairy type. Pick another type from
[`include/constants/pokemon.h`](../include/constants/pokemon.h).

### `error: 'MOVE_XYZ' undeclared`

You referenced a Gen 4+ move name that doesn't exist in Emerald's
move table. Either pick a Gen 3 move or add the move first with
`add_move.py`.

### Build succeeds but the ROM crashes on boot

Run the verifier:

```bash
python3 tools/agent_tools/verify_rom.py
```

If it reports `fatal`, `crash`, `abort`, or `undefined instruction`,
look at your most recent addition for a typo in a constant name
(`TYPE_`, `ABILITY_`, `MOVE_`, `ITEM_`). The compiler accepts the
typo because it's substituted as `0` silently.

If a build error names a specific `SPECIES_X` or `MOVE_X`, that name is
missing from one of the many lookup tables. `grep -rn "SPECIES_X"
src/data/` to find which tables do and don't have it.

## Tool errors

### `Anchor not found` / `Anchor not unique`

A script tried to edit a source file and couldn't find (or found
multiple copies of) the specific text it was looking for. Usually
this means:

- You already applied the same change once.
- Someone hand-edited the file between tool runs.

Roll back the file:

```bash
git checkout -- path/to/file.c
```

Then rerun the tool.

### `warning: missing terminating " character`

Output-format quirk. You passed a quote character inside `--dex-text`
or `--display`. Stick to ASCII text without quotes.

### mGBA hangs forever under `xvfb-run`

Known cosmetic issue — `xvfb-run` sometimes doesn't forward SIGTERM.
Kill it manually:

```bash
pkill -9 -f mgba
```

Does not affect normal use of mGBA when you open the ROM yourself.

## Gameplay issues

### I added a new Pokémon but can't find it in the game

Adding a species just makes it *exist* in the ROM. To put it into the
game world you need one of:

- `set_wild_encounter.py` — catch it in grass / water / fishing.
- `set_starter.py` — offer it as a starter.
- `swap_trainer_species.py` — put it on a trainer's team.
- A custom event script — if you want it as a gift.

### I changed the starter but my save still has the old starter

Saves are generated at new-game time. Existing save files have already
picked a starter. Start a new save to see starter changes.

### My old save stopped working after I ran the tools

The species ID list shifts when you `add_species`, so saved Pokémon
can get reinterpreted as the wrong species. Known limitation. For save
compatibility across mods, make all your additions *before* generating
the save you care about.

### "Gen 4" moves or types aren't working

Emerald is Generation 3. It has:

- 17 types (no Fairy).
- Moves up to `MOVE_PSYCHO_BOOST` (354).
- Abilities up to Air Lock (77).

New types and many new moves / abilities would require substantial
refactoring beyond the scope of this tooling.

### Perfect IVs / other mods don't apply to my existing Pokémon

`PERFECT_IVS` affects Pokémon that go through `CreateBoxMon` — wild
spawns, trainer teams, gifts, hatched eggs, new starters. It does
**not** retroactively fix IVs on Pokémon you already own. Catch fresh
ones or use debug tools to modify existing IVs.

## Debug tips

### See every species defined in the ROM

```bash
python3 tools/agent_tools/list_species.py | less
```

### Verify a specific mod actually compiled in

```bash
python3 tools/agent_tools/tweak_config.py      # with no flags, shows the rule "pass at least one flag"
grep "^#define PERFECT_IVS" include/config.h
```

### Boot-test after every change

```bash
python3 tools/agent_tools/build.py --verify
```

### Reset to vanilla

```bash
# Turn off every optional mod
python3 tools/agent_tools/tweak_config.py \
    --perfect-ivs off --never-miss off --unlimited-tms off \
    --instant-text off --run-anywhere off --skip-intro off \
    --catch-exp off --exp-all off --poison-doesnt-faint off \
    --physical-special-split off --quick-test off \
    --no-random-encounters off \
    --exp-multiplier 1 --catch-rate-bonus 1 --crit-rate-bonus 0 \
    --starting-money 3000 --shiny-odds 8

python3 tools/agent_tools/build.py
```

---

## Related docs

- [AGENTS.md](../AGENTS.md) — main user guide.
- [MODS.md](MODS.md) — full optional-mods reference.
- [QUICK_TEST.md](QUICK_TEST.md) — testing harness.

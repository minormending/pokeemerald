# Pokémon Emerald

This is a decompilation of Pokémon Emerald.

It builds the following ROM:

* [**pokeemerald.gba**](https://datomatic.no-intro.org/index.php?page=show_record&s=23&n=1961) `sha1: f3ae088181bf583e55daf962a92bb46f4f1d07b7`

To set up the repository, see [INSTALL.md](INSTALL.md).

For contacts and other pret projects, see [pret.github.io](https://pret.github.io/).

---

## Modding this fork

This fork adds a Python tooling layer for adding Pokémon, moves,
evolutions, starters, wild encounters, trainer-team swaps, and
compile-time gameplay mods (perfect IVs, never-miss, Gen 4+
physical/special split, and more) — one command each, no hand-editing
of data tables.

### Documentation

| Doc | What it covers |
|---|---|
| [**AGENTS.md**](AGENTS.md) | **Start here.** Install, first build, "what you can do", step-by-step tutorial. |
| [CLAUDE.md](CLAUDE.md) | Rules and context for AI coding agents (Claude Code, Cursor). |
| [docs/MODS.md](docs/MODS.md) | Full reference for the optional compile-time mods and cheat flags. |
| [docs/MOD_PACKS.md](docs/MOD_PACKS.md) | Applying multiple mods at once from a JSON recipe. |
| [docs/QUICK_TEST.md](docs/QUICK_TEST.md) | Fast in-game testing harness — New Game drops you on Route 102 with a Lv 50 team. |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Problem → fix list. |
| [tools/agent_tools/README.md](tools/agent_tools/README.md) | Script-by-script developer reference. |

### Two-line quick start

```bash
python3 tools/agent_tools/build.py --verify     # build and self-test
python3 tools/agent_tools/tweak_config.py --help   # see every mod flag
```

Output ROM lands at `pokeemerald_modern.gba`.

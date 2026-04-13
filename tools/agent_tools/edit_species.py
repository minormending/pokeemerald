#!/usr/bin/env python3
"""Modify an existing species' entry in src/data/pokemon/species_info.h.

Useful for rebalance / difficulty mods. Any `--stat` you omit stays as-is.

Example:
  # Buff Treecko to 80 attack / 100 speed.
  python3 tools/agent_tools/edit_species.py --species TREECKO \\
      --base-attack 80 --base-speed 100

  # Re-type Pikachu as Electric/Fairy. (Fairy doesn't exist in Gen 3, but
  # the same mechanism applies — use valid TYPE_* names.)
  python3 tools/agent_tools/edit_species.py --species PIKACHU \\
      --type1 ELECTRIC --type2 NORMAL

  # Change abilities.
  python3 tools/agent_tools/edit_species.py --species SNORLAX \\
      --ability1 THICK_FAT --ability2 GLUTTONY
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E


# Map of CLI flag → the `.field` name in the struct literal.
STAT_FIELDS = {
    "base_hp":        ("baseHP",        int),
    "base_attack":    ("baseAttack",    int),
    "base_defense":   ("baseDefense",   int),
    "base_speed":     ("baseSpeed",     int),
    "base_sp_attack": ("baseSpAttack",  int),
    "base_sp_defense":("baseSpDefense", int),
    "catch_rate":     ("catchRate",     int),
    "exp_yield":      ("expYield",      int),
    "egg_cycles":     ("eggCycles",     int),
}


def replace_scalar(block: str, field: str, value) -> str:
    """Replace `.field = ...,` inside a struct literal block."""
    pat = re.compile(rf"(\.{field}\s*=\s*)([^,\n]+)(,)")
    m = pat.search(block)
    if not m:
        raise SystemExit(f"field .{field} not found in species entry")
    return block[:m.start()] + m.group(1) + str(value) + m.group(3) + block[m.end():]


def find_species_block(text: str, species: str) -> tuple[int, int]:
    """Return (start, end) slice covering the `[SPECIES_X] = { ... },` entry."""
    anchor = f"[SPECIES_{species}] ="
    idx = text.find(anchor)
    if idx < 0:
        raise SystemExit(f"SPECIES_{species} not found in species_info.h")
    # find the opening `{` then walk braces
    brace = text.index("{", idx)
    depth = 0
    i = brace
    while i < len(text):
        if text[i] == "{": depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                # include trailing comma if present
                j = i + 1
                while j < len(text) and text[j] in " ,\t": j += 1
                return idx, j
        i += 1
    raise SystemExit("brace matching failed")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--species", required=True, help="SPECIES_* name without prefix")
    for flag in STAT_FIELDS:
        ap.add_argument(f"--{flag.replace('_','-')}", type=int)
    ap.add_argument("--type1")
    ap.add_argument("--type2")
    ap.add_argument("--ability1")
    ap.add_argument("--ability2")
    ap.add_argument("--growth-rate")
    ap.add_argument("--body-color")
    a = ap.parse_args(argv)

    text = E.read(P.SPECIES_INFO_H)
    s, e = find_species_block(text, a.species)
    block = text[s:e]

    changes: list[str] = []
    for flag, (field, _type) in STAT_FIELDS.items():
        val = getattr(a, flag, None)
        if val is not None:
            block = replace_scalar(block, field, val)
            changes.append(f"{field}={val}")

    if a.type1 or a.type2:
        # Replace `.types = { TYPE_X, TYPE_Y },`
        tpat = re.compile(r"(\.types\s*=\s*\{\s*)TYPE_(\w+)(\s*,\s*)TYPE_(\w+)(\s*\}\s*,)")
        m = tpat.search(block)
        if not m:
            raise SystemExit(".types line not found")
        t1 = a.type1 or m.group(2)
        t2 = a.type2 or m.group(4)
        block = block[:m.start()] + m.group(1) + f"TYPE_{t1}" + m.group(3) + f"TYPE_{t2}" + m.group(5) + block[m.end():]
        changes.append(f"types=[{t1},{t2}]")

    if a.ability1 or a.ability2:
        apat = re.compile(r"(\.abilities\s*=\s*\{\s*)ABILITY_(\w+)(\s*,\s*)ABILITY_(\w+)(\s*\}\s*,)")
        m = apat.search(block)
        if not m:
            raise SystemExit(".abilities line not found")
        ab1 = a.ability1 or m.group(2)
        ab2 = a.ability2 or m.group(4)
        block = block[:m.start()] + m.group(1) + f"ABILITY_{ab1}" + m.group(3) + f"ABILITY_{ab2}" + m.group(5) + block[m.end():]
        changes.append(f"abilities=[{ab1},{ab2}]")

    if a.growth_rate:
        block = re.sub(r"(\.growthRate\s*=\s*)GROWTH_\w+(,)",
                       rf"\1GROWTH_{a.growth_rate}\2", block, count=1)
        changes.append(f"growthRate={a.growth_rate}")
    if a.body_color:
        block = re.sub(r"(\.bodyColor\s*=\s*)BODY_COLOR_\w+(,)",
                       rf"\1BODY_COLOR_{a.body_color}\2", block, count=1)
        changes.append(f"bodyColor={a.body_color}")

    if not changes:
        ap.error("pass at least one change flag (see --help)")
    text = text[:s] + block + text[e:]
    E.write(P.SPECIES_INFO_H, text)
    print(f"SPECIES_{a.species}: " + ", ".join(changes))
    return 0


if __name__ == "__main__":
    sys.exit(main())

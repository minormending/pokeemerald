#!/usr/bin/env python3
"""Append a new move to pokeemerald.

Files touched:
  include/constants/moves.h         (adds MOVE_<NAME> define, bumps MOVES_COUNT)
  src/data/text/move_names.h        (display name)
  src/data/battle_moves.h           (BattleMove entry)
  src/data/contest_moves.h          (ContestMove entry, defaults to TOUGH)

The move's animation falls through to a default (Pound's) unless wired up
separately — good enough to compile, battle, and be selectable.

Example:
  python3 tools/agent_tools/add_move.py --name SAPPHIRE_FLAME \\
      --display "SAPPHIRE FLAME" --type FIRE --power 95 --accuracy 100 --pp 10
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E


def update_moves_h(name: str) -> int:
    text = E.read(P.MOVES_H)
    # Find "#define MOVES_COUNT N" — value is last-defined move + 1.
    needle = "#define MOVES_COUNT "
    start = text.index(needle)
    line_end = text.index("\n", start)
    moves_count = int(text[start:line_end].split()[-1])
    new_id = moves_count
    new_count = moves_count + 1
    insertion = f"#define MOVE_{name} {new_id}\n\n"
    text = text[:start] + insertion + f"#define MOVES_COUNT {new_count}" + text[line_end:]
    E.write(P.MOVES_H, text)
    return new_id


def update_move_names(name: str, display: str) -> None:
    text = E.read(P.MOVE_NAMES_H)
    line = f"    [MOVE_{name}] = _(\"{display}\"),\n"
    closing = "};\n"
    idx = text.rindex(closing)
    text = text[:idx] + line + text[idx:]
    E.write(P.MOVE_NAMES_H, text)


def update_battle_moves(name: str, power: int, mtype: str, acc: int, pp: int,
                        effect: str, target: str, priority: int,
                        secondary: int, flags: str, split: str) -> None:
    text = E.read(P.BATTLE_MOVES_H)
    block = f"""
    [MOVE_{name}] =
    {{
        .effect = EFFECT_{effect},
        .power = {power},
        .type = TYPE_{mtype},
        .accuracy = {acc},
        .pp = {pp},
        .secondaryEffectChance = {secondary},
        .target = MOVE_TARGET_{target},
        .priority = {priority},
        .flags = {flags},
        .split = SPLIT_{split},
    }},
"""
    closing = "\n};\n"
    idx = text.rindex(closing)
    text = text[:idx] + block + text[idx:]
    E.write(P.BATTLE_MOVES_H, text)


def update_contest_moves(name: str) -> None:
    text = E.read(P.CONTEST_MOVES_H)
    block = f"""
    [MOVE_{name}] =
    {{
        .effect = CONTEST_EFFECT_HIGHLY_APPEALING,
        .contestCategory = CONTEST_CATEGORY_TOUGH,
        .comboStarterId = 0,
        .comboMoves = {{0}},
    }},
"""
    anchor = "\nconst struct ContestEffect gContestEffects[]"
    idx = text.index(anchor)
    # Back up to the `};\n` that closes gContestMoves before this anchor.
    closing_idx = text.rfind("};\n", 0, idx)
    text = text[:closing_idx] + block + text[closing_idx:]
    E.write(P.CONTEST_MOVES_H, text)


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True, help="UPPER_SNAKE move identifier")
    p.add_argument("--display", required=True, help='Display name, e.g. "SAPPHIRE FLAME"')
    p.add_argument("--type", default="NORMAL")
    p.add_argument("--power", type=int, default=40)
    p.add_argument("--accuracy", type=int, default=100)
    p.add_argument("--pp", type=int, default=10)
    p.add_argument("--effect", default="HIT")
    p.add_argument("--target", default="SELECTED")
    p.add_argument("--priority", type=int, default=0)
    p.add_argument("--secondary", type=int, default=0)
    p.add_argument("--flags",
                   default="FLAG_PROTECT_AFFECTED | FLAG_MIRROR_MOVE_AFFECTED | FLAG_KINGS_ROCK_AFFECTED")
    p.add_argument("--split", choices=["PHYSICAL", "SPECIAL", "STATUS"],
                   help="Move category under PHYSICAL_SPECIAL_SPLIT. "
                        "Defaults: STATUS if power==0, else PHYSICAL.")
    a = p.parse_args(argv)

    if a.split is None:
        a.split = "STATUS" if a.power == 0 else "PHYSICAL"

    new_id = update_moves_h(a.name)
    update_move_names(a.name, a.display)
    update_battle_moves(a.name, a.power, a.type, a.accuracy, a.pp,
                        a.effect, a.target, a.priority, a.secondary, a.flags,
                        a.split)
    update_contest_moves(a.name)
    print(f"Added MOVE_{a.name} = {new_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

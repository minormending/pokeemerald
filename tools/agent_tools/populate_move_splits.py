#!/usr/bin/env python3
"""Rewrite src/data/battle_moves.h to inject `.split = SPLIT_X,` into every
move entry, using the Gen 4+ categorization from move_splits.py.

Idempotent: running twice is a no-op. Running after you add new moves with
add_move.py (which now writes its own .split line) is safe — this tool only
adds the line if it's absent.

Usage:
  python3 tools/agent_tools/populate_move_splits.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E
from move_splits import lookup, MOVE_SPLITS


def main() -> int:
    text = E.read(P.BATTLE_MOVES_H)

    # Match each `[MOVE_NAME] = { ... }` block.
    pat = re.compile(r"(\[MOVE_([A-Z0-9_]+)\]\s*=\s*\{)(.*?)(\n\s*\})", re.DOTALL)

    added = skipped = unknown = 0

    def repl(m: re.Match) -> str:
        nonlocal added, skipped, unknown
        head, name, body, tail = m.group(1), m.group(2), m.group(3), m.group(4)
        if ".split" in body:
            skipped += 1
            return m.group(0)
        if name not in MOVE_SPLITS:
            unknown += 1
            print(f"warn: no split for MOVE_{name}; defaulting to STATUS", file=sys.stderr)
        split = lookup(name)
        # Insert before the closing brace, at the indentation of the other fields.
        # Most fields are indented 8 spaces; match whatever the body uses.
        indent_m = re.search(r"\n( +)\.\w", body)
        indent = indent_m.group(1) if indent_m else "        "
        new_field = f"\n{indent}.split = SPLIT_{split},"
        added += 1
        return head + body + new_field + tail

    new_text = pat.sub(repl, text)
    if new_text == text:
        print(f"no changes (skipped={skipped})")
        return 0

    E.write(P.BATTLE_MOVES_H, new_text)
    print(f"ok: added={added} skipped={skipped} unknown={unknown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

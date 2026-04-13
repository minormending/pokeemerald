#!/usr/bin/env python3
"""Swap one of the three starter Pokémon.

Example:
  python3 tools/agent_tools/set_starter.py --slot grass --species FLARION

Slots: grass (default: TREECKO), fire (TORCHIC), water (MUDKIP).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E

STARTERS_C = P.ROOT / "src/starter_choose.c"
SLOT_ORDER = ["grass", "fire", "water"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True, choices=SLOT_ORDER)
    ap.add_argument("--species", required=True,
                    help="SPECIES_* name (without the SPECIES_ prefix).")
    a = ap.parse_args(argv)

    # Confirm the species constant exists.
    species_h = E.read(P.SPECIES_H)
    if not re.search(rf"^#define SPECIES_{a.species}\b", species_h, re.MULTILINE):
        raise SystemExit(f"SPECIES_{a.species} not defined. Add it first with add_species.py.")

    text = E.read(STARTERS_C)
    m = re.search(
        r"(static const u16 sStarterMon\[STARTER_MON_COUNT\] =\s*\{)([^}]*)(\};)",
        text, re.DOTALL,
    )
    if not m:
        raise SystemExit("could not locate sStarterMon[] in starter_choose.c")

    entries = [e.strip() for e in m.group(2).split(",") if e.strip()]
    if len(entries) != 3:
        raise SystemExit(f"expected 3 starter entries, found {len(entries)}")

    idx = SLOT_ORDER.index(a.slot)
    old = entries[idx]
    entries[idx] = f"SPECIES_{a.species}"
    new_body = "\n    " + ",\n    ".join(entries) + ",\n"
    new_block = m.group(1) + new_body + m.group(3)
    text = text[:m.start()] + new_block + text[m.end():]
    E.write(STARTERS_C, text)
    print(f"starter[{a.slot}]: {old} -> SPECIES_{a.species}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

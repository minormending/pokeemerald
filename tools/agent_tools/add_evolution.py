#!/usr/bin/env python3
"""Add (or replace) an evolution entry for a species.

Examples:
  # Flarion evolves into Charizard at level 36.
  python3 tools/agent_tools/add_evolution.py \\
      --from FLARION --to CHARIZARD --method LEVEL --param 36

  # Leafling evolves via Leaf Stone.
  python3 tools/agent_tools/add_evolution.py \\
      --from LEAFLING --to ROSELIA --method ITEM --param ITEM_LEAF_STONE

Method = one of LEVEL, FRIENDSHIP, FRIENDSHIP_DAY, FRIENDSHIP_NIGHT,
TRADE, TRADE_ITEM, ITEM, LEVEL_ATK_GT_DEF, LEVEL_ATK_EQ_DEF,
LEVEL_ATK_LT_DEF, LEVEL_SILCOON, LEVEL_CASCOON, LEVEL_NINJASK,
LEVEL_SHEDINJA, BEAUTY.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E

EVOLUTION_H = P.ROOT / "src/data/pokemon/evolution.h"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    # `from` is a Python keyword, so expose as --from via dest override.
    ap.add_argument("--from", dest="src", required=True,
                    help="Pre-evolution species (without SPECIES_).")
    ap.add_argument("--to", dest="dst", required=True,
                    help="Post-evolution species (without SPECIES_).")
    ap.add_argument("--method", default="LEVEL",
                    help="Evolution trigger; see --help header.")
    ap.add_argument("--param", default="0",
                    help="For LEVEL: the level number. For ITEM: ITEM_* name. For FRIENDSHIP: 0.")
    a = ap.parse_args(argv)

    species_h = E.read(P.SPECIES_H)
    for needed in (a.src, a.dst):
        if not re.search(rf"^#define SPECIES_{needed}\b", species_h, re.MULTILINE):
            raise SystemExit(f"SPECIES_{needed} is not defined.")

    line = (f"    [SPECIES_{a.src}] = "
            f"{{{{EVO_{a.method}, {a.param}, SPECIES_{a.dst}}}}},\n")

    text = E.read(EVOLUTION_H)
    existing = re.search(rf"^    \[SPECIES_{a.src}\]\s*=[^\n]*\n", text, re.MULTILINE)
    if existing:
        text = text[:existing.start()] + line + text[existing.end():]
        verb = "replaced"
    else:
        # Insert before the closing `};`.
        closing = "};\n"
        idx = text.rindex(closing)
        text = text[:idx] + line + text[idx:]
        verb = "added"
    E.write(EVOLUTION_H, text)
    print(f"{verb} evolution: SPECIES_{a.src} --[EVO_{a.method} {a.param}]--> SPECIES_{a.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

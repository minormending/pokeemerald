#!/usr/bin/env python3
"""Replace a wild-encounter slot in src/data/wild_encounters.json.

Example:
  # Put FLARION at slot 0 of ROUTE101's land encounters, level 5-5.
  python3 tools/agent_tools/set_wild_encounter.py \\
      --map MAP_ROUTE101 --field land_mons --slot 0 \\
      --species FLARION --level 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P

WILD_JSON = P.ROOT / "src/data/wild_encounters.json"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True)
    ap.add_argument("--field", required=True,
                    choices=["land_mons", "water_mons", "rock_smash_mons", "fishing_mons"])
    ap.add_argument("--slot", type=int, required=True)
    ap.add_argument("--species", required=True, help="Name without SPECIES_ prefix.")
    ap.add_argument("--level", type=int, required=True)
    ap.add_argument("--max-level", type=int)
    a = ap.parse_args(argv)

    data = json.loads(WILD_JSON.read_text())
    groups = data["wild_encounter_groups"]
    # The main (non-Altering-Cave) group is the first one.
    target = None
    for grp in groups:
        for enc in grp["encounters"]:
            if enc["map"] == a.map:
                target = enc
                break
        if target:
            break
    if not target:
        raise SystemExit(f"map {a.map!r} not found in wild_encounters.json")
    if a.field not in target:
        raise SystemExit(f"{a.map} has no {a.field} block")
    mons = target[a.field]["mons"]
    if not 0 <= a.slot < len(mons):
        raise SystemExit(f"slot must be 0..{len(mons)-1} for {a.map}/{a.field}")
    old = mons[a.slot]
    mons[a.slot] = {
        "min_level": a.level,
        "max_level": a.max_level or a.level,
        "species": f"SPECIES_{a.species}",
    }
    WILD_JSON.write_text(json.dumps(data, indent=2) + "\n")
    print(f"{a.map}/{a.field}[{a.slot}]: {old['species']} -> SPECIES_{a.species}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

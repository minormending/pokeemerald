#!/usr/bin/env python3
"""Swap a species in a trainer's party.

Locates `sParty_<Trainer>[]` in src/data/trainer_parties.h and rewrites every
`.species = SPECIES_OLD,` to `.species = SPECIES_NEW,` inside that block.

Example:
  # Give Roxanne's first team a FLARION in place of her NOSEPASS.
  python3 tools/agent_tools/swap_trainer_species.py \\
      --trainer Roxanne1 --from NOSEPASS --to FLARION
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E

TRAINER_PARTIES = P.ROOT / "src/data/trainer_parties.h"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trainer", required=True,
                    help="Name of the sParty_* static array (e.g. Roxanne1).")
    ap.add_argument("--from", dest="src", required=True, help="SPECIES_* (no prefix) to replace.")
    ap.add_argument("--to", dest="dst", required=True, help="SPECIES_* (no prefix) to put in.")
    a = ap.parse_args(argv)

    text = E.read(TRAINER_PARTIES)
    pat = re.compile(
        rf"(static const struct \w+ sParty_{a.trainer}\[\] = \{{)(.*?)(^\}};)",
        re.DOTALL | re.MULTILINE,
    )
    m = pat.search(text)
    if not m:
        raise SystemExit(f"sParty_{a.trainer}[] not found")
    body = m.group(2)
    new_body, n = re.subn(
        rf"(\.species\s*=\s*)SPECIES_{a.src}(\s*,)",
        rf"\1SPECIES_{a.dst}\2",
        body,
    )
    if n == 0:
        raise SystemExit(f"SPECIES_{a.src} not present in sParty_{a.trainer}[]")
    text = text[:m.start(2)] + new_body + text[m.end(2):]
    E.write(TRAINER_PARTIES, text)
    print(f"sParty_{a.trainer}[]: {n}x SPECIES_{a.src} -> SPECIES_{a.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

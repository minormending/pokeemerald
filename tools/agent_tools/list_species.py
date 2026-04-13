#!/usr/bin/env python3
"""List all SPECIES_* constants defined in include/constants/species.h."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E


def main() -> int:
    text = E.read(P.SPECIES_H)
    pat = re.compile(r"^#define (SPECIES_\w+)\s+(.+)$", re.MULTILINE)
    for m in pat.finditer(text):
        print(f"{m.group(1):32s} {m.group(2)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

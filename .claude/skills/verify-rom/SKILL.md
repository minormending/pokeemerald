---
name: verify-rom
description: Boot the built ROM under mgba headlessly and confirm it runs without crashing. Use after making changes to sanity-check the ROM. Runs tools/agent_tools/verify_rom.py.
---

# verify-rom

```bash
python3 tools/agent_tools/verify_rom.py            # default 8s boot
python3 tools/agent_tools/verify_rom.py --seconds 20
python3 tools/agent_tools/verify_rom.py --rom pokeemerald.gba
```

Checks:
1. `gbafix -p` accepts the header.
2. `mgba -l 255` runs for `--seconds` without logging `fatal`, `crash`,
   `abort`, `undefined instruction`, or `illegal`.
3. Detects gameplay activity (audio FIFO, DMA) to confirm init completed.

Requires `mgba-sdl` and `xvfb-run` (both already installed in this sandbox).
Exits non-zero on any failure so CI/loops can gate on it.

You can also run it as part of a build:
```bash
python3 tools/agent_tools/build.py --verify
```

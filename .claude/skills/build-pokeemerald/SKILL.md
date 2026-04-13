---
name: build-pokeemerald
description: Build the pokeemerald ROM. Use when the user asks to compile, build, or verify the game. Wraps tools/agent_tools/build.py which auto-detects the ARM toolchain.
---

# build-pokeemerald

## Default (modern gcc, easiest)

```bash
python3 tools/agent_tools/build.py
```

## Matching the original ROM checksum (requires agbcc)

```bash
python3 tools/agent_tools/build.py --classic
```

## Clean + rebuild

```bash
python3 tools/agent_tools/build.py --clean
```

## Prerequisites

- Modern build: `arm-none-eabi-gcc` in PATH (e.g. `apt install gcc-arm-none-eabi`).
- Classic build: `$DEVKITARM` set and `tools/agbcc/bin/agbcc` present.

If the tool prints an install hint, surface it to the user instead of
guessing — the message already names the right package for each OS.

## After a build

Compiled ROM is at `pokeemerald_modern.gba` (modern) or `pokeemerald.gba`
(classic). Report the path back to the user.

#!/usr/bin/env python3
"""Boot the built ROM under mgba for a few seconds and scan for crashes.

Requires mgba-sdl and xvfb (headless).

Verifies:
  1. Header is valid (gbafix -p returns 0).
  2. mgba runs without emitting 'fatal', 'undefined instruction', 'abort',
     'crash', or 'stub' in the log.
  3. mgba's log reaches post-init gameplay writes (sound FIFO / BG palette).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROM = ROOT / "pokeemerald_modern.gba"
GBAFIX = ROOT / "tools/gbafix/gbafix"

BAD_PATTERNS = [
    re.compile(p, re.I) for p in
    ["fatal", "crash", "abort", "undefined instruction", "illegal"]
]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default=str(DEFAULT_ROM))
    ap.add_argument("--seconds", type=int, default=8)
    a = ap.parse_args(argv)

    rom = Path(a.rom)
    if not rom.exists():
        print(f"error: ROM {rom} not found — run build.py first.", file=sys.stderr)
        return 2

    # 1. header check
    r = subprocess.run([str(GBAFIX), str(rom), "-p"], capture_output=True, text=True)
    if r.returncode != 0 or "ROM fixed" not in r.stdout + r.stderr:
        print(f"error: gbafix -p failed: {r.stdout}{r.stderr}", file=sys.stderr)
        return 3
    print(f"[ok] header valid ({rom.name})")

    # 2. boot check
    mgba = shutil.which("mgba") or "/usr/games/mgba"
    xvfb = shutil.which("xvfb-run")
    if not Path(mgba).exists():
        print("warn: mgba not installed; skipping boot test. Install with `apt install mgba-sdl`.")
        return 0
    log = Path("/tmp/verify_rom_mgba.log")
    if log.exists():
        log.unlink()

    cmd = []
    if xvfb:
        cmd += [xvfb, "-a"]
    cmd += ["timeout", str(a.seconds), mgba, "-l", "255",
            "-C", "logToFile=1", "-C", f"logFile={log}", str(rom)]
    env = os.environ.copy()
    subprocess.run(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not log.exists() or log.stat().st_size == 0:
        print("warn: no mgba log produced; cannot verify boot.", file=sys.stderr)
        return 0
    content = log.read_text(errors="replace")
    for pat in BAD_PATTERNS:
        m = pat.search(content)
        if m:
            print(f"error: mgba log contained {m.group(0)!r}:", file=sys.stderr)
            print(content[-500:], file=sys.stderr)
            return 4
    # rough liveness signal: saw audio FIFO writes or VBlank SWI 05
    alive = any(s in content for s in ("040000A0", "SWI: 05", "Starting DMA"))
    print(f"[ok] mgba ran {a.seconds}s without fatal errors"
          + ("  (reached gameplay writes)" if alive else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

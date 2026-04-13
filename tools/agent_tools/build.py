#!/usr/bin/env python3
"""Build the pokeemerald ROM.

Two supported modes:
  --modern  (default): uses a modern arm-none-eabi-gcc. Easier to install on
            Linux systems via devkitARM or the distro's `gcc-arm-none-eabi`.
  --classic: uses agbcc + the original Makefile target, required to match
            `rom.sha1` byte-for-byte.

This wrapper auto-detects the toolchain and prints actionable hints when it
can't find it. The actual build work is still done by `make`.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def find_toolchain(modern: bool) -> tuple[str, dict[str, str]]:
    env = os.environ.copy()
    if modern:
        # Look for arm-none-eabi-gcc.
        for candidate in ("arm-none-eabi-gcc",):
            if shutil.which(candidate):
                return "modern", env
        # devkitARM?
        dka = env.get("DEVKITARM") or "/opt/devkitpro/devkitARM"
        if Path(dka, "bin/arm-none-eabi-gcc").exists():
            env["DEVKITARM"] = dka
            env["PATH"] = f"{dka}/bin:{env['PATH']}"
            return "modern", env
        print("error: no arm-none-eabi-gcc found. Install with one of:", file=sys.stderr)
        print("  apt install gcc-arm-none-eabi  # Ubuntu/Debian", file=sys.stderr)
        print("  brew install --cask gcc-arm-embedded  # macOS", file=sys.stderr)
        print("  or install devkitARM: https://devkitpro.org/wiki/Getting_Started", file=sys.stderr)
        sys.exit(2)
    # Classic path: requires devkitARM AND the agbcc/ submodule present.
    dka = env.get("DEVKITARM") or "/opt/devkitpro/devkitARM"
    if not Path(dka, "bin/arm-none-eabi-gcc").exists():
        print("error: devkitARM required for classic build. Set $DEVKITARM or install devkitARM.",
              file=sys.stderr)
        sys.exit(2)
    env["DEVKITARM"] = dka
    env["PATH"] = f"{dka}/bin:{env['PATH']}"
    if not (ROOT / "tools/agbcc/bin/agbcc").exists():
        print("warning: tools/agbcc/bin/agbcc missing; classic build will fail. "
              "Clone https://github.com/pret/agbcc into tools/agbcc and run build.sh there.",
              file=sys.stderr)
    return "classic", env


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--classic", action="store_true",
                    help="Use agbcc (matches rom.sha1). Default is modern gcc.")
    ap.add_argument("--jobs", "-j", type=int, default=os.cpu_count() or 2)
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="After building, boot the ROM under mgba and scan for crashes.")
    ap.add_argument("extra", nargs="*", help="Extra make args.")
    a = ap.parse_args(argv)

    mode, env = find_toolchain(modern=not a.classic)

    cmd = ["make", "-C", str(ROOT), f"-j{a.jobs}"]
    if a.clean:
        subprocess.run(cmd + ["clean"], env=env, check=False)
    if mode == "modern":
        cmd.append("modern")
    cmd.extend(a.extra)
    print(">>", " ".join(cmd))
    rc = subprocess.call(cmd, env=env)
    if rc != 0 or not a.verify:
        return rc
    verify = Path(__file__).with_name("verify_rom.py")
    print(">> verifying ROM boots under mgba...")
    return subprocess.call([sys.executable, str(verify)])


if __name__ == "__main__":
    sys.exit(main())

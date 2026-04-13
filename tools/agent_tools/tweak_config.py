#!/usr/bin/env python3
"""Adjust global gameplay constants and optional compile-time mod toggles.

Supports:
  Balance knobs (integers written into #define values):
    --shiny-odds N       include/constants/pokemon.h : SHINY_ODDS
    --exp-multiplier N   include/config.h            : EXP_MULTIPLIER
    --catch-rate-bonus N include/config.h            : CATCH_RATE_BONUS
    --crit-rate-bonus N  include/config.h            : CRIT_RATE_BONUS
    --starting-money N   include/config.h            : STARTING_MONEY

  Boolean mods (accept on/off, 1/0, true/false):
    --perfect-ivs ON|OFF          PERFECT_IVS
    --never-miss ON|OFF           NEVER_MISS
    --no-random-encounters ON|OFF NO_RANDOM_ENCOUNTERS
    --unlimited-tms ON|OFF        UNLIMITED_TMS
    --instant-text ON|OFF         INSTANT_TEXT
    --run-anywhere ON|OFF         RUN_ANYWHERE
    --skip-intro ON|OFF           SKIP_INTRO

Examples:
  python3 tools/agent_tools/tweak_config.py --perfect-ivs on --exp-multiplier 3
  python3 tools/agent_tools/tweak_config.py --never-miss on --unlimited-tms on
  python3 tools/agent_tools/tweak_config.py --shiny-odds 512 --instant-text on
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E

POKEMON_H = P.ROOT / "include/constants/pokemon.h"
CONFIG_H  = P.ROOT / "include/config.h"


# Integer knobs: flag name → (file, #define name, CLI help).
INT_KNOBS = {
    "shiny_odds":       (POKEMON_H, "SHINY_ODDS",       "Numerator over 65536. Vanilla 8."),
    "exp_multiplier":   (CONFIG_H,  "EXP_MULTIPLIER",   "Integer multiplier on battle exp. Vanilla 1."),
    "catch_rate_bonus": (CONFIG_H,  "CATCH_RATE_BONUS", "Integer multiplier on capture odds. Vanilla 1."),
    "crit_rate_bonus":  (CONFIG_H,  "CRIT_RATE_BONUS",  "Stage offset added to crit table index. Vanilla 0."),
    "starting_money":   (CONFIG_H,  "STARTING_MONEY",   "Money on new game. Vanilla 3000."),
}

# Boolean mods: flag name → (file, #define name, CLI help).
BOOL_MODS = {
    "perfect_ivs":          (CONFIG_H, "PERFECT_IVS",          "Every mon gets 31 IVs everywhere."),
    "never_miss":           (CONFIG_H, "NEVER_MISS",           "Player moves never miss."),
    "no_random_encounters": (CONFIG_H, "NO_RANDOM_ENCOUNTERS", "Disable all random wild battles."),
    "unlimited_tms":        (CONFIG_H, "UNLIMITED_TMS",        "TMs are not consumed when taught."),
    "instant_text":         (CONFIG_H, "INSTANT_TEXT",         "All in-game text renders with 0 delay."),
    "run_anywhere":         (CONFIG_H, "RUN_ANYWHERE",         "Ignore gMapHeader.allowRunning restriction."),
    "skip_intro":           (CONFIG_H, "SKIP_INTRO",           "Skip the Latios/Latias intro cinematic."),
    "catch_exp":            (CONFIG_H, "CATCH_EXP",            "Catching a Pokémon grants XP (Gen 6+ behavior)."),
    "exp_all":              (CONFIG_H, "EXP_ALL",              "All alive party members gain XP from every KO."),
    "poison_doesnt_faint":  (CONFIG_H, "POISON_DOESNT_FAINT",  "Field poison clamps at 1 HP; never faints on overworld."),
    "physical_special_split":(CONFIG_H,"PHYSICAL_SPECIAL_SPLIT","Per-move Phys/Spec/Status category (Gen 4+ style)."),
    "quick_test":           (CONFIG_H, "QUICK_TEST",           "Skip intro, spawn Lv50 test party on Route 102 on new game."),
}


def parse_bool(raw: str) -> str:
    raw = raw.lower()
    if raw in ("on", "1", "true", "yes"):  return "1"
    if raw in ("off", "0", "false", "no"): return "0"
    raise argparse.ArgumentTypeError(f"expected on/off, got {raw!r}")


def set_define(path: Path, name: str, value: str) -> tuple[str, str]:
    text = E.read(path)
    pat = re.compile(rf"(#define\s+{name}\s+)(\S+)(.*)")
    m = pat.search(text)
    if not m:
        raise SystemExit(f"#define {name} not found in {path}")
    old = m.group(2)
    text = text[:m.start()] + f"{m.group(1)}{value}{m.group(3)}" + text[m.end():]
    E.write(path, text)
    return old, value


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for flag, (_f, name, help_) in INT_KNOBS.items():
        ap.add_argument(f"--{flag.replace('_','-')}", type=int,
                        help=f"{help_} (#define {name})")
    for flag, (_f, name, help_) in BOOL_MODS.items():
        ap.add_argument(f"--{flag.replace('_','-')}", type=parse_bool,
                        help=f"{help_} (#define {name}) — accepts on/off/1/0/true/false")
    a = ap.parse_args(argv)

    did = 0
    for flag, (path, name, _h) in INT_KNOBS.items():
        val = getattr(a, flag, None)
        if val is not None:
            old, new = set_define(path, name, str(val))
            extra = f"  (probability {int(new)/65536:.6f})" if name == "SHINY_ODDS" else ""
            print(f"{name}: {old} -> {new}{extra}")
            did += 1
    for flag, (path, name, _h) in BOOL_MODS.items():
        val = getattr(a, flag, None)
        if val is not None:
            old, new = set_define(path, name, val)
            state = "ENABLED" if new == "1" else "disabled"
            print(f"{name}: {old} -> {new}  ({state})")
            did += 1

    if not did:
        ap.error("pass at least one flag (see --help).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Apply a JSON 'mod pack' that bundles multiple tooling operations.

Schema:
{
  "species": [ { species spec as accepted by add_species.py --json }, ... ],
  "moves":   [ { "name": ..., "display": ..., "type": ..., "power": ..., ... }, ... ],
  "evolutions": [ { "from": ..., "to": ..., "method": ..., "param": ... }, ... ],
  "starters":[ { "slot": "grass|fire|water", "species": "<NAME>" }, ... ],
  "wilds":   [ { "map": "MAP_...", "field": "land_mons|...", "slot": 0,
                 "species": "<NAME>", "level": 5, "max_level": 8 }, ... ],
  "edits":   [ { "species": "<NAME>", "base_attack": 80, "type1": "FIRE", ... }, ... ],
  "config":  { "shiny_odds": 512 }
}

Every key is optional. Operations run in the order above. On any failure,
the per-tool atomic rollback rolls back only that step's files — earlier
successful steps persist. Run under `git` if you want full atomicity.

Example:
  python3 tools/agent_tools/mod_pack.py mods/megamix.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str, *args: str) -> None:
    cmd = [sys.executable, str(HERE / script), *args]
    print(">>", " ".join(cmd))
    r = subprocess.run(cmd)
    if r.returncode != 0:
        raise SystemExit(f"{script} failed with exit {r.returncode}")


def species_args(spec: dict) -> list[str]:
    """Convert a species JSON entry into add_species.py CLI args."""
    out = []
    mapping = {
        "name": "--name", "category": "--category", "ability": "--ability",
        "ability2": "--ability2", "clone_from": "--clone-from",
        "body_color": "--body-color", "growth_rate": "--growth-rate",
        "gender_ratio": "--gender-ratio", "egg_group1": "--egg-group1",
        "egg_group2": "--egg-group2", "dex_text": "--dex-text",
    }
    for k, flag in mapping.items():
        if k in spec:
            out += [flag, str(spec[k])]
    if "types" in spec: out += ["--types", ",".join(spec["types"])]
    if "stats" in spec: out += ["--stats", ",".join(map(str, spec["stats"]))]
    for ik, flag in [("height", "--height"), ("weight", "--weight"),
                     ("catch_rate", "--catch-rate"), ("exp_yield", "--exp-yield"),
                     ("egg_cycles", "--egg-cycles")]:
        if ik in spec: out += [flag, str(spec[ik])]
    if "learnset" in spec:
        if isinstance(spec["learnset"], list):
            out += ["--learnset", ",".join(f"{lvl}:{mv}" for lvl, mv in spec["learnset"])]
        else:
            out += ["--learnset", spec["learnset"]]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pack", help="Path to mod-pack JSON.")
    ap.add_argument("--verify", action="store_true", help="Run verify_rom.py at the end.")
    a = ap.parse_args(argv)

    data = json.loads(Path(a.pack).read_text())

    for s in data.get("species", []):
        run("add_species.py", *species_args(s))
    for m in data.get("moves", []):
        args = ["--name", m["name"], "--display", m["display"]]
        for k, flag in [("type", "--type"), ("power", "--power"),
                        ("accuracy", "--accuracy"), ("pp", "--pp"),
                        ("effect", "--effect"), ("secondary", "--secondary"),
                        ("target", "--target"), ("priority", "--priority"),
                        ("flags", "--flags"), ("split", "--split")]:
            if k in m:
                args += [flag, str(m[k])]
        run("add_move.py", *args)
    for ev in data.get("evolutions", []):
        run("add_evolution.py", "--from", ev["from"], "--to", ev["to"],
            "--method", ev.get("method", "LEVEL"), "--param", str(ev.get("param", 0)))
    for s in data.get("starters", []):
        run("set_starter.py", "--slot", s["slot"], "--species", s["species"])
    for w in data.get("wilds", []):
        args = ["--map", w["map"], "--field", w["field"], "--slot", str(w["slot"]),
                "--species", w["species"], "--level", str(w["level"])]
        if "max_level" in w:
            args += ["--max-level", str(w["max_level"])]
        run("set_wild_encounter.py", *args)
    for ed in data.get("edits", []):
        args = ["--species", ed["species"]]
        simple_keys = ["base_hp", "base_attack", "base_defense", "base_speed",
                       "base_sp_attack", "base_sp_defense", "catch_rate",
                       "exp_yield", "egg_cycles", "type1", "type2", "ability1",
                       "ability2", "growth_rate", "body_color"]
        for k in simple_keys:
            if k in ed:
                args += [f"--{k.replace('_','-')}", str(ed[k])]
        run("edit_species.py", *args)
    cfg = data.get("config", {})
    INT_KEYS  = ["shiny_odds", "exp_multiplier", "catch_rate_bonus",
                 "crit_rate_bonus", "starting_money"]
    BOOL_KEYS = ["perfect_ivs", "never_miss", "no_random_encounters",
                 "unlimited_tms", "instant_text", "run_anywhere", "skip_intro",
                 "catch_exp", "exp_all", "poison_doesnt_faint",
                 "physical_special_split", "quick_test"]
    tweak_args: list[str] = []
    for k in INT_KEYS:
        if k in cfg:
            tweak_args += [f"--{k.replace('_','-')}", str(cfg[k])]
    for k in BOOL_KEYS:
        if k in cfg:
            v = cfg[k]
            if isinstance(v, bool):
                v = "on" if v else "off"
            tweak_args += [f"--{k.replace('_','-')}", str(v)]
    if tweak_args:
        run("tweak_config.py", *tweak_args)

    print("\n[ok] mod pack applied:", a.pack)
    if a.verify:
        run("build.py", "--verify")
    return 0


if __name__ == "__main__":
    sys.exit(main())

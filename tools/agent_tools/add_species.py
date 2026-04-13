#!/usr/bin/env python3
"""Insert a new Pokémon species into pokeemerald.

The new species ID is inserted right before SPECIES_EGG so that form species
defined relative to NUM_SPECIES (the SPECIES_UNOWN_* block) and designated-
initializer tables all shift automatically. Graphics are reused from an
existing species (`--clone-from`), so no new art assets are required.

Files touched:
  include/constants/species.h
  include/constants/pokedex.h
  src/data/text/species_names.h
  src/data/pokemon/species_info.h
  src/data/pokemon/pokedex_entries.h
  src/data/pokemon/pokedex_text.h
  src/data/pokemon/pokedex_orders.h
  src/data/pokemon/level_up_learnset_pointers.h
  src/data/pokemon/level_up_learnsets.h
  src/data/pokemon_graphics/*.h (all lookup tables, reusing the clone's art)

Example:
  python3 tools/agent_tools/add_species.py \\
      --name FLARION --types FIRE,DRAGON \\
      --stats 80,120,70,95,110,75 --ability BLAZE \\
      --clone-from CHARIZARD \\
      --category "EMBER" --height 12 --weight 500 \\
      --dex-text "A fierce dragon said to breathe sapphire fire."

After running, `make` (via tools/agent_tools/build.py) should still succeed.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent))
import pe_paths as P
import pe_edit as E


def camel(species_name: str) -> str:
    """FLARION -> Flarion, BALD_MCBOOT -> BaldMcboot."""
    return "".join(part.capitalize() for part in species_name.split("_"))


# Graphics suffix overrides for species whose variable name doesn't follow the
# simple CamelCase of the SPECIES_* constant (e.g. UNOWN_EMARK ->
# UnownExclamationMark). Extend as needed.
GFX_SUFFIX_OVERRIDES = {
    "NIDORAN_F": "NidoranF",
    "NIDORAN_M": "NidoranM",
    "MR_MIME": "MrMime",
    "HO_OH": "HoOh",
    "UNOWN_EMARK": "UnownExclamationMark",
    "UNOWN_QMARK": "UnownQuestionMark",
}


def gfx_suffix(species_name: str) -> str:
    return GFX_SUFFIX_OVERRIDES.get(species_name, camel(species_name))


@dataclass
class Learnset:
    moves: List[tuple] = field(default_factory=list)  # list of (level, MOVE_NAME)

    @classmethod
    def parse(cls, raw: str) -> "Learnset":
        ls = cls()
        if not raw:
            return ls
        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue
            lvl_s, move = item.split(":")
            ls.moves.append((int(lvl_s), move.strip()))
        ls.moves.sort()
        return ls

    def c_array(self, static_name: str) -> str:
        lines = [f"static const u16 {static_name}[] = {{"]
        for lvl, move in self.moves:
            lines.append(f"    LEVEL_UP_MOVE({lvl}, MOVE_{move}),")
        lines.append("    LEVEL_UP_END,")
        lines.append("};\n")
        return "\n".join(lines)


@dataclass
class SpeciesSpec:
    name: str                 # FLARION
    types: List[str]          # ["FIRE", "DRAGON"]
    stats: List[int]          # [hp, atk, def, spe, spa, spd]
    ability: str              # "BLAZE"
    ability2: str = "NONE"
    hidden_ability: str = "NONE"
    clone_from: str = "BULBASAUR"
    category: str = "UNKNOWN"
    height: int = 10          # decimetres
    weight: int = 100         # hectograms
    dex_text: str = "A newly discovered creature."
    catch_rate: int = 45
    exp_yield: int = 64
    growth_rate: str = "MEDIUM_FAST"
    egg_group1: str = "NO_EGGS_DISCOVERED"
    egg_group2: str = "NO_EGGS_DISCOVERED"
    gender_ratio: str = "MON_GENDERLESS"
    egg_cycles: int = 40
    friendship: str = "STANDARD_FRIENDSHIP"
    body_color: str = "RED"
    learnset: Learnset = field(default_factory=Learnset)

    @property
    def cc(self) -> str:  # CamelCase for constant/variable names
        return camel(self.name)


# ----------------------------- editing steps --------------------------------


def update_species_h(spec: SpeciesSpec) -> int:
    """Insert `#define SPECIES_X N`; bump SPECIES_EGG. Returns the new ID."""
    text = E.read(P.SPECIES_H)
    # Find SPECIES_EGG line
    needle = "#define SPECIES_EGG "
    start = text.index(needle)
    line_end = text.index("\n", start)
    line = text[start:line_end]
    old_egg_id = int(line.split()[-1])
    new_id = old_egg_id
    new_egg = old_egg_id + 1

    # Build the new lines
    new_block = f"#define SPECIES_{spec.name} {new_id}\n#define SPECIES_EGG {new_egg}"
    text = text[:start] + new_block + text[line_end:]
    E.write(P.SPECIES_H, text)
    return new_id


def update_pokedex_h(spec: SpeciesSpec) -> None:
    """Append NATIONAL_DEX_<NAME> after the current NATIONAL_DEX_COUNT target."""
    import re
    text = E.read(P.POKEDEX_H)
    m = re.search(r"#define NATIONAL_DEX_COUNT\s+NATIONAL_DEX_(\w+)", text)
    if not m:
        raise RuntimeError("NATIONAL_DEX_COUNT definition not found")
    current_last = m.group(1)
    anchor = f"    NATIONAL_DEX_{current_last},\n"
    text = E.insert_after(text, anchor, f"    NATIONAL_DEX_{spec.name},\n")
    text = text.replace(
        f"#define NATIONAL_DEX_COUNT  NATIONAL_DEX_{current_last}",
        f"#define NATIONAL_DEX_COUNT  NATIONAL_DEX_{spec.name}",
        1,
    )
    E.write(P.POKEDEX_H, text)


def update_species_names_h(spec: SpeciesSpec) -> None:
    text = E.read(P.SPECIES_NAMES_H)
    anchor = "};\n"
    # Truncate to name length limit (10 chars)
    display = spec.name[:10]
    line = f"    [SPECIES_{spec.name}] = _(\"{display}\"),\n"
    # Insert before the LAST "};"
    idx = text.rfind(anchor)
    text = text[:idx] + line + text[idx:]
    E.write(P.SPECIES_NAMES_H, text)


def update_species_info_h(spec: SpeciesSpec) -> None:
    text = E.read(P.SPECIES_INFO_H)
    t1, t2 = (spec.types + spec.types[:1])[:2]
    hp, atk, df, spe, spa, spd = spec.stats
    block = f"""
    [SPECIES_{spec.name}] =
    {{
        .baseHP        = {hp},
        .baseAttack    = {atk},
        .baseDefense   = {df},
        .baseSpeed     = {spe},
        .baseSpAttack  = {spa},
        .baseSpDefense = {spd},
        .types = {{ TYPE_{t1}, TYPE_{t2} }},
        .catchRate = {spec.catch_rate},
        .expYield = {spec.exp_yield},
        .evYield_HP        = 0,
        .evYield_Attack    = 0,
        .evYield_Defense   = 0,
        .evYield_Speed     = 0,
        .evYield_SpAttack  = 0,
        .evYield_SpDefense = 0,
        .itemCommon = ITEM_NONE,
        .itemRare   = ITEM_NONE,
        .genderRatio = {spec.gender_ratio},
        .eggCycles = {spec.egg_cycles},
        .friendship = {spec.friendship},
        .growthRate = GROWTH_{spec.growth_rate},
        .eggGroups = {{ EGG_GROUP_{spec.egg_group1}, EGG_GROUP_{spec.egg_group2} }},
        .abilities = {{ABILITY_{spec.ability}, ABILITY_{spec.ability2}}},
        .safariZoneFleeRate = 0,
        .bodyColor = BODY_COLOR_{spec.body_color},
        .noFlip = FALSE,
    }},
"""
    # Insert before the closing `};` of gSpeciesInfo[].
    # There's only one top-level `};` at the end of the file's main array.
    closing = "\n};\n"
    idx = text.rindex(closing)
    # Ensure the previous entry ends with a comma (vanilla last entry may not).
    prefix = text[:idx]
    if prefix.rstrip().endswith("}"):
        prefix = prefix.rstrip() + ","
    text = prefix + block + text[idx:]
    E.write(P.SPECIES_INFO_H, text)


def update_pokedex_text_h(spec: SpeciesSpec) -> None:
    text = E.read(P.POKEDEX_TEXT_H)
    cc = spec.cc
    # Wrap description into ~40-char lines with \n inside the _() macro.
    words = spec.dex_text.split()
    lines: List[str] = []
    cur = ""
    for w in words:
        if len(cur) + 1 + len(w) > 38 and cur:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    # Pokédex entries are typically 4 lines; pad with empties if fewer.
    while len(lines) < 4:
        lines.append("")
    body = "\\n\"\n    \"".join(lines[:4])
    entry = (
        f"\nconst u8 g{cc}PokedexText[] = _(\n"
        f"    \"{body}\");\n"
    )
    text += entry
    E.write(P.POKEDEX_TEXT_H, text)


def update_pokedex_entries_h(spec: SpeciesSpec) -> None:
    text = E.read(P.POKEDEX_ENTRIES_H)
    cc = spec.cc
    block = f"""
    [NATIONAL_DEX_{spec.name}] =
    {{
        .categoryName = _("{spec.category}"),
        .height = {spec.height},
        .weight = {spec.weight},
        .description = g{cc}PokedexText,
        .pokemonScale = 256,
        .pokemonOffset = 0,
        .trainerScale = 256,
        .trainerOffset = 0,
    }},
"""
    closing = "\n};\n"
    idx = text.rindex(closing)
    text = text[:idx] + block + text[idx:]
    E.write(P.POKEDEX_ENTRIES_H, text)


def update_pokedex_orders_h(spec: SpeciesSpec) -> None:
    """Append to the end of each of the three order arrays."""
    text = E.read(P.POKEDEX_ORDERS_H)
    line = f"    NATIONAL_DEX_{spec.name},\n"
    # Each of the three arrays ends with `};\n`. Insert before each.
    # Use a walking replace to hit all three.
    out = []
    i = 0
    count = 0
    while i < len(text):
        j = text.find("\n};\n", i)
        if j < 0:
            out.append(text[i:])
            break
        out.append(text[i:j+1])  # up to and including the newline before };
        out.append(line)
        out.append(text[j+1:j+4])  # the "};\n"
        i = j + 4
        count += 1
    if count < 3:
        raise RuntimeError("pokedex_orders.h: expected 3 arrays, found %d" % count)
    E.write(P.POKEDEX_ORDERS_H, "".join(out))


def update_learnsets(spec: SpeciesSpec) -> None:
    static_name = f"s{spec.cc}LevelUpLearnset"
    # level_up_learnsets.h: append static array
    text = E.read(P.LVLUP_LEARNSETS_H)
    if not spec.learnset.moves:
        # default: learn TACKLE at level 1
        spec.learnset.moves = [(1, "TACKLE")]
    text = text.rstrip() + "\n\n" + spec.learnset.c_array(static_name)
    E.write(P.LVLUP_LEARNSETS_H, text)

    # level_up_learnset_pointers.h: designated initializer, insert before final `};`
    text = E.read(P.LVLUP_POINTERS_H)
    line = f"    [SPECIES_{spec.name}] = {static_name},\n"
    closing = "};\n"
    idx = text.rindex(closing)
    text = text[:idx] + line + text[idx:]
    E.write(P.LVLUP_POINTERS_H, text)


def update_graphics_tables(spec: SpeciesSpec) -> None:
    clone_suffix = gfx_suffix(spec.clone_from)
    name = spec.name
    cc = spec.cc

    # 1) front_pic_table.h, still_front_pic_table.h, back_pic_table.h (sequential macro entries)
    for path, macro, var_prefix in [
        (P.FRONT_PIC_TABLE_H,       "SPECIES_SPRITE", "gMonFrontPic_"),
        (P.STILL_FRONT_PIC_TABLE_H, "SPECIES_SPRITE", "gMonStillFrontPic_"),
        (P.BACK_PIC_TABLE_H,        "SPECIES_SPRITE", "gMonBackPic_"),
    ]:
        text = E.read(path)
        line = f"    {macro}({name}, {var_prefix}{clone_suffix}),\n"
        closing = "};\n"
        idx = text.rindex(closing)
        text = text[:idx] + line + text[idx:]
        E.write(path, text)

    # 2) palette_table.h, shiny_palette_table.h
    for path, macro, var_prefix in [
        (P.PALETTE_TABLE_H,       "SPECIES_PAL",       "gMonPalette_"),
        (P.SHINY_PALETTE_TABLE_H, "SPECIES_SHINY_PAL", "gMonShinyPalette_"),
    ]:
        text = E.read(path)
        line = f"    {macro}({name}, {var_prefix}{clone_suffix}),\n"
        closing = "};\n"
        idx = text.rindex(closing)
        text = text[:idx] + line + text[idx:]
        E.write(path, text)

    # 3) front_pic_anims.h, front_pic_coords, back_pic_coords, footprint, elevation, unknown_table
    #    These are designated initializers.
    edits = [
        (P.FRONT_PIC_ANIMS_H,      f"    [SPECIES_{name}] = sAnims_{clone_suffix},\n"),
        (P.FRONT_PIC_COORDS_H,     f"    [SPECIES_{name}] = {{ .size = MON_COORDS_SIZE(64, 64), .y_offset = 0 }},\n"),
        (P.BACK_PIC_COORDS_H,      f"    [SPECIES_{name}] = {{ .size = MON_COORDS_SIZE(64, 64), .y_offset = 0 }},\n"),
        (P.FOOTPRINT_TABLE_H,      f"    [SPECIES_{name}] = gMonFootprint_{clone_suffix},\n"),
        (P.ENEMY_MON_ELEVATION_H,  f"    [SPECIES_{name}] = 0,\n"),
        (P.UNKNOWN_TABLE_H,        f"    [SPECIES_{name}] = 0x0,\n"),
    ]
    for path, line in edits:
        text = E.read(path)
        # Insert before the LAST `};`
        closing = "};\n"
        idx = text.rindex(closing)
        text = text[:idx] + line + text[idx:]
        E.write(path, text)


# ----------------------------- CLI entry ------------------------------------


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Add a new species to pokeemerald.")
    p.add_argument("--name", required=True, help="UPPER_SNAKE species name, e.g. FLARION")
    p.add_argument("--types", required=True, help="Comma-separated 1 or 2 types, e.g. FIRE,DRAGON")
    p.add_argument("--stats", required=True, help="hp,atk,def,spe,spa,spd (6 ints)")
    p.add_argument("--ability", default="PRESSURE")
    p.add_argument("--ability2", default="NONE")
    p.add_argument("--clone-from", default="BULBASAUR",
                   help="Existing SPECIES_* (no prefix) to reuse graphics from.")
    p.add_argument("--category", default="UNKNOWN")
    p.add_argument("--height", type=int, default=10)
    p.add_argument("--weight", type=int, default=100)
    p.add_argument("--dex-text", default="A newly discovered creature.")
    p.add_argument("--catch-rate", type=int, default=45)
    p.add_argument("--exp-yield", type=int, default=100)
    p.add_argument("--growth-rate", default="MEDIUM_FAST")
    p.add_argument("--gender-ratio", default="PERCENT_FEMALE(50)")
    p.add_argument("--egg-group1", default="NO_EGGS_DISCOVERED")
    p.add_argument("--egg-group2", default="NO_EGGS_DISCOVERED")
    p.add_argument("--egg-cycles", type=int, default=40)
    p.add_argument("--body-color", default="RED")
    p.add_argument("--learnset", default="",
                   help="Comma list of LVL:MOVE pairs, e.g. 1:TACKLE,5:EMBER,12:GROWL")
    p.add_argument("--json", help="Alternative: load all args from a JSON file.")
    return p.parse_args(argv)


def spec_from_args(a: argparse.Namespace) -> SpeciesSpec:
    if a.json:
        data = json.loads(Path(a.json).read_text())
        spec = SpeciesSpec(
            name=data["name"],
            types=list(data["types"]),
            stats=list(data["stats"]),
            ability=data.get("ability", "PRESSURE"),
            ability2=data.get("ability2", "NONE"),
            clone_from=data.get("clone_from", "BULBASAUR"),
            category=data.get("category", "UNKNOWN"),
            height=int(data.get("height", 10)),
            weight=int(data.get("weight", 100)),
            dex_text=data.get("dex_text", "A newly discovered creature."),
            catch_rate=int(data.get("catch_rate", 45)),
            exp_yield=int(data.get("exp_yield", 100)),
            growth_rate=data.get("growth_rate", "MEDIUM_FAST"),
            egg_group1=data.get("egg_group1", "NO_EGGS_DISCOVERED"),
            egg_group2=data.get("egg_group2", "NO_EGGS_DISCOVERED"),
            gender_ratio=data.get("gender_ratio", "PERCENT_FEMALE(50)"),
            egg_cycles=int(data.get("egg_cycles", 40)),
            body_color=data.get("body_color", "RED"),
            learnset=Learnset.parse(data.get("learnset", "")),
        )
        return spec
    return SpeciesSpec(
        name=a.name,
        types=[t.strip() for t in a.types.split(",") if t.strip()],
        stats=[int(x) for x in a.stats.split(",")],
        ability=a.ability,
        ability2=a.ability2,
        clone_from=a.clone_from,
        category=a.category,
        height=a.height,
        weight=a.weight,
        dex_text=a.dex_text,
        catch_rate=a.catch_rate,
        exp_yield=a.exp_yield,
        growth_rate=a.growth_rate,
        gender_ratio=a.gender_ratio,
        egg_group1=a.egg_group1,
        egg_group2=a.egg_group2,
        egg_cycles=a.egg_cycles,
        body_color=a.body_color,
        learnset=Learnset.parse(a.learnset),
    )


ALL_TOUCHED_FILES = [
    P.SPECIES_H, P.POKEDEX_H, P.SPECIES_NAMES_H, P.SPECIES_INFO_H,
    P.POKEDEX_TEXT_H, P.POKEDEX_ENTRIES_H, P.POKEDEX_ORDERS_H,
    P.LVLUP_POINTERS_H, P.LVLUP_LEARNSETS_H,
    P.FRONT_PIC_TABLE_H, P.STILL_FRONT_PIC_TABLE_H, P.BACK_PIC_TABLE_H,
    P.PALETTE_TABLE_H, P.SHINY_PALETTE_TABLE_H, P.FRONT_PIC_ANIMS_H,
    P.FRONT_PIC_COORDS_H, P.BACK_PIC_COORDS_H, P.FOOTPRINT_TABLE_H,
    P.ENEMY_MON_ELEVATION_H, P.UNKNOWN_TABLE_H,
]


def add_species(spec: SpeciesSpec) -> int:
    if len(spec.stats) != 6:
        raise SystemExit("--stats must have 6 values")
    if not (1 <= len(spec.types) <= 2):
        raise SystemExit("--types must have 1 or 2 entries")

    # Snapshot all touched files so we can roll back on failure.
    backups = {p: p.read_bytes() for p in ALL_TOUCHED_FILES}
    try:
        new_id = update_species_h(spec)
        update_pokedex_h(spec)
        update_species_names_h(spec)
        update_species_info_h(spec)
        update_pokedex_text_h(spec)
        update_pokedex_entries_h(spec)
        update_pokedex_orders_h(spec)
        update_learnsets(spec)
        update_graphics_tables(spec)
    except Exception:
        for p, data in backups.items():
            p.write_bytes(data)
        raise
    return new_id


def main(argv=None) -> int:
    a = parse_args(argv)
    spec = spec_from_args(a)
    new_id = add_species(spec)
    print(f"Added SPECIES_{spec.name} = {new_id}")
    print(f"  cloned graphics from SPECIES_{spec.clone_from}")
    print(f"  NATIONAL_DEX_{spec.name} appended; NATIONAL_DEX_COUNT updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())

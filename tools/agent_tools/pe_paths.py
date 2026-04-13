"""Shared path constants for pokeemerald agent tooling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# Constants
SPECIES_H         = ROOT / "include/constants/species.h"
POKEDEX_H         = ROOT / "include/constants/pokedex.h"
MOVES_H           = ROOT / "include/constants/moves.h"

# Pokemon data
SPECIES_INFO_H    = ROOT / "src/data/pokemon/species_info.h"
POKEDEX_ENTRIES_H = ROOT / "src/data/pokemon/pokedex_entries.h"
POKEDEX_TEXT_H    = ROOT / "src/data/pokemon/pokedex_text.h"
POKEDEX_ORDERS_H  = ROOT / "src/data/pokemon/pokedex_orders.h"
LVLUP_POINTERS_H  = ROOT / "src/data/pokemon/level_up_learnset_pointers.h"
LVLUP_LEARNSETS_H = ROOT / "src/data/pokemon/level_up_learnsets.h"
CRY_IDS_H         = ROOT / "src/data/pokemon/cry_ids.h"

# Names
SPECIES_NAMES_H   = ROOT / "src/data/text/species_names.h"
MOVE_NAMES_H      = ROOT / "src/data/text/move_names.h"

# Graphics tables
FRONT_PIC_TABLE_H      = ROOT / "src/data/pokemon_graphics/front_pic_table.h"
STILL_FRONT_PIC_TABLE_H= ROOT / "src/data/pokemon_graphics/still_front_pic_table.h"
BACK_PIC_TABLE_H       = ROOT / "src/data/pokemon_graphics/back_pic_table.h"
PALETTE_TABLE_H        = ROOT / "src/data/pokemon_graphics/palette_table.h"
SHINY_PALETTE_TABLE_H  = ROOT / "src/data/pokemon_graphics/shiny_palette_table.h"
FRONT_PIC_ANIMS_H      = ROOT / "src/data/pokemon_graphics/front_pic_anims.h"
FRONT_PIC_COORDS_H     = ROOT / "src/data/pokemon_graphics/front_pic_coordinates.h"
BACK_PIC_COORDS_H      = ROOT / "src/data/pokemon_graphics/back_pic_coordinates.h"
FOOTPRINT_TABLE_H      = ROOT / "src/data/pokemon_graphics/footprint_table.h"
ENEMY_MON_ELEVATION_H  = ROOT / "src/data/pokemon_graphics/enemy_mon_elevation.h"
UNKNOWN_TABLE_H        = ROOT / "src/data/pokemon_graphics/unknown_table.h"

# Moves
BATTLE_MOVES_H   = ROOT / "src/data/battle_moves.h"
CONTEST_MOVES_H  = ROOT / "src/data/contest_moves.h"

AGENT_TOOLS_DIR  = ROOT / "tools/agent_tools"

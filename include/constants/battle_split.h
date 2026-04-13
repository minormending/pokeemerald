#ifndef GUARD_CONSTANTS_BATTLE_SPLIT_H
#define GUARD_CONSTANTS_BATTLE_SPLIT_H

// Per-move damage category. Used when PHYSICAL_SPECIAL_SPLIT is enabled.
// See include/config.h, include/battle.h (IS_MOVE_PHYSICAL macros) and
// src/pokemon.c::CalculateBaseDamage for the consumers.

#define SPLIT_PHYSICAL 0
#define SPLIT_SPECIAL  1
#define SPLIT_STATUS   2

#endif // GUARD_CONSTANTS_BATTLE_SPLIT_H

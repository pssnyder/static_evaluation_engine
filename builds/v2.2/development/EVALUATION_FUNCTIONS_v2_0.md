# Cece Chess Engine v2.0 - Evaluation Functions Documentation

## Overview
This document outlines all evaluation functions and heuristics available in the Cece v2.0 chess engine evaluation system. The evaluation is organized into six main categories with configurable weights.

---

## Core Evaluation Categories

### 1. Material Evaluation (`_evaluate_material`) - Weight: 1.0
**Base piece values (centipawns):**
- Pawn: 100
- Knight: 300 
- Bishop: 275 (lower base, gets bonus when paired)
- Rook: 500
- Queen: 900
- King: 20000

**Dynamic Material Adjustments:**
- `bishop_pair_bonus`: +25 centipawns when both bishops present
- `single_bishop_penalty`: -25 centipawns when only one bishop
- Dynamic piece values based on position context

### 2. Positional Evaluation (`_evaluate_positional`) - Weight: 0.6
**Piece-Square Tables (PST):**
- **Pawn Table**: Strong advancement bonuses (80cp on 7th rank)
- **Knight Table**: Extreme rim penalties (-80cp corners, -40cp edges)
- **Knight Opening Table**: Harsh development penalties (-150cp corners in opening)
- **Bishop Table**: Diagonal control bonuses (+20cp center)
- **Rook Table**: 7th rank bonuses (+20cp), center file preferences
- **Queen Table**: Strong corner penalties (-50cp), early development penalties (-75cp on 1st rank)
- **King Middlegame Table**: Encourages castling (+25cp castled positions)

**Game Phase Awareness:**
- Opening: Moves 1-12, uses specialized knight opening table
- Endgame: <14 pieces remaining
- Automatic PST selection based on game phase

### 3. Tactical Evaluation (`_evaluate_tactical`) - Weight: 0.9
**Advanced Tactical Pattern Recognition:**
- **Pin Detection**: Identifies pieces pinned to king or valuable pieces
- **Fork Detection**: Knight and pawn fork patterns
- **Discovered Attack Recognition**: Pieces that can reveal attacks by moving
- **Skewer Detection**: Higher value pieces forced to move, exposing lower value pieces
- **Deflection Patterns**: Pieces forced away from defensive duties

**Static Exchange Evaluation (SEE):**
- **Version 1**: `_see_evaluate_capture()` - Basic material exchange calculation
- **Version 2**: `_see_evaluate_capture_v2()` - Enhanced with better attacker sequence
- Minimax-based exchange evaluation for capture sequences
- Least Valuable Attacker (LVA) logic

### 4. Threat Evaluation (`_evaluate_threats`) - Weight: 0.5
**Threat Detection System:**
- Hanging piece detection
- Undefended piece penalties
- Attack/defense imbalances
- Tactical vulnerability assessment

### 5. Castling Evaluation (`_evaluate_castling`) - Weight: 0.4
**Castling Assessment:**
- `_evaluate_side_castling()` for both sides
- Castling rights preservation bonuses
- King safety improvements from castling
- Rook activation benefits

### 6. King Safety Evaluation (`_evaluate_king_safety`) - Weight: 0.8
**King Safety Metrics:**
- `king_safety_zone_bonus`: +20cp per protected square around king
- `exposed_king_penalty`: -150cp for exposed king
- `_get_king_area()`: Defines 3x3 area around king for safety calculation
- Attack patterns against king zone
- Pawn shield evaluation

---

## Development and Opening Heuristics

### Development Evaluation (`_evaluate_development`)
**Development Tracking:**
- `same_piece_twice_penalty`: -50cp for moving same piece twice in opening
- `early_queen_penalty`: -75cp for premature queen development
- `minor_piece_unmoved_bonus`: +30cp per undeveloped minor piece (for opponent)
- Piece move counting and tracking system
- Opening phase thresholds (12 moves)

### Game Phase Detection (`_get_game_phase`)
**Phase Classification:**
- **Opening**: First 12 moves
- **Endgame**: <14 pieces on board
- **Middlegame**: Everything else
- Automatic evaluation adjustment based on phase

---

## Advanced Features

### Tal-Style Tactical Preferences
- `open_file_bonus`: +40cp for rook on open file
- `tension_bonus`: +15cp per tension point
- Aggressive piece placement rewards

### Static Exchange Evaluation (SEE) System
**Two-Version Implementation:**
1. **SEE v1**: Basic material exchange calculation
2. **SEE v2**: Enhanced with improved attacker detection and sequencing
3. **Minimax Gain Calculation**: Recursive material exchange evaluation
4. **LVA Logic**: Always use Least Valuable Attacker first

### Tactical Pattern Engine
**Pattern Recognition Functions:**
- `_check_piece_for_pins()`: Pin detection for individual pieces
- `_check_direction_for_pin()`: Directional pin analysis
- `_check_for_revealed_attack()`: Discovered attack detection
- Comprehensive tactical pattern scoring

---

## Configuration Parameters

### Adjustable Weights (Centipawns)
```python
# Material bonuses/penalties
bishop_pair_bonus = 25
single_bishop_penalty = 25

# Development penalties  
same_piece_twice_penalty = 50
early_queen_penalty = 75
minor_piece_unmoved_bonus = 30

# King safety
king_safety_zone_bonus = 20
exposed_king_penalty = 150

# Tactical preferences
open_file_bonus = 40
tension_bonus = 15

# Game phase thresholds
opening_move_threshold = 12
endgame_piece_threshold = 14
```

### Component Weights
```python
# Final score calculation weights
material_score * 1.0 +
positional_score * 0.6 +
tactical_score * 0.9 +
threat_score * 0.5 +
castling_score * 0.4 +
king_safety_score * 0.8
```

---

## Evaluation Flow

1. **Terminal Position Check**: Checkmate, stalemate, insufficient material
2. **Component Evaluation**: Each category evaluated independently
3. **Weighted Combination**: Components combined with fixed weights
4. **Perspective Adjustment**: Score returned from side-to-move perspective

---

## Technical Notes

- All scores in centipawns (1/100th of a pawn)
- Evaluation from side-to-move perspective
- Compatible with UCI protocol
- Detailed debugging information available
- Extensive tactical pattern recognition
- Game phase-aware adjustments
- Advanced SEE implementation for capture evaluation

---

*Generated: August 14, 2025*  
*Cece Chess Engine v2.0 Evaluation Documentation*

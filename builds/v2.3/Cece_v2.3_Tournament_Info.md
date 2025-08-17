# Cece v2.3 Chess Engine - Tournament Ready

**Engine Name:** Cece v2.3  
**Author:** Pat Snyder  
**Built:** August 17, 2025  
**Protocol:** UCI  
**File:** Cece_v2.3.exe  

## Key Features

- **Pure Static Evaluation** - No opening book or endgame tablebase dependencies
- **Enhanced Tactical Awareness** - Improved threat detection and capture evaluation
- **Strategic Discipline** - Focuses on proper development and king safety
- **Tournament Tested** - Based on analysis of 250+ tournament games

## v2.3 Strategic Improvements

Based on extensive tournament analysis, v2.3 addresses key strategic weaknesses:

- ✅ **Eliminated rook shuffling** - Removed piece-square table incentives for premature rook moves
- ✅ **Enhanced castling priority** - 2.5x weight increase for castling evaluation
- ✅ **Better king safety** - Heavily penalizes king moves before castling
- ✅ **Improved tactical awareness** - Increased threat and capture evaluation priority
- ✅ **Stronger rook preservation** - Massive penalties for moving rooks before castling

## Arena Setup Instructions

1. **Copy** `Cece_v2.3.exe` to your engines folder
2. **Add Engine** in Arena:
   - Click "Engines" → "Install New Engine"
   - Browse to `Cece_v2.3.exe`
   - Type: UCI
   - Name: "Cece v2.3"
3. **Configure** (optional):
   - Hash: 64-512 MB (default: 64 MB)
   - Threads: 1 (single-threaded engine)
   - Time control: Any (tested from 1+0 to 120+1)

## Expected Performance

- **Playing Style:** Positional with tactical awareness
- **Strength:** ~2000-2200 Elo estimated
- **Time Management:** Efficient search, good for rapid/blitz
- **Specialties:** King safety, proper development, tactical combinations

## Version History

- **v2.3** (Aug 2025): Strategic discipline improvements, eliminates rook shuffling
- **v2.2** (Aug 2025): Enhanced rook preservation and castling evaluation  
- **v2.0** (Aug 2025): Major tactical improvements with SEE and pattern recognition
- **v1.x** (Jul 2025): Foundation builds with basic evaluation

## Technical Details

- **Language:** Python 3.13
- **Dependencies:** Embedded (python-chess)
- **Size:** 8.7 MB
- **Platform:** Windows x64
- **UCI Options:**
  - Debug (true/false)
  - Hash (1-1024 MB)
  - Threads (1-8, recommend 1)
  - MaterialWeight (50-200)
  - PositionalWeight (0-100)
  - TacticalWeight (0-100)
  - SafetyWeight (0-100)

---

**License:** GPL-3.0  
**Attribution:** Built on python-chess library by Niklas Fiekas

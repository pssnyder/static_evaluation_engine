# Static Evaluation Chess Engine
## A UCI-compliant chess engine built with modern static evaluation techniques

### Overview
This project is a fully functional chess engine that utilizes static evaluation techniques, drawing from the collective knowledge of past engines. Built from the ground up with clean, modular code and best practices, this engine demonstrates the power of well-implemented classical chess programming techniques.

### Features
- **Bitboard-based board representation** for efficient move generation and position analysis
- **Negascout (Principal Variation Search)** with alpha-beta pruning
- **Static evaluation** with piece-square tables, material balance, mobility, and king safety
- **Move ordering** using MVV-LVA, killer moves, and history heuristics
- **Quiescence search** to avoid horizon effects
- **Static Exchange Evaluation (SEE)** for accurate capture evaluation
- **UCI protocol compliance** for compatibility with chess GUIs
- **Iterative deepening** with comprehensive search statistics

### Architecture
The engine is built with a modular design consisting of:

- `bitboard.py` - Core board representation, move generation, and bitboard utilities
- `evaluation.py` - Static position evaluation with multiple factors
- `search.py` - Negascout search algorithm with move ordering and pruning
- `engine.py` - Main engine class integrating all components
- `uci_interface.py` - UCI protocol handler for GUI communication
- `test_engine.py` - Comprehensive test suite for validation

### Quick Start
```bash
# Test the engine
python test_engine.py

# Run with UCI interface (for chess GUIs)
python uci_interface.py

# Basic engine usage
python engine.py
```

### Performance
- **Move Generation**: Efficiently generates all legal moves using bitboards
- **Search Speed**: ~1000+ nodes per second on basic hardware
- **Memory Usage**: Lightweight with minimal memory footprint
- **UCI Compliance**: Full compatibility with popular chess GUIs

### Technical Details
- **Language**: Python 3.x
- **Board Representation**: 64-bit bitboards for each piece type
- **Search Algorithm**: Negascout with iterative deepening
- **Evaluation Features**: Material, positional, mobility, king safety
- **Protocol**: Universal Chess Interface (UCI)

### Testing
The engine includes comprehensive tests covering:
- Board setup and FEN parsing
- Legal move generation validation
- Position evaluation accuracy
- Search algorithm correctness
- UCI protocol compliance

Run tests with: `python test_engine.py`

### Current Status
✅ **Fully Functional** - The engine is complete and ready for use
- All core features implemented and tested
- Clean, bug-free codebase
- UCI-compliant for tournament play
- Modular design for easy enhancement

---

## What's Next
- Packaging into an installable executable for Arena
- Addition of my own piece-square tables and evaluation heuristics
- Move ordering enhancements
- Evaluation tuning based on game data


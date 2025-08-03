# Cece v1.0 - UCI Command Reference

## 📡 Universal Chess Interface (UCI) Protocol

Cece implements the complete UCI protocol for compatibility with chess GUIs.

## 🎛️ Engine Identification

### Basic Commands
```
uci          → Engine responds with id and options
isready      → Engine responds "readyok" when ready
quit         → Terminates the engine
```

### Engine Response
```
id name Cece - Static Evaluation Chess Engine
id author Your Name
option name MaterialWeight type spin default 100 min 50 max 200
option name PositionalWeight type spin default 30 min 0 max 100
option name TacticalWeight type spin default 20 min 0 max 100
option name SafetyWeight type spin default 15 min 0 max 100
uciok
```

## ⚙️ Configuration Options

### Setting Engine Options
```
setoption name MaterialWeight value 120
setoption name PositionalWeight value 40
setoption name TacticalWeight value 25
setoption name SafetyWeight value 10
```

### Available Options

| Option | Type | Min | Max | Default | Description |
|--------|------|-----|-----|---------|-------------|
| MaterialWeight | spin | 50 | 200 | 100 | Weight for material evaluation |
| PositionalWeight | spin | 0 | 100 | 30 | Weight for positional factors |
| TacticalWeight | spin | 0 | 100 | 20 | Weight for tactical patterns |
| SafetyWeight | spin | 0 | 100 | 15 | Weight for king safety |

## 🎯 Position Setup

### Starting Position
```
position startpos
```

### Position with Moves
```
position startpos moves e2e4 e7e5 g1f3 b8c6
```

### FEN Position
```
position fen rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1
```

### FEN with Moves
```
position fen [fen_string] moves e7e5 g1f3
```

## 🔍 Search Commands

### Fixed Depth Search
```
go depth 10      # Search exactly 10 plies
go depth 15      # Search exactly 15 plies
```

### Timed Search
```
go movetime 5000    # Search for 5 seconds
go movetime 30000   # Search for 30 seconds
```

### Time Control
```
go wtime 300000 btime 300000 winc 5000 binc 5000
# White: 5 minutes, Black: 5 minutes, 5 second increment
```

### Infinite Search
```
go infinite    # Search until "stop" command
stop          # Stop current search
```

### Node-Limited Search
```
go nodes 100000    # Search exactly 100,000 nodes
```

## 📊 Engine Output During Search

### Info Strings
```
info depth 8 score cp 25 nodes 12547 nps 5234 time 2398 pv e2e4 e7e5
```

### Output Components
- `depth 8`: Current search depth
- `score cp 25`: Evaluation in centipawns (+0.25 for White)
- `nodes 12547`: Nodes searched
- `nps 5234`: Nodes per second
- `time 2398`: Time elapsed in milliseconds
- `pv e2e4 e7e5`: Principal variation (best line)

### Final Response
```
bestmove e2e4    # Best move found
bestmove e2e4 ponder e7e5    # Best move with ponder move
```

## 🎮 Complete Game Example

```
> uci
< id name Cece - Static Evaluation Chess Engine
< id author Your Name
< [options listed]
< uciok

> isready
< readyok

> ucinewgame
< [ready for new game]

> position startpos
< [position set]

> go depth 8
< info depth 1 score cp 26 nodes 20 nps 2000 time 10 pv e2e4
< info depth 2 score cp 0 nodes 156 nps 3120 time 50 pv e2e4 e7e5
< [... more depth info ...]
< info depth 8 score cp 25 nodes 12547 nps 5234 time 2398 pv e2e4 e7e5
< bestmove e2e4

> position startpos moves e2e4 e7e5
> go movetime 3000
< [search info for 3 seconds]
< bestmove g1f3

> quit
< [engine terminates]
```

## 🔧 Advanced Features

### New Game Setup
```
ucinewgame       # Prepare for new game (clears hash, history)
```

### Pondering Support
Cece supports pondering (thinking on opponent's time):
```
go ponder        # Start pondering mode
ponderhit        # Opponent played predicted move
stop             # Stop pondering
```

## ⚠️ Error Handling

### Invalid Commands
- Unknown commands are ignored
- Malformed position strings default to starting position
- Invalid moves are rejected

### Search Interruption
- `stop` command gracefully stops current search
- Engine always responds with `bestmove` even if interrupted

---

This UCI implementation ensures maximum compatibility with chess GUIs while providing full access to Cece's evaluation capabilities.

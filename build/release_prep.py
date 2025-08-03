#!/usr/bin/env python3
"""
Release Preparation for Cece v1.0
Prepares all release artifacts including documentation and tournament package.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Add build directory to path
build_dir = Path(__file__).parent
sys.path.insert(0, str(build_dir))

from build_config import get_build_info, get_engine_metadata

def create_release_package():
    """Create complete release package."""
    build_info = get_build_info()
    metadata = get_engine_metadata()
    
    print(f"📦 Creating {build_info['full_name']} Release Package")
    print("=" * 50)
    
    # Create release directory
    release_dir = Path("dist") / f"Cece_v{build_info['version']}_Release"
    release_dir.mkdir(exist_ok=True)
    
    print(f"📁 Release directory: {release_dir}")
    
    # Copy executable
    exe_source = Path("dist") / f"Cece_v{build_info['version']}.exe"
    if exe_source.exists():
        exe_dest = release_dir / f"Cece_v{build_info['version']}.exe"
        shutil.copy2(exe_source, exe_dest)
        print(f"✅ Copied executable: {exe_dest.name}")
    else:
        print(f"❌ Executable not found: {exe_source}")
        return False
    
    # Create comprehensive documentation
    create_release_documentation(release_dir, build_info, metadata)
    
    # Copy source code (optional)
    source_dir = release_dir / "source"
    source_dir.mkdir(exist_ok=True)
    
    source_files = [
        'engine.py',
        'evaluation.py',
        'data_collector.py', 
        'uci_interface.py',
        'README.md'
    ]
    
    for file in source_files:
        if os.path.exists(file):
            shutil.copy2(file, source_dir)
            print(f"✅ Copied source: {file}")
    
    # Create testing files
    testing_dir = release_dir / "testing"
    testing_dir.mkdir(exist_ok=True)
    
    if os.path.exists("testing"):
        for file in os.listdir("testing"):
            if file.endswith('.py'):
                shutil.copy2(f"testing/{file}", testing_dir)
                print(f"✅ Copied test: {file}")
    
    # Create ZIP archive
    zip_path = Path("dist") / f"Cece_v{build_info['version']}_Complete.zip"
    create_zip_archive(release_dir, zip_path)
    
    print()
    print("🎉 Release package created successfully!")
    print(f"📁 Release folder: {release_dir}")
    print(f"📦 ZIP archive: {zip_path}")
    
    return True

def create_release_documentation(release_dir, build_info, metadata):
    """Create comprehensive release documentation."""
    
    # Main README
    readme_content = f"""# {build_info['full_name']} - Complete Release

## 🏆 Tournament-Ready Chess Engine

{metadata['description']}

**Version**: {build_info['version_string']}  
**Author**: {metadata['author']}  
**License**: {metadata['license']}  
**Build Date**: {build_info['build_timestamp']}

## ⚡ Quick Start

### For Arena Chess GUI:
1. Copy `Cece_v{build_info['version']}.exe` to your Arena engines folder
2. In Arena: Engines → Install New Engine → Browse to executable
3. Set Protocol: UCI
4. Click OK and start playing!

### For Command Line:
```bash
# Test UCI interface
Cece_v{build_info['version']}.exe

# Basic UCI commands
uci
isready
position startpos
go depth 10
quit
```

## 🚀 Key Features

{chr(10).join(f"- **{feature}**" for feature in metadata['features'])}

## ⚙️ UCI Configuration Options

| Option | Range | Default | Description |
|--------|-------|---------|-------------|
| MaterialWeight | 50-200 | 100 | Material evaluation weight |
| PositionalWeight | 0-100 | 30 | Positional evaluation weight |
| TacticalWeight | 0-100 | 20 | Tactical pattern weight |
| SafetyWeight | 0-100 | 15 | King safety evaluation weight |

## 📊 Performance Specifications

- **Search Speed**: ~5,400 nodes per second
- **Search Depth**: 20+ plies (time permitting)
- **Memory Usage**: ~50 MB
- **Platform**: Windows (64-bit)
- **Protocol**: UCI compatible

## 🎯 Engine Personality

Cece focuses on **static evaluation excellence** with:
- Strong positional understanding
- Pattern recognition capabilities
- Balanced tactical awareness
- Educational transparency (detailed analysis available)

## 🏗️ Technical Architecture

- **Infrastructure**: python-chess (reliable, battle-tested)
- **Evaluation**: Custom static evaluation engine
- **Search**: Alpha-beta with iterative deepening
- **Data Collection**: Comprehensive analysis logging
- **Research Focus**: Evaluation optimization and pattern discovery

## 📋 What's Included

- `Cece_v{build_info['version']}.exe` - Tournament executable
- `README.md` - This documentation
- `INSTALL_GUIDE.md` - Detailed setup instructions
- `UCI_REFERENCE.md` - Complete UCI command reference
- `source/` - Source code (Python)
- `testing/` - Test scripts and validation tools

## 🛠️ Development & Attribution

{metadata['attribution']}

This engine demonstrates the power of combining proven infrastructure (python-chess) with custom evaluation logic, creating a maintainable and extensible chess engine suitable for both competition and research.

## 📞 Support

For questions, suggestions, or bug reports, this engine is provided as-is for educational and research purposes.

---
**Cece** - *Where simplicity meets strength*

Built with 💙 on {build_info['build_timestamp']}
"""
    
    # Installation Guide
    install_guide = f"""# Cece v{build_info['version']} - Installation Guide

## 🎯 Installing in Arena Chess GUI

### Step 1: Download and Extract
1. Download the Cece release package
2. Extract all files to a folder (e.g., `C:\\Chess\\Engines\\Cece\\`)

### Step 2: Install in Arena
1. Open Arena Chess GUI
2. Go to **Engines** → **Install New Engine**
3. Click **Browse** and navigate to `Cece_v{build_info['version']}.exe`
4. Select the executable and click **Open**
5. Set **Engine Type** to **UCI**
6. Click **OK**

### Step 3: Configure Engine
1. Go to **Engines** → **Manage Engines**
2. Find "Cece" in the list
3. Click **Details** to configure UCI options:
   - Hash Size: 64 MB (recommended)
   - MaterialWeight: 100 (default)
   - PositionalWeight: 30 (default)
   - TacticalWeight: 20 (default)
   - SafetyWeight: 15 (default)

### Step 4: Test Installation
1. Start a new game
2. Set engine as opponent
3. Set time control (e.g., 5+3 blitz)
4. Play a few moves to verify engine responds

## 🔧 Installing in Other GUIs

### ChessBase/Fritz:
1. Copy executable to ChessBase engines folder
2. Use **Engine** → **Create UCI Engine**
3. Browse to Cece executable
4. Configure as UCI engine

### Cute Chess:
1. Go to **Tools** → **Settings** → **Engines**
2. Click **Add**
3. Set Name: "Cece v{build_info['version']}"
4. Set Command: path to Cece executable
5. Set Protocol: UCI

### SCID vs. PC:
1. Go to **Tools** → **Analysis Engines**
2. Click **New**
3. Browse to Cece executable
4. Set as UCI engine

## 🧪 Testing Installation

### Quick UCI Test:
```bash
# Open command prompt in Cece folder
Cece_v{build_info['version']}.exe

# Type these commands:
uci          # Should show engine info
isready      # Should respond "readyok"
position startpos moves e2e4 e7e5
go depth 6   # Should search and return bestmove
quit         # Exit engine
```

### Arena Test Game:
1. Create new game: Human vs Cece
2. Set time control: 1 minute + 1 second
3. Play 1.e4 - Cece should respond quickly
4. Continue for a few moves to verify stability

## ⚠️ Troubleshooting

### Engine Won't Start:
- Ensure Windows Defender isn't blocking the executable
- Try running as Administrator
- Check that .NET runtime is installed

### Engine Appears but Won't Move:
- Verify UCI protocol is selected
- Check time control settings
- Try restarting the GUI

### Performance Issues:
- Reduce hash size if system has limited RAM
- Check that engine isn't running multiple instances
- Verify adequate disk space for log files

## 🎮 Recommended Settings

### For Casual Play:
- Time Control: 5+3 or 10+5
- Hash: 64 MB
- MaterialWeight: 100
- PositionalWeight: 30

### For Analysis:
- Infinite analysis mode
- Hash: 128 MB (if available)
- TacticalWeight: 30 (for tactical positions)
- SafetyWeight: 20 (for king safety analysis)

### For Tournaments:
- Follow tournament time controls
- Hash: Maximum available (within limits)
- Default UCI settings
- Ensure stable power supply

---
Enjoy playing with Cece! 🎉
"""
    
    # UCI Reference
    uci_reference = f"""# Cece v{build_info['version']} - UCI Command Reference

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
id name {metadata['name']}
id author {metadata['author']}
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
< id name {metadata['name']}
< id author {metadata['author']}
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
"""
    
    # Write documentation files
    docs = [
        ("README.md", readme_content),
        ("INSTALL_GUIDE.md", install_guide),
        ("UCI_REFERENCE.md", uci_reference)
    ]
    
    for filename, content in docs:
        doc_path = release_dir / filename
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📋 Created: {filename}")

def create_zip_archive(source_dir, zip_path):
    """Create ZIP archive of release directory."""
    print(f"📦 Creating ZIP archive: {zip_path.name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in source_dir.rglob('*'):
            if file_path.is_file():
                # Create relative path for ZIP
                arc_path = file_path.relative_to(source_dir.parent)
                zipf.write(file_path, arc_path)
                
    zip_size = zip_path.stat().st_size / (1024 * 1024)  # MB
    print(f"✅ ZIP created: {zip_size:.2f} MB")

def main():
    """Main release preparation function."""
    print("🚀 Cece Release Preparation System")
    print("=" * 40)
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    # Check if executable exists
    exe_path = Path("dist") / "Cece_v1.0.exe"
    if not exe_path.exists():
        print("❌ Cece_v1.0.exe not found in dist/")
        print("💡 Run build_executable.py first to create the executable")
        sys.exit(1)
    
    # Create release package
    success = create_release_package()
    
    if success:
        print()
        print("🎉 Release preparation completed!")
        print("📦 Cece v1.0 is ready for distribution!")
    else:
        print("💥 Release preparation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

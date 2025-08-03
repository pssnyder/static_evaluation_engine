# Cece v1.0 - Installation Guide

## 🎯 Installing in Arena Chess GUI

### Step 1: Download and Extract
1. Download the Cece release package
2. Extract all files to a folder (e.g., `C:\Chess\Engines\Cece\`)

### Step 2: Install in Arena
1. Open Arena Chess GUI
2. Go to **Engines** → **Install New Engine**
3. Click **Browse** and navigate to `Cece_v1.0.exe`
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
3. Set Name: "Cece v1.0"
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
Cece_v1.0.exe

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

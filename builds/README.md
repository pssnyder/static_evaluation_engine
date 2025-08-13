# Cece Chess Engine Build System

This directory contains the build system for creating standalone executables of the Cece chess engine.

## Quick Start

To build any version of Cece:

1. Make sure you have a version directory (e.g., `v2.1/`)
2. Run the build script:
   ```bash
   python build_exe.py v2.1
   ```
3. The executable will be created in the `../dist/` directory

## Build Process

The `build_exe.py` script performs the following steps:

1. **Copy Source Files**: Copies core engine files from the root directory to `<version>/work/`
   - `engine.py`
   - `evaluation.py`
   - `uci_interface.py`
   - `data_collector.py`
   - `requirements.txt` (if present)

2. **Create Launcher**: Generates `cece_launcher.py` that starts the UCI interface

3. **Generate Spec File**: Creates a PyInstaller spec file (`Cece_<version>.spec`)

4. **Build Executable**: Runs PyInstaller to create the standalone .exe

5. **Move to Dist**: Places final executable in `../dist/Cece_<version>.exe`

## Directory Structure

```
builds/
├── build_exe.py           # Main build script
├── README.md             # This file
├── v2.1/                 # Version directory
│   ├── work/             # Working files (created during build)
│   ├── development/      # Development files (optional)
│   └── testing/          # Testing files (optional)
└── ../dist/              # Final executables
    └── Cece_v2.1.exe     # Built executable
```

## Requirements

- Python 3.8+
- PyInstaller (`pip install pyinstaller`)
- python-chess (`pip install python-chess`)

## Usage Examples

```bash
# Build version 2.1
python build_exe.py v2.1

# Build version 2.0 (if directory exists)
python build_exe.py v2.0
```

## Notes

- The build script automatically cleans the work directory before building
- All working files are contained within the version's work directory
- The final executable is self-contained and includes all dependencies
- Build artifacts remain in the work directory for debugging if needed

---
*Cece Chess Engine Build System*

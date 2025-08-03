#!/usr/bin/env python3
"""
Build script for Cece (Static Evaluation Chess Engine) executable.
Creates a standalone executable for tournament use in chess GUIs like Arena.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from build_config import get_build_info, get_engine_metadata

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking build dependencies...")
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✅ PyInstaller: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    # Check python-chess
    try:
        import chess
        print(f"✅ python-chess: {chess.__version__}")
    except ImportError:
        print("❌ python-chess not found. Install with: pip install python-chess")
        return False
    
    # Check required engine files
    required_files = ['engine.py', 'evaluation.py', 'data_collector.py', 'uci_interface.py']
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            return False
    
    return True

def create_launcher_script():
    """Create a launcher script for the UCI interface."""
    build_info = get_build_info()
    metadata = get_engine_metadata()
    
    launcher_content = f'''#!/usr/bin/env python3
"""
Cece v{build_info["version"]} - UCI Launcher
{metadata["description"]}

Author: {metadata["author"]}
License: {metadata["license"]}
Attribution: {metadata["attribution"]}

This is the main entry point for the Cece chess engine.
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """Main entry point for Cece UCI interface."""
    try:
        from uci_interface import UCIInterface
        
        # Create and run UCI interface
        uci = UCIInterface()
        uci.run()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open('cece_launcher.py', 'w') as f:
        f.write(launcher_content)
    
    print("✅ Created UCI launcher script")

def build_executable():
    """Build the Cece executable using PyInstaller."""
    # Get dynamic build info
    build_info = get_build_info()
    metadata = get_engine_metadata()
    
    print(f"🔧 Building {build_info['full_name']} Executable")
    print("=" * 60)
    
    # Display build information
    print(f"Engine: {build_info['full_name']}")
    print(f"Version: {build_info['version_string']}")
    print(f"Description: {metadata['description']}")
    print(f"Author: {metadata['author']}")
    print(f"Executable: {build_info['executable_name']}")
    print(f"Build Time: {build_info['build_timestamp']}")
    print()
    
    print("Features:")
    for i, feature in enumerate(metadata['features'], 1):
        print(f"  {i}. {feature}")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Build failed: Missing dependencies")
        return False
    
    # Create launcher script
    create_launcher_script()
    
    # Prepare build directory
    build_dir = Path("build") / f"v{build_info['version']}"
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy source files to build directory
    source_files = [
        'engine.py',
        'evaluation.py', 
        'data_collector.py',
        'uci_interface.py',
        'cece_launcher.py'
    ]
    
    print("📁 Copying source files to build directory...")
    for file in source_files:
        if os.path.exists(file):
            shutil.copy2(file, build_dir)
            print(f"   ✅ {file}")
    
    # Build command
    executable_name = build_info['executable_name'].replace('.exe', '')
    
    cmd = [
        "python", "-m", "PyInstaller",
        "--onefile",                           # Single executable
        "--name", executable_name,             # Dynamic executable name
        "--distpath", "dist",                  # Output to dist folder
        "--workpath", str(build_dir / "work"), # Work directory
        "--specpath", str(build_dir),          # Spec file location
        "--clean",                             # Clean before build
        
        # Hidden imports for dependencies
        "--hidden-import", "chess",
        "--hidden-import", "chess.engine",
        "--hidden-import", "chess.pgn",
        "--hidden-import", "chess.svg",
        "--hidden-import", "chess.polyglot",
        
        # Console application (no GUI)
        "--console",
        
        # Entry point
        "cece_launcher.py"
    ]
    
    print("🏗️  Starting PyInstaller build...")
    print("Command:", " ".join(cmd))
    print()
    
    try:
        # Run PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build completed successfully!")
        print()
        
        # Check if executable was created
        exe_path = Path("dist") / f"{executable_name}.exe"
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"📦 Executable created: {exe_path}")
            print(f"📏 File size: {exe_size:.2f} MB")
            
            # Create tournament folder
            tournament_dir = Path("dist") / build_info['tournament_folder']
            tournament_dir.mkdir(exist_ok=True)
            
            # Copy executable to tournament folder
            tournament_exe = tournament_dir / f"{executable_name}.exe"
            shutil.copy2(exe_path, tournament_exe)
            
            # Create README for tournament
            create_tournament_readme(tournament_dir, build_info, metadata)
            
            print(f"🏆 Tournament package: {tournament_dir}")
            print()
            print("🎯 Next Steps:")
            print(f"   1. Test executable: {exe_path}")
            print(f"   2. Configure in Arena: {tournament_exe}")
            print(f"   3. Tournament ready: {tournament_dir}")
            
        else:
            print("❌ Executable not found after build")
            return False
            
    except subprocess.CalledProcessError as e:
        print("❌ Build failed!")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    
    finally:
        # Cleanup launcher script
        if os.path.exists('cece_launcher.py'):
            os.remove('cece_launcher.py')
    
    return True

def create_tournament_readme(tournament_dir, build_info, metadata):
    """Create README file for tournament package."""
    readme_content = f"""# {build_info['full_name']} - Tournament Package

## Engine Information
- **Name**: {metadata['name']}
- **Version**: {build_info['version_string']}
- **Author**: {metadata['author']}
- **License**: {metadata['license']}
- **Build Date**: {build_info['build_timestamp']}

## Description
{metadata['description']}

## Key Features
{chr(10).join(f"- {feature}" for feature in metadata['features'])}

## Arena Setup Instructions

1. **Install Engine**:
   - Copy `{build_info['executable_name']}` to your Arena engines folder
   - Or use the full path to this executable

2. **Configure in Arena**:
   - Open Arena Chess GUI
   - Go to Engines -> Install New Engine
   - Browse to `{build_info['executable_name']}`
   - Set Type: UCI
   - Click OK

3. **Engine Settings**:
   - Protocol: UCI
   - Time Control: Supports all standard time controls
   - Hash Size: 64 MB (adjustable)
   - Threads: 1 (single-threaded)

## UCI Options
- **MaterialWeight**: Adjust material evaluation weight (50-200, default 100)
- **PositionalWeight**: Adjust positional evaluation weight (0-100, default 30)
- **TacticalWeight**: Adjust tactical evaluation weight (0-100, default 20)
- **SafetyWeight**: Adjust king safety weight (0-100, default 15)

## Performance
- **Search Speed**: ~5,400 nodes per second
- **Search Depth**: Up to 20+ plies (depending on time control)
- **Evaluation**: Advanced static evaluation with pattern recognition
- **Style**: Positional with tactical awareness

## Technical Details
- **Architecture**: Hybrid (python-chess infrastructure + custom evaluation)
- **Board Representation**: python-chess Board class
- **Search Algorithm**: Alpha-beta with iterative deepening
- **Move Ordering**: MVV-LVA, promotions, checks
- **Time Management**: Professional UCI time control support

## Attribution
{metadata['attribution']}

## Support
This engine is designed for educational and research purposes.
Enjoy exploring chess with Cece!

---
Generated on {build_info['build_timestamp']}
"""
    
    readme_path = tournament_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"📋 Created tournament README: {readme_path}")

def main():
    """Main build function."""
    print("🚀 Cece Build System")
    print("=" * 30)
    
    # Change to project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"📁 Project directory: {project_root}")
    print()
    
    # Build executable
    success = build_executable()
    
    if success:
        print("🎉 Build completed successfully!")
        print("🏁 Cece is ready for tournament play!")
    else:
        print("💥 Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()

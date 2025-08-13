"""
Simple Cece Chess Engine Build Script

This script builds a standalone executable from any version folder.
Usage: python build_exe.py <version_folder>
Example: python build_exe.py v2.1

The script will:
1. Copy source files to builds/<version>/work/ directory
2. Generate PyInstaller spec file
3. Build the executable
4. Move final .exe to dist/ directory

Author: Pat Snyder
License: GPL-3.0
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python build_exe.py <version_folder>")
        print("Example: python build_exe.py v2.1")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Setup paths
    script_dir = Path(__file__).parent  # builds directory
    root_dir = script_dir.parent        # static_evaluation_engine directory
    version_dir = script_dir / version
    build_dir = version_dir / "build"   # Use existing build directory
    dist_dir = root_dir / "dist"
    
    print(f"Building Cece Chess Engine {version}")
    print(f"Version directory: {version_dir}")
    print(f"Build directory: {build_dir}")
    print(f"Output directory: {dist_dir}")
    
    # Validate version directory exists
    if not version_dir.exists():
        print(f"Error: Version directory {version_dir} does not exist!")
        sys.exit(1)
    
    # Clean and create build directory for PyInstaller files
    if build_dir.exists():
        print("Cleaning existing build directory...")
        try:
            shutil.rmtree(build_dir)
        except PermissionError:
            print("Warning: Could not remove build directory (files may be in use)")
            print("Continuing with existing build directory...")
    
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create dist directory if it doesn't exist
    dist_dir.mkdir(exist_ok=True)
    
    # Copy core engine files from root directory to version directory
    core_files = [
        "engine.py",
        "evaluation.py", 
        "uci_interface.py",
        "data_collector.py"
    ]
    
    print("Updating core engine files from root directory...")
    for file in core_files:
        src = root_dir / file
        dst = version_dir / file
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Updated {file}")
        else:
            print(f"  Warning: {file} not found in root directory")
    
    # Copy requirements.txt if it exists
    req_file = root_dir / "requirements.txt"
    dst_req = version_dir / "requirements.txt"
    if req_file.exists():
        shutil.copy2(req_file, dst_req)
        print("  Updated requirements.txt")
    else:
        print("  Note: requirements.txt not found (optional)")
    
    # Create launcher script in version directory if it doesn't exist
    launcher_path = version_dir / "cece_launcher.py"
    if not launcher_path.exists():
        launcher_content = f'''"""
Cece Chess Engine {version} Launcher

Simple launcher that starts the UCI interface.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from uci_interface import main

if __name__ == "__main__":
    main()
'''
        
        with open(launcher_path, 'w') as f:
            f.write(launcher_content)
        print("  Created cece_launcher.py")
    else:
        print("  Found existing cece_launcher.py")
    
    # Create PyInstaller spec file in version directory
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cece_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['chess', 'chess.engine', 'chess.pgn'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Cece_{version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    spec_path = version_dir / f"Cece_{version}.spec"
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    print(f"  Created Cece_{version}.spec")
    
    # Build the executable from version directory
    print("Building executable with PyInstaller...")
    os.chdir(version_dir)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            f"Cece_{version}.spec", 
            "--clean",
            "--workpath", str(build_dir),  # Use build directory for working files
            "--distpath", str(build_dir / "dist")  # Put built exe in build/dist
        ], check=True, capture_output=True, text=True)
        
        print("Build completed successfully!")
        
        # Move executable to main dist directory
        built_exe = build_dir / "dist" / f"Cece_{version}.exe"
        final_exe = dist_dir / f"Cece_{version}.exe"
        
        if built_exe.exists():
            if final_exe.exists():
                final_exe.unlink()  # Remove existing file
            shutil.move(str(built_exe), str(final_exe))
            print(f"Executable moved to: {final_exe}")
            print(f"Build size: {final_exe.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("Error: Built executable not found!")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed!")
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)
    
    print(f"\\nBuild complete! Executable available at:")
    print(f"  {final_exe}")
    print(f"\\nTo test the engine, run:")
    print(f"  {final_exe}")

if __name__ == "__main__":
    main()

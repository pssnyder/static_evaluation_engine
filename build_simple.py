#!/usr/bin/env python3
"""
Simple Build Script for Cece Engine
===================================

Clean build process that:
1. Copies source files to build/v{VERSION}/
2. Builds from that directory 
3. Places work files in build/v{VERSION}/work/
4. Places final exe in dist/

Usage: python build_simple.py [version]
Example: python build_simple.py 1.2
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def main():
    # Get version from command line or default to 1.1
    version = sys.argv[1] if len(sys.argv) > 1 else "1.1"
    
    print(f"🚀 Building Cece v{version}")
    print("=" * 40)
    
    # Define paths
    root_dir = Path(".")
    build_dir = Path(f"build/v{version}")
    work_dir = build_dir / "work"
    dist_dir = Path("dist")
    
    # Source files to copy
    source_files = [
        "uci_interface.py",
        "engine.py", 
        "evaluation.py",
        "data_collector.py"
    ]
    
    print("📁 Setting up build directory...")
    
    # Create build directory structure
    build_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(exist_ok=True)
    dist_dir.mkdir(exist_ok=True)
    
    # Copy source files to build directory
    for file in source_files:
        if (root_dir / file).exists():
            shutil.copy2(root_dir / file, build_dir / file)
            print(f"  ✅ Copied {file}")
        else:
            print(f"  ❌ Missing {file}")
            return 1
    
    print("\n🔨 Building executable...")
    
    # Change to build directory
    original_dir = os.getcwd()
    os.chdir(build_dir)
    
    try:
        # PyInstaller command - put ALL build artifacts in work/
        cmd = [
            "pyinstaller", 
            "--onefile",
            "--console",
            f"--name=Cece_v{version}",
            "--distpath=../../dist",
            "--workpath=work",
            "--specpath=.",  # Put spec file in build/v{version}/ not work/
            "--clean",       # Clean previous build artifacts
            "uci_interface.py"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build successful!")
            
            # Check if exe was created
            exe_path = Path(f"../../dist/Cece_v{version}.exe")
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"📦 Executable created: Cece_v{version}.exe ({size_mb:.1f} MB)")
            else:
                print("❌ Executable not found in dist/")
                return 1
                
        else:
            print("❌ Build failed!")
            print("Error output:", result.stderr)
            return 1
            
    finally:
        # Return to original directory
        os.chdir(original_dir)
    
    print("\n🎯 Build complete!")
    print(f"📁 Source archived in: {build_dir}")
    print(f"🔧 Work files in: {work_dir}") 
    print(f"🎮 Executable in: dist/Cece_v{version}.exe")
    
    return 0

if __name__ == "__main__":
    exit(main())

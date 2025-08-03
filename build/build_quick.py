#!/usr/bin/env python3
"""
Quick Build Script for Cece v1.0
Creates executable and tournament package ready for Arena.
"""

import os
import sys
from pathlib import Path

# Add build directory to path
build_dir = Path(__file__).parent
sys.path.insert(0, str(build_dir))

from build_executable import main as build_main

def quick_build():
    """Quick build with minimal output."""
    print("⚡ Cece v1.0 Quick Build")
    print("=" * 25)
    
    try:
        build_main()
        print()
        print("✅ Quick build completed!")
        print("🎯 Check dist/ folder for Cece_v1.0.exe")
        
    except Exception as e:
        print(f"❌ Build error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    quick_build()

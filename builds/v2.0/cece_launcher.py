#!/usr/bin/env python3
"""
Cece v2.0 Chess Engine Launcher
Launches the Cece v2.0 chess engine with UCI interface
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uci_interface import UCIInterface

def main():
    """Main entry point for Cece v2.0"""
    try:
        # Create and start UCI interface
        uci = UCIInterface()
        print("Cece v2.0 Chess Engine")
        print("Ready for UCI commands...")
        uci.run()
    except KeyboardInterrupt:
        print("\nCece v2.0 shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting Cece v2.0: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

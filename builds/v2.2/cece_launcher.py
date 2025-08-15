#!/usr/bin/env python3
"""
Cece Chess Engine v2.2 Launcher
================================

Critical Improvements in v2.2:
- Castling system overhaul (227-point bonus)
- Rook preservation system (540-point penalty)
- Enhanced development penalties
- SEE function consolidation
- Tournament issue fixes

Author: Pat Snyder
Based on python-chess by Niklas Fiekas
"""

import sys
import os
import chess

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from uci_interface import UCIInterface

def main():
    """Launch Cece v2.2 chess engine with UCI interface."""
    print("Cece Chess Engine v2.2")
    print("======================")
    print("Author: Pat Snyder")
    print("Critical improvements: Castling priority, Rook preservation, Development fixes")
    print("Built on python-chess by Niklas Fiekas")
    print("Ready for UCI commands...")
    print()
    
    # Initialize and run UCI interface
    try:
        uci = UCIInterface()
        uci.run()
    except KeyboardInterrupt:
        print("\\nShutting down Cece v2.2...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

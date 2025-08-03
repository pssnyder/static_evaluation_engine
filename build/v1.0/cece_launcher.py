#!/usr/bin/env python3
"""
Cece v1.0 - UCI Launcher
Minimalist chess engine focusing on evaluation excellence

Author: Your Name
License: GPL-3.0
Attribution: Built on python-chess by Niklas Fiekas

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
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

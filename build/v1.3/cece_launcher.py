#!/usr/bin/env python3
"""
Cece v1.3 - UCI Launcher
Chess engine with enhanced dynamic evaluation and tactical improvements

Author: Pat Snyder
License: GPL-3.0
Attribution: Built on python-chess by Niklas Fiekas

This is the main entry point for the Cece v1.3 chess engine.
Features:
- Dynamic piece values with bishop pair logic
- Game phase-aware PST tables
- Development tracking and penalties
- Enhanced king safety evaluation
- Tal-style tactical preferences
- Adaptive time management
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def main():
    """Main entry point for Cece v1.3 UCI interface."""
    try:
        from uci_interface import UCIInterface
        
        print("Starting Cece v1.3 - Enhanced Chess Engine", file=sys.stderr)
        print("Features: Dynamic evaluation, tactical improvements, adaptive time management", file=sys.stderr)
        
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

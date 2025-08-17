"""
Cece Chess Engine v2.3 Launcher

Simple launcher that starts the UCI interface.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from uci_interface import main

if __name__ == "__main__":
    main()

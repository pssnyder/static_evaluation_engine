"""
Cece Chess Engine v2.1 Launcher

Simple launcher that starts the UCI interface.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import all required modules explicitly for PyInstaller
import engine
import evaluation
import data_collector
import uci_interface

if __name__ == "__main__":
    uci_interface.main()

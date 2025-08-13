#!/usr/bin/env python3
"""
Quick test of the corrected enhanced puzzle tester.
"""

import os
import sys
sys.path.append("s:/Maker Stuff/Programming/Static Evaluation Chess Engine/static_evaluation_engine/testing")

from enhanced_puzzle_tester import EnhancedPuzzleTester

def test_corrected_logic():
    """Test the corrected puzzle logic with a few puzzles."""
    
    engine_path = "s:/Maker Stuff/Programming/Static Evaluation Chess Engine/static_evaluation_engine/dist/Cece_v1.0.exe"
    csv_path = "s:/Maker Stuff/Programming/Static Evaluation Chess Engine/static_evaluation_engine/testing/lichess_db_puzzle.csv"
    
    if not os.path.exists(engine_path):
        print(f"❌ Engine not found: {engine_path}")
        return
        
    if not os.path.exists(csv_path):
        print(f"❌ CSV not found: {csv_path}")
        return
    
    print("🧪 Testing Corrected Puzzle Logic")
    print("=" * 50)
    
    tester = EnhancedPuzzleTester(engine_path, csv_path)
    
    # Test just 2 puzzles to verify the logic
    tester.run_test_session(
        count=2,
        rating_min=1200,
        rating_max=1800,
        themes_filter=["mate"]  # Start with mate puzzles
    )

if __name__ == "__main__":
    test_corrected_logic()

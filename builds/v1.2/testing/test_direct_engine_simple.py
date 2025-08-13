#!/usr/bin/env python3
"""
Direct engine test - bypass UCI interface entirely
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from engine import ChessEngine

def test_direct_engine():
    """Test the engine directly without UCI interface."""
    
    print("🎯 Direct Engine Test (No UCI)")
    print("=" * 35)
    
    try:
        # Create engine directly
        engine = ChessEngine()
        print(f"✅ Engine initialized: {engine.info['name']}")
        
        # Test 1: Starting position
        print("\n--- Test 1: Starting Position ---")
        engine.set_position(None, [])
        print(f"Position: {engine.board.fen()}")
        
        # Get best move
        print("Searching...")
        best_move = engine.get_best_move(depth=3, time_limit=3.0)
        print(f"Best move: {best_move}")
        
        if best_move:
            print("✅ Direct engine working correctly!")
        else:
            print("❌ Direct engine returned None")
            
        # Test 2: After e4
        print("\n--- Test 2: After 1.e4 ---")
        engine.set_position(None, ['e2e4'])
        print(f"Position: {engine.board.fen()}")
        
        best_move2 = engine.get_best_move(depth=3, time_limit=3.0)
        print(f"Best move: {best_move2}")
        
        # Test 3: Puzzle position
        print("\n--- Test 3: Puzzle Position ---")
        puzzle_fen = "2r1q1k1/8/b2b1r1p/Pp1pNpp1/3Pn3/1RPQ3P/P1B1NPP1/4R1K1 w - - 3 28"
        engine.set_position(puzzle_fen, [])
        print(f"Position: {engine.board.fen()}")
        
        best_move3 = engine.get_best_move(depth=3, time_limit=3.0)
        print(f"Best move: {best_move3}")
        
        return best_move is not None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_engine()
    if success:
        print("\n🎉 Direct engine test PASSED!")
        print("   Issue is in UCI interface, not engine core")
    else:
        print("\n💥 Direct engine test FAILED!")
        print("   Issue is in engine core")

#!/usr/bin/env python3
"""
Direct Engine Test - test the engine.py module directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from engine import ChessEngine

def test_engine_directly():
    """Test the engine directly without UCI."""
    
    print("🔧 Direct Engine Test")
    print("=" * 20)
    
    try:
        engine = ChessEngine()
        print(f"✅ Engine created: {engine.info['name']}")
        
        # Test basic functionality
        engine.set_position(None, [])
        print(f"✅ Position set: {engine.board.fen()}")
        
        # Test search
        print("🔍 Testing search...")
        best_move = engine.get_best_move(depth=3, time_limit=2.0)
        print(f"✅ Best move: {best_move}")
        
        # Test with time control scenario
        print("\n🕐 Testing time control scenario...")
        best_move2 = engine.get_best_move(depth=10, time_limit=10.0)  # 10 second limit
        print(f"✅ Best move (10s): {best_move2}")
        
        # Test short time
        print("\n⚡ Testing short time...")
        best_move3 = engine.get_best_move(depth=10, time_limit=1.0)  # 1 second limit
        print(f"✅ Best move (1s): {best_move3}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_engine_directly()
    if success:
        print("\n✅ Direct engine test PASSED")
    else:
        print("\n❌ Direct engine test FAILED")

#!/usr/bin/env python3
"""
Quick integration test for v1.3 evaluation improvements.
"""

import sys
import traceback

def test_evaluation():
    """Test the v1.3 evaluation system."""
    print("🔬 Testing v1.3 Evaluation Integration")
    print("=" * 40)
    
    try:
        # Test imports
        import chess
        print("✓ Chess module imported")
        
        from evaluation import Evaluation
        print("✓ Evaluation module imported")
        
        # Test evaluation creation
        eval_obj = Evaluation()
        print("✓ Evaluation object created")
        
        # Test basic evaluation
        board = chess.Board()
        score = eval_obj.evaluate(board)
        print(f"✓ Starting position score: {score}")
        
        # Test bad knight move (should be penalized by opening knight table)
        board.push_san('Nh3')
        score_after_nh3 = eval_obj.evaluate(board)
        print(f"✓ After Nh3 score: {score_after_nh3}")
        print(f"  Change: {score_after_nh3 - score} (should be negative)")
        
        # Test detailed evaluation
        detailed = eval_obj.evaluate_detailed(board)
        print(f"✓ Detailed evaluation keys: {list(detailed.keys())}")
        
        print("\n🎉 v1.3 evaluation integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

def test_engine():
    """Test the v1.3 engine integration."""
    print("\n🚀 Testing v1.3 Engine Integration")
    print("=" * 40)
    
    try:
        from engine import ChessEngine
        print("✓ Engine module imported")
        
        engine = ChessEngine()
        print(f"✓ Engine created: {engine.info['name']} v{engine.info['version']}")
        
        # Test basic move search
        engine.set_position()
        print("✓ Position set to starting position")
        
        # Test analysis
        analysis = engine.analyze_position()
        print(f"✓ Position analysis completed")
        
        print("\n🎉 v1.3 engine integration successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    eval_success = test_evaluation()
    engine_success = test_engine()
    
    if eval_success and engine_success:
        print("\n🏆 All v1.3 integration tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

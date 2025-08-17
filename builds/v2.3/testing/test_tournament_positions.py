#!/usr/bin/env python3
"""
Test Cece v2.2 Against Tournament Positions

Tests the engine's evaluation and move choices in actual problem positions
from tournament games.
"""

import chess
import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation import Evaluation
from engine import ChessEngine

def test_tournament_positions():
    """Test engine performance on actual tournament problem positions"""
    print("=" * 60)
    print("TESTING TOURNAMENT PROBLEM POSITIONS")
    print("=" * 60)
    
    engine = ChessEngine()
    evaluator = Evaluation()
    
    # Test Position 1: Response to 1.e4 (from tournament where Cece played Nh6)
    print("\n1. RESPONSE TO 1.e4")
    print("-" * 30)
    board = chess.Board()
    board.push(chess.Move.from_uci("e2e4"))
    
    print(f"Position: {board.fen()}")
    
    # Get evaluation breakdown
    eval_result = evaluator.evaluate_detailed(board)
    print(f"Position evaluation: {eval_result['total_score']}")
    
    # Test specific bad moves
    test_moves = [
        ("g8h6", "Nh6 (TERRIBLE)"),
        ("g8f6", "Nf6 (normal)"),
        ("e7e5", "e5 (normal)"),
        ("c7c5", "c5 (normal)")
    ]
    
    for move_uci, move_desc in test_moves:
        test_board = board.copy()
        test_board.push(chess.Move.from_uci(move_uci))
        eval_result = evaluator.evaluate_detailed(test_board)
        print(f"  After {move_desc}: {eval_result['total_score']}")
    
    # Get engine's choice
    engine.board = board
    best_move = engine.get_best_move(depth=4)
    print(f"Engine chooses: {best_move}")
    
    # Test Position 2: Early castling opportunity
    print("\n2. CASTLING OPPORTUNITY")
    print("-" * 30)
    # Position where castling should be prioritized
    fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    board = chess.Board(fen)
    
    print(f"Position: {board.fen()}")
    eval_before = evaluator.evaluate_detailed(board)
    print(f"Evaluation before castling: {eval_before['total_score']}")
    print(f"Castling component: {eval_before['castling']}")
    
    # Test castling move
    castle_board = board.copy()
    castle_board.push(chess.Move.from_uci("e1g1"))  # Castle
    eval_after = evaluator.evaluate_detailed(castle_board)
    print(f"Evaluation after castling: {eval_after['total_score']}")
    print(f"Castling bonus: {eval_after['total_score'] - eval_before['total_score']}")
    
    # Get engine's choice
    engine.board = board
    best_move = engine.get_best_move(depth=3)
    print(f"Engine chooses: {best_move}")
    
    if best_move and best_move.uci() == "e1g1":
        print("✅ Engine correctly chooses to castle!")
    else:
        print("❌ Engine doesn't castle - investigating other moves")
    
    # Test Position 3: Rook preservation
    print("\n3. ROOK PRESERVATION TEST")
    print("-" * 30)
    # Position where rook should not move early
    board = chess.Board()
    moves = ["e2e4", "e7e5", "f1c4", "f8c5", "g1f3", "g8f6"]
    for move in moves:
        board.push(chess.Move.from_uci(move))
    
    print(f"Position: {board.fen()}")
    eval_before = evaluator.evaluate_detailed(board)
    print(f"Evaluation: {eval_before['total_score']}")
    print(f"Rook preservation: {eval_before['rook_preservation']}")
    
    # Test bad rook move
    bad_board = board.copy()
    bad_board.push(chess.Move.from_uci("h1g1"))  # Bad rook move
    eval_bad = evaluator.evaluate_detailed(bad_board)
    print(f"After Rg1: {eval_bad['total_score']}")
    print(f"Rook preservation penalty: {eval_bad['rook_preservation']}")
    print(f"Total penalty: {eval_bad['total_score'] - eval_before['total_score']}")
    
    # Get engine's choice
    engine.board = board
    best_move = engine.get_best_move(depth=3)
    print(f"Engine chooses: {best_move}")
    
    if best_move and best_move.uci() == "h1g1":
        print("❌ Engine still wants to move rook early!")
    else:
        print("✅ Engine avoids early rook moves")

def test_evaluation_components():
    """Test that all evaluation components are balanced"""
    print("\n" + "=" * 60)
    print("EVALUATION COMPONENT BALANCE TEST")
    print("=" * 60)
    
    evaluator = Evaluation()
    
    # Test position with clear tactical vs positional tradeoffs
    fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    board = chess.Board(fen)
    
    result = evaluator.evaluate_detailed(board)
    
    print("Component breakdown:")
    for component, score in result.items():
        if component != 'total_score':
            print(f"  {component:20}: {score:6}")
    print(f"  {'TOTAL':20}: {result['total_score']:6}")
    
    # Verify weights are having proper effect
    print(f"\nWeighted impact:")
    print(f"  Material (×1.0):         {result.get('material', 0) * 1.0:6}")
    print(f"  Positional (×0.6):       {result.get('positional', 0) * 0.6:6}")
    print(f"  Tactical (×0.9):         {result.get('tactical', 0) * 0.9:6}")
    print(f"  Threats (×0.5):          {result.get('threats', 0) * 0.5:6}")
    print(f"  Castling (×1.5):         {result.get('castling', 0) * 1.5:6}")
    print(f"  King Safety (×0.8):      {result.get('king_safety', 0) * 0.8:6}")
    print(f"  Rook Preservation (×1.2): {result.get('rook_preservation', 0) * 1.2:6}")

if __name__ == "__main__":
    print("CECE v2.2 TOURNAMENT POSITION TESTS")
    print("Testing engine performance on actual problem positions")
    
    try:
        test_tournament_positions()
        test_evaluation_components()
        
        print("\n" + "=" * 60)
        print("✅ TOURNAMENT POSITION TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

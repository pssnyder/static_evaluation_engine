#!/usr/bin/env python3
"""
Test Cece v2.2 Critical Improvements

Tests the most critical fixes:
1. Castling system enhancement
2. Rook preservation 
3. Opening development penalties
4. SEE function consolidation
"""

import chess
import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation import Evaluation
from engine import ChessEngine

def test_castling_priority():
    """Test that castling is heavily prioritized"""
    print("=" * 60)
    print("TESTING CASTLING PRIORITY")
    print("=" * 60)
    
    # Position where castling should be strongly preferred
    fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    board = chess.Board(fen)
    evaluator = Evaluation()
    
    print(f"Position: {fen}")
    print(f"Can white castle kingside: {board.has_kingside_castling_rights(chess.WHITE)}")
    print(f"Can white castle queenside: {board.has_queenside_castling_rights(chess.WHITE)}")
    
    result = evaluator.evaluate_detailed(board)
    print(f"Castling score: {result['castling']}")
    print(f"Rook preservation score: {result['rook_preservation']}")
    print(f"Total evaluation: {result['total_score']}")
    
    # Test position after castling
    board_castled = chess.Board(fen)
    board_castled.push(chess.Move.from_uci("e1g1"))  # Castle kingside
    
    result_castled = evaluator.evaluate_detailed(board_castled)
    print(f"\nAfter castling:")
    print(f"Castling score: {result_castled['castling']}")
    print(f"Total evaluation: {result_castled['total_score']}")
    print(f"Castling bonus: {result_castled['total_score'] - result['total_score']}")

def test_early_rook_penalty():
    """Test that early rook moves are heavily penalized"""
    print("\n" + "=" * 60)
    print("TESTING EARLY ROOK MOVE PENALTIES")
    print("=" * 60)
    
    # Opening position
    board = chess.Board()
    evaluator = Evaluation()
    
    # Move pieces to expose rook but keep king on starting square
    moves = ["e2e4", "e7e5", "f1c4", "f8c5", "g1f3", "g8f6"]
    for move_str in moves:
        board.push(chess.Move.from_uci(move_str))
    
    print(f"Position after development: {board.fen()}")
    
    # Evaluate before rook move
    result_before = evaluator.evaluate_detailed(board)
    print(f"Evaluation before rook move: {result_before['total_score']}")
    print(f"Rook preservation score: {result_before['rook_preservation']}")
    
    # Now move the rook (destroying castling)
    board.push(chess.Move.from_uci("h1g1"))  # Move rook, lose castling
    
    result_after = evaluator.evaluate_detailed(board)
    print(f"Evaluation after rook move: {result_after['total_score']}")
    print(f"Rook preservation score: {result_after['rook_preservation']}")
    print(f"Penalty for early rook move: {result_after['total_score'] - result_before['total_score']}")

def test_knight_rim_penalties():
    """Test that knight rim moves are heavily penalized"""
    print("\n" + "=" * 60)
    print("TESTING KNIGHT RIM PENALTIES")
    print("=" * 60)
    
    board = chess.Board()
    evaluator = Evaluation()
    
    # Test normal knight development
    board.push(chess.Move.from_uci("g1f3"))  # Good knight development
    result_good = evaluator.evaluate_detailed(board)
    print(f"After Nf3 (good): {result_good['total_score']}")
    
    # Reset and test bad knight move
    board = chess.Board()
    board.push(chess.Move.from_uci("g1h3"))  # Bad knight to rim
    result_bad = evaluator.evaluate_detailed(board)
    print(f"After Nh3 (bad): {result_bad['total_score']}")
    print(f"Penalty for rim knight: {result_bad['total_score'] - result_good['total_score']}")
    
    # Test the terrible Nh6 that appeared in tournament
    board = chess.Board()
    board.push(chess.Move.from_uci("e2e4"))
    board.push(chess.Move.from_uci("g8h6"))  # Terrible Nh6
    result_terrible = evaluator.evaluate_detailed(board)
    print(f"After 1.e4 Nh6 (terrible): {result_terrible['total_score']}")

def test_see_functionality():
    """Test that SEE function works correctly"""
    print("\n" + "=" * 60)
    print("TESTING SEE FUNCTIONALITY")
    print("=" * 60)
    
    # Position with a simple capture
    fen = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2"
    board = chess.Board(fen)
    evaluator = Evaluation()
    
    # Test capturing the pawn
    capture_move = chess.Move.from_uci("e4d5")
    see_value = evaluator._see_evaluate_capture(board, capture_move)
    print(f"SEE value for exd5: {see_value}")
    print("Expected: 100 (win a pawn)")

def test_development_penalties():
    """Test enhanced development penalties"""
    print("\n" + "=" * 60)
    print("TESTING DEVELOPMENT PENALTIES")
    print("=" * 60)
    
    board = chess.Board()
    evaluator = Evaluation()
    
    # Good development
    moves_good = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "f8c5"]
    for move in moves_good:
        board.push(chess.Move.from_uci(move))
    
    result_good = evaluator.evaluate_detailed(board)
    print(f"Good development score: {result_good['total_score']}")
    
    # Bad development - early queen
    board = chess.Board()
    moves_bad = ["e2e4", "e7e5", "d1h5", "b8c6"]  # Early queen out
    for move in moves_bad:
        board.push(chess.Move.from_uci(move))
    
    result_bad = evaluator.evaluate_detailed(board)
    print(f"Early queen development score: {result_bad['total_score']}")
    print(f"Early queen penalty: {result_bad['total_score'] - result_good['total_score']}")

def test_engine_best_moves():
    """Test that engine now prefers good moves"""
    print("\n" + "=" * 60)
    print("TESTING ENGINE MOVE PREFERENCES")
    print("=" * 60)
    
    engine = ChessEngine()
    
    # Test response to 1.e4
    board = chess.Board()
    board.push(chess.Move.from_uci("e2e4"))
    
    print("Position after 1.e4:")
    print(board)
    
    # Get engine's preferred response
    best_move = engine.get_best_move(depth=4)
    print(f"Engine's best response: {best_move}")
    
    # Get evaluation for current position
    engine.board = board  # Set the position
    evaluation = engine.evaluator.evaluate_detailed(board)
    print(f"Evaluation: {evaluation['total_score']}")
    
    # Verify it's not the terrible Nh6
    if best_move and best_move.uci() == "g8h6":
        print("❌ FAILURE: Engine still wants to play Nh6!")
    else:
        print("✅ SUCCESS: Engine avoids Nh6")

if __name__ == "__main__":
    print("CECE v2.2 CRITICAL IMPROVEMENTS TEST")
    print("Testing castling priority, rook preservation, and development")
    
    try:
        test_castling_priority()
        test_early_rook_penalty()
        test_knight_rim_penalties()
        test_see_functionality()
        test_development_penalties()
        test_engine_best_moves()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

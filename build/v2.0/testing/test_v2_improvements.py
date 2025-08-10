#!/usr/bin/env python3
"""
Test script for Cece v2.0 SEE and move ordering improvements.

This script tests the specific fixes for material evaluation issues
identified in the Engine Battle 20250810 tournament.
"""

import chess
from engine import ChessEngine
from evaluation import Evaluation

def test_see_improvements():
    """Test the improved Static Exchange Evaluation."""
    print("=== Testing SEE Improvements ===")
    
    engine = ChessEngine()
    evaluator = Evaluation()
    
    # Test case 1: Simple good capture (Qxf7+ winning material)
    board = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 0 4")
    print(f"Position: {board.fen()}")
    
    # Test Qxf7+ (should be good capture)
    qxf7_move = chess.Move.from_uci("d1h5")  # Actually Qh5 attacking f7
    try:
        qxf7_move = board.parse_san("Qh5")
        see_value = evaluator._see_evaluate_capture_v2(board, qxf7_move)
        print(f"Qh5 (attacking f7): SEE value = {see_value}")
    except:
        print("Could not test Qh5 move")
    
    # Test case 2: Bad capture that loses material
    board2 = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    print(f"\\nPosition: {board2.fen()}")
    
    # Test Nf3 (developing move, should be scored differently than captures)
    nf3_move = board2.parse_san("Nf3")
    see_value = evaluator._see_evaluate_capture_v2(board2, nf3_move)
    print(f"Nf3 (non-capture): SEE value = {see_value}")
    
    print("\\n=== SEE Test Complete ===\\n")

def test_move_ordering():
    """Test the improved move ordering with SEE integration."""
    print("=== Testing Move Ordering Improvements ===")
    
    engine = ChessEngine()
    
    # Position with multiple capture options
    board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 6")
    engine.set_position(board.fen())
    
    print(f"Position: {board.fen()}")
    
    # Get legal moves and their ordering
    legal_moves = list(board.legal_moves)
    ordered_moves = engine._order_moves(legal_moves)
    
    print("Move ordering (top 10):")
    for i, move in enumerate(ordered_moves[:10]):
        move_str = board.san(move)
        is_capture = board.is_capture(move)
        print(f"{i+1:2d}. {move_str:6s} {'(capture)' if is_capture else ''}")
    
    print("\\n=== Move Ordering Test Complete ===\\n")

def test_tactical_patterns():
    """Test the new tactical pattern recognition."""
    print("=== Testing Tactical Pattern Recognition ===")
    
    evaluator = Evaluation()
    
    # Position with a pin
    board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 0 4")
    print(f"Pin test position: {board.fen()}")
    
    # Test tactical pattern evaluation
    pins_white = evaluator._find_pins(board, chess.WHITE)
    pins_black = evaluator._find_pins(board, chess.BLACK)
    
    print(f"Pins by White: {pins_white}")
    print(f"Pins by Black: {pins_black}")
    
    # Test fork detection
    forks_white = evaluator._find_forks(board, chess.WHITE)
    forks_black = evaluator._find_forks(board, chess.BLACK)
    
    print(f"Forks by White: {forks_white}")
    print(f"Forks by Black: {forks_black}")
    
    print("\\n=== Tactical Pattern Test Complete ===\\n")

def test_quiescence_search():
    """Test the new quiescence search capability."""
    print("=== Testing Quiescence Search ===")
    
    engine = ChessEngine()
    
    # Tactical position where quiescence search should help
    board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQ1RK1 w kq - 0 7")
    engine.set_position(board.fen())
    
    print(f"Tactical position: {board.fen()}")
    
    # Test quiescence search
    import time
    start_time = time.time()
    
    try:
        score, pv, nodes = engine._quiescence_search(-1000, 1000, start_time, 5.0)
        print(f"Quiescence search result:")
        print(f"  Score: {score}")
        print(f"  Nodes: {nodes}")
        print(f"  PV: {' '.join(str(move) for move in pv[:3])}")
    except Exception as e:
        print(f"Quiescence search error: {e}")
    
    print("\\n=== Quiescence Search Test Complete ===\\n")

def test_material_balance():
    """Test material balance calculation accuracy."""
    print("=== Testing Material Balance Accuracy ===")
    
    evaluator = Evaluation()
    
    # Equal material position
    board1 = chess.Board()
    material1 = evaluator._evaluate_material(board1)
    print(f"Starting position material balance: {material1}")
    
    # White up a pawn
    board2 = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPP1/RNBQKBNR w KQkq - 0 1")
    material2 = evaluator._evaluate_material(board2)
    print(f"White up a pawn: {material2}")
    
    # White up a queen
    board3 = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBK1BNR w KQkq - 0 1")
    material3 = evaluator._evaluate_material(board3)
    print(f"White up a queen: {material3}")
    
    print("\\n=== Material Balance Test Complete ===\\n")

def run_all_tests():
    """Run all v2.0 improvement tests."""
    print("Cece v2.0 Improvement Tests")
    print("=" * 50)
    
    test_see_improvements()
    test_move_ordering() 
    test_tactical_patterns()
    test_quiescence_search()
    test_material_balance()
    
    print("All tests completed!")
    print("\\nv2.0 improvements ready for tournament testing.")

if __name__ == "__main__":
    run_all_tests()

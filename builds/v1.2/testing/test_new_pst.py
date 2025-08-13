#!/usr/bin/env python3
"""
Test the updated piece-square tables in the evaluation function.
"""

import sys
import os
sys.path.append("s:/Maker Stuff/Programming/Static Evaluation Chess Engine/static_evaluation_engine")

import chess
from evaluation import Evaluation

def test_evaluation_with_new_pst():
    """Test the evaluation with the new piece-square tables."""
    
    print("🧪 Testing Updated Piece-Square Tables")
    print("=" * 50)
    
    eval_engine = Evaluation()
    
    # Test starting position
    board = chess.Board()
    detailed_eval = eval_engine.evaluate_detailed(board)
    
    print("📋 Starting Position Evaluation:")
    print(f"Total Score: {detailed_eval['total_score']}")
    print(f"Material: {detailed_eval['material']}")
    print(f"Positional: {detailed_eval['positional']}")
    print(f"Tactical: {detailed_eval['tactical']}")
    print(f"King Safety: {detailed_eval['king_safety']}")
    print(f"Piece Activity: {detailed_eval['piece_activity']}")
    print()
    
    # Test a middle game position
    print("📋 Middle Game Position:")
    # Sicilian Dragon position
    board.set_fen("rnbqkb1r/pp2pppp/3p1n2/8/3PP3/2N2N2/PPP2PPP/R1BQKB1R b KQkq - 0 4")
    detailed_eval = eval_engine.evaluate_detailed(board)
    
    print(f"FEN: {board.fen()}")
    print(f"Total Score: {detailed_eval['total_score']}")
    print(f"Material: {detailed_eval['material']}")
    print(f"Positional: {detailed_eval['positional']}")
    print(f"Tactical: {detailed_eval['tactical']}")
    print(f"King Safety: {detailed_eval['king_safety']}")
    print(f"Piece Activity: {detailed_eval['piece_activity']}")
    print()
    
    # Test a puzzle position
    print("📋 Tactical Puzzle Position:")
    # Use one of the puzzle positions from our tests
    board.set_fen("4rk2/p1q5/1p3Q1b/8/1p5N/2P1p3/P3P3/2K5 b - - 0 43")
    detailed_eval = eval_engine.evaluate_detailed(board)
    
    print(f"FEN: {board.fen()}")
    print(f"Total Score: {detailed_eval['total_score']}")
    print(f"Material: {detailed_eval['material']}")
    print(f"Positional: {detailed_eval['positional']}")
    print(f"Tactical: {detailed_eval['tactical']}")
    print(f"King Safety: {detailed_eval['king_safety']}")
    print(f"Piece Activity: {detailed_eval['piece_activity']}")
    print()
    
    # Test individual piece placement
    print("📋 Individual Piece Square Table Tests:")
    
    # Test knight in center vs corner
    board = chess.Board("8/8/8/3N4/8/8/8/8 w - - 0 1")  # Knight on d5 (center)
    center_score = eval_engine.evaluate_positional(board)
    
    board = chess.Board("N7/8/8/8/8/8/8/8 w - - 0 1")  # Knight on a8 (corner)
    corner_score = eval_engine.evaluate_positional(board)
    
    print(f"Knight on d5 (center): +{eval_engine.knight_table[chess.D5]}")
    print(f"Knight on a8 (corner): +{eval_engine.knight_table[chess.A8]}")
    print(f"Center knight should be better: {center_score > corner_score} ✅" if center_score > corner_score else f"Center knight should be better: {center_score > corner_score} ❌")
    print()
    
    # Test bishop on long diagonal
    board = chess.Board("8/8/8/8/8/2B5/8/8 w - - 0 1")  # Bishop on c3
    diagonal_score = eval_engine.evaluate_positional(board)
    
    board = chess.Board("B7/8/8/8/8/8/8/8 w - - 0 1")  # Bishop on a8 (corner)
    corner_bishop_score = eval_engine.evaluate_positional(board)
    
    print(f"Bishop on c3 (good diagonal): +{eval_engine.bishop_table[chess.C3]}")
    print(f"Bishop on a8 (corner): +{eval_engine.bishop_table[chess.A8]}")
    print(f"Diagonal bishop should be better: {diagonal_score > corner_bishop_score} ✅" if diagonal_score > corner_bishop_score else f"Diagonal bishop should be better: {diagonal_score > corner_bishop_score} ❌")
    print()
    
    print("✅ Piece-square table update completed successfully!")

if __name__ == "__main__":
    test_evaluation_with_new_pst()

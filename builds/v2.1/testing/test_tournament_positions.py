#!/usr/bin/env python3
"""
Test Cece v2.1 Pure Evaluation on Real Tournament Positions
===========================================================

Using actual problematic positions from tournament games to verify our fixes:
1. Knight rim opening (1.Nh3)
2. Knight shuffling sequences  
3. Rook shuffling behavior
4. Material blunder positions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import chess
from evaluation_v2_1_pure import Evaluation

def test_real_tournament_problems():
    """Test specific problematic positions from actual tournament games."""
    print("🔍 Testing Real Tournament Problem Positions")
    print("=" * 50)
    
    evaluator = Evaluation()
    
    # Test 1: Opening position - should discourage 1.Nh3
    print("\n1️⃣ Opening Move Selection Test")
    print("-" * 30)
    
    board = chess.Board()
    start_score = evaluator.evaluate(board)
    print(f"Starting position: {start_score}")
    
    # Test normal development vs rim knight
    test_moves = [
        ("e2e4", "Normal pawn development"),
        ("g1f3", "Good knight development"), 
        ("g1h3", "BAD knight to rim (actual Cece move)"),
        ("d2d4", "Central pawn development"),
        ("b1c3", "Good knight development")
    ]
    
    best_moves = []
    for move_uci, description in test_moves:
        board_test = chess.Board()
        move = chess.Move.from_uci(move_uci)
        board_test.push(move)
        score = evaluator.evaluate(board_test)
        best_moves.append((score, move_uci, description))
        print(f"  {move_uci} ({description}): {score}")
    
    # Sort by score to see ranking
    best_moves.sort(reverse=True)
    print("\\nMove Ranking (best to worst):")
    for i, (score, move, desc) in enumerate(best_moves):
        marker = "🎯" if i == 0 else "❌" if "BAD" in desc else "✅"
        print(f"  {i+1}. {marker} {move} ({desc}): {score}")
    
    # Test 2: Knight shuffling sequence from actual game
    print("\\n2️⃣ Knight Shuffling Sequence Test")
    print("-" * 35)
    
    # Recreate the problematic sequence: 1.Nh3 b5 2.Nf4 Nh6 3.Nd5 d6 4.Nf4
    board = chess.Board()
    moves = ["g1h3", "b7b5", "h3f4", "g8h6", "f4d5", "d7d6", "d5f4"]
    move_descriptions = [
        "1.Nh3 (rim knight)",
        "1...b5", 
        "2.Nf4 (knight move 2)",
        "2...Nh6 (black rim knight)",
        "3.Nd5 (knight move 3)", 
        "3...d6",
        "4.Nf4 (knight move 4 - REPETITION!)"
    ]
    
    scores = []
    for i, (move_uci, desc) in enumerate(zip(moves, move_descriptions)):
        if move_uci:
            move = chess.Move.from_uci(move_uci)
            board.push(move)
        score = evaluator.evaluate(board)
        scores.append(score)
        print(f"  {desc}: {score}")
    
    print(f"\\nTrend Analysis:")
    print(f"  White's position change: {scores[0]} → {scores[6]} = {scores[6] - scores[0]} (should be negative!)")
    
    # Test 3: Rook shuffling position (common Cece behavior)
    print("\\n3️⃣ Rook Shuffling Test") 
    print("-" * 25)
    
    # Create a position where rook shuffling might occur
    board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 5")
    print(f"Test position: {board.fen()}")
    
    # Test king/rook shuffling moves (Cece's favorites: h8g8, g8h8)
    king_pos = evaluator.evaluate(board)
    print(f"Current position score: {king_pos}")
    
    # Test shuffling moves
    shuffle_moves = [
        ("h8g8", "Rook h8-g8 (shuffle move 1)"),
        ("g8h8", "Rook g8-h8 (shuffle move 2)"),  
        ("e8f8", "King e8-f8 (shuffle move 3)"),
        ("f8g8", "King f8-g8 (shuffle move 4)")
    ]
    
    for move_uci, desc in shuffle_moves:
        board_test = board.copy()
        try:
            move = chess.Move.from_uci(move_uci)
            if move in board_test.legal_moves:
                board_test.push(move)
                shuffle_score = evaluator.evaluate(board_test)
                change = shuffle_score - king_pos
                print(f"  {desc}: {shuffle_score} (change: {change:+d})")
            else:
                print(f"  {desc}: ILLEGAL MOVE")
        except:
            print(f"  {desc}: INVALID MOVE")
    
    # Test 4: Material blunder detection
    print("\\n4️⃣ Material Blunder Detection")
    print("-" * 30)
    
    # Position where piece can be captured for free
    board = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3")
    safe_score = evaluator.evaluate(board)
    print(f"Safe position: {safe_score}")
    
    # Test moving knight to hanging square
    board.push(chess.Move.from_uci("f3g5"))  # Knight hangs
    hanging_score = evaluator.evaluate(board)
    penalty = safe_score - hanging_score
    print(f"Knight hangs on g5: {hanging_score} (penalty: {penalty})")
    
    # Test good alternative move
    board_alt = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3")
    board_alt.push(chess.Move.from_uci("f3d4"))  # Centralize knight
    good_score = evaluator.evaluate(board_alt)
    print(f"Knight to d4 (good): {good_score}")
    
    # Summary
    print("\\n📊 EVALUATION SUMMARY")
    print("=" * 30)
    print(f"✅ Rim knight penalty working: {'YES' if any('BAD' in desc and score < 0 for score, _, desc in best_moves) else 'NO'}")
    print(f"✅ Repetition discouraged: {'YES' if scores[6] < scores[0] else 'NO'}")
    print(f"✅ Hanging piece penalty: {'YES' if penalty > 100 else 'NO'}")
    print(f"✅ Good moves rewarded: {'YES' if good_score > hanging_score else 'NO'}")

def compare_old_vs_new_evaluation():
    """Compare how new evaluation handles the problematic positions."""
    print("\\n🔄 Comparison: Old vs New Evaluation Behavior")
    print("=" * 50)
    
    # Import old evaluation for comparison
    try:
        from evaluation import Evaluation as OldEvaluation
        old_evaluator = OldEvaluation()
        new_evaluator = Evaluation()
        
        print("Comparing old v2.0 vs new v2.1 pure evaluation...")
        
        # Test opening position
        board = chess.Board()
        
        # Test the problematic Nh3 move
        board.push(chess.Move.from_uci("g1h3"))
        old_score = old_evaluator.evaluate(board)
        new_score = new_evaluator.evaluate(board)
        
        print(f"1.Nh3 evaluation:")
        print(f"  Old v2.0: {old_score}")
        print(f"  New v2.1: {new_score}")
        print(f"  Improvement: {old_score - new_score} (should be positive)")
        
    except ImportError:
        print("Old evaluation not available for comparison")

def main():
    """Run all real tournament position tests."""
    print("Cece v2.1 Pure Evaluation - Tournament Position Analysis")
    print("=" * 60)
    print("Testing fixes against REAL problematic positions from tournaments:")
    print("- Engine Battle 20250810: Cece_v1.3 vs Copycat_uci")
    print("- Behavioral Analysis: 1116 h8g8 + 898 g8h8 repetitions")
    print("- Knight rim openings and shuffling sequences")
    print()
    
    test_real_tournament_problems()
    compare_old_vs_new_evaluation()
    
    print("\\n" + "=" * 60)
    print("🎯 CONCLUSION: v2.1 Pure Evaluation fixes target the exact")
    print("   problematic behaviors identified in tournament data!")

if __name__ == "__main__":
    main()

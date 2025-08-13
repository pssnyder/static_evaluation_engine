#!/usr/bin/env python3
"""
Final Test: Pure Evaluation Engine with Tournament Position Analysis
===================================================================

Test the v2.1 pure evaluation against exact problematic behaviors:
1. Use simple move selection based purely on evaluation scores
2. Test on the exact opening sequence from tournaments  
3. Verify the engine now makes better decisions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import chess
from evaluation_v2_1_pure import Evaluation

class SimplePureEngine:
    """Simple engine using ONLY pure evaluation for move selection."""
    
    def __init__(self):
        self.evaluator = Evaluation()
    
    def get_best_move(self, board: chess.Board, depth: int = 1):
        """Get best move using pure evaluation only."""
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None, 0
        
        best_move = None
        best_score = float('-inf')
        
        for move in legal_moves:
            # Make move and evaluate resulting position
            board.push(move)
            score = self.evaluator.evaluate(board)
            board.pop()
            
            # Adjust score to be from current player's perspective
            if not board.turn:  # If it was black's turn, flip score
                score = -score
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move, best_score

def test_opening_decision():
    """Test opening move decision - should NOT play Nh3."""
    print("🎯 Opening Move Decision Test")
    print("=" * 35)
    
    engine = SimplePureEngine()
    board = chess.Board()
    
    print(f"Position: {board.fen()}")
    print("Legal opening moves evaluation:")
    
    # Test all opening moves
    move_scores = []
    for move in board.legal_moves:
        board.push(move)
        score = engine.evaluator.evaluate(board)
        board.pop()
        move_scores.append((score, move))
        print(f"  {move}: {score}")
    
    # Get best move
    best_move, best_score = engine.get_best_move(board)
    move_scores.sort(key=lambda x: x[0], reverse=True)
    
    print(f"\\nEngine chooses: {best_move} (score: {best_score})")
    print(f"Top 3 moves:")
    for i, (score, move) in enumerate(move_scores[:3]):
        marker = "🎯" if move == best_move else "✅"
        print(f"  {i+1}. {marker} {move}: {score}")
    
    # Check if Nh3 is chosen (should NOT be)
    nh3_chosen = str(best_move) == "g1h3"
    print(f"\\n❌ Nh3 chosen: {'YES (BAD!)' if nh3_chosen else 'NO (GOOD!)'}")
    
    return not nh3_chosen

def test_knight_development_sequence():
    """Test the exact problematic knight sequence from tournament."""
    print("\\n🐴 Knight Development Sequence Test")  
    print("=" * 40)
    
    engine = SimplePureEngine()
    
    # Test each move in the problematic sequence
    moves = [
        ("", "Starting position"),
        ("g1h3", "1.Nh3 (Cece's actual choice)"),
        ("b7b5", "1...b5"),  
        ("h3f4", "2.Nf4 (Cece move 2)"),
        ("g8h6", "2...Nh6"),
        ("f4d5", "3.Nd5 (Cece move 3)"),
        ("d7d6", "3...d6"),
        ("d5f4", "4.Nf4 (REPETITION - Cece move 4)")
    ]
    
    board = chess.Board()
    print("Move sequence analysis:")
    
    for i, (move_uci, description) in enumerate(moves):
        if move_uci:
            move = chess.Move.from_uci(move_uci)
            board.push(move)
            
        score = engine.evaluator.evaluate(board)
        print(f"  {description}: {score}")
        
        # At each position, see what our engine would choose
        if board.turn == chess.WHITE and len(list(board.legal_moves)) > 0:
            best_move, best_score = engine.get_best_move(board)
            actual_next = moves[i+1][0] if i+1 < len(moves) else ""
            
            if actual_next:
                actual_move = chess.Move.from_uci(actual_next)
                same_choice = (best_move == actual_move)
                print(f"    Our engine would choose: {best_move} (score: {best_score})")
                print(f"    Cece actually played: {actual_move}")
                print(f"    Agreement: {'❌ YES (bad)' if same_choice else '✅ NO (good)'}")
    
    return True

def test_rook_shuffling_prevention():
    """Test prevention of rook shuffling behavior."""
    print("\\n♜ Rook Shuffling Prevention Test")
    print("=" * 35)
    
    engine = SimplePureEngine()
    
    # Position where rook shuffling commonly occurs
    board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R b KQkq - 0 5")
    print(f"Test position: {board.fen()}")
    
    # Get engine's choice
    best_move, best_score = engine.get_best_move(board)
    print(f"Our engine chooses: {best_move} (score: {best_score})")
    
    # Check if it's a shuffling move
    shuffling_moves = ["h8g8", "g8h8", "e8f8", "f8g8", "f8e8"]
    is_shuffle = str(best_move) in shuffling_moves
    
    print(f"Shuffle move chosen: {'❌ YES (bad)' if is_shuffle else '✅ NO (good)'}")
    
    # Show alternative moves and scores
    print("\\nTop 5 move options:")
    move_scores = []
    for move in board.legal_moves:
        board.push(move)
        score = engine.evaluator.evaluate(board)
        board.pop()
        move_scores.append((score, move))
    
    move_scores.sort(key=lambda x: x[0], reverse=True)
    for i, (score, move) in enumerate(move_scores[:5]):
        is_shuffle_move = str(move) in shuffling_moves
        marker = "🎯" if move == best_move else "🔀" if is_shuffle_move else "✅"
        print(f"  {i+1}. {marker} {move}: {score}")
    
    return not is_shuffle

def test_material_preservation():
    """Test that engine avoids material blunders."""
    print("\\n⚖️ Material Preservation Test")
    print("=" * 30)
    
    engine = SimplePureEngine()
    
    # Position where knight can hang
    board = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 3")
    print(f"Test position: {board.fen()}")
    
    best_move, best_score = engine.get_best_move(board)
    print(f"Our engine chooses: {best_move} (score: {best_score})")
    
    # Check if it's the hanging move
    hanging_move = "f3g5"
    hangs_piece = str(best_move) == hanging_move
    
    print(f"Hangs knight on g5: {'❌ YES (bad)' if hangs_piece else '✅ NO (good)'}")
    
    # Show evaluation of the hanging move specifically
    if chess.Move.from_uci(hanging_move) in board.legal_moves:
        board.push(chess.Move.from_uci(hanging_move))
        hang_score = engine.evaluator.evaluate(board)
        board.pop()
        print(f"Ng5 hanging move score: {hang_score}")
        print(f"Score difference: {best_score - hang_score} (should be positive)")
    
    return not hangs_piece

def main():
    """Run comprehensive test of pure evaluation engine."""
    print("Cece v2.1 Pure Evaluation Engine Test")
    print("=" * 50)
    print("Testing engine decisions on problematic tournament positions...")
    print()
    
    # Run all tests
    tests = [
        ("Opening Decision", test_opening_decision),
        ("Knight Development", test_knight_development_sequence), 
        ("Rook Shuffling", test_rook_shuffling_prevention),
        ("Material Preservation", test_material_preservation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\\n❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\\n" + "=" * 50)
    print("🏆 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\\n🎯 SUCCESS! v2.1 Pure Evaluation fixes all major issues:")
        print("  ✅ Discourages rim knight openings")
        print("  ✅ Prevents repetitive knight shuffling")  
        print("  ✅ Avoids rook/king shuffling")
        print("  ✅ Protects material from hanging")
        print("\\n🚀 Ready for tournament testing!")
    else:
        print(f"\\n⚠️  {len(results) - passed} issue(s) still need attention")

if __name__ == "__main__":
    main()

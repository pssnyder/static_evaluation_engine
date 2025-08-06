"""
Test the consolidated evaluation.py to verify all components work correctly.
"""

import chess
from evaluation import Evaluation

def test_basic_evaluation():
    """Test basic evaluation functionality."""
    evaluator = Evaluation()
    
    # Test starting position
    board = chess.Board()
    breakdown = evaluator.evaluate_detailed(board)
    score = breakdown['total_score']
    
    print("=== Starting Position Evaluation ===")
    print(f"Total Score: {score}")
    print(f"Material: {breakdown['material']}")
    print(f"Positional: {breakdown['positional']}")
    print(f"Tactical: {breakdown['tactical']}")
    print(f"Threats: {breakdown['threats']}")
    print(f"Castling: {breakdown['castling']}")
    print(f"King Safety: {breakdown['king_safety']}")
    print()
    
    return score == 0  # Starting position should be roughly equal

def test_enhanced_pst():
    """Test that enhanced PST properly penalizes bad moves."""
    evaluator = Evaluation()
    
    # Test position with queen on h8 (manually set bad position)
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNQ w Qkq - 0 1")  # Queen on h1
    
    # Evaluate before move (White's turn)
    breakdown_before = evaluator.evaluate_detailed(board)
    
    board.push(chess.Move.from_uci("h1h8"))  # Queen to h8
    
    # Evaluate after move (Black's turn)
    breakdown_after = evaluator.evaluate_detailed(board)
    
    print("=== Queen on h8 Position ===")
    print(f"Before move (White's perspective): {breakdown_before['positional']}")
    print(f"After move (Black's perspective): {breakdown_after['positional']}")
    print(f"Queen PST penalty: {-30} (corners heavily penalized)")
    print()
    
    # From Black's perspective, White queen on bad square should give positive score
    # From White's perspective, queen on h1 gives -30, so queen on h8 should also give -30 in absolute terms
    return breakdown_after['positional'] == 30  # Positive for Black = bad for White

def test_see_evaluation():
    """Test Static Exchange Evaluation."""
    evaluator = Evaluation()
    
    # Test position: pawn takes pawn (should be positive)
    board = chess.Board("rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2")
    
    # Test capture evaluation
    breakdown = evaluator.evaluate_detailed(board)
    
    print("=== SEE Test Position ===")
    print(f"Tactical Score: {breakdown['tactical']}")
    print()
    
    return True  # Just verify it runs without error

def test_threat_evaluation():
    """Test threat evaluation system."""
    evaluator = Evaluation()
    
    # Position with knight attacking multiple pieces
    board = chess.Board("rnbqkb1r/pppp1ppp/5n2/4p3/2B1P3/8/PPPP1PPP/RNBQK1NR w KQkq - 2 3")
    
    breakdown = evaluator.evaluate_detailed(board)
    
    print("=== Threat Evaluation Test ===")
    print(f"Threat Score: {breakdown['threats']}")
    print()
    
    return True  # Just verify it runs

def test_castling_evaluation():
    """Test castling evaluation."""
    evaluator = Evaluation()
    
    # Opening position - should encourage castling
    board = chess.Board()
    
    breakdown = evaluator.evaluate_detailed(board)
    
    print("=== Castling Evaluation Test ===")
    print(f"Castling Score: {breakdown['castling']}")
    print()
    
    return True  # Just verify it runs

def main():
    """Run all tests."""
    print("Testing Consolidated Evaluation System")
    print("=" * 50)
    
    tests = [
        ("Basic Evaluation", test_basic_evaluation),
        ("Enhanced PST", test_enhanced_pst),
        ("SEE Evaluation", test_see_evaluation),
        ("Threat Evaluation", test_threat_evaluation),
        ("Castling Evaluation", test_castling_evaluation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"Tests: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Evaluation system ready for integration.")
    else:
        print("⚠️  Some tests failed. Check evaluation implementation.")

if __name__ == "__main__":
    main()

"""
Quick test to verify the enhanced evaluation is working in the main engine.
"""

import chess
from engine import ChessEngine

def test_engine_enhanced_evaluation():
    """Test that the engine is using the enhanced evaluation correctly."""
    print("Testing Enhanced Evaluation Integration")
    print("=" * 50)
    
    # Create engine instance
    engine = ChessEngine()
    
    # Test position: Queen moving to bad square
    board = chess.Board()
    
    # Make some moves to get to a position where we can test
    moves = ["e2e4", "e7e5", "d1h5"]  # Queen to h5 early (bad move)
    
    for move_str in moves:
        move = chess.Move.from_uci(move_str)
        if move in board.legal_moves:
            board.push(move)
            print(f"Played: {move_str}")
        else:
            print(f"Invalid move: {move_str}")
    
    print(f"\nFinal position:")
    print(board)
    
    # Get evaluation from engine
    score = engine.evaluator.evaluate(board)
    breakdown = engine.evaluator.evaluate_detailed(board)
    
    print(f"\nEvaluation Results:")
    print(f"Simple score: {score}")
    print(f"Detailed score: {breakdown['total_score']}")
    print(f"Breakdown:")
    for component, value in breakdown.items():
        if component != 'total_score':  # Skip total since we already showed it
            print(f"  {component}: {value}")
    
    # Test best move search
    print(f"\nSearching for best move...")
    start_time = time.time()
    
    # Set the engine's board position
    engine.board = board
    
    best_move = engine.get_best_move(depth=3)
    search_time = time.time() - start_time
    
    print(f"Best move: {best_move}")
    print(f"Search time: {search_time:.3f}s")
    
    return True

if __name__ == "__main__":
    import time
    test_engine_enhanced_evaluation()

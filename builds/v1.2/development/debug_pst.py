"""
Debug the PST evaluation for the queen on h8 position.
"""

import chess
from evaluation import Evaluation

def debug_queen_position():
    """Debug the queen on h8 position evaluation."""
    evaluator = Evaluation()
    
    # Create position with queen on h8
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNQ w Qkq - 0 1")  # Queen on h1
    print("Initial position:")
    print(board)
    print(f"Turn: {'White' if board.turn else 'Black'}")
    
    # Evaluate before move
    score_before, breakdown_before = evaluator.evaluate_detailed(board)
    print(f"\nBefore queen move - Positional: {breakdown_before['positional']}")
    
    # Move queen to h8
    board.push(chess.Move.from_uci("h1h8"))
    print(f"\nAfter queen to h8:")
    print(board)
    print(f"Turn: {'White' if board.turn else 'Black'}")
    
    # Evaluate after move
    score_after, breakdown_after = evaluator.evaluate_detailed(board)
    print(f"After queen move - Positional: {breakdown_after['positional']}")
    
    # Check PST value directly
    queen_square = chess.H8
    table_index = evaluator._square_to_table_index(queen_square, chess.WHITE)
    pst_value = evaluator.queen_table[table_index]
    print(f"\nDirect PST lookup:")
    print(f"Queen on h8 table index: {table_index}")
    print(f"PST value: {pst_value}")
    
    # Check if there are any other pieces affecting the score
    print(f"\nFull breakdown after move:")
    for key, value in breakdown_after.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    debug_queen_position()

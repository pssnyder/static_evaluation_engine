#!/usr/bin/env python3
"""
Deep dive analysis of evaluation problems in the Cece v1.2 vs v1.0 game.
Focus on why PST penalties aren't working effectively.
"""

import chess
import chess.pgn
from io import StringIO
from evaluation import Evaluation

def detailed_evaluation_analysis():
    """Analyze why the evaluation isn't preventing poor moves."""
    
    print("🔍 DEEP EVALUATION ANALYSIS")
    print("=" * 50)
    
    evaluator = Evaluation()
    
    # Test the actual PST values being used
    print("📊 PST VALUES ANALYSIS")
    print("-" * 30)
    
    print("Knight PST values (White perspective):")
    knight_table = evaluator.knight_table
    
    # Show key squares
    key_squares = {
        'a1': chess.A1, 'b1': chess.B1, 'c1': chess.C1, 'd1': chess.D1,
        'e1': chess.E1, 'f1': chess.F1, 'g1': chess.G1, 'h1': chess.H1,
        'a3': chess.A3, 'b3': chess.B3, 'c3': chess.C3, 'd3': chess.D3,
        'e3': chess.E3, 'f3': chess.F3, 'g3': chess.G3, 'h3': chess.H3,
        'd4': chess.D4, 'e4': chess.E4, 'd5': chess.D5, 'e5': chess.E5
    }
    
    for name, square in key_squares.items():
        index = evaluator._square_to_table_index(square, chess.WHITE)
        value = knight_table[index]
        print(f"  {name}: {value:3d}")
    
    print("\n🎯 SPECIFIC MOVE ANALYSIS")
    print("-" * 30)
    
    # Analyze the actual positions from the game
    test_positions = [
        ("Starting position", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("After 1. Nc3", "rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR b KQkq - 1 1"),
        ("After 1... c6 2. Nh3", "rnbqkbnr/pp1ppppp/2p5/8/8/2N4N/PPPPPPPP/R1BQKB1R b KQkq - 1 2"),
        ("After 2... h6 3. Ng1", "rnbqkbnr/pp1pppp1/2p4p/8/8/2N5/PPPPPPPP/R1BQKBNR b KQkq - 1 3")
    ]
    
    for desc, fen in test_positions:
        print(f"\n{desc}:")
        board = chess.Board(fen)
        breakdown = evaluator.evaluate_detailed(board)
        
        print(f"  FEN: {fen}")
        print(f"  Total: {breakdown['total_score']}")
        print(f"  Positional: {breakdown['positional']}")
        
        # Show white knight positions and values
        white_knights = board.pieces(chess.KNIGHT, chess.WHITE)
        print(f"  White knights:")
        for knight_sq in white_knights:
            sq_name = chess.square_name(knight_sq)
            index = evaluator._square_to_table_index(knight_sq, chess.WHITE)
            value = knight_table[index]
            print(f"    {sq_name}: {value}")
    
    print("\n⚖️ EVALUATION WEIGHTS ANALYSIS")
    print("-" * 30)
    
    print("Evaluation system structure:")
    print(f"  PST evaluation is integrated into positional score")
    print(f"  Knight h3 penalty: -30")
    print(f"  This penalty should make h3 moves less attractive")
    
    print("\n🚨 PROBLEM IDENTIFICATION")
    print("-" * 30)
    
    # Test what the engine sees for alternative moves
    board = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    
    print("Starting position - comparing first moves:")
    legal_moves = list(board.legal_moves)
    move_evaluations = []
    
    for move in legal_moves[:10]:  # Test first 10 moves
        board_copy = board.copy()
        board_copy.push(move)
        breakdown = evaluator.evaluate_detailed(board_copy)
        # Convert to White's perspective (evaluation is from current player's view)
        score = -breakdown['total_score'] if board_copy.turn == chess.BLACK else breakdown['total_score']
        move_evaluations.append((move, score, breakdown))
    
    # Sort by score (best first for White)
    move_evaluations.sort(key=lambda x: x[1], reverse=True)
    
    print("Top 10 moves by evaluation:")
    for i, (move, score, breakdown) in enumerate(move_evaluations[:10]):
        print(f"  {i+1:2d}. {move}: {score:4d} (pos: {breakdown['positional']:3d})")
    
    print("\n🔧 SEARCH DEPTH IMPACT")
    print("-" * 30)
    
    # Test what happens at different depths
    print("This analysis suggests several issues:")
    print("1. PST penalties may be too weak relative to other factors")
    print("2. Search depth might be too shallow to see long-term positional consequences")
    print("3. Other evaluation components might be overwhelming positional scores")
    print("4. The evaluation may not be properly considering move sequences")

def test_pst_effectiveness():
    """Test if PST values are strong enough to influence move selection."""
    
    print("\n🧪 PST EFFECTIVENESS TEST")
    print("=" * 30)
    
    evaluator = Evaluation()
    
    # Create a test position where PST should heavily influence the choice
    board = chess.Board("rnbqkb1r/pppppppp/5n2/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 1 2")
    
    print("Test position: Knight can go to various squares")
    print(f"FEN: {board.fen()}")
    
    # Test knight moves from g1
    knight_moves = [
        chess.Move.from_uci("g1f3"),  # Good central square
        chess.Move.from_uci("g1h3"),  # Rim square (bad)
        chess.Move.from_uci("g1e2"),  # Passive but not terrible
    ]
    
    print("\nKnight move comparison:")
    for move in knight_moves:
        if move in board.legal_moves:
            board_copy = board.copy()
            board_copy.push(move)
            breakdown = evaluator.evaluate_detailed(board_copy)
            
            # Get knight position after move
            knight_square = move.to_square
            sq_name = chess.square_name(knight_square)
            index = evaluator._square_to_table_index(knight_square, chess.WHITE)
            pst_value = evaluator.knight_table[index]
            
            print(f"  {move} ({sq_name}): Total = {breakdown['total_score']}, PST = {pst_value}")

if __name__ == "__main__":
    detailed_evaluation_analysis()
    test_pst_effectiveness()

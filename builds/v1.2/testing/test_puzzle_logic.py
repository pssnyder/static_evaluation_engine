#!/usr/bin/env python3
"""
Test the corrected puzzle sequence logic with a known example.
"""

import chess
from enhanced_puzzle_tester import Puzzle

def test_puzzle_logic():
    """Test puzzle sequence interpretation with a known example."""
    
    # Using the first puzzle from the CSV as an example
    # PuzzleId: 00008
    # FEN: r6k/pp2r2p/4Rp1Q/3p4/8/1N1P2R1/PqP2bPP/7K b - - 0 24
    # Moves: f2g3 e6e7 b2b1 b3c1 b1c1 h6c1
    
    puzzle = Puzzle(
        puzzle_id="00008",
        fen="r6k/pp2r2p/4Rp1Q/3p4/8/1N1P2R1/PqP2bPP/7K b - - 0 24",
        moves=["f2g3", "e6e7", "b2b1", "b3c1", "b1c1", "h6c1"],
        rating=1928,
        themes=["crushing", "hangingPiece", "long", "middlegame"],
        opening_tags=""
    )
    
    print("🧩 Testing Puzzle Sequence Logic")
    print("=" * 50)
    print(f"Puzzle ID: {puzzle.puzzle_id}")
    print(f"Rating: {puzzle.rating}")
    print(f"Themes: {' '.join(puzzle.themes)}")
    print(f"Solution: {' '.join(puzzle.moves)}")
    print()
    
    # Set up the board
    board = chess.Board(puzzle.fen)
    print(f"Initial position: {'White' if board.turn else 'Black'} to move")
    print(f"FEN: {puzzle.fen}")
    print()
    
    # Analyze the sequence
    engine_moves = []
    opponent_moves = []
    
    for move_num, move in enumerate(puzzle.moves, 1):
        is_engine_move = (move_num % 2 == 1)  # Odd moves are engine moves
        
        if is_engine_move:
            engine_moves.append((move_num, move, board.fen()))
            print(f"Engine Move {(move_num + 1) // 2}: {move}")
            print(f"  Position: {board.fen()}")
            print(f"  Side to move: {'White' if board.turn else 'Black'}")
        else:
            opponent_moves.append((move_num, move, board.fen()))
            print(f"Opponent Move {move_num // 2}: {move}")
            print(f"  Position: {board.fen()}")
            print(f"  Side to move: {'White' if board.turn else 'Black'}")
        
        # Apply the move
        try:
            chess_move = chess.Move.from_uci(move)
            board.push(chess_move)
            print(f"  After {move}: {board.fen()}")
        except:
            print(f"  ❌ Invalid move: {move}")
            break
        print()
    
    print("📊 Summary:")
    print(f"Total moves in sequence: {len(puzzle.moves)}")
    print(f"Engine moves to test: {len(engine_moves)}")
    print(f"Opponent responses: {len(opponent_moves)}")
    print()
    
    print("🎯 Engine moves to test:")
    for i, (move_num, move, fen) in enumerate(engine_moves, 1):
        print(f"  Test {i}: {move} (from position {fen[:20]}...)")
    
    print()
    print("🤖 Opponent responses:")
    for i, (move_num, move, fen) in enumerate(opponent_moves, 1):
        print(f"  Response {i}: {move} (from position {fen[:20]}...)")

if __name__ == "__main__":
    test_puzzle_logic()

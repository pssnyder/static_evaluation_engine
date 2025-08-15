#!/usr/bin/env python3
"""
Debug Rook Preservation Function
"""

import chess
import sys
import os

# Add the parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation import Evaluation

def debug_rook_preservation():
    """Debug the rook preservation function"""
    print("DEBUGGING ROOK PRESERVATION")
    print("="*50)
    
    evaluator = Evaluation()
    
    # Test 1: Starting position (should be 0)
    board = chess.Board()
    print(f"Starting position: {board.fen()}")
    print(f"White has kingside castling: {board.has_kingside_castling_rights(chess.WHITE)}")
    print(f"White has queenside castling: {board.has_queenside_castling_rights(chess.WHITE)}")
    
    rook_score = evaluator._evaluate_rook_preservation(board)
    print(f"Rook preservation score: {rook_score}")
    print()
    
    # Test 2: After developing pieces but keeping king on e1
    moves = ["e2e4", "e7e5", "f1c4", "f8c5", "g1f3", "g8f6"]
    for move_str in moves:
        board.push(chess.Move.from_uci(move_str))
    
    print(f"After development: {board.fen()}")
    print(f"White king on e1: {board.king(chess.WHITE) == chess.E1}")
    print(f"White has kingside castling: {board.has_kingside_castling_rights(chess.WHITE)}")
    print(f"White has queenside castling: {board.has_queenside_castling_rights(chess.WHITE)}")
    
    rook_score = evaluator._evaluate_rook_preservation(board)
    print(f"Rook preservation score: {rook_score}")
    print()
    
    # Test 3: Move the h1 rook while king still on e1 (should be big penalty)
    board.push(chess.Move.from_uci("h1g1"))  # Move rook
    
    print(f"After Rg1: {board.fen()}")
    print(f"White king on e1: {board.king(chess.WHITE) == chess.E1}")
    print(f"White has kingside castling: {board.has_kingside_castling_rights(chess.WHITE)}")
    print(f"White has queenside castling: {board.has_queenside_castling_rights(chess.WHITE)}")
    
    rook_score = evaluator._evaluate_rook_preservation(board)
    print(f"Rook preservation score: {rook_score}")
    print(f"Expected: -200 penalty for moving kingside rook while king on e1")

if __name__ == "__main__":
    debug_rook_preservation()

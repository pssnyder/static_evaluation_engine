"""
Quick debug test for UCI issue in Cece v2.1
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'v2.1'))

from engine import ChessEngine
import chess

def debug_search():
    """Debug the search to see why PV is empty."""
    
    engine = ChessEngine()
    engine.set_position()  # Start position
    
    print("Board:", engine.board.fen())
    print("Legal moves:", [str(m) for m in engine.board.legal_moves])
    
    # Test the search directly
    print("\n=== Testing search_position ===")
    search_result = engine.search_position(3, 5.0)
    
    print(f"Search result:")
    print(f"  Depth: {search_result.depth}")
    print(f"  Nodes: {search_result.nodes}")
    print(f"  Score: {search_result.score}")
    print(f"  PV length: {len(search_result.pv)}")
    print(f"  PV: {search_result.pv}")
    print(f"  Time: {search_result.time_ms}")
    print(f"  NPS: {search_result.nps}")
    
    # Test get_best_move
    print("\n=== Testing get_best_move ===")
    best_move = engine.get_best_move(3, 5.0)
    print(f"Best move: {best_move}")
    print(f"Best move type: {type(best_move)}")
    
    if best_move:
        print(f"Best move UCI: {best_move.uci()}")
    
    return best_move

if __name__ == "__main__":
    debug_search()

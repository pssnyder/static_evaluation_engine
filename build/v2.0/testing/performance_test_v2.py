#!/usr/bin/env python3
"""
Performance test for Cece v2.0 to ensure improvements don't hurt speed.
"""

import chess
import time
from engine import ChessEngine

def performance_test():
    """Test engine performance on various positions."""
    print("Cece v2.0 Performance Test")
    print("=" * 40)
    
    engine = ChessEngine()
    
    # Test positions of varying complexity
    test_positions = [
        ("Starting position", chess.STARTING_FEN),
        ("Middlegame", "r1bqkb1r/pppp1ppp/2n2n2/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"),
        ("Tactical position", "r2qk2r/ppp2ppp/2n1bn2/2bpp3/2B1P3/3P1N2/PPP1NPPP/R1BQK2R w KQkq - 0 8"),
        ("Endgame", "8/8/3k4/8/3K4/8/8/R7 w - - 0 1")
    ]
    
    total_time = 0
    total_nodes = 0
    
    for name, fen in test_positions:
        print(f"\\nTesting: {name}")
        engine.set_position(fen)
        
        start_time = time.time()
        search_result = engine.search_position(depth=4, time_limit=3.0)
        elapsed = time.time() - start_time
        
        total_time += elapsed
        total_nodes += search_result.nodes
        
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Nodes: {search_result.nodes:,}")
        print(f"  NPS: {search_result.nps:,}")
        print(f"  Score: {search_result.score}")
        
        if search_result.pv:
            pv_str = ' '.join(str(move) for move in search_result.pv[:3])
            print(f"  Best line: {pv_str}")
    
    print(f"\\nOverall Performance:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Total nodes: {total_nodes:,}")
    if total_time > 0:
        print(f"  Average NPS: {total_nodes/total_time:,.0f}")
    
    print(f"\\nPerformance Assessment:")
    avg_nps = total_nodes/total_time if total_time > 0 else 0
    if avg_nps > 50000:
        print("✅ Excellent performance (>50k NPS)")
    elif avg_nps > 20000:
        print("✅ Good performance (>20k NPS)")
    elif avg_nps > 10000:
        print("⚠️  Acceptable performance (>10k NPS)")
    else:
        print("❌ Performance needs optimization (<10k NPS)")

if __name__ == "__main__":
    performance_test()

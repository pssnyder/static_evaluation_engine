"""
Debug the illegal move from the v1.1 game
"""

import chess
import chess.pgn
from io import StringIO

# The PGN from the problematic game
pgn_text = """
[Event "Engine Battle 20250803"]
[Site "MAIN-DESKTOP"]
[Date "2025.08.03"]
[Round "1"]
[White "Cece_v1.1"]
[Black "Cece_v1.1"]
[Result "0-1"]

1. Nh3 f6 2. Ng5 g6 3. Nxh7 Nh6 4. Nxf8 Rh7 5. Nxh7 c6 6. f4 e6 7. a3 d6 8.
g3 Qe7 9. Nxf6+ Kd8 10. Ne4 Bd7 11. Rg1 Qf8 12. Nf2 Qh8 13. Rg2 Qg8 14. Rg1
Qh7 15. Rg2 Qg8 16. Nc3 Qe8 17. Nd5 Qh8
"""

def debug_illegal_move():
    """Debug the illegal move issue."""
    
    print("🔍 Debugging illegal move from v1.1 game")
    print("=" * 50)
    
    # Parse the game
    pgn = StringIO(pgn_text)
    game = chess.pgn.read_game(pgn)
    
    if not game:
        print("❌ Could not parse PGN")
        return
    
    # Replay the game
    board = game.board()
    
    print("Starting position:")
    print(board)
    print()
    
    move_count = 0
    for move in game.mainline_moves():
        move_count += 1
        
        print(f"Move {move_count}: {move}")
        print(f"Legal moves: {len(list(board.legal_moves))}")
        
        # Check if move is legal
        if move not in board.legal_moves:
            print(f"❌ ILLEGAL MOVE DETECTED: {move}")
            print(f"Position: {board.fen()}")
            print("Legal moves:")
            for legal_move in board.legal_moves:
                print(f"  {legal_move}")
            break
        
        board.push(move)
        
        # Show position after critical moves
        if move_count in [16, 17]:
            print(f"Position after move {move_count}:")
            print(board)
            print(f"FEN: {board.fen()}")
            print()
    
    print("\\nDebug complete")

if __name__ == "__main__":
    debug_illegal_move()

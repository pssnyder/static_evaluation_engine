#!/usr/bin/env python3
"""
Analyze White's play in Cece v1.2 vs Cece v1.0 game.
Step through key positions and show evaluation breakdowns.
"""

import chess
import chess.pgn
from io import StringIO
from evaluation import Evaluation

def analyze_white_play():
    """Analyze White's key evaluation decisions in the sample game."""
    
    # The game PGN
    pgn_text = """
[Event "Computer chess game"]
[Site "MAIN-DESKTOP"]
[Date "2025.08.06"]
[Round "?"]
[White "Cece_v1.2"]
[Black "Cece_v1.0"]
[Result "1-0"]
[BlackElo "100"]
[ECO "A00"]
[Opening "Dunst (Sleipner-Heinrichsen-Van Geet) Opening"]
[Time "09:20:20"]
[WhiteElo "2000"]
[TimeControl "120+1"]
[Termination "normal"]
[PlyCount "59"]
[WhiteType "program"]
[BlackType "program"]

1. Nc3 c6 2. Nh3 h6 3. Ng1 f6 4. Nh3 g6 5. Ng1 Qb6 6. Ne4 Rh7 7. Nxf6+ exf6
8. Nh3 Qxf2+ 9. Nxf2 Ba3 10. bxa3 Re7 11. e4 Kf7 12. Be2 Kf8 13. O-O Ke8
14. Bg4 Rxe4 15. Nxe4 Kf8 16. Be2 Ke8 17. Bc4 Kf8 18. Re1 Ke8 19. d3 Kf8
20. Bxg8 Ke7 21. Nxf6+ Kd6 22. Ne8+ Kc5 23. Be3+ Kb5 24. Nc7+ Ka4 25. Bxh6
Ka5 26. Bd2+ Kb6 27. Nxa8+ Kc5 28. Bf7 Kd6 29. Qg4 c5 30. Qxg6# 1-0
"""
    
    print("🔍 ANALYZING WHITE'S PLAY - Cece v1.2 vs Cece v1.0")
    print("=" * 60)
    
    # Parse the game
    pgn = StringIO(pgn_text)
    game = chess.pgn.read_game(pgn)
    if not game:
        print("❌ Could not parse PGN")
        return
    
    evaluator = Evaluation()
    board = game.board()
    
    # Key positions to analyze in detail
    key_moves = [
        (1, "1. Nc3", "Opening choice - unconventional development"),
        (2, "2. Nh3", "Knight to rim - questionable"),
        (3, "3. Ng1", "Knight retreat - strange pattern"),
        (4, "4. Nh3", "Repeat knight maneuver"),
        (5, "5. Ng1", "Another retreat"),
        (6, "6. Ne4", "Finally centralizing"),
        (10, "10. bxa3", "Pawn structure damage"),
        (11, "11. e4", "Central pawn advance"),
        (14, "14. Bg4", "Bishop development"),
        (20, "20. Bxg8", "Piece trade"),
        (21, "21. Nxf6+", "Check and attack"),
        (29, "29. Qg4", "Queen activation"),
        (30, "30. Qxg6#", "Checkmate")
    ]
    
    move_count = 0
    for move in game.mainline_moves():
        move_count += 1
        board.push(move)
        
        # Check if this is a key move to analyze
        for key_move_num, key_move_desc, key_move_comment in key_moves:
            if move_count == key_move_num:
                analyze_position(evaluator, board, move_count, key_move_desc, key_move_comment, move)
                break
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY OF WHITE'S EVALUATION PATTERNS")
    print("=" * 60)
    
    # Analyze opening pattern
    print("\n🎯 Opening Analysis:")
    print("White's first 5 moves show a problematic pattern:")
    print("1. Nc3 - PST penalty for knight on rim")
    print("2. Nh3 - Much worse PST penalty (knights hate rim)")
    print("3. Ng1 - No improvement, back to starting square")
    print("4. Nh3 - Repeating bad placement")
    print("5. Ng1 - Still not learning from PST penalties")
    print("\n💡 This suggests PST penalties aren't strong enough")
    print("   or search depth too shallow to see consequences.")

def analyze_position(evaluator, board, move_num, move_desc, comment, last_move):
    """Analyze a specific position in detail."""
    
    print(f"\n{'='*40}")
    print(f"Move {move_num}: {move_desc}")
    print(f"Comment: {comment}")
    print(f"{'='*40}")
    
    # Get full evaluation breakdown
    breakdown = evaluator.evaluate_detailed(board)
    
    print(f"Position: {board.fen()}")
    print(f"Side to move: {'White' if board.turn else 'Black'}")
    print(f"Last move: {last_move}")
    
    print(f"\n📊 Evaluation Breakdown:")
    print(f"Total Score: {breakdown['total_score']}")
    print(f"Material: {breakdown['material']}")
    print(f"Positional: {breakdown['positional']}")
    print(f"Tactical: {breakdown['tactical']}")
    print(f"Threats: {breakdown['threats']}")
    print(f"Castling: {breakdown['castling']}")
    print(f"King Safety: {breakdown['king_safety']}")
    
    # Analyze specific pieces if relevant to the move
    if move_num <= 6:  # Opening knight moves
        analyze_knight_placement(evaluator, board, move_num)
    elif move_num == 11:  # e4 advance
        analyze_pawn_structure(evaluator, board)
    elif move_num >= 20:  # Endgame tactics
        analyze_tactical_elements(evaluator, board)

def analyze_knight_placement(evaluator, board, move_num):
    """Analyze knight placement and PST impact."""
    print(f"\n🐴 Knight Analysis (Move {move_num}):")
    
    for color in [chess.WHITE, chess.BLACK]:
        color_name = "White" if color == chess.WHITE else "Black"
        knights = board.pieces(chess.KNIGHT, color)
        
        print(f"{color_name} knights:")
        for knight_square in knights:
            square_name = chess.square_name(knight_square)
            table_index = evaluator._square_to_table_index(knight_square, color)
            pst_value = evaluator.knight_table[table_index]
            print(f"  {square_name}: PST value = {pst_value}")
            
            # Special analysis for rim knights
            file = chess.square_file(knight_square)
            rank = chess.square_rank(knight_square)
            if file == 0 or file == 7 or rank == 0 or rank == 7:
                print(f"    ⚠️ Knight on rim! Heavy PST penalty.")

def analyze_pawn_structure(evaluator, board):
    """Analyze pawn structure after e4."""
    print(f"\n♟️ Pawn Structure Analysis:")
    
    # Count pawns by file
    for color in [chess.WHITE, chess.BLACK]:
        color_name = "White" if color == chess.WHITE else "Black"
        pawns = board.pieces(chess.PAWN, color)
        
        files = {}
        for pawn_square in pawns:
            file = chess.square_file(pawn_square)
            files[file] = files.get(file, 0) + 1
        
        print(f"{color_name} pawn structure:")
        for file, count in sorted(files.items()):
            file_name = chr(ord('a') + file)
            print(f"  {file_name}-file: {count} pawn(s)")
            if count > 1:
                print(f"    ⚠️ Doubled pawns on {file_name}-file")

def analyze_tactical_elements(evaluator, board):
    """Analyze tactical elements in complex positions."""
    print(f"\n⚔️ Tactical Analysis:")
    
    # Check for checks, captures, threats
    if board.is_check():
        print("  ✓ Position has check")
    
    # Count attacked pieces
    for color in [chess.WHITE, chess.BLACK]:
        color_name = "White" if color == chess.WHITE else "Black"
        attacked_pieces = []
        
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece and piece.color == color:
                if board.is_attacked_by(not color, square):
                    piece_name = chess.piece_name(piece.piece_type)
                    square_name = chess.square_name(square)
                    attacked_pieces.append(f"{piece_name} on {square_name}")
        
        if attacked_pieces:
            print(f"  {color_name} pieces under attack:")
            for attacked in attacked_pieces:
                print(f"    - {attacked}")

if __name__ == "__main__":
    analyze_white_play()

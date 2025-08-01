"""
Simple test script to debug the chess engine.
"""

from bitboard import Board, Move, Color, Square
from evaluation import Evaluation

def test_board():
    """Test basic board functionality."""
    print("Testing board setup...")
    board = Board()
    
    print("Initial position:")
    print(board)
    print(f"FEN: {board.to_fen()}")
    
    # Test legal move generation
    print("\nTesting move generation...")
    legal_moves = board.generate_legal_moves()
    print(f"Number of legal moves: {len(legal_moves)}")
    
    # Print first few moves
    print("First 10 legal moves:")
    for i, move in enumerate(legal_moves[:10]):
        from_sq = Square.from_index(move.from_square)
        to_sq = Square.from_index(move.to_square)
        print(f"  {i+1}. {from_sq} -> {to_sq} ({move})")
    
    # Test making a move
    print("\nTesting move execution...")
    e2e4_move = None
    for move in legal_moves:
        from_sq = Square.from_index(move.from_square)
        to_sq = Square.from_index(move.to_square)
        if str(from_sq) == "e2" and str(to_sq) == "e4":
            e2e4_move = move
            break
    
    if e2e4_move:
        print(f"Making move: {e2e4_move}")
        success = board.make_move(e2e4_move)
        print(f"Move successful: {success}")
        print("Position after e2-e4:")
        print(board)
        print(f"FEN: {board.to_fen()}")
        
        # Check black's legal moves
        black_moves = board.generate_legal_moves()
        print(f"Black has {len(black_moves)} legal moves")
        print("First 5 black moves:")
        for i, move in enumerate(black_moves[:5]):
            from_sq = Square.from_index(move.from_square)
            to_sq = Square.from_index(move.to_square)
            print(f"  {i+1}. {from_sq} -> {to_sq} ({move})")
    else:
        print("Could not find e2-e4 move!")

def test_evaluation():
    """Test evaluation function."""
    print("\n" + "="*50)
    print("Testing evaluation...")
    
    board = Board()
    evaluator = Evaluation()
    
    # Test starting position
    score = evaluator.evaluate(board)
    print(f"Starting position evaluation: {score}")
    
    # Test after e2-e4
    legal_moves = board.generate_legal_moves()
    e2e4_move = None
    for move in legal_moves:
        from_sq = Square.from_index(move.from_square)
        to_sq = Square.from_index(move.to_square)
        if str(from_sq) == "e2" and str(to_sq) == "e4":
            e2e4_move = move
            break
    
    if e2e4_move and board.make_move(e2e4_move):
        score = evaluator.evaluate(board)
        print(f"After e2-e4 evaluation: {score}")

if __name__ == "__main__":
    test_board()
    test_evaluation()
    test_move_validation()
    test_search_simple()
    """Test move validation and illegal move detection."""
    print("\n" + "="*50)
    print("Testing move validation...")
    
    board = Board()
    
    # Test a clearly illegal move
    print("Testing illegal moves...")
    legal_moves = board.generate_legal_moves()
    
    # Check if h7h2 is in legal moves (it shouldn't be)
    h7h2_found = False
    for move in legal_moves:
        from_sq = Square.from_index(move.from_square)
        to_sq = Square.from_index(move.to_square)
        move_str = f"{from_sq}{to_sq}"
        if move_str == "h7h2":
            h7h2_found = True
            print(f"ERROR: Found illegal move {move_str} in legal moves!")
            break
    
    if not h7h2_found:
        print("Good: h7h2 not found in legal moves")
    
    # Print all legal moves to verify
    print(f"\nAll {len(legal_moves)} legal moves:")
    for i, move in enumerate(legal_moves):
        from_sq = Square.from_index(move.from_square)
        to_sq = Square.from_index(move.to_square)
        move_str = f"{from_sq}{to_sq}"
        print(f"  {i+1:2d}. {move_str}")

def test_search_simple():
    """Test search with depth 1 only."""
    print("\n" + "="*50)
    print("Testing simple search...")
    
    from search import NegascoutSearch
    from bitboard_evaluation import Evaluation
    
    board = Board()
    evaluator = Evaluation()
    searcher = NegascoutSearch(evaluator)
    
    print("Running depth-1 search...")
    best_move, score, stats = searcher.search(board, 1, 1.0)
    
    print(f"Best move: {best_move}")
    print(f"Score: {score}")
    print(f"Stats: {stats}")
    
    if best_move:
        from_sq = Square.from_index(best_move.from_square)
        to_sq = Square.from_index(best_move.to_square)
        print(f"Move details: {from_sq} -> {to_sq}")

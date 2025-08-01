"""
Main chess engine implementation.
"""

from bitboard import Board, Move, Color
from evaluation import Evaluation
from search import NegascoutSearch
from typing import Optional, Tuple, Dict


class ChessEngine:
    """Main chess engine class."""
    
    def __init__(self):
        self.board = Board()
        self.evaluator = Evaluation()
        self.searcher = NegascoutSearch(self.evaluator)
        
        # Engine settings
        self.max_depth = 6
        self.time_limit = 5.0
    
    def set_position(self, fen: Optional[str] = None):
        """Set the board position from FEN or starting position."""
        if fen:
            self.board.from_fen(fen)
        else:
            self.board.setup_starting_position()
    
    def get_best_move(self, depth: Optional[int] = None, time_limit: Optional[float] = None) -> Optional[Move]:
        """Get the best move for the current position."""
        search_depth = depth if depth is not None else self.max_depth
        search_time = time_limit if time_limit is not None else self.time_limit
        
        best_move, score, stats = self.searcher.search(self.board, search_depth, search_time)
        
        print(f"Search completed:")
        print(f"  Best move: {best_move}")
        print(f"  Evaluation: {score}")
        print(f"  Nodes searched: {stats['nodes_searched']}")
        print(f"  Time taken: {stats['time_taken']:.3f}s")
        print(f"  Nodes per second: {stats['nps']:.0f}")
        
        return best_move
    
    def make_move(self, move: Move) -> bool:
        """Make a move on the board."""
        return self.board.make_move(move)
    
    def make_move_string(self, move_str: str) -> bool:
        """Make a move from string notation (e.g., 'e2e4')."""
        legal_moves = self.board.generate_legal_moves()
        
        for move in legal_moves:
            if str(move) == move_str:
                return self.board.make_move(move)
        
        return False
    
    def get_legal_moves(self) -> list:
        """Get all legal moves in current position."""
        return self.board.generate_legal_moves()
    
    def is_game_over(self) -> Tuple[bool, str]:
        """Check if the game is over and return reason."""
        legal_moves = self.board.generate_legal_moves()
        
        if not legal_moves:
            if self.board.is_in_check(self.board.to_move):
                winner = "Black" if self.board.to_move == Color.WHITE else "White"
                return True, f"Checkmate - {winner} wins"
            else:
                return True, "Stalemate - Draw"
        
        if self.evaluator.is_draw(self.board):
            return True, "Draw by insufficient material or repetition"
        
        return False, ""
    
    def get_position_fen(self) -> str:
        """Get the current position as FEN string."""
        return self.board.to_fen()
    
    def evaluate_position(self) -> int:
        """Get the static evaluation of current position."""
        return self.evaluator.evaluate(self.board)
    
    def print_board(self):
        """Print the current board position."""
        print(self.board)
        print(f"FEN: {self.board.to_fen()}")
        print(f"Evaluation: {self.evaluator.evaluate(self.board)}")
        print(f"Legal moves: {len(self.board.generate_legal_moves())}")


def main():
    """Simple test of the engine."""
    engine = ChessEngine()
    
    print("Static Evaluation Chess Engine")
    print("=" * 40)
    
    engine.print_board()
    
    # Test a few moves
    test_moves = ["e2e4", "e7e5", "g1f3", "b8c6"]
    
    for move_str in test_moves:
        print(f"\nMaking move: {move_str}")
        if engine.make_move_string(move_str):
            engine.print_board()
            
            # Get engine's response
            print("\nEngine thinking...")
            best_move = engine.get_best_move(depth=4)
            if best_move:
                print(f"Engine plays: {best_move}")
                engine.make_move(best_move)
                engine.print_board()
        else:
            print(f"Invalid move: {move_str}")
        
        # Check if game is over
        game_over, reason = engine.is_game_over()
        if game_over:
            print(f"Game over: {reason}")
            break


if __name__ == "__main__":
    main()
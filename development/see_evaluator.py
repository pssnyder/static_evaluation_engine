"""
Static Exchange Evaluation (SEE) for Cece v1.2

Evaluates the material gain/loss from a sequence of captures on a square.
This helps the engine avoid bad trades and tactical blunders.

Key Features:
- Calculates net material after all captures
- Considers piece values and attack sequences
- Prevents moves like Ng5 that lose material
- Improves tactical awareness
"""

import chess
from typing import List, Optional, Tuple

class StaticExchangeEvaluator:
    """Evaluates static exchange of pieces on squares."""
    
    def __init__(self):
        # Standard piece values for SEE calculation
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000  # King capture ends sequence
        }
    
    def evaluate_capture(self, board: chess.Board, move: chess.Move) -> int:
        """
        Evaluate the static exchange value of a capture move.
        
        Args:
            board: Current board position
            move: The capture move to evaluate
            
        Returns:
            Net material gain/loss from the capture sequence
        """
        if not board.is_capture(move):
            return 0
            
        # Get the target square and initial victim
        target_square = move.to_square
        victim = board.piece_at(target_square)
        
        if not victim:
            return 0
            
        # Start the exchange sequence
        gain = [self.piece_values[victim.piece_type]]
        
        # Make the initial capture
        board_copy = board.copy()
        board_copy.push(move)
        
        # Get attacking piece value
        attacker = board.piece_at(move.from_square)
        if attacker:
            attacking_piece_value = self.piece_values[attacker.piece_type]
        else:
            return gain[0]  # No attacker somehow
        
        # Continue the exchange sequence
        self._continue_exchange(board_copy, target_square, attacking_piece_value, gain)
        
        # Calculate final result using minimax
        return self._minimax_gain(gain)
    
    def _continue_exchange(self, board: chess.Board, square: chess.Square, 
                          last_attacker_value: int, gain: List[int]):
        """Continue the exchange sequence recursively."""
        
        # Find the least valuable attacker
        attacker_move = self._find_least_valuable_attacker(board, square)
        
        if not attacker_move:
            return  # No more attackers
            
        # Get the attacking piece
        attacker = board.piece_at(attacker_move.from_square)
        if not attacker:
            return
            
        attacker_value = self.piece_values[attacker.piece_type]
        
        # Add the captured piece value to gain
        gain.append(last_attacker_value - gain[-1])
        
        # Make the capture
        board.push(attacker_move)
        
        # Continue recursively
        self._continue_exchange(board, square, attacker_value, gain)
    
    def _find_least_valuable_attacker(self, board: chess.Board, 
                                    square: chess.Square) -> Optional[chess.Move]:
        """Find the least valuable piece that can attack the square."""
        
        attacking_moves = []
        
        # Check all legal moves for attacks on the square
        for move in board.legal_moves:
            if move.to_square == square and board.is_capture(move):
                attacker = board.piece_at(move.from_square)
                if attacker:
                    attacking_moves.append((move, self.piece_values[attacker.piece_type]))
        
        if not attacking_moves:
            return None
            
        # Return move with least valuable attacker
        attacking_moves.sort(key=lambda x: x[1])
        return attacking_moves[0][0]
    
    def _minimax_gain(self, gain: List[int]) -> int:
        """Calculate final gain using minimax principle."""
        if not gain:
            return 0
            
        # Work backwards through the gain list
        for i in range(len(gain) - 2, -1, -1):
            gain[i] = max(0, gain[i] - gain[i + 1])
            
        return gain[0]
    
    def evaluate_square_safety(self, board: chess.Board, square: chess.Square) -> int:
        """
        Evaluate how safe it is to place a piece on a square.
        
        Returns:
            Positive if square is safe, negative if dangerous
        """
        # Count attackers and defenders
        attackers = self._count_attackers(board, square, not board.turn)
        defenders = self._count_attackers(board, square, board.turn)
        
        # Simple heuristic: more defenders = safer
        safety_score = (len(defenders) - len(attackers)) * 50
        
        return safety_score
    
    def _count_attackers(self, board: chess.Board, square: chess.Square, 
                        color: chess.Color) -> List[chess.Square]:
        """Count pieces of given color that attack a square."""
        attackers = []
        
        # Check each piece type
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, 
                          chess.ROOK, chess.QUEEN, chess.KING]:
            
            # Find pieces of this type and color
            piece_squares = board.pieces(piece_type, color)
            
            for piece_square in piece_squares:
                # Check if this piece attacks the target square
                if self._piece_attacks_square(board, piece_square, square, piece_type):
                    attackers.append(piece_square)
        
        return attackers
    
    def _piece_attacks_square(self, board: chess.Board, piece_square: chess.Square,
                            target_square: chess.Square, piece_type: int) -> bool:
        """Check if a piece attacks a target square."""
        
        piece = board.piece_at(piece_square)
        if not piece:
            return False
            
        # Check if piece attacks target square
        attacks = board.attacks(piece_square)
        return target_square in attacks
    
    def get_best_capture_sequence(self, board: chess.Board) -> List[Tuple[chess.Move, int]]:
        """
        Get all captures sorted by SEE value.
        
        Returns:
            List of (move, see_value) tuples sorted by value
        """
        captures = []
        
        for move in board.legal_moves:
            if board.is_capture(move):
                see_value = self.evaluate_capture(board, move)
                captures.append((move, see_value))
        
        # Sort by SEE value (best first)
        captures.sort(key=lambda x: x[1], reverse=True)
        
        return captures

# Test functions for development
def test_see_evaluation():
    """Test the SEE evaluator with known positions."""
    see = StaticExchangeEvaluator()
    
    # Test position: Queen takes pawn defended by rook
    # Should lose queen (900) - pawn (100) = -800
    board = chess.Board("rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2")
    
    # Move queen to take pawn on d5
    move = chess.Move.from_uci("d1d5")
    
    if move in board.legal_moves:
        see_value = see.evaluate_capture(board, move)
        print(f"SEE for Qxd5: {see_value} (should be negative)")
    
    print("SEE evaluator test complete")

if __name__ == "__main__":
    test_see_evaluation()

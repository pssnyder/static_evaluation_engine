"""
Threat Evaluator for Cece v1.2

Evaluates piece threats and safety to prevent tactical blunders.
Helps avoid moves like Ng5 that expose pieces to capture.

Key Features:
- Evaluates piece threats using MVV-LVA
- Calculates hanging pieces
- Assesses piece safety after moves
- Prevents sacrificial blunders
"""

import chess
from typing import Dict, List, Tuple, Optional, Any

class ThreatEvaluator:
    """Evaluates threats and piece safety."""
    
    def __init__(self):
        # Piece values for threat calculation
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
    
    def evaluate_threats(self, board: chess.Board) -> int:
        """
        Evaluate all threats on the board.
        
        Returns:
            Positive score favors current player, negative favors opponent
        """
        score = 0
        
        # Evaluate threats for both sides
        our_threats = self._calculate_side_threats(board, board.turn)
        their_threats = self._calculate_side_threats(board, not board.turn)
        
        score += our_threats - their_threats
        
        # Evaluate hanging pieces
        our_hanging = self._find_hanging_pieces(board, board.turn)
        their_hanging = self._find_hanging_pieces(board, not board.turn)
        
        score -= our_hanging  # Penalty for our hanging pieces
        score += their_hanging  # Bonus for their hanging pieces
        
        return score
    
    def _calculate_side_threats(self, board: chess.Board, color: chess.Color) -> int:
        """Calculate total threat value for one side."""
        threat_score = 0
        
        # Find all pieces of this color
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, 
                          chess.ROOK, chess.QUEEN, chess.KING]:
            
            piece_squares = board.pieces(piece_type, color)
            
            for square in piece_squares:
                # Get squares this piece attacks
                attacks = board.attacks(square)
                
                for target_square in attacks:
                    target_piece = board.piece_at(target_square)
                    
                    # If attacking enemy piece
                    if target_piece and target_piece.color != color:
                        # Calculate threat value using MVV-LVA principle
                        victim_value = self.piece_values[target_piece.piece_type]
                        attacker_value = self.piece_values[piece_type]
                        
                        # Higher value for capturing more valuable pieces with less valuable pieces
                        if victim_value >= attacker_value:
                            threat_score += victim_value - attacker_value + 10
                        else:
                            # Still some value for any threat
                            threat_score += 5
        
        return threat_score
    
    def _find_hanging_pieces(self, board: chess.Board, color: chess.Color) -> int:
        """Find pieces that are hanging (undefended and attacked)."""
        hanging_value = 0
        
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, 
                          chess.ROOK, chess.QUEEN]:  # Don't check king
            
            piece_squares = board.pieces(piece_type, color)
            
            for square in piece_squares:
                if self._is_piece_hanging(board, square, color):
                    hanging_value += self.piece_values[piece_type]
        
        return hanging_value
    
    def _is_piece_hanging(self, board: chess.Board, square: chess.Square, 
                         color: chess.Color) -> bool:
        """Check if a piece is hanging (attacked but not defended)."""
        
        # Count attackers by opponent
        attackers = 0
        for attacker_square in chess.SQUARES:
            piece = board.piece_at(attacker_square)
            if piece and piece.color != color:
                if square in board.attacks(attacker_square):
                    attackers += 1
        
        if attackers == 0:
            return False  # Not attacked
        
        # Count defenders
        defenders = 0
        for defender_square in chess.SQUARES:
            piece = board.piece_at(defender_square)
            if piece and piece.color == color and defender_square != square:
                if square in board.attacks(defender_square):
                    defenders += 1
        
        return attackers > defenders
    
    def evaluate_move_safety(self, board: chess.Board, move: chess.Move) -> int:
        """
        Evaluate the safety of a move before making it.
        
        Returns:
            Positive if move is safe, negative if dangerous
        """
        safety_score = 0
        
        # Make the move temporarily
        board_copy = board.copy()
        board_copy.push(move)
        
        # Check if the moved piece is now hanging
        moved_piece = board_copy.piece_at(move.to_square)
        if moved_piece:
            if self._is_piece_hanging(board_copy, move.to_square, moved_piece.color):
                # Severe penalty for moving into danger
                piece_value = self.piece_values[moved_piece.piece_type]
                safety_score -= piece_value
        
        # Check for discovered attacks on our pieces
        discovered_threats = self._find_discovered_threats(board, board_copy, move)
        safety_score -= discovered_threats
        
        return safety_score
    
    def _find_discovered_threats(self, original_board: chess.Board, 
                               new_board: chess.Board, move: chess.Move) -> int:
        """Find pieces that become threatened after a move."""
        threat_value = 0
        
        moving_color = original_board.turn
        
        # Check all our pieces for new threats
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, 
                          chess.ROOK, chess.QUEEN, chess.KING]:
            
            piece_squares = new_board.pieces(piece_type, moving_color)
            
            for square in piece_squares:
                # Skip the piece that just moved (already checked)
                if square == move.to_square:
                    continue
                    
                # Check if this piece was safe before but threatened now
                was_safe = not self._is_piece_hanging(original_board, square, moving_color)
                is_threatened = self._is_piece_hanging(new_board, square, moving_color)
                
                if was_safe and is_threatened:
                    threat_value += self.piece_values[piece_type] // 2  # Partial penalty
        
        return threat_value
    
    def get_threat_analysis(self, board: chess.Board) -> Dict[str, Any]:
        """Get detailed threat analysis for debugging."""
        analysis = {
            'total_threat_score': self.evaluate_threats(board),
            'hanging_pieces': {
                'white': [],
                'black': []
            },
            'piece_threats': {
                'white_threatens': [],
                'black_threatens': []
            }
        }
        
        # Find hanging pieces
        for color in [chess.WHITE, chess.BLACK]:
            color_name = 'white' if color == chess.WHITE else 'black'
            
            for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, 
                              chess.ROOK, chess.QUEEN]:
                
                piece_squares = board.pieces(piece_type, color)
                
                for square in piece_squares:
                    if self._is_piece_hanging(board, square, color):
                        piece_name = chess.piece_name(piece_type)
                        square_name = chess.square_name(square)
                        analysis['hanging_pieces'][color_name].append(
                            f"{piece_name} on {square_name}"
                        )
        
        return analysis
    
    def suggest_safe_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[Tuple[chess.Move, int]]:
        """
        Rate moves by safety score.
        
        Returns:
            List of (move, safety_score) tuples sorted by safety
        """
        move_safety = []
        
        for move in moves:
            safety = self.evaluate_move_safety(board, move)
            move_safety.append((move, safety))
        
        # Sort by safety (safest first)
        move_safety.sort(key=lambda x: x[1], reverse=True)
        
        return move_safety

# Test functions
def test_threat_evaluator():
    """Test the threat evaluator with the problematic position."""
    threat_eval = ThreatEvaluator()
    
    # Starting position
    board = chess.Board()
    
    print("=== Starting Position Analysis ===")
    analysis = threat_eval.get_threat_analysis(board)
    print(f"Threat score: {analysis['total_threat_score']}")
    print(f"Hanging pieces: {analysis['hanging_pieces']}")
    
    # After 1. Nh3
    board.push_san("Nh3")
    print("\n=== After 1. Nh3 ===")
    analysis = threat_eval.get_threat_analysis(board)
    print(f"Threat score: {analysis['total_threat_score']}")
    
    # Test the problematic 2. Ng5 move
    board.push_san("f6")  # Black's response
    
    print("\n=== Evaluating 2. Ng5 ===")
    ng5_move = chess.Move.from_uci("h3g5")
    safety = threat_eval.evaluate_move_safety(board, ng5_move)
    print(f"Safety score for Ng5: {safety} (should be very negative)")
    
    print("Threat evaluator test complete")

if __name__ == "__main__":
    test_threat_evaluator()

#!/usr/bin/env python3
"""
Cece v1.3 Evaluation Redesign Implementation
Dynamic piece values with proper pawn-relative scoring based on strategic preferences.
"""

import chess
from typing import Dict, Any, List, Tuple

class EvaluationV13:
    """
    v1.3 Evaluation with dynamic piece values and pawn-relative scoring.
    Designed for Tal-style tactical play with proper calculation foundation.
    """
    
    def __init__(self):
        # Base piece values (in centipawns)
        self.base_piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,    # Static baseline
            chess.BISHOP: 275,    # Lower base, gets bonus when paired
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Strategic bonuses/penalties (in pawn equivalents * 100)
        self.bishop_pair_bonus = 25      # +0.25 pawns when both bishops present
        self.single_bishop_penalty = 25  # -0.25 pawns when only one bishop
        
        # Development penalties (stronger than positional)
        self.same_piece_twice_penalty = 50   # -0.50 pawns for moving same piece twice
        self.early_queen_penalty = 75        # -0.75 pawns for early queen moves
        self.minor_piece_unmoved_bonus = 30  # +0.30 pawns per undeveloped minor piece
        
        # King safety zones and bonuses
        self.king_safety_zone_bonus = 20    # +0.20 pawns per protected square
        self.exposed_king_penalty = 150     # -1.50 pawns for exposed king
        
        # Tal-style tactical preferences
        self.open_file_bonus = 40           # +0.40 pawns for rook on open file
        self.tension_bonus = 15             # +0.15 pawns per tension point
        self.sacrifice_calculation_bonus = 100  # +1.00 pawns for calculated sacrifices
        
        # Game phase tracking
        self.opening_move_threshold = 12     # Moves 1-12 = opening
        self.endgame_piece_threshold = 14    # < 14 pieces = endgame
        
        # Initialize enhanced PST tables with game phase consideration
        self.init_enhanced_pst_tables()
        
        # Move tracking for development analysis
        self.piece_move_count = {}
        self.developed_pieces = set()
    
    def init_enhanced_pst_tables(self):
        """Initialize game-phase aware PST tables."""
        
        # Opening knight table - harsh rim penalties for development
        self.knight_opening_table = [
            -150,-100, -75, -50, -50, -75,-100,-150,  # Rank 8 - very harsh
            -100, -50, -25,  -5,  -5, -25, -50,-100,  # Rank 7
             -75, -25,  20,  30,  30,  20, -25, -75,  # Rank 6
             -50,  -5,  30,  40,  40,  30,  -5, -50,  # Rank 5
             -50,  -5,  30,  40,  40,  30,  -5, -50,  # Rank 4
             -75, -25,  20,  30,  30,  20, -25, -75,  # Rank 3
             -100, -50, -25,  -5,  -5, -25, -50,-100,  # Rank 2
             -150,-100, -75, -50, -50, -75,-100,-150   # Rank 1 - very harsh
        ]
        
        # Middlegame/Endgame knight table - reduced rim penalties for tactical flexibility
        self.knight_tactical_table = [
            -80, -60, -40, -20, -20, -40, -60, -80,   # Rank 8 - less harsh
            -60, -30, -10,   5,   5, -10, -30, -60,   # Rank 7
            -40, -10,  25,  35,  35,  25, -10, -40,   # Rank 6
            -20,   5,  35,  45,  45,  35,   5, -20,   # Rank 5
            -20,   5,  35,  45,  45,  35,   5, -20,   # Rank 4
            -40, -10,  25,  35,  35,  25, -10, -40,   # Rank 3
            -60, -30, -10,   5,   5, -10, -30, -60,   # Rank 2
            -80, -60, -40, -20, -20, -40, -60, -80    # Rank 1 - less harsh
        ]
        
        # Queen table - severe early development penalties
        self.queen_table = [
            -50, -40, -30, -20, -20, -30, -40, -50,   # Rank 8
            -40, -20, -10,  -5,  -5, -10, -20, -40,   # Rank 7
            -30, -10,  10,  15,  15,  10, -10, -30,   # Rank 6
            -20,  -5,  15,  20,  20,  15,  -5, -20,   # Rank 5
            -20,  -5,  15,  20,  20,  15,  -5, -20,   # Rank 4
            -30, -10,  10,  15,  15,  10, -10, -30,   # Rank 3
            -40, -20, -10,  -5,  -5, -10, -20, -40,   # Rank 2
            -75, -50, -40, -30, -30, -40, -50, -75    # Rank 1 - harsh early penalty
        ]
        
        # Enhanced pawn table encouraging central control and advancement
        self.pawn_table = [
             0,   0,   0,   0,   0,   0,   0,   0,   # Rank 8 (promotion)
            80,  80,  80,  80,  80,  80,  80,  80,   # Rank 7 - strong promotion threat
            25,  25,  35,  45,  45,  35,  25,  25,   # Rank 6
            15,  15,  20,  35,  35,  20,  15,  15,   # Rank 5
            10,  10,  15,  30,  30,  15,  10,  10,   # Rank 4
             5,   5,  10,  25,  25,  10,   5,   5,   # Rank 3
             5,  10,  10, -20, -20,  10,  10,   5,   # Rank 2
             0,   0,   0,   0,   0,   0,   0,   0    # Rank 1
        ]
        
        # Other piece tables can be added as needed
    
    def get_dynamic_piece_values(self, board: chess.Board) -> Dict[int, int]:
        """Calculate dynamic piece values based on current position."""
        values = self.base_piece_values.copy()
        
        # Bishop pair evaluation
        white_bishops = len(board.pieces(chess.BISHOP, chess.WHITE))
        black_bishops = len(board.pieces(chess.BISHOP, chess.BLACK))
        
        # Adjust bishop values based on pair presence
        if white_bishops == 2:
            values[chess.BISHOP] = self.base_piece_values[chess.BISHOP] + self.bishop_pair_bonus
        elif white_bishops == 1:
            values[chess.BISHOP] = self.base_piece_values[chess.BISHOP] - self.single_bishop_penalty
            
        # Note: This is simplified - in full implementation, we'd track per-color
        
        return values
    
    def get_game_phase(self, board: chess.Board) -> str:
        """Determine current game phase for PST selection."""
        move_count = board.fullmove_number
        total_pieces = len(board.piece_map())
        
        if move_count <= self.opening_move_threshold:
            return "opening"
        elif total_pieces < self.endgame_piece_threshold:
            return "endgame"
        else:
            return "middlegame"
    
    def evaluate_development(self, board: chess.Board) -> int:
        """Evaluate piece development with penalties for repeated moves."""
        development_score = 0
        game_phase = self.get_game_phase(board)
        
        if game_phase != "opening":
            return 0  # Only apply in opening
        
        # Count undeveloped minor pieces
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if (color == board.turn) else -1
            
            # Starting squares for minor pieces
            if color == chess.WHITE:
                starting_squares = [chess.B1, chess.G1, chess.C1, chess.F1]  # Knights and bishops
            else:
                starting_squares = [chess.B8, chess.G8, chess.C8, chess.F8]
            
            undeveloped_count = 0
            for square in starting_squares:
                piece = board.piece_at(square)
                if piece and piece.color == color and piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                    undeveloped_count += 1
            
            # Penalty for each undeveloped piece
            development_score += multiplier * undeveloped_count * self.minor_piece_unmoved_bonus
        
        # Early queen penalty
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if (color == board.turn) else -1
            queens = board.pieces(chess.QUEEN, color)
            
            for queen_square in queens:
                # If queen is not on starting square in opening, apply penalty
                starting_square = chess.D1 if color == chess.WHITE else chess.D8
                if queen_square != starting_square and game_phase == "opening":
                    development_score += multiplier * self.early_queen_penalty
        
        return development_score
    
    def evaluate_king_safety_zones(self, board: chess.Board) -> int:
        """Evaluate king safety using 6-square protection zones."""
        safety_score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if (color == board.turn) else -1
            king_square = board.king(color)
            
            if not king_square:
                continue
                
            king_file = chess.square_file(king_square)
            king_rank = chess.square_rank(king_square)
            
            # Define the 2x3 safety zone in front of the king
            if color == chess.WHITE:
                zone_ranks = [king_rank + 1, king_rank + 2]
            else:
                zone_ranks = [king_rank - 1, king_rank - 2]
            
            zone_files = [king_file - 1, king_file, king_file + 1]
            
            protected_squares = 0
            total_zone_squares = 0
            
            for rank in zone_ranks:
                for file in zone_files:
                    if 0 <= rank <= 7 and 0 <= file <= 7:
                        zone_square = chess.square(file, rank)
                        total_zone_squares += 1
                        
                        piece = board.piece_at(zone_square)
                        if piece and piece.color == color:
                            protected_squares += 1
                        elif board.is_attacked_by(color, zone_square):
                            protected_squares += 0.5  # Attacked but not occupied
            
            # Calculate safety bonus
            if total_zone_squares > 0:
                protection_ratio = protected_squares / total_zone_squares
                safety_score += multiplier * int(protection_ratio * self.king_safety_zone_bonus * total_zone_squares)
            
            # Severe penalty for exposed king
            if protected_squares < 2:
                safety_score += multiplier * self.exposed_king_penalty
        
        return safety_score
    
    def evaluate_tal_style_factors(self, board: chess.Board) -> int:
        """Evaluate factors that encourage Tal-style tactical play."""
        tal_score = 0
        
        # Open files bonus for rooks
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if (color == board.turn) else -1
            rooks = board.pieces(chess.ROOK, color)
            
            for rook_square in rooks:
                rook_file = chess.square_file(rook_square)
                
                # Check if file is open (no pawns)
                file_is_open = True
                for rank in range(8):
                    check_square = chess.square(rook_file, rank)
                    piece = board.piece_at(check_square)
                    if piece and piece.piece_type == chess.PAWN:
                        file_is_open = False
                        break
                
                if file_is_open:
                    tal_score += multiplier * self.open_file_bonus
        
        # Tension evaluation (simplified)
        tension_count = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                attackers = len(board.attackers(not piece.color, square))
                defenders = len(board.attackers(piece.color, square))
                if attackers > 0 and defenders > 0:
                    tension_count += 1
        
        tal_score += tension_count * self.tension_bonus
        
        return tal_score
    
    def evaluate_position(self, board: chess.Board) -> Dict[str, Any]:
        """Main evaluation function with all v1.3 improvements."""
        
        # Get dynamic piece values for this position
        piece_values = self.get_dynamic_piece_values(board)
        
        # Calculate material balance with dynamic values
        material_score = 0
        for piece_type, value in piece_values.items():
            if piece_type == chess.KING:
                continue
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            material_score += (white_count - black_count) * value
        
        # Positional evaluation with game-phase aware PST
        positional_score = self._evaluate_positional_v13(board)
        
        # Development evaluation
        development_score = self.evaluate_development(board)
        
        # Enhanced king safety
        king_safety_score = self.evaluate_king_safety_zones(board)
        
        # Tal-style tactical factors
        tactical_score = self.evaluate_tal_style_factors(board)
        
        # Total score calculation
        total_score = (material_score + positional_score + development_score + 
                      king_safety_score + tactical_score)
        
        # Return from current player's perspective
        if board.turn == chess.BLACK:
            total_score = -total_score
        
        return {
            'total_score': total_score,
            'material': material_score,
            'positional': positional_score,
            'development': development_score,
            'king_safety': king_safety_score,
            'tactical': tactical_score,
            'game_phase': self.get_game_phase(board)
        }
    
    def _evaluate_positional_v13(self, board: chess.Board) -> int:
        """Enhanced positional evaluation with game-phase PST."""
        positional_score = 0
        game_phase = self.get_game_phase(board)
        
        # Select appropriate knight table based on game phase
        if game_phase == "opening":
            knight_table = self.knight_opening_table
        else:
            knight_table = self.knight_tactical_table
        
        # Evaluate knights with phase-appropriate table
        for square in board.pieces(chess.KNIGHT, chess.WHITE):
            table_index = self._square_to_table_index(square, chess.WHITE)
            positional_score += knight_table[table_index]
        
        for square in board.pieces(chess.KNIGHT, chess.BLACK):
            table_index = self._square_to_table_index(square, chess.BLACK)
            positional_score -= knight_table[table_index]
        
        # Evaluate queens with early development penalties
        for square in board.pieces(chess.QUEEN, chess.WHITE):
            table_index = self._square_to_table_index(square, chess.WHITE)
            positional_score += self.queen_table[table_index]
            
        for square in board.pieces(chess.QUEEN, chess.BLACK):
            table_index = self._square_to_table_index(square, chess.BLACK)
            positional_score -= self.queen_table[table_index]
        
        # Evaluate pawns with advancement bonus
        for square in board.pieces(chess.PAWN, chess.WHITE):
            table_index = self._square_to_table_index(square, chess.WHITE)
            positional_score += self.pawn_table[table_index]
            
        for square in board.pieces(chess.PAWN, chess.BLACK):
            table_index = self._square_to_table_index(square, chess.BLACK)
            positional_score -= self.pawn_table[table_index]
        
        return positional_score
    
    def _square_to_table_index(self, square: chess.Square, color: chess.Color) -> int:
        """Convert square to PST index, flipping for black."""
        if color == chess.WHITE:
            return square ^ 56  # Flip rank for white
        else:
            return square


# Test the new evaluation system
def test_v13_evaluation():
    """Test the new v1.3 evaluation system."""
    print("🧪 TESTING CECE v1.3 EVALUATION SYSTEM")
    print("=" * 50)
    
    evaluator = EvaluationV13()
    
    # Test starting position
    board = chess.Board()
    result = evaluator.evaluate_position(board)
    
    print("Starting Position:")
    for component, value in result.items():
        if component != 'game_phase':
            pawn_equiv = value / 100
            print(f"  {component}: {value:4d} ({pawn_equiv:+.2f} pawns)")
        else:
            print(f"  {component}: {value}")
    
    print(f"\nTotal: {result['total_score']} ({result['total_score']/100:+.2f} pawns)")
    
    # Test after problematic Nh3 move
    board.push_san("Nh3")
    result = evaluator.evaluate_position(board)
    
    print(f"\nAfter 1. Nh3 (should be heavily penalized):")
    print(f"  Total: {result['total_score']} ({result['total_score']/100:+.2f} pawns)")
    print(f"  Positional: {result['positional']} ({result['positional']/100:+.2f} pawns)")

if __name__ == "__main__":
    test_v13_evaluation()

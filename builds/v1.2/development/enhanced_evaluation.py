"""
Enhanced Evaluation System for Cece v1.2

Integrates new evaluators:
- Static Exchange Evaluation (SEE)
- Threat Evaluation  
- Castling Evaluation
- Enhanced PST enforcement
- Better move ordering
"""

import chess
from typing import Dict, Optional, Any, Tuple
from see_evaluator import StaticExchangeEvaluator
from threat_evaluator import ThreatEvaluator
from development.castling_evaluator import CastlingEvaluator

class EnhancedEvaluation:
    """Enhanced evaluation system with improved tactical awareness."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize enhanced evaluation system."""
        self.config = config or {}
        
        # Initialize specialized evaluators
        self.see_evaluator = StaticExchangeEvaluator()
        self.threat_evaluator = ThreatEvaluator()
        self.castling_evaluator = CastlingEvaluator()
        
        # Enhanced evaluation weights
        self.weights = self.config.get('weights', {
            'material': 1.0,
            'positional': 0.6,      # Increased PST weight
            'tactical': 0.9,        # Increased tactical weight
            'king_safety': 0.8,     # Increased safety weight
            'see_bonus': 0.7,       # NEW: SEE evaluation
            'threat_bonus': 0.5,    # NEW: Threat evaluation
            'castling_bonus': 0.4   # NEW: Castling evaluation
        })
        
        # Piece values
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Initialize piece-square tables
        self.init_enhanced_pst()
    
    def init_enhanced_pst(self):
        """Initialize enhanced piece-square tables."""
        
        # Enhanced queen table - stronger corner penalties
        self.queen_table = [
            -30,-20,-15,-10,-10,-15,-20,-30,  # 8th rank - STRONGER corner penalty
            -20,-10, -5,  0,  0, -5,-10,-20,  # 7th rank
            -15, -5,  5, 10, 10,  5, -5,-15,  # 6th rank
            -10,  0, 10, 15, 15, 10,  0,-10,  # 5th rank
            -10,  0, 10, 15, 15, 10,  0,-10,  # 4th rank
            -15, -5,  5, 10, 10,  5, -5,-15,  # 3rd rank
            -20,-10, -5,  0,  0, -5,-10,-20,  # 2nd rank
            -30,-20,-15,-10,-10,-15,-20,-30   # 1st rank - STRONGER corner penalty
        ]
        
        # Enhanced knight table - even stronger rim penalties
        self.knight_table = [
            -80,-40,-30,-25,-25,-30,-40,-80,  # Extremely strong rim penalty
            -40,-20,  0,  5,  5,  0,-20,-40,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -25,  5, 20, 25, 25, 20,  5,-25,
            -25,  5, 20, 25, 25, 20,  5,-25,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -80,-40,-30,-25,-25,-30,-40,-80   # Extremely strong rim penalty
        ]
        
        # Other tables remain similar but with slight adjustments
        self.pawn_table = [
             0,  0,  0,  0,  0,  0,  0,  0,
            60, 60, 60, 60, 60, 60, 60, 60,  # Stronger 7th rank bonus
            15, 15, 25, 35, 35, 25, 15, 15,
            10, 10, 15, 30, 30, 15, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        self.bishop_table = [
            -25,-15,-15,-15,-15,-15,-15,-25,
            -15,  0,  5,  5,  5,  5,  0,-15,
            -15,  5, 10, 15, 15, 10,  5,-15,
            -15,  5, 15, 20, 20, 15,  5,-15,
            -15,  5, 15, 20, 20, 15,  5,-15,
            -15, 10, 15, 15, 15, 15, 10,-15,
            -15,  5,  0,  0,  0,  0,  5,-15,
            -25,-15,-25,-15,-15,-25,-15,-25
        ]
        
        self.rook_table = [
             5,  5,  5,  5,  5,  5,  5,  5,
            15, 20, 20, 20, 20, 20, 20, 15,
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  5,  5, 10, 10,  5,  5,  0,
             0,  0,  0, 10, 10,  0,  0,  0
        ]
        
        self.king_mg_table = [
            -40,-50,-50,-60,-60,-50,-50,-40,
            -40,-50,-50,-60,-60,-50,-50,-40,
            -40,-50,-50,-60,-60,-50,-50,-40,
            -40,-50,-50,-60,-60,-50,-50,-40,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-30,-30,-30,-30,-20,
             15, 15, -5, -5, -5, -5, 15, 15,  # Castling squares bonus
             15, 25,  5, -5, -5,  5, 25, 15
        ]
    
    def evaluate_position(self, board: chess.Board) -> Tuple[int, Dict[str, Any]]:
        """
        Enhanced position evaluation with detailed breakdown.
        
        Returns:
            (total_score, evaluation_details)
        """
        details = {}
        total_score = 0
        
        # 1. Material evaluation
        material_score = self._evaluate_material(board)
        details['material'] = material_score
        total_score += material_score * self.weights['material']
        
        # 2. Enhanced positional evaluation (PST)
        positional_score = self._evaluate_positional_enhanced(board)
        details['positional'] = positional_score
        total_score += positional_score * self.weights['positional']
        
        # 3. Tactical evaluation with SEE
        see_score = self._evaluate_see_tactics(board)
        details['see_tactics'] = see_score
        total_score += see_score * self.weights['see_bonus']
        
        # 4. Threat evaluation
        threat_score = self.threat_evaluator.evaluate_threats(board)
        details['threats'] = threat_score
        total_score += threat_score * self.weights['threat_bonus']
        
        # 5. Castling evaluation
        castling_score = self.castling_evaluator.evaluate_castling(board)
        details['castling'] = castling_score
        total_score += castling_score * self.weights['castling_bonus']
        
        # 6. King safety
        king_safety_score = self._evaluate_king_safety(board)
        details['king_safety'] = king_safety_score
        total_score += king_safety_score * self.weights['king_safety']
        
        details['total_score'] = int(total_score)
        return int(total_score), details
    
    def _evaluate_material(self, board: chess.Board) -> int:
        """Basic material evaluation."""
        material_balance = 0
        
        for piece_type, value in self.piece_values.items():
            if piece_type == chess.KING:
                continue
                
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            
            material_balance += (white_count - black_count) * value
        
        # Return from perspective of side to move
        if board.turn == chess.WHITE:
            return material_balance
        else:
            return -material_balance
    
    def _evaluate_positional_enhanced(self, board: chess.Board) -> int:
        """Enhanced positional evaluation with stronger PST enforcement."""
        positional_score = 0
        
        # Map piece types to their PST
        pst_map = {
            chess.PAWN: self.pawn_table,
            chess.KNIGHT: self.knight_table,
            chess.BISHOP: self.bishop_table,
            chess.ROOK: self.rook_table,
            chess.QUEEN: self.queen_table,
            chess.KING: self.king_mg_table
        }
        
        for piece_type, pst in pst_map.items():
            # White pieces
            for square in board.pieces(piece_type, chess.WHITE):
                table_index = self._square_to_table_index(square, chess.WHITE)
                positional_score += pst[table_index]
            
            # Black pieces (flip table)
            for square in board.pieces(piece_type, chess.BLACK):
                table_index = self._square_to_table_index(square, chess.BLACK)
                positional_score -= pst[table_index]
        
        # Return from perspective of side to move
        if board.turn == chess.BLACK:
            positional_score = -positional_score
            
        return positional_score
    
    def _square_to_table_index(self, square: chess.Square, color: chess.Color) -> int:
        """Convert square to PST index, flipping for black."""
        if color == chess.WHITE:
            # White: rank 0 (1st) = index 56-63, rank 7 (8th) = index 0-7
            return square ^ 56
        else:
            # Black: use square directly
            return square
    
    def _evaluate_see_tactics(self, board: chess.Board) -> int:
        """Evaluate tactical opportunities using SEE."""
        see_score = 0
        
        # Get all captures and evaluate them
        captures = self.see_evaluator.get_best_capture_sequence(board)
        
        # Reward good captures, penalize bad ones
        for move, see_value in captures:
            if see_value > 0:
                see_score += min(see_value, 200)  # Cap bonus to prevent overvaluation
            elif see_value < 0:
                see_score += see_value // 2  # Partial penalty for bad captures available
        
        return see_score
    
    def _evaluate_king_safety(self, board: chess.Board) -> int:
        """Enhanced king safety evaluation."""
        safety_score = 0
        
        our_king = board.king(board.turn)
        their_king = board.king(not board.turn)
        
        if our_king:
            # Check attacks on squares around our king
            king_area = self._get_king_area(our_king)
            attacks_on_our_king = sum(1 for sq in king_area 
                                    if board.is_attacked_by(not board.turn, sq))
            safety_score -= attacks_on_our_king * 15
        
        if their_king:
            # Bonus for attacking their king area
            king_area = self._get_king_area(their_king)
            attacks_on_their_king = sum(1 for sq in king_area 
                                      if board.is_attacked_by(board.turn, sq))
            safety_score += attacks_on_their_king * 10
        
        return safety_score
    
    def _get_king_area(self, king_square: chess.Square) -> list:
        """Get squares around the king."""
        king_area = []
        file = chess.square_file(king_square)
        rank = chess.square_rank(king_square)
        
        for f_off in [-1, 0, 1]:
            for r_off in [-1, 0, 1]:
                new_file = file + f_off
                new_rank = rank + r_off
                
                if 0 <= new_file <= 7 and 0 <= new_rank <= 7:
                    king_area.append(chess.square(new_file, new_rank))
        
        return king_area
    
    def evaluate_move_quality(self, board: chess.Board, move: chess.Move) -> Dict[str, Any]:
        """
        Comprehensive move evaluation for debugging.
        
        This helps identify why the engine makes certain moves.
        """
        evaluation = {
            'move': str(move),
            'is_capture': board.is_capture(move),
            'is_check': False,
            'see_value': 0,
            'threat_safety': 0,
            'pst_change': 0,
            'overall_quality': 0
        }
        
        # Check if move gives check
        board_copy = board.copy()
        board_copy.push(move)
        evaluation['is_check'] = board_copy.is_check()
        
        # SEE evaluation for captures
        if board.is_capture(move):
            evaluation['see_value'] = self.see_evaluator.evaluate_capture(board, move)
        
        # Threat safety evaluation
        evaluation['threat_safety'] = self.threat_evaluator.evaluate_move_safety(board, move)
        
        # PST change evaluation
        piece = board.piece_at(move.from_square)
        if piece:
            pst_map = {
                chess.PAWN: self.pawn_table,
                chess.KNIGHT: self.knight_table,
                chess.BISHOP: self.bishop_table,
                chess.ROOK: self.rook_table,
                chess.QUEEN: self.queen_table,
                chess.KING: self.king_mg_table
            }
            
            if piece.piece_type in pst_map:
                pst = pst_map[piece.piece_type]
                
                from_index = self._square_to_table_index(move.from_square, piece.color)
                to_index = self._square_to_table_index(move.to_square, piece.color)
                
                evaluation['pst_change'] = pst[to_index] - pst[from_index]
        
        # Overall quality score
        quality = evaluation['see_value'] + evaluation['threat_safety'] + evaluation['pst_change']
        
        if evaluation['is_check']:
            quality += 20
            
        evaluation['overall_quality'] = quality
        
        return evaluation

# Test the enhanced evaluation
def test_enhanced_evaluation():
    """Test the enhanced evaluation on the problematic position."""
    eval_system = EnhancedEvaluation()
    
    # Test queen on h8 move
    board = chess.Board("rnb1k3/pp2q3/2pppNpn/8/5P2/P5P1/1PPPP2P/RNBQKB1R b KQq - 0 9")
    
    print("=== Testing Queen to h8 Move ===")
    qh8_move = chess.Move.from_uci("e7h8")  # Queen from e7 to h8
    
    if qh8_move in board.legal_moves:
        move_eval = eval_system.evaluate_move_quality(board, qh8_move)
        print(f"Move evaluation for Qe7-h8:")
        for key, value in move_eval.items():
            print(f"  {key}: {value}")
        
        # Check PST values directly
        queen_table = eval_system.queen_table
        e7_index = eval_system._square_to_table_index(chess.E7, chess.BLACK)
        h8_index = eval_system._square_to_table_index(chess.H8, chess.BLACK)
        
        print(f"\\nPST Analysis:")
        print(f"  e7 PST value: {queen_table[e7_index]}")
        print(f"  h8 PST value: {queen_table[h8_index]}")
        print(f"  PST change: {queen_table[h8_index] - queen_table[e7_index]}")
    
    print("Enhanced evaluation test complete")

if __name__ == "__main__":
    test_enhanced_evaluation()

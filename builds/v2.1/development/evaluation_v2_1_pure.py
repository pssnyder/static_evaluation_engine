"""
Cece v2.1 - Pure Evaluation Focus
=================================

This version strips back to PURE EVALUATION ONLY and fixes the specific issues:
1. Move repetition (knight-only development, rook shuffling)
2. Material handling (bad captures, piece placement)
3. Development prioritization

NO search complexity - pure evaluation scores only.
"""

import chess
from typing import Dict, Optional, Any, List

class Evaluation:
    """
    Pure evaluation-only engine focused on scoring positions correctly.
    
    Key fixes:
    - Proper development scoring (penalty for undeveloped, bonus for developed)
    - Strong piece placement evaluation
    - Simple but accurate material assessment
    - No complex search logic - just position scoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize pure evaluation system."""
        
        # Base piece values (centipawns)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 315,  # Slightly higher than knight
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Development tracking weights
        self.development_bonus = 50        # Per developed piece in opening
        self.undeveloped_penalty = 80      # Per undeveloped piece after move 8
        self.repeat_move_penalty = 120     # Moving same piece multiple times early
        self.central_control_bonus = 30    # Controlling center squares
        
        # Material safety weights
        self.hanging_piece_penalty = 400   # Stronger penalty for hanging pieces
        self.capture_safety_bonus = 50     # Safe capture available
        
        # Initialize PSTs focused on good development
        self._init_development_focused_psts()
    
    def evaluate(self, board: chess.Board) -> int:
        """
        Main evaluation - returns single score for position.
        
        Returns score from perspective of side to move.
        """
        if board.is_checkmate():
            return -20000 if board.turn == chess.WHITE else 20000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        # Core evaluation components
        material_score = self._evaluate_material_simple(board)
        development_score = self._evaluate_development_properly(board)  
        placement_score = self._evaluate_piece_placement(board)
        safety_score = self._evaluate_piece_safety(board)
        
        # Simple weighted sum
        total_score = (
            material_score * 1.0 +     # Material is most important
            development_score * 0.8 +   # Development critical in opening
            placement_score * 0.6 +     # Good piece placement
            safety_score * 0.9          # Don't hang pieces!
        )
        
        # Return from perspective of side to move
        return int(total_score) if board.turn == chess.WHITE else int(-total_score)
    
    def _evaluate_material_simple(self, board: chess.Board) -> int:
        """Simple, accurate material counting."""
        material_balance = 0
        
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            material_balance += (white_count - black_count) * self.piece_values[piece_type]
        
        return material_balance
    
    def _evaluate_development_properly(self, board: chess.Board) -> int:
        """FIX: Proper development evaluation - reward developed pieces!"""
        development_score = 0
        move_count = board.fullmove_number
        
        # Only apply development rules in opening/early middlegame
        if move_count > 15:
            return 0
        
        # Check development for both sides
        white_dev = self._calculate_side_development(board, chess.WHITE, move_count)
        black_dev = self._calculate_side_development(board, chess.BLACK, move_count)
        
        development_score = white_dev - black_dev
        return development_score
    
    def _calculate_side_development(self, board: chess.Board, color: chess.Color, move_count: int) -> int:
        """Calculate development score for one side."""
        dev_score = 0
        
        # Starting squares for pieces
        if color == chess.WHITE:
            knight_starts = [chess.B1, chess.G1]
            bishop_starts = [chess.C1, chess.F1]
            king_start = chess.E1
            queen_start = chess.D1
        else:
            knight_starts = [chess.B8, chess.G8]
            bishop_starts = [chess.C8, chess.F8]
            king_start = chess.E8
            queen_start = chess.D8
        
        # Count developed minor pieces (REWARD for developing!)
        knights = board.pieces(chess.KNIGHT, color)
        developed_knights = 0
        for knight_square in knights:
            if knight_square not in knight_starts:
                developed_knights += 1
                dev_score += self.development_bonus  # BONUS for development
        
        bishops = board.pieces(chess.BISHOP, color)
        developed_bishops = 0
        for bishop_square in bishops:
            if bishop_square not in bishop_starts:
                developed_bishops += 1
                dev_score += self.development_bonus  # BONUS for development
        
        # PENALTY for undeveloped pieces after move 8
        if move_count >= 8:
            undeveloped_knights = sum(1 for sq in knight_starts if sq in knights)
            undeveloped_bishops = sum(1 for sq in bishop_starts if sq in bishops)
            
            dev_score -= (undeveloped_knights + undeveloped_bishops) * self.undeveloped_penalty
        
        # PENALTY for early queen development
        queens = board.pieces(chess.QUEEN, color)
        if queens and move_count <= 8:
            queen_square = list(queens)[0]
            if queen_square != queen_start:
                dev_score -= 100  # Strong penalty for early queen
        
        # BONUS for castling
        king_pieces = board.pieces(chess.KING, color)
        if king_pieces and move_count >= 6:
            king_square = list(king_pieces)[0]
            if color == chess.WHITE and king_square in [chess.G1, chess.C1]:
                dev_score += 60  # Castled bonus
            elif color == chess.BLACK and king_square in [chess.G8, chess.C8]:
                dev_score += 60  # Castled bonus
            elif king_square == king_start and move_count >= 12:
                dev_score -= 80  # Penalty for not castling late
        
        return dev_score
    
    def _evaluate_piece_placement(self, board: chess.Board) -> int:
        """Evaluate piece placement using simplified PSTs."""
        placement_score = 0
        game_phase = self._get_game_phase(board)
        
        # Apply PST scores for both sides
        white_placement = self._calculate_side_placement(board, chess.WHITE, game_phase)
        black_placement = self._calculate_side_placement(board, chess.BLACK, game_phase)
        
        placement_score = white_placement - black_placement
        return placement_score
    
    def _calculate_side_placement(self, board: chess.Board, color: chess.Color, game_phase: str) -> int:
        """Calculate placement score for one side."""
        placement_score = 0
        
        # Choose appropriate PSTs based on game phase
        if game_phase == "opening":
            knight_table = self.knight_development_table
        else:
            knight_table = self.knight_table
        
        # Apply PST scores
        piece_tables = {
            chess.PAWN: self.pawn_table,
            chess.KNIGHT: knight_table,
            chess.BISHOP: self.bishop_table,
            chess.ROOK: self.rook_table,
            chess.QUEEN: self.queen_table,
            chess.KING: self.king_table
        }
        
        for piece_type, table in piece_tables.items():
            pieces = board.pieces(piece_type, color)
            for square in pieces:
                table_index = self._square_to_table_index(square, color)
                placement_score += table[table_index]
        
        return placement_score
    
    def _evaluate_piece_safety(self, board: chess.Board) -> int:
        """Evaluate piece safety - prevent hanging pieces and bad captures."""
        safety_score = 0
        
        # Check both sides for hanging pieces
        white_hanging = self._find_hanging_pieces_simple(board, chess.WHITE)
        black_hanging = self._find_hanging_pieces_simple(board, chess.BLACK)
        
        safety_score = black_hanging - white_hanging  # Opponent hanging = good for us
        
        return safety_score
    
    def _find_hanging_pieces_simple(self, board: chess.Board, color: chess.Color) -> int:
        """Simple hanging piece detection."""
        hanging_value = 0
        
        for piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
            pieces = board.pieces(piece_type, color)
            
            for square in pieces:
                # Check if piece is attacked by lower-value enemy pieces
                if board.is_attacked_by(not color, square):
                    # Check if adequately defended
                    if not self._is_adequately_defended(board, square, color):
                        hanging_value += self.piece_values[piece_type]
        
        return hanging_value
    
    def _is_adequately_defended(self, board: chess.Board, square: chess.Square, color: chess.Color) -> bool:
        """Check if a square is adequately defended."""
        piece = board.piece_at(square)
        if not piece:
            return True
        
        # Count attackers vs defenders
        attackers = 0
        defenders = 0
        
        for sq in chess.SQUARES:
            piece_on_sq = board.piece_at(sq)
            if piece_on_sq and square in board.attacks(sq):
                if piece_on_sq.color != color:
                    attackers += 1
                elif piece_on_sq.color == color and sq != square:
                    defenders += 1
        
        return defenders >= attackers
    
    def _get_game_phase(self, board: chess.Board) -> str:
        """Simple game phase detection."""
        move_count = board.fullmove_number
        piece_count = len(board.piece_map())
        
        if move_count <= 12 or piece_count >= 28:
            return "opening"
        elif piece_count >= 16:
            return "middlegame"
        else:
            return "endgame"
    
    def _square_to_table_index(self, square: chess.Square, color: chess.Color) -> int:
        """Convert square to PST index."""
        if color == chess.WHITE:
            return square ^ 56  # Flip for white
        else:
            return square
    
    def _init_development_focused_psts(self):
        """Initialize PSTs that encourage proper development."""
        
        # Pawn table - encourage central control
        self.pawn_table = [
             0,   0,   0,   0,   0,   0,   0,   0,  # 8th rank
            80,  80,  80,  80,  80,  80,  80,  80,  # 7th rank
            30,  30,  40,  50,  50,  40,  30,  30,  # 6th rank
            20,  20,  25,  40,  40,  25,  20,  20,  # 5th rank
            15,  15,  20,  35,  35,  20,  15,  15,  # 4th rank
            10,  10,  15,  25,  25,  15,  10,  10,  # 3rd rank
             5,  10,  10, -20, -20,  10,  10,   5,  # 2nd rank
             0,   0,   0,   0,   0,   0,   0,   0   # 1st rank
        ]
        
        # Knight development table - EXTREME penalties for rim/corner
        self.knight_development_table = [
            -200, -150, -100,  -50,  -50, -100, -150, -200,  # 8th rank - stay away!
            -150,  -80,  -40,   -20,  -20,  -40,  -80, -150,  # 7th rank
            -100,  -40,   30,    50,   50,   30,  -40, -100,  # 6th rank - good development
             -50,  -20,   50,    70,   70,   50,  -20,  -50,  # 5th rank - excellent
             -50,  -20,   50,    70,   70,   50,  -20,  -50,  # 4th rank - excellent
            -100,  -40,   30,    50,   50,   30,  -40, -100,  # 3rd rank - good development
            -150,  -80,  -40,   -20,  -20,  -40,  -80, -150,  # 2nd rank
            -200, -150, -100,   -50,  -50, -100, -150, -200   # 1st rank - starting pos penalty
        ]
        
        # Regular knight table for middlegame/endgame
        self.knight_table = [
            -50, -30, -20, -15, -15, -20, -30, -50,
            -30, -10,   5,  10,  10,   5, -10, -30,
            -20,   5,  20,  25,  25,  20,   5, -20,
            -15,  10,  25,  30,  30,  25,  10, -15,
            -15,  10,  25,  30,  30,  25,  10, -15,
            -20,   5,  20,  25,  25,  20,   5, -20,
            -30, -10,   5,  10,  10,   5, -10, -30,
            -50, -30, -20, -15, -15, -20, -30, -50
        ]
        
        # Bishop table - encourage long diagonals
        self.bishop_table = [
            -20, -15, -15, -15, -15, -15, -15, -20,
            -15,   0,   5,   5,   5,   5,   0, -15,
            -15,   5,  10,  15,  15,  10,   5, -15,
            -15,   5,  15,  20,  20,  15,   5, -15,
            -15,   5,  15,  20,  20,  15,   5, -15,
            -15,  10,  15,  15,  15,  15,  10, -15,
            -15,   5,   0,   0,   0,   0,   5, -15,
            -20, -15, -25, -15, -15, -25, -15, -20
        ]
        
        # Rook table - encourage central files and 7th rank
        self.rook_table = [
             0,   0,   5,   5,   5,   5,   0,   0,
            10,  15,  15,  15,  15,  15,  15,  10,  # 7th rank bonus
             0,   0,   5,   5,   5,   5,   0,   0,
             0,   0,   5,   5,   5,   5,   0,   0,
             0,   0,   5,   5,   5,   5,   0,   0,
             0,   0,   5,   5,   5,   5,   0,   0,
             0,   5,   5,  10,  10,   5,   5,   0,
             0,   0,   0,  10,  10,   0,   0,   0
        ]
        
        # Queen table - STRONG corner penalties, modest center preference
        self.queen_table = [
            -30, -20, -15, -10, -10, -15, -20, -30,
            -20, -10,  -5,   0,   0,  -5, -10, -20,
            -15,  -5,   5,  10,  10,   5,  -5, -15,
            -10,   0,  10,  15,  15,  10,   0, -10,
            -10,   0,  10,  15,  15,  10,   0, -10,
            -15,  -5,   5,  10,  10,   5,  -5, -15,
            -20, -10,  -5,   0,   0,  -5, -10, -20,
            -30, -20, -15, -10, -10, -15, -20, -30
        ]
        
        # King table - encourage castling
        self.king_table = [
            -50, -40, -40, -50, -50, -40, -40, -50,
            -40, -40, -40, -40, -40, -40, -40, -40,
            -40, -40, -40, -40, -40, -40, -40, -40,
            -40, -40, -40, -40, -40, -40, -40, -40,
            -30, -30, -30, -30, -30, -30, -30, -30,
            -20, -20, -20, -20, -20, -20, -20, -20,
             10,  10,  -5,  -5,  -5,  -5,  10,  10,  # Castled position bonus
             10,  20,   5,  -5,  -5,   5,  20,  10
        ]

# Helper function for compatibility with existing engine
def create_evaluator(config: Optional[Dict[str, Any]] = None) -> Evaluation:
    """Create an evaluator instance."""
    return Evaluation(config)

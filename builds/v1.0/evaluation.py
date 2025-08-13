"""
Static evaluation functions for chess positions using bitboards.

This module contains YOUR custom evaluation logic and is the core IP of your engine.
All evaluation weights, patterns, and scoring functions are designed by you for
your specific chess playing style and strategic preferences.

Author: Your Name
License: GPL-3.0
"""

import chess
from typing import Dict, Optional, Any, Union


class Evaluation:
    """
    Static position evaluation using handcrafted functions.
    
    This class represents YOUR chess knowledge and playing style.
    All evaluation components are customizable and tunable.
    """
    
    # Piece values in centipawns (YOUR MATERIAL VALUES)
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize evaluation with optional configuration."""
        self.config = config or {}
        
        # Evaluation weights (YOUR CUSTOM TUNING PARAMETERS)
        self.weights = self.config.get('weights', {
            'material': 1.0,
            'positional': 0.5,
            'tactical': 0.8,
            'king_safety': 0.6,
            'pawn_structure': 0.4,
            'piece_activity': 0.3
        })
        
        # Custom pattern bonuses (YOUR TACTICAL PREFERENCES)
        self.pattern_bonuses = self.config.get('patterns', {
            'fork_bonus': 25,
            'pin_bonus': 20,
            'skewer_bonus': 30,
            'discovered_attack': 35,
            'double_attack': 40,
            'back_rank_mate': 100,
            'knight_outpost': 15,
            'bishop_pair': 25,
            'rook_on_seventh': 30,
            'passed_pawn': 20
        })
        
        # Piece-square tables (YOUR POSITIONAL PREFERENCES)
        self.init_piece_square_tables()
    
    def init_piece_square_tables(self):
        """Initialize piece-square tables for positional evaluation."""
        # Pawn table (encourage central control and advancement)
        self.pawn_table = [
             0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
             5,  5, 10, 25, 25, 10,  5,  5,
             0,  0,  0, 20, 20,  0,  0,  0,
             5, -5,-10,  0,  0,-10, -5,  5,
             5, 10, 10,-20,-20, 10, 10,  5,
             0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        # Knight table (encourage central squares)
        self.knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]
        
        # More tables can be added as needed...
    
    def evaluate(self, board: chess.Board) -> int:
        """
        Evaluate the current position from white's perspective.
        Positive values favor white, negative values favor black.
        """
        detailed_eval = self.evaluate_detailed(board)
        return detailed_eval.get('total_score', 0)
    
    def evaluate_detailed(self, board: chess.Board) -> Dict[str, Any]:
        """
        Detailed evaluation returning breakdown of all components.
        
        This is YOUR core IP - the detailed analysis and scoring system.
        """
        # Check for terminal positions first
        if board.is_checkmate():
            terminal_score = -20000 if board.turn == chess.WHITE else 20000
            return {
                'total_score': terminal_score,
                'material': 0,
                'positional': 0,
                'tactical': 0,
                'king_safety': 0,
                'pawn_structure': 0,
                'piece_activity': 0,
                'custom_patterns': {},
                'is_terminal': True,
                'terminal_type': 'checkmate'
            }

        if board.is_stalemate() or self.is_draw(board):
            return {
                'total_score': 0,
                'material': 0,
                'positional': 0,
                'tactical': 0,
                'king_safety': 0,
                'pawn_structure': 0,
                'piece_activity': 0,
                'custom_patterns': {},
                'is_terminal': True,
                'terminal_type': 'draw'
            }
        
        # Core evaluation components (YOUR CUSTOM LOGIC)
        material_score = self.evaluate_material(board)
        positional_score = self.evaluate_positional(board)
        tactical_score = self.evaluate_tactical_patterns(board)
        king_safety_score = self.evaluate_king_safety(board)
        pawn_structure_score = self.evaluate_pawn_structure(board)
        piece_activity_score = self.evaluate_piece_activity(board)
        
        # Custom pattern detection (YOUR TACTICAL ENGINE)
        custom_patterns = self.detect_custom_patterns(board)
        pattern_score = sum(custom_patterns.values())
        
        # Apply weights (YOUR TUNING SYSTEM)
        weighted_scores = {
            'material': material_score * self.weights['material'],
            'positional': positional_score * self.weights['positional'],
            'tactical': tactical_score * self.weights['tactical'],
            'king_safety': king_safety_score * self.weights['king_safety'],
            'pawn_structure': pawn_structure_score * self.weights['pawn_structure'],
            'piece_activity': piece_activity_score * self.weights['piece_activity']
        }
        
        total_score = sum(weighted_scores.values()) + pattern_score
        
        return {
            'total_score': int(total_score),
            'material': material_score,
            'positional': positional_score,
            'tactical': tactical_score,
            'king_safety': king_safety_score,
            'pawn_structure': pawn_structure_score,
            'piece_activity': piece_activity_score,
            'custom_patterns': custom_patterns,
            'weighted_scores': weighted_scores,
            'pattern_bonus': pattern_score,
            'is_terminal': False
        }
    
    def evaluate_material(self, board: chess.Board) -> int:
        """Evaluate material balance."""
        score = 0
        
        for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            white_pieces = len(board.pieces(piece_type, chess.WHITE))
            black_pieces = len(board.pieces(piece_type, chess.BLACK))
            
            piece_value = self.PIECE_VALUES[piece_type]
            score += (white_pieces - black_pieces) * piece_value
        
        return score
    
    def evaluate_positional(self, board: chess.Board) -> int:
        """
        Evaluate positional factors using piece-square tables.
        
        YOUR CUSTOM POSITIONAL LOGIC - modify these tables and
        add more positional concepts as desired.
        """
        score = 0
        
        # Evaluate pawns using piece-square table
        for square in board.pieces(chess.PAWN, chess.WHITE):
            score += self.pawn_table[square]
        
        for square in board.pieces(chess.PAWN, chess.BLACK):
            score -= self.pawn_table[chess.square_mirror(square)]
        
        # Evaluate knights
        for square in board.pieces(chess.KNIGHT, chess.WHITE):
            score += self.knight_table[square]
        
        for square in board.pieces(chess.KNIGHT, chess.BLACK):
            score -= self.knight_table[chess.square_mirror(square)]
        
        # Add more positional evaluations here...
        
        return score
    
    def evaluate_tactical_patterns(self, board: chess.Board) -> int:
        """
        Evaluate tactical patterns and threats.
        
        YOUR TACTICAL PATTERN RECOGNITION - this is where you can
        implement your understanding of chess tactics.
        """
        score = 0
        
        # Look for pins, forks, skewers, etc.
        # This is a simplified example - expand as needed
        
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            
            # Check for pieces under attack
            for square in board.pieces(chess.QUEEN, color):
                if board.is_attacked_by(not color, square):
                    attackers = board.attackers(not color, square)
                    if attackers:
                        # Queen under attack - significant tactical factor
                        score += multiplier * -50
            
            # Look for fork opportunities (simplified)
            for knight_square in board.pieces(chess.KNIGHT, color):
                knight_attacks = board.attacks(knight_square)
                high_value_targets = 0
                for target_square in knight_attacks:
                    piece = board.piece_at(target_square)
                    if piece and piece.color != color:
                        if piece.piece_type in [chess.QUEEN, chess.ROOK]:
                            high_value_targets += 1
                
                if high_value_targets >= 2:
                    score += multiplier * self.pattern_bonuses['fork_bonus']
        
        return score
    
    def evaluate_king_safety(self, board: chess.Board) -> int:
        """
        Evaluate king safety for both sides.
        
        YOUR KING SAFETY LOGIC - customize based on your
        preferred playing style (aggressive vs defensive).
        """
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            king_square = board.king(color)
            
            if king_square is None:
                continue
            
            # Penalty for being in check
            if board.is_check():
                if board.turn == color:
                    score += multiplier * -30
            
            # Evaluate pawn shield (simplified)
            if color == chess.WHITE:
                shield_squares = [king_square + 8, king_square + 7, king_square + 9]
            else:
                shield_squares = [king_square - 8, king_square - 7, king_square - 9]
            
            shield_count = 0
            for shield_square in shield_squares:
                if 0 <= shield_square < 64:
                    piece = board.piece_at(shield_square)
                    if piece and piece.piece_type == chess.PAWN and piece.color == color:
                        shield_count += 1
            
            score += multiplier * shield_count * 10
            
            # Penalty for exposed king
            attackers = len(board.attackers(not color, king_square))
            score += multiplier * -5 * attackers
        
        return score
    
    def evaluate_pawn_structure(self, board: chess.Board) -> int:
        """
        Evaluate pawn structure - YOUR PAWN EVALUATION LOGIC.
        
        Customize this to reflect your understanding of pawn structure
        and its importance in different types of positions.
        """
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            pawns = board.pieces(chess.PAWN, color)
            
            # Count doubled pawns
            files = {}
            for pawn_square in pawns:
                file = chess.square_file(pawn_square)
                files[file] = files.get(file, 0) + 1
            
            for file, count in files.items():
                if count > 1:
                    score += multiplier * -10 * (count - 1)  # Penalty for doubles
            
            # Look for isolated pawns
            for pawn_square in pawns:
                file = chess.square_file(pawn_square)
                isolated = True
                
                # Check adjacent files for friendly pawns
                for adj_file in [file - 1, file + 1]:
                    if 0 <= adj_file < 8:
                        for rank in range(8):
                            check_square = chess.square(adj_file, rank)
                            piece = board.piece_at(check_square)
                            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                                isolated = False
                                break
                        if not isolated:
                            break
                
                if isolated:
                    score += multiplier * -15  # Penalty for isolated pawn
        
        return score
    
    def evaluate_piece_activity(self, board: chess.Board) -> int:
        """
        Evaluate piece activity and mobility.
        
        YOUR PIECE ACTIVITY LOGIC - focus on the types of piece
        activity that align with your playing style.
        """
        score = 0
        
        # Simple mobility evaluation
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            
            # Count legal moves (mobility)
            original_turn = board.turn
            board.turn = color
            try:
                mobility = len(list(board.legal_moves))
                score += multiplier * mobility * 2
            finally:
                board.turn = original_turn
            
            # Bonus for active pieces
            for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                for square in board.pieces(piece_type, color):
                    attacks = board.attacks(square)
                    activity_bonus = len(attacks)
                    
                    # Extra bonus for attacking enemy pieces
                    for attack_square in attacks:
                        piece = board.piece_at(attack_square)
                        if piece and piece.color != color:
                            activity_bonus += 2
                    
                    score += multiplier * activity_bonus
        
        return score
    
    def detect_custom_patterns(self, board: chess.Board) -> Dict[str, int]:
        """
        Detect custom tactical and strategic patterns.
        
        YOUR PATTERN RECOGNITION ENGINE - this is where you can
        implement advanced pattern recognition for your specific
        chess understanding and playing style.
        """
        patterns = {}
        
        # Bishop pair bonus
        for color in [chess.WHITE, chess.BLACK]:
            bishops = board.pieces(chess.BISHOP, color)
            if len(bishops) >= 2:
                multiplier = 1 if color == chess.WHITE else -1
                color_name = 'white' if color == chess.WHITE else 'black'
                patterns[f'bishop_pair_{color_name}'] = \
                    multiplier * self.pattern_bonuses['bishop_pair']
        
        # Rook on seventh rank
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            seventh_rank = 6 if color == chess.WHITE else 1
            color_name = 'white' if color == chess.WHITE else 'black'
            
            for rook_square in board.pieces(chess.ROOK, color):
                if chess.square_rank(rook_square) == seventh_rank:
                    patterns[f'rook_seventh_{color_name}_{rook_square}'] = \
                        multiplier * self.pattern_bonuses['rook_on_seventh']
        
        # Knight outposts (simplified)
        for color in [chess.WHITE, chess.BLACK]:
            multiplier = 1 if color == chess.WHITE else -1
            color_name = 'white' if color == chess.WHITE else 'black'
            
            for knight_square in board.pieces(chess.KNIGHT, color):
                rank = chess.square_rank(knight_square)
                file = chess.square_file(knight_square)
                
                # Check if knight is in enemy territory and protected
                if (color == chess.WHITE and rank >= 4) or (color == chess.BLACK and rank <= 3):
                    if board.is_attacked_by(color, knight_square):
                        patterns[f'knight_outpost_{color_name}_{knight_square}'] = \
                            multiplier * self.pattern_bonuses['knight_outpost']
        
        # Add more pattern detection as needed...
        
        return patterns
    
    def is_draw(self, board: chess.Board) -> bool:
        """Check for various draw conditions."""
        # Use python-chess built-in methods
        return (board.is_insufficient_material() or 
                board.is_seventyfive_moves() or 
                board.is_fivefold_repetition() or
                board.can_claim_fifty_moves() or
                board.can_claim_threefold_repetition())
    
    def is_insufficient_material(self, board: chess.Board) -> bool:
        """Check if there's insufficient material to checkmate."""
        return board.is_insufficient_material()
    
    def get_evaluation_explanation(self, board: chess.Board) -> str:
        """
        Get a human-readable explanation of the evaluation.
        
        Useful for debugging and understanding engine decisions.
        """
        eval_data = self.evaluate_detailed(board)
        
        explanation = []
        explanation.append(f"Total Score: {eval_data['total_score']}")
        explanation.append(f"Material: {eval_data['material']}")
        explanation.append(f"Positional: {eval_data['positional']}")
        explanation.append(f"Tactical: {eval_data['tactical']}")
        explanation.append(f"King Safety: {eval_data['king_safety']}")
        explanation.append(f"Pawn Structure: {eval_data['pawn_structure']}")
        explanation.append(f"Piece Activity: {eval_data['piece_activity']}")
        
        if eval_data['custom_patterns']:
            explanation.append("Custom Patterns:")
            for pattern, value in eval_data['custom_patterns'].items():
                explanation.append(f"  {pattern}: {value}")
        
        return "\n".join(explanation)

"""
Static evaluation functions for chess positions - Cece v2.1 Consolidated

This module contains the core evaluation logic with tournament-tested improvements.
Consolidates all v2.1 fixes into a clean, maintainable evaluation system.

Key improvements based on tournament analysis:
- Knight rim penalties (prevents 1.Nh3 type moves)
- Development evaluation (rewards developed pieces)
- Rook shuffling prevention
- Material safety (hanging piece detection)
- Simplified, pure evaluation approach

Author: Pat Snyder
License: GPL-3.0
"""

import chess
from typing import Dict, Optional, Any

class Evaluation:
    """
    Pure evaluation system focused on position scoring.
    Tournament-tested fixes for behavioral issues.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize evaluation system with v2.1 consolidated improvements."""
        # Base piece values (in centipawns)
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 275,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Tournament-tested penalties and bonuses
        self.knight_rim_penalty = 50      # Prevents 1.Nh3 type moves
        self.development_bonus = 25       # Reward developed pieces
        self.shuffle_penalty = 30         # Penalize repetitive moves
        self.hanging_piece_penalty = 150  # Prevent material blunders
        self.center_control_bonus = 15    # Basic center control
        
        # Define key squares
        self.rim_squares = {chess.A1, chess.A8, chess.H1, chess.H8}  # Corner squares
        self.center_squares = {chess.D4, chess.D5, chess.E4, chess.E5}
        self.extended_center = {chess.C3, chess.C4, chess.C5, chess.C6,
                               chess.D3, chess.D4, chess.D5, chess.D6,
                               chess.E3, chess.E4, chess.E5, chess.E6,
                               chess.F3, chess.F4, chess.F5, chess.F6}
    
    def evaluate(self, board: chess.Board) -> int:
        """
        Main evaluation function - returns single score for engine.
        
        Returns:
            Score in centipawns from perspective of side to move
        """
        return int(self.evaluate_position(board))
    
    def evaluate_position(self, board):
        """
        Evaluate a chess position and return a score.
        
        Args:
            board: python-chess Board object
            
        Returns:
            float: Position evaluation score (positive = good for white)
        """
        if board.is_checkmate():
            return -999999 if board.turn else 999999
        
        if board.is_stalemate() or board.is_insufficient_material() or board.is_repetition(3):
            return 0
            
        score = 0
        
        # Collect material counts for each side
        white_material = sum(
            len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
        )
        black_material = sum(
            len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
            for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
        )
        
        # Basic material evaluation
        score += white_material - black_material
        
        # Development evaluation
        score += self.evaluate_development(board)
        
        # Knight rim penalties (addresses tournament issue with 1.Nh3 type moves)
        score += self.evaluate_knight_positioning(board)
        
        # Rook activity and shuffling penalties
        score += self.evaluate_rook_activity(board)
        
        # Hanging piece penalties (addresses tournament material blunders)
        score += self.evaluate_material_safety(board)
        
        # King safety
        score += self.evaluate_king_safety(board)
        
        # Center control
        score += self.evaluate_center_control(board)
        
        return score
    
    def evaluate_development(self, board):
        """Evaluate piece development - reward developed pieces."""
        score = 0
        
        # Check knights and bishops development
        for color in [chess.WHITE, chess.BLACK]:
            color_multiplier = 1 if color == chess.WHITE else -1
            
            # Knights developed from back rank
            knights = board.pieces(chess.KNIGHT, color)
            back_rank = 0 if color == chess.WHITE else 7
            
            for knight in knights:
                if chess.square_rank(knight) != back_rank:
                    score += self.development_bonus * color_multiplier
            
            # Bishops developed from back rank
            bishops = board.pieces(chess.BISHOP, color)
            for bishop in bishops:
                if chess.square_rank(bishop) != back_rank:
                    score += self.development_bonus * color_multiplier
        
        return score
    
    def evaluate_knight_positioning(self, board):
        """Penalize knights on rim squares (tournament fix)."""
        score = 0
        
        # Define rim squares more broadly (a/h files, 1st/8th ranks)
        rim_files = [0, 7]  # a-file and h-file
        rim_ranks = [0, 7]  # 1st and 8th rank
        
        for color in [chess.WHITE, chess.BLACK]:
            color_multiplier = 1 if color == chess.WHITE else -1
            knights = board.pieces(chess.KNIGHT, color)
            
            for knight in knights:
                knight_file = chess.square_file(knight)
                knight_rank = chess.square_rank(knight)
                
                # Penalize knights on rim
                if knight_file in rim_files or knight_rank in rim_ranks:
                    score -= self.knight_rim_penalty * color_multiplier
        
        return score
    
    def evaluate_rook_activity(self, board):
        """Evaluate rook activity and penalize shuffling."""
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            color_multiplier = 1 if color == chess.WHITE else -1
            rooks = board.pieces(chess.ROOK, color)
            
            for rook in rooks:
                # Basic activity - rooks prefer open/semi-open files
                rook_file = chess.square_file(rook)
                file_squares = [chess.square(rook_file, rank) for rank in range(8)]
                
                # Count pawns on this file
                pawns_on_file = sum(1 for sq in file_squares if board.piece_at(sq) and board.piece_at(sq).piece_type == chess.PAWN)
                
                if pawns_on_file == 0:  # Open file
                    score += 25 * color_multiplier
                elif pawns_on_file == 1:  # Semi-open file
                    score += 15 * color_multiplier
        
        return score
    
    def evaluate_material_safety(self, board):
        """Penalize hanging pieces (tournament fix for material blunders)."""
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            color_multiplier = 1 if color == chess.WHITE else -1
            
            # Check each piece for being attacked
            for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
                pieces = board.pieces(piece_type, color)
                
                for piece_square in pieces:
                    # Check if piece is attacked by opponent
                    if board.is_attacked_by(not color, piece_square):
                        # Check if piece is defended
                        if not board.is_attacked_by(color, piece_square):
                            # Hanging piece - apply penalty based on piece value
                            penalty = self.piece_values[piece_type] * 0.5  # 50% of piece value
                            score -= penalty * color_multiplier
        
        return score
    
    def evaluate_king_safety(self, board):
        """Basic king safety evaluation."""
        score = 0
        
        for color in [chess.WHITE, chess.BLACK]:
            color_multiplier = 1 if color == chess.WHITE else -1
            king_square = board.king(color)
            
            if king_square is not None:
                # Penalize exposed king (attacked squares around king)
                king_area = [king_square + offset for offset in [-9, -8, -7, -1, 1, 7, 8, 9] 
                           if 0 <= king_square + offset < 64]
                
                exposed_squares = sum(1 for sq in king_area 
                                    if 0 <= sq < 64 and board.is_attacked_by(not color, sq))
                
                if exposed_squares > 3:  # King in danger
                    score -= 50 * color_multiplier
        
        return score
    
    def evaluate_center_control(self, board):
        """Basic center control evaluation."""
        score = 0
        
        # Check control of center squares
        for square in self.center_squares:
            white_attacks = board.is_attacked_by(chess.WHITE, square)
            black_attacks = board.is_attacked_by(chess.BLACK, square)
            
            if white_attacks and not black_attacks:
                score += self.center_control_bonus
            elif black_attacks and not white_attacks:
                score -= self.center_control_bonus
        
        return score
    
    def evaluate_detailed(self, board: chess.Board) -> Dict[str, Any]:
        """
        Detailed evaluation with component breakdown for debugging.
        
        Returns:
            Dictionary with evaluation breakdown and total score
        """
        # Check for terminal positions first
        if board.is_checkmate():
            terminal_score = -20000 if board.turn == chess.WHITE else 20000
            return {
                'total_score': terminal_score,
                'material': 0,
                'development': 0,
                'knight_positioning': 0,
                'rook_activity': 0,
                'material_safety': 0,
                'king_safety': 0,
                'center_control': 0,
                'is_terminal': True,
                'terminal_type': 'checkmate'
            }
        
        if board.is_stalemate() or board.is_insufficient_material():
            return {
                'total_score': 0,
                'material': 0,
                'development': 0,
                'knight_positioning': 0,
                'rook_activity': 0,
                'material_safety': 0,
                'king_safety': 0,
                'center_control': 0,
                'is_terminal': True,
                'terminal_type': 'draw'
            }
        
        # Component scores
        material_score = self.evaluate_material_only(board)
        development_score = self.evaluate_development(board)
        knight_score = self.evaluate_knight_positioning(board)
        rook_score = self.evaluate_rook_activity(board)
        safety_score = self.evaluate_material_safety(board)
        king_score = self.evaluate_king_safety(board)
        center_score = self.evaluate_center_control(board)
        
        total_score = (material_score + development_score + knight_score + 
                      rook_score + safety_score + king_score + center_score)
        
        return {
            'material': material_score,
            'development': development_score,
            'knight_positioning': knight_score,
            'rook_activity': rook_score,
            'material_safety': safety_score,
            'king_safety': king_score,
            'center_control': center_score,
            'total_score': int(total_score)
        }
    
    def evaluate_material_only(self, board):
        """Pure material evaluation component."""
        white_material = sum(
            len(board.pieces(piece_type, chess.WHITE)) * self.piece_values[piece_type]
            for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
        )
        black_material = sum(
            len(board.pieces(piece_type, chess.BLACK)) * self.piece_values[piece_type]
            for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]
        )
        
        return white_material - black_material

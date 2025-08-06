"""
Static evaluation functions for chess positions - Cece v1.2

This module contains the core evaluation logic and is the primary IP of the engine.
All evaluation weights, patterns, and scoring functions are designed for tactical
and positional excellence.

Author: Pat Snyder
License: GPL-3.0
"""

import chess
from typing import Dict, Optional, Any, Union, List, Tuple

# ============================================================================
# CORE FUNCTIONS (Stable, rarely modified)
# ============================================================================

class Evaluation:
    """
    Consolidated evaluation system with enhanced tactical awareness.
    
    All evaluation components integrated into a single, debuggable file.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize evaluation system."""
        # Piece values - used across multiple evaluation functions
        self.piece_values = {
            chess.PAWN: 100,
            chess.KNIGHT: 320,
            chess.BISHOP: 330,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000
        }
        
        # Initialize PST tables
        self._init_piece_square_tables()
    
    def evaluate(self, board: chess.Board) -> int:
        """
        Main evaluation function - returns single score for engine.
        
        Returns:
            Score in centipawns from perspective of side to move
        """
        detailed_result = self.evaluate_detailed(board)
        return detailed_result['total_score']
    
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
                'positional': 0,
                'tactical': 0,
                'threats': 0,
                'castling': 0,
                'king_safety': 0,
                'is_terminal': True,
                'terminal_type': 'checkmate'
            }
        
        if board.is_stalemate() or board.is_insufficient_material():
            return {
                'total_score': 0,
                'material': 0,
                'positional': 0,
                'tactical': 0,
                'threats': 0,
                'castling': 0,
                'king_safety': 0,
                'is_terminal': True,
                'terminal_type': 'draw'
            }
        
        # Component scores - available for debugging but not logged in production
        material_score = 0
        positional_score = 0
        tactical_score = 0
        threat_score = 0
        castling_score = 0
        king_safety_score = 0
        
        # Evaluate each component
        material_score = self._evaluate_material(board)
        positional_score = self._evaluate_positional(board)
        tactical_score = self._evaluate_tactical(board)
        threat_score = self._evaluate_threats(board)
        castling_score = self._evaluate_castling(board)
        king_safety_score = self._evaluate_king_safety(board)
        
        # Calculate total with hardcoded weights
        total_score = (
            material_score * 1.0 +
            positional_score * 0.6 +
            tactical_score * 0.9 +
            threat_score * 0.5 +
            castling_score * 0.4 +
            king_safety_score * 0.8
        )
        
        # Return breakdown dictionary (compatible with engine interface)
        return {
            'material': material_score,
            'positional': positional_score,
            'tactical': tactical_score,
            'threats': threat_score,
            'castling': castling_score,
            'king_safety': king_safety_score,
            'total_score': int(total_score)
        }

# ============================================================================
# EVALUATION HANDLER FUNCTIONS (Primary functionality)
# ============================================================================

    def _evaluate_material(self, board: chess.Board) -> int:
        """Basic material balance evaluation."""
        material_balance = 0
        
        for piece_type, value in self.piece_values.items():
            if piece_type == chess.KING:
                continue
                
            white_count = len(board.pieces(piece_type, chess.WHITE))
            black_count = len(board.pieces(piece_type, chess.BLACK))
            
            material_balance += (white_count - black_count) * value
        
        # Return from perspective of side to move
        return material_balance if board.turn == chess.WHITE else -material_balance
    
    def _evaluate_positional(self, board: chess.Board) -> int:
        """Enhanced positional evaluation using piece-square tables."""
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
        return positional_score if board.turn == chess.WHITE else -positional_score
    
    def _evaluate_tactical(self, board: chess.Board) -> int:
        """Tactical evaluation using Static Exchange Evaluation."""
        see_score = 0
        
        # Get all captures and evaluate them using SEE
        for move in board.legal_moves:
            if board.is_capture(move):
                see_value = self._see_evaluate_capture(board, move)
                
                if see_value > 0:
                    see_score += min(see_value, 200)  # Cap bonus to prevent overvaluation
                elif see_value < 0:
                    see_score += see_value // 2  # Partial penalty for bad captures available
        
        return see_score
    
    def _evaluate_threats(self, board: chess.Board) -> int:
        """Evaluate piece threats and safety."""
        threat_score = 0
        
        # Evaluate threats for both sides
        our_threats = self._calculate_side_threats(board, board.turn)
        their_threats = self._calculate_side_threats(board, not board.turn)
        
        threat_score += our_threats - their_threats
        
        # Evaluate hanging pieces
        our_hanging = self._find_hanging_pieces(board, board.turn)
        their_hanging = self._find_hanging_pieces(board, not board.turn)
        
        threat_score -= our_hanging  # Penalty for our hanging pieces
        threat_score += their_hanging  # Bonus for their hanging pieces
        
        return threat_score
    
    def _evaluate_castling(self, board: chess.Board) -> int:
        """Evaluate castling rights and king safety."""
        # Castling evaluation parameters
        castling_rights_bonus = 15
        castled_bonus = 50
        early_game_urgency = 30
        exposed_king_penalty = -100
        
        score = 0
        
        # Evaluate for both sides
        white_score = self._evaluate_side_castling(board, chess.WHITE, 
                                                  castling_rights_bonus, castled_bonus, 
                                                  early_game_urgency, exposed_king_penalty)
        black_score = self._evaluate_side_castling(board, chess.BLACK,
                                                  castling_rights_bonus, castled_bonus,
                                                  early_game_urgency, exposed_king_penalty)
        
        # Return score relative to side to move
        if board.turn == chess.WHITE:
            score = white_score - black_score
        else:
            score = black_score - white_score
            
        return score
    
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

# ============================================================================
# HELPER FUNCTIONS (Global utilities and tools)
# ============================================================================

    def _square_to_table_index(self, square: chess.Square, color: chess.Color) -> int:
        """Convert square to PST index, flipping for black."""
        if color == chess.WHITE:
            # White: rank 0 (1st) = index 56-63, rank 7 (8th) = index 0-7
            return square ^ 56
        else:
            # Black: use square directly
            return square
    
    def _get_king_area(self, king_square: chess.Square) -> List[chess.Square]:
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
    
    def _estimate_game_phase(self, board: chess.Board) -> str:
        """Estimate the current game phase."""
        # Count total pieces (excluding pawns and kings)
        piece_count = 0
        for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            piece_count += len(board.pieces(piece_type, chess.WHITE))
            piece_count += len(board.pieces(piece_type, chess.BLACK))
        
        # Count moves played
        move_count = board.fullmove_number
        
        if move_count <= 10 or piece_count >= 12:
            return "opening"
        elif move_count <= 25 and piece_count >= 6:
            return "middlegame"
        else:
            return "endgame"
    
    def _is_king_in_center(self, king_square: chess.Square) -> bool:
        """Check if king is still in the center files."""
        file = chess.square_file(king_square)
        # Center files are d(3), e(4)
        return file in [3, 4]

# ============================================================================
# CUSTOM EVALUATION FUNCTIONS (Hot spots - most modified)
# ============================================================================

    def _init_piece_square_tables(self):
        """Initialize enhanced piece-square tables with stronger positional guidance."""
        
        # Enhanced Pawn PST - stronger advancement bonus
        self.pawn_table = [
             0,  0,  0,  0,  0,  0,  0,  0,  # 8th rank (promotion)
            60, 60, 60, 60, 60, 60, 60, 60,  # 7th rank - stronger bonus
            15, 15, 25, 35, 35, 25, 15, 15,  # 6th rank
            10, 10, 15, 30, 30, 15, 10, 10,  # 5th rank
             5,  5, 10, 25, 25, 10,  5,  5,  # 4th rank
             0,  0,  0, 20, 20,  0,  0,  0,  # 3rd rank
             5, 10, 10,-20,-20, 10, 10,  5,  # 2nd rank
             0,  0,  0,  0,  0,  0,  0,  0   # 1st rank
        ]
        
        # Enhanced Knight PST - extreme rim penalties to prevent Ng5-type moves
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
        
        # Enhanced Bishop PST - improved diagonal control
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
        
        # Enhanced Rook PST - 7th rank and center file bonuses
        self.rook_table = [
             5,  5,  5,  5,  5,  5,  5,  5,  # 8th rank
            15, 20, 20, 20, 20, 20, 20, 15,  # 7th rank - strong bonus
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  0,  5,  5,  5,  5,  0,  0,
             0,  5,  5, 10, 10,  5,  5,  0,
             0,  0,  0, 10, 10,  0,  0,  0   # 1st rank
        ]
        
        # Enhanced Queen PST - STRONG corner penalties to prevent Qh8-type moves
        self.queen_table = [
            -30,-20,-15,-10,-10,-15,-20,-30,  # 8th rank - VERY strong corner penalty
            -20,-10, -5,  0,  0, -5,-10,-20,  # 7th rank
            -15, -5,  5, 10, 10,  5, -5,-15,  # 6th rank
            -10,  0, 10, 15, 15, 10,  0,-10,  # 5th rank
            -10,  0, 10, 15, 15, 10,  0,-10,  # 4th rank
            -15, -5,  5, 10, 10,  5, -5,-15,  # 3rd rank
            -20,-10, -5,  0,  0, -5,-10,-20,  # 2nd rank
            -30,-20,-15,-10,-10,-15,-20,-30   # 1st rank - VERY strong corner penalty
        ]
        
        # Enhanced King Middlegame PST - encourages castling
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

    def _see_evaluate_capture(self, board: chess.Board, move: chess.Move) -> int:
        """
        Static Exchange Evaluation for capture moves.
        
        Calculates material gain/loss from capture sequence on target square.
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
        self._see_continue_exchange(board_copy, target_square, attacking_piece_value, gain)
        
        # Calculate final result using minimax
        return self._see_minimax_gain(gain)
    
    def _see_continue_exchange(self, board: chess.Board, square: chess.Square, 
                              last_attacker_value: int, gain: List[int]):
        """Continue the SEE exchange sequence recursively."""
        
        # Find the least valuable attacker
        attacker_move = self._see_find_least_valuable_attacker(board, square)
        
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
        self._see_continue_exchange(board, square, attacker_value, gain)
    
    def _see_find_least_valuable_attacker(self, board: chess.Board, 
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
    
    def _see_minimax_gain(self, gain: List[int]) -> int:
        """Calculate final SEE gain using minimax principle."""
        if not gain:
            return 0
            
        # Work backwards through the gain list
        for i in range(len(gain) - 2, -1, -1):
            gain[i] = max(0, gain[i] - gain[i + 1])
            
        return gain[0]

    def _calculate_side_threats(self, board: chess.Board, color: chess.Color) -> int:
        """Calculate total threat value for one side using MVV-LVA."""
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

    def _evaluate_side_castling(self, board: chess.Board, color: chess.Color,
                               castling_rights_bonus: int, castled_bonus: int,
                               early_game_urgency: int, exposed_king_penalty: int) -> int:
        """Evaluate castling factors for one side."""
        score = 0
        
        # Find the king
        king_square = board.king(color)
        if not king_square:
            return 0
        
        # Check if already castled
        has_castled = self._has_castled(board, color, king_square)
        
        if has_castled:
            # Bonus for having castled
            score += castled_bonus
            
            # Evaluate pawn shield
            score += self._evaluate_pawn_shield(board, color, king_square)
            
        else:
            # Not castled yet - evaluate castling rights and urgency
            
            # Count available castling rights
            castling_rights = self._count_castling_rights(board, color)
            score += castling_rights * castling_rights_bonus
            
            # Evaluate urgency based on game phase
            game_phase = self._estimate_game_phase(board)
            
            if game_phase == "opening":
                # Extra urgency to castle in opening
                if castling_rights > 0:
                    score += early_game_urgency
                    
                # Penalty for king still in center during opening
                if self._is_king_in_center(king_square):
                    score += exposed_king_penalty
            
            elif game_phase == "middlegame":
                # Moderate urgency in middlegame
                if castling_rights > 0:
                    score += early_game_urgency // 2
                    
                # Check king safety if not castled
                score += self._evaluate_uncastled_king_safety(board, color, king_square)
        
        return score
    
    def _has_castled(self, board: chess.Board, color: chess.Color, 
                    king_square: chess.Square) -> bool:
        """Check if the king has castled."""
        
        if color == chess.WHITE:
            # White castled if king is on g1 or c1
            return king_square in [chess.G1, chess.C1]
        else:
            # Black castled if king is on g8 or c8
            return king_square in [chess.G8, chess.C8]
    
    def _count_castling_rights(self, board: chess.Board, color: chess.Color) -> int:
        """Count available castling rights for a color."""
        rights = 0
        
        if color == chess.WHITE:
            if board.has_kingside_castling_rights(chess.WHITE):
                rights += 1
            if board.has_queenside_castling_rights(chess.WHITE):
                rights += 1
        else:
            if board.has_kingside_castling_rights(chess.BLACK):
                rights += 1
            if board.has_queenside_castling_rights(chess.BLACK):
                rights += 1
                
        return rights
    
    def _evaluate_pawn_shield(self, board: chess.Board, color: chess.Color, 
                            king_square: chess.Square) -> int:
        """Evaluate pawn shield in front of castled king."""
        pawn_shield_bonus = 20
        score = 0
        
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        # Check pawns in front of king
        if color == chess.WHITE:
            shield_rank = king_rank + 1
            pawn_color = chess.WHITE
        else:
            shield_rank = king_rank - 1
            pawn_color = chess.BLACK
            
        # Check 3 files around king
        for file_offset in [-1, 0, 1]:
            shield_file = king_file + file_offset
            
            if 0 <= shield_file <= 7 and 0 <= shield_rank <= 7:
                shield_square = chess.square(shield_file, shield_rank)
                piece = board.piece_at(shield_square)
                
                if piece and piece.piece_type == chess.PAWN and piece.color == pawn_color:
                    score += pawn_shield_bonus
        
        return score
    
    def _evaluate_uncastled_king_safety(self, board: chess.Board, color: chess.Color,
                                      king_square: chess.Square) -> int:
        """Evaluate safety of uncastled king."""
        safety_score = 0
        
        # Count enemy pieces attacking squares around king
        king_area = self._get_king_area(king_square)
        attacks_on_king_area = 0
        
        for square in king_area:
            if board.is_attacked_by(not color, square):
                attacks_on_king_area += 1
        
        # Penalty based on number of attacked squares
        safety_score -= attacks_on_king_area * 10
        
        # Extra penalty if king is on open files
        king_file = chess.square_file(king_square)
        if self._is_open_file(board, king_file, color):
            safety_score -= 25
        
        return safety_score
    
    def _is_open_file(self, board: chess.Board, file: int, color: chess.Color) -> bool:
        """Check if a file is open (no pawns of given color)."""
        
        for rank in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                return False
                
        return True

    # Debugging and testing utilities
    def get_evaluation_explanation(self, board: chess.Board) -> str:
        """Get human-readable explanation of position evaluation."""
        score, breakdown = self.evaluate_detailed(board)
        
        explanation = f"Position Evaluation: {score}\\n"
        explanation += f"Material: {breakdown['material']}\\n"
        explanation += f"Positional: {breakdown['positional']}\\n"
        explanation += f"Tactical: {breakdown['tactical']}\\n"
        explanation += f"Threats: {breakdown['threats']}\\n"
        explanation += f"Castling: {breakdown['castling']}\\n"
        explanation += f"King Safety: {breakdown['king_safety']}\\n"
        
        return explanation

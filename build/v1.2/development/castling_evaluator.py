"""
Castling Evaluator for Cece v1.2

Specialized evaluation for castling rights and king safety.
Encourages proper development and timely castling.

Key Features:
- Rewards maintaining castling rights
- Gives bonus for successful castling
- Evaluates king safety in different phases
- Balances development vs safety
"""

import chess
from typing import Dict, Tuple, Any

class CastlingEvaluator:
    """Evaluates castling rights and king safety."""
    
    def __init__(self):
        # Scoring parameters
        self.castling_rights_bonus = 15    # Bonus per available castling right
        self.castled_bonus = 50           # Bonus for having castled
        self.early_game_castling_urgency = 30  # Extra urgency in opening
        
        # King safety parameters
        self.exposed_king_penalty = -100  # Penalty for exposed king in center
        self.pawn_shield_bonus = 20       # Bonus per pawn in front of castled king
    
    def evaluate_castling(self, board: chess.Board) -> int:
        """
        Evaluate castling-related factors for current position.
        
        Returns:
            Score favoring the side to move
        """
        score = 0
        
        # Evaluate for both sides
        white_score = self._evaluate_side_castling(board, chess.WHITE)
        black_score = self._evaluate_side_castling(board, chess.BLACK)
        
        # Return score relative to side to move
        if board.turn == chess.WHITE:
            score = white_score - black_score
        else:
            score = black_score - white_score
            
        return score
    
    def _evaluate_side_castling(self, board: chess.Board, color: chess.Color) -> int:
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
            score += self.castled_bonus
            
            # Evaluate pawn shield
            score += self._evaluate_pawn_shield(board, color, king_square)
            
        else:
            # Not castled yet - evaluate castling rights and urgency
            
            # Count available castling rights
            castling_rights = self._count_castling_rights(board, color)
            score += castling_rights * self.castling_rights_bonus
            
            # Evaluate urgency based on game phase
            game_phase = self._estimate_game_phase(board)
            
            if game_phase == "opening":
                # Extra urgency to castle in opening
                if castling_rights > 0:
                    score += self.early_game_castling_urgency
                    
                # Penalty for king still in center during opening
                if self._is_king_in_center(king_square):
                    score += self.exposed_king_penalty
            
            elif game_phase == "middlegame":
                # Moderate urgency in middlegame
                if castling_rights > 0:
                    score += self.early_game_castling_urgency // 2
                    
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
    
    def _is_king_in_center(self, king_square: chess.Square) -> bool:
        """Check if king is still in the center files."""
        file = chess.square_file(king_square)
        # Center files are d(3), e(4)
        return file in [3, 4]
    
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
    
    def _evaluate_pawn_shield(self, board: chess.Board, color: chess.Color, 
                            king_square: chess.Square) -> int:
        """Evaluate pawn shield in front of castled king."""
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
                    score += self.pawn_shield_bonus
        
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
    
    def _get_king_area(self, king_square: chess.Square) -> list:
        """Get squares in the king's immediate area."""
        king_area = []
        king_file = chess.square_file(king_square)
        king_rank = chess.square_rank(king_square)
        
        for file_offset in [-1, 0, 1]:
            for rank_offset in [-1, 0, 1]:
                file = king_file + file_offset
                rank = king_rank + rank_offset
                
                if 0 <= file <= 7 and 0 <= rank <= 7:
                    square = chess.square(file, rank)
                    king_area.append(square)
        
        return king_area
    
    def _is_open_file(self, board: chess.Board, file: int, color: chess.Color) -> bool:
        """Check if a file is open (no pawns of given color)."""
        
        for rank in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                return False
                
        return True
    
    def get_castling_advice(self, board: chess.Board) -> Dict[str, Any]:
        """Get castling advice for current position."""
        
        color = board.turn
        advice = {
            'should_castle': False,
            'urgency': 'low',
            'available_castling': [],
            'king_safety_score': 0,
            'reasoning': []
        }
        
        # Check available castling moves
        for move in board.legal_moves:
            if board.is_castling(move):
                if board.is_kingside_castling(move):
                    advice['available_castling'].append('kingside')
                else:
                    advice['available_castling'].append('queenside')
        
        if advice['available_castling']:
            advice['should_castle'] = True
            
            # Determine urgency
            game_phase = self._estimate_game_phase(board)
            king_square = board.king(color)
            
            if game_phase == "opening":
                advice['urgency'] = 'high'
                advice['reasoning'].append("Opening phase - castle for safety")
                
            if king_square and self._is_king_in_center(king_square):
                advice['urgency'] = 'very_high'
                advice['reasoning'].append("King exposed in center")
                
            # Evaluate king safety
            if king_square:
                safety = self._evaluate_uncastled_king_safety(board, color, king_square)
                advice['king_safety_score'] = safety
                
                if safety < -50:
                    advice['urgency'] = 'critical'
                    advice['reasoning'].append("King under serious threat")
        
        return advice

# Test functions
def test_castling_evaluator():
    """Test castling evaluation."""
    castling_eval = CastlingEvaluator()
    
    # Starting position
    board = chess.Board()
    print("=== Starting Position ===")
    score = castling_eval.evaluate_castling(board)
    advice = castling_eval.get_castling_advice(board)
    print(f"Castling score: {score}")
    print(f"Should castle: {advice['should_castle']}")
    print(f"Urgency: {advice['urgency']}")
    
    # After some development
    for move in ["e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5"]:
        board.push_san(move)
    
    print("\n=== After Development ===")
    score = castling_eval.evaluate_castling(board)
    advice = castling_eval.get_castling_advice(board)
    print(f"Castling score: {score}")
    print(f"Available castling: {advice['available_castling']}")
    print(f"Urgency: {advice['urgency']}")
    print(f"Reasoning: {advice['reasoning']}")
    
    print("Castling evaluator test complete")

if __name__ == "__main__":
    test_castling_evaluator()

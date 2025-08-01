"""
Static evaluation functions for chess positions using bitboards.
"""

from bitboard import Board, PieceType, Color, BitboardUtils
from typing import Dict


class Evaluation:
    """Static position evaluation using handcrafted functions."""
    
    # Piece values in centipawns
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }
    
    def __init__(self):
        pass
    
    def evaluate(self, board: Board) -> int:
        """
        Evaluate the current position from white's perspective.
        Positive values favor white, negative values favor black.
        """
        if self.is_checkmate(board):
            return -20000 if board.to_move == Color.WHITE else 20000
        
        if self.is_stalemate(board) or self.is_draw(board):
            return 0
        
        score = 0
        
        # Material evaluation
        score += self.evaluate_material(board)
        
        # Piece activity (simplified mobility)
        score += self.evaluate_mobility(board)
        
        # King safety (simplified)
        score += self.evaluate_king_safety(board)
        
        return score
    
    def evaluate_material(self, board: Board) -> int:
        """Evaluate material balance."""
        score = 0
        
        for piece_type in PieceType:
            white_pieces = BitboardUtils.count_bits(board.pieces[Color.WHITE.value][piece_type.value])
            black_pieces = BitboardUtils.count_bits(board.pieces[Color.BLACK.value][piece_type.value])
            
            piece_value = self.PIECE_VALUES[piece_type]
            score += (white_pieces - black_pieces) * piece_value
        
        return score
    
    def evaluate_mobility(self, board: Board) -> int:
        """Evaluate piece mobility (simplified)."""
        score = 0
        
        # Save current state
        original_to_move = board.to_move
        
        # White mobility
        board.to_move = Color.WHITE
        white_moves = len(board.generate_pseudo_legal_moves())
        
        # Black mobility  
        board.to_move = Color.BLACK
        black_moves = len(board.generate_pseudo_legal_moves())
        
        # Restore original state
        board.to_move = original_to_move
        
        score += (white_moves - black_moves) * 2
        
        return score
    
    def evaluate_king_safety(self, board: Board) -> int:
        """Evaluate king safety (simplified)."""
        score = 0
        
        # Find kings
        white_king_bb = board.pieces[Color.WHITE.value][PieceType.KING.value]
        black_king_bb = board.pieces[Color.BLACK.value][PieceType.KING.value]
        
        if white_king_bb:
            white_king_square = (white_king_bb - 1).bit_length() - 1
            if board.is_square_attacked(white_king_square, Color.BLACK):
                score -= 50  # Penalty for being in check
        
        if black_king_bb:
            black_king_square = (black_king_bb - 1).bit_length() - 1
            if board.is_square_attacked(black_king_square, Color.WHITE):
                score += 50  # Bonus for attacking enemy king
        
        return score
    
    def is_checkmate(self, board: Board) -> bool:
        """Check if the current position is checkmate."""
        if not board.is_in_check(board.to_move):
            return False
        
        legal_moves = board.generate_legal_moves()
        return len(legal_moves) == 0
    
    def is_stalemate(self, board: Board) -> bool:
        """Check if the current position is stalemate."""
        if board.is_in_check(board.to_move):
            return False
        
        legal_moves = board.generate_legal_moves()
        return len(legal_moves) == 0
    
    def is_draw(self, board: Board) -> bool:
        """Check for various draw conditions."""
        # Fifty-move rule
        if board.halfmove_clock >= 100:
            return True
        
        # Insufficient material
        if self.is_insufficient_material(board):
            return True
        
        # Threefold repetition (simplified check)
        if len(board.position_history) >= 6:
            current_position = board.to_fen().split()[0]  # Just board position
            count = board.position_history.count(current_position)
            if count >= 3:
                return True
        
        return False
    
    def is_insufficient_material(self, board: Board) -> bool:
        """Check if there's insufficient material to checkmate."""
        # Count pieces for each side
        white_pieces = {}
        black_pieces = {}
        
        for piece_type in PieceType:
            if piece_type != PieceType.KING:  # Don't count kings
                white_count = BitboardUtils.count_bits(board.pieces[Color.WHITE.value][piece_type.value])
                black_count = BitboardUtils.count_bits(board.pieces[Color.BLACK.value][piece_type.value])
                
                if white_count > 0:
                    white_pieces[piece_type] = white_count
                if black_count > 0:
                    black_pieces[piece_type] = black_count
        
        # King vs King
        if not white_pieces and not black_pieces:
            return True
        
        # King + minor piece vs King
        if (len(white_pieces) == 1 and not black_pieces and 
            PieceType.BISHOP in white_pieces or PieceType.KNIGHT in white_pieces):
            return True
        
        if (len(black_pieces) == 1 and not white_pieces and 
            PieceType.BISHOP in black_pieces or PieceType.KNIGHT in black_pieces):
            return True
        
        # King + Bishop vs King + Bishop (same color squares - simplified)
        if (len(white_pieces) == 1 and len(black_pieces) == 1 and
            PieceType.BISHOP in white_pieces and PieceType.BISHOP in black_pieces):
            return True
        
        return False

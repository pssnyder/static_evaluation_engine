"""
Chess board representation using bitboards for maximum efficiency.
"""

import copy
from typing import List, Tuple, Optional, Dict, Set
from enum import Enum


class PieceType(Enum):
    PAWN = 0
    KNIGHT = 1
    BISHOP = 2
    ROOK = 3
    QUEEN = 4
    KING = 5


class Color(Enum):
    WHITE = 0
    BLACK = 1


class Square:
    """Represents a square on the chess board."""
    
    def __init__(self, file: int, rank: int):
        self.file = file  # 0-7 (a-h)
        self.rank = rank  # 0-7 (1-8)
        self.index = rank * 8 + file
    
    def __str__(self):
        return chr(ord('a') + self.file) + str(self.rank + 1)
    
    def __eq__(self, other):
        return self.index == other.index if isinstance(other, Square) else False
    
    def __hash__(self):
        return hash(self.index)
    
    @classmethod
    def from_string(cls, square_str: str):
        """Create square from algebraic notation (e.g., 'e4')"""
        file = ord(square_str[0]) - ord('a')
        rank = int(square_str[1]) - 1
        return cls(file, rank)
    
    @classmethod
    def from_index(cls, index: int):
        """Create square from board index (0-63)"""
        return cls(index % 8, index // 8)


class Move:
    """Represents a chess move."""
    
    def __init__(self, from_square: int, to_square: int, 
                 promotion: Optional[PieceType] = None, 
                 is_castling: bool = False,
                 is_en_passant: bool = False):
        self.from_square = from_square  # Square index 0-63
        self.to_square = to_square      # Square index 0-63
        self.promotion = promotion
        self.is_castling = is_castling
        self.is_en_passant = is_en_passant
        self.captured_piece: Optional[PieceType] = None
        self.score = 0  # For move ordering
    
    def __str__(self):
        from_sq = Square.from_index(self.from_square)
        to_sq = Square.from_index(self.to_square)
        move_str = str(from_sq) + str(to_sq)
        if self.promotion:
            promotion_symbols = {
                PieceType.QUEEN: 'q',
                PieceType.ROOK: 'r',
                PieceType.BISHOP: 'b',
                PieceType.KNIGHT: 'n'
            }
            move_str += promotion_symbols[self.promotion]
        return move_str
    
    def __eq__(self, other):
        return (self.from_square == other.from_square and
                self.to_square == other.to_square and
                self.promotion == other.promotion) if isinstance(other, Move) else False


class BitboardUtils:
    """Utility functions for bitboard operations."""
    
    # File masks
    FILE_A = 0x0101010101010101
    FILE_B = 0x0202020202020202
    FILE_C = 0x0404040404040404
    FILE_D = 0x0808080808080808
    FILE_E = 0x1010101010101010
    FILE_F = 0x2020202020202020
    FILE_G = 0x4040404040404040
    FILE_H = 0x8080808080808080
    
    # Rank masks
    RANK_1 = 0x00000000000000FF
    RANK_2 = 0x000000000000FF00
    RANK_3 = 0x0000000000FF0000
    RANK_4 = 0x00000000FF000000
    RANK_5 = 0x000000FF00000000
    RANK_6 = 0x0000FF0000000000
    RANK_7 = 0x00FF000000000000
    RANK_8 = 0xFF00000000000000
    
    FILES = [FILE_A, FILE_B, FILE_C, FILE_D, FILE_E, FILE_F, FILE_G, FILE_H]
    RANKS = [RANK_1, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8]
    
    # Diagonal masks
    DIAGONAL_A1H8 = 0x8040201008040201
    DIAGONAL_H1A8 = 0x0102040810204080
    
    @staticmethod
    def set_bit(bitboard: int, square: int) -> int:
        """Set bit at given square."""
        return bitboard | (1 << square)
    
    @staticmethod
    def clear_bit(bitboard: int, square: int) -> int:
        """Clear bit at given square."""
        return bitboard & ~(1 << square)
    
    @staticmethod
    def get_bit(bitboard: int, square: int) -> bool:
        """Check if bit is set at given square."""
        return bool(bitboard & (1 << square))
    
    @staticmethod
    def pop_lsb(bitboard: int) -> Tuple[int, int]:
        """Pop least significant bit and return square index."""
        if bitboard == 0:
            return 0, -1
        lsb = bitboard & -bitboard
        square = (lsb - 1).bit_length() - 1
        return bitboard ^ lsb, square
    
    @staticmethod
    def count_bits(bitboard: int) -> int:
        """Count number of set bits."""
        return bin(bitboard).count('1')
    
    @staticmethod
    def shift_north(bitboard: int) -> int:
        """Shift bitboard north (towards rank 8)."""
        return (bitboard << 8) & 0xFFFFFFFFFFFFFFFF
    
    @staticmethod
    def shift_south(bitboard: int) -> int:
        """Shift bitboard south (towards rank 1)."""
        return bitboard >> 8
    
    @staticmethod
    def shift_east(bitboard: int) -> int:
        """Shift bitboard east (towards H file)."""
        return (bitboard << 1) & ~BitboardUtils.FILE_A
    
    @staticmethod
    def shift_west(bitboard: int) -> int:
        """Shift bitboard west (towards A file)."""
        return (bitboard >> 1) & ~BitboardUtils.FILE_H
    
    @staticmethod
    def shift_northeast(bitboard: int) -> int:
        """Shift bitboard northeast."""
        return (bitboard << 9) & ~BitboardUtils.FILE_A
    
    @staticmethod
    def shift_northwest(bitboard: int) -> int:
        """Shift bitboard northwest."""
        return (bitboard << 7) & ~BitboardUtils.FILE_H
    
    @staticmethod
    def shift_southeast(bitboard: int) -> int:
        """Shift bitboard southeast."""
        return (bitboard >> 7) & ~BitboardUtils.FILE_A
    
    @staticmethod
    def shift_southwest(bitboard: int) -> int:
        """Shift bitboard southwest."""
        return (bitboard >> 9) & ~BitboardUtils.FILE_H


class AttackTables:
    """Precomputed attack tables for pieces."""
    
    def __init__(self):
        self.knight_attacks = [0] * 64
        self.king_attacks = [0] * 64
        self.pawn_attacks = [[0] * 64, [0] * 64]  # [color][square]
        
        self._init_knight_attacks()
        self._init_king_attacks()
        self._init_pawn_attacks()
    
    def _init_knight_attacks(self):
        """Initialize knight attack table."""
        knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for square in range(64):
            file, rank = square % 8, square // 8
            attacks = 0
            
            for df, dr in knight_deltas:
                target_file, target_rank = file + df, rank + dr
                if 0 <= target_file <= 7 and 0 <= target_rank <= 7:
                    target_square = target_rank * 8 + target_file
                    attacks = BitboardUtils.set_bit(attacks, target_square)
            
            self.knight_attacks[square] = attacks
    
    def _init_king_attacks(self):
        """Initialize king attack table."""
        king_deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                      (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for square in range(64):
            file, rank = square % 8, square // 8
            attacks = 0
            
            for df, dr in king_deltas:
                target_file, target_rank = file + df, rank + dr
                if 0 <= target_file <= 7 and 0 <= target_rank <= 7:
                    target_square = target_rank * 8 + target_file
                    attacks = BitboardUtils.set_bit(attacks, target_square)
            
            self.king_attacks[square] = attacks
    
    def _init_pawn_attacks(self):
        """Initialize pawn attack tables."""
        for square in range(64):
            file, rank = square % 8, square // 8
            
            # White pawn attacks
            white_attacks = 0
            if rank < 7:  # Not on 8th rank
                if file > 0:  # Can capture left
                    target = (rank + 1) * 8 + (file - 1)
                    white_attacks = BitboardUtils.set_bit(white_attacks, target)
                if file < 7:  # Can capture right
                    target = (rank + 1) * 8 + (file + 1)
                    white_attacks = BitboardUtils.set_bit(white_attacks, target)
            
            # Black pawn attacks
            black_attacks = 0
            if rank > 0:  # Not on 1st rank
                if file > 0:  # Can capture left
                    target = (rank - 1) * 8 + (file - 1)
                    black_attacks = BitboardUtils.set_bit(black_attacks, target)
                if file < 7:  # Can capture right
                    target = (rank - 1) * 8 + (file + 1)
                    black_attacks = BitboardUtils.set_bit(black_attacks, target)
            
            self.pawn_attacks[Color.WHITE.value][square] = white_attacks
            self.pawn_attacks[Color.BLACK.value][square] = black_attacks


class Board:
    """Bitboard-based chess board representation."""
    
    def __init__(self):
        # Piece bitboards [color][piece_type]
        self.pieces = [[0] * 6 for _ in range(2)]
        
        # Occupancy bitboards
        self.color_occupancy = [0, 0]  # [white, black]
        self.all_occupancy = 0
        
        # Game state
        self.to_move = Color.WHITE
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant_square: Optional[int] = None  # Square index
        self.halfmove_clock = 0
        self.fullmove_number = 1
        
        # History for undo and repetition detection
        self.move_history: List[Move] = []
        self.position_history: List[str] = []
        
        # Attack tables
        self.attack_tables = AttackTables()
        
        self.setup_starting_position()
    
    def setup_starting_position(self):
        """Set up the standard chess starting position."""
        # Clear all bitboards
        self.pieces = [[0] * 6 for _ in range(2)]
        self.color_occupancy = [0, 0]
        self.all_occupancy = 0
        
        # Set up pieces
        piece_setup = [
            (PieceType.ROOK, [0, 7, 56, 63]),
            (PieceType.KNIGHT, [1, 6, 57, 62]),
            (PieceType.BISHOP, [2, 5, 58, 61]),
            (PieceType.QUEEN, [3, 59]),
            (PieceType.KING, [4, 60])
        ]
        
        for piece_type, squares in piece_setup:
            for square in squares:
                color = Color.WHITE if square < 32 else Color.BLACK
                self.set_piece(square, piece_type, color)
        
        # Set up pawns
        for square in range(8, 16):  # White pawns
            self.set_piece(square, PieceType.PAWN, Color.WHITE)
        
        for square in range(48, 56):  # Black pawns
            self.set_piece(square, PieceType.PAWN, Color.BLACK)
        
        self.update_occupancy()
    
    def set_piece(self, square: int, piece_type: PieceType, color: Color):
        """Set a piece on the board."""
        self.pieces[color.value][piece_type.value] = BitboardUtils.set_bit(
            self.pieces[color.value][piece_type.value], square)
    
    def remove_piece(self, square: int, piece_type: PieceType, color: Color):
        """Remove a piece from the board."""
        self.pieces[color.value][piece_type.value] = BitboardUtils.clear_bit(
            self.pieces[color.value][piece_type.value], square)
    
    def get_piece_at(self, square: int) -> Optional[Tuple[PieceType, Color]]:
        """Get the piece at a given square."""
        for color in [Color.WHITE, Color.BLACK]:
            for piece_type in PieceType:
                if BitboardUtils.get_bit(self.pieces[color.value][piece_type.value], square):
                    return piece_type, color
        return None
    
    def update_occupancy(self):
        """Update occupancy bitboards."""
        self.color_occupancy[Color.WHITE.value] = 0
        self.color_occupancy[Color.BLACK.value] = 0
        
        for piece_type in PieceType:
            self.color_occupancy[Color.WHITE.value] |= self.pieces[Color.WHITE.value][piece_type.value]
            self.color_occupancy[Color.BLACK.value] |= self.pieces[Color.BLACK.value][piece_type.value]
        
        self.all_occupancy = self.color_occupancy[Color.WHITE.value] | self.color_occupancy[Color.BLACK.value]
    
    def is_square_attacked(self, square: int, by_color: Color) -> bool:
        """Check if a square is attacked by pieces of given color."""
        enemy_color = Color.WHITE if by_color == Color.BLACK else Color.BLACK
        
        # Pawn attacks
        pawn_attacks = self.attack_tables.pawn_attacks[enemy_color.value][square]
        if pawn_attacks & self.pieces[by_color.value][PieceType.PAWN.value]:
            return True
        
        # Knight attacks
        knight_attacks = self.attack_tables.knight_attacks[square]
        if knight_attacks & self.pieces[by_color.value][PieceType.KNIGHT.value]:
            return True
        
        # King attacks
        king_attacks = self.attack_tables.king_attacks[square]
        if king_attacks & self.pieces[by_color.value][PieceType.KING.value]:
            return True
        
        # Sliding piece attacks
        if self.get_sliding_attacks(square) & (
            self.pieces[by_color.value][PieceType.BISHOP.value] |
            self.pieces[by_color.value][PieceType.ROOK.value] |
            self.pieces[by_color.value][PieceType.QUEEN.value]
        ):
            return True
        
        return False
    
    def get_sliding_attacks(self, square: int) -> int:
        """Get all squares attacked by sliding pieces from given square."""
        attacks = 0
        file, rank = square % 8, square // 8
        
        # Horizontal and vertical
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for df, dr in directions:
            for dist in range(1, 8):
                target_file, target_rank = file + df * dist, rank + dr * dist
                if not (0 <= target_file <= 7 and 0 <= target_rank <= 7):
                    break
                
                target_square = target_rank * 8 + target_file
                attacks = BitboardUtils.set_bit(attacks, target_square)
                
                if BitboardUtils.get_bit(self.all_occupancy, target_square):
                    break
        
        # Diagonal
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for df, dr in directions:
            for dist in range(1, 8):
                target_file, target_rank = file + df * dist, rank + dr * dist
                if not (0 <= target_file <= 7 and 0 <= target_rank <= 7):
                    break
                
                target_square = target_rank * 8 + target_file
                attacks = BitboardUtils.set_bit(attacks, target_square)
                
                if BitboardUtils.get_bit(self.all_occupancy, target_square):
                    break
        
        return attacks
    
    def is_in_check(self, color: Color) -> bool:
        """Check if the king of given color is in check."""
        king_bitboard = self.pieces[color.value][PieceType.KING.value]
        if king_bitboard == 0:
            return False
        
        king_square = (king_bitboard - 1).bit_length() - 1
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        return self.is_square_attacked(king_square, enemy_color)
    
    def generate_pseudo_legal_moves(self) -> List[Move]:
        """Generate all pseudo-legal moves for the current position."""
        moves = []
        
        for piece_type in PieceType:
            piece_bitboard = self.pieces[self.to_move.value][piece_type.value]
            
            while piece_bitboard:
                piece_bitboard, square = BitboardUtils.pop_lsb(piece_bitboard)
                moves.extend(self._generate_piece_moves(square, piece_type))
        
        return moves
    
    def _generate_piece_moves(self, square: int, piece_type: PieceType) -> List[Move]:
        """Generate moves for a specific piece."""
        moves = []
        
        if piece_type == PieceType.PAWN:
            moves.extend(self._generate_pawn_moves(square))
        elif piece_type == PieceType.KNIGHT:
            moves.extend(self._generate_knight_moves(square))
        elif piece_type == PieceType.BISHOP:
            moves.extend(self._generate_bishop_moves(square))
        elif piece_type == PieceType.ROOK:
            moves.extend(self._generate_rook_moves(square))
        elif piece_type == PieceType.QUEEN:
            moves.extend(self._generate_queen_moves(square))
        elif piece_type == PieceType.KING:
            moves.extend(self._generate_king_moves(square))
        
        return moves
    
    def _generate_pawn_moves(self, square: int) -> List[Move]:
        """Generate pawn moves."""
        moves = []
        file, rank = square % 8, square // 8
        
        if self.to_move == Color.WHITE:
            direction = 1
            start_rank = 1
            promotion_rank = 7
        else:
            direction = -1
            start_rank = 6
            promotion_rank = 0
        
        # Forward move
        target_rank = rank + direction
        if 0 <= target_rank <= 7:
            target_square = target_rank * 8 + file
            if not BitboardUtils.get_bit(self.all_occupancy, target_square):
                if target_rank == promotion_rank:
                    # Promotion
                    for promo_piece in [PieceType.QUEEN, PieceType.ROOK, 
                                       PieceType.BISHOP, PieceType.KNIGHT]:
                        moves.append(Move(square, target_square, promotion=promo_piece))
                else:
                    moves.append(Move(square, target_square))
                
                # Double forward move
                if rank == start_rank:
                    double_target = (target_rank + direction) * 8 + file
                    if not BitboardUtils.get_bit(self.all_occupancy, double_target):
                        moves.append(Move(square, double_target))
        
        # Captures
        enemy_color = Color.BLACK if self.to_move == Color.WHITE else Color.WHITE
        for file_offset in [-1, 1]:
            target_file = file + file_offset
            target_rank = rank + direction
            
            if 0 <= target_file <= 7 and 0 <= target_rank <= 7:
                target_square = target_rank * 8 + target_file
                
                if BitboardUtils.get_bit(self.color_occupancy[enemy_color.value], target_square):
                    if target_rank == promotion_rank:
                        # Promotion capture
                        for promo_piece in [PieceType.QUEEN, PieceType.ROOK, 
                                           PieceType.BISHOP, PieceType.KNIGHT]:
                            moves.append(Move(square, target_square, promotion=promo_piece))
                    else:
                        moves.append(Move(square, target_square))
                
                # En passant
                if self.en_passant_square and target_square == self.en_passant_square:
                    moves.append(Move(square, target_square, is_en_passant=True))
        
        return moves
    
    def _generate_knight_moves(self, square: int) -> List[Move]:
        """Generate knight moves."""
        moves = []
        attacks = self.attack_tables.knight_attacks[square]
        
        # Remove friendly pieces
        attacks &= ~self.color_occupancy[self.to_move.value]
        
        while attacks:
            attacks, target_square = BitboardUtils.pop_lsb(attacks)
            moves.append(Move(square, target_square))
        
        return moves
    
    def _generate_king_moves(self, square: int) -> List[Move]:
        """Generate king moves including castling."""
        moves = []
        attacks = self.attack_tables.king_attacks[square]
        
        # Remove friendly pieces
        attacks &= ~self.color_occupancy[self.to_move.value]
        
        while attacks:
            attacks, target_square = BitboardUtils.pop_lsb(attacks)
            moves.append(Move(square, target_square))
        
        # Castling
        if not self.is_in_check(self.to_move):
            if self.to_move == Color.WHITE:
                # Kingside castling
                if (self.castling_rights['K'] and 
                    not (self.all_occupancy & 0x60) and  # f1, g1 empty
                    not self.is_square_attacked(5, Color.BLACK) and
                    not self.is_square_attacked(6, Color.BLACK)):
                    moves.append(Move(square, 6, is_castling=True))
                
                # Queenside castling
                if (self.castling_rights['Q'] and 
                    not (self.all_occupancy & 0x0E) and  # b1, c1, d1 empty
                    not self.is_square_attacked(3, Color.BLACK) and
                    not self.is_square_attacked(2, Color.BLACK)):
                    moves.append(Move(square, 2, is_castling=True))
            else:
                # Kingside castling
                if (self.castling_rights['k'] and 
                    not (self.all_occupancy & 0x6000000000000000) and  # f8, g8 empty
                    not self.is_square_attacked(61, Color.WHITE) and
                    not self.is_square_attacked(62, Color.WHITE)):
                    moves.append(Move(square, 62, is_castling=True))
                
                # Queenside castling
                if (self.castling_rights['q'] and 
                    not (self.all_occupancy & 0x0E00000000000000) and  # b8, c8, d8 empty
                    not self.is_square_attacked(59, Color.WHITE) and
                    not self.is_square_attacked(58, Color.WHITE)):
                    moves.append(Move(square, 58, is_castling=True))
        
        return moves
    
    def _generate_sliding_moves(self, square: int, piece_type: PieceType) -> List[Move]:
        """Generate moves for sliding pieces."""
        moves = []
        file, rank = square % 8, square // 8
        
        if piece_type in [PieceType.ROOK, PieceType.QUEEN]:
            # Horizontal and vertical
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            for df, dr in directions:
                for dist in range(1, 8):
                    target_file, target_rank = file + df * dist, rank + dr * dist
                    if not (0 <= target_file <= 7 and 0 <= target_rank <= 7):
                        break
                    
                    target_square = target_rank * 8 + target_file
                    
                    if BitboardUtils.get_bit(self.color_occupancy[self.to_move.value], target_square):
                        break  # Blocked by friendly piece
                    
                    moves.append(Move(square, target_square))
                    
                    if BitboardUtils.get_bit(self.all_occupancy, target_square):
                        break  # Blocked by enemy piece (but move is valid)
        
        if piece_type in [PieceType.BISHOP, PieceType.QUEEN]:
            # Diagonal
            directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            for df, dr in directions:
                for dist in range(1, 8):
                    target_file, target_rank = file + df * dist, rank + dr * dist
                    if not (0 <= target_file <= 7 and 0 <= target_rank <= 7):
                        break
                    
                    target_square = target_rank * 8 + target_file
                    
                    if BitboardUtils.get_bit(self.color_occupancy[self.to_move.value], target_square):
                        break  # Blocked by friendly piece
                    
                    moves.append(Move(square, target_square))
                    
                    if BitboardUtils.get_bit(self.all_occupancy, target_square):
                        break  # Blocked by enemy piece (but move is valid)
        
        return moves
    
    def _generate_bishop_moves(self, square: int) -> List[Move]:
        """Generate bishop moves."""
        return self._generate_sliding_moves(square, PieceType.BISHOP)
    
    def _generate_rook_moves(self, square: int) -> List[Move]:
        """Generate rook moves."""
        return self._generate_sliding_moves(square, PieceType.ROOK)
    
    def _generate_queen_moves(self, square: int) -> List[Move]:
        """Generate queen moves."""
        return self._generate_sliding_moves(square, PieceType.QUEEN)
    
    def generate_legal_moves(self) -> List[Move]:
        """Generate all legal moves for the current position."""
        pseudo_legal_moves = self.generate_pseudo_legal_moves()
        legal_moves = []
        
        for move in pseudo_legal_moves:
            if self.is_legal_move(move):
                legal_moves.append(move)
        
        return legal_moves
    
    def is_legal_move(self, move: Move) -> bool:
        """Check if a move is legal (doesn't leave king in check)."""
        # Make the move temporarily
        old_state = self._save_state()
        self._make_move_internal(move)
        
        # Check if the king is in check after the move
        previous_color = Color.BLACK if self.to_move == Color.WHITE else Color.WHITE
        is_legal = not self.is_in_check(previous_color)
        
        # Restore the position
        self._restore_state(old_state)
        
        return is_legal
    
    def make_move(self, move: Move) -> bool:
        """Make a move on the board. Returns True if successful."""
        if not self.is_legal_move(move):
            return False
        
        self._make_move_internal(move)
        self.move_history.append(move)
        self.position_history.append(self.to_fen())
        
        return True
    
    def _make_move_internal(self, move: Move):
        """Internal method to make a move without legality checks."""
        # Get moving piece
        moving_piece = self.get_piece_at(move.from_square)
        if not moving_piece:
            return
        
        piece_type, color = moving_piece
        
        # Get captured piece
        captured_piece = self.get_piece_at(move.to_square)
        if captured_piece:
            move.captured_piece = captured_piece[0]
        
        # Handle special moves
        if move.is_castling:
            self._handle_castling(move)
        elif move.is_en_passant:
            self._handle_en_passant(move)
        else:
            # Normal move
            self.remove_piece(move.from_square, piece_type, color)
            
            # Remove captured piece
            if captured_piece:
                self.remove_piece(move.to_square, captured_piece[0], captured_piece[1])
            
            # Place piece on target square
            if move.promotion:
                self.set_piece(move.to_square, move.promotion, color)
            else:
                self.set_piece(move.to_square, piece_type, color)
        
        # Update occupancy
        self.update_occupancy()
        
        # Update castling rights
        self._update_castling_rights(move, piece_type, color)
        
        # Update en passant square
        self._update_en_passant(move, piece_type)
        
        # Update clocks
        if piece_type == PieceType.PAWN or captured_piece:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        if self.to_move == Color.BLACK:
            self.fullmove_number += 1
        
        # Switch turn
        self.to_move = Color.BLACK if self.to_move == Color.WHITE else Color.WHITE
    
    def _handle_castling(self, move: Move):
        """Handle castling move."""
        color = self.to_move
        
        # Remove king and rook from original squares
        self.remove_piece(move.from_square, PieceType.KING, color)
        
        if move.to_square == 6 or move.to_square == 62:  # Kingside
            rook_from = 7 if color == Color.WHITE else 63
            rook_to = 5 if color == Color.WHITE else 61
        else:  # Queenside
            rook_from = 0 if color == Color.WHITE else 56
            rook_to = 3 if color == Color.WHITE else 59
        
        self.remove_piece(rook_from, PieceType.ROOK, color)
        
        # Place king and rook on new squares
        self.set_piece(move.to_square, PieceType.KING, color)
        self.set_piece(rook_to, PieceType.ROOK, color)
    
    def _handle_en_passant(self, move: Move):
        """Handle en passant capture."""
        color = self.to_move
        enemy_color = Color.BLACK if color == Color.WHITE else Color.WHITE
        
        # Move pawn
        self.remove_piece(move.from_square, PieceType.PAWN, color)
        self.set_piece(move.to_square, PieceType.PAWN, color)
        
        # Remove captured pawn
        captured_pawn_square = move.to_square - 8 if color == Color.WHITE else move.to_square + 8
        self.remove_piece(captured_pawn_square, PieceType.PAWN, enemy_color)
        move.captured_piece = PieceType.PAWN
    
    def _update_castling_rights(self, move: Move, piece_type: PieceType, color: Color):
        """Update castling rights after a move."""
        # King moves
        if piece_type == PieceType.KING:
            if color == Color.WHITE:
                self.castling_rights['K'] = False
                self.castling_rights['Q'] = False
            else:
                self.castling_rights['k'] = False
                self.castling_rights['q'] = False
        
        # Rook moves
        elif piece_type == PieceType.ROOK:
            if color == Color.WHITE:
                if move.from_square == 0:
                    self.castling_rights['Q'] = False
                elif move.from_square == 7:
                    self.castling_rights['K'] = False
            else:
                if move.from_square == 56:
                    self.castling_rights['q'] = False
                elif move.from_square == 63:
                    self.castling_rights['k'] = False
        
        # Rook captured
        if move.captured_piece == PieceType.ROOK:
            if move.to_square == 0:
                self.castling_rights['Q'] = False
            elif move.to_square == 7:
                self.castling_rights['K'] = False
            elif move.to_square == 56:
                self.castling_rights['q'] = False
            elif move.to_square == 63:
                self.castling_rights['k'] = False
    
    def _update_en_passant(self, move: Move, piece_type: PieceType):
        """Update en passant square after a move."""
        self.en_passant_square = None
        
        if piece_type == PieceType.PAWN:
            from_rank = move.from_square // 8
            to_rank = move.to_square // 8
            
            if abs(to_rank - from_rank) == 2:
                # Double pawn move
                self.en_passant_square = move.from_square + (8 if self.to_move == Color.WHITE else -8)
    
    def _save_state(self):
        """Save current board state for undo."""
        return {
            'pieces': copy.deepcopy(self.pieces),
            'color_occupancy': self.color_occupancy.copy(),
            'all_occupancy': self.all_occupancy,
            'to_move': self.to_move,
            'castling_rights': self.castling_rights.copy(),
            'en_passant_square': self.en_passant_square,
            'halfmove_clock': self.halfmove_clock,
            'fullmove_number': self.fullmove_number
        }
    
    def _restore_state(self, state):
        """Restore board state from saved state."""
        self.pieces = state['pieces']
        self.color_occupancy = state['color_occupancy']
        self.all_occupancy = state['all_occupancy']
        self.to_move = state['to_move']
        self.castling_rights = state['castling_rights']
        self.en_passant_square = state['en_passant_square']
        self.halfmove_clock = state['halfmove_clock']
        self.fullmove_number = state['fullmove_number']
    
    def to_fen(self) -> str:
        """Convert board position to FEN notation."""
        # Piece placement
        fen_parts = []
        for rank in range(7, -1, -1):
            rank_str = ""
            empty_count = 0
            
            for file in range(8):
                square = rank * 8 + file
                piece = self.get_piece_at(square)
                
                if piece:
                    if empty_count > 0:
                        rank_str += str(empty_count)
                        empty_count = 0
                    
                    piece_type, color = piece
                    piece_symbols = ['p', 'n', 'b', 'r', 'q', 'k']
                    symbol = piece_symbols[piece_type.value]
                    if color == Color.WHITE:
                        symbol = symbol.upper()
                    rank_str += symbol
                else:
                    empty_count += 1
            
            if empty_count > 0:
                rank_str += str(empty_count)
            
            fen_parts.append(rank_str)
        
        fen = "/".join(fen_parts)
        
        # Active color
        fen += " " + ("w" if self.to_move == Color.WHITE else "b")
        
        # Castling rights
        castling = ""
        for right in ['K', 'Q', 'k', 'q']:
            if self.castling_rights[right]:
                castling += right
        fen += " " + (castling if castling else "-")
        
        # En passant
        if self.en_passant_square is not None:
            ep_square = Square.from_index(self.en_passant_square)
            fen += " " + str(ep_square)
        else:
            fen += " -"
        
        # Halfmove and fullmove
        fen += f" {self.halfmove_clock} {self.fullmove_number}"
        
        return fen
    
    def from_fen(self, fen: str):
        """Set board position from FEN notation."""
        parts = fen.strip().split()
        
        # Clear board
        self.pieces = [[0] * 6 for _ in range(2)]
        self.color_occupancy = [0, 0]
        self.all_occupancy = 0
        
        # Piece placement
        piece_chars = {
            'P': (PieceType.PAWN, Color.WHITE),
            'N': (PieceType.KNIGHT, Color.WHITE),
            'B': (PieceType.BISHOP, Color.WHITE),
            'R': (PieceType.ROOK, Color.WHITE),
            'Q': (PieceType.QUEEN, Color.WHITE),
            'K': (PieceType.KING, Color.WHITE),
            'p': (PieceType.PAWN, Color.BLACK),
            'n': (PieceType.KNIGHT, Color.BLACK),
            'b': (PieceType.BISHOP, Color.BLACK),
            'r': (PieceType.ROOK, Color.BLACK),
            'q': (PieceType.QUEEN, Color.BLACK),
            'k': (PieceType.KING, Color.BLACK),
        }
        
        rank = 7
        file = 0
        for char in parts[0]:
            if char == '/':
                rank -= 1
                file = 0
            elif char.isdigit():
                file += int(char)
            else:
                piece_type, color = piece_chars[char]
                square = rank * 8 + file
                self.set_piece(square, piece_type, color)
                file += 1
        
        # Update occupancy
        self.update_occupancy()
        
        # Active color
        self.to_move = Color.WHITE if parts[1] == 'w' else Color.BLACK
        
        # Castling rights
        self.castling_rights = {'K': False, 'Q': False, 'k': False, 'q': False}
        for char in parts[2]:
            if char in self.castling_rights:
                self.castling_rights[char] = True
        
        # En passant
        if parts[3] != '-':
            ep_square = Square.from_string(parts[3])
            self.en_passant_square = ep_square.index
        else:
            self.en_passant_square = None
        
        # Clocks
        self.halfmove_clock = int(parts[4])
        self.fullmove_number = int(parts[5])
        
        # Clear history
        self.move_history = []
        self.position_history = [fen]
    
    def __str__(self):
        """String representation of the board."""
        piece_symbols = ['P', 'N', 'B', 'R', 'Q', 'K']
        
        board_str = ""
        for rank in range(7, -1, -1):
            board_str += f"{rank + 1} "
            for file in range(8):
                square = rank * 8 + file
                piece = self.get_piece_at(square)
                
                if piece:
                    piece_type, color = piece
                    symbol = piece_symbols[piece_type.value]
                    if color == Color.BLACK:
                        symbol = symbol.lower()
                    board_str += symbol
                else:
                    board_str += '.'
                board_str += " "
            board_str += "\n"
        board_str += "  a b c d e f g h\n"
        return board_str

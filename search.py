"""
Search algorithms including negascout, move ordering, quiescence, and SEE.
"""

import time
from typing import List, Optional, Tuple, Dict, Union
from bitboard import Board, Move, Color, PieceType, BitboardUtils
from evaluation import Evaluation


class MoveOrderer:
    """Handles move ordering for better alpha-beta pruning."""
    
    # Move ordering scores
    HASH_MOVE_SCORE = 10000
    WINNING_CAPTURE_BASE = 8000
    KILLER_MOVE_SCORE = 7000
    QUIET_MOVE_BASE = 1000
    LOSING_CAPTURE_BASE = 100
    
    # Piece values for MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }
    
    def __init__(self):
        self.killer_moves: List[List[Optional[Move]]] = [[None, None] for _ in range(64)]  # Two killer moves per ply
        self.history_table: Dict[Tuple[int, int], int] = {}  # History heuristic table
        self.see_calculator = StaticExchangeEvaluator()
    
    def order_moves(self, board: Board, moves: List[Move], ply: int, 
                   hash_move: Optional[Move] = None) -> List[Move]:
        """Order moves for better alpha-beta performance."""
        scored_moves = []
        
        for move in moves:
            score = self.score_move(board, move, ply, hash_move)
            move.score = score
            scored_moves.append(move)
        
        # Sort moves by score (highest first)
        scored_moves.sort(key=lambda m: m.score, reverse=True)
        return scored_moves
    
    def score_move(self, board: Board, move: Move, ply: int, 
                  hash_move: Optional[Move] = None) -> int:
        """Calculate a score for move ordering."""
        # Hash move (from transposition table)
        if hash_move and self.moves_equal(move, hash_move):
            return self.HASH_MOVE_SCORE
        
        # Captures
        captured_piece = board.get_piece_at(move.to_square)
        if captured_piece:
            moving_piece = board.get_piece_at(move.from_square)
            if moving_piece:
                victim_value = self.PIECE_VALUES[captured_piece[0]]
                aggressor_value = self.PIECE_VALUES[moving_piece[0]]
                
                # Use SEE for more accurate capture evaluation
                see_score = self.see_calculator.evaluate(board, move)
                if see_score >= 0:
                    # Winning or equal capture
                    return self.WINNING_CAPTURE_BASE + victim_value - aggressor_value
                else:
                    # Losing capture
                    return self.LOSING_CAPTURE_BASE + see_score
        
        # Promotions
        if move.promotion:
            promotion_bonus = self.PIECE_VALUES[move.promotion]
            return self.WINNING_CAPTURE_BASE + promotion_bonus
        
        # Killer moves
        if ply < len(self.killer_moves):
            for killer in self.killer_moves[ply]:
                if killer and self.moves_equal(move, killer):
                    return self.KILLER_MOVE_SCORE
        
        # History heuristic
        move_key = (move.from_square, move.to_square)
        history_score = self.history_table.get(move_key, 0)
        
        return self.QUIET_MOVE_BASE + history_score
    
    def update_killer_moves(self, move: Move, ply: int, board: Board):
        """Update killer moves when a move causes a beta cutoff."""
        if ply < len(self.killer_moves):
            # Don't store captures as killers
            if not board.get_piece_at(move.to_square):
                if not (self.killer_moves[ply][0] and self.moves_equal(move, self.killer_moves[ply][0])):
                    self.killer_moves[ply][1] = self.killer_moves[ply][0]
                    self.killer_moves[ply][0] = move
    
    def update_history(self, move: Move, depth: int):
        """Update history heuristic when a move causes a beta cutoff."""
        move_key = (move.from_square, move.to_square)
        bonus = depth * depth
        self.history_table[move_key] = self.history_table.get(move_key, 0) + bonus
    
    def moves_equal(self, move1: Move, move2: Optional[Move]) -> bool:
        """Check if two moves are equal."""
        if move2 is None:
            return False
        return (move1.from_square == move2.from_square and
                move1.to_square == move2.to_square and
                move1.promotion == move2.promotion)


class StaticExchangeEvaluator:
    """Static Exchange Evaluation for accurate capture assessment."""
    
    PIECE_VALUES = {
        PieceType.PAWN: 100,
        PieceType.KNIGHT: 320,
        PieceType.BISHOP: 330,
        PieceType.ROOK: 500,
        PieceType.QUEEN: 900,
        PieceType.KING: 20000
    }
    
    def evaluate(self, board: Board, move: Move) -> int:
        """
        Evaluate the static exchange value of a capture.
        Returns the material balance after all exchanges.
        """
        target_square = move.to_square
        captured_piece = board.get_piece_at(target_square)
        
        if not captured_piece:
            return 0  # Not a capture
        
        # Get all attackers to the target square
        white_attackers = self.get_attackers(board, target_square, Color.WHITE)
        black_attackers = self.get_attackers(board, target_square, Color.BLACK)
        
        # Remove the moving piece from attackers (it's making the initial capture)
        moving_color = board.to_move
        if moving_color == Color.WHITE:
            white_attackers.discard(move.from_square)
        else:
            black_attackers.discard(move.from_square)
        
        # Simulate the exchange sequence
        gain = [0] * 32  # Maximum possible exchange depth
        depth = 0
        
        # Initial capture value
        gain[depth] = self.PIECE_VALUES[captured_piece[0]]
        
        # Current piece on the square (the one that just captured)
        moving_piece = board.get_piece_at(move.from_square)
        if not moving_piece:
            return 0
        
        current_piece_value = self.PIECE_VALUES[moving_piece[0]]
        current_color = Color.BLACK if moving_color == Color.WHITE else Color.WHITE
        
        depth += 1
        
        while True:
            # Find the least valuable attacker for the current side
            attacker_square = None
            min_value = 99999
            
            attackers = black_attackers if current_color == Color.BLACK else white_attackers
            
            for square in attackers:
                piece = board.get_piece_at(square)
                if piece:
                    piece_value = self.PIECE_VALUES[piece[0]]
                    if piece_value < min_value:
                        min_value = piece_value
                        attacker_square = square
            
            if attacker_square is None:
                break  # No more attackers
            
            # Make the capture
            gain[depth] = current_piece_value - gain[depth - 1]
            
            # Remove the attacker from the appropriate set
            if current_color == Color.BLACK:
                black_attackers.discard(attacker_square)
            else:
                white_attackers.discard(attacker_square)
            
            # Update for next iteration
            current_piece_value = min_value
            current_color = Color.BLACK if current_color == Color.WHITE else Color.WHITE
            depth += 1
            
            if depth >= 32:  # Safety limit
                break
        
        # Minimax back through the gains
        while depth > 1:
            depth -= 1
            gain[depth - 1] = -max(-gain[depth - 1], gain[depth])
        
        return gain[0]
    
    def get_attackers(self, board: Board, square: int, color: Color) -> set:
        """Get all pieces of given color that attack the target square."""
        attackers = set()
        
        # Check each piece type
        for piece_type in PieceType:
            piece_bitboard = board.pieces[color.value][piece_type.value]
            
            # Use bitboard operations to find attackers
            while piece_bitboard:
                piece_bitboard, piece_square = BitboardUtils.pop_lsb(piece_bitboard)
                
                if self.piece_attacks_square(board, piece_square, piece_type, square):
                    attackers.add(piece_square)
        
        return attackers
    
    def piece_attacks_square(self, board: Board, piece_square: int, 
                           piece_type: PieceType, target_square: int) -> bool:
        """Check if a piece attacks a target square."""
        if piece_type == PieceType.PAWN:
            # Get the color of the piece
            piece_info = board.get_piece_at(piece_square)
            if not piece_info:
                return False
            color = piece_info[1]
            
            pawn_attacks = board.attack_tables.pawn_attacks[color.value][piece_square]
            return bool(pawn_attacks & (1 << target_square))
        
        elif piece_type == PieceType.KNIGHT:
            knight_attacks = board.attack_tables.knight_attacks[piece_square]
            return bool(knight_attacks & (1 << target_square))
        
        elif piece_type == PieceType.KING:
            king_attacks = board.attack_tables.king_attacks[piece_square]
            return bool(king_attacks & (1 << target_square))
        
        elif piece_type in [PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN]:
            # Use sliding piece attack generation
            return self.sliding_piece_attacks(board, piece_square, piece_type, target_square)
        
        return False
    
    def sliding_piece_attacks(self, board: Board, piece_square: int, 
                            piece_type: PieceType, target_square: int) -> bool:
        """Check if a sliding piece attacks a target square."""
        file_diff = (target_square % 8) - (piece_square % 8)
        rank_diff = (target_square // 8) - (piece_square // 8)
        
        # Check if move is valid for piece type
        is_diagonal = abs(file_diff) == abs(rank_diff)
        is_straight = file_diff == 0 or rank_diff == 0
        
        if piece_type == PieceType.BISHOP and not is_diagonal:
            return False
        elif piece_type == PieceType.ROOK and not is_straight:
            return False
        elif piece_type == PieceType.QUEEN and not (is_diagonal or is_straight):
            return False
        
        # Check for clear path
        if file_diff == 0 and rank_diff == 0:
            return False
        
        step_file = 0 if file_diff == 0 else (1 if file_diff > 0 else -1)
        step_rank = 0 if rank_diff == 0 else (1 if rank_diff > 0 else -1)
        
        current_square = piece_square + step_rank * 8 + step_file
        
        while current_square != target_square:
            if board.get_piece_at(current_square):
                return False  # Path blocked
            current_square += step_rank * 8 + step_file
        
        return True


class QuiescenceSearch:
    """Quiescence search to avoid horizon effect."""
    
    def __init__(self, evaluator: Evaluation, move_orderer: MoveOrderer):
        self.evaluator = evaluator
        self.move_orderer = move_orderer
        self.nodes_searched = 0
    
    def search(self, board: Board, alpha: int, beta: int, depth: int = 0) -> int:
        """
        Quiescence search - only search captures and checks to quiet positions.
        """
        self.nodes_searched += 1
        
        # Stand pat (do nothing) evaluation
        stand_pat = self.evaluator.evaluate(board)
        
        # Adjust score for side to move
        if board.to_move == Color.BLACK:
            stand_pat = -stand_pat
        
        # Beta cutoff
        if stand_pat >= beta:
            return beta
        
        # Update alpha
        if stand_pat > alpha:
            alpha = stand_pat
        
        # Maximum quiescence depth
        if depth >= 16:
            return stand_pat
        
        # Generate captures and checks
        moves = self.generate_quiescence_moves(board)
        
        if not moves:
            return stand_pat
        
        # Order moves
        moves = self.move_orderer.order_moves(board, moves, depth)
        
        for move in moves:
            # Make move
            if not board.make_move(move):
                continue
            
            # Recursive search
            score = -self.search(board, -beta, -alpha, depth + 1)
            
            # Unmake move (restore from history)
            self.unmake_last_move(board)
            
            if score >= beta:
                return beta
            
            if score > alpha:
                alpha = score
        
        return alpha
    
    def generate_quiescence_moves(self, board: Board) -> List[Move]:
        """Generate moves for quiescence search (captures and checks)."""
        moves = []
        pseudo_legal_moves = board.generate_pseudo_legal_moves()
        
        for move in pseudo_legal_moves:
            # Include captures
            if board.get_piece_at(move.to_square):
                moves.append(move)
            # Include promotions
            elif move.promotion:
                moves.append(move)
            # Include checks (simplified - could be optimized)
            else:
                # Make move temporarily to check if it gives check
                old_state = board._save_state()
                board._make_move_internal(move)
                
                enemy_color = Color.BLACK if board.to_move == Color.WHITE else Color.WHITE
                if board.is_in_check(enemy_color):
                    moves.append(move)
                
                board._restore_state(old_state)
        
        return moves
    
    def unmake_last_move(self, board: Board):
        """Unmake the last move (simplified - uses history)."""
        if board.move_history:
            board.move_history.pop()
            if board.position_history:
                board.position_history.pop()
                if board.position_history:
                    board.from_fen(board.position_history[-1])


class NegascoutSearch:
    """Negascout (Principal Variation Search) implementation."""
    
    def __init__(self, evaluator: Evaluation):
        self.evaluator = evaluator
        self.move_orderer = MoveOrderer()
        self.quiescence = QuiescenceSearch(evaluator, self.move_orderer)
        
        # Search statistics
        self.nodes_searched = 0
        self.cutoffs = 0
        self.transposition_hits = 0
        
        # Transposition table (simplified)
        self.transposition_table = {}
        
        # Time management
        self.start_time = 0
        self.time_limit = 0
        self.should_stop = False
    
    def search(self, board: Board, depth: int, time_limit: float = 10.0) -> Tuple[Optional[Move], int, Dict]:
        """
        Main search function using iterative deepening.
        Returns best move, evaluation, and search statistics.
        """
        self.start_time = time.time()
        self.time_limit = time_limit
        self.should_stop = False
        self.nodes_searched = 0
        self.cutoffs = 0
        self.transposition_hits = 0
        
        best_move = None
        best_score = 0
        
        # Iterative deepening
        for current_depth in range(1, depth + 1):
            if self.should_stop:
                break
            
            alpha = -999999
            beta = 999999
            
            score = self.negascout(board, current_depth, alpha, beta, 0, True)
            
            if not self.should_stop:
                # Find the best move from this depth
                moves = board.generate_legal_moves()
                if moves:
                    moves = self.move_orderer.order_moves(board, moves, 0)
                    
                    # The best move should be the first after ordering
                    for move in moves:
                        old_state = board._save_state()
                        board._make_move_internal(move)
                        
                        move_score = -self.negascout(board, current_depth - 1, -beta, -alpha, 1, False)
                        
                        board._restore_state(old_state)
                        
                        if move_score > alpha:
                            alpha = move_score
                            best_move = move
                            best_score = score
                        
                        if self.should_stop:
                            break
                
                print(f"Depth {current_depth}: Score {score}, Best move: {best_move}, "
                      f"Nodes: {self.nodes_searched}")
        
        statistics = {
            'nodes_searched': self.nodes_searched,
            'cutoffs': self.cutoffs,
            'transposition_hits': self.transposition_hits,
            'time_taken': time.time() - self.start_time,
            'nps': self.nodes_searched / max(time.time() - self.start_time, 0.001)
        }
        
        return best_move, best_score, statistics
    
    def negascout(self, board: Board, depth: int, alpha: int, beta: int, 
                 ply: int, is_pv_node: bool) -> int:
        """
        Negascout search algorithm.
        """
        # Check time limit
        if time.time() - self.start_time > self.time_limit:
            self.should_stop = True
            return 0
        
        self.nodes_searched += 1
        
        # Terminal conditions
        if depth <= 0:
            return self.quiescence.search(board, alpha, beta)
        
        # Check for checkmate/stalemate
        moves = board.generate_legal_moves()
        if not moves:
            if board.is_in_check(board.to_move):
                return -20000 + ply  # Checkmate (prefer closer mates)
            else:
                return 0  # Stalemate
        
        # Check for draw
        if self.is_draw(board):
            return 0
        
        # Move ordering
        moves = self.move_orderer.order_moves(board, moves, ply)
        
        first_move = True
        best_score = -999999
        
        for i, move in enumerate(moves):
            if self.should_stop:
                break
            
            # Make move
            old_state = board._save_state()
            board._make_move_internal(move)
            
            score = 0
            
            if first_move:
                # Full window search for first move
                score = -self.negascout(board, depth - 1, -beta, -alpha, ply + 1, is_pv_node)
                first_move = False
            else:
                # Null window search
                score = -self.negascout(board, depth - 1, -alpha - 1, -alpha, ply + 1, False)
                
                # Re-search if necessary
                if alpha < score < beta and is_pv_node:
                    score = -self.negascout(board, depth - 1, -beta, -score, ply + 1, True)
            
            # Unmake move
            board._restore_state(old_state)
            
            if score > best_score:
                best_score = score
            
            if score > alpha:
                alpha = score
            
            if alpha >= beta:
                # Beta cutoff
                self.cutoffs += 1
                self.move_orderer.update_killer_moves(move, ply, board)
                self.move_orderer.update_history(move, depth)
                break
        
        return best_score
    
    def is_draw(self, board: Board) -> bool:
        """Check for draw conditions."""
        # Fifty-move rule
        if board.halfmove_clock >= 100:
            return True
        
        # Threefold repetition (simplified)
        if len(board.position_history) >= 6:
            current_position = board.to_fen().split()[0]
            count = board.position_history.count(current_position)
            if count >= 3:
                return True
        
        # Insufficient material (simplified)
        return self.evaluator.is_insufficient_material(board)

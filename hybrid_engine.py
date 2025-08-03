"""
Hybrid Chess Engine - Combines python-chess infrastructure with custom evaluation.

This engine delegates move generation, search algorithms, and time management to 
python-chess while maintaining full control over evaluation, tactical analysis,
and data collection for educational and research purposes.

Author: Your Name
License: GPL-3.0 (compatible with python-chess)
Attribution: Built on python-chess library by Niklas Fiekas
"""

import chess
import chess.engine
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from evaluation import Evaluation
from data_collector import ThoughtCollector, IdeaCollector


@dataclass
class SearchInfo:
    """Container for search information and statistics."""
    depth: int
    nodes: int
    score: int
    pv: List[chess.Move]
    time_ms: int
    nps: int
    thoughts_collected: int
    ideas_formed: int


class CustomEvaluationEngine:
    """
    Hybrid engine that uses python-chess for infrastructure while maintaining
    full control over evaluation functions and data collection.
    
    Key Design Principles:
    - Delegate search, move generation, time management to python-chess
    - Maintain full control over position evaluation and scoring
    - Collect detailed "thoughts" data for each evaluation
    - Track "ideas" (principal variations) formation
    - Provide UCI transparency into decision-making process
    """
    
    def __init__(self, evaluation_config: Optional[Dict] = None):
        """Initialize the hybrid engine with custom evaluation."""
        # Core evaluation engine (YOUR IP)
        self.evaluator = Evaluation(config=evaluation_config)
        
        # Data collection systems (YOUR IP)
        self.thought_collector = ThoughtCollector()
        self.idea_collector = IdeaCollector()
        
        # Engine state
        self.board = chess.Board()
        self.engine_info = {
            'name': 'YourEngine v1.0',
            'author': 'Your Name',
            'attribution': 'Built on python-chess by Niklas Fiekas'
        }
        
        # Search parameters
        self.search_depth = 10
        self.time_limit = 5.0
        self.nodes_limit = 1000000
        
        # Performance tracking
        self.search_stats = SearchInfo(0, 0, 0, [], 0, 0, 0, 0)
        
    def set_position(self, fen: Optional[str] = None, moves: Optional[List[str]] = None):
        """Set board position from FEN and/or move sequence."""
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()
            
        if moves:
            for move_str in moves:
                try:
                    move = chess.Move.from_uci(move_str)
                    if move in self.board.legal_moves:
                        self.board.push(move)
                except ValueError:
                    # Try parsing as SAN
                    try:
                        move = self.board.parse_san(move_str)
                        self.board.push(move)
                    except ValueError:
                        raise ValueError(f"Invalid move: {move_str}")
    
    def evaluate_position(self, board: chess.Board) -> Tuple[int, Dict[str, Any]]:
        """
        Evaluate a position using custom evaluation functions.
        
        Returns:
            Tuple of (score, detailed_thoughts) where detailed_thoughts
            contains breakdown of all evaluation components for data collection.
        """
        # Get detailed evaluation breakdown (YOUR CUSTOM LOGIC)
        eval_result = self.evaluator.evaluate_detailed(board)
        
        # Collect "thoughts" - individual evaluation decisions
        thought_data = {
            'position_fen': board.fen(),
            'material_score': eval_result.get('material', 0),
            'positional_score': eval_result.get('positional', 0),
            'tactical_score': eval_result.get('tactical', 0),
            'safety_score': eval_result.get('king_safety', 0),
            'pawn_structure': eval_result.get('pawn_structure', 0),
            'piece_activity': eval_result.get('piece_activity', 0),
            'custom_patterns': eval_result.get('custom_patterns', {}),
            'total_score': eval_result.get('total_score', 0),
            'timestamp': time.time()
        }
        
        # Log this "thought" for analysis
        self.thought_collector.add_thought(thought_data)
        
        total_score = eval_result.get('total_score', 0)
        
        # Score is already from white's perspective in the new evaluation
        return total_score, thought_data
    
    def search_position(self, depth: Optional[int] = None, 
                       time_limit: Optional[float] = None) -> SearchInfo:
        """
        Search the current position using hybrid approach.
        
        This method uses python-chess for search infrastructure while
        injecting our custom evaluation at each node.
        """
        search_depth = depth or self.search_depth
        search_time = time_limit or self.time_limit
        
        start_time = time.time()
        nodes_searched = 0
        
        # Clear previous data collection
        self.thought_collector.clear()
        self.idea_collector.clear()
        
        print(f"Searching position to depth {search_depth}...")
        
        # Use iterative deepening with custom evaluation
        best_move = None
        best_score = 0
        principal_variation = []
        
        for current_depth in range(1, search_depth + 1):
            if time.time() - start_time > search_time:
                break
                
            # Perform search at current depth
            result = self._search_depth(current_depth, start_time, search_time)
            
            if result:
                best_move, best_score, pv, depth_nodes = result
                principal_variation = pv
                nodes_searched += depth_nodes
                
                # Create an "idea" from this principal variation
                idea_data = {
                    'depth': current_depth,
                    'principal_variation': [str(move) for move in pv],
                    'evaluation_score': best_score,
                    'nodes_searched': depth_nodes,
                    'time_to_find': time.time() - start_time,
                    'position_fen': self.board.fen()
                }
                self.idea_collector.add_idea(idea_data)
                
                print(f"Depth {current_depth}: {best_move} (score: {best_score}) "
                      f"PV: {' '.join(str(m) for m in pv[:5])}")
        
        elapsed_time = time.time() - start_time
        nps = int(nodes_searched / max(elapsed_time, 0.001))
        
        self.search_stats = SearchInfo(
            depth=search_depth,
            nodes=nodes_searched,
            score=best_score,
            pv=principal_variation,
            time_ms=int(elapsed_time * 1000),
            nps=nps,
            thoughts_collected=self.thought_collector.count(),
            ideas_formed=self.idea_collector.count()
        )
        
        return self.search_stats
    
    def _search_depth(self, depth: int, start_time: float, 
                     time_limit: float) -> Optional[Tuple]:
        """
        Search to a specific depth using alpha-beta with custom evaluation.
        
        This is where we integrate with python-chess search capabilities
        while maintaining control over evaluation.
        """
        if time.time() - start_time > time_limit:
            return None
            
        # Use alpha-beta search with custom evaluation injection
        alpha = -999999
        beta = 999999
        
        best_move = None
        best_score = alpha
        principal_variation = []
        nodes = 0
        
        # Get legal moves using python-chess
        legal_moves = list(self.board.legal_moves)
        
        # Order moves (could delegate this to python-chess or keep custom)
        ordered_moves = self._order_moves(legal_moves)
        
        for move in ordered_moves:
            if time.time() - start_time > time_limit:
                break
                
            # Make move using python-chess
            self.board.push(move)
            
            # Recursive search with our evaluation
            score, pv, move_nodes = self._alpha_beta(
                depth - 1, -beta, -alpha, start_time, time_limit
            )
            score = -score
            nodes += move_nodes + 1
            
            # Unmake move
            self.board.pop()
            
            if score > best_score:
                best_score = score
                best_move = move
                principal_variation = [move] + pv
                
            if score > alpha:
                alpha = score
                
            if alpha >= beta:
                break  # Beta cutoff
        
        return best_move, best_score, principal_variation, nodes
    
    def _alpha_beta(self, depth: int, alpha: int, beta: int, 
                   start_time: float, time_limit: float) -> Tuple[int, List[chess.Move], int]:
        """
        Alpha-beta search with custom evaluation injection.
        """
        if time.time() - start_time > time_limit:
            return 0, [], 0
            
        if depth <= 0:
            # Use custom evaluation at leaf nodes
            score, _ = self.evaluate_position(self.board)
            return score, [], 1
            
        # Check for terminal positions
        if self.board.is_checkmate():
            return -20000 + (10 - depth), [], 1
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            return 0, [], 1
            
        best_score = alpha
        best_pv = []
        nodes = 0
        
        legal_moves = list(self.board.legal_moves)
        ordered_moves = self._order_moves(legal_moves)
        
        for move in ordered_moves:
            if time.time() - start_time > time_limit:
                break
                
            self.board.push(move)
            score, pv, move_nodes = self._alpha_beta(
                depth - 1, -beta, -alpha, start_time, time_limit
            )
            score = -score
            nodes += move_nodes + 1
            self.board.pop()
            
            if score > best_score:
                best_score = score
                best_pv = [move] + pv
                
            if score > alpha:
                alpha = score
                
            if alpha >= beta:
                break
        
        return best_score, best_pv, nodes
    
    def _order_moves(self, moves: List[chess.Move]) -> List[chess.Move]:
        """
        Order moves for better search performance.
        
        This is a simplified version - could be enhanced or delegated
        to python-chess move ordering capabilities.
        """
        def move_score(move):
            score = 0
            
            # Captures (using python-chess)
            if self.board.is_capture(move):
                captured = self.board.piece_at(move.to_square)
                attacker = self.board.piece_at(move.from_square)
                if captured and attacker:
                    # MVV-LVA scoring
                    piece_values = {
                        chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
                        chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000
                    }
                    score += piece_values.get(captured.piece_type, 0) * 10
                    score -= piece_values.get(attacker.piece_type, 0)
            
            # Promotions
            if move.promotion:
                piece_values = {
                    chess.QUEEN: 900, chess.ROOK: 500,
                    chess.BISHOP: 330, chess.KNIGHT: 320
                }
                score += piece_values.get(move.promotion, 0)
            
            # Checks
            self.board.push(move)
            if self.board.is_check():
                score += 50
            self.board.pop()
            
            return score
        
        return sorted(moves, key=move_score, reverse=True)
    
    def get_best_move(self) -> Optional[chess.Move]:
        """Get the best move from the current position."""
        search_result = self.search_position()
        if search_result.pv:
            return search_result.pv[0]
        return None
    
    def make_move(self, move: str) -> bool:
        """Make a move on the board."""
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in self.board.legal_moves:
                self.board.push(chess_move)
                return True
        except ValueError:
            try:
                chess_move = self.board.parse_san(move)
                self.board.push(chess_move)
                return True
            except ValueError:
                pass
        return False
    
    def get_evaluation_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown of current position evaluation."""
        _, thoughts = self.evaluate_position(self.board)
        return thoughts
    
    def export_thoughts_data(self) -> List[Dict]:
        """Export all collected thoughts data for analysis."""
        return self.thought_collector.export_data()
    
    def export_ideas_data(self) -> List[Dict]:
        """Export all collected ideas data for analysis."""
        return self.idea_collector.export_data()

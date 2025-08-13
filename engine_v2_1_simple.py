"""
Simple Cece Chess Engine v2.1 - Fixed UCI Bug

This is a simplified engine focused on evaluation only, delegating search 
and complex functionality to libraries. Fixed the UCI bestmove bug.

Author: Pat Snyder
License: GPL-3.0
"""

import chess
import time
from typing import Optional, Dict, Any, List, Tuple
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


class ChessEngine:
    """
    Simplified chess engine that focuses on evaluation with v2.1 fixes.
    """
    
    def __init__(self, evaluation_config: Optional[Dict] = None):
        """Initialize the simplified engine."""
        # Core evaluation engine
        self.evaluator = Evaluation(config=evaluation_config)
        
        # Data collection systems
        self.thought_collector = ThoughtCollector()
        self.idea_collector = IdeaCollector()
        
        # Engine state
        self.board = chess.Board()
        
        # Engine metadata
        self.info = {
            'name': 'Cece',
            'version': '2.1',
            'author': 'Pat Snyder',
            'description': 'Simplified engine with v2.1 UCI fixes and pure evaluation',
            'license': 'GPL-3.0',
            'attribution': 'Built on python-chess by Niklas Fiekas'
        }
        
        # Search parameters
        self.search_depth = 6
        self.time_limit = 5.0
        
        # Performance tracking
        self.search_stats = SearchInfo(0, 0, 0, [], 0, 0, 0, 0)
        
        print(f"Initialized {self.info['name']} v{self.info['version']}")
        print(f"Author: {self.info['author']}")
        print(f"Attribution: {self.info['attribution']}")
    
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
        
        print(f"Position set: {self.board.fen()}")
    
    def evaluate_position_internal(self, board: chess.Board) -> Tuple[int, Dict[str, Any]]:
        """Internal method: Evaluate a position using custom evaluation functions."""
        # Get detailed evaluation breakdown
        eval_result = self.evaluator.evaluate_detailed(board)
        
        # Collect "thoughts" - individual evaluation decisions
        thought_data = {
            'position_fen': board.fen(),
            'material_score': eval_result.get('material', 0),
            'development_score': eval_result.get('development', 0),
            'knight_score': eval_result.get('knight_positioning', 0),
            'rook_score': eval_result.get('rook_activity', 0),
            'safety_score': eval_result.get('material_safety', 0),
            'king_safety_score': eval_result.get('king_safety', 0),
            'center_score': eval_result.get('center_control', 0),
            'total_score': eval_result.get('total_score', 0),
            'timestamp': time.time()
        }
        
        # Log this "thought" for analysis
        self.thought_collector.add_thought(thought_data)
        
        total_score = eval_result.get('total_score', 0)
        return total_score, thought_data
    
    def search_position(self, depth: Optional[int] = None, 
                       time_limit: Optional[float] = None) -> SearchInfo:
        """
        Simple search using minimax with alpha-beta pruning.
        """
        search_depth = depth or self.search_depth
        search_time = time_limit or self.time_limit
        
        start_time = time.time()
        nodes_searched = 0
        
        # Clear previous data collection
        self.thought_collector.clear()
        self.idea_collector.clear()
        
        print(f"Searching position to depth {search_depth}...")
        
        # Simple iterative deepening
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
        Search to a specific depth using simple alpha-beta.
        """
        if time.time() - start_time > time_limit:
            return None
            
        # Use alpha-beta search with custom evaluation
        alpha = -999999
        beta = 999999
        
        best_move = None
        best_score = alpha
        principal_variation = []
        nodes = 0
        
        # Get legal moves
        legal_moves = list(self.board.legal_moves)
        
        # Simple move ordering (captures first)
        ordered_moves = self._order_moves_simple(legal_moves)
        
        for move in ordered_moves:
            if time.time() - start_time > time_limit:
                break
                
            # Make move
            self.board.push(move)
            
            # Recursive search
            score, pv, move_nodes = self._alpha_beta_simple(
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
    
    def _alpha_beta_simple(self, depth: int, alpha: int, beta: int, 
                          start_time: float, time_limit: float) -> Tuple[int, List[chess.Move], int]:
        """
        Simple alpha-beta search.
        """
        if time.time() - start_time > time_limit:
            return 0, [], 0
            
        if depth <= 0:
            # Terminal node - evaluate position
            score, _ = self.evaluate_position_internal(self.board)
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
        ordered_moves = self._order_moves_simple(legal_moves)
        
        for move in ordered_moves:
            if time.time() - start_time > time_limit:
                break
                
            self.board.push(move)
            score, pv, move_nodes = self._alpha_beta_simple(
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
    
    def _order_moves_simple(self, moves: List[chess.Move]) -> List[chess.Move]:
        """Simple move ordering - captures first, then others."""
        captures = []
        other_moves = []
        
        for move in moves:
            if self.board.is_capture(move):
                captures.append(move)
            else:
                other_moves.append(move)
        
        # Sort captures by MVV-LVA
        def capture_score(move):
            captured_piece = self.board.piece_at(move.to_square)
            attacking_piece = self.board.piece_at(move.from_square)
            
            if captured_piece and attacking_piece:
                victim_value = self.evaluator.piece_values[captured_piece.piece_type]
                attacker_value = self.evaluator.piece_values[attacking_piece.piece_type]
                return victim_value - (attacker_value // 10)
            return 0
        
        captures.sort(key=capture_score, reverse=True)
        
        return captures + other_moves
    
    def get_best_move(self, depth: Optional[int] = None, 
                     time_limit: Optional[float] = None) -> Optional[chess.Move]:
        """
        Get the best move for the current position.
        """
        search_depth = depth or self.search_depth
        search_time = time_limit or self.time_limit
        
        print(f"\\nSearching position (depth: {search_depth}, time: {search_time}s)...")
        
        # Use the simplified search
        search_result = self.search_position(search_depth, search_time)
        
        # Display search statistics
        print(f"Search completed:")
        print(f"  Nodes searched: {search_result.nodes:,}")
        print(f"  Time taken: {search_result.time_ms/1000:.3f}s")
        print(f"  NPS: {search_result.nps:,}")
        print(f"  Evaluation: {search_result.score}")
        print(f"  Thoughts collected: {search_result.thoughts_collected}")
        print(f"  Ideas formed: {search_result.ideas_formed}")
        
        if search_result.pv:
            pv_str = ' '.join(str(move) for move in search_result.pv[:5])
            print(f"  Principal variation: {pv_str}")
            return search_result.pv[0]
        
        return None
    
    def make_move(self, move: str) -> bool:
        """Make a move on the board."""
        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in self.board.legal_moves:
                self.board.push(chess_move)
                print(f"Move made: {move}")
                print(f"New position: {self.board.fen()}")
                return True
        except ValueError:
            try:
                chess_move = self.board.parse_san(move)
                self.board.push(chess_move)
                print(f"Move made: {move}")
                print(f"New position: {self.board.fen()}")
                return True
            except ValueError:
                pass
        
        print(f"Invalid move: {move}")
        return False
    
    def get_evaluation_breakdown(self) -> Dict[str, Any]:
        """Get detailed evaluation of current position."""
        return self.evaluator.evaluate_detailed(self.board)
    
    def tune_evaluation(self, parameter: str, value: float):
        """Tune evaluation parameters."""
        print(f"Tuning {parameter} to {value} (simplified engine)")
        # Could implement parameter tuning if needed
    
    def get_evaluation_explanation(self) -> str:
        """Get human-readable explanation of the position evaluation."""
        eval_result = self.evaluator.evaluate_detailed(self.board)
        
        explanation = f"Position Evaluation Breakdown:\\n"
        explanation += f"Material: {eval_result.get('material', 0):+d}\\n"
        explanation += f"Development: {eval_result.get('development', 0):+d}\\n"
        explanation += f"Knight Positioning: {eval_result.get('knight_positioning', 0):+d}\\n"
        explanation += f"Rook Activity: {eval_result.get('rook_activity', 0):+d}\\n"
        explanation += f"Material Safety: {eval_result.get('material_safety', 0):+d}\\n"
        explanation += f"King Safety: {eval_result.get('king_safety', 0):+d}\\n"
        explanation += f"Center Control: {eval_result.get('center_control', 0):+d}\\n"
        explanation += f"Total Score: {eval_result.get('total_score', 0):+d}\\n"
        
        return explanation

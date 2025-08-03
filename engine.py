"""
Hybrid Chess Engine - Complete Implementation

This engine combines the best of both worlds:
- Uses python-chess for reliable infrastructure (move generation, board representation, etc.)
- Maintains full control over evaluation logic for your custom chess personality
- Provides comprehensive data collection for analysis and tuning

Architecture:
- Delegates complex chess infrastructure to proven libraries
- Focuses your effort on evaluation, pattern recognition, and analysis
- Maintains ethical use of open source while clearly defining your contributions

Author: Your Name
License: GPL-3.0 (compatible with python-chess)
Attribution: Built on python-chess library by Niklas Fiekas
"""

import chess
import chess.engine
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
    Hybrid chess engine that combines python-chess infrastructure with custom evaluation.
    
    This class provides both:
    1. Core engine functionality (search, evaluation, data collection)
    2. User-friendly interface methods (analysis, tuning, benchmarking)
    
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
        
        # Engine metadata
        self.info = {
            'name': 'YourChessEngine',
            'version': '1.0',
            'author': 'Your Name',
            'description': 'Hybrid engine focusing on custom evaluation and analysis',
            'license': 'GPL-3.0',
            'attribution': 'Built on python-chess by Niklas Fiekas'
        }
        
        # Search parameters
        self.search_depth = 10
        self.time_limit = 5.0
        self.nodes_limit = 1000000
        
        # Performance tracking
        self.search_stats = SearchInfo(0, 0, 0, [], 0, 0, 0, 0)
        
        print(f"Initialized {self.info['name']} v{self.info['version']}")
        print(f"Author: {self.info['author']}")
        print(f"Attribution: {self.info['attribution']}")
    
    # === Core Engine Methods ===
    
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
        """
        Internal method: Evaluate a position using custom evaluation functions.
        
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
        
        # Order moves for better search performance
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
    
    # === User-Friendly Interface Methods ===
    
    def get_best_move(self, depth: Optional[int] = None, 
                     time_limit: Optional[float] = None) -> Optional[chess.Move]:
        """
        Get the best move for the current position.
        """
        search_depth = depth or self.search_depth
        search_time = time_limit or self.time_limit
        
        print(f"\\nSearching position (depth: {search_depth}, time: {search_time}s)...")
        
        # Use the hybrid search that combines efficiency with custom evaluation
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
    
    def analyze_position(self) -> Dict[str, Any]:
        """
        Get detailed analysis of the current position.
        """
        analysis = self.get_evaluation_breakdown()
        
        print("\\n=== Position Analysis ===")
        print(f"FEN: {self.board.fen()}")
        print(f"Total Score: {analysis['total_score']}")
        print(f"Material: {analysis['material_score']}")
        print(f"Positional: {analysis['positional_score']}")
        print(f"Tactical: {analysis['tactical_score']}")
        print(f"King Safety: {analysis['safety_score']}")
        print(f"Pawn Structure: {analysis['pawn_structure']}")
        print(f"Piece Activity: {analysis['piece_activity']}")
        
        if analysis['custom_patterns']:
            print("\\nCustom Patterns Detected:")
            for pattern, value in analysis['custom_patterns'].items():
                print(f"  {pattern}: {value}")
        
        return analysis
    
    def get_evaluation_breakdown(self) -> Dict[str, Any]:
        """Get detailed breakdown of current position evaluation."""
        _, thoughts = self.evaluate_position_internal(self.board)
        return thoughts
    
    def export_analysis_data(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Export collected analysis data for research and tuning.
        """
        thoughts_data = self.thought_collector.export_data()
        ideas_data = self.idea_collector.export_data()
        
        export_data = {
            'engine_info': self.info,
            'session_summary': {
                'total_thoughts': len(thoughts_data),
                'total_ideas': len(ideas_data),
                'positions_analyzed': len(set(t['position_fen'] for t in thoughts_data)),
                'export_timestamp': time.time()
            },
            'thoughts': thoughts_data,
            'ideas': ideas_data
        }
        
        if filename:
            import json
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"Analysis data exported to: {filename}")
        
        print(f"\\nSession Summary:")
        print(f"  Thoughts collected: {export_data['session_summary']['total_thoughts']}")
        print(f"  Ideas formed: {export_data['session_summary']['total_ideas']}")
        print(f"  Positions analyzed: {export_data['session_summary']['positions_analyzed']}")
        
        return export_data
    
    def tune_evaluation(self, parameter: str, value: float):
        """
        Tune evaluation parameters for experimentation.
        """
        if parameter in self.evaluator.weights:
            old_value = self.evaluator.weights[parameter]
            self.evaluator.weights[parameter] = value
            print(f"Tuned {parameter}: {old_value} -> {value}")
        elif parameter in self.evaluator.pattern_bonuses:
            old_value = self.evaluator.pattern_bonuses[parameter]
            self.evaluator.pattern_bonuses[parameter] = int(value)
            print(f"Tuned {parameter}: {old_value} -> {int(value)}")
        else:
            print(f"Unknown parameter: {parameter}")
            print("Available weights:", list(self.evaluator.weights.keys()))
            print("Available patterns:", list(self.evaluator.pattern_bonuses.keys()))
    
    def get_evaluation_explanation(self) -> str:
        """Get human-readable explanation of position evaluation."""
        return self.evaluator.get_evaluation_explanation(self.board)
    
    def play_move_sequence(self, moves: List[str]) -> List[Dict[str, Any]]:
        """
        Play a sequence of moves and collect analysis data.
        """
        move_analyses = []
        
        for i, move_str in enumerate(moves):
            print(f"\\nMove {i+1}: {move_str}")
            
            # Analyze position before move
            pre_analysis = self.analyze_position()
            
            # Make the move
            if not self.make_move(move_str):
                print(f"Invalid move sequence stopped at: {move_str}")
                break
            
            # Analyze position after move
            post_analysis = self.analyze_position()
            
            move_analyses.append({
                'move': move_str,
                'move_number': i + 1,
                'before': pre_analysis,
                'after': post_analysis,
                'evaluation_change': post_analysis['total_score'] - pre_analysis['total_score']
            })
        
        return move_analyses
    
    def benchmark(self, positions: List[str], depth: int = 6) -> Dict[str, Any]:
        """
        Benchmark the engine on a set of positions.
        """
        results = []
        total_time = 0
        total_nodes = 0
        
        print(f"\\nBenchmarking on {len(positions)} positions at depth {depth}...")
        
        for i, fen in enumerate(positions):
            print(f"Position {i+1}/{len(positions)}: {fen[:50]}...")
            
            self.set_position(fen)
            start_time = time.time()
            
            search_result = self.search_position(depth, time_limit=30.0)
            
            elapsed = time.time() - start_time
            total_time += elapsed
            total_nodes += search_result.nodes
            
            results.append({
                'position': fen,
                'best_move': str(search_result.pv[0]) if search_result.pv else None,
                'evaluation': search_result.score,
                'nodes': search_result.nodes,
                'time': elapsed,
                'nps': search_result.nps
            })
        
        avg_time = total_time / len(positions)
        avg_nodes = total_nodes / len(positions)
        overall_nps = total_nodes / total_time if total_time > 0 else 0
        
        benchmark_summary = {
            'positions_tested': len(positions),
            'depth': depth,
            'total_time': total_time,
            'total_nodes': total_nodes,
            'average_time': avg_time,
            'average_nodes': avg_nodes,
            'overall_nps': overall_nps,
            'results': results
        }
        
        print(f"\\nBenchmark Complete:")
        print(f"  Positions: {len(positions)}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Total nodes: {total_nodes:,}")
        print(f"  Average NPS: {overall_nps:,.0f}")
        
        return benchmark_summary
    
    def __str__(self):
        """String representation of the engine."""
        return f"{self.info['name']} v{self.info['version']} by {self.info['author']}"
